"""
Test MockGPIOController functionality.

Validates GPIO mocking including safety interlocks and monitoring.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockGPIOController  # noqa: E402


def test_mock_gpio_connect_success() -> None:
    """Test successful GPIO connection."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()

    result = mock.connect(port="COM4")

    assert result is True
    assert mock.is_connected is True
    assert ("connect", {"port": "COM4"}) in mock.call_log


def test_mock_gpio_connect_failure() -> None:
    """Test GPIO connection failure simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.simulate_connection_failure = True

    result = mock.connect()

    assert result is False
    assert mock.is_connected is False


def test_mock_gpio_watchdog_heartbeat() -> None:
    """Test watchdog heartbeat tracking."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Send heartbeat
    result = mock.send_watchdog_heartbeat()

    assert result is True
    assert mock.heartbeat_count == 1
    assert mock.last_heartbeat_time is not None

    # Send another heartbeat
    mock.send_watchdog_heartbeat()
    assert mock.heartbeat_count == 2


def test_mock_gpio_smoothing_motor() -> None:
    """Test smoothing motor control."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Start motor
    result = mock.start_smoothing_motor()
    assert result is True
    assert mock.motor_enabled is True

    # Stop motor
    result = mock.stop_smoothing_motor()
    assert result is True
    assert mock.motor_enabled is False


def test_mock_gpio_vibration_detection() -> None:
    """Test vibration detection when motor is on."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Motor off - no vibration
    assert mock.vibration_detected is False

    # Start motor - vibration should be detected
    mock.start_smoothing_motor()
    assert mock.vibration_detected is True

    # Stop motor - vibration should stop
    mock.stop_smoothing_motor()
    assert mock.vibration_detected is False


def test_mock_gpio_aiming_laser() -> None:
    """Test aiming laser control."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Start aiming laser
    result = mock.start_aiming_laser()
    assert result is True
    assert mock.aiming_laser_enabled is True

    # Stop aiming laser
    result = mock.stop_aiming_laser()
    assert result is True
    assert mock.aiming_laser_enabled is False


def test_mock_gpio_photodiode_readings() -> None:
    """Test photodiode voltage and power readings."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # With aiming laser off - low voltage
    mock._update_status()
    voltage = mock.get_photodiode_voltage()
    power = mock.get_photodiode_power()
    assert voltage == 0.1  # Background noise
    assert power == 0.1 * 400.0  # 40 mW

    # With aiming laser on - higher voltage
    mock.start_aiming_laser()
    mock._update_status()
    voltage = mock.get_photodiode_voltage()
    power = mock.get_photodiode_power()
    assert voltage == 2.5  # Simulated laser voltage
    assert power == 2.5 * 400.0  # 1000 mW


def test_mock_gpio_safety_interlock() -> None:
    """Test safety interlock status (motor AND vibration)."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Initially not safe (motor off)
    assert mock.get_safety_status() is False

    # Start motor - should become safe (motor + vibration)
    mock.start_smoothing_motor()
    assert mock.get_safety_status() is True

    # Stop motor - not safe again
    mock.stop_smoothing_motor()
    assert mock.get_safety_status() is False


def test_mock_gpio_safety_requires_both_conditions() -> None:
    """Test that safety requires BOTH motor and vibration."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Motor on but no vibration (unrealistic but testable)
    mock.motor_enabled = True
    mock.vibration_detected = False
    assert mock.get_safety_status() is False

    # Vibration but motor off (unrealistic but testable)
    mock.motor_enabled = False
    mock.vibration_detected = True
    assert mock.get_safety_status() is False

    # Both on - safe
    mock.motor_enabled = True
    mock.vibration_detected = True
    assert mock.get_safety_status() is True


def test_mock_gpio_disconnect_disables_outputs() -> None:
    """Test that disconnect disables all outputs."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()
    mock.start_smoothing_motor()
    mock.start_aiming_laser()

    mock.disconnect()

    assert mock.is_connected is False
    assert mock.motor_enabled is False
    assert mock.aiming_laser_enabled is False
    assert mock.vibration_detected is False


def test_mock_gpio_monitoring_timer() -> None:
    """Test that monitoring timer updates readings."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()
    mock.start_aiming_laser()

    # Manually trigger timer update
    mock._update_status()

    # Should have updated photodiode readings
    assert mock.photodiode_voltage == 2.5
    assert mock.photodiode_power_mw == 1000.0


def test_mock_gpio_heartbeat_without_connection() -> None:
    """Test heartbeat fails when not connected."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()

    result = mock.send_watchdog_heartbeat()

    assert result is False
    assert mock.heartbeat_count == 0


def test_mock_gpio_voltage_to_power_conversion() -> None:
    """Test photodiode voltage-to-power conversion."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()

    # Test calibration constant (400 mW/V)
    mock.photodiode_voltage = 5.0  # Max voltage
    mock.photodiode_power_mw = mock.photodiode_voltage * mock.photodiode_voltage_to_power
    assert mock.photodiode_power_mw == 2000.0  # Max power


def test_mock_gpio_reset() -> None:
    """Test GPIO reset functionality."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockGPIOController()
    mock.connect()
    mock.start_smoothing_motor()
    mock.start_aiming_laser()
    mock.heartbeat_count = 10
    mock.simulate_connection_failure = True

    mock.reset()

    assert mock.is_connected is False
    assert mock.motor_enabled is False
    assert mock.aiming_laser_enabled is False
    assert mock.vibration_detected is False
    assert mock.heartbeat_count == 0
    assert mock.simulate_connection_failure is False
    assert len(mock.call_log) == 0
