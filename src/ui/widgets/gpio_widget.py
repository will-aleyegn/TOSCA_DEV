"""
GPIO safety interlock widget for the TOSCA GUI.

Provides safety monitoring interface for smoothing device and photodiode.
"""

import logging
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.config_loader import get_config
from hardware.gpio_controller import GPIOController

logger = logging.getLogger(__name__)


class GPIOWidget(QWidget):
    """
    GPIO safety monitoring widget with connection and status displays.
    """

    # Signal emitted when GPIO controller connection status changes
    # Emitted AFTER controller is created and connected
    gpio_connection_changed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()

        # Create controller
        self.controller: Optional[GPIOController] = None

        # State tracking
        self.is_connected = False
        self.motor_enabled = False
        self.vibration_detected = False
        self.photodiode_voltage = 0.0
        self.photodiode_power = 0.0
        self.safety_ok = False

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Constrain maximum width to prevent excessive horizontal stretching
        self.setMaximumWidth(700)

        # Connection controls
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Smoothing device section
        smoothing_group = self._create_smoothing_group()
        layout.addWidget(smoothing_group)

        # Photodiode section
        photodiode_group = self._create_photodiode_group()
        layout.addWidget(photodiode_group)

        # Safety interlock status
        safety_group = self._create_safety_group()
        layout.addWidget(safety_group)

        layout.addStretch()

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("GPIO Connection")
        layout = QHBoxLayout()

        # COM Port label
        port_label = QLabel("Port:")
        layout.addWidget(port_label)

        # COM Port selection
        self.com_port_combo = QComboBox()
        self.com_port_combo.setFixedWidth(100)
        # Populate with common Windows COM ports
        for i in range(1, 21):
            self.com_port_combo.addItem(f"COM{i}")
        # Set default from config
        config = get_config()
        default_port = config.hardware.gpio.com_port
        index = self.com_port_combo.findText(default_port)
        if index >= 0:
            self.com_port_combo.setCurrentIndex(index)
        layout.addWidget(self.com_port_combo)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)

        # Status label
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        layout.addWidget(self.connection_status_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_smoothing_group(self) -> QGroupBox:
        """Create smoothing device control group."""
        group = QGroupBox("Smoothing Device")
        layout = QVBoxLayout()

        # Motor control
        motor_layout = QHBoxLayout()
        motor_layout.addWidget(QLabel("Motor Control:"))

        self.motor_enable_btn = QPushButton("Enable Motor")
        self.motor_enable_btn.clicked.connect(lambda: self._on_motor_clicked(True))
        self.motor_enable_btn.setEnabled(False)
        motor_layout.addWidget(self.motor_enable_btn)

        self.motor_disable_btn = QPushButton("Disable Motor")
        self.motor_disable_btn.clicked.connect(lambda: self._on_motor_clicked(False))
        self.motor_disable_btn.setEnabled(False)
        motor_layout.addWidget(self.motor_disable_btn)

        motor_layout.addStretch()
        layout.addLayout(motor_layout)

        # Motor voltage control
        voltage_layout = QHBoxLayout()
        voltage_layout.addWidget(QLabel("Motor Voltage:"))

        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0.0, 3.0)
        self.voltage_spinbox.setSingleStep(0.1)
        self.voltage_spinbox.setValue(2.0)
        self.voltage_spinbox.setSuffix(" V")
        self.voltage_spinbox.setEnabled(False)
        self.voltage_spinbox.setToolTip(
            "Set motor voltage (0V = OFF, 1.5V-3.0V = operating range)\n"
            "Calibrated vibration levels:\n"
            "  1.5V: ~1.8g\n"
            "  2.0V: ~1.6g\n"
            "  2.5V: ~1.9g\n"
            "  3.0V: ~2.9g"
        )
        self.voltage_spinbox.valueChanged.connect(self._on_voltage_set)
        voltage_layout.addWidget(self.voltage_spinbox)

        self.apply_voltage_btn = QPushButton("Apply")
        self.apply_voltage_btn.setEnabled(False)
        self.apply_voltage_btn.clicked.connect(self._on_apply_voltage_clicked)
        voltage_layout.addWidget(self.apply_voltage_btn)

        voltage_layout.addStretch()
        layout.addLayout(voltage_layout)

        # Status display
        status_layout = QGridLayout()

        self.motor_status_label = QLabel("OFF")
        self.motor_status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(QLabel("Motor Status:"), 0, 0)
        status_layout.addWidget(self.motor_status_label, 0, 1)

        self.vibration_status_label = QLabel("NO VIBRATION")
        self.vibration_status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(QLabel("Vibration Sensor:"), 1, 0)
        status_layout.addWidget(self.vibration_status_label, 1, 1)

        self.vibration_level_label = QLabel("-- g")
        self.vibration_level_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #2196F3;"
        )
        status_layout.addWidget(QLabel("Vibration Level:"), 2, 0)
        status_layout.addWidget(self.vibration_level_label, 2, 1)

        layout.addLayout(status_layout)

        # Accelerometer reinitialize button
        accel_layout = QHBoxLayout()
        accel_layout.addWidget(QLabel("Accelerometer:"))

        self.accel_reinit_btn = QPushButton("Reinitialize")
        self.accel_reinit_btn.clicked.connect(self._on_accel_reinit_clicked)
        self.accel_reinit_btn.setEnabled(False)
        self.accel_reinit_btn.setToolTip(
            "Force accelerometer re-detection on I2C bus.\n"
            "Use if accelerometer was plugged in after connection."
        )
        accel_layout.addWidget(self.accel_reinit_btn)

        accel_layout.addStretch()
        layout.addLayout(accel_layout)

        group.setLayout(layout)
        return group

    def _create_photodiode_group(self) -> QGroupBox:
        """Create photodiode monitoring group."""
        group = QGroupBox("Photodiode Laser Monitor")
        layout = QGridLayout()

        # Voltage display
        self.voltage_label = QLabel("-- V")
        self.voltage_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(QLabel("Voltage:"), 0, 0)
        layout.addWidget(self.voltage_label, 0, 1)

        # Power display
        self.power_label = QLabel("-- mW")
        self.power_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(QLabel("Calculated Power:"), 1, 0)
        layout.addWidget(self.power_label, 1, 1)

        group.setLayout(layout)
        return group

    def _create_safety_group(self) -> QGroupBox:
        """Create safety interlock status group."""
        group = QGroupBox("Safety Interlock Status")
        layout = QVBoxLayout()

        self.safety_status_label = QLabel("INTERLOCKS NOT SATISFIED")
        self.safety_status_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; padding: 10px; "
            "background-color: #f44336; color: white; border-radius: 5px;"
        )
        self.safety_status_label.setMinimumHeight(50)
        layout.addWidget(self.safety_status_label)

        # Requirements list
        requirements_layout = QVBoxLayout()
        requirements_layout.addWidget(QLabel("Requirements for laser operation:"))
        requirements_layout.addWidget(QLabel("  ✓ Smoothing motor must be ON"))
        requirements_layout.addWidget(QLabel("  ✓ Vibration must be DETECTED"))
        layout.addLayout(requirements_layout)

        group.setLayout(layout)
        return group

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection status."""
        # Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)

        # Motor controls
        controls_enabled = self.is_connected
        self.motor_enable_btn.setEnabled(controls_enabled and not self.motor_enabled)
        self.motor_disable_btn.setEnabled(controls_enabled and self.motor_enabled)

        # Accelerometer reinitialize button
        self.accel_reinit_btn.setEnabled(self.is_connected)

        # Voltage controls - only enabled when motor is running
        voltage_controls_enabled = self.is_connected and self.motor_enabled
        self.voltage_spinbox.setEnabled(voltage_controls_enabled)
        # Apply button state managed by _on_voltage_set
        if not voltage_controls_enabled:
            self.apply_voltage_btn.setEnabled(False)

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        # Get selected COM port
        selected_port = self.com_port_combo.currentText()
        logger.info(f"Connecting to GPIO on {selected_port}...")

        # Create controller if needed
        if not self.controller:
            try:
                self.controller = GPIOController()

                # Connect signals
                self.controller.connection_changed.connect(self._on_connection_changed)
                self.controller.smoothing_motor_changed.connect(self._on_motor_changed)
                self.controller.smoothing_vibration_changed.connect(self._on_vibration_changed)
                self.controller.vibration_level_changed.connect(self._on_vibration_level_changed)
                self.controller.photodiode_voltage_changed.connect(self._on_voltage_changed)
                self.controller.photodiode_power_changed.connect(self._on_power_changed)
                self.controller.safety_interlock_changed.connect(self._on_safety_changed)
                self.controller.error_occurred.connect(self._on_error)

            except ImportError as e:
                logger.error(f"Failed to create GPIO controller: {e}")
                self.connection_status_label.setText("Libraries not installed")
                return

        # Connect to GPIO using selected COM port
        logger.info(f"Attempting to connect to Arduino on {selected_port}")
        success = self.controller.connect(port=selected_port)

        if not success:
            logger.error(f"Failed to connect to GPIO on {selected_port}")
            self.connection_status_label.setText(f"Connection failed ({selected_port})")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from GPIO...")
            self.controller.disconnect()

    @pyqtSlot(bool)
    def _on_motor_clicked(self, enable: bool) -> None:
        """Handle motor enable/disable button click."""
        if self.controller:
            if enable:
                self.controller.start_smoothing_motor()
            else:
                self.controller.stop_smoothing_motor()

    @pyqtSlot(float)
    def _on_voltage_set(self, voltage: float) -> None:
        """Handle voltage spinbox value change."""
        # Enable Apply button when value changes
        if self.is_connected and self.motor_enabled:
            self.apply_voltage_btn.setEnabled(True)

    @pyqtSlot()
    def _on_apply_voltage_clicked(self) -> None:
        """Handle Apply button click."""
        if self.controller and self.is_connected and self.motor_enabled:
            voltage = self.voltage_spinbox.value()
            pwm = int((voltage / 5.0) * 255)
            logger.info(f"Setting motor voltage to {voltage}V (PWM={pwm})")
            success = self.controller.set_motor_speed(pwm)
            if success:
                logger.info(f"Motor voltage set successfully to {voltage}V")
                # Disable Apply button after successful application
                self.apply_voltage_btn.setEnabled(False)
            else:
                logger.warning(f"Failed to set motor voltage to {voltage}V")

    @pyqtSlot()
    def _on_accel_reinit_clicked(self) -> None:
        """Handle accelerometer reinitialize button click."""
        if self.controller:
            logger.info("User requested accelerometer reinitialization")
            success = self.controller.reinitialize_accelerometer()
            if success:
                logger.info("Accelerometer reinitialized successfully")
            else:
                logger.warning("Accelerometer reinitialization failed")

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        status_text = "Connected" if connected else "Disconnected"
        self.connection_status_label.setText(status_text)
        self.connection_status_label.setStyleSheet(
            f"font-weight: bold; color: {'#4CAF50' if connected else '#f44336'};"
        )
        logger.info(f"GPIO connection status: {status_text}")
        self._update_ui_state()

        # Emit signal to notify other components (e.g., main window for watchdog)
        self.gpio_connection_changed.emit(connected)

    @pyqtSlot(bool)
    def _on_motor_changed(self, enabled: bool) -> None:
        """Handle motor state change."""
        self.motor_enabled = enabled
        status_text = "ON" if enabled else "OFF"
        self.motor_status_label.setText(status_text)
        self.motor_status_label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {'#4CAF50' if enabled else '#9E9E9E'};"
        )
        self._update_ui_state()

    @pyqtSlot(bool)
    def _on_vibration_changed(self, detected: bool) -> None:
        """Handle vibration detection change."""
        self.vibration_detected = detected
        status_text = "VIBRATING" if detected else "NO VIBRATION"
        self.vibration_status_label.setText(status_text)
        self.vibration_status_label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {'#4CAF50' if detected else '#f44336'};"
        )

    @pyqtSlot(float)
    def _on_vibration_level_changed(self, magnitude: float) -> None:
        """Handle vibration magnitude update."""
        self.vibration_level_label.setText(f"{magnitude:.3f} g")
        # Color code based on threshold (0.8g)
        if magnitude > 0.8:
            color = "#4CAF50"  # Green - motor running
        elif magnitude > 0.5:
            color = "#FF9800"  # Orange - intermediate
        else:
            color = "#2196F3"  # Blue - baseline/off
        self.vibration_level_label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {color};"
        )

    @pyqtSlot(float)
    def _on_voltage_changed(self, voltage: float) -> None:
        """Handle photodiode voltage update."""
        self.photodiode_voltage = voltage
        self.voltage_label.setText(f"{voltage:.3f} V")

    @pyqtSlot(float)
    def _on_power_changed(self, power_mw: float) -> None:
        """Handle photodiode power update."""
        self.photodiode_power = power_mw
        self.power_label.setText(f"{power_mw:.1f} mW")

    @pyqtSlot(bool)
    def _on_safety_changed(self, safety_ok: bool) -> None:
        """Handle safety interlock status change."""
        self.safety_ok = safety_ok

        if safety_ok:
            self.safety_status_label.setText("INTERLOCKS SATISFIED - LASER ENABLED")
            self.safety_status_label.setStyleSheet(
                "font-weight: bold; font-size: 16px; padding: 10px; "
                "background-color: #4CAF50; color: white; border-radius: 5px;"
            )
        else:
            self.safety_status_label.setText("INTERLOCKS NOT SATISFIED - LASER DISABLED")
            self.safety_status_label.setStyleSheet(
                "font-weight: bold; font-size: 16px; padding: 10px; "
                "background-color: #f44336; color: white; border-radius: 5px;"
            )

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from controller."""
        logger.error(f"GPIO error: {error_msg}")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
