"""
Camera display and control widget with live view.

Provides:
- Live camera feed with frame updates
- Exposure and gain controls
- Still image capture
- Video recording (manual and auto-record when laser on)
"""

import logging
from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class CameraWidget(QWidget):
    """
    Live camera feed with alignment indicators and controls.

    Features:
    - Real-time camera streaming
    - Exposure and gain adjustment
    - Still image capture with custom filename
    - Manual video recording
    - Auto-record when laser is on (TODO)
    """

    def __init__(self) -> None:
        super().__init__()

        # Camera controller will be injected later
        self.camera_controller = None

        # State
        self.is_connected = False
        self.is_streaming = False
        self.current_fps = 0.0

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self._create_camera_display(), 3)
        layout.addWidget(self._create_control_panel(), 1)

    def _create_camera_display(self) -> QGroupBox:
        """Create camera feed display area."""
        group = QGroupBox("Live Camera Feed")
        layout = QVBoxLayout()

        self.camera_display = QLabel("Camera feed will appear here")
        self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_display.setMinimumSize(800, 600)
        self.camera_display.setStyleSheet(
            "background-color: #2b2b2b; color: #888; font-size: 16px;"
        )
        self.camera_display.setScaledContents(False)
        layout.addWidget(self.camera_display)

        # Status bar
        status_layout = QHBoxLayout()
        self.connection_status = QLabel("Status: Not Connected")
        self.fps_label = QLabel("FPS: --")
        self.recording_indicator = QLabel("")
        self.recording_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")

        status_layout.addWidget(self.connection_status)
        status_layout.addStretch()
        status_layout.addWidget(self.fps_label)
        status_layout.addWidget(self.recording_indicator)

        layout.addLayout(status_layout)

        group.setLayout(layout)
        return group

    def _create_control_panel(self) -> QGroupBox:
        """Create camera control panel."""
        group = QGroupBox("Camera Controls")
        layout = QVBoxLayout()

        # Connection controls
        conn_group = self._create_connection_controls()
        layout.addWidget(conn_group)

        # Camera settings
        settings_group = self._create_camera_settings()
        layout.addWidget(settings_group)

        # Capture controls
        capture_group = self._create_capture_controls()
        layout.addWidget(capture_group)

        # Recording controls
        record_group = self._create_recording_controls()
        layout.addWidget(record_group)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_connection_controls(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection")
        layout = QVBoxLayout()

        self.connect_btn = QPushButton("Connect Camera")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setEnabled(False)
        self.stream_btn.clicked.connect(self._on_stream_clicked)
        layout.addWidget(self.stream_btn)

        group.setLayout(layout)
        return group

    def _create_camera_settings(self) -> QGroupBox:
        """Create camera settings control group."""
        group = QGroupBox("Camera Settings")
        layout = QVBoxLayout()

        # Exposure control
        exp_header = QHBoxLayout()
        exp_header.addWidget(QLabel("Exposure (us):"))
        self.auto_exposure_check = QCheckBox("Auto")
        self.auto_exposure_check.setEnabled(False)
        self.auto_exposure_check.stateChanged.connect(self._on_auto_exposure_changed)
        exp_header.addWidget(self.auto_exposure_check)
        exp_header.addStretch()
        layout.addLayout(exp_header)

        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(100)
        self.exposure_slider.setMaximum(100000)
        self.exposure_slider.setValue(10000)
        self.exposure_slider.setEnabled(False)
        self.exposure_slider.valueChanged.connect(self._on_exposure_changed)
        layout.addWidget(self.exposure_slider)

        exp_value_layout = QHBoxLayout()
        self.exposure_value_label = QLabel("10000 us")
        exp_value_layout.addWidget(self.exposure_value_label)
        self.exposure_input = QLineEdit()
        self.exposure_input.setPlaceholderText("Enter value")
        self.exposure_input.setMaximumWidth(100)
        self.exposure_input.setEnabled(False)
        self.exposure_input.returnPressed.connect(self._on_exposure_input_changed)
        exp_value_layout.addWidget(self.exposure_input)
        exp_value_layout.addStretch()
        layout.addLayout(exp_value_layout)

        # Gain control
        gain_header = QHBoxLayout()
        gain_header.addWidget(QLabel("Gain (dB):"))
        self.auto_gain_check = QCheckBox("Auto")
        self.auto_gain_check.setEnabled(False)
        self.auto_gain_check.stateChanged.connect(self._on_auto_gain_changed)
        gain_header.addWidget(self.auto_gain_check)
        gain_header.addStretch()
        layout.addLayout(gain_header)

        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(240)  # 24.0 dB * 10
        self.gain_slider.setValue(0)
        self.gain_slider.setEnabled(False)
        self.gain_slider.valueChanged.connect(self._on_gain_changed)
        layout.addWidget(self.gain_slider)

        gain_value_layout = QHBoxLayout()
        self.gain_value_label = QLabel("0.0 dB")
        gain_value_layout.addWidget(self.gain_value_label)
        self.gain_input = QLineEdit()
        self.gain_input.setPlaceholderText("Enter value")
        self.gain_input.setMaximumWidth(100)
        self.gain_input.setEnabled(False)
        self.gain_input.returnPressed.connect(self._on_gain_input_changed)
        gain_value_layout.addWidget(self.gain_input)
        gain_value_layout.addStretch()
        layout.addLayout(gain_value_layout)

        # Auto white balance
        wb_layout = QHBoxLayout()
        wb_layout.addWidget(QLabel("White Balance:"))
        self.auto_wb_check = QCheckBox("Auto")
        self.auto_wb_check.setEnabled(False)
        self.auto_wb_check.stateChanged.connect(self._on_auto_wb_changed)
        wb_layout.addWidget(self.auto_wb_check)
        wb_layout.addStretch()
        layout.addLayout(wb_layout)

        group.setLayout(layout)
        return group

    def _create_capture_controls(self) -> QGroupBox:
        """Create image capture control group."""
        group = QGroupBox("Still Image Capture")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Base Filename:"))
        self.image_filename_input = QLineEdit()
        self.image_filename_input.setPlaceholderText("image")
        self.image_filename_input.setText("capture")
        layout.addWidget(self.image_filename_input)

        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setEnabled(False)
        self.capture_btn.clicked.connect(self._on_capture_image)
        layout.addWidget(self.capture_btn)

        self.last_capture_label = QLabel("No images captured")
        self.last_capture_label.setWordWrap(True)
        self.last_capture_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.last_capture_label)

        group.setLayout(layout)
        return group

    def _create_recording_controls(self) -> QGroupBox:
        """Create video recording control group."""
        group = QGroupBox("Video Recording")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Base Filename:"))
        self.video_filename_input = QLineEdit()
        self.video_filename_input.setPlaceholderText("video")
        self.video_filename_input.setText("recording")
        layout.addWidget(self.video_filename_input)

        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setEnabled(False)
        self.record_btn.clicked.connect(self._on_record_clicked)
        layout.addWidget(self.record_btn)

        self.recording_status_label = QLabel("Not recording")
        self.recording_status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.recording_status_label)

        group.setLayout(layout)
        return group

    def set_camera_controller(self, controller: Any) -> None:
        """
        Inject camera controller dependency.

        Args:
            controller: CameraController instance
        """
        self.camera_controller = controller

        # Connect signals
        controller.frame_ready.connect(self._on_frame_received)
        controller.fps_update.connect(self._on_fps_update)
        controller.connection_changed.connect(self._on_connection_changed)
        controller.error_occurred.connect(self._on_error)
        controller.recording_status_changed.connect(self._on_recording_status_changed)

        logger.info("Camera controller connected to widget")

    # Event handlers
    def _on_connect_clicked(self) -> None:
        """Handle connect/disconnect button click."""
        if not self.camera_controller:
            return

        if self.is_connected:
            self.camera_controller.disconnect()
        else:
            success = self.camera_controller.connect()
            if success:
                # Update slider ranges from camera
                exp_min, exp_max = self.camera_controller.get_exposure_range()
                self.exposure_slider.setMinimum(int(exp_min))
                self.exposure_slider.setMaximum(int(exp_max))

                gain_min, gain_max = self.camera_controller.get_gain_range()
                self.gain_slider.setMinimum(int(gain_min * 10))
                self.gain_slider.setMaximum(int(gain_max * 10))

    def _on_stream_clicked(self) -> None:
        """Handle start/stop streaming button click."""
        if not self.camera_controller:
            return

        if self.is_streaming:
            self.camera_controller.stop_streaming()
            self.is_streaming = False
            self.stream_btn.setText("Start Streaming")
            self.capture_btn.setEnabled(False)
            self.record_btn.setEnabled(False)
            self.exposure_slider.setEnabled(False)
            self.gain_slider.setEnabled(False)
            self.exposure_input.setEnabled(False)
            self.gain_input.setEnabled(False)
            self.auto_exposure_check.setEnabled(False)
            self.auto_gain_check.setEnabled(False)
            self.auto_wb_check.setEnabled(False)
        else:
            success = self.camera_controller.start_streaming()
            if success:
                self.is_streaming = True
                self.stream_btn.setText("Stop Streaming")
                self.capture_btn.setEnabled(True)
                self.record_btn.setEnabled(True)
                self.exposure_slider.setEnabled(True)
                self.gain_slider.setEnabled(True)
                self.exposure_input.setEnabled(True)
                self.gain_input.setEnabled(True)
                self.auto_exposure_check.setEnabled(True)
                self.auto_gain_check.setEnabled(True)
                self.auto_wb_check.setEnabled(True)

    def _on_exposure_changed(self, value: int) -> None:
        """Handle exposure slider change."""
        if self.camera_controller:
            self.camera_controller.set_exposure(float(value))
            self.exposure_value_label.setText(f"{value} us")
            self.exposure_input.setText(str(value))

    def _on_exposure_input_changed(self) -> None:
        """Handle exposure input box change."""
        try:
            value = int(self.exposure_input.text())
            self.exposure_slider.setValue(value)
        except ValueError:
            logger.warning(f"Invalid exposure value: {self.exposure_input.text()}")

    def _on_gain_changed(self, value: int) -> None:
        """Handle gain slider change."""
        if self.camera_controller:
            gain_db = value / 10.0
            self.camera_controller.set_gain(gain_db)
            self.gain_value_label.setText(f"{gain_db:.1f} dB")
            self.gain_input.setText(f"{gain_db:.1f}")

    def _on_gain_input_changed(self) -> None:
        """Handle gain input box change."""
        try:
            gain_db = float(self.gain_input.text())
            value = int(gain_db * 10)
            self.gain_slider.setValue(value)
        except ValueError:
            logger.warning(f"Invalid gain value: {self.gain_input.text()}")

    def _on_auto_exposure_changed(self, state: int) -> None:
        """Handle auto exposure checkbox change."""
        # TODO: Implement auto exposure via camera controller
        logger.info(f"Auto exposure {'enabled' if state else 'disabled'}")
        if state:
            self.exposure_slider.setEnabled(False)
            self.exposure_input.setEnabled(False)
        else:
            self.exposure_slider.setEnabled(True)
            self.exposure_input.setEnabled(True)

    def _on_auto_gain_changed(self, state: int) -> None:
        """Handle auto gain checkbox change."""
        # TODO: Implement auto gain via camera controller
        logger.info(f"Auto gain {'enabled' if state else 'disabled'}")
        if state:
            self.gain_slider.setEnabled(False)
            self.gain_input.setEnabled(False)
        else:
            self.gain_slider.setEnabled(True)
            self.gain_input.setEnabled(True)

    def _on_auto_wb_changed(self, state: int) -> None:
        """Handle auto white balance checkbox change."""
        # TODO: Implement auto white balance via camera controller
        logger.info(f"Auto white balance {'enabled' if state else 'disabled'}")

    def _on_capture_image(self) -> None:
        """Handle capture image button click."""
        # TODO: Implement actual image capture
        # For now, just save current frame
        logger.info("Image capture requested - feature pending implementation")
        self.last_capture_label.setText("Feature pending implementation")

    def _on_record_clicked(self) -> None:
        """Handle record button click."""
        if not self.camera_controller:
            return

        if self.camera_controller.is_recording:
            self.camera_controller.stop_recording()
        else:
            base_filename = self.video_filename_input.text() or "recording"
            self.camera_controller.start_recording(base_filename)

    # Slots for camera controller signals
    @pyqtSlot(np.ndarray)
    def _on_frame_received(self, frame: np.ndarray) -> None:
        """
        Update display with new frame.

        Args:
            frame: Numpy array frame from camera
        """
        try:
            # Convert to QImage
            if len(frame.shape) == 2:
                # Grayscale
                height, width = frame.shape
                bytes_per_line = width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
                )
            else:
                # RGB
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )

            # Convert to pixmap and display
            pixmap = QPixmap.fromImage(q_image)

            # Scale to fit display while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.camera_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.camera_display.setPixmap(scaled_pixmap)

        except Exception as e:
            logger.error(f"Error displaying frame: {e}")

    @pyqtSlot(float)
    def _on_fps_update(self, fps: float) -> None:
        """Update FPS display."""
        self.current_fps = fps
        self.fps_label.setText(f"FPS: {fps:.1f}")

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected

        if connected:
            self.connection_status.setText("Status: Connected")
            self.connection_status.setStyleSheet("color: green;")
            self.connect_btn.setText("Disconnect")
            self.stream_btn.setEnabled(True)
        else:
            self.connection_status.setText("Status: Not Connected")
            self.connection_status.setStyleSheet("color: red;")
            self.connect_btn.setText("Connect Camera")
            self.stream_btn.setEnabled(False)
            self.capture_btn.setEnabled(False)
            self.record_btn.setEnabled(False)
            self.camera_display.clear()
            self.camera_display.setText("Camera feed will appear here")

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from camera controller."""
        logger.error(f"Camera error: {error_msg}")
        self.connection_status.setText(f"Error: {error_msg}")
        self.connection_status.setStyleSheet("color: red;")

    @pyqtSlot(bool)
    def _on_recording_status_changed(self, recording: bool) -> None:
        """Handle recording status change."""
        if recording:
            self.record_btn.setText("Stop Recording")
            self.recording_indicator.setText("● REC")
            self.recording_status_label.setText("Recording...")
            self.recording_status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.record_btn.setText("Start Recording")
            self.recording_indicator.setText("")
            self.recording_status_label.setText("Not recording")
            self.recording_status_label.setStyleSheet("color: #666; font-size: 10px;")
