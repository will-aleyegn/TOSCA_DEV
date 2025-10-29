"""
Motor control widget with accelerometer display.

Provides:
- Motor speed control (PWM 0-153)
- Real-time vibration monitoring
- Accelerometer X, Y, Z display
- Motor-first initialization sequence
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MotorWidget(QWidget):
    """
    Motor speed control with accelerometer display.

    Features:
    - Slider for PWM control (0-153)
    - Preset speed buttons
    - Real-time vibration level
    - X, Y, Z acceleration display
    - Auto-refresh accelerometer data
    """

    def __init__(self) -> None:
        super().__init__()

        self.gpio_controller: Optional[any] = None
        self.dev_mode = False

        # Auto-refresh timer for accelerometer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_accelerometer)
        self.refresh_timer.setInterval(2000)  # Update every 2 seconds

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Motor speed control group
        motor_group = QGroupBox("Smoothing Motor Control")
        motor_layout = QVBoxLayout()

        # Speed slider
        slider_layout = QVBoxLayout()

        self.speed_label = QLabel("Motor Speed: OFF")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        slider_layout.addWidget(self.speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(153)
        self.speed_slider.setValue(0)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.speed_slider)

        # PWM and voltage display
        info_layout = QHBoxLayout()
        self.pwm_label = QLabel("PWM: 0")
        self.voltage_label = QLabel("Voltage: 0.00V")
        info_layout.addWidget(self.pwm_label)
        info_layout.addWidget(self.voltage_label)
        slider_layout.addLayout(info_layout)

        motor_layout.addLayout(slider_layout)

        # Preset buttons
        preset_layout = QHBoxLayout()

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.stop_btn.clicked.connect(lambda: self._set_speed(0))
        preset_layout.addWidget(self.stop_btn)

        self.low_btn = QPushButton("LOW\n(1.5V)")
        self.low_btn.clicked.connect(lambda: self._set_speed(76))
        preset_layout.addWidget(self.low_btn)

        self.med_btn = QPushButton("MEDIUM\n(2.0V)")
        self.med_btn.clicked.connect(lambda: self._set_speed(100))
        preset_layout.addWidget(self.med_btn)

        self.high_btn = QPushButton("HIGH\n(2.5V)")
        self.high_btn.clicked.connect(lambda: self._set_speed(127))
        preset_layout.addWidget(self.high_btn)

        self.max_btn = QPushButton("MAX\n(3.0V)")
        self.max_btn.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        self.max_btn.clicked.connect(lambda: self._set_speed(153))
        preset_layout.addWidget(self.max_btn)

        motor_layout.addLayout(preset_layout)

        motor_group.setLayout(motor_layout)
        layout.addWidget(motor_group)

        # Accelerometer display group
        accel_group = QGroupBox("Vibration Monitor (MPU6050)")
        accel_layout = QVBoxLayout()

        # Init button
        init_layout = QHBoxLayout()
        self.init_accel_btn = QPushButton("Initialize Accelerometer")
        self.init_accel_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.init_accel_btn.clicked.connect(self._init_accelerometer)
        init_layout.addWidget(self.init_accel_btn)

        self.auto_refresh_btn = QPushButton("Auto-Refresh: OFF")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.clicked.connect(self._toggle_auto_refresh)
        init_layout.addWidget(self.auto_refresh_btn)

        accel_layout.addLayout(init_layout)

        # Vibration level (large display)
        self.vibration_label = QLabel("Vibration: -- g")
        self.vibration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vibration_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; padding: 10px; "
            "border: 2px solid #ddd; border-radius: 5px; background-color: #f5f5f5;"
        )
        accel_layout.addWidget(self.vibration_label)

        # X, Y, Z acceleration
        xyz_layout = QHBoxLayout()
        self.accel_x_label = QLabel("X: -- g")
        self.accel_x_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accel_y_label = QLabel("Y: -- g")
        self.accel_y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accel_z_label = QLabel("Z: -- g")
        self.accel_z_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for label in [self.accel_x_label, self.accel_y_label, self.accel_z_label]:
            label.setStyleSheet(
                "font-size: 12px; padding: 5px; border: 1px solid #ddd; "
                "border-radius: 3px; background-color: white;"
            )

        xyz_layout.addWidget(self.accel_x_label)
        xyz_layout.addWidget(self.accel_y_label)
        xyz_layout.addWidget(self.accel_z_label)
        accel_layout.addLayout(xyz_layout)

        # Status
        self.accel_status_label = QLabel("Status: Not initialized")
        self.accel_status_label.setStyleSheet("font-size: 11px; color: #666;")
        accel_layout.addWidget(self.accel_status_label)

        accel_group.setLayout(accel_layout)
        layout.addWidget(accel_group)

        # Initially disable controls
        self._set_controls_enabled(False)

    def set_gpio_controller(self, gpio_controller: any) -> None:
        """
        Set GPIO controller and connect signals.

        Args:
            gpio_controller: GPIOController instance
        """
        self.gpio_controller = gpio_controller

        # Connect signals
        self.gpio_controller.motor_speed_changed.connect(self._on_motor_speed_changed)
        self.gpio_controller.vibration_level_changed.connect(self._on_vibration_changed)
        self.gpio_controller.accelerometer_data_changed.connect(self._on_accel_data_changed)
        self.gpio_controller.connection_changed.connect(self._on_connection_changed)

        # Enable controls if connected
        self._set_controls_enabled(self.gpio_controller.is_connected)

        logger.info("Motor widget connected to GPIO controller")

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Enable/disable controls based on connection status."""
        self.speed_slider.setEnabled(enabled)
        self.stop_btn.setEnabled(enabled)
        self.low_btn.setEnabled(enabled)
        self.med_btn.setEnabled(enabled)
        self.high_btn.setEnabled(enabled)
        self.max_btn.setEnabled(enabled)
        self.init_accel_btn.setEnabled(enabled)
        self.auto_refresh_btn.setEnabled(enabled)

    def _on_connection_changed(self, connected: bool) -> None:
        """Handle GPIO connection status change."""
        self._set_controls_enabled(connected)

        if not connected:
            self.refresh_timer.stop()
            self.auto_refresh_btn.setChecked(False)
            self.auto_refresh_btn.setText("Auto-Refresh: OFF")
            self.accel_status_label.setText("Status: GPIO disconnected")

    def _on_slider_changed(self, value: int) -> None:
        """Handle slider value change."""
        voltage = (value / 255.0) * 5.0

        if value == 0:
            self.speed_label.setText("Motor Speed: OFF")
        elif value < 76:
            self.speed_label.setText("Motor Speed: VERY LOW")
        elif value <= 100:
            self.speed_label.setText("Motor Speed: LOW")
        elif value <= 127:
            self.speed_label.setText("Motor Speed: MEDIUM")
        else:
            self.speed_label.setText("Motor Speed: HIGH")

        self.pwm_label.setText(f"PWM: {value}")
        self.voltage_label.setText(f"Voltage: {voltage:.2f}V")

    def _set_speed(self, pwm: int) -> None:
        """
        Set motor speed and initialize accelerometer.

        Uses motor-first sequence:
        1. Set motor speed
        2. Wait for stabilization
        3. Initialize accelerometer

        Args:
            pwm: PWM value (0-153)
        """
        if not self.gpio_controller or not self.gpio_controller.is_connected:
            logger.warning("Cannot set motor speed - GPIO not connected")
            return

        # Update slider
        self.speed_slider.setValue(pwm)

        # Set motor speed
        success = self.gpio_controller.set_motor_speed(pwm)

        if success:
            logger.info(f"Motor speed set to PWM {pwm}")

            # If motor is running and accelerometer not initialized, init it
            if pwm > 0 and not self.gpio_controller.accelerometer_initialized:
                # Wait for motor to stabilize before initializing accel
                QTimer.singleShot(1500, self._init_accelerometer)
        else:
            logger.error(f"Failed to set motor speed to PWM {pwm}")

    def _init_accelerometer(self) -> None:
        """Initialize MPU6050 accelerometer."""
        if not self.gpio_controller or not self.gpio_controller.is_connected:
            self.accel_status_label.setText("Status: GPIO not connected")
            return

        self.accel_status_label.setText("Status: Initializing...")

        success = self.gpio_controller.init_accelerometer()

        if success:
            self.accel_status_label.setText("Status: Ready (MPU6050 @ 0x68)")
            logger.info("Accelerometer initialized")

            # Read initial values
            self._refresh_accelerometer()
        else:
            self.accel_status_label.setText("Status: Initialization failed")
            logger.error("Accelerometer initialization failed")

    def _toggle_auto_refresh(self, checked: bool) -> None:
        """Toggle automatic accelerometer refresh."""
        if checked:
            self.refresh_timer.start()
            self.auto_refresh_btn.setText("Auto-Refresh: ON")
            logger.info("Accelerometer auto-refresh enabled (2s interval)")
        else:
            self.refresh_timer.stop()
            self.auto_refresh_btn.setText("Auto-Refresh: OFF")
            logger.info("Accelerometer auto-refresh disabled")

    def _refresh_accelerometer(self) -> None:
        """Read and display accelerometer data."""
        if not self.gpio_controller or not self.gpio_controller.accelerometer_initialized:
            return

        # Read vibration level
        self.gpio_controller.get_vibration_level()

        # Read acceleration
        self.gpio_controller.get_acceleration()

    def _on_motor_speed_changed(self, pwm: int) -> None:
        """Handle motor speed change from GPIO controller."""
        # Update slider without triggering signal
        self.speed_slider.blockSignals(True)
        self.speed_slider.setValue(pwm)
        self.speed_slider.blockSignals(False)

        # Update labels
        self._on_slider_changed(pwm)

    def _on_vibration_changed(self, vibration: float) -> None:
        """Handle vibration level update."""
        self.vibration_label.setText(f"Vibration: {vibration:.3f} g")

        # Color code based on level
        if vibration < 0.1:
            color = "#4CAF50"  # Green (low)
        elif vibration < 0.3:
            color = "#ff9800"  # Orange (medium)
        else:
            color = "#f44336"  # Red (high)

        self.vibration_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; padding: 10px; "
            f"border: 2px solid {color}; border-radius: 5px; "
            f"background-color: #f5f5f5; color: {color};"
        )

    def _on_accel_data_changed(self, x: float, y: float, z: float) -> None:
        """Handle acceleration data update."""
        self.accel_x_label.setText(f"X: {x:+.3f} g")
        self.accel_y_label.setText(f"Y: {y:+.3f} g")
        self.accel_z_label.setText(f"Z: {z:+.3f} g")

    def set_dev_mode(self, enabled: bool) -> None:
        """
        Set developer mode (currently unused for motor widget).

        Args:
            enabled: True to enable dev mode
        """
        self.dev_mode = enabled
