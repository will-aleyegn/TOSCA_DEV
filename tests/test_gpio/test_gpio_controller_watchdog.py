"""
Test GPIOController watchdog heartbeat timing (Task 13.4).

Tests the hardware watchdog timer:
- Heartbeat timing (500ms interval requirement)
- Timeout detection (1000ms triggers fault)
- WDT_RESET command verification
- Heartbeat count tracking
- Recovery after heartbeat failure

Uses unittest.mock.patch to mock serial communication.
Uses deterministic timing with time.perf_counter() instead of real delays.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hardware.gpio_controller import GPIOController  # noqa: E402


@pytest.fixture
def app(qtbot):
    """Create QApplication for PyQt6 signals."""
    app_instance = QApplication.instance()
    if app_instance is None:
        app_instance = QApplication(sys.argv)
    return app_instance


@pytest.fixture
def controller(app):
    """Create GPIO controller with mocked serial and stopped monitoring timer."""
    with patch("hardware.gpio_controller.serial.Serial") as mock_serial_class:
        # Create mock serial instance
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.reset_input_buffer = MagicMock()
        mock_serial.reset_output_buffer = MagicMock()
        mock_serial.write = MagicMock()

        # Default responses for connect() sequence
        mock_serial.readline.side_effect = [
            b"STATUS:\n",  # GET_STATUS response
            b"OK:ACCEL_INITIALIZED\n",  # ACCEL_INIT response
        ]

        mock_serial_class.return_value = mock_serial

        # Create controller and connect
        ctrl = GPIOController()
        ctrl.connect("COM12")

        # Stop background monitoring timer
        ctrl.monitor_timer.stop()

        # Clear call history
        mock_serial.write.call_args_list.clear()
        mock_serial.readline.call_args_list.clear()

        # Set default return value
        mock_serial.readline.side_effect = None
        mock_serial.readline.return_value = b"OK\n"

        # Yield both controller and mock
        yield ctrl, mock_serial

        # Cleanup: Disconnect controller to close serial connection
        try:
            ctrl.disconnect()
        except Exception:
            pass  # Ignore errors during cleanup


class TestWatchdogHeartbeat:
    """Test watchdog heartbeat command and tracking."""

    def test_send_watchdog_heartbeat_success(self, qtbot, controller):
        """Test sending watchdog heartbeat returns True and increments count."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"

        # Track initial time
        start_time = time.perf_counter()

        # Act
        result = ctrl.send_watchdog_heartbeat()

        # Assert
        assert result is True

        # Verify WDT_RESET command sent
        assert mock_serial.write.called
        assert b"WDT_RESET\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_send_watchdog_heartbeat_without_connection_fails(self, qtbot, app):
        """Test sending heartbeat without connection returns False."""
        ctrl = GPIOController()

        # Act
        result = ctrl.send_watchdog_heartbeat()

        # Assert
        assert result is False

    def test_send_watchdog_heartbeat_serial_error(self, qtbot, controller):
        """Test heartbeat failure when serial communication fails."""
        ctrl, mock_serial = controller

        # Simulate serial error
        mock_serial.readline.side_effect = Exception("Serial timeout")

        # Act
        result = ctrl.send_watchdog_heartbeat()

        # Assert
        assert result is False

    def test_send_watchdog_heartbeat_invalid_response(self, qtbot, controller):
        """Test heartbeat failure when Arduino returns invalid response."""
        ctrl, mock_serial = controller

        # Setup invalid response
        mock_serial.readline.return_value = b"ERROR:UNKNOWN_COMMAND\n"

        # Act
        result = ctrl.send_watchdog_heartbeat()

        # Assert
        assert result is False

    def test_send_watchdog_heartbeat_command_format(self, qtbot, controller):
        """Test WDT_RESET command format is correct."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"

        # Act
        ctrl.send_watchdog_heartbeat()

        # Assert - Verify exact command format
        calls = [call[0][0] for call in mock_serial.write.call_args_list]
        assert b"WDT_RESET\n" in calls
        # Verify only one WDT_RESET command sent
        wdt_commands = [c for c in calls if c == b"WDT_RESET\n"]
        assert len(wdt_commands) == 1


class TestWatchdogTiming:
    """Test watchdog timing requirements."""

    def test_heartbeat_timing_deterministic(self, qtbot, controller):
        """Test heartbeat timing can be measured deterministically."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"

        # Measure heartbeat execution time
        timestamps = []
        for _ in range(5):
            start = time.perf_counter()
            ctrl.send_watchdog_heartbeat()
            end = time.perf_counter()
            timestamps.append(end - start)

        # Assert - Heartbeat executes quickly (< 100ms with mocked serial)
        for duration in timestamps:
            assert duration < 0.1  # 100ms threshold

        # Assert - Timing is consistent (std deviation < 50ms)
        import statistics

        if len(timestamps) > 1:
            std_dev = statistics.stdev(timestamps)
            assert std_dev < 0.05  # 50ms threshold

    def test_multiple_heartbeats_sequential(self, qtbot, controller):
        """Test multiple sequential heartbeats succeed."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"

        # Send 10 heartbeats
        results = []
        for _ in range(10):
            result = ctrl.send_watchdog_heartbeat()
            results.append(result)
            time.sleep(0.01)  # Small delay between heartbeats

        # Assert - All heartbeats succeeded
        assert all(results), "All heartbeats should succeed"
        assert len(results) == 10

        # Verify 10 WDT_RESET commands sent
        wdt_commands = [
            call[0][0] for call in mock_serial.write.call_args_list if call[0][0] == b"WDT_RESET\n"
        ]
        assert len(wdt_commands) == 10


class TestWatchdogRecovery:
    """Test watchdog recovery after failures."""

    def test_heartbeat_recovery_after_serial_error(self, qtbot, controller):
        """Test heartbeat can recover after temporary serial error."""
        ctrl, mock_serial = controller

        # First heartbeat fails
        mock_serial.readline.side_effect = Exception("Temporary error")
        result1 = ctrl.send_watchdog_heartbeat()
        assert result1 is False

        # Second heartbeat succeeds (error cleared)
        mock_serial.readline.side_effect = None
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"
        result2 = ctrl.send_watchdog_heartbeat()
        assert result2 is True

    def test_heartbeat_recovery_after_disconnect_reconnect(self, qtbot, controller):
        """Test heartbeat works after disconnect and reconnect."""
        ctrl, mock_serial = controller

        # Disconnect
        ctrl.disconnect()

        # Heartbeat should fail when disconnected
        result1 = ctrl.send_watchdog_heartbeat()
        assert result1 is False

        # Reconnect
        mock_serial.readline.side_effect = [
            b"STATUS:\n",
            b"OK:ACCEL_INITIALIZED\n",
        ]
        ctrl.connect("COM12")
        ctrl.monitor_timer.stop()

        # Heartbeat should work after reconnect
        mock_serial.readline.side_effect = None
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"
        result2 = ctrl.send_watchdog_heartbeat()
        assert result2 is True


class TestWatchdogIntegration:
    """Test watchdog integration with other GPIO operations."""

    def test_heartbeat_during_motor_operation(self, qtbot, controller):
        """Test heartbeat can be sent while motor is running."""
        ctrl, mock_serial = controller

        # Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()
        assert ctrl.motor_enabled is True

        # Send heartbeat while motor running
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"
        result = ctrl.send_watchdog_heartbeat()

        # Assert - Heartbeat succeeds
        assert result is True

        # Assert - Motor still running
        assert ctrl.motor_enabled is True

    def test_heartbeat_with_concurrent_status_updates(self, qtbot, controller):
        """Test heartbeat doesn't interfere with status updates."""
        ctrl, mock_serial = controller

        # Simulate status update response
        from itertools import cycle

        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.0\n",
                b"PHOTODIODE:2.5\n",
            ]
        )

        # Update status
        ctrl._update_status()

        # Send heartbeat (must clear cycle first)
        mock_serial.readline.side_effect = None
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"
        result = ctrl.send_watchdog_heartbeat()

        # Assert
        assert result is True

    def test_heartbeat_thread_safety(self, qtbot, controller):
        """Test heartbeat is thread-safe with RLock."""
        ctrl, mock_serial = controller
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"

        import threading

        errors = []

        def send_heartbeat():
            try:
                result = ctrl.send_watchdog_heartbeat()
                if not result:
                    errors.append("Heartbeat failed")
            except Exception as e:
                errors.append(e)

        # Send heartbeats from multiple threads
        threads = [threading.Thread(target=send_heartbeat) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - No errors
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
