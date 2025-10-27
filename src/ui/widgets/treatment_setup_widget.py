"""
Treatment Setup Widget - Interactive configuration before treatment execution.

This widget provides full control over treatment parameters, protocol selection,
and hardware configuration. Used for building/planning treatments before execution.
"""

import logging
from typing import Any, Optional

from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.actuator_widget import ActuatorWidget
from ui.widgets.laser_widget import LaserWidget
from ui.widgets.motor_widget import MotorWidget

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

        # Hardware control widgets
        self.laser_widget: LaserWidget = LaserWidget()
        self.actuator_widget: ActuatorWidget = ActuatorWidget()
        self.motor_widget: MotorWidget = MotorWidget()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header
        header = QLabel("Treatment Configuration")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Protocol selector placeholder (Phase 3.1)
        protocol_group = self._create_protocol_selector()
        layout.addWidget(protocol_group)

        # Hardware configuration sections
        hardware_layout = QHBoxLayout()

        # Left: Laser configuration
        hardware_layout.addWidget(self.laser_widget, 1)

        # Middle: Actuator configuration
        hardware_layout.addWidget(self.actuator_widget, 1)

        # Right: Motor configuration
        hardware_layout.addWidget(self.motor_widget, 1)

        layout.addLayout(hardware_layout)

        # Validation and ready check
        validation_group = self._create_validation_section()
        layout.addWidget(validation_group)

        layout.addStretch()

    def _create_protocol_selector(self) -> QGroupBox:
        """Create protocol selection section."""
        group = QGroupBox("Protocol Selection")
        layout = QVBoxLayout()

        placeholder = QLabel(
            "Protocol Selector (Phase 3.1)\n\n"
            "• Load treatment protocol from file\n"
            "• Preview protocol actions\n"
            "• Validate protocol parameters"
        )
        placeholder.setStyleSheet("color: #666; padding: 20px;")
        layout.addWidget(placeholder)

        group.setLayout(layout)
        return group

    def _create_validation_section(self) -> QGroupBox:
        """Create treatment validation section."""
        group = QGroupBox("Treatment Validation")
        layout = QVBoxLayout()

        # Validation checklist
        self.validation_label = QLabel(
            "✓ Protocol loaded\n"
            "✓ Laser configured\n"
            "✓ Actuator ready\n"
            "✓ Motor operational\n"
            "⚠ Subject session required"
        )
        self.validation_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(self.validation_label)

        # Ready to execute button
        self.ready_button = QPushButton("Ready to Execute Treatment")
        self.ready_button.setMinimumHeight(50)
        self.ready_button.setEnabled(False)
        self.ready_button.setStyleSheet(
            "font-size: 14px; font-weight: bold; "
            "background-color: #2196F3; color: white;"
        )
        self.ready_button.setToolTip(
            "Switch to Active Treatment tab when all validations pass"
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

        # Pass to child widgets
        if hasattr(self.laser_widget, "set_dev_mode"):
            self.laser_widget.set_dev_mode(dev_mode)
        if hasattr(self.actuator_widget, "set_dev_mode"):
            self.actuator_widget.set_dev_mode(dev_mode)
        if hasattr(self.motor_widget, "set_dev_mode"):
            self.motor_widget.set_dev_mode(dev_mode)

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.laser_widget:
            self.laser_widget.cleanup()
        if self.actuator_widget:
            self.actuator_widget.cleanup()
