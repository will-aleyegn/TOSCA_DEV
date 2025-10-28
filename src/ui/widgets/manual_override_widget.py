"""
Manual Interlock Override Widget - DEV MODE ONLY.

WARNING: This widget allows bypassing safety interlocks for testing purposes.
Should ONLY be used in development mode with appropriate safety measures in place.
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class ManualOverrideWidget(QWidget):
    """
    Manual safety interlock override controls for development/testing.

    ⚠️ DEV MODE ONLY - DANGEROUS ⚠️

    Features:
    - Manual override of GPIO interlock
    - Manual override of session validity
    - Manual override of power limit
    - Visual warning indicators
    - All overrides logged for audit trail

    Security:
    - Only functional when dev_mode=True
    - Prominent warning labels
    - All actions logged
    """

    def __init__(self) -> None:
        super().__init__()
        self.safety_manager = None
        self.dev_mode = False

        # Override states
        self.gpio_override_active = False
        self.session_override_active = False
        self.power_override_active = False

        self._init_ui()
        self._update_enabled_state()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Danger warning header
        warning_label = QLabel("⚠️ MANUAL OVERRIDE - DEV MODE ONLY ⚠️")
        warning_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; padding: 8px; "
            "background-color: #ff5722; color: white; border-radius: 3px;"
        )
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning_label)

        # Warning message
        warning_text = QLabel(
            "Manual overrides bypass safety interlocks.\n"
            "Use ONLY for controlled testing.\n"
            "All override actions are logged."
        )
        warning_text.setStyleSheet(
            "color: #ff5722; font-size: 11px; font-weight: bold; padding: 5px;"
        )
        warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_text.setWordWrap(True)
        layout.addWidget(warning_text)

        # Override controls group
        override_group = QGroupBox("Interlock Overrides")
        override_layout = QVBoxLayout()
        override_group.setLayout(override_layout)

        # GPIO override
        gpio_layout = QHBoxLayout()
        gpio_label = QLabel("GPIO Interlock:")
        gpio_label.setMinimumWidth(120)
        gpio_layout.addWidget(gpio_label)

        self.gpio_override_checkbox = QCheckBox("Force OK")
        self.gpio_override_checkbox.setToolTip("Override GPIO interlock (motor/photodiode check)")
        self.gpio_override_checkbox.stateChanged.connect(self._on_gpio_override_changed)
        gpio_layout.addWidget(self.gpio_override_checkbox)

        self.gpio_status_label = QLabel("(Currently: FAIL)")
        self.gpio_status_label.setStyleSheet("color: #888; font-size: 10px;")
        gpio_layout.addWidget(self.gpio_status_label)
        gpio_layout.addStretch()

        override_layout.addLayout(gpio_layout)

        # Session override
        session_layout = QHBoxLayout()
        session_label = QLabel("Session Valid:")
        session_label.setMinimumWidth(120)
        session_layout.addWidget(session_label)

        self.session_override_checkbox = QCheckBox("Force Valid")
        self.session_override_checkbox.setToolTip("Override session validity check")
        self.session_override_checkbox.stateChanged.connect(self._on_session_override_changed)
        session_layout.addWidget(self.session_override_checkbox)

        self.session_status_label = QLabel("(Currently: INVALID)")
        self.session_status_label.setStyleSheet("color: #888; font-size: 10px;")
        session_layout.addWidget(self.session_status_label)
        session_layout.addStretch()

        override_layout.addLayout(session_layout)

        # Power limit override
        power_layout = QHBoxLayout()
        power_label = QLabel("Power Limit:")
        power_label.setMinimumWidth(120)
        power_layout.addWidget(power_label)

        self.power_override_checkbox = QCheckBox("Force OK")
        self.power_override_checkbox.setToolTip("Override power limit check")
        self.power_override_checkbox.stateChanged.connect(self._on_power_override_changed)
        power_layout.addWidget(self.power_override_checkbox)

        self.power_status_label = QLabel("(Currently: OK)")
        self.power_status_label.setStyleSheet("color: #888; font-size: 10px;")
        power_layout.addWidget(self.power_status_label)
        power_layout.addStretch()

        override_layout.addLayout(power_layout)

        layout.addWidget(override_group)

        # Status label
        self.status_label = QLabel("No overrides active")
        self.status_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def set_safety_manager(self, safety_manager) -> None:
        """
        Connect to safety manager for override control.

        Args:
            safety_manager: SafetyManager instance
        """
        self.safety_manager = safety_manager
        logger.info("Manual override widget connected to safety manager")

    def set_dev_mode(self, dev_mode: bool) -> None:
        """
        Enable/disable dev mode.

        Args:
            dev_mode: True to enable manual overrides
        """
        self.dev_mode = dev_mode

        if not dev_mode:
            # Disable all overrides when leaving dev mode
            self.gpio_override_checkbox.setChecked(False)
            self.session_override_checkbox.setChecked(False)
            self.power_override_checkbox.setChecked(False)

        self._update_enabled_state()

        logger.warning(f"Manual override widget dev mode: {dev_mode}")

    def _update_enabled_state(self) -> None:
        """Update enabled state of override controls based on dev mode."""
        enabled = self.dev_mode and self.safety_manager is not None

        self.gpio_override_checkbox.setEnabled(enabled)
        self.session_override_checkbox.setEnabled(enabled)
        self.power_override_checkbox.setEnabled(enabled)

        if not enabled:
            self.status_label.setText("Overrides disabled (not in dev mode)")
            self.status_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")

    def _on_gpio_override_changed(self, state: int) -> None:
        """Handle GPIO override checkbox change."""
        if not self.dev_mode or not self.safety_manager:
            return

        self.gpio_override_active = state == Qt.CheckState.Checked.value

        if self.gpio_override_active:
            self.safety_manager.set_gpio_interlock_status(True)
            self.gpio_status_label.setText("(OVERRIDDEN → OK)")
            self.gpio_status_label.setStyleSheet(
                "color: #ff5722; font-size: 10px; font-weight: bold;"
            )
            logger.warning("⚠️ GPIO interlock MANUALLY OVERRIDDEN → OK")
        else:
            # Note: When unchecked, the actual GPIO status will be restored by the controller
            self.gpio_status_label.setText("(Override removed)")
            self.gpio_status_label.setStyleSheet("color: #888; font-size: 10px;")
            logger.warning("GPIO interlock override REMOVED")

        self._update_status()

    def _on_session_override_changed(self, state: int) -> None:
        """Handle session override checkbox change."""
        if not self.dev_mode or not self.safety_manager:
            return

        self.session_override_active = state == Qt.CheckState.Checked.value

        if self.session_override_active:
            self.safety_manager.set_session_valid(True)
            self.session_status_label.setText("(OVERRIDDEN → VALID)")
            self.session_status_label.setStyleSheet(
                "color: #ff5722; font-size: 10px; font-weight: bold;"
            )
            logger.warning("⚠️ Session validity MANUALLY OVERRIDDEN → VALID")
        else:
            self.safety_manager.set_session_valid(False)
            self.session_status_label.setText("(Override removed)")
            self.session_status_label.setStyleSheet("color: #888; font-size: 10px;")
            logger.warning("Session validity override REMOVED")

        self._update_status()

    def _on_power_override_changed(self, state: int) -> None:
        """Handle power limit override checkbox change."""
        if not self.dev_mode or not self.safety_manager:
            return

        self.power_override_active = state == Qt.CheckState.Checked.value

        if self.power_override_active:
            self.safety_manager.set_power_limit_ok(True)
            self.power_status_label.setText("(OVERRIDDEN → OK)")
            self.power_status_label.setStyleSheet(
                "color: #ff5722; font-size: 10px; font-weight: bold;"
            )
            logger.warning("⚠️ Power limit MANUALLY OVERRIDDEN → OK")
        else:
            # Restore to default OK state
            self.safety_manager.set_power_limit_ok(True)
            self.power_status_label.setText("(Override removed)")
            self.power_status_label.setStyleSheet("color: #888; font-size: 10px;")
            logger.warning("Power limit override REMOVED")

        self._update_status()

    def _update_status(self) -> None:
        """Update overall override status label."""
        active_overrides = []

        if self.gpio_override_active:
            active_overrides.append("GPIO")
        if self.session_override_active:
            active_overrides.append("Session")
        if self.power_override_active:
            active_overrides.append("Power")

        if active_overrides:
            override_list = ", ".join(active_overrides)
            self.status_label.setText(f"⚠️ ACTIVE OVERRIDES: {override_list}")
            self.status_label.setStyleSheet(
                "color: #ff5722; font-size: 11px; font-weight: bold; padding: 5px; "
                "background-color: #2b2b2b; border-radius: 3px;"
            )
        else:
            self.status_label.setText("No overrides active")
            self.status_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
