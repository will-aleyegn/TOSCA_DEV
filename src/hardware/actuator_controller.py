# -*- coding: utf-8 -*-
"""
Actuator hardware abstraction layer for Xeryon linear stage.

Provides PyQt6-integrated actuator control with:
- Position control (absolute and relative)
- Speed control
- Homing (index finding)
- Position limits
- Status monitoring
"""

import logging
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

try:
    # Import Xeryon library
    import sys

    xeryon_path = Path(__file__).parent.parent.parent / "components" / "actuator_module"
    if str(xeryon_path) not in sys.path:
        sys.path.insert(0, str(xeryon_path))

    from Xeryon import Axis, Stage, Units, Xeryon

    XERYON_AVAILABLE = True
except ImportError:
    XERYON_AVAILABLE = False
    logging.warning("Xeryon library not available - actuator features disabled")

logger = logging.getLogger(__name__)


class ActuatorController(QObject):
    """
    Xeryon actuator controller with PyQt6 integration.

    Provides thread-safe actuator operations with Qt signals.
    Uses native Xeryon API features following Hardware API Usage rule.
    """

    # Signals
    position_changed = pyqtSignal(float)  # Current position in µm
    position_reached = pyqtSignal(float)  # Target position reached
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # Status description (homing, moving, ready, error)
    homing_progress = pyqtSignal(str)  # Homing status updates
    limits_changed = pyqtSignal(float, float)  # (low_limit_um, high_limit_um)
    limit_warning = pyqtSignal(str, float)  # (direction, distance_from_limit)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()

        if not XERYON_AVAILABLE:
            raise ImportError("Xeryon library is not installed - actuator features unavailable")

        self.controller: Optional[Xeryon] = None
        self.axis: Optional[Axis] = None
        self.is_connected = False
        self.is_homed = False
        self.event_logger = event_logger

        # Position monitoring timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.setInterval(100)  # Update every 100ms

        # Settings
        self.working_units = Units.mu  # Micrometers for TOSCA
        self.position_tolerance_um = 5.0  # ±5 µm tolerance

        # Hardware limits (will be read from device)
        self.low_limit_um = -45000.0  # Default TOSCA XLA-5-125-10MU: -45mm
        self.high_limit_um = 45000.0  # Default TOSCA XLA-5-125-10MU: +45mm
        self.limit_warning_distance_um = 1000.0  # Warn when within 1mm of limit

        # Acceleration settings (will be read from device)
        self.acceleration = 65500  # Default from settings_default.txt
        self.deceleration = 65500  # Default from settings_default.txt

        logger.info("Actuator controller initialized")

    def connect(self, com_port: str = "COM3", baudrate: int = 9600, auto_home: bool = True) -> bool:
        """
        Connect to Xeryon actuator.

        TOSCA hardware config: 9600 baud, XLA_1250_5N stage, Units.mu
        See XERYON_API_REFERENCE.md for API details.

        Args:
            com_port: Serial port (e.g., "COM3")
            baudrate: TOSCA uses 9600 (NOT library default 115200)
            auto_home: Auto-home after connection

        Returns:
            True if connected successfully
        """
        try:
            logger.info(f"Connecting to actuator on {com_port} at {baudrate} baud")

            self.controller = Xeryon(COM_port=com_port, baudrate=baudrate)
            self.axis = self.controller.addAxis(Stage.XLA_1250_5N, "X")
            self.controller.start()

            self.axis.setUnits(self.working_units)
            self.axis.setSetting("DISABLE_WAITING", True)

            self.is_connected = True
            self.connection_changed.emit(True)

            self.is_homed = self.axis.isEncoderValid()
            logger.info("Connected successfully")

            if auto_home and not self.is_homed:
                self.status_changed.emit("homing")
                import time

                time.sleep(0.5)

                success = self.axis.findIndex(forceWaiting=True, direction=0)

                if success:
                    self.is_homed = True
                    logger.info("Auto-homing complete")
                    self.status_changed.emit("ready")
                else:
                    logger.warning("Auto-homing failed")
                    self.status_changed.emit("not_homed")
            elif self.is_homed:
                self.status_changed.emit("ready")
            else:
                self.status_changed.emit("not_homed")

            low_limit, high_limit = self.get_limits()
            self.get_acceleration_settings()
            self.limits_changed.emit(low_limit, high_limit)

            # Log event
            if self.event_logger:
                from ..core.event_logger import EventType

                status = "homed" if self.is_homed else "not homed"
                self.event_logger.log_hardware_event(
                    event_type=EventType.HARDWARE_ACTUATOR_CONNECT,
                    description=f"Actuator connected on {com_port} ({status})",
                    device_name="Xeryon Linear Stage",
                )

            # Start position monitoring
            self.position_timer.start()

            return True

        except Exception as e:
            error_msg = f"Actuator connection failed: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

            # Log error event
            if self.event_logger:
                from ..core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.HARDWARE_ERROR,
                    description=error_msg,
                    severity=EventSeverity.WARNING,
                    details={"device": "Xeryon Linear Stage", "port": com_port},
                )

            return False

    def disconnect(self) -> None:
        """Disconnect from actuator."""
        # Stop position monitoring
        self.position_timer.stop()

        if self.controller:
            try:
                self.controller.stop()
            except Exception as e:
                logger.warning(f"Error stopping controller: {e}")
            self.controller = None

        self.axis = None
        self.is_connected = False
        self.is_homed = False
        self.connection_changed.emit(False)
        logger.info("Actuator disconnected")

        # Log event
        if self.event_logger:
            from ..core.event_logger import EventType

            self.event_logger.log_hardware_event(
                event_type=EventType.HARDWARE_ACTUATOR_DISCONNECT,
                description="Actuator disconnected",
                device_name="Xeryon Linear Stage",
            )

    def find_index(self) -> bool:
        """
        Home the actuator (find encoder index).

        Uses native Xeryon API (axis.findIndex).
        Must complete before position commands work.

        Returns:
            True if homing started successfully
        """
        if not self.is_connected or not self.axis:
            self.error_occurred.emit("Actuator not connected")
            return False

        try:
            logger.info("Starting index finding (homing)...")
            self.status_changed.emit("homing")
            self.homing_progress.emit("Searching for index position...")

            # Use native hardware homing feature
            self.axis.findIndex()

            # Monitor homing status
            QTimer.singleShot(100, self._check_homing_status)

            # Log event
            if self.event_logger:
                from ..core.event_logger import EventType

                self.event_logger.log_event(
                    event_type=EventType.HARDWARE_ACTUATOR_HOME_START,
                    description="Actuator homing started (finding index position)",
                )

            return True

        except Exception as e:
            error_msg = f"Failed to start homing: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.status_changed.emit("error")
            return False

    def _check_homing_status(self) -> None:
        """Check if homing is complete."""
        if not self.axis:
            return

        try:
            if self.axis.isSearchingIndex():
                # Still searching
                self.homing_progress.emit("Still searching for index...")
                QTimer.singleShot(200, self._check_homing_status)
            elif self.axis.isEncoderValid():
                # Homing complete
                self.is_homed = True
                self.homing_progress.emit("Index found - homing complete!")
                self.status_changed.emit("ready")
                logger.info("Homing complete - encoder valid")

                # Emit current position
                pos = self.axis.getEPOS()
                self.position_changed.emit(pos)

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_event(
                        event_type=EventType.HARDWARE_ACTUATOR_HOME_COMPLETE,
                        description=f"Actuator homing completed (position: {pos:.1f} µm)",
                        details={"position_um": pos},
                    )
            else:
                # Homing failed
                error_msg = "Homing failed - encoder not valid"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                self.status_changed.emit("error")

        except Exception as e:
            error_msg = f"Error checking homing status: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.status_changed.emit("error")

    def set_position(self, position_um: float) -> bool:
        """
        Move to absolute position.

        Uses native Xeryon API (axis.setDPOS).

        Args:
            position_um: Target position in micrometers

        Returns:
            True if command sent successfully
        """
        if not self.is_connected or not self.axis:
            self.error_occurred.emit("Actuator not connected")
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed - call find_index() first")
            return False

        # Validate position is within limits
        is_valid, error_msg = self.validate_position(position_um)
        if not is_valid:
            logger.warning(f"Position rejected: {error_msg}")
            self.error_occurred.emit(error_msg)
            return False

        try:
            # Use native hardware absolute positioning
            self.axis.setDPOS(position_um, self.working_units)

            self.status_changed.emit("moving")
            logger.debug(f"Moving to position: {position_um} µm")

            # Monitor position reached
            QTimer.singleShot(100, self._check_position_reached)

            return True

        except Exception as e:
            error_msg = f"Failed to set position: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def _check_position_reached(self) -> None:
        """Check if target position has been reached."""
        if not self.axis:
            return

        try:
            if self.axis.isPositionReached():
                # Position reached
                current_pos = self.axis.getEPOS()
                self.position_reached.emit(current_pos)
                self.status_changed.emit("ready")
                logger.debug(f"Position reached: {current_pos:.1f} µm")

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_event(
                        event_type=EventType.HARDWARE_ACTUATOR_MOVE,
                        description=f"Actuator moved to position: {current_pos:.1f} µm",
                        details={"position_um": current_pos},
                    )
            else:
                # Still moving
                QTimer.singleShot(50, self._check_position_reached)

        except Exception as e:
            error_msg = f"Error checking position: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def make_step(self, step_um: float) -> bool:
        """
        Make relative step from current position.

        Uses native Xeryon API (axis.step).

        Args:
            step_um: Step size in micrometers (positive or negative)

        Returns:
            True if command sent successfully
        """
        if not self.is_connected or not self.axis:
            self.error_occurred.emit("Actuator not connected")
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed")
            return False

        # Calculate target position and validate
        current_pos = self.axis.getEPOS()
        target_pos = current_pos + step_um

        is_valid, error_msg = self.validate_position(target_pos)
        if not is_valid:
            logger.warning(f"Step rejected: {error_msg}")
            self.error_occurred.emit(error_msg)
            return False

        try:
            # Use native hardware relative positioning
            self.axis.step(step_um)

            self.status_changed.emit("moving")
            logger.debug(f"Making step: {step_um:+.1f} µm (target: {target_pos:.1f} µm)")

            # Monitor position reached
            QTimer.singleShot(100, self._check_position_reached)

            return True

        except Exception as e:
            error_msg = f"Failed to make step: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def get_position(self) -> Optional[float]:
        """
        Get current position.

        Returns:
            Current position in micrometers, or None if error
        """
        if not self.is_connected or not self.axis:
            return None

        try:
            return float(self.axis.getEPOS())
        except Exception as e:
            logger.error(f"Failed to get position: {e}")
            return None

    def _update_position(self) -> None:
        """Periodically update position (called by timer)."""
        if not self.is_connected or not self.axis:
            return

        try:
            current_pos = self.axis.getEPOS()
            self.position_changed.emit(current_pos)

            # Check if at hardware limits (for scan auto-stop)
            if self.axis.isAtLeftEnd() or self.axis.isAtRightEnd():
                # At a limit - stop any scanning
                if self.axis.isScanning():
                    logger.warning("Limit reached during scan - stopping")
                    self.stop_scan()

            # Check for limit proximity warnings
            proximity_info = self.check_limit_proximity(current_pos)
            if proximity_info:
                direction, distance = proximity_info
                self.limit_warning.emit(direction, distance)

        except Exception as e:
            # Don't spam errors for periodic updates
            logger.debug(f"Ignoring error during periodic status update: {e}")

    def set_speed(self, speed: int) -> bool:
        """
        Set movement speed.

        Uses native Xeryon API (axis.setSpeed) with unit conversion.

        Args:
            speed: Speed in micrometers per second (µm/s)

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            # Use official API's setSpeed() method
            # This handles unit conversion: µm/s → SSPD setting
            self.axis.setSpeed(speed)
            logger.debug(f"Speed set to {speed} µm/s")
            return True
        except Exception as e:
            logger.error(f"Failed to set speed: {e}")
            return False

    def start_scan(self, direction: int) -> bool:
        """
        Start continuous scan (velocity control) using official Xeryon API.

        Official API: axis.startScan(direction, execTime=None)
            - Direction: +1 (positive/increasing) or -1 (negative/decreasing)
            - Continuous movement at constant speed
            - Speed maintained by closed-loop control
            - Continues until stopScan() is called
            - See: XERYON_API_REFERENCE.md "Scan" section

        Args:
            direction: Scan direction (+1 positive, -1 negative)

        Returns:
            True if scan started successfully
        """
        if not self.is_connected or not self.axis:
            self.error_occurred.emit("Actuator not connected")
            return False

        if not self.is_homed:
            self.error_occurred.emit("Actuator not homed")
            return False

        try:
            # Use official API for continuous scanning
            self.axis.startScan(direction)
            self.status_changed.emit("scanning")
            dir_str = "positive" if direction > 0 else "negative"
            logger.info(f"Scan started in {dir_str} direction")
            return True
        except Exception as e:
            error_msg = f"Failed to start scan: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def stop_scan(self) -> bool:
        """
        Stop continuous scan using official Xeryon API.

        Official API: axis.stopScan()
            - Stops scanning movement
            - See: XERYON_API_REFERENCE.md "Scan" section

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            self.axis.stopScan()
            self.status_changed.emit("ready")
            logger.info("Scan stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop scan: {e}")
            return False

    def set_position_limits(self, low_um: float, high_um: float) -> bool:
        """
        Set position limits.

        Uses native hardware limit features (Hardware API Usage rule).

        Args:
            low_um: Low limit in micrometers
            high_um: High limit in micrometers

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            self.axis.sendCommand(f"LLIM={int(low_um)}")
            self.axis.sendCommand(f"HLIM={int(high_um)}")
            logger.info(f"Position limits set: {low_um} - {high_um} µm")
            return True
        except Exception as e:
            logger.error(f"Failed to set limits: {e}")
            return False

    def stop_movement(self) -> bool:
        """
        Stop all movement immediately.

        Returns:
            True if successful
        """
        if not self.controller:
            return False

        try:
            self.controller.stopMovements()
            self.status_changed.emit("ready")
            logger.info("Movement stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop movement: {e}")
            return False

    def reset(self) -> bool:
        """
        Reset controller (clears errors).

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            self.axis.reset()
            logger.info("Controller reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset: {e}")
            return False

    def get_limits(self) -> tuple[float, float]:
        """
        Get hardware position limits from device.

        Queries LLIM and HLIM settings from the actuator.

        Returns:
            Tuple of (low_limit_um, high_limit_um)
        """
        if not self.axis:
            return (self.low_limit_um, self.high_limit_um)

        try:
            # Query LLIM and HLIM from device
            # The axis.getSetting() method reads settings from device
            low_limit = float(self.axis.getSetting("LLIM"))
            high_limit = float(self.axis.getSetting("HLIM"))

            # Update cached values
            self.low_limit_um = low_limit
            self.high_limit_um = high_limit

            logger.debug(f"Hardware limits: {low_limit:.0f} to {high_limit:.0f} µm")
            return (low_limit, high_limit)

        except Exception as e:
            logger.warning(f"Failed to read limits from device: {e}")
            return (self.low_limit_um, self.high_limit_um)

    def get_acceleration_settings(self) -> tuple[int, int]:
        """
        Get acceleration and deceleration settings from device.

        Queries ACCE and DECE settings from the actuator.

        Returns:
            Tuple of (acceleration, deceleration)
        """
        if not self.axis:
            return (self.acceleration, self.deceleration)

        try:
            # Query ACCE and DECE from device
            acce = int(self.axis.getSetting("ACCE"))
            dece = int(self.axis.getSetting("DECE"))

            # Update cached values
            self.acceleration = acce
            self.deceleration = dece

            logger.debug(f"Acceleration settings: ACCE={acce}, DECE={dece}")
            return (acce, dece)

        except Exception as e:
            logger.warning(f"Failed to read acceleration settings: {e}")
            return (self.acceleration, self.deceleration)

    def set_acceleration(self, acceleration: int) -> bool:
        """
        Set acceleration value.

        Args:
            acceleration: Acceleration value (typical range: 10000-65535)

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            self.axis.sendCommand(f"ACCE={acceleration}")
            self.acceleration = acceleration
            logger.info(f"Acceleration set to {acceleration}")
            return True
        except Exception as e:
            logger.error(f"Failed to set acceleration: {e}")
            return False

    def set_deceleration(self, deceleration: int) -> bool:
        """
        Set deceleration value.

        Args:
            deceleration: Deceleration value (typical range: 10000-65535)

        Returns:
            True if successful
        """
        if not self.axis:
            return False

        try:
            self.axis.sendCommand(f"DECE={deceleration}")
            self.deceleration = deceleration
            logger.info(f"Deceleration set to {deceleration}")
            return True
        except Exception as e:
            logger.error(f"Failed to set deceleration: {e}")
            return False

    def validate_position(self, target_position_um: float) -> tuple[bool, str]:
        """
        Validate if a target position is within hardware limits.

        Args:
            target_position_um: Target position to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if position is within limits
            - error_message: Empty string if valid, error description if invalid
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
        Check if position is near a limit and return warning info.

        Args:
            position_um: Position to check

        Returns:
            Tuple of (direction, distance) if within warning distance, None otherwise
            - direction: "low" or "high"
            - distance: Distance from limit in µm
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

    def get_status_info(self) -> dict:
        """
        Get comprehensive status information.

        Returns:
            Dictionary with status information
        """
        if not self.axis:
            return {
                "connected": False,
                "homed": False,
                "position_um": 0.0,
                "status": "disconnected",
            }

        try:
            current_pos = self.axis.getEPOS()

            # Check if at limits
            at_low_limit = self.axis.isAtLeftEnd()
            at_high_limit = self.axis.isAtRightEnd()

            return {
                "connected": self.is_connected,
                "homed": self.is_homed,
                "position_um": current_pos,
                "position_reached": self.axis.isPositionReached(),
                "encoder_valid": self.axis.isEncoderValid(),
                "searching_index": self.axis.isSearchingIndex(),
                "safety_timeout": self.axis.isSafetyTimeoutTriggered(),
                "at_low_limit": at_low_limit,
                "at_high_limit": at_high_limit,
                "low_limit_um": self.low_limit_um,
                "high_limit_um": self.high_limit_um,
                "distance_from_low_limit": current_pos - self.low_limit_um,
                "distance_from_high_limit": self.high_limit_um - current_pos,
                "status": "ready" if self.is_homed else "not_homed",
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"connected": self.is_connected, "error": str(e)}
