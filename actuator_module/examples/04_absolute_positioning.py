"""
Absolute Positioning Test

This script tests absolute positioning (setDPOS) with the Xeryon stage.
Requires index to be found first (run 03_find_index.py).

Usage:
    python 04_absolute_positioning.py [COM_PORT]

Example:
    python 04_absolute_positioning.py COM3
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from Xeryon import Axis, Stage, Units, Xeryon  # noqa: E402


def test_absolute_positioning(com_port: Optional[str] = None) -> int:
    """
    Test absolute positioning commands.

    Args:
        com_port: Serial port name. If None, prompts for input.

    Returns:
        Exit code (0 for success)
    """
    if com_port is None:
        com_port = input("Enter COM port (e.g., COM3): ").strip()

    print("\n=== Xeryon Actuator - Absolute Positioning Test ===")
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
        print("\nWorking units: Micrometers (µm)")

        # Define test positions (for TOSCA ring size range)
        test_positions = [
            ("Minimum", 0),
            ("25%", 750),
            ("Middle", 1500),
            ("75%", 2250),
            ("Maximum", 3000),
        ]

        print("\n=== Testing Ring Size Range (0-3000 µm) ===\n")

        for name, target_um in test_positions:
            print(f"Moving to {name}: {target_um} µm...")

            start_time = time.time()
            axis.setDPOS(target_um, Units.mu)
            elapsed = time.time() - start_time

            # Verify position
            actual_um = axis.getEPOS()
            error_um = abs(actual_um - target_um)

            print(f"  Target: {target_um} µm")
            print(f"  Actual: {actual_um:.2f} µm")
            print(f"  Error: {error_um:.2f} µm")
            print(f"  Time: {elapsed:.3f} seconds")
            print(f"  Position Reached: {axis.isPositionReached()}")
            print()

            time.sleep(0.5)  # Brief pause between moves

        # Return to middle position
        print("Returning to middle position (1500 µm)...")
        axis.setDPOS(1500, Units.mu)

        print("\nAbsolute positioning test complete!")
        print("\nNext Steps:")
        print("  1. Run: python 05_relative_movement.py")
        print("     (Test incremental steps)")

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
    return test_absolute_positioning(com_port)


if __name__ == "__main__":
    sys.exit(main())
