"""
Event logger for TOSCA treatment system.

Provides immutable audit trail for all safety-critical and operational events.
Integrates with database SafetyLog table for persistence and emits PyQt6 signals.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event type categories."""

    # Safety events
    SAFETY_EMERGENCY_STOP = "e_stop_pressed"
    SAFETY_EMERGENCY_CLEAR = "e_stop_released"
    SAFETY_INTERLOCK_FAIL = "interlock_failure"
    SAFETY_INTERLOCK_OK = "interlock_recovery"
    SAFETY_POWER_LIMIT = "power_limit_exceeded"
    SAFETY_GPIO_FAIL = "gpio_interlock_failure"
    SAFETY_GPIO_OK = "gpio_interlock_ok"

    # Hardware events
    HARDWARE_CAMERA_CONNECT = "camera_connected"
    HARDWARE_CAMERA_DISCONNECT = "camera_disconnected"
    HARDWARE_CAMERA_RECORDING_START = "camera_recording_started"
    HARDWARE_CAMERA_RECORDING_STOP = "camera_recording_stopped"
    HARDWARE_CAMERA_CAPTURE = "camera_image_captured"
    HARDWARE_LASER_CONNECT = "laser_connected"
    HARDWARE_LASER_DISCONNECT = "laser_disconnected"
    HARDWARE_LASER_TEMP_CHANGE = "laser_temperature_changed"
    HARDWARE_ACTUATOR_CONNECT = "actuator_connected"
    HARDWARE_ACTUATOR_DISCONNECT = "actuator_disconnected"
    HARDWARE_ACTUATOR_HOME_START = "actuator_homing_started"
    HARDWARE_ACTUATOR_HOME_COMPLETE = "actuator_homing_completed"
    HARDWARE_ACTUATOR_MOVE = "actuator_position_changed"
    HARDWARE_GPIO_CONNECT = "gpio_connected"
    HARDWARE_GPIO_DISCONNECT = "gpio_disconnected"
    HARDWARE_ERROR = "hardware_error"

    # Treatment events
    TREATMENT_SESSION_START = "session_started"
    TREATMENT_SESSION_END = "session_ended"
    TREATMENT_SESSION_ABORT = "session_aborted"
    TREATMENT_LASER_ON = "laser_enabled"
    TREATMENT_LASER_OFF = "laser_disabled"
    TREATMENT_POWER_CHANGE = "laser_power_changed"
    TREATMENT_PROTOCOL_START = "protocol_started"
    TREATMENT_PROTOCOL_END = "protocol_completed"

    # User events
    USER_LOGIN = "user_login"
    USER_ACTION = "user_action"
    USER_OVERRIDE = "user_override"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


