# Arduino Nano GPIO Setup Guide

**Purpose:** Configure Arduino Nano for TOSCA safety interlock monitoring

**Hardware:** Arduino Nano (ATmega328P)
**Communication:** USB (power + data)
**Protocol:** Firmata (StandardFirmata)

---

## Hardware Wiring

### Pin Configuration

| Arduino Pin | Function | Type | Description |
|------------|----------|------|-------------|
| D2 | Motor Control | Output | Smoothing device motor enable (HIGH = ON) |
| D3 | Vibration Sensor | Input | Smoothing device vibration detection |
| A0 | Photodiode | Analog Input | Laser power monitoring (0-5V → 0-2000mW) |
| GND | Ground | - | Common ground for all sensors |
| 5V | Power Out | - | Optional sensor power supply |

### Wiring Diagram

```
Arduino Nano
┌────────────────────────┐
│                        │
│  [D2]────→ Motor Driver (5V logic)
│                        │
│  [D3]←──── Vibration Sensor (with pullup)
│                        │
│  [A0]←──── Photodiode (0-5V signal)
│                        │
│  [GND]──── Common Ground
│                        │
│  [USB]──── Computer (power + data)
│                        │
└────────────────────────┘
```

---

## Software Setup

### Step 1: Install Arduino IDE

1. Download Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install for your platform (Windows/Mac/Linux)
3. Launch Arduino IDE

### Step 2: Flash StandardFirmata

**One-time setup - no Arduino programming required!**

1. **Connect Arduino Nano**
   - Plug Arduino into USB port
   - Wait for drivers to install (Windows may auto-install)

2. **Select Board**
   - Tools → Board → Arduino AVR Boards → Arduino Nano
   - Tools → Processor → ATmega328P (Old Bootloader)
   - Tools → Port → Select your COM port (e.g., COM3)

3. **Load StandardFirmata**
   - File → Examples → Firmata → StandardFirmata
   - Click "Upload" button (right arrow icon)
   - Wait for "Done uploading" message

4. **Verify Installation**
   - Open Serial Monitor (Tools → Serial Monitor)
   - Set baud rate to 57600
   - You should see Firmata version info

**That's it! Your Arduino is now ready for TOSCA.**

---

## Python Integration

### Install pyfirmata2

```bash
pip install pyfirmata2
```

**Note:** We use `pyfirmata2` instead of the original `pyfirmata` for Python 3.12+ compatibility.

### Find Arduino Port

**Windows:**
```bash
# Check Device Manager → Ports (COM & LPT)
# Usually COM3, COM4, etc.
```

**Linux:**
```bash
ls /dev/ttyUSB*
# Usually /dev/ttyUSB0
```

**macOS:**
```bash
ls /dev/cu.usbserial*
# Usually /dev/cu.usbserial-*
```

### Test Connection

```python
from pyfirmata2 import Arduino

# Replace 'COM3' with your actual port
board = Arduino('COM3')
print("Arduino connected!")

# Test motor control pin
motor_pin = board.get_pin('d:2:o')
motor_pin.write(1)  # Turn on
motor_pin.write(0)  # Turn off

board.exit()
```

---

## TOSCA Integration

### Configure GPIO Controller

In TOSCA main window or safety widget:

1. **Connect to Arduino**
   - Click "Connect GPIO" button
   - Arduino should be detected on default port (COM3)
   - Green indicator = connected

2. **Test Safety Interlocks**
   - Click "Start Motor" button
   - Motor output (D2) should go HIGH
   - Vibration sensor (D3) will detect vibration
   - Photodiode (A0) will show laser power

3. **Monitor Status**
   - Safety tab shows real-time GPIO status
   - Motor: ON/OFF
   - Vibration: Detected/Not Detected
   - Photodiode: Voltage and calculated power

---

## Troubleshooting

### Arduino Not Detected

**Issue:** "Cannot find Arduino on COM port"

**Solutions:**
1. Check USB cable (must be data cable, not charge-only)
2. Verify Arduino shows up in Device Manager (Windows)
3. Try different COM port in GPIO settings
4. Reinstall CH340 drivers (for clone Arduinos)

### Firmata Not Responding

**Issue:** "Timeout waiting for Arduino"

**Solutions:**
1. Re-flash StandardFirmata
2. Power cycle Arduino (unplug/replug USB)
3. Check serial port is not in use by another program
4. Try baud rate 57600 instead of 115200

### Pins Not Working

