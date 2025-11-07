"""
Test GPIOController thread safety and integration (Task 13.5).

Comprehensive tests covering:
- Thread safety for concurrent GPIO operations using threading.RLock pattern
- Integration tests combining smoothing motor + watchdog + status updates
- Signal emission thread safety with PyQt6 signals
- Concurrent access validation for all public methods
- Coverage validation targeting 45-50% on gpio_controller.py

Uses unittest.mock.patch to mock serial communication.
Focuses on thread safety and integration rather than individual component tests.
"""

import sys
import threading
import time
from itertools import cycle
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


class TestAdvancedThreadSafety:
    """Test thread safety for concurrent GPIO operations with RLock."""

    def test_concurrent_motor_and_watchdog(self, qtbot, controller):
        """Test concurrent motor control and watchdog heartbeat operations are thread-safe."""
        ctrl, mock_serial = controller

        errors = []
        operations_completed = {"motor": 0, "watchdog": 0}

        def motor_operations():
            try:
                for _ in range(10):
                    mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
                    ctrl.start_smoothing_motor()
                    time.sleep(0.001)
                    mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"
                    ctrl.stop_smoothing_motor()
                    operations_completed["motor"] += 1
            except Exception as e:
                errors.append(("motor", e))

        def watchdog_operations():
            try:
                for _ in range(10):
                    mock_serial.readline.return_value = b"OK:WDT_RESET\n"
                    ctrl.send_watchdog_heartbeat()
                    operations_completed["watchdog"] += 1
                    time.sleep(0.001)
            except Exception as e:
                errors.append(("watchdog", e))

        # Start threads
        t1 = threading.Thread(target=motor_operations)
        t2 = threading.Thread(target=watchdog_operations)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Assert
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert operations_completed["motor"] == 10
        assert operations_completed["watchdog"] == 10

    def test_concurrent_status_reads(self, qtbot, controller):
        """Test concurrent get_status() calls are thread-safe."""
        ctrl, mock_serial = controller

        errors = []
        results = []

        def read_status():
            try:
                for _ in range(20):
                    status = ctrl.get_status()
                    results.append(status)
            except Exception as e:
                errors.append(e)

        # Start multiple reader threads
        threads = [threading.Thread(target=read_status) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert
        assert len(errors) == 0
        assert len(results) == 100  # 5 threads × 20 reads each

        # Verify all results have expected structure
        for status in results:
            assert "connected" in status
            assert "motor_enabled" in status
            assert "safety_ok" in status

    def test_concurrent_mixed_operations(self, qtbot, controller):
        """Test mixed concurrent operations (read/write) are thread-safe."""
        ctrl, mock_serial = controller

        errors = []
        mock_serial.readline.side_effect = cycle(
            [
                b"OK:MOTOR_SPEED:100\n",
                b"OK:WDT_RESET\n",
                b"VIBRATION:1.0\n",
                b"PHOTODIODE:2.5\n",
            ]
        )

        def mixed_operations():
            try:
                for _ in range(5):
                    ctrl.get_status()
                    ctrl.start_smoothing_motor()
                    ctrl.send_watchdog_heartbeat()
                    ctrl._update_status()
                    ctrl.stop_smoothing_motor()
            except Exception as e:
                errors.append(e)

        # Start multiple threads doing mixed operations
        threads = [threading.Thread(target=mixed_operations) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - No errors occurred
        assert len(errors) == 0

    def test_rlock_reentrant_behavior(self, qtbot, controller):
        """Test RLock allows reentrant calls from the same thread."""
        ctrl, mock_serial = controller

        # Setup mock responses
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"

        # Test reentrant locking (calling method that acquires lock from within locked section)
        with ctrl._lock:
            # This should not deadlock because RLock is reentrant
            result = ctrl.start_smoothing_motor()
            assert result is True

    def test_signal_emission_thread_safety(self, qtbot, controller):
        """Test PyQt6 signal emissions are thread-safe."""
        ctrl, mock_serial = controller

        signal_emissions = []
        errors = []

        # Connect to all safety-related signals
        ctrl.smoothing_motor_changed.connect(lambda x: signal_emissions.append(("motor", x)))
        ctrl.smoothing_vibration_changed.connect(
            lambda x: signal_emissions.append(("vibration", x))
        )
        ctrl.safety_interlock_changed.connect(lambda x: signal_emissions.append(("safety", x)))

        def trigger_signals():
            try:
                mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
                ctrl.start_smoothing_motor()

                mock_serial.readline.side_effect = cycle(
                    [
                        b"VIBRATION:1.5\n",
                        b"PHOTODIODE:0.0\n",
                    ]
                )
                for _ in range(3):  # Trigger debouncing
                    ctrl._update_status()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        # Start multiple threads emitting signals
        threads = [threading.Thread(target=trigger_signals) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        qtbot.wait(100)  # Wait for signal processing

        # Assert - No errors and signals were emitted
        assert len(errors) == 0
        assert len(signal_emissions) > 0


class TestIntegration:
    """Integration tests combining multiple GPIO operations."""

    def test_complete_motor_vibration_watchdog_workflow(self, qtbot, controller):
        """Test complete workflow: start motor → detect vibration → send heartbeat."""
        ctrl, mock_serial = controller

        # Track signal emissions
        safety_signals = []
        ctrl.safety_interlock_changed.connect(lambda x: safety_signals.append(x))

        # Step 1: Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        result1 = ctrl.start_smoothing_motor()
        assert result1 is True
        assert ctrl.motor_enabled is True

        # Step 2: Trigger vibration detection (3 readings for debounce)
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.5\n",
                b"PHOTODIODE:0.0\n",
            ]
        )
        for _ in range(3):
            ctrl._update_status()
            qtbot.wait(10)

        # Verify safety interlock is now active
        assert ctrl.get_safety_status() is True
        assert True in safety_signals

        # Step 3: Send watchdog heartbeat
        mock_serial.readline.side_effect = None
        mock_serial.readline.return_value = b"OK:WDT_RESET\n"
        result2 = ctrl.send_watchdog_heartbeat()
        assert result2 is True

        # Step 4: Stop motor (should clear safety)
        mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"
        ctrl.stop_smoothing_motor()
        qtbot.wait(10)

        assert ctrl.motor_enabled is False
        assert ctrl.get_safety_status() is False
        assert False in safety_signals

    def test_rapid_motor_cycling_with_heartbeat(self, qtbot, controller):
        """Test rapid motor start/stop cycles while sending heartbeats."""
        ctrl, mock_serial = controller

        errors = []

        # Setup alternating responses
        mock_serial.readline.side_effect = cycle(
            [
                b"OK:MOTOR_SPEED:100\n",
                b"OK:MOTOR_OFF\n",
                b"OK:WDT_RESET\n",
            ]
        )

        try:
            for _ in range(10):
                ctrl.start_smoothing_motor()
                ctrl.send_watchdog_heartbeat()
                ctrl.stop_smoothing_motor()
                ctrl.send_watchdog_heartbeat()
        except Exception as e:
            errors.append(e)

        # Assert - No errors during rapid cycling
        assert len(errors) == 0

    def test_status_monitoring_during_operations(self, qtbot, controller):
        """Test _update_status() works correctly during motor operations."""
        ctrl, mock_serial = controller

        # Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        # Setup status responses
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.2\n",
                b"PHOTODIODE:2.5\n",
            ]
        )

        # Call _update_status() multiple times
        for _ in range(5):
            ctrl._update_status()
            qtbot.wait(10)

        # Verify state was updated
        assert ctrl.vibration_level > 0.0

    def test_disconnect_during_active_operations(self, qtbot, controller):
        """Test disconnect cleanly stops all operations."""
        ctrl, mock_serial = controller

        # Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()
        assert ctrl.motor_enabled is True

        # Setup mock responses for disconnect (stop motor + stop aiming laser)
        mock_serial.readline.side_effect = [
            b"OK:MOTOR_OFF\n",  # stop_smoothing_motor response
            b"OK:LASER_OFF\n",  # stop_aiming_laser response
        ]

        # Disconnect
        ctrl.disconnect()

        # Verify motor was stopped
        assert ctrl.motor_enabled is False
        assert ctrl.is_connected is False

    def test_reconnect_after_disconnect(self, qtbot, controller):
        """Test reconnect functionality after disconnect."""
        ctrl, mock_serial = controller

        # Disconnect
        ctrl.disconnect()
        assert ctrl.is_connected is False

        # Reconnect
        mock_serial.readline.side_effect = [
            b"STATUS:\n",
            b"OK:ACCEL_INITIALIZED\n",
        ]
        result = ctrl.connect("COM12")

        # Stop monitoring timer again
        ctrl.monitor_timer.stop()

        # Verify reconnection
        assert result is True
        assert ctrl.is_connected is True

    def test_get_status_reflects_all_operations(self, qtbot, controller):
        """Test get_status() accurately reflects state after multiple operations."""
        ctrl, mock_serial = controller

        # Initial state
        status1 = ctrl.get_status()
        assert status1["motor_enabled"] is False
        assert status1["safety_ok"] is False

        # Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        status2 = ctrl.get_status()
        assert status2["motor_enabled"] is True
        assert status2["safety_ok"] is False  # No vibration yet

        # Trigger vibration
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.5\n",
                b"PHOTODIODE:0.0\n",
            ]
        )
        for _ in range(3):
            ctrl._update_status()
            qtbot.wait(10)

        status3 = ctrl.get_status()
        assert status3["motor_enabled"] is True
        assert status3["vibration_detected"] is True
        assert status3["safety_ok"] is True


