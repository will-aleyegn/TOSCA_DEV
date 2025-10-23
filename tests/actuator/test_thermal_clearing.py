#!/usr/bin/env python3
"""
Test different strategies for clearing thermal protection errors.
"""

import sys
import time
from pathlib import Path

# Import Xeryon library
xeryon_path = Path(__file__).parent / "components" / "actuator_module"
if str(xeryon_path) not in sys.path:
    sys.path.insert(0, str(xeryon_path))

from Xeryon import Stage, Xeryon


def test_thermal_clearing():
    """Test thermal protection clearing strategies."""
    print("\n=== Thermal Protection Clearing Test ===\n")

    # Create controller
    print("1. Creating controller...")
    controller = Xeryon(COM_port="COM3", baudrate=9600)
    axis = controller.addAxis(Stage.XLA_1250_5N, "X")

    print("2. Starting controller (this triggers thermal errors)...")
    controller.start()
    time.sleep(0.5)

    print("\n3. Initial status:")
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    # Strategy 1: Wait for errors to clear naturally
    print("\n4. Strategy 1: Wait 2 seconds for auto-clear...")
    time.sleep(2.0)
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    # Strategy 2: Send ENBL=1 multiple times
    print("\n5. Strategy 2: Send ENBL=1 five times...")
    for i in range(5):
        axis.sendCommand("ENBL=1")
        time.sleep(0.2)
        stat = axis.getData("STAT")
        print(
            f"   After ENBL {i+1}: STAT={stat}, Thermal1={axis.isThermalProtection1()}, Thermal2={axis.isThermalProtection2()}"
        )

    # Strategy 3: Send RSET then ENBL
    print("\n6. Strategy 3: Send RSET=0, wait, then ENBL=1...")
    axis.sendCommand("RSET=0")
    time.sleep(0.5)
    print(f"   After RSET: STAT={axis.getData('STAT')}")
    axis.sendCommand("ENBL=1")
    time.sleep(0.5)
    print(f"   After ENBL: STAT={axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    # Strategy 4: Check if thermal errors prevent movement
    print("\n7. Strategy 4: Can we move despite thermal errors?")
    print("   Trying small step (STEP=10)...")
    axis.sendCommand("STEP=10")
    time.sleep(1.0)
    print(f"   EPOS: {axis.getData('EPOS')}")
    print(f"   Motor moved: {axis.getData('EPOS') != 0}")

    # Final check
    print("\n8. Final status:")
    print(f"   STAT: {axis.getData('STAT')}")
    print(f"   Thermal1: {axis.isThermalProtection1()}")
    print(f"   Thermal2: {axis.isThermalProtection2()}")

    # Cleanup
    print("\n9. Stopping controller...")
    controller.stop()

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    try:
        test_thermal_clearing()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
