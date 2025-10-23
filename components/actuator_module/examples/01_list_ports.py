"""
List Available Serial Ports

This script detects all available COM ports on the system.
Use this to find the correct port for the Xeryon actuator.

Usage:
    python 01_list_ports.py
"""

import sys
from typing import List, Tuple

import serial.tools.list_ports


def list_available_ports() -> List[Tuple[str, str, str]]:
    """
    List all available serial ports.

    Returns:
        List of tuples: (port_name, description, hardware_id)
    """
    ports = serial.tools.list_ports.comports()
    return [(port.device, port.description, port.hwid) for port in sorted(ports)]


def main() -> int:
    """
    Main function to list serial ports.

    Returns:
        Exit code (0 for success)
    """
    print("=== Xeryon Actuator - Serial Port Detection ===\n")

    ports = list_available_ports()

    if not ports:
        print("No serial ports found.")
        print("\nTroubleshooting:")
        print("  1. Ensure Xeryon actuator is powered on")
        print("  2. Check USB cable connection")
        print("  3. Install USB-Serial drivers if needed")
        return 1

    print(f"Found {len(ports)} serial port(s):\n")

    for idx, (port, desc, hwid) in enumerate(ports, 1):
        print(f"{idx}. Port: {port}")
        print(f"   Description: {desc}")
        print(f"   Hardware ID: {hwid}")
        print()

    print("Next Steps:")
    print("  1. Identify the Xeryon controller port")
    print("  2. Run: python 02_connect_actuator.py <PORT>")
    print("     Example: python 02_connect_actuator.py COM3")

    return 0


if __name__ == "__main__":
    sys.exit(main())
