# TOSCA Arduino Uno - NEW Pin Configuration
# Updated for actual hardware: DC Motor + I2C Accelerometer

## Hardware Specifications

### 1. Smoothing Motor (DC Motor)
- **Model**: Amazon B0967SC28N
- **Voltage Range**: 1.5V - 3.0V DC
- **Control Method**: PWM (Pulse Width Modulation)
- **Arduino Pin**: D9 (PWM capable)
- **Connection**:
  - Motor (+) → Arduino D9
  - Motor (-) → Arduino GND

### 2. Accelerometer (I2C)
- **Model**: Amazon B01DK83ZYQ (ADXL345 or MPU6050)
- **Communication**: I2C (SDA/SCL)
- **Power**: 5V, ~2mA current draw
- **Arduino Pins**:
  - VCC → Arduino 5V
  - GND → Arduino GND
  - SDA → Arduino A4 (I2C Data)
  - SCL → Arduino A5 (I2C Clock)

### 3. Photodiode (Laser Power Monitor)
- **Type**: Analog voltage input (0-5V)
- **Arduino Pin**: A0
- **Purpose**: Real-time laser power verification

### 4. Aiming Laser (650nm Red)
- **Type**: Digital on/off control
- **Arduino Pin**: D4
- **Purpose**: Visual alignment

### 5. Footpedal (Optional - Future)
- **Type**: Digital input (normally open switch)
- **Arduino Pin**: D5 (INPUT_PULLUP)
- **Purpose**: Deadman safety switch

---

## Pin Assignment Table

| Pin | Function | Direction | Device | Voltage |
|-----|----------|-----------|--------|---------|
| **D4** | Aiming Laser | OUTPUT | Red laser control | Digital 0/5V |
| **D5** | Footpedal | INPUT_PULLUP | Safety switch | Digital (active LOW) |
| **D9** | Motor Control | PWM OUTPUT | Smoothing motor | PWM 1.5-3V |
| **A0** | Photodiode | ANALOG IN | Laser power sensor | 0-5V analog |
| **A4** | SDA | I2C DATA | Accelerometer | I2C protocol |
| **A5** | SCL | I2C CLOCK | Accelerometer | I2C protocol |

---

## PWM Motor Speed Control

The motor requires variable voltage (1.5V - 3.0V) for speed control.
Arduino's analogWrite() provides PWM with values 0-255:

```
Speed Level    Voltage    PWM Value    Duty Cycle
───────────────────────────────────────────────────
MIN (stopped)  0.0V       0            0%
LOW            1.5V       76           30%
MEDIUM         2.25V      115          45%
HIGH           3.0V       153          60%
MAX (danger)   5.0V       255          100% WARNING: DO NOT USE
```

**CRITICAL**: Never exceed 3.0V (PWM 153) to avoid motor damage!

---

## I2C Accelerometer Communication

The accelerometer uses I2C protocol with Arduino's Wire library:

```cpp
#include <Wire.h>

// Common I2C addresses (depends on model):
#define ACCEL_ADDR_ADXL345  0x53  // ADXL345
#define ACCEL_ADDR_MPU6050  0x68  // MPU6050

// I2C pins are fixed on Uno:
// SDA = A4
// SCL = A5
```

**Features Available:**
- 3-axis acceleration data (X, Y, Z)
- Vibration detection (motion threshold)
- Tap detection
- Data logging for analysis

---

## Serial Protocol Commands (NEW)

### Motor Control (PWM):
```
MOTOR_SPEED:<value>     Set motor speed (0-153)
                        Example: MOTOR_SPEED:76 (1.5V)
                        Example: MOTOR_SPEED:153 (3.0V)
MOTOR_OFF               Stop motor (PWM = 0)
GET_MOTOR_SPEED         Read current motor speed
```

### Accelerometer (I2C):
```
GET_ACCEL               Read X, Y, Z acceleration (in g's)
                        Response: ACCEL:X,Y,Z
GET_VIBRATION_LEVEL     Read vibration magnitude
                        Response: VIBRATION:magnitude
ACCEL_CALIBRATE         Calibrate accelerometer (zero-point)
ACCEL_SET_THRESHOLD:val Set vibration detection threshold
```

### Existing Commands (unchanged):
```
WDT_RESET               Reset watchdog timer (heartbeat)
LASER_ON                Enable aiming laser (D4 HIGH)
LASER_OFF               Disable aiming laser (D4 LOW)
GET_PHOTODIODE          Read photodiode voltage (A0)
GET_FOOTPEDAL           Read footpedal state (D5)
GET_STATUS              Get all sensor states
```

---

## Circuit Notes

### Motor PWM Circuit:
```
Arduino D9 ──┬──> Motor (+)
             │
             └──[Flyback Diode]──> GND
                                   │
Motor (-) ─────────────────────────┘
```

**Flyback Diode**: 1N4001 or similar (protects Arduino from motor inductance)

### Accelerometer I2C:
```
Arduino 5V ────> Accel VCC
Arduino GND ───> Accel GND
Arduino A4 ─────> Accel SDA (with 4.7kΩ pull-up to 5V)
Arduino A5 ─────> Accel SCL (with 4.7kΩ pull-up to 5V)
```

**Pull-up Resistors**: Often built into accelerometer breakout board

---

## Required Arduino Libraries

```cpp
#include <Wire.h>           // I2C communication (built-in)
#include <avr/wdt.h>        // Watchdog timer (built-in)

// Third-party libraries (install via Library Manager):
#include <Adafruit_ADXL345_U.h>   // If using ADXL345
// OR
#include <MPU6050.h>               // If using MPU6050
```

---

## Safety Considerations

1. **Motor Overvoltage Protection**:
   - Maximum PWM value enforced in firmware: 153 (3.0V)
   - Software limits prevent exceeding motor ratings

2. **I2C Bus Stability**:
   - Pull-up resistors required (4.7kΩ typical)
   - Check for I2C address conflicts if adding more devices

3. **Vibration Threshold**:
   - Set threshold to detect motor running vs stopped
   - Too sensitive = false alarms
   - Not sensitive enough = misses motor failure

4. **Watchdog Integration**:
   - Motor stopped on watchdog timeout
   - Accelerometer checked during safety status

---

## Testing Procedure

### 1. Test Motor PWM:
```
MOTOR_SPEED:76     # Should run slowly (1.5V)
GET_MOTOR_SPEED    # Verify: 76
MOTOR_SPEED:153    # Should run faster (3.0V)
MOTOR_OFF          # Should stop
```

### 2. Test Accelerometer:
```
GET_ACCEL          # Should return X,Y,Z values
                   # At rest: ~0,0,1 (1g gravity on Z-axis)
GET_VIBRATION_LEVEL # Should be low when motor off
MOTOR_SPEED:100    # Start motor
GET_VIBRATION_LEVEL # Should increase with motor running
```

### 3. Test Vibration Detection:
```
ACCEL_SET_THRESHOLD:50  # Set sensitivity
MOTOR_OFF               # Vibration should drop below threshold
MOTOR_SPEED:100         # Vibration should exceed threshold
```

---

## Data Logging Format

Accelerometer data can be logged for analysis:

```
Timestamp, AccelX, AccelY, AccelZ, Magnitude, MotorSpeed
1698765432, 0.05, -0.02, 1.02, 0.06, 76
1698765433, 0.12, -0.08, 0.98, 0.15, 76
1698765434, 0.18, 0.05, 1.01, 0.19, 100
```

Use this to:
- Tune vibration detection threshold
- Verify motor runs consistently
- Detect motor degradation over time
- Correlate vibration with laser treatment quality
