# -*- coding: utf-8 -*-
"""
Camera hardware abstraction layer for Allied Vision cameras.

Provides PyQt6-integrated camera control with:
- Live streaming with Qt signals
- Exposure and gain control
- Still image capture
- Video recording
- Thread-safe camera operations
"""

import logging
import threading
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
                logger.debug("Frame callback called but running=False")
                return

            try:
                # Convert frame to numpy array
                self.frame_count += 1
                current_time = time.time()

                # Debug: Log first few frames
                if self.frame_count <= 5:
                    logger.info(f"Frame callback invoked: frame #{self.frame_count}")

                # Throttle GUI updates to target FPS
                time_since_last_gui_frame = current_time - self.last_gui_frame_time
                min_frame_interval = 1.0 / self.gui_fps_target

                if time_since_last_gui_frame >= min_frame_interval:
                    # Convert frame to numpy array
                    frame_data = frame.as_numpy_ndarray()

                    # Convert to RGB8 format for consistent GUI display
                    # Handle various pixel formats from camera
                    try:
                        pixel_format = frame.get_pixel_format()

                        # Convert based on pixel format
                        if pixel_format == vmbpy.PixelFormat.Mono8:
                            # Grayscale -> RGB (duplicate to 3 channels)
                            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_GRAY2RGB)
                        elif pixel_format == vmbpy.PixelFormat.Bgr8:
                            # BGR -> RGB (OpenCV uses BGR, Qt needs RGB)
                            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
                        elif pixel_format == vmbpy.PixelFormat.Rgb8:
                            # Already RGB, just ensure contiguous
                            frame_rgb = np.ascontiguousarray(frame_data)
                        elif pixel_format in (
                            vmbpy.PixelFormat.BayerRG8,
                            vmbpy.PixelFormat.BayerGR8,
                            vmbpy.PixelFormat.BayerGB8,
                            vmbpy.PixelFormat.BayerBG8,
                        ):
                            # Bayer pattern -> RGB (debayering)
                            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BayerRG2RGB)
                        elif pixel_format == vmbpy.PixelFormat.YUV422Packed:
                            # YUV -> RGB
                            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_YUV2RGB_UYVY)
                        else:
                            # Unsupported format - log warning and use as-is
                            logger.warning(
                                f"Unsupported pixel format {pixel_format}, using raw data"
                            )
                            frame_rgb = np.ascontiguousarray(frame_data)

                        # Debug: Log first few GUI frames with format info
                        if self.gui_frame_count < 5:
                            logger.info(
                                f"Emitting frame to GUI: #{self.gui_frame_count + 1}, "
                                f"format: {pixel_format}, shape: {frame_rgb.shape}"
                            )

                    except Exception as conv_e:
                        # Conversion failed - log error and use raw data as fallback
                        logger.error(f"Pixel format conversion failed: {conv_e}, using raw data")
                        frame_rgb = np.ascontiguousarray(frame_data)

                    # Emit frame to GUI (no copy needed - Qt signals handle data safely)
                    self.frame_ready.emit(frame_rgb)
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
    exposure_changed = pyqtSignal(float)  # Emits new exposure in µs (thread-safe)
    gain_changed = pyqtSignal(float)  # Emits new gain in dB (thread-safe)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()

        if not VMBPY_AVAILABLE:
            raise ImportError("VmbPy is not installed - camera features unavailable")

        # Thread safety lock for camera operations (reentrant for nested calls)
        self._lock = threading.RLock()

        self.vmb = vmbpy.VmbSystem.get_instance()
        self.camera: Optional["vmbpy.Camera"] = None
        self.stream_thread: Optional[CameraStreamThread] = None
        self.video_recorder: Optional[VideoRecorder] = None
        self.is_connected = False
        self.is_streaming = False
        self.is_recording = False
        self.event_logger = event_logger
        self._vmb_context_active = False  # Track VmbSystem context state

        # Store latest frame for image capture
        self.latest_frame: Optional[np.ndarray] = None

        logger.info("Camera controller initialized (thread-safe)")

    def connect(self, camera_id: Optional[str] = None) -> bool:
        """
        Connect to camera.

        Args:
            camera_id: Optional camera ID. If None, connects to first available.

        Returns:
            True if connected successfully
        """
        with self._lock:
            try:
                # Enter VmbSystem context (stays active until disconnect)
                if not self._vmb_context_active:
                    self.vmb.__enter__()
                    self._vmb_context_active = True
                    logger.debug("VmbSystem context entered")

                # Discover cameras
                cameras = self.vmb.get_all_cameras()
                if not cameras:
                    self.error_occurred.emit("No cameras detected")
                    # Exit VmbSystem context since we're not connecting
                    if self._vmb_context_active:
                        self.vmb.__exit__(None, None, None)
                        self._vmb_context_active = False
                    return False

                if camera_id:
                    camera = self.vmb.get_camera_by_id(camera_id)
                else:
                    camera = cameras[0]

                # Open camera-specific context (stays open during streaming)
                self.camera = camera
                self.camera.__enter__()
                self.is_connected = True

                # Set explicit pixel format for predictable streaming (per Allied Vision docs)
                try:
                    supported_formats = self.camera.get_pixel_formats()
                    # Prefer Bgr8 (native OpenCV format) > Rgb8 > Mono8
                    if vmbpy.PixelFormat.Bgr8 in supported_formats:
                        self.camera.set_pixel_format(vmbpy.PixelFormat.Bgr8)
                        logger.info("Camera pixel format set to Bgr8 (native OpenCV format)")
                    elif vmbpy.PixelFormat.Rgb8 in supported_formats:
                        self.camera.set_pixel_format(vmbpy.PixelFormat.Rgb8)
                        logger.info("Camera pixel format set to Rgb8")
                    elif vmbpy.PixelFormat.Mono8 in supported_formats:
                        self.camera.set_pixel_format(vmbpy.PixelFormat.Mono8)
                        logger.info("Camera pixel format set to Mono8")
                    else:
                        current_fmt = self.camera.get_pixel_format()
                        logger.warning(f"Using camera default pixel format: {current_fmt}")
                except Exception as e:
                    logger.error(f"Failed to set pixel format: {e}")

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

                # Clean up contexts on failure
                if self.camera:
                    try:
                        self.camera.__exit__(None, None, None)
                    except Exception as cleanup_e:
                        logger.warning(f"Error during camera cleanup: {cleanup_e}")
                    self.camera = None

                # Exit VmbSystem context if it was entered
                if self._vmb_context_active:
                    try:
                        self.vmb.__exit__(None, None, None)
                        self._vmb_context_active = False
                    except Exception as cleanup_e:
                        logger.warning(f"Error during VmbPy cleanup: {cleanup_e}")
                        self._vmb_context_active = False

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
        with self._lock:
            self.stop_streaming()

            # Close camera context (camera-specific cleanup)
            if self.camera:
                try:
                    self.camera.__exit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Ignoring error during camera cleanup: {e}")
                self.camera = None

            # Exit VmbSystem context (opened during connect)
            if self._vmb_context_active:
                try:
                    self.vmb.__exit__(None, None, None)
                    self._vmb_context_active = False
                    logger.debug("VmbSystem context exited")
                except Exception as e:
                    logger.warning(f"Error exiting VmbSystem context: {e}")
                    self._vmb_context_active = False

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

    def get_status(self) -> dict[str, Any]:
        """
        Get current camera status and state information.

        Returns:
            Dictionary containing:
            - connected (bool): Connection status
            - streaming (bool): Streaming state
            - recording (bool): Recording state
            - camera_id (str | None): Camera identifier if connected
            - frame_rate (float | None): Current FPS if streaming
        """
        with self._lock:
            status: dict[str, Any] = {
                "connected": self.is_connected,
                "streaming": self.is_streaming,
                "recording": self.is_recording,
                "camera_id": None,
                "frame_rate": None,
            }

            if self.is_connected and self.camera:
                try:
                    status["camera_id"] = self.camera.get_id()
                except Exception:
                    pass

            if self.is_streaming and self.stream_thread:
                status["frame_rate"] = getattr(self.stream_thread, "current_fps", None)

            return status

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

        with self._lock:
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
        with self._lock:
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
        with self._lock:
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

        with self._lock:
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

                # Log event
                if self.event_logger:
                    from ..core.event_logger import EventType

                    self.event_logger.log_event(
                        event_type=EventType.HARDWARE_CAMERA_CAPTURE,
                        description=f"Image captured: {filename}",
                        details={"output_path": str(output_path)},
                    )

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

        with self._lock:
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
        with self._lock:
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
        Set camera exposure time (thread-safe).

        Args:
            exposure_us: Exposure time in microseconds

        Returns:
            True if successful
        """
        with self._lock:
            if not self.camera:
                return False

            try:
                # Use property pattern (cleaner VmbPy API)
                self.camera.ExposureTime.set(exposure_us)

                # Read back actual value and emit signal
                actual_exposure = self.camera.ExposureTime.get()
                logger.debug(f"Exposure set to {actual_exposure} us (requested: {exposure_us})")
                self.exposure_changed.emit(actual_exposure)
                return True
            except Exception as e:
                logger.error(f"Failed to set exposure: {e}")
                return False

    def set_gain(self, gain_db: float) -> bool:
        """
        Set camera gain (thread-safe).

        Args:
            gain_db: Gain in dB

        Returns:
            True if successful
        """
        with self._lock:
            if not self.camera:
                return False

            try:
                # Use property pattern (cleaner VmbPy API)
                self.camera.Gain.set(gain_db)

                # Read back actual value and emit signal
                actual_gain = self.camera.Gain.get()
                logger.debug(f"Gain set to {actual_gain} dB (requested: {gain_db})")
                self.gain_changed.emit(actual_gain)
                return True
            except Exception as e:
                logger.error(f"Failed to set gain: {e}")
                return False

    def get_exposure(self) -> float:
        """
        Get current camera exposure time (thread-safe).

        Returns:
            Current exposure time in microseconds, or 0.0 if not connected
        """
        with self._lock:
            if not self.camera:
                return 0.0

            try:
                return self.camera.ExposureTime.get()
            except Exception as e:
                logger.error(f"Failed to get exposure: {e}")
                return 0.0

    def get_gain(self) -> float:
        """
        Get current camera gain (thread-safe).

        Returns:
            Current gain in dB, or 0.0 if not connected
        """
        with self._lock:
            if not self.camera:
                return 0.0

            try:
                return self.camera.Gain.get()
            except Exception as e:
                logger.error(f"Failed to get gain: {e}")
                return 0.0

    def get_exposure_range(self) -> tuple:
        """Get min/max exposure values in microseconds."""
        if not self.camera:
            return (0.0, 1000000.0)

        try:
            # Use property pattern (cleaner VmbPy API)
            min_val, max_val = self.camera.ExposureTime.get_range()
            return (min_val, max_val)
        except Exception:
            return (0.0, 1000000.0)

    def get_gain_range(self) -> tuple:
        """Get min/max gain values in dB."""
        if not self.camera:
            return (0.0, 24.0)

        try:
            # Use property pattern (cleaner VmbPy API)
            min_val, max_val = self.camera.Gain.get_range()
            return (min_val, max_val)
        except Exception:
            return (0.0, 24.0)

    def set_binning(self, binning_factor: int) -> bool:
        """
        Set camera binning to increase frame rate.

        Binning combines adjacent pixels, trading resolution for speed.
        Higher binning = lower resolution but faster frame rate.

        Args:
            binning_factor: Binning multiplier (1=full res, 2=2x2, 4=4x4, 8=8x8)

        Returns:
            True if successful
        """
        if not self.camera:
            return False

        if binning_factor not in [1, 2, 4, 8]:
            logger.error(f"Invalid binning factor: {binning_factor}. Must be 1, 2, 4, or 8")
            return False

        try:
            # Set horizontal and vertical binning (property pattern)
            self.camera.BinningHorizontal.set(binning_factor)
            self.camera.BinningVertical.set(binning_factor)
            logger.info(f"Camera binning set to {binning_factor}×{binning_factor}")
            return True
        except Exception as e:
            logger.error(f"Failed to set binning: {e}")
            return False

    def get_binning(self) -> int:
        """
        Get current binning factor.

        Returns:
            Current binning factor (1, 2, 4, or 8)
        """
        if not self.camera:
            return 1

        try:
            # Read horizontal binning (vertical should match)
            binning = int(self.camera.BinningHorizontal.get())
            return binning
        except Exception:
            return 1

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
            self.camera.ExposureAuto.set(mode)
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
            self.camera.GainAuto.set(mode)
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
            self.camera.BalanceWhiteAuto.set(mode)
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
            # Use property pattern
            min_fps, max_fps = self.camera.AcquisitionFrameRate.get_range()
            current_fps = self.camera.AcquisitionFrameRate.get()
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
            # Enable frame rate control (property pattern)
            self.camera.AcquisitionFrameRateEnable.set(True)

            # Get the valid range for this camera
            min_fps, max_fps = self.camera.AcquisitionFrameRate.get_range()

            # Clamp to valid range
            clamped_fps = max(min_fps, min(fps, max_fps))

            if clamped_fps != fps:
                logger.warning(
                    f"Requested FPS {fps} outside valid range "
                    f"[{min_fps:.2f}, {max_fps:.2f}]. Using {clamped_fps:.2f}"
                )

            # Set frame rate
            self.camera.AcquisitionFrameRate.set(clamped_fps)
            logger.info(f"Camera acquisition frame rate set to {clamped_fps:.2f} FPS")
            return True
        except Exception as e:
            logger.error(f"Failed to set acquisition frame rate: {e}")
            return False
