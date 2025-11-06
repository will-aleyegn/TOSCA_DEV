"""
Module: Main Window
Project: TOSCA Laser Control System

Purpose: Primary application window with 3-tab interface (Setup, Treatment, Safety)
         and global toolbar. Provides emergency stop button, hardware connection
         management, and safety status display.
Safety Critical: Yes
"""

import asyncio
import logging
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from config.config_loader import get_config
from core.event_logger import EventLogger, EventSeverity, EventType
from core.protocol_engine import ProtocolEngine
from core.safety import SafetyManager, SafetyState
from core.safety_watchdog import SafetyWatchdog
from core.session_manager import SessionManager
from database.db_manager import DatabaseManager
from ui.dialogs.research_mode_warning_dialog import ResearchModeWarningDialog
from ui.widgets.camera_widget import CameraWidget
from ui.widgets.protocol_steps_display_widget import ProtocolStepsDisplayWidget
from ui.widgets.safety_widget import SafetyWidget
from ui.widgets.unified_header_widget import UnifiedHeaderWidget
from ui.widgets.unified_session_setup_widget import UnifiedSessionSetupWidget
from ui.widgets.workflow_step_indicator import WorkflowStepIndicator
# OLD imports removed: SubjectWidget, TreatmentSetupWidget (replaced by unified widgets)

logger = logging.getLogger(__name__)


# ============================================================================
# Protocol Execution Worker (QRunnable + asyncio.run())
# ============================================================================


class LineProtocolWorkerSignals(QObject):
    """Signals for LineProtocolWorker communication with main thread."""

    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)  # error_message


class LineProtocolWorker(QRunnable):
    """
    Worker for executing line-based protocols in a background thread.

    Uses QRunnable + asyncio.run() pattern for safe async execution.
    This creates a new asyncio event loop in the worker thread,
    separate from the PyQt6 event loop.
    """

    def __init__(self, engine, protocol):
        super().__init__()
        self.engine = engine
        self.protocol = protocol
        self.signals = LineProtocolWorkerSignals()

    def run(self) -> None:
        """Execute protocol in worker thread with asyncio.run()."""
        try:
            # Create new asyncio event loop for this thread
            success, message = asyncio.run(
                self.engine.execute_protocol(self.protocol, record=True, stop_on_error=True)
            )

            # Emit finished signal
            self.signals.finished.emit(success, message)

        except Exception as e:
            logger.error(f"Protocol worker exception: {e}", exc_info=True)
            self.signals.error.emit(str(e))


# ============================================================================
# Main Window
# ============================================================================


