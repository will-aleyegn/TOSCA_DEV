# -*- coding: utf-8 -*-
"""
Comprehensive tests for EventLogger.

Tests dual persistence (JSONL + database), fault tolerance, immutability,
and signal emission for the TOSCA medical device audit trail.

CRITICAL: EventLogger must maintain audit trail integrity even when one
persistence layer fails (medical device compliance requirement).
"""

import json
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

from core.event_logger import EventLogger, EventSeverity, EventType


@pytest.fixture
def app():
    """Create QCoreApplication for signal testing."""
    return QCoreApplication.instance() or QCoreApplication(sys.argv)


@pytest.fixture
def mock_db_manager():
    """Provides a MagicMock for the DatabaseManager."""
    return MagicMock()


@pytest.fixture
def tmp_log_file(tmp_path: Path) -> Path:
    """Provides a temporary path for the JSONL log file."""
    return tmp_path / "logs" / "events.jsonl"


@pytest.fixture
def event_logger(mock_db_manager: MagicMock, tmp_log_file: Path) -> EventLogger:
    """Provides an EventLogger instance with mocked database."""
    return EventLogger(db_manager=mock_db_manager, log_file=tmp_log_file)


class TestEventLoggerInitialization:
    """Test EventLogger initialization."""

    def test_initialization_creates_log_directory(
        self, mock_db_manager: MagicMock, tmp_log_file: Path
    ):
        """
        Verify that EventLogger constructor creates the necessary log directory.
        This is critical for ensuring file logging can succeed.
        """
        # Arrange: Ensure the parent directory does not exist
        assert not tmp_log_file.parent.exists()

        # Act
        EventLogger(db_manager=mock_db_manager, log_file=tmp_log_file)

        # Assert
        assert tmp_log_file.parent.exists()
        assert tmp_log_file.parent.is_dir()

    def test_initialization_with_default_log_path(self, mock_db_manager):
        """Test that EventLogger uses default path if none provided."""
        # Act
        logger = EventLogger(db_manager=mock_db_manager)

        # Assert
        assert logger.log_file == Path("data/logs/events.jsonl")


class TestDualPersistence:
    """Test dual persistence to JSONL file and database."""

    def test_log_event_happy_path(
        self, event_logger: EventLogger, mock_db_manager: MagicMock, tmp_log_file: Path, qtbot
    ):
        """
        Test the ideal scenario: logging an event successfully to database, file, and emitting signal.
        This confirms core functionality under normal operating conditions.
        """
        # Arrange
        event_type = EventType.SYSTEM_STARTUP
        severity = EventSeverity.INFO
        description = "System has started successfully."
        details = {"version": "1.0.0"}

        event_logger.set_session(session_id=101, tech_id=1)

        # Act
        with qtbot.waitSignal(event_logger.event_logged, timeout=1000) as blocker:
            event_logger.log_event(
                event_type=event_type,
                description=description,
                severity=severity,
                details=details,
            )

        # Assert
        # 1. Database was called correctly
        mock_db_manager.log_safety_event.assert_called_once_with(
            event_type=event_type.value,
            severity=severity.value,
            description=description,
            session_id=101,
            tech_id=1,
            system_state=None,
            action_taken=None,
        )

        # 2. File was written correctly
        assert tmp_log_file.exists()
        log_content = tmp_log_file.read_text()
        log_data = json.loads(log_content)

        assert log_data["event_type"] == event_type.value
        assert log_data["severity"] == severity.value
        assert log_data["description"] == description
        assert log_data["session_id"] == 101
        assert log_data["tech_id"] == 1
        assert log_data["details"] == details
        assert "timestamp" in log_data

        # 3. Signal was emitted with correct payload
        assert blocker.args == [event_type.value, severity.value, description]

    def test_log_event_writes_to_jsonl_file(self, event_logger: EventLogger, tmp_log_file: Path):
        """Verify events are written to JSONL file in correct format."""
        # Act: Log multiple events
        event_logger.log_event(EventType.SYSTEM_STARTUP, "Event 1")
        event_logger.log_event(EventType.HARDWARE_CAMERA_CONNECT, "Event 2")

        # Assert: File contains two lines
        lines = tmp_log_file.read_text().strip().split("\n")
        assert len(lines) == 2

        # Each line is valid JSON
        event1 = json.loads(lines[0])
        event2 = json.loads(lines[1])
        assert event1["description"] == "Event 1"
        assert event2["description"] == "Event 2"

    def test_jsonl_file_is_append_only(self, event_logger: EventLogger, tmp_log_file: Path):
        """
        Verify JSONL file is append-only (immutability requirement for medical device audit trail).
        """
        # Act: Log events sequentially
        event_logger.log_event(EventType.SYSTEM_STARTUP, "First event")
        first_content = tmp_log_file.read_text()

        event_logger.log_event(EventType.SYSTEM_SHUTDOWN, "Second event")
        second_content = tmp_log_file.read_text()

        # Assert: Second content includes first content (append-only)
        assert first_content in second_content
        assert len(second_content) > len(first_content)

        # Parse both events
        lines = second_content.strip().split("\n")
        assert len(lines) == 2


