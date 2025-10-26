"""
Test MockLaserController functionality.

Validates that laser mocking works including power control and TEC temperature.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockLaserController  # noqa: E402


def test_mock_laser_connect_success() -> None:
    """Test successful laser connection."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()

    result = mock.connect(com_port="COM4", baudrate=38400)

    assert result is True
    assert mock.is_connected is True
    assert ("connect", {"com_port": "COM4", "baudrate": 38400}) in mock.call_log


def test_mock_laser_connect_failure() -> None:
    """Test laser connection failure simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.simulate_connection_failure = True

    result = mock.connect()

    assert result is False
    assert mock.is_connected is False


def test_mock_laser_output_enable() -> None:
    """Test laser output enable/disable."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    # Enable output
    result = mock.set_output(True)
    assert result is True
    assert mock.is_output_enabled is True

    # Disable output
    result = mock.set_output(False)
    assert result is True  # Operation succeeded
    assert mock.is_output_enabled is False  # But output is now disabled


def test_mock_laser_set_current() -> None:
    """Test setting laser current."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    result = mock.set_current(500.0)

    assert result is True
    assert mock.current_setpoint_ma == 500.0
    assert ("set_current", {"current_ma": 500.0}) in mock.call_log


def test_mock_laser_set_power() -> None:
    """Test setting laser power."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    result = mock.set_power(1000.0)

    assert result is True
    assert mock.power_setpoint_mw == 1000.0
    assert ("set_power", {"power_mw": 1000.0}) in mock.call_log


def test_mock_laser_current_limit() -> None:
    """Test current limit enforcement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    result = mock.set_current(3000.0)  # Exceeds max_current_ma (2000)

    assert result is False


def test_mock_laser_power_limit() -> None:
    """Test power limit enforcement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    result = mock.set_power(3000.0)  # Exceeds max_power_mw (2000)

    assert result is False


def test_mock_laser_temperature_control() -> None:
    """Test TEC temperature control."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    result = mock.set_temperature(22.0)

    assert result is True
    assert mock.temperature_setpoint_c == 22.0
    assert mock._temperature_reading_c == 22.0


def test_mock_laser_read_current() -> None:
    """Test reading laser current."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()
    mock.set_current(750.0)
    mock.set_output(True)

    current = mock.read_current()

    assert current == 750.0


def test_mock_laser_output_updates_readings() -> None:
    """Test that enabling output updates current/power readings."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()

    # Set values but don't enable output
    mock.set_current(800.0)
    mock.set_power(1200.0)
    assert mock.read_current() == 0.0
    assert mock.read_power() == 0.0

    # Enable output - readings should match setpoints
    mock.set_output(True)
    assert mock.read_current() == 800.0
    assert mock.read_power() == 1200.0

    # Disable output - readings should go to zero
    mock.set_output(False)
    assert mock.read_current() == 0.0
    assert mock.read_power() == 0.0


def test_mock_laser_disconnect_disables_output() -> None:
    """Test that disconnect automatically disables output."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()
    mock.set_output(True)

    mock.disconnect()

    assert mock.is_output_enabled is False
    assert mock.is_connected is False


def test_mock_laser_reset() -> None:
    """Test laser reset functionality."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockLaserController()
    mock.connect()
    mock.set_current(1000.0)
    mock.set_output(True)

    mock.reset()

    assert mock.is_connected is False
    assert mock.is_output_enabled is False
    assert mock.current_setpoint_ma == 0.0
    assert len(mock.call_log) == 0
