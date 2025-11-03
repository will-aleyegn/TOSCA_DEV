#!/usr/bin/env python3
"""
I2C Scanner for TOSCA Watchdog
Helps diagnose accelerometer detection issues
"""

import time

import serial

PORT = "COM6"
BAUDRATE = 9600


def main():
    print("=" * 60)
    print("I2C ACCELEROMETER DIAGNOSTIC TOOL")
    print("=" * 60)

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"[OK] Connected to {PORT}\n")

        # Wait for Arduino startup
        print("Waiting for Arduino startup...")
        time.sleep(3)

        # Clear any startup messages
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print("\nStartup messages received:")
            print("-" * 60)
            print(startup)
            print("-" * 60)

        # Keep watchdog alive
        print("\n[INFO] Sending WDT_RESET...")
        ser.write(b"WDT_RESET\n")
        time.sleep(0.5)
        if ser.in_waiting > 0:
            resp = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(f"Response: {resp.strip()}")

        # Try to initialize accelerometer
        print("\n" + "=" * 60)
        print("ATTEMPTING ACCELEROMETER DETECTION")
        print("=" * 60)
        print("\n[INFO] Sending ACCEL_INIT command...")
        ser.write(b"ACCEL_INIT\n")
        time.sleep(1.0)

        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print("\nResponse:")
            print("-" * 60)
            print(response)
            print("-" * 60)

            if "OK:ACCEL_INITIALIZED" in response:
                print("\n[SUCCESS] Accelerometer detected!")

                # Try to read data
                print("\n[INFO] Reading acceleration data...")
                ser.write(b"GET_ACCEL\n")
                time.sleep(0.5)
                if ser.in_waiting > 0:
                    accel_data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                    print(f"Acceleration: {accel_data.strip()}")

            elif "ERROR:NO_ACCEL_FOUND" in response:
                print("\n[FAILED] No accelerometer detected on I2C bus")
                print("\nTroubleshooting steps:")
                print("1. Check power to accelerometer:")
                print("   - Does it have a power LED? Is it ON?")
                print("   - Measure voltage: VCC should be ~5V")
                print("\n2. Check I2C wiring:")
                print("   Accelerometer    Arduino")
                print("   ────────────────────────")
                print("   VCC          ->  5V")
                print("   GND          ->  GND")
                print("   SDA          ->  A4")
                print("   SCL          ->  A5")
                print("\n3. Common mistakes:")
                print("   - SDA and SCL swapped (try reversing)")
                print("   - Loose connections (wiggle wires)")
                print("   - Wrong I2C address")
                print("\n4. What accelerometer model do you have?")
                print("   - ADXL345 (address 0x53)")
                print("   - MPU6050 (address 0x68)")
                print("   - LIS3DH (address 0x18)")
                print("   - Other?")
        else:
            print("\n[WARN] No response from Arduino")
            print("   - Check COM port connection")
            print("   - Try unplugging and replugging Arduino")

        # Get full status
        print("\n" + "=" * 60)
        print("FULL SYSTEM STATUS")
        print("=" * 60)
        ser.write(b"WDT_RESET\n")
        time.sleep(0.2)
        ser.write(b"GET_STATUS\n")
        time.sleep(0.5)

        if ser.in_waiting > 0:
            status = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print(status)

        ser.close()
        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)

    except serial.SerialException as e:
        print(f"\n[ERROR] {e}")
        print(f"   - Check that {PORT} is correct")
        print(f"   - Close other programs using the port")
    except KeyboardInterrupt:
        print("\n\n[ABORT] Diagnostic cancelled")


if __name__ == "__main__":
    main()
