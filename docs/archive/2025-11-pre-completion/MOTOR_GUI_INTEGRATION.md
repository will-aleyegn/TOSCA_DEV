# Motor Control & Accelerometer GUI Integration

**Last Updated:** 2025-11-04

**Status:** [DONE] COMPLETE
**Date:** 2025-10-27

---

## Summary

Added motor speed control and accelerometer monitoring to the TOSCA GUI Treatment tab. The motor widget provides a slider for PWM control (0-153), preset speed buttons, and real-time vibration monitoring with X/Y/Z acceleration display.

---

## Changes Made

### 1. GPIO Controller Extensions (`src/hardware/gpio_controller.py`)

**Added Signals:**
```python
motor_speed_changed = pyqtSignal(int)  # Motor PWM speed (0-153)
accelerometer_data_changed = pyqtSignal(float, float, float)  # X, Y, Z (g)
vibration_level_changed = pyqtSignal(float)  # Vibration magnitude (g)
```text

**Added State Variables:**
```python
self.motor_speed_pwm = 0  # PWM value (0-153)
self.accelerometer_initialized = False
self.accel_x, self.accel_y, self.accel_z = 0.0, 0.0, 0.0
self.vibration_level = 0.0
```text

**New Methods:**

1. **`set_motor_speed(pwm: int) -> bool`**
   - Sets motor speed using PWM (0-153)
   - 0 = OFF, 76 = 1.5V (min), 153 = 3.0V (max)
   - Clamps to safe range automatically
   - Sends `MOTOR_SPEED:XX` or `MOTOR_OFF` command

2. **`init_accelerometer() -> bool`**
   - Initializes MPU6050 accelerometer at I2C address 0x68
   - Must be called before reading acceleration
   - Uses motor-first sequence to avoid Arduino reset

3. **`get_acceleration() -> tuple[float, float, float] | None`**
   - Reads X, Y, Z acceleration in g's
   - Emits `accelerometer_data_changed` signal
   - Returns None if not initialized

4. **`get_vibration_level() -> float | None`**
   - Reads vibration magnitude from MPU6050
   - Emits `vibration_level_changed` signal
   - Useful for motor health monitoring

---

### 2. Motor Widget (`src/ui/widgets/motor_widget.py`)

**New file** - Complete motor control and accelerometer display widget.

**Features:**

#### Motor Control Section
- **Speed Slider**: Horizontal slider (0-153 PWM)
- **Speed Label**: Shows current speed (OFF/VERY LOW/LOW/MEDIUM/HIGH)
- **PWM Display**: Shows exact PWM value
- **Voltage Display**: Calculates and shows voltage (0-5V)

#### Preset Buttons
- **STOP** (red): PWM 0
- **LOW**: PWM 76 (1.5V)
- **MEDIUM**: PWM 100 (2.0V)
- **HIGH**: PWM 127 (2.5V)
- **MAX** (orange): PWM 153 (3.0V)

#### Accelerometer Monitor Section
- **Initialize Button**: Initializes MPU6050
- **Auto-Refresh Toggle**: Enables 2-second automatic data refresh
- **Vibration Display**: Large color-coded vibration level
  - Green: < 0.1g (low)
  - Orange: 0.1-0.3g (medium)
  - Red: > 0.3g (high)
- **X, Y, Z Display**: Shows 3-axis acceleration in g's
- **Status Label**: Shows initialization status

**Key Implementation Details:**

```python
def _set_speed(self, pwm: int) -> None:
    """
    Uses motor-first sequence:
    1. Set motor speed
    2. Wait 1.5 seconds for stabilization
    3. Auto-initialize accelerometer if needed
    """
```text

---

### 3. Treatment Widget Integration (`src/ui/widgets/treatment_widget.py`)

**Changes:**
```python
# Import motor widget
from ui.widgets.motor_widget import MotorWidget

# Add to __init__
self.motor_widget: MotorWidget = MotorWidget()

# Add to right side layout (below actuator widget)
right_layout.addWidget(self.motor_widget)
```text

