"""
Main application window with tab-based navigation.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.event_logger import EventLogger, EventSeverity, EventType
from core.protocol_engine import ProtocolEngine
from core.safety import SafetyManager
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
        logger.info("Database, session, and event logger initialized")

        # Log system startup
        self.event_logger.log_system_event(
            EventType.SYSTEM_STARTUP, "TOSCA system started", EventSeverity.INFO
        )

        self._init_ui()
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

        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_bar.addWidget(status_widget)

    def _on_dev_mode_changed(self, state: int) -> None:
        """Handle dev mode checkbox change."""
        dev_mode = bool(state)
        logger.info(f"Dev mode {'enabled' if dev_mode else 'disabled'}")
        self.dev_mode_changed.emit(dev_mode)

        # Update UI to reflect dev mode
        if dev_mode:
            self.setWindowTitle("TOSCA Laser Control System - DEVELOPER MODE")
            self.subject_widget.setEnabled(False)  # Disable subject selection in dev mode
            # In dev mode, bypass session requirement for safety
            self.safety_manager.set_session_valid(True)
        else:
            self.setWindowTitle("TOSCA Laser Control System")
            self.subject_widget.setEnabled(True)
            # In normal mode, require valid session
            self.safety_manager.set_session_valid(False)

    def _connect_safety_system(self) -> None:
        """Connect safety system components."""
        # Connect safety manager to safety widget for display
        self.safety_widget.set_safety_manager(self.safety_manager)
        logger.info("Safety manager connected to safety widget")

        # Connect GPIO safety interlock to safety manager
        if hasattr(self.safety_widget, "gpio_widget") and self.safety_widget.gpio_widget:
            gpio_widget = self.safety_widget.gpio_widget
            if hasattr(gpio_widget, "controller") and gpio_widget.controller:
                gpio_widget.controller.safety_interlock_changed.connect(
                    self.safety_manager.set_gpio_interlock_status
                )
                logger.info("GPIO safety interlocks connected to safety manager")

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
            laser_controller=laser_controller, actuator_controller=actuator_controller
        )

        # Pass protocol engine to treatment widget for UI integration
        if hasattr(self.treatment_widget, "set_protocol_engine"):
            self.treatment_widget.set_protocol_engine(self.protocol_engine)

        logger.info(
            f"Protocol engine initialized (laser: {laser_controller is not None}, "
            f"actuator: {actuator_controller is not None})"
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

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Application closing, cleaning up resources...")

        # Log system shutdown
        if hasattr(self, "event_logger") and self.event_logger:
            self.event_logger.log_system_event(
                EventType.SYSTEM_SHUTDOWN, "TOSCA system shutting down", EventSeverity.INFO
            )

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
