"""
Test GPIOController smoothing motor and vibration detection (Task 13.3).

Tests the dual-signal validation system:
- Smoothing motor control (D2 pin)
- Vibration detection from MPU6050 (I2C/D3)
- Safety interlock requiring BOTH motor ON and vibration detected
- Debouncing logic (3 consecutive readings)
- PyQt6 signal emissions

Uses unittest.mock.patch to mock serial communication.
"""

import sys
import threading
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

        # Stop background monitoring timer to prevent mock exhaustion
        ctrl.monitor_timer.stop()

        # Clear ONLY the call history, not the mock behavior
        # This preserves side_effect/return_value while clearing call_args_list
        mock_serial.write.call_args_list.clear()
        mock_serial.readline.call_args_list.clear()

        # Set default return value for subsequent calls (tests can override)
        mock_serial.readline.side_effect = None  # Clear side_effect
        mock_serial.readline.return_value = b"OK\n"  # Default response

        # Yield both controller and mock for test use
        yield ctrl, mock_serial

        # Cleanup: Disconnect controller to close serial connection
        try:
            ctrl.disconnect()
        except Exception:
            pass  # Ignore errors during cleanup


class TestSmoothingMotorControl:
    """Test smoothing motor control methods."""

    def test_start_smoothing_motor_success(self, qtbot, controller):
        """Test starting smoothing motor sends MOTOR_SPEED:100 command."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"

        # Act
        result = ctrl.start_smoothing_motor()

        # Assert
        assert result is True
        assert ctrl.motor_enabled is True
        assert ctrl.motor_speed_pwm == 100

        # Verify command sent
        assert mock_serial.write.called
        assert b"MOTOR_SPEED:100\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_start_smoothing_motor_emits_signals(self, qtbot, controller):
        """Test starting smoothing motor emits smoothing_motor_changed and motor_speed_changed signals."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"

        # Track signal emissions
        motor_signals = []
        speed_signals = []
        ctrl.smoothing_motor_changed.connect(lambda x: motor_signals.append(x))
        ctrl.motor_speed_changed.connect(lambda x: speed_signals.append(x))

        # Act
        ctrl.start_smoothing_motor()
        qtbot.wait(10)

        # Assert
        assert len(motor_signals) == 1
        assert motor_signals[0] is True
        assert len(speed_signals) == 1
        assert speed_signals[0] == 100

    def test_stop_smoothing_motor_success(self, qtbot, controller):
        """Test stopping smoothing motor sends MOTOR_OFF command."""
        ctrl, mock_serial = controller

        # Start motor first
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        # Setup mock response for stop
        mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"

        # Act
        result = ctrl.stop_smoothing_motor()

        # Assert
        assert result is True
        assert ctrl.motor_enabled is False
        assert ctrl.motor_speed_pwm == 0

        # Verify command sent
        assert b"MOTOR_OFF\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_stop_smoothing_motor_emits_signals(self, qtbot, controller):
        """Test stopping smoothing motor emits smoothing_motor_changed and motor_speed_changed signals."""
        ctrl, mock_serial = controller

        # Start motor first
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        # Track signal emissions
        motor_signals = []
        speed_signals = []
        ctrl.smoothing_motor_changed.connect(lambda x: motor_signals.append(x))
        ctrl.motor_speed_changed.connect(lambda x: speed_signals.append(x))

        # Setup mock response for stop
        mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"

        # Act
        ctrl.stop_smoothing_motor()
        qtbot.wait(10)

        # Assert
        assert len(motor_signals) == 1
        assert motor_signals[0] is False
        assert len(speed_signals) == 1
        assert speed_signals[0] == 0

    def test_set_motor_speed_valid_pwm(self, qtbot, controller):
        """Test setting motor speed with valid PWM value (0-153)."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:76\n"

        # Act
        result = ctrl.set_motor_speed(76)  # 1.5V minimum rated speed

        # Assert
        assert result is True
        assert ctrl.motor_enabled is True
        assert ctrl.motor_speed_pwm == 76

        # Verify command sent
        assert b"MOTOR_SPEED:76\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_set_motor_speed_clamps_to_maximum(self, qtbot, controller):
        """Test setting motor speed above 153 clamps to maximum safe speed."""
        ctrl, mock_serial = controller

        # Setup mock response (controller clamps to 153)
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:153\n"

        # Act
        result = ctrl.set_motor_speed(200)  # Over maximum

        # Assert
        assert result is True
        assert ctrl.motor_speed_pwm == 153  # Clamped to maximum

        # Verify clamped value was sent
        assert b"MOTOR_SPEED:153\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_set_motor_speed_zero_stops_motor(self, qtbot, controller):
        """Test setting motor speed to zero calls stop motor."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"

        # Act
        result = ctrl.set_motor_speed(0)

        # Assert
        assert result is True
        assert ctrl.motor_enabled is False
        assert ctrl.motor_speed_pwm == 0

        # Verify MOTOR_OFF command sent
        assert b"MOTOR_OFF\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_start_motor_without_connection_fails(self, qtbot, app):
        """Test starting motor without connection returns False."""
        # Create controller without connecting
        ctrl = GPIOController()

        # Act
        result = ctrl.start_smoothing_motor()

        # Assert
        assert result is False
        assert ctrl.motor_enabled is False


