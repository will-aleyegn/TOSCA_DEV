"""
Protocol Steps Display Widget for TOSCA Treatment Workflow.

Displays treatment protocol steps as a visual list with real-time highlighting
of the current step during execution. Shows completed steps with checkmarks.

Medical Device Context:
    - Visual feedback for operator during treatment
    - Shows current position in protocol (green highlight)
    - Completed steps marked with checkmark
    - Auto-scrolls to keep current step visible
    - Provides pause/stop controls for protocol execution

Author: TOSCA Development Team
Date: 2025-11-05
Version: 0.9.15-alpha (Treatment Workflow Redesign)
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_tokens import Colors

logger = logging.getLogger(__name__)


class ProtocolStepsDisplayWidget(QWidget):
    """
    Protocol steps display widget for Treatment Workflow tab.

    Shows protocol steps as numbered list with visual indicators:
    - Current step: Green background with arrow prefix
    - Completed steps: Dark green background with checkmark
    - Pending steps: Default background

    Signals:
        pause_requested(): User clicked Pause button
        stop_requested(): User clicked Stop button
    """

    # Signals
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize protocol steps display widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # State tracking
        self.steps: List[str] = []
        self.current_step_index = -1
        self.protocol_loaded = False

        # Initialize UI
        self._init_ui()

        logger.info("ProtocolStepsDisplayWidget initialized")

    def _init_ui(self) -> None:
        """Create protocol steps display UI."""
        # Main layout - vertical (steps list only, chart is separate in main_window)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        # Protocol steps list
        steps_group = QGroupBox("Protocol Steps")
        steps_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Colors.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        steps_layout = QVBoxLayout()
        steps_layout.setSpacing(8)
        steps_group.setLayout(steps_layout)

        # Step list widget
        self.step_list = QListWidget()
        self.step_list.setMinimumHeight(200)
        self.step_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 4px;
                font-size: 11pt;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 2px;
            }}
        """)
        steps_layout.addWidget(self.step_list)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WARNING};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #EF6C00;
            }}
            QPushButton:disabled {{
                background-color: {Colors.SECONDARY};
                color: {Colors.TEXT_DISABLED};
            }}
        """)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        button_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.DANGER};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.EMERGENCY};
            }}
            QPushButton:disabled {{
                background-color: {Colors.SECONDARY};
                color: {Colors.TEXT_DISABLED};
            }}
        """)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        button_layout.addWidget(self.stop_btn)

        steps_layout.addLayout(button_layout)

        # Add steps group to main layout (chart is now separate in main_window)
        main_layout.addWidget(steps_group)

        logger.debug("ProtocolStepsDisplayWidget UI created")

    @pyqtSlot(str)
    def load_protocol(self, protocol_path: str) -> None:
        """
        Load protocol from JSON file and populate step list.

        Args:
            protocol_path: Path to protocol JSON file
        """
        try:
            # Parse protocol JSON
            with open(protocol_path, 'r') as f:
                protocol_data = json.load(f)

            # Extract and format steps
            self.steps = []

            # Handle LineProtocol format (lines array)
            if 'lines' in protocol_data:
                for i, line in enumerate(protocol_data['lines']):
                    step_text = self._format_line_protocol_step(line, i + 1)
                    self.steps.append(step_text)

            # Handle legacy Protocol format (actions array)
            elif 'actions' in protocol_data:
                for i, action in enumerate(protocol_data['actions']):
                    step_text = self._format_legacy_protocol_step(action, i + 1)
                    self.steps.append(step_text)

            else:
                logger.error(f"Unknown protocol format in {protocol_path}")
                self.steps = [f"Step 1: Unknown protocol format"]

            # Populate list widget
            self.step_list.clear()
            for i, step in enumerate(self.steps):
                item = QListWidgetItem(f"  Step {i+1}: {step}")
                item.setBackground(QColor(Colors.PANEL))
                self.step_list.addItem(item)

            self.protocol_loaded = True
            self.current_step_index = -1


            logger.info(f"Protocol loaded: {len(self.steps)} steps from {Path(protocol_path).name}")

        except Exception as e:
            logger.error(f"Failed to load protocol: {e}")
            self.steps = [f"Error loading protocol: {e}"]
            self.step_list.clear()
            item = QListWidgetItem(f"  Error: {e}")
            self.step_list.addItem(item)

    def _format_line_protocol_step(self, line: dict, step_num: int) -> str:
        """
        Format a LineProtocol line as human-readable text.

        Args:
            line: Line dictionary from protocol JSON
            step_num: Step number for display

        Returns:
            Formatted step description
        """
        # Handle new line protocol format (movement + laser objects)
        action_texts = []

        # Parse movement action
        movement = line.get('movement', {})
        if movement:
            movement_type = movement.get('type', 'none')
            params = movement.get('params', {})

            if movement_type == 'move':
                target_pos = params.get('target_position_mm', 0)
                move_type = params.get('move_type', 'absolute')
                if move_type == 'absolute':
                    action_texts.append(f"Move to {target_pos} mm")
                else:
                    action_texts.append(f"Move {target_pos:+.1f} mm")
            elif movement_type == 'dwell':
                duration = params.get('duration_seconds', 0)
                action_texts.append(f"Dwell {duration} s")

        # Parse laser action
        laser = line.get('laser', {})
        if laser:
            laser_type = laser.get('type', 'none')
            params = laser.get('params', {})

            if laser_type == 'set_current':
                current_ma = params.get('current_milliamps', 0)
                action_texts.append(f"Laser {current_ma} mA")
            elif laser_type == 'set':
                power_w = params.get('power_watts', 0)
                action_texts.append(f"Laser {power_w} W")
            elif laser_type == 'ramp_current':
                start_ma = params.get('start_milliamps', 0)
                end_ma = params.get('end_milliamps', 0)
                action_texts.append(f"Ramp laser {start_ma}→{end_ma} mA")

        # Handle legacy format (actions array) for backward compatibility
        actions = line.get('actions', [])
        if actions and not action_texts:
            for action in actions:
                action_type = action.get('type', 'unknown')
                params = action.get('parameters', {})

                if action_type == 'laser_set_current':
                    current_ma = params.get('current_milliamps', 0)
                    action_texts.append(f"Set laser to {current_ma} mA")

                elif action_type == 'actuator_move_absolute':
                    position_mm = params.get('position_mm', 0)
                    action_texts.append(f"Move actuator to {position_mm} mm")

                elif action_type == 'actuator_move_relative':
                    distance_mm = params.get('distance_mm', 0)
                    action_texts.append(f"Move actuator {distance_mm:+.1f} mm")

                elif action_type == 'wait':
                    duration_s = params.get('duration_seconds', 0)
                    action_texts.append(f"Wait {duration_s} seconds")

                else:
                    action_texts.append(f"{action_type}")

        # Return formatted text or "No actions" if empty
        if not action_texts:
            return "No actions"

        # Combine actions with " + " if multiple
        return " + ".join(action_texts)

    def _format_legacy_protocol_step(self, action: dict, step_num: int) -> str:
        """
        Format a legacy Protocol action as human-readable text.

        Args:
            action: Action dictionary from protocol JSON
            step_num: Step number for display

        Returns:
            Formatted step description
        """
        action_type = action.get('type', 'unknown')
        params = action.get('parameters', {})

        if action_type == 'set_laser_power':
            power_w = params.get('power_watts', 0)
            return f"Set laser power to {power_w} W"

        elif action_type == 'move_actuator':
            position_mm = params.get('position_mm', 0)
            return f"Move actuator to {position_mm} mm"

        elif action_type == 'wait':
            duration_s = params.get('duration_seconds', 0)
            return f"Wait {duration_s} seconds"

        else:
            return f"{action_type}"

    @pyqtSlot(int)
    def set_current_step(self, step_number: int) -> None:
        """
        Highlight current step (called by protocol engine).

        Args:
            step_number: 0-based step index
        """
        if not self.protocol_loaded or step_number < 0 or step_number >= len(self.steps):
            return

        # Unhighlight previous step
        if 0 <= self.current_step_index < self.step_list.count():
            prev_item = self.step_list.item(self.current_step_index)
            prev_item.setBackground(QColor(Colors.PANEL))
            prev_item.setText(f"  Step {self.current_step_index+1}: {self.steps[self.current_step_index]}")

        # Highlight current step
        self.current_step_index = step_number
        item = self.step_list.item(step_number)
        item.setBackground(QColor(Colors.SAFE))  # Green highlight
        item.setText(f"> Step {step_number+1}: {self.steps[step_number]}")  # Arrow prefix

        # Scroll to make current step visible
        self.step_list.scrollToItem(item, QListWidget.ScrollHint.PositionAtCenter)

        # Enable control buttons during execution
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        logger.debug(f"Current step highlighted: {step_number+1}/{len(self.steps)}")

    @pyqtSlot(int)
    def mark_step_complete(self, step_number: int) -> None:
        """
        Mark step as completed (checkmark + dark green background).

        Args:
            step_number: 0-based step index
        """
        if not self.protocol_loaded or step_number < 0 or step_number >= len(self.steps):
            return

        item = self.step_list.item(step_number)
        item.setBackground(QColor("#1B5E20"))  # Dark green
        item.setText(f"✓ Step {step_number+1}: {self.steps[step_number]}")  # Checkmark

        logger.debug(f"Step marked complete: {step_number+1}/{len(self.steps)}")

    def reset_display(self) -> None:
        """Reset display (clear highlighting, disable buttons)."""
        # Reset all items to default
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            item.setBackground(QColor(Colors.PANEL))
            item.setText(f"  Step {i+1}: {self.steps[i]}")

        self.current_step_index = -1
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        logger.info("Protocol steps display reset")

    @pyqtSlot()
    def _on_pause_clicked(self) -> None:
        """Handle pause button click."""
        logger.info("Pause button clicked")
        self.pause_requested.emit()

    @pyqtSlot()
    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        logger.info("Stop button clicked")
        self.stop_requested.emit()
        self.reset_display()

    def cleanup(self) -> None:
        """Cleanup widget resources."""
        self.step_list.clear()
        self.steps = []
        logger.info("ProtocolStepsDisplayWidget cleanup complete")
