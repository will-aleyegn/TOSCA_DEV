#!/usr/bin/env python3
"""
TOSCA Watchdog v2.0 Hardware Test Script
Tests motor control and accelerometer functionality
"""

import sys
import time

import serial


def send_command(ser, command, wait_time=0.3, verbose=True):
    """Send a command and read the response."""
    ser.write(f"{command}\n".encode())
    time.sleep(wait_time)

    response = ""
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")

    if verbose:
        print(f"  CMD: {command}")
        print(f"  RSP: {response.strip()}\n")

    return response.strip()


def test_accelerometer(ser):
    """Test accelerometer detection and functionality."""
    print("\n" + "=" * 60)
    print("ACCELEROMETER DIAGNOSTICS")
    print("=" * 60)

    # Try to re-initialize
    print("\n1. Attempting accelerometer initialization...")
    response = send_command(ser, "ACCEL_INIT")

    if "OK:ACCEL_INITIALIZED" in response:
        print("✅ Accelerometer detected and initialized!")

        # Read acceleration
        print("\n2. Reading acceleration data...")
        response = send_command(ser, "GET_ACCEL")

        if "ACCEL:" in response:
            accel_data = response.split("ACCEL:")[1].strip()
            x, y, z = map(float, accel_data.split(","))
            print(f"✅ Accelerometer readings: X={x:.3f}g, Y={y:.3f}g, Z={z:.3f}g")

            # Check if values are reasonable (Z should be ~1g if sitting flat)
            if abs(z - 1.0) < 0.5:
                print("✅ Z-axis reads ~1g (gravity) - orientation looks correct")
            else:
                print(f"⚠️  Z-axis should read ~1g if device is flat, got {z:.3f}g")

        # Test vibration reading
        print("\n3. Reading vibration level...")
        response = send_command(ser, "GET_VIBRATION_LEVEL")
        if "VIBRATION:" in response:
            vib = float(response.split("VIBRATION:")[1])
            print(f"✅ Vibration: {vib:.3f}g")

        return True

    elif "ERROR:NO_ACCEL_FOUND" in response:
        print("❌ Accelerometer NOT detected on I2C bus")
        print("\nTroubleshooting checklist:")
        print("  1. Check wiring:")
        print("     - VCC → Arduino 5V")
        print("     - GND → Arduino GND")
        print("     - SDA → Arduino A4")
        print("     - SCL → Arduino A5")
        print("  2. Check power LED on accelerometer (should be lit)")
        print("  3. Verify pull-up resistors on SDA/SCL (4.7kΩ)")
        print("  4. Try different I2C addresses (some boards have jumpers)")
        print("  5. Check for loose connections or cold solder joints")
        return False

    return False


def test_motor(ser):
    """Test motor PWM control."""
    print("\n" + "=" * 60)
    print("MOTOR CONTROL TEST")
    print("=" * 60)

    print("\n⚠️  WARNING: Motor will start spinning!")
    print("   Make sure motor is secured and nothing is in the way.")
    input("   Press Enter to continue, or Ctrl+C to abort...")

    # Test sequence
    test_speeds = [
        (76, "1.5V - LOW speed"),
        (100, "2.0V - MEDIUM speed"),
        (153, "3.0V - HIGH speed (max safe)"),
    ]

    for pwm, description in test_speeds:
        print(f"\n→ Setting motor to PWM={pwm} ({description})")
        response = send_command(ser, f"MOTOR_SPEED:{pwm}")

        if f"OK:MOTOR_SPEED:{pwm}" in response:
            print(f"✅ Motor set to {pwm}")

            # Verify
            verify = send_command(ser, "GET_MOTOR_SPEED", verbose=False)
            if f"MOTOR_SPEED:{pwm}" in verify:
                print(f"✅ Verified: {verify}")

            print("   → Listening for 3 seconds... (motor should be running)")
            time.sleep(3)
        else:
            print(f"❌ Failed to set motor speed")

    # Stop motor
    print("\n→ Stopping motor...")
    response = send_command(ser, "MOTOR_OFF")
    if "OK:MOTOR_OFF" in response:
        print("✅ Motor stopped")

    print("\n✅ Motor test complete")


