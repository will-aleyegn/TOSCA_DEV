# -*- coding: utf-8 -*-
"""
Laser hardware abstraction layer for Arroyo Instruments laser driver.

Provides PyQt6-integrated laser control with:
- Current control for laser diode
- Output enable/disable
- Safety limits
- Status monitoring
- Thread-safe serial communication

Note: TEC temperature control is handled by separate TECController.
"""

import logging
import threading
from typing import Any, Optional

import serial
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)


class LaserController(QObject):
    """
    Arroyo laser driver controller with PyQt6 integration.

    Provides thread-safe laser operations with Qt signals.
    Uses Arroyo serial command protocol.
    """

    # Signals
    power_changed = pyqtSignal(float)  # Current power in mW
    current_changed = pyqtSignal(float)  # Current in mA
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected
    output_changed = pyqtSignal(bool)  # True=enabled, False=disabled
    error_occurred = pyqtSignal(str)  # Error message
    status_changed = pyqtSignal(str)  # Status description
    limit_warning = pyqtSignal(str)  # Limit warning message

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()

        self.ser: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_output_enabled = False
        self.event_logger = event_logger

        # Thread safety lock for serial communication (reentrant for nested calls)
        self._lock = threading.RLock()

        # Monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_status)
        self.monitor_timer.setInterval(500)  # Update every 500ms

        # Settings
        self.current_setpoint_ma = 0.0
        self.power_setpoint_mw = 0.0

        # Safety limits (will be read from device)
        self.max_current_ma = 2000.0
        self.max_power_mw = 2000.0

        logger.info("Laser controller initialized (thread-safe)")

    def connect(self, com_port: str = "COM10", baudrate: int = 38400) -> bool:
        """
        Connect to Arroyo laser driver.

        Args:
            com_port: Serial port (e.g., "COM4")
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
                        logger.info(f"Connected to: {response}")
                        self.is_connected = True
                        self.connection_changed.emit(True)
                        self.status_changed.emit("connected")

                        # Log event
                        if self.event_logger:
                            from ..core.event_logger import EventType

                            self.event_logger.log_hardware_event(
                                event_type=EventType.HARDWARE_LASER_CONNECT,
                                description=f"Laser connected: {response.strip()}",
                                device_name="Arroyo Laser Driver",
                            )

                        # Read initial limits
                        self._read_limits()

                        # Start monitoring
                        self.monitor_timer.start()

                        return True
                    else:
                        logger.error("No response from laser driver")
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
                        description=f"Laser connection failed: {e}",
                        severity=EventSeverity.WARNING,
                        details={"device": "Arroyo Laser Driver", "port": com_port},
                    )

                return False
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                self.error_occurred.emit(f"Connection failed: {e}")
                return False

    def disconnect(self) -> None:
        """Disconnect from laser driver."""
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
                logger.info("Disconnected from laser driver")

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_hardware_event(
                        event_type=EventType.HARDWARE_LASER_DISCONNECT,
                        description="Laser disconnected",
                        device_name="Arroyo Laser Driver",
                    )

    def get_status(self) -> dict[str, Any]:
        """
        Get current laser status and state information.

        Returns:
            Dictionary containing:
            - connected (bool): Connection status
            - output_enabled (bool): Laser output state
            - current_setpoint_ma (float): Current setpoint in mA
            - power_setpoint_mw (float): Power setpoint in mW
        """
        with self._lock:
            return {
                "connected": self.is_connected,
                "output_enabled": self.is_output_enabled,
                "current_setpoint_ma": self.current_setpoint_ma,
                "power_setpoint_mw": self.power_setpoint_mw,
            }

    def _write_command(self, command: str) -> Optional[str]:
        """
        Send command to laser driver and return response.

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
            # Read current limit
            response = self._write_command("LAS:LIM:LDI?")
            if response:
                self.max_current_ma = float(response) * 1000  # Convert A to mA

            logger.info(f"Limits: Current={self.max_current_ma:.0f}mA")

        except Exception as e:
            logger.warning(f"Failed to read limits: {e}")

    def set_output(self, enabled: bool) -> bool:
        """
        Enable or disable laser output.

        Args:
            enabled: True to enable, False to disable

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to laser driver")
            return False

        with self._lock:
            try:
                value = 1 if enabled else 0
                self._write_command(f"LAS:OUT {value}")

                # Verify
                response = self._write_command("LAS:OUT?")
                if response and int(response) == value:
                    self.is_output_enabled = enabled
                    self.output_changed.emit(enabled)
                    status = "enabled" if enabled else "disabled"
                    logger.info(f"Laser output {status}")

                    # Log event
                    if self.event_logger:
                        from ..core.event_logger import EventType

                        event_type = (
                            EventType.TREATMENT_LASER_ON
                            if enabled
                            else EventType.TREATMENT_LASER_OFF
                        )
                        self.event_logger.log_event(
                            event_type=event_type,
                            description=f"Laser output {status}",
                            details={"current_setpoint": self.current_setpoint_ma},
                        )

                    return True
                else:
                    logger.error("Failed to set output")
                    return False

            except Exception as e:
                logger.error(f"Failed to set output: {e}")
                self.error_occurred.emit(f"Output control failed: {e}")
                return False

    def set_current(self, current_ma: float) -> bool:
        """
        Set laser diode current.

        Args:
            current_ma: Current in milliamps

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to laser driver")
            return False

        if current_ma > self.max_current_ma:
            logger.error(f"Current {current_ma:.1f}mA exceeds limit {self.max_current_ma:.0f}mA")
            self.limit_warning.emit(f"Current exceeds limit: {self.max_current_ma:.0f}mA")
            return False

        with self._lock:
            try:
                # Convert mA to A for command
                current_a = current_ma / 1000.0
                self._write_command(f"LAS:LDI {current_a:.4f}")

                # Verify
                response = self._write_command("LAS:SET:LDI?")
                if response:
                    set_current = float(response) * 1000  # Convert A to mA
                    if abs(set_current - current_ma) < 0.1:
                        self.current_setpoint_ma = current_ma
                        logger.info(f"Set laser current to {current_ma:.1f} mA")

                        # Log event
                        if self.event_logger:
                            from ..core.event_logger import EventType

                            self.event_logger.log_event(
                                event_type=EventType.TREATMENT_POWER_CHANGE,
                                description=f"Laser current set to {current_ma:.1f} mA",
                                details={"current_ma": current_ma},
                            )

                        return True

                logger.error("Failed to set current")
                return False

            except Exception as e:
                logger.error(f"Failed to set current: {e}")
                self.error_occurred.emit(f"Current control failed: {e}")
                return False

    def set_power(self, power_mw: float) -> bool:
        """
        Set laser power (if power mode is supported).

        Args:
            power_mw: Power in milliwatts

        Returns:
            True if successful
        """
        if not self.is_connected:
            logger.error("Not connected to laser driver")
            return False

        if power_mw > self.max_power_mw:
            logger.error(f"Power {power_mw:.1f}mW exceeds limit {self.max_power_mw:.0f}mW")
            self.limit_warning.emit(f"Power exceeds limit: {self.max_power_mw:.0f}mW")
            return False

        try:
            # Note: Power mode may not be available on all models
            # This is a placeholder for future implementation
            self.power_setpoint_mw = power_mw
            logger.warning("Power mode not yet implemented, using current mode")
            # TODO(#128): Implement power mode when available (hardware may not support)
            return False

        except Exception as e:
            logger.error(f"Failed to set power: {e}")
            self.error_occurred.emit(f"Power control failed: {e}")
            return False

    def read_current(self) -> Optional[float]:
        """
        Read actual laser current.

        Returns:
            Current in mA or None if error
        """
        try:
            response = self._write_command("LAS:LDI?")
            if response:
                return float(response) * 1000  # Convert A to mA
            return None
        except Exception as e:
            logger.error(f"Failed to read current: {e}")
            return None

    def read_power(self) -> Optional[float]:
        """
        Read actual laser power (if available).

        Returns:
            Power in mW or None if error
        """
        # Note: Actual power measurement may require photodiode feedback
        # This is a placeholder for future implementation
        return None

    def _update_status(self) -> None:
        """Update status from device (called by timer)."""
        if not self.is_connected:
            return

        with self._lock:
            try:
                # Read current
                current = self.read_current()
                if current is not None:
                    self.current_changed.emit(current)

                # Read output state
                response = self._write_command("LAS:OUT?")
                if response:
                    output_enabled = bool(int(response))
                    if output_enabled != self.is_output_enabled:
                        self.is_output_enabled = output_enabled
                        self.output_changed.emit(output_enabled)

            except Exception as e:
                logger.error(f"Status update error: {e}")
