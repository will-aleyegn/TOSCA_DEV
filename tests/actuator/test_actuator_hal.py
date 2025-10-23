#!/usr/bin/env python3
"""
Test script for Actuator HAL

Tests connection, homing, and basic positioning with physical actuator.
"""

import logging
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.hardware.actuator_controller import ActuatorController

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_actuator() -> None:  # noqa: C901
    """Test actuator HAL functionality."""
    print("\n=== Actuator HAL Test ===")
    print("\nSAFETY NOTICE:")
    print("  - Test uses VERY SLOW speed (100)")
    print("  - Test uses VERY SHORT movements (50 µm + 25 µm)")
    print("  - Total travel: ~75 µm from home position")
    print("\nPress ENTER to continue or Ctrl+C to abort...")
    input()

    # Create QApplication (required for PyQt6 signals)
    app = QApplication(sys.argv)

    # Create controller
    controller = ActuatorController()

    # Connect signals
    controller.connection_changed.connect(
        lambda connected: print(f"Connection: {'CONNECTED' if connected else 'DISCONNECTED'}")
    )
    controller.status_changed.connect(lambda status: print(f"Status: {status}"))
    controller.position_changed.connect(lambda pos: print(f"Position: {pos:.1f} µm"))
    controller.position_reached.connect(lambda pos: print(f"Target reached: {pos:.1f} µm"))
    controller.homing_progress.connect(lambda msg: print(f"Homing: {msg}"))
    controller.error_occurred.connect(lambda err: print(f"ERROR: {err}"))

    # Test sequence
    def run_tests() -> None:
        """Execute test sequence."""
        print("\n--- Test 1: Connection ---")
        # Try COM3 first (common default)
        if not controller.connect("COM3"):
            print("Failed to connect on COM3")
            print("Please specify correct COM port:")
            com_port = input("COM port: ").strip()
            if not controller.connect(com_port):
                print("Connection failed. Exiting.")
                QTimer.singleShot(100, app.quit)
                return

        # Wait for position monitoring to start
        QTimer.singleShot(500, test_homing)

    def test_homing() -> None:
        """Test homing procedure."""
        print("\n--- Test 2: Homing (Index Finding) ---")

        status = controller.get_status_info()
        if status.get("homed"):
            print("Already homed! Skipping to positioning test.")
            QTimer.singleShot(500, test_positioning)
        else:
            print("Starting homing procedure...")
            controller.find_index()
            # Wait for homing to complete
            QTimer.singleShot(5000, check_homing_complete)

    def check_homing_complete() -> None:
        """Check if homing completed."""
        status = controller.get_status_info()
        if status.get("homed"):
            print("\nHoming successful!")
            QTimer.singleShot(1000, test_positioning)
        else:
            print("\nHoming in progress or failed.")
            print("Waiting longer...")
            QTimer.singleShot(3000, check_homing_complete)

    def test_positioning() -> None:
        """Test positioning."""
        print("\n--- Test 3: Absolute Positioning (SAFE: 50 µm) ---")

        # Set slow speed first
        print("Setting SLOW speed (100)...")
        controller.set_speed(100)  # Very slow movement

        # Move only 50 µm from home
        print("Moving to 50 µm (VERY SHORT TRAVEL)...")
        controller.set_position(50.0)

        # Wait for movement
        QTimer.singleShot(3000, test_relative)

    def test_relative() -> None:
        """Test relative movement."""
        print("\n--- Test 4: Relative Movement (SAFE: +25 µm) ---")

        # Step only +25 µm (very small)
        print("Stepping +25 µm (VERY SHORT TRAVEL)...")
        controller.make_step(25.0)

        # Wait for movement
        QTimer.singleShot(3000, test_status)

    def test_status() -> None:
        """Test status reporting."""
        print("\n--- Test 5: Status Information ---")

        status = controller.get_status_info()
        print("\nFinal Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Cleanup
        print("\n--- Test Complete ---")
        print("Disconnecting...")
        controller.disconnect()

        # Exit application
        QTimer.singleShot(500, app.quit)

    # Start test sequence
    QTimer.singleShot(100, run_tests)

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    test_actuator()