**Layout:**
```
┌────────────┬────────────┬─────────────────┐
│   Laser    │ Treatment  │   Actuator      │
│  Controls  │  Controls  │   Controls      │
│            │            │                 │
│            │            ├─────────────────┤
│            │            │  Motor Control  │
│            │            │  & Accelerometer│
└────────────┴────────────┴─────────────────┘
```text

---

### 4. Main Window Connection (`src/ui/main_window.py`)

**GPIO Controller Connection:**
```python
# Connect GPIO controller to motor widget
if hasattr(self.treatment_widget, "motor_widget"):
    motor_widget = self.treatment_widget.motor_widget
    motor_widget.set_gpio_controller(gpio_widget.controller)
    logger.info("GPIO controller connected to motor widget")
```text

**Dev Mode Connection:**
```python
# Connect dev mode to motor widget
if hasattr(self.treatment_widget, "motor_widget"):
    self.dev_mode_changed.connect(self.treatment_widget.motor_widget.set_dev_mode)
```text

---

## Usage Instructions

### 1. Start TOSCA GUI
```bash
python src/main.py
```text

### 2. Connect Arduino Watchdog
- Navigate to **Safety Status** tab
- Click **Connect GPIO**
- Select COM port (COM6)
- Motor widget will enable automatically when connected

### 3. Control Motor Speed

**Using Slider:**
1. Drag slider to desired PWM value (0-153)
2. Motor speed updates automatically
3. Voltage display shows equivalent voltage

**Using Preset Buttons:**
1. Click any preset button (STOP/LOW/MEDIUM/HIGH/MAX)
2. Motor jumps to that speed immediately
3. If motor was off, accelerometer auto-initializes after 1.5s

### 4. Monitor Vibration

**Initialize Accelerometer:**
1. Start motor at desired speed
2. Wait 1-2 seconds for stabilization
3. Click **Initialize Accelerometer**
4. Status will show "Ready (MPU6050 @ 0x68)"

**Enable Auto-Refresh:**
1. Click **Auto-Refresh: OFF** button
2. Button changes to **Auto-Refresh: ON**
3. Vibration and acceleration update every 2 seconds

**Read Displays:**
- **Vibration**: Shows magnitude in g's (color-coded)
- **X, Y, Z**: Shows 3-axis acceleration
- **Status**: Shows initialization state

---

## Hardware Requirements

### Arduino Uno (Watchdog)
- **Firmware**: arduino_watchdog_v2.1 (with watchdog timing fixes)
- **Port**: COM6 (or configured port)
- **Baud Rate**: 9600

### DC Coreless Motor
- **Model**: 7x25mm (Amazon B0967SC28N)
- **Connection**: Arduino D9 (PWM)
- **Voltage**: 1.5-3.0V
- **Current**: ~6-20mA

### MPU6050 Accelerometer
- **Interface**: I2C (address 0x68)
- **Connections**:
  - VCC → Arduino 5V
  - GND → Arduino GND
  - SDA → Arduino A4
  - SCL → Arduino A5

---

## Serial Commands (Sent by GUI)

### Motor Control
```
MOTOR_SPEED:76   # Set motor to PWM 76 (1.5V)
MOTOR_SPEED:100  # Set motor to PWM 100 (2.0V)
MOTOR_SPEED:153  # Set motor to PWM 153 (3.0V max)
MOTOR_OFF        # Stop motor (PWM 0)
GET_MOTOR_SPEED  # Read current PWM value
```text

### Accelerometer
```
ACCEL_INIT             # Initialize MPU6050
GET_ACCEL              # Read X, Y, Z acceleration
GET_VIBRATION_LEVEL    # Read vibration magnitude
ACCEL_CALIBRATE        # Calibrate zero-point
ACCEL_SET_THRESHOLD:X  # Set vibration threshold
```text

### Watchdog
```
WDT_RESET   # Heartbeat (sent every 500ms automatically)
```text

---

## Important Notes

### WARNING: Motor-First Sequence

**Always start motor BEFORE initializing accelerometer!**

**Why?** Starting the motor creates electrical transients that can reset the Arduino if the accelerometer is already initialized. The motor widget handles this automatically:

