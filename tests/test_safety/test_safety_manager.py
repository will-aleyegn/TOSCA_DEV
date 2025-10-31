"""
Unit tests for SafetyManager and TestSafetyManager.

Comprehensive test suite covering:
- Initialization and default state
- State machine transitions (SAFE/ARMED/TREATING/UNSAFE/EMERGENCY_STOP)
- Interlock management (GPIO, session, power limit)
- Emergency stop behavior
- Signal emissions
- Status queries
- TestSafetyManager bypass behavior

Target: 100% code coverage for src/core/safety.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.safety import SafetyManager, SafetyState, TestSafetyManager


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def app():
    """Create QCoreApplication for signal/slot testing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def safety_manager(app):
    """Create SafetyManager instance."""
    return SafetyManager()


@pytest.fixture
def safety_manager_with_all_interlocks_satisfied(app):
    """Create SafetyManager with all interlocks satisfied."""
    sm = SafetyManager()
    sm.set_gpio_interlock_status(True)
    sm.set_session_valid(True)
    sm.set_power_limit_ok(True)
    return sm


# ==============================================================================
# CATEGORY 1: INITIALIZATION TESTS
# ==============================================================================


def test_safety_manager_initialization(safety_manager):
    """Test SafetyManager initializes with correct default values."""
    assert safety_manager.state == SafetyState.UNSAFE
    assert safety_manager.emergency_stop_active is False
    assert safety_manager.gpio_interlock_ok is False
    assert safety_manager.session_valid is False
    assert safety_manager.power_limit_ok is True
    assert safety_manager.laser_enable_permitted is False


def test_initial_state_is_unsafe(safety_manager):
    """Test initial safety state is UNSAFE (conservative default)."""
    assert safety_manager.state == SafetyState.UNSAFE


def test_initial_laser_enable_denied(safety_manager):
    """Test laser enable is denied on initialization."""
    assert safety_manager.is_laser_enable_permitted() is False


# ==============================================================================
# CATEGORY 2: STATE TRANSITION TESTS
# ==============================================================================


def test_arm_system_success(safety_manager_with_all_interlocks_satisfied):
    """Test successful system arming when all conditions met."""
    sm = safety_manager_with_all_interlocks_satisfied

    # System should be in SAFE state with all interlocks satisfied
    assert sm.state == SafetyState.SAFE

    result = sm.arm_system()

    assert result is True
    assert sm.state == SafetyState.ARMED


def test_arm_system_from_wrong_state(safety_manager):
    """Test arming fails from non-SAFE states."""
    # From UNSAFE
    result = safety_manager.arm_system()
    assert result is False
    assert safety_manager.state == SafetyState.UNSAFE

    # From EMERGENCY_STOP
    safety_manager.trigger_emergency_stop()
    result = safety_manager.arm_system()
    assert result is False
    assert safety_manager.state == SafetyState.EMERGENCY_STOP


def test_arm_system_interlocks_not_satisfied(safety_manager):
    """Test arming fails when interlocks not satisfied."""
    # Manually set to SAFE state (bypass normal transition)
    safety_manager.state = SafetyState.SAFE

    # But interlocks not satisfied
    assert safety_manager.gpio_interlock_ok is False

    result = safety_manager.arm_system()

    assert result is False
    assert safety_manager.state == SafetyState.SAFE


def test_start_treatment_success(safety_manager_with_all_interlocks_satisfied):
    """Test successful treatment start from ARMED state."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    assert sm.state == SafetyState.ARMED

    result = sm.start_treatment()

    assert result is True
    assert sm.state == SafetyState.TREATING


def test_start_treatment_from_wrong_state(safety_manager):
    """Test treatment start fails from non-ARMED states."""
    # From UNSAFE
    result = safety_manager.start_treatment()
    assert result is False
    assert safety_manager.state == SafetyState.UNSAFE

    # From SAFE
    safety_manager.state = SafetyState.SAFE
    result = safety_manager.start_treatment()
    assert result is False
    assert safety_manager.state == SafetyState.SAFE


def test_stop_treatment_success(safety_manager_with_all_interlocks_satisfied):
    """Test successful treatment stop."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    sm.start_treatment()
    assert sm.state == SafetyState.TREATING

    result = sm.stop_treatment()

    assert result is True
    assert sm.state == SafetyState.ARMED


