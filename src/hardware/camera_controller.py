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

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


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

        # Frame throttling for GUI updates
        self.gui_frame_count = 0
        self.last_gui_frame_time = 0.0
        self.gui_fps_target = 30.0  # Limit GUI updates to 30 FPS

    def run(self) -> None:  # noqa: C901
        """Start streaming frames."""
        import time

        self.running = True
        self.frame_count = 0
        self.start_time = time.time()
        self.last_gui_frame_time = 0.0  # Reset to ensure first frame passes

        def frame_callback(cam: Any, stream: Any, frame: Any) -> None:
            """Callback for each frame."""
            if not self.running:
                return

            try:
                # Convert frame to numpy array
                self.frame_count += 1
                current_time = time.time()

                # Throttle GUI updates to target FPS
                time_since_last_gui_frame = current_time - self.last_gui_frame_time
                min_frame_interval = 1.0 / self.gui_fps_target

                if time_since_last_gui_frame >= min_frame_interval:
                    # Only process frame data when we're actually going to send it
                    frame_data = np.ascontiguousarray(frame.as_numpy_ndarray())

                    # Emit frame to GUI (no copy needed - Qt signals handle data safely)
                    self.frame_ready.emit(frame_data)
                    self.last_gui_frame_time = current_time
                    self.gui_frame_count += 1

                    # Debug logging every 30 GUI frames
                    if self.gui_frame_count % 30 == 0:
                        gui_fps = (
                            30.0 / (current_time - self.start_time)
                            if current_time > self.start_time
                            else 0
                        )
                        msg = (
                            f"GUI frames: {self.gui_frame_count}, "
                            f"Camera frames: {self.frame_count}, "
                            f"GUI FPS: {gui_fps:.1f}"
                        )
                        logger.debug(msg)

                # Calculate and emit camera FPS every 30 frames (real camera rate)
                if self.frame_count % 30 == 0:
                    elapsed = current_time - self.start_time
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
            except Exception as e:
                logger.warning(f"Ignoring error during camera stream shutdown: {e}")

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

    def __init__(self, event_logger: Optional[Any] = None) -> None:
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
        self.event_logger = event_logger

        # Store latest frame for image capture
        self.latest_frame: Optional[np.ndarray] = None

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

            camera_id_str = self.camera.get_id()
            logger.info(f"Connected to camera: {camera_id_str}")

            # Log event
            if self.event_logger:
                from ..core.event_logger import EventType

                self.event_logger.log_hardware_event(
                    event_type=EventType.HARDWARE_CAMERA_CONNECT,
                    description=f"Camera connected: {camera_id_str}",
                    device_name="Allied Vision Camera",
                )

            # Log frame rate capabilities
            fps_info = self.get_acquisition_frame_rate_info()
            logger.info(
                f"Camera FPS range: [{fps_info['min_fps']:.2f}, "
                f"{fps_info['max_fps']:.2f}], current: {fps_info['current_fps']:.2f}"
            )

            return True

        except Exception as e:
            error_msg = f"Camera connection failed: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

            # Log error event
            if self.event_logger:
                from ..core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.HARDWARE_ERROR,
                    description=error_msg,
                    severity=EventSeverity.WARNING,
                    details={"device": "Allied Vision Camera"},
                )

            return False

    def disconnect(self) -> None:
        """Disconnect from camera."""
        self.stop_streaming()

        if self.camera:
            try:
                self.camera.__exit__(None, None, None)
            except Exception as e:
                logger.warning(f"Ignoring error during camera cleanup: {e}")
            self.camera = None

        try:
            self.vmb.__exit__(None, None, None)
        except Exception as e:
            logger.warning(f"Ignoring error during VmbPy cleanup: {e}")

        self.is_connected = False
        self.connection_changed.emit(False)
        logger.info("Camera disconnected")

        # Log event
        if self.event_logger:
            from ..core.event_logger import EventType

            self.event_logger.log_hardware_event(
                event_type=EventType.HARDWARE_CAMERA_DISCONNECT,
                description="Camera disconnected",
                device_name="Allied Vision Camera",
            )

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
            # Try to set camera acquisition frame rate to 30 FPS
            fps_info = self.get_acquisition_frame_rate_info()
            if fps_info["max_fps"] >= 30.0:
                # Hardware supports desired frame rate
                self.set_acquisition_frame_rate(30.0)
                logger.info("Using hardware frame rate control (30 FPS)")
            else:
                # Hardware frame rate limited, use software throttling instead
                logger.warning(
                    f"Camera max FPS ({fps_info['max_fps']:.2f}) < 30. "
                    f"Using software throttling instead"
                )

            self.stream_thread = CameraStreamThread(self.camera)
            self.stream_thread.frame_ready.connect(self._on_frame_received)
            self.stream_thread.fps_update.connect(self.fps_update.emit)
            self.stream_thread.error_occurred.connect(self.error_occurred.emit)
            self.stream_thread.start()

            self.is_streaming = True
            logger.info("Camera streaming started at 30 FPS")
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
        # Store latest frame for image capture
        self.latest_frame = frame.copy()

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
        self, base_filename: str, output_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Capture still image from camera.

        Args:
            base_filename: Base filename (timestamp will be appended)
            output_dir: Output directory for image (defaults to PROJECT_ROOT/data/images)

        Returns:
            Path to saved image, or None if failed
        """
        if output_dir is None:
            output_dir = PROJECT_ROOT / "data" / "images"

        if not self.is_streaming:
            self.error_occurred.emit("Camera not streaming")
            return None

        if self.latest_frame is None:
            self.error_occurred.emit("No frame available to capture")
            return None

        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}_{timestamp}.png"
            output_path = output_dir / filename

            # Convert to BGR if needed (VmbPy gives RGB, OpenCV saves BGR)
            if len(self.latest_frame.shape) == 3 and self.latest_frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(self.latest_frame, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = self.latest_frame

            # Save image
            cv2.imwrite(str(output_path), frame_bgr)

            logger.info(f"Image captured: {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to capture image: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

    def start_recording(
        self, base_filename: str = "video", output_dir: Optional[Path] = None
    ) -> bool:
        """
        Start video recording.

        Args:
            base_filename: Base filename for video
            output_dir: Output directory (defaults to PROJECT_ROOT/data/videos)

        Returns:
            True if recording started
        """
        if output_dir is None:
            output_dir = PROJECT_ROOT / "data" / "videos"

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

            # Log event
            if self.event_logger:
                from ..core.event_logger import EventType

                self.event_logger.log_event(
                    event_type=EventType.HARDWARE_CAMERA_RECORDING_START,
                    description=f"Video recording started: {filename}",
                    details={"output_path": str(output_path)},
                )

            return True

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

            # Log error event
            if self.event_logger:
                from ..core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.HARDWARE_ERROR,
                    description=error_msg,
                    severity=EventSeverity.WARNING,
                    details={"device": "Allied Vision Camera", "operation": "start_recording"},
                )

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

        # Log event
        if self.event_logger:
            from ..core.event_logger import EventType

            self.event_logger.log_event(
                event_type=EventType.HARDWARE_CAMERA_RECORDING_STOP,
                description="Video recording stopped",
            )

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
            # Use get_feature_by_name (per LESSONS_LEARNED.md)
            self.camera.get_feature_by_name("ExposureTime").set(exposure_us)
            logger.debug(f"Exposure set to {exposure_us} us")
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
            # Use get_feature_by_name (per LESSONS_LEARNED.md)
            self.camera.get_feature_by_name("Gain").set(gain_db)
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
            # Use get_feature_by_name (per LESSONS_LEARNED.md)
            exp_feature = self.camera.get_feature_by_name("ExposureTime")
            return (exp_feature.get_range()[0], exp_feature.get_range()[1])
        except Exception:
            return (0.0, 1000000.0)

    def get_gain_range(self) -> tuple:
        """Get min/max gain values in dB."""
        if not self.camera:
            return (0.0, 24.0)

        try:
            # Use get_feature_by_name (per LESSONS_LEARNED.md)
            gain_feature = self.camera.get_feature_by_name("Gain")
            return (gain_feature.get_range()[0], gain_feature.get_range()[1])
        except Exception:
            return (0.0, 24.0)

    def set_auto_exposure(self, enabled: bool) -> bool:
        """
        Enable or disable auto exposure.

        Args:
            enabled: True to enable auto exposure, False to disable

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            mode = "Continuous" if enabled else "Off"
            self.camera.get_feature_by_name("ExposureAuto").set(mode)
            logger.debug(f"Auto exposure set to {mode}")
            return True
        except Exception as e:
            logger.error(f"Failed to set auto exposure: {e}")
            return False

    def set_auto_gain(self, enabled: bool) -> bool:
        """
        Enable or disable auto gain.

        Args:
            enabled: True to enable auto gain, False to disable

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            mode = "Continuous" if enabled else "Off"
            self.camera.get_feature_by_name("GainAuto").set(mode)
            logger.debug(f"Auto gain set to {mode}")
            return True
        except Exception as e:
            logger.error(f"Failed to set auto gain: {e}")
            return False

    def set_auto_white_balance(self, enabled: bool) -> bool:
        """
        Enable or disable auto white balance.

        Args:
            enabled: True to enable auto white balance, False to disable

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            mode = "Continuous" if enabled else "Off"
            self.camera.get_feature_by_name("BalanceWhiteAuto").set(mode)
            logger.debug(f"Auto white balance set to {mode}")
            return True
        except Exception as e:
            logger.error(f"Failed to set auto white balance: {e}")
            return False

    def get_acquisition_frame_rate_info(self) -> dict:
        """
        Get information about camera's frame rate capabilities.

        Returns:
            Dictionary with min_fps, max_fps, current_fps
        """
        if not self.camera:
            return {"min_fps": 0, "max_fps": 0, "current_fps": 0}

        try:
            fps_feature = self.camera.get_feature_by_name("AcquisitionFrameRate")
            min_fps, max_fps = fps_feature.get_range()
            current_fps = fps_feature.get()
            return {
                "min_fps": min_fps,
                "max_fps": max_fps,
                "current_fps": current_fps,
            }
        except Exception as e:
            logger.error(f"Failed to get frame rate info: {e}")
            return {"min_fps": 0, "max_fps": 0, "current_fps": 0}

    def set_acquisition_frame_rate(self, fps: float) -> bool:
        """
        Set camera's acquisition frame rate.

        Args:
            fps: Desired frames per second

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        try:
            # Enable frame rate control
            self.camera.get_feature_by_name("AcquisitionFrameRateEnable").set(True)

            # Get the valid range for this camera
            fps_feature = self.camera.get_feature_by_name("AcquisitionFrameRate")
            min_fps, max_fps = fps_feature.get_range()

            # Clamp to valid range
            clamped_fps = max(min_fps, min(fps, max_fps))

            if clamped_fps != fps:
                logger.warning(
                    f"Requested FPS {fps} outside valid range "
                    f"[{min_fps:.2f}, {max_fps:.2f}]. Using {clamped_fps:.2f}"
                )

            # Set frame rate
            fps_feature.set(clamped_fps)
            logger.info(f"Camera acquisition frame rate set to {clamped_fps:.2f} FPS")
            return True
        except Exception as e:
            logger.error(f"Failed to set acquisition frame rate: {e}")
            return False
