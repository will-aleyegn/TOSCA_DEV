"""
Camera display and alignment widget.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class CameraWidget(QWidget):
    """
    Live camera feed with alignment indicators.

    Displays:
    - Camera feed (placeholder)
    - Ring detection overlay
    - Focus quality indicator
    - Alignment status
    """

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self._create_camera_display(), 3)
        layout.addWidget(self._create_control_panel(), 1)

    def _create_camera_display(self) -> QGroupBox:
        """Create camera feed display area."""
        group = QGroupBox("Live Camera Feed")
        layout = QVBoxLayout()

        self.camera_display = QLabel("Camera feed will appear here")
        self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_display.setMinimumSize(800, 600)
        self.camera_display.setStyleSheet(
            "background-color: #2b2b2b; color: #888; font-size: 16px;"
        )
        layout.addWidget(self.camera_display)

        self.status_label = QLabel("Camera: Not Connected")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        group.setLayout(layout)
        return group

    def _create_control_panel(self) -> QGroupBox:
        """Create camera control panel."""
        group = QGroupBox("Camera Controls")
        layout = QVBoxLayout()

        self.connect_button = QPushButton("Connect Camera")
        layout.addWidget(self.connect_button)

        self.capture_button = QPushButton("Capture Frame")
        self.capture_button.setEnabled(False)
        layout.addWidget(self.capture_button)

        layout.addWidget(QLabel("Alignment Status:"))
        self.ring_status = QLabel("Ring: Not Detected")
        self.ring_status.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.ring_status)

        self.focus_status = QLabel("Focus: N/A")
        self.focus_status.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.focus_status)

        layout.addStretch()

        group.setLayout(layout)
        return group