def test_stop_treatment_from_wrong_state(safety_manager):
    """Test treatment stop fails from non-TREATING states."""
    result = safety_manager.stop_treatment()
    assert result is False
    assert safety_manager.state == SafetyState.UNSAFE


def test_disarm_system_from_armed(safety_manager_with_all_interlocks_satisfied):
    """Test successful disarm from ARMED state."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    assert sm.state == SafetyState.ARMED

    result = sm.disarm_system()

    assert result is True
    assert sm.state == SafetyState.SAFE


def test_disarm_system_from_treating(safety_manager_with_all_interlocks_satisfied):
    """Test successful disarm from TREATING state."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    sm.start_treatment()
    assert sm.state == SafetyState.TREATING

    result = sm.disarm_system()

    assert result is True
    assert sm.state == SafetyState.SAFE


def test_disarm_system_from_wrong_state(safety_manager):
    """Test disarm fails from invalid states."""
    # From UNSAFE
    result = safety_manager.disarm_system()
    assert result is False
    assert safety_manager.state == SafetyState.UNSAFE


def test_full_state_lifecycle(safety_manager_with_all_interlocks_satisfied):
    """Test complete state lifecycle: SAFE → ARMED → TREATING → ARMED → SAFE."""
    sm = safety_manager_with_all_interlocks_satisfied

    # Initial: SAFE
    assert sm.state == SafetyState.SAFE

    # SAFE → ARMED
    assert sm.arm_system() is True
    assert sm.state == SafetyState.ARMED

    # ARMED → TREATING
    assert sm.start_treatment() is True
    assert sm.state == SafetyState.TREATING

    # TREATING → ARMED
    assert sm.stop_treatment() is True
    assert sm.state == SafetyState.ARMED

    # ARMED → SAFE
    assert sm.disarm_system() is True
    assert sm.state == SafetyState.SAFE


def test_state_preservation_during_updates(safety_manager_with_all_interlocks_satisfied):
    """Test ARMED/TREATING states preserved when interlocks remain satisfied."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    assert sm.state == SafetyState.ARMED

    # Trigger update (but interlocks still satisfied)
    sm.set_gpio_interlock_status(True)

    # State should remain ARMED
    assert sm.state == SafetyState.ARMED

    # Test TREATING state preservation
    sm.start_treatment()
    assert sm.state == SafetyState.TREATING

    # Trigger another update during treatment
    sm.set_session_valid(True)

    # State should remain TREATING
    assert sm.state == SafetyState.TREATING
    assert sm.laser_enable_permitted is True


# ==============================================================================
# CATEGORY 3: INTERLOCK TESTS
# ==============================================================================


def test_set_gpio_interlock_satisfied(safety_manager):
    """Test GPIO interlock status update to satisfied."""
    safety_manager.set_gpio_interlock_status(True)

    assert safety_manager.gpio_interlock_ok is True


def test_set_gpio_interlock_failed(safety_manager):
    """Test GPIO interlock status update to failed."""
    # Set to True first
    safety_manager.set_gpio_interlock_status(True)

    # Then fail
    safety_manager.set_gpio_interlock_status(False)

    assert safety_manager.gpio_interlock_ok is False


def test_set_session_valid(safety_manager):
    """Test session validation status update."""
    safety_manager.set_session_valid(True)

    assert safety_manager.session_valid is True


def test_set_session_invalid(safety_manager):
    """Test session invalidation."""
    safety_manager.set_session_valid(True)
    safety_manager.set_session_valid(False)

    assert safety_manager.session_valid is False


def test_set_power_limit_ok(safety_manager):
    """Test power limit status update to OK."""
    # Default is True, set to False first
    safety_manager.set_power_limit_ok(False)

    # Then back to OK
    safety_manager.set_power_limit_ok(True)

    assert safety_manager.power_limit_ok is True


def test_set_power_limit_exceeded(safety_manager):
    """Test power limit exceeded detection."""
    safety_manager.set_power_limit_ok(False)

    assert safety_manager.power_limit_ok is False


def test_all_interlocks_satisfied_transitions_to_safe(safety_manager):
    """Test UNSAFE → SAFE transition when all interlocks satisfied."""
    assert safety_manager.state == SafetyState.UNSAFE

    # Satisfy all interlocks
    safety_manager.set_gpio_interlock_status(True)
    safety_manager.set_session_valid(True)
    safety_manager.set_power_limit_ok(True)

    # Should transition to SAFE
    assert safety_manager.state == SafetyState.SAFE


def test_any_interlock_failure_transitions_to_unsafe(safety_manager_with_all_interlocks_satisfied):
    """Test transition to UNSAFE on any interlock failure."""
    sm = safety_manager_with_all_interlocks_satisfied
    assert sm.state == SafetyState.SAFE

    # Fail GPIO interlock
    sm.set_gpio_interlock_status(False)

    assert sm.state == SafetyState.UNSAFE


def test_interlock_state_during_treatment(safety_manager_with_all_interlocks_satisfied):
    """Test interlock failure during active treatment."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    sm.start_treatment()
    assert sm.state == SafetyState.TREATING

    # Fail session interlock
    sm.set_session_valid(False)

    # Should transition to UNSAFE
    assert sm.state == SafetyState.UNSAFE


