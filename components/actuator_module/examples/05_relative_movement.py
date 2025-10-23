"""
Relative Movement Test

This script tests relative positioning (makeStep) with the Xeryon stage.
Useful for incremental adjustments during treatment.

Usage:
    python 05_relative_movement.py [COM_PORT]

Example:
    python 05_relative_movement.py COM3
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from Xeryon import Axis, Stage, Units, Xeryon  # noqa: E402


def test_relative_movement(com_port: Optional[str] = None) -> int:
    """
    Test relative movement commands (steps).

    Args:
        com_port: Serial port name. If None, prompts for input.

    Returns:
        Exit code (0 for success)
    """
    if com_port is None:
        com_port = input("Enter COM port (e.g., COM3): ").strip()

    print("\n=== Xeryon Actuator - Relative Movement Test ===")
    print(f"Port: {com_port}\n")

    try:
        # Create controller and axis
        controller = Xeryon(COM_port=com_port, baudrate=115200)
        axis = Axis(controller, "A", Stage.XLS_312)

        print("Starting controller...")
        controller.start()

        # Verify index is found
        if not axis.isEncoderValid():
            print("\n⚠ Warning: Encoder not valid. Finding index first...")
            axis.findIndex()

        # Set working units to micrometers
        axis.setUnits(Units.mu)

        # Move to middle position first
        print("\nMoving to starting position (1500 µm)...")
        axis.setDPOS(1500, Units.mu)
        start_pos = axis.getEPOS()
        print(f"Starting position: {start_pos:.2f} µm\n")

        # Define relative steps to test
        steps = [
            ("+100 µm", 100),
            ("+50 µm", 50),
            ("-75 µm", -75),
            ("+25 µm", 25),
            ("-100 µm", -100),
        ]

        print("=== Testing Relative Steps ===\n")

        for description, step_size in steps:
            before_pos = axis.getEPOS()

            print(f"Step: {description}")
            print(f"  Before: {before_pos:.2f} µm")

            start_time = time.time()
            axis.step(step_size)
            elapsed = time.time() - start_time

            after_pos = axis.getEPOS()
            actual_step = after_pos - before_pos

            print(f"  After: {after_pos:.2f} µm")
            print(f"  Actual step: {actual_step:.2f} µm")
            print(f"  Time: {elapsed:.3f} seconds")
            print()

            time.sleep(0.3)

        # Return to starting position
        final_pos = axis.getEPOS()
        print(f"Final position: {final_pos:.2f} µm")
        print(f"Net displacement: {final_pos - start_pos:.2f} µm")

        print("\nReturning to middle position...")
        axis.setDPOS(1500, Units.mu)

        print("\nRelative movement test complete!")
        print("\nNext Steps:")
        print("  1. Run: python 06_speed_and_limits.py")
        print("     (Test speed control and safety limits)")

        # Cleanup
        print("\nClosing connection...")
        controller.stop()

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        return 1


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code
    """
    com_port = sys.argv[1] if len(sys.argv) > 1 else None
    return test_relative_movement(com_port)


if __name__ == "__main__":
    sys.exit(main())
