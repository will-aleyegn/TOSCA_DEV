"""
Event logging system for immutable audit trail.

Logs all safety-critical events, user actions, and system state changes
to both file and database for regulatory compliance and debugging.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event classification for audit trail."""

    # Safety events
    SAFETY_INTERLOCK_TRIGGERED = "safety_interlock_triggered"
    SAFETY_INTERLOCK_CLEARED = "safety_interlock_cleared"
    EMERGENCY_STOP = "emergency_stop"

    # Session events
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    SUBJECT_SELECTED = "subject_selected"

    # Treatment events
    PROTOCOL_STARTED = "protocol_started"
    PROTOCOL_PAUSED = "protocol_paused"
    PROTOCOL_RESUMED = "protocol_resumed"
    PROTOCOL_STOPPED = "protocol_stopped"
    PROTOCOL_COMPLETED = "protocol_completed"
    ACTION_EXECUTED = "action_executed"

    # Hardware events
    LASER_POWER_CHANGED = "laser_power_changed"
    ACTUATOR_MOVED = "actuator_moved"
    CAMERA_FRAME_CAPTURED = "camera_frame_captured"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    ERROR_OCCURRED = "error_occurred"


class EventLogger:
    """
    Centralized event logging for audit trail.

    Logs events to both file and database (when available).
    All logged events are immutable and timestamped.
    """

    def __init__(
        self,
        log_file: Optional[Path] = None,
        db_connection: Optional[Any] = None,
    ) -> None:
        """
        Initialize event logger.

        Args:
            log_file: Path to event log file (defaults to data/logs/events.jsonl)
            db_connection: Database connection for event storage (optional)
        """
        self.log_file = log_file or Path("data/logs/events.jsonl")
        self.db_connection = db_connection

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Event logger initialized: {self.log_file}")

    def log_event(
        self,
        event_type: EventType,
        details: Dict[str, Any],
        session_id: Optional[str] = None,
        severity: str = "INFO",
    ) -> None:
        """
        Log an event to file and database.

        Args:
            event_type: Type of event being logged
            details: Event-specific details (dict)
            session_id: Optional session identifier
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "severity": severity,
            "session_id": session_id,
            "details": details,
        }

        # Log to file (JSONL format - one JSON object per line)
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to write event to file: {e}")

        # Log to database (when available)
        if self.db_connection:
            try:
                self._log_to_database(event)
            except Exception as e:
                logger.error(f"Failed to write event to database: {e}")

        # Also log to standard logger
        log_message = f"{event_type.value}: {details}"
        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, log_message)

    def _log_to_database(self, event: Dict[str, Any]) -> None:
        """
        Write event to database.

        Args:
            event: Event dictionary to store

        Note: Implementation pending database layer completion
        """
        # TODO: Implement database storage
        # Will use SQLAlchemy model when database layer is complete
        pass

    def log_safety_event(
        self,
        interlock_name: str,
        triggered: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log safety interlock event.

        Args:
            interlock_name: Name of the interlock (e.g., "footpedal", "photodiode")
            triggered: True if triggered, False if cleared
            details: Additional event details
        """
        event_type = (
            EventType.SAFETY_INTERLOCK_TRIGGERED
            if triggered
            else EventType.SAFETY_INTERLOCK_CLEARED
        )

        event_details = {
            "interlock": interlock_name,
            **(details or {}),
        }

        self.log_event(
            event_type=event_type,
            details=event_details,
            severity="CRITICAL" if triggered else "INFO",
        )

    def log_protocol_event(
        self,
        protocol_name: str,
        action: str,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log protocol execution event.

        Args:
            protocol_name: Name of the protocol
            action: Action taken (started, paused, resumed, stopped, completed)
            session_id: Session identifier
            details: Additional event details
        """
        event_type_map = {
            "started": EventType.PROTOCOL_STARTED,
            "paused": EventType.PROTOCOL_PAUSED,
            "resumed": EventType.PROTOCOL_RESUMED,
            "stopped": EventType.PROTOCOL_STOPPED,
            "completed": EventType.PROTOCOL_COMPLETED,
        }

        event_type = event_type_map.get(action.lower())
        if not event_type:
            logger.warning(f"Unknown protocol action: {action}")
            return

        event_details = {
            "protocol_name": protocol_name,
            **(details or {}),
        }

        self.log_event(
            event_type=event_type,
            details=event_details,
            session_id=session_id,
            severity="INFO",
        )


# Global event logger instance
_event_logger: Optional[EventLogger] = None


def get_event_logger() -> EventLogger:
    """
    Get global event logger instance.

    Returns:
        EventLogger instance
    """
    global _event_logger
    if _event_logger is None:
        _event_logger = EventLogger()
    return _event_logger
