"""
Unit tests for database vacuum operation.

Tests vacuum functionality, error handling, and statistics calculation.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from database.db_manager import DatabaseManager


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_vacuum.db"
    db = DatabaseManager(str(db_path))
    db.initialize()
    yield db
    # Cleanup happens automatically with tmp_path


def test_vacuum_reduces_size(temp_db):
    """Test that vacuum reduces database file size after fragmentation."""
    # Add and delete data to create fragmentation
    with temp_db.get_session() as session:
        from database.models import Subject

        # Create many subjects
        for i in range(100):
            subject = Subject(
                first_name=f"Test{i}",
                last_name=f"Subject{i}",
                date_of_birth="2000-01-01",
                medical_record_number=f"MRN{i:06d}",
            )
            session.add(subject)
        session.commit()

        # Delete half of them to create fragmentation
        subjects = session.query(Subject).all()
        for subject in subjects[:50]:
            session.delete(subject)
        session.commit()

    # Get size before vacuum
    success_before, size_before_mb, _ = temp_db.get_database_size()
    assert success_before

    # Vacuum and verify size reduction
    success, message, stats = temp_db.vacuum_database()
    assert success, f"Vacuum failed: {message}"
    assert "size_reduction_percent" in stats
    assert stats["size_reduction_percent"] >= 0
    assert "size_before_mb" in stats
    assert "size_after_mb" in stats

    # Verify size actually decreased (or stayed same if minimal data)
    assert stats["size_after_mb"] <= stats["size_before_mb"]


def test_vacuum_handles_missing_file():
    """Test vacuum handles missing database file gracefully."""
    db = DatabaseManager("nonexistent.db")
    success, message, stats = db.vacuum_database()
    assert not success
    assert "not found" in message.lower() or "not exist" in message.lower()


def test_vacuum_statistics_accurate(temp_db):
    """Test vacuum statistics calculation is accurate."""
    # Add some data
    with temp_db.get_session() as session:
        from database.models import Subject

        subject = Subject(
            first_name="Test",
            last_name="Subject",
            date_of_birth="2000-01-01",
            medical_record_number="MRN000001",
        )
        session.add(subject)
        session.commit()

    # Get size before vacuum
    success_before, size_before_mb, _ = temp_db.get_database_size()
    assert success_before

    # Vacuum
    success, message, stats = temp_db.vacuum_database()
    assert success

    # Verify statistics accuracy
    assert abs(stats["size_before_mb"] - size_before_mb) < 0.01  # Within 10KB tolerance
    assert stats["size_after_mb"] > 0
    assert stats["size_reduction_percent"] >= 0
    assert stats["size_reduction_percent"] <= 100


def test_vacuum_on_empty_database(temp_db):
    """Test vacuum on empty database doesn't fail."""
    success, message, stats = temp_db.vacuum_database()
    assert success
    assert stats["size_reduction_percent"] >= 0


def test_vacuum_preserves_data(temp_db):
    """Test that vacuum doesn't lose data."""
    # Add data
    with temp_db.get_session() as session:
        from database.models import Subject

        for i in range(10):
            subject = Subject(
                first_name=f"Test{i}",
                last_name=f"Subject{i}",
                date_of_birth="2000-01-01",
                medical_record_number=f"MRN{i:06d}",
            )
            session.add(subject)
        session.commit()

    # Count records before vacuum
    with temp_db.get_session() as session:
        from database.models import Subject

        count_before = session.query(Subject).count()

    # Vacuum
    success, message, stats = temp_db.vacuum_database()
    assert success

    # Count records after vacuum
    with temp_db.get_session() as session:
        from database.models import Subject

        count_after = session.query(Subject).count()

    # Verify data preserved
    assert count_before == count_after == 10
