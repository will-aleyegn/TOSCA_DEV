# -*- coding: utf-8 -*-
"""
TEC (Thermoelectric Cooler) hardware abstraction layer for Arroyo Instruments.

Provides PyQt6-integrated TEC control with:
- Temperature setpoint control
- Temperature monitoring
- Output enable/disable
- PID control configuration
- Safety limits
- Status monitoring
- Thread-safe serial communication
"""

import logging
import threading
from typing import Any, Optional

import serial
from PyQt6.QtCore import QTimer, pyqtSignal

from .hardware_controller_base import HardwareControllerBase

logger = logging.getLogger(__name__)


class TECController(HardwareControllerBase):
    """
    Arroyo TEC controller with PyQt6 integration.

    Provides thread-safe TEC operations with Qt signals for temperature control.
    Uses Arroyo serial command protocol (TEC: commands).
    """

    # Signals
    temperature_changed = pyqtSignal(float)  # Actual temperature in °C
    temperature_setpoint_changed = pyqtSignal(float)  # Setpoint temperature in °C
    output_changed = pyqtSignal(bool)  # True=enabled, False=disabled
    current_changed = pyqtSignal(float)  # TEC current in A
    voltage_changed = pyqtSignal(float)  # TEC voltage in V
    status_changed = pyqtSignal(str)  # Status description
    limit_warning = pyqtSignal(str)  # Limit warning message

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__(event_logger)

        self.ser: Optional[serial.Serial] = None
        self.is_output_enabled = False

        # Thread safety lock for serial communication (reentrant for nested calls)
        self._lock = threading.RLock()

        # Monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_status)
        self.monitor_timer.setInterval(500)  # Update every 500ms

        # Settings
        self.temperature_setpoint_c = 25.0

        # Safety limits (will be read from device)
        self.max_temperature_c = 35.0
        self.min_temperature_c = 15.0

        logger.info("TEC controller initialized (thread-safe)")

    def connect(self, com_port: str = "COM9", baudrate: int = 38400) -> bool:
        """
        Connect to Arroyo TEC controller.

        Args:
            com_port: Serial port (e.g., "COM9")
            baudrate: Communication speed (default 38400)

        Returns:
            True if connected successfully
        """
        with self._lock:
            try:
                self.ser = serial.Serial(
                    port=com_port,
                    baudrate=baudrate,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1.0,
                    write_timeout=1.0,
                )

                if self.ser.is_open:
                    # Test connection with ID query
                    response = self._write_command("*IDN?")
                    if response:
                        logger.info(f"Connected to TEC: {response}")
                        self.is_connected = True
                        self.connection_changed.emit(True)
                        self.status_changed.emit("connected")

                        # Log event
                        if self.event_logger:
                            from ..core.event_logger import EventType

                            self.event_logger.log_hardware_event(
                                event_type=EventType.HARDWARE_TEC_CONNECT,
                                description=f"TEC connected: {response.strip()}",
                                device_name="Arroyo TEC Controller",
                            )

                        # Read initial limits
                        self._read_limits()

                        # Start monitoring
                        self.monitor_timer.start()

                        return True
                    else:
                        logger.error("No response from TEC controller")
                        self.ser.close()
                        return False
                else:
                    logger.error(f"Failed to open {com_port}")
                    return False

            except serial.SerialException as e:
                logger.error(f"Serial connection error: {e}")
                self.error_occurred.emit(f"Connection failed: {e}")

                # Log error event
                if self.event_logger:
                    from ..core.event_logger import EventSeverity, EventType

                    self.event_logger.log_event(
                        event_type=EventType.HARDWARE_ERROR,
                        description=f"TEC connection failed: {e}",
                        severity=EventSeverity.WARNING,
                        details={"device": "Arroyo TEC Controller", "port": com_port},
                    )

                return False
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                self.error_occurred.emit(f"Connection failed: {e}")
                return False

    def disconnect(self) -> None:
        """Disconnect from TEC controller."""
        with self._lock:
            if self.ser and self.ser.is_open:
                # Disable output before disconnecting
                self.set_output(False)

                # Stop monitoring
                self.monitor_timer.stop()

                # Close serial port
                self.ser.close()
                self.is_connected = False
                self.connection_changed.emit(False)
                self.status_changed.emit("disconnected")
                logger.info("Disconnected from TEC controller")

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_hardware_event(
                        event_type=EventType.HARDWARE_TEC_DISCONNECT,
                        description="TEC disconnected",
                        device_name="Arroyo TEC Controller",
                    )

    def get_status(self) -> dict[str, Any]:
        """
        Get current TEC status and state information.

        Returns:
            Dictionary containing:
            - connected (bool): Connection status
            - output_enabled (bool): TEC output state
            - temperature_setpoint_c (float): Temperature setpoint in °C
        """
        with self._lock:
            return {
                "connected": self.is_connected,
                "output_enabled": self.is_output_enabled,
                "temperature_setpoint_c": self.temperature_setpoint_c,
            }

    def _write_command(self, command: str) -> Optional[str]:
        """
        Send command to TEC controller and return response.

        Args:
            command: ASCII command string

        Returns:
            Response string or None if error
        """
        if not self.ser or not self.ser.is_open:
            logger.error("Serial port not open")
            return None

        with self._lock:
            try:
                # Send command
                self.ser.write(str.encode(command) + b"\r\n")

                # Read response for query commands
                if "?" in command:
                    response: str = self.ser.readline().decode("utf-8").strip()
                    return response
                return ""

            except serial.SerialException as e:
                logger.error(f"Serial communication error: {e}")
                self.error_occurred.emit(f"Communication error: {e}")
                return None
            except Exception as e:
                logger.error(f"Command error: {e}")
                self.error_occurred.emit(f"Command error: {e}")
                return None

    def _read_limits(self) -> None:
        """Read safety limits from device."""
        try:
            # Read TEC temperature limits
            response = self._write_command("TEC:LIM:THI?")
            if response:
                self.max_temperature_c = float(response)

            response = self._write_command("TEC:LIM:TLO?")
            if response:
                self.min_temperature_c = float(response)

            logger.info(f"Limits: Temp={self.min_temperature_c:.1f}-{self.max_temperature_c:.1f}°C")

        except Exception as e:
            logger.warning(f"Failed to read limits: {e}")

    def set_output(self, enabled: bool) -> bool:
        """
        Enable or disable TEC output.

        Args:
            enabled: True to enable, False to disable

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to TEC controller")
            return False

        with self._lock:
            try:
                value = 1 if enabled else 0
                self._write_command(f"TEC:OUT {value}")

                # Verify
                response = self._write_command("TEC:OUT?")
                if response and int(response) == value:
                    self.is_output_enabled = enabled
                    self.output_changed.emit(enabled)
                    status = "enabled" if enabled else "disabled"
                    logger.info(f"TEC output {status}")

                    # Log event
                    if self.event_logger:
                        from ..core.event_logger import EventType

                        event_type = EventType.TEC_ENABLED if enabled else EventType.TEC_DISABLED
                        self.event_logger.log_event(
                            event_type=event_type,
                            description=f"TEC output {status}",
                            details={"temperature_setpoint": self.temperature_setpoint_c},
                        )

                    return True
                else:
                    logger.error("Failed to set output")
                    return False

            except Exception as e:
                logger.error(f"Failed to set output: {e}")
                self.error_occurred.emit(f"Output control failed: {e}")
                return False

    def set_temperature(self, temperature_c: float) -> bool:
        """
        Set TEC temperature setpoint.

        Args:
            temperature_c: Temperature in Celsius

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to TEC controller")
            return False

        if not (self.min_temperature_c <= temperature_c <= self.max_temperature_c):
            logger.error(
                f"Temperature {temperature_c:.1f}°C outside limits "
                f"({self.min_temperature_c:.1f}-{self.max_temperature_c:.1f}°C)"
            )
            self.limit_warning.emit(
                f"Temperature outside limits: "
                f"{self.min_temperature_c:.1f}-{self.max_temperature_c:.1f}°C"
            )
            return False

        with self._lock:
            try:
                self._write_command(f"TEC:T {temperature_c:.2f}")

                # Verify
                response = self._write_command("TEC:SET:T?")
                if response:
                    set_temp = float(response)
                    if abs(set_temp - temperature_c) < 0.1:
                        self.temperature_setpoint_c = temperature_c
                        self.temperature_setpoint_changed.emit(temperature_c)
                        logger.info(f"Set TEC temperature to {temperature_c:.1f}°C")

                        # Log event
                        if self.event_logger:
                            from ..core.event_logger import EventType

                            self.event_logger.log_event(
                                event_type=EventType.TEC_TEMP_CHANGE,
                                description=f"TEC temperature set to {temperature_c:.1f}°C",
                                details={"temperature_c": temperature_c},
                            )

                        return True

                logger.error("Failed to set temperature")
                return False

            except Exception as e:
                logger.error(f"Failed to set temperature: {e}")
                self.error_occurred.emit(f"Temperature control failed: {e}")
                return False

    def read_temperature(self) -> Optional[float]:
        """
        Read actual TEC temperature.

        Returns:
            Temperature in °C or None if error
        """
        try:
            response = self._write_command("TEC:T?")
            if response:
                return float(response)
            return None
        except Exception as e:
            logger.error(f"Failed to read temperature: {e}")
            return None

    def read_current(self) -> Optional[float]:
        """
        Read actual TEC current.

        Returns:
            Current in A or None if error
        """
        try:
            response = self._write_command("TEC:ITE?")
            if response:
                return float(response)
            return None
        except Exception as e:
            logger.error(f"Failed to read current: {e}")
            return None

    def read_voltage(self) -> Optional[float]:
        """
        Read actual TEC voltage.

        Returns:
            Voltage in V or None if error
        """
        try:
            response = self._write_command("TEC:V?")
            if response:
                return float(response)
            return None
        except Exception as e:
            logger.error(f"Failed to read voltage: {e}")
            return None

    def _update_status(self) -> None:
        """Update status from device (called by timer)."""
        if not self.is_connected:
            return

        with self._lock:
            try:
                # Read temperature
                temperature = self.read_temperature()
                if temperature is not None:
                    self.temperature_changed.emit(temperature)

                # Read current
                current = self.read_current()
                if current is not None:
                    self.current_changed.emit(current)

                # Read voltage
                voltage = self.read_voltage()
                if voltage is not None:
                    self.voltage_changed.emit(voltage)

                # Read output state
                response = self._write_command("TEC:OUT?")
                if response:
                    output_enabled = bool(int(response))
                    if output_enabled != self.is_output_enabled:
                        self.is_output_enabled = output_enabled
                        self.output_changed.emit(output_enabled)

            except Exception as e:
                logger.error(f"Status update error: {e}")
