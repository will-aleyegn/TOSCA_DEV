"""
Test suite for GPIO Controller and Safety Interlocks.

Tests hardware safety interlocks without physical Arduino.
"""

import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.mocks import MockGPIOController


@pytest.fixture(scope="module")
def qapp():
    """Provide QCoreApplication for tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def connected_gpio():
    """Provide connected mock GPIO controller."""
    mock = MockGPIOController()
    mock.connect(port="COM4")
    yield mock
    mock.disconnect()
    mock.reset()


class TestGPIOController:
    """Test GPIO controller functionality."""

    def test_connection(self, qapp):
        """Test GPIO connection."""
        controller = MockGPIOController()

        result = controller.connect(port="COM4")

        assert result is True
        assert controller.is_connected is True

    def test_smoothing_motor_control(self, qapp, connected_gpio):
        """Test smoothing motor start/stop."""
        result = connected_gpio.start_smoothing_motor()

        assert result is True
        assert connected_gpio.motor_enabled is True

    def test_vibration_detection(self, qapp, connected_gpio):
        """Test vibration detection when motor runs."""
        connected_gpio.start_smoothing_motor()

        assert connected_gpio.vibration_detected is True

    def test_safety_interlock(self, qapp, connected_gpio):
        """Test safety interlock status (motor AND vibration)."""
        connected_gpio.start_smoothing_motor()

        safety_ok = connected_gpio.get_safety_status()

        assert safety_ok is True

    def test_watchdog_heartbeat(self, qapp, connected_gpio):
        """Test watchdog heartbeat."""
        result = connected_gpio.send_watchdog_heartbeat()

        assert result is True
        assert connected_gpio.heartbeat_count >= 1

    def test_photodiode_reading(self, qapp, connected_gpio):
        """Test photodiode voltage and power reading."""
        voltage = connected_gpio.get_photodiode_voltage()
        power = connected_gpio.get_photodiode_power()

        assert isinstance(voltage, float)
        assert isinstance(power, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