class TestFaultTolerance:
    """Test fault tolerance - critical for medical device compliance."""

    def test_database_failure_still_logs_to_file(
        self, event_logger: EventLogger, mock_db_manager: MagicMock, tmp_log_file: Path, qtbot
    ):
        """
        CRITICAL: If database fails, logger MUST NOT crash and MUST still log
        to backup file and emit signal for UI.
        """
        # Arrange
        mock_db_manager.log_safety_event.side_effect = Exception("Database connection lost")
        event_type = EventType.SAFETY_EMERGENCY_STOP
        severity = EventSeverity.EMERGENCY
        description = "E-stop pressed"

        # Act
        with qtbot.waitSignal(event_logger.event_logged, timeout=1000) as blocker:
            # This call should not raise an exception
            event_logger.log_event(event_type, description, severity)

        # Assert
        # 1. Database call was attempted
        mock_db_manager.log_safety_event.assert_called_once()

        # 2. File logging still succeeded
        assert tmp_log_file.exists()
        log_data = json.loads(tmp_log_file.read_text())
        assert log_data["event_type"] == event_type.value
        assert log_data["description"] == description

        # 3. Signal was still emitted
        assert blocker.args == [event_type.value, severity.value, description]

    @patch("builtins.open")
    def test_file_io_failure_still_logs_to_database(
        self, mock_open, event_logger: EventLogger, mock_db_manager: MagicMock, qtbot
    ):
        """
        CRITICAL: If filesystem is read-only or full, logger MUST NOT crash
        and MUST still log to database and emit signal.
        """
        # Arrange
        mock_open.side_effect = IOError("Permission denied")
        event_type = EventType.HARDWARE_ERROR
        severity = EventSeverity.CRITICAL
        description = "Laser communication failed"

        # Act
        with qtbot.waitSignal(event_logger.event_logged, timeout=1000) as blocker:
            # This call should not raise an exception
            event_logger.log_event(event_type, description, severity)

        # Assert
        # 1. Database logging still succeeded
        mock_db_manager.log_safety_event.assert_called_once_with(
            event_type=event_type.value,
            severity=severity.value,
            description=description,
            session_id=None,
            tech_id=None,
            system_state=None,
            action_taken=None,
        )

        # 2. Signal was still emitted
        assert blocker.args == [event_type.value, severity.value, description]

    def test_log_event_handles_non_serializable_details(
        self, event_logger: EventLogger, mock_db_manager: MagicMock, caplog
    ):
        """
        Test that non-JSON-serializable data in 'details' doesn't crash the logger.
        File logging exception is caught, but database logging continues.
        """
        # Arrange
        # datetime objects are not directly serializable by default json.dumps
        bad_details = {"time": datetime.now()}

        # Act
        event_logger.log_event(
            event_type=EventType.SYSTEM_ERROR, description="Bad details", details=bad_details
        )

        # Assert
        # 1. Database call still succeeded (it doesn't get the 'details' dict directly)
        mock_db_manager.log_safety_event.assert_called_once()

        # 2. An error was logged about the file write failure
        assert "Failed to log event to file" in caplog.text


class TestSessionContext:
    """Test session context management."""

    def test_set_session_includes_session_id_in_events(
        self, event_logger: EventLogger, tmp_log_file: Path
    ):
        """Verify that session_id and tech_id are included after set_session()."""
        # Arrange
        event_logger.set_session(session_id=202, tech_id=2)

        # Act
        event_logger.log_event(EventType.TREATMENT_SESSION_START, "Session started")

        # Assert
        log_data = json.loads(tmp_log_file.read_text())
        assert log_data["session_id"] == 202
        assert log_data["tech_id"] == 2

    def test_clear_session_removes_session_context(
        self, event_logger: EventLogger, tmp_log_file: Path
    ):
        """Verify that clear_session() removes session_id and tech_id from events."""
        # Arrange
        event_logger.set_session(session_id=303, tech_id=3)
        event_logger.clear_session()

        # Act
        event_logger.log_event(EventType.SYSTEM_SHUTDOWN, "Session cleared")

        # Assert
        log_data = json.loads(tmp_log_file.read_text())
        assert log_data["session_id"] is None
        assert log_data["tech_id"] is None

    def test_session_context_is_managed_correctly(
        self, event_logger: EventLogger, tmp_log_file: Path
    ):
        """
        Verify that session context (session_id, tech_id) is correctly applied
        to logs after set_session() and removed after clear_session().
        """
        # Log event with no session
        event_logger.log_event(EventType.SYSTEM_STARTUP, "No session")

        # Set session and log again
        event_logger.set_session(session_id=404, tech_id=4)
        event_logger.log_event(EventType.TREATMENT_SESSION_START, "Session started")

        # Clear session and log a final time
        event_logger.clear_session()
        event_logger.log_event(EventType.SYSTEM_SHUTDOWN, "Session cleared")

        # Assert
        lines = tmp_log_file.read_text().strip().split("\n")
        assert len(lines) == 3

        log1 = json.loads(lines[0])
        assert log1["session_id"] is None
        assert log1["tech_id"] is None

        log2 = json.loads(lines[1])
        assert log2["session_id"] == 404
        assert log2["tech_id"] == 4

        log3 = json.loads(lines[2])
        assert log3["session_id"] is None
        assert log3["tech_id"] is None


