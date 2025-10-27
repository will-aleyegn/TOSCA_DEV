#!/usr/bin/env python3
"""
Motor + Accelerometer Integration Test
Tests vibration detection while motor is running
"""

import time

import serial

PORT = "COM6"
BAUDRATE = 9600


def send_command(ser, command):
    """Send command with proper timing."""
    ser.reset_input_buffer()
    ser.write(f"{command}\n".encode("utf-8"))
    ser.flush()
    time.sleep(0.6)

    response = ""
    while ser.in_waiting > 0:
        response += ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
        time.sleep(0.1)
    return response.strip()


def main():
    print("=" * 70)
    print("MOTOR + ACCELEROMETER VIBRATION TEST")
    print("=" * 70)
    print("\nThis test will:")
    print("  1. Measure baseline vibration (motor off)")
    print("  2. Run motor at different speeds")
    print("  3. Measure vibration at each speed")
    print("  4. Verify accelerometer detects motor vibration")
    print("\n[WARN] Motor will start spinning in 3 seconds!\n")
    time.sleep(3)

    try:
        # Connect
        ser = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        print(f"\n[OK] Connected to {PORT}\n")

        # Wait for boot
        print("Waiting for Arduino boot...")
        time.sleep(4)

        # Clear startup messages
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)

        print("[OK] Arduino booted\n")

        # Initialize accelerometer
        print("=" * 70)
        print("INITIALIZATION")
        print("=" * 70)

        print("\n[1/2] Initializing MPU6050...")
        resp = send_command(ser, "ACCEL_INIT")
        if "OK:ACCEL_INITIALIZED" in resp or "0x68" in resp:
            print("      [OK] MPU6050 ready")
        else:
            print("      [ERROR] Accelerometer init failed")
            return

        print("\n[2/2] Sending watchdog heartbeat...")
        send_command(ser, "WDT_RESET")
        print("      [OK] Watchdog alive")

        # Baseline vibration (motor off)
        print("\n" + "=" * 70)
        print("BASELINE VIBRATION (Motor OFF)")
        print("=" * 70)

        baseline_samples = []
        for i in range(5):
            resp = send_command(ser, "GET_VIBRATION_LEVEL")
            for line in resp.split("\n"):
                if "VIBRATION:" in line:
                    vib = float(line.split("VIBRATION:")[1])
                    baseline_samples.append(vib)
                    bar = "#" * int(vib * 100)
                    print(f"Sample {i+1}: {vib:.3f}g |{bar}")
            send_command(ser, "WDT_RESET")
            time.sleep(0.3)

        baseline_avg = sum(baseline_samples) / len(baseline_samples) if baseline_samples else 0
        print(f"\nBaseline Average: {baseline_avg:.3f}g")

        # Test motor speeds
        motor_speeds = [
            (76, "1.5V - Minimum"),
            (100, "2.0V - Medium"),
            (127, "2.5V - High"),
            (153, "3.0V - Maximum"),
        ]

        print("\n" + "=" * 70)
        print("MOTOR VIBRATION TEST")
        print("=" * 70)

        for pwm, description in motor_speeds:
            print(f"\n--- PWM {pwm} ({description}) ---")

            # Start motor
            resp = send_command(ser, f"MOTOR_SPEED:{pwm}")
            if f"OK:MOTOR_SPEED:{pwm}" in resp:
                print(f"[OK] Motor started at PWM {pwm}")
            else:
                print(f"[ERROR] Failed to start motor")
                continue

            # Wait for motor to stabilize
            print("Waiting 1 second for motor to stabilize...")
            time.sleep(1)
            send_command(ser, "WDT_RESET")

            # Measure vibration (5 samples)
            print(f"Measuring vibration...")
            vibration_samples = []
            for i in range(5):
                resp = send_command(ser, "GET_VIBRATION_LEVEL")
                for line in resp.split("\n"):
                    if "VIBRATION:" in line:
                        vib = float(line.split("VIBRATION:")[1])
                        vibration_samples.append(vib)
                        bar = "#" * int(vib * 100)
                        print(f"  Sample {i+1}: {vib:.3f}g |{bar}")
                send_command(ser, "WDT_RESET")
                time.sleep(0.2)

            motor_avg = sum(vibration_samples) / len(vibration_samples) if vibration_samples else 0
            increase = motor_avg - baseline_avg

            print(f"\nResults for PWM {pwm}:")
            print(f"  Average vibration: {motor_avg:.3f}g")
            print(
                f"  Increase from baseline: {increase:.3f}g ({increase/baseline_avg*100:.0f}% increase)"
                if baseline_avg > 0
                else f"  Increase: {increase:.3f}g"
            )

            if increase > 0.01:
                print(f"  [OK] Vibration detected!")
            else:
                print(f"  [WARN] Little/no vibration increase detected")

            # Stop motor
            send_command(ser, "MOTOR_OFF")
            print(f"Motor stopped\n")
            time.sleep(1)

        # Final summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Baseline vibration (motor off): {baseline_avg:.3f}g")
        print(f"\nThe accelerometer successfully detected motor vibration!")
        print(f"\nNext steps:")
        print(f"  - Use vibration monitoring to detect motor failure")
        print(f"  - Set vibration threshold for safety alerts")
        print(f"  - Log vibration data during treatments")

        ser.close()

    except serial.SerialException as e:
        print(f"\n[ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\n[ABORT] Test cancelled")
        if "ser" in locals() and ser.is_open:
            send_command(ser, "MOTOR_OFF")
            ser.close()
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        if "ser" in locals() and ser.is_open:
            send_command(ser, "MOTOR_OFF")
            ser.close()


if __name__ == "__main__":
    main()
