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
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.hardware.actuator_controller import ActuatorController
from src.hardware.actuator_sequence import ActionType, ActuatorSequence, SequenceAction

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

        # Scan range state
        self.scan_range_active = False
        self.scan_range_timer: Optional[QTimer] = None
        self.scan_current_position = 0.0
        self.scan_target_position = 0.0
        self.scan_step_size = 0.0
        self.scan_dwell_time = 0.0
        self.scan_loop = False
        self.scan_from = 0.0
        self.scan_to = 0.0
        self.scan_dwell_start_time = 0.0
        self.scan_in_dwell = False

        # Sequence builder state
        self.sequence = ActuatorSequence()
        self.sequence_running = False
        self.sequence_timer: Optional[QTimer] = None
        self.sequence_current_step = 0
        self.sequence_current_loop = 0

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Connection controls (always visible)
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Status display (always visible)
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        # Tabbed interface for controls
        tabs = QTabWidget()

        # Tab 1: Position Control
        position_tab = QWidget()
        position_layout = QVBoxLayout(position_tab)
        position_layout.addWidget(self._create_position_group())
        position_layout.addWidget(self._create_step_group())
        position_layout.addStretch()
        tabs.addTab(position_tab, "Position Control")

        # Tab 2: Scanning
        scan_tab = QWidget()
        scan_layout = QVBoxLayout(scan_tab)
        scan_layout.addWidget(self._create_scan_group())
        scan_layout.addWidget(self._create_scan_range_group())
        scan_layout.addStretch()
        tabs.addTab(scan_tab, "Scanning")

        # Tab 3: Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.addWidget(self._create_speed_group())
        settings_layout.addWidget(self._create_acceleration_group())
        settings_layout.addWidget(self._create_limits_group())
        settings_layout.addStretch()
        tabs.addTab(settings_tab, "Settings")

        # Tab 4: Sequence Builder
        sequence_tab = QWidget()
        sequence_layout = QVBoxLayout(sequence_tab)
        sequence_layout.addWidget(self._create_sequence_params_group())
        sequence_layout.addWidget(self._create_sequence_list_group())
        sequence_layout.addWidget(self._create_sequence_controls_group())
        sequence_layout.addStretch()
        tabs.addTab(sequence_tab, "Sequence Builder")

        layout.addWidget(tabs)

        # Initial state
        self._update_ui_state()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection & Homing")
        layout = QHBoxLayout()

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Home button
        self.home_btn = QPushButton("Find Home")
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
        self.position_input.setRange(-45000.0, 45000.0)  # ±45mm (full hardware range)
        self.position_input.setValue(0.0)
        self.position_input.setSuffix(" µm")
        self.position_input.setDecimals(2)
        self.position_input.setSingleStep(100.0)  # Larger step for larger range
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

        # Custom step (full range available)
        custom_layout = QHBoxLayout()
        self.custom_step_input = QDoubleSpinBox()
        self.custom_step_input.setRange(-90000.0, 90000.0)  # ±90mm (max possible step)
        self.custom_step_input.setValue(100.0)
        self.custom_step_input.setSuffix(" µm")
        self.custom_step_input.setDecimals(2)
        self.custom_step_input.setSingleStep(100.0)  # Larger step for larger range
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

        self.scan_negative_btn = QPushButton("Scan Negative")
        self.scan_negative_btn.clicked.connect(lambda: self._on_scan_clicked(-1))
        self.scan_negative_btn.setEnabled(False)
        self.scan_negative_btn.setStyleSheet("background-color: #4CAF50;")
        button_layout.addWidget(self.scan_negative_btn)

        self.scan_stop_btn = QPushButton("STOP")
        self.scan_stop_btn.clicked.connect(self._on_scan_stop_clicked)
        self.scan_stop_btn.setEnabled(False)
        self.scan_stop_btn.setStyleSheet("background-color: #f44336; font-weight: bold;")
        button_layout.addWidget(self.scan_stop_btn)

        self.scan_positive_btn = QPushButton("Scan Positive")
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

    def _create_scan_range_group(self) -> QGroupBox:
        """Create advanced scan range control group."""
        group = QGroupBox("Scan Range (Automated)")
        layout = QVBoxLayout()

        # From/To position inputs
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("From:"))
        self.scan_from_input = QDoubleSpinBox()
        self.scan_from_input.setRange(-45000.0, 45000.0)
        self.scan_from_input.setValue(-1000.0)
        self.scan_from_input.setSuffix(" µm")
        self.scan_from_input.setDecimals(2)
        self.scan_from_input.setSingleStep(100.0)
        self.scan_from_input.setEnabled(False)
        range_layout.addWidget(self.scan_from_input)

        range_layout.addWidget(QLabel("To:"))
        self.scan_to_input = QDoubleSpinBox()
        self.scan_to_input.setRange(-45000.0, 45000.0)
        self.scan_to_input.setValue(1000.0)
        self.scan_to_input.setSuffix(" µm")
        self.scan_to_input.setDecimals(2)
        self.scan_to_input.setSingleStep(100.0)
        self.scan_to_input.setEnabled(False)
        range_layout.addWidget(self.scan_to_input)

        layout.addLayout(range_layout)

        # Step size and dwell time
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Step:"))
        self.scan_step_input = QDoubleSpinBox()
        self.scan_step_input.setRange(1.0, 10000.0)
        self.scan_step_input.setValue(100.0)
        self.scan_step_input.setSuffix(" µm")
        self.scan_step_input.setDecimals(2)
        self.scan_step_input.setSingleStep(10.0)
        self.scan_step_input.setEnabled(False)
        params_layout.addWidget(self.scan_step_input)

        params_layout.addWidget(QLabel("Dwell:"))
        self.scan_dwell_input = QDoubleSpinBox()
        self.scan_dwell_input.setRange(0.0, 10.0)
        self.scan_dwell_input.setValue(0.5)
        self.scan_dwell_input.setSuffix(" sec")
        self.scan_dwell_input.setDecimals(2)
        self.scan_dwell_input.setSingleStep(0.1)
        self.scan_dwell_input.setEnabled(False)
        params_layout.addWidget(self.scan_dwell_input)

        layout.addLayout(params_layout)

        from PyQt6.QtWidgets import QCheckBox

        self.scan_loop_checkbox = QCheckBox("Loop continuously")
        self.scan_loop_checkbox.setEnabled(False)
        layout.addWidget(self.scan_loop_checkbox)

        # Control buttons
        button_layout = QHBoxLayout()
        self.scan_range_start_btn = QPushButton("Start Scan Range")
        self.scan_range_start_btn.clicked.connect(self._on_scan_range_start)
        self.scan_range_start_btn.setEnabled(False)
        self.scan_range_start_btn.setStyleSheet("background-color: #4CAF50;")
        button_layout.addWidget(self.scan_range_start_btn)

        self.scan_range_stop_btn = QPushButton("Stop Scan Range")
        self.scan_range_stop_btn.clicked.connect(self._on_scan_range_stop)
        self.scan_range_stop_btn.setEnabled(False)
        self.scan_range_stop_btn.setStyleSheet("background-color: #f44336;")
        button_layout.addWidget(self.scan_range_stop_btn)

        layout.addLayout(button_layout)

        # Status label
        self.scan_range_status_label = QLabel("Status: Ready")
        self.scan_range_status_label.setWordWrap(True)
        layout.addWidget(self.scan_range_status_label)

        group.setLayout(layout)
        return group

    def _create_speed_group(self) -> QGroupBox:
        """Create speed control group."""
        group = QGroupBox("Speed Control")
        layout = QVBoxLayout()

        range_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QCheckBox

        self.fast_speed_checkbox = QCheckBox("Enable Fast Mode (up to 400 mm/s)")
        self.fast_speed_checkbox.setChecked(False)
        self.fast_speed_checkbox.stateChanged.connect(self._on_fast_mode_changed)
        self.fast_speed_checkbox.setEnabled(False)
        self.fast_speed_checkbox.setStyleSheet("color: #FFC107; font-weight: bold;")
        range_layout.addWidget(self.fast_speed_checkbox)
        range_layout.addStretch()
        layout.addLayout(range_layout)

        # Speed slider (µm/s)
        slider_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(500, 10000)  # Default: 500-10000 µm/s (0.5-10 mm/s)
        self.speed_slider.setValue(2000)  # Default: medium speed (2 mm/s)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(1000)
        self.speed_slider.valueChanged.connect(self._on_speed_display_changed)
        self.speed_slider.sliderReleased.connect(self._on_speed_released)
        self.speed_slider.setEnabled(False)

        self.speed_label = QLabel("2000 µm/s (2 mm/s)")
        self.speed_label.setMinimumWidth(120)

        slider_layout.addWidget(QLabel("Slow"))
        slider_layout.addWidget(self.speed_slider)
        slider_layout.addWidget(QLabel("Fast"))
        slider_layout.addWidget(self.speed_label)
        layout.addLayout(slider_layout)

        # Info label
        self.speed_info_label = QLabel("Normal mode: 0.5-10 mm/s (safe range)")
        self.speed_info_label.setStyleSheet("font-size: 9pt; color: gray;")
        layout.addWidget(self.speed_info_label)

        group.setLayout(layout)
        return group

    def _create_acceleration_group(self) -> QGroupBox:
        """Create acceleration/deceleration control group."""
        group = QGroupBox("Acceleration Control")
        layout = QVBoxLayout()

        # Acceleration slider
        accel_layout = QHBoxLayout()
        accel_layout.addWidget(QLabel("Acceleration:"))

        self.accel_slider = QSlider(Qt.Orientation.Horizontal)
        self.accel_slider.setRange(10000, 65535)  # Valid ACCE range
        self.accel_slider.setValue(65500)  # Default high acceleration
        self.accel_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.accel_slider.setTickInterval(10000)
        self.accel_slider.valueChanged.connect(self._on_accel_display_changed)
        self.accel_slider.sliderReleased.connect(self._on_accel_released)
        self.accel_slider.setEnabled(False)
        accel_layout.addWidget(self.accel_slider)

        self.accel_label = QLabel("65500")
        self.accel_label.setMinimumWidth(50)
        accel_layout.addWidget(self.accel_label)

        layout.addLayout(accel_layout)

        # Deceleration slider
        decel_layout = QHBoxLayout()
        decel_layout.addWidget(QLabel("Deceleration:"))

        self.decel_slider = QSlider(Qt.Orientation.Horizontal)
        self.decel_slider.setRange(10000, 65535)  # Valid DECE range
        self.decel_slider.setValue(65500)  # Default high deceleration
        self.decel_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.decel_slider.setTickInterval(10000)
        self.decel_slider.valueChanged.connect(self._on_decel_display_changed)
        self.decel_slider.sliderReleased.connect(self._on_decel_released)
        self.decel_slider.setEnabled(False)
        decel_layout.addWidget(self.decel_slider)

        self.decel_label = QLabel("65500")
        self.decel_label.setMinimumWidth(50)
        decel_layout.addWidget(self.decel_label)

        layout.addLayout(decel_layout)

        # Info label
        info_label = QLabel("Higher values = faster acceleration/deceleration")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 9pt; color: gray;")
        layout.addWidget(info_label)

        group.setLayout(layout)
        return group

    def _create_limits_group(self) -> QGroupBox:
        """Create hardware limits display group."""
        group = QGroupBox("Hardware Limits")
        layout = QVBoxLayout()

        # Limit values display
        limits_layout = QHBoxLayout()
        limits_layout.addWidget(QLabel("Range:"))

        self.limits_label = QLabel("-45000 to +45000 µm")
        self.limits_label.setStyleSheet("font-weight: bold;")
        limits_layout.addWidget(self.limits_label)
        limits_layout.addStretch()

        layout.addLayout(limits_layout)

        # Distance from limits (with color coding)
        distance_layout = QVBoxLayout()

        self.low_limit_distance_label = QLabel("Low limit: -- µm away")
        self.low_limit_distance_label.setStyleSheet("background-color: #4CAF50; padding: 3px;")
        distance_layout.addWidget(self.low_limit_distance_label)

        self.high_limit_distance_label = QLabel("High limit: -- µm away")
        self.high_limit_distance_label.setStyleSheet("background-color: #4CAF50; padding: 3px;")
        distance_layout.addWidget(self.high_limit_distance_label)

        layout.addLayout(distance_layout)

        # Warning label
        self.limit_warning_label = QLabel("")
        self.limit_warning_label.setWordWrap(True)
        self.limit_warning_label.setStyleSheet(
            "background-color: #FFC107; padding: 5px; font-weight: bold;"
        )
        self.limit_warning_label.setVisible(False)
        layout.addWidget(self.limit_warning_label)

        group.setLayout(layout)
        return group

    def _create_status_group(self) -> QGroupBox:
        """Create status display group."""
        group = QGroupBox("Status")
        layout = QGridLayout()

        # Row 1: Connection and Homing
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Connection:"), 0, 0)
        layout.addWidget(self.connection_status_label, 0, 1)

        self.homing_status_label = QLabel("Not Homed")
        self.homing_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Homed:"), 0, 2)
        layout.addWidget(self.homing_status_label, 0, 3)

        # Row 2: Position and Motion
        self.position_label = QLabel("-- µm")
        self.position_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Position:"), 1, 0)
        layout.addWidget(self.position_label, 1, 1)

        self.motion_status_label = QLabel("Idle")
        self.motion_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Motion:"), 1, 2)
        layout.addWidget(self.motion_status_label, 1, 3)

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

        # Scan range controls
        scan_range_enabled = controls_enabled and not self.scan_range_active
        self.scan_from_input.setEnabled(scan_range_enabled)
        self.scan_to_input.setEnabled(scan_range_enabled)
        self.scan_step_input.setEnabled(scan_range_enabled)
        self.scan_dwell_input.setEnabled(scan_range_enabled)
        self.scan_loop_checkbox.setEnabled(scan_range_enabled)
        self.scan_range_start_btn.setEnabled(scan_range_enabled)
        self.scan_range_stop_btn.setEnabled(controls_enabled and self.scan_range_active)

        self.speed_slider.setEnabled(controls_enabled)
        self.fast_speed_checkbox.setEnabled(controls_enabled)
        self.accel_slider.setEnabled(controls_enabled)
        self.decel_slider.setEnabled(controls_enabled)

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
            self.controller.limits_changed.connect(self._on_limits_changed)
            self.controller.limit_warning.connect(self._on_limit_warning)

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
        mm_per_s = value / 1000.0
        self.speed_label.setText(f"{value} µm/s ({mm_per_s:.1f} mm/s)")

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
            self.motion_status_label.setText(f"Scanning {dir_str}")

    @pyqtSlot()
    def _on_scan_stop_clicked(self) -> None:
        """Handle scan stop button click."""
        if self.controller:
            logger.info("Stopping scan")
            self.controller.stop_scan()
            self.motion_status_label.setText("Stopped")

    @pyqtSlot(int)
    def _on_fast_mode_changed(self, state: int) -> None:
        """Handle fast mode checkbox change."""
        from PyQt6.QtCore import Qt as QtCore

        is_fast = state == QtCore.CheckState.Checked.value

        if is_fast:
            # Fast mode: 0.5-400 mm/s (500-400000 µm/s)
            self.speed_slider.setRange(500, 400000)
            self.speed_slider.setTickInterval(50000)
            self.speed_info_label.setText("Fast mode: 0.5-400 mm/s (USE WITH CAUTION!)")
            self.speed_info_label.setStyleSheet(
                "font-size: 9pt; color: #f44336; font-weight: bold;"
            )
            logger.warning("Fast speed mode ENABLED - max 400 mm/s")
        else:
            # Normal mode: 0.5-10 mm/s (500-10000 µm/s)
            current_speed = self.speed_slider.value()
            self.speed_slider.setRange(500, 10000)
            self.speed_slider.setTickInterval(1000)
            self.speed_info_label.setText("Normal mode: 0.5-10 mm/s (safe range)")
            self.speed_info_label.setStyleSheet("font-size: 9pt; color: gray;")

            # Clamp speed if it exceeds new max
            if current_speed > 10000:
                self.speed_slider.setValue(10000)
                if self.controller and self.is_connected:
                    self.controller.set_speed(10000)

            logger.info("Fast speed mode disabled - max 10 mm/s")

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

    @pyqtSlot(str)
    def _on_status_changed(self, status: str) -> None:
        """Handle actuator status change."""
        # Update homing status
        if status == "ready":
            self.is_homed = True
            self.homing_status_label.setText("Yes")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
            self._update_ui_state()
        elif status == "not_homed":
            self.is_homed = False
            self.homing_status_label.setText("No")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #FFC107;")
            self._update_ui_state()

        # Update motion status
        status_map = {
            "homing": "Homing...",
            "moving": "Moving...",
            "scanning": "Scanning",
            "ready": "Ready",
            "not_homed": "Not Homed",
            "error": "Error",
        }
        motion_text = status_map.get(status, status.title())
        self.motion_status_label.setText(motion_text)

    @pyqtSlot(float)
    def _on_position_changed(self, position_um: float) -> None:
        """Handle position update."""
        self.current_position_um = position_um
        self.position_label.setText(f"{position_um:.2f} µm")

        # Update distance from limits with color coding
        if self.controller:
            low_limit = self.controller.low_limit_um
            high_limit = self.controller.high_limit_um

            distance_from_low = position_um - low_limit
            distance_from_high = high_limit - position_um

            # Color code based on distance (green > 5000, yellow 1000-5000, red < 1000)
            def get_color(distance: float) -> str:
                if distance > 5000:
                    return "#4CAF50"  # Green - safe
                elif distance > 1000:
                    return "#FFC107"  # Yellow - warning
                else:
                    return "#f44336"  # Red - danger

            low_color = get_color(distance_from_low)
            high_color = get_color(distance_from_high)

            self.low_limit_distance_label.setText(f"Low limit: {distance_from_low:.0f} µm away")
            self.low_limit_distance_label.setStyleSheet(
                f"background-color: {low_color}; padding: 3px; color: white;"
            )

            self.high_limit_distance_label.setText(f"High limit: {distance_from_high:.0f} µm away")
            self.high_limit_distance_label.setStyleSheet(
                f"background-color: {high_color}; padding: 3px; color: white;"
            )

            # Hide warning label if far from limits
            if distance_from_low > 1000 and distance_from_high > 1000:
                self.limit_warning_label.setVisible(False)

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

    @pyqtSlot(int)
    def _on_accel_display_changed(self, value: int) -> None:
        """Update acceleration label (doesn't send to hardware yet)."""
        self.accel_label.setText(str(value))

    @pyqtSlot()
    def _on_accel_released(self) -> None:
        """Handle acceleration slider release (send to hardware)."""
        value = self.accel_slider.value()
        if self.controller and self.is_connected:
            self.controller.set_acceleration(value)
            logger.debug(f"Acceleration set to {value}")

    @pyqtSlot(int)
    def _on_decel_display_changed(self, value: int) -> None:
        """Update deceleration label (doesn't send to hardware yet)."""
        self.decel_label.setText(str(value))

    @pyqtSlot()
    def _on_decel_released(self) -> None:
        """Handle deceleration slider release (send to hardware)."""
        value = self.decel_slider.value()
        if self.controller and self.is_connected:
            self.controller.set_deceleration(value)
            logger.debug(f"Deceleration set to {value}")

    @pyqtSlot(float, float)
    def _on_limits_changed(self, low_limit: float, high_limit: float) -> None:
        """Handle hardware limits update."""
        self.limits_label.setText(f"{low_limit:.0f} to {high_limit:.0f} µm")
        logger.info(f"Hardware limits updated: {low_limit:.0f} to {high_limit:.0f} µm")

    @pyqtSlot(str, float)
    def _on_limit_warning(self, direction: str, distance: float) -> None:
        """Handle limit proximity warning."""
        warning_text = f"WARNING: {distance:.0f} µm from {direction} limit!"
        self.limit_warning_label.setText(warning_text)
        self.limit_warning_label.setVisible(True)
        logger.warning(warning_text)

    @pyqtSlot()
    def _on_scan_range_start(self) -> None:
        """Handle scan range start button click."""
        if not self.controller or not self.is_homed:
            return

        # Get parameters
        self.scan_from = self.scan_from_input.value()
        self.scan_to = self.scan_to_input.value()
        self.scan_step_size = self.scan_step_input.value()
        self.scan_dwell_time = self.scan_dwell_input.value()
        self.scan_loop = self.scan_loop_checkbox.isChecked()

        # Validate range
        if abs(self.scan_to - self.scan_from) < self.scan_step_size:
            logger.error("Scan range too small for step size")
            self.scan_range_status_label.setText("Error: Range too small for step size")
            return

        # Initialize scan
        self.scan_range_active = True
        self.scan_current_position = self.scan_from
        direction = 1 if self.scan_to > self.scan_from else -1
        self.scan_step_size = abs(self.scan_step_size) * direction

        # Move to start position
        logger.info(
            f"Starting scan range: {self.scan_from:.0f} to {self.scan_to:.0f} µm, "
            f"step {abs(self.scan_step_size):.0f} µm, dwell {self.scan_dwell_time}s, "
            f"loop={self.scan_loop}"
        )
        self.controller.set_position(self.scan_from)
        self.scan_range_status_label.setText(f"Moving to start: {self.scan_from:.0f} µm")

        # Create timer for stepping (check position reached every 100ms)
        self.scan_range_timer = QTimer()
        self.scan_range_timer.timeout.connect(self._on_scan_range_step)
        self.scan_range_timer.start(100)  # Check every 100ms

        self.scan_in_dwell = False
        self._update_ui_state()

    @pyqtSlot()
    def _on_scan_range_stop(self) -> None:
        """Handle scan range stop button click."""
        if self.scan_range_timer:
            self.scan_range_timer.stop()
            self.scan_range_timer = None

        self.scan_range_active = False
        self.scan_in_dwell = False
        self.scan_range_status_label.setText("Status: Stopped")
        logger.info("Scan range stopped")
        self._update_ui_state()

    def _on_scan_range_step(self) -> None:
        """Timer callback for scan range stepping."""
        if not self.controller or not self.is_homed:
            self._on_scan_range_stop()
            return

        # Check if position reached
        if not self.controller.axis.isPositionReached():
            return  # Still moving to current position

        # Handle dwell time (non-blocking)
        if not self.scan_in_dwell:
            # Just reached position - start dwell
            import time

            self.scan_dwell_start_time = time.time()
            self.scan_in_dwell = True
            return
        else:
            # Check if dwell time elapsed
            import time

            elapsed = time.time() - self.scan_dwell_start_time
            if elapsed < self.scan_dwell_time:
                return  # Still dwelling

            # Dwell complete
            self.scan_in_dwell = False

        # Calculate next position
        next_pos = self.scan_current_position + self.scan_step_size

        # Check if we've reached the end
        if self.scan_step_size > 0:
            at_end = next_pos >= self.scan_to
        else:
            at_end = next_pos <= self.scan_to

        if at_end:
            # At end position - move to exact end if not already there
            if abs(self.scan_current_position - self.scan_to) > 1.0:
                self.controller.set_position(self.scan_to)
                self.scan_current_position = self.scan_to
                self.scan_in_dwell = False  # Will dwell on next callback
                return

            # Check if we should loop
            if self.scan_loop:
                # Restart from beginning
                logger.info("Scan range complete - looping")
                self.scan_current_position = self.scan_from
                self.controller.set_position(self.scan_from)
                self.scan_range_status_label.setText(f"Loop: Moving to {self.scan_from:.0f} µm")
                self.scan_in_dwell = False
            else:
                # Stop scanning
                logger.info("Scan range complete - stopping")
                self._on_scan_range_stop()
        else:
            # Move to next position
            self.scan_current_position = next_pos
            self.controller.set_position(next_pos)
            progress = abs(next_pos - self.scan_from) / abs(self.scan_to - self.scan_from) * 100
            self.scan_range_status_label.setText(f"Scanning: {next_pos:.0f} µm ({progress:.0f}%)")

    def _create_sequence_params_group(self) -> QGroupBox:
        """Create sequence action parameters group."""
        group = QGroupBox("Action Parameters")
        layout = QVBoxLayout()

        # Action type selector
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action Type:"))
        self.seq_action_combo = QComboBox()
        self.seq_action_combo.addItems([action.value for action in ActionType])
        self.seq_action_combo.currentIndexChanged.connect(self._update_sequence_param_visibility)
        action_layout.addWidget(self.seq_action_combo)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Position/Distance
        self.seq_pos_layout = QHBoxLayout()
        self.seq_pos_label = QLabel("Position (µm):")
        self.seq_pos_input = QDoubleSpinBox()
        self.seq_pos_input.setRange(-45000, 45000)
        self.seq_pos_input.setDecimals(1)
        self.seq_pos_layout.addWidget(self.seq_pos_label)
        self.seq_pos_layout.addWidget(self.seq_pos_input)
        self.seq_pos_layout.addStretch()
        layout.addLayout(self.seq_pos_layout)

        # Speed
        self.seq_speed_layout = QHBoxLayout()
        self.seq_speed_layout.addWidget(QLabel("Speed (µm/s):"))
        self.seq_speed_input = QDoubleSpinBox()
        self.seq_speed_input.setRange(500, 10000)
        self.seq_speed_input.setValue(2000)
        self.seq_speed_input.setDecimals(0)
        self.seq_speed_layout.addWidget(self.seq_speed_input)
        self.seq_speed_layout.addStretch()
        layout.addLayout(self.seq_speed_layout)

        # Direction
        self.seq_dir_layout = QHBoxLayout()
        self.seq_dir_layout.addWidget(QLabel("Direction:"))
        self.seq_dir_combo = QComboBox()
        self.seq_dir_combo.addItems(["positive", "negative"])
        self.seq_dir_layout.addWidget(self.seq_dir_combo)
        self.seq_dir_layout.addStretch()
        layout.addLayout(self.seq_dir_layout)

        # Duration
        self.seq_dur_layout = QHBoxLayout()
        self.seq_dur_layout.addWidget(QLabel("Duration (s):"))
        self.seq_dur_input = QDoubleSpinBox()
        self.seq_dur_input.setRange(0.1, 60.0)
        self.seq_dur_input.setValue(1.0)
        self.seq_dur_input.setDecimals(1)
        self.seq_dur_layout.addWidget(self.seq_dur_input)
        self.seq_dur_layout.addStretch()
        layout.addLayout(self.seq_dur_layout)

        # Add button
        self.seq_add_btn = QPushButton("Add to Sequence")
        self.seq_add_btn.clicked.connect(self._on_seq_add_action)
        self.seq_add_btn.setEnabled(False)
        layout.addWidget(self.seq_add_btn)

        group.setLayout(layout)
        self._update_sequence_param_visibility()
        return group

    def _create_sequence_list_group(self) -> QGroupBox:
        """Create sequence list group."""
        group = QGroupBox("Sequence")
        layout = QVBoxLayout()

        # Sequence list
        self.seq_list = QListWidget()
        self.seq_list.setMaximumHeight(200)
        layout.addWidget(self.seq_list)

        # List manipulation buttons
        btn_layout = QHBoxLayout()
        self.seq_delete_btn = QPushButton("Delete")
        self.seq_delete_btn.clicked.connect(self._on_seq_delete)
        self.seq_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.seq_delete_btn)

        self.seq_clear_btn = QPushButton("Clear All")
        self.seq_clear_btn.clicked.connect(self._on_seq_clear)
        self.seq_clear_btn.setEnabled(False)
        btn_layout.addWidget(self.seq_clear_btn)

        self.seq_up_btn = QPushButton("Move Up")
        self.seq_up_btn.clicked.connect(self._on_seq_move_up)
        self.seq_up_btn.setEnabled(False)
        btn_layout.addWidget(self.seq_up_btn)

        self.seq_down_btn = QPushButton("Move Down")
        self.seq_down_btn.clicked.connect(self._on_seq_move_down)
        self.seq_down_btn.setEnabled(False)
        btn_layout.addWidget(self.seq_down_btn)

        layout.addLayout(btn_layout)

        # Loop controls
        loop_layout = QHBoxLayout()
        self.seq_loop_check = QCheckBox("Loop Sequence")
        self.seq_loop_check.stateChanged.connect(self._on_seq_loop_changed)
        loop_layout.addWidget(self.seq_loop_check)

        loop_layout.addWidget(QLabel("Loop Count:"))
        self.seq_loop_count = QSpinBox()
        self.seq_loop_count.setRange(1, 100)
        self.seq_loop_count.setValue(1)
        self.seq_loop_count.setEnabled(False)
        loop_layout.addWidget(self.seq_loop_count)
        loop_layout.addStretch()

        layout.addLayout(loop_layout)

        group.setLayout(layout)
        return group

    def _create_sequence_controls_group(self) -> QGroupBox:
        """Create sequence execution controls group."""
        group = QGroupBox("Execution")
        layout = QHBoxLayout()

        self.seq_run_btn = QPushButton("Run Sequence")
        self.seq_run_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.seq_run_btn.clicked.connect(self._on_seq_run)
        self.seq_run_btn.setEnabled(False)
        layout.addWidget(self.seq_run_btn)

        self.seq_stop_btn = QPushButton("Stop")
        self.seq_stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.seq_stop_btn.clicked.connect(self._on_seq_stop)
        self.seq_stop_btn.setEnabled(False)
        layout.addWidget(self.seq_stop_btn)

        self.seq_save_btn = QPushButton("Save Sequence")
        self.seq_save_btn.clicked.connect(self._on_seq_save)
        self.seq_save_btn.setEnabled(False)
        layout.addWidget(self.seq_save_btn)

        self.seq_load_btn = QPushButton("Load Sequence")
        self.seq_load_btn.clicked.connect(self._on_seq_load)
        self.seq_load_btn.setEnabled(False)
        layout.addWidget(self.seq_load_btn)

        group.setLayout(layout)
        return group

    @pyqtSlot()
    def _update_sequence_param_visibility(self) -> None:  # noqa: C901
        """Update parameter visibility based on selected action type."""
        action_text = self.seq_action_combo.currentText()
        action_type = None
        for action in ActionType:
            if action.value == action_text:
                action_type = action
                break

        # Hide all first
        for widget in self.seq_pos_layout.parentWidget().findChildren(QWidget):
            if widget.layout() in [
                self.seq_pos_layout,
                self.seq_speed_layout,
                self.seq_dir_layout,
                self.seq_dur_layout,
            ]:
                widget.hide()

        # Show based on action type
        if action_type == ActionType.MOVE_ABSOLUTE:
            self.seq_pos_label.setText("Position (µm):")
            for i in range(self.seq_pos_layout.count()):
                self.seq_pos_layout.itemAt(i).widget().show()
            for i in range(self.seq_speed_layout.count()):
                self.seq_speed_layout.itemAt(i).widget().show()

        elif action_type == ActionType.MOVE_RELATIVE:
            self.seq_pos_label.setText("Distance (µm):")
            for i in range(self.seq_pos_layout.count()):
                self.seq_pos_layout.itemAt(i).widget().show()
            for i in range(self.seq_speed_layout.count()):
                self.seq_speed_layout.itemAt(i).widget().show()

        elif action_type == ActionType.HOME:
            for i in range(self.seq_speed_layout.count()):
                self.seq_speed_layout.itemAt(i).widget().show()

        elif action_type == ActionType.PAUSE:
            for i in range(self.seq_dur_layout.count()):
                self.seq_dur_layout.itemAt(i).widget().show()

        elif action_type == ActionType.SET_SPEED:
            for i in range(self.seq_speed_layout.count()):
                self.seq_speed_layout.itemAt(i).widget().show()

        elif action_type == ActionType.SCAN:
            for i in range(self.seq_speed_layout.count()):
                self.seq_speed_layout.itemAt(i).widget().show()
            for i in range(self.seq_dir_layout.count()):
                self.seq_dir_layout.itemAt(i).widget().show()
            for i in range(self.seq_dur_layout.count()):
                self.seq_dur_layout.itemAt(i).widget().show()

    @pyqtSlot()
    def _on_seq_add_action(self) -> None:
        """Add action to sequence."""
        action_text = self.seq_action_combo.currentText()
        action_type = None
        for action in ActionType:
            if action.value == action_text:
                action_type = action
                break

        if not action_type:
            return

        params = {}

        if action_type == ActionType.MOVE_ABSOLUTE:
            params = {
                "position": self.seq_pos_input.value(),
                "speed": self.seq_speed_input.value(),
                "unit": "um",
            }
        elif action_type == ActionType.MOVE_RELATIVE:
            params = {
                "distance": self.seq_pos_input.value(),
                "speed": self.seq_speed_input.value(),
                "unit": "um",
            }
        elif action_type == ActionType.HOME:
            params = {"speed": self.seq_speed_input.value()}
        elif action_type == ActionType.PAUSE:
            params = {"duration": self.seq_dur_input.value()}
        elif action_type == ActionType.SET_SPEED:
            params = {"speed": self.seq_speed_input.value(), "unit": "um"}
        elif action_type == ActionType.SCAN:
            params = {
                "speed": self.seq_speed_input.value(),
                "direction": self.seq_dir_combo.currentText(),
                "duration": self.seq_dur_input.value(),
                "unit": "um",
            }

        seq_action = SequenceAction(action_type, params)
        self.sequence.add_action(seq_action)
        self.seq_list.addItem(str(seq_action))
        self._update_sequence_buttons()
        logger.debug(f"Added sequence action: {seq_action}")

    @pyqtSlot()
    def _on_seq_delete(self) -> None:
        """Delete selected action from sequence."""
        current_row = self.seq_list.currentRow()
        if current_row >= 0:
            self.sequence.remove_action(current_row)
            self.seq_list.takeItem(current_row)
            self._update_sequence_buttons()

    @pyqtSlot()
    def _on_seq_clear(self) -> None:
        """Clear all actions from sequence."""
        self.sequence.clear()
        self.seq_list.clear()
        self._update_sequence_buttons()

    @pyqtSlot()
    def _on_seq_move_up(self) -> None:
        """Move selected action up in sequence."""
        current_row = self.seq_list.currentRow()
        if self.sequence.move_action_up(current_row):
            item = self.seq_list.takeItem(current_row)
            self.seq_list.insertItem(current_row - 1, item)
            self.seq_list.setCurrentRow(current_row - 1)

    @pyqtSlot()
    def _on_seq_move_down(self) -> None:
        """Move selected action down in sequence."""
        current_row = self.seq_list.currentRow()
        if self.sequence.move_action_down(current_row):
            item = self.seq_list.takeItem(current_row)
            self.seq_list.insertItem(current_row + 1, item)
            self.seq_list.setCurrentRow(current_row + 1)

    @pyqtSlot(int)
    def _on_seq_loop_changed(self, state: int) -> None:
        """Handle loop checkbox state change."""
        from PyQt6.QtCore import Qt as QtCore

        self.sequence.loop_enabled = state == QtCore.CheckState.Checked.value
        self.seq_loop_count.setEnabled(self.sequence.loop_enabled)

    @pyqtSlot()
    def _on_seq_save(self) -> None:
        """Save sequence to JSON file."""
        if len(self.sequence) == 0:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Sequence", "", "JSON Files (*.json)")

        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            self.sequence.loop_count = self.seq_loop_count.value()
            self.sequence.save(Path(file_path))
            logger.info(f"Saved sequence to {file_path}")

    @pyqtSlot()
    def _on_seq_load(self) -> None:
        """Load sequence from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Sequence", "", "JSON Files (*.json)")

        if file_path:
            self.sequence.load(Path(file_path))
            self.seq_list.clear()
            for action in self.sequence.actions:
                self.seq_list.addItem(str(action))
            self.seq_loop_check.setChecked(self.sequence.loop_enabled)
            self.seq_loop_count.setValue(self.sequence.loop_count)
            self._update_sequence_buttons()
            logger.info(f"Loaded sequence from {file_path}")

    @pyqtSlot()
    def _on_seq_run(self) -> None:
        """Start sequence execution."""
        if not self.controller or not self.is_homed or len(self.sequence) == 0:
            return

        self.sequence_running = True
        self.sequence_current_step = 0
        self.sequence_current_loop = 0
        self.sequence.loop_count = self.seq_loop_count.value()

        self.sequence_timer = QTimer()
        self.sequence_timer.timeout.connect(self._execute_sequence_step)
        self.sequence_timer.start(100)

        self._update_sequence_buttons()
        logger.info("Starting sequence execution")

    @pyqtSlot()
    def _on_seq_stop(self) -> None:
        """Stop sequence execution."""
        if self.sequence_timer:
            self.sequence_timer.stop()
            self.sequence_timer = None

        self.sequence_running = False
        self._update_sequence_buttons()
        logger.info("Stopped sequence execution")

    def _execute_sequence_step(self) -> None:  # noqa: C901
        """Execute current step in sequence."""
        if not self.sequence_running or not self.controller:
            self._on_seq_stop()
            return

        loop_count = self.sequence.loop_count if self.sequence.loop_enabled else 1

        if self.sequence_current_loop >= loop_count:
            self._on_seq_stop()
            logger.info("Sequence execution complete")
            return

        if self.sequence_current_step >= len(self.sequence):
            self.sequence_current_loop += 1
            self.sequence_current_step = 0

            if self.sequence_current_loop >= loop_count:
                self._on_seq_stop()
                logger.info("Sequence execution complete")
                return

        action = self.sequence.actions[self.sequence_current_step]
        self.seq_list.setCurrentRow(self.sequence_current_step)

        try:
            if action.action_type == ActionType.MOVE_ABSOLUTE:
                self.controller.set_speed(int(action.params.get("speed", 2000)))
                self.controller.set_position(action.params.get("position", 0))

            elif action.action_type == ActionType.MOVE_RELATIVE:
                self.controller.set_speed(int(action.params.get("speed", 2000)))
                self.controller.make_step(action.params.get("distance", 0))

            elif action.action_type == ActionType.HOME:
                self.controller.set_speed(int(action.params.get("speed", 2000)))
                self.controller.find_index()

            elif action.action_type == ActionType.PAUSE:
                import time

                time.sleep(action.params.get("duration", 1.0))

            elif action.action_type == ActionType.SET_SPEED:
                self.controller.set_speed(int(action.params.get("speed", 2000)))

            elif action.action_type == ActionType.SCAN:
                speed = int(action.params.get("speed", 2000))
                direction = 1 if action.params.get("direction") == "positive" else -1
                duration = action.params.get("duration", 1.0)
                self.controller.set_speed(speed)
                self.controller.start_scan(direction)
                import time

                time.sleep(duration)
                self.controller.stop_scan()

            self.sequence_current_step += 1

        except Exception as e:
            logger.error(f"Error executing sequence step: {e}")
            self._on_seq_stop()

    def _update_sequence_buttons(self) -> None:
        """Update sequence button states."""
        has_sequence = len(self.sequence) > 0
        is_connected_and_homed = self.is_connected and self.is_homed

        self.seq_add_btn.setEnabled(is_connected_and_homed)
        self.seq_delete_btn.setEnabled(has_sequence)
        self.seq_clear_btn.setEnabled(has_sequence)
        self.seq_up_btn.setEnabled(has_sequence)
        self.seq_down_btn.setEnabled(has_sequence)
        self.seq_run_btn.setEnabled(
            has_sequence and is_connected_and_homed and not self.sequence_running
        )
        self.seq_stop_btn.setEnabled(self.sequence_running)
        self.seq_save_btn.setEnabled(has_sequence)
        self.seq_load_btn.setEnabled(is_connected_and_homed and not self.sequence_running)

    def cleanup(self) -> None:
        """Cleanup resources."""
        # Stop scan range if active
        if self.scan_range_timer:
            self.scan_range_timer.stop()
            self.scan_range_timer = None

        # Stop sequence if active
        if self.sequence_timer:
            self.sequence_timer.stop()
            self.sequence_timer = None

        if self.controller:
            self.controller.disconnect()
            self.controller = None
