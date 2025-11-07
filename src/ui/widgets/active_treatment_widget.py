"""
Active Treatment Widget - Read-only monitoring dashboard during treatment execution.

This widget provides real-time monitoring of active treatments with minimal
interactive controls. Focus is on situational awareness and safety.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import (
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
from ui.widgets.smoothing_status_widget import SmoothingStatusWidget
from ui.workers.protocol_worker import ProtocolWorker

logger = logging.getLogger(__name__)


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
        self.camera_live_view: Optional[Any] = None  # Will be set from main_window
        self.protocol_worker: Optional[ProtocolWorker] = None  # Thread-safe worker

        # Dashboard widgets
        self.interlocks_widget: InterlocksWidget = InterlocksWidget()
        self.smoothing_status_widget: SmoothingStatusWidget = SmoothingStatusWidget()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components with horizontal monitoring layout."""
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # === LEFT: Camera + Controls (3/5 width) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setLayout(left_layout)

        # Camera monitoring (takes most space)
        camera_section = self._create_camera_section()
        left_layout.addWidget(camera_section, 3)

        # Treatment controls (compact, at bottom)
        control_section = self._create_control_section()
        left_layout.addWidget(control_section, 1)

        layout.addWidget(left_panel, 3)

        # === RIGHT: Safety Status Panel (2/5 width) ===
        safety_panel = self._create_safety_panel()
        layout.addWidget(safety_panel, 2)

    def _create_camera_section(self) -> QGroupBox:
        """Create camera monitoring section."""
        group = QGroupBox("Camera Monitor")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Camera feed placeholder (will be replaced with actual camera widget)
        self.camera_display = QLabel("Camera Feed\n(Monitoring)")
        self.camera_display.setStyleSheet(
            "QLabel { "
            "background-color: #2b2b2b; "
            "color: #666; "
            "font-size: 16px; "
            "border: 2px solid #444; "
            "}"
        )
        self.camera_display.setMinimumHeight(250)
        self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_display)

        # Real-time parameter display (read-only, compact)
        params_layout = QHBoxLayout()

        self.laser_power_label = self._create_status_display("Laser", "0.00 W")
        params_layout.addWidget(self.laser_power_label)

        self.actuator_pos_label = self._create_status_display("Pos", "0 μm")
        params_layout.addWidget(self.actuator_pos_label)

        self.motor_vibration_label = self._create_status_display("Vib", "0.00 g")
        params_layout.addWidget(self.motor_vibration_label)

        layout.addLayout(params_layout)

        group.setLayout(layout)
        return group

    def _create_status_display(self, label: str, initial_value: str) -> QWidget:
        """Create a compact read-only status display."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 14px; color: #888;")  # Increased from 11px for clinical readability
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)

        value_widget = QLabel(initial_value)
        value_widget.setStyleSheet(
            "font-size: 18px; font-weight: bold; "  # Increased from 13px for 60cm viewing distance
            "padding: 4px; background-color: #3c3c3c; border-radius: 2px;"
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
        scroll.setMaximumWidth(450)  # Prevent excessive horizontal stretching

        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)

        # Safety interlocks
        layout.addWidget(self.interlocks_widget)

        # Smoothing motor status and controls
        layout.addWidget(self.smoothing_status_widget)

        # Event log
        event_log_group = QGroupBox("Treatment Events")
        event_layout = QVBoxLayout()

        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(200)
        self.event_log.setPlaceholderText("Treatment events will appear here...")
        self.event_log.setStyleSheet("font-size: 11px; font-family: monospace;")
        event_layout.addWidget(self.event_log)

        event_log_group.setLayout(event_layout)
        layout.addWidget(event_log_group)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _create_control_section(self) -> QGroupBox:
        """Create compact treatment control section."""
        group = QGroupBox("Control")
        layout = QHBoxLayout()  # Horizontal for compactness
        layout.setContentsMargins(5, 5, 5, 5)

        # Left: Progress + Status (vertical)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(3)

        # Progress bar (compact)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                font-size: 11px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            """
        )
        left_layout.addWidget(self.progress_bar)

        # Status label (compact)
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-size: 11px; padding: 2px;")
        left_layout.addWidget(self.status_label)

        # Action label (compact)
        self.action_label = QLabel("")
        self.action_label.setStyleSheet("font-size: 11px; color: #888; padding: 2px;")
        left_layout.addWidget(self.action_label)

        layout.addLayout(left_layout, 2)

        # Right: Stop button (compact)
        self.stop_button = QPushButton("⏹ STOP")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(45)
        self.stop_button.setMaximumWidth(120)
        self.stop_button.setStyleSheet(
            "font-size: 14px; font-weight: bold; " "background-color: #f44336; color: white;"
        )
        self.stop_button.clicked.connect(self._on_stop_treatment)
        layout.addWidget(self.stop_button, 0, Qt.AlignmentFlag.AlignRight)

        group.setLayout(layout)
        return group

    def set_camera_live_view(self, camera_live_view: Any) -> None:
        """
        Set the camera live view for live feed display.

        Args:
            camera_live_view: Camera live view widget instance
        """
        self.camera_live_view = camera_live_view

        if camera_live_view and hasattr(camera_live_view, "pixmap_ready"):
            # Connect to the camera widget's pixmap_ready signal
            # This is the CORRECT way to share camera feed between widgets
            # Never reparent widgets from other components - use signals instead!
            camera_live_view.pixmap_ready.connect(self._on_camera_frame_ready)
            logger.info("Camera feed connected to active treatment dashboard via signal")
        else:
            logger.warning("Camera widget has no pixmap_ready signal - using placeholder")

    def _on_camera_frame_ready(self, pixmap: Any) -> None:
        """
        Update camera display with new frame from CameraWidget.

        Args:
            pixmap: QPixmap to display
        """
        # Scale to fit our display size while maintaining aspect ratio
        from PyQt6.QtCore import Qt

        scaled_pixmap = pixmap.scaled(
            self.camera_display.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self.camera_display.setPixmap(scaled_pixmap)

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
        """
        Cleanup resources on widget shutdown.

        Cancels any running protocol worker and waits for thread pool completion.
        """
        logger.info("Cleaning up ActiveTreatmentWidget...")

        # Cancel any running protocol execution
        if self.protocol_worker and not self.protocol_worker.is_cancelled():
            logger.info("Cancelling active protocol worker")
            self.protocol_worker.cancel()

        # Wait for thread pool to complete (max 2 seconds)
        QThreadPool.globalInstance().waitForDone(2000)

        logger.info("ActiveTreatmentWidget cleanup complete")
