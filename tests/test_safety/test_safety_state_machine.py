"""
Test Safety State Machine Transitions (Task 14.1).

Comprehensive tests for all valid and invalid state transitions in the safety state machine:
- Valid sequences: SAFE→ARMED→TREATING→ARMED→SAFE
- Invalid transitions: SAFE→TREATING (must go through ARMED)
- State transition validation
- Signal emission verification

Targets lines 130-211 in safety.py (state machine methods).
"""

import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.safety import SafetyManager, SafetyState  # noqa: E402


@pytest.fixture
def app(qtbot):
    """Create QApplication for PyQt6 signals."""
    app_instance = QApplication.instance()
    if app_instance is None:
        app_instance = QApplication(sys.argv)
    return app_instance


@pytest.fixture
def safety_manager(app):
    """Create safety manager with all interlocks satisfied."""
    manager = SafetyManager()

    # Satisfy all interlocks to enable state transitions
    manager.set_gpio_interlock_status(True)
    manager.set_session_valid(True)
    manager.set_power_limit_ok(True)

    return manager


class TestValidStateTransitions:
    """Test all valid state transitions."""

    def test_initial_state_is_safe(self, qtbot, safety_manager):
        """Test initial state after interlocks satisfied is SAFE."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True

    def test_safe_to_armed_transition(self, qtbot, safety_manager):
        """Test transition from SAFE to ARMED state."""
        # Track signal emissions
        state_signals = []
        event_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act
        result = safety_manager.arm_system()

        # Assert
        assert result is True
        assert safety_manager.state == SafetyState.ARMED
        assert SafetyState.ARMED in state_signals
        assert ("state_change", "ARMED") in event_signals

    def test_armed_to_treating_transition(self, qtbot, safety_manager):
        """Test transition from ARMED to TREATING state."""
        # Setup: arm system first
        safety_manager.arm_system()

        # Track signal emissions
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act
        result = safety_manager.start_treatment()

        # Assert
        assert result is True
        assert safety_manager.state == SafetyState.TREATING
        assert SafetyState.TREATING in state_signals

    def test_treating_to_armed_transition(self, qtbot, safety_manager):
        """Test transition from TREATING back to ARMED state."""
        # Setup: arm system and start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()

        # Track signal emissions
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act
        result = safety_manager.stop_treatment()

        # Assert
        assert result is True
        assert safety_manager.state == SafetyState.ARMED
        assert SafetyState.ARMED in state_signals

    def test_armed_to_safe_transition(self, qtbot, safety_manager):
        """Test transition from ARMED to SAFE state (disarm)."""
        # Setup: arm system
        safety_manager.arm_system()

        # Track signal emissions
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act
        result = safety_manager.disarm_system()

        # Assert
        assert result is True
        assert safety_manager.state == SafetyState.SAFE
        assert SafetyState.SAFE in state_signals

    def test_treating_to_safe_transition(self, qtbot, safety_manager):
        """Test transition from TREATING directly to SAFE (disarm during treatment)."""
        # Setup: arm system and start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()

        # Track signal emissions
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act
        result = safety_manager.disarm_system()

        # Assert
        assert result is True
        assert safety_manager.state == SafetyState.SAFE
        assert SafetyState.SAFE in state_signals

    def test_complete_valid_sequence_safe_armed_treating_armed_safe(self, qtbot, safety_manager):
        """Test complete valid sequence: SAFE→ARMED→TREATING→ARMED→SAFE."""
        # Track all state changes
        state_changes = []
        safety_manager.safety_state_changed.connect(lambda s: state_changes.append(s))

        # Execute complete sequence
        assert safety_manager.state == SafetyState.SAFE

        result1 = safety_manager.arm_system()
        assert result1 is True
        assert safety_manager.state == SafetyState.ARMED

        result2 = safety_manager.start_treatment()
        assert result2 is True
        assert safety_manager.state == SafetyState.TREATING

        result3 = safety_manager.stop_treatment()
        assert result3 is True
        assert safety_manager.state == SafetyState.ARMED

        result4 = safety_manager.disarm_system()
        assert result4 is True
        assert safety_manager.state == SafetyState.SAFE

        # Verify signal emissions
        assert len(state_changes) == 4
        assert state_changes == [
            SafetyState.ARMED,
            SafetyState.TREATING,
            SafetyState.ARMED,
            SafetyState.SAFE,
        ]

    def test_unsafe_to_safe_recovery(self, qtbot, safety_manager):
        """Test automatic transition from UNSAFE to SAFE when interlocks restored."""
        # Setup: force UNSAFE state by failing interlocks
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False

        # Track signal emissions
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: restore interlocks
        safety_manager.set_gpio_interlock_status(True)

        # Assert: automatic recovery to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals
        assert True in enable_signals


class TestInvalidStateTransitions:
    """Test invalid state transitions that should be blocked."""

    def test_cannot_arm_from_unsafe(self, qtbot, safety_manager):
        """Test that system cannot be armed from UNSAFE state."""
        # Setup: force UNSAFE state
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Act: try to arm (should fail)
        result = safety_manager.arm_system()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.UNSAFE

    def test_cannot_arm_from_armed(self, qtbot, safety_manager):
        """Test that system cannot be armed when already ARMED."""
        # Setup: arm system
        safety_manager.arm_system()
        assert safety_manager.state == SafetyState.ARMED

        # Act: try to arm again (should fail)
        result = safety_manager.arm_system()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.ARMED

    def test_cannot_arm_from_treating(self, qtbot, safety_manager):
        """Test that system cannot be armed when TREATING."""
        # Setup: arm and start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING

        # Act: try to arm (should fail)
        result = safety_manager.arm_system()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.TREATING

    def test_cannot_start_treatment_from_safe(self, qtbot, safety_manager):
        """Test that treatment cannot start from SAFE state (must arm first)."""
        assert safety_manager.state == SafetyState.SAFE

        # Act: try to start treatment without arming (should fail)
        result = safety_manager.start_treatment()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.SAFE

    def test_cannot_start_treatment_from_treating(self, qtbot, safety_manager):
        """Test that treatment cannot start when already TREATING."""
        # Setup: arm and start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING

        # Act: try to start treatment again (should fail)
        result = safety_manager.start_treatment()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.TREATING

    def test_cannot_stop_treatment_from_safe(self, qtbot, safety_manager):
        """Test that stop_treatment fails when not TREATING."""
        assert safety_manager.state == SafetyState.SAFE

        # Act: try to stop treatment (should fail)
        result = safety_manager.stop_treatment()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.SAFE

    def test_cannot_stop_treatment_from_armed(self, qtbot, safety_manager):
        """Test that stop_treatment fails when ARMED but not TREATING."""
        # Setup: arm system
        safety_manager.arm_system()
        assert safety_manager.state == SafetyState.ARMED

        # Act: try to stop treatment (should fail)
        result = safety_manager.stop_treatment()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.ARMED

    def test_cannot_disarm_from_safe(self, qtbot, safety_manager):
        """Test that disarm fails when already SAFE."""
        assert safety_manager.state == SafetyState.SAFE

        # Act: try to disarm (should fail)
        result = safety_manager.disarm_system()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.SAFE

    def test_cannot_disarm_from_unsafe(self, qtbot, safety_manager):
        """Test that disarm fails when UNSAFE."""
        # Setup: force UNSAFE state
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Act: try to disarm (should fail)
        result = safety_manager.disarm_system()

        # Assert
        assert result is False
        assert safety_manager.state == SafetyState.UNSAFE


class TestInterlockRequirements:
    """Test interlock requirements for state transitions."""

    def test_cannot_arm_without_gpio_interlock(self, qtbot, app):
        """Test that system cannot be armed without GPIO interlock."""
        manager = SafetyManager()
        # Only satisfy some interlocks
        manager.set_gpio_interlock_status(False)  # GPIO NOT satisfied
        manager.set_session_valid(True)
        manager.set_power_limit_ok(True)

        # Act: try to arm (should fail)
        result = manager.arm_system()

        # Assert
        assert result is False
        assert manager.state == SafetyState.UNSAFE

    def test_cannot_arm_without_session(self, qtbot, app):
        """Test that system cannot be armed without valid session."""
        manager = SafetyManager()
        # Only satisfy some interlocks
        manager.set_gpio_interlock_status(True)
        manager.set_session_valid(False)  # Session NOT valid
        manager.set_power_limit_ok(True)

        # Act: try to arm (should fail)
        result = manager.arm_system()

        # Assert
        assert result is False
        assert manager.state == SafetyState.UNSAFE

    def test_cannot_arm_with_power_limit_exceeded(self, qtbot, app):
        """Test that system cannot be armed when power limit exceeded."""
        manager = SafetyManager()
        # Only satisfy some interlocks
        manager.set_gpio_interlock_status(True)
        manager.set_session_valid(True)
        manager.set_power_limit_ok(False)  # Power limit EXCEEDED

        # Act: try to arm (should fail)
        result = manager.arm_system()

        # Assert
        assert result is False
        assert manager.state == SafetyState.UNSAFE

    def test_arm_requires_all_interlocks(self, qtbot, app):
        """Test that ALL interlocks must be satisfied to arm system."""
        manager = SafetyManager()

        # Test with various combinations of missing interlocks
        combinations = [
            (False, False, False),
            (True, False, False),
            (False, True, False),
            (False, False, True),
            (True, True, False),
            (True, False, True),
            (False, True, True),
        ]

        for gpio_ok, session_ok, power_ok in combinations:
            manager.set_gpio_interlock_status(gpio_ok)
            manager.set_session_valid(session_ok)
            manager.set_power_limit_ok(power_ok)

            result = manager.arm_system()

            # Should fail if ANY interlock is not satisfied
            assert result is False
            assert manager.state in (SafetyState.SAFE, SafetyState.UNSAFE)


class TestParameterizedTransitions:
    """Parameterized tests for comprehensive state coverage."""

    @pytest.mark.parametrize(
        "initial_state,method,expected_success",
        [
            (SafetyState.SAFE, "arm_system", True),
            (SafetyState.ARMED, "arm_system", False),
            (SafetyState.TREATING, "arm_system", False),
            (SafetyState.UNSAFE, "arm_system", False),
            (SafetyState.SAFE, "start_treatment", False),
            (SafetyState.ARMED, "start_treatment", True),
            (SafetyState.TREATING, "start_treatment", False),
            (SafetyState.UNSAFE, "start_treatment", False),
            (SafetyState.SAFE, "stop_treatment", False),
            (SafetyState.ARMED, "stop_treatment", False),
            (SafetyState.TREATING, "stop_treatment", True),
            (SafetyState.UNSAFE, "stop_treatment", False),
            (SafetyState.SAFE, "disarm_system", False),
            (SafetyState.ARMED, "disarm_system", True),
            (SafetyState.TREATING, "disarm_system", True),
            (SafetyState.UNSAFE, "disarm_system", False),
        ],
    )
    def test_transition_from_state(
        self, qtbot, safety_manager, initial_state, method, expected_success
    ):
        """Test state machine method calls from various initial states."""
        # Setup: force initial state
        if initial_state == SafetyState.ARMED:
            safety_manager.arm_system()
        elif initial_state == SafetyState.TREATING:
            safety_manager.arm_system()
            safety_manager.start_treatment()
        elif initial_state == SafetyState.UNSAFE:
            safety_manager.set_gpio_interlock_status(False)

        # Act: call the method
        result = getattr(safety_manager, method)()

        # Assert
        assert result is expected_success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
