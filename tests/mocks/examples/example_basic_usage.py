"""
Example: Basic mock usage patterns.

Demonstrates fundamental patterns used across all mocks:
- Connection simulation
- Call logging
- Error injection
- State verification
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

# Add src and project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.mocks import MockLaserController


def example_basic_connection():
    """Example 1: Basic connection and state verification."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    # Create mock
    mock = MockLaserController()

    # Connect successfully
    result = mock.connect(com_port="COM4", baudrate=38400)
    assert result is True
    assert mock.is_connected is True

    # Verify call was logged
    assert ("connect", {"com_port": "COM4", "baudrate": 38400}) in mock.call_log

    print("[OK] Basic connection works")


def example_connection_failure():
    """Example 2: Simulating connection failures."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()

    # Enable failure simulation
    mock.simulate_connection_failure = True

    # Connection should fail
    result = mock.connect()
    assert result is False
    assert mock.is_connected is False

    print("[OK] Connection failure simulation works")


def example_call_logging():
    """Example 3: Verifying method calls with call logging."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()
    mock.connect()

    # Perform operations
    mock.set_power(1000.0)
    mock.set_current(500.0)
    mock.set_output(True)

    # Verify all calls were logged
    assert ("set_power", {"power_mw": 1000.0}) in mock.call_log
    assert ("set_current", {"current_ma": 500.0}) in mock.call_log
    assert ("set_output", {"enabled": True}) in mock.call_log

    print("[OK] Call logging works")


def example_state_verification():
    """Example 4: Verifying internal state changes."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()
    mock.connect()

    # Set power
    mock.set_power(1500.0)
    assert mock.power_setpoint_mw == 1500.0

    # Enable output
    mock.set_output(True)
    assert mock.is_output_enabled is True

    # Read power (should match setpoint when output enabled)
    power = mock.read_power()
    assert power == 1500.0

    print("[OK] State verification works")


def example_test_isolation():
    """Example 5: Using reset() for test isolation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)

    mock = MockLaserController()

    # Test 1: Setup some state
    mock.connect()
    mock.set_power(1000.0)
    mock.simulate_connection_failure = True

    # Reset for test 2
    mock.reset()

    # Verify clean state
    assert mock.is_connected is False
    assert mock.power_setpoint_mw == 0.0
    assert mock.simulate_connection_failure is False
    assert len(mock.call_log) == 0

    print("[OK] Reset() provides test isolation")


if __name__ == "__main__":
    example_basic_connection()
    example_connection_failure()
    example_call_logging()
    example_state_verification()
    example_test_isolation()

    print("\n[PASS] All basic usage examples passed!")
