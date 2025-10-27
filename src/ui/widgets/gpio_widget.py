"""
GPIO safety interlock widget for the TOSCA GUI.

Provides safety monitoring interface for smoothing device and photodiode.
"""

import logging
from typing import Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
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

        layout.addLayout(status_layout)

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

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        logger.info("Connecting to GPIO...")

        # Create controller if needed
        if not self.controller:
            try:
                self.controller = GPIOController()

                # Connect signals
                self.controller.connection_changed.connect(self._on_connection_changed)
                self.controller.smoothing_motor_changed.connect(self._on_motor_changed)
                self.controller.smoothing_vibration_changed.connect(self._on_vibration_changed)
                self.controller.photodiode_voltage_changed.connect(self._on_voltage_changed)
                self.controller.photodiode_power_changed.connect(self._on_power_changed)
                self.controller.safety_interlock_changed.connect(self._on_safety_changed)
                self.controller.error_occurred.connect(self._on_error)

            except ImportError as e:
                logger.error(f"Failed to create GPIO controller: {e}")
                self.connection_status_label.setText("Libraries not installed")
                return

        # Get COM port from config
        config = get_config()
        com_port = config.hardware.gpio.com_port

        # Connect to GPIO
        logger.info(f"Attempting to connect to Arduino on {com_port}")
        success = self.controller.connect(port=com_port)

        if not success:
            logger.error(f"Failed to connect to GPIO on {com_port}")
            self.connection_status_label.setText(f"Connection failed ({com_port})")

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
