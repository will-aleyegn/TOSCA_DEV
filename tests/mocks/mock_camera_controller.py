"""
Mock implementation of CameraController for testing.

Simulates camera behavior including streaming, recording, and frame generation.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from tests.mocks.mock_qobject_base import MockQObjectBase


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

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock camera controller."""
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

    def connect(self, camera_id: Optional[str] = None) -> bool:
        """Simulate connecting to camera."""
        self._log_call("connect", camera_id=camera_id)
        self._apply_delay()

        if self.simulate_connection_failure:
            self.error_occurred.emit("Failed to connect (simulated)")
            return False

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

    def stop_streaming(self) -> None:
        """Simulate stopping video stream."""
        self._log_call("stop_streaming")
        self.is_streaming = False
        self._frame_timer.stop()

    def _generate_frame(self) -> None:
        """Generate and emit simulated camera frame."""
        if not self.is_streaming:
            return

        frame = np.random.randint(0, 255, size=self.simulated_frame_shape, dtype=np.uint8)
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

    def stop_recording(self) -> None:
        """Simulate stopping recording."""
        self._log_call("stop_recording")
        self.is_recording = False
        self.recording_status_changed.emit(False)

    def set_exposure(self, exposure_us: float) -> bool:
        """Simulate setting camera exposure."""
        self._log_call("set_exposure", exposure_us=exposure_us)
        self.exposure_us = exposure_us
        return True

    def set_gain(self, gain_db: float) -> bool:
        """Simulate setting camera gain."""
        self._log_call("set_gain", gain_db=gain_db)
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
