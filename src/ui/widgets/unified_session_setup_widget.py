"""
Unified Session Setup Widget for TOSCA Treatment Workflow.

Combines subject selection, technician selection, and protocol file picker
into a single, streamlined form for starting treatment sessions.

This widget replaces the previous scattered approach where subject selection,
technician input, and protocol configuration were handled separately.

Medical Device Context:
    - Single source of truth for session parameters
    - Validates all inputs before session creation
    - Prevents mid-session parameter changes (inputs disabled during treatment)
    - Emits signals for protocol loading and session state changes

Author: TOSCA Development Team
Date: 2025-11-05
Version: 0.9.15-alpha (Treatment Workflow Redesign)
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.session_manager import SessionManager
from database.db_manager import DatabaseManager
from ui.design_tokens import Colors

logger = logging.getLogger(__name__)


class UnifiedSessionSetupWidget(QWidget):
    """
    Unified session setup widget for Treatment Workflow tab.

    Combines:
    - Subject selection (dropdown from database)
    - Technician selection (dropdown)
    - Protocol file picker (JSON files)
    - Session start/end controls

    Signals:
        session_started(subject_id, technician, protocol_path):
            Emitted when user starts a new session
        session_ended():
            Emitted when user ends the active session
        protocol_loaded(protocol_path):
            Emitted when protocol is selected (for step display widget)
    """

    # Signals
    session_started = pyqtSignal(str, str, str)  # subject_id, technician, protocol_path
    session_ended = pyqtSignal()
    protocol_loaded = pyqtSignal(str)  # protocol_path

    def __init__(
        self,
        session_manager: SessionManager,
        db_manager: DatabaseManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize unified session setup widget.

        Args:
            session_manager: SessionManager instance for session lifecycle
            db_manager: DatabaseManager instance for subject/technician data
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.session_manager = session_manager
        self.db_manager = db_manager

        # State tracking
        self.protocol_file_path: Optional[str] = None
        self.current_session_id: Optional[int] = None
        self.session_active = False

        # Initialize UI
        self._init_ui()
        self._load_subjects()
        self._load_technicians()

        logger.info("UnifiedSessionSetupWidget initialized")

    def _init_ui(self) -> None:
        """Create unified session setup UI."""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        self.setLayout(layout)

        # Group box
        group = QGroupBox("Session Setup")
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Colors.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)
        group.setLayout(group_layout)

        # Subject selection
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 11pt; font-weight: normal;")
        group_layout.addWidget(subject_label)

        self.subject_dropdown = QComboBox()
        self.subject_dropdown.setMinimumHeight(40)  # Touch-friendly
        self.subject_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
            QComboBox:focus {{
                border: 2px solid {Colors.BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        group_layout.addWidget(self.subject_dropdown)

        # Add new subject button
        self.add_subject_btn = QPushButton("+ Add New Subject")
        self.add_subject_btn.setMinimumHeight(35)
        self.add_subject_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
            }}
        """)
        self.add_subject_btn.clicked.connect(self._on_add_subject_clicked)
        group_layout.addWidget(self.add_subject_btn)

        # Technician selection
        tech_label = QLabel("Technician:")
        tech_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 11pt; font-weight: normal;")
        group_layout.addWidget(tech_label)

        self.technician_dropdown = QComboBox()
        self.technician_dropdown.setMinimumHeight(40)  # Touch-friendly
        self.technician_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
            QComboBox:focus {{
                border: 2px solid {Colors.BORDER_FOCUS};
            }}
        """)
        group_layout.addWidget(self.technician_dropdown)

        # Protocol file selection
        protocol_label = QLabel("Treatment Protocol:")
        protocol_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 11pt; font-weight: normal;")
        group_layout.addWidget(protocol_label)

        # Protocol file display
        self.protocol_file_label = QLineEdit()
        self.protocol_file_label.setReadOnly(True)
        self.protocol_file_label.setPlaceholderText("No protocol selected")
        self.protocol_file_label.setMinimumHeight(40)
        self.protocol_file_label.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
        """)
        group_layout.addWidget(self.protocol_file_label)

        # Browse button
        self.browse_btn = QPushButton("Browse Protocols...")
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
            }}
        """)
        self.browse_btn.clicked.connect(self._on_browse_protocol_clicked)
        group_layout.addWidget(self.browse_btn)

        # Start/End session button
        self.session_button = QPushButton("START SESSION")
        self.session_button.setMinimumHeight(60)  # Large, prominent button
        self.session_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SAFE};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.CONNECTED};
            }}
            QPushButton:disabled {{
                background-color: {Colors.SECONDARY};
                color: {Colors.TEXT_DISABLED};
            }}
        """)
        self.session_button.clicked.connect(self._on_session_button_clicked)
        group_layout.addWidget(self.session_button)

        layout.addWidget(group)
        layout.addStretch()

        # Set fixed width for left column
        self.setFixedWidth(380)

        logger.debug("UnifiedSessionSetupWidget UI created")

    def _load_subjects(self) -> None:
        """Load subjects from database into dropdown."""
        try:
            subjects = self.db_manager.get_all_subjects()
            self.subject_dropdown.clear()
            self.subject_dropdown.addItem("Select Subject...", None)  # Placeholder

            for subject in subjects:
                # Subject model has subject_code (e.g., "P-2025-0001"), not name
                display_text = f"{subject.subject_code}"
                self.subject_dropdown.addItem(display_text, subject.subject_code)

            logger.info(f"Loaded {len(subjects)} subjects into dropdown")
        except Exception as e:
            logger.error(f"Failed to load subjects: {e}")
            QMessageBox.warning(self, "Database Error", f"Could not load subjects: {e}")

    def _load_technicians(self) -> None:
        """Load technicians into dropdown."""
        # Hardcoded list for now (can be moved to database later)
        technicians = [
            "Select Technician...",  # Placeholder
            "Dr. Smith",
            "Dr. Jones",
            "Technician A",
            "Technician B",
        ]

        self.technician_dropdown.clear()
        for tech in technicians:
            self.technician_dropdown.addItem(tech)

        logger.info(f"Loaded {len(technicians)-1} technicians into dropdown")

    @pyqtSlot()
    def _on_add_subject_clicked(self) -> None:
        """Handle add new subject button click."""
        from ui.dialogs.add_subject_dialog import AddSubjectDialog

        # Open dialog for adding new subject
        dialog = AddSubjectDialog(
            db_manager=self.db_manager, current_tech_id=1, parent=self  # Default tech_id=1 for dev mode
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Dialog accepted - subject was created
            subject_code = dialog.get_created_subject_code()
            logger.info(f"Subject created via dialog: {subject_code}")

            # Reload subjects dropdown to include new subject
            self._load_subjects()

            # Auto-select the newly created subject
            index = self.subject_dropdown.findData(subject_code)
            if index >= 0:
                self.subject_dropdown.setCurrentIndex(index)
                logger.info(f"Auto-selected new subject: {subject_code}")
        else:
            # Dialog cancelled
            logger.info("Add subject dialog cancelled")

    @pyqtSlot()
    def _on_browse_protocol_clicked(self) -> None:
        """Handle browse protocol button click."""
        # Open file dialog for protocol selection
        protocols_dir = Path("data/protocols")
        if not protocols_dir.exists():
            protocols_dir = Path(".")  # Fallback to current directory

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Treatment Protocol",
            str(protocols_dir),
            "Protocol Files (*.json);;All Files (*)",
        )

        if file_path:
            self.protocol_file_path = file_path
            self.protocol_file_label.setText(Path(file_path).name)
            logger.info(f"Protocol selected: {file_path}")

            # Emit signal for protocol steps display widget
            self.protocol_loaded.emit(file_path)

    @pyqtSlot()
    def _on_session_button_clicked(self) -> None:
        """Handle session button click (start or end session)."""
        if not self.session_active:
            self._start_session()
        else:
            self._end_session()

    def _start_session(self) -> None:
        """Start a new treatment session."""
        # Validate inputs
        subject_id = self.subject_dropdown.currentData()
        technician = self.technician_dropdown.currentText()
        protocol_path = self.protocol_file_path

        if not subject_id or subject_id is None:
            QMessageBox.warning(
                self, "Missing Information", "Please select a subject before starting the session."
            )
            return

        if not technician or technician == "Select Technician...":
            QMessageBox.warning(
                self, "Missing Information", "Please select a technician before starting the session."
            )
            return

        if not protocol_path:
            QMessageBox.warning(
                self, "Missing Information", "Please select a treatment protocol before starting the session."
            )
            return

        # Create session
        try:
            self.current_session_id = self.session_manager.create_session(
                subject_id=subject_id, technician=technician
            )

            # Update UI state
            self.session_active = True
            self._set_inputs_enabled(False)
            self.session_button.setText("END SESSION")
            self.session_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DANGER};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 12px;
                    font-size: 14pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.EMERGENCY};
                }}
            """)

            # Emit signals
            self.session_started.emit(subject_id, technician, protocol_path)

            logger.info(
                f"Session started: ID={self.current_session_id}, Subject={subject_id}, "
                f"Technician={technician}, Protocol={protocol_path}"
            )

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            QMessageBox.critical(self, "Session Error", f"Could not create session: {e}")

    def _end_session(self) -> None:
        """End the active treatment session."""
        if not self.current_session_id:
            return

        try:
            self.session_manager.end_session(self.current_session_id)

            # Update UI state
            self.session_active = False
            self.current_session_id = None
            self._set_inputs_enabled(True)
            self.session_button.setText("START SESSION")
            self.session_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.SAFE};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 12px;
                    font-size: 14pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.CONNECTED};
                }}
            """)

            # Emit signal
            self.session_ended.emit()

            logger.info(f"Session ended: ID={self.current_session_id}")

        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            QMessageBox.critical(self, "Session Error", f"Could not end session: {e}")

    def _set_inputs_enabled(self, enabled: bool) -> None:
        """
        Enable or disable input controls.

        Args:
            enabled: True to enable inputs, False to disable during active session
        """
        self.subject_dropdown.setEnabled(enabled)
        self.add_subject_btn.setEnabled(enabled)
        self.technician_dropdown.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)

    def cleanup(self) -> None:
        """Cleanup widget resources."""
        # End session if active
        if self.session_active and self.current_session_id:
            try:
                self.session_manager.end_session(self.current_session_id)
                logger.info(f"Session {self.current_session_id} ended during cleanup")
            except Exception as e:
                logger.error(f"Error ending session during cleanup: {e}")

        logger.info("UnifiedSessionSetupWidget cleanup complete")
