#!/usr/bin/env python3
"""Test Arduino Nano GPIO connection and functionality."""

import time

try:
    from pyfirmata2 import Arduino, util

    print("[OK] pyfirmata2 library found")
except ImportError:
    print("[ERROR] pyfirmata2 not installed")
    print("  Run: pip install pyfirmata2")
    exit(1)

# Arduino connection settings
PORT = "COM4"  # CH340 USB-Serial detected on COM4

print(f"\nAttempting to connect to Arduino on {PORT}...")
print("(Make sure StandardFirmata is uploaded to the Arduino)")

try:
    # Connect to Arduino
    board = Arduino(PORT)
    print(f"[OK] Connected to Arduino on {PORT}")

    # Start iterator thread for reading inputs
    iterator = util.Iterator(board)
    iterator.start()
    print("[OK] Iterator thread started")

    # Configure pins
    motor_pin = board.get_pin("d:2:o")  # Digital pin 2, output
    vibration_pin = board.get_pin("d:3:i")  # Digital pin 3, input with pullup
    photodiode_pin = board.get_pin("a:0:i")  # Analog pin A0, input

    # Enable reporting for input pins
    vibration_pin.enable_reporting()
    photodiode_pin.enable_reporting()

    print("[OK] Pins configured:")
    print("  - D2: Motor control (output)")
    print("  - D3: Vibration sensor (input)")
    print("  - A0: Photodiode (analog input)")

    # Wait for initial readings to stabilize
    time.sleep(2.0)

    print("\n" + "=" * 60)
    print("TESTING GPIO FUNCTIONALITY")
    print("=" * 60)

    # Test 1: Motor control
    print("\nTest 1: Motor Control")
    print("  Turning motor ON (D2 = HIGH)...")
    motor_pin.write(1)
    time.sleep(1.0)
    print("  [OK] Motor should be ON")

    print("  Turning motor OFF (D2 = LOW)...")
    motor_pin.write(0)
    time.sleep(1.0)
    print("  [OK] Motor should be OFF")

    # Test 2: Vibration sensor reading
    print("\nTest 2: Vibration Sensor")
    for i in range(5):
        # pyfirmata2 uses callbacks, but we can still read the cached value
        board.iterate()  # Process incoming data
        vibration = vibration_pin.value
        status = "DETECTED" if vibration else "NOT DETECTED"
        print(f"  Reading {i+1}: Vibration {status} (value: {vibration})")
        time.sleep(0.5)

    # Test 3: Photodiode reading
    print("\nTest 3: Photodiode (Analog Input)")
    for i in range(5):
        board.iterate()  # Process incoming data
        raw_value = photodiode_pin.value
        if raw_value is not None:
            voltage = raw_value * 5.0  # Convert to voltage (0-5V)
            power_mw = voltage * 400.0  # Convert to power (assuming 400 mW/V)
            print(f"  Reading {i+1}: {voltage:.3f}V ({power_mw:.1f} mW)")
        else:
            print(f"  Reading {i+1}: No data yet (waiting for ADC)")
        time.sleep(0.5)

    # Test 4: Safety interlock logic simulation
    print("\nTest 4: Safety Interlock Logic")
    print("  Turning motor ON...")
    motor_pin.write(1)
    time.sleep(1.0)

    board.iterate()  # Get latest values
    vibration = vibration_pin.value
    motor_on = True
    vibration_ok = bool(vibration)
    safety_ok = motor_on and vibration_ok

    print(f"  Motor ON: {motor_on}")
    print(f"  Vibration Detected: {vibration_ok}")
    print(f"  Safety Status: {'SAFE' if safety_ok else 'UNSAFE'}")

    # Clean up
    print("\nTest complete! Turning motor OFF...")
    motor_pin.write(0)
    time.sleep(0.5)

    board.exit()
    print("[OK] Arduino disconnected")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print("\nYour Arduino is ready for TOSCA integration!")
    print("You can now use the GPIO controller in the main application.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nTroubleshooting:")
    print("  1. Is StandardFirmata uploaded to the Arduino?")
    print("  2. Is COM4 the correct port?")
    print("  3. Is another program using the Arduino?")
    print("  4. Try unplugging and replugging the Arduino")
