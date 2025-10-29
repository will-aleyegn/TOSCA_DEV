"""
Actuator connection and homing widget for Hardware & Diagnostics tab.

Provides compact hardware setup interface without sequence building.
"""

import logging

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class ActuatorConnectionWidget(QWidget):
    """
    Compact actuator connection and homing widget for hardware setup.

    Provides connection, homing, and status display without sequence building.
    Controller is shared with full ActuatorWidget in Protocol Builder tab.
    """

    def __init__(self, actuator_widget=None) -> None:
        super().__init__()

        # Reference to ActuatorWidget (for shared controller access)
        self.actuator_widget = actuator_widget

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
        self.setMaximumWidth(600)

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

        # COM Port label
        port_label = QLabel("Port:")
        layout.addWidget(port_label)

        # COM Port selection
        self.com_port_combo = QComboBox()
        self.com_port_combo.setFixedWidth(100)
        # Populate with common Windows COM ports
        for i in range(1, 21):
            self.com_port_combo.addItem(f"COM{i}")
        # Set default to COM3 (from config.yaml: actuator is on COM3)
        index = self.com_port_combo.findText("COM3")
        if index >= 0:
            self.com_port_combo.setCurrentIndex(index)
        layout.addWidget(self.com_port_combo)

        # Connect button - fixed width for compact layout
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(120)
        self.connect_btn.setMinimumHeight(32)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Home button - fixed width for compact layout
        self.home_btn = QPushButton("Find Home")
        self.home_btn.setFixedWidth(120)
        self.home_btn.setMinimumHeight(32)
        self.home_btn.clicked.connect(self._on_home_clicked)
        self.home_btn.setEnabled(False)
        layout.addWidget(self.home_btn)

        # Disconnect button - fixed width for compact layout
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(120)
        self.disconnect_btn.setMinimumHeight(32)
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)

        layout.addStretch()  # Push buttons to left, leave right space empty

        group.setLayout(layout)
        return group

    def _create_status_group(self) -> QGroupBox:
        """Create status display group."""
        group = QGroupBox("Status")
        layout = QGridLayout()

        # Row 1: Connection and Homing
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        layout.addWidget(QLabel("Connection:"), 0, 0)
        layout.addWidget(self.connection_status_label, 0, 1)

        self.homing_status_label = QLabel("Not Homed")
        self.homing_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        layout.addWidget(QLabel("Homed:"), 0, 2)
        layout.addWidget(self.homing_status_label, 0, 3)

        # Row 2: Position
        self.position_label = QLabel("-- μm")
        self.position_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Position:"), 1, 0)
        layout.addWidget(self.position_label, 1, 1)

        # Row 3: Motion status
        self.motion_status_label = QLabel("Idle")
        self.motion_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(QLabel("Motion:"), 1, 2)
        layout.addWidget(self.motion_status_label, 1, 3)

        group.setLayout(layout)
        return group

    def connect_signals(self) -> None:
        """Connect to shared controller signals (called after controller is created)."""
        if not self.actuator_widget or not self.actuator_widget.controller:
            return

        controller = self.actuator_widget.controller

        # Connect to controller signals (use try/except to avoid double-connection errors)
        try:
            controller.connection_changed.connect(self._on_connection_changed)
            controller.homing_progress.connect(self._on_homing_progress)
            controller.status_changed.connect(self._on_status_changed)
            controller.position_changed.connect(self._on_position_changed)

            # Update state from controller
            self.is_connected = controller.is_connected
            self.is_homed = controller.is_homed
            self.current_position_um = controller.current_position_um
            self._update_ui_state()

            logger.info("ActuatorConnectionWidget connected to shared controller signals")
        except RuntimeError as e:
            # Signals already connected
            logger.debug(f"Signals already connected: {e}")

    def _on_connect_clicked(self) -> None:
        """Handle connect button click - delegates to ActuatorWidget."""
        if not self.actuator_widget:
            logger.error("No ActuatorWidget reference - cannot connect")
            return

        # Get selected COM port
        selected_port = self.com_port_combo.currentText()

        # Trigger connect in the main ActuatorWidget (creates controller if needed)
        self.actuator_widget._on_connect_clicked(com_port=selected_port)

        # Connect our signals after controller is created
        self.connect_signals()

    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click - delegates to ActuatorWidget."""
        if not self.actuator_widget:
            return

        self.actuator_widget._on_disconnect_clicked()

    def _on_home_clicked(self) -> None:
        """Handle home button click - delegates to ActuatorWidget."""
        if not self.actuator_widget:
            return

        logger.info("Starting homing sequence from Hardware tab...")
        self.actuator_widget._on_home_clicked()

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        self._update_ui_state()

    @pyqtSlot(str)
    def _on_homing_progress(self, message: str) -> None:
        """Handle homing progress updates."""
        logger.info(f"Homing: {message}")
        # Check if homing is complete based on message
        if "complete" in message.lower():
            self.is_homed = True
            self._update_ui_state()

    @pyqtSlot(str)
    def _on_status_changed(self, status: str) -> None:
        """Handle status changes (ready, homing, moving, error)."""
        self.motion_status_label.setText(status.capitalize())

        # Color code based on status
        if "error" in status.lower():
            self.motion_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        elif status.lower() in ["homing", "moving"]:
            self.motion_status_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        elif status.lower() == "ready":
            self.motion_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        else:
            self.motion_status_label.setStyleSheet("font-weight: bold;")

    @pyqtSlot(float)
    def _on_position_changed(self, position_um: float) -> None:
        """Handle position update."""
        self.current_position_um = position_um
        self.position_label.setText(f"{position_um:.1f} μm")

    def _update_ui_state(self) -> None:
        """Update UI based on current state."""
        # Connection status
        if self.is_connected:
            self.connection_status_label.setText("Connected")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.home_btn.setEnabled(not self.is_homed)
        else:
            self.connection_status_label.setText("Disconnected")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.home_btn.setEnabled(False)

        # Homing status
        if self.is_homed:
            self.homing_status_label.setText("Homed")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        else:
            self.homing_status_label.setText("Not Homed")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #f44336;")

    def cleanup(self) -> None:
        """Cleanup resources (controller is shared, don't disconnect)."""
        # Don't disconnect - controller is shared with ActuatorWidget
        pass
