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
    ARMED = "ARMED"  # Ready to treat, all interlocks satisfied
    TREATING = "TREATING"  # Active treatment in progress
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

    def arm_system(self) -> bool:
        """
        Transition from SAFE to ARMED state.

        System can only be armed when:
        - Current state is SAFE
        - All interlocks are satisfied
        - Valid session is active

        Returns:
            True if system successfully armed, False otherwise
        """
        if self.state != SafetyState.SAFE:
            logger.warning(f"Cannot arm system from state: {self.state.value}")
            return False

        if not (self.gpio_interlock_ok and self.session_valid and self.power_limit_ok):
            logger.warning("Cannot arm system: not all interlocks satisfied")
            return False

        self.state = SafetyState.ARMED
        self.safety_state_changed.emit(self.state)
        self.safety_event.emit("state_change", "ARMED")
        logger.info("System armed - ready for treatment")
        return True

    def start_treatment(self) -> bool:
        """
        Transition from ARMED to TREATING state.

        Treatment can only start when system is ARMED.

        Returns:
            True if treatment started successfully, False otherwise
        """
        if self.state != SafetyState.ARMED:
            logger.warning(f"Cannot start treatment from state: {self.state.value}")
            return False

        self.state = SafetyState.TREATING
        self.safety_state_changed.emit(self.state)
        self.safety_event.emit("state_change", "TREATING")
        logger.info("Treatment started")
        return True

    def stop_treatment(self) -> bool:
        """
        Transition from TREATING to ARMED state.

        Stops active treatment and returns to ARMED state.

        Returns:
            True if treatment stopped successfully, False otherwise
        """
        if self.state != SafetyState.TREATING:
            logger.warning(f"Cannot stop treatment from state: {self.state.value}")
            return False

        self.state = SafetyState.ARMED
        self.safety_state_changed.emit(self.state)
        self.safety_event.emit("state_change", "ARMED (treatment stopped)")
        logger.info("Treatment stopped - system still armed")
        return True

    def disarm_system(self) -> bool:
        """
        Transition from ARMED to SAFE state.

        Returns system to safe state when treatment is complete.

        Returns:
            True if system successfully disarmed, False otherwise
        """
        if self.state not in (SafetyState.ARMED, SafetyState.TREATING):
            logger.warning(f"Cannot disarm system from state: {self.state.value}")
            return False

        self.state = SafetyState.SAFE
        self.safety_state_changed.emit(self.state)
        self.safety_event.emit("state_change", "SAFE (disarmed)")
        logger.info("System disarmed - returned to safe state")
        return True

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

        Note: ARMED and TREATING states require explicit transitions via
        arm_system() and start_treatment(). This method only handles
        safety violations (transitions to UNSAFE or EMERGENCY_STOP).
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
                # If interlocks satisfied, maintain current state
                # (don't automatically transition to SAFE from ARMED/TREATING)
                if self.state in (SafetyState.ARMED, SafetyState.TREATING):
                    new_state = self.state  # Stay in ARMED or TREATING
                    new_enable = True
                else:
                    # From UNSAFE -> SAFE when interlocks are satisfied
                    new_state = SafetyState.SAFE
                    new_enable = True
            else:
                # Safety violation - transition to UNSAFE from any state
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


# ==============================================================================
# TEST/EXPERIMENTATION SAFETY MANAGER
# ==============================================================================
# WARNING: WARNING: This class is for hardware experimentation and testing ONLY
# WARNING: NOT FOR PRODUCTION USE
# ==============================================================================


class TestSafetyManager(SafetyManager):
    """
    Test/experimentation safety manager with relaxed safety checks.

    WARNING: DANGER: This class bypasses normal safety interlocks for hardware
    experimentation and development. Use ONLY for:
    - Hardware setup and calibration
    - Component testing
    - Development and debugging
    - Offline experiments

    🚫 NEVER use in production or clinical settings!

    Differences from production SafetyManager:
    - Session validation automatically satisfied
    - GPIO interlocks can be optionally bypassed
    - Emergency stop still functional
    - All bypass actions are logged for audit

    Note: A dedicated test application should be developed for hardware
    experimentation to completely separate test and production code paths.
    """

    def __init__(self, bypass_gpio: bool = False) -> None:
        """
        Initialize test safety manager.

        Args:
            bypass_gpio: If True, bypass GPIO interlock checks (use with extreme caution!)
        """
        super().__init__()

        self.bypass_gpio = bypass_gpio
        self.test_mode = True  # Flag to indicate test mode

        # Log prominent warning
        logger.warning("=" * 70)
        logger.warning("WARNING:  TEST SAFETY MANAGER ACTIVATED")
        logger.warning("WARNING:  Safety interlocks are BYPASSED for experimentation")
        logger.warning("WARNING:  NOT FOR PRODUCTION OR CLINICAL USE")
        logger.warning("=" * 70)

        # Automatically satisfy session requirement for testing
        self.set_session_valid(True)
        logger.warning("Test mode: Session validation automatically satisfied")

        if bypass_gpio:
            logger.critical("WARNING:  GPIO INTERLOCK BYPASS ENABLED - USE WITH EXTREME CAUTION!")
            self.set_gpio_interlock_status(True)

    def set_session_valid(self, valid: bool) -> None:
        """
        Override: In test mode, session is always valid.

        This is logged but not enforced.
        """
        logger.debug("Test mode: set_session_valid() called (automatically satisfied)")
        # Always set to True in test mode
        super().set_session_valid(True)

    def set_gpio_interlock_status(self, ok: bool) -> None:
        """
        Override: In test mode with GPIO bypass, interlocks always satisfied.

        Args:
            ok: Ignored if bypass_gpio=True
        """
        if self.bypass_gpio:
            logger.debug("Test mode: GPIO interlock bypassed (automatically satisfied)")
            super().set_gpio_interlock_status(True)
        else:
            # Normal GPIO interlock handling
            super().set_gpio_interlock_status(ok)

    def get_safety_status_text(self) -> str:
        """Override: Add test mode warning to status text."""
        base_status = super().get_safety_status_text()
        return f"WARNING:  TEST MODE - {base_status}"

    def _update_safety_state(self) -> None:
        """Override: Log all safety state changes in test mode."""
        logger.debug(
            f"Test mode safety state update: "
            f"GPIO={self.gpio_interlock_ok}, "
            f"Session={self.session_valid}, "
            f"Power={self.power_limit_ok}, "
            f"E-Stop={self.emergency_stop_active}"
        )
        super()._update_safety_state()
