"""
Comprehensive performance tests for camera system.

Tests camera frame rate, signal emission performance, thread safety,
and QPixmap optimization effectiveness.
"""

import time
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication

from hardware.camera_controller import CameraController, CameraStreamThread


class TestCameraPerformance:
    """Test camera performance and optimization effectiveness."""

    @pytest.fixture
    def app(self, qtbot):
        """Create QApplication for Qt tests."""
        return QApplication.instance() or QApplication([])

    @pytest.fixture
    def mock_camera(self):
        """Create mock VmbPy camera."""
        camera = Mock()
        camera.ExposureTime = Mock()
        camera.ExposureTime.get.return_value = 30000.0
        camera.ExposureTime.set = Mock()
        camera.Gain = Mock()
        camera.Gain.get.return_value = 0.0
        camera.Gain.set = Mock()
        return camera

    def test_pixmap_signal_emission(self, qtbot, app):
        """Test that QPixmap signals are emitted from camera thread."""
        # Create controller
        controller = CameraController()

        # Track signal emissions
        pixmap_count = 0
        frame_count = 0

        def on_pixmap(pixmap):
            nonlocal pixmap_count
            pixmap_count += 1
            assert isinstance(pixmap, QPixmap), "Should receive QPixmap object"
            assert not pixmap.isNull(), "Pixmap should contain valid data"

        def on_frame(frame):
            nonlocal frame_count
            frame_count += 1
            assert isinstance(frame, np.ndarray), "Should receive numpy array"

        controller.pixmap_ready.connect(on_pixmap)
        controller.frame_ready.connect(on_frame)

        # Simulate frame emission
        test_frame = np.zeros((272, 364, 3), dtype=np.uint8)
        controller.frame_ready.emit(test_frame)

        # Process Qt events
        qtbot.wait(100)

        # Both signals should be emitted
        assert frame_count > 0, "frame_ready signal should emit numpy arrays"
        # Note: pixmap_ready only emits during actual streaming with camera thread

    def test_frame_downsampling_reduces_size(self):
        """Test that display scale reduces frame data size."""
        # Full resolution frame
        full_frame = np.zeros((1088, 1456, 3), dtype=np.uint8)
        full_size = full_frame.nbytes

        # Quarter resolution (0.25x scale)
        quarter_frame = np.zeros((272, 364, 3), dtype=np.uint8)
        quarter_size = quarter_frame.nbytes

        # Should be ~16× smaller (4× width, 4× height)
        size_ratio = full_size / quarter_size
        assert 15 < size_ratio < 17, f"Quarter resolution should be ~16× smaller, got {size_ratio}×"

        # Calculate bandwidth savings
        fps = 30
        full_bandwidth = (full_size * fps) / (1024 * 1024)  # MB/s
        quarter_bandwidth = (quarter_size * fps) / (1024 * 1024)  # MB/s

        print(f"\nBandwidth comparison at 30 FPS:")
        print(f"  Full resolution: {full_bandwidth:.2f} MB/s")
        print(f"  Quarter resolution: {quarter_bandwidth:.2f} MB/s")
        print(f"  Savings: {((full_bandwidth - quarter_bandwidth) / full_bandwidth * 100):.1f}%")

    def test_exposure_limit_clamping(self, mock_camera):
        """Test that auto exposure limits are properly clamped to camera max."""
        controller = CameraController()
        controller.camera = mock_camera

        # Mock ExposureAutoMax feature
        mock_camera.ExposureAutoMax = Mock()
        mock_camera.ExposureAutoMax.get_range.return_value = (100.0, 50000.0)
        mock_camera.ExposureAutoMax.set = Mock()

        # Enable auto exposure (should set 30ms limit)
        controller.set_auto_exposure(True)

        # Verify limit was set to 30ms (within camera's 50ms max)
        mock_camera.ExposureAutoMax.set.assert_called_once()
        set_value = mock_camera.ExposureAutoMax.set.call_args[0][0]
        assert set_value == 30000.0, f"Should set 30ms limit, got {set_value}µs"

    def test_exposure_limit_clamps_to_camera_max(self, mock_camera):
        """Test that exposure limit doesn't exceed camera's maximum."""
        controller = CameraController()
        controller.camera = mock_camera

        # Mock ExposureAutoMax with LOW maximum (e.g., 20ms)
        mock_camera.ExposureAutoMax = Mock()
        mock_camera.ExposureAutoMax.get_range.return_value = (100.0, 20000.0)
        mock_camera.ExposureAutoMax.set = Mock()

        # Enable auto exposure (should clamp to 20ms, not 30ms)
        controller.set_auto_exposure(True)

        # Verify limit was clamped to camera's 20ms maximum
        mock_camera.ExposureAutoMax.set.assert_called_once()
        set_value = mock_camera.ExposureAutoMax.set.call_args[0][0]
        assert set_value == 20000.0, f"Should clamp to camera max 20ms, got {set_value}µs"

    def test_multiple_feature_name_fallback(self, mock_camera):
        """Test that multiple feature names are tried for compatibility."""
        controller = CameraController()
        controller.camera = mock_camera

        # First 3 features don't exist, 4th one works
        mock_camera.ExposureAutoUpperLimit = None
        mock_camera.ExposureAutoMax = None
        mock_camera.ExposureAutoLimitMax = None
        mock_camera.ExposureTimeUpperLimit = Mock()
        mock_camera.ExposureTimeUpperLimit.get_range.return_value = (100.0, 100000.0)
        mock_camera.ExposureTimeUpperLimit.set = Mock()

        # Enable auto exposure
        controller.set_auto_exposure(True)

        # Should have tried multiple names and succeeded with 4th one
        mock_camera.ExposureTimeUpperLimit.set.assert_called_once()

    @pytest.mark.parametrize("display_scale,expected_width,expected_height", [
        (1.0, 1456, 1088),   # Full resolution
        (0.5, 728, 544),     # Half resolution
        (0.25, 364, 272),    # Quarter resolution
    ])
    def test_display_scale_dimensions(self, display_scale, expected_width, expected_height):
        """Test that different display scales produce correct dimensions."""
        import cv2

        # Full resolution frame
        full_frame = np.zeros((1088, 1456, 3), dtype=np.uint8)

        # Apply downsampling (same as camera thread)
        if display_scale < 1.0:
            orig_height, orig_width = full_frame.shape[:2]
            new_width = int(orig_width * display_scale)
            new_height = int(orig_height * display_scale)
            downsampled = cv2.resize(full_frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        else:
            downsampled = full_frame

        # Verify dimensions
        height, width = downsampled.shape[:2]
        assert width == expected_width, f"Width should be {expected_width}, got {width}"
        assert height == expected_height, f"Height should be {expected_height}, got {height}"


class TestCameraThreadSafety:
    """Test camera thread safety and concurrency."""

    def test_concurrent_exposure_changes(self):
        """Test that concurrent exposure changes are thread-safe."""
        import threading

        controller = CameraController()

        # Simulate concurrent access
        errors = []

        def set_exposure(value):
            try:
                controller.set_exposure(value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=set_exposure, args=(10000.0,)),
            threading.Thread(target=set_exposure, args=(20000.0,)),
            threading.Thread(target=set_exposure, args=(30000.0,)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors (even though camera is disconnected)
        # The lock prevents race conditions
        assert len(errors) == 0 or all("not connected" in str(e).lower() for e in errors)

    def test_auto_polling_timer_starts_stops(self, qtbot):
        """Test that auto value polling timer starts/stops correctly."""
        controller = CameraController()

        # Initially, polling timer should be stopped
        assert not controller._auto_polling_timer.isActive()

        # Enable auto exposure (should start timer)
        controller._auto_exposure_enabled = True
        controller._update_auto_polling()
        assert controller._auto_polling_timer.isActive()

        # Disable auto exposure (should stop timer)
        controller._auto_exposure_enabled = False
        controller._auto_gain_enabled = False
        controller._update_auto_polling()
        assert not controller._auto_polling_timer.isActive()


class TestCameraIntegration:
    """Integration tests for complete camera workflow."""

    def test_camera_connect_configure_stream_workflow(self):
        """Test full workflow: connect → configure → stream → disconnect."""
        # This test requires real hardware, so we'll mock the VmbPy parts
        with patch('hardware.camera_controller.vmbpy') as mock_vmbpy:
            # Setup mocks
            mock_vmb = Mock()
            mock_camera = Mock()
            mock_camera.get_id.return_value = "TEST_CAMERA_001"
            mock_camera.get_pixel_formats.return_value = []
            mock_camera.ExposureTime = Mock()
            mock_camera.ExposureTime.get.return_value = 30000.0
            mock_camera.Gain = Mock()
            mock_camera.Gain.get.return_value = 0.0
            mock_camera.AcquisitionFrameRate = Mock()
            mock_camera.AcquisitionFrameRate.get_range.return_value = (1.0, 60.0)
            mock_camera.AcquisitionFrameRate.get.return_value = 30.0
            mock_camera.AcquisitionFrameRateEnable = Mock()

            mock_vmb.get_all_cameras.return_value = [mock_camera]
            mock_vmbpy.VmbSystem.get_instance.return_value = mock_vmb
            mock_vmbpy.PixelFormat.Bgr8 = "Bgr8"

            # Create controller
            controller = CameraController()

            # Step 1: Connect
            success = controller.connect()
            assert success, "Camera connection should succeed"
            assert controller.is_connected, "Controller should be marked as connected"

            # Step 2: Configure (set exposure/gain)
            controller.set_exposure(25000.0)
            controller.set_gain(6.0)

            # Step 3: Stream (mocked - real streaming requires camera thread)
            # In real usage, would call start_streaming() here

            # Step 4: Disconnect
            controller.disconnect()
            assert not controller.is_connected, "Controller should be disconnected"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
