"""
Compact smoothing motor status and control widget.

Designed for embedding in active treatment dashboard.
Provides essential motor controls and live status monitoring.
"""

import logging
from typing import Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class SmoothingStatusWidget(QWidget):
    """
    Compact smoothing motor status widget for active treatment dashboard.

    Features:
    - Motor Enable/Disable buttons
    - Voltage spinbox + Apply button
    - Live vibration magnitude
    - Live photodiode power
    """

    def __init__(self) -> None:
        super().__init__()
        self.controller: Optional[Any] = None
        self.is_connected = False
        self.motor_enabled = False

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize compact UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Main group
        group = QGroupBox("Smoothing Motor")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        # 1. Motor Control Buttons (horizontal)
        motor_layout = QHBoxLayout()

        self.enable_btn = QPushButton("Enable")
        self.enable_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 11px; font-weight: bold;"
        )
        self.enable_btn.clicked.connect(lambda: self._on_motor_control(True))
        self.enable_btn.setEnabled(False)
        self.enable_btn.setMinimumHeight(30)
        motor_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("Disable")
        self.disable_btn.setStyleSheet(
            "background-color: #f44336; color: white; font-size: 11px; font-weight: bold;"
        )
        self.disable_btn.clicked.connect(lambda: self._on_motor_control(False))
        self.disable_btn.setEnabled(False)
        self.disable_btn.setMinimumHeight(30)
        motor_layout.addWidget(self.disable_btn)

        group_layout.addLayout(motor_layout)

        # 2. Voltage Control (horizontal)
        voltage_layout = QHBoxLayout()
        voltage_label = QLabel("Voltage:")
        voltage_label.setStyleSheet("font-size: 11px;")
        voltage_layout.addWidget(voltage_label)

        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0.0, 3.0)
        self.voltage_spinbox.setSingleStep(0.1)
        self.voltage_spinbox.setValue(2.0)
        self.voltage_spinbox.setSuffix(" V")
        self.voltage_spinbox.setEnabled(False)
        self.voltage_spinbox.setStyleSheet("font-size: 11px;")
        self.voltage_spinbox.valueChanged.connect(self._on_voltage_changed)
        voltage_layout.addWidget(self.voltage_spinbox)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("font-size: 11px;")
        self.apply_btn.clicked.connect(self._on_apply_voltage)
        voltage_layout.addWidget(self.apply_btn)

        group_layout.addLayout(voltage_layout)

        # 3. Live Status (grid)
        status_layout = QGridLayout()

        # Vibration
        vib_label = QLabel("Vibration:")
        vib_label.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(vib_label, 0, 0)

        self.vibration_label = QLabel("-- g")
        self.vibration_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #2196F3;")
        status_layout.addWidget(self.vibration_label, 0, 1)

        # Photodiode
        photo_label = QLabel("Photodiode:")
        photo_label.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(photo_label, 1, 0)

        self.photodiode_label = QLabel("-- mW")
        self.photodiode_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #2196F3;")
        status_layout.addWidget(self.photodiode_label, 1, 1)

        group_layout.addLayout(status_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def set_gpio_controller(self, controller: Any) -> None:
        """Connect to GPIO controller and subscribe to signals."""
        self.controller = controller

        # Connect signals
        controller.connection_changed.connect(self._on_connection_changed)
        controller.smoothing_motor_changed.connect(self._on_motor_changed)
        controller.vibration_level_changed.connect(self._on_vibration_level_changed)
        controller.photodiode_power_changed.connect(self._on_power_changed)

        # Update initial state
        self.is_connected = controller.is_connected if controller else False
        self._update_controls()

        logger.info("SmoothingStatusWidget connected to GPIO controller")

    def _update_controls(self) -> None:
        """Update control states based on connection and motor status."""
        controls_enabled = self.is_connected

        self.enable_btn.setEnabled(controls_enabled and not self.motor_enabled)
        self.disable_btn.setEnabled(controls_enabled and self.motor_enabled)

        voltage_enabled = controls_enabled and self.motor_enabled
        self.voltage_spinbox.setEnabled(voltage_enabled)
        if not voltage_enabled:
            self.apply_btn.setEnabled(False)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle GPIO connection status change."""
        self.is_connected = connected
        self._update_controls()

    @pyqtSlot(bool)
    def _on_motor_changed(self, enabled: bool) -> None:
        """Handle motor state change."""
        self.motor_enabled = enabled
        self._update_controls()

    @pyqtSlot(float)
    def _on_vibration_level_changed(self, magnitude: float) -> None:
        """Update vibration magnitude display."""
        self.vibration_label.setText(f"{magnitude:.2f} g")

        # Color code
        if magnitude > 0.8:
            color = "#4CAF50"  # Green - motor running
        elif magnitude > 0.5:
            color = "#FF9800"  # Orange
        else:
            color = "#2196F3"  # Blue

        self.vibration_label.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {color};")

    @pyqtSlot(float)
    def _on_power_changed(self, power_mw: float) -> None:
        """Update photodiode power display."""
        self.photodiode_label.setText(f"{power_mw:.1f} mW")

    def _on_motor_control(self, enable: bool) -> None:
        """Handle motor enable/disable button click."""
        if self.controller:
            if enable:
                self.controller.start_smoothing_motor()
                logger.info("Smoothing motor enabled via active treatment dashboard")
            else:
                self.controller.stop_smoothing_motor()
                logger.info("Smoothing motor disabled via active treatment dashboard")

    def _on_voltage_changed(self, voltage: float) -> None:
        """Enable Apply button when voltage changes."""
        if self.is_connected and self.motor_enabled:
            self.apply_btn.setEnabled(True)

    def _on_apply_voltage(self) -> None:
        """Apply voltage setting to motor."""
        if self.controller and self.is_connected and self.motor_enabled:
            voltage = self.voltage_spinbox.value()
            pwm = int((voltage / 5.0) * 255)
            success = self.controller.set_motor_speed(pwm)
            if success:
                self.apply_btn.setEnabled(False)
                logger.info(
                    f"Motor voltage set to {voltage:.1f}V (PWM: {pwm}) via active treatment"
                )
