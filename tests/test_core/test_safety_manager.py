# -*- coding: utf-8 -*-
"""
Comprehensive tests for SafetyManager.

Tests the safety state machine, interlock coordination, emergency stop,
and signal emission for the TOSCA medical device system.
"""

import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from core.safety import SafetyManager, SafetyState


@pytest.fixture
def app():
    """Create QCoreApplication for signal/slot testing."""
    return QCoreApplication.instance() or QCoreApplication(sys.argv)


@pytest.fixture
def safety_manager(app):
    """Create a fresh SafetyManager instance."""
    return SafetyManager()


class TestSafetyManagerInitialization:
    """Test SafetyManager initialization and initial state."""

    def test_initial_state_is_unsafe(self, safety_manager):
        """Verify that SafetyManager starts in UNSAFE state (secure default)."""
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted
        assert not safety_manager.emergency_stop_active

    def test_initial_interlocks_are_false(self, safety_manager):
        """Verify all interlocks start in safe (disabled) state."""
        assert not safety_manager.gpio_interlock_ok
        assert not safety_manager.session_valid
        assert safety_manager.power_limit_ok  # Power limit starts OK (no session = no power)


class TestSafetyStateTransitions:
    """Test safety state machine transitions."""

    def test_transition_unsafe_to_safe_all_interlocks_ok(self, safety_manager, qtbot):
        """Test UNSAFE → SAFE when all interlocks are satisfied."""
        # Arrange: Start in UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE

        # Act: Satisfy all interlocks
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.set_gpio_interlock_status(True)
            safety_manager.set_session_valid(True)
            safety_manager.set_power_limit_ok(True)

        # Assert: Transitioned to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted
        assert blocker.args[0] == SafetyState.SAFE

    def test_transition_safe_to_unsafe_gpio_fails(self, safety_manager, qtbot):
        """Test SAFE → UNSAFE when GPIO interlock fails."""
        # Arrange: Start in SAFE state
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        assert safety_manager.state == SafetyState.SAFE

        # Act: GPIO interlock fails
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.set_gpio_interlock_status(False)

        # Assert: Transitioned to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted
        assert blocker.args[0] == SafetyState.UNSAFE

    def test_transition_safe_to_unsafe_session_invalid(self, safety_manager, qtbot):
        """Test SAFE → UNSAFE when session becomes invalid."""
        # Arrange: Start in SAFE state
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        assert safety_manager.state == SafetyState.SAFE

        # Act: Session becomes invalid
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.set_session_valid(False)

        # Assert: Transitioned to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted

    def test_transition_safe_to_unsafe_power_limit_exceeded(self, safety_manager, qtbot):
        """Test SAFE → UNSAFE when power limit is exceeded."""
        # Arrange: Start in SAFE state
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        assert safety_manager.state == SafetyState.SAFE

        # Act: Power limit exceeded
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.set_power_limit_ok(False)

        # Assert: Transitioned to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted


class TestEmergencyStop:
    """Test emergency stop functionality."""

    def test_emergency_stop_overrides_all_interlocks(self, safety_manager, qtbot):
        """Test that emergency stop overrides SAFE state and disables laser."""
        # Arrange: Start in SAFE state
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted

        # Act: Trigger emergency stop
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.trigger_emergency_stop()

        # Assert: Emergency stop state, laser disabled
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active
        assert not safety_manager.laser_enable_permitted
        assert blocker.args[0] == SafetyState.EMERGENCY_STOP

    def test_emergency_stop_from_unsafe_state(self, safety_manager, qtbot):
        """Test emergency stop can be triggered from UNSAFE state."""
        # Arrange: Start in UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE

        # Act: Trigger emergency stop
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000):
            safety_manager.trigger_emergency_stop()

        # Assert: Emergency stop state
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active

    def test_emergency_stop_clear_returns_to_normal_evaluation(self, safety_manager, qtbot):
        """Test clearing emergency stop returns to normal interlock evaluation."""
        # Arrange: Trigger emergency stop from SAFE state
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Clear emergency stop
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.clear_emergency_stop()

        # Assert: Returns to SAFE (interlocks still satisfied)
        assert safety_manager.state == SafetyState.SAFE
        assert not safety_manager.emergency_stop_active
        assert safety_manager.laser_enable_permitted
        assert blocker.args[0] == SafetyState.SAFE

    def test_emergency_stop_clear_to_unsafe_if_interlocks_not_met(self, safety_manager, qtbot):
        """Test clearing emergency stop returns to UNSAFE if interlocks not satisfied."""
        # Arrange: Trigger emergency stop from UNSAFE state
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Clear emergency stop (interlocks still not satisfied)
        with qtbot.waitSignal(safety_manager.safety_state_changed, timeout=1000) as blocker:
            safety_manager.clear_emergency_stop()

        # Assert: Returns to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.emergency_stop_active
        assert not safety_manager.laser_enable_permitted


