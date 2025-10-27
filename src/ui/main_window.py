"""
Main application window with tab-based navigation.
"""

import logging
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.event_logger import EventLogger, EventSeverity, EventType
from core.protocol_engine import ProtocolEngine
from core.safety import SafetyManager
from core.safety_watchdog import SafetyWatchdog
from core.session_manager import SessionManager
from database.db_manager import DatabaseManager
from ui.widgets.camera_widget import CameraWidget
from ui.widgets.safety_widget import SafetyWidget
from ui.widgets.subject_widget import SubjectWidget
from ui.widgets.treatment_widget import TreatmentWidget

logger = logging.getLogger(__name__)


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

        self.setWindowTitle("TOSCA Laser Control System")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize database and session managers
        self.db_manager = DatabaseManager()
        self.db_manager.initialize()
        self.session_manager = SessionManager(self.db_manager)
        self.event_logger = EventLogger(self.db_manager)

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

        self._init_ui()
        self._init_toolbar()
        self._init_status_bar()

        logger.info("Main window initialized")

    def _init_ui(self) -> None:
        """Initialize main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel("TOSCA Laser Control System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.subject_widget = SubjectWidget()
        self.subject_widget.set_managers(self.db_manager, self.session_manager)
        self.subject_widget.session_started.connect(self._on_session_started)
        self.tabs.addTab(self.subject_widget, "Subject Selection")

        self.camera_widget = CameraWidget()
        self.tabs.addTab(self.camera_widget, "Camera/Alignment")

        # Initialize camera controller (if available)
        try:
            from hardware.camera_controller import CameraController

            self.camera_controller = CameraController()
            self.camera_widget.set_camera_controller(self.camera_controller)
            logger.info("Camera controller initialized")
        except ImportError as e:
            logger.warning(f"Camera controller not available: {e}")
            self.camera_controller = None

        self.treatment_widget = TreatmentWidget()
        self.tabs.addTab(self.treatment_widget, "Treatment Control")

        # Connect dev mode signal to widgets (after widgets are created)
        self.dev_mode_changed.connect(self.camera_widget.set_dev_mode)
        self.dev_mode_changed.connect(self.treatment_widget.set_dev_mode)

        # Connect dev mode to motor widget
        if hasattr(self.treatment_widget, "motor_widget"):
            self.dev_mode_changed.connect(self.treatment_widget.motor_widget.set_dev_mode)

        self.safety_widget = SafetyWidget(db_manager=self.db_manager)
        self.tabs.addTab(self.safety_widget, "Safety Status")

        # Initialize safety manager
        self.safety_manager = SafetyManager()
        self._connect_safety_system()
        logger.info("Safety manager initialized and connected")

        # Initialize protocol engine with hardware controllers
        self._init_protocol_engine()

        # Connect event logger to widgets
        self._connect_event_logger()

    def _init_toolbar(self) -> None:
        """Initialize global toolbar with critical controls."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Global E-STOP button (always accessible)
        self.global_estop_btn = QPushButton("🛑 EMERGENCY STOP")
        self.global_estop_btn.setMinimumHeight(40)
        self.global_estop_btn.setStyleSheet(
            "QPushButton { background-color: #d32f2f; color: white; "
            "padding: 8px 16px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        self.global_estop_btn.setToolTip("Emergency stop - immediately disable treatment laser")
        self.global_estop_btn.clicked.connect(self._on_global_estop_clicked)
        toolbar.addWidget(self.global_estop_btn)

        toolbar.addSeparator()

        # Connect All button
        self.connect_all_btn = QPushButton("🔌 Connect All")
        self.connect_all_btn.setMinimumHeight(35)
        self.connect_all_btn.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; "
            "padding: 6px 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1565C0; }"
        )
        self.connect_all_btn.setToolTip("Connect to all hardware (Camera, Laser, Actuator, GPIO)")
        self.connect_all_btn.clicked.connect(self._on_connect_all_clicked)
        toolbar.addWidget(self.connect_all_btn)

        # Disconnect All button
        self.disconnect_all_btn = QPushButton("Disconnect All")
        self.disconnect_all_btn.setMinimumHeight(35)
        self.disconnect_all_btn.setEnabled(False)
        self.disconnect_all_btn.setToolTip("Disconnect from all hardware")
        self.disconnect_all_btn.clicked.connect(self._on_disconnect_all_clicked)
        toolbar.addWidget(self.disconnect_all_btn)

        toolbar.addSeparator()

        # Pause Protocol button
        self.pause_protocol_btn = QPushButton("⏸ Pause")
        self.pause_protocol_btn.setMinimumHeight(35)
        self.pause_protocol_btn.setEnabled(False)
        self.pause_protocol_btn.setToolTip("Pause current treatment protocol")
        self.pause_protocol_btn.clicked.connect(self._on_pause_protocol_clicked)
        toolbar.addWidget(self.pause_protocol_btn)

        # Resume Protocol button
        self.resume_protocol_btn = QPushButton("▶ Resume")
        self.resume_protocol_btn.setMinimumHeight(35)
        self.resume_protocol_btn.setEnabled(False)
        self.resume_protocol_btn.setToolTip("Resume paused treatment protocol")
        self.resume_protocol_btn.clicked.connect(self._on_resume_protocol_clicked)
        toolbar.addWidget(self.resume_protocol_btn)

        logger.info("Global toolbar initialized")

    def _init_status_bar(self) -> None:
        """Initialize status bar with connection indicators."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        status_layout = QHBoxLayout()

        # Dev mode toggle
        self.dev_mode_check = QCheckBox("Dev Mode")
        self.dev_mode_check.setToolTip(
            "Enable developer mode to bypass session management and customize save paths"
        )
        self.dev_mode_check.stateChanged.connect(self._on_dev_mode_changed)
        status_layout.addWidget(self.dev_mode_check)
        status_layout.addWidget(QLabel("|"))

        # Connection status
        self.camera_status = QLabel("Camera: Not Connected")
        self.laser_status = QLabel("Laser: Not Connected")
        self.actuator_status = QLabel("Actuator: Not Connected")

        status_layout.addWidget(self.camera_status)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.laser_status)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.actuator_status)
        status_layout.addStretch()

        # Close program button
        self.close_btn = QPushButton("Close Program")
        self.close_btn.setStyleSheet(
            "QPushButton { background-color: #F44336; color: white; "
            "padding: 5px 10px; font-weight: bold; }"
            "QPushButton:hover { background-color: #D32F2F; }"
        )
        self.close_btn.clicked.connect(self._on_close_program)
        status_layout.addWidget(self.close_btn)

        status_layout.addWidget(QLabel("|"))

        # Master Safety Indicator (always visible, right side)
        self.master_safety_indicator = QLabel("SYSTEM SAFE")
        self.master_safety_indicator.setStyleSheet(
            "QLabel { background-color: #4CAF50; color: white; "
            "padding: 8px 16px; font-weight: bold; font-size: 14px; "
            "border-radius: 3px; }"
        )
        self.master_safety_indicator.setToolTip(
            "Master safety status - reflects all interlock conditions"
        )
        status_layout.addWidget(self.master_safety_indicator)

        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_bar.addWidget(status_widget)

        # Connect safety manager to master indicator
        if hasattr(self, "safety_manager") and self.safety_manager:
            self.safety_manager.safety_state_changed.connect(self._update_master_safety_indicator)
            logger.info("Master safety indicator connected to SafetyManager")

    def _on_close_program(self) -> None:
        """Handle close program button click."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit TOSCA?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("User initiated program exit via Close button")
            self.close()

    def _on_dev_mode_changed(self, state: int) -> None:
        """Handle dev mode checkbox change."""
        dev_mode = bool(state)
        logger.info(f"Dev mode {'enabled' if dev_mode else 'disabled'}")
        self.dev_mode_changed.emit(dev_mode)

        # Update UI to reflect dev mode
        if dev_mode:
            self.setWindowTitle("TOSCA Laser Control System - DEVELOPER MODE")
            self.subject_widget.setEnabled(False)  # Disable subject selection in dev mode
            logger.warning(
                "Developer mode enabled - session management bypassed for UI convenience. "
                "Safety interlocks remain ACTIVE and enforced. "
                "For hardware experimentation, use a dedicated test application with "
                "TestSafetyManager."
            )
        else:
            self.setWindowTitle("TOSCA Laser Control System")
            self.subject_widget.setEnabled(True)

    def _connect_safety_system(self) -> None:
        """Connect safety system components."""
        # Connect safety manager to safety widget for display
        self.safety_widget.set_safety_manager(self.safety_manager)
        logger.info("Safety manager connected to safety widget")

        # Connect to GPIO widget's connection status signal
        # Controller doesn't exist yet - created when user clicks Connect
        # So we connect to widget's forwarding signal instead
        if hasattr(self.safety_widget, "gpio_widget") and self.safety_widget.gpio_widget:
            gpio_widget = self.safety_widget.gpio_widget
            # Connect to GPIO widget's stable signal (not controller's)
            gpio_widget.gpio_connection_changed.connect(self._on_gpio_connection_changed)
            logger.info("Main window connected to GPIO widget connection signal")

        # Connect safety manager to treatment widgets
        # Laser widget will check safety manager before enabling
        if hasattr(self.treatment_widget, "laser_widget"):
            laser_widget = self.treatment_widget.laser_widget
            # Store reference to safety manager in laser widget
            laser_widget.safety_manager = self.safety_manager
            logger.info("Safety manager connected to laser widget")

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
        if hasattr(self.treatment_widget, "laser_widget"):
            laser_widget = self.treatment_widget.laser_widget
            if hasattr(laser_widget, "controller") and laser_widget.controller:
                if laser_widget.controller.is_connected:
                    logger.critical("Disabling treatment laser due to watchdog timeout")
                    laser_widget.controller.set_output(False)
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
            gpio_widget = self.safety_widget.gpio_widget
            if gpio_widget and gpio_widget.controller:
                # Connect GPIO safety interlock to safety manager
                try:
                    gpio_widget.controller.safety_interlock_changed.connect(
                        self.safety_manager.set_gpio_interlock_status
                    )
                    logger.info("GPIO safety interlocks connected to safety manager")
                except RuntimeError:
                    # Signal already connected, ignore
                    pass

                # Attach GPIO controller to watchdog
                self.safety_watchdog.gpio_controller = gpio_widget.controller
                logger.info("GPIO controller attached to safety watchdog")

                # Connect watchdog signals if not already connected
                try:
                    self.safety_watchdog.heartbeat_failed.connect(
                        lambda msg: logger.error(f"Watchdog heartbeat failed: {msg}")
                    )
                    self.safety_watchdog.watchdog_timeout_detected.connect(
                        self._handle_watchdog_timeout
                    )
                except RuntimeError:
                    # Signals already connected, ignore
                    pass

                # Start heartbeat - CRITICAL for Arduino stability
                if self.safety_watchdog.start():
                    logger.info("Safety watchdog started (500ms heartbeat, 1000ms timeout)")
                else:
                    logger.error("CRITICAL: Safety watchdog failed to start!")
        else:
            # GPIO disconnected - stop heartbeat
            self.safety_watchdog.stop()
            logger.info("Safety watchdog stopped (GPIO disconnected)")

    def _init_protocol_engine(self) -> None:
        """Initialize protocol engine and wire to hardware controllers."""
        # Get controller references from widgets
        # Note: Controllers may be None if widgets haven't connected to hardware yet
        laser_controller = None
        actuator_controller = None

        if hasattr(self.treatment_widget, "laser_widget"):
            laser_widget = self.treatment_widget.laser_widget
            laser_controller = getattr(laser_widget, "controller", None)

        if hasattr(self.treatment_widget, "actuator_widget"):
            actuator_widget = self.treatment_widget.actuator_widget
            actuator_controller = getattr(actuator_widget, "controller", None)

        # Initialize protocol engine with available controllers
        self.protocol_engine = ProtocolEngine(
            laser_controller=laser_controller,
            actuator_controller=actuator_controller,
            safety_manager=self.safety_manager,
        )

        # Pass protocol engine to treatment widget for UI integration
        if hasattr(self.treatment_widget, "set_protocol_engine"):
            self.treatment_widget.set_protocol_engine(self.protocol_engine)

        logger.info(
            f"Protocol engine initialized (laser: {laser_controller is not None}, "
            f"actuator: {actuator_controller is not None}, "
            f"safety: {self.safety_manager is not None})"
        )

    def _connect_event_logger(self) -> None:
        """Connect event logger to system components."""
        # Connect session manager signals
        self.session_manager.session_started.connect(self._on_event_logger_session_started)
        self.session_manager.session_ended.connect(self._on_event_logger_session_ended)

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
        Handle session started event.

        Args:
            session_id: ID of started session
        """
        logger.info(f"Session {session_id} started - updating safety system")
        # Mark session as valid for safety system
        self.safety_manager.set_session_valid(True)

    def _on_global_estop_clicked(self) -> None:
        """Handle global E-STOP button click."""
        logger.critical("GLOBAL E-STOP ACTIVATED BY USER")
        if self.safety_manager:
            self.safety_manager.trigger_emergency_stop()
            # Disable E-Stop button after activation
            self.global_estop_btn.setEnabled(False)
            self.global_estop_btn.setText("🛑 E-STOP ACTIVE")

    def _on_connect_all_clicked(self) -> None:
        """Handle Connect All button click."""
        logger.info("Connecting to all hardware...")

        # Connect GPIO (Safety tab)
        if hasattr(self.safety_widget, "gpio_widget") and self.safety_widget.gpio_widget:
            gpio_widget = self.safety_widget.gpio_widget
            if not gpio_widget.is_connected:
                logger.info("Connecting GPIO...")
                gpio_widget._on_connect_clicked()

        # Connect Camera
        if hasattr(self.camera_widget, "connect_camera"):
            logger.info("Connecting Camera...")
            self.camera_widget.connect_camera()

        # Connect Laser (Treatment tab)
        if hasattr(self.treatment_widget, "laser_widget"):
            laser_widget = self.treatment_widget.laser_widget
            if hasattr(laser_widget, "is_connected") and not laser_widget.is_connected:
                logger.info("Connecting Laser...")
                if hasattr(laser_widget, "_on_connect_clicked"):
                    laser_widget._on_connect_clicked()

        # Connect Actuator (Treatment tab)
        if hasattr(self.treatment_widget, "actuator_widget"):
            actuator_widget = self.treatment_widget.actuator_widget
            if hasattr(actuator_widget, "is_connected") and not actuator_widget.is_connected:
                logger.info("Connecting Actuator...")
                if hasattr(actuator_widget, "_on_connect_clicked"):
                    actuator_widget._on_connect_clicked()

        # Update button states
        self.connect_all_btn.setEnabled(False)
        self.disconnect_all_btn.setEnabled(True)
        logger.info("Connect All completed")

    def _on_disconnect_all_clicked(self) -> None:
        """Handle Disconnect All button click."""
        logger.info("Disconnecting from all hardware...")

        # Disconnect GPIO
        if hasattr(self.safety_widget, "gpio_widget") and self.safety_widget.gpio_widget:
            gpio_widget = self.safety_widget.gpio_widget
            if gpio_widget.is_connected:
                logger.info("Disconnecting GPIO...")
                gpio_widget._on_disconnect_clicked()

        # Disconnect Camera
        if hasattr(self.camera_widget, "disconnect_camera"):
            logger.info("Disconnecting Camera...")
            self.camera_widget.disconnect_camera()

        # Disconnect Laser
        if hasattr(self.treatment_widget, "laser_widget"):
            laser_widget = self.treatment_widget.laser_widget
            if hasattr(laser_widget, "is_connected") and laser_widget.is_connected:
                logger.info("Disconnecting Laser...")
                if hasattr(laser_widget, "_on_disconnect_clicked"):
                    laser_widget._on_disconnect_clicked()

        # Disconnect Actuator
        if hasattr(self.treatment_widget, "actuator_widget"):
            actuator_widget = self.treatment_widget.actuator_widget
            if hasattr(actuator_widget, "is_connected") and actuator_widget.is_connected:
                logger.info("Disconnecting Actuator...")
                if hasattr(actuator_widget, "_on_disconnect_clicked"):
                    actuator_widget._on_disconnect_clicked()

        # Update button states
        self.connect_all_btn.setEnabled(True)
        self.disconnect_all_btn.setEnabled(False)
        logger.info("Disconnect All completed")

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
        from core.safety import SafetyState

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Application closing, cleaning up resources...")

        # Log system shutdown
        if hasattr(self, "event_logger") and self.event_logger:
            self.event_logger.log_system_event(
                EventType.SYSTEM_SHUTDOWN, "TOSCA system shutting down", EventSeverity.INFO
            )

        # Stop safety watchdog FIRST (before GPIO disconnects)
        # CRITICAL: Must stop heartbeat before disconnecting GPIO
        if hasattr(self, "safety_watchdog") and self.safety_watchdog:
            self.safety_watchdog.stop()
            logger.info("Safety watchdog stopped")

        # Cleanup camera
        if hasattr(self, "camera_widget") and self.camera_widget:
            self.camera_widget.cleanup()

        # Cleanup treatment (actuator + laser)
        if hasattr(self, "treatment_widget") and self.treatment_widget:
            self.treatment_widget.cleanup()

        # Cleanup safety (GPIO)
        if hasattr(self, "safety_widget") and self.safety_widget:
            self.safety_widget.cleanup()

        # Cleanup database
        if hasattr(self, "db_manager") and self.db_manager:
            self.db_manager.close()

        logger.info("Cleanup complete")
        event.accept()
