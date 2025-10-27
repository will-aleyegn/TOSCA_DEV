"""
Active Treatment Widget - Read-only monitoring dashboard during treatment execution.

This widget provides real-time monitoring of active treatments with minimal
interactive controls. Focus is on situational awareness and safety.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.interlocks_widget import InterlocksWidget

logger = logging.getLogger(__name__)


class ProtocolExecutionThread(QThread):
    """Thread for executing protocols asynchronously."""

    # Signals
    execution_complete = pyqtSignal(bool, str)  # (success, message)
    execution_error = pyqtSignal(str)  # error_message

    def __init__(self, protocol_engine: Any, protocol: Any) -> None:
        super().__init__()
        self.protocol_engine = protocol_engine
        self.protocol = protocol

    def run(self) -> None:
        """Run protocol execution in thread."""
        try:
            # Create event loop for async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Execute protocol
            success, message = loop.run_until_complete(
                self.protocol_engine.execute_protocol(self.protocol, record=True)
            )

            self.execution_complete.emit(success, message)

        except Exception as e:
            logger.error(f"Protocol execution error: {e}")
            self.execution_error.emit(str(e))


class ActiveTreatmentWidget(QWidget):
    """
    Active treatment monitoring dashboard.

    Displays:
    - Camera feed (monitoring only, no controls)
    - Current laser power (read-only)
    - Current actuator position (read-only)
    - Treatment progress and status
    - Safety interlocks status
    - Event log
    - STOP button (safety control only)

    This is the "execution" interface - minimal interaction, maximum monitoring.
    """

    def __init__(self) -> None:
        super().__init__()
        self.protocol_engine: Optional[Any] = None
        self.safety_manager: Optional[Any] = None
        self.camera_widget: Optional[Any] = None  # Will be set from main_window

        # Dashboard widgets
        self.interlocks_widget: InterlocksWidget = InterlocksWidget()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components with monitoring dashboard layout."""
        layout = QGridLayout()
        self.setLayout(layout)

        # === TOP: Camera Feed (Monitoring) ===
        camera_section = self._create_camera_section()
        layout.addWidget(camera_section, 0, 0, 2, 2)  # Spans 2 rows, 2 columns

        # === RIGHT: Safety Status Panel ===
        safety_panel = self._create_safety_panel()
        layout.addWidget(safety_panel, 0, 2, 2, 1)  # Spans 2 rows, column 2

        # === BOTTOM: Treatment Controls ===
        control_section = self._create_control_section()
        layout.addWidget(control_section, 2, 0, 1, 3)  # Row 2, spans all columns

        # Set stretch factors (camera:safety = 3:1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)

    def _create_camera_section(self) -> QGroupBox:
        """Create camera monitoring section."""
        group = QGroupBox("Treatment Monitoring")
        layout = QVBoxLayout()

        # Camera feed placeholder (will be replaced with actual camera widget)
        self.camera_display = QLabel("Camera Feed\n(Monitoring Only)")
        self.camera_display.setStyleSheet(
            "QLabel { "
            "background-color: #2b2b2b; "
            "color: #666; "
            "font-size: 20px; "
            "border: 2px solid #444; "
            "}"
        )
        self.camera_display.setMinimumHeight(400)
        self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_display)

        # Real-time parameter display (read-only)
        params_layout = QHBoxLayout()

        self.laser_power_label = self._create_status_display("Laser Power", "0.00 W")
        params_layout.addWidget(self.laser_power_label)

        self.actuator_pos_label = self._create_status_display("Actuator", "0 μm")
        params_layout.addWidget(self.actuator_pos_label)

        self.motor_vibration_label = self._create_status_display("Vibration", "0.00 g")
        params_layout.addWidget(self.motor_vibration_label)

        layout.addLayout(params_layout)

        group.setLayout(layout)
        return group

    def _create_status_display(self, label: str, initial_value: str) -> QWidget:
        """Create a read-only status display."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 11px; color: #888;")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)

        value_widget = QLabel(initial_value)
        value_widget.setStyleSheet(
            "font-size: 18px; font-weight: bold; "
            "padding: 8px; background-color: #3c3c3c; border-radius: 3px;"
        )
        value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_widget)

        widget.setLayout(layout)
        setattr(widget, "value_label", value_widget)
        return widget

    def _create_safety_panel(self) -> QWidget:
        """Create safety monitoring panel."""
        # Create scroll area for safety panel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)

        # Safety interlocks
        layout.addWidget(self.interlocks_widget)

        # Event log
        event_log_group = QGroupBox("Treatment Events")
        event_layout = QVBoxLayout()

        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(200)
        self.event_log.setPlaceholderText("Treatment events will appear here...")
        self.event_log.setStyleSheet("font-size: 10px; font-family: monospace;")
        event_layout.addWidget(self.event_log)

        event_log_group.setLayout(event_layout)
        layout.addWidget(event_log_group)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_control_section(self) -> QGroupBox:
        """Create treatment control section."""
        group = QGroupBox("Treatment Control")
        layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            """
        )
        layout.addWidget(self.progress_bar)

        # Status and action labels
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-size: 13px; padding: 5px;")
        status_layout.addWidget(self.status_label, 1)

        self.action_label = QLabel("")
        self.action_label.setStyleSheet("font-size: 12px; color: #888; padding: 5px;")
        status_layout.addWidget(self.action_label, 1)

        layout.addLayout(status_layout)

        # Control buttons
        button_layout = QHBoxLayout()

        self.stop_button = QPushButton("⏹ STOP TREATMENT")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setStyleSheet(
            "font-size: 16px; font-weight: bold; "
            "background-color: #f44336; color: white;"
        )
        self.stop_button.clicked.connect(self._on_stop_treatment)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def set_camera_widget(self, camera_widget: Any) -> None:
        """
        Set the camera widget for live feed display.

        Args:
            camera_widget: CameraWidget instance
        """
        self.camera_widget = camera_widget
        # TODO: Replace placeholder with actual camera feed in Phase 2.3
        logger.info("Camera widget connected to active treatment monitoring")

    def set_protocol_engine(self, protocol_engine: Any) -> None:
        """
        Set the protocol engine for treatment execution monitoring.

        Args:
            protocol_engine: ProtocolEngine instance
        """
        self.protocol_engine = protocol_engine
        logger.info("Protocol engine connected to active treatment widget")

        if self.protocol_engine:
            # Connect protocol engine callbacks
            self.protocol_engine.on_action_start = self._on_action_start
            self.protocol_engine.on_action_complete = self._on_action_complete
            self.protocol_engine.on_progress_update = self._on_progress_update
            self.protocol_engine.on_state_change = self._on_state_change

    def set_safety_manager(self, safety_manager: Any) -> None:
        """
        Set the safety manager for interlock monitoring.

        Args:
            safety_manager: SafetyManager instance
        """
        self.safety_manager = safety_manager
        logger.info("Safety manager connected to active treatment widget")

        # Connect interlocks widget
        if self.interlocks_widget and safety_manager:
            self.interlocks_widget.set_safety_manager(safety_manager)

    def _on_stop_treatment(self) -> None:
        """Handle stop treatment button click."""
        if self.protocol_engine:
            self.protocol_engine.stop()
            self.status_label.setText("Status: Stopping...")
            self.action_label.setText("Waiting for safe shutdown...")
            self._log_event("Treatment stop requested by operator")

    def _on_action_start(self, action: Any) -> None:
        """Handle protocol action start."""
        action_type = action.action_type.value if hasattr(action, "action_type") else "Unknown"
        action_id = action.action_id if hasattr(action, "action_id") else "?"
        self.action_label.setText(f"Executing: {action_type} (Action {action_id})")
        self._log_event(f"Action started: {action_type}")

    def _on_action_complete(self, action: Any) -> None:
        """Handle protocol action completion."""
        action_type = action.action_type.value if hasattr(action, "action_type") else "Unknown"
        self._log_event(f"Action completed: {action_type}")

    def _on_progress_update(self, progress: float) -> None:
        """Update progress bar."""
        self.progress_bar.setValue(int(progress * 100))

    def _on_state_change(self, state: Any) -> None:
        """Handle protocol state change."""
        state_value = state.value if hasattr(state, "value") else str(state)
        logger.info(f"Protocol state: {state_value}")

    def _log_event(self, message: str) -> None:
        """Log an event to the event log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")

    def cleanup(self) -> None:
        """Cleanup resources."""
        pass
