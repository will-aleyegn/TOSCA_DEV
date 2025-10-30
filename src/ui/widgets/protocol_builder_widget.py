"""
Protocol Builder Widget - Visual editor for creating treatment protocols.

Provides a graphical interface for building Protocol objects with all action types:
- SetLaserPower: Set fixed laser power
- RampLaserPower: Gradually ramp laser power over time
- MoveActuator: Move actuator to position
- Wait: Pause for duration
- Loop: Repeat action sequence

Protocols can be saved/loaded as JSON files for execution by ProtocolEngine.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.core.protocol import (
    ActionType,
    LoopParams,
    MoveActuatorParams,
    Protocol,
    ProtocolAction,
    RampLaserPowerParams,
    RampType,
    SafetyLimits,
    SetLaserPowerParams,
    WaitParams,
)

logger = logging.getLogger(__name__)


class ProtocolBuilderWidget(QWidget):
    """
    Visual protocol builder for creating treatment protocols.

    Features:
    - Add/remove/reorder protocol actions
    - Configure parameters for each action type
    - Set safety limits
    - Save/load protocols as JSON
    - Real-time validation
    """

    protocol_created = pyqtSignal(Protocol)  # Emitted when protocol is built

    def __init__(self) -> None:
        super().__init__()

        # Current protocol being built
        self.current_protocol: Optional[Protocol] = None
        self.actions: list[ProtocolAction] = []
        self.next_action_id = 1

        # Safety limits (will be editable)
        self.safety_limits = SafetyLimits()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Constrain maximum width
        self.setMaximumWidth(900)

        # Protocol metadata
        layout.addWidget(self._create_metadata_group())

        # Action parameters (dynamic form)
        layout.addWidget(self._create_action_params_group())

        # Action list
        layout.addWidget(self._create_action_list_group())

        # Protocol controls (save/load/validate)
        layout.addWidget(self._create_protocol_controls_group())

        layout.addStretch()

    def _create_metadata_group(self) -> QGroupBox:
        """Create protocol metadata input group."""
        group = QGroupBox("Protocol Information")
        layout = QVBoxLayout()

        # Protocol name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.protocol_name_input = QComboBox()
        self.protocol_name_input.setEditable(True)
        self.protocol_name_input.setPlaceholderText("Enter protocol name...")
        name_layout.addWidget(self.protocol_name_input)
        layout.addLayout(name_layout)

        # Version and Author
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Version:"))
        self.version_input = QComboBox()
        self.version_input.setEditable(True)
        self.version_input.addItem("1.0.0")
        self.version_input.setCurrentText("1.0.0")
        info_layout.addWidget(self.version_input)

        info_layout.addWidget(QLabel("Author:"))
        self.author_input = QComboBox()
        self.author_input.setEditable(True)
        self.author_input.setPlaceholderText("Your name...")
        info_layout.addWidget(self.author_input)
        layout.addLayout(info_layout)

        group.setLayout(layout)
        return group

    def _create_action_params_group(self) -> QGroupBox:
        """Create action parameter configuration group."""
        group = QGroupBox("Action Parameters")
        layout = QVBoxLayout()

        # Action type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Action Type:"))
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(
            ["Set Laser Power", "Ramp Laser Power", "Move Actuator", "Wait", "Loop"]
        )
        self.action_type_combo.currentIndexChanged.connect(self._on_action_type_changed)
        type_layout.addWidget(self.action_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # === SET LASER POWER PARAMETERS ===
        self.set_power_widget = QWidget()
        set_power_layout = QHBoxLayout()
        set_power_layout.addWidget(QLabel("Power (W):"))
        self.set_power_input = QDoubleSpinBox()
        self.set_power_input.setRange(0, 100)
        self.set_power_input.setValue(1.0)
        self.set_power_input.setDecimals(2)
        self.set_power_input.setSingleStep(0.1)
        set_power_layout.addWidget(self.set_power_input)
        set_power_layout.addStretch()
        self.set_power_widget.setLayout(set_power_layout)
        layout.addWidget(self.set_power_widget)

        # === RAMP LASER POWER PARAMETERS ===
        self.ramp_power_widget = QWidget()
        ramp_power_layout = QVBoxLayout()

        # Start and End power
        power_range_layout = QHBoxLayout()
        power_range_layout.addWidget(QLabel("Start Power (W):"))
        self.ramp_start_power_input = QDoubleSpinBox()
        self.ramp_start_power_input.setRange(0, 100)
        self.ramp_start_power_input.setValue(0.1)
        self.ramp_start_power_input.setDecimals(2)
        self.ramp_start_power_input.setSingleStep(0.1)
        power_range_layout.addWidget(self.ramp_start_power_input)

        power_range_layout.addWidget(QLabel("End Power (W):"))
        self.ramp_end_power_input = QDoubleSpinBox()
        self.ramp_end_power_input.setRange(0, 100)
        self.ramp_end_power_input.setValue(2.0)
        self.ramp_end_power_input.setDecimals(2)
        self.ramp_end_power_input.setSingleStep(0.1)
        power_range_layout.addWidget(self.ramp_end_power_input)
        ramp_power_layout.addLayout(power_range_layout)

        # Duration and Ramp Type
        ramp_config_layout = QHBoxLayout()
        ramp_config_layout.addWidget(QLabel("Duration (s):"))
        self.ramp_duration_input = QDoubleSpinBox()
        self.ramp_duration_input.setRange(0.1, 600)
        self.ramp_duration_input.setValue(10.0)
        self.ramp_duration_input.setDecimals(1)
        ramp_config_layout.addWidget(self.ramp_duration_input)

        ramp_config_layout.addWidget(QLabel("Ramp Type:"))
        self.ramp_type_combo = QComboBox()
        self.ramp_type_combo.addItems(["linear", "logarithmic", "exponential", "constant"])
        ramp_config_layout.addWidget(self.ramp_type_combo)
        ramp_power_layout.addLayout(ramp_config_layout)

        self.ramp_power_widget.setLayout(ramp_power_layout)
        layout.addWidget(self.ramp_power_widget)

        # === MOVE ACTUATOR PARAMETERS ===
        self.move_actuator_widget = QWidget()
        move_layout = QHBoxLayout()
        move_layout.addWidget(QLabel("Target Position (µm):"))
        self.move_position_input = QDoubleSpinBox()
        self.move_position_input.setRange(-45000, 45000)
        self.move_position_input.setValue(1000.0)
        self.move_position_input.setDecimals(1)
        move_layout.addWidget(self.move_position_input)

        move_layout.addWidget(QLabel("Speed (µm/s):"))
        self.move_speed_input = QDoubleSpinBox()
        self.move_speed_input.setRange(1, 1000)
        self.move_speed_input.setValue(100.0)
        self.move_speed_input.setDecimals(1)
        move_layout.addWidget(self.move_speed_input)

        move_layout.addWidget(QLabel("Laser Power (W):"))
        self.move_laser_power_input = QDoubleSpinBox()
        self.move_laser_power_input.setRange(0, 100)
        self.move_laser_power_input.setValue(0.0)
        self.move_laser_power_input.setDecimals(2)
        self.move_laser_power_input.setSingleStep(0.1)
        self.move_laser_power_input.setToolTip("Laser power during movement (0 = off)")
        move_layout.addWidget(self.move_laser_power_input)

        move_layout.addStretch()
        self.move_actuator_widget.setLayout(move_layout)
        layout.addWidget(self.move_actuator_widget)

        # === WAIT PARAMETERS ===
        self.wait_widget = QWidget()
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("Duration (s):"))
        self.wait_duration_input = QDoubleSpinBox()
        self.wait_duration_input.setRange(0.1, 600)
        self.wait_duration_input.setValue(5.0)
        self.wait_duration_input.setDecimals(1)
        wait_layout.addWidget(self.wait_duration_input)
        wait_layout.addStretch()
        self.wait_widget.setLayout(wait_layout)
        layout.addWidget(self.wait_widget)

        # === LOOP PARAMETERS ===
        self.loop_widget = QWidget()
        loop_layout = QHBoxLayout()
        loop_layout.addWidget(QLabel("Repeat Count:"))
        self.loop_count_input = QSpinBox()
        self.loop_count_input.setRange(-1, 1000)
        self.loop_count_input.setValue(2)
        self.loop_count_input.setSpecialValueText("Infinite")
        loop_layout.addWidget(self.loop_count_input)
        loop_layout.addWidget(QLabel("(-1 = infinite)"))
        loop_layout.addStretch()
        self.loop_widget.setLayout(loop_layout)
        layout.addWidget(self.loop_widget)

        # Add action button
        add_layout = QHBoxLayout()
        self.add_action_btn = QPushButton("➕ Add Action to Protocol")
        self.add_action_btn.setMinimumHeight(35)
        self.add_action_btn.setStyleSheet(
            "font-weight: bold; background-color: #4CAF50; color: white;"
        )
        self.add_action_btn.clicked.connect(self._on_add_action)
        add_layout.addWidget(self.add_action_btn)
        layout.addLayout(add_layout)

        group.setLayout(layout)

        # Initialize visibility
        self._on_action_type_changed(0)

        return group

    def _create_action_list_group(self) -> QGroupBox:
        """Create action list display and management group."""
        group = QGroupBox("Protocol Action Sequence")
        layout = QVBoxLayout()

        # Action list
        self.action_list = QListWidget()
        self.action_list.setMinimumHeight(200)
        self.action_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.action_list)

        # Action management buttons
        btn_layout = QHBoxLayout()

        self.move_up_btn = QPushButton("⬆ Move Up")
        self.move_up_btn.clicked.connect(self._on_move_up)
        btn_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("⬇ Move Down")
        self.move_down_btn.clicked.connect(self._on_move_down)
        btn_layout.addWidget(self.move_down_btn)

        self.remove_btn = QPushButton("🗑 Remove")
        self.remove_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.remove_btn.clicked.connect(self._on_remove_action)
        btn_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._on_clear_all)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        # Action count display
        self.action_count_label = QLabel("Actions: 0")
        self.action_count_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.action_count_label)

        group.setLayout(layout)
        return group

    def _create_protocol_controls_group(self) -> QGroupBox:
        """Create protocol save/load/validate controls."""
        group = QGroupBox("Protocol Management")
        layout = QVBoxLayout()

        # Action buttons row
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Save Protocol")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self._on_save_protocol)
        btn_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("📂 Load Protocol")
        self.load_btn.setMinimumHeight(35)
        self.load_btn.clicked.connect(self._on_load_protocol)
        btn_layout.addWidget(self.load_btn)

        self.validate_btn = QPushButton("✓ Validate")
        self.validate_btn.setMinimumHeight(35)
        self.validate_btn.clicked.connect(self._on_validate_protocol)
        btn_layout.addWidget(self.validate_btn)

        layout.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel("Ready to build protocol")
        self.status_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        group.setLayout(layout)
        return group

    @pyqtSlot(int)
    def _on_action_type_changed(self, index: int) -> None:
        """Update parameter form visibility based on selected action type."""
        # Hide all parameter widgets
        self.set_power_widget.hide()
        self.ramp_power_widget.hide()
        self.move_actuator_widget.hide()
        self.wait_widget.hide()
        self.loop_widget.hide()

        # Show appropriate widget
        if index == 0:  # Set Laser Power
            self.set_power_widget.show()
        elif index == 1:  # Ramp Laser Power
            self.ramp_power_widget.show()
        elif index == 2:  # Move Actuator
            self.move_actuator_widget.show()
        elif index == 3:  # Wait
            self.wait_widget.show()
        elif index == 4:  # Loop
            self.loop_widget.show()

    @pyqtSlot()
    def _on_add_action(self) -> None:
        """Add action to protocol based on current parameters."""
        action_type_idx = self.action_type_combo.currentIndex()

        try:
            # Create appropriate action based on type
            if action_type_idx == 0:  # Set Laser Power
                params = SetLaserPowerParams(power_watts=self.set_power_input.value())
                action = ProtocolAction(
                    action_id=self.next_action_id,
                    action_type=ActionType.SET_LASER_POWER,
                    parameters=params,
                )

            elif action_type_idx == 1:  # Ramp Laser Power
                params = RampLaserPowerParams(
                    start_power_watts=self.ramp_start_power_input.value(),
                    end_power_watts=self.ramp_end_power_input.value(),
                    duration_seconds=self.ramp_duration_input.value(),
                    ramp_type=RampType(self.ramp_type_combo.currentText()),
                )
                action = ProtocolAction(
                    action_id=self.next_action_id,
                    action_type=ActionType.RAMP_LASER_POWER,
                    parameters=params,
                )

            elif action_type_idx == 2:  # Move Actuator
                laser_power = self.move_laser_power_input.value()
                params = MoveActuatorParams(
                    target_position_um=self.move_position_input.value(),
                    speed_um_per_sec=self.move_speed_input.value(),
                    laser_power_watts=laser_power if laser_power > 0 else None,
                )
                action = ProtocolAction(
                    action_id=self.next_action_id,
                    action_type=ActionType.MOVE_ACTUATOR,
                    parameters=params,
                )

            elif action_type_idx == 3:  # Wait
                params = WaitParams(duration_seconds=self.wait_duration_input.value())
                action = ProtocolAction(
                    action_id=self.next_action_id, action_type=ActionType.WAIT, parameters=params
                )

            elif action_type_idx == 4:  # Loop
                params = LoopParams(
                    repeat_count=self.loop_count_input.value(),
                    actions=[],  # Empty for now, nested actions not supported in UI yet
                )
                action = ProtocolAction(
                    action_id=self.next_action_id, action_type=ActionType.LOOP, parameters=params
                )

            else:
                logger.error(f"Unknown action type index: {action_type_idx}")
                return

            # Add to action list
            self.actions.append(action)
            self.next_action_id += 1

            # Update UI
            self._update_action_list()
            self.status_label.setText(f"✓ Action added: {action.action_type.value}")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")

            logger.info(f"Added action: {action.action_type.value}")

        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; padding: 5px;")
            logger.error(f"Failed to add action: {e}")

    def _update_action_list(self) -> None:
        """Update the action list display."""
        self.action_list.clear()

        for idx, action in enumerate(self.actions):
            # Format display string
            display_str = f"{idx + 1}. {action.action_type.value}"

            # Add parameter summary
            if isinstance(action.parameters, SetLaserPowerParams):
                display_str += f" ({action.parameters.power_watts:.2f}W)"
            elif isinstance(action.parameters, RampLaserPowerParams):
                ramp_type = action.parameters.ramp_type.value
                display_str += (
                    f" ({action.parameters.start_power_watts:.2f}W → "
                    f"{action.parameters.end_power_watts:.2f}W over "
                    f"{action.parameters.duration_seconds:.1f}s, {ramp_type})"
                )
            elif isinstance(action.parameters, MoveActuatorParams):
                power_str = ""
                if action.parameters.laser_power_watts is not None:
                    power_str = f" with {action.parameters.laser_power_watts:.2f}W"
                display_str += (
                    f" (to {action.parameters.target_position_um:.1f}µm "
                    f"@ {action.parameters.speed_um_per_sec:.1f}µm/s{power_str})"
                )
            elif isinstance(action.parameters, WaitParams):
                display_str += f" ({action.parameters.duration_seconds:.1f}s)"
            elif isinstance(action.parameters, LoopParams):
                count = action.parameters.repeat_count
                display_str += f" ({count}x)" if count != -1 else " (infinite)"

            item = QListWidgetItem(display_str)
            self.action_list.addItem(item)

        # Update count label
        self.action_count_label.setText(f"Actions: {len(self.actions)}")

    @pyqtSlot()
    def _on_move_up(self) -> None:
        """Move selected action up in the list."""
        current_row = self.action_list.currentRow()
        if current_row > 0:
            self.actions[current_row], self.actions[current_row - 1] = (
                self.actions[current_row - 1],
                self.actions[current_row],
            )
            self._update_action_list()
            self.action_list.setCurrentRow(current_row - 1)

    @pyqtSlot()
    def _on_move_down(self) -> None:
        """Move selected action down in the list."""
        current_row = self.action_list.currentRow()
        if 0 <= current_row < len(self.actions) - 1:
            self.actions[current_row], self.actions[current_row + 1] = (
                self.actions[current_row + 1],
                self.actions[current_row],
            )
            self._update_action_list()
            self.action_list.setCurrentRow(current_row + 1)

    @pyqtSlot()
    def _on_remove_action(self) -> None:
        """Remove selected action from the list."""
        current_row = self.action_list.currentRow()
        if 0 <= current_row < len(self.actions):
            removed = self.actions.pop(current_row)
            self._update_action_list()
            logger.info(f"Removed action: {removed.action_type.value}")

    @pyqtSlot()
    def _on_clear_all(self) -> None:
        """Clear all actions from the protocol."""
        if self.actions:
            reply = QMessageBox.question(
                self,
                "Clear All Actions",
                "Are you sure you want to remove all actions?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.actions.clear()
                self.next_action_id = 1
                self._update_action_list()
                logger.info("Cleared all actions")

    @pyqtSlot()
    def _on_save_protocol(self) -> None:
        """Save protocol to JSON file."""
        if not self.actions:
            QMessageBox.warning(self, "No Actions", "Protocol has no actions to save.")
            return

        # Build protocol object
        protocol_name = self.protocol_name_input.currentText()
        if not protocol_name:
            QMessageBox.warning(self, "Missing Name", "Please enter a protocol name.")
            return

        version = self.version_input.currentText()
        author = self.author_input.currentText()

        protocol = Protocol(
            protocol_name=protocol_name,
            version=version,
            actions=self.actions,
            description="",
            author=author,
            safety_limits=self.safety_limits,
        )

        # Validate before saving
        is_valid, errors = protocol.validate()
        if not is_valid:
            error_msg = "Protocol validation failed:\n\n" + "\n".join(errors)
            QMessageBox.critical(self, "Validation Error", error_msg)
            return

        # Select file path
        default_dir = Path("protocols/examples")
        default_dir.mkdir(parents=True, exist_ok=True)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Protocol",
            str(default_dir / f"{protocol_name.replace(' ', '_').lower()}.json"),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        # Save to file
        try:
            protocol_dict = protocol.to_dict()
            with open(file_path, "w") as f:
                json.dump(protocol_dict, f, indent=2)

            self.status_label.setText(f"✓ Protocol saved: {Path(file_path).name}")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")
            logger.info(f"Protocol saved to {file_path}")

            # Emit signal
            self.protocol_created.emit(protocol)

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save protocol:\n{e}")
            logger.error(f"Protocol save error: {e}")

    @pyqtSlot()
    def _on_load_protocol(self) -> None:
        """Load protocol from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Protocol",
            str(Path("protocols/examples")),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                protocol_dict = json.load(f)

            protocol = Protocol.from_dict(protocol_dict)

            # Update UI with loaded protocol
            self.protocol_name_input.setCurrentText(protocol.protocol_name)
            self.version_input.setCurrentText(protocol.version)
            self.author_input.setCurrentText(protocol.author)

            self.actions = protocol.actions
            self.safety_limits = protocol.safety_limits
            self.next_action_id = (
                max([a.action_id for a in self.actions]) + 1 if self.actions else 1
            )

            self._update_action_list()

            self.status_label.setText(f"✓ Protocol loaded: {Path(file_path).name}")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")
            logger.info(f"Protocol loaded from {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load protocol:\n{e}")
            logger.error(f"Protocol load error: {e}")

    @pyqtSlot()
    def _on_validate_protocol(self) -> None:
        """Validate current protocol."""
        if not self.actions:
            QMessageBox.information(self, "No Actions", "Protocol has no actions to validate.")
            return

        protocol_name = self.protocol_name_input.currentText() or "Unnamed Protocol"

        protocol = Protocol(
            protocol_name=protocol_name,
            version=self.version_input.currentText(),
            actions=self.actions,
            author=self.author_input.currentText(),
            safety_limits=self.safety_limits,
        )

        is_valid, errors = protocol.validate()

        if is_valid:
            duration = protocol.calculate_total_duration()
            duration_str = f"{duration:.1f}s" if duration >= 0 else "infinite (contains loop)"

            QMessageBox.information(
                self,
                "Validation Passed",
                f"✓ Protocol is valid!\n\n"
                f"Actions: {len(protocol.actions)}\n"
                f"Estimated Duration: {duration_str}",
            )
            self.status_label.setText("✓ Protocol validated successfully")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")
        else:
            error_msg = "Protocol validation failed:\n\n" + "\n".join(errors)
            QMessageBox.critical(self, "Validation Failed", error_msg)
            self.status_label.setText("❌ Validation failed")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; padding: 5px;")

    def get_protocol(self) -> Optional[Protocol]:
        """
        Get the current protocol being built.

        Returns:
            Protocol instance or None if no actions
        """
        if not self.actions:
            return None

        protocol_name = self.protocol_name_input.currentText() or "Unnamed Protocol"

        return Protocol(
            protocol_name=protocol_name,
            version=self.version_input.currentText(),
            actions=self.actions,
            author=self.author_input.currentText(),
            safety_limits=self.safety_limits,
        )
