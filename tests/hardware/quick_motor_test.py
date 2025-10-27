#!/usr/bin/env python3
"""
Quick Motor Test - Automated
Tests motor at safe speeds with watchdog
"""

import sys
import time

import serial

# Configuration
PORT = "COM6"  # Change if needed
BAUDRATE = 9600


def send_command(ser, command, wait_time=0.3):
    """Send command and get response."""
    ser.write(f"{command}\n".encode())
    time.sleep(wait_time)

    response = ""
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")

    print(f">> {command}")
    if response.strip():
        print(f"<< {response.strip()}")
    return response.strip()


def main():
    print("=" * 60)
    print("QUICK MOTOR TEST")
    print("=" * 60)
    print(f"\nConnecting to {PORT}...")

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"[OK] Connected to {PORT}\n")

        # Wait for startup
        time.sleep(2)
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print("Startup messages:")
            print(startup)
            print()

        # Keep watchdog alive
        send_command(ser, "WDT_RESET")
        time.sleep(0.5)

        # Get initial status
        print("\n" + "=" * 60)
        print("INITIAL STATUS")
        print("=" * 60)
        send_command(ser, "GET_STATUS", wait_time=0.5)

        # Test accelerometer
        print("\n" + "=" * 60)
        print("ACCELEROMETER TEST")
        print("=" * 60)
        response = send_command(ser, "ACCEL_INIT")

        if "OK:ACCEL_INITIALIZED" in response:
            print("[OK] Accelerometer detected!")
            send_command(ser, "GET_ACCEL")
        else:
            print("[WARN] No accelerometer detected")
            print("   Check wiring: VCC->5V, GND->GND, SDA->A4, SCL->A5")

        send_command(ser, "WDT_RESET")

        # Motor test
        print("\n" + "=" * 60)
        print("MOTOR TEST SEQUENCE")
        print("=" * 60)
        print("[WARN] Motor will start in 3 seconds...")
        time.sleep(1)
        send_command(ser, "WDT_RESET")
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)

        # Test speeds
        test_speeds = [
            (50, "~1.0V - Very low"),
            (76, "1.5V - Rated minimum"),
            (100, "2.0V - Medium"),
            (127, "2.5V - High"),
            (153, "3.0V - Maximum safe"),
        ]

        for pwm, description in test_speeds:
            print(f"\n-> PWM {pwm} ({description})")
            response = send_command(ser, f"MOTOR_SPEED:{pwm}")

            if f"OK:MOTOR_SPEED:{pwm}" in response:
                print(f"[OK] Motor set to {pwm}")

                # Verify
                verify = send_command(ser, "GET_MOTOR_SPEED")
                print(f"   Verified: {verify}")

                # Keep alive during run
                print(f"   Running for 3 seconds...")
                for i in range(6):
                    time.sleep(0.5)
                    send_command(ser, "WDT_RESET", wait_time=0.1)
                    print(".", end="", flush=True)
                print()
            else:
                print(f"[ERROR] Failed to set motor speed")
                break

        # Stop motor
        print("\n-> Stopping motor...")
        send_command(ser, "MOTOR_OFF")
        print("[OK] Motor stopped")

        # Final status
        print("\n" + "=" * 60)
        print("FINAL STATUS")
        print("=" * 60)
        send_command(ser, "GET_STATUS", wait_time=0.5)

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nDid the motor run smoothly? (yes/no)")
        print("If not, check:")
        print("  - Motor connections")
        print("  - Flyback diode installed")
        print("  - Power supply adequate")

        ser.close()

    except serial.SerialException as e:
        print(f"\n[ERROR] {e}")
        print(f"   Possible issues:")
        print(f"   - Wrong COM port (currently: {PORT})")
        print(f"   - Port in use by another program")
        print(f"   - Arduino not powered/connected")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[ABORT] Test aborted!")
        if "ser" in locals() and ser.is_open:
            send_command(ser, "MOTOR_OFF")
            ser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
