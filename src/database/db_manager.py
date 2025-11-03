"""
Database manager for TOSCA.

Handles database initialization, connection management, and CRUD operations.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, joinedload, sessionmaker

from database.models import Base, SafetyLog
from database.models import Session as SessionModel
from database.models import Subject, TechUser

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and operations.

    Provides high-level interface for database operations while
    maintaining connection pooling and transaction management.
    """

    def __init__(self, db_path: str = "data/tosca.db") -> None:
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.engine = None
        self.SessionLocal = None

    def initialize(self) -> None:
        """Initialize database connection and create tables if needed."""
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create engine with connection pooling
        database_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            connect_args={"check_same_thread": False},  # For SQLite
        )

        # Enable foreign keys and WAL mode for SQLite
        if self.engine:
            with self.engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys = ON"))
                conn.execute(text("PRAGMA journal_mode = WAL"))
                conn.commit()

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        # Initialize with default data if database is new
        if self._is_new_database():
            self._initialize_default_data()

        logger.info(f"Database initialized at {self.db_path}")

    def _is_new_database(self) -> bool:
        """Check if database is newly created (no users)."""
        with self.get_session() as session:
            result = session.execute(select(TechUser)).first()
            return result is None

    def _initialize_default_data(self) -> None:
        """Initialize database with default admin user and log entry."""
        with self.get_session() as session:
            # Create default admin user
            admin_user = TechUser(
                username="admin",
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            session.add(admin_user)
            session.commit()

            # Log database creation
            log_entry = SafetyLog(
                timestamp=datetime.now(),
                event_type="database_initialized",
                severity="info",
                description="Database schema created",
                system_state="idle",
                action_taken="none",
            )
            session.add(log_entry)
            session.commit()

        logger.info("Default data initialized (admin user created)")

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy session for database operations

        Usage:
            with db_manager.get_session() as session:
                # perform database operations
                session.commit()
        """
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    # Subject Operations

    def create_subject(
        self,
        subject_code: str,
        tech_id: int,
        date_of_birth: Optional[datetime] = None,
        gender: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Subject:
        """
        Create a new subject.

        Args:
            subject_code: Subject identifier (e.g., "P-2025-0001")
            tech_id: ID of technician creating the subject
            date_of_birth: Optional date of birth
            gender: Optional gender
            notes: Optional notes

        Returns:
            Created Subject instance
        """
        with self.get_session() as session:
            subject = Subject(
                subject_code=subject_code,
                created_by_tech_id=tech_id,
                date_of_birth=date_of_birth,
                gender=gender,
                notes=notes,
                created_date=datetime.now(),
                is_active=True,
            )
            session.add(subject)
            session.commit()
            session.refresh(subject)
            logger.info(f"Subject created: {subject_code}")
            return subject

    def get_subject_by_code(self, subject_code: str) -> Optional[Subject]:
        """
        Find subject by subject code.

        Args:
            subject_code: Subject identifier

        Returns:
            Subject instance or None if not found
        """
        with self.get_session() as session:
            result = session.execute(
                select(Subject).where(Subject.subject_code == subject_code)
            ).first()
            if result:
                return result[0]
            return None

    def get_subject_session_count(self, subject_id: int) -> int:
        """
        Get total session count for a subject.

        Args:
            subject_id: Subject ID

        Returns:
            Number of sessions
        """
        with self.get_session() as session:
            count: int = session.query(SessionModel).filter_by(subject_id=subject_id).count()
            return count

    def get_all_sessions(
        self, subject_id: Optional[int] = None, limit: int = 100
    ) -> list[SessionModel]:
        """
        Get all sessions from the database.

        Args:
            subject_id: Optional filter by subject ID
            limit: Maximum number of sessions to retrieve

        Returns:
            List of Session instances with related data
        """
        with self.get_session() as session:
            query = session.query(SessionModel).options(
                joinedload(SessionModel.subject), joinedload(SessionModel.technician)
            )

            if subject_id is not None:
                query = query.filter_by(subject_id=subject_id)

            # Order by start_time descending (most recent first)
            query = query.order_by(SessionModel.start_time.desc()).limit(limit)

            sessions: list[SessionModel] = query.all()
            logger.debug(f"Retrieved {len(sessions)} sessions")
            return sessions

    # Technician Operations

    def get_technician_by_username(self, username: str) -> Optional[TechUser]:
        """
        Find technician by username.

        Args:
            username: Technician username

        Returns:
            TechUser instance or None if not found
        """
        with self.get_session() as session:
            result = session.execute(select(TechUser).where(TechUser.username == username)).first()
            if result:
                return result[0]
            return None

    def update_technician_last_login(self, tech_id: int) -> None:
        """
        Update technician's last login time.

        Args:
            tech_id: Technician ID
        """
        with self.get_session() as session:
            tech = session.get(TechUser, tech_id)
            if tech:
                tech.last_login = datetime.now()
                session.commit()

    # Safety Log Operations

    def log_safety_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        session_id: Optional[int] = None,
        tech_id: Optional[int] = None,
        system_state: Optional[str] = None,
        action_taken: Optional[str] = None,
    ) -> SafetyLog:
        """
        Log a safety event.

        Args:
            event_type: Type of safety event
            severity: Event severity (info, warning, critical, emergency)
            description: Event description
            session_id: Optional session ID
            tech_id: Optional technician ID
            system_state: Optional system state
            action_taken: Optional action taken

        Returns:
            Created SafetyLog instance
        """
        with self.get_session() as session:
            log_entry = SafetyLog(
                timestamp=datetime.now(),
                event_type=event_type,
                severity=severity,
                description=description,
                session_id=session_id,
                tech_id=tech_id,
                system_state=system_state,
                action_taken=action_taken,
            )
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            logger.info(f"Safety event logged: {event_type} ({severity})")
            return log_entry

    def get_safety_logs(
        self,
        limit: int = 100,
        session_id: Optional[int] = None,
        min_severity: Optional[str] = None,
    ) -> list[SafetyLog]:
        """
        Retrieve safety logs from database.

        Args:
            limit: Maximum number of logs to retrieve (default: 100)
            session_id: Optional filter by session ID
            min_severity: Optional minimum severity filter (info, warning, critical, emergency)

        Returns:
            List of SafetyLog instances, ordered by timestamp (most recent first)
        """
        severity_order = {"info": 0, "warning": 1, "critical": 2, "emergency": 3}

        with self.get_session() as session:
            query = select(SafetyLog)

            # Filter by session if provided
            if session_id is not None:
                query = query.where(SafetyLog.session_id == session_id)

            # Filter by severity if provided
            if min_severity:
                min_level = severity_order.get(min_severity.lower(), 0)
                valid_severities = [
                    sev for sev, level in severity_order.items() if level >= min_level
                ]
                query = query.where(SafetyLog.severity.in_(valid_severities))

            # Order by timestamp descending (most recent first)
            query = query.order_by(SafetyLog.timestamp.desc()).limit(limit)

            result = session.execute(query)
            logs = list(result.scalars().all())
            logger.debug(f"Retrieved {len(logs)} safety logs")
            return logs

    # Database Maintenance Operations

    def vacuum_database(self) -> tuple[bool, str, dict]:
        """
        Perform VACUUM operation to reclaim space and defragment database.

        VACUUM rebuilds the database file, reclaiming unused space from deleted
        records and defragmenting the database for better performance.

        WARNING: This operation locks the database briefly (seconds to minutes
        depending on database size). Should only be called when no active
        sessions are running.

        Returns:
            tuple[bool, str, dict]: (success, message, stats)
                - success: True if vacuum succeeded, False if failed
                - message: Human-readable result message
                - stats: Dictionary containing before/after file sizes

        Example:
            success, message, stats = db_manager.vacuum_database()
            if success:
                print(f"Vacuum complete: {stats['size_before_mb']:.1f}MB -> "
                      f"{stats['size_after_mb']:.1f}MB "
                      f"({stats['size_reduction_percent']:.1f}% reduction)")
        """
        try:
            # Measure database file size before vacuum
            db_file = Path(self.db_path)
            if not db_file.exists():
                return False, "Database file not found", {}

            size_before_bytes = db_file.stat().st_size
            size_before_mb = size_before_bytes / (1024 * 1024)

            logger.info(f"Starting VACUUM operation (current size: {size_before_mb:.2f}MB)")

            # Perform VACUUM operation
            # This rebuilds the database file, reclaiming unused space
            with self.engine.connect() as conn:
                conn.execute(text("VACUUM"))
                conn.commit()

            # Measure database file size after vacuum
            size_after_bytes = db_file.stat().st_size
            size_after_mb = size_after_bytes / (1024 * 1024)
            size_reduction_bytes = size_before_bytes - size_after_bytes
            size_reduction_mb = size_reduction_bytes / (1024 * 1024)
            size_reduction_percent = (
                (size_reduction_bytes / size_before_bytes * 100) if size_before_bytes > 0 else 0
            )

            stats = {
                "size_before_bytes": size_before_bytes,
                "size_after_bytes": size_after_bytes,
                "size_before_mb": size_before_mb,
                "size_after_mb": size_after_mb,
                "size_reduction_bytes": size_reduction_bytes,
                "size_reduction_mb": size_reduction_mb,
                "size_reduction_percent": size_reduction_percent,
            }

            message = (
                f"Database vacuum complete: {size_before_mb:.2f}MB -> {size_after_mb:.2f}MB "
                f"({size_reduction_mb:.2f}MB freed, {size_reduction_percent:.1f}% reduction)"
            )
            logger.info(message)

            return True, message, stats

        except Exception as e:
            error_msg = f"Database vacuum failed: {e}"
            logger.error(error_msg)
            return False, error_msg, {}

    def get_database_size(self) -> tuple[bool, float, str]:
        """
        Get current database file size.

        Returns:
            tuple[bool, float, str]: (success, size_mb, message)
                - success: True if size retrieved, False if failed
                - size_mb: Database file size in MB
                - message: Human-readable message
        """
        try:
            db_file = Path(self.db_path)
            if not db_file.exists():
                return False, 0.0, "Database file not found"

            size_bytes = db_file.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            message = f"Database size: {size_mb:.2f}MB"
            return True, size_mb, message

        except Exception as e:
            error_msg = f"Failed to get database size: {e}"
            logger.error(error_msg)
            return False, 0.0, error_msg
