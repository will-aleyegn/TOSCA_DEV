"""
Example: Realistic testing scenarios.

Demonstrates testing complex workflows that mirror actual usage:
- Treatment workflow simulation
- Safety interlock testing
- Multi-device coordination
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

# Add src and project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.mocks import MockActuatorController, MockGPIOController, MockLaserController


def example_treatment_workflow():
    """Example 1: Simulating complete treatment workflow."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    # Setup devices
    laser = MockLaserController()
    actuator = MockActuatorController()
    gpio = MockGPIOController()

    # 1. Connect all devices
    assert laser.connect() is True
    assert actuator.connect(auto_home=True) is True
    assert gpio.connect() is True

    # 2. Wait for homing
    actuator._complete_homing()
    assert actuator.is_homed is True

    # 3. Enable safety interlocks
    gpio.start_smoothing_motor()
    assert gpio.get_safety_status() is True

    # 4. Move actuator to start position
    actuator.set_position(0.0)
    actuator._complete_movement()

    # 5. Set laser parameters
    laser.set_power(1000.0)
    laser.set_current(800.0)

    # 6. Enable laser output
    laser.set_output(True)
    assert laser.is_output_enabled is True
    assert laser.read_power() == 1000.0

    # 7. Perform treatment movement
    actuator.set_position(5000.0)
    actuator._complete_movement()

    # 8. Disable laser
    laser.set_output(False)
    assert laser.read_power() == 0.0

    # 9. Stop safety systems
    gpio.stop_smoothing_motor()
    assert gpio.get_safety_status() is False

    print("[OK] Treatment workflow simulation works")


def example_safety_failure_handling():
    """Example 2: Testing safety failure scenarios."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    laser = MockLaserController()
    gpio = MockGPIOController()

    # Setup
    laser.connect()
    gpio.connect()
    gpio.start_smoothing_motor()

    # Enable laser (safety OK)
    laser.set_output(True)
    assert laser.is_output_enabled is True

    # Simulate safety failure (motor stops)
    gpio.stop_smoothing_motor()
    assert gpio.get_safety_status() is False

    # In real system, this would trigger laser shutdown
    # Here we verify the safety status is False
    assert not gpio.motor_enabled
    assert not gpio.vibration_detected

    print("[OK] Safety failure detection works")


def example_position_scanning():
    """Example 3: Testing actuator scanning with laser."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    actuator = MockActuatorController()
    laser = MockLaserController()

    # Setup
    actuator.connect(auto_home=True)
    actuator._complete_homing()
    laser.connect()

    # Set laser power for scanning
    laser.set_power(500.0)
    laser.set_output(True)

    # Start scan in positive direction
    actuator.start_scan(direction=1)
    assert actuator.is_scanning is True

    # Simulate scan progress
    for _ in range(5):
        actuator._update_scan_position()

    # Verify position changed
    assert actuator.current_position_um > 0.0

    # Stop scan
    actuator.stop_scan()
    assert actuator.is_scanning is False

    # Disable laser
    laser.set_output(False)

    print("[OK] Position scanning with laser works")


def example_watchdog_monitoring():
    """Example 4: Testing watchdog heartbeat system."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    gpio = MockGPIOController()
    gpio.connect()

    # Send periodic heartbeats
    for i in range(10):
        result = gpio.send_watchdog_heartbeat()
        assert result is True
        assert gpio.heartbeat_count == i + 1

    # Verify last heartbeat timestamp exists
    assert gpio.last_heartbeat_time is not None

    print("[OK] Watchdog heartbeat monitoring works")


def example_limit_testing():
    """Example 5: Testing actuator limit enforcement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    actuator = MockActuatorController()
    actuator.connect(auto_home=True)
    actuator._complete_homing()

    # Try to exceed high limit
    result = actuator.set_position(50000.0)  # Exceeds 45000 µm
    assert result is False

    # Try to exceed low limit
    result = actuator.set_position(-50000.0)  # Below -45000 µm
    assert result is False

    # Valid position should work
    result = actuator.set_position(10000.0)
    assert result is True

    # Test proximity warning
    actuator.current_position_um = 44500.0  # Near high limit
    proximity = actuator.check_limit_proximity(44500.0)
    assert proximity is not None
    assert proximity[0] == "high"
    assert proximity[1] == 500.0  # 500 µm from limit

    print("[OK] Actuator limit enforcement works")


if __name__ == "__main__":
    example_treatment_workflow()
    example_safety_failure_handling()
    example_position_scanning()
    example_watchdog_monitoring()
    example_limit_testing()

    print("\n[PASS] All realistic scenario examples passed!")
