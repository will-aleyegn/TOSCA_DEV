"""
Quick 2-second vibration test.
"""

import time

import serial

COM_PORT = "COM12"  # Arduino GPIO controller


def send_heartbeat(ser):
    """Send watchdog reset."""
    ser.write(b"WDT_RESET\n")
    time.sleep(0.05)
    if ser.in_waiting > 0:
        ser.readline()  # Discard OK response


ser = serial.Serial(COM_PORT, 9600, timeout=1)
time.sleep(2)  # Wait for Arduino reset

print("Connected!")

# Clear startup messages
while ser.in_waiting > 0:
    ser.readline()

# Initialize accelerometer
print("Initializing accelerometer...")
ser.write(b"ACCEL_INIT\n")
time.sleep(0.5)
while ser.in_waiting > 0:
    print(f"  {ser.readline().decode().strip()}")

# Set motor to 100 PWM
print("\nStarting motor at 100 PWM...")
ser.write(b"MOTOR_SPEED:100\n")
time.sleep(0.3)
while ser.in_waiting > 0:
    print(f"  {ser.readline().decode().strip()}")

# Wait for motor to stabilize with heartbeats
print("Waiting for motor to stabilize...")
for _ in range(3):
    time.sleep(0.3)
    send_heartbeat(ser)

# Read vibration 5 times over 2 seconds
print("\nReading vibration (2 seconds)...")
for i in range(5):
    ser.write(b"GET_VIBRATION_LEVEL\n")
    time.sleep(0.2)

    print(f"  Sample {i+1}:")
    while ser.in_waiting > 0:
        line = ser.readline().decode().strip()
        print(f"    {line}")

    time.sleep(0.2)
    send_heartbeat(ser)

# Stop motor
print("\nStopping motor...")
ser.write(b"MOTOR_OFF\n")
time.sleep(0.2)
while ser.in_waiting > 0:
    print(f"  {ser.readline().decode().strip()}")

ser.close()
print("\nDone!")
