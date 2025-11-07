# -*- coding: utf-8 -*-
"""
Module: GPIO Controller
Project: TOSCA Laser Control System

Purpose: Arduino GPIO hardware abstraction layer for safety interlocks.
         Provides smoothing device control, photodiode monitoring, aiming laser control,
         hardware watchdog heartbeat, and thread-safe serial communication.
Safety Critical: Yes

Arduino Nano Pin Configuration:
- Digital Pin 2: Smoothing motor control (output)
- Digital Pin 3: Smoothing vibration sensor (input with pullup)
- Digital Pin 4: Aiming laser control (output)
- Analog Pin A0: photodiode laser pickoff measurement laser power monitoring (0-5V)

Serial Protocol (9600 baud, ASCII text commands):
- WDT_RESET: Reset watchdog timer (heartbeat)
- MOTOR_ON/MOTOR_OFF: Control laser spot smoothing module
- LASER_ON/LASER_OFF: Control aiming laser
- GET_VIBRATION: Read vibration sensor
- GET_PHOTODIODE: Read photodiode laser pickoff measurement voltage
- GET_STATUS: Get complete system status
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)

# Try to import pyserial
try:
    import serial

    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial not available - GPIO features disabled")


class GPIOController(QObject):
    """
    Arduino Nano GPIO controller with PyQt6 integration.

    Uses custom serial protocol with hardware watchdog timer.
    Replaces StandardFirmata with direct serial communication.

    Manages safety interlocks:
    - Smoothing device motor control (digital output)
    - Smoothing device vibration sensor (digital input)
    - photodiode laser pickoff measurement laser power monitoring (analog input)
    - Aiming laser control (digital output)
    - Hardware watchdog heartbeat
    """

    # Calibrated vibration detection threshold (from motor calibration data)
    # Motor OFF baseline: 0.14g, Motor ON minimum: 1.6g
    # Threshold provides 5.7x safety margin above noise
    VIBRATION_THRESHOLD_G = 0.8

    # Signals
    smoothing_motor_changed = pyqtSignal(bool)  # Motor state (on/off)
    motor_speed_changed = pyqtSignal(int)  # Motor PWM speed (0-153)
    smoothing_vibration_changed = pyqtSignal(bool)  # Vibration detected
    accelerometer_data_changed = pyqtSignal(float, float, float)  # X, Y, Z acceleration (g)
    vibration_level_changed = pyqtSignal(float)  # Vibration magnitude (g)
    photodiode_voltage_changed = pyqtSignal(float)  # Voltage in V
    photodiode_power_changed = pyqtSignal(float)  # Calculated power in mW
    aiming_laser_changed = pyqtSignal(bool)  # Aiming laser state (on/off)
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)  # Error message
    safety_interlock_changed = pyqtSignal(bool)  # Safety OK status

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()

        self.hardware_available = SERIAL_AVAILABLE
        self.event_logger = event_logger

        if not SERIAL_AVAILABLE:
            logger.warning("GPIO controller initialized in DISABLED mode - pyserial not available")

        # Thread safety lock for serial communication (reentrant for nested calls)
        self._lock = threading.RLock()

        # Serial connection
        self.serial: Optional[serial.Serial] = None
        self.port: Optional[str] = None

        # State tracking
        self.is_connected = False
        self.motor_enabled = False
        self.motor_speed_pwm = 0  # PWM value (0-153)
        self.aiming_laser_enabled = False
        self.vibration_detected = False
        self.accelerometer_initialized = False
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0
        self.vibration_level = 0.0
        self.photodiode_voltage = 0.0
        self.photodiode_power_mw = 0.0

        # Monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_status)
        self.monitor_timer.setInterval(100)  # Update every 100ms

        # Calibration constants
        self.photodiode_voltage_to_power = 400.0  # mW per volt (2000mW / 5V)
        self.vibration_debounce_count = 0
        self.vibration_debounce_threshold = 3  # Require 3 consecutive readings

        logger.info("GPIO controller initialized (custom serial protocol, thread-safe)")

    def __del__(self) -> None:
        """Destructor: Ensure serial connection is closed when object is destroyed."""
        try:
            if hasattr(self, "serial") and self.serial is not None:
                self.disconnect()
        except Exception:
            pass  # Ignore errors during cleanup

    def connect(self, port: str = "COM4") -> bool:
        """
        Connect to Arduino Nano and initialize GPIO pins.

        Opens serial connection (9600 baud) and verifies firmware responds.

        Args:
            port: Serial port (e.g., 'COM4' on Windows, '/dev/ttyUSB0' on Linux)

        Returns:
            True if connected successfully
        """
        if not self.hardware_available:
            self.error_occurred.emit("GPIO hardware not available - pyserial not installed")
            logger.warning("Cannot connect - pyserial not available")
            return False

        with self._lock:
            try:
                # Open serial connection
                self.serial = serial.Serial(
                    port=port,
                    baudrate=9600,
                    timeout=1.0,  # 1 second timeout for reads
                    write_timeout=1.0,
                )
                self.port = port

                # Wait for Arduino to reset (DTR toggling resets Arduino)
                time.sleep(2.0)

                # Clear any startup messages from serial buffer
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()

                logger.info(f"Serial port opened: {port} at 9600 baud")

                # Verify firmware responds (use multi-line to handle full status response)
                response = self._send_command("GET_STATUS", multi_line=True)
                if "STATUS:" not in response:
                    raise RuntimeError(f"Invalid firmware response: {response}")

                logger.info("Arduino watchdog firmware detected")

                self.is_connected = True
                self.connection_changed.emit(True)

                # Log event
                if self.event_logger:
                    from core.event_logger import EventType

                    self.event_logger.log_hardware_event(
                        event_type=EventType.HARDWARE_GPIO_CONNECT,
                        description=f"Arduino GPIO connected on {port}",
                        device_name="Arduino Nano (Watchdog Firmware)",
                    )

                # Start monitoring
                self.monitor_timer.start()
                logger.info("GPIO controller connected successfully")

                # Auto-initialize accelerometer (force I2C re-scan)
                # Arduino only scans for accelerometer once during setup()
                # If device wasn't ready then, it stays undetected
                # Sending ACCEL_INIT forces re-scan and initialization
                try:
                    logger.info("Initializing accelerometer...")
                    init_response = self._send_command("ACCEL_INIT")
                    if "OK:ACCEL_INITIALIZED" in init_response:
                        logger.info("Accelerometer initialized successfully")
                    elif "ERROR:NO_ACCEL_FOUND" in init_response:
                        logger.warning(
                            "No accelerometer detected on I2C bus - "
                            "check hardware connections (SDA=A4, SCL=A5)"
                        )
                    else:
                        logger.warning(f"Unexpected accelerometer init response: {init_response}")
                except Exception as e:
                    logger.warning(f"Accelerometer initialization failed: {e}")
                    # Don't fail connection if accelerometer init fails

                return True

            except Exception as e:
                error_msg = f"Arduino connection failed: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)

                # Clean up on failure
                if self.serial:
                    try:
                        self.serial.close()
                    except Exception:
                        pass
                    self.serial = None

                # Log error event
                if self.event_logger:
                    from core.event_logger import EventSeverity, EventType

                    self.event_logger.log_event(
                        event_type=EventType.HARDWARE_ERROR,
                        description=error_msg,
                        severity=EventSeverity.WARNING,
                        details={"device": "Arduino Nano", "port": port},
                    )

                return False

    def disconnect(self) -> None:
        """Disconnect from Arduino."""
        with self._lock:
            self.stop_smoothing_motor()
            self.stop_aiming_laser()
            self.monitor_timer.stop()

            if self.serial:
                try:
                    self.serial.close()
                except Exception as e:
                    logger.warning(f"Error closing serial connection: {e}")
                self.serial = None

            self.port = None
            self.is_connected = False
            self.connection_changed.emit(False)
            logger.info("GPIO controller disconnected")

            # Log event
            if self.event_logger:
                from core.event_logger import EventType

                self.event_logger.log_hardware_event(
                    event_type=EventType.HARDWARE_GPIO_DISCONNECT,
                    description="Arduino GPIO disconnected",
                    device_name="Arduino Nano",
                )

    def get_status(self) -> dict[str, Any]:
        """
        Get current GPIO status and state information.

        Returns:
            Dictionary containing:
            - connected (bool): Connection status
            - motor_enabled (bool): Smoothing motor state
            - vibration_detected (bool): Vibration sensor state
            - aiming_laser_enabled (bool): Aiming laser state
            - photodiode_voltage (float): photodiode laser pickoff measurement voltage in V
            - photodiode_power_mw (float): Calculated power in mW
            - safety_ok (bool): Overall safety interlock status
        """
        with self._lock:
            safety_ok = self.motor_enabled and self.vibration_detected
            return {
                "connected": self.is_connected,
                "motor_enabled": self.motor_enabled,
                "vibration_detected": self.vibration_detected,
                "aiming_laser_enabled": self.aiming_laser_enabled,
                "photodiode_voltage": self.photodiode_voltage,
                "photodiode_power_mw": self.photodiode_power_mw,
                "safety_ok": safety_ok,
            }

    def _send_command(  # noqa: C901
        self,
        command: str,
        expect_response: bool = True,
        expected_prefix: Optional[str] = None,
        multi_line: bool = False,
        timeout_lines: int = 20,
    ) -> str:
        """
        Send command to Arduino and read response with buffer flushing.

        FIX: Flushes serial buffers before sending to prevent response misalignment.

        Args:
            command: Command string (e.g., "WDT_RESET", "MOTOR_ON")
            expect_response: Whether to wait for response
            expected_prefix: Expected response prefix for validation (e.g., "OK:", "VIBRATION:")
            multi_line: Whether to read multiple lines until terminator
            timeout_lines: Maximum lines to read for multi-line responses (safety limit)

        Returns:
            Response string from Arduino (or empty if no response expected)

        Raises:
            RuntimeError: If serial communication fails or response validation fails
        """
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Serial port not open")

        with self._lock:
            try:
                # FIX 1: Clear any stale data from serial buffers BEFORE sending command
                # This prevents reading old responses from previous commands
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()

                # Send command with newline terminator
                cmd_bytes = (command + "\n").encode("utf-8")
                self.serial.write(cmd_bytes)

                # Selective logging: Skip routine monitoring commands to reduce log spam
                is_routine = command in ["GET_PHOTODIODE", "GET_VIBRATION", "GET_MOTOR_STATUS"]
                if not is_routine:
                    logger.debug(f"Sent: {command}")

                if not expect_response:
                    return ""

                # Read response
                if multi_line:
                    # FIX 3: Handle multi-line responses (e.g., GET_STATUS)
                    lines = []
                    for _ in range(timeout_lines):
                        line = self.serial.readline().decode("utf-8").strip()
                        if line:
                            if not is_routine:
                                logger.debug(f"Received: {line}")
                            lines.append(line)
                            # Stop at terminator
                            if (
                                line.startswith("OK:")
                                or line == "-----------------------------------"
                            ):
                                break
                    response = "\n".join(lines)
                else:
                    # Single line response (default)
                    response: str = self.serial.readline().decode("utf-8").strip()
                    if not is_routine:
                        logger.debug(f"Received: {response}")

                # FIX 4: Validate response matches expected format
                if expected_prefix and not response.startswith(expected_prefix):
                    logger.warning(
                        f"Response validation failed: "
                        f"expected '{expected_prefix}', got '{response}'"
                    )
                    # Don't raise error, just warn - allows graceful degradation
                    # Could add retry logic here if needed

                return response

            except serial.SerialTimeoutException:
                raise RuntimeError(f"Serial timeout sending command: {command}")
            except Exception as e:
                raise RuntimeError(f"Serial error: {e}")

    def send_watchdog_heartbeat(self) -> bool:
        """
        Send heartbeat pulse to hardware watchdog timer.

        Called by SafetyWatchdog every 500ms. Must be sent or
        hardware watchdog will timeout after 1000ms and trigger
        emergency shutdown.

        Returns:
            True if heartbeat sent successfully, False on error
        """
        if not self.is_connected or not self.serial:
            return False

        with self._lock:
            try:
                response = self._send_command("WDT_RESET", expected_prefix="OK:WDT_RESET")
                return "OK:WDT_RESET" in response
            except Exception as e:
                logger.error(f"Watchdog heartbeat failed: {e}")
                return False

    def start_smoothing_motor(self) -> bool:
        """
        Start laser spot smoothing module motor.

        Returns:
            True if motor started successfully
        """
        if not self.is_connected:
            self.error_occurred.emit("GPIO not connected")
            return False

        with self._lock:
            try:
                # Use default motor speed (100 PWM = ~2.0V)
                response = self._send_command("MOTOR_SPEED:100", expected_prefix="OK:MOTOR_SPEED:")

                if "OK:MOTOR_SPEED:" in response:
                    self.motor_enabled = True
                    self.motor_speed_pwm = 100
                    self.smoothing_motor_changed.emit(True)
                    self.motor_speed_changed.emit(100)
                    logger.info("Smoothing motor started at PWM 100")

                    # Log event
                    if self.event_logger:
                        from core.event_logger import EventType

                        self.event_logger.log_event(
                            event_type=EventType.SAFETY_GPIO_OK,
                            description="Smoothing motor started",
                        )

                    self._update_safety_status()
                    return True
                else:
                    raise RuntimeError(f"Unexpected response: {response}")

            except Exception as e:
                error_msg = f"Failed to start motor: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def stop_smoothing_motor(self) -> bool:
        """
        Stop laser spot smoothing module motor.

        Returns:
            True if motor stopped successfully
        """
        if not self.is_connected:
            return False

        with self._lock:
            try:
                response = self._send_command("MOTOR_OFF", expected_prefix="OK:MOTOR_OFF")

                if "OK:MOTOR_OFF" in response:
                    self.motor_enabled = False
                    self.motor_speed_pwm = 0
                    self.smoothing_motor_changed.emit(False)
                    self.motor_speed_changed.emit(0)
                    logger.info("Smoothing motor stopped")

                    # Log event
                    if self.event_logger:
                        from core.event_logger import EventType

                        self.event_logger.log_event(
                            event_type=EventType.SAFETY_GPIO_FAIL,
                            description="Smoothing motor stopped (safety interlock inactive)",
                        )

                    self._update_safety_status()
                    return True
                else:
                    raise RuntimeError(f"Unexpected response: {response}")

            except Exception as e:
                error_msg = f"Failed to stop motor: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def set_motor_speed(self, pwm: int) -> bool:
        """
        Set laser spot smoothing module speed using PWM (0-153).

        PWM Range:
            0   = Motor OFF (0V)
            76  = 1.5V (minimum rated speed)
            153 = 3.0V (maximum safe speed)

        Args:
            pwm: PWM value (0-153)

        Returns:
            True if speed set successfully
        """
        if not self.is_connected:
            self.error_occurred.emit("GPIO not connected")
            return False

        # Clamp PWM to safe range
        pwm = max(0, min(153, pwm))

        with self._lock:
            try:
                if pwm == 0:
                    # Stop motor
                    response = self._send_command("MOTOR_OFF", expected_prefix="OK:MOTOR_OFF")
                    if "OK:MOTOR_OFF" in response:
                        self.motor_enabled = False
                        self.motor_speed_pwm = 0
                        self.motor_speed_changed.emit(0)
                        self.smoothing_motor_changed.emit(False)
                        logger.info("Motor stopped (PWM=0)")
                        return True
                else:
                    # Set motor speed
                    response = self._send_command(
                        f"MOTOR_SPEED:{pwm}", expected_prefix="OK:MOTOR_SPEED:"
                    )

                    if f"OK:MOTOR_SPEED:{pwm}" in response:
                        self.motor_enabled = True
                        self.motor_speed_pwm = pwm
                        self.motor_speed_changed.emit(pwm)
                        self.smoothing_motor_changed.emit(True)
                        voltage = (pwm / 255.0) * 5.0
                        logger.info(f"Motor speed set to PWM {pwm} ({voltage:.2f}V)")
                        return True
                    else:
                        raise RuntimeError(f"Unexpected response: {response}")

            except Exception as e:
                error_msg = f"Failed to set motor speed: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def init_accelerometer(self) -> bool:
        """
        Initialize MPU6050 accelerometer.

        Must be called before reading acceleration data.
        Uses motor-first sequence to avoid reset.

        Returns:
            True if accelerometer initialized successfully
        """
        if not self.is_connected:
            self.error_occurred.emit("GPIO not connected")
            return False

        with self._lock:
            try:
                response = self._send_command("ACCEL_INIT")

                if "OK:ACCEL_INITIALIZED" in response or "0x68" in response:
                    self.accelerometer_initialized = True
                    logger.info("Accelerometer (MPU6050) initialized at 0x68")
                    return True
                else:
                    self.accelerometer_initialized = False
                    raise RuntimeError(f"Accelerometer not found: {response}")

            except Exception as e:
                error_msg = f"Failed to initialize accelerometer: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                self.accelerometer_initialized = False
                return False

    def get_acceleration(self) -> tuple[float, float, float] | None:
        """
        Read X, Y, Z acceleration from MPU6050.

        Returns:
            (x, y, z) acceleration in g's, or None if failed
        """
        if not self.is_connected or not self.accelerometer_initialized:
            return None

        with self._lock:
            try:
                response = self._send_command("GET_ACCEL")

                # Parse response: "ACCEL:X,Y,Z"
                for line in response.split("\n"):
                    if "ACCEL:" in line:
                        data = line.split("ACCEL:")[1].strip()
                        x, y, z = map(float, data.split(","))

                        self.accel_x = x
                        self.accel_y = y
                        self.accel_z = z
                        self.accelerometer_data_changed.emit(x, y, z)

                        return (x, y, z)

                return None

            except Exception as e:
                logger.error(f"Failed to read acceleration: {e}")
                return None

    def get_vibration_level(self) -> float | None:
        """
        Read vibration magnitude from MPU6050.

        Returns:
            Vibration magnitude in g's, or None if failed
        """
        if not self.is_connected or not self.accelerometer_initialized:
            return None

        with self._lock:
            try:
                response = self._send_command("GET_VIBRATION_LEVEL")

                # Parse response: "VIBRATION:magnitude"
                for line in response.split("\n"):
                    if "VIBRATION:" in line:
                        vib = float(line.split("VIBRATION:")[1].strip())

                        self.vibration_level = vib
                        self.vibration_level_changed.emit(vib)

                        return vib

                return None

            except Exception as e:
                logger.error(f"Failed to read vibration level: {e}")
                return None

    def start_aiming_laser(self) -> bool:
        """
        Start aiming laser (GPIO voltage output).

        Returns:
            True if aiming laser started successfully
        """
        if not self.is_connected:
            self.error_occurred.emit("GPIO not connected")
            return False

        with self._lock:
            try:
                response = self._send_command("LASER_ON", expected_prefix="OK:LASER_ON")

                if "OK:LASER_ON" in response:
                    self.aiming_laser_enabled = True
                    self.aiming_laser_changed.emit(True)
                    logger.info("Aiming laser enabled")

                    if self.event_logger:
                        from core.event_logger import EventType

                        self.event_logger.log_event(
                            event_type=EventType.TREATMENT_LASER_ON,
                            description="Aiming laser enabled",
                            details={"laser_type": "aiming"},
                        )

                    return True
                else:
                    raise RuntimeError(f"Unexpected response: {response}")

            except Exception as e:
                error_msg = f"Failed to enable aiming laser: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def stop_aiming_laser(self) -> bool:
        """
        Stop aiming laser (GPIO voltage output).

        Returns:
            True if aiming laser stopped successfully
        """
        if not self.is_connected:
            return False

        with self._lock:
            try:
                response = self._send_command("LASER_OFF", expected_prefix="OK:LASER_OFF")

                if "OK:LASER_OFF" in response:
                    self.aiming_laser_enabled = False
                    self.aiming_laser_changed.emit(False)
                    logger.info("Aiming laser disabled")

                    if self.event_logger:
                        from core.event_logger import EventType

                        self.event_logger.log_event(
                            event_type=EventType.TREATMENT_LASER_OFF,
                            description="Aiming laser disabled",
                            details={"laser_type": "aiming"},
                        )

                    return True
                else:
                    raise RuntimeError(f"Unexpected response: {response}")

            except Exception as e:
                error_msg = f"Failed to disable aiming laser: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def reinitialize_accelerometer(self) -> bool:
        """
        Manually reinitialize accelerometer (force I2C re-scan).

        The Arduino firmware only scans for the accelerometer once during setup().
        If the accelerometer wasn't ready at that moment, it stays undetected forever.
        This method forces a re-scan and initialization.

        Useful when:
        - Accelerometer was plugged in after Arduino powered on
        - I2C bus had temporary communication issues
        - Accelerometer needs to be reset

        Returns:
            True if accelerometer initialized successfully, False otherwise
        """
        if not self.is_connected:
            logger.warning("Cannot reinitialize accelerometer: GPIO not connected")
            return False

        with self._lock:
            try:
                logger.info("Manually reinitializing accelerometer...")
                response = self._send_command("ACCEL_INIT")

                if "OK:ACCEL_INITIALIZED" in response:
                    logger.info("Accelerometer reinitialized successfully")
                    return True
                elif "ERROR:NO_ACCEL_FOUND" in response:
                    logger.warning(
                        "No accelerometer detected on I2C bus - "
                        "check hardware connections (SDA=A4, SCL=A5)"
                    )
                    return False
                else:
                    logger.warning(f"Unexpected accelerometer init response: {response}")
                    return False

            except Exception as e:
                error_msg = f"Accelerometer reinitialization failed: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def _update_status(self) -> None:  # noqa: C901
        """Update all sensor readings (called by timer)."""
        if not self.is_connected:
            return

        with self._lock:
            try:
                # Read vibration level from accelerometer
                response = self._send_command("GET_VIBRATION_LEVEL", expected_prefix="VIBRATION:")
                if "VIBRATION:" in response:
                    try:
                        value_str = response.split(":")[1].strip()
                        vibration_magnitude = float(value_str)
                        self.vibration_level = vibration_magnitude
                        self.vibration_level_changed.emit(vibration_magnitude)

                        # Detect vibration above calibrated threshold
                        current_vibration = vibration_magnitude > self.VIBRATION_THRESHOLD_G

                        # Debounce vibration detection
                        if current_vibration:
                            self.vibration_debounce_count += 1
                            if self.vibration_debounce_count >= self.vibration_debounce_threshold:
                                if not self.vibration_detected:
                                    self.vibration_detected = True
                                    self.smoothing_vibration_changed.emit(True)
                                    logger.debug(f"Vibration detected: {vibration_magnitude:.3f}g")
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Failed to parse vibration value: {e}")
                else:
                    # Reset debounce counter if no vibration
                    if self.vibration_debounce_count > 0:
                        self.vibration_debounce_count -= 1
                        if self.vibration_debounce_count == 0 and self.vibration_detected:
                            self.vibration_detected = False
                            self.smoothing_vibration_changed.emit(False)
                            logger.debug("Vibration stopped (debounced)")

                # Update safety interlock status
                self._update_safety_status()

                # Read photodiode laser pickoff measurement voltage
                response = self._send_command(
                    "GET_PHOTODIODE", expected_prefix="photodiode laser pickoff measurement:"
                )
                if "photodiode laser pickoff measurement:" in response:
                    voltage_str = response.split(":")[1].strip()
                    self.photodiode_voltage = float(voltage_str)
                    self.photodiode_voltage_changed.emit(self.photodiode_voltage)

                    # Calculate laser power (mW)
                    self.photodiode_power_mw = (
                        self.photodiode_voltage * self.photodiode_voltage_to_power
                    )
                    self.photodiode_power_changed.emit(self.photodiode_power_mw)

            except Exception as e:
                logger.error(f"Error reading sensors: {e}")

    def _update_safety_status(self) -> None:
        """
        Update safety interlock status.

        Safety OK when:
        - Motor is ON
        - Vibration is detected (motor is working)
        """
        safety_ok = self.motor_enabled and self.vibration_detected
        self.safety_interlock_changed.emit(safety_ok)

    def get_safety_status(self) -> bool:
        """
        Get current safety interlock status.

        Returns:
            True if safety conditions met
        """
        with self._lock:
            return self.motor_enabled and self.vibration_detected

    def get_photodiode_voltage(self) -> float:
        """
        Get current photodiode laser pickoff measurement voltage.

        Returns:
            Voltage in V (0-5V)
        """
        with self._lock:
            return self.photodiode_voltage

    def get_photodiode_power(self) -> float:
        """
        Get calculated laser power from photodiode laser pickoff measurement.

        Returns:
            Power in mW
        """
        with self._lock:
            return self.photodiode_power_mw
