"""
Protocol Selector Widget - Enhanced protocol browsing and loading.

Provides a visual protocol library with preview and selection capabilities.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.protocol import Protocol

logger = logging.getLogger(__name__)


class ProtocolSelectorWidget(QWidget):
    """
    Enhanced protocol selector with visual library browser.

    Features:
    - Scans protocols/examples/ directory for available protocols
    - Displays protocol list with names and descriptions
    - Shows detailed preview of selected protocol
    - Allows loading from list or browsing for custom files
    - Emits signal when protocol is loaded
    """

    protocol_loaded = pyqtSignal(Protocol)  # Emitted when protocol successfully loaded

    def __init__(self) -> None:
        super().__init__()
        self.loaded_protocol: Optional[Protocol] = None
        self.protocols_dir = Path("protocols/examples")

        self._init_ui()
        self._scan_protocols()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Header
        header = QLabel("📚 Protocol Library")
        header.setStyleSheet(
            "font-size: 13px; font-weight: bold; padding: 6px; "
            "background-color: #424242; color: #64B5F6; border-radius: 3px;"
        )
        layout.addWidget(header)

        # Main content area (horizontal split)
        content_layout = QHBoxLayout()

        # Left: Protocol list
        list_group = QGroupBox("Available Protocols")
        list_layout = QVBoxLayout()

        self.protocol_list = QListWidget()
        self.protocol_list.setMinimumHeight(150)
        self.protocol_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.protocol_list.itemDoubleClicked.connect(self._on_list_double_click)
        list_layout.addWidget(self.protocol_list)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._scan_protocols)
        refresh_btn.setMaximumHeight(28)
        list_layout.addWidget(refresh_btn)

        list_group.setLayout(list_layout)
        content_layout.addWidget(list_group, 2)

        # Right: Protocol preview
        preview_group = QGroupBox("Protocol Details")
        preview_layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Select a protocol to view details...")
        self.preview_text.setStyleSheet("font-size: 11px; font-family: monospace;")
        self.preview_text.setMinimumHeight(150)
        preview_layout.addWidget(self.preview_text)

        preview_group.setLayout(preview_layout)
        content_layout.addWidget(preview_group, 3)

        layout.addLayout(content_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.load_btn = QPushButton("✓ Load Selected")
        self.load_btn.setEnabled(False)
        self.load_btn.setMinimumHeight(35)
        self.load_btn.setStyleSheet(
            "font-size: 12px; font-weight: bold; " "background-color: #4CAF50; color: white;"
        )
        self.load_btn.clicked.connect(self._on_load_selected)
        button_layout.addWidget(self.load_btn, 2)

        browse_btn = QPushButton("📁 Browse Files...")
        browse_btn.setMinimumHeight(35)
        browse_btn.setToolTip("Load protocol from custom location")
        browse_btn.clicked.connect(self._on_browse_clicked)
        button_layout.addWidget(browse_btn, 1)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("No protocol loaded")
        self.status_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def _scan_protocols(self) -> None:
        """Scan protocols directory and populate list."""
        self.protocol_list.clear()

        if not self.protocols_dir.exists():
            logger.warning(f"Protocols directory not found: {self.protocols_dir}")
            self.preview_text.setText(
                f"Protocol directory not found: {self.protocols_dir}\n\n"
                f"Create this directory and add protocol JSON files to use the library."
            )
            return

        # Find all JSON files in protocols directory
        json_files = list(self.protocols_dir.glob("*.json"))

        if not json_files:
            self.preview_text.setText(
                f"No protocol files found in {self.protocols_dir}\n\n"
                f"Add protocol JSON files to this directory to populate the library."
            )
            return

        # Load and display protocols
        for json_file in sorted(json_files):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                # Create list item with protocol name
                name = data.get("name", json_file.stem)
                description = data.get("description", "")

                item = QListWidgetItem(f"{name}")
                item.setToolTip(description)
                item.setData(Qt.ItemDataRole.UserRole, str(json_file))  # Store file path

                self.protocol_list.addItem(item)

            except Exception as e:
                logger.error(f"Failed to load protocol {json_file}: {e}")

        logger.info(f"Scanned {len(json_files)} protocol files")

    def _on_selection_changed(self) -> None:
        """Handle protocol selection change."""
        selected_items = self.protocol_list.selectedItems()

        if not selected_items:
            self.load_btn.setEnabled(False)
            self.preview_text.clear()
            return

        self.load_btn.setEnabled(True)

        # Load and display protocol details
        item = selected_items[0]
        file_path = Path(item.data(Qt.ItemDataRole.UserRole))

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Format preview
            name = data.get("name", "Unknown")
            version = data.get("version", "N/A")
            description = data.get("description", "No description")
            author = data.get("author", "Unknown")
            created = data.get("created_date", "Unknown")
            max_power = data.get("max_power_watts", 0)
            max_duration = data.get("max_duration_seconds", 0)
            actions = data.get("actions", [])

            preview = f"""Protocol: {name}
Version: {version}
Author: {author}
Created: {created}

Description:
{description}

Safety Limits:
  Max Power: {max_power} W
  Max Duration: {max_duration} s

Actions: {len(actions)} total
"""

            # Add action summary
            if actions:
                preview += "\nAction Sequence:\n"
                for i, action in enumerate(actions[:10], 1):  # Show first 10
                    action_type = action.get("action_type", "Unknown")
                    preview += f"  {i}. {action_type}\n"

                if len(actions) > 10:
                    preview += f"  ... and {len(actions) - 10} more\n"

            self.preview_text.setText(preview)

        except Exception as e:
            self.preview_text.setText(f"Error loading protocol details:\n{e}")
            logger.error(f"Failed to preview protocol {file_path}: {e}")

    def _on_list_double_click(self, item: QListWidgetItem) -> None:
        """Handle double-click on protocol list item."""
        self._on_load_selected()

    def _on_load_selected(self) -> None:
        """Load the currently selected protocol."""
        selected_items = self.protocol_list.selectedItems()

        if not selected_items:
            return

        item = selected_items[0]
        file_path = Path(item.data(Qt.ItemDataRole.UserRole))

        self._load_protocol_from_file(file_path)

    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Protocol File",
            str(Path.home()),
            "Protocol Files (*.json);;All Files (*)",
        )

        if file_path:
            self._load_protocol_from_file(Path(file_path))

    def _load_protocol_from_file(self, file_path: Path) -> None:
        """
        Load protocol from file and emit signal.

        Args:
            file_path: Path to protocol JSON file
        """
        try:
            with open(file_path, "r") as f:
                protocol_data = json.load(f)

            protocol = Protocol.from_dict(protocol_data)
            self.loaded_protocol = protocol

            self.status_label.setText(f"✓ Loaded: {protocol.name}")
            self.status_label.setStyleSheet(
                "color: #4CAF50; font-size: 11px; font-weight: bold; padding: 5px;"
            )

            # Emit signal
            self.protocol_loaded.emit(protocol)

            logger.info(f"Protocol loaded: {protocol.name} ({len(protocol.actions)} actions)")

        except FileNotFoundError:
            self.status_label.setText("❌ File not found")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; padding: 5px;")
        except json.JSONDecodeError as e:
            self.status_label.setText("❌ Invalid JSON")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; padding: 5px;")
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            self.status_label.setText("❌ Load failed")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; padding: 5px;")
            logger.error(f"Protocol load error: {e}")

    def get_loaded_protocol(self) -> Optional[Protocol]:
        """
        Get the currently loaded protocol.

        Returns:
            Loaded Protocol instance or None
        """
        return self.loaded_protocol
