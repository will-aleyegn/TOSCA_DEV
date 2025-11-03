# TOSCA Hardware Configuration Summary
**Date**: 2025-10-27
**Status**: [DONE] Configured for actual hardware (PWM motor + I2C accelerometer)

---

## 🎯 What We Accomplished

### 1. Defined Actual Hardware ✅
- **Smoothing Motor**: DC motor (1.5-3.0V) with **PWM variable speed control**
- **Vibration Sensor**: I2C accelerometer (ADXL345 or MPU6050) with **data logging**
- **Photodiode**: Laser power monitoring (0-5V analog)
- **Aiming Laser**: Red 650nm alignment laser
- **Footpedal**: Reserved for future (D5, not yet implemented)

### 2. Updated Arduino Firmware ✅
- **Created**: `firmware/arduino_watchdog/arduino_watchdog_v2.ino`
- **Features**:
  - PWM motor control (D9): Variable voltage 1.5V-3.0V
  - I2C accelerometer support (A4/A5): Auto-detect ADXL345/MPU6050/LIS3DH
  - Vibration magnitude calculation
  - Accelerometer calibration
  - Adjustable vibration threshold
  - All previous watchdog functionality preserved

### 3. Updated Configuration ✅
- **Modified**: `config.yaml` with new pin assignments
- **Added**:
  - Motor PWM parameters (min/max/default speed)
  - Accelerometer I2C settings
  - Vibration threshold
  - All new pin definitions

### 4. Created Documentation ✅
- **NEW_PIN_CONFIG.md**: Detailed pin configuration guide
- **UPLOAD_INSTRUCTIONS.md**: Step-by-step Arduino upload guide
- **HARDWARE_CONFIG_SUMMARY.md**: This file

---

## 📍 **NEW Pin Configuration**

### Arduino Uno Pin Assignments:

| Pin | Function | Type | Device | Voltage/Signal |
|-----|----------|------|--------|----------------|
| **D4** | Aiming Laser | OUTPUT | Red laser control | Digital 0/5V |
| **D5** | Footpedal (future) | INPUT_PULLUP | Safety switch | Active LOW |
| **D9** | **Motor Control** | **PWM OUTPUT** | **Smoothing motor** | **PWM 1.5-3.0V** |
| **A0** | Photodiode | ANALOG IN | Laser power sensor | 0-5V analog |
| **A4** | **SDA** | **I2C DATA** | **Accelerometer** | **I2C protocol** |
| **A5** | **SCL** | **I2C CLOCK** | **Accelerometer** | **I2C protocol** |

### Power Connections:
- Arduino 5V → Accelerometer VCC
- Arduino GND → Accelerometer GND, Motor (-)
- Arduino D9 → Motor (+)

---

## 🔧 **Motor PWM Speed Control**

Your motor operates at 1.5V - 3.0V. Arduino provides PWM on D9:

```
PWM Value    Voltage    Speed Level    Use Case
──────────────────────────────────────────────────
0            0.0V       Stopped        Motor off
76           1.5V       Low            Gentle smoothing
100          2.0V       Medium         Default speed
127          2.5V       High           Aggressive smoothing
153          3.0V       Maximum        DO NOT EXCEED!
```

**Safety**: Firmware enforces `MOTOR_PWM_MAX = 153` (3.0V) to protect motor.

---

## 📡 **Serial Protocol Commands (NEW)**

### Motor Control (PWM):
```
MOTOR_SPEED:<0-153>     Set motor speed (0-153 PWM value)
                        Example: MOTOR_SPEED:76  (1.5V, slow)
                        Example: MOTOR_SPEED:153 (3.0V, max)
MOTOR_OFF               Stop motor (PWM = 0)
GET_MOTOR_SPEED         Read current motor PWM value
```

### Accelerometer (I2C):
```
ACCEL_INIT              Re-scan and initialize accelerometer
GET_ACCEL               Read X,Y,Z acceleration (in g's)
                        Response: ACCEL:0.05,-0.02,1.02
GET_VIBRATION_LEVEL     Read vibration magnitude
                        Response: VIBRATION:0.156
ACCEL_CALIBRATE         Calibrate zero-point (keep still!)
ACCEL_SET_THRESHOLD:val Set vibration detection threshold
                        Example: ACCEL_SET_THRESHOLD:0.2
```

### Existing Commands (unchanged):
```
WDT_RESET               Reset watchdog (heartbeat)
LASER_ON                Enable aiming laser
LASER_OFF               Disable aiming laser
GET_PHOTODIODE          Read photodiode voltage
GET_FOOTPEDAL           Read footpedal state (future)
GET_STATUS              Get all sensor states
```

---

## 🔬 **Accelerometer Data Logging**

