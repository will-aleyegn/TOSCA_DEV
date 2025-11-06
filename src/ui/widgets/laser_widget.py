"""
Laser control widget for the TOSCA GUI.

Provides laser driver control interface, TEC control, and aiming laser control.
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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from hardware.laser_controller import LaserController
from hardware.tec_controller import TECController
from ui.constants import WIDGET_WIDTH_GRID
from ui.design_tokens import ButtonSizes

if TYPE_CHECKING:
    from hardware.gpio_controller import GPIOController

logger = logging.getLogger(__name__)


class LaserWidget(QWidget):
    """
    Unified laser systems control widget with treatment laser, TEC, and aiming laser controls.
    """

    def __init__(
        self,
        controller: Optional[LaserController] = None,
        tec_controller: Optional[TECController] = None,
    ) -> None:
        super().__init__()

        # Reference to controllers (created and managed by MainWindow)
        self.controller = controller
        self.tec_controller = tec_controller
        self.gpio_controller: Optional["GPIOController"] = None

        # State tracking - Laser
        self.is_connected = False
        self.is_output_enabled = False
        self.is_aiming_laser_enabled = False
        self.current_ma = 0.0

        # State tracking - TEC
        self.is_tec_connected = False
        self.is_tec_output_enabled = False
        self.current_temperature_c = 0.0
        self.setpoint_temperature_c = 25.0

        # Initialize UI
        self._init_ui()

        # Connect to controller signals if controllers provided
        if self.controller:
            self._connect_controller_signals()
        if self.tec_controller:
            self._connect_tec_controller_signals()

    def _connect_controller_signals(self) -> None:
        """Connect to laser controller signals (called when controller is injected)."""
        if not self.controller:
            return

        self.controller.connection_changed.connect(self._on_connection_changed)
        self.controller.output_changed.connect(self._on_output_changed)
        self.controller.current_changed.connect(self._on_current_changed_signal)
        self.controller.error_occurred.connect(self._on_error)
        logger.debug("LaserWidget signals connected to LaserController")

    def _connect_tec_controller_signals(self) -> None:
        """Connect to TEC controller signals (called when controller is injected)."""
        if not self.tec_controller:
            return

        self.tec_controller.connection_changed.connect(self._on_tec_connection_changed)
        self.tec_controller.output_changed.connect(self._on_tec_output_changed)
        self.tec_controller.temperature_changed.connect(self._on_tec_temperature_changed)
        self.tec_controller.temperature_setpoint_changed.connect(
            self._on_tec_setpoint_changed
        )
        self.tec_controller.error_occurred.connect(self._on_tec_error)
        logger.debug("LaserWidget signals connected to TECController")

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main widget layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Let grid layout control width (removed max width constraint for better horizontal space usage)

        # Create master QGroupBox for all laser subsystems
        master_group = QGroupBox("LASER SYSTEMS")
        master_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 11pt;
                font-weight: bold;
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            """
        )

        # Inner layout for all subsystems
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Consistent spacing between sections
        master_group.setLayout(layout)

        # (2) TEC Temperature Control - Initialize first for thermal stabilization
        tec_group = self._create_tec_control_group()
        layout.addWidget(tec_group)

        # (3) Treatment Laser - Enable after TEC stabilization
        # Add section label with initialization sequence indicator
        treatment_label = QLabel("(3) Treatment Laser  ↓")
        treatment_label.setStyleSheet(
            "font-size: 10pt; font-weight: bold; color: #888; padding: 8px 0px 4px 0px;"
        )
        layout.addWidget(treatment_label)

        # Status display (first - observe current state)
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        # Connection controls (second - establish connection)
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Power control (third - control output after connection)
        power_group = self._create_power_control_group()
        layout.addWidget(power_group)

        # Aiming laser control (at bottom, no number - auxiliary system)
        aiming_group = self._create_aiming_laser_group()
        layout.addWidget(aiming_group)

        layout.addStretch()

        # Add master group to main widget
        main_layout.addWidget(master_group)

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection")
        layout = QHBoxLayout()
        layout.setSpacing(8)  # Consistent button spacing

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.connect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(90)  # Secondary action width (grid layout)
        self.disconnect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
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
        layout.addWidget(QLabel("Status:"), 0, 0)  # Simplified from "Connection:"
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

        group.setLayout(layout)
        return group

    def _create_power_control_group(self) -> QGroupBox:
        """Create power control group."""
        group = QGroupBox("Treatment Laser Power")
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Consistent spacing within power controls

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

        # Link spinbox and slider (convert float to int for slider)
        self.current_spinbox.valueChanged.connect(
            lambda val: self.current_slider.setValue(int(val))
        )
        self.current_slider.valueChanged.connect(self.current_spinbox.setValue)

        # Output control buttons
        btn_layout = QHBoxLayout()

        self.enable_btn = QPushButton("ENABLE OUTPUT")
        self.enable_btn.setFixedWidth(140)  # Critical action width (grid layout)
        self.enable_btn.setMinimumHeight(ButtonSizes.PRIMARY)  # 50px
        self.enable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;"
        )
        self.enable_btn.clicked.connect(lambda: self._on_output_clicked(True))
        self.enable_btn.setEnabled(False)
        btn_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("DISABLE OUTPUT")
        self.disable_btn.setFixedWidth(140)  # Critical action width (grid layout)
        self.disable_btn.setMinimumHeight(ButtonSizes.PRIMARY)  # 50px
        self.disable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #f44336; color: white;"
        )
        self.disable_btn.clicked.connect(lambda: self._on_output_clicked(False))
        self.disable_btn.setEnabled(False)
        btn_layout.addWidget(self.disable_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def _create_aiming_laser_group(self) -> QGroupBox:
        """Create aiming laser control group with power and ON/OFF controls."""
        group = QGroupBox("Aiming Laser Power Control")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)

        # Power control row (spinbox + slider)
        power_layout = QHBoxLayout()
        power_layout.setSpacing(8)

        power_label = QLabel("Power (DAC):")
        power_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        power_layout.addWidget(power_label)

        self.aiming_power_spinbox = QSpinBox()
        self.aiming_power_spinbox.setRange(0, 4095)  # 12-bit DAC (MCP4725)
        self.aiming_power_spinbox.setValue(2048)  # Default 50% power
        self.aiming_power_spinbox.setFixedWidth(80)
        self.aiming_power_spinbox.setEnabled(False)
        self.aiming_power_spinbox.valueChanged.connect(self._on_aiming_power_spinbox_changed)
        power_layout.addWidget(self.aiming_power_spinbox)

        self.aiming_power_slider = QSlider(Qt.Orientation.Horizontal)
        self.aiming_power_slider.setRange(0, 4095)
        self.aiming_power_slider.setValue(2048)
        self.aiming_power_slider.setMinimumWidth(200)
        self.aiming_power_slider.setEnabled(False)
        self.aiming_power_slider.valueChanged.connect(self._on_aiming_power_slider_changed)
        power_layout.addWidget(self.aiming_power_slider)

        power_layout.addStretch()
        main_layout.addLayout(power_layout)

        # ON/OFF button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.aiming_laser_on_btn = QPushButton("Aiming ON")
        self.aiming_laser_on_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.aiming_laser_on_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.aiming_laser_on_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; background-color: #2196F3; color: white;"
        )
        self.aiming_laser_on_btn.clicked.connect(lambda: self._on_aiming_laser_clicked(True))
        self.aiming_laser_on_btn.setEnabled(False)
        button_layout.addWidget(self.aiming_laser_on_btn)

        self.aiming_laser_off_btn = QPushButton("Aiming OFF")
        self.aiming_laser_off_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.aiming_laser_off_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.aiming_laser_off_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; background-color: #9E9E9E; color: white;"
        )
        self.aiming_laser_off_btn.clicked.connect(lambda: self._on_aiming_laser_clicked(False))
        self.aiming_laser_off_btn.setEnabled(False)
        button_layout.addWidget(self.aiming_laser_off_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        group.setLayout(main_layout)
        return group

    def _create_tec_control_group(self) -> QGroupBox:
        """Create TEC (thermoelectric cooler) control group."""
        group = QGroupBox("(2) TEC Temperature Control  ↓")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)  # Consistent spacing within section

        # Connection controls
        connection_layout = QHBoxLayout()
        self.tec_connect_btn = QPushButton("TEC Connect")
        self.tec_connect_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.tec_connect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.tec_connect_btn.clicked.connect(self._on_tec_connect_clicked)
        connection_layout.addWidget(self.tec_connect_btn)

        self.tec_disconnect_btn = QPushButton("TEC Disconnect")
        self.tec_disconnect_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.tec_disconnect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.tec_disconnect_btn.clicked.connect(self._on_tec_disconnect_clicked)
        self.tec_disconnect_btn.setEnabled(False)
        connection_layout.addWidget(self.tec_disconnect_btn)
        main_layout.addLayout(connection_layout)

        # Status display
        status_layout = QGridLayout()

        # Row 1: Connection and Output
        self.tec_connection_status_label = QLabel("Disconnected")
        self.tec_connection_status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        status_layout.addWidget(self.tec_connection_status_label, 0, 1)

        self.tec_output_status_label = QLabel("OFF")
        self.tec_output_status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(QLabel("Output:"), 0, 2)
        status_layout.addWidget(self.tec_output_status_label, 0, 3)

        # Row 2: Current Temperature and Setpoint
        self.tec_temperature_label = QLabel("-- °C")
        self.tec_temperature_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(QLabel("Temperature:"), 1, 0)
        status_layout.addWidget(self.tec_temperature_label, 1, 1)

        self.tec_setpoint_label = QLabel("-- °C")
        self.tec_setpoint_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(QLabel("Setpoint:"), 1, 2)
        status_layout.addWidget(self.tec_setpoint_label, 1, 3)

        main_layout.addLayout(status_layout)

        # Temperature setpoint control
        setpoint_layout = QHBoxLayout()
        setpoint_layout.addWidget(QLabel("Setpoint (°C):"))

        self.tec_temp_spinbox = QDoubleSpinBox()
        self.tec_temp_spinbox.setRange(15, 35)  # Safe range for biological applications
        self.tec_temp_spinbox.setValue(25.0)
        self.tec_temp_spinbox.setDecimals(1)
        self.tec_temp_spinbox.setSingleStep(0.5)
        self.tec_temp_spinbox.setEnabled(False)
        setpoint_layout.addWidget(self.tec_temp_spinbox)

        self.tec_set_temp_btn = QPushButton("Set Temperature")
        self.tec_set_temp_btn.setFixedWidth(120)  # Primary action width (grid layout)
        self.tec_set_temp_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.tec_set_temp_btn.clicked.connect(self._on_tec_set_temperature)
        self.tec_set_temp_btn.setEnabled(False)
        setpoint_layout.addWidget(self.tec_set_temp_btn)

        setpoint_layout.addStretch()
        main_layout.addLayout(setpoint_layout)

        # Output control buttons
        btn_layout = QHBoxLayout()

        self.tec_enable_btn = QPushButton("ENABLE TEC")
        self.tec_enable_btn.setFixedWidth(130)  # Critical action width (grid layout)
        self.tec_enable_btn.setMinimumHeight(ButtonSizes.PRIMARY)  # 50px
        self.tec_enable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #2196F3; color: white;"
        )
        self.tec_enable_btn.clicked.connect(lambda: self._on_tec_output_clicked(True))
        self.tec_enable_btn.setEnabled(False)
        btn_layout.addWidget(self.tec_enable_btn)

        self.tec_disable_btn = QPushButton("DISABLE TEC")
        self.tec_disable_btn.setFixedWidth(130)  # Critical action width (grid layout)
        self.tec_disable_btn.setMinimumHeight(ButtonSizes.PRIMARY)  # 50px
        self.tec_disable_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #9E9E9E; color: white;"
        )
        self.tec_disable_btn.clicked.connect(lambda: self._on_tec_output_clicked(False))
        self.tec_disable_btn.setEnabled(False)
        btn_layout.addWidget(self.tec_disable_btn)

        main_layout.addLayout(btn_layout)

        group.setLayout(main_layout)
        return group

    def connect_device(self) -> bool:
        """
        Public method to programmatically connect to laser driver.

        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            logger.warning("Laser already connected")
            return True

        self._on_connect_clicked()
        return self.is_connected

    def disconnect_device(self) -> None:
        """Public method to programmatically disconnect from laser driver."""
        if not self.is_connected:
            logger.debug("Laser already disconnected")
            return

        self._on_disconnect_clicked()

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection status."""
        # Treatment Laser - Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)

        # Treatment Laser - Power controls
        controls_enabled = self.is_connected
        self.current_spinbox.setEnabled(controls_enabled)
        self.current_slider.setEnabled(controls_enabled)

        # Treatment Laser - Output buttons
        self.enable_btn.setEnabled(controls_enabled and not self.is_output_enabled)
        self.disable_btn.setEnabled(controls_enabled and self.is_output_enabled)

        # Aiming laser controls (enabled when GPIO is connected)
        gpio_connected = bool(self.gpio_controller and self.gpio_controller.is_connected)
        self.aiming_power_spinbox.setEnabled(gpio_connected)
        self.aiming_power_slider.setEnabled(gpio_connected)
        self.aiming_laser_on_btn.setEnabled(gpio_connected and not self.is_aiming_laser_enabled)
        self.aiming_laser_off_btn.setEnabled(gpio_connected and self.is_aiming_laser_enabled)

        # TEC - Connection buttons
        self.tec_connect_btn.setEnabled(not self.is_tec_connected)
        self.tec_disconnect_btn.setEnabled(self.is_tec_connected)

        # TEC - Temperature controls
        tec_controls_enabled = self.is_tec_connected
        self.tec_temp_spinbox.setEnabled(tec_controls_enabled)
        self.tec_set_temp_btn.setEnabled(tec_controls_enabled)

        # TEC - Output buttons
        self.tec_enable_btn.setEnabled(tec_controls_enabled and not self.is_tec_output_enabled)
        self.tec_disable_btn.setEnabled(tec_controls_enabled and self.is_tec_output_enabled)

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        if not self.controller:
            error_msg = (
                "Software Error: Laser controller not initialized. "
                "This indicates a configuration issue. "
                "Please restart the application."
            )
            logger.error(f"LaserWidget: No controller available (DI not configured properly)")
            self.connection_status_label.setText("Error: No controller")
            return

        logger.info("Connecting to laser driver...")

        # Connect to COM10 (laser driver port)
        success = self.controller.connect("COM10")

        if not success:
            error_msg = (
                "Failed to connect to laser driver on COM10. "
                "Check: (1) Device is powered on, "
                "(2) USB cable is connected, "
                "(3) COM10 is correct port (check Device Manager)"
            )
            logger.error(error_msg)
            self.connection_status_label.setText("Connection failed - check device")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from laser driver...")
            self.controller.disconnect()

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
        logger.info(f"Laser connection status: {status_text}")
        self._update_ui_state()

        # Notify main window status bar (if available)
        main_window = self.window()
        if main_window and hasattr(main_window, "update_laser_status"):
            main_window.update_laser_status(connected)

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

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from controller."""
        logger.error(f"Laser error: {error_msg}")
        # Update UI to show error to user
        self.connection_status_label.setText(f"Error: {error_msg}")
        self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")

    @pyqtSlot(int)
    def _on_aiming_power_spinbox_changed(self, value: int) -> None:
        """Handle aiming power spinbox value change."""
        # Update slider (block signals to prevent loop)
        self.aiming_power_slider.blockSignals(True)
        self.aiming_power_slider.setValue(value)
        self.aiming_power_slider.blockSignals(False)

        # Send power command to GPIO controller
        if self.gpio_controller and self.gpio_controller.is_connected:
            self.gpio_controller.set_aiming_laser_power(value)
            logger.debug(f"Aiming laser power set to {value} DAC")

    @pyqtSlot(int)
    def _on_aiming_power_slider_changed(self, value: int) -> None:
        """Handle aiming power slider value change."""
        # Update spinbox (block signals to prevent loop)
        self.aiming_power_spinbox.blockSignals(True)
        self.aiming_power_spinbox.setValue(value)
        self.aiming_power_spinbox.blockSignals(False)

        # Send power command to GPIO controller
        if self.gpio_controller and self.gpio_controller.is_connected:
            self.gpio_controller.set_aiming_laser_power(value)
            logger.debug(f"Aiming laser power set to {value} DAC")

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

    # TEC Control Slots

    @pyqtSlot()
    def _on_tec_connect_clicked(self) -> None:
        """Handle TEC connect button click."""
        if not self.tec_controller:
            error_msg = (
                "Software Error: TEC controller not initialized. "
                "This indicates a configuration issue. "
                "Please restart the application."
            )
            logger.error(f"LaserWidget: No TEC controller available (DI not configured properly)")
            self.tec_connection_status_label.setText("Error: No controller")
            return

        logger.info("Connecting to TEC controller...")

        # Connect to COM9 (TEC controller port)
        success = self.tec_controller.connect("COM9")

        if not success:
            error_msg = (
                "Failed to connect to TEC controller on COM9. "
                "Check: (1) Device is powered on, "
                "(2) USB cable is connected, "
                "(3) COM9 is correct port (check Device Manager)"
            )
            logger.error(error_msg)
            self.tec_connection_status_label.setText("Connection failed - check device")

    @pyqtSlot()
    def _on_tec_disconnect_clicked(self) -> None:
        """Handle TEC disconnect button click."""
        if self.tec_controller:
            logger.info("Disconnecting from TEC controller...")
            self.tec_controller.disconnect()

    @pyqtSlot()
    def _on_tec_set_temperature(self) -> None:
        """Handle TEC set temperature button click."""
        if self.tec_controller:
            temp = self.tec_temp_spinbox.value()
            logger.info(f"Setting TEC temperature to {temp:.1f}°C")
            success = self.tec_controller.set_temperature(temp)
            if success:
                self.setpoint_temperature_c = temp
                self._update_tec_status_display()

    @pyqtSlot(bool)
    def _on_tec_output_clicked(self, enable: bool) -> None:
        """Handle TEC output enable/disable button click."""
        if self.tec_controller:
            action = "enable" if enable else "disable"
            logger.info(f"Attempting to {action} TEC output")
            self.tec_controller.set_output(enable)

    @pyqtSlot(bool)
    def _on_tec_connection_changed(self, connected: bool) -> None:
        """Handle TEC connection state change."""
        self.is_tec_connected = connected
        status_text = "Connected (COM9)" if connected else "Disconnected"
        self.tec_connection_status_label.setText(status_text)
        self.tec_connection_status_label.setStyleSheet(
            f"font-weight: bold; color: {'#4CAF50' if connected else '#f44336'};"
        )
        logger.info(f"TEC connection status: {status_text}")

        # Update temperature spinbox range from device limits
        if connected and self.tec_controller:
            self.tec_temp_spinbox.setRange(
                self.tec_controller.min_temperature_c, self.tec_controller.max_temperature_c
            )
            logger.info(
                f"TEC temperature range updated: {self.tec_controller.min_temperature_c:.1f}°C "
                f"to {self.tec_controller.max_temperature_c:.1f}°C"
            )

        self._update_ui_state()
        self._update_tec_status_display()

    @pyqtSlot(bool)
    def _on_tec_output_changed(self, enabled: bool) -> None:
        """Handle TEC output state change."""
        self.is_tec_output_enabled = enabled
        status_text = "ON" if enabled else "OFF"
        self.tec_output_status_label.setText(status_text)
        self.tec_output_status_label.setStyleSheet(
            f"font-weight: bold; color: {'#2196F3' if enabled else '#9E9E9E'};"
        )
        logger.info(f"TEC output: {status_text}")
        self._update_ui_state()

    @pyqtSlot(float)
    def _on_tec_temperature_changed(self, temperature: float) -> None:
        """Handle TEC temperature reading update."""
        self.current_temperature_c = temperature
        self._update_tec_status_display()

    @pyqtSlot(float)
    def _on_tec_setpoint_changed(self, setpoint: float) -> None:
        """Handle TEC setpoint change from device."""
        self.setpoint_temperature_c = setpoint
        # Block signals to prevent infinite loop
        self.tec_temp_spinbox.blockSignals(True)
        self.tec_temp_spinbox.setValue(setpoint)
        self.tec_temp_spinbox.blockSignals(False)
        self._update_tec_status_display()

    @pyqtSlot(str)
    def _on_tec_error(self, error_message: str) -> None:
        """Handle TEC error from controller."""
        logger.error(f"TEC controller error: {error_message}")
        self.tec_connection_status_label.setText(f"Error: {error_message}")
        self.tec_connection_status_label.setStyleSheet("color: red; font-weight: bold;")

    def _update_tec_status_display(self) -> None:
        """Update TEC status display labels."""
        if self.is_tec_connected:
            self.tec_temperature_label.setText(f"{self.current_temperature_c:.2f} °C")
            self.tec_setpoint_label.setText(f"{self.setpoint_temperature_c:.1f} °C")
        else:
            self.tec_temperature_label.setText("-- °C")
            self.tec_setpoint_label.setText("-- °C")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
        if self.tec_controller:
            self.tec_controller.disconnect()
            self.tec_controller = None
