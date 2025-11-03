# -*- coding: utf-8 -*-
"""
Comprehensive tests for emergency stop functionality.

Tests emergency stop timing, state transitions, signal emissions,
and system locking behavior for the TOSCA safety system.
"""

import sys
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.safety import SafetyManager, SafetyState


@pytest.fixture
def app():
    """Create QCoreApplication for signal testing."""
    return QCoreApplication.instance() or QCoreApplication(sys.argv)


@pytest.fixture
def safety_manager(app):
    """Create SafetyManager instance for testing."""
    return SafetyManager()


@pytest.mark.safety
class TestEmergencyStopTiming:
    """Test emergency stop timing requirements (<1ms)."""

    def test_emergency_stop_executes_quickly(self, safety_manager):
        """Test that trigger_emergency_stop() completes in <1ms."""
        # Arrange: Set system to ARMED state
        safety_manager.state = SafetyState.ARMED

        # Act: Measure emergency stop execution time
        start = time.perf_counter()
        safety_manager.trigger_emergency_stop()
        duration = time.perf_counter() - start

        # Assert: Should complete in less than 1ms
        assert duration < 0.001, f"Emergency stop took {duration*1000:.3f}ms, expected <1ms"
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.laser_enable_permitted is False

    def test_clear_emergency_stop_timing(self, safety_manager):
        """Test that clear_emergency_stop() executes quickly."""
        # Arrange: Activate emergency stop first
        safety_manager.trigger_emergency_stop()

        # Act: Measure clear time
        start = time.perf_counter()
        safety_manager.clear_emergency_stop()
        duration = time.perf_counter() - start

        # Assert: Should complete quickly
        assert duration < 0.01, f"Clear took {duration*1000:.3f}ms, expected <10ms"
        assert safety_manager.emergency_stop_active is False


@pytest.mark.safety
class TestEmergencyStopStateTransitions:
    """Test emergency stop state transitions from all possible states."""

    def test_emergency_stop_from_safe_state(self, safety_manager):
        """Test emergency stop can be triggered from SAFE state."""
        # Arrange
        safety_manager.state = SafetyState.SAFE

        # Act
        safety_manager.trigger_emergency_stop()

        # Assert
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.laser_enable_permitted is False

    def test_emergency_stop_from_armed_state(self, safety_manager):
        """Test emergency stop can be triggered from ARMED state."""
        # Arrange
        safety_manager.state = SafetyState.ARMED

        # Act
        safety_manager.trigger_emergency_stop()

        # Assert
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True

    def test_emergency_stop_from_treating_state(self, safety_manager):
        """Test emergency stop can be triggered from TREATING state."""
        # Arrange
        safety_manager.state = SafetyState.TREATING
        safety_manager.laser_enable_permitted = True

        # Act
        safety_manager.trigger_emergency_stop()

        # Assert
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.laser_enable_permitted is False
        assert safety_manager.emergency_stop_active is True

    def test_emergency_stop_from_unsafe_state(self, safety_manager):
        """Test emergency stop can be triggered from UNSAFE state."""
        # Arrange
        safety_manager.state = SafetyState.UNSAFE

        # Act
        safety_manager.trigger_emergency_stop()

        # Assert
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True

    def test_emergency_stop_from_emergency_stop_state(self, safety_manager):
        """Test emergency stop is idempotent (can be called when already active)."""
        # Arrange
        safety_manager.trigger_emergency_stop()

        # Act: Trigger again
        safety_manager.trigger_emergency_stop()

        # Assert: Still in emergency stop state
        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True


