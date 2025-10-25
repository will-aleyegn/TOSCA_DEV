"""
Actuator control widget for the TOSCA GUI.

Provides actuator control with sequence builder for automated movement.
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QTimer, pyqtSlot
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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.hardware.actuator_controller import ActuatorController
from src.hardware.actuator_sequence import ActionType, ActuatorSequence, SequenceAction

logger = logging.getLogger(__name__)


class ActuatorWidget(QWidget):
    """
    Actuator control widget with sequence builder.
    """

    def __init__(self) -> None:
        super().__init__()

        # Create controller
        self.controller: Optional[ActuatorController] = None

        # State tracking
        self.is_connected = False
        self.is_homed = False
        self.current_position_um = 0.0

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

        # Connection controls
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Status display
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        # Sequence builder
        layout.addWidget(self._create_sequence_params_group())
        layout.addWidget(self._create_sequence_list_group())
        layout.addWidget(self._create_sequence_controls_group())

        layout.addStretch()

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

        # Update sequence builder button states
        self._update_sequence_buttons()

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

    @pyqtSlot(float, float)
    def _on_limits_changed(self, low_limit_um: float, high_limit_um: float) -> None:
        """Handle actuator limits change."""
        logger.info(f"Actuator limits: {low_limit_um:.0f} to {high_limit_um:.0f} µm")

    @pyqtSlot(str, float)
    def _on_limit_warning(self, direction: str, distance: float) -> None:
        """Handle limit warning."""
        logger.warning(f"Approaching {direction} limit: {distance:.0f} µm remaining")

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

        # Speed (displayed in mm/s, stored as µm/s)
        self.seq_speed_layout = QHBoxLayout()
        self.seq_speed_layout.addWidget(QLabel("Speed (mm/s):"))
        self.seq_speed_input = QDoubleSpinBox()
        self.seq_speed_input.setRange(0.5, 400.0)
        self.seq_speed_input.setValue(2.0)
        self.seq_speed_input.setDecimals(1)
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

        # Acceleration
        accel_layout = QHBoxLayout()
        accel_layout.addWidget(QLabel("Acceleration:"))
        self.seq_accel_input = QSpinBox()
        self.seq_accel_input.setRange(1000, 65500)
        self.seq_accel_input.setValue(65500)
        self.seq_accel_input.setSingleStep(1000)
        accel_layout.addWidget(self.seq_accel_input)
        accel_layout.addStretch()
        layout.addLayout(accel_layout)

        # Deceleration
        decel_layout = QHBoxLayout()
        decel_layout.addWidget(QLabel("Deceleration:"))
        self.seq_decel_input = QSpinBox()
        self.seq_decel_input.setRange(1000, 65500)
        self.seq_decel_input.setValue(65500)
        self.seq_decel_input.setSingleStep(1000)
        decel_layout.addWidget(self.seq_decel_input)
        decel_layout.addStretch()
        layout.addLayout(decel_layout)

        # Laser Power
        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Laser Power (mW):"))
        self.seq_power_input = QDoubleSpinBox()
        self.seq_power_input.setRange(0, 2000)
        self.seq_power_input.setValue(0)
        self.seq_power_input.setDecimals(1)
        power_layout.addWidget(self.seq_power_input)
        power_layout.addStretch()
        layout.addLayout(power_layout)

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
                widget = self.seq_pos_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.seq_speed_layout.count()):
                widget = self.seq_speed_layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif action_type == ActionType.MOVE_RELATIVE:
            self.seq_pos_label.setText("Distance (µm):")
            for i in range(self.seq_pos_layout.count()):
                widget = self.seq_pos_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.seq_speed_layout.count()):
                widget = self.seq_speed_layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif action_type == ActionType.HOME:
            for i in range(self.seq_speed_layout.count()):
                widget = self.seq_speed_layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif action_type == ActionType.PAUSE:
            for i in range(self.seq_dur_layout.count()):
                widget = self.seq_dur_layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif action_type == ActionType.SET_SPEED:
            for i in range(self.seq_speed_layout.count()):
                widget = self.seq_speed_layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif action_type == ActionType.SCAN:
            for i in range(self.seq_speed_layout.count()):
                widget = self.seq_speed_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.seq_dir_layout.count()):
                widget = self.seq_dir_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.seq_dur_layout.count()):
                widget = self.seq_dur_layout.itemAt(i).widget()
                if widget:
                    widget.show()

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

        # Convert speed from mm/s to µm/s
        speed_um_s = int(self.seq_speed_input.value() * 1000)

        # Common parameters for all actions
        common_params = {
            "acceleration": self.seq_accel_input.value(),
            "deceleration": self.seq_decel_input.value(),
            "laser_power": self.seq_power_input.value(),
        }

        if action_type == ActionType.MOVE_ABSOLUTE:
            params = {
                "position": self.seq_pos_input.value(),
                "speed": speed_um_s,
                "unit": "um",
                **common_params,
            }
        elif action_type == ActionType.MOVE_RELATIVE:
            params = {
                "distance": self.seq_pos_input.value(),
                "speed": speed_um_s,
                "unit": "um",
                **common_params,
            }
        elif action_type == ActionType.HOME:
            params = {"speed": speed_um_s, **common_params}
        elif action_type == ActionType.PAUSE:
            params = {"duration": self.seq_dur_input.value(), **common_params}
        elif action_type == ActionType.SET_SPEED:
            params = {"speed": speed_um_s, "unit": "um", **common_params}
        elif action_type == ActionType.SCAN:
            params = {
                "speed": speed_um_s,
                "direction": self.seq_dir_combo.currentText(),
                "duration": self.seq_dur_input.value(),
                "unit": "um",
                **common_params,
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
            # Set acceleration/deceleration for this step
            if hasattr(self.controller, "set_acceleration"):
                accel = action.params.get("acceleration", 65500)
                decel = action.params.get("deceleration", 65500)
                self.controller.set_acceleration(accel)
                self.controller.set_deceleration(decel)
                logger.debug(f"Set accel={accel}, decel={decel}")

            # TODO(#124): Set laser power when laser controller is integrated
            # with sequence execution
            laser_power = action.params.get("laser_power", 0)
            if laser_power > 0:
                logger.info(f"Laser power set to {laser_power:.0f} mW")
                # self.laser_controller.set_power(laser_power)

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
                # Non-blocking pause using QTimer
                duration_ms = int(action.params.get("duration", 1.0) * 1000)
                self.sequence_timer.stop()
                QTimer.singleShot(duration_ms, self._resume_sequence_after_pause)
                return  # Return early, don't increment step yet

            elif action.action_type == ActionType.SET_SPEED:
                self.controller.set_speed(int(action.params.get("speed", 2000)))

            elif action.action_type == ActionType.SCAN:
                # Non-blocking scan using QTimer
                speed = int(action.params.get("speed", 2000))
                direction = 1 if action.params.get("direction") == "positive" else -1
                duration_ms = int(action.params.get("duration", 1.0) * 1000)
                self.controller.set_speed(speed)
                self.controller.start_scan(direction)
                self.sequence_timer.stop()
                QTimer.singleShot(duration_ms, self._resume_sequence_after_scan)
                return  # Return early, don't increment step yet

            self.sequence_current_step += 1

        except Exception as e:
            logger.error(f"Error executing sequence step: {e}")
            self._on_seq_stop()

    def _resume_sequence_after_pause(self) -> None:
        """Resume sequence execution after a pause action completes."""
        if not self.sequence_running:
            return
        self.sequence_current_step += 1
        self.sequence_timer.start()

    def _resume_sequence_after_scan(self) -> None:
        """Resume sequence execution after a scan action completes."""
        if not self.sequence_running:
            return
        try:
            self.controller.stop_scan()
        except Exception as e:
            logger.error(f"Error stopping scan: {e}")
        self.sequence_current_step += 1
        self.sequence_timer.start()

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
        # Stop sequence if active
        if self.sequence_timer:
            self.sequence_timer.stop()
            self.sequence_timer = None

        if self.controller:
            self.controller.disconnect()
            self.controller = None
