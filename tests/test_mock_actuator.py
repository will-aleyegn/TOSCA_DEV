"""
Test MockActuatorController functionality.

Validates actuator mocking including position control, homing, and scanning.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockActuatorController  # noqa: E402


def test_mock_actuator_connect_success() -> None:
    """Test successful actuator connection."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()

    result = mock.connect(com_port="COM3", baudrate=9600, auto_home=False)

    assert result is True
    assert mock.is_connected is True
    assert ("connect", {"com_port": "COM3", "baudrate": 9600, "auto_home": False}) in mock.call_log


def test_mock_actuator_connect_failure() -> None:
    """Test actuator connection failure simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.simulate_connection_failure = True

    result = mock.connect()

    assert result is False
    assert mock.is_connected is False


def test_mock_actuator_homing() -> None:
    """Test actuator homing sequence."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.homing_delay_ms = 0  # Instant homing for testing

    # Start homing
    result = mock.find_index()
    assert result is True
    assert mock.is_homed is False  # Not yet complete

    # Wait for completion (trigger timer manually)
    mock._complete_homing()
    assert mock.is_homed is True
    assert mock.current_position_um == 0.0


def test_mock_actuator_set_position() -> None:
    """Test absolute position movement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True  # Simulate already homed

    result = mock.set_position(1000.0)

    assert result is True
    assert mock.target_position_um == 1000.0
    assert ("set_position", {"position_um": 1000.0}) in mock.call_log

    # Complete movement
    mock._complete_movement()
    assert mock.current_position_um == 1000.0


def test_mock_actuator_make_step() -> None:
    """Test relative step movement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True
    mock.current_position_um = 1000.0

    result = mock.make_step(500.0)

    assert result is True
    assert mock.target_position_um == 1500.0
    assert ("make_step", {"step_um": 500.0}) in mock.call_log


def test_mock_actuator_position_limits() -> None:
    """Test position limit enforcement."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True

    # Try to exceed high limit
    result = mock.set_position(50000.0)  # Exceeds 45000 µm
    assert result is False

    # Try to exceed low limit
    result = mock.set_position(-50000.0)  # Below -45000 µm
    assert result is False

    # Valid position should work
    result = mock.set_position(10000.0)
    assert result is True


def test_mock_actuator_scanning() -> None:
    """Test continuous scanning."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True

    # Start scan in positive direction
    result = mock.start_scan(direction=1)
    assert result is True
    assert mock.is_scanning is True
    assert mock.scan_direction == 1

    # Stop scan
    result = mock.stop_scan()
    assert result is True
    assert mock.is_scanning is False


def test_mock_actuator_scan_limit_stop() -> None:
    """Test scan auto-stop at limits."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True
    mock.current_position_um = 44000.0  # Near high limit
    mock.speed_um_per_s = 10000

    # Start scan toward high limit
    mock.start_scan(direction=1)

    # Simulate scan updates until limit hit
    while mock.is_scanning:
        mock._update_scan_position()

    # Should have stopped at/before limit
    assert mock.is_scanning is False
    assert mock.current_position_um <= mock.high_limit_um


def test_mock_actuator_get_position() -> None:
    """Test reading current position."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True
    mock.current_position_um = 2500.0

    position = mock.get_position()

    assert position == 2500.0


def test_mock_actuator_set_speed() -> None:
    """Test speed control."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect()

    result = mock.set_speed(20000)

    assert result is True
    assert mock.speed_um_per_s == 20000


def test_mock_actuator_limits_management() -> None:
    """Test setting and getting limits."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect()

    # Set custom limits
    result = mock.set_position_limits(-30000.0, 30000.0)
    assert result is True

    # Get limits
    low, high = mock.get_limits()
    assert low == -30000.0
    assert high == 30000.0


def test_mock_actuator_limit_proximity_warning() -> None:
    """Test limit proximity detection."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.limit_warning_distance_um = 1000.0

    # Near low limit
    proximity = mock.check_limit_proximity(-44500.0)  # 500 µm from -45000
    assert proximity is not None
    assert proximity[0] == "low"
    assert proximity[1] == 500.0

    # Near high limit
    proximity = mock.check_limit_proximity(44200.0)  # 800 µm from 45000
    assert proximity is not None
    assert proximity[0] == "high"
    assert proximity[1] == 800.0

    # Not near any limit
    proximity = mock.check_limit_proximity(0.0)
    assert proximity is None


def test_mock_actuator_requires_homing() -> None:
    """Test that position commands require homing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)

    # Not homed - should fail
    result = mock.set_position(1000.0)
    assert result is False

    # Home first
    mock.is_homed = True

    # Now should work
    result = mock.set_position(1000.0)
    assert result is True


def test_mock_actuator_status_info() -> None:
    """Test comprehensive status reporting."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True
    mock.current_position_um = 10000.0

    status = mock.get_status_info()

    assert status["connected"] is True
    assert status["homed"] is True
    assert status["position_um"] == 10000.0
    assert status["low_limit_um"] == -45000.0
    assert status["high_limit_um"] == 45000.0
    assert status["distance_from_low_limit"] == 55000.0
    assert status["distance_from_high_limit"] == 35000.0


def test_mock_actuator_disconnect_stops_movement() -> None:
    """Test that disconnect stops all motion."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect(auto_home=False)
    mock.is_homed = True

    # Start scan
    mock.start_scan(direction=1)
    assert mock.is_scanning is True

    # Disconnect
    mock.disconnect()

    assert mock.is_connected is False
    assert mock.is_homed is False
    assert mock.is_scanning is False


def test_mock_actuator_reset() -> None:
    """Test actuator reset functionality."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockActuatorController()
    mock.connect()
    mock.is_homed = True
    mock.current_position_um = 5000.0
    mock.simulate_connection_failure = True

    mock.reset()

    assert mock.is_connected is False
    assert mock.is_homed is False
    assert mock.current_position_um == 0.0
    assert mock.simulate_connection_failure is False
    assert len(mock.call_log) == 0
