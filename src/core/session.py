"""
Session management for TOSCA treatment sessions.

Handles session lifecycle, subject tracking, and treatment recording.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Treatment session states."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"


@dataclass
class Session:
    """
    Treatment session data model.

    Tracks all information about a single treatment session including
    subject, operator, timestamps, and treatment history.
    """

    session_id: str
    subject_id: str
    operator_id: str
    start_time: datetime
    state: SessionState = SessionState.INITIALIZING

    end_time: Optional[datetime] = None
    notes: str = ""
    video_file_path: Optional[str] = None

    # Treatment history (will be populated during session)
    protocols_executed: List[str] = field(default_factory=list)
    events: List[dict] = field(default_factory=list)

    # Safety tracking
    safety_events: List[dict] = field(default_factory=list)
    emergency_stops: int = 0

    def __post_init__(self) -> None:
        """Initialize session after creation."""
        logger.info(f"Session created: {self.session_id} for subject {self.subject_id}")

    def start(self) -> None:
        """Mark session as active."""
        self.state = SessionState.ACTIVE
        logger.info(f"Session {self.session_id} started")

    def pause(self) -> None:
        """Pause active session."""
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.PAUSED
            logger.info(f"Session {self.session_id} paused")

    def resume(self) -> None:
        """Resume paused session."""
        if self.state == SessionState.PAUSED:
            self.state = SessionState.ACTIVE
            logger.info(f"Session {self.session_id} resumed")

    def complete(self) -> None:
        """Mark session as completed."""
        self.end_time = datetime.now()
        self.state = SessionState.COMPLETED
        logger.info(f"Session {self.session_id} completed")

    def abort(self, reason: str = "") -> None:
        """Abort session due to error or emergency stop."""
        self.end_time = datetime.now()
        self.state = SessionState.ABORTED
        if reason:
            self.notes += f"\nAborted: {reason}"
        logger.warning(f"Session {self.session_id} aborted: {reason}")

    def add_protocol_execution(self, protocol_name: str) -> None:
        """Record protocol execution in session history."""
        self.protocols_executed.append(protocol_name)
        logger.debug(f"Protocol {protocol_name} added to session {self.session_id}")

    def add_event(self, event_type: str, details: dict) -> None:
        """
        Add event to session history.

        Args:
            event_type: Type of event
            details: Event details dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
        }
        self.events.append(event)

    def add_safety_event(self, event: dict) -> None:
        """
        Record safety event.

        Args:
            event: Safety event dictionary
        """
        self.safety_events.append(event)
        if event.get("type") == "emergency_stop":
            self.emergency_stops += 1
        logger.warning(f"Safety event in session {self.session_id}: {event}")

    def get_duration_seconds(self) -> Optional[float]:
        """
        Calculate session duration in seconds.

        Returns:
            Duration in seconds, or None if session not ended
        """
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> dict:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "subject_id": self.subject_id,
            "operator_id": self.operator_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "state": self.state.value,
            "notes": self.notes,
            "video_file_path": self.video_file_path,
            "protocols_executed": self.protocols_executed,
            "events": self.events,
            "safety_events": self.safety_events,
            "emergency_stops": self.emergency_stops,
            "duration_seconds": self.get_duration_seconds(),
        }
