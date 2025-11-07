"""
Test Safety Fault Handling and Recovery (Task 14.2).

Comprehensive tests for safety fault scenarios including:
- Automatic transition to UNSAFE from any state (SAFE, ARMED, TREATING)
- Each interlock failure type (GPIO, session, power limit)
- Signal emission verification for fault events
- Recovery validation when interlocks restored
- laser_enable_permitted behavior during faults
- Rapid fault/recovery cycles and edge cases

Targets lines 296-344 in safety.py (_update_safety_state method).
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

    # Satisfy all interlocks to start in SAFE state
    manager.set_gpio_interlock_status(True)
    manager.set_session_valid(True)
    manager.set_power_limit_ok(True)

    return manager


class TestFaultTransitionsFromAllStates:
    """Test automatic transition to UNSAFE from all states."""

    def test_fault_from_safe_state(self, qtbot, safety_manager):
        """Test transition SAFE -> UNSAFE when interlock fails."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True

        # Track signal emissions
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Fail GPIO interlock
        safety_manager.set_gpio_interlock_status(False)

        # Assert: Automatic transition to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.UNSAFE in state_signals
        assert False in enable_signals

    def test_fault_from_armed_state(self, qtbot, safety_manager):
        """Test transition ARMED -> UNSAFE when interlock fails."""
        # Setup: Arm system first
        safety_manager.arm_system()
        assert safety_manager.state == SafetyState.ARMED
        assert safety_manager.laser_enable_permitted is True

        # Track signal emissions
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Fail session interlock
        safety_manager.set_session_valid(False)

        # Assert: Automatic transition to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.UNSAFE in state_signals
        assert False in enable_signals

    def test_fault_from_treating_state(self, qtbot, safety_manager):
        """Test transition TREATING -> UNSAFE when interlock fails."""
        # Setup: Arm and start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING
        assert safety_manager.laser_enable_permitted is True

        # Track signal emissions
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Fail power limit interlock
        safety_manager.set_power_limit_ok(False)

        # Assert: Automatic transition to UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.UNSAFE in state_signals
        assert False in enable_signals


