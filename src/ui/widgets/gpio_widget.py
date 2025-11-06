"""
GPIO safety interlock widget for the TOSCA GUI.

Provides safety monitoring interface for laser spot smoothing module and photodiode laser pickoff measurement.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import serial.tools.list_ports
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.config_loader import get_config
from hardware.gpio_controller import GPIOController
from ui.constants import WIDGET_WIDTH_GRID
from ui.design_tokens import ButtonSizes, Colors

logger = logging.getLogger(__name__)

# Preferences file location
PREFERENCES_FILE = Path("data/hardware_preferences.json")


class GPIOWidget(QWidget):
    """
    GPIO safety monitoring widget with connection and status displays.
    """

    # Signal emitted when GPIO controller connection status changes
    # Emitted AFTER controller is created and connected
    gpio_connection_changed = pyqtSignal(bool)

    def __init__(self, controller: Optional[GPIOController] = None) -> None:
        super().__init__()

        # Reference to GPIOController (created and managed by MainWindow)
        self.controller = controller

        # State tracking
        self.is_connected = False
        self.safety_ok = False

        # Initialize UI
        self._init_ui()

        # Connect to controller signals if controller provided
        if self.controller:
            self._connect_controller_signals()

    def _connect_controller_signals(self) -> None:
        """Connect to controller signals (called when controller is injected)."""
        if not self.controller:
            return

        self.controller.connection_changed.connect(self._on_connection_changed)
        self.controller.safety_interlock_changed.connect(self._on_safety_changed)
        self.controller.error_occurred.connect(self._on_error)
        logger.debug("GPIOWidget signals connected to GPIOController")

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)  # Consistent spacing between sections

        # Constrain maximum width for 4-column grid layout
        self.setMaximumWidth(WIDGET_WIDTH_GRID)

        # (1) GPIO Connection - Connect first to enable downstream systems
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Dependency indicator - shows what GPIO enables
        dependency_label = QLabel("       ↓  ↓  ↓")
        dependency_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #666; padding: 0px;"
        )
        layout.addWidget(dependency_label)

        # Note: GPIO enables aiming laser, smoothing motor, and photodiode monitor
        # Overall safety status is shown in right-side Safety Panel

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
            # Load existing preferences
            prefs = self._load_preferences()
            prefs[key] = value

            # Ensure data directory exists
            PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Save preferences
            with open(PREFERENCES_FILE, "w") as f:
                json.dump(prefs, f, indent=2)
            logger.info(f"Saved preference: {key} = {value}")
        except Exception as e:
            logger.error(f"Could not save preference: {e}")

    def _get_available_ports(self) -> list[tuple[str, bool]]:
        """
        Get list of COM ports with availability status.

        Returns:
            List of (port_name, is_available) tuples
        """
        available_ports = {p.device for p in serial.tools.list_ports.comports()}
        all_ports = [f"COM{i}" for i in range(1, 21)]
        return [(port, port in available_ports) for port in all_ports]

    def _refresh_port_list(self) -> None:
        """Refresh the COM port dropdown with current available ports."""
        current_port = self.com_port_combo.currentText()

        # Clear and repopulate
        self.com_port_combo.clear()

        ports_with_status = self._get_available_ports()
        for port, is_available in ports_with_status:
            if is_available:
                # Add with # [DONE] indicator for available ports
                self.com_port_combo.addItem(f"# [DONE] {port}", userData=port)
            else:
                # Add without indicator for unavailable ports (grayed out)
                self.com_port_combo.addItem(f"  {port}", userData=port)

        # Restore previous selection if possible
        for i in range(self.com_port_combo.count()):
            port_data = self.com_port_combo.itemData(i)
            if port_data == current_port:
                self.com_port_combo.setCurrentIndex(i)
                break

        logger.info(
            f"Refreshed port list: {sum(1 for _, avail in ports_with_status if avail)} available"
        )

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("(1) GPIO CONNECTION (Arduino)  CONNECT FIRST")
        layout = QHBoxLayout()
        layout.setSpacing(8)  # Consistent spacing between controls

        # COM Port label
        port_label = QLabel("Port:")
        layout.addWidget(port_label)

        # COM Port selection
        self.com_port_combo = QComboBox()
        self.com_port_combo.setFixedWidth(150)  # Wider for # [DONE] indicator
        self.com_port_combo.setToolTip(
            "Select COM port for Arduino\n# [DONE] = Port detected and available"
        )
        layout.addWidget(self.com_port_combo)

        # Refresh button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(32)
        self.refresh_btn.setToolTip("Refresh available COM ports")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(self.refresh_btn)

        # Initial port population with detection
        self._refresh_port_list()

        # Set default from saved preference, or config, or first available
        prefs = self._load_preferences()
        saved_port = prefs.get("gpio_com_port")

        if saved_port:
            # Use saved preference
            for i in range(self.com_port_combo.count()):
                if self.com_port_combo.itemData(i) == saved_port:
                    self.com_port_combo.setCurrentIndex(i)
                    logger.info(f"Loaded saved GPIO port: {saved_port}")
                    break
        else:
            # Use config default
            config = get_config()
            default_port = config.hardware.gpio.com_port
            for i in range(self.com_port_combo.count()):
                if self.com_port_combo.itemData(i) == default_port:
                    self.com_port_combo.setCurrentIndex(i)
                    break

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.connect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(90)  # Secondary action width (grid layout)
        self.disconnect_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)

        # Status label
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet(f"font-weight: bold; color: {Colors.DANGER};")
        layout.addWidget(self.connection_status_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    # Note: Removed _create_safety_group() method (was empty group with redirect label)
    # Overall safety status is authoritatively displayed in right-side Safety Panel

    def connect_device(self) -> bool:
        """
        Public method to programmatically connect to GPIO.

        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            logger.warning("GPIO already connected")
            return True

        self._on_connect_clicked()
        return self.is_connected

    def disconnect_device(self) -> None:
        """Public method to programmatically disconnect from GPIO."""
        if not self.is_connected:
            logger.debug("GPIO already disconnected")
            return

        self._on_disconnect_clicked()

    def _update_ui_state(self) -> None:
        """Update UI element states based on connection status."""
        # Connection buttons
        self.connect_btn.setEnabled(not self.is_connected)
        self.disconnect_btn.setEnabled(self.is_connected)

    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        logger.info("Refreshing COM port list...")
        self._refresh_port_list()

    @pyqtSlot()
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        # Get selected COM port (from userData to remove # [DONE] indicator)
        selected_port = self.com_port_combo.currentData()
        if not selected_port:
            # Fallback to text if userData not set
            selected_port = self.com_port_combo.currentText().replace("# [DONE] ", "").strip()

        logger.info(f"Connecting to GPIO on {selected_port}...")

        # Save this port as preference for next time
        self._save_preference("gpio_com_port", selected_port)

        if not self.controller:
            error_msg = (
                "Software Error: GPIO controller not initialized. "
                "This indicates a configuration issue. "
                "Please restart the application."
            )
            logger.error(f"GPIOWidget: No controller available (DI not configured properly)")
            self.connection_status_label.setText("Error: No controller")
            return

        # Connect to GPIO using selected COM port
        logger.info(f"Attempting to connect to Arduino on {selected_port}")
        success = self.controller.connect(port=selected_port)

        if not success:
            error_msg = (
                f"Failed to connect to GPIO Arduino on {selected_port}. "
                f"Check: (1) Arduino is powered/connected, "
                f"(2) Correct COM port selected, "
                f"(3) No other app using port, "
                f"(4) Arduino has safety firmware loaded"
            )
            logger.error(error_msg)
            self.connection_status_label.setText(f"Connection failed - check device")

    @pyqtSlot()
    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        if self.controller:
            logger.info("Disconnecting from GPIO...")
            self.controller.disconnect()

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection status change."""
        self.is_connected = connected
        status_text = "Connected" if connected else "Disconnected"
        self.connection_status_label.setText(status_text)
        self.connection_status_label.setStyleSheet(
            f"font-weight: bold; color: {Colors.SAFE if connected else Colors.DANGER};"
        )
        logger.info(f"GPIO connection status: {status_text}")
        self._update_ui_state()

        # Emit signal to notify other components (e.g., main window for watchdog)
        self.gpio_connection_changed.emit(connected)

    @pyqtSlot(bool)
    def _on_safety_changed(self, safety_ok: bool) -> None:
        """Handle safety interlock status change.

        Note: Removed redundant safety status banner update.
        Overall safety status is shown in right-side Safety Panel (T4).
        This widget focuses on individual GPIO diagnostic states.
        """
        self.safety_ok = safety_ok
        # Safety status tracking only - Safety Panel (T4) displays overall status

    @pyqtSlot(str)
    def _on_error(self, error_msg: str) -> None:
        """Handle error from controller."""
        logger.error(f"GPIO error: {error_msg}")
        # Update UI to show error to user
        self.connection_status_label.setText(f"Error: {error_msg}")
        self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
