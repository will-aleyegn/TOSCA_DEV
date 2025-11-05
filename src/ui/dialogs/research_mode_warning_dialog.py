"""
Module: Research Mode Warning Dialog
Project: TOSCA Laser Control System

Purpose: Display warning dialog for research-only mode on startup.
         Requires explicit acknowledgment that system is not approved for clinical use.
Safety Critical: No
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

logger = logging.getLogger(__name__)


class ResearchModeWarningDialog(QDialog):
    """
    Warning dialog for research mode acknowledgment.

    Displays a prominent warning that the system is for research use only
    and requires the user to acknowledge understanding before proceeding.

    Features:
    - Large warning icon
    - Clear warning message
    - Checkbox requiring explicit acknowledgment
    - OK button (disabled until checkbox checked)
    - Cancel button (exits application)
    """

    def __init__(self, parent=None):
        """
        Initialize research mode warning dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("RESEARCH MODE WARNING")
        self.setModal(True)
        self.setMinimumWidth(600)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Warning icon and title
        title_layout = QHBoxLayout()

        # Warning icon (using QMessageBox icon)
        icon_label = QLabel()
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
        icon_label.setPixmap(icon.pixmap(64, 64))
        title_layout.addWidget(icon_label)

        # Title
        title_label = QLabel("RESEARCH MODE - NOT FOR CLINICAL USE")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #D32F2F;")
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label, 1)

        layout.addLayout(title_layout)

        # Warning message
        warning_text = (
            "This system is configured for RESEARCH USE ONLY.\n\n"
            "CRITICAL WARNINGS:\n"
            "• This software is NOT FDA-cleared or approved for clinical use\n"
            "• Database encryption is NOT implemented - all data stored in plaintext\n"
            "• User authentication is NOT implemented - no access controls\n"
            "• NOT suitable for protected health information (PHI)\n"
            "• NOT suitable for patient treatment\n\n"
            "This system is intended for:\n"
            "• Research and development\n"
            "• Hardware testing and calibration\n"
            "• Algorithm development\n"
            "• Educational purposes\n\n"
            "Do NOT use this system for:\n"
            "• Clinical patient treatment\n"
            "• Protected health information (PHI) storage\n"
            "• Production medical device operation\n"
            "• Any regulated medical environment"
        )

        message_label = QLabel(warning_text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            "font-size: 10pt; padding: 15px; "
            "background-color: #FFF3E0; border: 2px solid #F57C00; border-radius: 5px;"
        )
        layout.addWidget(message_label)

        # Acknowledgment checkbox
        self.acknowledge_checkbox = QCheckBox(
            "I understand this is research-only software and NOT for clinical use"
        )
        self.acknowledge_checkbox.setStyleSheet("font-size: 11pt; font-weight: bold;")
        self.acknowledge_checkbox.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.acknowledge_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel (Exit Application)")
        self.cancel_button.setStyleSheet("font-size: 10pt; padding: 8px;")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.ok_button = QPushButton("OK - I Understand")
        self.ok_button.setEnabled(False)  # Disabled until checkbox checked
        self.ok_button.setStyleSheet(
            "font-size: 10pt; font-weight: bold; padding: 8px; "
            "background-color: #4CAF50; color: white;"
        )
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        logger.info("Research mode warning dialog initialized")

    def _on_checkbox_changed(self, state: int) -> None:
        """
        Handle checkbox state change.

        Enables/disables OK button based on checkbox state.

        Args:
            state: Qt.CheckState value
        """
        is_checked = state == Qt.CheckState.Checked.value
        self.ok_button.setEnabled(is_checked)

        if is_checked:
            logger.info("User acknowledged research mode warning")
        else:
            logger.debug("User unchecked acknowledgment checkbox")

    def exec(self) -> int:
        """
        Execute dialog and return result.

        Returns:
            QDialog.DialogCode (Accepted or Rejected)
        """
        result = super().exec()

        if result == QDialog.DialogCode.Accepted:
            logger.info("Research mode warning accepted - continuing startup")
        else:
            logger.warning("Research mode warning rejected - application will exit")

        return result
