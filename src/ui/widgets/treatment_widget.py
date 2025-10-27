"""
Treatment control widget.
"""

import asyncio
import logging
from typing import Any, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.actuator_widget import ActuatorWidget
from ui.widgets.interlocks_widget import InterlocksWidget
from ui.widgets.laser_widget import LaserWidget
from ui.widgets.motor_widget import MotorWidget

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
        self.safety_manager: Optional[Any] = None

        # Hardware control widgets
        self.actuator_widget: ActuatorWidget = ActuatorWidget()
        self.laser_widget: LaserWidget = LaserWidget()
        self.motor_widget: MotorWidget = MotorWidget()

        # Dashboard widgets
        self.interlocks_widget: InterlocksWidget = InterlocksWidget()

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components with dashboard layout."""
        # Use grid layout for precise control over dashboard sections
        layout = QGridLayout()
        self.setLayout(layout)

        # === LEFT PANEL: Hardware Controls (Laser + Actuator) ===
        left_panel = self._create_left_panel()
        layout.addWidget(left_panel, 0, 0, 2, 1)  # Spans 2 rows, column 0

        # === CENTER PANEL: Camera Feed + Treatment Controls ===
        center_panel = self._create_center_panel()
        layout.addWidget(center_panel, 0, 1, 2, 1)  # Spans 2 rows, column 1

        # === RIGHT PANEL: Interlocks + Smoothing + Events ===
        right_panel = self._create_right_panel()
        layout.addWidget(right_panel, 0, 2, 2, 1)  # Spans 2 rows, column 2

        # Set column stretch factors (left:center:right = 2:3:2)
        layout.setColumnStretch(0, 2)  # Left panel (hardware controls)
        layout.setColumnStretch(1, 3)  # Center panel (camera + treatment)
        layout.setColumnStretch(2, 2)  # Right panel (interlocks + status)

    def _create_left_panel(self) -> QWidget:
        """Create left panel with hardware controls."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Laser controls
        layout.addWidget(self.laser_widget)

        # Actuator controls
        layout.addWidget(self.actuator_widget)

        # Motor widget (will be moved to right panel in Phase 2.5)
        # Keeping here temporarily for backward compatibility
        layout.addWidget(self.motor_widget)

        layout.addStretch()
        return panel

    def _create_center_panel(self) -> QWidget:
        """Create center panel with camera feed and treatment controls."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Placeholder for camera feed (Phase 2.3)
        camera_placeholder = QLabel("Camera Feed\n(Phase 2.3)")
        camera_placeholder.setStyleSheet(
            "QLabel { "
            "background-color: #2b2b2b; "
            "color: #666; "
            "font-size: 18px; "
            "border: 2px dashed #444; "
            "padding: 60px; "
            "}"
        )
        camera_placeholder.setMinimumHeight(300)
        layout.addWidget(camera_placeholder, 2)  # Give camera feed more space

        # Treatment controls at bottom of center panel
        layout.addWidget(self._create_treatment_control(), 1)

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create right panel with interlocks, smoothing status, and mini event log."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Safety interlocks status
        layout.addWidget(self.interlocks_widget)

        # Placeholder for smoothing motor controls (Phase 2.5)
        smoothing_placeholder = QGroupBox("Smoothing Motor")
        smoothing_layout = QVBoxLayout()
        smoothing_label = QLabel("(Phase 2.5)\nMotor controls will move here")
        smoothing_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        smoothing_layout.addWidget(smoothing_label)
        smoothing_placeholder.setLayout(smoothing_layout)
        layout.addWidget(smoothing_placeholder)

        # Mini event log
        layout.addWidget(self._create_mini_event_log())

        layout.addStretch()
        return panel

    def _create_mini_event_log(self) -> QGroupBox:
        """Create mini event log for dashboard."""
        group = QGroupBox("Recent Events")
        layout = QVBoxLayout()

        self.mini_event_log = QTextEdit()
        self.mini_event_log.setReadOnly(True)
        self.mini_event_log.setMaximumHeight(150)
        self.mini_event_log.setPlaceholderText("Treatment events will appear here...")
        self.mini_event_log.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.mini_event_log)

        group.setLayout(layout)
        return group

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
        self.start_button.clicked.connect(self._on_start_treatment)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("STOP TREATMENT")
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; background-color: #f44336; color: white;"
        )
        self.stop_button.clicked.connect(self._on_stop_treatment)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 1px;
            }
            """
        )
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Ready - No Active Session")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        # Action status label for real-time feedback
        self.action_label = QLabel("")
        self.action_label.setStyleSheet("font-size: 12px; padding: 5px; color: #666;")
        layout.addWidget(self.action_label)

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

        if self.protocol_engine:
            # Connect protocol engine callbacks to UI updates
            self.protocol_engine.on_action_start = self._on_action_start
            self.protocol_engine.on_action_complete = self._on_action_complete
            self.protocol_engine.on_progress_update = self._on_progress_update
            self.protocol_engine.on_state_change = self._on_state_change
            logger.info("Protocol engine callbacks connected for UI feedback")

    def set_safety_manager(self, safety_manager: Any) -> None:
        """
        Set the safety manager for interlock monitoring.

        Args:
            safety_manager: SafetyManager instance for monitoring interlocks
        """
        self.safety_manager = safety_manager
        logger.info("Safety manager connected to treatment widget")

        # Connect interlocks widget to safety manager
        if self.interlocks_widget and safety_manager:
            self.interlocks_widget.set_safety_manager(safety_manager)
            logger.info("InterlocksWidget connected to safety manager")

    def _on_start_treatment(self) -> None:
        """Handle start treatment button click."""
        if not self.protocol_engine:
            logger.error("Cannot start treatment: Protocol engine not available")
            self.status_label.setText("Status: Error - Protocol engine not available")
            return

        # Create a simple test protocol for now
        # TODO: Load protocol from file or configuration
        from core.protocol import (
            ActionType,
            MoveActuatorParams,
            Protocol,
            ProtocolAction,
            SetLaserPowerParams,
            WaitParams,
        )

        test_protocol = Protocol(
            protocol_name="Test Treatment",
            version="1.0.0",
            actions=[
                ProtocolAction(
                    action_id=1,
                    action_type=ActionType.SET_LASER_POWER,
                    parameters=SetLaserPowerParams(power_watts=0.1),
                ),
                ProtocolAction(
                    action_id=2,
                    action_type=ActionType.MOVE_ACTUATOR,
                    parameters=MoveActuatorParams(
                        target_position_um=1000.0, speed_um_per_sec=100.0
                    ),
                ),
                ProtocolAction(
                    action_id=3,
                    action_type=ActionType.WAIT,
                    parameters=WaitParams(duration_seconds=2.0),
                ),
                ProtocolAction(
                    action_id=4,
                    action_type=ActionType.SET_LASER_POWER,
                    parameters=SetLaserPowerParams(power_watts=0.0),
                ),
            ],
        )

        # Start protocol execution in thread
        self.execution_thread = ProtocolExecutionThread(self.protocol_engine, test_protocol)
        self.execution_thread.execution_complete.connect(self._on_execution_complete)
        self.execution_thread.execution_error.connect(self._on_execution_error)
        self.execution_thread.start()

        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Treatment Running")
        self.progress_bar.setValue(0)

    def _on_stop_treatment(self) -> None:
        """Handle stop treatment button click."""
        if self.protocol_engine:
            self.protocol_engine.stop()
            self.status_label.setText("Status: Stopping Treatment...")
            self.action_label.setText("Waiting for safe shutdown...")

    def _on_action_start(self, action: Any) -> None:
        """Handle protocol action start."""
        action_type = action.action_type.value if hasattr(action, "action_type") else "Unknown"
        action_id = action.action_id if hasattr(action, "action_id") else "?"
        self.action_label.setText(f"Executing: {action_type} (Action {action_id})")

    def _on_action_complete(self, action: Any) -> None:
        """Handle protocol action completion."""
        action_type = action.action_type.value if hasattr(action, "action_type") else "Unknown"
        logger.info(f"Action completed: {action_type}")

    def _on_progress_update(self, progress: float) -> None:
        """Update progress bar."""
        self.progress_bar.setValue(int(progress * 100))

    def _on_state_change(self, state: Any) -> None:
        """Handle protocol state change."""
        state_value = state.value if hasattr(state, "value") else str(state)
        logger.info(f"Protocol state: {state_value}")

    def _on_execution_complete(self, success: bool, message: str) -> None:
        """Handle protocol execution completion."""
        self.start_button.setEnabled(self.dev_mode)
        self.stop_button.setEnabled(False)

        if success:
            self.status_label.setText("Status: Treatment Complete")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText(f"Status: {message}")

        self.action_label.setText("")

    def _on_execution_error(self, error_msg: str) -> None:
        """Handle protocol execution error."""
        self.start_button.setEnabled(self.dev_mode)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Status: Error - {error_msg}")
        self.action_label.setText("")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.actuator_widget:
            self.actuator_widget.cleanup()
        if self.laser_widget:
            self.laser_widget.cleanup()
