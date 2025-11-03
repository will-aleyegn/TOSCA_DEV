#!/usr/bin/env python3
"""
Slow Accelerometer Test - Gives Arduino time to process
"""

import time

import serial

PORT = "COM6"
BAUDRATE = 9600


def send_command(ser, command):
    """Send command slowly and carefully."""
    # Clear input buffer
    ser.reset_input_buffer()

    # Send command with newline
    full_command = f"{command}\n"
    ser.write(full_command.encode("utf-8"))
    ser.flush()  # Wait for data to be sent

    # Give Arduino time to process (important!)
    time.sleep(0.8)

    # Read all available data
    response = ""
    while ser.in_waiting > 0:
        chunk = ser.read(ser.in_waiting)
        response += chunk.decode("utf-8", errors="ignore")
        time.sleep(0.1)  # Let more data arrive

    return response.strip()


def main():
    print("=" * 60)
    print("SLOW ACCELEROMETER TEST (MPU6050)")
    print("=" * 60)
    print("Using slower timing to avoid command truncation\n")

    try:
        # Open serial port
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"[OK] Connected to {PORT}\n")

        # Wait for Arduino boot
        print("Waiting 3 seconds for Arduino boot...")
        time.sleep(3)

        # Clear any startup messages
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print("Startup complete\n")

        # Test 1: Watchdog Reset
        print("[1/5] Testing watchdog reset...")
        resp = send_command(ser, "WDT_RESET")
        print(f"      Response: {resp[:50]}...")
        if "OK:WDT_RESET" in resp:
            print("      [OK] Watchdog responding\n")
        else:
            print("      [WARN] Unexpected response\n")

        # Test 2: Initialize Accelerometer
        print("[2/5] Initializing MPU6050...")
        resp = send_command(ser, "ACCEL_INIT")
        print(f"      Response: {resp[:80]}...")
        if "OK:ACCEL_INITIALIZED" in resp or "0x68" in resp:
            print("      [OK] MPU6050 detected at 0x68!\n")
        else:
            print("      [ERROR] Accelerometer not initialized\n")
            return

        # Keep alive
        send_command(ser, "WDT_RESET")

        # Test 3: Read Acceleration (single sample)
        print("[3/5] Reading single acceleration sample...")
        resp = send_command(ser, "GET_ACCEL")
        print(f"      Response: {resp}")

        if "ACCEL:" in resp:
            # Parse data
            for line in resp.split("\n"):
                if "ACCEL:" in line:
                    data = line.split("ACCEL:")[1].strip()
                    try:
                        x, y, z = map(float, data.split(","))
                        print(f"      [OK] X={x:.3f}g, Y={y:.3f}g, Z={z:.3f}g")

                        # Check if reasonable (Z should be ~1g if flat)
                        if 0.5 < z < 1.5:
                            print(f"      [OK] Z-axis looks correct (~1g gravity)\n")
                        else:
                            print(f"      [INFO] Check orientation (Z={z:.3f}g)\n")
                    except:
                        print(f"      [WARN] Could not parse: {data}\n")
        else:
            print(f"      [ERROR] No acceleration data received\n")

        # Keep alive
        send_command(ser, "WDT_RESET")

        # Test 4: Vibration Level
        print("[4/5] Reading vibration level...")
        resp = send_command(ser, "GET_VIBRATION_LEVEL")
        print(f"      Response: {resp}")

        if "VIBRATION:" in resp:
            for line in resp.split("\n"):
                if "VIBRATION:" in line:
                    vib = line.split("VIBRATION:")[1].strip()
                    print(f"      [OK] Vibration: {vib}g\n")
        else:
            print(f"      [ERROR] No vibration data\n")

        # Test 5: Full Status
        print("[5/5] Getting full system status...")
        resp = send_command(ser, "GET_STATUS")

        # Print relevant lines
        print("      System Status:")
        for line in resp.split("\n"):
            if any(
                keyword in line
                for keyword in ["Motor", "Laser", "Accelerometer", "Photodiode", "Watchdog"]
            ):
                print(f"      {line}")

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

        ser.close()

    except serial.SerialException as e:
        print(f"\n[ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\n[ABORT] Test cancelled")


if __name__ == "__main__":
    main()
