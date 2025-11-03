"""
Consolidated interlock status widget for Treatment Dashboard.

Displays all laser prerequisite interlocks in a compact format:
- Session Valid
- GPIO Interlock (laser spot smoothing module + photodiode laser pickoff measurement)
- Power Limit
- Final Laser Enable Permission
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.safety import SafetyManager, SafetyState


class InterlocksWidget(QGroupBox):
    """
    Consolidated display of all laser prerequisite interlocks.

    Shows the status of each interlock that must be satisfied before
    laser operation is permitted. This widget is designed for the
    Treatment Dashboard to provide at-a-glance safety status visibility.
    """

    def __init__(self) -> None:
        super().__init__("Safety Interlocks")
        self.safety_manager: Optional[SafetyManager] = None

        # Initialize interlock states
        self._session_valid = False
        self._gpio_interlock_ok = False
        self._power_limit_ok = True  # Default OK until we hear otherwise
        self._laser_enabled = False

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Individual interlock status indicators
        self.session_indicator = self._create_indicator("Session Valid")
        layout.addWidget(self.session_indicator)

        self.gpio_indicator = self._create_indicator("GPIO Interlock")
        layout.addWidget(self.gpio_indicator)

        self.power_indicator = self._create_indicator("Power Limit")
        layout.addWidget(self.power_indicator)

        # Separator line
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #3c3c3c;")
        layout.addWidget(separator)

        # Final laser enable status (prominent)
        laser_widget = QWidget()
        laser_layout = QHBoxLayout()
        laser_layout.setContentsMargins(0, 5, 0, 5)

        laser_label = QLabel("LASER:")
        laser_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        laser_layout.addWidget(laser_label)

        self.laser_status_label = QLabel("DENIED")
        self.laser_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.laser_status_label.setStyleSheet(
            "padding: 8px 12px; background-color: #f44336; color: white; "
            "font-weight: bold; font-size: 13px; border-radius: 3px;"
        )
        laser_layout.addWidget(self.laser_status_label, 1)

        laser_widget.setLayout(laser_layout)
        layout.addWidget(laser_widget)

        layout.addStretch()

    def _create_indicator(self, label_text: str) -> QWidget:
        """
        Create a status indicator row.

        Args:
            label_text: Text label for the indicator

        Returns:
            Widget containing label and status icon
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        label = QLabel(label_text + ":")
        label.setMinimumWidth(110)
        label.setStyleSheet("font-size: 11px;")
        layout.addWidget(label)

        # Status icon/text
        status_label = QLabel("# [FAILED] FAIL")
        status_label.setStyleSheet(
            "padding: 4px 8px; background-color: #2b2b2b; color: #f44336; "
            "font-weight: bold; font-size: 11px; border-radius: 2px;"
        )
        layout.addWidget(status_label)

        layout.addStretch()

        widget.setLayout(layout)

        # Store reference to status label for updates
        setattr(widget, "status_label", status_label)

        return widget

    def set_safety_manager(self, safety_manager: SafetyManager) -> None:
        """
        Connect to safety manager and wire up signals.

        Args:
            safety_manager: The SafetyManager instance to connect
        """
        self.safety_manager = safety_manager

        # Connect safety manager signals
        safety_manager.safety_state_changed.connect(self._on_safety_state_changed)
        safety_manager.laser_enable_changed.connect(self._on_laser_enable_changed)
        safety_manager.safety_event.connect(self._on_safety_event)

    @pyqtSlot(SafetyState)
    def _on_safety_state_changed(self, state: SafetyState) -> None:
        """
        Handle overall safety state changes.

        Args:
            state: New safety state
        """
        # GPIO interlock status is implied by safety state
        # If state is SAFE, GPIO must be OK (assuming other conditions met)
        # This is a heuristic - actual GPIO status comes from safety_event signals
        pass

    @pyqtSlot(bool)
    def _on_laser_enable_changed(self, enabled: bool) -> None:
        """
        Handle laser enable permission changes.

        Args:
            enabled: True if laser enable permitted
        """
        self._laser_enabled = enabled
        self._update_laser_status()

    @pyqtSlot(str, str)
    def _on_safety_event(self, event_type: str, message: str) -> None:
        """
        Handle safety events and update interlock indicators.

        Args:
            event_type: Type of event (interlock_gpio, session, power_limit, etc.)
            message: Event message
        """
        if event_type == "session":
            self._session_valid = message == "VALID"
            self._update_indicator(
                self.session_indicator,
                self._session_valid,
                "Session" if not self._session_valid else "",
            )

        elif event_type == "interlock_gpio":
            # GPIO interlock status
            self._gpio_interlock_ok = message == "OK"
            self._update_indicator(
                self.gpio_indicator,
                self._gpio_interlock_ok,
                "Motor/Photo" if not self._gpio_interlock_ok else "",
            )

        elif event_type == "power_limit":
            self._power_limit_ok = message == "OK"
            self._update_indicator(
                self.power_indicator,
                self._power_limit_ok,
                "Exceeded" if not self._power_limit_ok else "",
            )

    def _update_indicator(
        self, indicator_widget: QWidget, is_ok: bool, fail_reason: str = ""
    ) -> None:
        """
        Update an individual interlock indicator.

        Args:
            indicator_widget: The indicator widget to update
            is_ok: True if interlock is satisfied
            fail_reason: Optional reason text if interlock fails
        """
        status_label = getattr(indicator_widget, "status_label", None)
        if not status_label:
            return

        if is_ok:
            status_label.setText("# [DONE] OK")
            status_label.setStyleSheet(
                "padding: 4px 8px; background-color: #2b2b2b; color: #4CAF50; "
                "font-weight: bold; font-size: 11px; border-radius: 2px;"
            )
        else:
            text = f"# [FAILED] {fail_reason}" if fail_reason else "# [FAILED] FAIL"
            status_label.setText(text)
            status_label.setStyleSheet(
                "padding: 4px 8px; background-color: #2b2b2b; color: #f44336; "
                "font-weight: bold; font-size: 11px; border-radius: 2px;"
            )

    def _update_laser_status(self) -> None:
        """Update the final laser enable status display."""
        if self._laser_enabled:
            self.laser_status_label.setText("PERMITTED")
            self.laser_status_label.setStyleSheet(
                "padding: 8px 12px; background-color: #4CAF50; color: white; "
                "font-weight: bold; font-size: 13px; border-radius: 3px;"
            )
        else:
            self.laser_status_label.setText("DENIED")
            self.laser_status_label.setStyleSheet(
                "padding: 8px 12px; background-color: #f44336; color: white; "
                "font-weight: bold; font-size: 13px; border-radius: 3px;"
            )

    def update_session_status(self, valid: bool) -> None:
        """
        Manually update session status (for external calls).

        Args:
            valid: True if session is valid
        """
        self._session_valid = valid
        self._update_indicator(self.session_indicator, valid, "No Session" if not valid else "")

    def update_gpio_status(self, ok: bool, reason: str = "") -> None:
        """
        Manually update GPIO interlock status (for external calls).

        Args:
            ok: True if GPIO interlock is satisfied
            reason: Optional reason text if interlock fails
        """
        self._gpio_interlock_ok = ok
        self._update_indicator(self.gpio_indicator, ok, reason if not ok else "")

    def update_power_limit_status(self, ok: bool) -> None:
        """
        Manually update power limit status (for external calls).

        Args:
            ok: True if power limit is satisfied
        """
        self._power_limit_ok = ok
        self._update_indicator(self.power_indicator, ok, "Exceeded" if not ok else "")