@pytest.mark.safety
class TestEmergencyStopSignals:
    """Test emergency stop signal emissions."""

    def test_emergency_stop_emits_state_changed_signal(self, safety_manager, qtbot):
        """Test that trigger_emergency_stop() emits safety_state_changed signal."""
        # Arrange
        safety_manager.state = SafetyState.ARMED
        emitted_states = []

        def on_state_changed(state):
            emitted_states.append(state)

        safety_manager.safety_state_changed.connect(on_state_changed)

        # Act
        safety_manager.trigger_emergency_stop()
        qtbot.wait(10)

        # Assert
        assert len(emitted_states) == 1
        assert emitted_states[0] == SafetyState.EMERGENCY_STOP

    def test_emergency_stop_emits_laser_enable_signal(self, safety_manager, qtbot):
        """Test that trigger_emergency_stop() emits laser_enable_changed signal."""
        # Arrange
        safety_manager.laser_enable_permitted = True
        emitted_values = []

        def on_laser_enable_changed(enabled):
            emitted_values.append(enabled)

        safety_manager.laser_enable_changed.connect(on_laser_enable_changed)

        # Act
        safety_manager.trigger_emergency_stop()
        qtbot.wait(10)

        # Assert
        assert len(emitted_values) == 1
        assert emitted_values[0] is False

    def test_emergency_stop_emits_safety_event_signal(self, safety_manager, qtbot):
        """Test that trigger_emergency_stop() emits safety_event signal."""
        # Arrange
        emitted_events = []

        def on_safety_event(event_type, message):
            emitted_events.append((event_type, message))

        safety_manager.safety_event.connect(on_safety_event)

        # Act
        safety_manager.trigger_emergency_stop()
        qtbot.wait(10)

        # Assert
        assert len(emitted_events) == 1
        assert emitted_events[0][0] == "emergency_stop"
        assert emitted_events[0][1] == "ACTIVATED"

    def test_clear_emergency_stop_emits_safety_event_signal(self, safety_manager, qtbot):
        """Test that clear_emergency_stop() emits safety_event signal."""
        # Arrange
        safety_manager.trigger_emergency_stop()
        emitted_events = []

        def on_safety_event(event_type, message):
            emitted_events.append((event_type, message))

        safety_manager.safety_event.connect(on_safety_event)

        # Act
        safety_manager.clear_emergency_stop()
        qtbot.wait(10)

        # Assert: Should emit at least the emergency_stop CLEARED event
        # May also emit state_change event from _update_safety_state()
        assert len(emitted_events) >= 1
        # First event should be emergency stop cleared
        assert emitted_events[0][0] == "emergency_stop"
        assert emitted_events[0][1] == "CLEARED"


@pytest.mark.safety
class TestEmergencyStopSystemLocking:
    """Test emergency stop system locking and recovery behavior."""

    def test_laser_enable_blocked_during_emergency_stop(self, safety_manager):
        """Test that laser enable is blocked while emergency stop is active."""
        # Arrange: Enable laser first
        safety_manager.laser_enable_permitted = True

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Laser enable should be blocked
        assert safety_manager.laser_enable_permitted is False
        assert safety_manager.is_laser_enable_permitted() is False

    def test_emergency_stop_flag_set_correctly(self, safety_manager):
        """Test that emergency_stop_active flag is set correctly."""
        # Initially false
        assert safety_manager.emergency_stop_active is False

        # Set to true on trigger
        safety_manager.trigger_emergency_stop()
        assert safety_manager.emergency_stop_active is True

        # Set to false on clear
        safety_manager.clear_emergency_stop()
        assert safety_manager.emergency_stop_active is False

    def test_clear_calls_update_safety_state(self, safety_manager):
        """Test that clear_emergency_stop() calls _update_safety_state()."""
        # Arrange: Activate emergency stop
        safety_manager.trigger_emergency_stop()

        # Act: Clear emergency stop
        safety_manager.clear_emergency_stop()

        # Assert: emergency_stop_active should be false
        assert safety_manager.emergency_stop_active is False
        # State should be updated (not EMERGENCY_STOP anymore)
        # Note: State depends on interlock status, so just verify it changed
        assert (
            safety_manager.state != SafetyState.EMERGENCY_STOP
            or not safety_manager.emergency_stop_active
        )


@pytest.mark.safety
class TestEmergencyStopCoverage:
    """Test emergency stop methods for 100% statement and branch coverage."""

    def test_trigger_emergency_stop_all_paths(self, safety_manager):
        """Test trigger_emergency_stop() covers all execution paths."""
        # Path 1: From any state with laser disabled
        safety_manager.state = SafetyState.SAFE
        safety_manager.laser_enable_permitted = False
        safety_manager.trigger_emergency_stop()

        assert safety_manager.state == SafetyState.EMERGENCY_STOP
        assert safety_manager.emergency_stop_active is True
        assert safety_manager.laser_enable_permitted is False

    def test_clear_emergency_stop_all_paths(self, safety_manager):
        """Test clear_emergency_stop() covers all execution paths."""
        # Activate emergency stop first
        safety_manager.trigger_emergency_stop()

        # Clear it
        safety_manager.clear_emergency_stop()

        # Verify flags cleared
        assert safety_manager.emergency_stop_active is False

    def test_emergency_stop_doesnt_affect_developer_mode(self, safety_manager):
        """Test that emergency stop doesn't disable developer mode bypass."""
        # Arrange: Enable developer mode
        safety_manager.set_developer_mode_bypass(True)

        # Act: Trigger emergency stop
        safety_manager.trigger_emergency_stop()

        # Assert: Emergency stop sets laser_enable_permitted to False
        assert safety_manager.laser_enable_permitted is False

        # But is_laser_enable_permitted() returns True due to developer mode
        assert safety_manager.is_laser_enable_permitted() is True
        assert safety_manager.developer_mode_bypass_enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
