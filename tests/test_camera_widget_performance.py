"""
UI widget performance tests for camera display.

Tests QPixmap rendering, signal connections, and GUI responsiveness.
"""

import time
from unittest.mock import MagicMock, Mock
import numpy as np
import pytest
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication

from hardware.camera_controller import CameraController
from ui.widgets.camera_widget import CameraWidget


class TestCameraWidgetPerformance:
    """Test camera widget display performance."""

    @pytest.fixture
    def app(self, qtbot):
        """Create QApplication for Qt tests."""
        return QApplication.instance() or QApplication([])

    @pytest.fixture
    def controller(self):
        """Create mock camera controller."""
        controller = Mock(spec=CameraController)
        controller.is_connected = False
        controller.display_scale = 0.25
        controller.get_exposure_range.return_value = (100.0, 1000000.0)
        controller.get_gain_range.return_value = (0.0, 24.0)
        controller.pixmap_ready = MagicMock()
        controller.frame_ready = MagicMock()
        controller.fps_update = MagicMock()
        controller.connection_changed = MagicMock()
        controller.error_occurred = MagicMock()
        controller.recording_status_changed = MagicMock()
        controller.exposure_changed = MagicMock()
        controller.gain_changed = MagicMock()
        return controller

    @pytest.fixture
    def widget(self, qtbot, controller, app):
        """Create camera widget with mock controller."""
        widget = CameraWidget(controller)
        qtbot.addWidget(widget)
        return widget

    def test_pixmap_received_is_fast(self, widget, qtbot, app):
        """Test that _on_pixmap_received() processes frames quickly."""
        # Create test pixmap
        test_image = np.zeros((272, 364, 3), dtype=np.uint8)
        from PyQt6.QtGui import QImage
        q_image = QImage(test_image.data, 364, 272, 364 * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Measure processing time
        start = time.perf_counter()
        for _ in range(30):  # Simulate 30 frames
            widget._on_pixmap_received(pixmap)
            qtbot.wait(1)  # Allow Qt events to process
        elapsed = time.perf_counter() - start

        # Should process 30 frames in < 1 second (i.e., capable of >30 FPS)
        assert elapsed < 1.0, f"Processing 30 frames took {elapsed:.2f}s, should be <1s for 30 FPS"
        fps = 30 / elapsed
        print(f"\n_on_pixmap_received() performance: {fps:.1f} FPS")

    def test_frame_received_updates_resolution_only(self, widget, qtbot, app):
        """Test that _on_frame_received() only updates resolution info, not display."""
        # Set camera controller with scale info
        widget.camera_controller.display_scale = 0.25

        # Create test frame (downsampled size)
        test_frame = np.zeros((272, 364, 3), dtype=np.uint8)

        # Call frame handler
        widget._on_frame_received(test_frame)

        # Should update resolution text
        resolution_text = widget.resolution_info.text()
        assert "Display: 364×272" in resolution_text, "Should show display resolution"
        assert "0.25" in resolution_text, "Should show scale factor"

    def test_pixmap_signal_connection(self, widget, controller):
        """Test that widget is connected to pixmap_ready signal."""
        # Check that pixmap_ready signal is connected
        # (Mock objects track connect() calls)
        assert controller.pixmap_ready.connect.called, "Should connect to pixmap_ready signal"

    def test_safety_limiter_blocks_long_exposure(self, widget, controller, qtbot):
        """Test that exposure safety limiter prevents frame-drop-causing exposures."""
        widget.camera_controller = controller
        widget.camera_controller.is_connected = True
        widget.is_connected = True

        # Disable "allow long exposure" checkbox
        widget.allow_long_exposure_check.setChecked(False)

        # Try to set 100ms exposure (unsafe for 30 FPS)
        unsafe_exposure = 100000  # 100ms in microseconds

        # Trigger exposure change
        widget._on_exposure_changed(unsafe_exposure)

        # Should NOT call controller.set_exposure() with unsafe value
        # Should revert slider to safe value (33ms)
        assert widget.exposure_slider.value() == 33000, "Should revert to safe 33ms exposure"

    def test_safety_limiter_allows_long_exposure_when_enabled(self, widget, controller, qtbot):
        """Test that safety limiter can be overridden with checkbox."""
        widget.camera_controller = controller
        widget.camera_controller.is_connected = True
        widget.is_connected = True

        # Enable "allow long exposure" checkbox
        widget.allow_long_exposure_check.setChecked(True)

        # Set 100ms exposure (unsafe but explicitly allowed)
        long_exposure = 100000

        # Trigger exposure change
        widget._on_exposure_changed(long_exposure)

        # Should call controller.set_exposure() with long value
        controller.set_exposure.assert_called_with(float(long_exposure))

    def test_auto_exposure_disables_manual_controls(self, widget, controller, qtbot):
        """Test that enabling auto exposure disables manual controls."""
        widget.camera_controller = controller

        # Enable auto exposure
        widget.auto_exposure_check.setChecked(True)
        widget._on_auto_exposure_changed(Qt.CheckState.Checked.value)

        # Manual controls should be disabled
        assert not widget.exposure_slider.isEnabled(), "Exposure slider should be disabled"
        assert not widget.exposure_input.isEnabled(), "Exposure input should be disabled"

    def test_pixmap_sharing_with_other_widgets(self, widget, qtbot, app):
        """Test that pixmap is emitted for other widgets to use."""
        # Track pixmap_ready emissions
        emitted_pixmaps = []

        def on_pixmap_ready(pixmap):
            emitted_pixmaps.append(pixmap)

        widget.pixmap_ready.connect(on_pixmap_ready)

        # Create and process test pixmap
        test_image = np.zeros((272, 364, 3), dtype=np.uint8)
        from PyQt6.QtGui import QImage
        q_image = QImage(test_image.data, 364, 272, 364 * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        widget._on_pixmap_received(pixmap)
        qtbot.wait(10)

        # Should have emitted pixmap for other widgets
        assert len(emitted_pixmaps) == 1, "Should emit pixmap once for other widgets"
        assert isinstance(emitted_pixmaps[0], QPixmap), "Should emit QPixmap object"


class TestCameraWidgetUIResponsiveness:
    """Test that UI remains responsive during camera streaming."""

    @pytest.fixture
    def app(self, qtbot):
        """Create QApplication for Qt tests."""
        return QApplication.instance() or QApplication([])

    def test_button_clicks_during_frame_updates(self, qtbot, app):
        """Test that buttons remain responsive during rapid frame updates."""
        controller = Mock(spec=CameraController)
        controller.is_connected = True
        controller.display_scale = 0.25
        controller.get_exposure_range.return_value = (100.0, 1000000.0)
        controller.get_gain_range.return_value = (0.0, 24.0)
        controller.pixmap_ready = MagicMock()
        controller.frame_ready = MagicMock()
        controller.fps_update = MagicMock()
        controller.connection_changed = MagicMock()
        controller.error_occurred = MagicMock()
        controller.recording_status_changed = MagicMock()
        controller.exposure_changed = MagicMock()
        controller.gain_changed = MagicMock()

        widget = CameraWidget(controller)
        qtbot.addWidget(widget)

        # Simulate rapid frame updates (30 FPS)
        test_image = np.zeros((272, 364, 3), dtype=np.uint8)
        from PyQt6.QtGui import QImage
        q_image = QImage(test_image.data, 364, 272, 364 * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        click_successful = False

        def update_frames():
            """Update frames at 30 FPS for 1 second."""
            for _ in range(30):
                widget._on_pixmap_received(pixmap)
                qtbot.wait(33)  # 33ms = 30 FPS

        def click_button():
            """Try to click button during frame updates."""
            nonlocal click_successful
            qtbot.wait(500)  # Wait 500ms, then click
            # Try to trigger auto exposure checkbox
            widget.auto_exposure_check.setChecked(True)
            click_successful = True

        # Start frame updates in background
        timer = QTimer()
        timer.singleShot(0, update_frames)

        # Try to interact with UI during updates
        click_timer = QTimer()
        click_timer.singleShot(0, click_button)

        # Wait for both to complete
        qtbot.wait(1500)

        # Button click should have succeeded despite ongoing frame updates
        assert click_successful, "UI should remain responsive during frame updates"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
