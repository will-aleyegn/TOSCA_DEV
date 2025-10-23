"""
Find Index Position (Home)

This script finds the index (home) position of the Xeryon stage.
This MUST be done before absolute positioning commands will work correctly.

Usage:
    python 03_find_index.py [COM_PORT]

Example:
    python 03_find_index.py COM3
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from Xeryon import Axis, Stage, Units, Xeryon  # noqa: E402


def find_index(com_port: Optional[str] = None) -> int:
    """
    Find the index position of the Xeryon stage.

    Args:
        com_port: Serial port name. If None, prompts for input.

    Returns:
        Exit code (0 for success)
    """
    if com_port is None:
        com_port = input("Enter COM port (e.g., COM3): ").strip()

    print("\n=== Xeryon Actuator - Find Index Position ===")
    print(f"Port: {com_port}\n")

    try:
        # Create controller and axis
        controller = Xeryon(COM_port=com_port, baudrate=115200)
        axis = Axis(controller, "A", Stage.XLS_312)

        print("Starting controller...")
        controller.start()

        print("\nSearching for index position...")
        print("This may take 10-30 seconds depending on stage position.\n")

        start_time = time.time()

        # Find index (bidirectional search)
        success = axis.findIndex(direction=0)

        elapsed_time = time.time() - start_time

        if success:
            print(f"\n✓ Index found in {elapsed_time:.2f} seconds!")

            # Verify encoder is valid
            print(f"\nEncoder Valid: {axis.isEncoderValid()}")
            print(f"Position Reached: {axis.isPositionReached()}")

            # Get current position (in different units)
            axis.setUnits(Units.enc)
            pos_enc = axis.getEPOS()
            axis.setUnits(Units.mu)
            pos_um = axis.getEPOS()
            axis.setUnits(Units.mm)
            pos_mm = axis.getEPOS()

            print("\n=== Current Position ===")
            print(f"Encoder Units: {pos_enc}")
            print(f"Micrometers: {pos_um:.2f} µm")
            print(f"Millimeters: {pos_mm:.4f} mm")

            print("\nNext Steps:")
            print("  1. Run: python 04_absolute_positioning.py")
            print("     (Test moving to specific positions)")

        else:
            print("\n✗ Index search failed!")
            print("Check hardware and try again.")

        # Cleanup
        print("\nClosing connection...")
        controller.stop()

        return 0 if success else 1

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
    return find_index(com_port)


if __name__ == "__main__":
    sys.exit(main())
