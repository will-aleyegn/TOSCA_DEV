"""
Session manager for TOSCA treatment sessions.

Handles session lifecycle: creation, activation, completion, and data organization.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from database.db_manager import DatabaseManager
from database.models import Session, Subject

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

        # Developer mode bypass
        self.developer_mode_enabled = False

    def create_session(
        self,
        subject: Subject,
        tech_id: int,
        treatment_site: Optional[str] = None,
        treatment_notes: Optional[str] = None,
        protocol_id: Optional[int] = None,
    ) -> Optional[Session]:
        """
        Create a new treatment session.

        Args:
            subject: Subject for this session
            tech_id: Technician ID
            treatment_site: Optional anatomical location
            treatment_notes: Optional pre-treatment notes
            protocol_id: Optional protocol ID

        Returns:
            Created Session instance or None if creation fails
        """
        session_folder = None

        try:
            # Create database record FIRST (fixes transaction ordering)
            with self.db_manager.get_session() as db_session:
                session = Session(
                    subject_id=subject.subject_id,
                    tech_id=tech_id,
                    protocol_id=protocol_id,
                    start_time=datetime.now(),
                    status="in_progress",
                    treatment_site=treatment_site,
                    treatment_notes=treatment_notes,
                    session_folder_path=None,  # Will be updated after folder creation
                )
                db_session.add(session)
                db_session.commit()
                db_session.refresh(session)
        except Exception as e:
            logger.error(f"Database error during session creation: {e}", exc_info=True)
            return None

        # Create filesystem folder (only after successful database commit)
        try:
            session_folder = self._create_session_folder(subject.subject_code)
        except Exception as e:
            logger.error(f"Failed to create session folder: {e}", exc_info=True)
            # Database record exists but no folder - log for cleanup
            logger.warning(f"Session {session.session_id} created without folder path")
            # Continue with session creation (folder path will be None)

        # Update database with folder path (if folder was created)
        if session_folder:
            try:
                with self.db_manager.get_session() as db_session:
                    session_to_update = db_session.get(Session, session.session_id)
                    if session_to_update:
                        session_to_update.session_folder_path = str(session_folder)
                        db_session.commit()
                        session.session_folder_path = str(session_folder)  # Update local copy
            except Exception as e:
                logger.error(f"Failed to update session folder path: {e}", exc_info=True)
                # Folder exists but path not recorded - log for manual cleanup

        # Store current session
        self.current_session = session
        self.current_session_folder = session_folder

        logger.info(f"Session created: ID={session.session_id}, Subject={subject.subject_code}")
        self.session_started.emit(session.session_id)
        self.session_status_changed.emit(
            f"Session active: {subject.subject_code} (ID: {session.session_id})"
        )

        return session

    def create_dev_session(self) -> Optional[Session]:
        """
        Create/retrieve developer mode session.

        Automatically creates a DEV-SUBJECT and starts a session for quick testing.
        For calibration and testing ONLY.

        Returns:
            Created/active dev Session instance or None if creation fails
        """
        # If dev session already active, return it
        if self.current_session and self.current_session.subject_id == "DEV-SUBJECT":
            logger.debug("Developer session already active")
            return self.current_session

        try:
            # Check if dev subject exists, create if not
            with self.db_manager.get_session() as db_session:
                dev_subject = (
                    db_session.query(Subject).filter_by(subject_code="DEV-SUBJECT").first()
                )

                if not dev_subject:
                    logger.info("Creating DEV-SUBJECT for developer mode")
                    dev_subject = Subject(
                        subject_code="DEV-SUBJECT",
                        notes="Auto-created for developer mode testing",
                    )
                    db_session.add(dev_subject)
                    db_session.commit()

            # Create new dev session
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            with self.db_manager.get_session() as db_session:
                # Get the dev subject
                dev_subject = (
                    db_session.query(Subject).filter_by(subject_code="DEV-SUBJECT").first()
                )

                if not dev_subject:
                    logger.error("Failed to create/retrieve DEV-SUBJECT")
                    return None

                # Create session
                session = Session(
                    subject_id=dev_subject.subject_id,
                    tech_id=0,  # No technician in dev mode
                    protocol_id=None,
                    start_time=datetime.now(),
                    status="in_progress",
                    treatment_site="DEVELOPER MODE",
                    treatment_notes=f"Developer mode session {timestamp}",
                    session_folder_path=None,
                )

                db_session.add(session)
                db_session.commit()
                db_session.refresh(session)

                # Store current session (no folder needed for dev mode)
                self.current_session = session
                self.current_session_folder = None

                logger.warning(f"Developer session created: ID={session.session_id}")
                self.session_started.emit(session.session_id)
                self.session_status_changed.emit(
                    f"DEV MODE: Session active (ID: {session.session_id})"
                )

                return session

        except Exception as e:
            logger.error(f"Failed to create developer session: {e}", exc_info=True)
            return None

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

        In developer mode, automatically creates a dev session if none exists.

        Returns:
            Current Session instance or None
        """
        # Developer mode: auto-create dev session if needed
        if self.developer_mode_enabled and not self.current_session:
            logger.info("Developer mode: Auto-creating dev session")
            self.create_dev_session()

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
    ) -> bool:
        """
        Complete the current session.

        Args:
            post_treatment_notes: Optional post-treatment observations
            total_laser_on_time: Total laser on time (seconds)
            avg_power: Average power (watts)
            max_power: Maximum power (watts)
            total_energy: Total energy delivered (joules)

        Returns:
            True if session completed successfully, False otherwise
        """
        if not self.current_session:
            logger.warning("No active session to complete")
            return False

        end_time = datetime.now()
        duration = int((end_time - self.current_session.start_time).total_seconds())

        try:
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

                    # Clear current session only after successful commit
                    self.current_session = None
                    self.current_session_folder = None
                    return True
                else:
                    logger.error(f"Session {self.current_session.session_id} not found in database")
                    return False
        except Exception as e:
            logger.error(f"Database error during session completion: {e}", exc_info=True)
            return False

    def abort_session(self, abort_reason: str) -> bool:
        """
        Abort the current session.

        Args:
            abort_reason: Reason for aborting

        Returns:
            True if session aborted successfully, False otherwise
        """
        if not self.current_session:
            logger.warning("No active session to abort")
            return False

        end_time = datetime.now()
        duration = int((end_time - self.current_session.start_time).total_seconds())

        try:
            with self.db_manager.get_session() as db_session:
                session = db_session.get(Session, self.current_session.session_id)
                if session:
                    session.end_time = end_time
                    session.duration_seconds = duration
                    session.status = "aborted"
                    session.abort_reason = abort_reason
                    db_session.commit()

                    logger.warning(
                        f"Session aborted: ID={session.session_id}, Reason={abort_reason}"
                    )
                    self.session_ended.emit(session.session_id)
                    self.session_status_changed.emit("No active session")

                    # Clear current session only after successful commit
                    self.current_session = None
                    self.current_session_folder = None
                    return True
                else:
                    logger.error(f"Session {self.current_session.session_id} not found in database")
                    return False
        except Exception as e:
            logger.error(f"Database error during session abort: {e}", exc_info=True)
            return False

    def pause_session(self) -> bool:
        """
        Pause the current session.

        Returns:
            True if session paused successfully, False otherwise
        """
        if not self.current_session:
            logger.warning("No active session to pause")
            return False

        try:
            with self.db_manager.get_session() as db_session:
                session = db_session.get(Session, self.current_session.session_id)
                if session:
                    session.status = "paused"
                    db_session.commit()
                    logger.info(f"Session paused: ID={session.session_id}")
                    self.session_status_changed.emit(f"Session paused: ID={session.session_id}")
                    return True
                else:
                    logger.error(f"Session {self.current_session.session_id} not found in database")
                    return False
        except Exception as e:
            logger.error(f"Database error during session pause: {e}", exc_info=True)
            return False

    def resume_session(self) -> bool:
        """
        Resume the paused session.

        Returns:
            True if session resumed successfully, False otherwise
        """
        if not self.current_session:
            logger.warning("No session to resume")
            return False

        try:
            with self.db_manager.get_session() as db_session:
                session = db_session.get(Session, self.current_session.session_id)
                if session:
                    session.status = "in_progress"
                    db_session.commit()
                    logger.info(f"Session resumed: ID={session.session_id}")
                    self.session_status_changed.emit(f"Session resumed: ID={session.session_id}")
                    return True
                else:
                    logger.error(f"Session {self.current_session.session_id} not found in database")
                    return False
        except Exception as e:
            logger.error(f"Database error during session resume: {e}", exc_info=True)
            return False

    def end_session(self) -> None:
        """
        End the current session (alias for complete_session with no stats).

        This is a simplified version for manual session ending from UI.
        """
        if not self.current_session:
            logger.warning("No active session to end")
            return

        self.complete_session()

    def update_session_video_path(self, video_path: str) -> bool:
        """
        Update the video path for the current session.

        Args:
            video_path: Path to recorded video

        Returns:
            True if video path updated successfully, False otherwise
        """
        if not self.current_session:
            logger.warning("No active session to update video path")
            return False

        try:
            with self.db_manager.get_session() as db_session:
                session = db_session.get(Session, self.current_session.session_id)
                if session:
                    session.video_path = video_path
                    db_session.commit()
                    logger.info(f"Session video path updated: {video_path}")
                    return True
                else:
                    logger.error(f"Session {self.current_session.session_id} not found in database")
                    return False
        except Exception as e:
            logger.error(f"Database error updating video path: {e}", exc_info=True)
            return False

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
