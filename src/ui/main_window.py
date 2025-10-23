"""
Main application window with tab-based navigation.
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.camera_widget import CameraWidget
from ui.widgets.patient_widget import PatientWidget
from ui.widgets.safety_widget import SafetyWidget
from ui.widgets.treatment_widget import TreatmentWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window.

    Provides tab-based navigation between:
    - Patient selection
    - Camera/alignment view
    - Treatment control
    - Safety status
    """

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

        self.patient_widget = PatientWidget()
        self.tabs.addTab(self.patient_widget, "Patient Selection")

        self.camera_widget = CameraWidget()
        self.tabs.addTab(self.camera_widget, "Camera/Alignment")

        self.treatment_widget = TreatmentWidget()
        self.tabs.addTab(self.treatment_widget, "Treatment Control")

        self.safety_widget = SafetyWidget()
        self.tabs.addTab(self.safety_widget, "Safety Status")

    def _init_status_bar(self) -> None:
        """Initialize status bar with connection indicators."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        status_layout = QHBoxLayout()

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
