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
from typing import Optional

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

    def __init__(self) -> None:
        super().__init__()

        if not XERYON_AVAILABLE:
            raise ImportError("Xeryon library is not installed - actuator features unavailable")

        self.controller: Optional[Xeryon] = None
        self.axis: Optional[Axis] = None
        self.is_connected = False
        self.is_homed = False

        # Position monitoring timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.setInterval(100)  # Update every 100ms

        # Settings
        self.working_units = Units.mu  # Micrometers for TOSCA
        self.position_tolerance_um = 5.0  # ±5 µm tolerance

        logger.info("Actuator controller initialized")

    def connect(self, com_port: str = "COM3", baudrate: int = 9600, auto_home: bool = True) -> bool:
        """
        Connect to Xeryon actuator using official API.

        CRITICAL API Requirements:
            - Baudrate: TOSCA hardware uses 9600 (NOT the library default of 115200)
            - Stage Type: XLA_1250_3N (1.25 µm encoder resolution)
            - Working Units: Units.mu (micrometers) for TOSCA precision
            - AUTO_SEND_SETTINGS: False (use device-stored settings)

        Official API Flow (see XERYON_API_REFERENCE.md):
            1. Xeryon(COM_port, baudrate) - Create controller
            2. addAxis(Stage, letter) - Add linear actuator
            3. start() - Start communication, send settings, enable axes
            4. setUnits(Units.mu) - Set working units to micrometers
            5. findIndex() - Home the actuator (if auto_home=True)

        Args:
            com_port: Serial port name (e.g., "COM3")
            baudrate: Communication baud rate
                      TOSCA: 9600 (manufacturer pre-configured)
                      Library default: 115200
            auto_home: If True, automatically perform homing after connection

        Returns:
            True if connected successfully
        """
        try:
            logger.info("=== DEBUG: Starting connection ===")
            logger.info(f"DEBUG: COM port: {com_port}")
            logger.info(f"DEBUG: Baudrate: {baudrate}")

            import os

            logger.info(f"DEBUG: Current working directory: {os.getcwd()}")
            logger.info(f"DEBUG: config.txt exists: {os.path.exists('config.txt')}")
            logger.info(
                f"DEBUG: settings_default.txt exists: {os.path.exists('settings_default.txt')}"
            )
            logger.info(f"DEBUG: settings_user.txt exists: {os.path.exists('settings_user.txt')}")

            # Create controller
            logger.info("DEBUG: Creating Xeryon controller...")
            self.controller = Xeryon(COM_port=com_port, baudrate=baudrate)
            logger.info("DEBUG: Controller created successfully")
            logger.info(f"DEBUG: Controller type: {type(self.controller)}")
            logger.info(f"DEBUG: Controller attributes: {dir(self.controller)}")

            # Check available stages
            logger.info("DEBUG: Available Stage types:")
            for attr in dir(Stage):
                if not attr.startswith("_"):
                    logger.info(f"  - {attr}")

            # Create and register axis (from config.txt: X:XLA3=1250)
            # Hardware: XLA-5-125-10MU (5N motor, 1250nm encoder resolution)
            # addAxis creates Axis internally and adds to controller.axis_list
            logger.info("DEBUG: Calling addAxis(Stage.XLA_1250_5N, 'X')...")
            self.axis = self.controller.addAxis(Stage.XLA_1250_5N, "X")
            logger.info("DEBUG: Axis created and registered")
            logger.info(f"DEBUG: Number of axes: {len(self.controller.axis_list)}")
            logger.info(f"DEBUG: Axis letter: {self.axis.axis_letter}")
            logger.info(f"DEBUG: Axis stage: {self.axis.stage}")

            # Start controller
            logger.info("DEBUG: Calling controller.start()...")
            self.controller.start()
            logger.info("DEBUG: Controller started successfully!")

            # Set working units to micrometers
            self.axis.setUnits(self.working_units)

            # Settings are automatically sent from settings_user.txt (AUTO_SEND_SETTINGS=True)
            # Do NOT send redundant commands - let hardware use its configured values
            logger.info("Using settings from settings_user.txt (speed, limits, etc.)")

            self.is_connected = True
            self.connection_changed.emit(True)

            # Check if already homed
            self.is_homed = self.axis.isEncoderValid()

            logger.info(f"Connected to actuator on {com_port}")

            # Auto-home if requested and not already homed
            if auto_home and not self.is_homed:
                logger.info("Auto-homing actuator (blocking until complete)...")
                self.status_changed.emit("homing")

                # Check hardware status before homing
                import time

                time.sleep(0.5)  # Let hardware stabilize after start()

                logger.info("DEBUG: Pre-homing status check:")
                logger.info(f"  encoder_valid: {self.axis.isEncoderValid()}")
                logger.info(f"  searching_index: {self.axis.isSearchingIndex()}")
                logger.info(f"  position_reached: {self.axis.isPositionReached()}")
                logger.info(f"  safety_timeout: {self.axis.isSafetyTimeoutTriggered()}")

                # Use forceWaiting=True to make this blocking during initialization
                # This ensures actuator is ready before connect() returns
                logger.info("Starting index search (direction=0, bidirectional)...")
                success = self.axis.findIndex(forceWaiting=True, direction=0)

                if success:
                    self.is_homed = True
                    logger.info("Auto-homing complete - actuator ready")
                    self.status_changed.emit("ready")
                else:
                    logger.warning("Auto-homing failed - encoder not valid")
                    logger.warning("Try manual homing with find_index()")
                    self.status_changed.emit("not_homed")
            elif self.is_homed:
                logger.info("Actuator already homed (encoder valid)")
                self.status_changed.emit("ready")
            else:
                logger.warning("Actuator not homed - call find_index() before positioning")
                self.status_changed.emit("not_homed")

            # Start position monitoring
            self.position_timer.start()

            return True

        except Exception as e:
            error_msg = f"Actuator connection failed: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
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

    def find_index(self) -> bool:
        """
        Find encoder index (home the actuator) using official Xeryon API.

        Official API: axis.findIndex(direction)
            - Sends INDX=<direction> command to hardware
            - Direction 0: Bidirectional search (fastest)
            - Blocking: Waits for isEncoderValid() == True
            - See: XERYON_API_REFERENCE.md "Homing" section

        Hardware API Usage Rule:
            Use native Xeryon homing procedure (not manual index search)

        CRITICAL: Actuator must be homed before any position commands.
            - isEncoderValid() returns False until homing complete
            - setDPOS() and step() will fail if not homed

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
        Move to absolute position using official Xeryon API.

        Official API: axis.setDPOS(position, units)
            - Input: Position in current units (µm for Units.mu)
            - Conversion: API converts µm → encoder units internally
            - Blocking: Waits for position reached (unless DISABLE_WAITING=True)
            - See: XERYON_API_REFERENCE.md "Absolute Positioning" section

        Hardware API Usage Rule:
            Use native Xeryon position control (not manual encoder calculations)

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
            else:
                # Still moving
                QTimer.singleShot(50, self._check_position_reached)

        except Exception as e:
            error_msg = f"Error checking position: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def make_step(self, step_um: float) -> bool:
        """
        Make relative step from current position using official Xeryon API.

        Official API: axis.step(distance)
            - Input: Relative distance in current units (µm for Units.mu)
            - Positive: Move in positive direction
            - Negative: Move in negative direction
            - Implementation: Gets current position, calculates target, calls setDPOS()
            - See: XERYON_API_REFERENCE.md "Relative Movement" section

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

        try:
            # Use native hardware relative positioning
            self.axis.step(step_um)

            self.status_changed.emit("moving")
            logger.debug(f"Making step: {step_um:+.1f} µm")

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
            current_pos = self.axis.getEPOS(self.working_units)
            self.position_changed.emit(current_pos)
        except Exception:
            # Don't spam errors for periodic updates
            pass

    def set_speed(self, speed: int) -> bool:
        """
        Set movement speed using official Xeryon API.

        CRITICAL: Uses axis.setSpeed() which handles unit conversion.
        The official API converts input speed (in current units/second) to µm/s.

        Args:
            speed: Speed in micrometers per second (µm/s)
                   Since working_units = Units.mu, input is interpreted as µm/s
                   Typical range: 50 (very slow) to 500 (fast) µm/s

        Returns:
            True if successful

        Official API Reference:
            - Input: Speed in current units/second (µm/s for Units.mu)
            - Conversion: axis.setSpeed() converts to SSPD setting internally
            - See: XERYON_API_REFERENCE.md "Speed Control" section
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
            return {
                "connected": self.is_connected,
                "homed": self.is_homed,
                "position_um": self.axis.getEPOS(),
                "position_reached": self.axis.isPositionReached(),
                "encoder_valid": self.axis.isEncoderValid(),
                "searching_index": self.axis.isSearchingIndex(),
                "safety_timeout": self.axis.isSafetyTimeoutTriggered(),
                "status": "ready" if self.is_homed else "not_homed",
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"connected": self.is_connected, "error": str(e)}
