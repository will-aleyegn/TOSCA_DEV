"""
Camera connection status widget for Hardware & Diagnostics tab.

Provides simple connection management without the full camera display.
"""

import logging

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class CameraConnectionWidget(QWidget):
    """
    Simple camera connection status and control widget.

    Provides:
    - Connection status indicator
    - Connect/Disconnect buttons
    - Basic camera info (resolution, FPS)

    This widget is a lightweight companion to the full CameraWidget,
    designed for the Hardware & Diagnostics tab.
    """

    def __init__(self, camera_widget) -> None:
        """
        Initialize camera connection widget.

        Args:
            camera_widget: Reference to main CameraWidget for control delegation
        """
        super().__init__()
        self.camera_widget = camera_widget
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Connection status indicator
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("● Disconnected")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Camera info
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Camera not connected")
        self.info_label.setStyleSheet("color: #888; padding: 8px;")
        info_layout.addWidget(self.info_label)
        layout.addLayout(info_layout)

        # Connection controls - compact fixed-width buttons
        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(150)  # Fixed width instead of stretch
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; font-weight: bold; }"
            "QPushButton:hover { background-color: #1565C0; }"
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        button_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedWidth(150)  # Fixed width instead of stretch
        self.disconnect_btn.setMinimumHeight(35)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        button_layout.addWidget(self.disconnect_btn)

        button_layout.addStretch()  # Push buttons to left, leave right space empty

        layout.addLayout(button_layout)
        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect to camera widget signals."""
        if self.camera_widget:
            # Monitor connection status changes
            # Camera widget will update our status via _on_connection_changed
            pass

    def _on_connect_clicked(self) -> None:
        """Handle connect button click - delegate to main camera widget."""
        if self.camera_widget and hasattr(self.camera_widget, "connect_camera"):
            logger.info("Camera connection requested from Hardware tab")
            self.camera_widget.connect_camera()
            # Status will update via camera widget's connection_changed signal

    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click - delegate to main camera widget."""
        if self.camera_widget and hasattr(self.camera_widget, "disconnect_camera"):
            logger.info("Camera disconnection requested from Hardware tab")
            self.camera_widget.disconnect_camera()
            # Status will update via camera widget's connection_changed signal

    def update_connection_status(self, connected: bool) -> None:
        """
        Update connection status display.

        Args:
            connected: True if camera connected, False otherwise
        """
        if connected:
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)

            # Update info if camera controller available
            if (
                self.camera_widget
                and hasattr(self.camera_widget, "camera_controller")
                and self.camera_widget.camera_controller
            ):
                controller = self.camera_widget.camera_controller
                info_text = "Camera connected"
                if hasattr(controller, "get_frame_size"):
                    try:
                        width, height = controller.get_frame_size()
                        info_text += f"\nResolution: {width}x{height}"
                    except Exception:
                        pass
                if hasattr(self.camera_widget, "current_fps"):
                    fps = self.camera_widget.current_fps
                    info_text += f"\nFPS: {fps:.1f}"
                self.info_label.setText(info_text)
            else:
                self.info_label.setText("Camera connected")
        else:
            self.status_label.setText("● Disconnected")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.info_label.setText("Camera not connected")

    def cleanup(self) -> None:
        """Cleanup widget resources."""
        # Nothing to clean up - main camera widget handles cleanup
        pass
