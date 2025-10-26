"""
Mock implementation of LaserController for testing.

Simulates Arroyo laser driver behavior including power control and TEC monitoring.
"""

from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


class MockLaserController(MockQObjectBase):
    """
    Mock implementation of LaserController.

    Simulates laser behavior for testing without physical hardware.
    Supports power/current control, output enable, and TEC temperature.
    """

    # Signals matching LaserController interface
    power_changed = pyqtSignal(float)
    current_changed = pyqtSignal(float)
    temperature_changed = pyqtSignal(float)
    connection_changed = pyqtSignal(bool)
    output_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    limit_warning = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock laser controller."""
        super().__init__(parent)
        self.reset()

    def reset(self) -> None:
        """Reset mock to clean state."""
        super().reset()

        # State attributes matching LaserController
        self.is_connected: bool = False
        self.is_output_enabled: bool = False

        # Settings
        self.current_setpoint_ma: float = 0.0
        self.power_setpoint_mw: float = 0.0
        self.temperature_setpoint_c: float = 25.0

        # Safety limits
        self.max_current_ma: float = 2000.0
        self.max_power_mw: float = 2000.0
        self.max_temperature_c: float = 35.0
        self.min_temperature_c: float = 15.0

        # Current readings (simulated)
        self._current_reading_ma: float = 0.0
        self._power_reading_mw: float = 0.0
        self._temperature_reading_c: float = 25.0

    def connect(self, com_port: str = "COM4", baudrate: int = 38400) -> bool:
        """Simulate connecting to laser driver."""
        self._log_call("connect", com_port=com_port, baudrate=baudrate)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            return False

        self.is_connected = True
        self.connection_changed.emit(True)
        self.status_changed.emit("connected")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from laser driver."""
        self._log_call("disconnect")

        # Disable output before disconnecting
        if self.is_output_enabled:
            self.set_output(False)

        self.is_connected = False
        self.connection_changed.emit(False)
        self.status_changed.emit("disconnected")

    def set_output(self, enabled: bool) -> bool:
        """Simulate enabling/disabling laser output."""
        self._log_call("set_output", enabled=enabled)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.is_output_enabled = enabled
        self.output_changed.emit(enabled)

        # Update readings based on output state
        if enabled:
            self._current_reading_ma = self.current_setpoint_ma
            self._power_reading_mw = self.power_setpoint_mw
            self.current_changed.emit(self._current_reading_ma)
            self.power_changed.emit(self._power_reading_mw)
        else:
            self._current_reading_ma = 0.0
            self._power_reading_mw = 0.0
            self.current_changed.emit(0.0)
            self.power_changed.emit(0.0)

        return True

    def set_current(self, current_ma: float) -> bool:
        """Simulate setting laser current."""
        self._log_call("set_current", current_ma=current_ma)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Check limits
        if current_ma > self.max_current_ma:
            self.limit_warning.emit(f"Current {current_ma}mA exceeds limit {self.max_current_ma}mA")
            return False

        self.current_setpoint_ma = current_ma

        # Update reading if output enabled
        if self.is_output_enabled:
            self._current_reading_ma = current_ma
            self.current_changed.emit(current_ma)

        return True

    def set_power(self, power_mw: float) -> bool:
        """Simulate setting laser power."""
        self._log_call("set_power", power_mw=power_mw)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Check limits
        if power_mw > self.max_power_mw:
            self.limit_warning.emit(f"Power {power_mw}mW exceeds limit {self.max_power_mw}mW")
            return False

        self.power_setpoint_mw = power_mw

        # Update reading if output enabled
        if self.is_output_enabled:
            self._power_reading_mw = power_mw
            self.power_changed.emit(power_mw)

        return True

    def set_temperature(self, temperature_c: float) -> bool:
        """Simulate setting TEC temperature."""
        self._log_call("set_temperature", temperature_c=temperature_c)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Check limits
        if temperature_c > self.max_temperature_c or temperature_c < self.min_temperature_c:
            self.limit_warning.emit(
                f"Temperature {temperature_c}°C outside limits "
                f"({self.min_temperature_c}-{self.max_temperature_c}°C)"
            )
            return False

        self.temperature_setpoint_c = temperature_c
        self._temperature_reading_c = temperature_c
        self.temperature_changed.emit(temperature_c)
        return True

    def read_current(self) -> Optional[float]:
        """Simulate reading laser current."""
        self._log_call("read_current")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self._current_reading_ma

    def read_temperature(self) -> Optional[float]:
        """Simulate reading TEC temperature."""
        self._log_call("read_temperature")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self._temperature_reading_c

    def read_power(self) -> Optional[float]:
        """Simulate reading laser power."""
        self._log_call("read_power")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self._power_reading_mw
