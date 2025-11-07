#!/usr/bin/env python3
"""
Debug script for homing failure diagnosis.

This script monitors the STAT register and other status information
during the homing sequence to identify why isSearchingIndex() returns False.
"""

import sys
import time
from pathlib import Path

# Import Xeryon library
xeryon_path = Path(__file__).parent / "components" / "actuator_module"
if str(xeryon_path) not in sys.path:
    sys.path.insert(0, str(xeryon_path))

from Xeryon import Stage, Xeryon


def print_status(axis, label="Status"):
    """Print detailed status information."""
    stat_value = axis.getData("STAT")
    print(f"\n{label}:")
    print(
        f"  STAT register: {stat_value} (0b{bin(int(stat_value) if stat_value else 0)[2:].zfill(24)})"
    )
    print(f"  isEncoderValid: {axis.isEncoderValid()}")
    print(f"  isSearchingIndex: {axis.isSearchingIndex()}")
    print(f"  isEncoderAtIndex: {axis.isEncoderAtIndex()}")
    print(f"  isMotorOn: {axis.isMotorOn()}")
    print(f"  isClosedLoop: {axis.isClosedLoop()}")
    print(f"  isPositionReached: {axis.isPositionReached()}")
    print(f"  isThermalProtection1: {axis.isThermalProtection1()}")
    print(f"  isThermalProtection2: {axis.isThermalProtection2()}")
    print(f"  isSafetyTimeoutTriggered: {axis.isSafetyTimeoutTriggered()}")
    print(f"  EPOS: {axis.getData('EPOS')}")
    print(f"  DPOS: {axis.getData('DPOS')}")


def debug_homing():
    """Debug homing sequence."""
    print("=== Homing Debug Script ===")
    print("\nThis script will:")
    print("1. Connect to the actuator")
    print("2. Monitor STAT register before INDX command")
    print("3. Send INDX=0 command")
    print("4. Monitor STAT register changes during homing")
    print("\nPress ENTER to continue...")
    input()

    # Create controller
    print("\n1. Creating controller...")
    controller = Xeryon(COM_port="COM3", baudrate=9600)

    # Add axis
    print("2. Adding axis (XLA_1250_5N)...")
    axis = controller.addAxis(Stage.XLA_1250_5N, "X")

    # Start controller
    print("3. Starting controller...")
    controller.start()
    time.sleep(0.5)  # Let hardware stabilize

    # Check initial status
    print_status(axis, "Initial status (before INDX command)")

    # Wait for a few updates to stabilize
    print("\n4. Waiting for status updates to stabilize...")
    for i in range(5):
        time.sleep(0.3)
        stat = axis.getData("STAT")
        print(f"  Update {i+1}: STAT={stat}, searching_index={axis.isSearchingIndex()}")

    # Now send INDX command manually and monitor
    print("\n5. Sending INDX=0 command...")
    axis.sendCommand("INDX=0")

    # Monitor status changes for 10 seconds
    print("\n6. Monitoring status for 10 seconds after INDX command...")
    start_time = time.time()
    last_stat = None

    while time.time() - start_time < 10:
        current_stat = axis.getData("STAT")

        # Print status change
        if current_stat != last_stat:
            elapsed = time.time() - start_time
            print(f"\n  [{elapsed:.2f}s] STAT changed: {last_stat} -> {current_stat}")

            if current_stat:
                stat_int = int(current_stat)
                print(f"    Binary: 0b{bin(stat_int)[2:].zfill(24)}")
                print(f"    Bit 9 (searching_index): {(stat_int >> 9) & 1}")
                print(f"    Bit 8 (encoder_valid): {(stat_int >> 8) & 1}")
                print(f"    Bit 7 (encoder_at_index): {(stat_int >> 7) & 1}")
                print(f"    isSearchingIndex(): {axis.isSearchingIndex()}")
                print(f"    isEncoderValid(): {axis.isEncoderValid()}")

            last_stat = current_stat

        time.sleep(0.1)

    # Final status
    print_status(axis, "Final status (after 10 seconds)")

    # Try to read the status immediately after sending INDX
    print("\n7. Testing immediate status read after INDX command...")
    axis.sendCommand("INDX=0")
    print(f"  Immediate read (no wait): isSearchingIndex={axis.isSearchingIndex()}")
    time.sleep(0.1)
    print(f"  After 100ms: isSearchingIndex={axis.isSearchingIndex()}")
    time.sleep(0.2)
    print(f"  After 300ms: isSearchingIndex={axis.isSearchingIndex()}")
    time.sleep(0.5)
    print(f"  After 800ms: isSearchingIndex={axis.isSearchingIndex()}")

    # Cleanup
    print("\n8. Stopping controller...")
    controller.stop()

    print("\n=== Debug Complete ===")


if __name__ == "__main__":
    try:
        debug_homing()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
