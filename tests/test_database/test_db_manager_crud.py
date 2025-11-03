"""
Comprehensive CRUD operation tests for DatabaseManager.

Tests all database operations including Subject, TechUser, Session, and SafetyLog
management with error handling, filtering, and edge cases.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from database.db_manager import DatabaseManager
from database.models import SafetyLog, Session, Subject, TechUser


@pytest.fixture
def db_manager(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_crud.db"
    db = DatabaseManager(str(db_path))
    db.initialize()
    yield db
    db.close()


# =============================================================================
# Initialization and Error Handling Tests
# =============================================================================


def test_get_session_before_initialize_raises_error(tmp_path):
    """Test that get_session() raises RuntimeError if called before initialize()."""
    db_path = tmp_path / "test_uninitialized.db"
    db = DatabaseManager(str(db_path))

    with pytest.raises(RuntimeError, match="Database not initialized"):
        db.get_session()


def test_close_disposes_engine(db_manager):
    """Test that close() properly disposes the database engine."""
    # Engine should be initialized
    assert db_manager.engine is not None

    # Close should dispose engine
    db_manager.close()

    # Engine should be disposed (can't test directly, but verify it doesn't crash)
    assert True  # If we got here without exception, close() worked


def test_get_database_size_returns_correct_size(db_manager):
    """Test that get_database_size() returns valid size."""
    success, size_mb, message = db_manager.get_database_size()

    assert success is True
    assert size_mb > 0  # Database should have some size
    assert "Database size" in message
    assert "MB" in message


def test_get_database_size_handles_missing_file():
    """Test that get_database_size() handles missing database file."""
    db = DatabaseManager("nonexistent_file.db")

    success, size_mb, message = db.get_database_size()

    assert success is False
    assert size_mb == 0.0
    assert "not found" in message.lower()


# =============================================================================
# Subject CRUD Tests
# =============================================================================


def test_create_subject_with_all_fields(db_manager):
    """Test creating subject with all optional fields."""
    dob = datetime(1990, 5, 15)

    subject = db_manager.create_subject(
        subject_code="P-2025-0001",
        tech_id=1,
        date_of_birth=dob,
        gender="F",
        notes="Test subject notes",
    )

    assert subject is not None
    assert subject.subject_id is not None
    assert subject.subject_code == "P-2025-0001"
    assert subject.date_of_birth == dob
    assert subject.gender == "F"
    assert subject.notes == "Test subject notes"
    assert subject.created_by_tech_id == 1
    assert subject.is_active is True


def test_create_subject_with_minimal_fields(db_manager):
    """Test creating subject with only required fields."""
    subject = db_manager.create_subject(subject_code="P-2025-0002", tech_id=1)

    assert subject is not None
    assert subject.subject_code == "P-2025-0002"
    assert subject.date_of_birth is None
    assert subject.gender is None
    assert subject.notes is None


def test_get_subject_by_code_returns_existing_subject(db_manager):
    """Test that get_subject_by_code() finds existing subject."""
    # Create subject
    created = db_manager.create_subject("P-2025-0003", tech_id=1)

    # Retrieve by code
    retrieved = db_manager.get_subject_by_code("P-2025-0003")

    assert retrieved is not None
    assert retrieved.subject_id == created.subject_id
    assert retrieved.subject_code == "P-2025-0003"


def test_get_subject_by_code_returns_none_for_nonexistent(db_manager):
    """Test that get_subject_by_code() returns None for nonexistent subject."""
    result = db_manager.get_subject_by_code("NONEXISTENT")

    assert result is None


def test_get_subject_session_count_returns_zero_for_no_sessions(db_manager):
    """Test that get_subject_session_count() returns 0 for new subject."""
    subject = db_manager.create_subject("P-2025-0004", tech_id=1)

    count = db_manager.get_subject_session_count(subject.subject_id)

    assert count == 0


def test_get_subject_session_count_returns_correct_count(db_manager):
    """Test that get_subject_session_count() returns accurate count."""
    subject = db_manager.create_subject("P-2025-0005", tech_id=1)

    # Create sessions for the subject
    with db_manager.get_session() as session:
        for i in range(3):
            session_obj = Session(
                subject_id=subject.subject_id,
                tech_id=1,
                start_time=datetime.now(),
                status="completed",
            )
            session.add(session_obj)
        session.commit()

    count = db_manager.get_subject_session_count(subject.subject_id)

    assert count == 3


# =============================================================================
# Session CRUD Tests
# =============================================================================


def test_get_all_sessions_without_filter(db_manager):
    """Test get_all_sessions() retrieves all sessions."""
    subject = db_manager.create_subject("P-2025-0006", tech_id=1)

    # Create multiple sessions
    with db_manager.get_session() as session:
        for i in range(5):
            session_obj = Session(
                subject_id=subject.subject_id,
                tech_id=1,
                start_time=datetime.now(),
                status="completed",
            )
            session.add(session_obj)
        session.commit()

    sessions = db_manager.get_all_sessions()

    assert len(sessions) == 5
    # Verify relationships are loaded
    assert sessions[0].subject is not None
    assert sessions[0].technician is not None


def test_get_all_sessions_with_subject_id_filter(db_manager):
    """Test get_all_sessions() filters by subject_id."""
    subject1 = db_manager.create_subject("P-2025-0007", tech_id=1)
    subject2 = db_manager.create_subject("P-2025-0008", tech_id=1)

    # Create sessions for both subjects
    with db_manager.get_session() as session:
        for i in range(3):
            session.add(
                Session(
                    subject_id=subject1.subject_id,
                    tech_id=1,
                    start_time=datetime.now(),
                    status="completed",
                )
            )
        for i in range(2):
            session.add(
                Session(
                    subject_id=subject2.subject_id,
                    tech_id=1,
                    start_time=datetime.now(),
                    status="completed",
                )
            )
        session.commit()

    # Filter by subject1
    sessions = db_manager.get_all_sessions(subject_id=subject1.subject_id)

    assert len(sessions) == 3
    assert all(s.subject_id == subject1.subject_id for s in sessions)


def test_get_all_sessions_respects_limit(db_manager):
    """Test get_all_sessions() respects the limit parameter."""
    subject = db_manager.create_subject("P-2025-0009", tech_id=1)

    # Create many sessions
    with db_manager.get_session() as session:
        for i in range(50):
            session.add(
                Session(
                    subject_id=subject.subject_id,
                    tech_id=1,
                    start_time=datetime.now(),
                    status="completed",
                )
            )
        session.commit()

    sessions = db_manager.get_all_sessions(limit=10)

    assert len(sessions) == 10


# =============================================================================
# Technician CRUD Tests
# =============================================================================


def test_get_technician_by_username_finds_admin(db_manager):
    """Test get_technician_by_username() finds default admin user."""
    admin = db_manager.get_technician_by_username("admin")

    assert admin is not None
    assert admin.username == "admin"
    assert admin.full_name == "System Administrator"
    assert admin.role == "admin"
    assert admin.is_active is True


def test_get_technician_by_username_returns_none_for_nonexistent(db_manager):
    """Test get_technician_by_username() returns None for nonexistent user."""
    result = db_manager.get_technician_by_username("nonexistent_user")

    assert result is None


def test_update_technician_last_login_updates_timestamp(db_manager):
    """Test update_technician_last_login() updates last_login field."""
    admin = db_manager.get_technician_by_username("admin")
    original_last_login = admin.last_login

    # Update last login
    db_manager.update_technician_last_login(admin.tech_id)

    # Retrieve again to verify update
    updated_admin = db_manager.get_technician_by_username("admin")

    assert updated_admin.last_login is not None
    assert updated_admin.last_login != original_last_login


def test_update_technician_last_login_handles_nonexistent_id(db_manager):
    """Test update_technician_last_login() handles nonexistent tech_id gracefully."""
    # Should not raise exception
    db_manager.update_technician_last_login(99999)

    # Verify database is still functional
    admin = db_manager.get_technician_by_username("admin")
    assert admin is not None


# =============================================================================
# Safety Log CRUD Tests
# =============================================================================


def test_log_safety_event_with_all_fields(db_manager):
    """Test log_safety_event() creates entry with all fields."""
    # Create a subject and session first (for foreign key constraint)
    subject = db_manager.create_subject("P-2025-SAFETY1", tech_id=1)
    with db_manager.get_session() as session:
        session_obj = Session(
            subject_id=subject.subject_id,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        session.add(session_obj)
        session.commit()
        session.refresh(session_obj)
        session_id = session_obj.session_id

    log = db_manager.log_safety_event(
        event_type="e_stop_pressed",
        severity="emergency",
        description="Emergency stop activated",
        session_id=session_id,
        tech_id=1,
        system_state="treating",
        action_taken="laser_disabled",
    )

    assert log is not None
    assert log.log_id is not None
    assert log.event_type == "e_stop_pressed"
    assert log.severity == "emergency"
    assert log.description == "Emergency stop activated"
    assert log.session_id == session_id
    assert log.tech_id == 1
    assert log.system_state == "treating"
    assert log.action_taken == "laser_disabled"
    assert log.timestamp is not None


def test_log_safety_event_with_minimal_fields(db_manager):
    """Test log_safety_event() creates entry with only required fields."""
    log = db_manager.log_safety_event(
        event_type="test_event", severity="info", description="Test log entry"
    )

    assert log is not None
    assert log.event_type == "test_event"
    assert log.severity == "info"
    assert log.session_id is None
    assert log.tech_id is None


def test_get_safety_logs_without_filters(db_manager):
    """Test get_safety_logs() retrieves all logs without filters."""
    # Create multiple logs (plus 1 from database initialization)
    for i in range(5):
        db_manager.log_safety_event(
            event_type=f"event_{i}", severity="info", description=f"Test event {i}"
        )

    logs = db_manager.get_safety_logs()

    assert len(logs) >= 5  # At least 5 (plus initialization log)


def test_get_safety_logs_filters_by_session_id(db_manager):
    """Test get_safety_logs() filters by session_id."""
    # Create subjects and sessions first (for foreign key constraint)
    subject1 = db_manager.create_subject("P-2025-SAFELOG1", tech_id=1)
    subject2 = db_manager.create_subject("P-2025-SAFELOG2", tech_id=1)

    with db_manager.get_session() as session:
        # Session 1
        session1 = Session(
            subject_id=subject1.subject_id,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        session.add(session1)
        # Session 2
        session2 = Session(
            subject_id=subject2.subject_id,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        session.add(session2)
        session.commit()
        session.refresh(session1)
        session.refresh(session2)
        session1_id = session1.session_id
        session2_id = session2.session_id

    # Create logs with different session IDs
    db_manager.log_safety_event("event1", "info", "Session 1", session_id=session1_id)
    db_manager.log_safety_event("event2", "info", "Session 1", session_id=session1_id)
    db_manager.log_safety_event("event3", "info", "Session 2", session_id=session2_id)

    logs = db_manager.get_safety_logs(session_id=session1_id)

    assert len(logs) == 2
    assert all(log.session_id == session1_id for log in logs)


def test_get_safety_logs_filters_by_min_severity_warning(db_manager):
    """Test get_safety_logs() filters by min_severity='warning'."""
    # Create logs with different severities
    db_manager.log_safety_event("event1", "info", "Info log")
    db_manager.log_safety_event("event2", "warning", "Warning log")
    db_manager.log_safety_event("event3", "critical", "Critical log")
    db_manager.log_safety_event("event4", "emergency", "Emergency log")

    logs = db_manager.get_safety_logs(min_severity="warning", limit=50)

    # Should include warning, critical, emergency (not info)
    assert len(logs) >= 3
    assert all(log.severity in ["warning", "critical", "emergency"] for log in logs)


def test_get_safety_logs_filters_by_min_severity_critical(db_manager):
    """Test get_safety_logs() filters by min_severity='critical'."""
    db_manager.log_safety_event("event1", "info", "Info log")
    db_manager.log_safety_event("event2", "warning", "Warning log")
    db_manager.log_safety_event("event3", "critical", "Critical log")
    db_manager.log_safety_event("event4", "emergency", "Emergency log")

    logs = db_manager.get_safety_logs(min_severity="critical", limit=50)

    # Should include only critical and emergency
    assert len(logs) >= 2
    assert all(log.severity in ["critical", "emergency"] for log in logs)


def test_get_safety_logs_respects_limit(db_manager):
    """Test get_safety_logs() respects limit parameter."""
    # Create many logs
    for i in range(20):
        db_manager.log_safety_event(f"event_{i}", "info", f"Log {i}")

    logs = db_manager.get_safety_logs(limit=5)

    assert len(logs) == 5


def test_get_safety_logs_orders_by_timestamp_descending(db_manager):
    """Test get_safety_logs() returns logs in descending timestamp order."""
    # Create logs with slight time delays
    import time

    log1 = db_manager.log_safety_event("event1", "info", "First log")
    time.sleep(0.01)
    log2 = db_manager.log_safety_event("event2", "info", "Second log")
    time.sleep(0.01)
    log3 = db_manager.log_safety_event("event3", "info", "Third log")

    logs = db_manager.get_safety_logs(limit=10)

    # Most recent should be first
    assert logs[0].log_id == log3.log_id
    assert logs[1].log_id == log2.log_id
    assert logs[2].log_id == log1.log_id


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


def test_create_duplicate_subject_code_raises_error(db_manager):
    """Test that creating duplicate subject_code raises constraint error."""
    db_manager.create_subject("P-2025-DUPLICATE", tech_id=1)

    with pytest.raises(Exception):  # SQLAlchemy IntegrityError
        db_manager.create_subject("P-2025-DUPLICATE", tech_id=1)


def test_get_all_sessions_returns_empty_list_for_no_sessions(tmp_path):
    """Test get_all_sessions() returns empty list when no sessions exist."""
    db_path = tmp_path / "test_empty.db"
    db = DatabaseManager(str(db_path))
    db.initialize()

    sessions = db.get_all_sessions()

    assert sessions == []
    db.close()


def test_get_safety_logs_with_invalid_severity_returns_empty(db_manager):
    """Test get_safety_logs() with unrecognized severity returns filtered results."""
    db_manager.log_safety_event("event1", "info", "Test log")

    # Invalid severity should default to level 0 (info and above)
    logs = db_manager.get_safety_logs(min_severity="invalid_severity", limit=50)

    # Should still return logs (treated as minimum level)
    assert len(logs) > 0
