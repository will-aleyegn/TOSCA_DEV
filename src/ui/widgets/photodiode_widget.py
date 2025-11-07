"""
Photodiode Power Monitor Widget
Project: TOSCA Laser Control System

Purpose: Display photodiode power monitor readings (A0 analog input).
         Shows voltage and calculated power from calibration curve.

Safety Critical: Yes - Monitors actual laser output power
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_tokens import ButtonSizes, Colors, Spacing


class PhotodiodeWidget(QWidget):
    """
    Photodiode laser power monitor display.

    Shows:
    - Connection status (GPIO online/offline)
    - Voltage reading from A0 (0-5V)
    - Calculated power from calibration curve
    - Calibration button (future feature)
    """

    def __init__(self, gpio_controller: Optional[object] = None, parent: Optional[QWidget] = None) -> None:
        """
        Initialize photodiode widget.

        Args:
            gpio_controller: GPIO controller instance (for signal connections)
            parent: Parent widget
        """
        super().__init__(parent)
        self.gpio_controller = gpio_controller
        self.is_connected = False
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Let grid layout control width (removed max width constraint for better horizontal space usage)

        # Main group box
        group = QGroupBox("PHOTODIODE MONITOR  (monitors laser)")
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

        # Voltage reading (large, prominent)
        self.voltage_label = QLabel("Voltage: 0.00 V")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: {Spacing.NORMAL}px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.voltage_label)

        # Range info
        range_label = QLabel("Range: 0.0-5.0 V")
        range_label.setStyleSheet(
            f"font-size: 9pt; color: {Colors.TEXT_SECONDARY}; padding: 2px;"
        )
        range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(range_label)

        # Calculated power
        self.power_label = QLabel("Power: 0.0 mW")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.power_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.WARNING};
                border: 2px solid {Colors.WARNING};
                border-radius: 6px;
                padding: {Spacing.NORMAL}px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.power_label)

        # Calibration info
        calib_label = QLabel("(from calibration curve)")
        calib_label.setStyleSheet(
            f"font-size: 9pt; color: {Colors.TEXT_SECONDARY}; padding: 2px;"
        )
        calib_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(calib_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Calibrate button
        self.calibrate_btn = QPushButton("📈 Calibrate")
        self.calibrate_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.calibrate_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.calibrate_btn.setEnabled(False)  # Disabled until GPIO connects
        self.calibrate_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.TREATING};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.calibrate_btn.setToolTip("Calibrate photodiode voltage-to-power curve")
        self.calibrate_btn.clicked.connect(self._on_calibrate_clicked)
        button_layout.addWidget(self.calibrate_btn)

        # View Curve button
        self.view_curve_btn = QPushButton("📋 View Curve")
        self.view_curve_btn.setFixedWidth(100)  # Primary action width (grid layout)
        self.view_curve_btn.setMinimumHeight(ButtonSizes.SECONDARY)  # 40px
        self.view_curve_btn.setEnabled(False)  # Disabled until GPIO connects
        self.view_curve_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.TEXT_SECONDARY};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_DISABLED};
            }}
        """
        )
        self.view_curve_btn.setToolTip("View calibration curve data")
        self.view_curve_btn.clicked.connect(self._on_view_curve_clicked)
        button_layout.addWidget(self.view_curve_btn)

        layout.addLayout(button_layout)

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

            # Voltage reading
            if hasattr(self.gpio_controller, "photodiode_voltage_changed"):
                self.gpio_controller.photodiode_voltage_changed.connect(
                    self._on_voltage_changed
                )

            # Power reading
            if hasattr(self.gpio_controller, "photodiode_power_changed"):
                self.gpio_controller.photodiode_power_changed.connect(self._on_power_changed)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool) -> None:
        """
        Handle GPIO connection status change.

        Args:
            connected: True if GPIO connected, False if disconnected
        """
        self.is_connected = connected

        if connected:
            self.status_label.setText("Status: ✓ Connected")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.CONNECTED}; padding: 4px;"
            )
            self.calibrate_btn.setEnabled(True)
            self.view_curve_btn.setEnabled(True)
        else:
            self.status_label.setText("Status: ⚠️ Not Connected (GPIO offline)")
            self.status_label.setStyleSheet(
                f"font-size: 10pt; color: {Colors.TEXT_SECONDARY}; padding: 4px;"
            )
            self.voltage_label.setText("Voltage: 0.00 V")
            self.power_label.setText("Power: 0.0 mW")
            self.calibrate_btn.setEnabled(False)
            self.view_curve_btn.setEnabled(False)

    @pyqtSlot(float)
    def _on_voltage_changed(self, voltage: float) -> None:
        """
        Handle photodiode voltage reading update.

        Args:
            voltage: Voltage in volts (0.0-5.0)
        """
        if self.is_connected:
            self.voltage_label.setText(f"Voltage: {voltage:.3f} V")

            # Update color based on voltage level
            if voltage > 4.5:
                # Near saturation
                border_color = Colors.DANGER
            elif voltage > 0.1:
                # Valid reading
                border_color = Colors.SAFE
            else:
                # Very low / no signal
                border_color = Colors.BORDER_DEFAULT

            self.voltage_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {Colors.BACKGROUND};
                    color: {Colors.TEXT_PRIMARY};
                    border: 2px solid {border_color};
                    border-radius: 6px;
                    padding: {Spacing.NORMAL}px;
                    font-size: 12pt;
                    font-weight: bold;
                }}
            """
            )

    @pyqtSlot(float)
    def _on_power_changed(self, power_mw: float) -> None:
        """
        Handle photodiode power reading update.

        Args:
            power_mw: Calculated power in milliwatts
        """
        if self.is_connected:
            # Format power with appropriate precision
            if power_mw >= 1000.0:
                # Display in watts if >1W
                power_w = power_mw / 1000.0
                self.power_label.setText(f"Power: {power_w:.2f} W")
            else:
                self.power_label.setText(f"Power: {power_mw:.1f} mW")

    def _on_calibrate_clicked(self) -> None:
        """Handle Calibrate button click (future feature)."""
        # TODO: Implement calibration dialog
        # For now, show placeholder message
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Calibration",
            "Photodiode calibration feature coming soon.\n\n"
            "This will allow you to calibrate the voltage-to-power conversion curve "
            "using known laser power measurements.",
        )

    def _on_view_curve_clicked(self) -> None:
        """Handle View Curve button click (future feature)."""
        # TODO: Implement curve viewer dialog
        # For now, show placeholder message
        from PyQt6.QtWidgets import QMessageBox

        if self.gpio_controller and hasattr(self.gpio_controller, "photodiode_voltage_to_power"):
            conversion = self.gpio_controller.photodiode_voltage_to_power
            QMessageBox.information(
                self,
                "Calibration Curve",
                f"Current calibration:\n\n"
                f"Linear conversion: {conversion:.1f} mW/V\n\n"
                f"Example:\n"
                f"  1.0 V → {conversion:.0f} mW\n"
                f"  2.5 V → {conversion * 2.5:.0f} mW\n"
                f"  5.0 V → {conversion * 5.0:.0f} mW\n\n"
                f"Full curve viewer coming soon.",
            )
        else:
            QMessageBox.information(
                self,
                "Calibration Curve",
                "Calibration curve viewer coming soon.",
            )

    def cleanup(self) -> None:
        """Clean up resources (called on window close)."""
        # Disconnect signals if connected
        if self.gpio_controller is not None:
            try:
                if hasattr(self.gpio_controller, "connection_changed"):
                    self.gpio_controller.connection_changed.disconnect(
                        self._on_connection_changed
                    )
                if hasattr(self.gpio_controller, "photodiode_voltage_changed"):
                    self.gpio_controller.photodiode_voltage_changed.disconnect(
                        self._on_voltage_changed
                    )
                if hasattr(self.gpio_controller, "photodiode_power_changed"):
                    self.gpio_controller.photodiode_power_changed.disconnect(
                        self._on_power_changed
                    )
            except (RuntimeError, TypeError):
                pass  # Signals already disconnected
