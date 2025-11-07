"""
Laser Spot Smoothing Module Widget
Project: TOSCA Laser Control System

Purpose: Control and monitor laser spot smoothing module.
         PWM motor control (D9) + I2C accelerometer monitoring (A4/A5).

Safety Critical: Yes - Beam quality assurance
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.design_tokens import ButtonSizes, Colors

logger = logging.getLogger(__name__)


class SmoothingModuleWidget(QWidget):
    """
    Laser spot smoothing module control and monitoring.

    Controls:
    - Motor speed (PWM 0-153, voltage 0-3.0V)
    - Motor on/off

    Monitors:
    - Vibration level (accelerometer magnitude)
    - 3-axis acceleration (X, Y, Z)
    - Motor health status (vibration threshold)
    """

    def __init__(self, gpio_controller: Optional[object] = None, parent: Optional[QWidget] = None) -> None:
        """
        Initialize smoothing module widget.

        Args:
            gpio_controller: GPIO controller instance (for signal connections)
            parent: Parent widget
        """
        super().__init__(parent)
        self.gpio_controller = gpio_controller
        self.is_connected = False

        # Let grid layout control width (removed max width constraint for better horizontal space usage)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Main group box
        group = QGroupBox("SMOOTHING MODULE  (requires GPIO)")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {Colors.PANEL};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Colors.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Connection status
        self.status_label = QLabel("Status: Not Connected (GPIO offline)")
        self.status_label.setStyleSheet(
            f"font-size: 10pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
        )
        layout.addWidget(self.status_label)

        # === PWM MOTOR SECTION (D9) ===
        motor_label = QLabel("PWM Motor (D9):")
        motor_label.setStyleSheet(
            f"font-size: 10pt; font-weight: bold; color: {Colors.TEXT_PRIMARY}; padding: 4px;"
        )
        layout.addWidget(motor_label)

        # Speed slider
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(8)

        speed_text = QLabel("Speed:")
        speed_text.setStyleSheet(f"font-size: 10pt; color: {Colors.TEXT_PRIMARY};")
        speed_layout.addWidget(speed_text)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(153)  # PWM max (3.0V)
        self.speed_slider.setValue(100)  # Default: 2.0V
        self.speed_slider.setEnabled(False)  # Disabled until GPIO connects
        self.speed_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                background: {Colors.BACKGROUND};
                height: 10px;
                border-radius: 5px;
            }}
            QSlider::handle:horizontal {{
                background: {Colors.PRIMARY};
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Colors.TREATING};
            }}
            QSlider::handle:horizontal:disabled {{
                background: {Colors.SECONDARY};
            }}
        """
        )
        self.speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        self.speed_slider.setToolTip("Set target motor speed (0-153 PWM / 0-3.0V). Click Start button to apply.")
        speed_layout.addWidget(self.speed_slider, stretch=3)

        self.speed_value_label = QLabel("100 PWM")
        self.speed_value_label.setStyleSheet(
            f"font-size: 10pt; font-weight: bold; color: {Colors.TEXT_PRIMARY}; min-width: 80px;"
        )
        speed_layout.addWidget(self.speed_value_label)

        layout.addLayout(speed_layout)

        # Range and voltage info
        info_layout = QHBoxLayout()
        range_label = QLabel("Range: 0-153 (0-3.0V)")
        range_label.setStyleSheet(f"font-size: 9pt; color: {Colors.TEXT_SECONDARY};")
        info_layout.addWidget(range_label)

        self.voltage_label = QLabel("Voltage: 2.0 V")
        self.voltage_label.setStyleSheet(
            f"font-size: 9pt; color: {Colors.TEXT_SECONDARY}; font-weight: bold;"
        )
        info_layout.addWidget(self.voltage_label)

        info_layout.addStretch()

        default_label = QLabel("Default: 100 (2.0V)")
        default_label.setStyleSheet(f"font-size: 9pt; color: {Colors.TEXT_SECONDARY};")
        info_layout.addWidget(default_label)

        layout.addLayout(info_layout)

        # Motor control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.start_motor_btn = QPushButton("Start Motor")
        self.start_motor_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.start_motor_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.start_motor_btn.setEnabled(False)  # Disabled until GPIO connects
        self.start_motor_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SAFE};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.CONNECTED};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.start_motor_btn.setToolTip("Start motor at current speed slider value")
        self.start_motor_btn.clicked.connect(self._on_start_motor_clicked)
        button_layout.addWidget(self.start_motor_btn)

        self.stop_motor_btn = QPushButton("Stop Motor")
        self.stop_motor_btn.setFixedWidth(90)  # Secondary action width (grid layout)
        self.stop_motor_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.stop_motor_btn.setEnabled(False)  # Disabled until GPIO connects
        self.stop_motor_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.DANGER};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #A52A2A;
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.stop_motor_btn.setToolTip("Stop motor immediately (sets speed to 0)")
        self.stop_motor_btn.clicked.connect(self._on_stop_motor_clicked)
        button_layout.addWidget(self.stop_motor_btn)

        self.motor_status_label = QLabel("Motor: OFF")
        self.motor_status_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )
        button_layout.addWidget(self.motor_status_label, stretch=1)

        layout.addLayout(button_layout)

        # === ACCELEROMETER SECTION (A4/A5 I2C) ===
        accel_label = QLabel("Accelerometer (A4/A5 I2C):")
        accel_label.setStyleSheet(
            f"font-size: 10pt; font-weight: bold; color: {Colors.TEXT_PRIMARY}; padding: 4px; margin-top: 8px;"
        )
        layout.addWidget(accel_label)

        # Vibration level (large, prominent)
        vibration_layout = QHBoxLayout()
        vib_text = QLabel("Vibration:")
        vib_text.setStyleSheet(f"font-size: 10pt; color: {Colors.TEXT_PRIMARY};")
        vibration_layout.addWidget(vib_text)

        self.vibration_label = QLabel("0.00 g")
        self.vibration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vibration_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """
        )
        vibration_layout.addWidget(self.vibration_label, stretch=1)

        # Vibration threshold input
        threshold_label = QLabel("Threshold:")
        threshold_label.setStyleSheet(f"font-size: 10pt; color: {Colors.TEXT_SECONDARY};")
        vibration_layout.addWidget(threshold_label)

        self.threshold_input = QLineEdit("0.10")
        self.threshold_input.setFixedWidth(60)
        self.threshold_input.setEnabled(False)  # Disabled until GPIO connects
        self.threshold_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }}
            QLineEdit:disabled {{
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        vibration_layout.addWidget(self.threshold_input)

        g_label = QLabel("g")
        g_label.setStyleSheet(f"font-size: 10pt; color: {Colors.TEXT_SECONDARY};")
        vibration_layout.addWidget(g_label)

        layout.addLayout(vibration_layout)

        # XYZ acceleration
        xyz_layout = QHBoxLayout()
        xyz_layout.setSpacing(8)

        xyz_text = QLabel("XYZ:")
        xyz_text.setStyleSheet(f"font-size: 10pt; color: {Colors.TEXT_SECONDARY};")
        xyz_layout.addWidget(xyz_text)

        self.accel_xyz_label = QLabel("X: 0.00g  Y: 0.00g  Z: 1.00g  (calibrated)")
        self.accel_xyz_label.setStyleSheet(
            f"font-size: 9pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
        )
        xyz_layout.addWidget(self.accel_xyz_label)

        layout.addLayout(xyz_layout)

        # Health status
        self.health_label = QLabel("Health: Motor OFF (vibration below threshold)")
        self.health_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BG_WARNING};
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.health_label)

        # Calibration buttons
        calib_layout = QHBoxLayout()
        calib_layout.setSpacing(8)

        self.calibrate_btn = QPushButton("Calibrate")
        self.calibrate_btn.setFixedWidth(100)  # Secondary action width
        self.calibrate_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.calibrate_btn.setEnabled(False)  # Disabled until GPIO connects
        self.calibrate_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.TREATING};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.calibrate_btn.setToolTip("Calibrate accelerometer zero-point (keep motor still!)")
        self.calibrate_btn.clicked.connect(self._on_calibrate_clicked)
        calib_layout.addWidget(self.calibrate_btn)

        self.view_data_btn = QPushButton("View Data")
        self.view_data_btn.setFixedWidth(100)  # Secondary action width
        self.view_data_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.view_data_btn.setEnabled(False)  # Disabled until GPIO connects
        self.view_data_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.TEXT_SECONDARY};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.view_data_btn.setToolTip("View accelerometer data history")
        self.view_data_btn.clicked.connect(self._on_view_data_clicked)
        calib_layout.addWidget(self.view_data_btn)

        layout.addLayout(calib_layout)

        group.setLayout(layout)

        # Main widget layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        """Connect GPIO controller signals."""
        if self.gpio_controller is not None:
            # Connection status
            if hasattr(self.gpio_controller, "connection_changed"):
                self.gpio_controller.connection_changed.connect(self._on_connection_changed)

            # Motor speed
            if hasattr(self.gpio_controller, "motor_speed_changed"):
                self.gpio_controller.motor_speed_changed.connect(self._on_motor_speed_changed)

            # Motor state
            if hasattr(self.gpio_controller, "smoothing_motor_changed"):
                self.gpio_controller.smoothing_motor_changed.connect(self._on_motor_state_changed)

            # Vibration level
            if hasattr(self.gpio_controller, "vibration_level_changed"):
                self.gpio_controller.vibration_level_changed.connect(
                    self._on_vibration_level_changed
                )

            # Accelerometer data
            if hasattr(self.gpio_controller, "accelerometer_data_changed"):
                self.gpio_controller.accelerometer_data_changed.connect(
                    self._on_accelerometer_data_changed
                )

            # Vibration detection
            if hasattr(self.gpio_controller, "smoothing_vibration_changed"):
                self.gpio_controller.smoothing_vibration_changed.connect(
                    self._on_vibration_detected_changed
                )

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """
        Handle GPIO connection status change.

        Args:
            connected: True if GPIO connected, False if disconnected
        """
        self.is_connected = connected

        if connected:
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.CONNECTED}; padding: 4px;"
            )
            self.speed_slider.setEnabled(True)
            self.start_motor_btn.setEnabled(True)
            self.stop_motor_btn.setEnabled(True)
            self.threshold_input.setEnabled(True)
            self.calibrate_btn.setEnabled(True)
            self.view_data_btn.setEnabled(True)
        else:
            self.status_label.setText("Status: Not Connected (GPIO offline)")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
            )
            self.speed_slider.setEnabled(False)
            self.start_motor_btn.setEnabled(False)
            self.stop_motor_btn.setEnabled(False)
            self.threshold_input.setEnabled(False)
            self.calibrate_btn.setEnabled(False)
            self.view_data_btn.setEnabled(False)
            self.motor_status_label.setText("Motor: OFF")
            self.vibration_label.setText("0.00 g")
            self.accel_xyz_label.setText("X: 0.00g  Y: 0.00g  Z: 1.00g  (calibrated)")

    @pyqtSlot(int)
    def _on_speed_slider_changed(self, value: int) -> None:
        """
        Handle speed slider change (setpoint only - does not start motor).

        Args:
            value: PWM value (0-153)
        """
        self.speed_value_label.setText(f"{value} PWM")

        # Calculate voltage (5V * PWM/255)
        voltage = (5.0 * value) / 255.0
        self.voltage_label.setText(f"Voltage: {voltage:.2f} V")

        # NOTE: Slider only sets target speed - Start button applies it
        # Removed auto-start behavior that made Start/Stop buttons appear broken

    @pyqtSlot(int)
    def _on_motor_speed_changed(self, speed_pwm: int) -> None:
        """
        Handle motor speed feedback from hardware.

        Args:
            speed_pwm: PWM value from hardware (0-153)
        """
        # Update slider without triggering signal (hardware feedback loop)
        self.speed_slider.blockSignals(True)
        self.speed_slider.setValue(speed_pwm)
        self.speed_slider.blockSignals(False)

        self.speed_value_label.setText(f"{speed_pwm} PWM")
        voltage = (5.0 * speed_pwm) / 255.0
        self.voltage_label.setText(f"Voltage: {voltage:.2f} V")

    @pyqtSlot(bool)
    def _on_motor_state_changed(self, running: bool) -> None:
        """
        Handle motor state change.

        Args:
            running: True if motor running, False if stopped
        """
        if running:
            self.motor_status_label.setText("Motor: ON")
            self.motor_status_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_SUCCESS};
                    color: white;
                    border: 1px solid {Colors.SAFE};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )
        else:
            self.motor_status_label.setText("Motor: OFF")
            self.motor_status_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BACKGROUND};
                    color: {Colors.TEXT_SECONDARY};
                    border: 1px solid {Colors.BORDER_DEFAULT};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )

    @pyqtSlot(float)
    def _on_vibration_level_changed(self, vibration_g: float) -> None:
        """
        Handle vibration level update.

        Args:
            vibration_g: Vibration magnitude in g's
        """
        self.vibration_label.setText(f"{vibration_g:.3f} g")

        # Color based on threshold
        try:
            threshold = float(self.threshold_input.text())
        except ValueError:
            threshold = 0.1  # Default

        if vibration_g >= threshold:
            border_color = Colors.SAFE  # Above threshold (motor running)
        else:
            border_color = Colors.WARNING  # Below threshold (motor may be stopped)

        self.vibration_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """
        )

    @pyqtSlot(float, float, float)
    def _on_accelerometer_data_changed(self, x: float, y: float, z: float) -> None:
        """
        Handle accelerometer XYZ data update.

        Args:
            x: X-axis acceleration in g's
            y: Y-axis acceleration in g's
            z: Z-axis acceleration in g's
        """
        self.accel_xyz_label.setText(f"X: {x:.2f}g  Y: {y:.2f}g  Z: {z:.2f}g  (calibrated)")

    @pyqtSlot(bool)
    def _on_vibration_detected_changed(self, detected: bool) -> None:
        """
        Handle vibration detection status change.

        Args:
            detected: True if vibration above threshold, False otherwise
        """
        if detected:
            self.health_label.setText("Health: Motor running (vibration above threshold)")
            self.health_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_SUCCESS};
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )
        else:
            self.health_label.setText("Health: Motor OFF (vibration below threshold)")
            self.health_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_WARNING};
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )

    def _on_start_motor_clicked(self) -> None:
        """Handle Start Motor button click."""
        logger.info("Start Motor button clicked")
        if self.is_connected and self.gpio_controller:
            speed_pwm = self.speed_slider.value()
            logger.info(f"Starting motor at {speed_pwm} PWM ({(5.0 * speed_pwm) / 255.0:.2f}V)")

            # Set speed first, then start motor
            if hasattr(self.gpio_controller, "set_motor_speed"):
                self.gpio_controller.set_motor_speed(speed_pwm)

            if hasattr(self.gpio_controller, "start_smoothing_motor"):
                self.gpio_controller.start_smoothing_motor()
            else:
                logger.error("GPIO controller missing start_smoothing_motor method")
        else:
            logger.warning(f"Start motor failed: connected={self.is_connected}, controller={self.gpio_controller is not None}")

    def _on_stop_motor_clicked(self) -> None:
        """Handle Stop Motor button click."""
        logger.info("Stop Motor button clicked")
        if self.is_connected and self.gpio_controller:
            logger.info("Stopping motor")
            if hasattr(self.gpio_controller, "stop_smoothing_motor"):
                self.gpio_controller.stop_smoothing_motor()
            else:
                logger.error("GPIO controller missing stop_smoothing_motor method")
        else:
            logger.warning(f"Stop motor failed: connected={self.is_connected}, controller={self.gpio_controller is not None}")

    def _on_calibrate_clicked(self) -> None:
        """Handle Calibrate button click."""
        # TODO: Implement accelerometer calibration
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Calibration",
            "Accelerometer calibration:\n\n"
            "1. Keep motor completely still\n"
            "2. Click OK to calibrate zero-point\n"
            "3. Wait 3 seconds for calibration\n\n"
            "Note: Full calibration feature coming soon.",
        )

        # Send calibration command if controller supports it
        if self.is_connected and self.gpio_controller:
            if hasattr(self.gpio_controller, "calibrate_accelerometer"):
                self.gpio_controller.calibrate_accelerometer()

    def _on_view_data_clicked(self) -> None:
        """Handle View Data button click."""
        # TODO: Implement data viewer dialog
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Data Viewer",
            "Accelerometer data viewer coming soon.\n\n"
            "Will display:\n"
            "• Real-time XYZ acceleration plot\n"
            "• Vibration magnitude history\n"
            "• FFT frequency analysis\n"
            "• Data export to CSV",
        )

    def cleanup(self) -> None:
        """Clean up resources (called on window close)."""
        # Disconnect signals if connected
        if self.gpio_controller is not None:
            try:
                if hasattr(self.gpio_controller, "connection_changed"):
                    self.gpio_controller.connection_changed.disconnect(
                        self._on_connection_changed
                    )
                if hasattr(self.gpio_controller, "motor_speed_changed"):
                    self.gpio_controller.motor_speed_changed.disconnect(
                        self._on_motor_speed_changed
                    )
                if hasattr(self.gpio_controller, "smoothing_motor_changed"):
                    self.gpio_controller.smoothing_motor_changed.disconnect(
                        self._on_motor_state_changed
                    )
                if hasattr(self.gpio_controller, "vibration_level_changed"):
                    self.gpio_controller.vibration_level_changed.disconnect(
                        self._on_vibration_level_changed
                    )
                if hasattr(self.gpio_controller, "accelerometer_data_changed"):
                    self.gpio_controller.accelerometer_data_changed.disconnect(
                        self._on_accelerometer_data_changed
                    )
                if hasattr(self.gpio_controller, "smoothing_vibration_changed"):
                    self.gpio_controller.smoothing_vibration_changed.disconnect(
                        self._on_vibration_detected_changed
                    )
            except (RuntimeError, TypeError):
                pass  # Signals already disconnected
