"""
Safety status monitoring widget.
"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SafetyWidget(QWidget):
    """
    Safety system monitoring.

    Displays:
    - Footpedal status
    - Smoothing device status
    - Photodiode readings
    - E-stop status
    - Safety event log
    """

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        interlock_layout = QHBoxLayout()
        interlock_layout.addWidget(self._create_hardware_interlocks())
        interlock_layout.addWidget(self._create_software_interlocks())
        layout.addLayout(interlock_layout)

        layout.addWidget(self._create_event_log())

    def _create_hardware_interlocks(self) -> QGroupBox:
        """Create hardware interlock status group."""
        group = QGroupBox("Hardware Interlocks")
        layout = QVBoxLayout()

        self.footpedal_status = self._create_status_indicator("Footpedal", "NOT PRESSED")
        layout.addWidget(self.footpedal_status)

        self.smoothing_status = self._create_status_indicator("Smoothing Device", "NOT CONNECTED")
        layout.addWidget(self.smoothing_status)

        self.photodiode_status = self._create_status_indicator("Photodiode", "0.0 V")
        layout.addWidget(self.photodiode_status)

        group.setLayout(layout)
        return group

    def _create_software_interlocks(self) -> QGroupBox:
        """Create software interlock status group."""
        group = QGroupBox("Software Interlocks")
        layout = QVBoxLayout()

        self.estop_status = self._create_status_indicator("E-Stop", "CLEAR")
        layout.addWidget(self.estop_status)

        self.power_limit_status = self._create_status_indicator("Power Limit", "OK")
        layout.addWidget(self.power_limit_status)

        self.session_status = self._create_status_indicator("Session Valid", "NO SESSION")
        layout.addWidget(self.session_status)

        self.estop_button = QPushButton("EMERGENCY STOP")
        self.estop_button.setMinimumHeight(80)
        self.estop_button.setStyleSheet(
            "font-size: 24px; font-weight: bold; background-color: #d32f2f; color: white;"
        )
        layout.addWidget(self.estop_button)

        group.setLayout(layout)
        return group

    def _create_event_log(self) -> QGroupBox:
        """Create safety event log."""
        group = QGroupBox("Safety Event Log")
        layout = QVBoxLayout()

        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(200)
        self.event_log.setPlaceholderText(
            "Safety events will appear here...\nAll safety-critical events are logged."
        )
        layout.addWidget(self.event_log)

        group.setLayout(layout)
        return group

    def _create_status_indicator(self, label: str, initial_value: str) -> QWidget:
        """
        Create a status indicator widget.

        Args:
            label: Indicator label
            initial_value: Initial status value

        Returns:
            Status indicator widget
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(f"{label}:")
        label_widget.setMinimumWidth(150)
        layout.addWidget(label_widget)

        value_widget = QLabel(initial_value)
        value_widget.setStyleSheet("padding: 5px; background-color: #f0f0f0; font-weight: bold;")
        layout.addWidget(value_widget)

        layout.addStretch()

        widget.setLayout(layout)
        setattr(widget, "value_label", value_widget)
        return widget
