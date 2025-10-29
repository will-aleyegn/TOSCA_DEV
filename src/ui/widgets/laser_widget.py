"""
Laser control widget for the TOSCA GUI.

Provides laser driver control interface.
"""

import logging
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.hardware.laser_controller import LaserController

if TYPE_CHECKING:
    from hardware.gpio_controller import GPIOController

logger = logging.getLogger(__name__)


class LaserWidget(QWidget):
    """
    Laser control widget with connection and power controls.
    """

    def __init__(self) -> None:
        super().__init__()

        # Create controller
        self.controller: Optional[LaserController] = None
        self.gpio_controller: Optional["GPIOController"] = None

        # State tracking
        self.is_connected = False
        self.is_output_enabled = False
        self.is_aiming_laser_enabled = False
        self.current_ma = 0.0
        self.temperature_c = 0.0

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Constrain maximum width to prevent excessive horizontal stretching
        self.setMaximumWidth(800)

        # Connection controls
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Status display
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        # Power control
        power_group = self._create_power_control_group()
        layout.addWidget(power_group)

        # Temperature control
        temp_group = self._create_temperature_group()
        layout.addWidget(temp_group)

        # Aiming laser control
        aiming_group = self._create_aiming_laser_group()
        layout.addWidget(aiming_group)

        layout.addStretch()

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection")
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

        group.setLayout(layout)
        return group

    def _create_status_group(self) -> QGroupBox:
        """Create status display group."""
        group = QGroupBox("Status")
        layout = QGridLayout()

        # Row 1: Connection and Output
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Connection:"), 0, 0)
        layout.addWidget(self.connection_status_label, 0, 1)

        self.output_status_label = QLabel("OFF")
        self.output_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Output:"), 0, 2)
        layout.addWidget(self.output_status_label, 0, 3)

        # Row 2: Current and Temperature
        self.current_label = QLabel("-- mA")
        self.current_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Current:"), 1, 0)
        layout.addWidget(self.current_label, 1, 1)

        self.temperature_label = QLabel("-- °C")
        self.temperature_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Temperature:"), 1, 2)
        layout.addWidget(self.temperature_label, 1, 3)

        group.setLayout(layout)
        return group

    def _create_power_control_group(self) -> QGroupBox:
        """Create power control group."""
        group = QGroupBox("Laser Power")
        layout = QVBoxLayout()

        # Current control
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current (mA):"))
        self.current_spinbox = QDoubleSpinBox()
        self.current_spinbox.setRange(0, 2000)
        self.current_spinbox.setSingleStep(10)
        self.current_spinbox.setValue(0)
        self.current_spinbox.setEnabled(False)
        self.current_spinbox.valueChanged.connect(self._on_current_changed)
        current_layout.addWidget(self.current_spinbox)
        layout.addLayout(current_layout)

        # Current slider
        self.current_slider = QSlider(Qt.Orientation.Horizontal)
        self.current_slider.setRange(0, 2000)
        self.current_slider.setValue(0)
        self.current_slider.setEnabled(False)
        layout.addWidget(self.current_slider)

        # Link spinbox and slider
        self.current_spinbox.valueChanged.connect(self.current_slider.setValue)
        self.current_slider.valueChanged.connect(self.current_spinbox.setValue)

        # Output control buttons
        btn_layout = QHBoxLayout()

        self.enable_btn = QPushButton("ENABLE OUTPUT")
        self.enable_btn.setMinimumHeight(50)
        self.enable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;"
        )
        self.enable_btn.clicked.connect(lambda: self._on_output_clicked(True))
        self.enable_btn.setEnabled(False)
        btn_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("DISABLE OUTPUT")
        self.disable_btn.setMinimumHeight(50)
        self.disable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #f44336; color: white;"
        )
        self.disable_btn.clicked.connect(lambda: self._on_output_clicked(False))
        self.disable_btn.setEnabled(False)
        btn_layout.addWidget(self.disable_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def _create_temperature_group(self) -> QGroupBox:
        """Create TEC temperature control group."""
        group = QGroupBox("TEC Temperature")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Setpoint (°C):"))
        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(15, 35)
        self.temp_spinbox.setValue(25.0)
        self.temp_spinbox.setDecimals(1)
        self.temp_spinbox.setEnabled(False)
        layout.addWidget(self.temp_spinbox)

        self.set_temp_btn = QPushButton("Set Temperature")
        self.set_temp_btn.clicked.connect(self._on_set_temperature)
        self.set_temp_btn.setEnabled(False)
        layout.addWidget(self.set_temp_btn)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_aiming_laser_group(self) -> QGroupBox:
        """Create aiming laser control group."""
        group = QGroupBox("Aiming Laser")
        layout = QHBoxLayout()

        self.aiming_laser_on_btn = QPushButton("Aiming ON")
        self.aiming_laser_on_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; background-color: #2196F3; color: white;"
        )
        self.aiming_laser_on_btn.clicked.connect(lambda: self._on_aiming_laser_clicked(True))
        self.aiming_laser_on_btn.setEnabled(False)
        layout.addWidget(self.aiming_laser_on_btn)

        self.aiming_laser_off_btn = QPushButton("Aiming OFF")
        self.aiming_laser_off_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; background-color: #9E9E9E; color: white;"
        )
        self.aiming_laser_off_btn.clicked.connect(lambda: self._on_aiming_laser_clicked(False))
        self.aiming_laser_off_btn.setEnabled(False)
        layout.addWidget(self.aiming_laser_off_btn)

        group.setLayout(layout)
        return group

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection status."""
        # Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)

        # Power controls
        controls_enabled = self.is_connected
        self.current_spinbox.setEnabled(controls_enabled)
        self.current_slider.setEnabled(controls_enabled)
        self.temp_spinbox.setEnabled(controls_enabled)
        self.set_temp_btn.setEnabled(controls_enabled)

        # Output buttons
        self.enable_btn.setEnabled(controls_enabled and not self.is_output_enabled)
        self.disable_btn.setEnabled(controls_enabled and self.is_output_enabled)

        # Aiming laser buttons (enabled when GPIO is connected)
        gpio_connected = bool(self.gpio_controller and self.gpio_controller.is_connected)
        self.aiming_laser_on_btn.setEnabled(gpio_connected and not self.is_aiming_laser_enabled)
        self.aiming_laser_off_btn.setEnabled(gpio_connected and self.is_aiming_laser_enabled)

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        logger.info("Connecting to laser driver...")

        # Create controller if needed
        if not self.controller:
            self.controller = LaserController()

            # Connect signals
            self.controller.connection_changed.connect(self._on_connection_changed)
            self.controller.output_changed.connect(self._on_output_changed)
            self.controller.current_changed.connect(self._on_current_changed_signal)
            self.controller.temperature_changed.connect(self._on_temperature_changed)
            self.controller.error_occurred.connect(self._on_error)

        # Connect to COM4 by default (adjust as needed)
        success = self.controller.connect("COM4")

        if not success:
            logger.error("Failed to connect to laser driver")
            self.connection_status_label.setText("Connection failed")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from laser driver...")
            self.controller.disconnect()

    @pyqtSlot()
    def _on_set_temperature(self) -> None:
        """Handle set temperature button click."""
        if self.controller:
            temp = self.temp_spinbox.value()
            logger.info(f"Setting TEC temperature to {temp:.1f}°C")
            self.controller.set_temperature(temp)

    @pyqtSlot(float)
    def _on_current_changed(self, value: float) -> None:
        """Handle current spinbox/slider change."""
        if self.controller and self.is_connected:
            self.controller.set_current(value)

    @pyqtSlot(bool)
    def _on_output_clicked(self, enable: bool) -> None:
        """Handle output enable/disable button click."""
        if not self.controller:
            return

        # Check safety manager before enabling
        if enable:
            if hasattr(self, "safety_manager") and self.safety_manager:
                if not self.safety_manager.is_laser_enable_permitted():
                    status = self.safety_manager.get_safety_status_text()
                    logger.error(f"Laser enable denied: {status}")
                    self.controller.error_occurred.emit(f"Safety check failed: {status}")
                    return
            else:
                logger.warning("No safety manager - enabling laser without safety checks")

        self.controller.set_output(enable)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        status_text = "Connected" if connected else "Disconnected"
        self.connection_status_label.setText(status_text)
        self.connection_status_label.setStyleSheet(
            f"font-weight: bold; color: {'#4CAF50' if connected else '#f44336'};"
        )
        logger.info(f"Connection status: {status_text}")
        self._update_ui_state()

    @pyqtSlot(bool)
    def _on_output_changed(self, enabled: bool) -> None:
        """Handle output enable status change."""
        self.is_output_enabled = enabled
        status_text = "ON" if enabled else "OFF"
        self.output_status_label.setText(status_text)
        self.output_status_label.setStyleSheet(
            f"font-weight: bold; color: {'#4CAF50' if enabled else '#9E9E9E'};"
        )
        self._update_ui_state()

    @pyqtSlot(float)
    def _on_current_changed_signal(self, current_ma: float) -> None:
        """Handle current update from controller."""
        self.current_ma = current_ma
        self.current_label.setText(f"{current_ma:.1f} mA")

    @pyqtSlot(float)
    def _on_temperature_changed(self, temperature_c: float) -> None:
        """Handle temperature update from controller."""
        self.temperature_c = temperature_c
        self.temperature_label.setText(f"{temperature_c:.1f} °C")

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from controller."""
        logger.error(f"Laser error: {error_msg}")

    @pyqtSlot(bool)
    def _on_aiming_laser_clicked(self, enable: bool) -> None:
        """Handle aiming laser on/off button click."""
        if not self.gpio_controller:
            logger.warning("GPIO controller not available")
            return

        if enable:
            self.gpio_controller.start_aiming_laser()
        else:
            self.gpio_controller.stop_aiming_laser()

    @pyqtSlot(bool)
    def _on_aiming_laser_changed(self, enabled: bool) -> None:
        """Handle aiming laser state change from GPIO controller."""
        self.is_aiming_laser_enabled = enabled
        logger.info(f"Aiming laser: {'ON' if enabled else 'OFF'}")
        self._update_ui_state()

    def set_gpio_controller(self, gpio_controller: Optional["GPIOController"]) -> None:
        """
        Set the GPIO controller for aiming laser control.

        Args:
            gpio_controller: GPIOController instance
        """
        self.gpio_controller = gpio_controller

        if gpio_controller:
            gpio_controller.aiming_laser_changed.connect(self._on_aiming_laser_changed)
            logger.info("GPIO controller connected to laser widget")

        self._update_ui_state()

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
