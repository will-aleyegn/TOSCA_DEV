"""
Example: Testing PyQt6 signals with mocks.

Demonstrates how to verify signal emissions using QSignalSpy.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtTest import QSignalSpy

# Add src and project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.mocks import MockGPIOController, MockLaserController


def example_signal_spy():
    """Example 1: Using QSignalSpy to verify signal emissions."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()

    # Create spy for power_changed signal
    spy = QSignalSpy(mock.power_changed)

    # Trigger signal
    mock.connect()
    mock.set_power(1500.0)
    mock.set_output(True)

    # Verify signal emitted once with correct value
    assert len(spy) == 1
    assert spy[0][0] == 1500.0

    print("[OK] QSignalSpy works with mocks")


def example_multiple_signals():
    """Example 2: Tracking multiple signals."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()

    # Create spies for multiple signals
    connection_spy = QSignalSpy(mock.connection_changed)
    power_spy = QSignalSpy(mock.power_changed)
    output_spy = QSignalSpy(mock.output_changed)

    # Perform operations
    mock.connect()
    mock.set_power(1000.0)
    mock.set_output(True)

    # Verify all signals
    assert len(connection_spy) == 1
    assert connection_spy[0][0] is True

    assert len(power_spy) == 1
    assert power_spy[0][0] == 1000.0

    assert len(output_spy) == 1
    assert output_spy[0][0] is True

    print("[OK] Multiple signal tracking works")


def example_safety_interlock_signals():
    """Example 3: Testing safety interlock signal behavior."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockGPIOController()

    # Create spy for safety_interlock_changed
    safety_spy = QSignalSpy(mock.safety_interlock_changed)
    motor_spy = QSignalSpy(mock.smoothing_motor_changed)
    vibration_spy = QSignalSpy(mock.smoothing_vibration_changed)

    # Start motor (should trigger safety interlock)
    mock.connect()
    mock.start_smoothing_motor()

    # Verify signals
    assert len(motor_spy) == 1
    assert motor_spy[0][0] is True

    assert len(vibration_spy) == 1  # Auto-detected when motor on
    assert vibration_spy[0][0] is True

    assert len(safety_spy) == 1  # Safety OK when motor AND vibration
    assert safety_spy[0][0] is True

    print("[OK] Safety interlock signals work")


def example_signal_with_custom_slot():
    """Example 4: Connecting signals to custom slots."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()

    # Track signal emissions in a list
    power_updates = []

    def on_power_changed(power_mw):
        power_updates.append(power_mw)

    # Connect signal to custom slot
    mock.power_changed.connect(on_power_changed)

    # Trigger multiple updates
    mock.connect()
    mock.set_power(500.0)
    mock.set_output(True)
    mock.set_power(1000.0)
    mock.set_power(1500.0)

    # Verify all updates captured
    assert power_updates == [500.0, 1000.0, 1500.0]

    print("[OK] Custom signal slots work")


if __name__ == "__main__":
    example_signal_spy()
    example_multiple_signals()
    example_safety_interlock_signals()
    example_signal_with_custom_slot()

    print("\n[PASS] All signal testing examples passed!")
