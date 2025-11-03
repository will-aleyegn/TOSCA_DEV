"""
Unit tests for MockTECController.

Validates that the mock correctly simulates TEC behavior including:
- Connection/disconnection
- Temperature setpoint control
- Output enable/disable
- Thermal lag simulation
- Safety limit validation
- Signal emission
"""

import sys
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.mocks import MockTECController


@pytest.fixture
def qapp():
    """Create QCoreApplication for PyQt6 signal testing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app
    # No cleanup needed - QCoreApplication persists


@pytest.fixture
def mock_tec(qapp):
    """Create MockTECController instance."""
    tec = MockTECController()
    yield tec
    # Cleanup
    if tec.is_connected:
        tec.disconnect()


# =============================================================================
# Connection Tests
# =============================================================================


def test_initial_state(mock_tec):
    """Test mock starts in clean disconnected state."""
    assert mock_tec.is_connected is False
    assert mock_tec.is_output_enabled is False
    assert mock_tec.temperature_setpoint_c == 25.0
    assert mock_tec._temperature_reading_c == 25.0
    assert len(mock_tec.call_log) == 0


def test_connect_success(mock_tec):
    """Test successful connection."""
    result = mock_tec.connect(com_port="COM9", baudrate=38400)

    assert result is True
    assert mock_tec.is_connected is True
    assert ("connect", {"com_port": "COM9", "baudrate": 38400}) in mock_tec.call_log


def test_connect_failure_simulation(mock_tec):
    """Test simulated connection failure."""
    mock_tec.simulate_connection_failure = True

    result = mock_tec.connect()

    assert result is False
    assert mock_tec.is_connected is False


def test_disconnect(mock_tec):
    """Test disconnection disables output and clears connection."""
    mock_tec.connect()
    mock_tec.set_output(True)

    mock_tec.disconnect()

    assert mock_tec.is_connected is False
    assert mock_tec.is_output_enabled is False


# =============================================================================
# Temperature Control Tests
# =============================================================================


def test_set_temperature_success(mock_tec):
    """Test setting temperature setpoint within limits."""
    mock_tec.connect()

    result = mock_tec.set_temperature(30.0)

    assert result is True
    assert mock_tec.temperature_setpoint_c == 30.0
    assert ("set_temperature", {"temperature_c": 30.0}) in mock_tec.call_log


def test_set_temperature_above_max_limit(mock_tec):
    """Test temperature above maximum limit is rejected."""
    mock_tec.connect()

    result = mock_tec.set_temperature(40.0)  # Above max 35°C

    assert result is False
    assert mock_tec.temperature_setpoint_c == 25.0  # Unchanged


def test_set_temperature_below_min_limit(mock_tec):
    """Test temperature below minimum limit is rejected."""
    mock_tec.connect()

    result = mock_tec.set_temperature(10.0)  # Below min 15°C

    assert result is False
    assert mock_tec.temperature_setpoint_c == 25.0  # Unchanged


def test_set_temperature_requires_connection(mock_tec):
    """Test temperature setpoint requires connection."""
    result = mock_tec.set_temperature(30.0)

    assert result is False


def test_read_temperature_when_connected(mock_tec):
    """Test reading temperature when connected."""
    mock_tec.connect()

    temp = mock_tec.read_temperature()

    assert temp is not None
    assert temp == 25.0  # Initial ambient


def test_read_temperature_when_disconnected(mock_tec):
    """Test reading temperature returns None when disconnected."""
    temp = mock_tec.read_temperature()

    assert temp is None


# =============================================================================
# Output Control Tests
# =============================================================================


def test_set_output_enable(mock_tec):
    """Test enabling TEC output."""
    mock_tec.connect()
    mock_tec.set_temperature(20.0)

    result = mock_tec.set_output(True)

    assert result is True
    assert mock_tec.is_output_enabled is True
    # Should have non-zero current when controlling temperature
    assert mock_tec._current_reading_a > 0.0


def test_set_output_disable(mock_tec):
    """Test disabling TEC output."""
    mock_tec.connect()
    mock_tec.set_output(True)

    result = mock_tec.set_output(False)

    assert result is True
    assert mock_tec.is_output_enabled is False
    assert mock_tec._current_reading_a == 0.0
    assert mock_tec._voltage_reading_v == 0.0


def test_set_output_requires_connection(mock_tec):
    """Test output control requires connection."""
    result = mock_tec.set_output(True)

    assert result is False


def test_set_output_updates_current_and_voltage(mock_tec):
    """Test enabling output updates current and voltage readings."""
    mock_tec.connect()
    mock_tec.set_temperature(20.0)  # 5°C below ambient

    mock_tec.set_output(True)

    # Should have current/voltage based on temperature error
    assert mock_tec._current_reading_a > 0.0
    assert mock_tec._voltage_reading_v > 0.0
    assert mock_tec._voltage_reading_v == pytest.approx(mock_tec._current_reading_a * 1.5)


# =============================================================================
# Current and Voltage Reading Tests
# =============================================================================


def test_read_current_when_connected(mock_tec):
    """Test reading TEC current."""
    mock_tec.connect()
    mock_tec.set_output(True)

    current = mock_tec.read_current()

    assert current is not None
    assert current >= 0.0


def test_read_current_when_disconnected(mock_tec):
    """Test reading current returns None when disconnected."""
    current = mock_tec.read_current()

    assert current is None


def test_read_voltage_when_connected(mock_tec):
    """Test reading TEC voltage."""
    mock_tec.connect()
    mock_tec.set_output(True)

    voltage = mock_tec.read_voltage()

    assert voltage is not None
    assert voltage >= 0.0


def test_read_voltage_when_disconnected(mock_tec):
    """Test reading voltage returns None when disconnected."""
    voltage = mock_tec.read_voltage()

    assert voltage is None


# =============================================================================
# Thermal Simulation Tests
# =============================================================================


def test_thermal_lag_simulation_cooling(mock_tec):
    """Test realistic thermal lag when cooling from ambient to lower temperature."""
    mock_tec.connect()
    mock_tec.set_thermal_time_constant(0.1)  # Fast response for testing
    mock_tec.set_temperature(20.0)  # Cool to 20°C from 25°C ambient
    mock_tec.set_output(True)

    # Initial temperature should be at ambient
    initial_temp = mock_tec.read_temperature()
    assert initial_temp == pytest.approx(25.0, abs=0.1)

    # Wait for thermal response
    time.sleep(0.15)  # ~1.5 time constants

    # Temperature should have moved toward setpoint but not reached it
    current_temp = mock_tec.read_temperature()
    assert current_temp < 25.0  # Cooling down
    assert current_temp > 20.0  # Not at setpoint yet
    assert current_temp < initial_temp  # Definitely cooler


def test_thermal_lag_simulation_heating(mock_tec):
    """Test realistic thermal lag when heating from ambient to higher temperature."""
    mock_tec.connect()
    mock_tec.set_thermal_time_constant(0.1)  # Fast response for testing
    mock_tec.force_temperature(20.0)  # Start below ambient

    # Check initial temperature before starting simulation
    assert mock_tec._temperature_reading_c == pytest.approx(20.0, abs=0.01)

    mock_tec.set_temperature(30.0)  # Heat to 30°C
    mock_tec.set_output(True)

    # Wait for thermal response
    time.sleep(0.15)  # ~1.5 time constants

    # Temperature should have moved toward setpoint
    current_temp = mock_tec.read_temperature()
    assert current_temp > 20.0  # Heating up
    assert current_temp < 30.0  # Not at setpoint yet


def test_thermal_drift_to_ambient_when_output_disabled(mock_tec):
    """Test temperature drifts to ambient when output is disabled."""
    mock_tec.connect()
    mock_tec.set_thermal_time_constant(0.1)
    mock_tec.set_ambient_temperature(25.0)
    mock_tec.force_temperature(20.0)  # Force to 20°C

    # Disable output - should drift to ambient
    mock_tec.set_output(False)

    initial_temp = mock_tec.read_temperature()
    assert initial_temp == pytest.approx(20.0, abs=0.1)

    # Wait for drift
    time.sleep(0.15)

    # Should drift toward ambient (25°C)
    current_temp = mock_tec.read_temperature()
    assert current_temp > 20.0  # Drifting up
    assert current_temp < 25.0  # Not at ambient yet


# =============================================================================
# Status and Diagnostics Tests
# =============================================================================


def test_get_status_returns_comprehensive_info(mock_tec):
    """Test get_status() returns all TEC status information."""
    mock_tec.connect()
    mock_tec.set_temperature(30.0)
    mock_tec.set_output(True)

    status = mock_tec.get_status()

    assert status["connected"] is True
    assert status["output_enabled"] is True
    assert "temperature_c" in status
    assert "setpoint_c" in status
    assert status["setpoint_c"] == 30.0
    assert "current_a" in status
    assert "voltage_v" in status
    assert "at_setpoint" in status


def test_at_setpoint_detection(mock_tec):
    """Test get_status() correctly detects when at setpoint."""
    mock_tec.connect()
    mock_tec.set_temperature(25.0)
    mock_tec.force_temperature(25.05)  # Within 0.1°C tolerance

    status = mock_tec.get_status()

    assert status["at_setpoint"] is True


# =============================================================================
# Signal Emission Tests
# =============================================================================


def test_temperature_changed_signal(mock_tec, qtbot):
    """Test temperature_changed signal is emitted."""
    mock_tec.connect()
    mock_tec.set_output(True)

    with qtbot.waitSignal(mock_tec.temperature_changed, timeout=1000):
        mock_tec.force_temperature(30.0)


def test_temperature_setpoint_changed_signal(mock_tec, qtbot):
    """Test temperature_setpoint_changed signal is emitted."""
    mock_tec.connect()

    with qtbot.waitSignal(mock_tec.temperature_setpoint_changed, timeout=1000):
        mock_tec.set_temperature(30.0)


def test_output_changed_signal(mock_tec, qtbot):
    """Test output_changed signal is emitted."""
    mock_tec.connect()

    with qtbot.waitSignal(mock_tec.output_changed, timeout=1000):
        mock_tec.set_output(True)


def test_connection_changed_signal(mock_tec, qtbot):
    """Test connection_changed signal is emitted."""
    with qtbot.waitSignal(mock_tec.connection_changed, timeout=1000):
        mock_tec.connect()


# =============================================================================
# Error Simulation Tests
# =============================================================================


def test_operation_error_simulation(mock_tec):
    """Test simulated operation errors."""
    mock_tec.connect()
    mock_tec.simulate_operation_error = True

    result = mock_tec.set_temperature(30.0)

    assert result is False


def test_reset_clears_state(mock_tec):
    """Test reset() clears all state and call log."""
    mock_tec.connect()
    mock_tec.set_temperature(30.0)
    mock_tec.set_output(True)

    mock_tec.reset()

    assert mock_tec.is_connected is False
    assert mock_tec.is_output_enabled is False
    assert mock_tec.temperature_setpoint_c == 25.0
    assert len(mock_tec.call_log) == 0


# =============================================================================
# Advanced Simulation Features Tests
# =============================================================================


def test_set_thermal_time_constant(mock_tec):
    """Test setting thermal time constant."""
    mock_tec.set_thermal_time_constant(10.0)

    assert mock_tec._thermal_time_constant == 10.0


def test_set_ambient_temperature(mock_tec):
    """Test setting ambient temperature."""
    mock_tec.set_ambient_temperature(30.0)

    assert mock_tec._ambient_temperature_c == 30.0


def test_force_temperature(mock_tec):
    """Test force_temperature() for edge case testing."""
    mock_tec.force_temperature(35.0)

    assert mock_tec._temperature_reading_c == 35.0
