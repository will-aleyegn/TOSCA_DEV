"""
Safety status monitoring widget.
"""

from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.safety import SafetyManager, SafetyState
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

    def __init__(self, db_manager: Optional[Any] = None) -> None:
        super().__init__()
        self.gpio_widget: GPIOWidget = GPIOWidget()
        self.safety_manager: Optional[SafetyManager] = None
        self.db_manager = db_manager
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

        # Add refresh button
        self.refresh_button = QPushButton("Load Database Events")
        self.refresh_button.clicked.connect(self._load_database_events)
        if not self.db_manager:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setToolTip("Database not available")
        layout.addWidget(self.refresh_button)

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

    def set_safety_manager(self, safety_manager: SafetyManager) -> None:
        """
        Connect safety manager and wire up signals.

        Args:
            safety_manager: The SafetyManager instance to connect
        """
        self.safety_manager = safety_manager

        # Connect safety manager signals
        safety_manager.safety_state_changed.connect(self._on_safety_state_changed)
        safety_manager.laser_enable_changed.connect(self._on_laser_enable_changed)
        safety_manager.safety_event.connect(self._on_safety_event)

        # Wire emergency stop button
        self.estop_button.clicked.connect(self._on_estop_clicked)

        # Log initial connection
        self._log_event("Safety system initialized")

    @pyqtSlot()
    def _on_estop_clicked(self) -> None:
        """Handle emergency stop button click."""
        if self.safety_manager:
            self.safety_manager.trigger_emergency_stop()
            self.estop_button.setEnabled(False)
            self.estop_button.setText("E-STOP ACTIVE")

    @pyqtSlot(SafetyState)
    def _on_safety_state_changed(self, state: SafetyState) -> None:
        """
        Handle safety state changes.

        Args:
            state: New safety state
        """
        if state == SafetyState.SAFE:
            color = "#4CAF50"
            text = "SAFE"
        elif state == SafetyState.UNSAFE:
            color = "#FF9800"
            text = "UNSAFE"
        else:  # EMERGENCY_STOP
            color = "#f44336"
            text = "EMERGENCY STOP"

        # Update E-stop status indicator
        estop_label = getattr(self.estop_status, "value_label", None)
        if estop_label:
            if state == SafetyState.EMERGENCY_STOP:
                estop_label.setText("ACTIVE")
                estop_label.setStyleSheet(
                    f"padding: 5px; background-color: {color}; color: white; font-weight: bold;"
                )
            else:
                estop_label.setText("CLEAR")
                estop_label.setStyleSheet(
                    "padding: 5px; background-color: #f0f0f0; font-weight: bold;"
                )

        self._log_event(f"Safety state: {text}", urgent=(state == SafetyState.EMERGENCY_STOP))

    @pyqtSlot(bool)
    def _on_laser_enable_changed(self, enabled: bool) -> None:
        """
        Handle laser enable permission changes.

        Args:
            enabled: True if laser enable permitted
        """
        status = "PERMITTED" if enabled else "DENIED"
        self._log_event(f"Laser enable: {status}", urgent=not enabled)

    @pyqtSlot(str, str)
    def _on_safety_event(self, event_type: str, message: str) -> None:
        """
        Handle safety events.

        Args:
            event_type: Type of event (interlock_gpio, session, power_limit, etc.)
            message: Event message
        """
        # Update relevant status indicators
        if event_type == "session":
            session_label = getattr(self.session_status, "value_label", None)
            if session_label:
                session_label.setText(message)
                if message == "VALID":
                    session_label.setStyleSheet(
                        "padding: 5px; background-color: #4CAF50; color: white; font-weight: bold;"
                    )
                else:
                    session_label.setStyleSheet(
                        "padding: 5px; background-color: #f0f0f0; font-weight: bold;"
                    )

        elif event_type == "power_limit":
            power_label = getattr(self.power_limit_status, "value_label", None)
            if power_label:
                power_label.setText(message)
                if message == "OK":
                    power_label.setStyleSheet(
                        "padding: 5px; background-color: #4CAF50; color: white; font-weight: bold;"
                    )
                else:
                    power_label.setStyleSheet(
                        "padding: 5px; background-color: #f44336; color: white; font-weight: bold;"
                    )

        # Log all events
        urgent = event_type in ["emergency_stop", "power_limit"] and message in [
            "ACTIVATED",
            "EXCEEDED",
        ]
        self._log_event(f"[{event_type}] {message}", urgent=urgent)

    def _log_event(self, message: str, urgent: bool = False) -> None:
        """
        Log a safety event to the event log.

        Args:
            message: Event message
            urgent: If True, format as urgent (red/bold)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        if urgent:
            formatted_msg = (
                f'<span style="color: red; font-weight: bold;">[{timestamp}] {message}</span>'
            )
        else:
            formatted_msg = f"[{timestamp}] {message}"

        self.event_log.append(formatted_msg)

    @pyqtSlot()
    def _load_database_events(self) -> None:
        """Load and display events from database."""
        if not self.db_manager:
            self._log_event("Database not available", urgent=True)
            return

        try:
            # Get recent safety logs from database (last 50 events)
            logs = self.db_manager.get_safety_logs(limit=50)

            if not logs:
                self._log_event("No database events found", urgent=False)
                return

            # Clear existing log
            self.event_log.clear()

            # Display database events
            self._log_event(f"=== Loaded {len(logs)} events from database ===", urgent=False)

            for log in reversed(logs):  # Reverse to show oldest first
                # Format timestamp
                timestamp_str = log.timestamp.strftime("%H:%M:%S")

                # Determine if urgent based on severity
                urgent = log.severity in ["critical", "emergency"]

                # Format event description
                event_msg = f"{log.description}"
                if log.severity != "info":
                    event_msg = f"[{log.severity.upper()}] {event_msg}"

                # Log the event
                if urgent:
                    formatted_msg = (
                        f'<span style="color: red; font-weight: bold;">'
                        f"[{timestamp_str}] {event_msg}</span>"
                    )
                else:
                    formatted_msg = f"[{timestamp_str}] {event_msg}"

                self.event_log.append(formatted_msg)

            self._log_event("=== End of database events ===", urgent=False)

        except Exception as e:
            self._log_event(f"Failed to load database events: {e}", urgent=True)

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.gpio_widget:
            self.gpio_widget.cleanup()
