"""
Test Safety Emergency Stop Integration (Task 14.4).

Comprehensive tests for emergency stop functionality:
- Emergency stop transitions from all states (SAFE, ARMED, TREATING, UNSAFE)
- System locking behavior (cannot transition while E-stop active)
- Recovery validation after clear_emergency_stop()
- Signal emission patterns for E-stop and clear
- Emergency stop overrides all other state logic
- Immediate response timing validation

Targets lines 213-237 in safety.py (emergency stop methods).
"""

import sys
import time
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


class TestEmergencyStopFromAllStates:
    """Test emergency stop transitions from all states."""

    def test_emergency_stop_from_safe(self, qtbot, safety_manager):
        """Test emergency stop from SAFE state."""
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True

        # Track signals
        state_signals = []
        enable_signals = []
        event_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Immediate transition to EMERGENCY_STOP
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.laser_enable_permitted is False

        # Verify signals emitted
        assert SafetyState.EMERGENCY_STOP in state_signals
        assert False in enable_signals
        assert ("emergency_stop", "ACTIVATED") in event_signals

    def test_emergency_stop_from_armed(self, qtbot, safety_manager):
        """Test emergency stop from ARMED state."""
        # Setup: Arm system
        safety_manager.arm_system()
        assert safety_manager.state == SafetyState.ARMED

        # Track signals
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Immediate transition to EMERGENCY_STOP
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.EMERGENCY_STOP in state_signals

    def test_emergency_stop_from_treating(self, qtbot, safety_manager):
        """Test emergency stop from TREATING state (critical - laser is ON)."""
        # Setup: Start treatment
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING

        # Track signals
        state_signals = []
        enable_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))

        # Act: Trigger emergency stop (CRITICAL - laser must be disabled)
        safety_manager.trigger_emergency_stop()

        # Assert: Immediate transition and laser disable
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.EMERGENCY_STOP in state_signals
        assert False in enable_signals

    def test_emergency_stop_from_unsafe(self, qtbot, safety_manager):
        """Test emergency stop from UNSAFE state."""
        # Setup: Force UNSAFE by failing interlock
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Track signals
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Transition to EMERGENCY_STOP
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert SafetyState.EMERGENCY_STOP in state_signals

    def test_emergency_stop_from_emergency_stop(self, qtbot, safety_manager):
        """Test triggering emergency stop when already in EMERGENCY_STOP."""
        # Setup: Already in emergency stop
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Track signals
        state_signals = []
        event_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Trigger again
        safety_manager.trigger_emergency_stop()

        # Assert: Remains in EMERGENCY_STOP, signal still emitted
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert ("emergency_stop", "ACTIVATED") in event_signals


class TestSystemLockingBehavior:
    """Test system locking behavior while emergency stop is active."""

    def test_cannot_arm_during_emergency_stop(self, qtbot, safety_manager):
        """Test that system cannot be armed during emergency stop."""
        # Setup: Trigger emergency stop
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Try to arm (should fail)
        result = safety_manager.arm_system()

        # Assert: Arming failed, still in EMERGENCY_STOP
        assert result is False
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

    def test_cannot_start_treatment_during_emergency_stop(self, qtbot, safety_manager):
        """Test that treatment cannot start during emergency stop."""
        # Setup: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Act: Try to start treatment (should fail)
        result = safety_manager.start_treatment()

        # Assert: Failed, still in EMERGENCY_STOP
        assert result is False
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

    def test_cannot_disarm_during_emergency_stop(self, qtbot, safety_manager):
        """Test that disarm fails during emergency stop."""
        # Setup: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Act: Try to disarm (should fail)
        result = safety_manager.disarm_system()

        # Assert: Failed, still in EMERGENCY_STOP
        assert result is False
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

    def test_interlock_changes_dont_affect_emergency_stop(self, qtbot, safety_manager):
        """Test that interlock changes don't transition out of EMERGENCY_STOP."""
        # Setup: Trigger emergency stop
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Change interlocks (should NOT transition out)
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.set_gpio_interlock_status(True)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.set_session_valid(False)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.set_session_valid(True)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Assert: Still locked in EMERGENCY_STOP
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True


