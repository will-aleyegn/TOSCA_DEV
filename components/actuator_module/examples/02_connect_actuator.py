"""
Connect to Xeryon Actuator

This script connects to the Xeryon controller and retrieves stage information.

Usage:
    python 02_connect_actuator.py [COM_PORT]

Example:
    python 02_connect_actuator.py COM3
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import Xeryon
sys.path.insert(0, str(Path(__file__).parent.parent))

from Xeryon import Axis, Stage, Xeryon  # noqa: E402


def connect_and_get_info(com_port: Optional[str] = None) -> int:
    """
    Connect to Xeryon controller and display information.

    Args:
        com_port: Serial port name (e.g., "COM3"). If None, prompts for input.

    Returns:
        Exit code (0 for success)
    """
    if com_port is None:
        com_port = input("Enter COM port (e.g., COM3): ").strip()

    print("\n=== Xeryon Actuator - Connection Test ===")
    print(f"Port: {com_port}")
    print("Baudrate: 115200\n")

    try:
        # Create controller
        controller = Xeryon(COM_port=com_port, baudrate=115200)

        # Create axis (XLS-312 stage for TOSCA)
        axis = Axis(controller, "A", Stage.XLS_312)

        print("Starting controller...")
        controller.start()

        print("\nController Started Successfully!\n")

        # Get stage information
        print("=== Stage Information ===")
        print(f"Axis Letter: {axis.axis_letter}")
        print(f"Stage Type: {axis.stage}")
        print(f"Current Units: {axis.units}")

        # Query basic settings
        print("\n=== Current Settings ===")
        axis.sendCommand("SSPD=?")
        print("Scan Speed (SSPD): (check serial output)")

        axis.sendCommand("HLIM=?")
        print("High Limit (HLIM): (check serial output)")

        axis.sendCommand("LLIM=?")
        print("Low Limit (LLIM): (check serial output)")

        # Get status
        print("\n=== Current Status ===")
        status = axis.getData("STAT")
        print(f"Status Word: {status}")
        print(f"Encoder Valid: {axis.isEncoderValid()}")
        print(f"Position Reached: {axis.isPositionReached()}")
        print(f"Safety Timeout: {axis.isSafetyTimeoutTriggered()}")

        # Cleanup
        print("\nClosing connection...")
        controller.stop()

        print("\nConnection test successful!")
        print("\nNext Steps:")
        print("  1. Run: python 03_find_index.py")
        print("     (Required before positioning works)")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify correct COM port")
        print("  2. Check actuator is powered on")
        print("  3. Ensure no other software is using the port")
        return 1


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code
    """
    com_port = sys.argv[1] if len(sys.argv) > 1 else None
    return connect_and_get_info(com_port)


if __name__ == "__main__":
    sys.exit(main())
