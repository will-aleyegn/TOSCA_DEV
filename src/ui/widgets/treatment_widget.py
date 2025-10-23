"""
Treatment control widget.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


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
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self._create_laser_control())
        layout.addWidget(self._create_ring_control())
        layout.addWidget(self._create_treatment_control())
        layout.addStretch()

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

    def _create_ring_control(self) -> QGroupBox:
        """Create ring size control group."""
        group = QGroupBox("Ring Size Control (Actuator)")
        layout = QVBoxLayout()

        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position (µm):"))
        self.position_spinbox = QSpinBox()
        self.position_spinbox.setRange(0, 3000)
        self.position_spinbox.setSingleStep(50)
        self.position_spinbox.setValue(0)
        position_layout.addWidget(self.position_spinbox)
        layout.addLayout(position_layout)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 3000)
        self.position_slider.setValue(0)
        layout.addWidget(self.position_slider)

        self.position_spinbox.valueChanged.connect(self.position_slider.setValue)
        self.position_slider.valueChanged.connect(self.position_spinbox.setValue)

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
