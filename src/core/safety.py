# -*- coding: utf-8 -*-
"""
Safety system manager for TOSCA laser control.

Coordinates all safety interlocks and enforces laser enable/disable.
"""

import logging
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class SafetyState(Enum):
    """Safety system states."""

    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class SafetyManager(QObject):
    """
    Central safety manager for TOSCA system.

    Coordinates safety interlocks from:
    - GPIO controller (smoothing device, photodiode)
    - Emergency stop button
    - Software safety checks

    Enforces laser enable/disable based on safety state.
    """

    # Signals
    safety_state_changed = pyqtSignal(SafetyState)  # Overall safety state
    laser_enable_changed = pyqtSignal(bool)  # Laser enable permission
    safety_event = pyqtSignal(str, str)  # (event_type, message)

    def __init__(self) -> None:
        super().__init__()

        # Safety state
        self.state = SafetyState.UNSAFE
        self.emergency_stop_active = False

        # Interlock status
        self.gpio_interlock_ok = False
        self.session_valid = False
        self.power_limit_ok = True

        # Laser enable permission
        self.laser_enable_permitted = False

        logger.info("Safety manager initialized")

    def set_gpio_interlock_status(self, ok: bool) -> None:
        """
        Update GPIO interlock status.

        Args:
            ok: True if GPIO interlocks satisfied (motor ON + vibration detected)
        """
        if ok != self.gpio_interlock_ok:
            self.gpio_interlock_ok = ok
            status = "SATISFIED" if ok else "NOT SATISFIED"
            logger.info(f"GPIO interlock status: {status}")
            self.safety_event.emit("interlock_gpio", status)
            self._update_safety_state()

    def set_session_valid(self, valid: bool) -> None:
        """
        Update session validity status.

        Args:
            valid: True if valid session active
        """
        if valid != self.session_valid:
            self.session_valid = valid
            status = "VALID" if valid else "INVALID"
            logger.info(f"Session status: {status}")
            self.safety_event.emit("session", status)
            self._update_safety_state()

    def set_power_limit_ok(self, ok: bool) -> None:
        """
        Update power limit status.

        Args:
            ok: True if power within limits
        """
        if ok != self.power_limit_ok:
            self.power_limit_ok = ok
            status = "OK" if ok else "EXCEEDED"
            logger.warning(f"Power limit status: {status}")
            self.safety_event.emit("power_limit", status)
            self._update_safety_state()

    def trigger_emergency_stop(self) -> None:
        """
        Trigger emergency stop.

        Immediately disables laser and sets emergency stop state.
        """
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.emergency_stop_active = True
        self.state = SafetyState.EMERGENCY_STOP
        self.laser_enable_permitted = False

        self.safety_state_changed.emit(self.state)
        self.laser_enable_changed.emit(False)
        self.safety_event.emit("emergency_stop", "ACTIVATED")

    def clear_emergency_stop(self) -> None:
        """
        Clear emergency stop.

        Returns to normal safety evaluation.
        """
        logger.info("Emergency stop cleared")
        self.emergency_stop_active = False
        self.safety_event.emit("emergency_stop", "CLEARED")
        self._update_safety_state()

    def is_laser_enable_permitted(self) -> bool:
        """
        Check if laser enable is permitted.

        Returns:
            True if all safety conditions met
        """
        return self.laser_enable_permitted

    def get_safety_status_text(self) -> str:
        """
        Get human-readable safety status.

        Returns:
            Status text describing current safety state
        """
        if self.state == SafetyState.EMERGENCY_STOP:
            return "EMERGENCY STOP ACTIVE - LASER DISABLED"
        elif self.state == SafetyState.SAFE:
            return "ALL INTERLOCKS SATISFIED - LASER ENABLED"
        else:
            # Build detailed message about why unsafe
            reasons = []
            if not self.gpio_interlock_ok:
                reasons.append("GPIO interlocks not satisfied")
            if not self.session_valid:
                reasons.append("No valid session")
            if not self.power_limit_ok:
                reasons.append("Power limit exceeded")

            if reasons:
                return "INTERLOCKS NOT SATISFIED: " + ", ".join(reasons)
            else:
                return "SYSTEM NOT READY"

    def get_interlock_details(self) -> dict:
        """
        Get detailed interlock status.

        Returns:
            Dictionary with all interlock states
        """
        return {
            "state": self.state.value,
            "emergency_stop": self.emergency_stop_active,
            "gpio_interlock": self.gpio_interlock_ok,
            "session_valid": self.session_valid,
            "power_limit_ok": self.power_limit_ok,
            "laser_enable_permitted": self.laser_enable_permitted,
        }

    def _update_safety_state(self) -> None:
        """
        Evaluate all safety conditions and update state.

        Called whenever any safety input changes.
        """
        # Emergency stop overrides everything
        if self.emergency_stop_active:
            new_state = SafetyState.EMERGENCY_STOP
            new_enable = False
        else:
            # Check all safety conditions
            all_conditions_met = (
                self.gpio_interlock_ok and self.session_valid and self.power_limit_ok
            )

            if all_conditions_met:
                new_state = SafetyState.SAFE
                new_enable = True
            else:
                new_state = SafetyState.UNSAFE
                new_enable = False

        # Update state if changed
        if new_state != self.state:
            logger.info(f"Safety state changed: {self.state.value} → {new_state.value}")
            self.state = new_state
            self.safety_state_changed.emit(new_state)
            self.safety_event.emit("state_change", new_state.value)

        # Update laser enable permission if changed
        if new_enable != self.laser_enable_permitted:
            self.laser_enable_permitted = new_enable
            self.laser_enable_changed.emit(new_enable)
            status = "PERMITTED" if new_enable else "DENIED"
            logger.info(f"Laser enable: {status}")
            self.safety_event.emit("laser_enable", status)
