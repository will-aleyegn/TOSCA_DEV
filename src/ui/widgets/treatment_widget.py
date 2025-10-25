"""
Treatment control widget.
"""

import logging
from typing import Any, Optional

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.widgets.actuator_widget import ActuatorWidget
from ui.widgets.laser_widget import LaserWidget

logger = logging.getLogger(__name__)


class TreatmentWidget(QWidget):
    """
    Treatment control panel.

    Controls:
    - Laser power
    - Ring size (actuator position)
    - Treatment start/stop
    - Real-time monitoring
    """

    def __init__(self) -> None:
        super().__init__()
        self.dev_mode = False
        self.protocol_engine: Optional[Any] = None
        self.actuator_widget: ActuatorWidget = ActuatorWidget()
        self.laser_widget: LaserWidget = LaserWidget()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()  # Horizontal layout for side-by-side controls
        self.setLayout(layout)

        # Left side: Laser controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.laser_widget)
        left_layout.addStretch()

        # Middle: Treatment controls
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self._create_treatment_control())
        middle_layout.addStretch()

        # Right side: Actuator controls
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.actuator_widget)

        # Add to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(middle_layout, 1)
        layout.addLayout(right_layout, 1)

    def _create_treatment_control(self) -> QGroupBox:
        """Create treatment start/stop controls."""
        group = QGroupBox("Treatment Control")
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("START TREATMENT")
        self.start_button.setEnabled(False)
        self.start_button.setMinimumHeight(60)
        self.start_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; background-color: #4CAF50; color: white;"
        )
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("STOP TREATMENT")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; background-color: #f44336; color: white;"
        )
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel("Status: Ready - No Active Session")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        group.setLayout(layout)
        return group

    def set_dev_mode(self, dev_mode: bool) -> None:
        """
        Enable/disable developer mode.

        In dev mode, treatment controls are enabled without requiring an active session.

        Args:
            dev_mode: True to enable dev mode, False to disable
        """
        self.dev_mode = dev_mode
        logger.info(f"Treatment widget dev mode: {dev_mode}")

        if dev_mode:
            # Enable treatment controls in dev mode
            self.start_button.setEnabled(True)
            self.status_label.setText("Status: Developer Mode - Session Optional")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px; color: orange;")
        else:
            self.start_button.setEnabled(False)
            self.status_label.setText("Status: Ready - No Active Session")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")

    def set_protocol_engine(self, protocol_engine: Any) -> None:
        """
        Set the protocol engine for treatment execution.

        Args:
            protocol_engine: ProtocolEngine instance for executing treatment protocols
        """
        self.protocol_engine = protocol_engine
        logger.info("Protocol engine connected to treatment widget")

        # TODO: Connect START/STOP buttons to protocol execution
        # For now, just log that protocol engine is available
        if self.protocol_engine:
            logger.info("Protocol engine ready for treatment execution")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.actuator_widget:
            self.actuator_widget.cleanup()
        if self.laser_widget:
            self.laser_widget.cleanup()
