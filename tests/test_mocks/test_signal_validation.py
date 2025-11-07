"""
Comprehensive tests for MockQObjectBase signal emission validation framework.

Tests signal tracking, validation, timing, sequencing, and statistics functionality.
"""

import sys
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication, pyqtSignal

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.mocks import MockQObjectBase


# Test mock with signals for demonstration
class TestMockWithSignals(MockQObjectBase):
    """Test mock that emits signals with logging."""

    # Define test signals
    value_changed = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    data_ready = pyqtSignal(int, str, bool)
    error_occurred = pyqtSignal(str)

    def emit_value_change(self, value: int) -> None:
        """Emit value_changed signal with logging."""
        self.value_changed.emit(value)
        self._log_signal_emission("value_changed", value)

    def emit_status_change(self, status: str) -> None:
        """Emit status_changed signal with logging."""
        self.status_changed.emit(status)
        self._log_signal_emission("status_changed", status)

    def emit_data_ready(self, count: int, name: str, flag: bool) -> None:
        """Emit data_ready signal with logging."""
        self.data_ready.emit(count, name, flag)
        self._log_signal_emission("data_ready", count, name, flag)

    def emit_error(self, message: str) -> None:
        """Emit error_occurred signal with logging."""
        self.error_occurred.emit(message)
        self._log_signal_emission("error_occurred", message)


@pytest.fixture
def qapp():
    """Create QCoreApplication for PyQt6 signal testing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def mock_with_signals(qapp):
    """Create test mock with signals."""
    mock = TestMockWithSignals()
    yield mock


# =============================================================================
# Signal Emission Logging Tests
# =============================================================================


def test_signal_logging_enabled_by_default(mock_with_signals):
    """Test signal logging is enabled by default."""
    assert mock_with_signals.enable_signal_logging is True


def test_log_signal_emission(mock_with_signals):
    """Test signal emission is logged."""
    mock_with_signals.emit_value_change(42)

    assert len(mock_with_signals.signal_log) == 1
    signal_name, args, timestamp = mock_with_signals.signal_log[0]
    assert signal_name == "value_changed"
    assert args == (42,)
    assert isinstance(timestamp, float)


def test_log_multiple_signal_emissions(mock_with_signals):
    """Test multiple signal emissions are logged."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")
    mock_with_signals.emit_value_change(20)

    assert len(mock_with_signals.signal_log) == 3
    assert mock_with_signals.signal_log[0][0] == "value_changed"
    assert mock_with_signals.signal_log[1][0] == "status_changed"
    assert mock_with_signals.signal_log[2][0] == "value_changed"


def test_log_signal_with_multiple_args(mock_with_signals):
    """Test logging signal with multiple arguments."""
    mock_with_signals.emit_data_ready(5, "test", True)

    signal_name, args, _ = mock_with_signals.signal_log[0]
    assert signal_name == "data_ready"
    assert args == (5, "test", True)


def test_signal_logging_can_be_disabled(mock_with_signals):
    """Test signal logging can be disabled."""
    mock_with_signals.enable_signal_logging = False

    mock_with_signals.emit_value_change(42)

    assert len(mock_with_signals.signal_log) == 0


# =============================================================================
# Signal Emission Query Tests
# =============================================================================


def test_get_all_signal_emissions(mock_with_signals):
    """Test getting all signal emissions."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")

    emissions = mock_with_signals.get_signal_emissions()

    assert len(emissions) == 2
    assert emissions[0][0] == "value_changed"
    assert emissions[1][0] == "status_changed"


def test_get_signal_emissions_filtered(mock_with_signals):
    """Test getting signal emissions filtered by name."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")
    mock_with_signals.emit_value_change(20)

    emissions = mock_with_signals.get_signal_emissions("value_changed")

    assert len(emissions) == 2
    assert all(e[0] == "value_changed" for e in emissions)