1. User sets motor speed → Motor starts
2. Wait 1.5 seconds → Motor stabilizes
3. Auto-init accelerometer → Ready to read

**Manual sequence:**
```python
gpio_controller.set_motor_speed(100)  # Start motor
time.sleep(1.5)                       # Wait for stabilization
gpio_controller.init_accelerometer()  # Now safe to init
gpio_controller.get_vibration_level() # Read vibration
```bash

### Power Considerations

- Arduino may reset on repeated accelerometer reads
- Single vibration reads are reliable
- Use 2-second intervals for auto-refresh
- External 5V power supply recommended

### Safety Integration

- Motor speed is logged to event system
- All speed changes emit signals for monitoring
- Emergency stop via STOP button always available
- Watchdog automatically resets if GUI disconnects

---

## Testing

### Quick Function Test

1. **Motor Control Test:**
   ```
   - Click "LOW" button
   - Verify motor starts spinning
   - Check PWM shows "76" and voltage "1.49V"
   - Click "STOP"
   - Verify motor stops
   ```text

2. **Accelerometer Test:**
   ```
   - Start motor at MEDIUM speed
   - Wait 2 seconds
   - Click "Initialize Accelerometer"
   - Verify status shows "Ready"
   - Check X, Y, Z values appear
   - Check vibration level > 0.15g
   ```text

3. **Auto-Refresh Test:**
   ```
   - With motor running and accel initialized
   - Click "Auto-Refresh: OFF"
   - Verify button changes to "ON"
   - Watch vibration value update every 2 seconds
   - Tap motor mount to see vibration spike
   ```

### Full Integration Test

See: `test_complete_integration.py` for standalone Python test

---

## Troubleshooting

### Motor widget disabled
- Check GPIO connection on Safety Status tab
- Verify Arduino on COM6
- Check firmware is arduino_watchdog_v2.1

### Accelerometer initialization fails
- Start motor first, wait 2 seconds
- Check wiring: SDA→A4, SCL→A5, VCC→5V, GND→GND
- Verify MPU6050 power LED is lit
- Check I2C address is 0x68

### Arduino resets during operation
- Use 2-second auto-refresh interval (not faster)
- External 5V power supply recommended
- Consider transistor motor driver for isolation

### Vibration reads 0.000g
- Accelerometer needs re-initialization after reset
- Click "Initialize Accelerometer" again
- Check motor is actually running

---

## Future Enhancements

### Possible Improvements

1. **Vibration Alerts**
   - Set threshold for motor failure detection
   - Audio/visual alarm when vibration too high/low
   - Log vibration anomalies to database

2. **Motor Health Tracking**
   - Store vibration history over time
   - Detect bearing wear from vibration patterns
   - Predict motor failure

3. **Treatment Integration**
   - Auto-start motor during treatment protocols
   - Monitor vibration during laser delivery
   - Stop treatment if motor fails

4. **Advanced Controls**
   - PID speed control for precise RPM
   - Acceleration/deceleration ramping
   - Speed profiles for different treatment types

5. **Hardware Improvements**
   - Transistor motor driver circuit
   - Separate motor power supply
   - EMI filtering for cleaner signals

---

## Files Modified/Created

### New Files
- `src/ui/widgets/motor_widget.py` (389 lines)
- `MOTOR_GUI_INTEGRATION.md` (this file)

### Modified Files
- `src/hardware/gpio_controller.py`
  - Added 3 signals, 6 state variables, 4 methods (156 lines added)
- `src/ui/widgets/treatment_widget.py`
  - Added motor_widget import and integration (4 lines changed)
- `src/ui/main_window.py`
  - Added GPIO and dev mode connections (8 lines added)

---

## [DONE] Integration Complete

**Motor speed control and accelerometer monitoring are now fully integrated into the TOSCA GUI!**

The motor widget appears on the Treatment Control tab, right side, below the actuator controls. Users can adjust motor speed with a slider or preset buttons, and monitor real-time vibration with color-coded feedback.

**Ready for production testing!**
