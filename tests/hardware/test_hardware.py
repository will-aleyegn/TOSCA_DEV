#!/usr/bin/env python3
"""
Hardware Detection Script for TOSCA
Identifies connected devices on available COM ports
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import time

import serial


def test_com_port(port_name: str, baudrate: int = 9600, timeout: float = 2.0):
    """
    Test if a COM port is accessible and try to identify the device.

    Args:
        port_name: COM port name (e.g., "COM3")
        baudrate: Baud rate to test
        timeout: Read timeout in seconds
    """
    print(f"\n{'='*60}")
    print(f"Testing {port_name} at {baudrate} baud...")
    print(f"{'='*60}")

    try:
        # Open the port
        ser = serial.Serial(
            port=port_name, baudrate=baudrate, timeout=timeout, write_timeout=timeout
        )

        print(f"✅ Successfully opened {port_name}")
        print(f"   - Baudrate: {baudrate}")
        print(f"   - Timeout: {timeout}s")

        # Try to read any existing data
        time.sleep(0.5)
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"   - Data in buffer: {data[:100]}")  # First 100 bytes
        else:
            print(f"   - No data in buffer")

        # Try to send a simple query (varies by device)
        print(f"\n   Attempting device identification...")

        # Try Arduino-style commands (GPIO controller)
        ser.write(b"STATUS\n")
        time.sleep(0.3)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(f"   - Response to 'STATUS': {response.strip()}")
            print(f"   - Likely: Arduino GPIO Controller")

        # Try Arroyo laser commands
        ser.write(b"*IDN?\n")
        time.sleep(0.3)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(f"   - Response to '*IDN?': {response.strip()}")
            print(f"   - Likely: Arroyo Laser Controller")

        # Try Xeryon actuator commands
        ser.write(b"?\n")  # Xeryon status query
        time.sleep(0.3)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(f"   - Response to '?': {response.strip()}")
            print(f"   - Likely: Xeryon Linear Actuator")

        ser.close()
        print(f"✅ Port closed successfully")

    except serial.SerialException as e:
        print(f"❌ Error opening {port_name}: {e}")
        print(f"   - Port may be in use by another application")
        print(f"   - Or device not connected/powered")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main hardware detection routine."""
    print("\n" + "=" * 60)
    print("TOSCA Hardware Detection Utility")
    print("=" * 60)
    print("\nThis script will test available COM ports and identify devices.")
    print("⚠️  WARNING: This will send test commands to connected devices.")
    print("    Ensure laser safety interlocks are disconnected!\n")

    input("Press Enter to continue, or Ctrl+C to abort...")

    # Detected ports
    available_ports = ["COM1", "COM3", "COM6"]

    # Test each port with common baudrates
    test_configs = [
        ("COM1", 9600),  # Generic
        ("COM3", 9600),  # Xeryon actuator (per config.yaml)
        ("COM3", 115200),  # Alternative baudrate
        ("COM6", 9600),  # Unknown
        ("COM6", 38400),  # Arroyo laser typical
        ("COM6", 115200),  # Arduino typical
    ]

    for port, baudrate in test_configs:
        if port in available_ports:
            test_com_port(port, baudrate)
            time.sleep(1)  # Pause between tests

    print("\n" + "=" * 60)
    print("Hardware Detection Complete")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review the output above to identify your devices")
    print("2. Update config.yaml with correct COM ports")
    print("3. Run TOSCA GUI with: python src/main.py")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Detection aborted by user")
        sys.exit(0)
