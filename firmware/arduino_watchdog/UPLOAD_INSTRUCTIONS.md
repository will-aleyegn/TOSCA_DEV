# How to Upload TOSCA Watchdog v2.0 to Arduino Uno

## Prerequisites

1. **Arduino IDE** (version 1.8.x or 2.x)
   - Download from: https://www.arduino.cc/en/software

2. **Arduino Uno** connected via USB (should show as COM6)

3. **Hardware connected**:
   - Motor on D9 + GND
   - Accelerometer on 5V, GND, A4 (SDA), A5 (SCL)
   - MCP4725 DAC on 5V, GND, A4 (SDA), A5 (SCL) - Shared I2C bus
   - Photodiode on A0

---

## Upload Steps

### 1. Open Arduino IDE

### 2. Load the Firmware
- File → Open
- Navigate to: `C:\Users\wille\Desktop\TOSCA-dev\firmware\arduino_watchdog\`
- Open: `arduino_watchdog_v2.ino`

### 3. Configure Board
- Tools → Board → Arduino AVR Boards → **Arduino Uno**
- Tools → Port → **COM6** (your Arduino port)
- Tools → Programmer → **AVRISP mkII** (or leave default)

### 4. Verify/Compile
- Click the **[DONE] Verify** button (or Sketch → Verify/Compile)
- Wait for "Done compiling" message
- Check for errors in the output window

### 5. Upload
- Click the **→ Upload** button (or Sketch → Upload)
- Wait for "Done uploading" message
- Arduino will reset automatically

### 6. Test Communication
- Tools → Serial Monitor
- Set baud rate to **9600**
- You should see:
  ```
  TOSCA Safety Watchdog v2.0
  Initializing...
  I2C bus initialized
  Scanning for I2C accelerometer...
  Accelerometer detected at 0x__ (if connected)
  Watchdog enabled (1000ms timeout)
  Ready. Send WDT_RESET every 500ms
  -----------------------------------
  ```

### 7. Test Commands
Type these commands in the Serial Monitor (must send newline):

```
GET_STATUS              # Should show all sensors
MOTOR_SPEED:76          # Motor should run slowly (1.5V)
GET_MOTOR_SPEED         # Should return: MOTOR_SPEED:76
GET_ACCEL               # Should return X,Y,Z values
MOTOR_OFF               # Motor stops
```

---

## Troubleshooting

### Error: "avrdude: stk500_recv(): programmer is not responding"
- **Solution**:
  - Check USB cable connection
  - Try different USB port
  - Reset Arduino by pressing reset button
  - Close other programs using COM6 (including TOSCA GUI!)

### Error: "Port COM6 not found"
- **Solution**:
  - Check Device Manager (Windows)
  - Arduino should show under "Ports (COM & LPT)"
  - Install CH340 or FTDI drivers if needed

### Accelerometer not detected
- **Check wiring**:
  - VCC → 5V
  - GND → GND
  - SDA → A4
  - SCL → A5
- **Check I2C pull-up resistors** (often built into breakout board)
- Try command: `ACCEL_INIT` to re-scan

### Motor not running
- **Check wiring**: Motor + → D9, Motor - → GND
- **Check voltage**: Use multimeter on D9, should show 1.5-3V when running
- **Check PWM value**: Must be >0, max 153
- Command: `MOTOR_SPEED:100` should definitely work

---

## Pin Verification Checklist

Before powering on, verify these connections:

- [ ] Motor (+) → Arduino D9
- [ ] Motor (-) → Arduino GND
- [ ] Accelerometer VCC → Arduino 5V
- [ ] Accelerometer GND → Arduino GND
- [ ] Accelerometer SDA → Arduino A4
- [ ] Accelerometer SCL → Arduino A5
- [ ] Photodiode signal → Arduino A0
- [ ] MCP4725 DAC VCC → Arduino 5V
- [ ] MCP4725 DAC GND → Arduino GND
- [ ] MCP4725 DAC SDA → Arduino A4 (shared I2C bus)
- [ ] MCP4725 DAC SCL → Arduino A5 (shared I2C bus)
- [ ] Footpedal switch → Arduino D5 (future)

---

## Next Steps After Upload

1. **Keep Serial Monitor open** for testing
2. **Test motor PWM**: Try speeds 50, 100, 150
3. **Test accelerometer**: Run motor, check vibration increases
4. **Calibrate accelerometer**: Command `ACCEL_CALIBRATE` with motor OFF
5. **Set vibration threshold**: Command `ACCEL_SET_THRESHOLD:0.2`
6. **Test watchdog**: Stop sending WDT_RESET, Arduino should halt after 1 second

---

## Safety Notes

- WARNING: **DO NOT** exceed MOTOR_SPEED:153 (motor damage!)
- WARNING: **DO NOT** connect treatment laser yet (SEMINEX unit only)
- WARNING: **Keep photodiode covered** until laser is ready
- WARNING: **Test watchdog** before connecting any lasers