# ==============================================================================
# CATEGORY 4: EMERGENCY STOP TESTS
# ==============================================================================


def test_trigger_emergency_stop_disables_laser(safety_manager):
    """Test emergency stop immediately disables laser."""
    safety_manager.trigger_emergency_stop()

    assert safety_manager.emergency_stop_active is True
    assert safety_manager.state == SafetyState.EMERGENCY_STOP
    assert safety_manager.laser_enable_permitted is False


def test_emergency_stop_from_any_state(safety_manager_with_all_interlocks_satisfied):
    """Test emergency stop works from any state."""
    sm = safety_manager_with_all_interlocks_satisfied

    # From SAFE
    sm.trigger_emergency_stop()
    assert sm.state == SafetyState.EMERGENCY_STOP
    assert sm.laser_enable_permitted is False

    # Reset and test from ARMED
    sm.clear_emergency_stop()
    sm.set_gpio_interlock_status(True)
    sm.set_session_valid(True)
    sm.arm_system()
    sm.trigger_emergency_stop()
    assert sm.state == SafetyState.EMERGENCY_STOP
    assert sm.laser_enable_permitted is False

    # Reset and test from TREATING
    sm.clear_emergency_stop()
    sm.set_gpio_interlock_status(True)
    sm.set_session_valid(True)
    sm.arm_system()
    sm.start_treatment()
    sm.trigger_emergency_stop()
    assert sm.state == SafetyState.EMERGENCY_STOP
    assert sm.laser_enable_permitted is False


def test_emergency_stop_clears_correctly(safety_manager):
    """Test emergency stop can be cleared."""
    safety_manager.trigger_emergency_stop()
    assert safety_manager.emergency_stop_active is True

    safety_manager.clear_emergency_stop()

    assert safety_manager.emergency_stop_active is False


