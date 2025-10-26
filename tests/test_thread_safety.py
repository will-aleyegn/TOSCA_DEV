# -*- coding: utf-8 -*-
"""
Thread safety tests for hardware controllers.

Tests concurrent access to hardware controllers from multiple threads
to verify that threading.RLock protection works correctly.
"""

import sys
import threading
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.mocks import MockActuatorController, MockGPIOController, MockLaserController


class TestLaserThreadSafety:
    """Test thread safety of LaserController."""

    def test_concurrent_power_changes(self):
        """Test concurrent set_power calls from multiple threads."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockLaserController()
        mock.connect()

        errors = []
        power_values = [500.0, 1000.0, 1500.0, 2000.0]

        def set_power_repeatedly(power):
            for _ in range(10):
                try:
                    mock.set_power(power)
                    time.sleep(0.001)  # Small delay
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=set_power_repeatedly, args=(p,)) for p in power_values]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify final state is consistent
        assert mock.power_setpoint_mw in power_values

    def test_concurrent_connect_disconnect(self):
        """Test concurrent connect/disconnect operations."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockLaserController()
        errors = []

        def connect_disconnect_cycle():
            for _ in range(5):
                try:
                    mock.connect()
                    time.sleep(0.001)
                    mock.disconnect()
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=connect_disconnect_cycle) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"


class TestActuatorThreadSafety:
    """Test thread safety of ActuatorController."""

    def test_concurrent_position_commands(self):
        """Test concurrent set_position calls from multiple threads."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockActuatorController()
        mock.connect(auto_home=True)
        mock._complete_homing()

        errors = []
        positions = [0.0, 5000.0, 10000.0, 15000.0]

        def set_position_repeatedly(position):
            for _ in range(10):
                try:
                    mock.set_position(position)
                    mock._complete_movement()
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=set_position_repeatedly, args=(p,)) for p in positions]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify final position is consistent
        assert mock.current_position_um in positions

    def test_concurrent_read_operations(self):
        """Test concurrent get_position calls (read-only operations)."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockActuatorController()
        mock.connect(auto_home=True)
        mock._complete_homing()
        mock.set_position(1000.0)

        errors = []
        positions_read = []

        def read_position_repeatedly():
            for _ in range(20):
                try:
                    pos = mock.get_position()
                    if pos is not None:
                        positions_read.append(pos)
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=read_position_repeatedly) for _ in range(4)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify we got readings
        assert len(positions_read) > 0


class TestGPIOThreadSafety:
    """Test thread safety of GPIOController."""

    def test_concurrent_motor_control(self):
        """Test concurrent motor start/stop from multiple threads."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockGPIOController()
        mock.connect()

        errors = []

        def motor_cycle():
            for _ in range(10):
                try:
                    mock.start_smoothing_motor()
                    time.sleep(0.001)
                    mock.stop_smoothing_motor()
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=motor_cycle) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify final state is consistent
        assert isinstance(mock.motor_enabled, bool)

    def test_concurrent_sensor_reads(self):
        """Test concurrent sensor reading operations."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        mock = MockGPIOController()
        mock.connect()

        errors = []
        readings = []

        def read_sensors_repeatedly():
            for _ in range(20):
                try:
                    voltage = mock.get_photodiode_voltage()
                    power = mock.get_photodiode_power()
                    safety = mock.get_safety_status()
                    readings.append((voltage, power, safety))
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(str(e))

        # Create threads
        threads = [threading.Thread(target=read_sensors_repeatedly) for _ in range(4)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify we got readings
        assert len(readings) > 0


class TestCrossControllerThreadSafety:
    """Test thread safety across multiple controllers."""

    def test_concurrent_multi_controller_operations(self):
        """Test concurrent operations on different controllers."""
        app = QCoreApplication.instance() or QCoreApplication(sys.argv)

        laser = MockLaserController()
        actuator = MockActuatorController()
        gpio = MockGPIOController()

        # Connect all
        laser.connect()
        actuator.connect(auto_home=True)
        actuator._complete_homing()
        gpio.connect()

        errors = []

        def laser_operations():
            for _ in range(10):
                try:
                    laser.set_power(1000.0)
                    laser.set_output(True)
                    time.sleep(0.001)
                    laser.set_output(False)
                except Exception as e:
                    errors.append(f"Laser: {e}")

        def actuator_operations():
            for _ in range(10):
                try:
                    actuator.set_position(5000.0)
                    actuator._complete_movement()
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(f"Actuator: {e}")

        def gpio_operations():
            for _ in range(10):
                try:
                    gpio.start_smoothing_motor()
                    time.sleep(0.001)
                    gpio.stop_smoothing_motor()
                except Exception as e:
                    errors.append(f"GPIO: {e}")

        # Create threads for each controller
        threads = [
            threading.Thread(target=laser_operations),
            threading.Thread(target=laser_operations),  # Two threads per controller
            threading.Thread(target=actuator_operations),
            threading.Thread(target=actuator_operations),
            threading.Thread(target=gpio_operations),
            threading.Thread(target=gpio_operations),
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