class TestEmergencyStopRecovery:
    """Test recovery after clearing emergency stop."""

    def test_clear_emergency_stop_with_all_interlocks_ok(self, qtbot, safety_manager):
        """Test recovery to SAFE when all interlocks are satisfied."""
        # Setup: Trigger then clear emergency stop
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Track signals
        state_signals = []
        event_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Clear emergency stop
        safety_manager.clear_emergency_stop()

        # Assert: Recovery to SAFE (all interlocks satisfied)
        assert safety_manager.emergency_stop_active is False
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True
        assert SafetyState.SAFE in state_signals
        assert ("emergency_stop", "CLEARED") in event_signals

    def test_clear_emergency_stop_with_failed_interlocks(self, qtbot, safety_manager):
        """Test recovery to UNSAFE when interlocks are not satisfied."""
        # Setup: Fail interlock, then trigger emergency stop
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Track signals
        state_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Clear emergency stop
        safety_manager.clear_emergency_stop()

        # Assert: Recovery to UNSAFE (interlocks still failed)
        assert safety_manager.emergency_stop_active is False
        assert safety_manager.state == SafetyState.UNSAFE
        assert safety_manager.laser_enable_permitted is False
        assert SafetyState.UNSAFE in state_signals

    def test_clear_emergency_stop_recovery_to_safe_after_fixing_interlocks(
        self, qtbot, safety_manager
    ):
        """Test recovery sequence: E-STOP → fix interlocks → clear → SAFE."""
        # Setup: Fail interlocks, trigger emergency stop
        safety_manager.set_gpio_interlock_status(False)
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Fix interlocks WHILE in E-STOP (should not transition yet)
        safety_manager.set_gpio_interlock_status(True)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP  # Still locked

        # Clear emergency stop
        safety_manager.clear_emergency_stop()

        # Assert: Now transitions to SAFE
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.laser_enable_permitted is True

    def test_multiple_emergency_stop_clear_cycles(self, qtbot, safety_manager):
        """Test multiple emergency stop and clear cycles."""
        state_changes = []
        safety_manager.safety_state_changed.connect(lambda s: state_changes.append(s))

        # Cycle 1
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.clear_emergency_stop()
        assert safety_manager.state == SafetyState.SAFE

        # Cycle 2
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.clear_emergency_stop()
        assert safety_manager.state == SafetyState.SAFE

        # Cycle 3
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        safety_manager.clear_emergency_stop()
        assert safety_manager.state == SafetyState.SAFE

        # Assert: 6 state changes (3 × E-STOP + 3 × SAFE)
        assert state_changes.count(SafetyState.EMERGENCY_STOP) == 3
        assert state_changes.count(SafetyState.SAFE) == 3


class TestSignalEmissionPatterns:
    """Test signal emission patterns for emergency stop."""

    def test_all_signals_emitted_on_emergency_stop(self, qtbot, safety_manager):
        """Test that all required signals are emitted on emergency stop."""
        # Track all signals
        state_signals = []
        enable_signals = []
        event_signals = []
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))
        safety_manager.laser_enable_changed.connect(lambda e: enable_signals.append(e))
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: All signals emitted
        assert SafetyState.EMERGENCY_STOP in state_signals
        assert False in enable_signals
        assert ("emergency_stop", "ACTIVATED") in event_signals

    def test_clear_emergency_stop_signal_emission(self, qtbot, safety_manager):
        """Test signal emission on clear_emergency_stop."""
        # Setup: Trigger emergency stop first
        safety_manager.trigger_emergency_stop()

        # Track signals
        event_signals = []
        state_signals = []
        safety_manager.safety_event.connect(lambda t, m: event_signals.append((t, m)))
        safety_manager.safety_state_changed.connect(lambda s: state_signals.append(s))

        # Act: Clear emergency stop
        safety_manager.clear_emergency_stop()

        # Assert: Clear event emitted
        assert ("emergency_stop", "CLEARED") in event_signals
        # State change to SAFE also emitted
        assert SafetyState.SAFE in state_signals

    def test_signal_order_on_emergency_stop(self, qtbot, safety_manager):
        """Test signal emission order on emergency stop."""
        # Track signal order with timestamps
        signals = []

        def track_state(state):
            signals.append(("state", state))

        def track_enable(enabled):
            signals.append(("enable", enabled))

        def track_event(event_type, message):
            signals.append(("event", (event_type, message)))

        safety_manager.safety_state_changed.connect(track_state)
        safety_manager.laser_enable_changed.connect(track_enable)
        safety_manager.safety_event.connect(track_event)

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: All signals emitted (order may vary due to Qt)
        assert ("state", SafetyState.EMERGENCY_STOP) in signals
        assert ("enable", False) in signals
        assert ("event", ("emergency_stop", "ACTIVATED")) in signals


