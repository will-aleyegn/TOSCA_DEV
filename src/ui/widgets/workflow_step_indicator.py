"""
Workflow Step Indicator Widget

Visual indicator showing treatment workflow progression:
1. Select Subject
2. Load Protocol
3. Begin Treatment

Author: TOSCA Development Team
Date: 2025-11-05
Version: 0.9.13-alpha
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class WorkflowStepIndicator(QWidget):
    """
    Visual workflow step indicator for treatment workflow.

    Shows progression through:
    1. Select Subject (default active)
    2. Load Protocol (after session started)
    3. Begin Treatment (after protocol loaded)

    Usage:
        indicator = WorkflowStepIndicator()
        indicator.set_step(2)  # Activate step 2
    """

    def __init__(self, parent=None):
        """Initialize workflow step indicator."""
        super().__init__(parent)
        self.current_step = 1

        # Store step widgets for dynamic updates
        self.step_widgets = []

        self._init_ui()

    def _init_ui(self):
        """Create step indicator UI (compact version for unified header)."""
        layout = QHBoxLayout()
        layout.setSpacing(8)  # Compact spacing
        layout.setContentsMargins(8, 6, 8, 6)  # Minimal margins

        # Step 1: Select Subject
        step1 = self._create_step_widget(
            number=1,
            title="Subject",  # Shortened
            status="active"  # Start with step 1 active
        )
        self.step_widgets.append(step1)
        layout.addWidget(step1)

        # Arrow connector
        layout.addWidget(self._create_arrow())

        # Step 2: Load Protocol
        step2 = self._create_step_widget(
            number=2,
            title="Protocol",  # Shortened
            status="pending"
        )
        self.step_widgets.append(step2)
        layout.addWidget(step2)

        # Arrow connector
        layout.addWidget(self._create_arrow())

        # Step 3: Begin Treatment
        step3 = self._create_step_widget(
            number=3,
            title="Treat",  # Shortened
            status="pending"
        )
        self.step_widgets.append(step3)
        layout.addWidget(step3)

        self.setLayout(layout)

        # Transparent background for unified header integration
        self.setStyleSheet(
            "WorkflowStepIndicator { "
            "  background-color: transparent; "
            "  border: none; "
            "}"
        )

    def set_step(self, step: int):
        """
        Update current workflow step.

        Args:
            step: Step number (1, 2, or 3)
                1 = Select Subject (active)
                2 = Load Protocol (step 1 complete, step 2 active)
                3 = Begin Treatment (steps 1-2 complete, step 3 active)
        """
        if step < 1 or step > 3:
            return

        self.current_step = step

        # Update all step widgets
        for i, widget in enumerate(self.step_widgets):
            step_num = i + 1

            if step_num < step:
                # Previous steps: Complete
                self._update_step_styling(widget, "complete")
            elif step_num == step:
                # Current step: Active
                self._update_step_styling(widget, "active")
            else:
                # Future steps: Pending
                self._update_step_styling(widget, "pending")

    def _create_step_widget(self, number: int, title: str, status: str) -> QWidget:
        """
        Create individual step widget (compact version).

        Args:
            number: Step number (1, 2, or 3)
            title: Step title text
            status: Initial status ("pending", "active", or "complete")

        Returns:
            QWidget containing step display
        """
        widget = QWidget()
        widget.setFixedSize(95, 55)  # Compact size for header

        # Store status for easy updates
        widget.setProperty("status", status)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)

        # Step number and title
        title_label = QLabel(f"{number}. {title}")
        title_label.setObjectName("step_title")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)  # Increased from 9pt for clinical readability
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(False)
        layout.addWidget(title_label)

        # Status indicator
        status_label = QLabel("")
        status_label.setObjectName("step_status")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(8)  # Compact font size
        status_font.setBold(True)
        status_label.setFont(status_font)
        layout.addWidget(status_label)

        widget.setLayout(layout)

        # Apply initial styling
        self._update_step_styling(widget, status)

        return widget

    def _update_step_styling(self, widget: QWidget, status: str):
        """
        Update step widget styling based on status.

        Args:
            widget: Step widget to update
            status: New status ("pending", "active", or "complete")
        """
        widget.setProperty("status", status)

        # Get child labels
        title_label = widget.findChild(QLabel, "step_title")
        status_label = widget.findChild(QLabel, "step_status")

        if status == "pending":
            # Pending: Gray, not started
            widget.setStyleSheet(
                "QWidget { "
                "  background-color: #F5F5F5; "
                "  border: 1px solid #E0E0E0; "
                "  border-radius: 6px; "
                "}"
            )
            if title_label:
                title_label.setStyleSheet("color: #9E9E9E;")
            if status_label:
                status_label.setText("○ PENDING")
                status_label.setStyleSheet("color: #9E9E9E;")

        elif status == "active":
            # Active: Blue, in progress
            widget.setStyleSheet(
                "QWidget { "
                "  background-color: #E3F2FD; "
                "  border: 2px solid #1976D2; "
                "  border-radius: 6px; "
                "}"
            )
            if title_label:
                title_label.setStyleSheet("color: #1976D2;")
            if status_label:
                status_label.setText("● ACTIVE")
                status_label.setStyleSheet("color: #1976D2; font-weight: bold;")

        elif status == "complete":
            # Complete: Green, finished
            widget.setStyleSheet(
                "QWidget { "
                "  background-color: #E8F5E9; "
                "  border: 1px solid #4CAF50; "
                "  border-radius: 6px; "
                "}"
            )
            if title_label:
                title_label.setStyleSheet("color: #2E7D32;")
            if status_label:
                status_label.setText("✓ COMPLETE")
                status_label.setStyleSheet("color: #2E7D32; font-weight: bold;")

    def _create_arrow(self) -> QLabel:
        """
        Create arrow connector between steps (compact version).

        Returns:
            QLabel with arrow character
        """
        arrow = QLabel("→")
        arrow.setStyleSheet(
            "font-size: 18px; "  # Smaller arrow
            "color: #9E9E9E; "
            "font-weight: bold; "
            "padding: 0 4px;"  # Minimal padding
        )
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return arrow