class TestSignalEmission:
    """Test PyQt6 signal emission."""

    def test_laser_enable_changed_signal_emitted(self, safety_manager, qtbot):
        """Verify laser_enable_changed signal emits when laser permission changes."""
        # Arrange: Start in UNSAFE (laser disabled)
        assert not safety_manager.laser_enable_permitted

        # Act: Transition to SAFE (laser enabled)
        with qtbot.waitSignal(safety_manager.laser_enable_changed, timeout=1000) as blocker:
            safety_manager.set_gpio_interlock_status(True)
            safety_manager.set_session_valid(True)
            safety_manager.set_power_limit_ok(True)

        # Assert: Signal emitted with True
        assert blocker.args[0] is True
        assert safety_manager.laser_enable_permitted

    def test_safety_event_signal_with_correct_details(self, safety_manager, qtbot):
        """Verify safety_event signal emits with correct event type and message."""
        # Act: Change GPIO interlock
        with qtbot.waitSignal(safety_manager.safety_event, timeout=1000) as blocker:
            safety_manager.set_gpio_interlock_status(True)

        # Assert: Signal emitted with correct details
        event_type, message = blocker.args
        assert event_type == "interlock_gpio"
        assert message == "SATISFIED"

    def test_multiple_rapid_interlock_changes(self, safety_manager):
        """Test that rapid interlock changes are handled correctly without race conditions."""
        # Act: Rapidly toggle interlocks
        for _ in range(10):
            safety_manager.set_gpio_interlock_status(True)
            safety_manager.set_gpio_interlock_status(False)
            safety_manager.set_session_valid(True)
            safety_manager.set_session_valid(False)

        # Assert: Final state is UNSAFE (last changes were False)
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted


class TestStatusReporting:
    """Test status reporting methods."""

    def test_get_safety_status_text_shows_all_reasons(self, safety_manager):
        """Verify get_safety_status_text() shows all reasons for UNSAFE state."""
        # Arrange: All interlocks false
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.set_session_valid(False)
        safety_manager.set_power_limit_ok(False)

        # Act
        status = safety_manager.get_safety_status_text()

        # Assert: All reasons listed
        assert "INTERLOCKS NOT SATISFIED" in status
        assert "GPIO interlocks not satisfied" in status
        assert "No valid session" in status
        assert "Power limit exceeded" in status

    def test_get_safety_status_text_safe_state(self, safety_manager):
        """Verify status text for SAFE state."""
        # Arrange: All interlocks satisfied
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)

        # Act
        status = safety_manager.get_safety_status_text()

        # Assert
        assert "ALL INTERLOCKS SATISFIED" in status
        assert "LASER ENABLED" in status

    def test_get_safety_status_text_emergency_stop(self, safety_manager):
        """Verify status text for EMERGENCY_STOP state."""
        # Arrange: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Act
        status = safety_manager.get_safety_status_text()

        # Assert
        assert "EMERGENCY STOP ACTIVE" in status
        assert "LASER DISABLED" in status

    def test_get_interlock_details_returns_complete_dict(self, safety_manager):
        """Verify get_interlock_details() returns all interlock states."""
        # Arrange: Set various interlock states
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(False)
        safety_manager.set_power_limit_ok(True)

        # Act
        details = safety_manager.get_interlock_details()

        # Assert: All keys present
        assert "state" in details
        assert "emergency_stop" in details
        assert "gpio_interlock" in details
        assert "session_valid" in details
        assert "power_limit_ok" in details
        assert "laser_enable_permitted" in details

        # Assert: Correct values
        assert details["state"] == SafetyState.UNSAFE.value
        assert details["gpio_interlock"] is True
        assert details["session_valid"] is False
        assert details["power_limit_ok"] is True
        assert details["laser_enable_permitted"] is False

    def test_is_laser_enable_permitted_reflects_state(self, safety_manager):
        """Verify is_laser_enable_permitted() returns correct value."""
        # Initially UNSAFE
        assert not safety_manager.is_laser_enable_permitted()

        # Transition to SAFE
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)
        assert safety_manager.is_laser_enable_permitted()

        # Emergency stop
        safety_manager.trigger_emergency_stop()
        assert not safety_manager.is_laser_enable_permitted()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_setting_same_interlock_value_twice_no_signal(self, safety_manager, qtbot):
        """Verify setting the same interlock value twice doesn't emit duplicate signals."""
        # Arrange: Set GPIO to True
        safety_manager.set_gpio_interlock_status(True)

        # Act: Set GPIO to True again (no change)
        # Should NOT emit signal
        try:
            with qtbot.waitSignal(safety_manager.safety_event, timeout=100):
                safety_manager.set_gpio_interlock_status(True)
            # If signal was emitted, fail the test
            pytest.fail("Signal should not be emitted for duplicate value")
        except Exception:
            # Expected: timeout because no signal emitted
            pass

    def test_partial_interlock_satisfaction_remains_unsafe(self, safety_manager):
        """Verify that satisfying only some interlocks keeps state UNSAFE."""
        # Act: Satisfy only GPIO and session (power limit already OK)
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        # Don't set power_limit_ok to False, it starts as True

        # Actually, all three are now satisfied, so state should be SAFE
        # Let's fix the test: set power limit to False first
        safety_manager.set_power_limit_ok(False)

        # Now satisfy only GPIO and session
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)

        # Assert: Still UNSAFE (power limit not OK)
        assert safety_manager.state == SafetyState.UNSAFE
        assert not safety_manager.laser_enable_permitted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
