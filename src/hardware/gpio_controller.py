# -*- coding: utf-8 -*-
"""
GPIO hardware abstraction layer for Arduino Nano safety interlocks.

Provides PyQt6-integrated GPIO control for:
- Smoothing device control and monitoring
- Photodiode laser power monitoring
- Aiming laser control
- Hardware watchdog timer heartbeat
- Thread-safe serial communication

Arduino Nano Pin Configuration:
- Digital Pin 2: Smoothing motor control (output)
- Digital Pin 3: Smoothing vibration sensor (input with pullup)
- Digital Pin 4: Aiming laser control (output)
- Analog Pin A0: Photodiode laser power monitoring (0-5V)

Serial Protocol (9600 baud, ASCII text commands):
- WDT_RESET: Reset watchdog timer (heartbeat)
- MOTOR_ON/MOTOR_OFF: Control smoothing motor
- LASER_ON/LASER_OFF: Control aiming laser
- GET_VIBRATION: Read vibration sensor
- GET_PHOTODIODE: Read photodiode voltage
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
    - Photodiode laser power monitoring (analog input)
    - Aiming laser control (digital output)
    - Hardware watchdog heartbeat
    """

    # Signals
    smoothing_motor_changed = pyqtSignal(bool)  # Motor state (on/off)
    smoothing_vibration_changed = pyqtSignal(bool)  # Vibration detected
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
        self.aiming_laser_enabled = False
        self.vibration_detected = False
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

                # Verify firmware responds
                response = self._send_command("GET_STATUS")
                if "STATUS:" not in response:
                    raise RuntimeError(f"Invalid firmware response: {response}")

                logger.info("Arduino watchdog firmware detected")

                self.is_connected = True
                self.connection_changed.emit(True)

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_hardware_event(
                        event_type=EventType.HARDWARE_GPIO_CONNECT,
                        description=f"Arduino GPIO connected on {port}",
                        device_name="Arduino Nano (Watchdog Firmware)",
                    )

                # Start monitoring
                self.monitor_timer.start()
                logger.info("GPIO controller connected successfully")

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
                    from ..core.event_logger import EventSeverity, EventType

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
                from ..core.event_logger import EventType

                self.event_logger.log_hardware_event(
                    event_type=EventType.HARDWARE_GPIO_DISCONNECT,
                    description="Arduino GPIO disconnected",
                    device_name="Arduino Nano",
                )

    def _send_command(self, command: str, expect_response: bool = True) -> str:
        """
        Send command to Arduino and read response.

        Args:
            command: Command string (e.g., "WDT_RESET", "MOTOR_ON")
            expect_response: Whether to wait for response

        Returns:
            Response string from Arduino (or empty if no response expected)

        Raises:
            RuntimeError: If serial communication fails
        """
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Serial port not open")

        with self._lock:
            try:
                # Send command with newline terminator
                cmd_bytes = (command + "\n").encode("utf-8")
                self.serial.write(cmd_bytes)
                logger.debug(f"Sent: {command}")

                if not expect_response:
                    return ""

                # Read response (single line)
                response: str = self.serial.readline().decode("utf-8").strip()
                logger.debug(f"Received: {response}")

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
                response = self._send_command("WDT_RESET")
                return "OK:WDT_RESET" in response
            except Exception as e:
                logger.error(f"Watchdog heartbeat failed: {e}")
                return False

    def start_smoothing_motor(self) -> bool:
        """
        Start smoothing device motor.

        Returns:
            True if motor started successfully
        """
        if not self.is_connected:
            self.error_occurred.emit("GPIO not connected")
            return False

        with self._lock:
            try:
                response = self._send_command("MOTOR_ON")

                if "OK:MOTOR_ON" in response:
                    self.motor_enabled = True
                    self.smoothing_motor_changed.emit(True)
                    logger.info("Smoothing motor started")

                    # Log event
                    if self.event_logger:
                        from ..core.event_logger import EventType

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
        Stop smoothing device motor.

        Returns:
            True if motor stopped successfully
        """
        if not self.is_connected:
            return False

        with self._lock:
            try:
                response = self._send_command("MOTOR_OFF")

                if "OK:MOTOR_OFF" in response:
                    self.motor_enabled = False
                    self.smoothing_motor_changed.emit(False)
                    logger.info("Smoothing motor stopped")

                    # Log event
                    if self.event_logger:
                        from ..core.event_logger import EventType

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
                response = self._send_command("LASER_ON")

                if "OK:LASER_ON" in response:
                    self.aiming_laser_enabled = True
                    self.aiming_laser_changed.emit(True)
                    logger.info("Aiming laser enabled")

                    if self.event_logger:
                        from ..core.event_logger import EventType

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
                response = self._send_command("LASER_OFF")

                if "OK:LASER_OFF" in response:
                    self.aiming_laser_enabled = False
                    self.aiming_laser_changed.emit(False)
                    logger.info("Aiming laser disabled")

                    if self.event_logger:
                        from ..core.event_logger import EventType

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

    def _update_status(self) -> None:
        """Update all sensor readings (called by timer)."""
        if not self.is_connected:
            return

        with self._lock:
            try:
                # Read vibration sensor
                response = self._send_command("GET_VIBRATION")
                if "VIBRATION:" in response:
                    value = response.split(":")[1].strip()
                    current_vibration = value == "1"

                    # Debounce vibration detection
                    if current_vibration:
                        self.vibration_debounce_count += 1
                        if self.vibration_debounce_count >= self.vibration_debounce_threshold:
                            if not self.vibration_detected:
                                self.vibration_detected = True
                                self.smoothing_vibration_changed.emit(True)
                                logger.debug("Vibration detected (debounced)")
                                self._update_safety_status()
                    else:
                        if self.vibration_detected:
                            self.vibration_detected = False
                            self.smoothing_vibration_changed.emit(False)
                            logger.debug("Vibration stopped")
                            self._update_safety_status()
                        self.vibration_debounce_count = 0

                # Read photodiode voltage
                response = self._send_command("GET_PHOTODIODE")
                if "PHOTODIODE:" in response:
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
        Get current photodiode voltage.

        Returns:
            Voltage in V (0-5V)
        """
        with self._lock:
            return self.photodiode_voltage

    def get_photodiode_power(self) -> float:
        """
        Get calculated laser power from photodiode.

        Returns:
            Power in mW
        """
        with self._lock:
            return self.photodiode_power_mw
