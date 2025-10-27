#!/usr/bin/env python3
"""
Accelerometer Test - MPU6050
Tests accelerometer readings with proper reset handling
"""

import time

import serial

PORT = "COM6"
BAUDRATE = 9600


def wait_for_ready(ser, timeout=5):
    """Wait for Arduino to finish booting."""
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            if "Ready" in data or "---" in data:
                return True
        time.sleep(0.1)
    return True


def send_command_safe(ser, command, wait_time=0.5):
    """Send command with retry on reset."""
    # Clear buffer
    if ser.in_waiting > 0:
        ser.read(ser.in_waiting)

    # Send command
    ser.write(f"{command}\n".encode())
    time.sleep(wait_time)

    # Read response
    response = ""
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")

    # Check for reset
    if "TOSCA Safety Watchdog" in response:
        print("[WARN] Arduino reset detected, waiting...")
        wait_for_ready(ser)
        # Retry command
        ser.write(f"{command}\n".encode())
        time.sleep(wait_time)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")

    return response.strip()


def main():
    print("=" * 60)
    print("MPU6050 ACCELEROMETER TEST")
    print("=" * 60)

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"[OK] Connected to {PORT}\n")

        print("Waiting for Arduino to boot...")
        wait_for_ready(ser, timeout=5)
        print("[OK] Arduino ready\n")

        # Keep watchdog alive
        print("Sending initial heartbeat...")
        resp = send_command_safe(ser, "WDT_RESET", wait_time=0.3)
        if "OK:WDT_RESET" in resp:
            print("[OK] Watchdog alive\n")

        # Initialize accelerometer
        print("=" * 60)
        print("INITIALIZING MPU6050")
        print("=" * 60)
        resp = send_command_safe(ser, "ACCEL_INIT", wait_time=1.0)
        print(f"Response: {resp}\n")

        if "OK:ACCEL_INITIALIZED" in resp:
            print("[SUCCESS] MPU6050 initialized!\n")

            # Read acceleration 10 times
            print("=" * 60)
            print("READING ACCELERATION (10 samples)")
            print("=" * 60)
            print("Sample |    X (g) |    Y (g) |    Z (g) | Magnitude")
            print("-------|----------|----------|----------|----------")

            for i in range(10):
                # Keep watchdog alive
                send_command_safe(ser, "WDT_RESET", wait_time=0.1)

                # Read acceleration
                resp = send_command_safe(ser, "GET_ACCEL", wait_time=0.3)

                if "ACCEL:" in resp:
                    accel_line = [line for line in resp.split("\n") if "ACCEL:" in line][0]
                    accel_data = accel_line.split("ACCEL:")[1].strip()
                    x, y, z = map(float, accel_data.split(","))
                    mag = (x**2 + y**2 + z**2) ** 0.5
                    print(f"  {i+1:2d}   | {x:8.3f} | {y:8.3f} | {z:8.3f} | {mag:8.3f}")
                else:
                    print(f"  {i+1:2d}   | ERROR reading data")

                time.sleep(0.5)

            # Test vibration reading
            print("\n" + "=" * 60)
            print("VIBRATION TEST")
            print("=" * 60)
            print("Tap or shake the accelerometer...\n")

            for i in range(10):
                send_command_safe(ser, "WDT_RESET", wait_time=0.1)
                resp = send_command_safe(ser, "GET_VIBRATION_LEVEL", wait_time=0.3)

                if "VIBRATION:" in resp:
                    vib_line = [line for line in resp.split("\n") if "VIBRATION:" in line][0]
                    vib = float(vib_line.split("VIBRATION:")[1])

                    # Visual bar
                    bar_len = int(vib * 50)
                    bar = "#" * bar_len
                    print(f"Vibration: {vib:6.3f}g |{bar}")

                time.sleep(0.5)

            print("\n[SUCCESS] Accelerometer test complete!")

        else:
            print("[ERROR] Failed to initialize accelerometer")
            print("Check wiring and connections")

        ser.close()

    except serial.SerialException as e:
        print(f"\n[ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\n[ABORT] Test cancelled")


if __name__ == "__main__":
    main()