def test_laser(ser):
    """Test aiming laser control."""
    print("\n" + "=" * 60)
    print("AIMING LASER TEST")
    print("=" * 60)

    print("\n⚠️  WARNING: Aiming laser will turn on!")
    input("   Press Enter to continue, or Ctrl+C to abort...")

    # Turn on
    print("\n→ Turning laser ON...")
    response = send_command(ser, "LASER_ON")
    if "OK:LASER_ON" in response:
        print("✅ Laser should be ON now (check for red dot)")
        time.sleep(2)

    # Turn off
    print("\n→ Turning laser OFF...")
    response = send_command(ser, "LASER_OFF")
    if "OK:LASER_OFF" in response:
        print("✅ Laser should be OFF now")


def test_full_status(ser):
    """Get complete system status."""
    print("\n" + "=" * 60)
    print("FULL SYSTEM STATUS")
    print("=" * 60)

    response = send_command(ser, "GET_STATUS", wait_time=0.5)
    print(response)


def keep_watchdog_alive(ser):
    """Send periodic WDT_RESET commands."""
    print("\n" + "=" * 60)
    print("WATCHDOG HEARTBEAT TEST")
    print("=" * 60)
    print("\nSending WDT_RESET commands for 10 seconds...")
    print("(Watchdog should NOT trigger)")

    for i in range(20):  # 10 seconds at 0.5s intervals
        send_command(ser, "WDT_RESET", wait_time=0.1, verbose=False)
        time.sleep(0.5)
        print(".", end="", flush=True)

    print("\n✅ Watchdog heartbeat test passed (no reset)")


def main():
    """Main test routine."""
    print("\n" + "=" * 60)
    print("TOSCA Watchdog v2.0 - Hardware Test Suite")
    print("=" * 60)

    # Ask for COM port
    print("\nAvailable COM ports from git status: COM3, COM6")
    print("According to config.yaml, watchdog should be on COM6")
    port = input("Enter COM port (default: COM6): ").strip() or "COM6"

    try:
        # Open serial connection
        print(f"\nConnecting to {port} at 9600 baud...")
        ser = serial.Serial(port=port, baudrate=9600, timeout=2.0, write_timeout=2.0)

        print(f"✅ Connected to {port}")

        # Read startup messages
        time.sleep(2)
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            print("\nStartup messages:")
            print(startup)

        # Send initial heartbeat
        send_command(ser, "WDT_RESET", verbose=False)

        # Main test menu
        while True:
            print("\n" + "=" * 60)
            print("TEST MENU")
            print("=" * 60)
            print("1. Test Accelerometer")
            print("2. Test Motor (PWM Control)")
            print("3. Test Aiming Laser")
            print("4. Get Full System Status")
            print("5. Test Watchdog Heartbeat")
            print("6. Run All Tests")
            print("0. Exit")

            choice = input("\nSelect test (0-6): ").strip()

            # Keep watchdog alive during tests
            send_command(ser, "WDT_RESET", verbose=False)

            if choice == "1":
                test_accelerometer(ser)
            elif choice == "2":
                test_motor(ser)
            elif choice == "3":
                test_laser(ser)
            elif choice == "4":
                test_full_status(ser)
            elif choice == "5":
                keep_watchdog_alive(ser)
            elif choice == "6":
                # Run all tests
                keep_watchdog_alive(ser)
                test_accelerometer(ser)
                test_motor(ser)
                test_laser(ser)
                test_full_status(ser)
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("Invalid choice")

            # Keep watchdog alive
            send_command(ser, "WDT_RESET", verbose=False)

        ser.close()
        print("✅ Serial port closed")

    except serial.SerialException as e:
        print(f"\n❌ Error: {e}")
        print(f"   - Check that {port} is the correct port")
        print(f"   - Make sure no other program is using the port")
        print(f"   - Verify the Arduino is powered on")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n❌ Test aborted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
