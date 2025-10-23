#!/usr/bin/env python3
"""
Test which specific setting triggers thermal protection.
Send settings one at a time to isolate the culprit.
"""

import sys
import time
from pathlib import Path

xeryon_path = Path(__file__).parent / "components" / "actuator_module"
if str(xeryon_path) not in sys.path:
    sys.path.insert(0, str(xeryon_path))

from Xeryon import Stage, Xeryon


def test_setting(axis, tag, value, label):
    """Test sending a single setting and check if it triggers thermal error."""
    print(f"\n  Testing: {tag}={value} ({label})")

    # Get status before
    stat_before = axis.getData("STAT")
    thermal_before = axis.isThermalProtection1() or axis.isThermalProtection2()

    # Send setting
    axis.sendCommand(f"{tag}={value}")
    time.sleep(0.3)  # Wait for hardware to process

    # Get status after
    stat_after = axis.getData("STAT")
    thermal_after = axis.isThermalProtection1() or axis.isThermalProtection2()

    # Report
    if thermal_after and not thermal_before:
        print(f"    *** TRIGGERED THERMAL ERROR! ***")
        print(f"    STAT: {stat_before} -> {stat_after}")
        return True
    elif thermal_after:
        print(f"    Still has thermal error (was already present)")
        return False
    else:
        print(f"    OK - No thermal error")
        return False


def main():
    print("\n=== Minimal Settings Test ===")
    print("Testing which setting triggers thermal protection...\n")

    # Create controller
    print("1. Creating controller...")
    controller = Xeryon(COM_port="COM3", baudrate=9600)
    axis = controller.addAxis(Stage.XLA_1250_5N, "X")

    print("2. Starting communication...")
    comm = controller.getCommunication().start()
    time.sleep(0.5)

    print("\n3. Initial status:")
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal errors: {axis.isThermalProtection1() or axis.isThermalProtection2()}")

    # Test critical settings one by one
    print("\n4. Testing settings individually...")

    culprits = []

    # Stage type command (this is sent first by sendSettings())
    if test_setting(axis, "XLA3", "1250", "Stage type"):
        culprits.append("XLA3=1250")

    # Frequency settings
    if test_setting(axis, "FREQ", "87000", "Excitation frequency zone 1"):
        culprits.append("FREQ=87000")

    if test_setting(axis, "FRQ2", "85000", "Excitation frequency zone 2"):
        culprits.append("FRQ2=85000")

    # Amplitude settings
    if test_setting(axis, "AMPL", "45", "Open-loop amplitude"):
        culprits.append("AMPL=45")

    if test_setting(axis, "MAMP", "45", "Max closed-loop amplitude"):
        culprits.append("MAMP=45")

    if test_setting(axis, "MIMP", "20", "Min closed-loop amplitude"):
        culprits.append("MIMP=20")

    # Control factors
    if test_setting(axis, "PROP", "120", "Proportional factor zone 1"):
        culprits.append("PROP=120")

    if test_setting(axis, "PRO2", "60", "Proportional factor zone 2"):
        culprits.append("PRO2=60")

    if test_setting(axis, "INTF", "15", "Integral factor"):
        culprits.append("INTF=15")

    # Encoder settings
    if test_setting(axis, "ENCO", "-32", "Encoder offset"):
        culprits.append("ENCO=-32")

    # Summary
    print("\n5. Summary:")
    if culprits:
        print(f"   Settings that triggered thermal errors:")
        for setting in culprits:
            print(f"     - {setting}")
    else:
        print("   No single setting triggered thermal errors")
        print("   (May require combination or different issue)")

    print(f"\n6. Final STAT: {axis.getData('STAT')}")

    # Cleanup
    print("\n7. Stopping...")
    controller.stop()

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
