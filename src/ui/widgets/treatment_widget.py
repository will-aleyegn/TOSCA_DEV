"""
Treatment control widget.
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.actuator_widget import ActuatorWidget

logger = logging.getLogger(__name__)


class TreatmentWidget(QWidget):
    """
    Treatment control panel.

    Controls:
    - Laser power
    - Ring size (actuator position)
    - Treatment start/stop
    - Real-time monitoring
    """

    def __init__(self) -> None:
        super().__init__()
        self.dev_mode = False
        self.actuator_widget: ActuatorWidget = ActuatorWidget()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()  # Horizontal layout for side-by-side controls
        self.setLayout(layout)

        # Left side: Laser and treatment controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(self._create_laser_control())
        left_layout.addWidget(self._create_treatment_control())
        left_layout.addStretch()

        # Right side: Actuator controls
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.actuator_widget)

        # Add to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)

    def _create_laser_control(self) -> QGroupBox:
        """Create laser power control group."""
        group = QGroupBox("Laser Power Control")
        layout = QVBoxLayout()

        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Power (mW):"))
        self.power_spinbox = QDoubleSpinBox()
        self.power_spinbox.setRange(0, 2000)
        self.power_spinbox.setSingleStep(10)
        self.power_spinbox.setValue(0)
        power_layout.addWidget(self.power_spinbox)
        layout.addLayout(power_layout)

        self.power_slider = QSlider(Qt.Orientation.Horizontal)
        self.power_slider.setRange(0, 2000)
        self.power_slider.setValue(0)
        layout.addWidget(self.power_slider)

        self.power_spinbox.valueChanged.connect(self.power_slider.setValue)
        self.power_slider.valueChanged.connect(self.power_spinbox.setValue)

        group.setLayout(layout)
        return group

    def _create_treatment_control(self) -> QGroupBox:
        """Create treatment start/stop controls."""
        group = QGroupBox("Treatment Control")
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("START TREATMENT")
        self.start_button.setEnabled(False)
        self.start_button.setMinimumHeight(60)
        self.start_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; background-color: #4CAF50; color: white;"
        )
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("STOP TREATMENT")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; background-color: #f44336; color: white;"
        )
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel("Status: Ready - No Active Session")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        group.setLayout(layout)
        return group

    def set_dev_mode(self, dev_mode: bool) -> None:
        """
        Enable/disable developer mode.

        In dev mode, treatment controls are enabled without requiring an active session.

        Args:
            dev_mode: True to enable dev mode, False to disable
        """
        self.dev_mode = dev_mode
        logger.info(f"Treatment widget dev mode: {dev_mode}")

        if dev_mode:
            # Enable treatment controls in dev mode
            self.start_button.setEnabled(True)
            self.status_label.setText("Status: Developer Mode - Session Optional")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px; color: orange;")
        else:
            self.start_button.setEnabled(False)
            self.status_label.setText("Status: Ready - No Active Session")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.actuator_widget:
            self.actuator_widget.cleanup()
