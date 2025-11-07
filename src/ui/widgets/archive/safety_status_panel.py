"""
Safety Status Panel - Always-visible safety monitoring widget.

This panel provides persistent visibility of critical safety information across all tabs:
- Safety state (SAFE, ARMED, TREATING, UNSAFE, EMERGENCY_STOP)
- Hardware interlocks (footpedal, smoothing, photodiode, watchdog)
- Laser power monitoring (current vs. limit)
- Active session information

Medical Device Context:
    - Required for FDA compliance (continuous safety monitoring visibility)
    - Must be visible at all times during operation
    - Updates in real-time via safety manager signals

Usage:
    panel = SafetyStatusPanel()
    panel.set_safety_manager(safety_manager)
    panel.set_session_manager(session_manager)
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from core.safety import SafetyManager, SafetyState

logger = logging.getLogger(__name__)


class SafetyStatusPanel(QWidget):
    """
    Always-visible safety status panel for medical device monitoring.

    Displays:
    - Current safety state with color coding
    - Hardware interlock status (4 interlocks)
    - Laser power monitoring with progress bar
    - Active session information (if available)

    This widget is docked on the right side of the main window and remains
    visible across all tabs for continuous safety monitoring.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.safety_manager: Optional[SafetyManager] = None
        self.session_manager = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        self.setLayout(layout)

        # Set fixed width for docked panel
        self.setFixedWidth(240)
        self.setStyleSheet("background-color: white; border-left: 1px solid #E0E0E0;")

        # Panel header
        header = QLabel("SAFETY STATUS")
        header.setStyleSheet(
            "font-size: 12pt; font-weight: bold; padding: 8px; "
            "background-color: #37474F; color: white; border-radius: 3px;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Safety state section
        state_group = self._create_safety_state_section()
        layout.addWidget(state_group)

        # Interlocks section
        interlocks_group = self._create_interlocks_section()
        layout.addWidget(interlocks_group)

        # Power monitoring section
        power_group = self._create_power_section()
        layout.addWidget(power_group)

        # Session info section
        session_group = self._create_session_section()
        layout.addWidget(session_group)

        layout.addStretch()

        logger.info("Safety status panel initialized")

    def _create_safety_state_section(self) -> QGroupBox:
        """Create safety state display section."""
        group = QGroupBox("System State")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 8, 5, 5)

        # Safety state label (large, color-coded)
        self.state_label = QLabel("SAFE")
        self.state_label.setStyleSheet(
            "font-size: 16pt; font-weight: bold; padding: 8px; "
            "background-color: #4CAF50; color: white; border-radius: 3px;"
        )
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.state_label)

        # Status message
        self.status_message = QLabel("All systems operational")
        self.status_message.setStyleSheet("font-size: 9pt; color: #666; padding: 4px;")
        self.status_message.setWordWrap(True)
        layout.addWidget(self.status_message)

        group.setLayout(layout)
        return group

    def _create_interlocks_section(self) -> QGroupBox:
        """Create hardware interlocks display section."""
        group = QGroupBox("Interlocks")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 8, 5, 5)
        layout.setSpacing(4)

        # Footpedal interlock
        self.footpedal_label = QLabel("○ Footpedal: UNKNOWN")
        self.footpedal_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(self.footpedal_label)

        # Smoothing motor interlock
        self.smoothing_label = QLabel("○ Smoothing: UNKNOWN")
        self.smoothing_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(self.smoothing_label)

        # Photodiode interlock
        self.photodiode_label = QLabel("○ Photodiode: UNKNOWN")
        self.photodiode_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(self.photodiode_label)

        # Watchdog interlock
        self.watchdog_label = QLabel("○ Watchdog: UNKNOWN")
        self.watchdog_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(self.watchdog_label)

        group.setLayout(layout)
        return group

    def _create_power_section(self) -> QGroupBox:
        """Create laser power monitoring section."""
        group = QGroupBox("Power Status")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 8, 5, 5)
        layout.setSpacing(4)

        # Current power label
        self.current_power_label = QLabel("Current: 0.00 W")
        self.current_power_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        layout.addWidget(self.current_power_label)

        # Power limit label
        self.power_limit_label = QLabel("Limit: 10.00 W")
        self.power_limit_label.setStyleSheet("font-size: 9pt; color: #666;")
        layout.addWidget(self.power_limit_label)

        # Progress bar
        self.power_progress = QProgressBar()
        self.power_progress.setRange(0, 100)
        self.power_progress.setValue(0)
        self.power_progress.setTextVisible(True)
        self.power_progress.setFormat("%p%")
        self.power_progress.setStyleSheet(
            "QProgressBar { border: 1px solid #ccc; border-radius: 3px; text-align: center; }"
            "QProgressBar::chunk { background-color: #4CAF50; }"
        )
        layout.addWidget(self.power_progress)

        group.setLayout(layout)
        return group

    def _create_session_section(self) -> QGroupBox:
        """Create session information section."""
        group = QGroupBox("Session")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 8, 5, 5)
        layout.setSpacing(2)

        # Session info label
        self.session_info_label = QLabel("No active session")
        self.session_info_label.setStyleSheet("font-size: 9pt; color: #666;")
        self.session_info_label.setWordWrap(True)
        layout.addWidget(self.session_info_label)

        group.setLayout(layout)
        return group

    def set_safety_manager(self, safety_manager: SafetyManager) -> None:
        """
        Connect to safety manager for real-time updates.

        Args:
            safety_manager: Safety manager instance
        """
        self.safety_manager = safety_manager

        # Connect signals
        safety_manager.safety_state_changed.connect(self._on_safety_state_changed)
        safety_manager.interlock_status_changed.connect(self._on_interlock_status_changed)

        # Request initial state
        self._on_safety_state_changed(safety_manager.state)
        self._update_interlock_display()

        logger.info("Safety status panel connected to SafetyManager")

    def set_session_manager(self, session_manager) -> None:
        """
        Connect to session manager for session info updates.

        Args:
            session_manager: Session manager instance
        """
        self.session_manager = session_manager

        # Connect signals if available
        if hasattr(session_manager, "session_started"):
            session_manager.session_started.connect(self._on_session_updated)
        if hasattr(session_manager, "session_ended"):
            session_manager.session_ended.connect(self._on_session_updated)

        # Update initial display
        self._update_session_display()

        logger.info("Safety status panel connected to SessionManager")

    @pyqtSlot(SafetyState)
    def _on_safety_state_changed(self, state: SafetyState) -> None:
        """
        Handle safety state changes.

        Args:
            state: New safety state
        """
        # Update state label with color coding
        state_colors = {
            SafetyState.SAFE: ("#4CAF50", "All systems operational"),
            SafetyState.ARMED: ("#FF9800", "System armed - ready for treatment"),
            SafetyState.TREATING: ("#2196F3", "Treatment in progress"),
            SafetyState.UNSAFE: ("#F44336", "Safety violation detected"),
            SafetyState.EMERGENCY_STOP: ("#D32F2F", "EMERGENCY STOP ACTIVATED"),
        }

        color, message = state_colors.get(state, ("#9E9E9E", "Unknown state"))

        self.state_label.setText(state.value.replace("_", " "))
        self.state_label.setStyleSheet(
            f"font-size: 16pt; font-weight: bold; padding: 8px; "
            f"background-color: {color}; color: white; border-radius: 3px;"
        )
        self.status_message.setText(message)

    @pyqtSlot()
    def _on_interlock_status_changed(self) -> None:
        """Handle interlock status changes."""
        self._update_interlock_display()

    def _update_interlock_display(self) -> None:
        """Update interlock status display."""
        if not self.safety_manager:
            return

        # Get interlock states from safety manager
        interlocks = self.safety_manager.get_interlock_status()

        # Update footpedal
        footpedal_ok = interlocks.get("footpedal", False)
        self._update_interlock_label(
            self.footpedal_label, "Footpedal", footpedal_ok, "PRESSED" if footpedal_ok else "RELEASED"
        )

        # Update smoothing motor
        smoothing_ok = interlocks.get("smoothing", False)
        self._update_interlock_label(
            self.smoothing_label, "Smoothing", smoothing_ok, "HEALTHY" if smoothing_ok else "FAULT"
        )

        # Update photodiode
        photodiode_ok = interlocks.get("photodiode", False)
        self._update_interlock_label(
            self.photodiode_label, "Photodiode", photodiode_ok, "OK" if photodiode_ok else "FAULT"
        )

        # Update watchdog
        watchdog_ok = interlocks.get("watchdog", False)
        self._update_interlock_label(
            self.watchdog_label, "Watchdog", watchdog_ok, "ACTIVE" if watchdog_ok else "TIMEOUT"
        )

    def _update_interlock_label(
        self, label: QLabel, name: str, ok: bool, status: str
    ) -> None:
        """
        Update a single interlock label.

        Args:
            label: QLabel to update
            name: Interlock name
            ok: Whether interlock is OK
            status: Status text
        """
        symbol = "✓" if ok else "✗"
        color = "#4CAF50" if ok else "#F44336"
        label.setText(f"{symbol} {name}: {status}")
        label.setStyleSheet(f"font-size: 9pt; color: {color}; font-weight: bold;")

    def update_power_status(self, current_w: float, limit_w: float) -> None:
        """
        Update laser power monitoring display.

        Args:
            current_w: Current laser power (watts)
            limit_w: Maximum allowed power (watts)
        """
        self.current_power_label.setText(f"Current: {current_w:.2f} W")
        self.power_limit_label.setText(f"Limit: {limit_w:.2f} W")

        # Update progress bar
        if limit_w > 0:
            percentage = int((current_w / limit_w) * 100)
            self.power_progress.setValue(percentage)

            # Change color based on percentage
            if percentage >= 90:
                chunk_color = "#F44336"  # Red - near limit
            elif percentage >= 75:
                chunk_color = "#FF9800"  # Orange - warning
            else:
                chunk_color = "#4CAF50"  # Green - normal

            self.power_progress.setStyleSheet(
                "QProgressBar { border: 1px solid #ccc; border-radius: 3px; text-align: center; }"
                f"QProgressBar::chunk {{ background-color: {chunk_color}; }}"
            )
        else:
            self.power_progress.setValue(0)

    @pyqtSlot(int)
    def _on_session_updated(self, session_id: int) -> None:
        """Handle session start/end events."""
        self._update_session_display()

    def _update_session_display(self) -> None:
        """Update session information display."""
        if not self.session_manager:
            self.session_info_label.setText("No session manager")
            return

        current_session = self.session_manager.get_current_session()

        if current_session:
            subject_code = current_session.subject_code
            tech_name = current_session.tech_name
            self.session_info_label.setText(f"{subject_code}\nTech: {tech_name}")
            self.session_info_label.setStyleSheet(
                "font-size: 9pt; color: #1976D2; font-weight: bold;"
            )
        else:
            self.session_info_label.setText("No active session")
            self.session_info_label.setStyleSheet("font-size: 9pt; color: #666;")
