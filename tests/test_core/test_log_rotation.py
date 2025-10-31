"""
Unit tests for log rotation and cleanup.

Tests rotation trigger, file naming, and retention policy.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.event_logger import EventLogger, EventSeverity, EventType
from database.db_manager import DatabaseManager


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary log directory for testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    db.initialize()
    return db


@pytest.fixture
def event_logger(temp_db, temp_log_dir):
    """Create event logger with temporary files."""
    log_file = temp_log_dir / "events.jsonl"
    logger = EventLogger(
        db_manager=temp_db,
        log_file=log_file,
        rotation_size_mb=0.001,  # Very small for testing (1KB)
        retention_days=7,
    )
    return logger


def test_rotation_at_size_threshold(event_logger, temp_log_dir):
    """Test log rotates when size exceeds threshold."""
    # Write enough events to exceed 1KB threshold
    for i in range(50):
        event_logger.log_event(
            event_type=EventType.SYSTEM_STARTUP,
            description=f"Test event {i} with lots of data to increase file size quickly",
            severity=EventSeverity.INFO,
        )

    # Check that rotation occurred (should have rotated file in directory)
    log_files = list(temp_log_dir.glob("*.jsonl"))
    # Should have current log + at least one rotated log
    assert len(log_files) >= 2, f"Expected rotation but found {len(log_files)} files"

    # Verify rotated file naming format
    rotated_files = [f for f in log_files if "_20" in f.name]  # Has timestamp
    assert len(rotated_files) >= 1, "Should have at least one rotated file with timestamp"


def test_cleanup_deletes_old_logs(temp_log_dir, temp_db):
    """Test old logs are deleted based on retention policy."""
    # Create event logger with 1-day retention
    log_file = temp_log_dir / "events.jsonl"
    logger = EventLogger(
        db_manager=temp_db,
        log_file=log_file,
        rotation_size_mb=100,
        retention_days=1,
    )

    # Create fake old log files
    old_date = datetime.now() - timedelta(days=10)
    old_filename = f"events_{old_date.strftime('%Y-%m-%d')}_12-00-00.jsonl"
    old_file = temp_log_dir / old_filename
    old_file.touch()

    # Create recent log file
    recent_date = datetime.now()
    recent_filename = f"events_{recent_date.strftime('%Y-%m-%d')}_12-00-00.jsonl"
    recent_file = temp_log_dir / recent_filename
    recent_file.touch()

    # Trigger cleanup
    logger._cleanup_old_logs()

    # Verify old file deleted, recent file kept
    assert not old_file.exists(), "Old log file should be deleted"
    assert recent_file.exists(), "Recent log file should be kept"


def test_rotation_filename_format(event_logger, temp_log_dir):
    """Test rotated files have correct timestamp format."""
    # Force rotation by writing large data
    large_data = "X" * 2000  # 2KB of data
    for i in range(10):
        event_logger.log_event(
            event_type=EventType.SYSTEM_STARTUP,
            description=f"Large event {i}: {large_data}",
            severity=EventSeverity.INFO,
        )

    # Find rotated files
    rotated_files = list(temp_log_dir.glob("events_20*.jsonl"))
    if rotated_files:
        # Verify timestamp format: events_YYYY-MM-DD_HH-MM-SS.jsonl
        for rotated_file in rotated_files:
            filename = rotated_file.stem
            parts = filename.split("_")
            assert len(parts) >= 4, f"Invalid filename format: {filename}"

            # Verify date part (YYYY-MM-DD)
            date_part = parts[1]
            try:
                datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"Invalid date format in filename: {date_part}")


def test_concurrent_rotation_handling(event_logger, temp_log_dir):
    """Test that concurrent rotation attempts don't cause errors."""
    # This tests the try-except safety in rotation code
    import threading

    errors = []

    def write_events():
        try:
            for i in range(20):
                event_logger.log_event(
                    event_type=EventType.SYSTEM_STARTUP,
                    description=f"Concurrent event {threading.current_thread().name} - {i} - {'X' * 200}",
                    severity=EventSeverity.INFO,
                )
        except Exception as e:
            errors.append(e)

    # Run multiple threads writing simultaneously
    threads = [threading.Thread(target=write_events, name=f"Thread{i}") for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no errors occurred
    assert len(errors) == 0, f"Concurrent rotation caused errors: {errors}"


def test_cleanup_preserves_current_log(event_logger, temp_log_dir):
    """Test cleanup doesn't delete the current active log file."""
    # Create some old rotated logs
    old_date = datetime.now() - timedelta(days=30)
    old_filename = f"events_{old_date.strftime('%Y-%m-%d')}_12-00-00.jsonl"
    old_file = temp_log_dir / old_filename
    old_file.write_text("old data")

    # Get current log file
    current_log = event_logger.log_file

    # Write to current log
    event_logger.log_event(
        event_type=EventType.SYSTEM_STARTUP,
        description="Current event",
        severity=EventSeverity.INFO,
    )

    # Run cleanup
    event_logger._cleanup_old_logs()

    # Verify current log still exists
    assert current_log.exists(), "Current log file should not be deleted"


def test_rotation_preserves_log_integrity(event_logger, temp_log_dir):
    """Test that rotation doesn't corrupt or lose events."""
    import json

    # Write events before rotation
    events_before = []
    for i in range(30):
        desc = f"Event before rotation {i}"
        events_before.append(desc)
        event_logger.log_event(
            event_type=EventType.SYSTEM_STARTUP,
            description=desc,
            severity=EventSeverity.INFO,
        )

    # Force rotation with large data
    for i in range(10):
        event_logger.log_event(
            event_type=EventType.SYSTEM_STARTUP,
            description=f"Large event {i}: {'X' * 500}",
            severity=EventSeverity.INFO,
        )

    # Write events after rotation
    events_after = []
    for i in range(10):
        desc = f"Event after rotation {i}"
        events_after.append(desc)
        event_logger.log_event(
            event_type=EventType.SYSTEM_STARTUP,
            description=desc,
            severity=EventSeverity.INFO,
        )

    # Read all log files and verify all events present
    all_events = []
    for log_file in temp_log_dir.glob("*.jsonl"):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    all_events.append(event["description"])

    # Verify all events present
    for desc in events_before + events_after:
        assert desc in all_events, f"Event missing after rotation: {desc}"
