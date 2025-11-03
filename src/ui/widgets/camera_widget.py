"""
Camera display and control widget with live view.

Provides:
- Live camera feed with frame updates
- Exposure and gain controls
- Still image capture
- Video recording (manual and auto-record when laser on)
"""

import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
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
    """

    # Signal emitted when a new frame is ready for display
    # Other widgets can connect to this to display the same camera feed
    pixmap_ready = pyqtSignal(QPixmap)

    def __init__(self, camera_controller: Optional[Any] = None) -> None:
        super().__init__()

        # Reference to CameraController (created and managed by MainWindow)
        self.camera_controller = camera_controller

        # State
        self.is_connected = False
        self.is_streaming = False
        self.current_fps = 0.0
        self.dev_mode = False
        self.custom_video_path: Optional[Path] = None
        self.custom_image_path: Optional[Path] = None

        self._init_ui()

        # Connect to controller signals if controller provided
        if self.camera_controller:
            self._connect_controller_signals()

    def _connect_controller_signals(self) -> None:
        """Connect to controller signals (called when controller is injected)."""
        if not self.camera_controller:
            return

        # PERFORMANCE: Use pixmap_ready for GUI display (pre-converted in camera thread)
        # NOTE: frame_ready NOT connected - numpy arrays only emitted when recording (future feature)
        self.camera_controller.pixmap_ready.connect(self._on_pixmap_received)
        self.camera_controller.fps_update.connect(self._on_fps_update)
        self.camera_controller.connection_changed.connect(self._on_connection_changed)
        self.camera_controller.error_occurred.connect(self._on_error)
        self.camera_controller.recording_status_changed.connect(self._on_recording_status_changed)
        # Connect camera setting signals for hardware feedback loop
        self.camera_controller.exposure_changed.connect(self._on_exposure_hardware_changed)
        self.camera_controller.gain_changed.connect(self._on_gain_hardware_changed)
        logger.debug("CameraWidget signals connected to CameraController")

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
        self.camera_display.setMinimumSize(
            640, 480
        )  # Reduced from 800x600 for better layout proportions
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

        # Camera settings info bar
        settings_layout = QHBoxLayout()
        self.exposure_info = QLabel("Exposure: --")
        self.exposure_info.setStyleSheet("color: #888; font-size: 10px;")
        self.gain_info = QLabel("Gain: --")
        self.gain_info.setStyleSheet("color: #888; font-size: 10px;")
        self.resolution_info = QLabel("Resolution: --")
        self.resolution_info.setStyleSheet("color: #888; font-size: 10px;")

        settings_layout.addWidget(self.exposure_info)
        settings_layout.addWidget(QLabel("|"))
        settings_layout.addWidget(self.gain_info)
        settings_layout.addWidget(QLabel("|"))
        settings_layout.addWidget(self.resolution_info)
        settings_layout.addStretch()

        layout.addLayout(settings_layout)

        group.setLayout(layout)
        return group

    def _create_control_panel(self) -> QGroupBox:
        """Create camera control panel."""
        group = QGroupBox("Camera Controls")
        layout = QVBoxLayout()

        # Constrain maximum width for compact controls
        group.setMaximumWidth(350)

        # Connection controls
        self.connection_controls_group = self._create_connection_controls()
        layout.addWidget(self.connection_controls_group)

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

    def hide_connection_controls(self) -> None:
        """
        Hide connection controls (for use in non-hardware tabs).

        Connection should only be managed from Hardware & Diagnostics tab.
        Other tabs (Treatment Workflow, Protocol Builder) should only use
        already-connected hardware.
        """
        if hasattr(self, "connection_controls_group"):
            self.connection_controls_group.setVisible(False)
            logger.info("Camera connection controls hidden (non-hardware tab)")

    def show_connection_controls(self) -> None:
        """Show connection controls (for use in Hardware & Diagnostics tab)."""
        if hasattr(self, "connection_controls_group"):
            self.connection_controls_group.setVisible(True)
            logger.info("Camera connection controls shown (hardware tab)")

    def connect_camera(self) -> bool:
        """
        Public API: Connect to camera.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.camera_controller:
            logger.warning("Cannot connect camera: controller not initialized")
            return False

        if self.is_connected:
            logger.info("Camera already connected")
            return True

        logger.info("Connecting to camera...")
        success = self.camera_controller.connect()
        if success:
            # Update slider ranges from camera
            exp_min, exp_max = self.camera_controller.get_exposure_range()
            self.exposure_slider.setMinimum(int(exp_min))
            self.exposure_slider.setMaximum(int(exp_max))

            gain_min, gain_max = self.camera_controller.get_gain_range()
            self.gain_slider.setMinimum(int(gain_min * 10))
            self.gain_slider.setMaximum(int(gain_max * 10))

            logger.info("Camera connected successfully")
        else:
            logger.error("Failed to connect camera")

        return success

    def disconnect_camera(self) -> bool:
        """
        Public API: Disconnect from camera.

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if not self.camera_controller:
            logger.warning("Cannot disconnect camera: controller not initialized")
            return False

        if not self.is_connected:
            logger.info("Camera already disconnected")
            return True

        logger.info("Disconnecting from camera...")
        success = self.camera_controller.disconnect()
        if success:
            logger.info("Camera disconnected successfully")
        else:
            logger.error("Failed to disconnect camera")

        return success

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
        exp_header.addWidget(QLabel("Exposure (µs):"))
        self.auto_exposure_check = QCheckBox("Auto")
        self.auto_exposure_check.setEnabled(False)
        self.auto_exposure_check.stateChanged.connect(self._on_auto_exposure_changed)
        exp_header.addWidget(self.auto_exposure_check)
        exp_header.addStretch()
        layout.addLayout(exp_header)

        # Long exposure warning checkbox (safety feature)
        self.allow_long_exposure_check = QCheckBox("Allow Long Exposure (>33ms, may drop frames)")
        self.allow_long_exposure_check.setEnabled(False)
        self.allow_long_exposure_check.setToolTip(
            "Enable to set exposure times longer than frame period.\n"
            "Warning: Exposures >33ms at 30 FPS will cause frame drops.\n"
            "Only use for still imaging, not live viewing."
        )
        self.allow_long_exposure_check.setStyleSheet("color: #ff8800; font-weight: bold;")
        self.allow_long_exposure_check.stateChanged.connect(self._on_allow_long_exposure_changed)
        layout.addWidget(self.allow_long_exposure_check)

        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(100)  # 0.1 ms minimum
        self.exposure_slider.setMaximum(1000000)  # 1 second maximum (user-friendly range)
        self.exposure_slider.setValue(10000)  # 10ms default (safe for 30 FPS)
        self.exposure_slider.setEnabled(False)
        self.exposure_slider.valueChanged.connect(self._on_exposure_changed)
        layout.addWidget(self.exposure_slider)

        exp_value_layout = QHBoxLayout()
        self.exposure_value_label = QLabel("10000 µs (10.0 ms)")
        exp_value_layout.addWidget(self.exposure_value_label)
        self.exposure_input = QLineEdit()
        self.exposure_input.setPlaceholderText("Enter µs")
        self.exposure_input.setMaximumWidth(100)
        self.exposure_input.setEnabled(False)
        self.exposure_input.returnPressed.connect(self._on_exposure_input_changed)
        exp_value_layout.addWidget(self.exposure_input)
        exp_value_layout.addStretch()
        layout.addLayout(exp_value_layout)

        # Exposure warning label (appears when long exposure selected)
        self.exposure_warning_label = QLabel("")
        self.exposure_warning_label.setStyleSheet(
            "color: #ff5555; font-weight: bold; font-size: 10px;"
        )
        self.exposure_warning_label.setWordWrap(True)
        layout.addWidget(self.exposure_warning_label)

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

        # Display scale control (camera-side downsampling for performance)
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Display Scale:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(
            [
                "Full (1×) - High detail, slower",
                "Half (½×) - Balanced",
                "Quarter (¼×) - Fast, smooth (30 FPS)",
            ]
        )
        self.scale_combo.setCurrentIndex(2)  # Default to quarter resolution for 30 FPS
        self.scale_combo.setEnabled(True)
        self.scale_combo.setToolTip(
            "Camera-side downsampling for optimal performance.\n"
            "Quarter scale: 15× bandwidth reduction → full 30 FPS\n"
            "Captured images/videos always use full resolution."
        )
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        scale_layout.addWidget(self.scale_combo)
        scale_layout.addStretch()
        layout.addLayout(scale_layout)

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

        # Dev mode: Custom path selection
        self.image_path_group = QWidget()
        path_layout = QVBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)

        path_layout.addWidget(QLabel("Custom Save Path:"))
        path_select_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setPlaceholderText("Use default path")
        self.image_path_input.setReadOnly(True)
        path_select_layout.addWidget(self.image_path_input)

        self.image_path_browse_btn = QPushButton("Browse...")
        self.image_path_browse_btn.clicked.connect(self._on_browse_image_path)
        path_select_layout.addWidget(self.image_path_browse_btn)

        path_layout.addLayout(path_select_layout)
        self.image_path_group.setLayout(path_layout)
        self.image_path_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.image_path_group)

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

        # Dev mode: Custom path selection
        self.video_path_group = QWidget()
        path_layout = QVBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)

        path_layout.addWidget(QLabel("Custom Save Path:"))
        path_select_layout = QHBoxLayout()
        self.video_path_input = QLineEdit()
        self.video_path_input.setPlaceholderText("Use default path")
        self.video_path_input.setReadOnly(True)
        path_select_layout.addWidget(self.video_path_input)

        self.video_path_browse_btn = QPushButton("Browse...")
        self.video_path_browse_btn.clicked.connect(self._on_browse_video_path)
        path_select_layout.addWidget(self.video_path_browse_btn)

        path_layout.addLayout(path_select_layout)
        self.video_path_group.setLayout(path_layout)
        self.video_path_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.video_path_group)

        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setEnabled(False)
        self.record_btn.clicked.connect(self._on_record_clicked)
        layout.addWidget(self.record_btn)

        self.recording_status_label = QLabel("Not recording")
        self.recording_status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.recording_status_label)

        group.setLayout(layout)
        return group

    def set_dev_mode(self, dev_mode: bool) -> None:
        """
        Enable/disable developer mode.

        Args:
            dev_mode: True to enable dev mode, False to disable
        """
        self.dev_mode = dev_mode
        logger.info(f"Camera widget dev mode: {dev_mode}")

        # Show/hide custom path controls
        self.video_path_group.setVisible(dev_mode)
        self.image_path_group.setVisible(dev_mode)

        if not dev_mode:
            # Clear custom paths when exiting dev mode
            self.custom_video_path = None
            self.custom_image_path = None
            self.video_path_input.clear()
            self.image_path_input.clear()

    def _on_browse_video_path(self) -> None:
        """Browse for custom video save path."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Video Save Directory", str(Path.home())
        )
        if directory:
            self.custom_video_path = Path(directory)
            self.video_path_input.setText(str(self.custom_video_path))
            logger.info(f"Custom video path set: {self.custom_video_path}")

    def _on_browse_image_path(self) -> None:
        """Browse for custom image save path."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Image Save Directory", str(Path.home())
        )
        if directory:
            self.custom_image_path = Path(directory)
            self.image_path_input.setText(str(self.custom_image_path))
            logger.info(f"Custom image path set: {self.custom_image_path}")

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

                # Enable controls for pre-configuration (before streaming)
                self.exposure_slider.setEnabled(True)
                self.gain_slider.setEnabled(True)
                self.exposure_input.setEnabled(True)
                self.gain_input.setEnabled(True)
                self.auto_exposure_check.setEnabled(True)
                self.auto_gain_check.setEnabled(True)
                self.auto_wb_check.setEnabled(True)
                self.allow_long_exposure_check.setEnabled(True)

                # Read and display current camera settings
                current_exposure = self.camera_controller.get_exposure()
                current_gain = self.camera_controller.get_gain()

                # Update UI with current hardware values
                self._on_exposure_hardware_changed(current_exposure)
                self._on_gain_hardware_changed(current_gain)

                logger.info(
                    f"Camera settings enabled for pre-configuration: "
                    f"Exposure={int(current_exposure)}µs, Gain={current_gain:.1f}dB"
                )

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
            # Keep controls enabled for configuration (user can adjust before next stream)
            # Don't disable: exposure_slider, gain_slider, auto checks
        else:
            # Apply pre-configured settings to camera hardware before streaming
            if not self.auto_exposure_check.isChecked():
                exp_value = self.exposure_slider.value()
                self.camera_controller.set_exposure(float(exp_value))
                logger.info(f"Pre-configured exposure applied: {exp_value}µs")

            if not self.auto_gain_check.isChecked():
                gain_value = self.gain_slider.value() / 10.0
                self.camera_controller.set_gain(gain_value)
                logger.info(f"Pre-configured gain applied: {gain_value:.1f}dB")

            success = self.camera_controller.start_streaming()
            if success:
                self.is_streaming = True
                self.stream_btn.setText("Stop Streaming")
                self.capture_btn.setEnabled(True)
                self.record_btn.setEnabled(True)

                # Display current settings (already configured)
                exp_value = self.exposure_slider.value()
                exp_ms = exp_value / 1000.0
                self.exposure_info.setText(f"Exposure: {exp_value} µs ({exp_ms:.1f} ms)")
                gain_value = self.gain_slider.value() / 10.0
                self.gain_info.setText(f"Gain: {gain_value:.1f} dB")

                # Check if current exposure requires long exposure mode
                self._check_exposure_safety(exp_value)

                logger.info("Streaming started with pre-configured settings")

    def cleanup(self) -> None:
        """Cleanup camera resources on application exit."""
        try:
            if hasattr(self, "camera_controller") and self.camera_controller:
                if self.camera_controller.is_streaming:
                    self.camera_controller.stop_streaming()
                if self.camera_controller.is_connected:
                    self.camera_controller.disconnect()
        except Exception as e:
            logger.error(f"Error during camera cleanup: {e}")

    def _on_exposure_changed(self, value: int) -> None:
        """Handle exposure slider change - sends command to camera with safety check."""
        if not self.camera_controller:
            return

        # Safety check: prevent long exposures without explicit user permission
        if not self._is_exposure_safe(value):
            # Revert to safe value (33ms = 33,333 µs at 30 FPS)
            safe_value = 33000
            self.exposure_slider.blockSignals(True)
            self.exposure_slider.setValue(safe_value)
            self.exposure_slider.blockSignals(False)

            # Show warning
            self.exposure_warning_label.setText(
                "WARNING: Exposure limited to 33ms (30 FPS). Enable 'Allow Long Exposure' for longer times."
            )
            logger.warning(
                f"Exposure change blocked: {value}µs exceeds frame period. "
                f"Enable 'Allow Long Exposure' checkbox to proceed."
            )
            return
        else:
            # Clear warning if exposure is now safe
            self.exposure_warning_label.setText("")

        # Send command to camera hardware
        # Works both during streaming (live update) and before streaming (pre-configuration)
        self.camera_controller.set_exposure(float(value))

        # Update label immediately for pre-configuration feedback
        exp_ms = value / 1000.0
        self.exposure_value_label.setText(f"{value} µs ({exp_ms:.1f} ms)")
        if self.is_streaming:
            self.exposure_info.setText(f"Exposure: {value} µs ({exp_ms:.1f} ms)")

    def _on_exposure_input_changed(self) -> None:
        """Handle exposure input box change."""
        try:
            value = int(self.exposure_input.text())
            # Safety check will happen in _on_exposure_changed when slider updates
            self.exposure_slider.setValue(value)
        except ValueError:
            logger.warning(f"Invalid exposure value: {self.exposure_input.text()}")

    def _on_gain_changed(self, value: int) -> None:
        """Handle gain slider change - sends command to camera."""
        if self.camera_controller:
            # Send command to camera hardware
            gain_db = value / 10.0
            self.camera_controller.set_gain(gain_db)

            # Update label immediately for pre-configuration feedback
            self.gain_value_label.setText(f"{gain_db:.1f} dB")
            if self.is_streaming:
                self.gain_info.setText(f"Gain: {gain_db:.1f} dB")

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
        enabled = bool(state)
        logger.info(f"Auto exposure {'enabled' if enabled else 'disabled'}")

        if self.camera_controller:
            self.camera_controller.set_auto_exposure(enabled)

        if enabled:
            # Disable manual controls when auto mode active
            self.exposure_slider.setEnabled(False)
            self.exposure_input.setEnabled(False)
            self.allow_long_exposure_check.setEnabled(False)
            # Clear warning (auto mode manages exposure)
            self.exposure_warning_label.setText("")
        else:
            # Re-enable manual controls
            self.exposure_slider.setEnabled(True)
            self.exposure_input.setEnabled(True)
            self.allow_long_exposure_check.setEnabled(True)
            # Check current exposure safety
            self._check_exposure_safety(self.exposure_slider.value())

    def _on_auto_gain_changed(self, state: int) -> None:
        """Handle auto gain checkbox change."""
        enabled = bool(state)
        logger.info(f"Auto gain {'enabled' if enabled else 'disabled'}")

        if self.camera_controller:
            self.camera_controller.set_auto_gain(enabled)

        if enabled:
            self.gain_slider.setEnabled(False)
            self.gain_input.setEnabled(False)
        else:
            self.gain_slider.setEnabled(True)
            self.gain_input.setEnabled(True)

    def _on_auto_wb_changed(self, state: int) -> None:
        """Handle auto white balance checkbox change."""
        enabled = bool(state)
        logger.info(f"Auto white balance {'enabled' if enabled else 'disabled'}")

        if self.camera_controller:
            self.camera_controller.set_auto_white_balance(enabled)

    def _on_exposure_hardware_changed(self, exposure_us: float) -> None:
        """
        Handle exposure changed signal from camera hardware (thread-safe feedback).

        This is called when the camera confirms an exposure change.
        Updates ALL UI elements to reflect the actual hardware state.

        Args:
            exposure_us: Actual exposure time from camera hardware
        """
        exposure_int = int(exposure_us)
        exposure_ms = exposure_us / 1000.0

        # Block signals to prevent triggering set_exposure again
        self.exposure_slider.blockSignals(True)
        self.exposure_input.blockSignals(True)

        # Update all exposure UI elements
        self.exposure_slider.setValue(exposure_int)
        self.exposure_value_label.setText(f"{exposure_int} µs ({exposure_ms:.1f} ms)")
        self.exposure_input.setText(str(exposure_int))
        self.exposure_info.setText(f"Exposure: {exposure_int} µs ({exposure_ms:.1f} ms)")

        # Check exposure safety and update warnings
        self._check_exposure_safety(exposure_int)

        # Re-enable signals
        self.exposure_slider.blockSignals(False)
        self.exposure_input.blockSignals(False)

        logger.debug(f"UI updated with hardware exposure: {exposure_int} µs")

    def _on_gain_hardware_changed(self, gain_db: float) -> None:
        """
        Handle gain changed signal from camera hardware (thread-safe feedback).

        This is called when the camera confirms a gain change.
        Updates ALL UI elements to reflect the actual hardware state.

        Args:
            gain_db: Actual gain from camera hardware in dB
        """
        gain_int = int(gain_db * 10)  # Convert dB to slider value

        # Block signals to prevent triggering set_gain again
        self.gain_slider.blockSignals(True)
        self.gain_input.blockSignals(True)

        # Update all gain UI elements
        self.gain_slider.setValue(gain_int)
        self.gain_value_label.setText(f"{gain_db:.1f} dB")
        self.gain_input.setText(f"{gain_db:.1f}")
        self.gain_info.setText(f"Gain: {gain_db:.1f} dB")

        # Re-enable signals
        self.gain_slider.blockSignals(False)
        self.gain_input.blockSignals(False)

        logger.debug(f"UI updated with hardware gain: {gain_db:.1f} dB")

    def _on_scale_changed(self, index: int) -> None:
        """Handle display scale selection change - updates camera controller."""
        # Map combo box index to scale factor
        scale_map = {0: 1.0, 1: 0.5, 2: 0.25}
        scale = scale_map.get(index, 0.25)

        if self.camera_controller:
            self.camera_controller.set_display_scale(scale)
            logger.info(f"Display scale changed to {scale}× (camera-side downsampling)")
        else:
            logger.warning("Cannot change display scale: camera controller not initialized")

    def _on_capture_image(self) -> None:
        """Handle capture image button click."""
        if not self.camera_controller:
            return

        # Get base filename from input
        base_filename = self.image_filename_input.text() or "capture"

        # Use custom path if in dev mode
        output_dir = None
        if self.dev_mode and self.custom_image_path:
            output_dir = self.custom_image_path
            logger.info(f"Using custom image path: {output_dir}")

        # Capture image
        saved_path = self.camera_controller.capture_image(base_filename, output_dir)

        if saved_path:
            self.last_capture_label.setText(f"Saved: {saved_path}")
            self.last_capture_label.setStyleSheet("color: green; font-size: 10px;")
            logger.info(f"Image captured successfully: {saved_path}")
        else:
            self.last_capture_label.setText("Capture failed - check logs")
            self.last_capture_label.setStyleSheet("color: red; font-size: 10px;")

    def _on_record_clicked(self) -> None:
        """Handle record button click."""
        if not self.camera_controller:
            return

        if self.camera_controller.is_recording:
            self.camera_controller.stop_recording()
        else:
            base_filename = self.video_filename_input.text() or "recording"

            # Use custom path if in dev mode
            output_dir = None
            if self.dev_mode and self.custom_video_path:
                output_dir = self.custom_video_path
                logger.info(f"Using custom video path: {output_dir}")

            self.camera_controller.start_recording(base_filename, output_dir)

    # Slots for camera controller signals
    @pyqtSlot(QPixmap)
    def _on_pixmap_received(self, pixmap: QPixmap) -> None:
        """
        Update display with pre-converted QPixmap (FAST - no GUI thread conversion!).

        This is the primary display path for GUI updates. The pixmap is already
        converted to QPixmap in the camera thread, so we just scale and display it.

        Args:
            pixmap: Pre-converted QPixmap from camera controller
        """
        try:
            # Debug: Log first few received pixmaps
            if not hasattr(self, "_pixmap_receive_count"):
                self._pixmap_receive_count = 0
            self._pixmap_receive_count += 1
            if self._pixmap_receive_count <= 5:
                logger.info(
                    f"CameraWidget received PIXMAP #{self._pixmap_receive_count}, "
                    f"size: {pixmap.width()}×{pixmap.height()}"
                )
            # Scale to fit display while maintaining aspect ratio
            # Use FastTransformation for real-time video (SmoothTransformation is too slow)
            scaled_pixmap = pixmap.scaled(
                self.camera_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )

            # Display (extremely fast - no conversion needed!)
            self.camera_display.setPixmap(scaled_pixmap)

            # Emit pixmap for other widgets (e.g., ActiveTreatmentWidget)
            # This allows multiple displays of the same camera feed without widget reparenting
            self.pixmap_ready.emit(pixmap)

        except Exception as e:
            logger.error(f"Error displaying pixmap: {e}")

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

            # Disable controls when camera disconnected
            self.exposure_slider.setEnabled(False)
            self.gain_slider.setEnabled(False)
            self.exposure_input.setEnabled(False)
            self.gain_input.setEnabled(False)
            self.auto_exposure_check.setEnabled(False)
            self.auto_gain_check.setEnabled(False)
            self.auto_wb_check.setEnabled(False)
            self.allow_long_exposure_check.setEnabled(False)

        # Notify main window status bar (if available)
        main_window = self.window()
        if main_window and hasattr(main_window, "update_camera_status"):
            main_window.update_camera_status(connected)

        # Notify hardware tab panel (if available)
        if main_window and hasattr(main_window, "camera_hardware_panel"):
            main_window.camera_hardware_panel.update_connection_status(connected)

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
            self.recording_indicator.setText("REC")
            self.recording_status_label.setText("Recording...")
            self.recording_status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.record_btn.setText("Start Recording")
            self.recording_indicator.setText("")
            self.recording_status_label.setText("Not recording")
            self.recording_status_label.setStyleSheet("color: #666; font-size: 10px;")

    def _on_allow_long_exposure_changed(self, state: int) -> None:
        """Handle allow long exposure checkbox change."""
        enabled = bool(state)
        if enabled:
            logger.info("Long exposure mode enabled (may cause frame drops)")
            self.exposure_warning_label.setText("")
        else:
            logger.info("Long exposure mode disabled (limited to 33ms)")
            # Check if current exposure needs to be clamped
            current_exposure = self.exposure_slider.value()
            self._check_exposure_safety(current_exposure)

    def _is_exposure_safe(self, exposure_us: int) -> bool:
        """
        Check if exposure time is safe for current frame rate.

        Safe exposure = exposure that won't cause frame drops at 30 FPS.
        At 30 FPS, frame period = 33.33ms, so safe exposure < 33ms.

        Args:
            exposure_us: Exposure time in microseconds

        Returns:
            True if safe (< 33ms) OR long exposure mode enabled
        """
        # Frame period at 30 FPS = 33.33ms = 33,333 microseconds
        max_safe_exposure_us = 33000  # Slightly under 33.33ms for margin

        # Allow if under limit OR long exposure mode explicitly enabled
        return exposure_us <= max_safe_exposure_us or self.allow_long_exposure_check.isChecked()

    def _check_exposure_safety(self, exposure_us: int) -> None:
        """
        Check exposure safety and update warning label.

        Args:
            exposure_us: Exposure time in microseconds
        """
        if not self._is_exposure_safe(exposure_us):
            exposure_ms = exposure_us / 1000.0
            self.exposure_warning_label.setText(
                f"WARNING: Exposure {exposure_ms:.1f}ms > 33ms frame period. "
                f"Enable 'Allow Long Exposure' or reduce exposure."
            )
        else:
            # Clear warning if exposure is safe
            if exposure_us > 33000 and self.allow_long_exposure_check.isChecked():
                # Show informational message when long exposure is intentionally enabled
                exposure_ms = exposure_us / 1000.0
                fps_estimate = 1000.0 / exposure_ms if exposure_ms > 0 else 30.0
                self.exposure_warning_label.setText(
                    f"ℹ️ Long exposure active ({exposure_ms:.1f}ms). "
                    f"Expect ~{fps_estimate:.1f} FPS (frame drops normal)."
                )
                self.exposure_warning_label.setStyleSheet(
                    "color: #ff8800; font-weight: bold; font-size: 10px;"
                )
            else:
                self.exposure_warning_label.setText("")
                self.exposure_warning_label.setStyleSheet(
                    "color: #ff5555; font-weight: bold; font-size: 10px;"
                )