The accelerometer can provide:
- **3-axis acceleration** (X, Y, Z in g's)
- **Vibration magnitude** (combined motion)
- **Threshold detection** (motor running vs stopped)
- **Data capture** for analysis

**Typical Values**:
- At rest: X≈0, Y≈0, Z≈1 (gravity)
- Motor running: Vibration magnitude > threshold (e.g., 0.1-0.5g)
- Motor stopped: Vibration magnitude < threshold

**Use Cases**:
- Verify motor is actually spinning
- Tune vibration threshold
- Correlate vibration with treatment quality
- Detect motor degradation over time

---

## ⚙️ **What Needs to be Done Next**

### Immediate (You):
1. **Upload new firmware** to Arduino Uno
   - Follow `UPLOAD_INSTRUCTIONS.md`
   - Use Arduino IDE
   - Upload `arduino_watchdog_v2.ino`

2. **Connect hardware** (if not already):
   - Motor to D9 + GND
   - Accelerometer to 5V, GND, A4, A5
   - Photodiode to A0
   - Aiming laser to D4 (optional)

3. **Test in Serial Monitor**:
   ```
   GET_STATUS              # Should show all sensors
   MOTOR_SPEED:100         # Motor should run at 2V
   GET_ACCEL               # Should return X,Y,Z values
   GET_VIBRATION_LEVEL     # Should increase with motor on
   ```

### Soon (Code Updates):
4. **Update Python GPIO controller**
   - Add PWM motor commands
   - Add I2C accelerometer reading
   - Add vibration monitoring
   - Update safety interlock logic

5. **Update GUI**
   - Add motor speed slider (0-153)
   - Add real-time vibration display
   - Add accelerometer data plot
   - Add vibration threshold adjustment

6. **Testing & Calibration**:
   - Calibrate accelerometer (motor OFF)
   - Set vibration threshold
   - Test motor speeds (50, 100, 150)
   - Verify vibration detection
   - Test watchdog timeout (stop heartbeat)

---

## 📊 **Implementation Status**

| Component | Hardware | Firmware | Config | Python | GUI | Status |
|-----------|----------|----------|--------|--------|-----|--------|
| **PWM Motor** | [DONE] | [DONE] | [DONE] | [PENDING] | [PENDING] | Ready for upload |
| **I2C Accelerometer** | [DONE] | [DONE] | [DONE] | [PENDING] | [PENDING] | Ready for upload |
| **Photodiode** | [DONE] | [DONE] | [DONE] | [PENDING] | [PENDING] | Existing (no changes) |
| **Aiming Laser** | [PENDING] | [DONE] | [DONE] | [PENDING] | [PENDING] | Ready (if hardware connected) |
| **Footpedal** | [FAILED] | [DONE] | [DONE] | [FAILED] | [FAILED] | Reserved for future |
| **Watchdog** | [DONE] | [DONE] | [DONE] | [DONE] | [DONE] | Fully functional |

**Legend**: [DONE] Done | [PENDING] Needs update | [FAILED] Not started

---

## 🛡️ **Safety Features (Preserved)**

All existing safety features remain functional:

1. **Hardware Watchdog** (1000ms timeout)
   - Requires heartbeat every 500ms
   - Emergency shutdown if software freezes
   - Motor + laser OFF on timeout

2. **PWM Limits** (motor protection)
   - Maximum PWM enforced: 153 (3.0V)
   - Prevents motor overvoltage damage

3. **Fail-safe Defaults**
   - All outputs start OFF on power-up
   - Safe state on watchdog timeout

---

## 📝 **Configuration Files Modified**

```
[DONE] firmware/arduino_watchdog/arduino_watchdog_v2.ino (NEW)
[DONE] firmware/arduino_watchdog/NEW_PIN_CONFIG.md (NEW)
[DONE] firmware/arduino_watchdog/UPLOAD_INSTRUCTIONS.md (NEW)
[DONE] config.yaml (UPDATED - GPIO section)
[PENDING] src/hardware/gpio_controller.py (NEEDS UPDATE)
[PENDING] src/ui/widgets/gpio_widget.py (NEEDS UPDATE)
```

---

## 🎯 **Next Session Goals**

1. Upload firmware to Arduino ✨
2. Test motor PWM control
3. Test accelerometer I2C communication
4. Calibrate accelerometer
5. Set vibration threshold
6. Update Python GPIO controller
7. Test complete system integration

---

## 📞 **Quick Reference**

### Motor Speeds to Try:
- `MOTOR_SPEED:50` - Very slow (1.0V)
- `MOTOR_SPEED:76` - Slow (1.5V)
- `MOTOR_SPEED:100` - Medium (2.0V) ← **Recommended default**
- `MOTOR_SPEED:127` - Fast (2.5V)
- `MOTOR_SPEED:153` - Maximum (3.0V) ⚠️

### Typical Vibration Values:
- Motor OFF: 0.01 - 0.05g
- Motor running: 0.1 - 0.5g (depends on speed)
- Recommended threshold: **0.1g**

### Arduino Upload Checklist:
- [ ] Arduino IDE installed
- [ ] COM6 port selected
- [ ] Board set to "Arduino Uno"
- [ ] Firmware compiles without errors
- [ ] Upload successful (see "Done uploading")
- [ ] Serial monitor shows "v2.0" startup message
- [ ] `GET_STATUS` command works
- [ ] Accelerometer detected (if connected)

---

**You're ready to upload! Follow `UPLOAD_INSTRUCTIONS.md` to get started.** 🚀
