"""
Test vibration reading with motor OFF.
"""

import time

import serial

COM_PORT = "COM12"  # Arduino GPIO controller


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

# Make sure motor is OFF
print("\nEnsuring motor is OFF...")
ser.write(b"MOTOR_OFF\n")
time.sleep(0.2)
while ser.in_waiting > 0:
    print(f"  {ser.readline().decode().strip()}")

# Wait for vibrations to settle
print("Waiting for vibrations to settle...")
for _ in range(3):
    time.sleep(0.3)
    send_heartbeat(ser)

# Read vibration 10 times
print("\nReading vibration with motor OFF (10 samples):")
vibrations = []
for i in range(10):
    ser.write(b"GET_VIBRATION_LEVEL\n")
    time.sleep(0.2)

    while ser.in_waiting > 0:
        line = ser.readline().decode().strip()
        if line.startswith("VIBRATION:"):
            magnitude = float(line.split(":")[1])
            vibrations.append(magnitude)
            print(f"  Sample {i+1:2d}: {magnitude:.3f}g")

    time.sleep(0.2)
    send_heartbeat(ser)

# Stats
if vibrations:
    avg = sum(vibrations) / len(vibrations)
    min_v = min(vibrations)
    max_v = max(vibrations)
    print(f"\nAverage: {avg:.3f}g")
    print(f"Min: {min_v:.3f}g")
    print(f"Max: {max_v:.3f}g")

ser.close()
print("\nDone!")