class MainWindow(QMainWindow):
    """
    Main application window.

    Provides tab-based navigation between:
    - Subject selection
    - Camera/alignment view
    - Treatment control
    - Safety status
    """

    # Signals
    dev_mode_changed = pyqtSignal(bool)  # True=dev mode, False=normal mode

    def __init__(self) -> None:
        super().__init__()

        logger.info("Initializing main window")

        # Load configuration
        config = get_config()

        # Set window title with research mode watermark if configured
        if config.gui.research_mode:
            title = "TOSCA v0.9.11-alpha - RESEARCH MODE ONLY"
            self.setWindowTitle(title)
        else:
            title = "TOSCA Laser Control System"
            self.setWindowTitle(title)

        # Store original title for developer mode restoration
        self.original_title = title

        self.setGeometry(100, 100, 1200, 900)  # Adjusted from 1400x900 for better vertical space

        # Initialize database and session managers
        self.db_manager = DatabaseManager()
        self.db_manager.initialize()
        self.session_manager = SessionManager(self.db_manager)
        self.event_logger = EventLogger(self.db_manager)

        # ===================================================================
        # HARDWARE CONTROLLERS - Centralized Instantiation (Dependency Injection)
        # ===================================================================
        # All hardware controllers are instantiated here and injected into widgets
        # This follows the Hollywood Principle: "Don't call us, we'll call you"
        # Benefits: Clear lifecycle management, easier testing, consistent architecture

        from hardware.actuator_controller import ActuatorController
        from hardware.camera_controller import CameraController
        from hardware.gpio_controller import GPIOController
        from hardware.laser_controller import LaserController
        from hardware.tec_controller import TECController

        self.actuator_controller = ActuatorController()
        self.laser_controller = LaserController()
        self.tec_controller = TECController()
        self.gpio_controller = GPIOController()
        self.camera_controller = CameraController(event_logger=self.event_logger)

        logger.info("All hardware controllers instantiated in MainWindow")

        # SAFETY-CRITICAL: Initialize watchdog early (before GPIO connection)
        # GPIO controller will be attached later in _connect_safety_system()
        self.safety_watchdog = SafetyWatchdog(
            gpio_controller=None, event_logger=self.event_logger  # Will be set when GPIO connects
        )
        logger.info("Safety watchdog pre-initialized (awaiting GPIO connection)")
        logger.info("Database, session, and event logger initialized")

        # Log system startup
        self.event_logger.log_system_event(
            EventType.SYSTEM_STARTUP, "TOSCA system started", EventSeverity.INFO
        )

        # Show research mode warning dialog if configured
        self._show_research_mode_warning()

        self._init_ui()
        self._init_menubar()

        logger.info("Main window initialized")

    def _show_research_mode_warning(self) -> None:
        """
        Show research mode warning dialog if configured.

        Displays a warning dialog informing the user that the system is for
        research use only and not approved for clinical use. Requires explicit
        acknowledgment before proceeding.

        If the user rejects the warning (clicks Cancel), the application exits.
        """
        config = get_config()

        if config.gui.show_warning_on_startup:
            logger.info("Showing research mode warning dialog")

            dialog = ResearchModeWarningDialog(self)
            result = dialog.exec()

            if result == ResearchModeWarningDialog.DialogCode.Accepted:
                # User acknowledged warning
                self.event_logger.log_system_event(
                    EventType.USER_ACTION,
                    "Research mode warning acknowledged",
                    EventSeverity.INFO,
                )
                logger.info("User acknowledged research mode warning")
            else:
                # User rejected warning - exit application
                self.event_logger.log_system_event(
                    EventType.USER_ACTION,
                    "Research mode warning rejected - exiting application",
                    EventSeverity.WARNING,
                )
                logger.warning("User rejected research mode warning - exiting")
                # Close and exit
                import sys

                sys.exit(0)
        else:
            logger.info("Research mode warning dialog disabled in configuration")

    def _init_ui(self) -> None:
        """Initialize main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # NEW: Unified header at top (replaces toolbar + right panel + status bar)
        self.unified_header = UnifiedHeaderWidget()
        main_layout.addWidget(self.unified_header)

        # OLD: Horizontal split with right panel (COMMENTED OUT)
        # from PyQt6.QtWidgets import QHBoxLayout
        # content_layout = QHBoxLayout()
        # main_layout.addLayout(content_layout)

        # Tabs (main content) - now full width without right panel
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)  # Changed from content_layout to main_layout

        # OLD: Right side safety panel (COMMENTED OUT - moved to unified header)
        # from ui.widgets.safety_status_panel import SafetyStatusPanel
        # self.safety_status_panel = SafetyStatusPanel()
        # content_layout.addWidget(self.safety_status_panel)

        # TAB 1: HARDWARE & DIAGNOSTICS
        # Layout: 4-column grid for compact hardware module arrangement
        # Individual widgets provide their own connection controls
        hardware_tab = QWidget()
        hardware_tab_main_layout = QVBoxLayout()
        hardware_tab.setLayout(hardware_tab_main_layout)

        # === SCROLLABLE GRID LAYOUT (4-COLUMN) ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        from PyQt6.QtWidgets import QGridLayout
        self.hardware_grid_layout = QGridLayout()  # Make instance variable for later actuator insertion
        self.hardware_grid_layout.setSpacing(12)  # Spacing between grid cells
        self.hardware_grid_layout.setContentsMargins(8, 8, 8, 8)
        scroll_content.setLayout(self.hardware_grid_layout)

        # === ROW 0: GPIO CONNECTION (FULL WIDTH - 4 COLUMNS) ===
        from ui.widgets.gpio_widget import GPIOWidget

        self.gpio_widget = GPIOWidget(controller=self.gpio_controller)
        self.hardware_grid_layout.addWidget(self.gpio_widget, 0, 0, 1, 4)  # Row 0, Col 0, span 1 row, 4 cols

        # === ROW 1: SAFETY INTERLOCKS (3 COLUMNS) ===
        from ui.widgets.footpedal_widget import FootpedalWidget
        from ui.widgets.photodiode_widget import PhotodiodeWidget
        from ui.widgets.smoothing_module_widget import SmoothingModuleWidget

        self.footpedal_widget = FootpedalWidget(gpio_controller=self.gpio_controller)
        self.hardware_grid_layout.addWidget(self.footpedal_widget, 1, 0)  # Row 1, Col 0

        self.photodiode_widget = PhotodiodeWidget(gpio_controller=self.gpio_controller)
        self.hardware_grid_layout.addWidget(self.photodiode_widget, 1, 1)  # Row 1, Col 1

        self.smoothing_module_widget = SmoothingModuleWidget(gpio_controller=self.gpio_controller)
        self.hardware_grid_layout.addWidget(self.smoothing_module_widget, 1, 2)  # Row 1, Col 2

        # === ROW 2: LASER SYSTEMS (2 COLUMNS) ===
        # Note: laser_widget contains both aiming and treatment laser controls
        # User requested these side-by-side; currently they're in one widget with vertical layout
        # This spans 2 columns to provide space for both sections
        from ui.widgets.laser_widget import LaserWidget

        self.laser_widget = LaserWidget(
            controller=self.laser_controller, tec_controller=self.tec_controller
        )
        self.laser_widget.gpio_controller = self.gpio_controller  # For aiming laser controls
        self.hardware_grid_layout.addWidget(self.laser_widget, 2, 0, 1, 2)  # Row 2, Col 0-1, span 2 cols

        # === ROW 3: CAMERA + ACTUATOR (2 COLUMNS) ===
        from ui.widgets.camera_hardware_panel import CameraHardwarePanel

        self.camera_hardware_panel = CameraHardwarePanel(None)  # Will set camera_live_view later
        self.hardware_grid_layout.addWidget(self.camera_hardware_panel, 3, 0)  # Row 3, Col 0

        # === MOTION CONTROL (Actuator) ===
        # Will be created and inserted here after controllers are initialized
        # Store grid position for later insertion
        self.actuator_grid_row = 3
        self.actuator_grid_col = 1

        # Set column stretch factors (all equal width)
        for col in range(4):
            self.hardware_grid_layout.setColumnStretch(col, 1)

        # === ROW 4+: SAFETY EVENT LOG & CONFIG (INSIDE SCROLL AREA) ===
        # Add safety log and config to grid so they scroll with hardware modules
        self.safety_widget = SafetyWidget(
            db_manager=self.db_manager, gpio_controller=self.gpio_controller
        )
        # Hide software interlocks section (now in persistent header)
        if hasattr(self.safety_widget, 'software_interlocks_widget'):
            self.safety_widget.software_interlocks_widget.hide()

        # Set reasonable height constraints for safety log
        self.safety_widget.setMaximumHeight(300)  # Max 300px to prevent screen dominance

        self.hardware_grid_layout.addWidget(self.safety_widget, 4, 0, 1, 4)  # Row 4, full width

        from ui.widgets.config_display_widget import ConfigDisplayWidget
        self.config_display_widget = ConfigDisplayWidget()
        self.hardware_grid_layout.addWidget(self.config_display_widget, 5, 0, 1, 4)  # Row 5, full width

        # Set row stretch factors to control vertical space distribution
        # Rows 0-3 (hardware modules) get equal minimal stretch
        for row in range(4):
            self.hardware_grid_layout.setRowStretch(row, 0)  # No stretch - use minimum size
        # Row 4 (safety log) gets some stretch
        self.hardware_grid_layout.setRowStretch(4, 1)
        # Row 5 (config) gets minimal stretch
        self.hardware_grid_layout.setRowStretch(5, 0)

        scroll_area.setWidget(scroll_content)
        hardware_tab_main_layout.addWidget(scroll_area)

        self.tabs.addTab(hardware_tab, "Hardware & Diagnostics")

        # TAB 2: TREATMENT WORKFLOW
        # Subject management + Camera + Protocol selector + Execution monitoring
        # Layout: 2-column (40% controls | 60% camera) with scrolling
        treatment_tab = QWidget()
        treatment_main_layout = QHBoxLayout()
        treatment_tab.setLayout(treatment_main_layout)

        # === LEFT COLUMN (40%): Workflow Controls ===
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; }")

        left_content = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        left_content.setLayout(left_layout)

        # Top row: Session Setup (left) + Camera Controls (right) side-by-side
        top_horizontal = QHBoxLayout()
        top_horizontal.setSpacing(8)

        # Left sub-column: Unified Session Setup
        self.unified_session_setup = UnifiedSessionSetupWidget(
            session_manager=self.session_manager,
            db_manager=self.db_manager
        )
        top_horizontal.addWidget(self.unified_session_setup, 1)  # 50% of left column

        # Right sub-column: Camera Controls (compact)
        self.camera_controls_widget = self._create_compact_camera_controls()
        top_horizontal.addWidget(self.camera_controls_widget, 1)  # 50% of left column

        left_layout.addLayout(top_horizontal)

        # Bottom: Protocol Steps Display (full width within left column)
        self.protocol_steps_display = ProtocolStepsDisplayWidget()
        left_layout.addWidget(self.protocol_steps_display)

        left_scroll.setWidget(left_content)
        left_scroll.setMinimumWidth(400)  # Prevent excessive squishing
        treatment_main_layout.addWidget(left_scroll, 2)  # 40% width (stretch=2)

        # === RIGHT COLUMN (60%): Camera Feed ONLY (No scroll area for maximum space) ===
        # Camera Feed ONLY (no controls, no chart below) - maximized for best visibility
        self.camera_live_view = CameraWidget(
            camera_controller=self.camera_controller,
            show_settings=False  # Hide exposure/gain controls - Hardware tab only
        )
        # Hide ENTIRE control panel (connection, streaming, capture, record)
        # Controls moved to left column in compact format
        self.camera_live_view.hide_all_controls()
        self.camera_live_view.setMinimumWidth(900)  # Ensure minimum width for camera visibility
        treatment_main_layout.addWidget(self.camera_live_view, 3)  # 60% width (stretch=3)

        # NOTE: Position chart removed from Treatment tab - can be added back to Protocol Builder if needed

        # NOTE: CameraController already instantiated in __init__
        # and injected into camera_live_view widget

        # Wire camera connection widget to main camera widget for status updates
        self.camera_hardware_panel.camera_live_view = self.camera_live_view
        self.camera_hardware_panel._connect_signals()  # Connect signals now that camera_live_view is set
        logger.info("Camera hardware panel wired to camera widget signals")

        self.tabs.addTab(treatment_tab, "Treatment Workflow")

        # === SIGNAL WIRING ===

        # Wire unified session setup to protocol steps display
        self.unified_session_setup.protocol_loaded.connect(self.protocol_steps_display.load_protocol)
        logger.info("Unified session setup protocol_loaded -> protocol steps display")

        # Wire unified session setup to workflow step indicator
        self.unified_session_setup.session_started.connect(
            lambda subject_id, technician, protocol_path: self.unified_header.set_workflow_step(2)
        )
        self.unified_session_setup.protocol_loaded.connect(
            lambda path: self.unified_header.set_workflow_step(3)
        )
        self.unified_session_setup.session_ended.connect(
            lambda: self.unified_header.set_workflow_step(1)
        )
        logger.info("Unified session setup -> workflow step indicator (unified header)")

        # Wire unified session setup to safety manager for session validation
        self.unified_session_setup.session_started.connect(
            lambda subject_id, technician, protocol_path: self._on_session_started_new(subject_id, technician, protocol_path)
        )
        logger.info("Unified session setup -> safety manager session validation")

        # Wire protocol steps display pause/stop buttons to line protocol engine
        self.protocol_steps_display.pause_requested.connect(
            lambda: self.line_protocol_engine.pause() if hasattr(self, 'line_protocol_engine') else None
        )
        self.protocol_steps_display.stop_requested.connect(
            lambda: self.line_protocol_engine.stop() if hasattr(self, 'line_protocol_engine') else None
        )
        logger.info("Protocol steps display pause/stop buttons wired to line protocol engine")

        # Connect dev mode signal to widgets (after widgets are created)
        self.dev_mode_changed.connect(self.camera_live_view.set_dev_mode)
        # OLD: treatment_setup_widget removed in redesign
        # Motor widget removed from treatment setup - now only in GPIO diagnostics

        # TAB 3: LINE-BASED PROTOCOL BUILDER
        # LineProtocolBuilderWidget for creating treatment protocols with concurrent actions
        protocol_builder_tab = QWidget()
        builder_layout = QVBoxLayout()
        protocol_builder_tab.setLayout(builder_layout)

        # LineProtocolBuilderWidget (line-based concurrent action protocol editor)
        from core.protocol_line import SafetyLimits
        from ui.widgets.line_protocol_builder import LineProtocolBuilderWidget

        self.line_protocol_builder = LineProtocolBuilderWidget()

        # Configure safety limits from TOSCA defaults
        safety_limits = SafetyLimits(
            max_power_watts=10.0,
            max_duration_seconds=300.0,
            min_actuator_position_mm=-20.0,
            max_actuator_position_mm=20.0,
            max_actuator_speed_mm_per_s=5.0,
        )
        self.line_protocol_builder.set_safety_limits(safety_limits)

        # Connect protocol execution signal
        self.line_protocol_builder.protocol_ready.connect(self._on_line_protocol_ready)

        builder_layout.addWidget(self.line_protocol_builder)

        self.tabs.addTab(protocol_builder_tab, "Protocol Builder")

        # Set default tab to Treatment Workflow (index 1) instead of Hardware (index 0)
        self.tabs.setCurrentIndex(1)
        logger.info("Default tab set to Treatment Workflow")

        # Add Actuator Connection widget to Hardware tab
        # (ActuatorController already instantiated in __init__ with other hardware controllers)
        from ui.widgets.actuator_connection_widget import ActuatorConnectionWidget

        self.actuator_connection_widget = ActuatorConnectionWidget(
            controller=self.actuator_controller
        )
        # Insert into grid at stored position (Row 3, Col 1)
        self.hardware_grid_layout.addWidget(
            self.actuator_connection_widget, self.actuator_grid_row, self.actuator_grid_col
        )
        logger.info("Actuator connection widget added to Hardware tab grid (Row 3, Col 1)")

        # Initialize safety manager
        self.safety_manager = SafetyManager()
        self._connect_safety_system()
        logger.info("Safety manager initialized and connected")

        # OLD: Safety status panel connections (COMMENTED OUT - now in unified header)
        # self.safety_status_panel.set_safety_manager(self.safety_manager)
        # self.safety_status_panel.set_session_manager(self.session_manager)
        # logger.info("Safety status panel connected to managers")

        # Initialize protocol engine with hardware controllers
        self._init_protocol_engine()

        # Connect event logger to widgets
        self._connect_event_logger()

        # Wire unified header signals (must be after safety_manager is created)
        self._wire_unified_header_signals()


    def _create_compact_camera_controls(self) -> Any:
        """
        Create compact camera controls for Treatment tab left column.

        Includes:
        - Start/Stop Streaming button
        - Capture Image button
        - Start/Stop Recording button
        - Brightness slider (optional - TODO)

        Returns:
            QGroupBox with compact camera controls
        """
        from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout
        from ui.design_tokens import Colors

        group = QGroupBox("Camera Controls")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Colors.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Stream button (PRIMARY ACTION - prominent, green, large)
        self.treatment_stream_btn = QPushButton("▶ Start Streaming")
        self.treatment_stream_btn.setMinimumHeight(50)  # Touch-friendly
        self.treatment_stream_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SAFE};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.CONNECTED};
            }}
            QPushButton:disabled {{
                background-color: {Colors.SECONDARY};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.treatment_stream_btn.clicked.connect(self._on_treatment_stream_clicked)
        layout.addWidget(self.treatment_stream_btn)

        # Capture/Record buttons row (SECONDARY ACTIONS - blue, side-by-side)
        capture_layout = QHBoxLayout()
        capture_layout.setSpacing(8)

        self.treatment_capture_btn = QPushButton("📷 Capture")
        self.treatment_capture_btn.setMinimumHeight(45)  # Touch-friendly
        self.treatment_capture_btn.setEnabled(False)  # Disabled until streaming
        self.treatment_capture_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #2979FF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2962FF;
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.treatment_capture_btn.clicked.connect(
            lambda: self.camera_live_view._on_capture_image() if hasattr(self, "camera_live_view") else None
        )
        capture_layout.addWidget(self.treatment_capture_btn)

        self.treatment_record_btn = QPushButton("🔴 Record")
        self.treatment_record_btn.setMinimumHeight(45)  # Touch-friendly
        self.treatment_record_btn.setEnabled(False)  # Disabled until streaming
        self.treatment_record_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #2979FF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2962FF;
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.treatment_record_btn.clicked.connect(self._on_treatment_record_clicked)
        capture_layout.addWidget(self.treatment_record_btn)

        layout.addLayout(capture_layout)

        group.setLayout(layout)
        return group

    def _on_treatment_stream_clicked(self) -> None:
        """Handle treatment tab stream button click."""
        if self.camera_live_view.is_streaming:
            self.camera_controller.stop_streaming()
            self.camera_live_view.is_streaming = False
            self.treatment_stream_btn.setText("Start Streaming")
            self.treatment_capture_btn.setEnabled(False)
            self.treatment_record_btn.setEnabled(False)
        else:
            self.camera_controller.start_streaming()
            self.camera_live_view.is_streaming = True
            self.treatment_stream_btn.setText("Stop Streaming")
            self.treatment_capture_btn.setEnabled(True)
            self.treatment_record_btn.setEnabled(True)

    def _on_treatment_record_clicked(self) -> None:
        """Handle treatment tab record button click."""
        if self.camera_controller.is_recording:
            self.camera_controller.stop_recording()
            self.treatment_record_btn.setText("Start Recording")
        else:
            base_filename = "treatment_recording"
            self.camera_controller.start_recording(base_filename)
            self.treatment_record_btn.setText("Stop Recording")

    # NOTE: Protocol chart removed from Treatment tab (camera feed takes full 60%)
    # This method can be added back to Protocol Builder tab if needed

    def _init_menubar(self) -> None:
        """Initialize menubar with File and Developer menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Exit action
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Developer menu
        developer_menu = menubar.addMenu("&Developer")

        # Dev Mode toggle (moved from status bar)
        self.dev_mode_action = developer_menu.addAction("Developer Mode")
        self.dev_mode_action.setCheckable(True)
        self.dev_mode_action.setChecked(False)
        self.dev_mode_action.setToolTip(
            "Enable developer mode to bypass session management and customize save paths"
        )
        self.dev_mode_action.triggered.connect(self._on_dev_mode_changed_menubar)

        logger.info("Menubar initialized")

    def _wire_unified_header_signals(self) -> None:
        """Wire unified header widget signals to main window functionality."""
        # E-Stop button -> Global E-Stop handler
        self.unified_header.e_stop_clicked.connect(self._on_global_estop_clicked)
        logger.info("Unified header E-Stop connected to global handler")

        # Safety state updates -> Unified header safety display
        self.safety_manager.safety_state_changed.connect(self.unified_header.update_safety_state)
        # Emit initial state
        self.unified_header.update_safety_state(self.safety_manager.state)
        logger.info("Safety manager connected to unified header safety display")

        # Software interlocks updates -> Unified header software interlocks display
        self.safety_manager.safety_state_changed.connect(self._update_software_interlocks_header)
        # Emit initial state
        self._update_software_interlocks_header(self.safety_manager.state)
        logger.info("Safety manager connected to unified header software interlocks")

        # Interlock status updates -> Unified header interlock indicators
        # Wire GPIO interlock signals when GPIO connects (will be set in _handle_hardware_connection)
        # self.gpio_controller.safety_interlock_changed.connect(self.unified_header.update_interlock_status)

        # Workflow step updates (from subject/treatment widgets)
        # Already connected in _init_ui, but we'll redirect to unified header
        # Disconnect old workflow_steps widget connections and reconnect to unified header
        # (Will be done after we fix the workflow_steps references below)

        logger.info("Unified header signals wired successfully")

    # ========================================================================
    def _update_session_indicator(self) -> None:
        """Update session indicator in status bar with current session info."""
        current_session = self.session_manager.get_current_session()

        if current_session:
            # Session active - show indicator
            from datetime import datetime, timezone

            subject_code = current_session.subject_code
            tech_name = current_session.tech_name
            start_time = current_session.start_time

            # Calculate duration
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            duration = datetime.now(timezone.utc) - start_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Update label
            self.session_info_label.setText(
                f"SESSION: {subject_code} | Tech: {tech_name} | Duration: {duration_str}"
            )
            self.session_info_label.setStyleSheet(
                "font-size: 11pt; padding: 4px 8px; color: #1976D2; font-weight: bold; "
                "background-color: #E3F2FD; border-radius: 3px;"
            )
            self.session_panel_widget.setVisible(True)

            # Start duration timer (updates every second)
            if not self.session_duration_timer.isActive():
                self.session_duration_timer.start(1000)  # 1 second interval

            logger.info(f"Session indicator updated: {subject_code} - {duration_str}")
        else:
            # No active session - hide indicator
            self.session_info_label.setText("No active session")
            self.session_info_label.setStyleSheet(
                "font-size: 11pt; padding: 4px 8px; color: #757575; "
                "background-color: #F5F5F5; border-radius: 3px;"
            )
            self.session_panel_widget.setVisible(False)

            # Stop timer
            if self.session_duration_timer.isActive():
                self.session_duration_timer.stop()

            logger.info("Session indicator cleared (no active session)")

    def _update_session_duration(self) -> None:
        """Update session duration display (called every second by timer)."""
        current_session = self.session_manager.get_current_session()

        if current_session:
            from datetime import datetime, timezone

            subject_code = current_session.subject_code
            tech_name = current_session.tech_name
            start_time = current_session.start_time

            # Calculate duration
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            duration = datetime.now(timezone.utc) - start_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Update label (keep same styling)
            self.session_info_label.setText(
                f"SESSION: {subject_code} | Tech: {tech_name} | Duration: {duration_str}"
            )
        else:
            # Session ended - stop timer
            if self.session_duration_timer.isActive():
                self.session_duration_timer.stop()
            self._update_session_indicator()  # Refresh to "No active session"

    def _show_dev_mode_confirmation(self) -> bool:
        """
        Show confirmation dialog for enabling developer mode.

        Returns:
            True if user confirmed, False if cancelled
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("[!] Developer Mode Warning")
        msg.setText(
            "You are about to enable Developer Mode with:\n\n"
            "• Safety interlock bypass\n"
            "• Session requirement bypass\n\n"
            "This mode is for CALIBRATION AND TESTING ONLY.\n"
            "Never use for actual patient treatment.\n\n"
            "All actions will be logged for audit trail."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        return msg.exec() == QMessageBox.StandardButton.Yes

    def _show_dev_mode_warnings(self, show: bool) -> None:
        """
        Show/hide developer mode warnings in UI.

        Args:
            show: True to show warnings, False to hide
        """
        if show:
            # Status bar warning (persistent)
            self.statusBar().showMessage(
                "[!] DEVELOPER MODE: Safety Bypasses Active - FOR TESTING ONLY",
                0,  # Timeout = 0 means persistent
            )
            self.statusBar().setStyleSheet(
                "background-color: #FF0000; color: white; font-weight: bold;"
            )

            # Title bar watermark
            self.setWindowTitle(f"{self.original_title} [DEV MODE - BYPASSES ACTIVE]")
        else:
            # Restore normal status bar
            self.statusBar().clearMessage()
            self.statusBar().setStyleSheet("")

            # Restore normal title
            self.setWindowTitle(self.original_title)

    def _on_dev_mode_changed_menubar(self, checked: bool) -> None:
        """Handle dev mode menu action toggle with safety bypass."""
        if checked:
            # Show confirmation
            if not self._show_dev_mode_confirmation():
                self.dev_mode_action.setChecked(False)
                return

            # Enable developer mode
            self.safety_manager.set_developer_mode_bypass(True)
            self.session_manager.developer_mode_enabled = True

            # Update UI warnings
            self._show_dev_mode_warnings(True)

            logger.critical("DEVELOPER MODE ENABLED BY USER")

            # Log event
            if hasattr(self, "event_logger"):
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    EventType.USER_OVERRIDE,
                    "Developer mode ENABLED - Safety bypasses active",
                    EventSeverity.CRITICAL,
                )
        else:
            # Disable developer mode
            self.safety_manager.set_developer_mode_bypass(False)
            self.session_manager.developer_mode_enabled = False

            # Remove UI warnings
            self._show_dev_mode_warnings(False)

            logger.info("Developer mode disabled by user")

            # Log event
            if hasattr(self, "event_logger"):
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    EventType.USER_OVERRIDE,
                    "Developer mode DISABLED",
                    EventSeverity.INFO,
                )

        # Emit signal for other widgets
        self.dev_mode_changed.emit(checked)

    def _update_camera_header_status(self, connected: bool) -> None:
        """Update camera section header with connection status."""
        if connected:
            self.camera_header.setText("[CAM] Camera System [OK]")
            self.camera_header.setStyleSheet(
                "font-size: 13px; font-weight: bold; padding: 8px; margin-top: 4px; "
                "background-color: #2E7D32; color: white; border-radius: 3px;"
            )
        else:
            self.camera_header.setText("[CAM] Camera System [X]")
            self.camera_header.setStyleSheet(
                "font-size: 13px; font-weight: bold; padding: 8px; margin-top: 4px; "
                "background-color: #37474F; color: #64B5F6; border-radius: 3px;"
            )

    # NOTE: Header status methods removed - hardware tab now uses individual widget controls
    # def _update_actuator_header_status(self, connected: bool) -> None:
    #     """Update actuator section header with connection status."""
    #     pass
    #
    # def _update_laser_header_status(self, connected: bool) -> None:
    #     """Update laser section header with connection status."""
    #     pass

    def _connect_safety_system(self) -> None:
        """Connect safety system components."""
        # Connect safety manager to safety widget for display
        self.safety_widget.set_safety_manager(self.safety_manager)
        logger.info("Safety manager connected to safety widget")

        # Connect to GPIO widget's connection status signal
        # Controller doesn't exist yet - created when user clicks Connect
        # So we connect to widget's forwarding signal instead
        if hasattr(self, "gpio_widget") and self.gpio_widget:
            gpio_widget = self.gpio_widget
            # Connect to GPIO widget's stable signal (not controller's)
            gpio_widget.gpio_connection_changed.connect(self._on_gpio_connection_changed)
            logger.info("Main window connected to GPIO widget connection signal")

        # Connect safety manager to laser widget (in Hardware & Diagnostics tab)
        # Laser widget will check safety manager before enabling
        if hasattr(self, "laser_widget"):
            self.laser_widget.safety_manager = self.safety_manager
            logger.info("Safety manager connected to laser widget")

        # Connect GPIO controller safety interlock signal to safety manager (one-time connection)
        # Note: Controller exists from __init__, so connect immediately
        self.gpio_controller.safety_interlock_changed.connect(
            self.safety_manager.set_gpio_interlock_status
        )
        logger.info("GPIO controller safety interlocks -> safety manager (connected)")

        # Connect safety manager interlock status to unified header (one-time connection)
        self.safety_manager.interlock_status_changed.connect(self._update_unified_header_interlocks)
        logger.info("Safety manager interlocks -> unified header (connected)")

        # Connect watchdog signals (one-time connection)
        self.safety_watchdog.heartbeat_failed.connect(
            lambda msg: logger.error(f"Watchdog heartbeat failed: {msg}")
        )
        self.safety_watchdog.watchdog_timeout_detected.connect(
            self._handle_watchdog_timeout
        )
        logger.info("Safety watchdog signals connected")

        # Log safety events (in addition to widget display)
        self.safety_manager.safety_state_changed.connect(
            lambda state: logger.info(f"Safety state: {state.value}")
        )
        self.safety_manager.laser_enable_changed.connect(
            lambda enabled: logger.info(f"Laser enable: {'PERMITTED' if enabled else 'DENIED'}")
        )
        self.safety_manager.safety_event.connect(
            lambda event_type, message: logger.info(f"Safety event [{event_type}]: {message}")
        )

    def _handle_watchdog_timeout(self) -> None:
        """
        Handle safety watchdog timeout with selective shutdown.

        SELECTIVE SHUTDOWN POLICY:
        - Treatment laser: DISABLED (safety-critical)
        - Other systems: REMAIN OPERATIONAL for monitoring and assessment
          (camera, actuator, aiming laser, GPIO monitoring)

        This allows operators to:
        - Visually assess the situation via camera
        - Safely reposition equipment
        - Diagnose the cause of timeout
        - Perform orderly shutdown

        Reference: docs/architecture/SAFETY_SHUTDOWN_POLICY.md
        """
        logger.critical("WATCHDOG TIMEOUT DETECTED - GPIO CONNECTION LOST")
        logger.critical("Executing SELECTIVE SHUTDOWN: Treatment laser ONLY")

        # 1. Trigger emergency stop in safety manager
        # This prevents laser from being re-enabled
        self.safety_manager.trigger_emergency_stop()

        # 2. Disable treatment laser ONLY (selective shutdown)
        if hasattr(self, "laser_widget"):
            if hasattr(self.laser_widget, "controller") and self.laser_widget.controller:
                if self.laser_widget.controller.is_connected:
                    logger.critical("Disabling treatment laser due to watchdog timeout")
                    self.laser_widget.controller.set_output(False)
                else:
                    logger.warning(
                        "Laser controller not connected - cannot perform shutdown "
                        "(may already be disconnected)"
                    )

        # 3. Log critical event
        if hasattr(self, "event_logger") and self.event_logger:
            self.event_logger.log_system_event(
                EventType.SYSTEM_ERROR,
                "Watchdog timeout - treatment laser disabled, other systems remain operational",
                EventSeverity.EMERGENCY,
            )

        # 4. Show critical warning to user
        QMessageBox.critical(
            self,
            "Safety Watchdog Timeout",
            "CRITICAL SAFETY EVENT: Watchdog timeout detected.\n\n"
            "Treatment laser has been DISABLED.\n"
            "Other systems remain operational for monitoring.\n\n"
            "Possible causes:\n"
            "- GUI freeze or high CPU load\n"
            "- GPIO connection lost\n"
            "- Serial communication failure\n\n"
            "Check system logs and verify all connections before proceeding.",
        )

    def _on_gpio_connection_changed(self, connected: bool) -> None:
        """
        Handle GPIO connection status changes.

        Starts watchdog heartbeat when GPIO connects,
        stops heartbeat when GPIO disconnects.

        Args:
            connected: True if GPIO connected, False if disconnected
        """
        if connected:
            # GPIO connected - attach to watchdog and start heartbeat
            gpio_widget = self.gpio_widget
            if gpio_widget and gpio_widget.controller:
                # Attach GPIO controller to watchdog
                self.safety_watchdog.gpio_controller = gpio_widget.controller
                logger.info("GPIO controller attached to safety watchdog")

                # Update initial interlock state
                self._update_unified_header_interlocks()

                # Start heartbeat - CRITICAL for Arduino stability
                if self.safety_watchdog.start():
                    logger.info("Safety watchdog started (500ms heartbeat, 1000ms timeout)")
                else:
                    logger.error("CRITICAL: Safety watchdog failed to start!")
        else:
            # GPIO disconnected - stop heartbeat
            self.safety_watchdog.stop()
            logger.info("Safety watchdog stopped (GPIO disconnected)")

    def _update_unified_header_interlocks(self) -> None:
        """
        Update unified header interlock indicators from safety manager.

        Adapter method that fetches interlock status from safety manager
        and passes it to unified header widget.
        """
        interlocks = self.safety_manager.get_interlock_status()
        self.unified_header.update_interlock_status(interlocks)

    def _update_software_interlocks_header(self, state) -> None:
        """
        Update unified header software interlocks from safety manager state.

        Args:
            state: SafetyState from safety manager
        """
        from core.safety import SafetyState

        # Determine software interlock states
        estop_active = state == SafetyState.EMERGENCY_STOP
        power_ok = True  # TODO: Wire to actual power limit monitoring
        session_valid = hasattr(self, 'session_manager') and self.session_manager.get_current_session() is not None

        # Get session ID if active
        session_id = None
        if session_valid:
            session = self.session_manager.get_current_session()
            if session:
                session_id = str(session.session_id)

        # Update unified header
        self.unified_header.update_software_interlocks(
            estop_active=estop_active,
            power_ok=power_ok,
            session_valid=session_valid,
            session_id=session_id
        )

    def _init_protocol_engine(self) -> None:
        """Initialize protocol engine and wire to hardware controllers."""
        # All hardware controllers are managed directly by MainWindow (Dependency Injection pattern)
        # Controllers are instantiated in __init__ and injected into widgets
        # Protocol engine receives controller references directly from MainWindow

        # Initialize protocol engine with MainWindow-managed controllers
        self.protocol_engine = ProtocolEngine(
            laser_controller=self.laser_controller,
            actuator_controller=self.actuator_controller,
            safety_manager=self.safety_manager,
        )

        # Initialize line-based protocol engine
        from core.line_protocol_engine import LineBasedProtocolEngine

        self.line_protocol_engine = LineBasedProtocolEngine(
            laser_controller=self.laser_controller,
            actuator_controller=self.actuator_controller,
            safety_manager=self.safety_manager,
        )

        # Connect line protocol engine callbacks for UI updates
        self.line_protocol_engine.on_line_start = self._on_protocol_line_start
        self.line_protocol_engine.on_line_complete = self._on_protocol_line_complete
        self.line_protocol_engine.on_progress_update = self._on_protocol_progress_update
        self.line_protocol_engine.on_state_change = self._on_protocol_state_change

        logger.info(
            f"Protocol engines initialized with MainWindow controllers "
            f"(laser: {self.laser_controller is not None}, "
            f"actuator: {self.actuator_controller is not None}, "
            f"safety: {self.safety_manager is not None})"
        )

    def _connect_event_logger(self) -> None:
        """Connect event logger to system components."""
        # Connect session manager signals
        self.session_manager.session_started.connect(self._on_event_logger_session_started)
        self.session_manager.session_ended.connect(self._on_event_logger_session_ended)

        # Connect session changes to software interlocks header update
        self.session_manager.session_started.connect(
            lambda session_id: self._update_software_interlocks_header(self.safety_manager.state)
        )
        self.session_manager.session_ended.connect(
            lambda session_id: self._update_software_interlocks_header(self.safety_manager.state)
        )

        # Connect event logger to safety widget for display
        if hasattr(self.safety_widget, "event_log"):
            self.event_logger.event_logged.connect(
                lambda event_type, severity, desc: logger.info(
                    f"Event: [{severity}] {event_type} - {desc}"
                )
            )

        logger.info("Event logger connected to system")

    def _on_event_logger_session_started(self, session_id: int) -> None:
        """
        Handle session started for event logging.

        Args:
            session_id: ID of started session
        """
        # Set session in event logger
        session = self.session_manager.get_current_session()
        if session:
            self.event_logger.set_session(session_id, session.tech_id)
            self.event_logger.log_treatment_event(
                EventType.TREATMENT_SESSION_START,
                f"Treatment session {session_id} started for subject {session.subject_id}",
            )

    def _on_event_logger_session_ended(self, session_id: int) -> None:
        """
        Handle session ended for event logging.

        Args:
            session_id: ID of ended session
        """
        self.event_logger.log_treatment_event(
            EventType.TREATMENT_SESSION_END, f"Treatment session {session_id} ended"
        )
        self.event_logger.clear_session()

    def _on_session_started(self, session_id: int) -> None:
        """
        Handle session started event (OLD - for SubjectWidget).

        Args:
            session_id: ID of started session
        """
        logger.info(f"Session {session_id} started - updating safety system and session indicator")
        # Mark session as valid for safety system
        self.safety_manager.set_session_valid(True)

        # Update session indicator in status bar
        self._update_session_indicator()

    def _on_session_started_new(self, subject_id: str, technician: str, protocol_path: str) -> None:
        """
        Handle session started event (NEW - for UnifiedSessionSetupWidget).

        Args:
            subject_id: Subject ID from database
            technician: Technician name
            protocol_path: Path to protocol JSON file
        """
        logger.info(f"NEW session started: Subject={subject_id}, Tech={technician}, Protocol={protocol_path}")

        # Mark session as valid for safety system
        self.safety_manager.set_session_valid(True)

        # Update session indicator in status bar (if exists)
        if hasattr(self, '_update_session_indicator'):
            self._update_session_indicator()

        logger.info("Session validated for safety system")

    def _on_start_treatment(self) -> None:
        """
        Handle Start Treatment button click.

        Transitions from Setup view to Active view within Treatment Dashboard.
        This is a one-way transition - operator stays in Active view until
        treatment completes.
        """
        logger.info("Starting treatment - switching to Active view")
        self.treatment_stack.setCurrentIndex(1)  # Switch to Active view
        logger.info("Treatment Dashboard now showing Active view (monitoring)")

        # Optional: Disable Start Treatment button to prevent re-clicks
        self.treatment_setup_widget.ready_button.setEnabled(False)
        self.treatment_setup_widget.ready_button.setText("Treatment Active")

    def _on_line_protocol_ready(self, protocol: Any) -> None:
        """
        Handle protocol ready signal from LineProtocolBuilderWidget.

        Executes the line-based protocol using the LineBasedProtocolEngine.

        Args:
            protocol: LineBasedProtocol ready for execution
        """
        from core.protocol_line import LineBasedProtocol

        if not isinstance(protocol, LineBasedProtocol):
            logger.error(f"Invalid protocol type: {type(protocol)}")
            QMessageBox.critical(
                self, "Protocol Error", "Invalid protocol format. Please rebuild the protocol."
            )
            return

        logger.info(f"Protocol ready for execution: {protocol.protocol_name}")
        logger.info(f"  - Lines: {len(protocol.lines)}")
        logger.info(f"  - Loop count: {protocol.loop_count}")
        logger.info(f"  - Total duration: {protocol.calculate_total_duration():.1f}s")

        # Log detailed line information
        for line in protocol.lines:
            logger.info(f"  - {line.get_summary()}")

        # Confirm execution with user
        reply = QMessageBox.question(
            self,
            "Execute Protocol",
            f"Execute protocol '{protocol.protocol_name}'?\n\n"
            f"Protocol Details:\n"
            f"  • Lines: {len(protocol.lines)}\n"
            f"  • Loop count: {protocol.loop_count}\n"
            f"  • Total duration: {protocol.calculate_total_duration():.1f}s\n\n"
            f"[!] Safety checks will be performed before execution starts.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            logger.info("Protocol execution cancelled by user")
            return

        # Execute protocol asynchronously using QRunnable pattern

        # Store protocol for execution
        self._current_executing_protocol = protocol

        # Create worker for async execution
        worker = LineProtocolWorker(self.line_protocol_engine, protocol)
        worker.signals.finished.connect(self._on_protocol_execution_finished)
        worker.signals.error.connect(self._on_protocol_execution_error)

        # Submit to thread pool
        QThreadPool.globalInstance().start(worker)
        logger.info("Protocol execution started in worker thread")

    def _on_protocol_execution_finished(self, success: bool, message: str) -> None:
        """Handle protocol execution completion."""
        if success:
            QMessageBox.information(self, "Protocol Complete", message)
        else:
            QMessageBox.critical(self, "Protocol Failed", message)

    def _on_protocol_execution_error(self, error_msg: str) -> None:
        """Handle protocol execution error."""
        logger.error(f"Protocol execution error: {error_msg}")
        QMessageBox.critical(self, "Execution Error", f"Protocol execution failed:\n{error_msg}")

    def _on_protocol_line_start(self, line_number: int, loop_iteration: int) -> None:
        """Callback when protocol line starts execution."""
        logger.info(f"Line {line_number} started (Loop {loop_iteration})")
        # Update UI status (could show in status bar or dedicated widget)
        self.statusBar().showMessage(f"Executing Line {line_number} (Loop {loop_iteration})", 2000)

    def _on_protocol_line_complete(self, line_number: int, loop_iteration: int) -> None:
        """Callback when protocol line completes execution."""
        logger.debug(f"Line {line_number} completed (Loop {loop_iteration})")

    def _on_protocol_progress_update(self, progress: float) -> None:
        """Callback for protocol execution progress (0.0 to 1.0)."""
        # Update progress in UI (could use progress bar)
        percent = int(progress * 100)
        logger.debug(f"Protocol progress: {percent}%")
        # Could update status bar or progress widget here
        if percent % 10 == 0:  # Log every 10%
            logger.info(f"Protocol execution: {percent}% complete")

    def _on_protocol_state_change(self, state) -> None:
        """Callback when protocol execution state changes."""
        from core.line_protocol_engine import ExecutionState

        logger.info(f"Protocol execution state changed to: {state.value}")

        if state == ExecutionState.RUNNING:
            self.statusBar().showMessage("Protocol execution started", 3000)
        elif state == ExecutionState.PAUSED:
            self.statusBar().showMessage("Protocol execution paused", 0)
        elif state == ExecutionState.STOPPED:
            self.statusBar().showMessage("Protocol execution stopped", 5000)
        elif state == ExecutionState.COMPLETED:
            self.statusBar().showMessage("Protocol execution completed successfully", 5000)
        elif state == ExecutionState.ERROR:
            self.statusBar().showMessage("Protocol execution failed", 5000)

    def _on_global_estop_clicked(self) -> None:
        """Handle global E-STOP button click."""
        logger.critical("GLOBAL E-STOP ACTIVATED BY USER")
        if self.safety_manager:
            self.safety_manager.trigger_emergency_stop()
            # Disable E-Stop button after activation
            self.global_estop_btn.setEnabled(False)
            self.global_estop_btn.setText("[STOP] E-STOP ACTIVE")

    def _on_test_all_clicked(self) -> None:
        """Run diagnostic test on all hardware components."""
        logger.info("Starting hardware diagnostic test...")

        # Run tests for each component
        test_results = {
            "camera": self._test_camera(),
            "actuator": self._test_actuator(),
            "laser": self._test_laser(),
            "gpio": self._test_gpio(),
        }

        # Show results dialog
        from ui.dialogs import HardwareTestDialog

        dialog = HardwareTestDialog(test_results, parent=self)
        dialog.exec()

        logger.info("Hardware diagnostic test completed")

    def _test_camera(self) -> dict:
        """
        Test camera system.

        Returns:
            Dict with name, passed status, and details list
        """
        result = {"name": "[CAM] Camera System", "passed": False, "details": []}

        if hasattr(self, "camera_live_view") and self.camera_live_view:
            if self.camera_live_view.is_connected:
                result["passed"] = True
                result["details"].append("Camera connected")

                # Add FPS if streaming
                if self.camera_live_view.is_streaming:
                    fps = self.camera_live_view.current_fps
                    result["details"].append(f"Streaming at {fps:.1f} FPS")
                else:
                    result["details"].append("Not streaming (OK)")

                # Add controller info if available
                if (
                    hasattr(self.camera_live_view, "camera_controller")
                    and self.camera_live_view.camera_controller
                ):
                    controller = self.camera_live_view.camera_controller
                    if hasattr(controller, "camera") and controller.camera:
                        try:
                            model = controller.camera.get_model()
                            result["details"].append(f"Model: {model}")
                        except Exception:
                            pass
            else:
                result["details"].append("Camera not connected")
        else:
            result["details"].append("Camera widget not initialized")

        return result

    def _test_actuator(self) -> dict:
        """
        Test linear actuator system.

        Returns:
            Dict with name, passed status, and details list
        """
        result = {"name": "[ACT] Linear Actuator", "passed": False, "details": []}

        if hasattr(self, "actuator_connection_widget") and self.actuator_connection_widget:
            if (
                hasattr(self.actuator_connection_widget, "is_connected")
                and self.actuator_connection_widget.is_connected
            ):
                result["passed"] = True
                result["details"].append("Actuator connected")

                # Add homing status
                if (
                    hasattr(self.actuator_connection_widget, "is_homed")
                    and self.actuator_connection_widget.is_homed
                ):
                    result["details"].append("Homed and ready")
                else:
                    result["details"].append("Not homed (requires homing)")

                # Add position if available
                if hasattr(self.actuator_connection_widget, "current_position_um"):
                    pos_mm = self.actuator_connection_widget.current_position_um / 1000.0
                    result["details"].append(f"Position: {pos_mm:.2f} mm")

                # Add range if available
                if hasattr(self.actuator_connection_widget, "max_position_um"):
                    max_mm = self.actuator_connection_widget.max_position_um / 1000.0
                    result["details"].append(f"Range: 0-{max_mm:.1f} mm")
            else:
                result["details"].append("Actuator not connected")
        else:
            result["details"].append("Actuator widget not initialized")

        return result

    def _test_laser(self) -> dict:
        """
        Test laser systems (aiming + treatment).

        Returns:
            Dict with name, passed status, and details list
        """
        result = {"name": "[LSR] Laser Systems", "passed": False, "details": []}

        if hasattr(self, "laser_widget") and self.laser_widget:
            # Check aiming laser
            aiming_connected = False
            treatment_connected = False

            if hasattr(self.laser_widget, "aiming_laser") and self.laser_widget.aiming_laser:
                if (
                    hasattr(self.laser_widget.aiming_laser, "is_connected")
                    and self.laser_widget.aiming_laser.is_connected
                ):
                    aiming_connected = True
                    result["details"].append("Aiming laser: Connected")
                else:
                    result["details"].append("Aiming laser: Not connected")
            else:
                result["details"].append("Aiming laser: Not initialized")

            # Check treatment laser
            if hasattr(self.laser_widget, "treatment_laser") and self.laser_widget.treatment_laser:
                if (
                    hasattr(self.laser_widget.treatment_laser, "is_connected")
                    and self.laser_widget.treatment_laser.is_connected
                ):
                    treatment_connected = True
                    result["details"].append("Treatment laser: Connected")
                else:
                    result["details"].append("Treatment laser: Not connected")
            else:
                result["details"].append("Treatment laser: Not initialized")

            # Pass if at least one laser is connected
            result["passed"] = aiming_connected or treatment_connected
        else:
            result["details"].append("Laser widget not initialized")

        return result

    def _test_gpio(self) -> dict:
        """
        Test GPIO system (laser spot smoothing module + photodiode laser pickoff measurement).

        Returns:
            Dict with name, passed status, and details list
        """
        result = {"name": "[CONN] GPIO Diagnostics", "passed": False, "details": []}

        if hasattr(self, "safety_widget") and self.safety_widget:
            if hasattr(self, "gpio_widget") and self.gpio_widget:
                gpio_widget = self.gpio_widget

                # Check GPIO connection
                if hasattr(gpio_widget, "is_connected") and gpio_widget.is_connected:
                    result["passed"] = True
                    result["details"].append("GPIO controller connected")

                    # Check laser spot smoothing module
                    if hasattr(gpio_widget, "smoothing_motor_voltage"):
                        voltage = gpio_widget.smoothing_motor_voltage
                        result["details"].append(f"Smoothing motor: {voltage:.2f}V")

                    # Check photodiode laser pickoff measurement
                    if hasattr(gpio_widget, "photodiode_voltage"):
                        voltage = gpio_widget.photodiode_voltage
                        result["details"].append(
                            f"photodiode laser pickoff measurement: {voltage:.2f}V"
                        )

                    # Check interlocks
                    if (
                        hasattr(self.safety_widget, "safety_manager")
                        and self.safety_widget.safety_manager
                    ):
                        result["details"].append("Safety interlocks active")
                else:
                    result["details"].append("GPIO controller not connected")
            else:
                result["details"].append("GPIO widget not initialized")
        else:
            result["details"].append("Safety widget not initialized")

        return result

    def _on_pause_protocol_clicked(self) -> None:
        """Handle Pause Protocol button click."""
        logger.info("Pausing treatment protocol...")
        if self.protocol_engine and hasattr(self.protocol_engine, "pause"):
            self.protocol_engine.pause()
            self.pause_protocol_btn.setEnabled(False)
            self.resume_protocol_btn.setEnabled(True)
            logger.info("Protocol paused")
        else:
            logger.warning("Cannot pause: Protocol engine not available or pause not implemented")

    def _on_resume_protocol_clicked(self) -> None:
        """Handle Resume Protocol button click."""
        logger.info("Resuming treatment protocol...")
        if self.protocol_engine and hasattr(self.protocol_engine, "resume"):
            self.protocol_engine.resume()
            self.pause_protocol_btn.setEnabled(True)
            self.resume_protocol_btn.setEnabled(False)
            logger.info("Protocol resumed")
        else:
            logger.warning("Cannot resume: Protocol engine not available or resume not implemented")

    def _update_master_safety_indicator(self, state: Any) -> None:
        """
        Update master safety indicator in status bar.

        Args:
            state: SafetyState enum value (SAFE, UNSAFE, EMERGENCY_STOP)
        """
        if state == SafetyState.SAFE:
            text = "SYSTEM SAFE"
            color = "#4CAF50"  # Green
            logger.debug("Master safety indicator: SAFE")
        elif state == SafetyState.UNSAFE:
            text = "SYSTEM UNSAFE"
            color = "#FF9800"  # Orange
            logger.warning("Master safety indicator: UNSAFE")
        else:  # EMERGENCY_STOP
            text = "EMERGENCY STOP"
            color = "#F44336"  # Red
            logger.critical("Master safety indicator: E-STOP")

        self.master_safety_indicator.setText(text)
        self.master_safety_indicator.setStyleSheet(
            f"QLabel {{ background-color: {color}; color: white; "
            f"padding: 8px 16px; font-weight: bold; font-size: 14px; "
            f"border-radius: 3px; }}"
        )

    def update_camera_status(self, connected: bool) -> None:
        """Update camera connection status indicator."""
        if connected:
            self.camera_status.setText("●")
            self.camera_status.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green dot
            self.camera_status.setToolTip("Camera: Connected")
        else:
            self.camera_status.setText("●")
            self.camera_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot
            self.camera_status.setToolTip("Camera: Disconnected")

        # Update hardware tab header
        self._update_camera_header_status(connected)

    def update_laser_status(self, connected: bool) -> None:
        """Update laser connection status indicator."""
        # Update status label if it exists (may be removed in some UI configurations)
        if hasattr(self, 'laser_status'):
            if connected:
                self.laser_status.setText("●")
                self.laser_status.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green dot
                self.laser_status.setToolTip("Laser: Connected")
            else:
                self.laser_status.setText("●")
                self.laser_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot
                self.laser_status.setToolTip("Laser: Disconnected")

        # Hardware tab headers removed (individual widget controls used instead)
        # self._update_laser_header_status(connected)

    def update_actuator_status(self, connected: bool) -> None:
        """Update actuator connection status indicator."""
        # Update status label if it exists (may be removed in some UI configurations)
        if hasattr(self, 'actuator_status'):
            if connected:
                self.actuator_status.setText("●")
                self.actuator_status.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green dot
                self.actuator_status.setToolTip("Actuator: Connected")
            else:
                self.actuator_status.setText("●")
                self.actuator_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot
                self.actuator_status.setToolTip("Actuator: Disconnected")

        # Hardware tab headers removed (individual widget controls used instead)
        # self._update_actuator_header_status(connected)

    def _disable_dev_mode_on_close(self) -> None:
        """Auto-disable developer mode on application close (safety default)."""
        if hasattr(self, "dev_mode_action") and self.dev_mode_action.isChecked():
            logger.info("Auto-disabling developer mode on application close")
            self.dev_mode_action.setChecked(False)

    def _log_shutdown_event(self) -> None:
        """Log system shutdown event."""
        if hasattr(self, "event_logger") and self.event_logger:
            self.event_logger.log_system_event(
                EventType.SYSTEM_SHUTDOWN, "TOSCA system shutting down", EventSeverity.INFO
            )

    def _stop_safety_watchdog(self) -> None:
        """Stop safety watchdog before GPIO disconnect."""
        if hasattr(self, "safety_watchdog") and self.safety_watchdog:
            self.safety_watchdog.stop()
            logger.info("Safety watchdog stopped")

    def _disconnect_hardware(self, controller_name: str, controller: Any) -> None:
        """
        Generic hardware disconnect with error handling.

        Args:
            controller_name: Name for logging (e.g., "camera", "actuator")
            controller: Hardware controller instance
        """
        if not hasattr(self, controller_name) or controller is None:
            return

        if not controller.is_connected:
            return

        logger.info(f"Auto-disconnecting {controller_name} on shutdown")
        try:
            # Special handling for camera (stop streaming first)
            if controller_name == "camera_controller" and controller.is_streaming:
                controller.stop_streaming()
            controller.disconnect()
        except Exception as e:
            logger.warning(f"Error during {controller_name} auto-disconnect: {e}")

    def _rebuild_all_stylesheets(self) -> None:
        """
        Rebuild all widget stylesheets after theme change.

        Called by unified_header when user toggles theme.
        Re-evaluates all f-string color interpolations with new theme values.
        """
        from ui.design_tokens import Colors

        # Rebuild unified header (it handles its own rebuild)
        if hasattr(self, "unified_header") and self.unified_header:
            self.unified_header._rebuild_stylesheets()

        # Rebuild main window background
        self.setStyleSheet(f"background-color: {Colors.BACKGROUND};")

        # Rebuild tab widget
        if hasattr(self, "tabs") and self.tabs:
            self.tabs.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {Colors.BORDER_DEFAULT};
                    background-color: {Colors.BACKGROUND};
                }}
                QTabBar::tab {{
                    background-color: {Colors.PANEL};
                    color: {Colors.TEXT_PRIMARY};
                    padding: 8px 16px;
                    border: 1px solid {Colors.BORDER_DEFAULT};
                }}
                QTabBar::tab:selected {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                }}
            """)

        # Note: Individual widgets will need their own stylesheet rebuild methods
        # This is a simplified implementation - full theme support requires:
        # 1. Each widget implements _rebuild_stylesheets() method
        # 2. Main window calls widget._rebuild_stylesheets() for each child
        # 3. Widgets re-evaluate all f-string color interpolations

        logger.info("Main window stylesheets rebuilt for theme change")

    def _cleanup_all_widgets(self) -> None:
        """Clean up all widget resources."""
        # Camera
        if hasattr(self, "camera_live_view") and self.camera_live_view:
            self.camera_live_view.cleanup()

        # NEW Treatment widgets
        if hasattr(self, "unified_session_setup") and self.unified_session_setup:
            self.unified_session_setup.cleanup()
        if hasattr(self, "protocol_steps_display") and self.protocol_steps_display:
            self.protocol_steps_display.cleanup()
        # OLD: active_treatment_widget removed in redesign

        # Hardware & Diagnostics
        if hasattr(self, "laser_widget") and self.laser_widget:
            self.laser_widget.cleanup()
        if hasattr(self, "safety_widget") and self.safety_widget:
            self.safety_widget.cleanup()

        # Modular GPIO widgets
        if hasattr(self, "gpio_widget") and self.gpio_widget:
            self.gpio_widget.cleanup()
        if hasattr(self, "footpedal_widget") and self.footpedal_widget:
            self.footpedal_widget.cleanup()
        if hasattr(self, "photodiode_widget") and self.photodiode_widget:
            self.photodiode_widget.cleanup()
        if hasattr(self, "smoothing_module_widget") and self.smoothing_module_widget:
            self.smoothing_module_widget.cleanup()

        # Protocol Builder
        if hasattr(self, "actuator_connection_widget") and self.actuator_connection_widget:
            self.actuator_connection_widget.cleanup()

    def _close_database(self) -> None:
        """Close database connection."""
        if hasattr(self, "db_manager") and self.db_manager:
            self.db_manager.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Application closing, cleaning up resources...")

        # Safety: Disable dev mode, log shutdown, stop watchdog
        self._disable_dev_mode_on_close()
        self._log_shutdown_event()
        self._stop_safety_watchdog()

        # Disconnect all hardware controllers
        self._disconnect_hardware("camera_controller", self.camera_controller)
        self._disconnect_hardware("actuator_controller", self.actuator_controller)
        self._disconnect_hardware("gpio_controller", self.gpio_controller)
        self._disconnect_hardware("laser_controller", self.laser_controller)
        self._disconnect_hardware("tec_controller", self.tec_controller)

        # Cleanup widgets and database
        self._cleanup_all_widgets()
        self._close_database()

        logger.info("Cleanup complete")
        event.accept()
