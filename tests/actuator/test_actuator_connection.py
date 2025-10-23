#!/usr/bin/env python3
"""
Non-interactive actuator connection test.

Tests only connection and basic status - no movement.
"""

import logging
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.hardware.actuator_controller import ActuatorController

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_connection() -> int:
    """Test actuator connection only."""
    print("\n=== Actuator Connection Test ===\n")

    app = QApplication(sys.argv)
    controller = ActuatorController()

    success = False

    def do_test() -> None:
        nonlocal success
        print("Attempting connection on COM3...")

        if controller.connect("COM3"):
            print("\nConnection successful!")
            status = controller.get_status_info()
            print("\nStatus Information:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            success = True
        else:
            print("\nConnection failed.")
            print("Check:")
            print("  - Actuator powered on")
            print("  - USB cable connected")
            print("  - Correct COM port (try Device Manager)")

        controller.disconnect()
        QTimer.singleShot(100, app.quit)

    QTimer.singleShot(100, do_test)
    app.exec()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(test_connection())