class TestInterlockFailureTypes:
    """Test each type of interlock failure (GPIO, session, power)."""

    def test_gpio_interlock_failure(self, qtbot, safety_manager):
        """Test GPIO interlock failure causes UNSAFE transition."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.gpio_interlock_ok is True

        # Track safety events
        event_signals = []
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Fail GPIO interlock
        safety_manager.set_gpio_interlock_status(False)

        # Assert
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.gpio_interlock_ok is False
        assert safety_manager.laser_enable_permitted is False
        assert ("interlock_gpio", "NOT SATISFIED") in event_signals
        assert ("state_change", "UNSAFE") in event_signals

    def test_session_interlock_failure(self, qtbot, safety_manager):
        """Test session validity failure causes UNSAFE transition."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.session_valid is True

        # Track safety events
        event_signals = []
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Invalidate session
        safety_manager.set_session_valid(False)

        # Assert
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.session_valid is False
        assert safety_manager.laser_enable_permitted is False
        assert ("session", "INVALID") in event_signals
        assert ("state_change", "UNSAFE") in event_signals

    def test_power_limit_failure(self, qtbot, safety_manager):
        """Test power limit exceeded causes UNSAFE transition."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.power_limit_ok is True

        # Track safety events
        event_signals = []
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Exceed power limit
        safety_manager.set_power_limit_ok(False)

        # Assert
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.power_limit_ok is False
        assert safety_manager.laser_enable_permitted is False
        assert ("power_limit", "EXCEEDED") in event_signals
        assert ("state_change", "UNSAFE") in event_signals

    def test_multiple_interlock_failures_simultaneously(self, qtbot, safety_manager):
        """Test multiple interlock failures at once."""
        assert safety_manager.state == SafetyState.SAFE

        # Act: Fail all interlocks simultaneously
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.set_session_valid(False)
        safety_manager.set_power_limit_ok(False)

        # Assert: State is UNSAFE and all interlocks failed
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.gpio_interlock_ok is False
        assert safety_manager.session_valid is False
        assert safety_manager.power_limit_ok is False
        assert safety_manager.laser_enable_permitted is False


class TestFaultRecovery:
    """Test recovery mechanisms when interlocks are restored."""

    def test_recovery_from_gpio_failure(self, qtbot, safety_manager):
        """Test recovery to SAFE when GPIO interlock is restored."""
        # Setup: Force UNSAFE by failing GPIO
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Track signals
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Restore GPIO interlock
        safety_manager.set_gpio_interlock_status(True)

        # Assert: Automatic recovery to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals
        assert True in enable_signals

    def test_recovery_from_session_failure(self, qtbot, safety_manager):
        """Test recovery to SAFE when session is restored."""
        # Setup: Force UNSAFE by invalidating session
        safety_manager.set_session_valid(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Track signals
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Restore session
        safety_manager.set_session_valid(True)

        # Assert: Automatic recovery to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals
        assert True in enable_signals

    def test_recovery_from_power_limit_failure(self, qtbot, safety_manager):
        """Test recovery to SAFE when power limit is restored."""
        # Setup: Force UNSAFE by exceeding power limit
        safety_manager.set_power_limit_ok(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Track signals
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Restore power limit
        safety_manager.set_power_limit_ok(True)

        # Assert: Automatic recovery to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals
        assert True in enable_signals

    def test_partial_recovery_insufficient(self, qtbot, safety_manager):
        """Test that partial recovery (not all interlocks) keeps system UNSAFE."""
        # Setup: Fail all interlocks
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.set_session_valid(False)
        safety_manager.set_power_limit_ok(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Act: Restore only two out of three interlocks
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        # Power limit still failed

        # Assert: System remains UNSAFE
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False

    def test_full_recovery_after_multiple_failures(self, qtbot, safety_manager):
        """Test recovery to SAFE after restoring all failed interlocks."""
        # Setup: Fail all interlocks
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.set_session_valid(False)
        safety_manager.set_power_limit_ok(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Track state changes
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Restore all interlocks one by one
        safety_manager.set_gpio_interlock_status(True)
        assert safety_manager.state == SafetyState.UNSAFE  # Still unsafe

        safety_manager.set_session_valid(True)
        assert safety_manager.state == SafetyState.UNSAFE  # Still unsafe

        safety_manager.set_power_limit_ok(True)
        # Now all interlocks satisfied

        # Assert: Recovery to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals


class TestLaserEnablePermission:
    """Test laser_enable_permitted behavior during faults."""

    def test_laser_enable_false_immediately_on_fault(self, qtbot, safety_manager):
        """Test laser_enable_permitted becomes False immediately on fault."""
        # Start in SAFE with laser enabled
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True

        # Track laser enable changes
        enable_changes = []
        safety_manager.laser_enable_changed.connect(lambda e: enable_changes.append(e))

        # Act: Trigger fault
        safety_manager.set_gpio_interlock_status(False)

        # Assert: Immediate disable
        assert safety_manager.laser_enable_permitted is False
        assert len(enable_changes) == 1
        assert enable_changes[0] is False

    def test_laser_enable_false_during_treating(self, qtbot, safety_manager):
        """Test laser_enable_permitted becomes False even during TREATING."""
        # Setup: Start treatment (laser would be ON)
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING
        assert safety_manager.laser_enable_permitted is True

        # Track laser enable changes
        enable_changes = []
        safety_manager.laser_enable_changed.connect(lambda e: enable_changes.append(e))

        # Act: Trigger fault during treatment
        safety_manager.set_power_limit_ok(False)

        # Assert: Immediate disable even during active treatment
        assert safety_manager.laser_enable_permitted is False
        assert len(enable_changes) == 1
        assert enable_changes[0] is False

    def test_laser_enable_remains_false_until_all_interlocks_satisfied(self, qtbot, safety_manager):
        """Test laser_enable_permitted stays False until all interlocks satisfied."""
        # Setup: Fail multiple interlocks
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.set_session_valid(False)
        assert safety_manager.laser_enable_permitted is False

        # Track laser enable changes
        enable_changes = []
        safety_manager.laser_enable_changed.connect(lambda e: enable_changes.append(e))

        # Act: Restore one interlock (insufficient)
        safety_manager.set_gpio_interlock_status(True)

        # Assert: Laser enable still False (no signal emission)
        assert safety_manager.laser_enable_permitted is False
        assert len(enable_changes) == 0  # No change signal

        # Act: Restore remaining interlock
        safety_manager.set_session_valid(True)

        # Assert: Now laser enable becomes True
        assert safety_manager.laser_enable_permitted is True
        assert len(enable_changes) == 1
        assert enable_changes[0] is True


class TestFaultSignalEmission:
    """Test proper signal emission for fault events."""

    def test_state_changed_signal_on_fault(self, qtbot, safety_manager):
        """Test safety_state_changed signal emitted on fault."""
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Trigger fault
        safety_manager.set_gpio_interlock_status(False)

        # Assert: Signal emitted
        assert len(state_signals) == 1
        assert state_signals[0] == SafetyState.UNSAFE

    def test_safety_event_signal_on_fault(self, qtbot, safety_manager):
        """Test safety_event signal emitted with correct fault information."""
        event_signals = []
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Trigger fault
        safety_manager.set_session_valid(False)

        # Assert: Multiple events emitted (interlock + state change)
        assert len(event_signals) >= 2
        assert ("session", "INVALID") in event_signals
        assert ("state_change", "UNSAFE") in event_signals

    def test_laser_enable_changed_signal_on_fault(self, qtbot, safety_manager):
        """Test laser_enable_changed signal emitted on fault."""
        enable_signals = []
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Trigger fault
        safety_manager.set_power_limit_ok(False)

        # Assert: Signal emitted with False value
        assert len(enable_signals) == 1
        assert enable_signals[0] is False

    def test_all_signals_emitted_on_recovery(self, qtbot, safety_manager):
        """Test all recovery signals emitted when interlocks restored."""
        # Setup: Force UNSAFE
        safety_manager.set_gpio_interlock_status(False)

        # Track all signals
        state_signals = []
        event_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Recover
        safety_manager.set_gpio_interlock_status(True)

        # Assert: All recovery signals emitted
        assert SafetyState.SAFE in state_signals
        assert ("interlock_gpio", "SATISFIED") in event_signals
        assert ("state_change", "SAFE") in event_signals
        assert True in enable_signals


class TestRapidFaultCycles:
    """Test rapid fault/recovery cycles and edge cases."""

    def test_rapid_fault_recovery_cycles(self, qtbot, safety_manager):
        """Test rapid repeated fault/recovery cycles."""
        state_changes = []
        safety_manager.safety_state_changed.connect(lambda s: state_changes.append(s))

        # Act: Perform 5 rapid fault/recovery cycles
        for _ in range(5):
            safety_manager.set_gpio_interlock_status(False)
            assert safety_manager.state == SafetyState.UNSAFE
            safety_manager.set_gpio_interlock_status(True)
            assert safety_manager.state == SafetyState.SAFE

        # Assert: All state changes tracked
        assert len(state_changes) == 10  # 5 UNSAFE + 5 SAFE
        assert state_changes == [
            SafetyState.UNSAFE,
            SafetyState.SAFE,
            SafetyState.UNSAFE,
            SafetyState.SAFE,
            SafetyState.UNSAFE,
            SafetyState.SAFE,
            SafetyState.UNSAFE,
            SafetyState.SAFE,
            SafetyState.UNSAFE,
            SafetyState.SAFE,
        ]

    def test_fault_during_state_transition_attempt(self, qtbot, safety_manager):
        """Test fault occurring while attempting state transition."""
        # Setup: System in SAFE
        assert safety_manager.state == SafetyState.SAFE

        # Act: Fail interlock, then try to arm (should fail)
        safety_manager.set_gpio_interlock_status(False)
        result = safety_manager.arm_system()

        # Assert: Arming failed, system remains UNSAFE
        assert result is False
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False

    def test_multiple_faults_before_recovery(self, qtbot, safety_manager):
        """Test multiple different faults occurring before any recovery."""
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Trigger multiple faults in sequence
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        safety_manager.set_session_valid(False)
        assert safety_manager.state == SafetyState.UNSAFE

        safety_manager.set_power_limit_ok(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Assert: Only one UNSAFE transition (already in UNSAFE)
        assert len(state_signals) == 1
        assert state_signals[0] == SafetyState.UNSAFE

    def test_fault_and_recovery_from_different_interlocks(self, qtbot, safety_manager):
        """Test fault from one interlock, recovery from different one."""
        # Act: Fail GPIO
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Now fail session too
        safety_manager.set_session_valid(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Restore GPIO (but session still failed)
        safety_manager.set_gpio_interlock_status(True)
        assert safety_manager.state == SafetyState.UNSAFE  # Still unsafe

        # Restore session
        safety_manager.set_session_valid(True)

        # Assert: Now recovered
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
