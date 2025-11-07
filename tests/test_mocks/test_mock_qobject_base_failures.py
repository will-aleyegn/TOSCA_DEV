"""
Comprehensive tests for MockQObjectBase advanced failure simulation.

Tests all advanced failure modes including:
- Intermittent failures
- Timeout simulation
- Device busy states
- Communication errors
- Power supply failures
- Calibration failures
- Hardware limit violations
- Error state persistence
- Failure statistics
"""

import sys
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.mocks import FailureMode, MockQObjectBase


@pytest.fixture
def qapp():
    """Create QCoreApplication for PyQt6."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def mock_base(qapp):
    """Create MockQObjectBase instance."""
    mock = MockQObjectBase()
    yield mock


# =============================================================================
# Basic Failure Mode Tests (Backward Compatibility)
# =============================================================================


def test_simulate_connection_failure_backward_compat(mock_base):
    """Test basic connection failure simulation (backward compatible)."""
    mock_base.simulate_connection_failure = True

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert error_msg == "Connection failed (simulated)"


def test_simulate_operation_error_backward_compat(mock_base):
    """Test basic operation error simulation (backward compatible)."""
    mock_base.simulate_operation_error = True
    mock_base.error_message = "Custom error message"

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert error_msg == "Custom error message"


def test_response_delay(mock_base):
    """Test configurable response delay."""
    mock_base.response_delay_s = 0.1

    start = time.time()
    mock_base._apply_delay()
    elapsed = time.time() - start

    assert elapsed >= 0.1
    assert elapsed < 0.2  # Allow some overhead


# =============================================================================
# Intermittent Failure Tests
# =============================================================================


def test_intermittent_failure_probability_zero(mock_base):
    """Test intermittent failures never occur with 0% probability."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 0.0

    # Run multiple times - should never fail
    for _ in range(100):
        should_fail, _ = mock_base._should_fail()
        assert should_fail is False


def test_intermittent_failure_probability_one(mock_base):
    """Test intermittent failures always occur with 100% probability."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 1.0

    # Run multiple times - should always fail
    for i in range(10):
        should_fail, error_msg = mock_base._should_fail()
        assert should_fail is True
        assert f"Intermittent failure #{i+1}" in error_msg


def test_intermittent_failure_probability_half(mock_base):
    """Test intermittent failures occur approximately 50% of the time."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 0.5

    # Run many times and count failures
    failure_count = 0
    trials = 1000
    for _ in range(trials):
        should_fail, _ = mock_base._should_fail()
        if should_fail:
            failure_count += 1

    # Should be approximately 50% (allow 10% variance)
    assert 400 <= failure_count <= 600


