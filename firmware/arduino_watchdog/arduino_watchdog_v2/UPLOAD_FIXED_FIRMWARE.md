# Upload Fixed Watchdog Firmware v2.1

## What Was Fixed

**Problem:** Arduino was resetting during accelerometer operations because I2C communication took longer than the 1-second watchdog timeout.

**Solution:** Added `wdt_reset()` calls throughout I2C operations to keep the watchdog alive during:
- Accelerometer detection (scanning I2C addresses)
- Accelerometer initialization (MPU6050/ADXL345/LIS3DH setup)
- Reading acceleration data
- Calibration (50-sample averaging)

## Upload Instructions

### 1. Open Arduino IDE

### 2. Load the Firmware
- File → Open
- Navigate to: `firmware/arduino_watchdog/arduino_watchdog_v2/arduino_watchdog_v2.ino`

### 3. Select Board and Port
- Tools → Board → Arduino AVR Boards → Arduino Uno
- Tools → Port → COM6 (or your Arduino's port)

### 4. Upload
- Click the **Upload** button (→) or press Ctrl+U
- Wait for "Done uploading" message

### 5. Verify Upload
Open Serial Monitor (Tools → Serial Monitor or Ctrl+Shift+M):
- Set baud rate to **9600**
- You should see:
```
TOSCA Safety Watchdog v2.0
Initializing...
I2C bus initialized (with timeout protection)
Scanning for I2C accelerometer...
Accelerometer detected at 0x68
MPU6050 initialized (wake from sleep)
Watchdog enabled (1000ms timeout)
Ready. Send WDT_RESET every 500ms
-----------------------------------
```

### 6. Test Accelerometer
In Serial Monitor, type these commands (press Enter after each):

```
ACCEL_INIT
```
**Expected:** `OK:ACCEL_INITIALIZED`

```
GET_ACCEL
```
**Expected:** `ACCEL:0.123,-0.045,1.012` (your values will vary)

```
GET_VIBRATION_LEVEL
```
**Expected:** `VIBRATION:0.045`

### 7. Run Python Test
Close Serial Monitor, then run:
```bash
python test_accel_slow.py
```

Should now show acceleration readings without Arduino resets!

---

## Changes Made to Firmware

```cpp
// Added in detectAccelerometer():
wdt_reset();  // Keep watchdog alive during I2C scan

// Added in initAccelerometer():
wdt_reset();  // Before init
wdt_reset();  // After init

// Added in readAcceleration():
wdt_reset();  // Before I2C read

// Added in calibrateAccelerometer():
wdt_reset();  // Before calibration
wdt_reset();  // In loop (50 times)

// Added in processCommand():
wdt_reset();  // Before ACCEL_INIT
wdt_reset();  // After ACCEL_INIT
wdt_reset();  // Before/after ACCEL_CALIBRATE
wdt_reset();  // Before GET_ACCEL
wdt_reset();  // Before GET_VIBRATION_LEVEL
```

---

## Troubleshooting

### "Port in use" error
- Close Serial Monitor
- Close any other programs using COM6
- Try upload again

### Still getting resets
- Check that firmware uploaded successfully
- Verify you're using the correct .ino file
- Try power cycling the Arduino (unplug/replug USB)

### Accelerometer not detected
- Check wiring:
  - VCC → 5V
  - GND → GND
  - SDA → A4
  - SCL → A5
- Verify accelerometer power LED is ON
- Try `ACCEL_INIT` command manually

---

## Next Steps After Upload

1. Test with `python test_accel_slow.py`
2. Test motor and accelerometer together
3. Integrate into main TOSCA GUI
