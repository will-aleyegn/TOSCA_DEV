"""
Subject selection widget.
"""

import logging
import re
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
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

        layout.addWidget(QLabel("Subject ID:"))
        self.subject_id_input = QLineEdit()
        self.subject_id_input.setPlaceholderText("Enter subject ID (e.g., P-2025-0001)...")
        layout.addWidget(self.subject_id_input)

        self.search_button = QPushButton("Search Subject")
        self.search_button.clicked.connect(self._on_search_subject)
        layout.addWidget(self.search_button)

        self.create_button = QPushButton("Create New Subject")
        self.create_button.clicked.connect(self._on_create_subject)
        layout.addWidget(self.create_button)

        self.view_sessions_button = QPushButton("View Sessions")
        self.view_sessions_button.clicked.connect(self._on_view_sessions)
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

        layout.addWidget(QLabel("Technician ID:"))
        self.technician_id_input = QLineEdit()
        self.technician_id_input.setPlaceholderText("Enter technician ID (e.g., admin)...")
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

    @pyqtSlot()
    def _on_search_subject(self) -> None:
        """Handle search subject button click."""
        if not self.db_manager:
            self.subject_info_display.setText("Error: Database not initialized")
            return

        subject_code = self.subject_id_input.text().strip()
        if not subject_code:
            self.subject_info_display.setText("Please enter a subject ID")
            return

        # Validate subject code format
        if not SUBJECT_CODE_PATTERN.match(subject_code):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Subject ID must be in format 'P-YYYY-NNNN'\n\nExample: P-2025-0001",
            )
            return

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

        subject_code = self.subject_id_input.text().strip()
        if not subject_code:
            self.subject_info_display.setText("Please enter a subject ID")
            return

        # Validate subject code format
        if not SUBJECT_CODE_PATTERN.match(subject_code):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Subject ID must be in format 'P-YYYY-NNNN'\n\nExample: P-2025-0001",
            )
            return

        # Require technician ID before creating subject (fixes audit trail)
        tech_username = self.technician_id_input.text().strip()
        if not tech_username:
            QMessageBox.warning(
                self,
                "Technician Required",
                "Please enter Technician ID before creating subjects.\n\n"
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

        tech_username = self.technician_id_input.text().strip()
        if not tech_username:
            self.subject_info_display.setText("Please enter technician ID")
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

            self.subject_info_display.setText(
                f"Session started\n\n"
                f"Session ID: {session.session_id}\n"
                f"Subject: {self.current_subject.subject_code}\n"
                f"Technician: {tech.full_name}\n"
                f"Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Folder: {session.session_folder_path if session.session_folder_path else 'Not created'}"
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
