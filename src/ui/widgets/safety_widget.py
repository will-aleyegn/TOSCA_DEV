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

from ui.widgets.gpio_widget import GPIOWidget


class SafetyWidget(QWidget):
    """
    Safety system monitoring.

    Displays:
    - GPIO safety controls (smoothing device, photodiode)
    - Footpedal status (future)
    - E-stop status
    - Safety event log
    """

    def __init__(self) -> None:
        super().__init__()
        self.gpio_widget: GPIOWidget = GPIOWidget()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()  # Changed to horizontal for side-by-side
        self.setLayout(layout)

        # Left side: GPIO controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.gpio_widget)
        layout.addLayout(left_layout, 2)

        # Right side: Software interlocks and event log
        right_layout = QVBoxLayout()
        right_layout.addWidget(self._create_software_interlocks())
        right_layout.addWidget(self._create_event_log())
        layout.addLayout(right_layout, 1)

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

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.gpio_widget:
            self.gpio_widget.cleanup()
