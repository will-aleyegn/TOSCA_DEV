"""
Session manager for TOSCA treatment sessions.

Handles session lifecycle: creation, activation, completion, and data organization.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.database.db_manager import DatabaseManager
from src.database.models import Session, Subject

logger = logging.getLogger(__name__)


class SessionManager(QObject):
    """
    Manages treatment session lifecycle.

    Coordinates session creation, activation, file organization,
    and completion with database persistence.
    """

    # Signals
    session_started = pyqtSignal(int)  # session_id
    session_ended = pyqtSignal(int)  # session_id
    session_status_changed = pyqtSignal(str)  # status text

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize session manager.

        Args:
            db_manager: Database manager instance
        """
        super().__init__()
        self.db_manager = db_manager
        self.current_session: Optional[Session] = None
        self.current_session_folder: Optional[Path] = None

    def create_session(
        self,
        subject: Subject,
        tech_id: int,
        treatment_site: Optional[str] = None,
        treatment_notes: Optional[str] = None,
        protocol_id: Optional[int] = None,
    ) -> Session:
        """
        Create a new treatment session.

        Args:
            subject: Subject for this session
            tech_id: Technician ID
            treatment_site: Optional anatomical location
            treatment_notes: Optional pre-treatment notes
            protocol_id: Optional protocol ID

        Returns:
            Created Session instance
        """
        # Create session folder
        session_folder = self._create_session_folder(subject.subject_code)

        # Create database record
        with self.db_manager.get_session() as db_session:
            session = Session(
                subject_id=subject.subject_id,
                tech_id=tech_id,
                protocol_id=protocol_id,
                start_time=datetime.now(),
                status="in_progress",
                treatment_site=treatment_site,
                treatment_notes=treatment_notes,
                session_folder_path=str(session_folder),
            )
            db_session.add(session)
            db_session.commit()
            db_session.refresh(session)

            # Store current session
            self.current_session = session
            self.current_session_folder = session_folder

            logger.info(f"Session created: ID={session.session_id}, Subject={subject.subject_code}")
            self.session_started.emit(session.session_id)
            self.session_status_changed.emit(
                f"Session active: {subject.subject_code} (ID: {session.session_id})"
            )

            return session

    def _create_session_folder(self, subject_code: str) -> Path:
        """
        Create session data folder.

        Args:
            subject_code: Subject identifier

        Returns:
            Path to session folder

        Folder structure:
            data/sessions/P-2025-0001/2025-10-24_143022/
        """
        base_path = Path("data/sessions")
        subject_path = base_path / subject_code
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        session_path = subject_path / timestamp

        session_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Session folder created: {session_path}")

        return session_path

    def get_current_session(self) -> Optional[Session]:
        """
        Get the current active session.

        Returns:
            Current Session instance or None
        """
        return self.current_session

    def get_session_folder(self) -> Optional[Path]:
        """
        Get the current session folder path.

        Returns:
            Path to session folder or None
        """
        return self.current_session_folder

    def is_session_active(self) -> bool:
        """
        Check if a session is currently active.

        Returns:
            True if session active
        """
        return self.current_session is not None and self.current_session.status == "in_progress"

    def complete_session(
        self,
        post_treatment_notes: Optional[str] = None,
        total_laser_on_time: Optional[float] = None,
        avg_power: Optional[float] = None,
        max_power: Optional[float] = None,
        total_energy: Optional[float] = None,
    ) -> None:
        """
        Complete the current session.

        Args:
            post_treatment_notes: Optional post-treatment observations
            total_laser_on_time: Total laser on time (seconds)
            avg_power: Average power (watts)
            max_power: Maximum power (watts)
            total_energy: Total energy delivered (joules)
        """
        if not self.current_session:
            logger.warning("No active session to complete")
            return

        end_time = datetime.now()
        duration = int((end_time - self.current_session.start_time).total_seconds())

        with self.db_manager.get_session() as db_session:
            # Get fresh session from database
            session = db_session.get(Session, self.current_session.session_id)
            if session:
                session.end_time = end_time
                session.duration_seconds = duration
                session.status = "completed"
                session.post_treatment_notes = post_treatment_notes
                session.total_laser_on_time_seconds = total_laser_on_time
                session.avg_power_watts = avg_power
                session.max_power_watts = max_power
                session.total_energy_joules = total_energy
                db_session.commit()

                logger.info(f"Session completed: ID={session.session_id}, Duration={duration}s")
                self.session_ended.emit(session.session_id)
                self.session_status_changed.emit("No active session")

        # Clear current session
        self.current_session = None
        self.current_session_folder = None

    def abort_session(self, abort_reason: str) -> None:
        """
        Abort the current session.

        Args:
            abort_reason: Reason for aborting
        """
        if not self.current_session:
            logger.warning("No active session to abort")
            return

        end_time = datetime.now()
        duration = int((end_time - self.current_session.start_time).total_seconds())

        with self.db_manager.get_session() as db_session:
            session = db_session.get(Session, self.current_session.session_id)
            if session:
                session.end_time = end_time
                session.duration_seconds = duration
                session.status = "aborted"
                session.abort_reason = abort_reason
                db_session.commit()

                logger.warning(f"Session aborted: ID={session.session_id}, Reason={abort_reason}")
                self.session_ended.emit(session.session_id)
                self.session_status_changed.emit("No active session")

        # Clear current session
        self.current_session = None
        self.current_session_folder = None

    def pause_session(self) -> None:
        """Pause the current session."""
        if not self.current_session:
            logger.warning("No active session to pause")
            return

        with self.db_manager.get_session() as db_session:
            session = db_session.get(Session, self.current_session.session_id)
            if session:
                session.status = "paused"
                db_session.commit()
                logger.info(f"Session paused: ID={session.session_id}")
                self.session_status_changed.emit(f"Session paused: ID={session.session_id}")

    def resume_session(self) -> None:
        """Resume the paused session."""
        if not self.current_session:
            logger.warning("No session to resume")
            return

        with self.db_manager.get_session() as db_session:
            session = db_session.get(Session, self.current_session.session_id)
            if session:
                session.status = "in_progress"
                db_session.commit()
                logger.info(f"Session resumed: ID={session.session_id}")
                self.session_status_changed.emit(f"Session resumed: ID={session.session_id}")

    def end_session(self) -> None:
        """
        End the current session (alias for complete_session with no stats).

        This is a simplified version for manual session ending from UI.
        """
        if not self.current_session:
            logger.warning("No active session to end")
            return

        self.complete_session()

    def update_session_video_path(self, video_path: str) -> None:
        """
        Update the video path for the current session.

        Args:
            video_path: Path to recorded video
        """
        if not self.current_session:
            logger.warning("No active session to update video path")
            return

        with self.db_manager.get_session() as db_session:
            session = db_session.get(Session, self.current_session.session_id)
            if session:
                session.video_path = video_path
                db_session.commit()
                logger.info(f"Session video path updated: {video_path}")

    def get_session_info_text(self) -> str:
        """
        Get human-readable session info.

        Returns:
            Session information text
        """
        if not self.current_session:
            return "No active session"

        duration = int((datetime.now() - self.current_session.start_time).total_seconds())
        minutes = duration // 60
        seconds = duration % 60

        return (
            f"Session ID: {self.current_session.session_id}\n"
            f"Status: {self.current_session.status}\n"
            f"Duration: {minutes:02d}:{seconds:02d}\n"
            f"Folder: {self.current_session.session_folder_path}"
        )
