"""
Main application window with tab-based navigation.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
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

from ui.widgets.camera_widget import CameraWidget
from ui.widgets.protocol_builder_widget import ProtocolBuilderWidget
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

        self.protocol_builder_widget = ProtocolBuilderWidget()
        self.tabs.addTab(self.protocol_builder_widget, "Protocol Builder")

        self.safety_widget = SafetyWidget()
        self.tabs.addTab(self.safety_widget, "Safety Status")

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
        else:
            self.setWindowTitle("TOSCA Laser Control System")
            self.subject_widget.setEnabled(True)
