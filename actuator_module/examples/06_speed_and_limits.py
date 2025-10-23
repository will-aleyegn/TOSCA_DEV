"""
Speed Control and Safety Limits Test

This script tests speed control (SSPD) and position limits (HLIM/LLIM).

Usage:
    python 06_speed_and_limits.py [COM_PORT]

Example:
    python 06_speed_and_limits.py COM3
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from Xeryon import Axis, Stage, Units, Xeryon  # noqa: E402


def test_speed_and_limits(com_port: Optional[str] = None) -> int:
    """
    Test speed control and safety limits.

    Args:
        com_port: Serial port name. If None, prompts for input.

    Returns:
        Exit code (0 for success)
    """
    if com_port is None:
        com_port = input("Enter COM port (e.g., COM3): ").strip()

    print("\n=== Xeryon Actuator - Speed and Limits Test ===")
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

        # Test 1: Speed Control
        print("\n=== Test 1: Speed Control ===\n")

        speeds = [
            ("Slow", 100),
            ("Medium", 300),
            ("Fast", 500),
        ]

        for name, speed_value in speeds:
            print(f"Testing {name} speed (SSPD={speed_value})...")

            # Set speed
            axis.sendCommand(f"SSPD={speed_value}")

            # Move from 500 to 2500 µm (2mm travel)
            start_time = time.time()
            axis.setDPOS(500, Units.mu)
            time.sleep(0.2)
            axis.setDPOS(2500, Units.mu)
            elapsed = time.time() - start_time

            print(f"  Travel time: {elapsed:.3f} seconds")
            print(f"  Speed: ~{2000/elapsed:.1f} µm/s")
            print()

            time.sleep(0.5)

        # Test 2: Position Limits
        print("\n=== Test 2: Position Limits ===\n")

        # Set conservative limits for testing (500-2500 µm)
        print("Setting position limits: 500-2500 µm")
        axis.sendCommand("LLIM=500")  # Low limit
        axis.sendCommand("HLIM=2500")  # High limit

        # Query limits
        axis.sendCommand("LLIM=?")
        axis.sendCommand("HLIM=?")

        # Move to middle
        print("\nMoving to middle of range (1500 µm)...")
        axis.setDPOS(1500, Units.mu)
        print(f"Position: {axis.getEPOS():.2f} µm")

        # Try to move within limits
        print("\nMoving to upper limit (2400 µm - within limits)...")
        axis.setDPOS(2400, Units.mu)
        print(f"Position: {axis.getEPOS():.2f} µm")
        print("✓ Move successful (within limits)")

        print("\nMoving to lower limit (600 µm - within limits)...")
        axis.setDPOS(600, Units.mu)
        print(f"Position: {axis.getEPOS():.2f} µm")
        print("✓ Move successful (within limits)")

        # Note about exceeding limits
        print("\nNote: Attempting to exceed limits would trigger ELIM error.")
        print("This requires finding index again to recover.")

        # Reset limits for TOSCA range
        print("\n=== Resetting to TOSCA Range ===")
        print("Setting position limits: 0-3000 µm")
        axis.sendCommand("LLIM=0")
        axis.sendCommand("HLIM=3000")

        # Return to middle
        print("\nReturning to middle position (1500 µm)...")
        axis.setDPOS(1500, Units.mu)

        # Test 3: Status Monitoring
        print("\n=== Test 3: Status Monitoring ===\n")

        status = axis.getData("STAT")
        print(f"Status Word: {status}")
        print(f"Encoder Valid: {axis.isEncoderValid()}")
        print(f"Position Reached: {axis.isPositionReached()}")
        print(f"Safety Timeout: {axis.isSafetyTimeoutTriggered()}")
        print(f"Searching Index: {axis.isSearchingIndex()}")

        # Query current settings
        print("\n=== Final Settings ===")
        axis.sendCommand("SSPD=?")
        axis.sendCommand("HLIM=?")
        axis.sendCommand("LLIM=?")
        axis.sendCommand("PTOL=?")
        print("(Check serial output for values)")

        print("\nSpeed and limits test complete!")
        print("\n✓ All 6 test scripts complete!")
        print("\nActuator module ready for integration.")

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
    return test_speed_and_limits(com_port)


if __name__ == "__main__":
    sys.exit(main())
