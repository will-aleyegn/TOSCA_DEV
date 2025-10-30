"""
Actuator control widget for the TOSCA GUI.

Provides actuator control interface for hardware connection and status monitoring.
NOTE: Sequence building UI removed - use ProtocolBuilderWidget for treatment protocols.
"""

import logging
from typing import Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.hardware.actuator_controller import ActuatorController

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

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Constrain maximum width to prevent excessive horizontal stretching
        self.setMaximumWidth(900)

        # Connection controls
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Status display
        status_group = self._create_status_group()
        layout.addWidget(status_group)

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
    def _on_connect_clicked(self, com_port: str = "COM3") -> None:
        """Handle connect button click."""
        logger.info(f"Connecting to actuator on {com_port}...")

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
        success = self.controller.connect(com_port, auto_home=False)

        if not success:
            logger.error(f"Failed to connect to actuator on {com_port}")
            self.connection_status_label.setText(f"Status: Connection failed ({com_port})")

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

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