def test_intermittent_failure_increments_counter(mock_base):
    """Test intermittent failures increment failure counter."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 1.0

    for _ in range(5):
        mock_base._should_fail()

    stats = mock_base.get_failure_statistics()
    assert stats["failure_count"] == 5


# =============================================================================
# Device Busy State Tests
# =============================================================================


def test_device_busy_state(mock_base):
    """Test device busy state prevents operations."""
    mock_base.failure_mode = FailureMode.DEVICE_BUSY
    mock_base.device_busy_duration_s = 0.5
    mock_base._set_busy_state()

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert "Device busy" in error_msg
    assert "available in" in error_msg


def test_device_busy_state_clears_after_duration(mock_base):
    """Test device becomes available after busy duration."""
    mock_base.failure_mode = FailureMode.DEVICE_BUSY
    mock_base.device_busy_duration_s = 0.2
    mock_base._set_busy_state()

    # Should be busy initially
    should_fail, _ = mock_base._should_fail()
    assert should_fail is True

    # Wait for busy duration
    time.sleep(0.25)

    # Should be available now
    should_fail, _ = mock_base._should_fail()
    assert should_fail is False


def test_device_busy_shows_remaining_time(mock_base):
    """Test device busy message shows remaining time."""
    mock_base.failure_mode = FailureMode.DEVICE_BUSY
    mock_base.device_busy_duration_s = 1.0
    mock_base._set_busy_state()

    _, error_msg = mock_base._should_fail()

    # Should show approximately 1.0s remaining
    assert "available in 1.0s" in error_msg or "available in 0.9s" in error_msg


# =============================================================================
# Timeout Simulation Tests
# =============================================================================


def test_timeout_before_threshold(mock_base):
    """Test operation does not timeout before threshold."""
    mock_base.failure_mode = FailureMode.TIMEOUT
    mock_base.timeout_threshold_s = 1.0
    mock_base._start_operation()

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


def test_timeout_after_threshold(mock_base):
    """Test operation times out after threshold."""
    mock_base.failure_mode = FailureMode.TIMEOUT
    mock_base.timeout_threshold_s = 0.1
    mock_base._start_operation()

    time.sleep(0.15)

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert "Operation timeout" in error_msg
    assert "threshold: 0.1s" in error_msg


def test_timeout_cleared_by_end_operation(mock_base):
    """Test timeout is cleared when operation ends."""
    mock_base.failure_mode = FailureMode.TIMEOUT
    mock_base.timeout_threshold_s = 0.1
    mock_base._start_operation()

    time.sleep(0.15)
    mock_base._end_operation()

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False  # Operation ended, no timeout


def test_timeout_shows_elapsed_time(mock_base):
    """Test timeout message shows elapsed time."""
    mock_base.failure_mode = FailureMode.TIMEOUT
    mock_base.timeout_threshold_s = 0.1
    mock_base._start_operation()

    time.sleep(0.2)

    _, error_msg = mock_base._should_fail()

    assert "after 0.2s" in error_msg or "after 0.3s" in error_msg


# =============================================================================
# Power Supply Failure Tests
# =============================================================================


def test_power_supply_sufficient(mock_base):
    """Test operation succeeds with sufficient power."""
    mock_base.failure_mode = FailureMode.POWER_FAILURE
    mock_base.power_supply_voltage_v = 12.0
    mock_base.min_power_voltage_v = 10.0

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


def test_power_supply_insufficient(mock_base):
    """Test operation fails with insufficient power."""
    mock_base.failure_mode = FailureMode.POWER_FAILURE
    mock_base.power_supply_voltage_v = 9.0
    mock_base.min_power_voltage_v = 10.0

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert "Insufficient power" in error_msg
    assert "9.0V" in error_msg
    assert "minimum: 10.0V" in error_msg


def test_power_supply_exact_minimum(mock_base):
    """Test operation succeeds at exact minimum voltage."""
    mock_base.failure_mode = FailureMode.POWER_FAILURE
    mock_base.power_supply_voltage_v = 10.0
    mock_base.min_power_voltage_v = 10.0

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


# =============================================================================
# Calibration Failure Tests
# =============================================================================


def test_calibration_not_required(mock_base):
    """Test operation succeeds when calibration not required."""
    mock_base.failure_mode = FailureMode.CALIBRATION_ERROR
    mock_base.calibration_required = False

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


def test_calibration_required(mock_base):
    """Test operation fails when calibration required."""
    mock_base.failure_mode = FailureMode.CALIBRATION_ERROR
    mock_base.calibration_required = True

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert "Calibration required" in error_msg


def test_perform_calibration_success(mock_base):
    """Test successful calibration."""
    mock_base.calibration_required = True

    result = mock_base.perform_calibration()

    assert result is True
    assert mock_base.calibration_required is False


def test_perform_calibration_fails_in_calibration_error_mode(mock_base):
    """Test calibration fails when in calibration error mode."""
    mock_base.failure_mode = FailureMode.CALIBRATION_ERROR

    result = mock_base.perform_calibration()

    assert result is False


def test_calibration_shows_time_since_last(mock_base):
    """Test calibration error shows time since last calibration."""
    mock_base.failure_mode = FailureMode.CALIBRATION_ERROR
    mock_base.calibration_required = True
    mock_base._last_calibration_time = time.time() - 100  # 100s ago

    _, error_msg = mock_base._should_fail()

    assert "last calibrated" in error_msg
    assert "100s ago" in error_msg or "99s ago" in error_msg


# =============================================================================
# Communication Error Tests
# =============================================================================


def test_communication_error(mock_base):
    """Test serial communication error simulation."""
    mock_base.failure_mode = FailureMode.COMMUNICATION_ERROR

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert "Serial communication error" in error_msg


# =============================================================================
# Hardware Limit Violation Tests
# =============================================================================


def test_hardware_limits_not_configured(mock_base):
    """Test parameter passes when no limits configured."""
    within_limits, _ = mock_base._check_hardware_limits("power", 5.0)

    assert within_limits is True


def test_hardware_limits_within_range(mock_base):
    """Test parameter within configured limits."""
    mock_base.hardware_limits["power"] = (0.0, 10.0)

    within_limits, _ = mock_base._check_hardware_limits("power", 5.0)

    assert within_limits is True


def test_hardware_limits_below_minimum(mock_base):
    """Test parameter below minimum limit."""
    mock_base.hardware_limits["power"] = (0.0, 10.0)

    within_limits, error_msg = mock_base._check_hardware_limits("power", -1.0)

    assert within_limits is False
    assert "power -1.0 below minimum 0.0" in error_msg


def test_hardware_limits_above_maximum(mock_base):
    """Test parameter above maximum limit."""
    mock_base.hardware_limits["power"] = (0.0, 10.0)

    within_limits, error_msg = mock_base._check_hardware_limits("power", 15.0)

    assert within_limits is False
    assert "power 15.0 above maximum 10.0" in error_msg


def test_hardware_limits_at_exact_boundaries(mock_base):
    """Test parameter at exact min/max boundaries."""
    mock_base.hardware_limits["power"] = (0.0, 10.0)

    within_limits_min, _ = mock_base._check_hardware_limits("power", 0.0)
    within_limits_max, _ = mock_base._check_hardware_limits("power", 10.0)

    assert within_limits_min is True
    assert within_limits_max is True


# =============================================================================
# Error State Persistence Tests
# =============================================================================


def test_error_state_not_persistent_by_default(mock_base):
    """Test errors do not persist by default."""
    mock_base.simulate_operation_error = True
    mock_base._should_fail()

    # Disable error
    mock_base.simulate_operation_error = False

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


def test_error_state_persists_when_enabled(mock_base):
    """Test errors persist when persistence enabled."""
    mock_base.persist_error_state = True
    mock_base._set_error_state("Persistent error")

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert error_msg == "Persistent error"


def test_error_state_survives_mode_changes(mock_base):
    """Test persistent error survives failure mode changes."""
    mock_base.persist_error_state = True
    mock_base._set_error_state("Sticky error")

    # Change failure mode
    mock_base.failure_mode = FailureMode.DEVICE_BUSY

    should_fail, error_msg = mock_base._should_fail()

    assert should_fail is True
    assert error_msg == "Sticky error"


def test_error_state_can_be_cleared(mock_base):
    """Test persistent error can be cleared."""
    mock_base.persist_error_state = True
    mock_base._set_error_state("Error to clear")

    mock_base._clear_error_state()

    should_fail, _ = mock_base._should_fail()

    assert should_fail is False


def test_error_state_increments_failure_count(mock_base):
    """Test setting error state increments failure counter."""
    mock_base.persist_error_state = True

    mock_base._set_error_state("Error 1")
    mock_base._set_error_state("Error 2")

    stats = mock_base.get_failure_statistics()
    assert stats["failure_count"] == 2


# =============================================================================
# Failure Statistics Tests
# =============================================================================


def test_failure_statistics_initial_state(mock_base):
    """Test failure statistics in initial state."""
    stats = mock_base.get_failure_statistics()

    assert stats["failure_count"] == 0
    assert stats["failure_mode"] == "none"
    assert stats["current_error_state"] is None
    assert stats["device_busy"] is False
    assert stats["operation_in_progress"] is False
    assert stats["calibration_required"] is False
    assert stats["power_voltage_v"] == 12.0
    assert stats["call_count"] == 0


def test_failure_statistics_tracks_failures(mock_base):
    """Test failure statistics tracks failure count."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 1.0

    for _ in range(5):
        mock_base._should_fail()

    stats = mock_base.get_failure_statistics()
    assert stats["failure_count"] == 5


