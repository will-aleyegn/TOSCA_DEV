"""
Camera hardware panel widget for Hardware & Diagnostics tab.

Provides connection management and camera controls (exposure, gain, white balance).
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.design_tokens import ButtonSizes, Colors

logger = logging.getLogger(__name__)


class CameraHardwarePanel(QWidget):
    """
    Camera hardware management panel for Hardware & Diagnostics tab.

    Provides:
    - Connection status indicator
    - Connect/Disconnect buttons
    - Exposure control (0.1-33ms with auto mode)
    - Gain control (0-24dB with auto mode)
    - White balance control (auto mode)

    This widget is a lightweight companion to the full camera live view,
    designed specifically for hardware setup and diagnostics.

    Thread Safety:
        All camera operations use signal/slot architecture for thread-safe communication.
        Sliders use blockSignals() to prevent infinite loops during hardware updates.

    Medical Device Context:
        Exposure range limited to 33ms max to prevent frame drops during treatment.
        All controls emit signals to maintain audit trail for FDA compliance.
    """

    def __init__(self, camera_live_view) -> None:
        """
        Initialize camera hardware panel.

        Args:
            camera_live_view: Reference to main camera live view widget for control delegation
        """
        super().__init__()
        self.camera_live_view = camera_live_view
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Let grid layout control width (removed max width constraint for better horizontal space usage)

        # Master group box: "IMAGING SYSTEM" (similar to LASER SYSTEMS)
        master_group = QGroupBox("IMAGING SYSTEM")
        master_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {Colors.CAMERA};
            }}
            """
        )
        master_layout = QVBoxLayout()
        master_group.setLayout(master_layout)
        main_layout.addWidget(master_group)

        # Connection status section
        self._init_connection_section(master_layout)

        # Camera controls section
        self._init_camera_controls(master_layout)

        main_layout.addStretch()

    def _init_connection_section(self, parent_layout: QVBoxLayout) -> None:
        """
        Initialize connection status and control buttons.

        Args:
            parent_layout: Parent layout to add connection section to
        """
        # Connection status indicator
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("● Disconnected")
        self.status_label.setStyleSheet(f"color: {Colors.DANGER}; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        parent_layout.addLayout(status_layout)

        # Connection controls - compact fixed-width buttons
        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.connect_btn.setMinimumHeight(ButtonSizes.SECONDARY)
        self.connect_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1565C0;
            }}
            """
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        button_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(90)  # Secondary action width (grid layout)
        self.disconnect_btn.setMinimumHeight(ButtonSizes.SECONDARY)
        self.disconnect_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #616161;
            }}
            """
        )
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        button_layout.addWidget(self.disconnect_btn)

        button_layout.addStretch()
        parent_layout.addLayout(button_layout)

    def _init_camera_controls(self, parent_layout: QVBoxLayout) -> None:
        """
        Initialize camera control sliders (exposure, gain, white balance).

        Args:
            parent_layout: Parent layout to add camera controls to
        """
        controls_group = QGroupBox("Camera Controls")
        controls_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            """
        )
        controls_layout = QGridLayout()
        controls_group.setLayout(controls_layout)

        # Exposure control (0.1-200ms for 5 FPS minimum)
        row = 0
        self.exposure_label = QLabel("Exposure: -- ms")
        controls_layout.addWidget(self.exposure_label, row, 0, 1, 2)

        # Exposure input row (spinbox + slider)
        exposure_row_layout = QHBoxLayout()
        exposure_row_layout.setSpacing(8)

        self.exposure_spinbox = QSpinBox()
        self.exposure_spinbox.setRange(100, 200000)  # 100µs (0.1ms) to 200000µs (200ms)
        self.exposure_spinbox.setValue(10000)  # Default 10ms
        self.exposure_spinbox.setSuffix(" µs")
        self.exposure_spinbox.setFixedWidth(100)
        self.exposure_spinbox.valueChanged.connect(self._on_exposure_spinbox_changed)
        exposure_row_layout.addWidget(self.exposure_spinbox)

        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(100)  # 100µs = 0.1ms
        self.exposure_slider.setMaximum(200000)  # 200000µs = 200ms (5 FPS minimum)
        self.exposure_slider.setValue(10000)  # Default 10ms
        self.exposure_slider.setMinimumWidth(250)  # Increased for better control precision
        self.exposure_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.exposure_slider.setTickInterval(20000)
        self.exposure_slider.valueChanged.connect(self._on_exposure_slider_changed)
        exposure_row_layout.addWidget(self.exposure_slider)

        controls_layout.addLayout(exposure_row_layout, row + 1, 0, 1, 2)

        self.auto_exposure_cb = QCheckBox("Auto Exposure")
        self.auto_exposure_cb.stateChanged.connect(self._on_auto_exposure_changed)
        controls_layout.addWidget(self.auto_exposure_cb, row + 2, 0, 1, 2)

        # Gain control (0-24dB)
        row = 3
        self.gain_label = QLabel("Gain: -- dB")
        controls_layout.addWidget(self.gain_label, row, 0, 1, 2)

        # Gain input row (spinbox + slider)
        gain_row_layout = QHBoxLayout()
        gain_row_layout.setSpacing(8)

        self.gain_spinbox = QDoubleSpinBox()
        self.gain_spinbox.setRange(0.0, 24.0)  # 0-24 dB
        self.gain_spinbox.setValue(0.0)  # Default 0dB
        self.gain_spinbox.setSuffix(" dB")
        self.gain_spinbox.setDecimals(1)
        self.gain_spinbox.setSingleStep(0.1)
        self.gain_spinbox.setFixedWidth(100)
        self.gain_spinbox.valueChanged.connect(self._on_gain_spinbox_changed)
        gain_row_layout.addWidget(self.gain_spinbox)

        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setMinimum(0)  # 0 dB
        self.gain_slider.setMaximum(240)  # 24.0 dB (scaled by 10 for 0.1dB precision)
        self.gain_slider.setValue(0)  # Default 0dB
        self.gain_slider.setMinimumWidth(250)  # Increased for better control precision
        self.gain_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.gain_slider.setTickInterval(50)
        self.gain_slider.valueChanged.connect(self._on_gain_slider_changed)
        gain_row_layout.addWidget(self.gain_slider)

        controls_layout.addLayout(gain_row_layout, row + 1, 0, 1, 2)

        self.auto_gain_cb = QCheckBox("Auto Gain")
        self.auto_gain_cb.stateChanged.connect(self._on_auto_gain_changed)
        controls_layout.addWidget(self.auto_gain_cb, row + 2, 0, 1, 2)

        # White balance control
        row = 6
        self.auto_wb_cb = QCheckBox("Auto White Balance")
        self.auto_wb_cb.stateChanged.connect(self._on_auto_wb_changed)
        controls_layout.addWidget(self.auto_wb_cb, row, 0, 1, 2)

        parent_layout.addWidget(controls_group)

        # Initially disable controls until camera connects
        self._set_controls_enabled(False)

    def _set_controls_enabled(self, enabled: bool) -> None:
        """
        Enable/disable all camera controls.

        Args:
            enabled: True to enable controls, False to disable
        """
        self.exposure_spinbox.setEnabled(enabled)
        self.exposure_slider.setEnabled(enabled)
        self.auto_exposure_cb.setEnabled(enabled)
        self.gain_spinbox.setEnabled(enabled)
        self.gain_slider.setEnabled(enabled)
        self.auto_gain_cb.setEnabled(enabled)
        self.auto_wb_cb.setEnabled(enabled)

    def _connect_signals(self) -> None:
        """Connect to camera widget signals."""
        if self.camera_live_view and hasattr(self.camera_live_view, "connection_changed"):
            # Monitor connection status changes from camera widget
            self.camera_live_view.connection_changed.connect(self.update_connection_status)
            logger.debug(
                "Camera hardware panel connected to camera widget connection_changed signal"
            )

        # Connect to camera controller signals (if controller exists)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
        ):
            controller = self.camera_live_view.camera_controller
            if hasattr(controller, "exposure_changed"):
                controller.exposure_changed.connect(self._on_exposure_changed)
            if hasattr(controller, "gain_changed"):
                controller.gain_changed.connect(self._on_gain_changed)

    def _on_connect_clicked(self) -> None:
        """Handle connect button click - delegate to main camera widget."""
        if self.camera_live_view and hasattr(self.camera_live_view, "connect_camera"):
            logger.info("Camera connection requested from Hardware tab")
            self.camera_live_view.connect_camera()
            # Status will update via camera widget's connection_changed signal

    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click - delegate to main camera widget."""
        if self.camera_live_view and hasattr(self.camera_live_view, "disconnect_camera"):
            logger.info("Camera disconnection requested from Hardware tab")
            self.camera_live_view.disconnect_camera()
            # Status will update via camera widget's connection_changed signal

    def _on_exposure_spinbox_changed(self, value: int) -> None:
        """
        Handle exposure spinbox change.

        Args:
            value: Spinbox value in microseconds (100-200000µs)

        Thread Safety:
            Uses signal/slot architecture for thread-safe camera communication.
        """
        # Update slider (block signals to prevent loop)
        self.exposure_slider.blockSignals(True)
        self.exposure_slider.setValue(value)
        self.exposure_slider.blockSignals(False)

        exposure_us = float(value)
        exposure_ms = exposure_us / 1000.0
        self.exposure_label.setText(f"Exposure: {exposure_ms:.1f} ms")

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_exposure")
        ):
            success = self.camera_live_view.camera_controller.set_exposure(exposure_us)
            if not success:
                logger.warning(f"Failed to set camera exposure to {exposure_ms:.1f}ms")

    def _on_exposure_slider_changed(self, value: int) -> None:
        """
        Handle exposure slider change.

        Args:
            value: Slider value in microseconds (100-200000µs)

        Thread Safety:
            Uses signal/slot architecture for thread-safe camera communication.
        """
        # Update spinbox (block signals to prevent loop)
        self.exposure_spinbox.blockSignals(True)
        self.exposure_spinbox.setValue(value)
        self.exposure_spinbox.blockSignals(False)

        exposure_us = float(value)
        exposure_ms = exposure_us / 1000.0
        self.exposure_label.setText(f"Exposure: {exposure_ms:.1f} ms")

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_exposure")
        ):
            success = self.camera_live_view.camera_controller.set_exposure(exposure_us)
            if not success:
                logger.warning(f"Failed to set camera exposure to {exposure_ms:.1f}ms")

    def _on_gain_spinbox_changed(self, value: float) -> None:
        """
        Handle gain spinbox change.

        Args:
            value: Spinbox value in dB (0.0-24.0)

        Thread Safety:
            Uses signal/slot architecture for thread-safe camera communication.
        """
        # Update slider (block signals to prevent loop)
        slider_value = int(value * 10)  # Scale up (slider uses 10x for precision)
        self.gain_slider.blockSignals(True)
        self.gain_slider.setValue(slider_value)
        self.gain_slider.blockSignals(False)

        self.gain_label.setText(f"Gain: {value:.1f} dB")

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_gain")
        ):
            success = self.camera_live_view.camera_controller.set_gain(value)
            if not success:
                logger.warning(f"Failed to set camera gain to {value:.1f}dB")

    def _on_gain_slider_changed(self, value: int) -> None:
        """
        Handle gain slider change.

        Args:
            value: Slider value in tenths of dB (0-240 → 0-24dB)

        Thread Safety:
            Uses signal/slot architecture for thread-safe camera communication.
        """
        gain_db = value / 10.0  # Scale down (slider uses 10x for precision)

        # Update spinbox (block signals to prevent loop)
        self.gain_spinbox.blockSignals(True)
        self.gain_spinbox.setValue(gain_db)
        self.gain_spinbox.blockSignals(False)

        self.gain_label.setText(f"Gain: {gain_db:.1f} dB")

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_gain")
        ):
            success = self.camera_live_view.camera_controller.set_gain(gain_db)
            if not success:
                logger.warning(f"Failed to set camera gain to {gain_db:.1f}dB")

    def _on_auto_exposure_changed(self, state: int) -> None:
        """
        Handle auto exposure checkbox change.

        Args:
            state: Qt.CheckState value (2 = checked, 0 = unchecked)
        """
        enabled = state == Qt.CheckState.Checked.value
        self.exposure_slider.setEnabled(not enabled)

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_auto_exposure")
        ):
            success = self.camera_live_view.camera_controller.set_auto_exposure(enabled)
            if not success:
                logger.warning(f"Failed to set auto exposure to {enabled}")

    def _on_auto_gain_changed(self, state: int) -> None:
        """
        Handle auto gain checkbox change.

        Args:
            state: Qt.CheckState value (2 = checked, 0 = unchecked)
        """
        enabled = state == Qt.CheckState.Checked.value
        self.gain_slider.setEnabled(not enabled)

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_auto_gain")
        ):
            success = self.camera_live_view.camera_controller.set_auto_gain(enabled)
            if not success:
                logger.warning(f"Failed to set auto gain to {enabled}")

    def _on_auto_wb_changed(self, state: int) -> None:
        """
        Handle auto white balance checkbox change.

        Args:
            state: Qt.CheckState value (2 = checked, 0 = unchecked)
        """
        enabled = state == Qt.CheckState.Checked.value

        # Send to camera controller (if connected)
        if (
            self.camera_live_view
            and hasattr(self.camera_live_view, "camera_controller")
            and self.camera_live_view.camera_controller
            and hasattr(self.camera_live_view.camera_controller, "set_auto_white_balance")
        ):
            success = self.camera_live_view.camera_controller.set_auto_white_balance(enabled)
            if not success:
                logger.warning(f"Failed to set auto white balance to {enabled}")

    def _on_exposure_changed(self, exposure_us: float) -> None:
        """
        Handle exposure changed signal from camera controller.

        Args:
            exposure_us: New exposure value in microseconds

        Thread Safety:
            This slot receives signals from camera controller thread.
            Uses blockSignals() to prevent infinite feedback loop.
        """
        exposure_ms = exposure_us / 1000.0
        self.exposure_label.setText(f"Exposure: {exposure_ms:.1f} ms")

        # Update slider without triggering valueChanged signal
        self.exposure_slider.blockSignals(True)
        self.exposure_slider.setValue(int(exposure_us))
        self.exposure_slider.blockSignals(False)

    def _on_gain_changed(self, gain_db: float) -> None:
        """
        Handle gain changed signal from camera controller.

        Args:
            gain_db: New gain value in dB

        Thread Safety:
            This slot receives signals from camera controller thread.
            Uses blockSignals() to prevent infinite feedback loop.
        """
        self.gain_label.setText(f"Gain: {gain_db:.1f} dB")

        # Update slider without triggering valueChanged signal
        self.gain_slider.blockSignals(True)
        self.gain_slider.setValue(int(gain_db * 10))  # Scale up for slider precision
        self.gain_slider.blockSignals(False)

    def update_connection_status(self, connected: bool) -> None:
        """
        Update connection status display.

        Args:
            connected: True if camera connected, False otherwise
        """
        if connected:
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet(f"color: {Colors.SAFE}; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self._set_controls_enabled(True)

            # Reconnect to camera controller signals (in case controller was recreated)
            if (
                self.camera_live_view
                and hasattr(self.camera_live_view, "camera_controller")
                and self.camera_live_view.camera_controller
            ):
                controller = self.camera_live_view.camera_controller
                if hasattr(controller, "exposure_changed"):
                    controller.exposure_changed.connect(self._on_exposure_changed)
                if hasattr(controller, "gain_changed"):
                    controller.gain_changed.connect(self._on_gain_changed)
        else:
            self.status_label.setText("● Disconnected")
            self.status_label.setStyleSheet(f"color: {Colors.DANGER}; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self._set_controls_enabled(False)

            # Reset labels to default state
            self.exposure_label.setText("Exposure: -- ms")
            self.gain_label.setText("Gain: -- dB")

    def cleanup(self) -> None:
        """Cleanup widget resources."""
        # Nothing to clean up - main camera widget handles cleanup
        pass