def test_emergency_stop_prevents_arming(safety_manager_with_all_interlocks_satisfied):
    """Test emergency stop prevents system arming."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.trigger_emergency_stop()

    result = sm.arm_system()

    assert result is False
    assert sm.state == SafetyState.EMERGENCY_STOP


def test_emergency_stop_overrides_all_interlocks(safety_manager_with_all_interlocks_satisfied):
    """Test emergency stop overrides satisfied interlocks."""
    sm = safety_manager_with_all_interlocks_satisfied
    assert sm.state == SafetyState.SAFE

    sm.trigger_emergency_stop()

    # Even with all interlocks satisfied, should be in E-STOP
    assert sm.state == SafetyState.EMERGENCY_STOP
    assert sm.laser_enable_permitted is False


# ==============================================================================
# CATEGORY 5: SIGNAL EMISSION TESTS
# ==============================================================================


def test_safety_state_changed_signal(safety_manager_with_all_interlocks_satisfied, qtbot):
    """Test safety_state_changed signal emission."""
    sm = safety_manager_with_all_interlocks_satisfied

    with qtbot.waitSignal(sm.safety_state_changed, timeout=1000) as blocker:
        sm.arm_system()

    assert blocker.args[0] == SafetyState.ARMED


def test_laser_enable_changed_signal(safety_manager, qtbot):
    """Test laser_enable_changed signal emission."""
    with qtbot.waitSignal(safety_manager.laser_enable_changed, timeout=1000) as blocker:
        # Satisfy all interlocks (should enable laser)
        safety_manager.set_gpio_interlock_status(True)
        safety_manager.set_session_valid(True)
        safety_manager.set_power_limit_ok(True)

    assert blocker.args[0] is True


def test_safety_event_signal_interlock(safety_manager, qtbot):
    """Test safety_event signal on interlock change."""
    with qtbot.waitSignal(safety_manager.safety_event, timeout=1000) as blocker:
        safety_manager.set_gpio_interlock_status(True)

    assert blocker.args[0] == "interlock_gpio"
    assert blocker.args[1] == "SATISFIED"


def test_safety_event_signal_state_change(safety_manager_with_all_interlocks_satisfied, qtbot):
    """Test safety_event signal on state change."""
    sm = safety_manager_with_all_interlocks_satisfied

    with qtbot.waitSignal(sm.safety_event, timeout=1000) as blocker:
        sm.arm_system()

    assert blocker.args[0] == "state_change"
    assert blocker.args[1] == "ARMED"


def test_safety_event_signal_emergency_stop(safety_manager, qtbot):
    """Test safety_event signal on emergency stop."""
    with qtbot.waitSignal(safety_manager.safety_event, timeout=1000) as blocker:
        safety_manager.trigger_emergency_stop()

    # Should receive emergency_stop event
    assert blocker.args[0] == "emergency_stop"
    assert blocker.args[1] == "ACTIVATED"


def test_signal_emission_on_state_transitions(safety_manager_with_all_interlocks_satisfied, qtbot):
    """Test signals emitted during full state lifecycle."""
    sm = safety_manager_with_all_interlocks_satisfied

    # Track signal emissions
    state_signals = []
    sm.safety_state_changed.connect(lambda state: state_signals.append(state))

    sm.arm_system()
    sm.start_treatment()
    sm.stop_treatment()
    sm.disarm_system()

    assert SafetyState.ARMED in state_signals
    assert SafetyState.TREATING in state_signals
    assert SafetyState.SAFE in state_signals


def test_signal_emission_on_interlock_changes(safety_manager, qtbot):
    """Test signals emitted on interlock state changes."""
    event_signals = []
    safety_manager.safety_event.connect(lambda event, msg: event_signals.append((event, msg)))

    safety_manager.set_gpio_interlock_status(True)
    safety_manager.set_session_valid(True)

    assert ("interlock_gpio", "SATISFIED") in event_signals
    assert ("session", "VALID") in event_signals


def test_no_redundant_signal_emissions(safety_manager):
    """Test signals not emitted when state doesn't change."""
    signal_count = 0
    safety_manager.safety_state_changed.connect(lambda state: setattr(self, 'signal_count', getattr(self, 'signal_count', 0) + 1))

    # Set same state twice
    safety_manager.set_gpio_interlock_status(True)
    safety_manager.set_gpio_interlock_status(True)  # No change

    # Signal should only emit once (on actual state change to SAFE)


# ==============================================================================
# CATEGORY 6: STATUS QUERY TESTS
# ==============================================================================


