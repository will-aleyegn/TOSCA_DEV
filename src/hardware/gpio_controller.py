# -*- coding: utf-8 -*-
"""
GPIO hardware abstraction layer for FT232H safety interlocks.

Provides PyQt6-integrated GPIO control for:
- Smoothing device control and monitoring
- Photodiode laser power monitoring
"""

import logging
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)

# Try to import Adafruit libraries
try:
    import board
    import busio
    import digitalio
    from adafruit_mcp3xxx.analog_in import AnalogIn
    from adafruit_mcp3xxx.mcp3008 import MCP3008

    ADAFRUIT_AVAILABLE = True
except ImportError:
    ADAFRUIT_AVAILABLE = False
    logger.warning("Adafruit libraries not available - GPIO features disabled")


class GPIOController(QObject):
    """
    FT232H GPIO controller with PyQt6 integration.

    Manages safety interlocks:
    - Smoothing device motor control (digital output)
    - Smoothing device vibration sensor (digital input)
    - Photodiode laser power monitoring (analog input via MCP3008)
    """

    # Signals
    smoothing_motor_changed = pyqtSignal(bool)  # Motor state (on/off)
    smoothing_vibration_changed = pyqtSignal(bool)  # Vibration detected
    photodiode_voltage_changed = pyqtSignal(float)  # Voltage in V
    photodiode_power_changed = pyqtSignal(float)  # Calculated power in mW
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)  # Error message
    safety_interlock_changed = pyqtSignal(bool)  # Safety OK status

    def __init__(self) -> None:
        super().__init__()

        if not ADAFRUIT_AVAILABLE:
            raise ImportError("Adafruit libraries not installed - GPIO features unavailable")

        # Hardware objects
        self.smoothing_motor_pin: Optional[digitalio.DigitalInOut] = None
        self.smoothing_sensor_pin: Optional[digitalio.DigitalInOut] = None
        self.spi: Optional[busio.SPI] = None
        self.mcp: Optional[MCP3008] = None
        self.photodiode_channel: Optional[AnalogIn] = None

        # State tracking
        self.is_connected = False
        self.motor_enabled = False
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

    def connect(self) -> bool:
        """
        Connect to FT232H and initialize GPIO pins and ADC.

        Pin Configuration:
        - C0: Smoothing motor control (digital output)
        - C1: Smoothing vibration sensor (digital input)
        - MCP3008 Ch0: Photodiode input (analog via SPI)

        Returns:
            True if connected successfully
        """
        try:
            # Initialize smoothing motor control (digital output)
            self.smoothing_motor_pin = digitalio.DigitalInOut(board.C0)
            self.smoothing_motor_pin.direction = digitalio.Direction.OUTPUT
            self.smoothing_motor_pin.value = False  # Start with motor off
            logger.info("Smoothing motor pin initialized (C0)")

            # Initialize smoothing vibration sensor (digital input)
            self.smoothing_sensor_pin = digitalio.DigitalInOut(board.C1)
            self.smoothing_sensor_pin.direction = digitalio.Direction.INPUT
            logger.info("Smoothing sensor pin initialized (C1)")

            # Initialize SPI for MCP3008 ADC
            self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(board.C2)  # Chip select on C2
            self.mcp = MCP3008(self.spi, cs)
            self.photodiode_channel = AnalogIn(self.mcp, 0)  # Channel 0
            logger.info("MCP3008 ADC initialized on SPI with CS on C2")

            self.is_connected = True
            self.connection_changed.emit(True)

            # Start monitoring
            self.monitor_timer.start()
            logger.info("GPIO controller connected successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to connect GPIO: {e}")
            self.error_occurred.emit(f"GPIO connection failed: {e}")
            self.is_connected = False
            self.connection_changed.emit(False)
            return False

    def disconnect(self) -> None:
        """Disconnect from GPIO and cleanup resources."""
        if not self.is_connected:
            return

        try:
            # Stop monitoring
            self.monitor_timer.stop()

            # Turn off smoothing motor
            if self.smoothing_motor_pin:
                self.smoothing_motor_pin.value = False
                self.motor_enabled = False
                self.smoothing_motor_changed.emit(False)

            # Cleanup pins
            if self.smoothing_motor_pin:
                self.smoothing_motor_pin.deinit()
            if self.smoothing_sensor_pin:
                self.smoothing_sensor_pin.deinit()

            # Cleanup SPI
            if self.spi:
                self.spi.deinit()

            self.is_connected = False
            self.connection_changed.emit(False)
            logger.info("GPIO controller disconnected")

        except Exception as e:
            logger.error(f"Error during GPIO disconnect: {e}")
            self.error_occurred.emit(f"Disconnect error: {e}")

    def set_smoothing_motor(self, enabled: bool) -> bool:
        """
        Enable or disable smoothing device motor.

        Args:
            enabled: True to turn motor on, False to turn off

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to GPIO")
            return False

        try:
            self.smoothing_motor_pin.value = enabled
            self.motor_enabled = enabled
            self.smoothing_motor_changed.emit(enabled)
            logger.info(f"Smoothing motor {'enabled' if enabled else 'disabled'}")
            return True

        except Exception as e:
            logger.error(f"Failed to set motor state: {e}")
            self.error_occurred.emit(f"Motor control failed: {e}")
            return False

    def read_smoothing_vibration(self) -> bool:
        """
        Read smoothing device vibration sensor.

        Uses debouncing to ensure stable reading.

        Returns:
            True if vibration detected, False otherwise
        """
        if not self.is_connected or not self.smoothing_sensor_pin:
            return False

        try:
            # Read current sensor state
            sensor_high = self.smoothing_sensor_pin.value

            # Debounce logic
            if sensor_high:
                self.vibration_debounce_count = min(
                    self.vibration_debounce_count + 1, self.vibration_debounce_threshold
                )
            else:
                self.vibration_debounce_count = max(self.vibration_debounce_count - 1, 0)

            # Update state if threshold crossed
            new_state = self.vibration_debounce_count >= self.vibration_debounce_threshold

            if new_state != self.vibration_detected:
                self.vibration_detected = new_state
                self.smoothing_vibration_changed.emit(new_state)
                logger.debug(f"Vibration detected: {new_state}")

            return new_state

        except Exception as e:
            logger.error(f"Failed to read vibration sensor: {e}")
            return False

    def read_photodiode(self) -> float:
        """
        Read photodiode voltage and calculate laser power.

        Returns:
            Voltage in volts (0-5V)
        """
        if not self.is_connected or not self.photodiode_channel:
            return 0.0

        try:
            # Read voltage from ADC
            voltage: float = float(self.photodiode_channel.voltage)
            self.photodiode_voltage = voltage

            # Calculate power (mW) from voltage
            # Assuming linear relationship: 5V = 2000mW
            power_mw = voltage * self.photodiode_voltage_to_power
            self.photodiode_power_mw = power_mw

            # Emit signals
            self.photodiode_voltage_changed.emit(voltage)
            self.photodiode_power_changed.emit(power_mw)

            return voltage

        except Exception as e:
            logger.error(f"Failed to read photodiode: {e}")
            return 0.0

    def is_safety_ok(self) -> bool:
        """
        Check if safety interlocks are satisfied.

        Safety requirements:
        - Smoothing device motor must be enabled
        - Smoothing device must be vibrating (sensor HIGH)

        Returns:
            True if all safety conditions met
        """
        safety_ok = self.motor_enabled and self.vibration_detected
        return safety_ok

    def set_photodiode_calibration(self, voltage_to_power: float) -> None:
        """
        Set photodiode calibration factor.

        Args:
            voltage_to_power: mW per volt conversion factor
        """
        self.photodiode_voltage_to_power = voltage_to_power
        logger.info(f"Photodiode calibration set to {voltage_to_power:.1f} mW/V")

    def _update_status(self) -> None:
        """Update status from sensors (called by timer)."""
        if not self.is_connected:
            return

        try:
            # Read smoothing vibration sensor
            self.read_smoothing_vibration()

            # Read photodiode
            self.read_photodiode()

            # Check safety interlock
            safety_ok = self.is_safety_ok()
            self.safety_interlock_changed.emit(safety_ok)

        except Exception as e:
            logger.error(f"Status update error: {e}")
            self.error_occurred.emit(f"Monitoring error: {e}")
