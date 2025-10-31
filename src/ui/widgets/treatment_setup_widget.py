"""
Treatment Setup Widget - Interactive configuration before treatment execution.

This widget provides full control over treatment parameters, protocol selection,
and hardware configuration. Used for building/planning treatments before execution.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.protocol import Protocol

# Hardware widgets removed - now in Hardware & Diagnostics and Protocol Builder tabs
# This widget is protocol-centric

logger = logging.getLogger(__name__)


class TreatmentSetupWidget(QWidget):
    """
    Treatment setup and configuration panel.

    Provides interactive controls for:
    - Protocol selection/configuration
    - Laser power settings
    - Actuator position settings
    - Smoothing motor configuration
    - Treatment parameter validation

    This is the "building" interface - all controls are active and editable.
    No camera feed needed (camera alignment done in Setup tab).
    """

    def __init__(self) -> None:
        super().__init__()
        self.dev_mode = False
        self.loaded_protocol: Optional[Protocol] = None

        # Hardware control widgets removed - now in Hardware & Diagnostics tab
        # This widget is protocol-centric: Load protocol → Validate → Execute

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components - protocol-centric layout."""
        # Vertical layout for protocol selector + validation
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Constrain maximum width to prevent excessive horizontal stretching
        self.setMaximumWidth(600)

        # Header
        header = QLabel("📋 Protocol-Based Treatment Configuration")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px; "
            "background-color: #424242; color: #81C784; border-radius: 3px;"
        )
        main_layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "1. Connect hardware in 'Hardware & Diagnostics' tab\n"
            "2. Load protocol below\n"
            "3. Start treatment when ready"
        )
        instructions.setStyleSheet("color: #888; font-size: 11px; padding: 10px;")
        main_layout.addWidget(instructions)

        # Protocol selector
        protocol_group = self._create_protocol_selector()
        main_layout.addWidget(protocol_group)

        # Validation section
        validation_group = self._create_validation_section()
        main_layout.addWidget(validation_group)

        main_layout.addStretch()

    def _create_protocol_selector(self) -> QGroupBox:
        """Create protocol selection section."""
        group = QGroupBox("Protocol")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Protocol selector button
        self.protocol_btn = QPushButton("📄 Load Protocol...")
        self.protocol_btn.setMinimumHeight(35)
        self.protocol_btn.setToolTip("Select treatment protocol file (.json)")
        self.protocol_btn.clicked.connect(self._on_load_protocol_clicked)
        layout.addWidget(self.protocol_btn)

        # Protocol name display
        self.protocol_name_label = QLabel("No protocol loaded")
        self.protocol_name_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        layout.addWidget(self.protocol_name_label)

        # Protocol info display (action count, estimated time)
        self.protocol_info_label = QLabel("")
        self.protocol_info_label.setStyleSheet("color: #888; font-size: 11px; padding: 2px;")
        layout.addWidget(self.protocol_info_label)

        group.setLayout(layout)
        return group

    def _create_validation_section(self) -> QGroupBox:
        """Create treatment validation section."""
        group = QGroupBox("Ready Check")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Compact validation checklist
        self.validation_label = QLabel(
            "# [DONE] Protocol\n" "# [DONE] Laser\n" "# [DONE] Actuator\n" "# [DONE] Motor\n" "⚠ Session"
        )
        self.validation_label.setStyleSheet(
            "font-family: monospace; font-size: 11px; padding: 5px;"
        )
        layout.addWidget(self.validation_label)

        # Ready to execute button (compact)
        self.ready_button = QPushButton("▶ Start Treatment")
        self.ready_button.setMinimumHeight(40)
        self.ready_button.setEnabled(False)
        self.ready_button.setStyleSheet(
            "font-size: 13px; font-weight: bold; " "background-color: #2196F3; color: white;"
        )
        self.ready_button.setToolTip(
            "Begin treatment execution - transitions to Active monitoring view"
        )
        layout.addWidget(self.ready_button)

        group.setLayout(layout)
        return group

    def set_dev_mode(self, dev_mode: bool) -> None:
        """
        Enable/disable developer mode.

        Args:
            dev_mode: True to enable dev mode
        """
        self.dev_mode = dev_mode
        logger.info(f"Treatment setup widget dev mode: {dev_mode}")
        # Hardware widgets removed - no child widgets to propagate to

    def _on_load_protocol_clicked(self) -> None:
        """Handle protocol load button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Protocol File",
            str(Path.home()),
            "Protocol Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                protocol_data = json.load(f)

            protocol = Protocol.from_dict(protocol_data)
            self.loaded_protocol = protocol

            self.protocol_name_label.setText(f"# [DONE] {protocol.protocol_name}")
            self.protocol_name_label.setStyleSheet(
                "color: #4CAF50; font-size: 11px; font-weight: bold; padding: 5px;"
            )

            action_count = len(protocol.actions)
            self.protocol_info_label.setText(f"{action_count} actions loaded")

            logger.info(f"Protocol loaded: {protocol.protocol_name} ({action_count} actions)")

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Invalid JSON: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load protocol: {e}")
            logger.error(f"Protocol load error: {e}")

    def cleanup(self) -> None:
        """Cleanup resources."""
        # Hardware widgets removed - no cleanup needed
        pass