class EventSeverity(Enum):
    """Event severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class EventLogger(QObject):
    """
    Central event logging system.

    Provides immutable audit trail for all system events.
    Events are persisted to database and emitted as signals for real-time display.
    Also logs to JSONL file for backup.
    """

    # Signals
    event_logged = pyqtSignal(str, str, str)  # (event_type, severity, description)

    def __init__(self, db_manager: DatabaseManager, log_file: Optional[Path] = None) -> None:
        """
        Initialize event logger.

        Args:
            db_manager: Database manager instance
            log_file: Optional path to JSONL log file (defaults to data/logs/events.jsonl)
        """
        super().__init__()
        self.db_manager = db_manager
        self.log_file = log_file or Path("data/logs/events.jsonl")
        self.current_session_id: Optional[int] = None
        self.current_tech_id: Optional[int] = None

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Event logger initialized: DB + file ({self.log_file})")

    def set_session(self, session_id: int, tech_id: int) -> None:
        """
        Set current session and technician for event logging.

        Args:
            session_id: Current session ID
            tech_id: Current technician ID
        """
        self.current_session_id = session_id
        self.current_tech_id = tech_id
        logger.info(f"Event logger session set: session={session_id}, tech={tech_id}")

    def clear_session(self) -> None:
        """Clear current session (called when session ends)."""
        self.current_session_id = None
        self.current_tech_id = None
        logger.info("Event logger session cleared")

    def log_event(
        self,
        event_type: EventType,
        description: str,
        severity: EventSeverity = EventSeverity.INFO,
        system_state: Optional[str] = None,
        laser_state: Optional[str] = None,
        footpedal_state: Optional[bool] = None,
        smoothing_device_state: Optional[bool] = None,
        photodiode_voltage: Optional[float] = None,
        action_taken: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log an event to database, file, and emit signal.

        Args:
            event_type: Type of event
            description: Human-readable description
            severity: Event severity level
            system_state: Optional system state (idle, ready, armed, treating, fault)
            laser_state: Optional laser state
            footpedal_state: Optional footpedal state
            smoothing_device_state: Optional smoothing device state
            photodiode_voltage: Optional photodiode voltage
            action_taken: Optional action taken in response
            details: Optional additional details (will be JSON-encoded)
        """
        # Log to database
        try:
            self.db_manager.log_safety_event(
                event_type=event_type.value,
                severity=severity.value,
                description=description,
                session_id=self.current_session_id,
                tech_id=self.current_tech_id,
                system_state=system_state,
                action_taken=action_taken,
            )
        except Exception as e:
            logger.error(f"Failed to log event to database: {e}")

        # Log to file (JSONL format)
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type.value,
                "severity": severity.value,
                "description": description,
                "session_id": self.current_session_id,
                "tech_id": self.current_tech_id,
                "system_state": system_state,
                "laser_state": laser_state,
                "action_taken": action_taken,
                "details": details,
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to log event to file: {e}")

        # Emit signal for real-time UI update
        self.event_logged.emit(event_type.value, severity.value, description)

        logger.info(f"Event logged: [{severity.value}] {event_type.value} - {description}")

    # Convenience methods for common events

    def log_safety_event(
        self,
        event_type: EventType,
        description: str,
        severity: EventSeverity = EventSeverity.WARNING,
        action_taken: Optional[str] = None,
    ) -> None:
        """
        Log a safety-related event.

        Args:
            event_type: Safety event type
            description: Event description
            severity: Event severity
            action_taken: Action taken in response
        """
        self.log_event(
            event_type=event_type,
            description=description,
            severity=severity,
            action_taken=action_taken,
        )

    def log_hardware_event(self, event_type: EventType, description: str, device_name: str) -> None:
        """
        Log a hardware connection event.

        Args:
            event_type: Hardware event type
            description: Event description
            device_name: Name of hardware device
        """
        self.log_event(
            event_type=event_type,
            description=description,
            severity=EventSeverity.INFO,
            details={"device": device_name},
        )

    def log_treatment_event(
        self,
        event_type: EventType,
        description: str,
        laser_power: Optional[float] = None,
        position: Optional[float] = None,
    ) -> None:
        """
        Log a treatment-related event.

        Args:
            event_type: Treatment event type
            description: Event description
            laser_power: Optional laser power in watts
            position: Optional actuator position
        """
        details = {}
        if laser_power is not None:
            details["laser_power_watts"] = laser_power
        if position is not None:
            details["actuator_position_um"] = position

        self.log_event(
            event_type=event_type,
            description=description,
            severity=EventSeverity.INFO,
            details=details if details else None,
        )

    def log_user_action(
        self,
        description: str,
        action_type: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log a user action.

        Args:
            description: Action description
            action_type: Type of action
            details: Optional action details
        """
        if details is None:
            details = {}
        details["action_type"] = action_type

        self.log_event(
            event_type=EventType.USER_ACTION,
            description=description,
            severity=EventSeverity.INFO,
            details=details,
        )

    def log_system_event(
        self,
        event_type: EventType,
        description: str,
        severity: EventSeverity = EventSeverity.INFO,
    ) -> None:
        """
        Log a system event.

        Args:
            event_type: System event type
            description: Event description
            severity: Event severity
        """
        self.log_event(event_type=event_type, description=description, severity=severity)

    def log_error(
        self,
        component: str,
        error_message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log an error event.

        Args:
            component: Component where error occurred
            error_message: Error message
            details: Optional error details
        """
        if details is None:
            details = {}
        details["component"] = component

        self.log_event(
            event_type=EventType.SYSTEM_ERROR,
            description=f"{component}: {error_message}",
            severity=EventSeverity.CRITICAL,
            details=details,
        )
