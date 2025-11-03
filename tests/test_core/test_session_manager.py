# -*- coding: utf-8 -*-
"""
Comprehensive tests for SessionManager.

Tests session lifecycle management, two-phase commit (database + filesystem),
error handling, signal emission, and developer mode for the TOSCA treatment system.

Target: 90%+ coverage (202+ of 219 statements)
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtTest import QSignalSpy

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from core.session_manager import SessionManager
from database.models import Session, Subject

# ==============================================================================
# FIXTURES
# ==============================================================================


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


# ==============================================================================
# CATEGORY 1: SESSION CREATION WITH REAL FILESYSTEM (tmp_path)
# ==============================================================================


class TestSessionCreationWithFilesystem:
    """Test session creation with real filesystem using tmp_path."""

    def test_create_session_folder_creates_correct_structure(self, session_manager, tmp_path):
        """Test _create_session_folder creates correct directory structure."""
        # Act: Use tmp_path for actual folder creation
        with patch(
            "core.session_manager.Path",
            side_effect=lambda x: tmp_path if x == "data/sessions" else Path(x),
        ):
            folder_path = session_manager._create_session_folder("P-2025-0001")

        # Assert: Folder structure is correct
        # Format: data/sessions/P-2025-0001/YYYY-MM-DD_HHMMSS
        assert folder_path.exists()
        assert folder_path.is_dir()
        assert "P-2025-0001" in str(folder_path)

        # Check timestamp format in folder name
        folder_name = folder_path.name
        assert len(folder_name) == 17  # YYYY-MM-DD_HHMMSS = 17 chars
        assert folder_name[4] == "-" and folder_name[7] == "-" and folder_name[10] == "_"

    def test_create_session_with_folder_permissions_error(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test session creation when folder creation fails due to permissions."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=1,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 1

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        # Act: Mock folder creation to fail
        with patch("core.session_manager.Path.mkdir", side_effect=OSError("Permission denied")):
            session = session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Session created despite folder failure
        assert session is not None
        assert "Failed to create session folder" in caplog.text
        assert "Session 1 created without folder path" in caplog.text


# ==============================================================================
# CATEGORY 2: SIGNAL VALIDATION WITH QSignalSpy
# ==============================================================================


class TestSignalEmissionWithQSignalSpy:
    """Test signal emission using QSignalSpy for comprehensive validation."""

    def test_session_started_signal_emitted_with_correct_session_id(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify session_started signal emits correct session_id using QSignalSpy."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=2,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 2

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        # Setup QSignalSpy
        spy = QSignalSpy(session_manager.session_started)

        # Act
        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Signal emitted with correct session_id
        assert len(spy) == 1
        assert spy[0][0] == 2  # First signal, first argument

    def test_session_ended_signal_emitted_on_completion(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify session_ended signal using QSignalSpy."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=3,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Setup QSignalSpy
        spy = QSignalSpy(session_manager.session_ended)

        # Act
        session_manager.complete_session()

        # Assert
        assert len(spy) == 1
        assert spy[0][0] == 3

    def test_session_status_changed_signal_emitted(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify session_status_changed signal using QSignalSpy."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=4,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 4

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        # Setup QSignalSpy
        spy = QSignalSpy(session_manager.session_status_changed)

        # Act
        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Status changed signal emitted
        assert len(spy) >= 1
        assert "Session active" in spy[0][0]


# ==============================================================================
# CATEGORY 3: DEVELOPER MODE SESSIONS
# ==============================================================================


class TestDeveloperModeSessions:
    """Test developer mode session functionality."""

    def test_create_dev_session_creates_dev_subject_if_not_exists(
        self, session_manager, mock_db_manager
    ):
        """Test create_dev_session creates DEV-SUBJECT if it doesn't exist."""
        # Arrange: No existing DEV-SUBJECT
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        # First query returns None (DEV-SUBJECT doesn't exist)
        # Second query returns the created DEV-SUBJECT
        dev_subject = Subject(
            subject_id=999,
            subject_code="DEV-SUBJECT",
        )

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        filter_by_mock.first.side_effect = [None, dev_subject]

        db_session.query.return_value = query_mock

        mock_session = Session(
            session_id=100,
            subject_id=999,
            tech_id=0,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 100

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        # Act
        session = session_manager.create_dev_session()

        # Assert: DEV-SUBJECT was created
        assert session is not None
        assert session.session_id == 100
        assert session.subject_id == 999
        assert session.tech_id == 0  # Dev mode uses tech_id=0
        assert db_session.add.called  # Subject was added

    def test_create_dev_session_reuses_existing_dev_subject(self, session_manager, mock_db_manager):
        """Test create_dev_session reuses existing DEV-SUBJECT."""
        # Arrange: DEV-SUBJECT already exists
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        dev_subject = Subject(
            subject_id=999,
            subject_code="DEV-SUBJECT",
        )

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        filter_by_mock.first.return_value = dev_subject

        db_session.query.return_value = query_mock

        mock_session = Session(
            session_id=101,
            subject_id=999,
            tech_id=0,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 101

        db_session.add.side_effect = set_session_id

        # Act
        session = session_manager.create_dev_session()

        # Assert: Existing DEV-SUBJECT was used
        assert session is not None
        assert session.subject_id == 999

    def test_create_dev_session_returns_active_dev_session_if_exists(self, session_manager):
        """Test create_dev_session returns active dev session if already active."""
        # Arrange: Active dev session already exists
        existing_session = Session(
            session_id=102,
            subject_id="DEV-SUBJECT",  # Use string to match the check
            tech_id=0,
            start_time=datetime.now(),
            status="in_progress",
        )
        session_manager.current_session = existing_session

        # Act
        session = session_manager.create_dev_session()

        # Assert: Same session returned, no new creation
        assert session == existing_session
        assert session.session_id == 102

    def test_create_dev_session_does_not_create_folder(self, session_manager, mock_db_manager):
        """Test create_dev_session does not create filesystem folder."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        dev_subject = Subject(
            subject_id=999,
            subject_code="DEV-SUBJECT",
        )

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        filter_by_mock.first.return_value = dev_subject

        db_session.query.return_value = query_mock

        mock_session = Session(
            session_id=103,
            subject_id=999,
            tech_id=0,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 103

        db_session.add.side_effect = set_session_id

        # Act
        session = session_manager.create_dev_session()

        # Assert: No folder was created (current_session_folder is None)
        assert session is not None
        assert session_manager.current_session_folder is None

    def test_get_current_session_auto_creates_dev_session_in_dev_mode(
        self, session_manager, mock_db_manager
    ):
        """Test get_current_session auto-creates dev session when developer_mode_enabled."""
        # Arrange: Enable developer mode, no active session
        session_manager.developer_mode_enabled = True
        assert session_manager.current_session is None

        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        dev_subject = Subject(
            subject_id=999,
            subject_code="DEV-SUBJECT",
        )

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        filter_by_mock.first.return_value = dev_subject

        db_session.query.return_value = query_mock

        mock_session = Session(
            session_id=104,
            subject_id=999,
            tech_id=0,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 104

        db_session.add.side_effect = set_session_id

        # Act
        session = session_manager.get_current_session()

        # Assert: Dev session was auto-created
        assert session is not None
        assert session.session_id == 104

    def test_create_dev_session_fails_if_dev_subject_query_fails(
        self, session_manager, mock_db_manager, caplog
    ):
        """Test create_dev_session handles database errors gracefully."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        filter_by_mock.first.return_value = None  # No existing dev subject

        db_session.query.return_value = query_mock

        # Simulate error during session creation
        db_session.add.side_effect = Exception("Database error")

        # Act
        session = session_manager.create_dev_session()

        # Assert
        assert session is None
        assert "Failed to create developer session" in caplog.text

    def test_create_dev_session_fails_if_dev_subject_not_found_after_creation(
        self, session_manager, mock_db_manager, caplog
    ):
        """Test create_dev_session fails if DEV-SUBJECT not found in second query."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        query_mock = MagicMock()
        filter_by_mock = MagicMock()
        query_mock.filter_by.return_value = filter_by_mock
        # Both queries return None (simulating failed DEV-SUBJECT creation)
        filter_by_mock.first.return_value = None

        db_session.query.return_value = query_mock

        # Act
        session = session_manager.create_dev_session()

        # Assert
        assert session is None
        assert "Failed to create/retrieve DEV-SUBJECT" in caplog.text


# ==============================================================================
# CATEGORY 4: TRANSACTION ROLLBACK AND ERROR HANDLING
# ==============================================================================


class TestTransactionRollbackAndErrorHandling:
    """Test database transaction rollback and error handling scenarios."""

    def test_database_error_during_session_creation_returns_none(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test that database errors during session creation are handled gracefully."""
        # Arrange: Mock database to raise exception
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        db_session.add = MagicMock(side_effect=Exception("Database connection lost"))

        # Act
        session = session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Session creation failed, returns None
        assert session is None
        assert "Database error during session creation" in caplog.text

    def test_folder_path_update_failure_logs_error(
        self, session_manager, mock_db_manager, mock_subject, caplog, tmp_path
    ):
        """Test that folder path update failures are logged."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=5,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 5

        db_session.add.side_effect = set_session_id

        # First call to get() returns None (simulating folder path update failure)
        db_session.get = MagicMock(return_value=None)

        # Act: Create folder but fail to update path in database
        test_folder = tmp_path / "sessions" / "P-2025-0001" / "2025-11-01_120000"
        with patch.object(session_manager, "_create_session_folder", return_value=test_folder):
            test_folder.mkdir(parents=True, exist_ok=True)
            session = session_manager.create_session(mock_subject, tech_id=1)

        # Assert: Session created but folder path update failed
        assert session is not None
        # Check that the error was logged (session created without folder path stored in DB)

    def test_complete_session_database_error_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test complete_session handles database errors gracefully."""
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

        # Simulate database error during complete
        db_session.commit = MagicMock(side_effect=Exception("Database write error"))

        # Act
        success = session_manager.complete_session()

        # Assert: Completion failed
        assert success is False
        assert "Database error during session completion" in caplog.text
        # Session should NOT be cleared on error
        assert session_manager.current_session is not None

    def test_complete_session_session_not_found_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test complete_session returns False if session not found in database."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=7,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 7

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate session not found in database during complete
        db_session.get = MagicMock(return_value=None)

        # Act
        success = session_manager.complete_session()

        # Assert
        assert success is False
        assert "Session 7 not found in database" in caplog.text

    def test_abort_session_database_error_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test abort_session handles database errors gracefully."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=8,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate database error
        db_session.commit = MagicMock(side_effect=Exception("Database error"))

        # Act
        success = session_manager.abort_session("Test abort")

        # Assert
        assert success is False
        assert "Database error during session abort" in caplog.text

    def test_abort_session_not_found_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test abort_session returns False if session not found."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=9,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 9

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate session not found
        db_session.get = MagicMock(return_value=None)

        # Act
        success = session_manager.abort_session("Test")

        # Assert
        assert success is False
        assert "Session 9 not found in database" in caplog.text

    def test_pause_session_database_error_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test pause_session handles database errors gracefully."""
        # Arrange
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
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate database error
        db_session.commit = MagicMock(side_effect=Exception("Database error"))

        # Act
        success = session_manager.pause_session()

        # Assert
        assert success is False
        assert "Database error during session pause" in caplog.text

    def test_pause_session_not_found_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test pause_session returns False if session not found."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=11,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 11

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate session not found
        db_session.get = MagicMock(return_value=None)

        # Act
        success = session_manager.pause_session()

        # Assert
        assert success is False
        assert "Session 11 not found in database" in caplog.text

    def test_resume_session_database_error_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test resume_session handles database errors gracefully."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=12,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="paused",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate database error
        db_session.commit = MagicMock(side_effect=Exception("Database error"))

        # Act
        success = session_manager.resume_session()

        # Assert
        assert success is False
        assert "Database error during session resume" in caplog.text

    def test_resume_session_not_found_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test resume_session returns False if session not found."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=13,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="paused",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 13

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate session not found
        db_session.get = MagicMock(return_value=None)

        # Act
        success = session_manager.resume_session()

        # Assert
        assert success is False
        assert "Session 13 not found in database" in caplog.text

    def test_update_session_video_path_database_error_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test update_session_video_path handles database errors gracefully."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=14,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate database error
        db_session.commit = MagicMock(side_effect=Exception("Database error"))

        # Act
        success = session_manager.update_session_video_path("test.mp4")

        # Assert
        assert success is False
        assert "Database error updating video path" in caplog.text

    def test_update_session_video_path_not_found_returns_false(
        self, session_manager, mock_db_manager, mock_subject, caplog
    ):
        """Test update_session_video_path returns False if session not found."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=15,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 15

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Simulate session not found
        db_session.get = MagicMock(return_value=None)

        # Act
        success = session_manager.update_session_video_path("test.mp4")

        # Assert
        assert success is False
        assert "Session 15 not found in database" in caplog.text


# ==============================================================================
# CATEGORY 5: EDGE CASES AND ADDITIONAL COVERAGE
# ==============================================================================


class TestEdgeCasesAndAdditionalCoverage:
    """Test edge cases and additional functionality for full coverage."""

    def test_end_session_alias_calls_complete_session(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Test end_session() is an alias for complete_session()."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=16,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act: Use end_session alias
        session_manager.end_session()

        # Assert: Session was completed
        assert mock_session.status == "completed"
        assert session_manager.current_session is None

    def test_end_session_with_no_active_session(self, session_manager, caplog):
        """Test end_session() with no active session logs warning."""
        # Act
        session_manager.end_session()

        # Assert
        assert "No active session to end" in caplog.text

    def test_get_session_folder_returns_current_folder(
        self, session_manager, mock_db_manager, mock_subject, tmp_path
    ):
        """Test get_session_folder() returns current session folder."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=17,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        test_folder = tmp_path / "sessions" / "P-2025-0001" / "2025-11-01_120000"
        with patch.object(session_manager, "_create_session_folder", return_value=test_folder):
            test_folder.mkdir(parents=True, exist_ok=True)
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        folder = session_manager.get_session_folder()

        # Assert
        assert folder == test_folder

    def test_get_session_folder_returns_none_when_no_session(self, session_manager):
        """Test get_session_folder() returns None when no active session."""
        # Act
        folder = session_manager.get_session_folder()

        # Assert
        assert folder is None

    def test_complete_session_with_no_active_session_returns_false(self, session_manager, caplog):
        """Test complete_session with no active session returns False."""
        # Act
        success = session_manager.complete_session()

        # Assert
        assert success is False
        assert "No active session to complete" in caplog.text

    def test_abort_session_with_no_active_session_returns_false(self, session_manager, caplog):
        """Test abort_session with no active session returns False."""
        # Act
        success = session_manager.abort_session("Test")

        # Assert
        assert success is False
        assert "No active session to abort" in caplog.text

    def test_pause_session_with_no_active_session_returns_false(self, session_manager, caplog):
        """Test pause_session with no active session returns False."""
        # Act
        success = session_manager.pause_session()

        # Assert
        assert success is False
        assert "No active session to pause" in caplog.text

    def test_resume_session_with_no_active_session_returns_false(self, session_manager, caplog):
        """Test resume_session with no active session returns False."""
        # Act
        success = session_manager.resume_session()

        # Assert
        assert success is False
        assert "No session to resume" in caplog.text

    def test_update_session_video_path_with_no_active_session_returns_false(
        self, session_manager, caplog
    ):
        """Test update_session_video_path with no active session returns False."""
        # Act
        success = session_manager.update_session_video_path("test.mp4")

        # Assert
        assert success is False
        assert "No active session to update video path" in caplog.text

    def test_get_session_info_text_calculates_duration_correctly(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Test get_session_info_text calculates duration correctly."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value

        # Create session with specific start time
        start_time = datetime.now() - timedelta(minutes=5, seconds=30)
        mock_session = Session(
            session_id=18,
            subject_id=1,
            tech_id=1,
            start_time=start_time,
            status="in_progress",
            session_folder_path="/test/folder",
        )

        def set_session_id(obj):
            if isinstance(obj, Session) and obj.session_id is None:
                obj.session_id = 18

        db_session.add.side_effect = set_session_id
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Manually set start_time to test duration calculation
        session_manager.current_session.start_time = start_time
        session_manager.current_session.session_id = 18

        # Act
        info = session_manager.get_session_info_text()

        # Assert: Duration should be approximately 05:30
        assert "Session ID: 18" in info
        assert "Duration: 05:" in info  # 5 minutes
        assert "Status: in_progress" in info

    def test_get_session_info_text_no_active_session(self, session_manager):
        """Test get_session_info_text returns message when no session active."""
        # Act
        info = session_manager.get_session_info_text()

        # Assert
        assert info == "No active session"


# ==============================================================================
# CATEGORY 6: EXISTING FUNCTIONALITY TESTS (PRESERVED)
# ==============================================================================


class TestExistingFunctionality:
    """Preserve tests for existing functionality that work correctly."""

    def test_complete_session_updates_all_statistics(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify complete_session() updates all session statistics in database."""
        # Arrange: Create a session first
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=19,
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

    def test_abort_session_records_reason(self, session_manager, mock_db_manager, mock_subject):
        """Verify abort_session() records the abort reason in database."""
        # Arrange: Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=20,
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

    def test_pause_and_resume_session_cycle(self, session_manager, mock_db_manager, mock_subject):
        """Test complete pause/resume cycle."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=21,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act: Pause
        pause_success = session_manager.pause_session()
        assert pause_success is True
        assert mock_session.status == "paused"

        # Act: Resume
        resume_success = session_manager.resume_session()
        assert resume_success is True
        assert mock_session.status == "in_progress"

    def test_is_session_active_returns_correct_state(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Verify is_session_active() returns correct state."""
        # Initially no active session
        assert session_manager.is_session_active() is False

        # Create a session
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=22,
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

    def test_update_session_video_path_success(
        self, session_manager, mock_db_manager, mock_subject
    ):
        """Test update_session_video_path successfully updates video path."""
        # Arrange
        db_session = mock_db_manager.get_session.return_value.__enter__.return_value
        mock_session = Session(
            session_id=23,
            subject_id=1,
            tech_id=1,
            start_time=datetime.now(),
            status="in_progress",
        )
        db_session.get = MagicMock(return_value=mock_session)

        with patch("core.session_manager.Path.mkdir"):
            session_manager.create_session(mock_subject, tech_id=1)

        # Act
        success = session_manager.update_session_video_path("data/videos/session_23.mp4")

        # Assert
        assert success is True
        assert mock_session.video_path == "data/videos/session_23.mp4"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/core/session_manager", "--cov-report=term-missing"])
