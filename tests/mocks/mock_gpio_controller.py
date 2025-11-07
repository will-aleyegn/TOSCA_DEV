"""
Mock implementation of GPIOController for testing.

Simulates Arduino Nano GPIO behavior including safety interlocks and monitoring.
"""

from __future__ import annotations

import time
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


class MockGPIOController(MockQObjectBase):
    """
    Mock implementation of GPIOController.

    Simulates Arduino Nano GPIO for testing without physical hardware.
    Supports motor control, vibration detection, photodiode monitoring, and aiming laser.
    """

    # Signals matching GPIOController interface
    smoothing_motor_changed = pyqtSignal(bool)  # Motor state (on/off)
    smoothing_vibration_changed = pyqtSignal(bool)  # Vibration detected
    photodiode_voltage_changed = pyqtSignal(float)  # Voltage in V
    photodiode_power_changed = pyqtSignal(float)  # Calculated power in mW
    aiming_laser_changed = pyqtSignal(bool)  # Aiming laser state (on/off)
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)  # Error message
    safety_interlock_changed = pyqtSignal(bool)  # Safety OK status

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock GPIO controller."""
        # Create monitoring timer BEFORE calling super().__init__() because super calls reset()
        self._monitor_timer = QTimer()

        # Now call parent init (which calls reset())
        super().__init__(parent)

        # Connect timer signal after parent init
        self._monitor_timer.timeout.connect(self._update_status)

    def reset(self) -> None:
        """Reset mock to clean state."""
        super().reset()

        # State attributes matching GPIOController
        self.is_connected: bool = False
        self.motor_enabled: bool = False
        self.aiming_laser_enabled: bool = False
        self.vibration_detected: bool = False
        self.photodiode_voltage: float = 0.0
        self.photodiode_power_mw: float = 0.0

        # Calibration constants
        self.photodiode_voltage_to_power: float = 400.0  # mW per volt (2000mW / 5V)
        self.vibration_debounce_count: int = 0
        self.vibration_debounce_threshold: int = 3

        # Watchdog tracking
        self.heartbeat_count: int = 0
        self.last_heartbeat_time: Optional[float] = None

        # Timer
        self._monitor_timer.stop()
        self._monitor_timer.setInterval(100)  # 100ms monitoring

        # Simulated sensor behavior
        self.simulate_vibration_when_motor_on: bool = True  # Realistic default

    def connect(self, port: str = "COM4") -> bool:
        """Simulate connecting to Arduino Nano."""
        self._log_call("connect", port=port)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            return False

        self.is_connected = True
        self.connection_changed.emit(True)

        # Start monitoring timer
        self._monitor_timer.start()

        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from Arduino."""
        self._log_call("disconnect")

        # Stop monitoring
        self._monitor_timer.stop()

        # Disable all outputs
        self.stop_smoothing_motor()
        self.stop_aiming_laser()

        self.is_connected = False
        self.connection_changed.emit(False)

    def send_watchdog_heartbeat(self) -> bool:
        """
        Send heartbeat pulse to hardware watchdog timer.

        Returns:
            True if heartbeat sent successfully, False on error
        """
        self._log_call("send_watchdog_heartbeat")
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            return False

        self.heartbeat_count += 1
        self.last_heartbeat_time = time.time()
        return True

    def start_smoothing_motor(self) -> bool:
        """Start smoothing device motor."""
        self._log_call("start_smoothing_motor")
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.motor_enabled = True
        self.smoothing_motor_changed.emit(True)

        # Simulate realistic vibration detection when motor starts
        if self.simulate_vibration_when_motor_on:
            self.vibration_detected = True
            self.smoothing_vibration_changed.emit(True)

        self._update_safety_status()
        return True

    def stop_smoothing_motor(self) -> bool:
        """Stop smoothing device motor."""
        self._log_call("stop_smoothing_motor")
        self._apply_delay()

        if not self.is_connected:
            return False

        self.motor_enabled = False
        self.smoothing_motor_changed.emit(False)

        # Vibration stops when motor stops
        if self.vibration_detected:
            self.vibration_detected = False
            self.smoothing_vibration_changed.emit(False)

        self._update_safety_status()
        return True

    def start_aiming_laser(self) -> bool:
        """Start aiming laser (GPIO voltage output)."""
        self._log_call("start_aiming_laser")
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.aiming_laser_enabled = True
        self.aiming_laser_changed.emit(True)
        return True

    def stop_aiming_laser(self) -> bool:
        """Stop aiming laser (GPIO voltage output)."""
        self._log_call("stop_aiming_laser")
        self._apply_delay()

        if not self.is_connected:
            return False

        self.aiming_laser_enabled = False
        self.aiming_laser_changed.emit(False)
        return True

    def _update_status(self) -> None:
        """Update all sensor readings (called by timer)."""
        if not self.is_connected:
            return

        # Photodiode voltage simulation
        # If aiming laser is on, simulate some voltage
        if self.aiming_laser_enabled:
            self.photodiode_voltage = 2.5  # Simulated 2.5V when laser on
        else:
            self.photodiode_voltage = 0.1  # Small background noise

        self.photodiode_voltage_changed.emit(self.photodiode_voltage)

        # Calculate laser power (mW)
        self.photodiode_power_mw = self.photodiode_voltage * self.photodiode_voltage_to_power
        self.photodiode_power_changed.emit(self.photodiode_power_mw)

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
            True if safety conditions met (motor on AND vibration detected)
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
