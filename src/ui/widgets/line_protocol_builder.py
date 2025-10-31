"""
Line-Based Protocol Builder Widget - Complete

Hybrid table/form UI for building protocols with concurrent line-based actions.
Each line can combine movement, laser control, and dwell time.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.protocol_line import (
    DwellParams,
    HomeParams,
    LaserRampParams,
    LaserSetParams,
    LineBasedProtocol,
    MoveParams,
    MoveType,
    ProtocolLine,
    SafetyLimits,
)

logger = logging.getLogger(__name__)


class LineProtocolBuilderWidget(QWidget):
    """
    Hybrid table/form UI for line-based protocol building.

    Features:
    - Protocol sequence view with concise line summaries
    - Contextual line editor panel for detailed configuration
    - Support for concurrent actions per line (move + laser + dwell)
    - Protocol loop support with repeat count
    - Save/load JSON protocols
    """

    # Signal emitted when protocol is ready to execute
    protocol_ready = pyqtSignal(LineBasedProtocol)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Current protocol state
        self.current_protocol: Optional[LineBasedProtocol] = None
        self.current_line_index: int = -1  # Index of selected line for editing
        self.current_position_mm: float = 0.0  # For duration calculations

        # Safety limits (should be loaded from config in production)
        self.safety_limits = SafetyLimits()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Header
        header = QLabel("🔧 Line-Based Protocol Builder")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px; "
            "background-color: #424242; color: #81C784; border-radius: 3px;"
        )
        main_layout.addWidget(header)

        # Protocol metadata section
        metadata_group = self._create_metadata_section()
        main_layout.addWidget(metadata_group)

        # Main content: Protocol sequence (left) + Line editor (right)
        content_layout = QHBoxLayout()

        # Left side: Protocol sequence view
        sequence_group = self._create_sequence_view()
        content_layout.addWidget(sequence_group, stretch=2)

        # Right side: Line editor panel
        editor_group = self._create_line_editor()
        content_layout.addWidget(editor_group, stretch=3)

        main_layout.addLayout(content_layout)

        # Bottom: Action buttons
        action_layout = self._create_action_buttons()
        main_layout.addLayout(action_layout)

        # Initialize with empty protocol
        self._create_new_protocol()

    # ========================================================================
    # UI Creation Methods
    # ========================================================================

    def _create_metadata_section(self) -> QGroupBox:
        """Create protocol metadata section (name, loop count)."""
        group = QGroupBox("Protocol Metadata")
        layout = QHBoxLayout()

        # Protocol name
        layout.addWidget(QLabel("Name:"))
        self.protocol_name_input = QLineEdit()
        self.protocol_name_input.setPlaceholderText("Enter protocol name...")
        self.protocol_name_input.textChanged.connect(self._on_metadata_changed)
        layout.addWidget(self.protocol_name_input, stretch=2)

        # Loop count
        layout.addWidget(QLabel("Loop Count:"))
        self.loop_count_spin = QSpinBox()
        self.loop_count_spin.setRange(1, 100)
        self.loop_count_spin.setValue(1)
        self.loop_count_spin.setToolTip("Number of times to repeat the entire protocol")
        self.loop_count_spin.valueChanged.connect(self._on_metadata_changed)
        layout.addWidget(self.loop_count_spin)

        # Total duration display
        layout.addWidget(QLabel("Total Duration:"))
        self.total_duration_label = QLabel("0.0s")
        self.total_duration_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.total_duration_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_sequence_view(self) -> QGroupBox:
        """Create protocol sequence view with line summaries."""
        group = QGroupBox("Protocol Sequence")
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Click a line to edit its parameters.\n"
            "Lines execute concurrently (move + laser + dwell)."
        )
        instructions.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        layout.addWidget(instructions)

        # Sequence list
        self.sequence_list = QListWidget()
        self.sequence_list.setAlternatingRowColors(True)
        self.sequence_list.currentRowChanged.connect(self._on_line_selected)
        layout.addWidget(self.sequence_list)

        # Sequence control buttons
        btn_layout = QHBoxLayout()

        self.add_line_btn = QPushButton("➕ Add Line")
        self.add_line_btn.clicked.connect(self._on_add_line)
        btn_layout.addWidget(self.add_line_btn)

        self.remove_line_btn = QPushButton("➖ Remove")
        self.remove_line_btn.clicked.connect(self._on_remove_line)
        self.remove_line_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_line_btn)

        self.move_up_btn = QPushButton("⬆ Up")
        self.move_up_btn.clicked.connect(self._on_move_line_up)
        self.move_up_btn.setEnabled(False)
        btn_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("⬇ Down")
        self.move_down_btn.clicked.connect(self._on_move_line_down)
        self.move_down_btn.setEnabled(False)
        btn_layout.addWidget(self.move_down_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def _create_line_editor(self) -> QGroupBox:
        """Create contextual line editor panel."""
        group = QGroupBox("Line Editor")
        layout = QVBoxLayout()

        # Editor status label
        self.editor_status_label = QLabel("No line selected - add a line to begin")
        self.editor_status_label.setStyleSheet("color: #888; font-style: italic; padding: 10px;")
        layout.addWidget(self.editor_status_label)

        # Movement section
        self.movement_group = self._create_movement_section()
        layout.addWidget(self.movement_group)

        # Laser section
        self.laser_group = self._create_laser_section()
        layout.addWidget(self.laser_group)

        # Dwell section
        self.dwell_group = self._create_dwell_section()
        layout.addWidget(self.dwell_group)

        # Line notes
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes for this line...")
        self.notes_input.textChanged.connect(self._on_line_params_changed)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # Apply changes button
        self.apply_changes_btn = QPushButton("✓ Apply Changes to Line")
        self.apply_changes_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;"
        )
        self.apply_changes_btn.clicked.connect(self._on_apply_changes)
        layout.addWidget(self.apply_changes_btn)

        layout.addStretch()

        # Disable editor initially
        self.movement_group.setEnabled(False)
        self.laser_group.setEnabled(False)
        self.dwell_group.setEnabled(False)
        self.apply_changes_btn.setEnabled(False)

        group.setLayout(layout)
        return group

    def _create_movement_section(self) -> QGroupBox:
        """Create movement configuration section."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Master enable checkbox
        header_layout = QHBoxLayout()
        self.movement_enable_check = QCheckBox("Movement")
        self.movement_enable_check.setStyleSheet("font-weight: bold;")
        self.movement_enable_check.toggled.connect(self._on_movement_enable_toggled)
        header_layout.addWidget(self.movement_enable_check)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Movement type radio buttons
        type_layout = QHBoxLayout()
        type_layout.addSpacing(20)  # Indent

        self.move_position_radio = QRadioButton("Position")
        self.move_position_radio.setChecked(True)
        self.move_position_radio.toggled.connect(self._on_movement_type_changed)
        type_layout.addWidget(self.move_position_radio)

        self.move_home_radio = QRadioButton("Home")
        self.move_home_radio.toggled.connect(self._on_movement_type_changed)
        type_layout.addWidget(self.move_home_radio)

        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Position parameters (shown when Position is selected)
        self.position_params_widget = QWidget()
        pos_layout = QVBoxLayout()
        pos_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        # Target position
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target (mm):"))
        self.target_position_spin = QDoubleSpinBox()
        self.target_position_spin.setRange(-20.0, 20.0)  # Support negative positions
        self.target_position_spin.setDecimals(2)
        self.target_position_spin.setSingleStep(0.1)
        self.target_position_spin.valueChanged.connect(self._on_line_params_changed)
        target_layout.addWidget(self.target_position_spin)
        target_layout.addStretch()
        pos_layout.addLayout(target_layout)

        # Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed (mm/s):"))
        self.move_speed_spin = QDoubleSpinBox()
        self.move_speed_spin.setRange(0.1, 5.0)
        self.move_speed_spin.setDecimals(2)
        self.move_speed_spin.setSingleStep(0.1)
        self.move_speed_spin.setValue(1.0)
        self.move_speed_spin.valueChanged.connect(self._on_line_params_changed)
        speed_layout.addWidget(self.move_speed_spin)
        speed_layout.addStretch()
        pos_layout.addLayout(speed_layout)

        # Move type (Absolute/Relative)
        move_type_layout = QHBoxLayout()
        move_type_layout.addWidget(QLabel("Type:"))
        self.move_type_combo = QComboBox()
        self.move_type_combo.addItems(["Absolute", "Relative"])
        self.move_type_combo.currentIndexChanged.connect(self._on_line_params_changed)
        move_type_layout.addWidget(self.move_type_combo)
        move_type_layout.addStretch()
        pos_layout.addLayout(move_type_layout)

        self.position_params_widget.setLayout(pos_layout)
        layout.addWidget(self.position_params_widget)

        # Home parameters (shown when Home is selected)
        self.home_params_widget = QWidget()
        home_layout = QVBoxLayout()
        home_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        home_speed_layout = QHBoxLayout()
        home_speed_layout.addWidget(QLabel("Homing Speed (mm/s):"))
        self.home_speed_spin = QDoubleSpinBox()
        self.home_speed_spin.setRange(0.1, 5.0)
        self.home_speed_spin.setDecimals(2)
        self.home_speed_spin.setSingleStep(0.1)
        self.home_speed_spin.setValue(2.0)
        self.home_speed_spin.valueChanged.connect(self._on_line_params_changed)
        home_speed_layout.addWidget(self.home_speed_spin)
        home_speed_layout.addStretch()
        home_layout.addLayout(home_speed_layout)

        self.home_params_widget.setLayout(home_layout)
        self.home_params_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.home_params_widget)

        group.setLayout(layout)
        return group

    def _create_laser_section(self) -> QGroupBox:
        """Create laser configuration section."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Master enable checkbox
        header_layout = QHBoxLayout()
        self.laser_enable_check = QCheckBox("Laser")
        self.laser_enable_check.setStyleSheet("font-weight: bold;")
        self.laser_enable_check.toggled.connect(self._on_laser_enable_toggled)
        header_layout.addWidget(self.laser_enable_check)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Laser mode radio buttons
        type_layout = QHBoxLayout()
        type_layout.addSpacing(20)  # Indent

        self.laser_set_radio = QRadioButton("Set Power")
        self.laser_set_radio.setChecked(True)
        self.laser_set_radio.toggled.connect(self._on_laser_type_changed)
        type_layout.addWidget(self.laser_set_radio)

        self.laser_ramp_radio = QRadioButton("Ramp Power")
        self.laser_ramp_radio.toggled.connect(self._on_laser_type_changed)
        type_layout.addWidget(self.laser_ramp_radio)

        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Set power parameters
        self.laser_set_params_widget = QWidget()
        set_layout = QVBoxLayout()
        set_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        set_power_layout = QHBoxLayout()
        set_power_layout.addWidget(QLabel("Power (W):"))
        self.laser_set_power_spin = QDoubleSpinBox()
        self.laser_set_power_spin.setRange(0.0, 10.0)
        self.laser_set_power_spin.setDecimals(2)
        self.laser_set_power_spin.setSingleStep(0.1)
        self.laser_set_power_spin.valueChanged.connect(self._on_line_params_changed)
        set_power_layout.addWidget(self.laser_set_power_spin)
        set_power_layout.addStretch()
        set_layout.addLayout(set_power_layout)

        self.laser_set_params_widget.setLayout(set_layout)
        layout.addWidget(self.laser_set_params_widget)

        # Ramp power parameters
        self.laser_ramp_params_widget = QWidget()
        ramp_layout = QVBoxLayout()
        ramp_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        # Start power
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Power (W):"))
        self.laser_start_power_spin = QDoubleSpinBox()
        self.laser_start_power_spin.setRange(0.0, 10.0)
        self.laser_start_power_spin.setDecimals(2)
        self.laser_start_power_spin.setSingleStep(0.1)
        self.laser_start_power_spin.valueChanged.connect(self._on_line_params_changed)
        start_layout.addWidget(self.laser_start_power_spin)
        start_layout.addStretch()
        ramp_layout.addLayout(start_layout)

        # End power
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Power (W):"))
        self.laser_end_power_spin = QDoubleSpinBox()
        self.laser_end_power_spin.setRange(0.0, 10.0)
        self.laser_end_power_spin.setDecimals(2)
        self.laser_end_power_spin.setSingleStep(0.1)
        self.laser_end_power_spin.valueChanged.connect(self._on_line_params_changed)
        end_layout.addWidget(self.laser_end_power_spin)
        end_layout.addStretch()
        ramp_layout.addLayout(end_layout)

        # Ramp duration
        ramp_dur_layout = QHBoxLayout()
        ramp_dur_layout.addWidget(QLabel("Duration (s):"))
        self.laser_ramp_duration_spin = QDoubleSpinBox()
        self.laser_ramp_duration_spin.setRange(0.1, 300.0)
        self.laser_ramp_duration_spin.setDecimals(1)
        self.laser_ramp_duration_spin.setSingleStep(0.5)
        self.laser_ramp_duration_spin.setValue(1.0)
        self.laser_ramp_duration_spin.valueChanged.connect(self._on_line_params_changed)
        ramp_dur_layout.addWidget(self.laser_ramp_duration_spin)
        ramp_dur_layout.addStretch()
        ramp_layout.addLayout(ramp_dur_layout)

        self.laser_ramp_params_widget.setLayout(ramp_layout)
        self.laser_ramp_params_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.laser_ramp_params_widget)

        group.setLayout(layout)
        return group

    def _create_dwell_section(self) -> QGroupBox:
        """Create dwell/wait configuration section."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Master enable checkbox
        header_layout = QHBoxLayout()
        self.dwell_enable_check = QCheckBox("Dwell (Wait)")
        self.dwell_enable_check.setStyleSheet("font-weight: bold;")
        self.dwell_enable_check.toggled.connect(self._on_dwell_enable_toggled)
        header_layout.addWidget(self.dwell_enable_check)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Dwell duration
        dwell_layout = QHBoxLayout()
        dwell_layout.addSpacing(20)  # Indent
        dwell_layout.addWidget(QLabel("Duration (s):"))
        self.dwell_duration_spin = QDoubleSpinBox()
        self.dwell_duration_spin.setRange(0.1, 300.0)
        self.dwell_duration_spin.setDecimals(1)
        self.dwell_duration_spin.setSingleStep(0.5)
        self.dwell_duration_spin.setValue(1.0)
        self.dwell_duration_spin.valueChanged.connect(self._on_line_params_changed)
        dwell_layout.addWidget(self.dwell_duration_spin)
        dwell_layout.addStretch()
        layout.addLayout(dwell_layout)

        group.setLayout(layout)
        return group

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create bottom action buttons (New, Save, Load, Execute)."""
        layout = QHBoxLayout()

        self.new_protocol_btn = QPushButton("📄 New Protocol")
        self.new_protocol_btn.clicked.connect(self._on_new_protocol)
        layout.addWidget(self.new_protocol_btn)

        self.save_protocol_btn = QPushButton("💾 Save Protocol")
        self.save_protocol_btn.clicked.connect(self._on_save_protocol)
        layout.addWidget(self.save_protocol_btn)

        self.load_protocol_btn = QPushButton("📂 Load Protocol")
        self.load_protocol_btn.clicked.connect(self._on_load_protocol)
        layout.addWidget(self.load_protocol_btn)

        layout.addStretch()

        self.execute_protocol_btn = QPushButton("▶ Execute Protocol")
        self.execute_protocol_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 10px;"
        )
        self.execute_protocol_btn.clicked.connect(self._on_execute_protocol)
        self.execute_protocol_btn.setEnabled(False)
        layout.addWidget(self.execute_protocol_btn)

        return layout

    # ========================================================================
    # Signal Handlers - Metadata
    # ========================================================================

    def _on_metadata_changed(self) -> None:
        """Handle protocol metadata changes (name, loop count)."""
        if self.current_protocol is None:
            return

        self.current_protocol.protocol_name = self.protocol_name_input.text()
        self.current_protocol.loop_count = self.loop_count_spin.value()

        self._update_total_duration()

    # ========================================================================
    # Signal Handlers - Line Selection
    # ========================================================================

    def _on_line_selected(self, index: int) -> None:
        """Handle line selection in sequence view."""
        self.current_line_index = index

        if index < 0 or self.current_protocol is None or index >= len(self.current_protocol.lines):
            # No valid selection
            self.editor_status_label.setText("No line selected - add a line to begin")
            self.movement_group.setEnabled(False)
            self.laser_group.setEnabled(False)
            self.dwell_group.setEnabled(False)
            self.apply_changes_btn.setEnabled(False)
            self.remove_line_btn.setEnabled(False)
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            return

        # Load line data into editor
        line = self.current_protocol.lines[index]
        self._load_line_into_editor(line)

        # Enable editor
        self.editor_status_label.setText(f"Editing Line {line.line_number}")
        self.movement_group.setEnabled(True)
        self.laser_group.setEnabled(True)
        self.dwell_group.setEnabled(True)
        self.apply_changes_btn.setEnabled(True)
        self.remove_line_btn.setEnabled(True)

        # Enable/disable move up/down buttons
        self.move_up_btn.setEnabled(index > 0)
        self.move_down_btn.setEnabled(index < len(self.current_protocol.lines) - 1)

    # ========================================================================
    # Signal Handlers - Sequence Controls
    # ========================================================================

    def _on_add_line(self) -> None:
        """Add new line to protocol."""
        if self.current_protocol is None:
            return

        # Create new line with default parameters
        line_number = len(self.current_protocol.lines) + 1
        new_line = ProtocolLine(line_number=line_number)

        self.current_protocol.lines.append(new_line)
        self._update_sequence_view()

        # Select the new line
        self.sequence_list.setCurrentRow(len(self.current_protocol.lines) - 1)

    def _on_remove_line(self) -> None:
        """Remove selected line from protocol."""
        if self.current_protocol is None or self.current_line_index < 0:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete Line {self.current_line_index + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.current_protocol.lines[self.current_line_index]

            # Renumber remaining lines
            for i, line in enumerate(self.current_protocol.lines):
                line.line_number = i + 1

            self._update_sequence_view()
            self.current_line_index = -1

    def _on_move_line_up(self) -> None:
        """Move selected line up in sequence."""
        if self.current_protocol is None or self.current_line_index <= 0:
            return

        # Swap lines
        idx = self.current_line_index
        self.current_protocol.lines[idx], self.current_protocol.lines[idx - 1] = (
            self.current_protocol.lines[idx - 1],
            self.current_protocol.lines[idx],
        )

        # Renumber
        self.current_protocol.lines[idx - 1].line_number = idx
        self.current_protocol.lines[idx].line_number = idx + 1

        self._update_sequence_view()
        self.sequence_list.setCurrentRow(idx - 1)

    def _on_move_line_down(self) -> None:
        """Move selected line down in sequence."""
        if self.current_protocol is None or self.current_line_index < 0:
            return

        if self.current_line_index >= len(self.current_protocol.lines) - 1:
            return

        # Swap lines
        idx = self.current_line_index
        self.current_protocol.lines[idx], self.current_protocol.lines[idx + 1] = (
            self.current_protocol.lines[idx + 1],
            self.current_protocol.lines[idx],
        )

        # Renumber
        self.current_protocol.lines[idx].line_number = idx + 1
        self.current_protocol.lines[idx + 1].line_number = idx + 2

        self._update_sequence_view()
        self.sequence_list.setCurrentRow(idx + 1)

    # ========================================================================
    # Signal Handlers - Line Editor
    # ========================================================================

    def _on_movement_enable_toggled(self, checked: bool) -> None:
        """Handle movement enable checkbox toggle."""
        self.move_position_radio.setEnabled(checked)
        self.move_home_radio.setEnabled(checked)
        self.position_params_widget.setEnabled(checked)
        self.home_params_widget.setEnabled(checked)

    def _on_movement_type_changed(self) -> None:
        """Handle movement type radio button change."""
        if self.move_position_radio.isChecked():
            self.position_params_widget.setVisible(True)
            self.home_params_widget.setVisible(False)
        else:
            self.position_params_widget.setVisible(False)
            self.home_params_widget.setVisible(True)

    def _on_laser_enable_toggled(self, checked: bool) -> None:
        """Handle laser enable checkbox toggle."""
        self.laser_set_radio.setEnabled(checked)
        self.laser_ramp_radio.setEnabled(checked)
        self.laser_set_params_widget.setEnabled(checked)
        self.laser_ramp_params_widget.setEnabled(checked)

    def _on_laser_type_changed(self) -> None:
        """Handle laser type radio button change."""
        if self.laser_set_radio.isChecked():
            self.laser_set_params_widget.setVisible(True)
            self.laser_ramp_params_widget.setVisible(False)
        else:
            self.laser_set_params_widget.setVisible(False)
            self.laser_ramp_params_widget.setVisible(True)

    def _on_dwell_enable_toggled(self, checked: bool) -> None:
        """Handle dwell enable checkbox toggle."""
        self.dwell_duration_spin.setEnabled(checked)

    def _on_line_params_changed(self) -> None:
        """Handle any line parameter change (for real-time validation)."""
        # This can be used for real-time validation feedback
        pass

    def _on_apply_changes(self) -> None:
        """Apply editor changes to current line."""
        if self.current_protocol is None or self.current_line_index < 0:
            return

        line = self.current_protocol.lines[self.current_line_index]

        # Apply movement parameters
        if self.movement_enable_check.isChecked():
            if self.move_position_radio.isChecked():
                move_type = (
                    MoveType.ABSOLUTE
                    if self.move_type_combo.currentIndex() == 0
                    else MoveType.RELATIVE
                )
                line.movement = MoveParams(
                    target_position_mm=self.target_position_spin.value(),
                    speed_mm_per_s=self.move_speed_spin.value(),
                    move_type=move_type,
                )
            else:
                line.movement = HomeParams(speed_mm_per_s=self.home_speed_spin.value())
        else:
            line.movement = None

        # Apply laser parameters
        if self.laser_enable_check.isChecked():
            if self.laser_set_radio.isChecked():
                line.laser = LaserSetParams(power_watts=self.laser_set_power_spin.value())
            else:
                line.laser = LaserRampParams(
                    start_power_watts=self.laser_start_power_spin.value(),
                    end_power_watts=self.laser_end_power_spin.value(),
                    duration_s=self.laser_ramp_duration_spin.value(),
                )
        else:
            line.laser = None

        # Apply dwell parameters
        if self.dwell_enable_check.isChecked():
            line.dwell = DwellParams(duration_s=self.dwell_duration_spin.value())
        else:
            line.dwell = None

        # Apply notes
        line.notes = self.notes_input.text()

        # Validate line
        valid, error = line.validate(self.safety_limits)
        if not valid:
            QMessageBox.warning(self, "Validation Error", f"Line validation failed:\n{error}")
            return

        # Update sequence view
        self._update_sequence_view()
        self._update_total_duration()

        logger.info(f"Applied changes to Line {line.line_number}")

    # ========================================================================
    # Signal Handlers - Protocol Operations
    # ========================================================================

    def _on_new_protocol(self) -> None:
        """Create new protocol."""
        # Confirm if current protocol has unsaved changes
        if self.current_protocol is not None and len(self.current_protocol.lines) > 0:
            reply = QMessageBox.question(
                self,
                "Confirm New Protocol",
                "Current protocol will be cleared. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self._create_new_protocol()

    def _on_save_protocol(self) -> None:
        """Save current protocol to JSON file."""
        if self.current_protocol is None:
            return

        # Validate protocol before saving
        valid, errors = self.current_protocol.validate()
        if not valid:
            error_msg = "\n".join(errors)
            QMessageBox.warning(
                self, "Protocol Validation Failed", f"Cannot save invalid protocol:\n\n{error_msg}"
            )
            return

        # Open file dialog
        default_name = self.current_protocol.protocol_name.replace(" ", "_") or "protocol"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Protocol",
            str(Path.home() / f"{default_name}.json"),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        # Ensure .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"

        try:
            # Serialize to JSON
            protocol_data = self.current_protocol.to_dict()

            # Save to file
            with open(file_path, "w") as f:
                json.dump(protocol_data, f, indent=2)

            logger.info(f"Protocol saved to: {file_path}")
            QMessageBox.information(
                self, "Protocol Saved", f"Protocol saved successfully:\n{file_path}"
            )

        except Exception as e:
            logger.error(f"Failed to save protocol: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save protocol:\n{str(e)}")

    def _on_load_protocol(self) -> None:
        """Load protocol from JSON file."""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Protocol",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            # Load from file
            with open(file_path, "r") as f:
                protocol_data = json.load(f)

            # Deserialize
            protocol = LineBasedProtocol.from_dict(protocol_data)

            # Validate
            valid, errors = protocol.validate()
            if not valid:
                error_msg = "\n".join(errors)
                reply = QMessageBox.warning(
                    self,
                    "Protocol Validation Failed",
                    f"Loaded protocol has validation errors:\n\n{error_msg}\n\nLoad anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            # Set as current protocol
            self.current_protocol = protocol
            self._refresh_ui_from_protocol()

            logger.info(f"Protocol loaded from: {file_path}")
            QMessageBox.information(
                self, "Protocol Loaded", f"Protocol loaded successfully:\n{protocol.protocol_name}"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {e}")
            QMessageBox.critical(self, "Load Error", f"Invalid JSON file:\n{str(e)}")

        except Exception as e:
            logger.error(f"Failed to load protocol: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load protocol:\n{str(e)}")

    def _on_execute_protocol(self) -> None:
        """Execute the current protocol."""
        if self.current_protocol is None:
            return

        # Validate protocol
        valid, errors = self.current_protocol.validate()
        if not valid:
            error_msg = "\n".join(errors)
            QMessageBox.warning(
                self,
                "Protocol Validation Failed",
                f"Cannot execute invalid protocol:\n\n{error_msg}",
            )
            return

        # Emit protocol_ready signal
        self.protocol_ready.emit(self.current_protocol)
        logger.info(f"Protocol ready for execution: {self.current_protocol.protocol_name}")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _create_new_protocol(self) -> None:
        """Create new empty protocol."""
        self.current_protocol = LineBasedProtocol(
            protocol_name="New Protocol",
            version="1.0",
            lines=[],
            safety_limits=self.safety_limits,
        )
        self._refresh_ui_from_protocol()
        logger.info("New protocol created")

    def _refresh_ui_from_protocol(self) -> None:
        """Refresh entire UI from current protocol."""
        if self.current_protocol is None:
            return

        # Update metadata
        self.protocol_name_input.setText(self.current_protocol.protocol_name)
        self.loop_count_spin.setValue(self.current_protocol.loop_count)

        # Update sequence view
        self._update_sequence_view()

        # Update total duration
        self._update_total_duration()

        # Clear line selection
        self.current_line_index = -1
        self.sequence_list.setCurrentRow(-1)

        # Enable execute button if protocol has lines
        self.execute_protocol_btn.setEnabled(len(self.current_protocol.lines) > 0)

    def _update_sequence_view(self) -> None:
        """Update protocol sequence list with line summaries."""
        if self.current_protocol is None:
            return

        # Save current selection
        current_row = self.sequence_list.currentRow()

        # Clear and rebuild
        self.sequence_list.clear()

        # Add line summaries
        for i, line in enumerate(self.current_protocol.lines):
            # Calculate current position for duration calculation
            # (simplified: assume starting from 0)
            summary = line.get_summary(current_position_mm=0.0)
            item = QListWidgetItem(summary)
            self.sequence_list.addItem(item)

        # Restore selection
        if 0 <= current_row < len(self.current_protocol.lines):
            self.sequence_list.setCurrentRow(current_row)

        # Update execute button state
        self.execute_protocol_btn.setEnabled(len(self.current_protocol.lines) > 0)

    def _update_total_duration(self) -> None:
        """Update total protocol duration display."""
        if self.current_protocol is None:
            self.total_duration_label.setText("0.0s")
            return

        total_duration = self.current_protocol.calculate_total_duration()
        self.total_duration_label.setText(f"{total_duration:.1f}s")

    def _load_line_into_editor(self, line: ProtocolLine) -> None:
        """Load line parameters into editor UI."""
        # Movement
        if line.movement is not None:
            self.movement_enable_check.setChecked(True)

            if isinstance(line.movement, MoveParams):
                self.move_position_radio.setChecked(True)
                self.target_position_spin.setValue(line.movement.target_position_mm)
                self.move_speed_spin.setValue(line.movement.speed_mm_per_s)
                self.move_type_combo.setCurrentIndex(
                    0 if line.movement.move_type == MoveType.ABSOLUTE else 1
                )
            elif isinstance(line.movement, HomeParams):
                self.move_home_radio.setChecked(True)
                self.home_speed_spin.setValue(line.movement.speed_mm_per_s)
        else:
            self.movement_enable_check.setChecked(False)

        # Laser
        if line.laser is not None:
            self.laser_enable_check.setChecked(True)

            if isinstance(line.laser, LaserSetParams):
                self.laser_set_radio.setChecked(True)
                self.laser_set_power_spin.setValue(line.laser.power_watts)
            elif isinstance(line.laser, LaserRampParams):
                self.laser_ramp_radio.setChecked(True)
                self.laser_start_power_spin.setValue(line.laser.start_power_watts)
                self.laser_end_power_spin.setValue(line.laser.end_power_watts)
                self.laser_ramp_duration_spin.setValue(line.laser.duration_s)
        else:
            self.laser_enable_check.setChecked(False)

        # Dwell
        if line.dwell is not None:
            self.dwell_enable_check.setChecked(True)
            self.dwell_duration_spin.setValue(line.dwell.duration_s)
        else:
            self.dwell_enable_check.setChecked(False)

        # Notes
        self.notes_input.setText(line.notes)

    def set_safety_limits(self, limits: SafetyLimits) -> None:
        """
        Update safety limits and refresh UI ranges.

        Args:
            limits: New safety limits
        """
        self.safety_limits = limits

        # Update UI control ranges
        self.target_position_spin.setRange(
            limits.min_actuator_position_mm, limits.max_actuator_position_mm
        )
        self.move_speed_spin.setRange(0.1, limits.max_actuator_speed_mm_per_s)
        self.home_speed_spin.setRange(0.1, limits.max_actuator_speed_mm_per_s)

        self.laser_set_power_spin.setRange(0.0, limits.max_power_watts)
        self.laser_start_power_spin.setRange(0.0, limits.max_power_watts)
        self.laser_end_power_spin.setRange(0.0, limits.max_power_watts)

        self.laser_ramp_duration_spin.setRange(0.1, limits.max_duration_seconds)
        self.dwell_duration_spin.setRange(0.1, limits.max_duration_seconds)

        logger.info(f"Safety limits updated: {limits}")

    def get_current_protocol(self) -> Optional[LineBasedProtocol]:
        """
        Get the current protocol.

        Returns:
            Current protocol or None
        """
        return self.current_protocol
