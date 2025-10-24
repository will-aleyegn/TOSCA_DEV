"""
Protocol Builder widget for creating action-based treatment protocols.

Allows users to:
- Create sequences of actions (laser power, actuator moves, waits, loops)
- Edit and reorder actions
- Save/load protocols to JSON files
- Execute protocols with recording
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.protocol import Protocol, ProtocolAction

logger = logging.getLogger(__name__)


class ProtocolBuilderWidget(QWidget):
    """
    Protocol Builder UI for creating action-based treatment protocols.

    Features:
    - Visual action sequence builder
    - Drag-and-drop reordering (future)
    - Protocol save/load
    - Validation and execution
    """

    def __init__(self) -> None:
        super().__init__()
        logger.info("Initializing Protocol Builder widget")

        # Current protocol being edited
        self.current_protocol: Optional[Protocol] = None
        self.protocol_file_path: Optional[Path] = None

        self._init_ui()
        self._create_new_protocol()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title_label = QLabel("Protocol Builder")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Protocol metadata section
        metadata_group = self._create_metadata_section()
        layout.addWidget(metadata_group)

        # Action sequence section
        sequence_group = self._create_action_sequence_section()
        layout.addWidget(sequence_group, stretch=1)

        # Control buttons section
        controls_layout = self._create_controls_section()
        layout.addLayout(controls_layout)

    def _create_metadata_section(self) -> QGroupBox:
        """Create protocol metadata input section."""
        group = QGroupBox("Protocol Information")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Protocol name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.protocol_name_input = QLineEdit()
        self.protocol_name_input.setPlaceholderText("Enter protocol name...")
        self.protocol_name_input.textChanged.connect(self._on_metadata_changed)
        name_layout.addWidget(self.protocol_name_input)
        layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter protocol description...")
        self.description_input.setMaximumHeight(60)
        self.description_input.textChanged.connect(self._on_metadata_changed)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)

        # File operations
        file_layout = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._on_new_protocol)
        file_layout.addWidget(self.new_btn)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self._on_open_protocol)
        file_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save_protocol)
        file_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As")
        self.save_as_btn.clicked.connect(self._on_save_as_protocol)
        file_layout.addWidget(self.save_as_btn)

        file_layout.addStretch()
        layout.addLayout(file_layout)

        return group

    def _create_action_sequence_section(self) -> QGroupBox:
        """Create action sequence table and controls."""
        group = QGroupBox("Action Sequence")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Action table
        self.action_table = QTableWidget()
        self.action_table.setColumnCount(4)
        self.action_table.setHorizontalHeaderLabels(["#", "Type", "Parameters", "Actions"])

        # Configure column widths
        header = self.action_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(3, 150)

        self.action_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.action_table)

        # Action buttons
        action_btn_layout = QHBoxLayout()

        self.add_action_btn = QPushButton("+ Add Action")
        self.add_action_btn.clicked.connect(self._on_add_action)
        action_btn_layout.addWidget(self.add_action_btn)

        action_btn_layout.addStretch()

        self.move_up_btn = QPushButton("↑ Move Up")
        self.move_up_btn.clicked.connect(self._on_move_up)
        action_btn_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓ Move Down")
        self.move_down_btn.clicked.connect(self._on_move_down)
        action_btn_layout.addWidget(self.move_down_btn)

        layout.addLayout(action_btn_layout)

        return group

    def _create_controls_section(self) -> QHBoxLayout:
        """Create protocol execution and status controls."""
        layout = QHBoxLayout()

        # Status display
        status_layout = QVBoxLayout()
        self.total_duration_label = QLabel("Total Duration: --")
        self.max_power_label = QLabel("Max Power: --")
        self.validation_status_label = QLabel("Status: Not validated")
        status_layout.addWidget(self.total_duration_label)
        status_layout.addWidget(self.max_power_label)
        status_layout.addWidget(self.validation_status_label)
        layout.addLayout(status_layout)

        layout.addStretch()

        # Execution buttons
        exec_layout = QVBoxLayout()
        self.validate_btn = QPushButton("Validate Protocol")
        self.validate_btn.clicked.connect(self._on_validate_protocol)
        exec_layout.addWidget(self.validate_btn)

        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self._on_execute_protocol)
        self.execute_btn.setEnabled(False)
        exec_layout.addWidget(self.execute_btn)

        self.execute_record_btn = QPushButton("Execute && Record")
        self.execute_record_btn.clicked.connect(self._on_execute_and_record)
        self.execute_record_btn.setEnabled(False)
        exec_layout.addWidget(self.execute_record_btn)

        layout.addLayout(exec_layout)

        return layout

    def _create_new_protocol(self) -> None:
        """Create a new empty protocol."""
        from datetime import datetime

        from core.protocol import SafetyLimits

        self.current_protocol = Protocol(
            protocol_name="Unnamed Protocol",
            version="1.0.0",
            actions=[],
            description="",
            created_date=datetime.now(),
            author="",
            safety_limits=SafetyLimits(),
        )
        self.protocol_file_path = None
        self._update_ui_from_protocol()

    def _update_ui_from_protocol(self) -> None:
        """Update UI to reflect current protocol."""
        if not self.current_protocol:
            return

        # Update metadata
        self.protocol_name_input.setText(self.current_protocol.protocol_name)
        self.description_input.setPlainText(self.current_protocol.description)

        # Update action table
        self._refresh_action_table()

        # Update status
        self._update_status_display()

    def _refresh_action_table(self) -> None:
        """Refresh the action table from current protocol."""
        self.action_table.setRowCount(0)

        if not self.current_protocol:
            return

        for i, action in enumerate(self.current_protocol.actions):
            self._add_action_row(i, action)

    def _add_action_row(self, row: int, action: ProtocolAction) -> None:
        """Add a row to the action table."""
        self.action_table.insertRow(row)

        # Action ID
        id_item = QTableWidgetItem(str(action.action_id))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_table.setItem(row, 0, id_item)

        # Action type
        type_item = QTableWidgetItem(action.action_type.value)
        self.action_table.setItem(row, 1, type_item)

        # Parameters summary
        params_text = self._format_action_parameters(action)
        params_item = QTableWidgetItem(params_text)
        self.action_table.setItem(row, 2, params_item)

        # Action buttons
        btn_widget = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(2, 2, 2, 2)
        btn_widget.setLayout(btn_layout)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda checked, r=row: self._on_edit_action(r))
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda checked, r=row: self._on_delete_action(r))
        btn_layout.addWidget(delete_btn)

        self.action_table.setCellWidget(row, 3, btn_widget)

    def _format_action_parameters(self, action: ProtocolAction) -> str:
        """Format action parameters for display in table."""
        from core.protocol import (
            LoopParams,
            MoveActuatorParams,
            RampLaserPowerParams,
            SetLaserPowerParams,
            WaitParams,
        )

        if isinstance(action.parameters, SetLaserPowerParams):
            return f"{action.parameters.power_watts} W"

        elif isinstance(action.parameters, RampLaserPowerParams):
            return (
                f"{action.parameters.start_power_watts}W → "
                f"{action.parameters.end_power_watts}W "
                f"over {action.parameters.duration_seconds}s "
                f"({action.parameters.ramp_type.value})"
            )

        elif isinstance(action.parameters, MoveActuatorParams):
            return (
                f"{action.parameters.target_position_um} µm "
                f"@ {action.parameters.speed_um_per_sec} µm/s"
            )

        elif isinstance(action.parameters, WaitParams):
            return f"{action.parameters.duration_seconds} seconds"

        elif isinstance(action.parameters, LoopParams):
            count_str = (
                "∞" if action.parameters.repeat_count == -1 else action.parameters.repeat_count
            )
            return f"Loop {count_str}× ({len(action.parameters.actions)} actions)"

        return "Unknown"

    def _update_status_display(self) -> None:
        """Update protocol status display."""
        if not self.current_protocol:
            return

        # Calculate total duration
        duration = self.current_protocol.calculate_total_duration()
        if duration == -1:
            duration_str = "∞ (infinite loop)"
        else:
            duration_str = f"{duration:.1f} seconds"
        self.total_duration_label.setText(f"Total Duration: {duration_str}")

        # Find max power
        max_power = self._find_max_power()
        self.max_power_label.setText(f"Max Power: {max_power:.1f} W")

        # Validation status will be updated by validate button

    def _find_max_power(self) -> float:
        """Find maximum laser power in protocol."""
        from core.protocol import LoopParams, RampLaserPowerParams, SetLaserPowerParams

        max_power = 0.0

        def check_actions(actions: List[ProtocolAction]) -> None:
            nonlocal max_power
            for action in actions:
                if isinstance(action.parameters, SetLaserPowerParams):
                    max_power = max(max_power, action.parameters.power_watts)
                elif isinstance(action.parameters, RampLaserPowerParams):
                    max_power = max(
                        max_power,
                        action.parameters.start_power_watts,
                        action.parameters.end_power_watts,
                    )
                elif isinstance(action.parameters, LoopParams):
                    check_actions(action.parameters.actions)

        if self.current_protocol:
            check_actions(self.current_protocol.actions)

        return max_power

    # Event handlers
    def _on_metadata_changed(self) -> None:
        """Handle metadata input changes."""
        if self.current_protocol:
            self.current_protocol.protocol_name = self.protocol_name_input.text()
            self.current_protocol.description = self.description_input.toPlainText()

    def _on_new_protocol(self) -> None:
        """Create a new protocol."""
        self._create_new_protocol()
        logger.info("Created new protocol")

    def _on_open_protocol(self) -> None:
        """Open an existing protocol from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Protocol", "data/protocols", "Protocol Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            self.current_protocol = Protocol.from_dict(data)
            self.protocol_file_path = Path(file_path)
            self._update_ui_from_protocol()
            logger.info(f"Loaded protocol from {file_path}")
            QMessageBox.information(self, "Success", "Protocol loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load protocol: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load protocol:\n{str(e)}")

    def _on_save_protocol(self) -> None:
        """Save current protocol to file."""
        if not self.protocol_file_path:
            self._on_save_as_protocol()
            return

        self._save_protocol_to_file(self.protocol_file_path)

    def _on_save_as_protocol(self) -> None:
        """Save current protocol to a new file."""
        if not self.current_protocol:
            return

        # Create default filename from protocol name
        default_name = self.current_protocol.protocol_name.replace(" ", "_")
        default_path = f"data/protocols/{default_name}_v{self.current_protocol.version}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Protocol As", default_path, "Protocol Files (*.json)"
        )

        if not file_path:
            return

        self.protocol_file_path = Path(file_path)
        self._save_protocol_to_file(self.protocol_file_path)

    def _save_protocol_to_file(self, file_path: Path) -> None:
        """Save protocol to specified file path."""
        if not self.current_protocol:
            return

        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to JSON
            with open(file_path, "w") as f:
                json.dump(self.current_protocol.to_dict(), f, indent=2)

            logger.info(f"Saved protocol to {file_path}")
            QMessageBox.information(self, "Success", f"Protocol saved to:\n{file_path}")

        except Exception as e:
            logger.error(f"Failed to save protocol: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save protocol:\n{str(e)}")

    def _on_add_action(self) -> None:
        """Add a new action to the protocol."""
        logger.info("Add action clicked - not yet implemented")
        QMessageBox.information(
            self, "Not Implemented", "Action editor dialogs coming in next phase"
        )

    def _on_edit_action(self, row: int) -> None:
        """Edit an existing action."""
        logger.info(f"Edit action {row} clicked - not yet implemented")
        QMessageBox.information(
            self, "Not Implemented", "Action editor dialogs coming in next phase"
        )

    def _on_delete_action(self, row: int) -> None:
        """Delete an action from the protocol."""
        if not self.current_protocol:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete action {row + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.current_protocol.actions[row]
            self._refresh_action_table()
            self._update_status_display()
            logger.info(f"Deleted action {row}")

    def _on_move_up(self) -> None:
        """Move selected action up in the sequence."""
        current_row = self.action_table.currentRow()
        if current_row <= 0 or not self.current_protocol:
            return

        # Swap actions
        actions = self.current_protocol.actions
        actions[current_row], actions[current_row - 1] = (
            actions[current_row - 1],
            actions[current_row],
        )

        self._refresh_action_table()
        self.action_table.selectRow(current_row - 1)

    def _on_move_down(self) -> None:
        """Move selected action down in the sequence."""
        if not self.current_protocol:
            return

        current_row = self.action_table.currentRow()
        if current_row < 0 or current_row >= len(self.current_protocol.actions) - 1:
            return

        # Swap actions
        actions = self.current_protocol.actions
        actions[current_row], actions[current_row + 1] = (
            actions[current_row + 1],
            actions[current_row],
        )

        self._refresh_action_table()
        self.action_table.selectRow(current_row + 1)

    def _on_validate_protocol(self) -> None:
        """Validate current protocol."""
        if not self.current_protocol:
            return

        valid, errors = self.current_protocol.validate()

        if valid:
            self.validation_status_label.setText("Status: ✓ Valid")
            self.validation_status_label.setStyleSheet("color: green;")
            self.execute_btn.setEnabled(True)
            self.execute_record_btn.setEnabled(True)
            QMessageBox.information(
                self, "Validation Success", "Protocol is valid and ready to execute"
            )
        else:
            self.validation_status_label.setText("Status: ✗ Invalid")
            self.validation_status_label.setStyleSheet("color: red;")
            self.execute_btn.setEnabled(False)
            self.execute_record_btn.setEnabled(False)
            error_msg = "\n".join(f"• {err}" for err in errors)
            QMessageBox.warning(
                self, "Validation Failed", f"Protocol validation failed:\n\n{error_msg}"
            )

    def _on_execute_protocol(self) -> None:
        """Execute current protocol without recording."""
        logger.info("Execute protocol clicked - not yet implemented")
        QMessageBox.information(self, "Not Implemented", "Protocol execution coming in next phase")

    def _on_execute_and_record(self) -> None:
        """Execute current protocol with recording."""
        logger.info("Execute and record clicked - not yet implemented")
        QMessageBox.information(
            self, "Not Implemented", "Protocol execution with recording coming in next phase"
        )