class TestVibrationDetection:
    """Test vibration detection from MPU6050 accelerometer."""

    def test_vibration_detected_above_threshold(self, qtbot, controller):
        """Test vibration detection when magnitude exceeds 0.8g threshold."""
        ctrl, mock_serial = controller

        # Setup mock responses for 3 updates (debounce requirement)
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.2\n",  # Above threshold
                b"PHOTODIODE:0.0\n",
            ]
        )

        # Track signal emissions
        vib_signals = []
        ctrl.smoothing_vibration_changed.connect(lambda x: vib_signals.append(x))

        # Act - Trigger 3 updates to satisfy debounce
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)

        # Assert
        assert ctrl.vibration_detected is True
        assert len(vib_signals) == 1
        assert vib_signals[0] is True

    def test_vibration_requires_debouncing(self, qtbot, controller):
        """Test vibration detection requires 3 consecutive readings above threshold."""
        ctrl, mock_serial = controller

        # Setup mock responses - third reading below threshold
        mock_serial.readline.side_effect = [
            b"VIBRATION:1.2\n",
            b"PHOTODIODE:0.0\n",  # Above threshold
            b"VIBRATION:1.5\n",
            b"PHOTODIODE:0.0\n",  # Above threshold
            b"VIBRATION:0.5\n",
            b"PHOTODIODE:0.0\n",  # BELOW threshold (debounce fails)
        ]

        # Track signal emissions
        vib_signals = []
        ctrl.smoothing_vibration_changed.connect(lambda x: vib_signals.append(x))

        # Act - Trigger 3 updates
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)

        # Assert - Vibration should NOT be detected (debounce failed)
        assert ctrl.vibration_detected is False
        assert len(vib_signals) == 0  # No signal emitted

    def test_vibration_below_threshold_not_detected(self, qtbot, controller):
        """Test vibration not detected when magnitude below 0.8g threshold."""
        ctrl, mock_serial = controller

        # Setup mock responses - all below threshold
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:0.14\n",  # Motor OFF baseline
                b"PHOTODIODE:0.0\n",
            ]
        )

        # Track signal emissions
        vib_signals = []
        ctrl.smoothing_vibration_changed.connect(lambda x: vib_signals.append(x))

        # Act - Trigger 3 updates
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)

        # Assert
        assert ctrl.vibration_detected is False
        assert len(vib_signals) == 0  # No signal emitted

    def test_vibration_level_signal_emission(self, qtbot, controller):
        """Test vibration_level_changed signal emits magnitude values."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.side_effect = [
            b"VIBRATION:1.234\n",
            b"PHOTODIODE:0.0\n",
        ]

        # Track signal emissions
        level_signals = []
        ctrl.vibration_level_changed.connect(lambda x: level_signals.append(x))

        # Act
        ctrl._update_status()
        qtbot.wait(10)

        # Assert
        assert len(level_signals) == 1
        assert level_signals[0] == pytest.approx(1.234, abs=0.001)

    def test_get_vibration_level_command(self, qtbot, controller):
        """Test get_vibration_level() sends GET_VIBRATION_LEVEL command."""
        ctrl, mock_serial = controller

        # Simulate initialized accelerometer
        ctrl.accelerometer_initialized = True

        # Setup mock response
        mock_serial.readline.return_value = b"VIBRATION:2.5\n"

        # Act
        result = ctrl.get_vibration_level()

        # Assert
        assert result == pytest.approx(2.5, abs=0.001)
        assert ctrl.vibration_level == pytest.approx(2.5, abs=0.001)

        # Verify command sent
        assert b"GET_VIBRATION_LEVEL\n" in [call[0][0] for call in mock_serial.write.call_args_list]


class TestDualSignalValidation:
    """Test dual-signal validation: motor AND vibration required for safety."""

    def test_safety_ok_requires_motor_and_vibration(self, qtbot, controller):
        """Test get_safety_status() returns True only when BOTH motor ON and vibration detected."""
        ctrl, mock_serial = controller

        # Initially not safe (motor off, no vibration)
        assert ctrl.get_safety_status() is False

        # Start motor (but no vibration yet)
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()
        assert ctrl.get_safety_status() is False  # Motor on but no vibration

        # Trigger vibration detection (3 readings for debounce)
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.5\n",
                b"PHOTODIODE:0.0\n",
            ]
        )
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)

        # Now both conditions met
        assert ctrl.get_safety_status() is True

    def test_safety_fails_with_motor_only(self, qtbot, controller):
        """Test safety status False when motor ON but no vibration."""
        ctrl, mock_serial = controller

        # Start motor
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        # Setup low vibration
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:0.2\n",  # Below threshold
                b"PHOTODIODE:0.0\n",
            ]
        )
        ctrl._update_status()
        qtbot.wait(10)

        # Assert - Motor on but no vibration detected
        assert ctrl.motor_enabled is True
        assert ctrl.vibration_detected is False
        assert ctrl.get_safety_status() is False

    def test_safety_fails_with_vibration_only(self, qtbot, app):
        """Test safety status False when vibration detected but motor OFF."""
        # Create controller without connecting (no fixture)
        ctrl = GPIOController()
        ctrl.motor_enabled = False  # Motor explicitly off
        ctrl.vibration_detected = True  # Vibration detected (unrealistic but testable)

        # Act
        result = ctrl.get_safety_status()

        # Assert
        assert result is False

    def test_safety_interlock_signal_emission(self, qtbot, controller):
        """Test safety_interlock_changed signal emits when safety status changes."""
        ctrl, mock_serial = controller

        # Track signal emissions
        safety_signals = []
        ctrl.safety_interlock_changed.connect(lambda x: safety_signals.append(x))

        # Start motor (emits False - motor on but no vibration)
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()
        qtbot.wait(10)

        # Trigger vibration detection
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.5\n",
                b"PHOTODIODE:0.0\n",
            ]
        )
        ctrl._update_status()  # Debounce count = 1
        qtbot.wait(10)
        ctrl._update_status()  # Debounce count = 2
        qtbot.wait(10)
        ctrl._update_status()  # Debounce satisfied, both conditions met
        qtbot.wait(10)

        # Assert - Should emit True when both conditions met
        assert len(safety_signals) >= 1
        # Last emission should be True
        assert safety_signals[-1] is True

    def test_stop_motor_clears_safety_interlock(self, qtbot, controller):
        """Test stopping motor clears safety interlock even with vibration."""
        ctrl, mock_serial = controller

        # Establish safe state (motor + vibration)
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"
        ctrl.start_smoothing_motor()

        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.5\n",
                b"PHOTODIODE:0.0\n",
            ]
        )
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        ctrl._update_status()
        qtbot.wait(10)
        assert ctrl.get_safety_status() is True

        # Track signal emissions for stop action
        safety_signals = []
        ctrl.safety_interlock_changed.connect(lambda x: safety_signals.append(x))

        # Act - Stop motor (must clear side_effect first - it takes precedence over return_value)
        mock_serial.readline.side_effect = None  # Clear cycle
        mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"
        ctrl.stop_smoothing_motor()
        qtbot.wait(10)

        # Assert - Safety should be False (motor off, even though vibration still detected)
        assert ctrl.get_safety_status() is False
        assert len(safety_signals) == 1
        assert safety_signals[0] is False


class TestThreadSafety:
    """Test thread safety for concurrent GPIO operations."""

    def test_concurrent_motor_control(self, qtbot, controller):
        """Test concurrent start/stop motor operations are thread-safe."""
        ctrl, mock_serial = controller

        # Setup cyclic mock responses
        mock_serial.readline.return_value = b"OK:MOTOR_SPEED:100\n"

        errors = []

        def start_motor():
            try:
                ctrl.start_smoothing_motor()
            except Exception as e:
                errors.append(e)

        def stop_motor():
            try:
                mock_serial.readline.return_value = b"OK:MOTOR_OFF\n"
                ctrl.stop_smoothing_motor()
            except Exception as e:
                errors.append(e)

        # Act - Start multiple threads
        threads = []
        for _ in range(5):
            t1 = threading.Thread(target=start_motor)
            t2 = threading.Thread(target=stop_motor)
            threads.extend([t1, t2])
            t1.start()
            t2.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Assert - No errors occurred
        assert len(errors) == 0

    def test_concurrent_status_updates(self, qtbot, controller):
        """Test concurrent _update_status() calls are thread-safe."""
        ctrl, mock_serial = controller

        # Setup cyclic mock responses
        mock_serial.readline.side_effect = cycle(
            [
                b"VIBRATION:1.0\n",
                b"PHOTODIODE:2.5\n",
            ]
        )

        errors = []

        def update_status():
            try:
                ctrl._update_status()
            except Exception as e:
                errors.append(e)

        # Act - Start multiple threads
        threads = [threading.Thread(target=update_status) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - No errors occurred
        assert len(errors) == 0


class TestAccelerometerInitialization:
    """Test accelerometer initialization methods."""

    def test_init_accelerometer_success(self, qtbot, controller):
        """Test successful accelerometer initialization."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:ACCEL_INITIALIZED\n"

        # Act
        result = ctrl.init_accelerometer()

        # Assert
        assert result is True
        assert ctrl.accelerometer_initialized is True

        # Verify command sent
        assert b"ACCEL_INIT\n" in [call[0][0] for call in mock_serial.write.call_args_list]

    def test_init_accelerometer_not_found(self, qtbot, controller):
        """Test accelerometer initialization fails when device not found."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"ERROR:NO_ACCEL_FOUND\n"

        # Act
        result = ctrl.init_accelerometer()

        # Assert
        assert result is False
        assert ctrl.accelerometer_initialized is False

    def test_reinitialize_accelerometer(self, qtbot, controller):
        """Test manual accelerometer reinitialization."""
        ctrl, mock_serial = controller

        # Setup mock response
        mock_serial.readline.return_value = b"OK:ACCEL_INITIALIZED\n"

        # Act
        result = ctrl.reinitialize_accelerometer()

        # Assert
        assert result is True

        # Verify command sent
        assert b"ACCEL_INIT\n" in [call[0][0] for call in mock_serial.write.call_args_list]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
