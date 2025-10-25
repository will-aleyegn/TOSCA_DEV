# -*- coding: utf-8 -*-
"""
GPIO hardware abstraction layer for Arduino Nano safety interlocks.

Provides PyQt6-integrated GPIO control for:
- Smoothing device control and monitoring
- Photodiode laser power monitoring
- Aiming laser control

Arduino Nano Pin Configuration:
- Digital Pin 2: Smoothing motor control (output)
- Digital Pin 3: Smoothing vibration sensor (input with pullup)
- Digital Pin 4: Aiming laser control (output)
- Analog Pin A0: Photodiode laser power monitoring (0-5V)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)

# Try to import pyfirmata2
try:
    from pyfirmata2 import Arduino, util

    PYFIRMATA_AVAILABLE = True
except ImportError:
    PYFIRMATA_AVAILABLE = False
    logger.warning("pyfirmata2 not available - GPIO features disabled")


class GPIOController(QObject):
    """
    Arduino Nano GPIO controller with PyQt6 integration.

    Manages safety interlocks:
    - Smoothing device motor control (digital output)
    - Smoothing device vibration sensor (digital input)
    - Photodiode laser power monitoring (analog input)
    - Aiming laser control (digital output)
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

        self.hardware_available = PYFIRMATA_AVAILABLE
        self.event_logger = event_logger

        if not PYFIRMATA_AVAILABLE:
            logger.warning(
                "GPIO controller initialized in DISABLED mode - pyfirmata2 not available"
            )

        # Hardware objects
        self.board: Optional[Arduino] = None
        self.iterator: Optional[util.Iterator] = None

        # Pin configuration
        self.motor_pin_number = 2  # Digital pin 2
        self.vibration_pin_number = 3  # Digital pin 3
        self.aiming_laser_pin_number = 4  # Digital pin 4
        self.photodiode_pin_number = 0  # Analog pin A0 (0 in pyfirmata)

        # Pin objects (will be set during connect)
        self.motor_pin = None
        self.vibration_pin = None
        self.aiming_laser_pin = None
        self.photodiode_pin = None

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

        logger.info("GPIO controller initialized")

    def connect(self, port: str = "COM4") -> bool:
        """
        Connect to Arduino Nano and initialize GPIO pins.

        Arduino Nano Pin Configuration:
        - Digital Pin 2: Smoothing motor control (output)
        - Digital Pin 3: Smoothing vibration sensor (input with pullup)
        - Digital Pin 4: Aiming laser control (output)
        - Analog Pin A0: Photodiode input (0-5V, 10-bit ADC)

        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)

        Returns:
            True if connected successfully
        """
        if not self.hardware_available:
            self.error_occurred.emit("GPIO hardware not available - pyfirmata2 not installed")
            logger.warning("Cannot connect - pyfirmata2 not available")
            return False

        try:
            # Connect to Arduino
            self.board = Arduino(port)
            logger.info(f"Connected to Arduino on {port}")

            # Start iterator for analog/digital read
            self.iterator = util.Iterator(self.board)
            self.iterator.start()

            # Configure motor control pin (digital output)
            self.motor_pin = self.board.get_pin(f"d:{self.motor_pin_number}:o")
            if self.motor_pin:
                self.motor_pin.write(0)  # Start with motor off
            logger.info(f"Motor control pin initialized (D{self.motor_pin_number})")

            # Configure vibration sensor pin (digital input with pullup)
            self.vibration_pin = self.board.get_pin(f"d:{self.vibration_pin_number}:i")
            if self.vibration_pin:
                self.vibration_pin.enable_reporting()
            logger.info(f"Vibration sensor pin initialized (D{self.vibration_pin_number})")

            # Configure aiming laser control pin (digital output)
            self.aiming_laser_pin = self.board.get_pin(f"d:{self.aiming_laser_pin_number}:o")
            if self.aiming_laser_pin:
                self.aiming_laser_pin.write(0)  # Start with aiming laser off
            logger.info(f"Aiming laser control pin initialized (D{self.aiming_laser_pin_number})")

            # Configure photodiode pin (analog input)
            self.photodiode_pin = self.board.get_pin(f"a:{self.photodiode_pin_number}:i")
            if self.photodiode_pin:
                self.photodiode_pin.enable_reporting()
            logger.info(f"Photodiode pin initialized (A{self.photodiode_pin_number})")

            self.is_connected = True
            self.connection_changed.emit(True)

            # Log event
            if self.event_logger:
                from ..core.event_logger import EventType

                self.event_logger.log_hardware_event(
                    event_type=EventType.HARDWARE_GPIO_CONNECT,
                    description=f"Arduino GPIO connected on {port}",
                    device_name="Arduino Nano",
                )

            # Start monitoring
            self.monitor_timer.start()
            logger.info("GPIO controller connected successfully")

            return True

        except Exception as e:
            error_msg = f"Arduino connection failed: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

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
        self.stop_smoothing_motor()
        self.stop_aiming_laser()
        self.monitor_timer.stop()

        if self.board:
            try:
                self.board.exit()
            except Exception as e:
                logger.warning(f"Error closing Arduino connection: {e}")
            self.board = None

        self.iterator = None
        self.motor_pin = None
        self.vibration_pin = None
        self.aiming_laser_pin = None
        self.photodiode_pin = None

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

    def start_smoothing_motor(self) -> bool:
        """
        Start smoothing device motor.

        Returns:
            True if motor started successfully
        """
        if not self.is_connected or not self.motor_pin:
            self.error_occurred.emit("GPIO not connected")
            return False

        try:
            self.motor_pin.write(1)
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
        if not self.is_connected or not self.motor_pin:
            return False

        try:
            self.motor_pin.write(0)
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

        except Exception as e:
            error_msg = f"Failed to stop motor: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def _update_status(self) -> None:  # noqa: C901
        """Update all sensor readings (called by timer)."""
        if not self.is_connected:
            return

        try:
            # Read vibration sensor (digital input)
            # pyfirmata2 uses .value (cached by iterator thread) instead of .read()
            if self.vibration_pin:
                vibration_reading = self.vibration_pin.value
                if vibration_reading is not None:
                    current_vibration = bool(vibration_reading)

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

            # Read photodiode voltage (analog input, 0-5V)
            # pyfirmata2 uses .value (cached by iterator thread) instead of .read()
            if self.photodiode_pin:
                voltage_reading = self.photodiode_pin.value
                if voltage_reading is not None:
                    # pyfirmata2 returns 0.0-1.0, scale to 0-5V
                    self.photodiode_voltage = voltage_reading * 5.0
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
        return self.motor_enabled and self.vibration_detected

    def get_photodiode_voltage(self) -> float:
        """
        Get current photodiode voltage.

        Returns:
            Voltage in V (0-5V)
        """
        return self.photodiode_voltage

    def get_photodiode_power(self) -> float:
        """
        Get calculated laser power from photodiode.

        Returns:
            Power in mW
        """
        return self.photodiode_power_mw

    def start_aiming_laser(self) -> bool:
        """
        Start aiming laser (GPIO voltage output).

        Returns:
            True if aiming laser started successfully
        """
        if not self.is_connected or not self.aiming_laser_pin:
            self.error_occurred.emit("GPIO not connected")
            return False

        try:
            self.aiming_laser_pin.write(1)
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
        if not self.is_connected or not self.aiming_laser_pin:
            return False

        try:
            self.aiming_laser_pin.write(0)
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

        except Exception as e:
            error_msg = f"Failed to disable aiming laser: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