class TestConvenienceMethods:
    """Test convenience wrapper methods."""

    @patch.object(EventLogger, "log_event")
    def test_log_safety_event_calls_log_event(
        self, mock_log_event: MagicMock, event_logger: EventLogger
    ):
        """Verify log_safety_event() calls log_event() with correct parameters."""
        # Act
        event_logger.log_safety_event(
            event_type=EventType.SAFETY_INTERLOCK_FAIL,
            description="GPIO interlock failed",
            severity=EventSeverity.CRITICAL,
            action_taken="Laser disabled",
        )

        # Assert
        mock_log_event.assert_called_once_with(
            event_type=EventType.SAFETY_INTERLOCK_FAIL,
            description="GPIO interlock failed",
            severity=EventSeverity.CRITICAL,
            action_taken="Laser disabled",
        )

    @patch.object(EventLogger, "log_event")
    def test_log_hardware_event_calls_log_event(
        self, mock_log_event: MagicMock, event_logger: EventLogger
    ):
        """Verify log_hardware_event() calls log_event() with structured details."""
        # Act
        event_logger.log_hardware_event(
            event_type=EventType.HARDWARE_CAMERA_CONNECT,
            description="Camera connected",
            device_name="Allied Vision 1800 U-158c",
        )

        # Assert
        mock_log_event.assert_called_once_with(
            event_type=EventType.HARDWARE_CAMERA_CONNECT,
            description="Camera connected",
            severity=EventSeverity.INFO,
            details={"device": "Allied Vision 1800 U-158c"},
        )

    @patch.object(EventLogger, "log_event")
    def test_log_treatment_event_with_power_details(
        self, mock_log_event: MagicMock, event_logger: EventLogger
    ):
        """Verify log_treatment_event() includes laser power and position in details."""
        # Act
        event_logger.log_treatment_event(
            event_type=EventType.TREATMENT_POWER_CHANGE,
            description="Power set to 5W",
            laser_power=5.0,
            position=1500.0,
        )

        # Assert
        mock_log_event.assert_called_with(
            event_type=EventType.TREATMENT_POWER_CHANGE,
            description="Power set to 5W",
            severity=EventSeverity.INFO,
            details={"laser_power_watts": 5.0, "actuator_position_um": 1500.0},
        )

    @patch.object(EventLogger, "log_event")
    def test_log_user_action_with_action_type(
        self, mock_log_event: MagicMock, event_logger: EventLogger
    ):
        """Verify log_user_action() includes action_type in details."""
        # Act
        event_logger.log_user_action(
            description="User clicked E-Stop",
            action_type="emergency_stop",
            details={"button_id": "btn_estop"},
        )

        # Assert
        mock_log_event.assert_called_once_with(
            event_type=EventType.USER_ACTION,
            description="User clicked E-Stop",
            severity=EventSeverity.INFO,
            details={"action_type": "emergency_stop", "button_id": "btn_estop"},
        )

    @patch.object(EventLogger, "log_event")
    def test_log_error_includes_component(
        self, mock_log_event: MagicMock, event_logger: EventLogger
    ):
        """Verify log_error() includes component in details and description."""
        # Act
        event_logger.log_error(
            component="LaserController",
            error_message="Connection timeout",
            details={"port": "COM1"},
        )

        # Assert
        mock_log_event.assert_called_once_with(
            event_type=EventType.SYSTEM_ERROR,
            description="LaserController: Connection timeout",
            severity=EventSeverity.CRITICAL,
            details={"component": "LaserController", "port": "COM1"},
        )


class TestSignalEmission:
    """Test PyQt6 signal emission."""

    def test_event_logged_signal_emitted_on_log(self, event_logger: EventLogger, qtbot):
        """Verify event_logged signal is emitted for every log_event() call."""
        # Act
        with qtbot.waitSignal(event_logger.event_logged, timeout=1000) as blocker:
            event_logger.log_event(
                EventType.TREATMENT_LASER_ON, "Laser enabled", EventSeverity.INFO
            )

        # Assert
        event_type, severity, description = blocker.args
        assert event_type == EventType.TREATMENT_LASER_ON.value
        assert severity == EventSeverity.INFO.value
        assert description == "Laser enabled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
