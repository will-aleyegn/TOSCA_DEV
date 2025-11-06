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


class SafetyWidget(QWidget):
    """
    Safety Event Log and Software Interlocks display.

    Provides:
    - Software interlock status (E-stop, power limit, session)
    - Comprehensive safety event log with database loading

    NOTE: This widget focuses on software safety monitoring.
    GPIO hardware diagnostics are shown separately in the hardware tab.
    Operator-critical safety info is displayed in status bar and treatment dashboard.
    """

    def __init__(
        self, db_manager: Optional[Any] = None, gpio_controller: Optional[Any] = None
    ) -> None:
        super().__init__()
        # Note: gpio_controller parameter kept for backward compatibility but not used
        # GPIO widget is now managed separately in main_window
        self.safety_manager: Optional[SafetyManager] = None
        self.db_manager = db_manager
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components for Safety Event Log display."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Constrain maximum width to prevent excessive horizontal stretching
        self.setMaximumWidth(800)

        # Software interlocks status (can be hidden if shown in persistent header)
        self.software_interlocks_widget = self._create_software_interlocks()
        main_layout.addWidget(self.software_interlocks_widget)

        # Safety event log (elevated for visibility)
        main_layout.addWidget(self._create_event_log())

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

        # Note: E-Stop button removed - use toolbar E-Stop button (always visible)
        # Toolbar E-Stop is the primary emergency control per IEC 62366-1 standards

        group.setLayout(layout)
        return group

    def _create_event_log(self) -> QGroupBox:
        """Create safety event log."""
        group = QGroupBox("Safety Event Log")
        layout = QVBoxLayout()

        # Event log text display
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(200)
        self.event_log.setPlaceholderText(
            "Safety events will appear here...\nAll safety-critical events are logged."
        )
        layout.addWidget(self.event_log)

        # Load button below the text display (better UX - action after viewing area)
        self.refresh_button = QPushButton("Load Database Events")
        self.refresh_button.clicked.connect(self._load_database_events)
        if not self.db_manager:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setToolTip("Database not available")
        layout.addWidget(self.refresh_button)

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

        # Note: E-Stop button signal connection removed (button no longer exists)
        # Use toolbar E-Stop button for emergency shutdown

        # Log initial connection
        self._log_event("Safety system initialized")

    # Note: _on_estop_clicked() method removed (redundant E-Stop button eliminated)
    # Toolbar E-Stop button in main_window.py is the primary emergency control

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
        # Note: GPIO widget removed from SafetyWidget (now shown separately)
        # No cleanup needed - event log is just a QTextEdit
        pass
