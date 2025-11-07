"""
Test runner for Line-Based Protocol Builder Widget.

Simple Qt application to test the protocol builder UI standalone.
"""

import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from core.protocol_line import LineBasedProtocol
from ui.widgets.line_protocol_builder import LineProtocolBuilderWidget

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestWindow(QMainWindow):
    """Simple test window for protocol builder."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOSCA Line Protocol Builder - Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create protocol builder widget
        self.protocol_builder = LineProtocolBuilderWidget()
        self.protocol_builder.protocol_ready.connect(self._on_protocol_ready)
        layout.addWidget(self.protocol_builder)

        logger.info("Test window initialized")

    def _on_protocol_ready(self, protocol: LineBasedProtocol):
        """Handle protocol ready signal."""
        logger.info(f"Protocol ready for execution: {protocol.protocol_name}")
        logger.info(f"  - Lines: {len(protocol.lines)}")
        logger.info(f"  - Loop count: {protocol.loop_count}")
        logger.info(f"  - Total duration: {protocol.calculate_total_duration():.1f}s")

        # Print line summaries
        for line in protocol.lines:
            logger.info(f"  - {line.get_summary()}")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show test window
    window = TestWindow()
    window.show()

    logger.info("Application started - load example protocols from examples/protocols/")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
