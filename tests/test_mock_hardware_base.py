"""
Test MockHardwareBase functionality.

Validates that hardware mocking infrastructure works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockHardwareBase  # noqa: E402


def test_mock_connect_success() -> None:
    """Test successful connection simulation."""
    mock = MockHardwareBase()

    result = mock.connect(port="COM4")

    assert result is True
    assert mock.is_connected is True
    assert ("connect", {"port": "COM4"}) in mock.call_log


def test_mock_connect_failure() -> None:
    """Test connection failure simulation."""
    mock = MockHardwareBase()
    mock.simulate_connection_failure = True

    result = mock.connect(port="COM4")

    assert result is False
    assert mock.is_connected is False


def test_mock_disconnect() -> None:
    """Test disconnect simulation."""
    mock = MockHardwareBase()
    mock.connect()

    mock.disconnect()

    assert mock.is_connected is False
    assert mock.disconnect_call_count == 1
    assert ("disconnect", {}) in mock.call_log


def test_mock_get_status() -> None:
    """Test status retrieval."""
    mock = MockHardwareBase()
    mock.connect()

    status = mock.get_status()

    assert status["connected"] is True
    assert status["is_mock"] is True


def test_mock_reset() -> None:
    """Test reset functionality."""
    mock = MockHardwareBase()
    mock.connect()
    mock.simulate_connection_failure = True

    mock.reset()

    assert mock.is_connected is False
    assert mock.simulate_connection_failure is False
    assert len(mock.call_log) == 0
