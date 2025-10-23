# -*- coding: utf-8 -*-
"""
Camera hardware abstraction layer for Allied Vision cameras.

Provides PyQt6-integrated camera control with:
- Live streaming with Qt signals
- Exposure and gain control
- Still image capture
- Video recording
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal

try:
    import vmbpy

    VMBPY_AVAILABLE = True
except ImportError:
    VMBPY_AVAILABLE = False
    logging.warning("VmbPy not available - camera features disabled")

logger = logging.getLogger(__name__)


class CameraStreamThread(QThread):
    """Thread for continuous camera streaming."""

    frame_ready = pyqtSignal(np.ndarray)  # Emits numpy array frames
    error_occurred = pyqtSignal(str)
    fps_update = pyqtSignal(float)

    def __init__(self, camera: "vmbpy.Camera") -> None:
        super().__init__()
        self.camera = camera
        self.running = False
        self.frame_count = 0
        self.start_time: Optional[float] = None

    def run(self) -> None:
        """Start streaming frames."""
        import time

        self.running = True
        self.frame_count = 0
        self.start_time = time.time()

        def frame_callback(cam: Any, stream: Any, frame: Any) -> None:
            """Callback for each frame."""
            if not self.running:
                return

            try:
                # Convert frame to numpy array
                frame_data = frame.as_numpy_ndarray()
                self.frame_count += 1

                # Emit frame to GUI
                self.frame_ready.emit(frame_data.copy())

                # Calculate and emit FPS every 30 frames
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / elapsed
                    self.fps_update.emit(fps)

            except Exception as e:
                logger.error(f"Frame callback error: {e}")
                self.error_occurred.emit(str(e))

            finally:
                cam.queue_frame(frame)

        try:
            self.camera.start_streaming(frame_callback)

            # Keep thread alive while streaming
            while self.running:
                self.msleep(100)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            try:
                self.camera.stop_streaming()
            except Exception:
                pass

    def stop(self) -> None:
        """Stop streaming."""
        self.running = False


class VideoRecorder:
    """Records camera frames to video file."""

    def __init__(
        self, output_path: Path, fps: float = 30.0, frame_size: tuple = (1456, 1088)
    ) -> None:
        """
        Initialize video recorder.

        Args:
            output_path: Path to output video file
            fps: Frames per second for video
            frame_size: Video frame size (width, height)
        """
        self.output_path = output_path
        self.fps = fps
        self.frame_size = frame_size
        self.writer: Optional[cv2.VideoWriter] = None
        self.frame_count = 0

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(str(output_path), fourcc, fps, frame_size)

        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open video writer: {output_path}")

        logger.info(f"Video recorder initialized: {output_path}")

    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write frame to video.

        Args:
            frame: Numpy array frame (BGR format)
        """
        if self.writer and self.writer.isOpened():
            # Resize if needed
            if frame.shape[:2][::-1] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)

            self.writer.write(frame)
            self.frame_count += 1

    def close(self) -> None:
        """Close video writer."""
        if self.writer:
            self.writer.release()
            logger.info(f"Video saved: {self.output_path} ({self.frame_count} frames)")
            self.writer = None


