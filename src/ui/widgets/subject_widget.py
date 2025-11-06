"""
Subject selection widget.
"""

import logging
import re
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.session_manager import SessionManager
from database.db_manager import DatabaseManager
from database.models import Subject

logger = logging.getLogger(__name__)

# Subject code format validation pattern (P-YYYY-NNNN)
SUBJECT_CODE_PATTERN = re.compile(r"^P-\d{4}-\d{4}$")


class SubjectWidget(QWidget):
    """
    Subject selection and session initiation.

    Allows operator to:
    - Search/select subject
    - Create new subject
    - Enter technician ID
    - Start new treatment session
    """

    # Signals
    session_started = pyqtSignal(int)  # session_id
    session_ended = pyqtSignal()  # emitted when session ends

    def __init__(self) -> None:
        super().__init__()
        self.db_manager: Optional[DatabaseManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.current_subject: Optional[Subject] = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Constrain maximum width for compact subject selection
        self.setMaximumWidth(400)

        layout.addWidget(self._create_subject_group())
        layout.addWidget(self._create_session_group())
        layout.addStretch()

    def _create_subject_group(self) -> QGroupBox:
        """Create subject search and selection group."""
        group = QGroupBox("Subject Selection")
        layout = QVBoxLayout()

        # Subject ID with auto-fill prefix
        layout.addWidget(QLabel("Subject ID (last 4 digits):"))

        # Horizontal layout for prefix label + input
        id_layout = QHBoxLayout()

        # Auto-filled prefix (P-YYYY-)
        current_year = datetime.now().year
        self.subject_id_prefix = f"P-{current_year}-"

        prefix_label = QLabel(self.subject_id_prefix)
        prefix_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        id_layout.addWidget(prefix_label)

        # Input for last 4 digits only
        self.subject_id_input = QLineEdit()
        self.subject_id_input.setPlaceholderText("____")  # Format hint: 4 digits
        self.subject_id_input.setMaxLength(4)  # Only 4 digits
        self.subject_id_input.setFixedWidth(200)  # Increased from 80px
        self.subject_id_input.setMinimumHeight(40)  # Touch-friendly
        self.subject_id_input.textChanged.connect(self._validate_subject_id_input)  # Real-time validation
        id_layout.addWidget(self.subject_id_input)
        id_layout.addStretch()

        layout.addLayout(id_layout)

        # Helper text below input field
        self.subject_id_helper = QLabel("Enter last 4 digits (e.g., 0001)")
        self.subject_id_helper.setStyleSheet(
            "font-size: 10pt; font-style: italic; color: #757575; margin-top: 4px;"
        )
        layout.addWidget(self.subject_id_helper)

        # Validation error label (hidden by default)
        self.subject_id_error = QLabel("")
        self.subject_id_error.setStyleSheet(
            "font-size: 10pt; color: #F44336; margin-top: 4px;"
        )
        self.subject_id_error.setVisible(False)
        layout.addWidget(self.subject_id_error)

        # Button layout for proper spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Primary button (Search) - Blue background
        self.search_button = QPushButton("Search Subject")
        self.search_button.clicked.connect(self._on_search_subject)
        self.search_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #1976D2; "
            "  color: white; "
            "  font-size: 12pt; "
            "  font-weight: bold; "
            "  padding: 10px 20px; "
            "  border-radius: 4px; "
            "  min-height: 40px; "
            "  min-width: 140px; "
            "}"
            "QPushButton:hover { "
            "  background-color: #1565C0; "
            "}"
            "QPushButton:disabled { "
            "  background-color: #BDBDBD; "
            "  color: #757575; "
            "}"
        )
        button_layout.addWidget(self.search_button)

        # Secondary button (Create) - Gray background
        self.create_button = QPushButton("Create New")
        self.create_button.clicked.connect(self._on_create_subject)
        self.create_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #F5F5F5; "
            "  color: #424242; "
            "  border: 1px solid #BDBDBD; "
            "  font-size: 12pt; "
            "  padding: 10px 20px; "
            "  border-radius: 4px; "
            "  min-height: 40px; "
            "  min-width: 120px; "
            "}"
            "QPushButton:hover { "
            "  background-color: #EEEEEE; "
            "}"
            "QPushButton:disabled { "
            "  background-color: #FAFAFA; "
            "  color: #BDBDBD; "
            "}"
        )
        button_layout.addWidget(self.create_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Tertiary button (View Sessions) - Text link style
        self.view_sessions_button = QPushButton("View Sessions")
        self.view_sessions_button.clicked.connect(self._on_view_sessions)
        self.view_sessions_button.setStyleSheet(
            "QPushButton { "
            "  background-color: transparent; "
            "  color: #1976D2; "
            "  font-size: 11pt; "
            "  border: none; "
            "  padding: 8px 16px; "
            "  text-align: left; "
            "  text-decoration: underline; "
            "}"
            "QPushButton:hover { "
            "  color: #1565C0; "
            "}"
        )
        layout.addWidget(self.view_sessions_button)

        self.subject_info_display = QTextEdit()
        self.subject_info_display.setPlaceholderText("Subject information will appear here...")
        self.subject_info_display.setMaximumHeight(150)
        self.subject_info_display.setReadOnly(True)
        layout.addWidget(self.subject_info_display)

        group.setLayout(layout)
        return group

    def _create_session_group(self) -> QGroupBox:
        """Create session initiation group."""
        group = QGroupBox("Start Treatment Session")
        layout = QVBoxLayout()

        # Technician dropdown
        layout.addWidget(QLabel("Technician:"))
        self.technician_id_input = QComboBox()
        self.technician_id_input.setEditable(False)  # Dropdown only, no manual entry

        # Add technician options
        self.technician_id_input.addItem("Select Technician...", "")  # Default placeholder
        self.technician_id_input.addItem("Admin", "admin")
        self.technician_id_input.addItem("Will", "will")
        self.technician_id_input.addItem("Operator 1", "operator1")
        self.technician_id_input.addItem("Operator 2", "operator2")

        layout.addWidget(self.technician_id_input)

        # Create button layout
        button_layout = QHBoxLayout()

        self.start_session_button = QPushButton("Start Session")
        self.start_session_button.setEnabled(False)
        self.start_session_button.setMinimumHeight(50)
        self.start_session_button.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;"
        )
        self.start_session_button.clicked.connect(self._on_start_session)
        button_layout.addWidget(self.start_session_button)

        self.end_session_button = QPushButton("End Session")
        self.end_session_button.setEnabled(False)
        self.end_session_button.setMinimumHeight(50)
        self.end_session_button.setStyleSheet(
            "font-size: 16px; font-weight: bold; background-color: #F44336; color: white;"
        )
        self.end_session_button.clicked.connect(self._on_end_session)
        button_layout.addWidget(self.end_session_button)

        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def set_managers(self, db_manager: DatabaseManager, session_manager: SessionManager) -> None:
        """
        Set database and session managers.

        Args:
            db_manager: Database manager instance
            session_manager: Session manager instance
        """
        self.db_manager = db_manager
        self.session_manager = session_manager
        logger.info("Subject widget managers configured")

    def _validate_subject_id_input(self, text: str) -> None:
        """
        Real-time validation of subject ID input.

        Updates input field styling based on validation state:
        - Neutral: Gray border (empty or partial entry)
        - Valid: Green border with checkmark (4 digits)
        - Invalid: Red border with error message (non-digits or too long)

        Args:
            text: Current input text
        """
        # Clear error message
        self.subject_id_error.setVisible(False)

        if len(text) == 0:
            # Neutral state - empty field
            self.subject_id_input.setStyleSheet(
                "QLineEdit { "
                "  border: 1px solid #BDBDBD; "
                "  border-radius: 4px; "
                "  padding: 8px; "
                "  background-color: white; "
                "}"
            )
            return

        if len(text) < 4:
            # Invalid - too short
            self.subject_id_input.setStyleSheet(
                "QLineEdit { "
                "  border: 2px solid #F44336; "
                "  border-radius: 4px; "
                "  padding: 8px; "
                "  background-color: #FFEBEE; "
                "}"
            )
            self.subject_id_error.setText("Must be exactly 4 digits")
            self.subject_id_error.setVisible(True)
            return

        if text.isdigit() and len(text) == 4:
            # Valid - 4 digits
            self.subject_id_input.setStyleSheet(
                "QLineEdit { "
                "  border: 2px solid #4CAF50; "
                "  border-radius: 4px; "
                "  padding: 8px; "
                "  background-color: #E8F5E9; "
                "}"
            )
            return

        # Invalid - non-digit characters
        self.subject_id_input.setStyleSheet(
            "QLineEdit { "
            "  border: 2px solid #F44336; "
            "  border-radius: 4px; "
            "  padding: 8px; "
            "  background-color: #FFEBEE; "
            "}"
        )
        self.subject_id_error.setText("Only digits 0-9 allowed")
        self.subject_id_error.setVisible(True)

    @pyqtSlot()
    def _on_search_subject(self) -> None:
        """Handle search subject button click."""
        if not self.db_manager:
            self.subject_info_display.setText("Error: Database not initialized")
            return

        # Get last 4 digits and construct full subject code
        last_four = self.subject_id_input.text().strip()
        if not last_four:
            self.subject_info_display.setText("Please enter the last 4 digits of subject ID")
            return

        # Validate it's exactly 4 digits
        if not re.match(r"^\d{4}$", last_four):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Subject ID must be exactly 4 digits\n\nExample: 0001",
            )
            return

        subject_code = self.subject_id_prefix + last_four

        try:
            subject = self.db_manager.get_subject_by_code(subject_code)
            if subject:
                self.current_subject = subject
                session_count = self.db_manager.get_subject_session_count(subject.subject_id)
                info_text = (
                    f"Subject ID: {subject.subject_code}\n"
                    f"Created: {subject.created_date.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Previous sessions: {session_count}\n"
                )
                if subject.notes:
                    info_text += f"Notes: {subject.notes}\n"

                self.subject_info_display.setText(info_text)
                self.start_session_button.setEnabled(True)
                logger.info(f"Subject found: {subject_code}")
            else:
                self.current_subject = None
                self.subject_info_display.setText(
                    f"Subject '{subject_code}' not found.\nClick 'Create New Subject' to add."
                )
                self.start_session_button.setEnabled(False)
                logger.warning(f"Subject not found: {subject_code}")
        except Exception as e:
            logger.error(f"Database error searching for subject: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to search for subject.\n\nPlease check database connection.",
            )
            self.current_subject = None
            self.start_session_button.setEnabled(False)

    @pyqtSlot()
    def _on_create_subject(self) -> None:
        """Handle create new subject button click."""
        if not self.db_manager:
            self.subject_info_display.setText("Error: Database not initialized")
            return

        # Get last 4 digits and construct full subject code
        last_four = self.subject_id_input.text().strip()
        if not last_four:
            self.subject_info_display.setText("Please enter the last 4 digits of subject ID")
            return

        # Validate it's exactly 4 digits
        if not re.match(r"^\d{4}$", last_four):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Subject ID must be exactly 4 digits\n\nExample: 0001",
            )
            return

        subject_code = self.subject_id_prefix + last_four

        # Require technician ID before creating subject (fixes audit trail)
        tech_username = self.technician_id_input.currentData()  # Get username from combobox
        if not tech_username:
            QMessageBox.warning(
                self,
                "Technician Required",
                "Please select a Technician before creating subjects.\n\n"
                "This ensures proper audit trail for regulatory compliance.",
            )
            return

        try:
            # Verify technician exists
            tech = self.db_manager.get_technician_by_username(tech_username)
            if not tech:
                QMessageBox.warning(
                    self,
                    "Invalid Technician",
                    f"Technician '{tech_username}' not found.\n\n"
                    f"Please enter a valid technician ID.",
                )
                return

            # Check if subject already exists
            existing = self.db_manager.get_subject_by_code(subject_code)
            if existing:
                self.subject_info_display.setText(f"Subject '{subject_code}' already exists!")
                return

            # Create new subject with actual technician ID (fixes audit trail)
            subject = self.db_manager.create_subject(
                subject_code=subject_code,
                tech_id=tech.tech_id,  # Use actual technician, not hardcoded admin
            )
            self.current_subject = subject
            self.subject_info_display.setText(
                f"New subject created\n\n"
                f"Subject ID: {subject.subject_code}\n"
                f"Created: {subject.created_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Created by: {tech.full_name}\n"
                f"Previous sessions: 0"
            )
            self.start_session_button.setEnabled(True)
            logger.info(f"Subject created: {subject_code} by tech_id={tech.tech_id}")
        except Exception as e:
            logger.error(f"Database error creating subject: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to create subject.\n\nPlease check database connection.",
            )
            self.current_subject = None
            self.start_session_button.setEnabled(False)

    @pyqtSlot()
    def _on_start_session(self) -> None:
        """Handle start session button click."""
        if not self.db_manager or not self.session_manager:
            self.subject_info_display.setText("Error: Managers not initialized")
            return

        if not self.current_subject:
            self.subject_info_display.setText("Please select or create a subject first")
            return

        tech_username = self.technician_id_input.currentData()  # Get username from combobox
        if not tech_username:
            self.subject_info_display.setText("Please select a technician")
            return

        try:
            # Look up technician - NO silent fallback to admin
            tech = self.db_manager.get_technician_by_username(tech_username)
            if not tech:
                QMessageBox.warning(
                    self,
                    "Technician Not Found",
                    f"Technician '{tech_username}' not found.\n\n"
                    f"Please enter a valid technician ID to start the session.",
                )
                return

            # Update last login time
            self.db_manager.update_technician_last_login(tech.tech_id)

            # Create session (returns Optional[Session])
            session = self.session_manager.create_session(
                subject=self.current_subject,
                tech_id=tech.tech_id,
            )

            if not session:
                QMessageBox.critical(
                    self,
                    "Session Creation Failed",
                    "Failed to create treatment session.\n\n"
                    "Please check database connection and try again.",
                )
                return

            # Simplified display - status bar shows Subject/Tech/Duration (T3 implementation)
            # Only show unique information here to avoid redundancy
            self.subject_info_display.setText(
                f"✓ Session Active\n\n"
                f"Session ID: {session.session_id}\n"
                f"Start: {session.start_time.strftime('%H:%M:%S')}\n"
                f"Data: {session.session_folder_path if session.session_folder_path else 'Not created'}\n\n"
                f"→ See status bar for Subject/Tech/Duration"
            )

            # Disable controls after session start and enable end button
            self.start_session_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.create_button.setEnabled(False)
            self.subject_id_input.setEnabled(False)
            self.technician_id_input.setEnabled(False)
            self.end_session_button.setEnabled(True)

            # Emit signal for main window
            self.session_started.emit(session.session_id)

            logger.info(
                f"Session started: ID={session.session_id}, Subject={self.current_subject.subject_code}, "
                f"Tech={tech.full_name}"
            )
        except Exception as e:
            logger.error(f"Error starting session: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Session Error",
                f"Failed to start session.\n\nPlease check database connection.",
            )

    @pyqtSlot()
    def _on_end_session(self) -> None:
        """Handle end session button click."""
        if not self.session_manager:
            self.subject_info_display.setText("Error: Session manager not initialized")
            return

        # Confirm with user
        reply = QMessageBox.question(
            self,
            "End Session",
            "Are you sure you want to end the current session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # End the session (returns bool indicating success)
            success = self.session_manager.end_session()

            if success or success is None:  # None means old API, assume success
                # Re-enable all disabled controls
                self.search_button.setEnabled(True)
                self.create_button.setEnabled(True)
                self.subject_id_input.setEnabled(True)
                self.technician_id_input.setEnabled(True)
                self.technician_id_input.setCurrentIndex(0)  # Reset to "Select Technician..."
                self.start_session_button.setEnabled(True if self.current_subject else False)

                # Disable end session button
                self.end_session_button.setEnabled(False)

                # Update display
                self.subject_info_display.setText("Session ended successfully")

                # Emit signal
                self.session_ended.emit()

                logger.info("Session ended by user")
            else:
                QMessageBox.warning(
                    self,
                    "Session End Failed",
                    "Failed to end session properly.\n\nPlease check logs.",
                )
        except Exception as e:
            logger.error(f"Error ending session: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Session Error", f"Failed to end session.\n\nPlease contact support."
            )

    @pyqtSlot()
    def _on_view_sessions(self) -> None:
        """Handle view sessions button click."""
        if not self.db_manager:
            QMessageBox.warning(self, "Error", "Database manager not initialized")
            return

        # Import here to avoid circular imports
        from ui.widgets.view_sessions_dialog import ViewSessionsDialog

        # Create and show the dialog
        dialog = ViewSessionsDialog(self.db_manager, self.current_subject, self)
        dialog.exec()
