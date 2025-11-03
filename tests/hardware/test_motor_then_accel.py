#!/usr/bin/env python3
"""
Test: Start motor FIRST, then initialize accelerometer
This tests if we can read vibration on an already-running motor
"""

import time

import serial

PORT = "COM6"
BAUDRATE = 9600


def send_cmd(ser, cmd):
    """Send command and get response."""
    ser.reset_input_buffer()
    ser.write(f"{cmd}\n".encode())
    ser.flush()
    time.sleep(0.8)

    resp = ""
    while ser.in_waiting > 0:
        resp += ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
        time.sleep(0.1)
    return resp.strip()


def main():
    print("=" * 60)
    print("ALTERNATE TEST: Motor First, Then Accelerometer")
    print("=" * 60)
    print("\nStrategy: Start motor, THEN init accelerometer")
    print("This avoids reset when motor starts\n")

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"[OK] Connected\n")

        # Boot
        time.sleep(4)
        ser.reset_input_buffer()

        # STEP 1: Start motor FIRST (before accelerometer)
        print("[STEP 1] Starting motor at PWM 100...")
        resp = send_cmd(ser, "MOTOR_SPEED:100")
        print(f"Response: {resp[:50]}")

        if "OK:MOTOR_SPEED:100" in resp:
            print("[OK] Motor running\n")
        else:
            print("[WARN] Unexpected response\n")

        # Wait for motor to stabilize
        time.sleep(2)

        # Keep watchdog alive
        send_cmd(ser, "WDT_RESET")

        # STEP 2: NOW initialize accelerometer (motor already running)
        print("[STEP 2] Initializing accelerometer (motor still running)...")
        resp = send_cmd(ser, "ACCEL_INIT")

        if "0x68" in resp:
            print("[OK] Accelerometer initialized while motor runs!\n")

            # STEP 3: Try to read vibration
            print("[STEP 3] Reading vibration...")
            for i in range(3):
                send_cmd(ser, "WDT_RESET")
                resp = send_cmd(ser, "GET_VIBRATION_LEVEL")

                print(f"Attempt {i+1}: {resp[:80]}")

                if "VIBRATION:" in resp:
                    for line in resp.split("\n"):
                        if "VIBRATION:" in line:
                            vib = line.split("VIBRATION:")[1].strip()
                            print(f"  [SUCCESS] Vibration: {vib}g")
                elif "TOSCA Safety Watchdog" in resp:
                    print(f"  [FAIL] Arduino reset")
                    break
                else:
                    print(f"  [WARN] Unexpected response")

        else:
            print(f"[FAIL] Accelerometer init failed: {resp[:80]}\n")

        # Stop motor
        print("\n[CLEANUP] Stopping motor...")
        send_cmd(ser, "MOTOR_OFF")
        print("[OK] Motor stopped")

        ser.close()

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
