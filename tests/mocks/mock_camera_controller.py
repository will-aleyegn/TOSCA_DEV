"""
Mock implementation of CameraController for testing.

Simulates camera behavior including streaming, recording, VmbPy API compliance,
and advanced features like pixel formats, binning, and trigger modes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

import numpy as np
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


class MockPixelFormat(Enum):
    """Mock pixel format enumeration matching VmbPy API."""

    Bgr8 = "Bgr8"
    Rgb8 = "Rgb8"
    Mono8 = "Mono8"


class MockTriggerMode(Enum):
    """Mock trigger mode enumeration."""

    Continuous = "Continuous"
    Software = "Software"
    Hardware = "Hardware"


class MockAcquisitionMode(Enum):
    """Mock acquisition mode enumeration."""

    Continuous = "Continuous"
    SingleFrame = "SingleFrame"
    MultiFrame = "MultiFrame"


class MockCameraController(MockQObjectBase):
    """
    Mock implementation of CameraController.

    Simulates camera behavior for testing without physical hardware.
    Supports connection simulation, frame generation, and recording.
    """

    # Signals matching CameraController interface
    frame_ready = pyqtSignal(np.ndarray)
    fps_update = pyqtSignal(float)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    recording_status_changed = pyqtSignal(bool)

    # Additional VmbPy-specific signals
    pixel_format_changed = pyqtSignal(object)  # MockPixelFormat
    binning_changed = pyqtSignal(int)
    trigger_mode_changed = pyqtSignal(object)  # MockTriggerMode
    acquisition_mode_changed = pyqtSignal(object)  # MockAcquisitionMode

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock camera controller."""
        # Initialize base dimensions first (needed by reset())
        self._base_width: int = 640
        self._base_height: int = 480

        super().__init__(parent)

        # Frame simulation settings
        self.simulated_fps: int = 30
        self.simulated_frame_shape: tuple[int, int, int] = (480, 640, 3)

        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self._generate_frame)

        # State set by reset()
        self.reset()

    def reset(self) -> None:
        """Reset mock to clean state."""
        super().reset()
        if hasattr(self, "_frame_timer") and self._frame_timer.isActive():
            self._frame_timer.stop()

        # State attributes matching CameraController
        self.is_connected: bool = False
        self.is_streaming: bool = False
        self.is_recording: bool = False
        self.latest_frame: Optional[np.ndarray] = None
        self.exposure_us: float = 1000.0
        self.gain_db: float = 10.0

        # VmbPy API attributes
        self.pixel_format: MockPixelFormat = MockPixelFormat.Bgr8
        self.binning_factor: int = 1
        self.binning: int = 1  # Alias for test compatibility
        self.trigger_mode: MockTriggerMode = MockTriggerMode.Continuous
        self.acquisition_mode: MockAcquisitionMode = MockAcquisitionMode.Continuous
        self.hardware_fps: float = 30.0

        # Update frame shape based on current settings
        self._update_frame_shape()

    def connect(self, camera_id: Optional[str] = None) -> bool:
        """Simulate connecting to camera."""
        self._log_call("connect", camera_id=camera_id)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            return False

        # Store camera_id as instance attribute
        self.camera_id = camera_id if camera_id is not None else "DEV_MOCK_001"

        self.is_connected = True
        self.connection_changed.emit(True)
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from camera."""
        self._log_call("disconnect")
        self.stop_streaming()
        self.stop_recording()
        self.is_connected = False
        self.connection_changed.emit(False)

    def start_streaming(self) -> bool:
        """Simulate starting video stream."""
        self._log_call("start_streaming")
        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.is_streaming = True
        self._frame_timer.start(int(1000 / self.simulated_fps))
        return True

    def stop_streaming(self) -> bool:
        """Simulate stopping video stream."""
        self._log_call("stop_streaming")

        if not self.is_connected:
            return False

        if not self.is_streaming:
            return False

        self.is_streaming = False
        self._frame_timer.stop()
        return True

    def _generate_frame(self) -> None:
        """
        Generate and emit simulated camera frame.

        Respects current pixel format and binning settings.
        Generates realistic frame data with proper numpy dtypes.
        """
        if not self.is_streaming:
            return

        # Generate frame with correct shape based on pixel format
        frame = np.random.randint(0, 255, size=self.simulated_frame_shape, dtype=np.uint8)

        # Ensure memory is contiguous (VmbPy requirement)
        frame = np.ascontiguousarray(frame)

        self.latest_frame = frame
        self.frame_ready.emit(frame)
        self.fps_update.emit(float(self.simulated_fps))

    def capture_image(self, filename: str) -> bool:
        """Simulate capturing single image."""
        self._log_call("capture_image", filename=filename)
        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False
        return True

    def start_recording(self, filename: str) -> bool:
        """Simulate starting recording."""
        self._log_call("start_recording", filename=filename)
        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.is_recording = True
        self.recording_status_changed.emit(True)
        return True

    def stop_recording(self) -> bool:
        """Simulate stopping recording."""
        self._log_call("stop_recording")

        if not self.is_recording:
            return False

        self.is_recording = False
        self.recording_status_changed.emit(False)
        return True

    def set_exposure(self, exposure_us: float) -> bool:
        """Simulate setting camera exposure."""
        self._log_call("set_exposure", exposure_us=exposure_us)

        if not self.is_connected or self.simulate_operation_error:
            if self.simulate_operation_error:
                self.error_occurred.emit(self.error_message)
            return False

        self.exposure_us = exposure_us
        return True

    def set_gain(self, gain_db: float) -> bool:
        """Simulate setting camera gain."""
        self._log_call("set_gain", gain_db=gain_db)

        if not self.is_connected or self.simulate_operation_error:
            if self.simulate_operation_error:
                self.error_occurred.emit(self.error_message)
            return False

        self.gain_db = gain_db
        return True

    def get_exposure_range(self) -> tuple[float, float]:
        """Return simulated exposure range."""
        self._log_call("get_exposure_range")
        return (100.0, 10000.0)

    def get_gain_range(self) -> tuple[float, float]:
        """Return simulated gain range."""
        self._log_call("get_gain_range")
        return (0.0, 40.0)

    # VmbPy API compliance methods

    def set_pixel_format(self, pixel_format: MockPixelFormat) -> bool:
        """
        Simulate setting camera pixel format.

        Args:
            pixel_format: Pixel format (Bgr8, Rgb8, Mono8) - can be enum or string

        Returns:
            True if successful
        """
        self._log_call("set_pixel_format", pixel_format=pixel_format)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Store original format (string or enum) for test compatibility
        self.pixel_format = pixel_format

        # Convert to enum for internal logic if needed
        if isinstance(pixel_format, str):
            pixel_format_enum = MockPixelFormat(pixel_format)
        else:
            pixel_format_enum = pixel_format

        # Store enum version for shape calculations
        self._pixel_format_enum = pixel_format_enum

        self._update_frame_shape()
        self.pixel_format_changed.emit(pixel_format)
        return True

    def get_pixel_format(self) -> MockPixelFormat:
        """
        Get current pixel format.

        Returns:
            Current pixel format
        """
        self._log_call("get_pixel_format")
        return self.pixel_format

    def set_binning(self, binning_factor: int) -> bool:
        """
        Simulate setting camera binning factor.

        Args:
            binning_factor: Binning factor (1, 2, 4, 8)

        Returns:
            True if successful
        """
        self._log_call("set_binning", binning_factor=binning_factor)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Validate binning factor
        if binning_factor not in [1, 2, 4, 8]:
            self.error_occurred.emit(f"Invalid binning factor: {binning_factor}")
            return False

        self.binning_factor = binning_factor
        self.binning = binning_factor  # Update alias
        self._update_frame_shape()
        self.binning_changed.emit(binning_factor)
        return True

    def get_binning(self) -> int:
        """
        Get current binning factor.

        Returns:
            Current binning factor
        """
        self._log_call("get_binning")
        return self.binning_factor

    def set_trigger_mode(self, trigger_mode: MockTriggerMode) -> bool:
        """
        Simulate setting camera trigger mode.

        Args:
            trigger_mode: Trigger mode (Continuous, Software, Hardware)

        Returns:
            True if successful
        """
        self._log_call("set_trigger_mode", trigger_mode=trigger_mode)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.trigger_mode = trigger_mode
        self.trigger_mode_changed.emit(trigger_mode)
        return True

    def get_trigger_mode(self) -> MockTriggerMode:
        """
        Get current trigger mode.

        Returns:
            Current trigger mode
        """
        self._log_call("get_trigger_mode")
        return self.trigger_mode

    def set_acquisition_mode(self, acquisition_mode: MockAcquisitionMode) -> bool:
        """
        Simulate setting camera acquisition mode.

        Args:
            acquisition_mode: Acquisition mode (Continuous, SingleFrame, MultiFrame)

        Returns:
            True if successful
        """
        self._log_call("set_acquisition_mode", acquisition_mode=acquisition_mode)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        self.acquisition_mode = acquisition_mode
        self.acquisition_mode_changed.emit(acquisition_mode)
        return True

    def get_acquisition_mode(self) -> MockAcquisitionMode:
        """
        Get current acquisition mode.

        Returns:
            Current acquisition mode
        """
        self._log_call("get_acquisition_mode")
        return self.acquisition_mode

    def set_hardware_fps(self, fps: float) -> bool:
        """
        Simulate setting hardware frame rate.

        Args:
            fps: Target frame rate in FPS

        Returns:
            True if successful
        """
        self._log_call("set_hardware_fps", fps=fps)
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Validate FPS range (typical camera limits)
        if fps < 1.0 or fps > 120.0:
            self.error_occurred.emit(f"FPS {fps} outside valid range (1-120)")
            return False

        self.hardware_fps = fps
        self.simulated_fps = int(fps)

        # Update timer if streaming
        if self.is_streaming:
            self._frame_timer.stop()
            self._frame_timer.start(int(1000 / self.simulated_fps))

        return True

    def get_hardware_fps(self) -> float:
        """
        Get current hardware frame rate.

        Returns:
            Current hardware FPS
        """
        self._log_call("get_hardware_fps")
        return self.hardware_fps

    def trigger_software_frame(self) -> bool:
        """
        Simulate software trigger for single frame capture.

        Returns:
            True if successful
        """
        self._log_call("trigger_software_frame")
        self._apply_delay()

        if not self.is_connected or self.simulate_operation_error:
            self.error_occurred.emit(self.error_message)
            return False

        # Handle both enum and string comparison for test compatibility
        if self.trigger_mode != MockTriggerMode.Software and self.trigger_mode != "Software":
            self.error_occurred.emit("Camera not in software trigger mode")
            return False

        # Generate single frame (even when not streaming)
        frame = np.random.randint(0, 255, size=self.simulated_frame_shape, dtype=np.uint8)
        frame = np.ascontiguousarray(frame)
        self.latest_frame = frame
        self.frame_ready.emit(frame)
        self.fps_update.emit(float(self.simulated_fps))
        return True

    def trigger_frame(self) -> bool:
        """Alias for trigger_software_frame for test compatibility."""
        return self.trigger_software_frame()

    def _update_frame_shape(self) -> None:
        """Update simulated frame shape based on pixel format and binning."""
        # Calculate binned dimensions
        width = self._base_width // self.binning_factor
        height = self._base_height // self.binning_factor

        # Update shape based on pixel format (use enum version if available)
        pixel_format_to_check = getattr(self, '_pixel_format_enum', self.pixel_format)

        # Handle both enum and string comparison
        if pixel_format_to_check == MockPixelFormat.Mono8 or pixel_format_to_check == "Mono8":
            self.simulated_frame_shape = (height, width)  # Grayscale (2D)
        else:
            self.simulated_frame_shape = (height, width, 3)  # Color (3D)
