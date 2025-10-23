"""
Actuator control widget for the TOSCA GUI.

Provides manual control of the Xeryon linear actuator with:
- Connection and homing controls
- Absolute position control
- Relative step controls
- Speed adjustment
- Real-time position display
- Status monitoring
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.hardware.actuator_controller import ActuatorController

logger = logging.getLogger(__name__)


class ActuatorWidget(QWidget):
    """
    Widget for manual actuator control.

    Features:
    - Connection management
    - Homing procedure
    - Absolute positioning
    - Relative movements
    - Speed control
    - Real-time position display
    """

    def __init__(self) -> None:
        super().__init__()

        # Create controller
        self.controller: Optional[ActuatorController] = None

        # State tracking
        self.is_connected = False
        self.is_homed = False
        self.current_position_um = 0.0

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Connection group
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Position control group
        position_group = self._create_position_group()
        layout.addWidget(position_group)

        # Step control group
        step_group = self._create_step_group()
        layout.addWidget(step_group)

        # Scan control group
        scan_group = self._create_scan_group()
        layout.addWidget(scan_group)

        # Speed control group
        speed_group = self._create_speed_group()
        layout.addWidget(speed_group)

        # Status display
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        layout.addStretch()

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection")
        layout = QVBoxLayout()

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Home button
        self.home_btn = QPushButton("Find Home (Index)")
        self.home_btn.clicked.connect(self._on_home_clicked)
        self.home_btn.setEnabled(False)
        layout.addWidget(self.home_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)

        group.setLayout(layout)
        return group

    def _create_position_group(self) -> QGroupBox:
        """Create absolute position control group."""
        group = QGroupBox("Absolute Position")
        layout = QHBoxLayout()

        # Position input (home at center, allows negative)
        self.position_input = QDoubleSpinBox()
        self.position_input.setRange(-1500.0, 1500.0)  # ±1500 µm (home at 0)
        self.position_input.setValue(0.0)
        self.position_input.setSuffix(" µm")
        self.position_input.setDecimals(2)
        self.position_input.setSingleStep(10.0)
        self.position_input.setEnabled(False)
        layout.addWidget(QLabel("Target:"))
        layout.addWidget(self.position_input)

        # Move button
        self.move_btn = QPushButton("Move To")
        self.move_btn.clicked.connect(self._on_move_clicked)
        self.move_btn.setEnabled(False)
        layout.addWidget(self.move_btn)

        group.setLayout(layout)
        return group

    def _create_step_group(self) -> QGroupBox:
        """Create relative step control group."""
        group = QGroupBox("Relative Steps")
        layout = QVBoxLayout()

        # Quick step buttons
        button_layout = QHBoxLayout()

        self.step_minus_100_btn = QPushButton("-100 µm")
        self.step_minus_100_btn.clicked.connect(lambda: self._on_step_clicked(-100.0))
        self.step_minus_100_btn.setEnabled(False)
        button_layout.addWidget(self.step_minus_100_btn)

        self.step_minus_10_btn = QPushButton("-10 µm")
        self.step_minus_10_btn.clicked.connect(lambda: self._on_step_clicked(-10.0))
        self.step_minus_10_btn.setEnabled(False)
        button_layout.addWidget(self.step_minus_10_btn)

        self.step_plus_10_btn = QPushButton("+10 µm")
        self.step_plus_10_btn.clicked.connect(lambda: self._on_step_clicked(10.0))
        self.step_plus_10_btn.setEnabled(False)
        button_layout.addWidget(self.step_plus_10_btn)

        self.step_plus_100_btn = QPushButton("+100 µm")
        self.step_plus_100_btn.clicked.connect(lambda: self._on_step_clicked(100.0))
        self.step_plus_100_btn.setEnabled(False)
        button_layout.addWidget(self.step_plus_100_btn)

        layout.addLayout(button_layout)

        # Custom step (removed restrictions - full range)
        custom_layout = QHBoxLayout()
        self.custom_step_input = QDoubleSpinBox()
        self.custom_step_input.setRange(-3000.0, 3000.0)  # ±3000 µm (full range)
        self.custom_step_input.setValue(50.0)
        self.custom_step_input.setSuffix(" µm")
        self.custom_step_input.setDecimals(2)
        self.custom_step_input.setSingleStep(10.0)
        self.custom_step_input.setEnabled(False)
        custom_layout.addWidget(QLabel("Custom:"))
        custom_layout.addWidget(self.custom_step_input)

        self.custom_step_btn = QPushButton("Step")
        self.custom_step_btn.clicked.connect(self._on_custom_step_clicked)
        self.custom_step_btn.setEnabled(False)
        custom_layout.addWidget(self.custom_step_btn)

        layout.addLayout(custom_layout)

        group.setLayout(layout)
        return group

    def _create_scan_group(self) -> QGroupBox:
        """Create continuous scan control group."""
        group = QGroupBox("Continuous Scan (Velocity Control)")
        layout = QVBoxLayout()

        # Scan buttons
        button_layout = QHBoxLayout()

        self.scan_negative_btn = QPushButton("◄ Scan Negative")
        self.scan_negative_btn.clicked.connect(lambda: self._on_scan_clicked(-1))
        self.scan_negative_btn.setEnabled(False)
        self.scan_negative_btn.setStyleSheet("background-color: #4CAF50;")
        button_layout.addWidget(self.scan_negative_btn)

        self.scan_stop_btn = QPushButton("■ STOP")
        self.scan_stop_btn.clicked.connect(self._on_scan_stop_clicked)
        self.scan_stop_btn.setEnabled(False)
        self.scan_stop_btn.setStyleSheet("background-color: #f44336; font-weight: bold;")
        button_layout.addWidget(self.scan_stop_btn)

        self.scan_positive_btn = QPushButton("Scan Positive ►")
        self.scan_positive_btn.clicked.connect(lambda: self._on_scan_clicked(1))
        self.scan_positive_btn.setEnabled(False)
        self.scan_positive_btn.setStyleSheet("background-color: #4CAF50;")
        button_layout.addWidget(self.scan_positive_btn)

        layout.addLayout(button_layout)

        # Info label
        info_label = QLabel("Scan = continuous movement at constant speed until stopped")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 9pt; color: gray;")
        layout.addWidget(info_label)

        group.setLayout(layout)
        return group

    def _create_speed_group(self) -> QGroupBox:
        """Create speed control group."""
        group = QGroupBox("Speed Control")
        layout = QHBoxLayout()

        # Speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 500)  # 50-500 encoder units/cycle
        self.speed_slider.setValue(100)  # Default: slow
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(50)
        self.speed_slider.valueChanged.connect(self._on_speed_display_changed)
        self.speed_slider.sliderReleased.connect(self._on_speed_released)
        self.speed_slider.setEnabled(False)

        self.speed_label = QLabel("100")
        self.speed_label.setMinimumWidth(50)

        layout.addWidget(QLabel("Slow"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(QLabel("Fast"))
        layout.addWidget(self.speed_label)

        group.setLayout(layout)
        return group

    def _create_status_group(self) -> QGroupBox:
        """Create status display group."""
        group = QGroupBox("Status")
        layout = QVBoxLayout()

        # Connection status
        self.connection_status_label = QLabel("Status: Disconnected")
        layout.addWidget(self.connection_status_label)

        # Homing status
        self.homing_status_label = QLabel("Homed: No")
        layout.addWidget(self.homing_status_label)

        # Current position
        self.position_label = QLabel("Position: -- µm")
        layout.addWidget(self.position_label)

        # Motion status
        self.motion_status_label = QLabel("Motion: Idle")
        layout.addWidget(self.motion_status_label)

        group.setLayout(layout)
        return group

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection and homing status."""
        # Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)
        self.home_btn.setEnabled(self.is_connected and not self.is_homed)

        # Position controls (require homed actuator)
        controls_enabled = self.is_connected and self.is_homed

        self.position_input.setEnabled(controls_enabled)
        self.move_btn.setEnabled(controls_enabled)

        self.step_minus_100_btn.setEnabled(controls_enabled)
        self.step_minus_10_btn.setEnabled(controls_enabled)
        self.step_plus_10_btn.setEnabled(controls_enabled)
        self.step_plus_100_btn.setEnabled(controls_enabled)
        self.custom_step_input.setEnabled(controls_enabled)
        self.custom_step_btn.setEnabled(controls_enabled)

        self.scan_negative_btn.setEnabled(controls_enabled)
        self.scan_positive_btn.setEnabled(controls_enabled)
        self.scan_stop_btn.setEnabled(controls_enabled)

        self.speed_slider.setEnabled(controls_enabled)

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        logger.info("Connecting to actuator...")

        # Create controller if needed
        if not self.controller:
            self.controller = ActuatorController()

            # Connect signals
            self.controller.connection_changed.connect(self._on_connection_changed)
            self.controller.status_changed.connect(self._on_status_changed)
            self.controller.position_changed.connect(self._on_position_changed)
            self.controller.position_reached.connect(self._on_position_reached)
            self.controller.error_occurred.connect(self._on_error)
            self.controller.homing_progress.connect(self._on_homing_progress)

        # Connect without auto-homing (user must click Find Home button)
        success = self.controller.connect("COM3", auto_home=False)

        if not success:
            logger.error("Failed to connect to actuator")
            self.connection_status_label.setText("Status: Connection failed")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from actuator...")
            self.controller.disconnect()

    @pyqtSlot()
    def _on_home_clicked(self) -> None:
        """Handle home button click."""
        if self.controller:
            logger.info("Starting homing procedure...")
            self.homing_status_label.setText("Homed: Searching...")
            self.controller.find_index()

    @pyqtSlot()
    def _on_move_clicked(self) -> None:
        """Handle move to position button click."""
        if self.controller and self.is_homed:
            target_pos = self.position_input.value()
            logger.info(f"Moving to position: {target_pos} µm")
            self.controller.set_position(target_pos)

    @pyqtSlot(float)
    def _on_step_clicked(self, step_um: float) -> None:
        """Handle step button click."""
        if self.controller and self.is_homed:
            logger.info(f"Stepping: {step_um:+.1f} µm")
            self.controller.make_step(step_um)

    @pyqtSlot()
    def _on_custom_step_clicked(self) -> None:
        """Handle custom step button click."""
        if self.controller and self.is_homed:
            step_um = self.custom_step_input.value()
            logger.info(f"Custom step: {step_um:+.1f} µm")
            self.controller.make_step(step_um)

    @pyqtSlot(int)
    def _on_speed_display_changed(self, value: int) -> None:
        """Update speed label (doesn't send to hardware yet)."""
        self.speed_label.setText(str(value))

    @pyqtSlot()
    def _on_speed_released(self) -> None:
        """Handle speed slider release (send to hardware)."""
        value = self.speed_slider.value()
        if self.controller and self.is_connected:
            self.controller.set_speed(value)
            logger.debug(f"Speed set to {value}")

    @pyqtSlot(int)
    def _on_scan_clicked(self, direction: int) -> None:
        """Handle scan button click."""
        if self.controller and self.is_homed:
            dir_str = "positive" if direction > 0 else "negative"
            logger.info(f"Starting continuous scan in {dir_str} direction")
            self.controller.start_scan(direction)
            self.motion_status_label.setText(f"Motion: Scanning {dir_str}")

    @pyqtSlot()
    def _on_scan_stop_clicked(self) -> None:
        """Handle scan stop button click."""
        if self.controller:
            logger.info("Stopping scan")
            self.controller.stop_scan()
            self.motion_status_label.setText("Motion: Stopped")

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        status_text = "Connected" if connected else "Disconnected"
        self.connection_status_label.setText(f"Status: {status_text}")
        logger.info(f"Connection status: {status_text}")
        self._update_ui_state()

    @pyqtSlot(str)
    def _on_status_changed(self, status: str) -> None:
        """Handle actuator status change."""
        # Update homing status
        if status == "ready":
            self.is_homed = True
            self.homing_status_label.setText("Homed: Yes")
            self._update_ui_state()
        elif status == "not_homed":
            self.is_homed = False
            self.homing_status_label.setText("Homed: No")
            self._update_ui_state()

        # Update motion status
        status_map = {
            "homing": "Homing...",
            "moving": "Moving...",
            "ready": "Ready",
            "not_homed": "Not Homed",
            "error": "Error",
        }
        motion_text = status_map.get(status, status.title())
        self.motion_status_label.setText(f"Motion: {motion_text}")

    @pyqtSlot(float)
    def _on_position_changed(self, position_um: float) -> None:
        """Handle position update."""
        self.current_position_um = position_um
        self.position_label.setText(f"Position: {position_um:.2f} µm")

    @pyqtSlot(float)
    def _on_position_reached(self, position_um: float) -> None:
        """Handle position reached notification."""
        logger.info(f"Position reached: {position_um:.2f} µm")

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from controller."""
        logger.error(f"Actuator error: {error_msg}")
        self.motion_status_label.setText(f"Error: {error_msg}")

    @pyqtSlot(str)
    def _on_homing_progress(self, message: str) -> None:
        """Handle homing progress updates."""
        logger.info(f"Homing: {message}")
        self.homing_status_label.setText(f"Homed: {message}")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