def test_get_signal_emission_count(mock_with_signals):
    """Test counting signal emissions."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_value_change(20)
    mock_with_signals.emit_status_change("active")

    assert mock_with_signals.get_signal_emission_count("value_changed") == 2
    assert mock_with_signals.get_signal_emission_count("status_changed") == 1
    assert mock_with_signals.get_signal_emission_count("error_occurred") == 0


def test_was_signal_emitted(mock_with_signals):
    """Test checking if signal was emitted."""
    mock_with_signals.emit_value_change(42)

    assert mock_with_signals.was_signal_emitted("value_changed") is True
    assert mock_with_signals.was_signal_emitted("status_changed") is False


def test_get_last_signal_args(mock_with_signals):
    """Test getting arguments from last signal emission."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_value_change(20)

    args = mock_with_signals.get_last_signal_args("value_changed")

    assert args == (20,)


def test_get_last_signal_args_never_emitted(mock_with_signals):
    """Test getting args for never-emitted signal returns None."""
    args = mock_with_signals.get_last_signal_args("value_changed")

    assert args is None


# =============================================================================
# Signal Timing Tests
# =============================================================================


def test_get_signal_timing(mock_with_signals):
    """Test getting signal emission timestamp."""
    start = time.time()
    mock_with_signals.emit_value_change(42)
    end = time.time()

    timestamp = mock_with_signals.get_signal_timing("value_changed")

    assert timestamp is not None
    assert start <= timestamp <= end


def test_get_signal_timing_never_emitted(mock_with_signals):
    """Test getting timing for never-emitted signal returns None."""
    timestamp = mock_with_signals.get_signal_timing("value_changed")

    assert timestamp is None


def test_get_signal_interval(mock_with_signals):
    """Test getting interval between signal emissions."""
    mock_with_signals.emit_value_change(10)
    time.sleep(0.1)
    mock_with_signals.emit_value_change(20)

    interval = mock_with_signals.get_signal_interval("value_changed")

    assert interval is not None
    assert interval >= 0.1
    assert interval < 0.2  # Allow some overhead


def test_get_signal_interval_insufficient_emissions(mock_with_signals):
    """Test getting interval with less than 2 emissions returns None."""
    mock_with_signals.emit_value_change(10)

    interval = mock_with_signals.get_signal_interval("value_changed")

    assert interval is None


def test_get_signal_interval_never_emitted(mock_with_signals):
    """Test getting interval for never-emitted signal returns None."""
    interval = mock_with_signals.get_signal_interval("value_changed")

    assert interval is None


# =============================================================================
# Signal Sequence Validation Tests
# =============================================================================


def test_verify_signal_sequence_correct_order(mock_with_signals):
    """Test verifying signals were emitted in correct sequence."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")
    mock_with_signals.emit_value_change(20)

    result = mock_with_signals.verify_signal_sequence(
        "value_changed", "status_changed", "value_changed"
    )

    assert result is True


def test_verify_signal_sequence_with_extra_signals(mock_with_signals):
    """Test sequence verification ignores extra signals."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_error("warning")  # Extra signal
    mock_with_signals.emit_status_change("active")

    result = mock_with_signals.verify_signal_sequence("value_changed", "status_changed")

    assert result is True


def test_verify_signal_sequence_wrong_order(mock_with_signals):
    """Test sequence verification fails with wrong order."""
    mock_with_signals.emit_status_change("active")
    mock_with_signals.emit_value_change(10)

    result = mock_with_signals.verify_signal_sequence("value_changed", "status_changed")

    assert result is False


def test_verify_signal_sequence_incomplete(mock_with_signals):
    """Test sequence verification fails when sequence incomplete."""
    mock_with_signals.emit_value_change(10)

    result = mock_with_signals.verify_signal_sequence(
        "value_changed", "status_changed", "value_changed"
    )

    assert result is False


def test_verify_signal_sequence_empty(mock_with_signals):
    """Test empty sequence verification always passes."""
    result = mock_with_signals.verify_signal_sequence()

    assert result is True


# =============================================================================
# Signal Parameter Validation Tests
# =============================================================================


def test_verify_signal_parameters_matching(mock_with_signals):
    """Test verifying signal was emitted with specific parameters."""
    mock_with_signals.emit_value_change(42)
    mock_with_signals.emit_value_change(100)

    result = mock_with_signals.verify_signal_parameters("value_changed", (42,))

    assert result is True


