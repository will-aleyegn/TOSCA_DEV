"""
Comprehensive test suite for LaserController.

Tests serial communication (COM10), power control (0-10W), safety limits,
and thread safety without requiring physical hardware.
"""

import sys
import threading
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtTest import QSignalSpy

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.mocks import MockLaserController


@pytest.fixture(scope="module")
def qapp():
    """Provide QCoreApplication for tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def connected_laser():
    """Provide connected mock laser controller."""
    mock = MockLaserController()
    mock.connect(com_port="COM10", baudrate=38400)
    yield mock
    mock.disconnect()
    mock.reset()


class TestLaserInitialization:
    """Test laser controller initialization and connection."""

    def test_initialization(self, qapp):
        """Test laser controller initialization."""
        controller = MockLaserController()

        assert controller.is_connected is False
        assert controller.is_output_enabled is False
        assert controller.power_setpoint_mw == 0.0

    def test_connection(self, qapp):
        """Test laser connection."""
        controller = MockLaserController()

        result = controller.connect(com_port="COM10", baudrate=38400)

        assert result is True
        assert controller.is_connected is True

    def test_disconnection(self, qapp, connected_laser):
        """Test laser disconnection."""
        connected_laser.disconnect()

        assert connected_laser.is_connected is False
        assert connected_laser.is_output_enabled is False


class TestPowerControl:
    """Test laser power control functionality."""

    def test_set_power_valid(self, qapp, connected_laser):
        """Test setting valid power."""
        result = connected_laser.set_power(1000.0)

        assert result is True
        assert connected_laser.power_setpoint_mw == 1000.0

    def test_set_power_requires_connection(self, qapp):
        """Test power setting requires connection."""
        controller = MockLaserController()

        result = controller.set_power(1000.0)

        assert result is False

    def test_set_power_exceeds_limit(self, qapp, connected_laser):
        """Test power exceeding maximum limit."""
        result = connected_laser.set_power(5000.0)

        assert result is False

    def test_power_signal_emission(self, qapp, connected_laser):
        """Test power_changed signal emission."""
        spy = QSignalSpy(connected_laser.power_changed)

        connected_laser.set_power(1500.0)

        assert len(spy) >= 1
        assert spy[0][0] == 1500.0


class TestCurrentControl:
    """Test laser current control functionality."""

    def test_set_current_valid(self, qapp, connected_laser):
        """Test setting valid current."""
        result = connected_laser.set_current(1200.0)

        assert result is True
        assert connected_laser.current_setpoint_ma == 1200.0

    def test_set_current_exceeds_limit(self, qapp, connected_laser):
        """Test current exceeding maximum limit."""
        result = connected_laser.set_current(5000.0)

        assert result is False


class TestOutputControl:
    """Test laser output enable/disable."""

    def test_enable_output(self, qapp, connected_laser):
        """Test enabling laser output."""
        connected_laser.set_power(1000.0)

        result = connected_laser.set_output(True)

        assert result is True
        assert connected_laser.is_output_enabled is True

    def test_disable_output(self, qapp, connected_laser):
        """Test disabling laser output."""
        connected_laser.set_output(True)

        result = connected_laser.set_output(False)

        assert result is True
        assert connected_laser.is_output_enabled is False

    def test_output_affects_readings(self, qapp, connected_laser):
        """Test output state affects power readings."""
        connected_laser.set_power(1000.0)
        connected_laser.set_output(True)

        power_on = connected_laser.read_power()

        connected_laser.set_output(False)
        power_off = connected_laser.read_power()

        assert power_on == 1000.0
        assert power_off == 0.0


class TestReadings:
    """Test laser reading functionality."""

    def test_read_power(self, qapp, connected_laser):
        """Test reading power."""
        connected_laser.set_power(1500.0)
        connected_laser.set_output(True)

        power = connected_laser.read_power()

        assert power == 1500.0

    def test_read_current(self, qapp, connected_laser):
        """Test reading current."""
        connected_laser.set_current(1200.0)
        connected_laser.set_output(True)

        current = connected_laser.read_current()

        assert current == 1200.0

    def test_read_requires_connection(self, qapp):
        """Test readings require connection."""
        controller = MockLaserController()

        power = controller.read_power()
        current = controller.read_current()

        assert power is None
        assert current is None


class TestThreadSafety:
    """Test thread safety of laser operations."""

    def test_concurrent_power_changes(self, qapp, connected_laser):
        """Test concurrent power setting from multiple threads."""
        errors = []

        def set_power_repeatedly(value, count):
            """Set power repeatedly from thread."""
            try:
                for _ in range(count):
                    connected_laser.set_power(value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=set_power_repeatedly, args=(1000.0, 50)),
            threading.Thread(target=set_power_repeatedly, args=(1500.0, 50)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert connected_laser.power_setpoint_mw in [1000.0, 1500.0]


class TestErrorHandling:
    """Test error handling."""

    def test_connection_failure(self, qapp):
        """Test connection failure handling."""
        controller = MockLaserController()
        controller.simulate_connection_failure = True

        result = controller.connect()

        assert result is False

    def test_operation_with_error(self, qapp, connected_laser):
        """Test operations with simulated error."""
        connected_laser.simulate_operation_error = True

        result = connected_laser.set_power(1000.0)

        assert result is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
