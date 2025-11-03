"""
Test MockCameraController functionality.

Validates that camera mocking works including frame generation and streaming.
"""

import sys
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QCoreApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockCameraController  # noqa: E402


def test_mock_camera_connect_success() -> None:
    """Test successful camera connection."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()

    result = mock.connect(camera_id="CAM123")

    assert result is True
    assert mock.is_connected is True
    assert ("connect", {"camera_id": "CAM123"}) in mock.call_log


def test_mock_camera_connect_failure() -> None:
    """Test camera connection failure simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()
    mock.simulate_connection_failure = True

    result = mock.connect()

    assert result is False
    assert mock.is_connected is False


def test_mock_camera_streaming() -> None:
    """Test camera streaming simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()
    mock.connect()

    result = mock.start_streaming()

    assert result is True
    assert mock.is_streaming is True
    assert ("start_streaming", {}) in mock.call_log


def test_mock_camera_frame_generation() -> None:
    """Test camera frame generation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()
    mock.connect()
    mock.start_streaming()

    # Manually trigger frame generation
    mock._generate_frame()

    assert mock.latest_frame is not None
    assert isinstance(mock.latest_frame, np.ndarray)
    assert mock.latest_frame.shape == (480, 640, 3)


def test_mock_camera_recording() -> None:
    """Test camera recording simulation."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()
    mock.connect()

    result = mock.start_recording("test.avi")

    assert result is True
    assert mock.is_recording is True
    assert ("start_recording", {"filename": "test.avi"}) in mock.call_log


def test_mock_camera_exposure_gain() -> None:
    """Test exposure and gain settings."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()

    mock.set_exposure(2000.0)
    mock.set_gain(20.0)

    assert mock.exposure_us == 2000.0
    assert mock.gain_db == 20.0


def test_mock_camera_reset() -> None:
    """Test camera reset functionality."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    mock = MockCameraController()
    mock.connect()
    mock.start_streaming()
    mock.simulate_connection_failure = True

    mock.reset()

    assert mock.is_connected is False
    assert mock.is_streaming is False
    assert mock.simulate_connection_failure is False
    assert len(mock.call_log) == 0
