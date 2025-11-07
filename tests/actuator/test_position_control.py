#!/usr/bin/env python3
"""
Test script for actuator position control.

Tests absolute positioning and relative movements with physical hardware.
SAFETY: Uses slow speed and small movements.
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


def test_position_control() -> None:  # noqa: C901
    """Test position control with safety limits."""
    print("\n=== Actuator Position Control Test ===")
    print("\nSAFETY NOTICE:")
    print("  - Slow speed (100)")
    print("  - Small movements only (0-500 µm range)")
    print("  - Tests: absolute positioning and relative steps")
    print("\nPress ENTER to continue or Ctrl+C to abort...")
    input()

    # Create QApplication
    app = QApplication(sys.argv)

    # Create controller
    controller = ActuatorController()

    # Test results
    test_results = {"connection": False, "homing": False, "absolute": False, "relative": False}

    # Connect signals
    controller.connection_changed.connect(
        lambda connected: print(f"Connection: {'CONNECTED' if connected else 'DISCONNECTED'}")
    )
    controller.status_changed.connect(lambda status: print(f"Status: {status}"))
    controller.position_changed.connect(lambda pos: print(f"  Position: {pos:.2f} µm"))
    controller.position_reached.connect(
        lambda pos: print(f"  # [DONE] Target reached: {pos:.2f} µm")
    )
    controller.error_occurred.connect(lambda err: print(f"ERROR: {err}"))

    def run_tests() -> None:
        """Execute test sequence."""
        print("\n--- Test 1: Connection ---")
        if not controller.connect("COM3"):
            print("Connection failed. Exiting.")
            QTimer.singleShot(100, app.quit)
            return

        test_results["connection"] = True

        # Wait for homing to complete (auto_home=True by default)
        QTimer.singleShot(2000, test_absolute_positioning)

    def test_absolute_positioning() -> None:
        """Test absolute positioning."""
        print("\n--- Test 2: Absolute Positioning ---")

        # Check if homed
        status = controller.get_status_info()
        if not status.get("homed"):
            print("ERROR: Actuator not homed. Cannot test positioning.")
            cleanup()
            return

        test_results["homing"] = True
        print("# [DONE] Actuator homed and ready")

        # Get current position
        current_pos = controller.get_position()
        print(f"Current position: {current_pos:.2f} µm")

        # Test 1: Move to 100 µm
        print("\nTest 2a: Moving to absolute position 100 µm...")
        controller.set_speed(100)  # Slow speed
        success = controller.set_position(100.0)

        if success:
            print("  Command sent successfully")
            # Wait for movement to complete
            QTimer.singleShot(5000, check_position_1)
        else:
            print("  Command failed!")
            cleanup()

    def check_position_1() -> None:
        """Check if position 1 reached."""
        current_pos = controller.get_position()
        target = 100.0
        error = abs(current_pos - target)

        print(f"\nPosition check: {current_pos:.2f} µm (target: {target:.2f} µm)")
        print(f"Error: {error:.2f} µm")

        if error <= 5.0:  # ±5 µm tolerance
            print("# [DONE] Position reached within tolerance")
            test_results["absolute"] = True
            # Continue to relative movement test
            QTimer.singleShot(1000, test_relative_movement)
        else:
            print("# [FAILED] Position error exceeds tolerance")
            cleanup()

    def test_relative_movement() -> None:
        """Test relative movements."""
        print("\n--- Test 3: Relative Movement ---")

        current_pos = controller.get_position()
        print(f"Current position: {current_pos:.2f} µm")

        # Test: Step +50 µm
        print("\nTest 3a: Stepping +50 µm...")
        success = controller.make_step(50.0)

        if success:
            print("  Command sent successfully")
            # Wait for movement
            QTimer.singleShot(3000, check_position_2)
        else:
            print("  Command failed!")
            cleanup()

    def check_position_2() -> None:
        """Check if relative step completed."""
        current_pos = controller.get_position()
        expected = 150.0  # 100 + 50
        error = abs(current_pos - expected)

        print(f"\nPosition check: {current_pos:.2f} µm (expected: {expected:.2f} µm)")
        print(f"Error: {error:.2f} µm")

        if error <= 5.0:
            print("# [DONE] Relative step successful")
            test_results["relative"] = True
            # Test negative step
            QTimer.singleShot(1000, test_negative_step)
        else:
            print("# [FAILED] Relative step error exceeds tolerance")
            cleanup()

    def test_negative_step() -> None:
        """Test negative step."""
        print("\nTest 3b: Stepping -100 µm (return to 50 µm)...")
        success = controller.make_step(-100.0)

        if success:
            print("  Command sent successfully")
            QTimer.singleShot(3000, check_position_3)
        else:
            print("  Command failed!")
            cleanup()

    def check_position_3() -> None:
        """Check final position."""
        current_pos = controller.get_position()
        expected = 50.0
        error = abs(current_pos - expected)

        print(f"\nPosition check: {current_pos:.2f} µm (expected: {expected:.2f} µm)")
        print(f"Error: {error:.2f} µm")

        if error <= 5.0:
            print("# [DONE] Negative step successful")
        else:
            print("# [FAILED] Negative step error exceeds tolerance")

        # All tests complete
        print_results()
        cleanup()

    def print_results() -> None:
        """Print test results summary."""
        print("\n=== Test Results ===")
        print(
            f"Connection:           {'# [DONE] PASS' if test_results['connection'] else '# [FAILED] FAIL'}"
        )
        print(
            f"Homing:              {'# [DONE] PASS' if test_results['homing'] else '# [FAILED] FAIL'}"
        )
        print(
            f"Absolute Positioning: {'# [DONE] PASS' if test_results['absolute'] else '# [FAILED] FAIL'}"
        )
        print(
            f"Relative Movement:    {'# [DONE] PASS' if test_results['relative'] else '# [FAILED] FAIL'}"
        )

        all_passed = all(test_results.values())
        print(
            f"\nOverall: {'# [DONE] ALL TESTS PASSED' if all_passed else '# [FAILED] SOME TESTS FAILED'}"
        )

    def cleanup() -> None:
        """Cleanup and exit."""
        print("\n--- Cleanup ---")
        print("Disconnecting...")
        controller.disconnect()
        QTimer.singleShot(500, app.quit)

    # Start test sequence
    QTimer.singleShot(100, run_tests)

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    test_position_control()
