"""
Module: Configuration Display Widget
Project: TOSCA Laser Control System

Purpose: Display and manage system configuration files (config.yaml) in Hardware & Diagnostics tab.
         Provides read-only visibility into hardware settings and configuration values.
Safety Critical: No
"""

import logging
import os
import subprocess
from pathlib import Path

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_tokens import Colors

logger = logging.getLogger(__name__)

# Config file location
CONFIG_FILE = Path("config.yaml")


class ConfigDisplayWidget(QWidget):
    """
    Read-only configuration display widget.

    Shows system configuration values from config.yaml in organized groups:
    - Serial connection settings
    - Motor control parameters
    - Camera settings
    - Safety timings
    """

    def __init__(self) -> None:
        super().__init__()

        self.config = None
        self._is_collapsed = True  # Start collapsed to save screen space

        self._init_ui()
        self._load_config()

    def _init_ui(self) -> None:
        """Initialize the user interface with collapsible functionality."""
        layout = QVBoxLayout(self)

        # Constrain maximum width
        self.setMaximumWidth(800)

        # Collapsible header with expand/collapse button
        self.toggle_btn = QPushButton("▶ Configuration Display (click to expand)")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_visibility)
        layout.addWidget(self.toggle_btn)

        # Container for all content (will be hidden/shown)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout()
        self.content_widget.setLayout(content_layout)

        # Config file location section
        location_group = self._create_location_group()
        content_layout.addWidget(location_group)

        # Serial connection settings
        serial_group = self._create_serial_group()
        content_layout.addWidget(serial_group)

        # Motor control settings
        motor_group = self._create_motor_group()
        content_layout.addWidget(motor_group)

        # Camera settings
        camera_group = self._create_camera_group()
        content_layout.addWidget(camera_group)

        # Safety timings
        safety_group = self._create_safety_group()
        content_layout.addWidget(safety_group)

        content_layout.addStretch()

        layout.addWidget(self.content_widget)

        # Start collapsed
        self.content_widget.setVisible(False)

    def _create_location_group(self) -> QGroupBox:
        """Create config file location display."""
        group = QGroupBox("Configuration File Location")
        layout = QHBoxLayout()

        # Config path label (absolute path)
        config_path = CONFIG_FILE.resolve()
        self.config_path_label = QLabel(str(config_path))
        self.config_path_label.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; "
            "background-color: #f5f5f5; padding: 5px; border: 1px solid #ddd; "
            "border-radius: 3px;"
        )
        self.config_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.config_path_label, 1)

        # Open button
        self.open_btn = QPushButton("[FILE] Open")
        self.open_btn.setFixedWidth(80)
        self.open_btn.setToolTip("Open config.yaml in default editor")
        self.open_btn.clicked.connect(self._open_config_file)
        layout.addWidget(self.open_btn)

        group.setLayout(layout)
        return group

    def _create_serial_group(self) -> QGroupBox:
        """Create serial connection settings display."""
        group = QGroupBox("Serial Connection Settings")
        layout = QGridLayout()

        # GPIO Baudrate
        layout.addWidget(QLabel("GPIO Baudrate:"), 0, 0)
        self.gpio_baudrate_label = QLabel("--")
        self.gpio_baudrate_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.gpio_baudrate_label, 0, 1)
        layout.addWidget(QLabel("(Read-only)"), 0, 2)

        # Actuator Baudrate
        layout.addWidget(QLabel("Actuator Baudrate:"), 1, 0)
        self.actuator_baudrate_label = QLabel("--")
        self.actuator_baudrate_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.actuator_baudrate_label, 1, 1)
        layout.addWidget(QLabel("(Read-only)"), 1, 2)

        # Laser COM Port
        layout.addWidget(QLabel("Laser COM Port:"), 2, 0)
        self.laser_com_label = QLabel("--")
        self.laser_com_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.laser_com_label, 2, 1)
        layout.addWidget(QLabel("(Read-only)"), 2, 2)

        # Laser Baudrate
        layout.addWidget(QLabel("Laser Baudrate:"), 3, 0)
        self.laser_baudrate_label = QLabel("--")
        self.laser_baudrate_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.laser_baudrate_label, 3, 1)
        layout.addWidget(QLabel("(Read-only)"), 3, 2)

        group.setLayout(layout)
        return group

    def _create_motor_group(self) -> QGroupBox:
        """Create motor control settings display."""
        group = QGroupBox("Motor Control Settings")
        layout = QGridLayout()

        # Motor PWM Max
        layout.addWidget(QLabel("Motor PWM Max:"), 0, 0)
        self.motor_pwm_max_label = QLabel("--")
        self.motor_pwm_max_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.motor_pwm_max_label, 0, 1)
        layout.addWidget(QLabel("(Safety limit - Read-only)"), 0, 2)

        # Motor Default Speed
        layout.addWidget(QLabel("Motor Default Speed:"), 1, 0)
        self.motor_default_speed_label = QLabel("--")
        self.motor_default_speed_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.motor_default_speed_label, 1, 1)
        layout.addWidget(QLabel("(Startup speed - Read-only)"), 1, 2)

        # Vibration Threshold
        layout.addWidget(QLabel("Vibration Threshold:"), 2, 0)
        self.vibration_threshold_label = QLabel("--")
        self.vibration_threshold_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.vibration_threshold_label, 2, 1)
        layout.addWidget(QLabel("(Detection sensitivity - Read-only)"), 2, 2)

        group.setLayout(layout)
        return group

    def _create_camera_group(self) -> QGroupBox:
        """Create camera settings display."""
        group = QGroupBox("Camera Settings (Performance Tuning)")
        layout = QGridLayout()

        # GUI FPS Target
        layout.addWidget(QLabel("GUI FPS Target:"), 0, 0)
        self.gui_fps_label = QLabel("--")
        self.gui_fps_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.gui_fps_label, 0, 1)
        layout.addWidget(QLabel("(Display update rate - Read-only)"), 0, 2)

        # Hardware FPS
        layout.addWidget(QLabel("Hardware FPS:"), 1, 0)
        self.hardware_fps_label = QLabel("--")
        self.hardware_fps_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.hardware_fps_label, 1, 1)
        layout.addWidget(QLabel("(Acquisition rate - Read-only)"), 1, 2)

        group.setLayout(layout)
        return group

    def _create_safety_group(self) -> QGroupBox:
        """Create safety timings display."""
        group = QGroupBox("Safety Timings (Calibration)")
        layout = QGridLayout()

        # Watchdog Heartbeat
        layout.addWidget(QLabel("Watchdog Heartbeat:"), 0, 0)
        self.watchdog_heartbeat_label = QLabel("--")
        self.watchdog_heartbeat_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.watchdog_heartbeat_label, 0, 1)
        layout.addWidget(QLabel("(Read-only)"), 0, 2)

        # Actuator Position Timer
        layout.addWidget(QLabel("Actuator Position Timer:"), 1, 0)
        self.actuator_timer_label = QLabel("--")
        self.actuator_timer_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.actuator_timer_label, 1, 1)
        layout.addWidget(QLabel("(Read-only)"), 1, 2)

        group.setLayout(layout)
        return group

    def _load_config(self) -> None:
        """Load configuration values from config.yaml."""
        try:
            # Load raw YAML to access all fields (including those not in Pydantic models)
            if not CONFIG_FILE.exists():
                logger.error(f"Config file not found: {CONFIG_FILE}")
                self._show_load_error()
                return

            with open(CONFIG_FILE, "r") as f:
                self.config = yaml.safe_load(f)

            # Serial settings
            gpio_config = self.config.get("hardware", {}).get("gpio", {})
            actuator_config = self.config.get("hardware", {}).get("actuator", {})
            laser_config = self.config.get("hardware", {}).get("laser", {})

            self.gpio_baudrate_label.setText(str(gpio_config.get("baudrate", "N/A")))
            self.actuator_baudrate_label.setText(str(actuator_config.get("baudrate", "N/A")))
            self.laser_com_label.setText(str(laser_config.get("com_port", "N/A")))
            self.laser_baudrate_label.setText(str(laser_config.get("baudrate", "N/A")))

            # Motor settings
            self.motor_pwm_max_label.setText(str(gpio_config.get("motor_pwm_max", "N/A")))
            self.motor_default_speed_label.setText(
                str(gpio_config.get("motor_default_speed", "N/A"))
            )
            self.vibration_threshold_label.setText(
                f"{gpio_config.get('vibration_threshold', 'N/A')} g"
            )

            # Camera settings
            camera_config = self.config.get("hardware", {}).get("camera", {})
            self.gui_fps_label.setText(f"{camera_config.get('gui_fps_target', 'N/A')} FPS")
            self.hardware_fps_label.setText(f"{camera_config.get('hardware_fps', 'N/A')} FPS")

            # Safety timings
            safety_config = self.config.get("safety", {})
            self.watchdog_heartbeat_label.setText(
                f"{safety_config.get('watchdog_heartbeat_ms', 'N/A')} ms"
            )
            self.actuator_timer_label.setText(
                f"{actuator_config.get('position_timer_ms', 'N/A')} ms"
            )

            logger.info("Configuration values loaded and displayed")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._show_load_error()

    def _show_load_error(self) -> None:
        """Display error state when config cannot be loaded."""
        error_text = "ERROR"
        for label in [
            self.gpio_baudrate_label,
            self.actuator_baudrate_label,
            self.laser_com_label,
            self.laser_baudrate_label,
            self.motor_pwm_max_label,
            self.motor_default_speed_label,
            self.vibration_threshold_label,
            self.gui_fps_label,
            self.hardware_fps_label,
            self.watchdog_heartbeat_label,
            self.actuator_timer_label,
        ]:
            label.setText(error_text)
            label.setStyleSheet(f"font-weight: bold; color: {Colors.DANGER};")

    def _open_config_file(self) -> None:
        """Open config.yaml in the system default editor."""
        try:
            config_path = CONFIG_FILE.resolve()

            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return

            # Windows: use 'start' command
            # macOS: use 'open' command
            # Linux: use 'xdg-open' command
            if os.name == "nt":  # Windows
                os.startfile(config_path)
            elif os.name == "posix":  # macOS or Linux
                subprocess.run(["xdg-open", str(config_path)])
            else:
                logger.warning(f"Unsupported OS for opening files: {os.name}")

            logger.info(f"Opened config file: {config_path}")

        except Exception as e:
            logger.error(f"Failed to open config file: {e}")