def test_failure_statistics_tracks_mode(mock_base):
    """Test failure statistics tracks current failure mode."""
    mock_base.failure_mode = FailureMode.TIMEOUT

    stats = mock_base.get_failure_statistics()

    assert stats["failure_mode"] == "timeout"


def test_failure_statistics_tracks_busy_state(mock_base):
    """Test failure statistics tracks device busy state."""
    mock_base.device_busy_duration_s = 1.0
    mock_base._set_busy_state()

    stats = mock_base.get_failure_statistics()

    assert stats["device_busy"] is True


def test_failure_statistics_tracks_operation(mock_base):
    """Test failure statistics tracks operation in progress."""
    mock_base._start_operation()

    stats = mock_base.get_failure_statistics()

    assert stats["operation_in_progress"] is True


# =============================================================================
# Reset Tests
# =============================================================================


def test_reset_clears_all_failure_modes(mock_base):
    """Test reset clears all failure mode configurations."""
    # Set up various failure modes
    mock_base.failure_mode = FailureMode.TIMEOUT
    mock_base.intermittent_failure_probability = 0.5
    mock_base.calibration_required = True
    mock_base.power_supply_voltage_v = 5.0
    mock_base._set_busy_state()
    mock_base._start_operation()
    mock_base._set_error_state("Test error")
    mock_base.persist_error_state = True

    mock_base.reset()

    # All should be reset to defaults
    assert mock_base.failure_mode == FailureMode.NONE
    assert mock_base.intermittent_failure_probability == 0.0
    assert mock_base.calibration_required is False
    assert mock_base.power_supply_voltage_v == 12.0
    assert mock_base.current_error_state is None
    assert mock_base.persist_error_state is False
    assert len(mock_base.call_log) == 0


def test_reset_clears_failure_statistics(mock_base):
    """Test reset clears failure statistics."""
    mock_base.failure_mode = FailureMode.INTERMITTENT_FAILURE
    mock_base.intermittent_failure_probability = 1.0

    for _ in range(10):
        mock_base._should_fail()

    mock_base.reset()

    stats = mock_base.get_failure_statistics()
    assert stats["failure_count"] == 0


# =============================================================================
# Call Logging Tests
# =============================================================================


def test_call_logging(mock_base):
    """Test method call logging."""
    mock_base._log_call("test_method", param1="value1", param2=42)

    assert len(mock_base.call_log) == 1
    assert mock_base.call_log[0] == ("test_method", {"param1": "value1", "param2": 42})


def test_call_logging_multiple_calls(mock_base):
    """Test logging multiple method calls."""
    mock_base._log_call("method1")
    mock_base._log_call("method2", arg="test")
    mock_base._log_call("method3", x=1, y=2)

    assert len(mock_base.call_log) == 3
    assert mock_base.call_log[0] == ("method1", {})
    assert mock_base.call_log[1] == ("method2", {"arg": "test"})
    assert mock_base.call_log[2] == ("method3", {"x": 1, "y": 2})
