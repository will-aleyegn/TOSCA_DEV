"""
Unified Header Widget for TOSCA UI Consolidation.

Combines all persistent UI elements into a single top header:
1. Emergency Stop button (left)
2. Workflow step indicator (center-left)
3. Safety status display (center-right)
4. Research mode warning (right)

This replaces the scattered toolbar, right panel, and status bar with one
authoritative location for all critical information.

Medical Device Context:
    - Single source of truth for safety status
    - E-Stop always accessible (120x60px, prominent)
    - Workflow steps guide operator through procedure
    - Research mode warning always visible

Author: TOSCA Development Team
Date: 2025-11-05
Version: 0.9.14-alpha (UI Consolidation)
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.safety import SafetyState
from ui.design_tokens import Colors, ThemeMode, toggle_theme, get_current_theme
from ui.widgets.workflow_step_indicator import WorkflowStepIndicator

logger = logging.getLogger(__name__)


class UnifiedHeaderWidget(QWidget):
    """
    Unified top header containing all persistent UI elements.

    Replaces:
    - Toolbar (E-Stop, Connect All, Test All buttons)
    - Right panel (Safety status panel)
    - Status bar (Hardware status, research mode)

    Sections (left to right):
    1. E-Stop button (120px) - Emergency shutdown control
    2. Workflow steps (350px) - Treatment workflow progression
    3. Safety status (300px) - Real-time safety monitoring
    4. Research badge (150px) - Research mode warning

    Total height: 80px (saves 325px vertical space)
    """

    # Signals
    e_stop_clicked = pyqtSignal()
    step_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # State tracking
        self.current_safety_state = SafetyState.SAFE
        self.interlock_status = {
            "footpedal": False,
            "smoothing": False,
            "photodiode": False,
            "watchdog": False,
        }

        # Initialize sections
        self._init_ui()

        logger.info("Unified header widget initialized")

    def _init_ui(self) -> None:
        """Create unified header layout."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        self.setLayout(layout)

        # Set fixed height for header (increased to accommodate 40px interlock indicators)
        self.setFixedHeight(90)  # Was 80px, now 90px for FDA-compliant touch targets
        self.setStyleSheet(f"background-color: {Colors.HEADER}; border-bottom: 2px solid {Colors.BORDER_DEFAULT};")

        # 1. E-Stop button (120px fixed width)
        self.estop_button = self._create_estop_button()
        layout.addWidget(self.estop_button)

        # Spacer
        layout.addSpacing(10)

        # 2. Workflow step indicator (350px fixed width)
        self.workflow_indicator = WorkflowStepIndicator()
        self.workflow_indicator.setFixedWidth(350)
        layout.addWidget(self.workflow_indicator)

        # Spacer
        layout.addSpacing(10)

        # 2.5. Software Interlocks (compact status indicators)
        self.software_interlocks_widget = self._create_software_interlocks()
        layout.addWidget(self.software_interlocks_widget)

        # Stretch spacer (pushes remaining items to right)
        layout.addStretch()

        # 3. Safety status section (300px fixed width)
        self.safety_widget = self._create_safety_section()
        layout.addWidget(self.safety_widget)

        # Spacer
        layout.addSpacing(10)

        # 4. Theme toggle button (60px fixed width)
        self.theme_toggle_button = self._create_theme_toggle_button()
        layout.addWidget(self.theme_toggle_button)

        # Spacer
        layout.addSpacing(10)

        # 5. Research mode badge (150px fixed width)
        self.research_badge = self._create_research_badge()
        layout.addWidget(self.research_badge)

        logger.debug("Unified header UI created")

    def _create_estop_button(self) -> QPushButton:
        """Create emergency stop button (left section)."""
        button = QPushButton("EMERGENCY\nSTOP")
        button.setFixedSize(120, 60)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.EMERGENCY};
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #B71C1C;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #B71C1C;
            }}
            QPushButton:pressed {{
                background-color: #7F0000;
            }}
        """)
        button.setToolTip("Emergency stop - immediately disable treatment laser\nPress F12 or click here")
        button.clicked.connect(self._on_estop_clicked)

        logger.debug("E-Stop button created")
        return button

    def _create_safety_section(self) -> QWidget:
        """Create compact safety status section (center-right) - single line."""
        widget = QWidget()
        widget.setFixedWidth(350)  # Slightly wider for horizontal layout
        layout = QHBoxLayout()  # Changed to horizontal
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        widget.setLayout(layout)

        # Safety state label (compact, inline)
        self.safety_state_label = QLabel("SAFE:")
        self.safety_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.safety_state_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SAFE};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 4px;
                min-width: 75px;
            }}
        """)
        layout.addWidget(self.safety_state_label)

        # Create 4 interlock indicators (inline)
        self.footpedal_label = self._create_interlock_indicator("foot", False)
        self.smoothing_label = self._create_interlock_indicator("smooth", False)
        self.photodiode_label = self._create_interlock_indicator("photo", False)
        self.watchdog_label = self._create_interlock_indicator("watch", False)

        layout.addWidget(self.footpedal_label)
        layout.addWidget(self.smoothing_label)
        layout.addWidget(self.photodiode_label)
        layout.addWidget(self.watchdog_label)

        widget.setStyleSheet(f"background-color: {Colors.PANEL}; border-radius: 4px;")
        logger.debug("Safety section created")
        return widget

    def _create_software_interlocks(self) -> QWidget:
        """Create compact software interlocks status section (after workflow steps)."""
        widget = QWidget()
        widget.setFixedWidth(300)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        widget.setLayout(layout)

        # E-Stop status (most critical)
        self.estop_status_label = QLabel("E-Stop: CLEAR")
        self.estop_status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SAFE};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 85px;
            }}
        """)
        layout.addWidget(self.estop_status_label)

        # Power Limit status
        self.power_limit_label = QLabel("Power: OK")
        self.power_limit_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SAFE};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 75px;
            }}
        """)
        layout.addWidget(self.power_limit_label)

        # Session status
        self.session_status_label = QLabel("Session: --")
        self.session_status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SECONDARY};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 85px;
            }}
        """)
        layout.addWidget(self.session_status_label)

        widget.setStyleSheet(f"background-color: {Colors.PANEL}; border-radius: 4px;")
        logger.debug("Software interlocks section created")
        return widget

    def _create_interlock_indicator(self, name: str, satisfied: bool) -> QLabel:
        """
        Create a single interlock indicator (compact inline version).

        Args:
            name: Short name (e.g., "foot", "smooth")
            satisfied: Whether interlock is satisfied

        Returns:
            QLabel configured as interlock indicator
        """
        label = QLabel(f"{name}{'✓' if satisfied else '✗'}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedHeight(40)  # FDA compliant touch target (was 28px)
        label.setMinimumWidth(60)  # Maintain aspect ratio
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SAFE if satisfied else Colors.DANGER};
                color: white;
                font-size: 11px;
                font-weight: bold;
                border-radius: 3px;
                padding: 4px 6px;
            }}
        """)
        label.setToolTip(f"{'Satisfied' if satisfied else 'NOT satisfied'}: {name}")
        return label

    def _create_theme_toggle_button(self) -> QPushButton:
        """Create theme toggle button (light/dark mode switch)."""
        # Get initial theme icon
        icon = "☀" if get_current_theme() == ThemeMode.DARK else "🌙"

        button = QPushButton(icon)
        button.setFixedSize(60, 60)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                font-size: 24px;
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {Colors.TREATING};
            }}
        """)
        button.setToolTip("Toggle light/dark theme\nLight theme for bright clinical environments (500-1000 lux)")
        button.clicked.connect(self._on_theme_toggle)

        logger.debug("Theme toggle button created")
        return button

    def _create_research_badge(self) -> QWidget:
        """Create research mode warning badge (right section)."""
        widget = QWidget()
        widget.setFixedWidth(150)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        widget.setLayout(layout)

        label = QLabel("⚠ Research\nMode Only")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.WARNING};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }}
        """)
        label.setToolTip("NOT for clinical use - v0.9.14-alpha\nResearch and development only")
        layout.addWidget(label)

        logger.debug("Research badge created")
        return widget

    # Signal handlers

    @pyqtSlot()
    def _on_estop_clicked(self) -> None:
        """Handle E-Stop button click."""
        logger.critical("E-STOP ACTIVATED FROM UNIFIED HEADER")
        self.e_stop_clicked.emit()

    @pyqtSlot()
    def _on_theme_toggle(self) -> None:
        """Handle theme toggle button click."""
        new_theme = toggle_theme()
        logger.info(f"Theme toggled to: {new_theme.value}")

        # Update button icon
        icon = "☀" if new_theme == ThemeMode.DARK else "🌙"
        self.theme_toggle_button.setText(icon)

        # Rebuild this widget's stylesheet with new theme colors
        self._rebuild_stylesheets()

        # Notify main window to rebuild all widget stylesheets
        main_window = self.window()
        if main_window and hasattr(main_window, "_rebuild_all_stylesheets"):
            main_window._rebuild_all_stylesheets()
            logger.info("Main window notified to rebuild all stylesheets for theme change")

    def _rebuild_stylesheets(self) -> None:
        """Rebuild all inline stylesheets in unified header with new theme colors."""
        # Rebuild unified header background
        self.setStyleSheet(f"background-color: {Colors.HEADER}; border-bottom: 2px solid {Colors.BORDER_DEFAULT};")

        # Rebuild E-Stop button stylesheet
        self.estop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.EMERGENCY};
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #B71C1C;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #B71C1C;
            }}
            QPushButton:pressed {{
                background-color: #7F0000;
            }}
        """)

        # Rebuild safety state label stylesheet
        color = Colors.SAFE if self.current_safety_state == SafetyState.SAFE else Colors.DANGER
        self.safety_state_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 4px;
                min-width: 75px;
            }}
        """)

        # Rebuild safety widget background
        self.safety_widget.setStyleSheet(f"background-color: {Colors.PANEL}; border-radius: 4px;")

        # Rebuild interlock indicators
        self._update_interlock_indicator(self.footpedal_label, "foot", self.interlock_status.get("footpedal", False))
        self._update_interlock_indicator(self.smoothing_label, "smooth", self.interlock_status.get("smoothing", False))
        self._update_interlock_indicator(self.photodiode_label, "photo", self.interlock_status.get("photodiode", False))
        self._update_interlock_indicator(self.watchdog_label, "watch", self.interlock_status.get("watchdog", False))

        # Rebuild theme toggle button stylesheet
        self.theme_toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                font-size: 24px;
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {Colors.TREATING};
            }}
        """)

        # Rebuild research badge stylesheet
        self.research_badge.findChild(QLabel).setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.WARNING};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }}
        """)

    # Public slots for external updates

    @pyqtSlot(SafetyState)
    def update_safety_state(self, state: SafetyState) -> None:
        """
        Update safety status display.

        Args:
            state: New safety state (SAFE, UNSAFE, TREATING, etc.)
        """
        self.current_safety_state = state

        # Update label text (with colon for inline layout)
        if state == SafetyState.SAFE:
            text = "SAFE:"
            color = Colors.SAFE
        elif state == SafetyState.ARMED:
            text = "ARMED:"
            color = Colors.PRIMARY
        elif state == SafetyState.TREATING:
            text = "TREATING:"
            color = Colors.TREATING
        elif state == SafetyState.UNSAFE:
            text = "UNSAFE:"
            color = Colors.DANGER
        else:  # EMERGENCY_STOP
            text = "E-STOP:"
            color = Colors.EMERGENCY

        self.safety_state_label.setText(text)
        self.safety_state_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 4px;
                min-width: 75px;
            }}
        """)

        logger.info(f"Safety state updated to: {text}")

    @pyqtSlot(dict)
    def update_interlock_status(self, interlocks: dict) -> None:
        """
        Update interlock indicators.

        Args:
            interlocks: Dictionary with keys: footpedal, smoothing, photodiode, watchdog
                       Values: True (satisfied) or False (not satisfied)
        """
        self.interlock_status = interlocks

        # Update each indicator
        self._update_interlock_indicator(
            self.footpedal_label, "foot", interlocks.get("footpedal", False)
        )
        self._update_interlock_indicator(
            self.smoothing_label, "smooth", interlocks.get("smoothing", False)
        )
        self._update_interlock_indicator(
            self.photodiode_label, "photo", interlocks.get("photodiode", False)
        )
        self._update_interlock_indicator(
            self.watchdog_label, "watch", interlocks.get("watchdog", False)
        )

        logger.debug(f"Interlock status updated: {interlocks}")

    def _update_interlock_indicator(self, label: QLabel, name: str, satisfied: bool) -> None:
        """
        Update a single interlock indicator (FDA compliant touch target).

        Args:
            label: QLabel to update
            name: Short name for display
            satisfied: Whether interlock is satisfied
        """
        label.setText(f"{name}{'✓' if satisfied else '✗'}")
        label.setFixedHeight(40)  # Maintain FDA compliance on updates
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SAFE if satisfied else Colors.DANGER};
                color: white;
                font-size: 11px;
                font-weight: bold;
                border-radius: 3px;
                padding: 4px 6px;
            }}
        """)
        label.setToolTip(f"{'Satisfied' if satisfied else 'NOT satisfied'}: {name}")

    @pyqtSlot(int)
    def set_workflow_step(self, step: int) -> None:
        """
        Update current workflow step.

        Args:
            step: Step number (1, 2, or 3)
        """
        if 1 <= step <= 3:
            self.workflow_indicator.set_step(step)
            logger.debug(f"Workflow step updated to: {step}")
        else:
            logger.warning(f"Invalid workflow step: {step} (must be 1-3)")

    def update_software_interlocks(
        self, estop_active: bool, power_ok: bool, session_valid: bool, session_id: Optional[str] = None
    ) -> None:
        """
        Update software interlock status indicators.

        Args:
            estop_active: True if E-Stop is active (DANGER), False if clear (SAFE)
            power_ok: True if power limit is satisfied
            session_valid: True if valid session exists
            session_id: Optional session ID to display
        """
        # E-Stop status (inverted logic - active is bad)
        if estop_active:
            self.estop_status_label.setText("E-Stop: ACTIVE")
            self.estop_status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.DANGER};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 85px;
                }}
            """)
        else:
            self.estop_status_label.setText("E-Stop: CLEAR")
            self.estop_status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.SAFE};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 85px;
                }}
            """)

        # Power limit status
        if power_ok:
            self.power_limit_label.setText("Power: OK")
            self.power_limit_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.SAFE};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 75px;
                }}
            """)
        else:
            self.power_limit_label.setText("Power: LIMIT")
            self.power_limit_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.WARNING};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 75px;
                }}
            """)

        # Session status
        if session_valid and session_id:
            self.session_status_label.setText(f"Session: #{session_id}")
            self.session_status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.SAFE};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 85px;
                }}
            """)
        else:
            self.session_status_label.setText("Session: --")
            self.session_status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.SECONDARY};
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 3px;
                    min-width: 85px;
                }}
            """)

    # Convenience methods

    def get_current_safety_state(self) -> SafetyState:
        """Get current safety state."""
        return self.current_safety_state

    def get_interlock_status(self) -> dict:
        """Get current interlock status."""
        return self.interlock_status.copy()