**Issue:** "Pin reads always 0" or "Pin won't write"

**Solutions:**
1. Verify pin numbers (D2 = digital 2, A0 = analog 0)
2. Check wiring connections
3. Test with Arduino IDE Serial Monitor first
4. Enable pullup for digital inputs if needed

### High CPU Usage

**Issue:** "Python process using lots of CPU"

**Solutions:**
1. This is normal - Iterator thread processes incoming data continuously
2. Reduce polling rate in gpio_controller.py if needed
3. pyfirmata2 has optimized performance for modern Python

---

## Pin Functions Explained

### D2 - Motor Control (Output)

- **Purpose:** Turn smoothing device motor on/off
- **Signal:** Digital HIGH (5V) = motor ON, LOW (0V) = motor OFF
- **Wiring:** Connect to motor driver input (5V logic level)
- **Code:** `motor_pin.write(1)` = ON, `motor_pin.write(0)` = OFF

### D3 - Vibration Sensor (Input)

- **Purpose:** Detect smoothing device vibration
- **Signal:** Digital HIGH = vibration detected, LOW = no vibration
- **Wiring:** Sensor output to D3, sensor ground to GND
- **Code:** `vibration = vibration_pin.read()` returns True/False
- **Debouncing:** Software debounce (3 consecutive readings)

### A0 - Photodiode (Analog Input)

- **Purpose:** Monitor laser power via photodiode voltage
- **Signal:** 0-5V analog (10-bit ADC = 0-1023 counts)
- **Wiring:** Photodiode signal to A0, photodiode ground to GND
- **Code:** `voltage = photodiode_pin.read() * 5.0` (in volts)
- **Conversion:** 5V = 2000mW laser power (400 mW/V)

---

## Advanced Configuration

### Custom Port Configuration

Edit `src/hardware/gpio_controller.py`:

```python
# Line 67-68
self.motor_pin_number = 2  # Change digital pin
self.photodiode_pin_number = 0  # Change analog pin (A0 = 0, A1 = 1, etc.)
```

### Calibration Constants

Edit `src/hardware/gpio_controller.py`:

```python
# Line 88
self.photodiode_voltage_to_power = 400.0  # Adjust mW per volt
```

**Calibration procedure:**
1. Measure known laser power with power meter
2. Read photodiode voltage from TOSCA
3. Calculate: `mW_per_volt = measured_power_mW / photodiode_voltage_V`
4. Update constant in code

### Vibration Debounce Tuning

Edit `src/hardware/gpio_controller.py`:

```python
# Line 90
self.vibration_debounce_threshold = 3  # Number of consecutive readings
```

- Higher value = less sensitive (fewer false positives)
- Lower value = more responsive (may have false triggers)
- Default (3) = good for most motors at 100ms polling

---

## Safety Interlock Logic

### Safety Conditions

Safety system permits laser enable when **ALL** conditions met:

1. [DONE] Motor is ON (D2 = HIGH)
2. [DONE] Vibration detected (D3 = HIGH, debounced)
3. [DONE] Photodiode reading valid (A0 reading stable)

If **ANY** condition fails:
- [FAILED] Laser is disabled immediately
- [FAILED] Safety event logged to database
- [FAILED] Safety widget shows "UNSAFE" status

### Emergency Stop Override

Emergency stop button overrides all safety checks:
- Immediately sets safety state to EMERGENCY_STOP
- Disables laser regardless of GPIO status
- Requires manual clear before resuming

---

## Performance Notes

### Polling Rate

- **Update interval:** 100ms (10 Hz)
- **Pin reading latency:** ~10ms typical
- **Total latency:** ~110ms from sensor change to UI update

### CPU Usage

- **Typical:** 1-2% CPU (background monitoring)
- **Iterator thread:** Runs continuously (normal)
- **No performance impact** on laser control timing

### Reliability

- **Connection:** Very stable over USB
- **Error handling:** Automatic reconnection on disconnect
- **Timeout:** 5 seconds for connection attempts

---

## References

- [Firmata Protocol](https://github.com/firmata/protocol)
- [PyFirmata Documentation](https://pyfirmata.readthedocs.io/)
- [Arduino Nano Pinout](https://www.arduino.cc/en/uploads/Main/ArduinoNanoManual23.pdf)

---

**Last Updated:** 2025-10-24
**Tested With:** Arduino Nano (ATmega328P), pyfirmata2 2.5.1, Python 3.12.10
