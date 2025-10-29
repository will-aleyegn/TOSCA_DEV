"""
View Sessions Dialog - displays session history.
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.database.db_manager import DatabaseManager
from src.database.models import Subject

logger = logging.getLogger(__name__)


class ViewSessionsDialog(QDialog):
    """
    Dialog to display session history.

    Shows a table of all sessions or sessions for a specific subject.
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        subject: Optional[Subject] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the View Sessions dialog.

        Args:
            db_manager: Database manager instance
            subject: Optional subject to filter sessions by
            parent: Parent widget
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.subject = subject
        self._init_ui()
        self._load_sessions()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        self.setWindowTitle("Session History")
        self.setModal(True)
        self.resize(900, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title label
        if self.subject:
            title_text = f"Sessions for Subject: {self.subject.subject_code}"
        else:
            title_text = "All Sessions"

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Session ID", "Subject ID", "Technician", "Start Time", "End Time", "Status"]
        )

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Session ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Subject ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Technician
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Start Time
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # End Time
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status

        # Make table read-only
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setMaximumWidth(100)
        layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _load_sessions(self) -> None:
        """Load sessions from database and populate table."""
        try:
            # Get sessions from database
            if self.subject:
                sessions = self.db_manager.get_all_sessions(subject_id=self.subject.subject_id)
            else:
                sessions = self.db_manager.get_all_sessions()

            # Set row count
            self.table.setRowCount(len(sessions))

            # Populate table
            for row, session in enumerate(sessions):
                # Session ID
                self.table.setItem(row, 0, QTableWidgetItem(str(session.session_id)))

                # Subject ID
                subject_code = session.subject.subject_code if session.subject else "Unknown"
                self.table.setItem(row, 1, QTableWidgetItem(subject_code))

                # Technician
                tech_name = session.technician.full_name if session.technician else "Unknown"
                self.table.setItem(row, 2, QTableWidgetItem(tech_name))

                # Start Time
                start_time = (
                    session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else ""
                )
                self.table.setItem(row, 3, QTableWidgetItem(start_time))

                # End Time
                end_time = (
                    session.end_time.strftime("%Y-%m-%d %H:%M:%S")
                    if session.end_time
                    else "In Progress"
                )
                self.table.setItem(row, 4, QTableWidgetItem(end_time))

                # Status
                status = session.status or "Unknown"
                status_item = QTableWidgetItem(status)

                # Color-code status
                if status == "completed":
                    status_item.setBackground(Qt.GlobalColor.green)
                elif status == "in_progress":
                    status_item.setBackground(Qt.GlobalColor.yellow)
                elif status == "aborted":
                    status_item.setBackground(Qt.GlobalColor.red)
                elif status == "paused":
                    status_item.setBackground(Qt.GlobalColor.cyan)

                self.table.setItem(row, 5, status_item)

            logger.info(f"Loaded {len(sessions)} sessions")

        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.table.setRowCount(0)