class TestConcurrencyStress:
    """Stress tests for concurrency edge cases."""

    def test_high_concurrency_motor_control(self, qtbot, controller):
        """Stress test with many concurrent motor control threads."""
        ctrl, mock_serial = controller

        errors = []
        operation_count = [0]

        mock_serial.readline.side_effect = cycle(
            [
                b"OK:MOTOR_SPEED:100\n",
                b"OK:MOTOR_OFF\n",
            ]
        )

        def motor_stress():
            try:
                for _ in range(5):
                    ctrl.start_smoothing_motor()
                    ctrl.stop_smoothing_motor()
                    operation_count[0] += 1
            except Exception as e:
                errors.append(e)

        # Start many threads
        threads = [threading.Thread(target=motor_stress) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert
        assert len(errors) == 0
        assert operation_count[0] == 100  # 20 threads × 5 operations

    def test_concurrent_reads_and_writes(self, qtbot, controller):
        """Test many concurrent read and write operations."""
        ctrl, mock_serial = controller

        errors = []
        read_count = [0]
        write_count = [0]

        mock_serial.readline.side_effect = cycle(
            [
                b"OK:MOTOR_SPEED:100\n",
                b"OK:WDT_RESET\n",
            ]
        )

        def reader():
            try:
                for _ in range(50):
                    ctrl.get_status()
                    read_count[0] += 1
            except Exception as e:
                errors.append(e)

        def writer():
            try:
                for _ in range(25):
                    ctrl.start_smoothing_motor()
                    ctrl.send_watchdog_heartbeat()
                    write_count[0] += 1
            except Exception as e:
                errors.append(e)

        # Start mixed reader and writer threads
        reader_threads = [threading.Thread(target=reader) for _ in range(5)]
        writer_threads = [threading.Thread(target=writer) for _ in range(5)]

        all_threads = reader_threads + writer_threads
        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()

        # Assert
        assert len(errors) == 0
        assert read_count[0] == 250  # 5 threads × 50 reads
        assert write_count[0] == 125  # 5 threads × 25 writes


class TestErrorHandling:
    """Test error handling in concurrent scenarios."""

    def test_serial_error_recovery_concurrent(self, qtbot, controller):
        """Test recovery from serial errors during concurrent operations."""
        ctrl, mock_serial = controller

        errors = []
        successes = [0]

        # Simulate intermittent serial errors
        responses = cycle(
            [
                Exception("Serial timeout"),
                b"OK:MOTOR_SPEED:100\n",
                b"OK:MOTOR_SPEED:100\n",
            ]
        )
        mock_serial.readline.side_effect = responses

        def operation():
            try:
                for _ in range(10):
                    result = ctrl.start_smoothing_motor()
                    if result:
                        successes[0] += 1
            except Exception as e:
                errors.append(e)

        # Start threads
        threads = [threading.Thread(target=operation) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - Some operations succeeded despite errors
        assert len(errors) == 0  # No unhandled exceptions
        assert successes[0] > 0  # Some operations succeeded

    def test_disconnected_state_concurrent(self, qtbot, controller):
        """Test operations fail gracefully when disconnected concurrently."""
        ctrl, mock_serial = controller

        # Disconnect
        ctrl.disconnect()

        errors = []
        results = []

        def operation():
            try:
                result = ctrl.start_smoothing_motor()
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Try operations from multiple threads
        threads = [threading.Thread(target=operation) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - All operations failed gracefully
        assert len(errors) == 0
        assert all(r is False for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