def test_verify_signal_parameters_multiple_args(mock_with_signals):
    """Test verifying signal parameters with multiple arguments."""
    mock_with_signals.emit_data_ready(5, "test", True)

    result = mock_with_signals.verify_signal_parameters("data_ready", (5, "test", True))

    assert result is True


def test_verify_signal_parameters_no_match(mock_with_signals):
    """Test parameter verification fails when no match."""
    mock_with_signals.emit_value_change(42)

    result = mock_with_signals.verify_signal_parameters("value_changed", (100,))

    assert result is False


def test_verify_signal_parameters_never_emitted(mock_with_signals):
    """Test parameter verification fails for never-emitted signal."""
    result = mock_with_signals.verify_signal_parameters("value_changed", (42,))

    assert result is False


# =============================================================================
# Signal Log Management Tests
# =============================================================================


def test_clear_signal_log(mock_with_signals):
    """Test clearing signal log."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")

    mock_with_signals.clear_signal_log()

    assert len(mock_with_signals.signal_log) == 0
    assert len(mock_with_signals._last_signal_time) == 0


def test_reset_clears_signal_log(mock_with_signals):
    """Test reset() clears signal log."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_status_change("active")

    mock_with_signals.reset()

    assert len(mock_with_signals.signal_log) == 0
    assert mock_with_signals.enable_signal_logging is True


# =============================================================================
# Signal Statistics Tests
# =============================================================================


def test_get_signal_statistics_initial(mock_with_signals):
    """Test signal statistics in initial state."""
    stats = mock_with_signals.get_signal_statistics()

    assert stats["total_emissions"] == 0
    assert stats["unique_signals"] == 0
    assert stats["signal_counts"] == {}
    assert stats["logging_enabled"] is True


def test_get_signal_statistics_with_emissions(mock_with_signals):
    """Test signal statistics with emissions."""
    mock_with_signals.emit_value_change(10)
    mock_with_signals.emit_value_change(20)
    mock_with_signals.emit_status_change("active")

    stats = mock_with_signals.get_signal_statistics()

    assert stats["total_emissions"] == 3
    assert stats["unique_signals"] == 2
    assert stats["signal_counts"]["value_changed"] == 2
    assert stats["signal_counts"]["status_changed"] == 1


def test_get_signal_statistics_logging_disabled(mock_with_signals):
    """Test signal statistics shows logging disabled."""
    mock_with_signals.enable_signal_logging = False

    stats = mock_with_signals.get_signal_statistics()

    assert stats["logging_enabled"] is False


# =============================================================================
# Integration Tests
# =============================================================================


def test_complex_signal_sequence(mock_with_signals):
    """Test complex signal sequence tracking and validation."""
    # Emit a complex sequence
    mock_with_signals.emit_status_change("initializing")
    time.sleep(0.05)
    mock_with_signals.emit_value_change(0)
    time.sleep(0.05)
    mock_with_signals.emit_status_change("running")
    time.sleep(0.05)
    mock_with_signals.emit_value_change(100)
    time.sleep(0.05)
    mock_with_signals.emit_status_change("complete")

    # Verify sequence
    assert mock_with_signals.verify_signal_sequence(
        "status_changed", "value_changed", "status_changed", "value_changed", "status_changed"
    )

    # Verify specific parameters
    assert mock_with_signals.verify_signal_parameters("status_changed", ("initializing",))
    assert mock_with_signals.verify_signal_parameters("value_changed", (100,))

    # Verify counts
    assert mock_with_signals.get_signal_emission_count("status_changed") == 3
    assert mock_with_signals.get_signal_emission_count("value_changed") == 2

    # Verify last emission
    assert mock_with_signals.get_last_signal_args("status_changed") == ("complete",)


def test_signal_tracking_with_qtbot(mock_with_signals, qtbot):
    """Test signal tracking works with pytest-qt."""
    # Use qtbot to wait for signal
    with qtbot.waitSignal(mock_with_signals.value_changed, timeout=1000):
        mock_with_signals.emit_value_change(42)

    # Verify signal was also logged
    assert mock_with_signals.was_signal_emitted("value_changed")
    assert mock_with_signals.get_last_signal_args("value_changed") == (42,)
