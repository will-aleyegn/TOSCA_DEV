"""
Footpedal Deadman Switch Widget
Project: TOSCA Laser Control System

Purpose: Display footpedal deadman switch status (D5 pin).
         Safety interlock - treatment laser requires footpedal pressed.

Safety Critical: Yes - Primary hardware safety interlock
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.constants import WIDGET_WIDTH_GRID
from ui.design_tokens import Colors


class FootpedalWidget(QWidget):
    """
    Footpedal deadman switch status display.

    Shows:
    - Connection status (GPIO online/offline)
    - Footpedal state (pressed/released)
    - Safety interlock status

    This is a display-only widget - footpedal is hardware input only.
    """

    def __init__(self, gpio_controller: Optional[object] = None, parent: Optional[QWidget] = None) -> None:
        """
        Initialize footpedal widget.

        Args:
            gpio_controller: GPIO controller instance (for signal connections)
            parent: Parent widget
        """
        super().__init__(parent)
        self.gpio_controller = gpio_controller
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Let grid layout control width (removed max width constraint for better horizontal space usage)
        # Main group box
        group = QGroupBox("FOOTPEDAL DEADMAN SWITCH (D5)")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {Colors.PANEL};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Colors.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Connection status
        self.status_label = QLabel("Status: ⚠️ Not Connected (GPIO offline)")
        self.status_label.setStyleSheet(
            f"font-size: 10pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
        )
        layout.addWidget(self.status_label)

        # Footpedal state (large, prominent)
        self.state_label = QLabel("State: ⚪ RELEASED")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 16px;
                font-size: 14pt;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.state_label)

        # Safety interlock status
        self.safety_label = QLabel("Safety: 🔒 Laser interlock ENGAGED")
        self.safety_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BG_ERROR};
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.safety_label)

        # Info text
        info_label = QLabel("Requires active press for laser operation")
        info_label.setStyleSheet(
            f"font-size: 9pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        group.setLayout(layout)

        # Main widget layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        """Connect GPIO controller signals."""
        if self.gpio_controller is not None:
            # Connection status
            if hasattr(self.gpio_controller, "connection_changed"):
                self.gpio_controller.connection_changed.connect(self._on_connection_changed)

            # Safety interlock status (includes footpedal state)
            if hasattr(self.gpio_controller, "safety_interlock_changed"):
                self.gpio_controller.safety_interlock_changed.connect(self._on_safety_interlock_changed)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """
        Handle GPIO connection status change.

        Args:
            connected: True if GPIO connected, False if disconnected
        """
        if connected:
            self.status_label.setText("Status: ✓ Connected")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.CONNECTED}; padding: 4px;"
            )
            # Default to released state when connected
            self._update_state(False)
        else:
            self.status_label.setText("Status: ⚠️ Not Connected (GPIO offline)")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
            )
            # Show unknown state when disconnected
            self.state_label.setText("State: ⚫ UNKNOWN")
            self.state_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BACKGROUND};
                    color: {Colors.TEXT_DISABLED};
                    border: 2px solid {Colors.BORDER_DEFAULT};
                    border-radius: 6px;
                    padding: 16px;
                    font-size: 14pt;
                    font-weight: bold;
                }}
            """
            )
            self.safety_label.setText("Safety: ⚫ UNKNOWN (GPIO offline)")
            self.safety_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BACKGROUND};
                    color: {Colors.TEXT_DISABLED};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )

    @pyqtSlot(bool)
    def _on_safety_interlock_changed(self, safe: bool) -> None:
        """
        Handle safety interlock status change (includes footpedal state).

        Args:
            safe: True if all interlocks satisfied (footpedal pressed), False otherwise
        """
        self._update_state(safe)

    def _update_state(self, pressed: bool) -> None:
        """
        Update footpedal state display.

        Args:
            pressed: True if footpedal pressed, False if released
        """
        if pressed:
            # Footpedal PRESSED - safety OK
            self.state_label.setText("State: 🟢 PRESSED")
            self.state_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_SUCCESS};
                    color: white;
                    border: 2px solid {Colors.SAFE};
                    border-radius: 6px;
                    padding: 16px;
                    font-size: 14pt;
                    font-weight: bold;
                }}
            """
            )
            self.safety_label.setText("Safety: ✓ Laser interlock RELEASED")
            self.safety_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_SUCCESS};
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )
        else:
            # Footpedal RELEASED - safety engaged
            self.state_label.setText("State: ⚪ RELEASED")
            self.state_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BACKGROUND};
                    color: {Colors.TEXT_PRIMARY};
                    border: 2px solid {Colors.BORDER_DEFAULT};
                    border-radius: 6px;
                    padding: 16px;
                    font-size: 14pt;
                    font-weight: bold;
                }}
            """
            )
            self.safety_label.setText("Safety: 🔒 Laser interlock ENGAGED")
            self.safety_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BG_ERROR};
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
            """
            )

    def cleanup(self) -> None:
        """Clean up resources (called on window close)."""
        # Disconnect signals if connected
        if self.gpio_controller is not None:
            try:
                if hasattr(self.gpio_controller, "connection_changed"):
                    self.gpio_controller.connection_changed.disconnect(self._on_connection_changed)
                if hasattr(self.gpio_controller, "safety_interlock_changed"):
                    self.gpio_controller.safety_interlock_changed.disconnect(
                        self._on_safety_interlock_changed
                    )
            except (RuntimeError, TypeError):
                pass  # Signals already disconnected
