"""
Actuator connection and homing widget for Hardware & Diagnostics tab.

Provides compact hardware setup interface without sequence building.
"""

import json
import logging
from pathlib import Path

import serial.tools.list_ports
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

# Preferences file location
PREFERENCES_FILE = Path("data/hardware_preferences.json")


class ActuatorConnectionWidget(QWidget):
    """
    Compact actuator connection and homing widget for hardware setup.

    Provides connection, homing, and status display without sequence building.
    Manages ActuatorController lifecycle and hardware communication.
    """

    def __init__(self, controller=None) -> None:
        super().__init__()

        # Reference to ActuatorController (created and managed by MainWindow)
        self.controller = controller

        # State tracking (mirrors controller state for UI updates)
        self.is_connected = False
        self.is_homed = False
        self.current_position_um = 0.0
        self.max_position_um = 90000.0  # Default 90mm range

        # Initialize UI
        self._init_ui()

        # Connect to controller signals if controller provided
        if self.controller:
            self._connect_controller_signals()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Constrain maximum width to prevent excessive horizontal stretching
        # Increased from 600 to accommodate 2-row button layout
        self.setMaximumWidth(700)

        # Connection controls
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Status display
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        layout.addStretch()

        # Initial state
        self._update_ui_state()

    def _load_preferences(self) -> dict:
        """Load hardware preferences from file."""
        try:
            if PREFERENCES_FILE.exists():
                with open(PREFERENCES_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load preferences: {e}")
        return {}

    def _save_preference(self, key: str, value: str) -> None:
        """Save a preference to file."""
        try:
            prefs = self._load_preferences()
            prefs[key] = value
            PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(PREFERENCES_FILE, "w") as f:
                json.dump(prefs, f, indent=2)
            logger.info(f"Saved preference: {key} = {value}")
        except Exception as e:
            logger.error(f"Could not save preference: {e}")

    def _get_available_ports(self) -> list[tuple[str, bool]]:
        """Get list of COM ports with availability status."""
        available_ports = {p.device for p in serial.tools.list_ports.comports()}
        all_ports = [f"COM{i}" for i in range(1, 21)]
        return [(port, port in available_ports) for port in all_ports]

    def _refresh_port_list(self) -> None:
        """Refresh the COM port dropdown with current available ports."""
        current_port = self.com_port_combo.currentData()
        self.com_port_combo.clear()
        ports_with_status = self._get_available_ports()
        for port, is_available in ports_with_status:
            if is_available:
                self.com_port_combo.addItem(f"✓ {port}", userData=port)
            else:
                self.com_port_combo.addItem(f"  {port}", userData=port)
        if current_port:
            for i in range(self.com_port_combo.count()):
                if self.com_port_combo.itemData(i) == current_port:
                    self.com_port_combo.setCurrentIndex(i)
                    break
        logger.info(
            f"Refreshed port list: {sum(1 for _, avail in ports_with_status if avail)} available"
        )

    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        logger.info("Refreshing COM port list...")
        self._refresh_port_list()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection & Homing")
        main_layout = QVBoxLayout()

        # Row 1: Port selection and connection controls
        row1_layout = QHBoxLayout()

        # COM Port label
        port_label = QLabel("Port:")
        row1_layout.addWidget(port_label)

        # COM Port selection
        self.com_port_combo = QComboBox()
        self.com_port_combo.setFixedWidth(150)  # Wider for ✓ indicator
        self.com_port_combo.setToolTip(
            "Select COM port for Actuator\n✓ = Port detected and available"
        )
        row1_layout.addWidget(self.com_port_combo)

        # Refresh button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(32)
        self.refresh_btn.setToolTip("Refresh available COM ports")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        row1_layout.addWidget(self.refresh_btn)

        # Initial port population with detection
        self._refresh_port_list()

        # Set default from saved preference, or use COM3
        prefs = self._load_preferences()
        saved_port = prefs.get("actuator_com_port", "COM3")
        for i in range(self.com_port_combo.count()):
            if self.com_port_combo.itemData(i) == saved_port:
                self.com_port_combo.setCurrentIndex(i)
                logger.info(f"Loaded saved Actuator port: {saved_port}")
                break

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(100)
        self.connect_btn.setMinimumHeight(32)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        row1_layout.addWidget(self.connect_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(100)
        self.disconnect_btn.setMinimumHeight(32)
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        row1_layout.addWidget(self.disconnect_btn)

        row1_layout.addStretch()  # Push controls to left
        main_layout.addLayout(row1_layout)

        # Row 2: Homing and diagnostic controls
        row2_layout = QHBoxLayout()

        # Home button
        self.home_btn = QPushButton("Find Home")
        self.home_btn.setFixedWidth(120)
        self.home_btn.setMinimumHeight(32)
        self.home_btn.clicked.connect(self._on_home_clicked)
        self.home_btn.setEnabled(False)
        row2_layout.addWidget(self.home_btn)

        # Query Settings button - for verifying device-stored settings
        self.query_settings_btn = QPushButton("Query Settings")
        self.query_settings_btn.setFixedWidth(120)
        self.query_settings_btn.setMinimumHeight(32)
        self.query_settings_btn.setToolTip(
            "Query device-stored settings\n(Best used after homing completes)"
        )
        self.query_settings_btn.clicked.connect(self._on_query_settings_clicked)
        self.query_settings_btn.setEnabled(False)
        row2_layout.addWidget(self.query_settings_btn)

        row2_layout.addStretch()  # Push controls to left
        main_layout.addLayout(row2_layout)

        group.setLayout(main_layout)
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

    def _connect_controller_signals(self) -> None:
        """Connect to controller signals."""
        if not self.controller:
            logger.warning("No controller available to connect signals")
            return

        # Connect to controller signals (use try/except to avoid double-connection errors)
        try:
            self.controller.connection_changed.connect(self._on_connection_changed)
            self.controller.homing_progress.connect(self._on_homing_progress)
            self.controller.status_changed.connect(self._on_status_changed)
            self.controller.position_changed.connect(self._on_position_changed)
            self.controller.limits_changed.connect(self._on_limits_changed)

            # Update state from controller
            self.is_connected = self.controller.is_connected
            self.is_homed = self.controller.is_homed

            # Get initial position from controller (returns None if not available)
            position = self.controller.get_position()
            if position is not None:
                self.current_position_um = position

            self._update_ui_state()

            logger.info("ActuatorConnectionWidget connected to controller signals")
        except RuntimeError as e:
            # Signals already connected
            logger.debug(f"Signals already connected: {e}")

    def _on_connect_clicked(self) -> None:
        """Handle connect button click - connects to actuator hardware."""
        if not self.controller:
            logger.error("No ActuatorController available - cannot connect")
            QMessageBox.warning(
                self,
                "Controller Error",
                "Actuator controller not initialized. Please restart the application.",
            )
            return

        # Get selected COM port (from userData to remove ✓ indicator)
        selected_port = self.com_port_combo.currentData()
        if not selected_port:
            # Fallback to text if userData not set
            selected_port = self.com_port_combo.currentText().replace("✓ ", "").strip()

        # Save this port as preference for next time
        self._save_preference("actuator_com_port", selected_port)

        logger.info(f"Connecting to actuator on {selected_port}...")

        # Connect without auto-homing (user must click Find Home button)
        success = self.controller.connect(selected_port, auto_home=False)

        if not success:
            logger.error(f"Failed to connect to actuator on {selected_port}")
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Failed to connect to actuator on {selected_port}.\n\n"
                f"Please check:\n"
                f"- Device is powered on\n"
                f"- Correct COM port selected\n"
                f"- USB cable is connected",
            )

    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click - disconnects from actuator hardware."""
        if not self.controller:
            return

        logger.info("Disconnecting from actuator...")
        self.controller.disconnect()

    def _on_home_clicked(self) -> None:
        """Handle home button click - initiates homing sequence."""
        if not self.controller:
            logger.error("No controller available for homing")
            return

        logger.info("Starting homing sequence from Hardware tab...")
        self.controller.find_index()

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        self._update_ui_state()

        # Notify main window status bar (if available)
        main_window = self.window()
        if main_window and hasattr(main_window, "update_actuator_status"):
            main_window.update_actuator_status(connected)
            logger.info(f"Actuator status bar updated: {'connected' if connected else 'disconnected'}")

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
            # Query settings enabled when connected (best after homing)
            self.query_settings_btn.setEnabled(True)
        else:
            self.connection_status_label.setText("Disconnected")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: #f44336;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.home_btn.setEnabled(False)
            self.query_settings_btn.setEnabled(False)

        # Homing status
        if self.is_homed:
            self.homing_status_label.setText("Homed")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        else:
            self.homing_status_label.setText("Not Homed")
            self.homing_status_label.setStyleSheet("font-weight: bold; color: #f44336;")

    def _on_query_settings_clicked(self) -> None:
        """Handle query settings button click - queries and displays device settings."""
        if not self.controller:
            QMessageBox.warning(
                self,
                "Not Connected",
                "Actuator must be connected to query settings.",
            )
            return

        logger.info("Querying device settings...")
        settings = self.controller.query_device_settings()

        # Check for errors
        if "error" in settings:
            QMessageBox.critical(
                self,
                "Query Failed",
                f"Failed to query device settings:\n\n{settings['error']}",
            )
            return

        # Format and display settings
        message, title, icon = self._format_settings_display(settings)
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _format_settings_display(self, settings: dict) -> tuple[str, str, QMessageBox.Icon]:
        """Format settings data for display.

        Args:
            settings: Dictionary containing device settings

        Returns:
            Tuple of (message, title, icon) for QMessageBox
        """
        available_count = settings.get("available_count", 0)
        total_queried = settings.get("total_queried", 0)

        if available_count == 0:
            return self._format_no_settings_message()

        return self._format_available_settings(settings, available_count, total_queried)

    def _format_no_settings_message(self) -> tuple[str, str, QMessageBox.Icon]:
        """Format message when no settings are available."""
        message = (
            "No device settings available\n\n"
            "This is expected if:\n"
            "- Device is still initializing\n"
            "- settings_default.txt is missing (intentional for TOSCA)\n"
            "- Settings haven't been sent by device yet\n\n"
            "The system is using conservative defaults:\n"
            "- LLIM = -45000 µm\n"
            "- HLIM = 45000 µm\n"
            "- ACCE/DECE = 65500\n\n"
            "Try again after homing completes or device has more time to initialize."
        )
        return (message, "No Settings Available", QMessageBox.Icon.Warning)

    def _format_available_settings(
        self, settings: dict, available_count: int, total_queried: int
    ) -> tuple[str, str, QMessageBox.Icon]:
        """Format available settings for display."""
        lines = [f"Retrieved {available_count}/{total_queried} device settings\n"]

        # Position limits
        lines.append("Position Limits:")
        self._add_setting_line(lines, settings, "LLIM", "Low Limit", " µm")
        self._add_setting_line(lines, settings, "HLIM", "High Limit", " µm")

        # Speed and motion
        lines.append("\nSpeed & Motion:")
        self._add_setting_line(lines, settings, "SSPD", "Speed", " µm/s")
        self._add_setting_line(lines, settings, "ACCE", "Acceleration", "")
        self._add_setting_line(lines, settings, "DECE", "Deceleration", "")

        # Tolerances
        lines.append("\nPosition Tolerances:")
        self._add_setting_line(lines, settings, "PTOL", "Primary", " encoder units")
        self._add_setting_line(lines, settings, "PTO2", "Secondary", " encoder units")
        self._add_setting_line(lines, settings, "TOUT", "Timeout", " ms")

        # Error limit
        lines.append("\nError Limits:")
        self._add_setting_line(lines, settings, "ELIM", "Error Limit", "")

        lines.append("\nDevice-stored settings (manufacturer-calibrated)")

        return ("\n".join(lines), "Device Settings", QMessageBox.Icon.Information)

    def _add_setting_line(
        self, lines: list, settings: dict, key: str, label: str, unit: str
    ) -> None:
        """Add a setting line to the display list.

        Args:
            lines: List to append formatted line to
            settings: Settings dictionary
            key: Setting key to look up
            label: Human-readable label
            unit: Unit suffix (e.g., ' µm', ' ms')
        """
        value = settings.get(key)
        if value:
            lines.append(f"  {key} ({label}) = {value}{unit}")
        else:
            lines.append(f"  {key} ({label}) = Not available")

    @pyqtSlot(float, float)
    def _on_limits_changed(self, low_limit_um: float, high_limit_um: float) -> None:
        """Handle actuator limits change."""
        logger.info(f"Actuator limits updated: {low_limit_um:.0f} to {high_limit_um:.0f} µm")
        self.max_position_um = high_limit_um

    def cleanup(self) -> None:
        """Cleanup resources - disconnect controller if connected."""
        if self.controller and self.is_connected:
            logger.info("ActuatorConnectionWidget cleanup: disconnecting controller")
            self.controller.disconnect()
