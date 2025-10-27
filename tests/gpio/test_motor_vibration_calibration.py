"""
Simple motor vibration calibration - 1.5V to 3.0V
"""

import csv
import time
from datetime import datetime

import serial

COM_PORT = "COM6"

# Voltage range - SIMPLIFIED (4 voltages only)
voltages = [1.5, 2.0, 2.5, 3.0]
SAMPLES_PER_VOLTAGE = 5


def voltage_to_pwm(voltage):
    """Convert voltage to PWM (0-255)."""
    return int((voltage / 5.0) * 255)


def send_heartbeat(ser):
    """Send watchdog reset."""
    ser.write(b"WDT_RESET\n")
    time.sleep(0.05)
    if ser.in_waiting > 0:
        ser.readline()


# Connect
print("Connecting...")
ser = serial.Serial(COM_PORT, 9600, timeout=1)
time.sleep(2)

# Clear startup
while ser.in_waiting > 0:
    ser.readline()

# Initialize accelerometer
print("Initializing accelerometer...")
ser.write(b"ACCEL_INIT\n")
time.sleep(0.5)
while ser.in_waiting > 0:
    print(f"  {ser.readline().decode().strip()}")

print()

# Create CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"motor_calibration_{timestamp}.csv"

print(f"Saving to: {csv_filename}")
print()

with open(csv_filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Voltage (V)", "PWM", "Sample", "Vibration (g)", "Timestamp"])

    # Test each voltage
    for voltage in voltages:
        pwm = voltage_to_pwm(voltage)
        print(f"Testing {voltage}V (PWM={pwm})...")

        # Set motor speed
        ser.write(f"MOTOR_SPEED:{pwm}\n".encode())
        time.sleep(0.2)
        while ser.in_waiting > 0:
            ser.readline()

        # Stabilize with heartbeats
        for _ in range(3):
            time.sleep(0.3)
            send_heartbeat(ser)

        # Collect samples
        vibrations = []
        for sample in range(1, SAMPLES_PER_VOLTAGE + 1):
            ser.write(b"GET_VIBRATION_LEVEL\n")
            time.sleep(0.2)

            magnitude = None
            while ser.in_waiting > 0:
                line = ser.readline().decode().strip()
                if line.startswith("VIBRATION:"):
                    magnitude = float(line.split(":")[1])

            if magnitude is not None:
                vibrations.append(magnitude)
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                writer.writerow([voltage, pwm, sample, f"{magnitude:.6f}", timestamp_str])
                print(f"  Sample {sample:2d}: {magnitude:.3f}g")
            else:
                print(f"  Sample {sample:2d}: ERROR")

            time.sleep(0.2)
            send_heartbeat(ser)

        # Stats
        if vibrations:
            avg = sum(vibrations) / len(vibrations)
            print(f"  Average: {avg:.3f}g")
        print()

# Stop motor
print("Stopping motor...")
ser.write(b"MOTOR_OFF\n")
time.sleep(0.2)

ser.close()
print(f"\nDone! Data saved to: {csv_filename}")
