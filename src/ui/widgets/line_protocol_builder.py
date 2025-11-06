"""
Line-Based Protocol Builder Widget - Complete

Hybrid table/form UI for building protocols with concurrent line-based actions.
Each line can combine movement, laser control, and dwell time.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
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
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.protocol_line import (
    DwellParams,
    HomeParams,
    LaserRampParams,
    LaserSetCurrentParams,
    LaserSetParams,
    LineBasedProtocol,
    MoveParams,
    MoveType,
    ProtocolLine,
    SafetyLimits,
)
from ui.design_tokens import Colors

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

        # Main content: 2 columns (unified builder | graph)
        content_layout = QHBoxLayout()

        # LEFT COLUMN: Unified protocol builder (single box)
        builder_group = self._create_unified_builder()
        content_layout.addWidget(builder_group, stretch=1)  # 50% width

        # RIGHT COLUMN: Position graph
        graph_group = self._create_graph_panel()
        content_layout.addWidget(graph_group, stretch=1)  # 50% width

        main_layout.addLayout(content_layout)

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

        # Total duration display
        layout.addWidget(QLabel("Total Duration:"))
        self.total_duration_label = QLabel("0.0s")
        self.total_duration_label.setStyleSheet(f"font-weight: bold; color: {Colors.SAFE};")
        layout.addWidget(self.total_duration_label)

        # Total energy display
        layout.addWidget(QLabel("Total Energy:"))
        self.total_energy_label = QLabel("0.0J")
        self.total_energy_label.setStyleSheet(f"font-weight: bold; color: {Colors.WARNING};")
        self.total_energy_label.setToolTip("Total laser energy delivered (Power × Time)")
        layout.addWidget(self.total_energy_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_unified_builder(self) -> QGroupBox:
        """Create unified protocol builder with logical workflow order."""
        group = QGroupBox("Protocol Builder")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # ===== 1. FILE OPERATIONS + PROTOCOL METADATA (combined row) =====
        file_metadata_layout = QHBoxLayout()

        # File operation buttons
        self.new_protocol_btn = QPushButton("📄 New")
        self.new_protocol_btn.clicked.connect(self._on_new_protocol)
        self.new_protocol_btn.setToolTip("Create new protocol")
        self.new_protocol_btn.setMinimumHeight(30)
        file_metadata_layout.addWidget(self.new_protocol_btn)

        self.load_protocol_btn = QPushButton("📂 Load")
        self.load_protocol_btn.clicked.connect(self._on_load_protocol)
        self.load_protocol_btn.setToolTip("Load existing protocol")
        self.load_protocol_btn.setMinimumHeight(30)
        file_metadata_layout.addWidget(self.load_protocol_btn)

        self.save_protocol_btn = QPushButton("💾 Save")
        self.save_protocol_btn.clicked.connect(self._on_save_protocol)
        self.save_protocol_btn.setToolTip("Save protocol to file")
        self.save_protocol_btn.setMinimumHeight(30)
        file_metadata_layout.addWidget(self.save_protocol_btn)

        file_metadata_layout.addWidget(QLabel(" | "))  # Visual separator

        # Protocol name
        file_metadata_layout.addWidget(QLabel("Name:"))
        self.protocol_name_input = QLineEdit()
        self.protocol_name_input.setPlaceholderText("Protocol name...")
        self.protocol_name_input.textChanged.connect(self._on_metadata_changed)
        self.protocol_name_input.setMaximumWidth(200)
        file_metadata_layout.addWidget(self.protocol_name_input)

        # Total duration display
        file_metadata_layout.addWidget(QLabel("Duration:"))
        self.total_duration_label = QLabel("0.0s")
        self.total_duration_label.setStyleSheet(f"font-weight: bold; color: {Colors.SAFE};")
        file_metadata_layout.addWidget(self.total_duration_label)

        # Total energy display
        file_metadata_layout.addWidget(QLabel("Energy:"))
        self.total_energy_label = QLabel("0.0J")
        self.total_energy_label.setStyleSheet(f"font-weight: bold; color: {Colors.WARNING};")
        self.total_energy_label.setToolTip("Total laser energy delivered (Power × Time)")
        file_metadata_layout.addWidget(self.total_energy_label)

        file_metadata_layout.addStretch()
        main_layout.addLayout(file_metadata_layout)

        # ===== 2. LINE EDITOR PARAMETERS (with Add Line button inside) =====

        # Create scroll area for editor parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setMaximumHeight(400)  # Limit height to leave room for sequence list

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)

        # Button row: Update Line + Add Line
        button_row = QHBoxLayout()
        button_row.setSpacing(5)

        self.update_line_btn = QPushButton("💾 Update Line")
        self.update_line_btn.setStyleSheet(
            "background-color: #388E3C; color: white; font-weight: bold; padding: 8px;"
        )
        self.update_line_btn.setToolTip("Save changes to current line")
        self.update_line_btn.setMinimumHeight(35)
        self.update_line_btn.clicked.connect(self._on_update_line)
        button_row.addWidget(self.update_line_btn)

        self.add_line_btn = QPushButton("➕ Add Line")
        self.add_line_btn.setStyleSheet(
            "background-color: #616161; color: white; font-weight: bold; padding: 8px;"
        )
        self.add_line_btn.setToolTip("Add new line to protocol")
        self.add_line_btn.setMinimumHeight(35)
        self.add_line_btn.clicked.connect(self._on_add_line)
        button_row.addWidget(self.add_line_btn)

        scroll_layout.addLayout(button_row)

        # Create 2-column layout for parameters
        params_columns = QHBoxLayout()
        params_columns.setSpacing(10)

        # LEFT COLUMN: Movement + Dwell (motion/timing related)
        left_column = QVBoxLayout()
        left_column.setSpacing(5)

        self.movement_group = self._create_movement_section()
        left_column.addWidget(self.movement_group)

        self.dwell_group = self._create_dwell_section()
        left_column.addWidget(self.dwell_group)

        left_column.addStretch()
        params_columns.addLayout(left_column, stretch=1)

        # RIGHT COLUMN: Laser + Line settings (power + repetition)
        right_column = QVBoxLayout()
        right_column.setSpacing(5)

        self.laser_group = self._create_laser_section()
        right_column.addWidget(self.laser_group)

        # Line loop count (inside right column)
        loop_group = QGroupBox("Line Repetition")
        loop_layout = QVBoxLayout()

        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Repeat:"))
        self.line_loop_spin = QSpinBox()
        self.line_loop_spin.setRange(1, 100)
        self.line_loop_spin.setValue(1)
        self.line_loop_spin.setToolTip("Number of times to repeat this specific line")
        self.line_loop_spin.setMinimumWidth(80)
        self.line_loop_spin.setSuffix(" times")
        self.line_loop_spin.valueChanged.connect(self._on_line_params_changed)
        repeat_layout.addWidget(self.line_loop_spin)
        repeat_layout.addStretch()
        loop_layout.addLayout(repeat_layout)

        # Line notes (inside right column)
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.textChanged.connect(self._on_line_params_changed)
        notes_layout.addWidget(self.notes_input)
        loop_layout.addLayout(notes_layout)

        loop_group.setLayout(loop_layout)
        right_column.addWidget(loop_group)

        right_column.addStretch()
        params_columns.addLayout(right_column, stretch=1)

        scroll_layout.addLayout(params_columns)

        scroll_layout.addStretch()

        # Disable editor initially
        self.movement_group.setEnabled(False)
        self.laser_group.setEnabled(False)
        self.dwell_group.setEnabled(False)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ===== 5. SEQUENCE LIST (at bottom) =====
        instructions = QLabel(
            "Lines execute concurrently (move + laser + dwell)."
        )
        instructions.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        main_layout.addWidget(instructions)

        self.sequence_list = QListWidget()
        self.sequence_list.setAlternatingRowColors(True)
        self.sequence_list.currentRowChanged.connect(self._on_line_selected)
        self.sequence_list.setMinimumHeight(200)  # Reduced from 300

        # Larger, more readable font for line list
        list_font = self.sequence_list.font()
        list_font.setPointSize(10)
        list_font.setFamily("Consolas")  # Monospace for column alignment
        self.sequence_list.setFont(list_font)

        main_layout.addWidget(self.sequence_list)

        # ===== 6. SEQUENCE CONTROL BUTTONS =====
        btn_layout = QHBoxLayout()

        self.remove_line_btn = QPushButton("➖ Remove")
        self.remove_line_btn.clicked.connect(self._on_remove_line)
        self.remove_line_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_line_btn)

        self.duplicate_line_btn = QPushButton("📋 Duplicate")
        self.duplicate_line_btn.clicked.connect(self._on_duplicate_line)
        self.duplicate_line_btn.setEnabled(False)
        self.duplicate_line_btn.setToolTip("Duplicate the selected line")
        btn_layout.addWidget(self.duplicate_line_btn)

        self.move_up_btn = QPushButton("⬆ Up")
        self.move_up_btn.clicked.connect(self._on_move_line_up)
        self.move_up_btn.setEnabled(False)
        btn_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("⬇ Down")
        self.move_down_btn.clicked.connect(self._on_move_line_down)
        self.move_down_btn.setEnabled(False)
        btn_layout.addWidget(self.move_down_btn)

        main_layout.addLayout(btn_layout)

        # ===== 7. PROTOCOL EXECUTION (at bottom) =====
        exec_layout = QHBoxLayout()
        exec_layout.addWidget(QLabel("Loops:"))
        self.loop_count_spin = QSpinBox()
        self.loop_count_spin.setRange(1, 100)
        self.loop_count_spin.setValue(1)
        self.loop_count_spin.setToolTip("Number of times to repeat the entire protocol")
        self.loop_count_spin.setMinimumWidth(70)
        self.loop_count_spin.valueChanged.connect(self._on_metadata_changed)
        exec_layout.addWidget(self.loop_count_spin)

        self.execute_protocol_btn = QPushButton("▶▶ EXECUTE PROTOCOL ◀◀")
        self.execute_protocol_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; "
            "padding: 10px; font-size: 14px;"
        )
        self.execute_protocol_btn.clicked.connect(self._on_execute_protocol)
        self.execute_protocol_btn.setEnabled(False)
        self.execute_protocol_btn.setMinimumHeight(45)
        exec_layout.addWidget(self.execute_protocol_btn, stretch=1)

        main_layout.addLayout(exec_layout)

        group.setLayout(main_layout)
        return group


    def _create_line_editor(self) -> QGroupBox:
        """Create contextual line editor panel with scrolling."""
        group = QGroupBox("Line Editor")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Editor status label (removed duplicate Add Line button)
        top_layout = QHBoxLayout()
        self.editor_status_label = QLabel("Select a line to edit or add a new line")
        self.editor_status_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        top_layout.addWidget(self.editor_status_label)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Create scroll area for editor content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(5)

        # Movement section
        self.movement_group = self._create_movement_section()
        layout.addWidget(self.movement_group)

        # Laser section
        self.laser_group = self._create_laser_section()
        layout.addWidget(self.laser_group)

        # Dwell section
        self.dwell_group = self._create_dwell_section()
        layout.addWidget(self.dwell_group)

        # Line loop count
        loop_layout = QHBoxLayout()
        loop_layout.addWidget(QLabel("Repeat this line:"))
        self.line_loop_spin = QSpinBox()
        self.line_loop_spin.setRange(1, 100)
        self.line_loop_spin.setValue(1)
        self.line_loop_spin.setToolTip("Number of times to repeat this specific line")
        self.line_loop_spin.setMinimumWidth(80)
        self.line_loop_spin.setSuffix(" times")
        self.line_loop_spin.valueChanged.connect(self._on_line_params_changed)
        loop_layout.addWidget(self.line_loop_spin)
        loop_layout.addStretch()
        layout.addLayout(loop_layout)

        # Line notes
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes for this line...")
        self.notes_input.textChanged.connect(self._on_line_params_changed)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        layout.addStretch()

        # Disable editor initially
        self.movement_group.setEnabled(False)
        self.laser_group.setEnabled(False)
        self.dwell_group.setEnabled(False)

        # Set scroll content and add to main layout
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        group.setLayout(main_layout)
        return group

    def _create_graph_panel(self) -> QGroupBox:
        """Create position and laser power graph panel (3rd column)."""
        group = QGroupBox("Position & Laser Power")
        layout = QVBoxLayout()

        # Create pyqtgraph plot widget with dual Y-axes
        self.position_plot = pg.PlotWidget()
        self.position_plot.setBackground("w")
        self.position_plot.setLabel("left", "Position", units="mm", color="blue")
        self.position_plot.setLabel("bottom", "Time", units="s")
        self.position_plot.setTitle("Actuator Position & Laser Power Over Time")
        self.position_plot.showGrid(x=True, y=True, alpha=0.3)

        # Create second Y-axis for laser power/current (right side)
        self.laser_axis = pg.ViewBox()
        self.position_plot.scene().addItem(self.laser_axis)
        self.position_plot.getAxis("right").linkToView(self.laser_axis)
        self.laser_axis.setXLink(self.position_plot)
        self.position_plot.getAxis("right").setLabel("Power/Current", units="mW/mA", color="orange")
        self.position_plot.showAxis("right")
        self.position_plot.getAxis("right").setStyle(showValues=True)

        # Update views when plot is resized
        def update_views():
            self.laser_axis.setGeometry(self.position_plot.getViewBox().sceneBoundingRect())
            self.laser_axis.linkedViewChanged(
                self.position_plot.getViewBox(), self.laser_axis.XAxis
            )

        self.position_plot.getViewBox().sigResized.connect(update_views)

        # Add reference lines
        self.position_plot.addLine(
            y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
        )

        layout.addWidget(self.position_plot)
        group.setLayout(layout)
        return group

    def _create_movement_section(self) -> QGroupBox:
        """Create movement configuration section."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Movement checkbox (enable/disable)
        self.movement_checkbox = QCheckBox("Movement")
        self.movement_checkbox.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.movement_checkbox.toggled.connect(self._on_line_params_changed)
        layout.addWidget(self.movement_checkbox)

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

        # Acceleration
        accel_layout = QHBoxLayout()
        accel_layout.addWidget(QLabel("Accel (mm/s²):"))
        self.move_accel_spin = QDoubleSpinBox()
        self.move_accel_spin.setRange(0.1, 20.0)
        self.move_accel_spin.setDecimals(1)
        self.move_accel_spin.setSingleStep(0.5)
        self.move_accel_spin.setValue(5.0)
        self.move_accel_spin.setToolTip("Acceleration rate for movement")
        self.move_accel_spin.valueChanged.connect(self._on_line_params_changed)
        accel_layout.addWidget(self.move_accel_spin)
        accel_layout.addStretch()
        pos_layout.addLayout(accel_layout)

        # Deceleration
        decel_layout = QHBoxLayout()
        decel_layout.addWidget(QLabel("Decel (mm/s²):"))
        self.move_decel_spin = QDoubleSpinBox()
        self.move_decel_spin.setRange(0.1, 20.0)
        self.move_decel_spin.setDecimals(1)
        self.move_decel_spin.setSingleStep(0.5)
        self.move_decel_spin.setValue(5.0)
        self.move_decel_spin.setToolTip("Deceleration rate for movement")
        self.move_decel_spin.valueChanged.connect(self._on_line_params_changed)
        decel_layout.addWidget(self.move_decel_spin)
        decel_layout.addStretch()
        pos_layout.addLayout(decel_layout)

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

        # Acceleration
        home_accel_layout = QHBoxLayout()
        home_accel_layout.addWidget(QLabel("Accel (mm/s²):"))
        self.home_accel_spin = QDoubleSpinBox()
        self.home_accel_spin.setRange(0.1, 20.0)
        self.home_accel_spin.setDecimals(1)
        self.home_accel_spin.setSingleStep(0.5)
        self.home_accel_spin.setValue(5.0)
        self.home_accel_spin.setToolTip("Acceleration rate for homing")
        self.home_accel_spin.valueChanged.connect(self._on_line_params_changed)
        home_accel_layout.addWidget(self.home_accel_spin)
        home_accel_layout.addStretch()
        home_layout.addLayout(home_accel_layout)

        # Deceleration
        home_decel_layout = QHBoxLayout()
        home_decel_layout.addWidget(QLabel("Decel (mm/s²):"))
        self.home_decel_spin = QDoubleSpinBox()
        self.home_decel_spin.setRange(0.1, 20.0)
        self.home_decel_spin.setDecimals(1)
        self.home_decel_spin.setSingleStep(0.5)
        self.home_decel_spin.setValue(5.0)
        self.home_decel_spin.setToolTip("Deceleration rate for homing")
        self.home_decel_spin.valueChanged.connect(self._on_line_params_changed)
        home_decel_layout.addWidget(self.home_decel_spin)
        home_decel_layout.addStretch()
        home_layout.addLayout(home_decel_layout)

        self.home_params_widget.setLayout(home_layout)
        self.home_params_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.home_params_widget)

        group.setLayout(layout)
        return group

    def _create_laser_section(self) -> QGroupBox:
        """Create laser configuration section."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Laser checkbox (enable/disable)
        self.laser_checkbox = QCheckBox("Laser")
        self.laser_checkbox.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.laser_checkbox.toggled.connect(self._on_line_params_changed)
        layout.addWidget(self.laser_checkbox)

        # Laser mode radio buttons (Set vs Ramp)
        type_layout = QHBoxLayout()
        type_layout.addSpacing(20)  # Indent

        self.laser_set_radio = QRadioButton("Set")
        self.laser_set_radio.setChecked(True)
        self.laser_set_radio.toggled.connect(self._on_laser_type_changed)
        type_layout.addWidget(self.laser_set_radio)

        self.laser_ramp_radio = QRadioButton("Ramp")
        self.laser_ramp_radio.toggled.connect(self._on_laser_type_changed)
        type_layout.addWidget(self.laser_ramp_radio)

        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Set laser parameters (power or current)
        self.laser_set_params_widget = QWidget()
        set_layout = QVBoxLayout()
        set_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        # Control mode (Power vs Current)
        control_mode_layout = QHBoxLayout()
        self.laser_power_mode_radio = QRadioButton("Power (mW)")
        self.laser_power_mode_radio.setChecked(True)
        self.laser_power_mode_radio.toggled.connect(self._on_laser_control_mode_changed)
        control_mode_layout.addWidget(self.laser_power_mode_radio)

        self.laser_current_mode_radio = QRadioButton("Current (mA)")
        self.laser_current_mode_radio.toggled.connect(self._on_laser_control_mode_changed)
        control_mode_layout.addWidget(self.laser_current_mode_radio)
        control_mode_layout.addStretch()
        set_layout.addLayout(control_mode_layout)

        # Power control (mW)
        self.laser_power_control_widget = QWidget()
        power_layout = QHBoxLayout()
        power_layout.setContentsMargins(0, 0, 0, 0)
        power_layout.addWidget(QLabel("Power (mW):"))
        self.laser_set_power_spin = QDoubleSpinBox()
        self.laser_set_power_spin.setRange(0.0, 10000.0)  # 0-10W in mW
        self.laser_set_power_spin.setDecimals(1)
        self.laser_set_power_spin.setSingleStep(10.0)
        self.laser_set_power_spin.valueChanged.connect(self._on_line_params_changed)
        power_layout.addWidget(self.laser_set_power_spin)
        power_layout.addStretch()
        self.laser_power_control_widget.setLayout(power_layout)
        set_layout.addWidget(self.laser_power_control_widget)

        # Current control (mA)
        self.laser_current_control_widget = QWidget()
        current_layout = QHBoxLayout()
        current_layout.setContentsMargins(0, 0, 0, 0)
        current_layout.addWidget(QLabel("Current (mA):"))
        self.laser_set_current_spin = QDoubleSpinBox()
        self.laser_set_current_spin.setRange(0.0, 2000.0)  # From config
        self.laser_set_current_spin.setDecimals(1)
        self.laser_set_current_spin.setSingleStep(10.0)
        self.laser_set_current_spin.valueChanged.connect(self._on_line_params_changed)
        current_layout.addWidget(self.laser_set_current_spin)
        current_layout.addStretch()
        self.laser_current_control_widget.setLayout(current_layout)
        self.laser_current_control_widget.setVisible(False)  # Hidden by default
        set_layout.addWidget(self.laser_current_control_widget)

        self.laser_set_params_widget.setLayout(set_layout)
        layout.addWidget(self.laser_set_params_widget)

        # Ramp laser parameters (power only for now)
        self.laser_ramp_params_widget = QWidget()
        ramp_layout = QVBoxLayout()
        ramp_layout.setContentsMargins(20, 0, 0, 0)  # Indent

        # Start power
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Power (mW):"))
        self.laser_start_power_spin = QDoubleSpinBox()
        self.laser_start_power_spin.setRange(0.0, 10000.0)
        self.laser_start_power_spin.setDecimals(1)
        self.laser_start_power_spin.setSingleStep(10.0)
        self.laser_start_power_spin.valueChanged.connect(self._on_line_params_changed)
        start_layout.addWidget(self.laser_start_power_spin)
        start_layout.addStretch()
        ramp_layout.addLayout(start_layout)

        # End power
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Power (mW):"))
        self.laser_end_power_spin = QDoubleSpinBox()
        self.laser_end_power_spin.setRange(0.0, 10000.0)
        self.laser_end_power_spin.setDecimals(1)
        self.laser_end_power_spin.setSingleStep(10.0)
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

        # Dwell checkbox (enable/disable)
        self.dwell_checkbox = QCheckBox("Dwell (Wait)")
        self.dwell_checkbox.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.dwell_checkbox.toggled.connect(self._on_line_params_changed)
        layout.addWidget(self.dwell_checkbox)

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

    def _create_slider_spinbox_combo(
        self,
        label: str,
        min_val: float,
        max_val: float,
        default: float,
        decimals: int = 2,
        step: float = 0.1,
        unit: str = "",
    ) -> tuple:
        """Create a slider+spinbox combination with visual feedback.

        Returns: (layout, spinbox, slider)
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"{label}:"))

        # Spinbox
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        spinbox.setValue(default)
        if unit:
            spinbox.setSuffix(f" {unit}")
        spinbox.setMinimumWidth(100)

        # Slider
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val * (10**decimals)))
        slider.setMaximum(int(max_val * (10**decimals)))
        slider.setValue(int(default * (10**decimals)))
        slider.setMinimumWidth(150)

        # Bidirectional sync with visual feedback
        def spinbox_changed(value):
            slider.blockSignals(True)
            slider.setValue(int(value * (10**decimals)))
            slider.blockSignals(False)
            # Color feedback based on proximity to limits
            range_pct = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            if range_pct < 0.2 or range_pct > 0.8:
                slider.setStyleSheet(
                    "QSlider::handle:horizontal { background: #FF9800; }"
                )  # Orange
            elif range_pct < 0.1 or range_pct > 0.9:
                slider.setStyleSheet("QSlider::handle:horizontal { background: #F44336; }")  # Red
            else:
                slider.setStyleSheet(f"QSlider::handle:horizontal { background: {Colors.SAFE}; }")  # Green

        def slider_changed(value):
            spinbox.blockSignals(True)
            spinbox.setValue(value / (10**decimals))
            spinbox.blockSignals(False)

        spinbox.valueChanged.connect(spinbox_changed)
        slider.valueChanged.connect(slider_changed)
        spinbox.valueChanged.connect(self._on_line_params_changed)

        layout.addWidget(spinbox)
        layout.addWidget(slider)
        layout.addStretch()

        # Initial color
        spinbox_changed(default)

        return layout, spinbox, slider

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

    def _auto_save_current_line(self) -> None:
        """Auto-save the currently selected line parameters."""
        if self.current_line_index < 0 or self.current_protocol is None:
            return

        if self.current_line_index >= len(self.current_protocol.lines):
            return

        line = self.current_protocol.lines[self.current_line_index]

        # Apply movement parameters (check checkbox)
        if self.movement_checkbox.isChecked():
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
                    acceleration_mm_per_s2=self.move_accel_spin.value(),
                    deceleration_mm_per_s2=self.move_decel_spin.value(),
                )
            else:
                line.movement = HomeParams(
                    speed_mm_per_s=self.home_speed_spin.value(),
                    acceleration_mm_per_s2=self.home_accel_spin.value(),
                    deceleration_mm_per_s2=self.home_decel_spin.value(),
                )
        else:
            line.movement = None

        # Apply laser parameters (check checkbox)
        if self.laser_checkbox.isChecked():
            if self.laser_set_radio.isChecked():
                # Check which control mode is selected (Power or Current)
                if self.laser_power_mode_radio.isChecked():
                    # Power mode: Convert mW to W for storage
                    power_w = self.laser_set_power_spin.value() / 1000.0
                    line.laser = LaserSetParams(power_watts=power_w)
                else:
                    # Current mode: Store mA value using proper current params class
                    current_ma = self.laser_set_current_spin.value()
                    line.laser = LaserSetCurrentParams(current_milliamps=current_ma)
            else:
                # Ramp: Convert mW to W (power mode only for ramps currently)
                start_w = self.laser_start_power_spin.value() / 1000.0
                end_w = self.laser_end_power_spin.value() / 1000.0
                line.laser = LaserRampParams(
                    start_power_watts=start_w,
                    end_power_watts=end_w,
                    duration_s=self.laser_ramp_duration_spin.value(),
                )
        else:
            line.laser = None

        # Apply dwell parameters (check checkbox)
        if self.dwell_checkbox.isChecked():
            line.dwell = DwellParams(duration_s=self.dwell_duration_spin.value())
        else:
            line.dwell = None

        # Apply notes
        line.notes = self.notes_input.text()

        # Apply loop count
        line.loop_count = self.line_loop_spin.value()

        # Update total duration (but DON'T update sequence view to avoid recursion)
        self._update_total_duration()

    def _on_line_selected(self, index: int) -> None:
        """Handle line selection in sequence view with auto-save."""
        # AUTO-SAVE: Save previous line before switching
        if (
            self.current_line_index >= 0
            and self.current_protocol is not None
            and self.current_line_index < len(self.current_protocol.lines)
        ):
            self._auto_save_current_line()
            # Update sequence view to show new summary (but block signals to avoid recursion)
            self.sequence_list.blockSignals(True)
            self._update_sequence_view()
            self.sequence_list.blockSignals(False)

        self.current_line_index = index

        if index < 0 or self.current_protocol is None or index >= len(self.current_protocol.lines):
            # No valid selection
            # self.editor_status_label.setText("No line selected - add a line to begin")  # Removed status label
            self.movement_group.setEnabled(False)
            self.laser_group.setEnabled(False)
            self.dwell_group.setEnabled(False)
            self.remove_line_btn.setEnabled(False)
            self.duplicate_line_btn.setEnabled(False)
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            return

        # Load line data into editor
        line = self.current_protocol.lines[index]
        self._load_line_into_editor(line)

        # Enable editor
        # self.editor_status_label.setText(f"✏️ Editing Line {line.line_number} (auto-save enabled)")  # Removed status label
        self.movement_group.setEnabled(True)
        self.laser_group.setEnabled(True)
        self.dwell_group.setEnabled(True)
        self.remove_line_btn.setEnabled(True)
        self.duplicate_line_btn.setEnabled(True)

        # Enable/disable move up/down buttons
        self.move_up_btn.setEnabled(index > 0)
        self.move_down_btn.setEnabled(index < len(self.current_protocol.lines) - 1)

    # ========================================================================
    # Signal Handlers - Sequence Controls
    # ========================================================================

    def _on_update_line(self) -> None:
        """Update current line with editor values (manual save)."""
        if self.current_protocol is None or self.current_line_index < 0:
            logger.warning("No line selected to update")
            return

        # Save current line parameters
        self._auto_save_current_line()

        # Update sequence view to show new summary (with signal blocking)
        self.sequence_list.blockSignals(True)
        self._update_sequence_view()
        self.sequence_list.blockSignals(False)

        # Re-select the current line to refresh display
        self.sequence_list.setCurrentRow(self.current_line_index)

        logger.info(f"Line {self.current_line_index + 1} updated manually")

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

    def _on_duplicate_line(self) -> None:
        """Duplicate the currently selected line."""
        if self.current_protocol is None or self.current_line_index < 0:
            return

        if self.current_line_index >= len(self.current_protocol.lines):
            return

        # Auto-save current line first
        self._auto_save_current_line()

        # Copy the line
        source_line = self.current_protocol.lines[self.current_line_index]
        new_line_number = len(self.current_protocol.lines) + 1

        # Create deep copy with new line number
        duplicated_line = ProtocolLine(
            line_number=new_line_number,
            movement=source_line.movement,
            laser=source_line.laser,
            dwell=source_line.dwell,
            notes=source_line.notes + " (copy)" if source_line.notes else "(copy)",
            loop_count=source_line.loop_count if hasattr(source_line, "loop_count") else 1,
        )

        # Insert after current line
        self.current_protocol.lines.insert(self.current_line_index + 1, duplicated_line)

        # Renumber all lines
        for i, line in enumerate(self.current_protocol.lines):
            line.line_number = i + 1

        # Update view and select new line
        self._update_sequence_view()
        self.sequence_list.setCurrentRow(self.current_line_index + 1)

        logger.info(f"Duplicated line {source_line.line_number}")

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

    def _on_laser_control_mode_changed(self) -> None:
        """Handle laser control mode change (Power vs Current)."""
        if self.laser_power_mode_radio.isChecked():
            self.laser_power_control_widget.setVisible(True)
            self.laser_current_control_widget.setVisible(False)
        else:
            self.laser_power_control_widget.setVisible(False)
            self.laser_current_control_widget.setVisible(True)

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

        # Apply movement parameters (always save if values present)
        if True:  # Always save movement
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
                    acceleration_mm_per_s2=self.move_accel_spin.value(),
                    deceleration_mm_per_s2=self.move_decel_spin.value(),
                )
            else:
                line.movement = HomeParams(
                    speed_mm_per_s=self.home_speed_spin.value(),
                    acceleration_mm_per_s2=self.home_accel_spin.value(),
                    deceleration_mm_per_s2=self.home_decel_spin.value(),
                )
        else:
            line.movement = None

        # Apply laser parameters (always save if values present)
        if True:  # Always save laser
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

        # Apply dwell parameters (always save if values present)
        if True:  # Always save dwell
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

        # Open file dialog with data/protocols as default directory
        default_name = self.current_protocol.protocol_name.replace(" ", "_") or "protocol"
        protocols_dir = Path("data/protocols")
        protocols_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Protocol",
            str(protocols_dir / f"{default_name}.json"),
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
        # Open file dialog with data/protocols as default directory
        protocols_dir = Path("data/protocols")
        protocols_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Protocol",
            str(protocols_dir),
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
        """Create new protocol with one default line."""
        # Create default first line
        default_line = ProtocolLine(line_number=1)

        self.current_protocol = LineBasedProtocol(
            protocol_name="New Protocol",
            version="1.0",
            lines=[default_line],
            safety_limits=self.safety_limits,
        )
        self._refresh_ui_from_protocol()

        # Auto-select the first line so user can start editing
        self.sequence_list.setCurrentRow(0)

        logger.info("New protocol created with default line")

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

        # Add line summaries with validation status
        for i, line in enumerate(self.current_protocol.lines):
            # Validate line
            valid, error_msg = line.validate(self.safety_limits)

            # Add status indicator
            if valid:
                status_icon = "✓"
            else:
                status_icon = "✗"

            # Calculate current position for duration calculation
            # (simplified: assume starting from 0)
            summary = line.get_summary(current_position_mm=0.0)
            item_text = f"{status_icon} {summary}"
            item = QListWidgetItem(item_text)

            # Color code based on validation (no green, use default text color for valid)
            if not valid:
                item.setForeground(Qt.GlobalColor.red)
                item.setToolTip(f"Validation Error: {error_msg}")
            else:
                # Use default text color (white/light gray in dark theme)
                item.setToolTip("Line validated successfully")

            self.sequence_list.addItem(item)

        # Restore selection
        if 0 <= current_row < len(self.current_protocol.lines):
            self.sequence_list.setCurrentRow(current_row)

        # Update execute button state
        self.execute_protocol_btn.setEnabled(len(self.current_protocol.lines) > 0)

    def _update_total_duration(self) -> None:
        """Update total protocol duration and energy displays."""
        if self.current_protocol is None:
            self.total_duration_label.setText("0.0s")
            self.total_energy_label.setText("0.0J")
            return

        total_duration = self.current_protocol.calculate_total_duration()
        self.total_duration_label.setText(f"{total_duration:.1f}s")

        total_energy = self.current_protocol.calculate_total_energy()
        self.total_energy_label.setText(f"{total_energy:.1f}J")

        # Update position graph
        self._update_position_graph()

    def _update_position_graph(self) -> None:
        """Update the position and laser power graph based on current protocol."""
        self.position_plot.clear()
        self.laser_axis.clear()

        if self.current_protocol is None or len(self.current_protocol.lines) == 0:
            # Add reference line and empty state message
            self.position_plot.addLine(
                y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            )
            return

        # Calculate position and laser power trajectories
        time_points = [0.0]
        position_points = [0.0]  # Start at home position
        laser_time_points = [0.0]
        laser_power_points = [0.0]  # Start with laser off
        current_position = 0.0
        current_time = 0.0

        for line in self.current_protocol.lines:
            line_loops = line.loop_count if hasattr(line, "loop_count") else 1

            for _ in range(line_loops):
                # Calculate duration for this line
                line_duration = line.calculate_duration(current_position)

                # Track start time for this line
                line_start_time = current_time

                # Update position based on movement
                if isinstance(line.movement, MoveParams):
                    target_pos = line.movement.target_position_mm
                    if line.movement.move_type == MoveType.RELATIVE:
                        target_pos = current_position + target_pos

                    # Add intermediate point for movement
                    time_points.append(current_time + line_duration)
                    position_points.append(target_pos)
                    current_position = target_pos

                elif isinstance(line.movement, HomeParams):
                    # Move to home (0)
                    time_points.append(current_time + line_duration)
                    position_points.append(0.0)
                    current_position = 0.0

                else:
                    # No movement, dwell at current position
                    if line.dwell is not None:
                        time_points.append(current_time + line.dwell.duration_s)
                        position_points.append(current_position)

                # Update laser power (convert W to mW or display mA for graph)
                if line.laser is not None:
                    if isinstance(line.laser, LaserSetParams):
                        # Power mode: Convert W to mW
                        power_mw = line.laser.power_watts * 1000.0
                        laser_time_points.append(line_start_time)
                        laser_power_points.append(power_mw)
                        laser_time_points.append(current_time + line_duration)
                        laser_power_points.append(power_mw)
                    elif isinstance(line.laser, LaserSetCurrentParams):
                        # Current mode: Display mA value directly
                        current_ma = line.laser.current_milliamps
                        laser_time_points.append(line_start_time)
                        laser_power_points.append(current_ma)
                        laser_time_points.append(current_time + line_duration)
                        laser_power_points.append(current_ma)
                    elif isinstance(line.laser, LaserRampParams):
                        # Ramping power - add intermediate points for smooth ramp (convert to mW)
                        num_points = 10
                        for i in range(num_points + 1):
                            fraction = i / num_points
                            ramp_time = line_start_time + (line.laser.duration_s * fraction)
                            ramp_power_w = line.laser.start_power_watts + (
                                (line.laser.end_power_watts - line.laser.start_power_watts)
                                * fraction
                            )
                            ramp_power_mw = ramp_power_w * 1000.0
                            laser_time_points.append(ramp_time)
                            laser_power_points.append(ramp_power_mw)
                else:
                    # Laser off during this line
                    laser_time_points.append(line_start_time)
                    laser_power_points.append(0.0)
                    laser_time_points.append(current_time + line_duration)
                    laser_power_points.append(0.0)

                current_time += line_duration

        # Plot position trajectory (left Y-axis, blue)
        self.position_plot.plot(
            time_points,
            position_points,
            pen=pg.mkPen("b", width=2),
            symbol="o",
            symbolSize=6,
            symbolBrush="b",
            name="Position",
        )

        # Plot laser power trajectory (right Y-axis, orange/red)
        laser_curve = pg.PlotCurveItem(
            laser_time_points,
            laser_power_points,
            pen=pg.mkPen(Colors.WARNING, width=2),
            name="Laser Power",
        )
        self.laser_axis.addItem(laser_curve)

        # Add reference lines
        self.position_plot.addLine(
            y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
        )

        # Add safety limit lines if available
        if self.safety_limits:
            self.position_plot.addLine(
                y=self.safety_limits.max_actuator_position_mm,
                pen=pg.mkPen("orange", width=1, style=pg.QtCore.Qt.PenStyle.DashLine),
            )
            self.position_plot.addLine(
                y=self.safety_limits.min_actuator_position_mm,
                pen=pg.mkPen("orange", width=1, style=pg.QtCore.Qt.PenStyle.DashLine),
            )

    def _load_line_into_editor(self, line: ProtocolLine) -> None:
        """Load line parameters into editor UI."""
        # Block all signals during loading to prevent auto-save triggers
        self.movement_checkbox.blockSignals(True)
        self.laser_checkbox.blockSignals(True)
        self.dwell_checkbox.blockSignals(True)

        # Movement (set checkbox and values)
        if line.movement is not None:
            self.movement_checkbox.setChecked(True)
            if isinstance(line.movement, MoveParams):
                self.move_position_radio.setChecked(True)
                self.target_position_spin.setValue(line.movement.target_position_mm)
                self.move_speed_spin.setValue(line.movement.speed_mm_per_s)
                self.move_accel_spin.setValue(line.movement.acceleration_mm_per_s2)
                self.move_decel_spin.setValue(line.movement.deceleration_mm_per_s2)
                self.move_type_combo.setCurrentIndex(
                    0 if line.movement.move_type == MoveType.ABSOLUTE else 1
                )
            elif isinstance(line.movement, HomeParams):
                self.move_home_radio.setChecked(True)
                self.home_speed_spin.setValue(line.movement.speed_mm_per_s)
                self.home_accel_spin.setValue(line.movement.acceleration_mm_per_s2)
                self.home_decel_spin.setValue(line.movement.deceleration_mm_per_s2)
        else:
            self.movement_checkbox.setChecked(False)

        # Laser (set checkbox and values, convert W to mW/mA for display)
        if line.laser is not None:
            self.laser_checkbox.setChecked(True)
            if isinstance(line.laser, LaserSetParams):
                self.laser_set_radio.setChecked(True)
                # Power mode: Convert W to mW for display
                self.laser_power_mode_radio.setChecked(True)
                self.laser_set_power_spin.setValue(line.laser.power_watts * 1000.0)
            elif isinstance(line.laser, LaserSetCurrentParams):
                self.laser_set_radio.setChecked(True)
                # Current mode: Display mA value
                self.laser_current_mode_radio.setChecked(True)
                self.laser_set_current_spin.setValue(line.laser.current_milliamps)
            elif isinstance(line.laser, LaserRampParams):
                self.laser_ramp_radio.setChecked(True)
                # Convert W to mW for display
                self.laser_start_power_spin.setValue(line.laser.start_power_watts * 1000.0)
                self.laser_end_power_spin.setValue(line.laser.end_power_watts * 1000.0)
                self.laser_ramp_duration_spin.setValue(line.laser.duration_s)
        else:
            self.laser_checkbox.setChecked(False)

        # Dwell (set checkbox and values)
        if line.dwell is not None:
            self.dwell_checkbox.setChecked(True)
            self.dwell_duration_spin.setValue(line.dwell.duration_s)
        else:
            self.dwell_checkbox.setChecked(False)

        # Notes
        self.notes_input.setText(line.notes)

        # Loop count
        self.line_loop_spin.setValue(line.loop_count if hasattr(line, "loop_count") else 1)

        # Unblock signals after loading complete
        self.movement_checkbox.blockSignals(False)
        self.laser_checkbox.blockSignals(False)
        self.dwell_checkbox.blockSignals(False)

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

        # Convert W to mW for UI limits
        self.laser_set_power_spin.setRange(0.0, limits.max_power_watts * 1000.0)
        self.laser_start_power_spin.setRange(0.0, limits.max_power_watts * 1000.0)
        self.laser_end_power_spin.setRange(0.0, limits.max_power_watts * 1000.0)

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