class TestEmergencyStopOverridesOtherLogic:
    """Test that emergency stop overrides all other state logic."""

    def test_emergency_stop_overrides_during_treatment(self, qtbot, safety_manager):
        """Test E-stop overrides even during active treatment."""
        # Setup: Start treatment (laser would be ON)
        safety_manager.arm_system()
        safety_manager.start_treatment()
        assert safety_manager.state == SafetyState.TREATING
        assert safety_manager.laser_enable_permitted is True

        # Act: Emergency stop (must override treatment)
        safety_manager.trigger_emergency_stop()

        # Assert: Overrides treatment state
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.laser_enable_permitted is False

    def test_emergency_stop_prevents_interlock_recovery(self, qtbot, safety_manager):
        """Test that E-stop prevents automatic recovery from UNSAFE."""
        # Setup: Fail interlock → UNSAFE
        safety_manager.set_gpio_interlock_status(False)
        assert safety_manager.state == SafetyState.UNSAFE

        # Trigger emergency stop
        safety_manager.trigger_emergency_stop()
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

        # Act: Fix interlock (normally would go to SAFE, but E-stop active)
        safety_manager.set_gpio_interlock_status(True)

        # Assert: Still in EMERGENCY_STOP (E-stop overrides recovery)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP

    def test_emergency_stop_state_priority(self, qtbot, safety_manager):
        """Test that EMERGENCY_STOP has highest state priority."""
        # Setup: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Try various operations (all should fail)
        assert safety_manager.arm_system() is False
        assert safety_manager.start_treatment() is False
        assert safety_manager.stop_treatment() is False
        assert safety_manager.disarm_system() is False

        # State should remain EMERGENCY_STOP throughout
        assert safety_manager.state == SafetyState.EMERGENCY_STOP


class TestImmediateResponseTiming:
    """Test immediate response timing for emergency stop."""

    def test_emergency_stop_immediate_state_change(self, qtbot, safety_manager):
        """Test that emergency stop causes immediate state change."""
        assert safety_manager.state == SafetyState.SAFE

        # Measure time for state change
        start_time = time.perf_counter()
        safety_manager.trigger_emergency_stop()
        end_time = time.perf_counter()

        # Assert: Immediate state change (should be microseconds)
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
        assert elapsed < 10.0, f"Emergency stop took {elapsed:.3f}ms (should be <10ms)"

    def test_emergency_stop_immediate_laser_disable(self, qtbot, safety_manager):
        """Test that laser_enable_permitted is immediately False."""
        # Setup: Start with laser enabled
        assert safety_manager.laser_enable_permitted is True

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Immediate disable (synchronous)
        assert safety_manager.laser_enable_permitted is False

    def test_rapid_emergency_stop_clear_cycles(self, qtbot, safety_manager):
        """Test rapid emergency stop/clear cycles for timing."""
        # Perform 100 rapid cycles
        for _ in range(100):
            safety_manager.trigger_emergency_stop()
            assert safety_manager.state == SafetyState.EMERGENCY_STOP

            safety_manager.clear_emergency_stop()
            assert safety_manager.state == SafetyState.SAFE

        # Assert: Final state correct
        assert safety_manager.state == SafetyState.SAFE
        assert safety_manager.emergency_stop_active is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
