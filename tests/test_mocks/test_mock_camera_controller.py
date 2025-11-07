"""
Unit tests for MockCameraController.

Validates that the mock correctly simulates camera behavior including:
- Connection/disconnection
- Streaming and recording
- VmbPy API compliance (pixel formats, binning, trigger modes)
- Hardware frame rate control
- Frame generation with proper dtypes
- Signal emission
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from PyQt6.QtCore import QCoreApplication

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.mocks import MockAcquisitionMode, MockCameraController, MockPixelFormat, MockTriggerMode


@pytest.fixture
def qapp():
    """Create QCoreApplication for PyQt6 signal testing."""
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app
    # No cleanup needed - QCoreApplication persists


@pytest.fixture
def mock_camera(qapp):
    """Create MockCameraController instance."""
    camera = MockCameraController()
    yield camera
    # Cleanup
    if camera.is_streaming:
        camera.stop_streaming()
    if camera.is_connected:
        camera.disconnect()


# =============================================================================
# Connection Tests
# =============================================================================


def test_initial_state(mock_camera):
    """Test mock starts in clean disconnected state."""
    assert mock_camera.is_connected is False
    assert mock_camera.is_streaming is False
    assert mock_camera.is_recording is False
    assert mock_camera.latest_frame is None
    assert mock_camera.exposure_us == 1000.0
    assert mock_camera.gain_db == 10.0
    assert len(mock_camera.call_log) == 0


def test_connect_success(mock_camera):
    """Test successful connection."""
    result = mock_camera.connect(camera_id="CAM_1800_U_158c")

    assert result is True
    assert mock_camera.is_connected is True
    assert ("connect", {"camera_id": "CAM_1800_U_158c"}) in mock_camera.call_log


def test_connect_failure_simulation(mock_camera):
    """Test simulated connection failure."""
    mock_camera.simulate_connection_failure = True

    result = mock_camera.connect()

    assert result is False
    assert mock_camera.is_connected is False


def test_disconnect(mock_camera):
    """Test disconnection stops streaming and recording."""
    mock_camera.connect()
    mock_camera.start_streaming()
    mock_camera.start_recording("test.avi")

    mock_camera.disconnect()

    assert mock_camera.is_connected is False
    assert mock_camera.is_streaming is False
    assert mock_camera.is_recording is False


# =============================================================================
# Streaming and Recording Tests
# =============================================================================


def test_start_streaming_success(mock_camera):
    """Test starting video stream."""
    mock_camera.connect()

    result = mock_camera.start_streaming()

    assert result is True
    assert mock_camera.is_streaming is True
    assert ("start_streaming", {}) in mock_camera.call_log


def test_start_streaming_requires_connection(mock_camera):
    """Test streaming requires connection."""
    result = mock_camera.start_streaming()

    assert result is False
    assert mock_camera.is_streaming is False


def test_stop_streaming(mock_camera):
    """Test stopping video stream."""
    mock_camera.connect()
    mock_camera.start_streaming()

    mock_camera.stop_streaming()

    assert mock_camera.is_streaming is False


def test_start_recording_success(mock_camera):
    """Test starting recording."""
    mock_camera.connect()

    result = mock_camera.start_recording("test_video.avi")

    assert result is True
    assert mock_camera.is_recording is True
    assert ("start_recording", {"filename": "test_video.avi"}) in mock_camera.call_log


def test_stop_recording(mock_camera):
    """Test stopping recording."""
    mock_camera.connect()
    mock_camera.start_recording("test.avi")

    mock_camera.stop_recording()

    assert mock_camera.is_recording is False


def test_capture_image_success(mock_camera):
    """Test capturing single image."""
    mock_camera.connect()

    result = mock_camera.capture_image("test_image.png")

    assert result is True
    assert ("capture_image", {"filename": "test_image.png"}) in mock_camera.call_log


# =============================================================================
# Frame Generation Tests
# =============================================================================


def test_frame_generation_color(mock_camera):
    """Test color frame generation (default Bgr8 format)."""
    mock_camera.connect()
    mock_camera.start_streaming()

    mock_camera._generate_frame()

    assert mock_camera.latest_frame is not None
    assert isinstance(mock_camera.latest_frame, np.ndarray)
    assert mock_camera.latest_frame.shape == (480, 640, 3)  # Color
    assert mock_camera.latest_frame.dtype == np.uint8
    assert mock_camera.latest_frame.flags["C_CONTIGUOUS"]  # VmbPy requirement


def test_frame_generation_mono8(mock_camera):
    """Test grayscale frame generation with Mono8 format."""
    mock_camera.connect()
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    mock_camera.start_streaming()

    mock_camera._generate_frame()

    assert mock_camera.latest_frame is not None
    assert mock_camera.latest_frame.shape == (480, 640)  # Grayscale (2D)
    assert mock_camera.latest_frame.dtype == np.uint8


def test_frame_generation_with_binning(mock_camera):
    """Test frame generation with binning applied."""
    mock_camera.connect()
    mock_camera.set_binning(2)  # 2x2 binning
    mock_camera.start_streaming()

    mock_camera._generate_frame()

    # Frame should be half resolution
    assert mock_camera.latest_frame.shape == (240, 320, 3)


def test_frame_generation_mono8_with_binning(mock_camera):
    """Test grayscale frame generation with binning."""
    mock_camera.connect()
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    mock_camera.set_binning(4)  # 4x4 binning
    mock_camera.start_streaming()

    mock_camera._generate_frame()

    # Frame should be quarter resolution, grayscale
    assert mock_camera.latest_frame.shape == (120, 160)


# =============================================================================
# VmbPy API Compliance Tests - Pixel Format
# =============================================================================


def test_set_pixel_format_bgr8(mock_camera):
    """Test setting Bgr8 pixel format."""
    mock_camera.connect()

    result = mock_camera.set_pixel_format(MockPixelFormat.Bgr8)

    assert result is True
    assert mock_camera.pixel_format == MockPixelFormat.Bgr8
    assert mock_camera.simulated_frame_shape == (480, 640, 3)


def test_set_pixel_format_rgb8(mock_camera):
    """Test setting Rgb8 pixel format."""
    mock_camera.connect()

    result = mock_camera.set_pixel_format(MockPixelFormat.Rgb8)

    assert result is True
    assert mock_camera.pixel_format == MockPixelFormat.Rgb8
    assert mock_camera.simulated_frame_shape == (480, 640, 3)


def test_set_pixel_format_mono8(mock_camera):
    """Test setting Mono8 pixel format."""
    mock_camera.connect()

    result = mock_camera.set_pixel_format(MockPixelFormat.Mono8)

    assert result is True
    assert mock_camera.pixel_format == MockPixelFormat.Mono8
    assert mock_camera.simulated_frame_shape == (480, 640)  # Grayscale


def test_set_pixel_format_requires_connection(mock_camera):
    """Test pixel format setting requires connection."""
    result = mock_camera.set_pixel_format(MockPixelFormat.Mono8)

    assert result is False


def test_get_pixel_format(mock_camera):
    """Test getting current pixel format."""
    mock_camera.connect()
    mock_camera.set_pixel_format(MockPixelFormat.Rgb8)

    pixel_format = mock_camera.get_pixel_format()

    assert pixel_format == MockPixelFormat.Rgb8


# =============================================================================
# VmbPy API Compliance Tests - Binning
# =============================================================================


def test_set_binning_1x(mock_camera):
    """Test setting 1x1 binning (no binning)."""
    mock_camera.connect()

    result = mock_camera.set_binning(1)

    assert result is True
    assert mock_camera.binning_factor == 1
    assert mock_camera.simulated_frame_shape == (480, 640, 3)


def test_set_binning_2x(mock_camera):
    """Test setting 2x2 binning."""
    mock_camera.connect()

    result = mock_camera.set_binning(2)

    assert result is True
    assert mock_camera.binning_factor == 2
    assert mock_camera.simulated_frame_shape == (240, 320, 3)


def test_set_binning_4x(mock_camera):
    """Test setting 4x4 binning."""
    mock_camera.connect()

    result = mock_camera.set_binning(4)

    assert result is True
    assert mock_camera.binning_factor == 4
    assert mock_camera.simulated_frame_shape == (120, 160, 3)


def test_set_binning_8x(mock_camera):
    """Test setting 8x8 binning."""
    mock_camera.connect()

    result = mock_camera.set_binning(8)

    assert result is True
    assert mock_camera.binning_factor == 8
    assert mock_camera.simulated_frame_shape == (60, 80, 3)


def test_set_binning_invalid_factor(mock_camera):
    """Test invalid binning factor is rejected."""
    mock_camera.connect()

    result = mock_camera.set_binning(3)  # Only 1, 2, 4, 8 allowed

    assert result is False
    assert mock_camera.binning_factor == 1  # Unchanged


def test_set_binning_requires_connection(mock_camera):
    """Test binning requires connection."""
    result = mock_camera.set_binning(2)

    assert result is False


def test_get_binning(mock_camera):
    """Test getting current binning factor."""
    mock_camera.connect()
    mock_camera.set_binning(4)

    binning = mock_camera.get_binning()

    assert binning == 4


# =============================================================================
# VmbPy API Compliance Tests - Trigger Mode
# =============================================================================


def test_set_trigger_mode_continuous(mock_camera):
    """Test setting continuous trigger mode."""
    mock_camera.connect()

    result = mock_camera.set_trigger_mode(MockTriggerMode.Continuous)

    assert result is True
    assert mock_camera.trigger_mode == MockTriggerMode.Continuous


def test_set_trigger_mode_software(mock_camera):
    """Test setting software trigger mode."""
    mock_camera.connect()

    result = mock_camera.set_trigger_mode(MockTriggerMode.Software)

    assert result is True
    assert mock_camera.trigger_mode == MockTriggerMode.Software


def test_set_trigger_mode_hardware(mock_camera):
    """Test setting hardware trigger mode."""
    mock_camera.connect()

    result = mock_camera.set_trigger_mode(MockTriggerMode.Hardware)

    assert result is True
    assert mock_camera.trigger_mode == MockTriggerMode.Hardware


def test_set_trigger_mode_requires_connection(mock_camera):
    """Test trigger mode requires connection."""
    result = mock_camera.set_trigger_mode(MockTriggerMode.Software)

    assert result is False


def test_get_trigger_mode(mock_camera):
    """Test getting current trigger mode."""
    mock_camera.connect()
    mock_camera.set_trigger_mode(MockTriggerMode.Software)

    trigger_mode = mock_camera.get_trigger_mode()

    assert trigger_mode == MockTriggerMode.Software


def test_trigger_software_frame(mock_camera):
    """Test software trigger frame capture."""
    mock_camera.connect()
    mock_camera.set_trigger_mode(MockTriggerMode.Software)

    result = mock_camera.trigger_software_frame()

    assert result is True
    assert mock_camera.latest_frame is not None


def test_trigger_software_frame_wrong_mode(mock_camera):
    """Test software trigger fails if not in software trigger mode."""
    mock_camera.connect()
    mock_camera.set_trigger_mode(MockTriggerMode.Continuous)

    result = mock_camera.trigger_software_frame()

    assert result is False


# =============================================================================
# VmbPy API Compliance Tests - Acquisition Mode
# =============================================================================


def test_set_acquisition_mode_continuous(mock_camera):
    """Test setting continuous acquisition mode."""
    mock_camera.connect()

    result = mock_camera.set_acquisition_mode(MockAcquisitionMode.Continuous)

    assert result is True
    assert mock_camera.acquisition_mode == MockAcquisitionMode.Continuous


def test_set_acquisition_mode_single_frame(mock_camera):
    """Test setting single frame acquisition mode."""
    mock_camera.connect()

    result = mock_camera.set_acquisition_mode(MockAcquisitionMode.SingleFrame)

    assert result is True
    assert mock_camera.acquisition_mode == MockAcquisitionMode.SingleFrame


def test_set_acquisition_mode_multi_frame(mock_camera):
    """Test setting multi-frame acquisition mode."""
    mock_camera.connect()

    result = mock_camera.set_acquisition_mode(MockAcquisitionMode.MultiFrame)

    assert result is True
    assert mock_camera.acquisition_mode == MockAcquisitionMode.MultiFrame


def test_set_acquisition_mode_requires_connection(mock_camera):
    """Test acquisition mode requires connection."""
    result = mock_camera.set_acquisition_mode(MockAcquisitionMode.SingleFrame)

    assert result is False


def test_get_acquisition_mode(mock_camera):
    """Test getting current acquisition mode."""
    mock_camera.connect()
    mock_camera.set_acquisition_mode(MockAcquisitionMode.SingleFrame)

    acquisition_mode = mock_camera.get_acquisition_mode()

    assert acquisition_mode == MockAcquisitionMode.SingleFrame


# =============================================================================
# VmbPy API Compliance Tests - Hardware FPS
# =============================================================================


def test_set_hardware_fps_30(mock_camera):
    """Test setting 30 FPS."""
    mock_camera.connect()

    result = mock_camera.set_hardware_fps(30.0)

    assert result is True
    assert mock_camera.hardware_fps == 30.0
    assert mock_camera.simulated_fps == 30


def test_set_hardware_fps_60(mock_camera):
    """Test setting 60 FPS."""
    mock_camera.connect()

    result = mock_camera.set_hardware_fps(60.0)

    assert result is True
    assert mock_camera.hardware_fps == 60.0
    assert mock_camera.simulated_fps == 60


def test_set_hardware_fps_updates_timer_when_streaming(mock_camera):
    """Test FPS change updates timer when streaming."""
    mock_camera.connect()
    mock_camera.start_streaming()

    result = mock_camera.set_hardware_fps(15.0)

    assert result is True
    assert mock_camera._frame_timer.interval() == int(1000 / 15)


def test_set_hardware_fps_below_minimum(mock_camera):
    """Test FPS below 1 is rejected."""
    mock_camera.connect()

    result = mock_camera.set_hardware_fps(0.5)

    assert result is False
    assert mock_camera.hardware_fps == 30.0  # Unchanged


def test_set_hardware_fps_above_maximum(mock_camera):
    """Test FPS above 120 is rejected."""
    mock_camera.connect()

    result = mock_camera.set_hardware_fps(150.0)

    assert result is False
    assert mock_camera.hardware_fps == 30.0  # Unchanged


def test_set_hardware_fps_requires_connection(mock_camera):
    """Test FPS setting requires connection."""
    result = mock_camera.set_hardware_fps(60.0)

    assert result is False


def test_get_hardware_fps(mock_camera):
    """Test getting current hardware FPS."""
    mock_camera.connect()
    mock_camera.set_hardware_fps(45.0)

    fps = mock_camera.get_hardware_fps()

    assert fps == 45.0


# =============================================================================
# Exposure and Gain Tests
# =============================================================================


def test_set_exposure(mock_camera):
    """Test setting camera exposure."""
    result = mock_camera.set_exposure(2000.0)

    assert result is True
    assert mock_camera.exposure_us == 2000.0


def test_set_gain(mock_camera):
    """Test setting camera gain."""
    result = mock_camera.set_gain(20.0)

    assert result is True
    assert mock_camera.gain_db == 20.0


def test_get_exposure_range(mock_camera):
    """Test getting exposure range."""
    exposure_range = mock_camera.get_exposure_range()

    assert exposure_range == (100.0, 10000.0)


def test_get_gain_range(mock_camera):
    """Test getting gain range."""
    gain_range = mock_camera.get_gain_range()

    assert gain_range == (0.0, 40.0)


# =============================================================================
# Signal Emission Tests
# =============================================================================


def test_frame_ready_signal(mock_camera, qtbot):
    """Test frame_ready signal is emitted."""
    mock_camera.connect()
    mock_camera.start_streaming()

    with qtbot.waitSignal(mock_camera.frame_ready, timeout=1000):
        mock_camera._generate_frame()


def test_fps_update_signal(mock_camera, qtbot):
    """Test fps_update signal is emitted."""
    mock_camera.connect()
    mock_camera.start_streaming()

    with qtbot.waitSignal(mock_camera.fps_update, timeout=1000):
        mock_camera._generate_frame()


def test_connection_changed_signal(mock_camera, qtbot):
    """Test connection_changed signal is emitted."""
    with qtbot.waitSignal(mock_camera.connection_changed, timeout=1000):
        mock_camera.connect()


def test_recording_status_changed_signal(mock_camera, qtbot):
    """Test recording_status_changed signal is emitted."""
    mock_camera.connect()

    with qtbot.waitSignal(mock_camera.recording_status_changed, timeout=1000):
        mock_camera.start_recording("test.avi")


def test_pixel_format_changed_signal(mock_camera, qtbot):
    """Test pixel_format_changed signal is emitted."""
    mock_camera.connect()

    with qtbot.waitSignal(mock_camera.pixel_format_changed, timeout=1000):
        mock_camera.set_pixel_format(MockPixelFormat.Mono8)


def test_binning_changed_signal(mock_camera, qtbot):
    """Test binning_changed signal is emitted."""
    mock_camera.connect()

    with qtbot.waitSignal(mock_camera.binning_changed, timeout=1000):
        mock_camera.set_binning(2)


def test_trigger_mode_changed_signal(mock_camera, qtbot):
    """Test trigger_mode_changed signal is emitted."""
    mock_camera.connect()

    with qtbot.waitSignal(mock_camera.trigger_mode_changed, timeout=1000):
        mock_camera.set_trigger_mode(MockTriggerMode.Software)


def test_acquisition_mode_changed_signal(mock_camera, qtbot):
    """Test acquisition_mode_changed signal is emitted."""
    mock_camera.connect()

    with qtbot.waitSignal(mock_camera.acquisition_mode_changed, timeout=1000):
        mock_camera.set_acquisition_mode(MockAcquisitionMode.SingleFrame)


# =============================================================================
# Error Simulation Tests
# =============================================================================


def test_operation_error_simulation(mock_camera):
    """Test simulated operation errors."""
    mock_camera.connect()
    mock_camera.simulate_operation_error = True

    result = mock_camera.set_pixel_format(MockPixelFormat.Mono8)

    assert result is False


def test_reset_clears_state(mock_camera):
    """Test reset() clears all state and call log."""
    mock_camera.connect()
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    mock_camera.set_binning(4)
    mock_camera.start_streaming()

    mock_camera.reset()

    assert mock_camera.is_connected is False
    assert mock_camera.is_streaming is False
    assert mock_camera.pixel_format == MockPixelFormat.Bgr8
    assert mock_camera.binning_factor == 1
    assert len(mock_camera.call_log) == 0


# =============================================================================
# Combined Feature Tests
# =============================================================================


def test_combined_pixel_format_and_binning(mock_camera):
    """Test combining pixel format and binning settings."""
    mock_camera.connect()
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    mock_camera.set_binning(2)
    mock_camera.start_streaming()

    mock_camera._generate_frame()

    # Should be half resolution, grayscale
    assert mock_camera.latest_frame.shape == (240, 320)
    assert mock_camera.latest_frame.dtype == np.uint8


def test_pixel_format_switch_updates_frame_shape(mock_camera):
    """Test switching pixel format updates frame shape correctly."""
    mock_camera.connect()

    # Start with color
    assert mock_camera.simulated_frame_shape == (480, 640, 3)

    # Switch to mono
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    assert mock_camera.simulated_frame_shape == (480, 640)

    # Switch back to color
    mock_camera.set_pixel_format(MockPixelFormat.Bgr8)
    assert mock_camera.simulated_frame_shape == (480, 640, 3)


def test_binning_with_different_pixel_formats(mock_camera):
    """Test binning works correctly with different pixel formats."""
    mock_camera.connect()
    mock_camera.set_binning(4)

    # Bgr8 with binning
    mock_camera.set_pixel_format(MockPixelFormat.Bgr8)
    assert mock_camera.simulated_frame_shape == (120, 160, 3)

    # Mono8 with binning
    mock_camera.set_pixel_format(MockPixelFormat.Mono8)
    assert mock_camera.simulated_frame_shape == (120, 160)

    # Rgb8 with binning
    mock_camera.set_pixel_format(MockPixelFormat.Rgb8)
    assert mock_camera.simulated_frame_shape == (120, 160, 3)
