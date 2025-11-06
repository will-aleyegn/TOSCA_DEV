"""
Add Subject Dialog for TOSCA Treatment Workflow.

Provides a form-based interface for creating new subject records with validation
and duplicate checking. Generates subject codes in the format P-YYYY-NNNN.

Medical Device Context:
    - Validates all inputs before database insertion
    - Checks for duplicate subject codes
    - Generates sequential subject IDs by year
    - Maintains audit trail of who created each subject

Author: TOSCA Development Team
Date: 2025-11-06
Version: 0.9.16-alpha (Code Review Fixes - Phase 2)
"""

import logging
import re
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from database.db_manager import DatabaseManager
from ui.design_tokens import Colors

logger = logging.getLogger(__name__)


class AddSubjectDialog(QDialog):
    """
    Dialog for adding new subject records to the database.

    Features:
    - Auto-generates subject codes in format P-YYYY-NNNN
    - Optional date of birth and gender fields
    - Notes field for additional information
    - Duplicate subject code validation
    - Creates subject in database on acceptance

    Returns:
        subject_code (str): The newly created subject code, or None if cancelled
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        current_tech_id: int = 1,
        parent: Optional[QDialog] = None,
    ) -> None:
        """
        Initialize add subject dialog.

        Args:
            db_manager: DatabaseManager instance for subject creation
            current_tech_id: ID of technician creating the subject (default: 1 for dev mode)
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.db_manager = db_manager
        self.current_tech_id = current_tech_id
        self.created_subject_code: Optional[str] = None

        self.setWindowTitle("Add New Subject")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._init_ui()
        self._generate_subject_code()

        logger.info("AddSubjectDialog initialized")

    def _init_ui(self) -> None:
        """Create dialog UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        self.setLayout(layout)

        # Title label
        title = QLabel("Add New Subject")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Subject Code (auto-generated, read-only)
        self.subject_code_input = QLineEdit()
        self.subject_code_input.setReadOnly(True)
        self.subject_code_input.setPlaceholderText("P-YYYY-NNNN (auto-generated)")
        self.subject_code_input.setMinimumHeight(35)
        self.subject_code_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
        """
        )
        form_layout.addRow("Subject Code*:", self.subject_code_input)

        # Date of Birth (optional)
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(datetime.now().date())
        self.dob_input.setMinimumHeight(35)
        self.dob_input.setStyleSheet(
            f"""
            QDateEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
            QDateEdit::drop-down {{
                border: none;
            }}
        """
        )
        form_layout.addRow("Date of Birth:", self.dob_input)

        # Gender (optional)
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Not Specified", "Male", "Female", "Other"])
        self.gender_input.setMinimumHeight(35)
        self.gender_input.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """
        )
        form_layout.addRow("Gender:", self.gender_input)

        # Notes (optional)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes about this subject...")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(120)
        self.notes_input.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
        """
        )
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        # Info label
        info_label = QLabel("* Subject code is automatically generated")
        info_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 9pt; font-style: italic;")
        layout.addWidget(info_label)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.BORDER_DEFAULT};
            }}
        """
        )
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("Create Subject")
        self.create_btn.setMinimumHeight(40)
        self.create_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.CONNECTED};
            }}
        """
        )
        self.create_btn.clicked.connect(self._on_create_clicked)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

        logger.debug("AddSubjectDialog UI created")

    def _generate_subject_code(self) -> None:
        """
        Generate next sequential subject code for current year.

        Format: P-YYYY-NNNN (e.g., P-2025-0001)

        Algorithm:
        1. Get all existing subjects for current year
        2. Find highest sequence number
        3. Increment by 1
        4. Zero-pad to 4 digits
        """
        try:
            current_year = datetime.now().year
            prefix = f"P-{current_year}-"

            # Get all subjects for this year
            all_subjects = self.db_manager.get_all_subjects()
            year_subjects = [s for s in all_subjects if s.subject_code.startswith(prefix)]

            if not year_subjects:
                # First subject of the year
                next_number = 1
            else:
                # Find highest sequence number
                sequence_numbers = []
                for subject in year_subjects:
                    # Extract NNNN from P-YYYY-NNNN
                    match = re.search(r"-(\d{4})$", subject.subject_code)
                    if match:
                        sequence_numbers.append(int(match.group(1)))

                next_number = max(sequence_numbers) + 1 if sequence_numbers else 1

            # Generate code with zero-padding
            subject_code = f"P-{current_year}-{next_number:04d}"
            self.subject_code_input.setText(subject_code)

            logger.info(f"Generated subject code: {subject_code}")

        except Exception as e:
            logger.error(f"Failed to generate subject code: {e}")
            QMessageBox.critical(
                self, "Generation Error", f"Could not generate subject code: {e}\n\nPlease try again."
            )
            self.reject()

    def _on_create_clicked(self) -> None:
        """Handle create button click."""
        # Validate inputs
        subject_code = self.subject_code_input.text().strip()
        if not subject_code:
            QMessageBox.warning(self, "Invalid Input", "Subject code is required.")
            return

        # Validate subject code format
        if not re.match(r"^P-\d{4}-\d{4}$", subject_code):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Subject code must be in format P-YYYY-NNNN (e.g., P-2025-0001).",
            )
            return

        # Check for duplicate
        existing = self.db_manager.get_subject_by_code(subject_code)
        if existing:
            QMessageBox.warning(
                self,
                "Duplicate Subject",
                f"Subject {subject_code} already exists in the database.\n\n"
                "Please use a different subject code.",
            )
            return

        # Parse optional fields
        dob = self.dob_input.date().toPyDate()
        gender = self.gender_input.currentText()
        if gender == "Not Specified":
            gender = None
        notes = self.notes_input.toPlainText().strip()
        if not notes:
            notes = None

        # Create subject in database
        try:
            subject = self.db_manager.create_subject(
                subject_code=subject_code,
                tech_id=self.current_tech_id,
                date_of_birth=datetime.combine(dob, datetime.min.time()),
                gender=gender,
                notes=notes,
            )

            self.created_subject_code = subject.subject_code
            logger.info(
                f"Subject created successfully: {subject.subject_code} "
                f"(tech_id={self.current_tech_id}, dob={dob}, gender={gender})"
            )

            QMessageBox.information(
                self,
                "Subject Created",
                f"Subject {subject.subject_code} has been created successfully!",
            )

            self.accept()

        except Exception as e:
            logger.error(f"Failed to create subject: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to create subject: {e}\n\nPlease check the logs and try again.",
            )

    def get_created_subject_code(self) -> Optional[str]:
        """
        Get the subject code that was created by this dialog.

        Returns:
            Subject code string, or None if dialog was cancelled
        """
        return self.created_subject_code
