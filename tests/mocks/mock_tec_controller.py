"""
Mock implementation of TECController for testing.

Simulates Arroyo TEC (Thermoelectric Cooler) behavior including temperature control
and monitoring with realistic thermal lag simulation.
"""

from __future__ import annotations

import math
import time
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


class MockTECController(MockQObjectBase):
    """
    Mock implementation of TECController.

    Simulates TEC behavior for testing without physical hardware.
    Supports temperature setpoint control, output enable, and realistic
    thermal lag simulation for temperature changes.
    """

    # Signals matching TECController interface
    temperature_changed = pyqtSignal(float)  # Actual temperature in °C
    temperature_setpoint_changed = pyqtSignal(float)  # Setpoint temperature in °C
    output_changed = pyqtSignal(bool)  # True=enabled, False=disabled
    current_changed = pyqtSignal(float)  # TEC current in A
    voltage_changed = pyqtSignal(float)  # TEC voltage in V
    status_changed = pyqtSignal(str)  # Status description
    limit_warning = pyqtSignal(str)  # Limit warning message
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock TEC controller."""
        super().__init__(parent)
        self.reset()

    def reset(self) -> None:
        """Reset mock to clean state."""
        super().reset()

        # State attributes matching TECController
        self.is_connected: bool = False
        self.is_output_enabled: bool = False

        # Temperature settings
        self.temperature_setpoint_c: float = 25.0
        self._temperature_reading_c: float = 25.0  # Ambient temperature

        # Safety limits
        self.max_temperature_c: float = 35.0
        self.min_temperature_c: float = 15.0
        self.max_current_a: float = 3.0
        self.max_voltage_v: float = 5.0

        # Current readings (simulated)
        self._current_reading_a: float = 0.0
        self._voltage_reading_v: float = 0.0

        # Thermal simulation parameters
        self._thermal_time_constant: float = 5.0  # seconds (time to reach 63% of target)
        self._last_update_time: float = time.time()
        self._ambient_temperature_c: float = 25.0

    def connect(self, com_port: str = "COM9", baudrate: int = 38400) -> bool:
        """
        Simulate connecting to TEC controller.

        Args:
            com_port: Serial port (default "COM9")
            baudrate: Communication speed (default 38400)

        Returns:
            True if connected successfully
        """
        self._log_call("connect", com_port=com_port, baudrate=baudrate)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            self.connection_changed.emit(False)
            return False

        self.is_connected = True
        self.connection_changed.emit(True)
        self.status_changed.emit("connected")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from TEC controller."""
        self._log_call("disconnect")

        # Disable output before disconnecting
        if self.is_output_enabled:
            self.set_output(False)

        self.is_connected = False
        self.connection_changed.emit(False)
        self.status_changed.emit("disconnected")

    def set_output(self, enabled: bool) -> bool:
        """
        Simulate enabling/disabling TEC output.

        Args:
            enabled: True to enable cooling, False to disable

        Returns:
            True if successful
        """
        self._log_call("set_output", enabled=enabled)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.is_output_enabled = enabled
        self.output_changed.emit(enabled)

        # Update readings based on output state
        if enabled:
            # Calculate TEC power requirements
            temp_delta = abs(self._temperature_reading_c - self.temperature_setpoint_c)
            self._current_reading_a = min(temp_delta * 0.3, self.max_current_a)  # Simulated PID
            self._voltage_reading_v = self._current_reading_a * 1.5  # V = I * R (simulated)
        else:
            # Output disabled - drift to ambient
            self._current_reading_a = 0.0
            self._voltage_reading_v = 0.0

        self.current_changed.emit(self._current_reading_a)
        self.voltage_changed.emit(self._voltage_reading_v)

        return True

    def set_temperature(self, temperature_c: float) -> bool:
        """
        Simulate setting TEC temperature setpoint.

        Args:
            temperature_c: Target temperature in °C

        Returns:
            True if successful
        """
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
        self.temperature_setpoint_changed.emit(temperature_c)

        # Update TEC current/voltage if output enabled
        if self.is_output_enabled:
            self._update_tec_power()

        return True

    def read_temperature(self) -> Optional[float]:
        """
        Simulate reading TEC temperature.

        Implements realistic thermal lag simulation using exponential decay model.

        Returns:
            Current temperature in °C, or None if disconnected
        """
        self._log_call("read_temperature")
        self._apply_delay()

        if not self.is_connected:
            return None

        # Update temperature with thermal lag simulation
        if self.is_output_enabled:
            self._simulate_thermal_response()
        else:
            # Drift toward ambient when output disabled
            self._simulate_thermal_drift()

        return self._temperature_reading_c

    def read_current(self) -> Optional[float]:
        """
        Simulate reading TEC current.

        Returns:
            Current in amperes, or None if disconnected
        """
        self._log_call("read_current")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self._current_reading_a

    def read_voltage(self) -> Optional[float]:
        """
        Simulate reading TEC voltage.

        Returns:
            Voltage in volts, or None if disconnected
        """
        self._log_call("read_voltage")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self._voltage_reading_v

    def get_status(self) -> dict[str, Any]:
        """
        Get comprehensive TEC status.

        Returns:
            Dictionary with all status information
        """
        self._log_call("get_status")

        return {
            "connected": self.is_connected,
            "output_enabled": self.is_output_enabled,
            "temperature_c": self._temperature_reading_c,
            "setpoint_c": self.temperature_setpoint_c,
            "current_a": self._current_reading_a,
            "voltage_v": self._voltage_reading_v,
            "at_setpoint": abs(self._temperature_reading_c - self.temperature_setpoint_c) < 0.1,
        }

    def _simulate_thermal_response(self) -> None:
        """
        Simulate thermal response to setpoint change using exponential decay model.

        Models realistic TEC behavior: T(t) = T_setpoint + (T_initial - T_setpoint) * exp(-t/τ)
        where τ is the thermal time constant.
        """
        current_time = time.time()
        dt = current_time - self._last_update_time
        self._last_update_time = current_time

        # Exponential approach to setpoint
        temp_error = self.temperature_setpoint_c - self._temperature_reading_c

        if abs(temp_error) > 0.01:  # Only update if significant error
            # Apply first-order exponential decay: ΔT = error * (1 - e^(-dt/τ))
            response_factor = 1.0 - math.exp(-dt / self._thermal_time_constant)

            # Limit response to prevent overshooting
            response_factor = min(response_factor, 0.95)

            self._temperature_reading_c += temp_error * response_factor
            self.temperature_changed.emit(self._temperature_reading_c)

            # Update TEC power based on error
            self._update_tec_power()

    def _simulate_thermal_drift(self) -> None:
        """Simulate thermal drift to ambient when output disabled."""
        current_time = time.time()
        dt = current_time - self._last_update_time
        self._last_update_time = current_time

        # Drift toward ambient temperature
        temp_error = self._ambient_temperature_c - self._temperature_reading_c
        drift_rate = dt / (self._thermal_time_constant * 2.0)  # Slower drift when unpowered

        if abs(temp_error) > 0.01:
            self._temperature_reading_c += temp_error * drift_rate
            self.temperature_changed.emit(self._temperature_reading_c)

    def _update_tec_power(self) -> None:
        """Update TEC current and voltage based on temperature error (simulated PID)."""
        if not self.is_output_enabled:
            return

        # Simple proportional control simulation
        temp_error = abs(self._temperature_reading_c - self.temperature_setpoint_c)

        # Current proportional to temperature error (simulated P-controller)
        self._current_reading_a = min(temp_error * 0.3, self.max_current_a)

        # Voltage = I * R (simulated resistance)
        self._voltage_reading_v = min(self._current_reading_a * 1.5, self.max_voltage_v)

        self.current_changed.emit(self._current_reading_a)
        self.voltage_changed.emit(self._voltage_reading_v)

    # Advanced simulation methods

    def set_thermal_time_constant(self, tau_seconds: float) -> None:
        """
        Set thermal time constant for temperature simulation.

        Args:
            tau_seconds: Time constant in seconds (time to reach 63% of target)
        """
        self._thermal_time_constant = tau_seconds

    def set_ambient_temperature(self, temperature_c: float) -> None:
        """
        Set ambient temperature for drift simulation.

        Args:
            temperature_c: Ambient temperature in °C
        """
        self._ambient_temperature_c = temperature_c

    def force_temperature(self, temperature_c: float) -> None:
        """
        Force temperature reading to specific value (for testing edge cases).

        Args:
            temperature_c: Temperature to force
        """
        self._temperature_reading_c = temperature_c
        self.temperature_changed.emit(temperature_c)
