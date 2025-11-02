"""
Test suites for TEC and Actuator Controllers.

Tests temperature management and positioning accuracy without physical hardware.
"""

import sys
import threading
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtTest import QSignalSpy

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.mocks import MockActuatorController, MockTECController


@pytest.fixture(scope="module")
def qapp():
    """Provide QCoreApplication for tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def connected_tec():
    """Provide connected mock TEC controller."""
    mock = MockTECController()
    mock.connect(com_port="COM9", baudrate=38400)
    yield mock
    mock.disconnect()
    mock.reset()


@pytest.fixture
def connected_actuator():
    """Provide connected mock actuator controller."""
    mock = MockActuatorController()
    mock.connect(com_port="COM3", baudrate=9600, auto_home=False)
    yield mock
    mock.disconnect()
    mock.reset()


class TestTECController:
    """Test TEC temperature control."""

    def test_set_temperature(self, qapp, connected_tec):
        """Test setting temperature."""
        result = connected_tec.set_temperature(20.0)

        assert result is True
        assert connected_tec.temperature_setpoint_c == 20.0

    def test_temperature_limits(self, qapp, connected_tec):
        """Test temperature limit enforcement."""
        result_low = connected_tec.set_temperature(10.0)  # Below 15°C
        result_high = connected_tec.set_temperature(40.0)  # Above 35°C

        assert result_low is False
        assert result_high is False

    def test_output_control(self, qapp, connected_tec):
        """Test TEC output enable/disable."""
        result = connected_tec.set_output(True)

        assert result is True
        assert connected_tec.is_output_enabled is True

    def test_temperature_reading(self, qapp, connected_tec):
        """Test reading temperature."""
        temp = connected_tec.read_temperature()

        assert temp is not None
        assert isinstance(temp, float)


class TestActuatorController:
    """Test actuator positioning."""

    def test_homing(self, qapp, connected_actuator):
        """Test homing sequence."""
        result = connected_actuator.find_index()

        assert result is True

    def test_set_position(self, qapp, connected_actuator):
        """Test setting position."""
        connected_actuator.find_index()
        connected_actuator._complete_homing()

        result = connected_actuator.set_position(10000.0)

        assert result is True

    def test_position_limits(self, qapp, connected_actuator):
        """Test position limit enforcement."""
        connected_actuator.find_index()
        connected_actuator._complete_homing()

        result = connected_actuator.set_position(50000.0)  # Beyond limit

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