class CameraController(QObject):
    """
    Allied Vision camera controller with PyQt integration.

    Provides thread-safe camera operations with Qt signals.
    """

    # Signals
    frame_ready = pyqtSignal(np.ndarray)
    fps_update = pyqtSignal(float)
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected
    error_occurred = pyqtSignal(str)
    recording_status_changed = pyqtSignal(bool)  # True=recording, False=stopped

    def __init__(self) -> None:
        super().__init__()

        if not VMBPY_AVAILABLE:
            raise ImportError("VmbPy is not installed - camera features unavailable")

        self.vmb = vmbpy.VmbSystem.get_instance()
        self.camera: Optional["vmbpy.Camera"] = None
        self.stream_thread: Optional[CameraStreamThread] = None
        self.video_recorder: Optional[VideoRecorder] = None
        self.is_connected = False
        self.is_streaming = False
        self.is_recording = False

        logger.info("Camera controller initialized")

    def connect(self, camera_id: Optional[str] = None) -> bool:
        """
        Connect to camera.

        Args:
            camera_id: Optional camera ID. If None, connects to first available.

        Returns:
            True if connected successfully
        """
        try:
            self.vmb.__enter__()

            cameras = self.vmb.get_all_cameras()
            if not cameras:
                self.error_occurred.emit("No cameras detected")
                return False

            if camera_id:
                self.camera = self.vmb.get_camera_by_id(camera_id)
            else:
                self.camera = cameras[0]

            self.camera.__enter__()
            self.is_connected = True
            self.connection_changed.emit(True)

            logger.info(f"Connected to camera: {self.camera.get_id()}")
            return True

        except Exception as e:
            error_msg = f"Camera connection failed: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def disconnect(self) -> None:
        """Disconnect from camera."""
        self.stop_streaming()

        if self.camera:
            try:
                self.camera.__exit__(None, None, None)
            except Exception:
                pass
            self.camera = None

        try:
            self.vmb.__exit__(None, None, None)
        except Exception:
            pass

        self.is_connected = False
        self.connection_changed.emit(False)
        logger.info("Camera disconnected")

    def start_streaming(self) -> bool:
        """
        Start live camera streaming.

        Returns:
            True if streaming started successfully
        """
        if not self.is_connected or not self.camera:
            self.error_occurred.emit("Camera not connected")
            return False

        if self.is_streaming:
            return True

        try:
            self.stream_thread = CameraStreamThread(self.camera)
            self.stream_thread.frame_ready.connect(self._on_frame_received)
            self.stream_thread.fps_update.connect(self.fps_update.emit)
            self.stream_thread.error_occurred.connect(self.error_occurred.emit)
            self.stream_thread.start()

            self.is_streaming = True
            logger.info("Camera streaming started")
            return True

        except Exception as e:
            error_msg = f"Failed to start streaming: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def stop_streaming(self) -> None:
        """Stop camera streaming."""
        if self.stream_thread:
            self.stream_thread.stop()
            self.stream_thread.wait()
            self.stream_thread = None

        self.is_streaming = False
        logger.info("Camera streaming stopped")

    def _on_frame_received(self, frame: np.ndarray) -> None:
        """
        Handle received frame.

        Args:
            frame: Numpy array frame
        """
        # Emit to GUI
        self.frame_ready.emit(frame)

        # Write to video if recording
        if self.is_recording and self.video_recorder:
            # Convert to BGR if needed (VmbPy gives RGB)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = frame

            self.video_recorder.write_frame(frame_bgr)

    def capture_image(
        self, base_filename: str, output_dir: Path = Path("data/images")
    ) -> Optional[Path]:
        """
        Capture still image from camera.

        Args:
            base_filename: Base filename (timestamp will be appended)
            output_dir: Output directory for image

        Returns:
            Path to saved image, or None if failed
        """
        if not self.is_streaming:
            self.error_occurred.emit("Camera not streaming")
            return None

        # Image will be captured from next frame
        # For now, we'll use a simple approach - could be enhanced with single-shot capture
        self.error_occurred.emit("Image capture not yet implemented - use frame from stream")
        return None

    def start_recording(
        self, base_filename: str = "video", output_dir: Path = Path("data/videos")
    ) -> bool:
        """
        Start video recording.

        Args:
            base_filename: Base filename for video
            output_dir: Output directory

        Returns:
            True if recording started
        """
        if self.is_recording:
            return True

        if not self.is_streaming:
            self.error_occurred.emit("Cannot record - camera not streaming")
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}_{timestamp}.mp4"
            output_path = output_dir / filename

            self.video_recorder = VideoRecorder(output_path)
            self.is_recording = True
            self.recording_status_changed.emit(True)

            logger.info(f"Video recording started: {output_path}")
            return True

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def stop_recording(self) -> None:
        """Stop video recording."""
        if not self.is_recording:
            return

        if self.video_recorder:
            self.video_recorder.close()
            self.video_recorder = None

        self.is_recording = False
        self.recording_status_changed.emit(False)
        logger.info("Video recording stopped")

    def set_exposure(self, exposure_us: float) -> bool:
        """
        Set camera exposure time.

        Args:
            exposure_us: Exposure time in microseconds

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            self.camera.ExposureTime.set(exposure_us)
            logger.debug(f"Exposure set to {exposure_us} �s")
            return True
        except Exception as e:
            logger.error(f"Failed to set exposure: {e}")
            return False

    def set_gain(self, gain_db: float) -> bool:
        """
        Set camera gain.

        Args:
            gain_db: Gain in dB

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            self.camera.Gain.set(gain_db)
            logger.debug(f"Gain set to {gain_db} dB")
            return True
        except Exception as e:
            logger.error(f"Failed to set gain: {e}")
            return False

    def get_exposure_range(self) -> tuple:
        """Get min/max exposure values in microseconds."""
        if not self.camera:
            return (0.0, 1000000.0)

        try:
            return (
                self.camera.ExposureTime.get_min(),
                self.camera.ExposureTime.get_max(),
            )
        except Exception:
            return (0.0, 1000000.0)

    def get_gain_range(self) -> tuple:
        """Get min/max gain values in dB."""
        if not self.camera:
            return (0.0, 24.0)

        try:
            return (self.camera.Gain.get_min(), self.camera.Gain.get_max())
        except Exception:
            return (0.0, 24.0)
