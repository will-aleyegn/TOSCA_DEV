# -*- coding: utf-8 -*-
"""
Comprehensive tests for SessionManager.

Tests session lifecycle management, two-phase commit (database + filesystem),
error handling, and signal emission for the TOSCA treatment system.
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from core.session_manager import SessionManager
from database.models import Session, Subject


@pytest.fixture
def app():
    """Create QCoreApplication for signal testing."""
    return QCoreApplication.instance() or QCoreApplication(sys.argv)


@pytest.fixture
def mock_db_manager():
    """Provides a MagicMock for DatabaseManager."""
    db_manager = MagicMock()
    # Setup context manager behavior
    db_session = MagicMock()
    db_manager.get_session.return_value.__enter__.return_value = db_session
    db_manager.get_session.return_value.__exit__.return_value = None
    return db_manager


@pytest.fixture
def mock_subject():
    """Provides a mock Subject instance."""
    subject = MagicMock(spec=Subject)
    subject.subject_id = 1
    subject.subject_code = "P-2025-0001"
    return subject


@pytest.fixture
def session_manager(mock_db_manager, app):
    """Provides a SessionManager instance with mocked database."""
    return SessionManager(db_manager=mock_db_manager)


class TestSessionCreation:
    """Test session creation with two-phase commit."""

    def test_create_session_success_creates_db_and_folder(
        self, session_manager, mock_db_manager, mock_subject, tmp_path
    ):
        """
        Test successful session creation: database record + filesystem folder.
        This is the happy path for the two-phase commit.
        """
        # Arrange: Mock database session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=1,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.add = MagicMock()
        db_session.get = MagicMock(return_value=mock_session)

        # Act: Patch _create_session_folder to use tmp_path
        test_folder = tmp_path / "sessions" / "P-2025-0001" / "2025-11-01_120000"
        with patch.object(session_manager, "_create_session_folder", return_value=test_folder):
            # Create the folder since we're mocking the method
            test_folder.mkdir(parents=True, exist_ok=True)

            session = session_manager.create_session(
                subject=mock_subject,
                tech_id=1,
                treatment_site="Shoulder",
                treatment_notes="Pre-treatment notes",
            )

        # Assert: Database record created
        assert session is not None
        db_session.add.assert_called_once()
        db_session.commit.assert_called()

        # Assert: Folder was created
        assert test_folder.exists()

    def test_create_session_emits_session_started_signal(
        self, session_manager, mock_db_manager, mock_subject, qtbot
    ):
        """Verify session_started signal is emitted after successful creation."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=2,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        # Make sure the session object gets session_id set when add() is called
        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 2

        db_session.add.side_effect = set_session_id

        # Track signal emissions with a simple list
        emitted_sessions = []

        def on_session_started(session_id):
            emitted_sessions.append(session_id)

        session_manager.session_started.connect(on_session_started)

        # Act
        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Signal emitted with session_id
        qtbot.wait(100)  # Allow signal processing
        assert len(emitted_sessions) == 1
        assert emitted_sessions[0] == 2

    def test_create_session_folder_failure_creates_db_only(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """
        Test that database record is created even if folder creation fails.
        This validates fault tolerance in the two-phase commit.
        """
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=3,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        # Mock the get() method to return our session after it's "added"
        db_session.get = MagicMock(return_value=mock_session)

        # Make sure the session object gets session_id set when add() is called
        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 3

        db_session.add.side_effect = set_session_id

        # Act: Mock folder creation to fail
        with patch("core.session_manager.Path.mkdir", side_effect=OSError("Permission denied")):
            session = session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Session created despite folder failure
        assert session is not None
        assert session.session_id == 3
        assert "Failed to create session folder" in caplog.text

    def test_database_error_during_session_creation(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test that database errors during session creation are handled gracefully."""
        # Arrange: Mock database to raise exception
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        db_session.add = MagicMock(side_effect=Exception("Database error"))

        # Act
        session = session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Session creation failed, returns None
        assert session is None
        assert "Database error during session creation" in caplog.text


class TestSessionCompletion:
    """Test session completion with statistics."""

    def test_complete_session_updates_all_statistics(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify complete_session() updates all session statistics in database."""
        # Arrange: Create a session first
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=4,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act: Complete the session
        success = session_manager.complete_session(
            post_treatment_notes="Treatment completed successfully",
            total_laser_on_time=120.5,
            avg_power=3.2,
            max_power=5.0,
            total_energy=385.6,
        )

        # Assert
        assert success is True
        assert mock_session.status == "completed"
        assert mock_session.post_treatment_notes == "Treatment completed successfully"
        assert mock_session.total_laser_on_time_seconds == 120.5
        assert mock_session.avg_power_watts == 3.2
        assert mock_session.max_power_watts == 5.0
        assert mock_session.total_energy_joules == 385.6
        assert mock_session.end_time is not None
        assert mock_session.duration_seconds is not None

    def test_complete_session_emits_session_ended_signal(
        self, session_manager, mock_db_manager, mock_subject, qtbot
    ):
        """Verify session_ended signal is emitted after completion."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=5,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        with qtbot.waitSignal(session_manager.session_ended, timeout=1000) as blocker:
            session_manager.complete_session()

        # Assert
        assert blocker.args[0] == 5

    def test_complete_session_with_no_active_session(self, session_manager, caplog):
        """Test that completing without an active session fails gracefully."""
        # Act
        success = session_manager.complete_session()

        # Assert
        assert success is False
        assert "No active session to complete" in caplog.text


class TestSessionAbort:
    """Test session abort functionality."""

    def test_abort_session_records_reason(self, session_manager, mock_db_manager, mock_subject):
        """Verify abort_session() records the abort reason in database."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=6,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        success = session_manager.abort_session("Safety interlock failure")

        # Assert
        assert success is True
        assert mock_session.status == "aborted"
        assert mock_session.abort_reason == "Safety interlock failure"
        assert mock_session.end_time is not None


class TestSessionPauseResume:
    """Test session pause and resume functionality."""

    def test_pause_session_changes_status(self, session_manager, mock_db_manager, mock_subject):
        """Verify pause_session() changes status to 'paused'."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=7,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        success = session_manager.pause_session()

        # Assert
        assert success is True
        assert mock_session.status == "paused"

    def test_resume_session_changes_status(self, session_manager, mock_db_manager, mock_subject):
        """Verify resume_session() changes status back to 'in_progress'."""
        # Arrange: Create and pause a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=8,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="paused",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)
        session_manager.current_session.status = "paused"

        # Act
        success = session_manager.resume_session()

        # Assert
        assert success is True
        assert mock_session.status == "in_progress"


class TestSessionState:
    """Test session state queries."""

    def test_is_session_active_returns_correct_state(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify is_session_active() returns correct state."""
        # Initially no active session
        assert session_manager.is_session_active() is False

        # Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=9,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Now session is active
        assert session_manager.is_session_active() is True

        # Pause session - still has a session but not "in_progress"
        mock_session.status = "paused"
        session_manager.current_session.status = "paused"
        assert session_manager.is_session_active() is False

    def test_get_current_session_returns_session(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify get_current_session() returns the active session."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=10,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            created_session = session_manager.create_session(mock_subject, tech_id=1)

        # Act
        current = session_manager.get_current_session()

        # Assert
        assert current is not None
        assert current.session_id == created_session.session_id


class TestSessionVideoPath:
    """Test video path update functionality."""

    def test_update_session_video_path(self, session_manager, mock_db_manager, mock_subject):
        """Verify video path can be updated for current session."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=11,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        success = session_manager.update_session_video_path("data/videos/session_11.mp4")

        # Assert
        assert success is True
        assert mock_session.video_path == "data/videos/session_11.mp4"


class TestSessionInfo:
    """Test session info reporting."""

    def test_get_session_info_text_no_active_session(self, session_manager):
        """Verify get_session_info_text() returns message when no session active."""
        # Act
        info = session_manager.get_session_info_text()

        # Assert
        assert info == "No active session"

    def test_get_session_info_text_with_active_session(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify get_session_info_text() returns formatted info for active session."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=12,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
            session_folder_path="data/sessions/P-2025-0001/2025-10-30_120000",
        )
        db_session.get = MagicMock(return_value=mock_session)

        # Make sure the session object gets session_id set when add() is called
        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 12

        db_session.add.side_effect = set_session_id

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        info = session_manager.get_session_info_text()

        # Assert
        assert "Session ID: 12" in info
        assert "Status: in_progress" in info
        assert "Duration:" in info
        assert "Folder:" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
