#!/usr/bin/env python3
"""
Test initialization WITHOUT calling reset() to see if thermal errors disappear.
"""

import sys
import time
from pathlib import Path

# Import Xeryon library
xeryon_path = Path(__file__).parent / "components" / "actuator_module"
if str(xeryon_path) not in sys.path:
    sys.path.insert(0, str(xeryon_path))

from Xeryon import Stage, Units, Xeryon


def test_no_reset():
    """Test initialization without reset()."""
    print("\n=== Test: Initialize WITHOUT reset() ===\n")

    # Create controller
    print("1. Creating controller...")
    controller = Xeryon(COM_port="COM3", baudrate=9600)

    print("2. Adding axis...")
    axis = controller.addAxis(Stage.XLA_1250_5N, "X")

    print("3. Starting communication (without controller.start())...")
    # Manually start communication without calling start() which does reset()
    comm = controller.getCommunication().start()

    print("4. Waiting for communication to stabilize...")
    time.sleep(0.5)

    print("\n5. Checking status BEFORE reset:")
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    print("\n6. Sending settings (without reset)...")
    controller.readSettings()
    controller.sendMasterSettings()
    axis.sendSettings()

    print("\n7. Sending ENBL=1...")
    axis.sendCommand("ENBL=1")
    time.sleep(0.3)

    print("\n8. Checking status AFTER settings (no reset):")
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    # Try setting units
    print("\n9. Setting units to micrometers...")
    axis.setUnits(Units.mu)

    # Check encoder status
    print("\n10. Checking encoder status:")
    print(f"    encoder_valid: {axis.isEncoderValid()}")
    print(f"    encoder_at_index: {axis.isEncoderAtIndex()}")

    # Try homing
    print("\n11. Attempting to find index...")
    print("    Sending INDX=0...")
    axis.sendCommand("INDX=0")

    # Monitor for 5 seconds
    print("    Monitoring for 5 seconds...")
    for i in range(25):
        time.sleep(0.2)
        stat = axis.getData("STAT")
        searching = axis.isSearchingIndex()
        thermal1 = axis.isThermalProtection1()
        thermal2 = axis.isThermalProtection2()
        encoder_valid = axis.isEncoderValid()

        if i % 5 == 0:  # Print every second
            print(
                f"    [{i*0.2:.1f}s] STAT={stat}, searching={searching}, thermal1={thermal1}, thermal2={thermal2}, valid={encoder_valid}"
            )

        if encoder_valid:
            print("\n    *** INDEX FOUND! ***")
            break

    print("\n12. Final status:")
    print(f"    STAT: {axis.getData('STAT')}")
    print(f"    encoder_valid: {axis.isEncoderValid()}")
    print(f"    Thermal1: {axis.isThermalProtection1()}")
    print(f"    Thermal2: {axis.isThermalProtection2()}")

    # Cleanup
    print("\n13. Stopping...")
    controller.stop()

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    try:
        test_no_reset()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
