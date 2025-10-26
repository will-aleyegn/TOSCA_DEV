"""
Mock implementation of ActuatorController for testing.

Simulates Xeryon linear stage behavior including position control and homing.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


class MockActuatorController(MockQObjectBase):
    """
    Mock implementation of ActuatorController.

    Simulates Xeryon linear stage for testing without physical hardware.
    Supports position control, homing, scanning, and limit management.
    """

    # Signals matching ActuatorController interface
    position_changed = pyqtSignal(float)  # Current position in µm
    position_reached = pyqtSignal(float)  # Target position reached
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)  # Error message
    status_changed = pyqtSignal(str)  # Status: homing, moving, ready, error
    homing_progress = pyqtSignal(str)  # Homing status updates
    limits_changed = pyqtSignal(float, float)  # (low_limit_um, high_limit_um)
    limit_warning = pyqtSignal(str, float)  # (direction, distance_from_limit)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock actuator controller."""
        # Create timers BEFORE calling super().__init__() because super calls reset()
        self._homing_timer = QTimer()
        self._homing_timer.setSingleShot(True)

        self._movement_timer = QTimer()
        self._movement_timer.setSingleShot(True)

        self._scan_timer = QTimer()

        # Now call parent init (which calls reset())
        super().__init__(parent)

        # Connect timer signals after parent init
        self._homing_timer.timeout.connect(self._complete_homing)
        self._movement_timer.timeout.connect(self._complete_movement)
        self._scan_timer.timeout.connect(self._update_scan_position)

    def reset(self) -> None:
        """Reset mock to clean state."""
        super().reset()

        # State attributes matching ActuatorController
        self.is_connected: bool = False
        self.is_homed: bool = False
        self.is_scanning: bool = False

        # Position tracking (µm)
        self.current_position_um: float = 0.0
        self.target_position_um: float = 0.0

        # Hardware limits (TOSCA XLA-5-125-10MU: -45mm to +45mm)
        self.low_limit_um: float = -45000.0
        self.high_limit_um: float = 45000.0
        self.limit_warning_distance_um: float = 1000.0

        # Movement settings
        self.speed_um_per_s: int = 10000  # 10 mm/s default
        self.acceleration: int = 65500
        self.deceleration: int = 65500
        self.position_tolerance_um: float = 5.0

        # Scanning state
        self.scan_direction: int = 0

        # Timers
        self._homing_timer.stop()
        self._movement_timer.stop()
        self._scan_timer.stop()

        # Homing simulation delay (ms)
        self.homing_delay_ms: int = 200

    def connect(self, com_port: str = "COM3", baudrate: int = 9600, auto_home: bool = True) -> bool:
        """Simulate connecting to Xeryon actuator."""
        self._log_call("connect", com_port=com_port, baudrate=baudrate, auto_home=auto_home)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            return False

        self.is_connected = True
        self.connection_changed.emit(True)
        self.status_changed.emit("connected")

        # Auto-home if requested
        if auto_home and not self.is_homed:
            self.find_index()

        self.limits_changed.emit(self.low_limit_um, self.high_limit_um)
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from actuator."""
        self._log_call("disconnect")

        # Stop any ongoing operations
        self.stop_movement()
        self._homing_timer.stop()
        self._movement_timer.stop()
        self._scan_timer.stop()

        self.is_connected = False
        self.is_homed = False
        self.connection_changed.emit(False)
        self.status_changed.emit("disconnected")

    def find_index(self) -> bool:
        """Simulate homing (index finding)."""
        self._log_call("find_index")
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.status_changed.emit("homing")
        self.homing_progress.emit("Searching for index position...")

        # Simulate homing delay
        self._homing_timer.start(self.homing_delay_ms)
        return True

    def _complete_homing(self) -> None:
        """Complete simulated homing sequence."""
        self.is_homed = True
        self.current_position_um = 0.0  # Reset to home position
        self.homing_progress.emit("Index found - homing complete!")
        self.status_changed.emit("ready")
        self.position_changed.emit(self.current_position_um)

    def set_position(self, position_um: float) -> bool:
        """Simulate absolute position movement."""
        self._log_call("set_position", position_um=position_um)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed - call find_index() first")
            return False

        # Validate position
        is_valid, error_msg = self.validate_position(position_um)
        if not is_valid:
            self.error_occurred.emit(error_msg)
            return False

        self.target_position_um = position_um
        self.status_changed.emit("moving")

        # Simulate movement delay (distance / speed)
        distance = abs(position_um - self.current_position_um)
        move_time_ms = int((distance / self.speed_um_per_s) * 1000)
        self._movement_timer.start(max(50, move_time_ms))

        return True

    def _complete_movement(self) -> None:
        """Complete simulated movement."""
        self.current_position_um = self.target_position_um
        self.position_changed.emit(self.current_position_um)
        self.position_reached.emit(self.current_position_um)
        self.status_changed.emit("ready")

        # Check limit proximity
        proximity_info = self.check_limit_proximity(self.current_position_um)
        if proximity_info:
            direction, distance = proximity_info
            self.limit_warning.emit(direction, distance)

    def make_step(self, step_um: float) -> bool:
        """Simulate relative step movement."""
        self._log_call("make_step", step_um=step_um)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed")
            return False

        # Calculate target and validate
        target_pos = self.current_position_um + step_um
        is_valid, error_msg = self.validate_position(target_pos)
        if not is_valid:
            self.error_occurred.emit(error_msg)
            return False

        # Use set_position for the actual movement
        return self.set_position(target_pos)

    def get_position(self) -> Optional[float]:
        """Get current position."""
        self._log_call("get_position")
        self._apply_delay()

        if not self.is_connected:
            return None

        return self.current_position_um

    def set_speed(self, speed: int) -> bool:
        """Set movement speed."""
        self._log_call("set_speed", speed=speed)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            return False

        self.speed_um_per_s = speed
        return True

    def start_scan(self, direction: int) -> bool:
        """Start continuous scanning."""
        self._log_call("start_scan", direction=direction)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed")
            return False

        self.is_scanning = True
        self.scan_direction = direction
        self.status_changed.emit("scanning")

        # Start scan timer (update position every 100ms)
        self._scan_timer.start(100)
        return True

    def _update_scan_position(self) -> None:
        """Update position during scanning."""
        if not self.is_scanning:
            return

        # Calculate position increment (speed * time)
        increment_um = self.scan_direction * (self.speed_um_per_s * 0.1)  # 100ms = 0.1s
        new_position = self.current_position_um + increment_um

        # Check limits
        if new_position <= self.low_limit_um or new_position >= self.high_limit_um:
            # Hit limit - stop scan
            self.stop_scan()
            return

        self.current_position_um = new_position
        self.position_changed.emit(self.current_position_um)

    def stop_scan(self) -> bool:
        """Stop continuous scanning."""
        self._log_call("stop_scan")

        if not self.is_connected:
            return False

        self.is_scanning = False
        self._scan_timer.stop()
        self.status_changed.emit("ready")
        return True

    def stop_movement(self) -> bool:
        """Stop all movement."""
        self._log_call("stop_movement")

        if not self.is_connected:
            return False

        self._movement_timer.stop()
        self.stop_scan()
        self.status_changed.emit("ready")
        return True

    def set_position_limits(self, low_um: float, high_um: float) -> bool:
        """Set position limits."""
        self._log_call("set_position_limits", low_um=low_um, high_um=high_um)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            return False

        self.low_limit_um = low_um
        self.high_limit_um = high_um
        self.limits_changed.emit(low_um, high_um)
        return True

    def get_limits(self) -> tuple[float, float]:
        """Get position limits."""
        self._log_call("get_limits")
        return (self.low_limit_um, self.high_limit_um)

    def set_acceleration(self, acceleration: int) -> bool:
        """Set acceleration value."""
        self._log_call("set_acceleration", acceleration=acceleration)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            return False

        self.acceleration = acceleration
        return True

    def set_deceleration(self, deceleration: int) -> bool:
        """Set deceleration value."""
        self._log_call("set_deceleration", deceleration=deceleration)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            return False

        self.deceleration = deceleration
        return True

    def get_acceleration_settings(self) -> tuple[int, int]:
        """Get acceleration and deceleration settings."""
        self._log_call("get_acceleration_settings")
        return (self.acceleration, self.deceleration)

    def validate_position(self, target_position_um: float) -> tuple[bool, str]:
        """
        Validate if position is within limits.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if target_position_um < self.low_limit_um:
            error = f"Position {target_position_um:.0f} µm below limit ({self.low_limit_um:.0f} µm)"
            return (False, error)

        if target_position_um > self.high_limit_um:
            error = (
                f"Position {target_position_um:.0f} µm above limit ({self.high_limit_um:.0f} µm)"
            )
            return (False, error)

        return (True, "")

    def check_limit_proximity(self, position_um: float) -> Optional[tuple[str, float]]:
        """
        Check if position is near a limit.

        Returns:
            Tuple of (direction, distance) if within warning distance, None otherwise
        """
        # Check low limit
        distance_from_low = position_um - self.low_limit_um
        if 0 < distance_from_low < self.limit_warning_distance_um:
            return ("low", distance_from_low)

        # Check high limit
        distance_from_high = self.high_limit_um - position_um
        if 0 < distance_from_high < self.limit_warning_distance_um:
            return ("high", distance_from_high)

        return None

    def get_status_info(self) -> dict[str, Any]:
        """Get comprehensive status information."""
        self._log_call("get_status_info")

        if not self.is_connected:
            return {
                "connected": False,
                "homed": False,
                "position_um": 0.0,
                "status": "disconnected",
            }

        return {
            "connected": self.is_connected,
            "homed": self.is_homed,
            "position_um": self.current_position_um,
            "position_reached": not self._movement_timer.isActive(),
            "encoder_valid": self.is_homed,
            "searching_index": self._homing_timer.isActive(),
            "at_low_limit": self.current_position_um <= self.low_limit_um,
            "at_high_limit": self.current_position_um >= self.high_limit_um,
            "low_limit_um": self.low_limit_um,
            "high_limit_um": self.high_limit_um,
            "distance_from_low_limit": self.current_position_um - self.low_limit_um,
            "distance_from_high_limit": self.high_limit_um - self.current_position_um,
            "status": "ready" if self.is_homed else "not_homed",
            "is_scanning": self.is_scanning,
        }
