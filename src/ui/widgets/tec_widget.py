"""
TEC control widget for the TOSCA GUI.

Provides thermoelectric cooler (TEC) temperature control interface.
"""

import logging
from typing import Optional

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

from src.hardware.tec_controller import TECController

logger = logging.getLogger(__name__)


class TECWidget(QWidget):
    """
    TEC control widget with connection and temperature controls.
    """

    def __init__(self) -> None:
        super().__init__()

        # Create controller
        self.controller: Optional[TECController] = None

        # State tracking
        self.is_connected = False
        self.is_output_enabled = False
        self.current_temperature_c = 0.0
        self.setpoint_temperature_c = 25.0

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

        # Temperature control
        temp_control_group = self._create_temperature_control_group()
        layout.addWidget(temp_control_group)

        layout.addStretch()

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("TEC Connection")
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
        group = QGroupBox("TEC Status")
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

        # Row 2: Current Temperature and Setpoint
        self.temperature_label = QLabel("-- °C")
        self.temperature_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(QLabel("Temperature:"), 1, 0)
        layout.addWidget(self.temperature_label, 1, 1)

        self.setpoint_label = QLabel("-- °C")
        self.setpoint_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Setpoint:"), 1, 2)
        layout.addWidget(self.setpoint_label, 1, 3)

        # Row 3: Current and Voltage
        self.current_label = QLabel("-- A")
        self.current_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Current:"), 2, 0)
        layout.addWidget(self.current_label, 2, 1)

        self.voltage_label = QLabel("-- V")
        self.voltage_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Voltage:"), 2, 2)
        layout.addWidget(self.voltage_label, 2, 3)

        group.setLayout(layout)
        return group

    def _create_temperature_control_group(self) -> QGroupBox:
        """Create temperature control group."""
        group = QGroupBox("Temperature Control")
        layout = QVBoxLayout()

        # Temperature setpoint control
        setpoint_layout = QHBoxLayout()
        setpoint_layout.addWidget(QLabel("Setpoint (°C):"))

        self.temp_spinbox = QDoubleSpinBox()
        # Range will be updated from device limits after connection
        # Initial safe range for medical/biological applications
        self.temp_spinbox.setRange(15, 35)
        self.temp_spinbox.setValue(25.0)
        self.temp_spinbox.setDecimals(1)
        self.temp_spinbox.setSingleStep(0.5)
        self.temp_spinbox.setEnabled(False)
        setpoint_layout.addWidget(self.temp_spinbox)

        self.set_temp_btn = QPushButton("Set Temperature")
        self.set_temp_btn.clicked.connect(self._on_set_temperature)
        self.set_temp_btn.setEnabled(False)
        setpoint_layout.addWidget(self.set_temp_btn)

        setpoint_layout.addStretch()
        layout.addLayout(setpoint_layout)

        # Output control buttons
        btn_layout = QHBoxLayout()

        self.enable_btn = QPushButton("ENABLE TEC OUTPUT")
        self.enable_btn.setMinimumHeight(50)
        self.enable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #2196F3; color: white;"
        )
        self.enable_btn.clicked.connect(lambda: self._on_output_clicked(True))
        self.enable_btn.setEnabled(False)
        btn_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("DISABLE TEC OUTPUT")
        self.disable_btn.setMinimumHeight(50)
        self.disable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #9E9E9E; color: white;"
        )
        self.disable_btn.clicked.connect(lambda: self._on_output_clicked(False))
        self.disable_btn.setEnabled(False)
        btn_layout.addWidget(self.disable_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection status."""
        # Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)

        # Temperature controls
        controls_enabled = self.is_connected
        self.temp_spinbox.setEnabled(controls_enabled)
        self.set_temp_btn.setEnabled(controls_enabled)

        # Output buttons
        self.enable_btn.setEnabled(controls_enabled and not self.is_output_enabled)
        self.disable_btn.setEnabled(controls_enabled and self.is_output_enabled)

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        logger.info("Connecting to TEC controller...")

        # Create controller if needed
        if not self.controller:
            self.controller = TECController()

            # Connect signals
            self.controller.connection_changed.connect(self._on_connection_changed)
            self.controller.output_changed.connect(self._on_output_changed)
            self.controller.temperature_changed.connect(self._on_temperature_changed)
            self.controller.temperature_setpoint_changed.connect(self._on_setpoint_changed)
            self.controller.current_changed.connect(self._on_current_changed)
            self.controller.voltage_changed.connect(self._on_voltage_changed)
            self.controller.error_occurred.connect(self._on_error)
            self.controller.limit_warning.connect(self._on_limit_warning)

        # Connect to COM9 (TEC controller port)
        success = self.controller.connect("COM9")

        if not success:
            logger.error("Failed to connect to TEC controller")
            self.connection_status_label.setText("Connection failed")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from TEC controller...")
            self.controller.disconnect()

    @pyqtSlot()
    def _on_set_temperature(self) -> None:
        """Handle set temperature button click."""
        if self.controller:
            temp = self.temp_spinbox.value()
            logger.info(f"Setting TEC temperature to {temp:.1f}°C")
            success = self.controller.set_temperature(temp)
            if success:
                self.setpoint_temperature_c = temp
                self._update_status_display()

    @pyqtSlot(bool)
    def _on_output_clicked(self, enable: bool) -> None:
        """Handle output enable/disable button click."""
        if self.controller:
            action = "enable" if enable else "disable"
            logger.info(f"Attempting to {action} TEC output")
            self.controller.set_output(enable)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection state change."""
        self.is_connected = connected

        if connected:
            self.connection_status_label.setText("Connected (COM9)")
            self.connection_status_label.setStyleSheet("color: green; font-weight: bold;")
            logger.info("TEC controller connected successfully")

            # Update temperature spinbox range from device limits
            if self.controller:
                self.temp_spinbox.setRange(
                    self.controller.min_temperature_c, self.controller.max_temperature_c
                )
                logger.info(
                    f"Temperature range updated: {self.controller.min_temperature_c:.1f}°C "
                    f"to {self.controller.max_temperature_c:.1f}°C"
                )
        else:
            self.connection_status_label.setText("Disconnected")
            self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.is_output_enabled = False
            logger.info("TEC controller disconnected")

        self._update_ui_state()
        self._update_status_display()

    @pyqtSlot(bool)
    def _on_output_changed(self, enabled: bool) -> None:
        """Handle output state change."""
        self.is_output_enabled = enabled

        if enabled:
            self.output_status_label.setText("ON")
            self.output_status_label.setStyleSheet("color: blue; font-weight: bold;")
            logger.info("TEC output enabled")
        else:
            self.output_status_label.setText("OFF")
            self.output_status_label.setStyleSheet("color: gray; font-weight: bold;")
            logger.info("TEC output disabled")

        self._update_ui_state()

    @pyqtSlot(float)
    def _on_temperature_changed(self, temperature: float) -> None:
        """Handle temperature reading update."""
        self.current_temperature_c = temperature
        self._update_status_display()

    @pyqtSlot(float)
    def _on_setpoint_changed(self, setpoint: float) -> None:
        """Handle setpoint change from device."""
        self.setpoint_temperature_c = setpoint
        self.temp_spinbox.setValue(setpoint)
        self._update_status_display()

    @pyqtSlot(float)
    def _on_current_changed(self, current: float) -> None:
        """Handle current reading update."""
        self.current_label.setText(f"{current:.2f} A")

    @pyqtSlot(float)
    def _on_voltage_changed(self, voltage: float) -> None:
        """Handle voltage reading update."""
        self.voltage_label.setText(f"{voltage:.2f} V")

    @pyqtSlot(str)
    def _on_error(self, error_message: str) -> None:
        """Handle error from controller."""
        logger.error(f"TEC controller error: {error_message}")
        self.connection_status_label.setText(f"Error: {error_message}")
        self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")

    @pyqtSlot(str)
    def _on_limit_warning(self, warning_message: str) -> None:
        """Handle limit warning from controller."""
        logger.warning(f"TEC limit warning: {warning_message}")

    def _update_status_display(self) -> None:
        """Update status display labels."""
        if self.is_connected:
            self.temperature_label.setText(f"{self.current_temperature_c:.2f} °C")
            self.setpoint_label.setText(f"{self.setpoint_temperature_c:.1f} °C")
        else:
            self.temperature_label.setText("-- °C")
            self.setpoint_label.setText("-- °C")
            self.current_label.setText("-- A")
            self.voltage_label.setText("-- V")

    def get_controller(self) -> Optional[TECController]:
        """
        Get the TEC controller instance.

        Returns:
            TECController instance or None if not created
        """
        return self.controller
