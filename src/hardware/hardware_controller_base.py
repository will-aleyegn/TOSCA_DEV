# -*- coding: utf-8 -*-
"""
Module: hardware_controller_base
Project: TOSCA Laser Control System

Purpose: Abstract base class for all hardware controllers in TOSCA.
Enforces consistent interface across Camera, Actuator, Laser, and GPIO controllers.
Combines PyQt6's QObject (for signals/slots) with ABC (for interface enforcement).
Safety Critical: Yes

Design Philosophy:
- Minimal interface - only what's truly common across all hardware
- PyQt6 signal/slot integration for thread-safe communication
- Optional event logging integration
- Type-safe with comprehensive type hints

All hardware controllers must:
1. Inherit from this base class
2. Implement connect() and disconnect() methods
3. Implement get_status() method
4. Emit connection_changed and error_occurred signals appropriately
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal


class QObjectABCMeta(type(QObject), type(ABC)):  # type: ignore[misc]
    """
    Metaclass that combines QObject's metaclass with ABC's metaclass.

    Required to create an abstract base class that also supports PyQt6 signals/slots.
    Resolves the metaclass conflict between QObject and ABC.
    """

    pass


class HardwareControllerBase(QObject, ABC, metaclass=QObjectABCMeta):
    """
    Abstract base class for all TOSCA hardware controllers.

    This class defines the minimum interface that all hardware controllers
    (Camera, Actuator, Laser, GPIO) must implement to ensure consistent
    behavior and integration with the TOSCA system.

    Signals:
        connection_changed: Emitted when connection state changes (bool: connected)
        error_occurred: Emitted when an error occurs (str: error message)

    Attributes:
        is_connected: Current connection state
        event_logger: Optional event logger for hardware events
    """

    # Required signals - all controllers must have these
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected
    error_occurred = pyqtSignal(str)  # Error message string

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        """
        Initialize hardware controller base.

        Args:
            event_logger: Optional event logger instance for hardware event tracking.
                         Should have methods like log_hardware_event(), log_event().
                         Type is intentionally generic to avoid circular dependencies.
        """
        super().__init__()
        self.is_connected: bool = False
        self.event_logger = event_logger

    @abstractmethod
    def connect(self, **_kwargs: Any) -> bool:
        """
        Connect to hardware device.

        This method must establish connection to the physical hardware,
        initialize device settings, verify communication, and emit the
        connection_changed signal.

        Args:
            **kwargs: Device-specific connection parameters. Common parameters:
                - Camera: camera_id (str, optional)
                - Actuator: com_port (str), baudrate (int), auto_home (bool)
                - Laser: com_port (str), baudrate (int)
                - GPIO: port (str)

        Returns:
            True if connection successful, False otherwise.
            Must update self.is_connected and emit connection_changed signal.

        Raises:
            May raise device-specific exceptions, but should handle gracefully
            by emitting error_occurred signal and returning False.

        Example:
            ```python
            def connect(self, com_port: str = "COM3") -> bool:
                try:
                    # Connect to hardware
                    self.device = DeviceAPI(com_port)
                    self.is_connected = True
                    self.connection_changed.emit(True)
                    return True
                except Exception as e:
                    self.error_occurred.emit(f"Connection failed: {e}")
                    return False
            ```
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from hardware device and cleanup resources.

        This method must:
        1. Stop any ongoing operations (streaming, monitoring, movement)
        2. Disable outputs safely (lasers, motors, etc.)
        3. Close communication ports
        4. Update self.is_connected = False
        5. Emit connection_changed(False) signal

        Should not raise exceptions - errors during cleanup should be
        logged but not propagated.

        Example:
            ```python
            def disconnect(self) -> None:
                self.stop_all_operations()
                if self.device:
                    try:
                        self.device.close()
                    except Exception as e:
                        logger.warning(f"Error during cleanup: {e}")
                    self.device = None
                self.is_connected = False
                self.connection_changed.emit(False)
            ```
        """
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Get current hardware status and state information.

        This method provides a standardized way to query the current state
        of the hardware device. Useful for debugging, monitoring, and UI updates.

        Returns:
            Dictionary containing status information. Must include:
            - 'connected' (bool): Connection status
            - Additional device-specific status fields

        Example return values:
            Camera: {'connected': True, 'streaming': True, 'fps': 30.0}
            Actuator: {'connected': True, 'homed': True, 'position_um': 1000.0}
            Laser: {'connected': True, 'output_enabled': False, 'current_ma': 0.0}
            GPIO: {'connected': True, 'motor_enabled': False, 'vibration': False}

        Note:
            This method should be fast and non-blocking. For expensive operations,
            use cached values updated by monitoring timers.
        """
        pass

    def is_hardware_available(self) -> bool:
        """
        Check if hardware dependencies are available.

        Useful for checking if required libraries (VmbPy, Xeryon, pyserial)
        are installed before attempting connection.

        Returns:
            True if hardware can be accessed, False if libraries missing.
            Base implementation returns True; override if needed.
        """
        return True

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            String showing class name and connection status.
        """
        status = "connected" if self.is_connected else "disconnected"
        return f"{self.__class__.__name__}(status={status})"