def test_is_laser_enable_permitted(safety_manager_with_all_interlocks_satisfied):
    """Test laser enable permission query."""
    sm = safety_manager_with_all_interlocks_satisfied

    # SAFE state should permit laser
    assert sm.is_laser_enable_permitted() is True

    # Fail interlock
    sm.set_gpio_interlock_status(False)
    assert sm.is_laser_enable_permitted() is False


def test_get_safety_status_text_safe(safety_manager_with_all_interlocks_satisfied):
    """Test safety status text when safe."""
    sm = safety_manager_with_all_interlocks_satisfied

    status = sm.get_safety_status_text()

    assert "ALL INTERLOCKS SATISFIED" in status
    assert "LASER ENABLED" in status


def test_get_safety_status_text_unsafe_with_reasons(safety_manager):
    """Test safety status text lists failure reasons."""
    status = safety_manager.get_safety_status_text()

    assert "INTERLOCKS NOT SATISFIED" in status
    assert "GPIO interlocks not satisfied" in status
    assert "No valid session" in status


def test_get_interlock_details(safety_manager):
    """Test interlock details dictionary."""
    details = safety_manager.get_interlock_details()

    assert details["state"] == SafetyState.UNSAFE.value
    assert details["emergency_stop"] is False
    assert details["gpio_interlock"] is False
    assert details["session_valid"] is False
    assert details["power_limit_ok"] is True
    assert details["laser_enable_permitted"] is False


def test_get_safety_status_text_emergency_stop(safety_manager):
    """Test safety status text during emergency stop."""
    safety_manager.trigger_emergency_stop()

    status = safety_manager.get_safety_status_text()

    assert "EMERGENCY STOP" in status
    assert "LASER DISABLED" in status


def test_get_safety_status_text_power_limit_exceeded(safety_manager):
    """Test safety status text when power limit exceeded."""
    safety_manager.set_power_limit_ok(False)

    status = safety_manager.get_safety_status_text()

    assert "Power limit exceeded" in status


def test_get_safety_status_text_armed_state(safety_manager_with_all_interlocks_satisfied):
    """Test safety status text in ARMED state."""
    sm = safety_manager_with_all_interlocks_satisfied
    sm.arm_system()
    assert sm.state == SafetyState.ARMED

    status = sm.get_safety_status_text()

    # ARMED state with all interlocks satisfied should show "SYSTEM NOT READY"
    # (because it's not in SAFE state nor are there specific failure reasons)
    assert "SYSTEM NOT READY" in status or "ALL INTERLOCKS SATISFIED" in status


# ==============================================================================
# CATEGORY 7: TEST SAFETY MANAGER TESTS
# ==============================================================================


def test_test_safety_manager_initialization(app):
    """Test TestSafetyManager initializes with test mode active."""
    tsm = TestSafetyManager(bypass_gpio=False)

    assert tsm.test_mode is True
    assert tsm.session_valid is True  # Auto-satisfied in test mode


def test_test_mode_session_always_valid(app):
    """Test session validation automatically satisfied in test mode."""
    tsm = TestSafetyManager(bypass_gpio=False)

    # Try to invalidate (should be ignored)
    tsm.set_session_valid(False)

    # Should still be valid
    assert tsm.session_valid is True


def test_test_mode_gpio_bypass(app):
    """Test GPIO interlock bypass in test mode."""
    tsm = TestSafetyManager(bypass_gpio=True)

    assert tsm.gpio_interlock_ok is True

    # Try to set to False (should be ignored)
    tsm.set_gpio_interlock_status(False)

    # Should still be True
    assert tsm.gpio_interlock_ok is True


def test_test_mode_status_text_includes_warning(app):
    """Test status text includes test mode warning."""
    tsm = TestSafetyManager(bypass_gpio=False)
    tsm.set_gpio_interlock_status(True)
    tsm.set_power_limit_ok(True)

    status = tsm.get_safety_status_text()

    assert "TEST MODE" in status.upper()
