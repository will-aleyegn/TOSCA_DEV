# GPIO Safety Interlocks Component

**Status:** Complete - Ready for hardware testing
**Last Updated:** 2025-10-24

---

## Overview

Hardware abstraction layer (HAL) for FT232H-based safety interlocks.

**Safety Features:**
- Smoothing device control and monitoring
- Photodiode laser power verification
- Real-time status monitoring with PyQt6 signals
- Safety interlock enforcement

---

## Hardware

**Device:** Adafruit FT232H Breakout Board (USB-C)
**ADC:** MCP3008 (8-channel 10-bit ADC via SPI)
**Interface:** USB to GPIO/SPI conversion

### Pin Configuration

| Pin | Function | Direction | Description |
|-----|----------|-----------|-------------|
| C0 | Smoothing Motor | Output | Controls vibrating motor power |
| C1 | Vibration Sensor | Input | Reads accelerometer signal |
| C2 | SPI CS | Output | MCP3008 chip select |
| SCK | SPI Clock | Output | SPI clock signal |
| MOSI | SPI MOSI | Output | SPI data out |
| MISO | SPI MISO | Input | SPI data in |
| MCP3008 Ch0 | Photodiode | Analog In | Laser power monitoring (0-5V) |

---

## Implementation Files

### Core Controller
- **Location:** `src/hardware/gpio_controller.py`
- **Class:** `GPIOController(QObject)`
- **Purpose:** Hardware abstraction with PyQt6 signals

### GUI Widget
- **Location:** `src/ui/widgets/gpio_widget.py`
- **Class:** `GPIOWidget(QWidget)`
- **Purpose:** User interface for safety monitoring

### Safety Integration
- **Location:** `src/ui/widgets/safety_widget.py`
- **Integration:** GPIO widget embedded in Safety Status tab

---

## Key Features

### 1. Smoothing Device Control
```python
from src.hardware.gpio_controller import GPIOController

controller = GPIOController()
controller.connect()

# Enable smoothing motor
controller.set_smoothing_motor(True)

# Check vibration status
vibrating = controller.read_smoothing_vibration()
```

### 2. Photodiode Monitoring
```python
# Read photodiode voltage (0-5V)
voltage = controller.read_photodiode()

# Calibration: mW per volt
controller.set_photodiode_calibration(400.0)  # 2000mW / 5V
```

### 3. Safety Interlock Logic
```python
# Check if safe to enable laser
safety_ok = controller.is_safety_ok()

# Requirements:
# - Motor must be ON
# - Vibration must be DETECTED
```

### 4. Signal Monitoring
```python
# Connect to signals
controller.smoothing_motor_changed.connect(on_motor_state)
controller.smoothing_vibration_changed.connect(on_vibration_detected)
controller.photodiode_voltage_changed.connect(on_voltage_update)
controller.photodiode_power_changed.connect(on_power_update)
controller.safety_interlock_changed.connect(on_safety_status)
```

---

## PyQt6 Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `smoothing_motor_changed` | `bool` | Motor state (on/off) |
| `smoothing_vibration_changed` | `bool` | Vibration detected |
| `photodiode_voltage_changed` | `float` | Voltage in V (0-5V) |
| `photodiode_power_changed` | `float` | Calculated power in mW |
| `connection_changed` | `bool` | Connection status |
| `error_occurred` | `str` | Error message |
| `safety_interlock_changed` | `bool` | Safety OK status |

---

## Safety Interlock Logic

### Requirements for Laser Operation

**Both conditions MUST be satisfied:**

1. ✅ **Smoothing Motor ON**
   - Motor control pin (C0) HIGH
   - Motor actively powered

2. ✅ **Vibration DETECTED**
   - Vibration sensor pin (C1) HIGH
   - Accelerometer confirms motor vibration
   - Debounced (3 consecutive readings)

### Safety State Machine

```
UNSAFE → Motor OFF
      → Motor ON, No Vibration

SAFE   → Motor ON + Vibration Detected
```

### Photodiode Verification

- **Purpose:** Verify actual laser output matches setpoint
- **Range:** 0-5V (0-2000 mW with default calibration)
- **Usage:** Real-time power monitoring, not interlock
- **Future:** Can be used for power limit safety checks

---

## Hardware Setup

### Required Components

1. **Adafruit FT232H Breakout Board** (USB-C)
2. **MCP3008 ADC** (8-channel 10-bit, SPI interface)
3. **Smoothing Device:**
   - Vibrating motor (controlled by C0)
   - Accelerometer with digital output (connected to C1)
   - Power transistor/relay for motor control
4. **Photodiode Circuit:**
   - Laser pickoff photodiode
   - Trans-impedance amplifier
   - 0-5V output (connected to MCP3008 Ch0)

### Wiring Diagram

```
FT232H                         MCP3008
------                         -------
C0 ──────► Motor Control       VDD  ──► 3.3V
C1 ──────► Vibration Sensor    VREF ──► 3.3V
C2 (CS) ──────────────────► CS/SHDN
SCK ───────────────────────► CLK
MOSI ──────────────────────► DIN
MISO ──────────────────────► DOUT
GND ────────────────────────► AGND/DGND
                               CH0  ──► Photodiode
```

---

## Dependencies

### Required Libraries

```bash
pip install adafruit-blinka
pip install adafruit-circuitpython-mcp3xxx
pip install pyftdi  # For FT232H support
```

### Python Packages
- `adafruit-blinka` - CircuitPython compatibility layer
- `adafruit-circuitpython-mcp3xxx` - MCP3008 ADC driver
- `pyftdi` - FT232H USB driver
- `PyQt6` - GUI framework

---

## Testing

### Hardware Required
- Adafruit FT232H breakout
- MCP3008 ADC chip
- Smoothing device (motor + accelerometer)
- Photodiode circuit
- Breadboard and jumper wires

### Test Procedure

#### 1. **Connection Test**
```python
controller = GPIOController()
success = controller.connect()
assert success, "Connection failed"
```

#### 2. **Motor Control Test**
```python
# Enable motor
controller.set_smoothing_motor(True)
time.sleep(0.5)

# Check motor state
assert controller.motor_enabled
```

#### 3. **Vibration Detection Test**
```python
# With motor running
vibration = controller.read_smoothing_vibration()
assert vibration, "Should detect vibration with motor on"

# With motor off
controller.set_smoothing_motor(False)
time.sleep(1.0)
vibration = controller.read_smoothing_vibration()
assert not vibration, "Should not detect vibration with motor off"
```

#### 4. **Photodiode Reading Test**
```python
# Read voltage
voltage = controller.read_photodiode()
assert 0.0 <= voltage <= 5.0, "Voltage out of range"

# Check power calculation
power = controller.photodiode_power_mw
expected = voltage * 400.0  # Default calibration
assert abs(power - expected) < 0.1
```

#### 5. **Safety Interlock Test**
```python
# Test unsafe condition
controller.set_smoothing_motor(False)
assert not controller.is_safety_ok()

# Test safe condition
controller.set_smoothing_motor(True)
time.sleep(1.0)  # Wait for vibration
assert controller.is_safety_ok()
```

### Test Without Hardware

GUI can be tested in "dry run" mode:
- Import will fail gracefully if libraries missing
- Controls will show but connection will fail
- No actual hardware commands sent

---

## Common Issues

### 1. Import Error: "Adafruit libraries not available"

**Solution:**
```bash
pip install adafruit-blinka adafruit-circuitpython-mcp3xxx pyftdi
```

### 2. Connection Fails

**Solutions:**
- Check USB connection
- Verify FT232H is recognized by OS
- Windows: Install libusb driver using Zadig
- Linux: Add udev rules for FT232H
- Check no other program is using FT232H

### 3. MCP3008 Not Responding

**Solutions:**
- Verify SPI wiring (SCK, MOSI, MISO, CS)
- Check MCP3008 power (VDD = 3.3V)
- Verify chip select pin (C2)
- Test with SPI loopback

### 4. Vibration Not Detected

**Solutions:**
- Check accelerometer output voltage (should be 3.3V or 5V when vibrating)
- Verify pull-up/pull-down resistor configuration
- Increase debounce threshold if signal noisy
- Check motor is actually vibrating

### 5. Photodiode Readings Unstable

**Solutions:**
- Check photodiode circuit output impedance
- Verify MCP3008 reference voltage (VREF = 3.3V)
- Add smoothing capacitor to photodiode output
- Increase ADC sampling time
- Recalibrate voltage_to_power factor

---

## Calibration

### Photodiode Calibration Procedure

1. **Setup:**
   - Connect known laser power source
   - Connect photodiode to MCP3008 Ch0

2. **Measure Points:**
   - Set laser to known powers (e.g., 500, 1000, 1500, 2000 mW)
   - Record photodiode voltage for each power

3. **Calculate Factor:**
   ```python
   # Example: 2000 mW at 5.0 V
   voltage_to_power = 2000.0 / 5.0  # = 400 mW/V

   controller.set_photodiode_calibration(voltage_to_power)
   ```

4. **Verify:**
   - Test at multiple power levels
   - Adjust if non-linear response
   - Document calibration in system log

---

## Integration with TOSCA

### Safety Widget Integration
GPIO controls are integrated into the Safety Status tab:

**Location:** `src/ui/widgets/safety_widget.py`

**Layout:**
- Left: GPIO controls (smoothing device, photodiode)
- Right: Software interlocks, E-stop, event log

### Laser Interlock Integration

**Future Enhancement:**
Laser controller should check GPIO safety before enabling:

```python
# In laser_controller.py set_output()
if enabled:
    if not gpio_controller.is_safety_ok():
        self.error_occurred.emit("Safety interlocks not satisfied")
        return False

# Proceed with laser enable
```

---

## Monitoring Configuration

### Update Rate
- **Timer Interval:** 100ms (10 Hz)
- **Debounce Count:** 3 readings (300ms settling)
- **Signal Emission:** On state change only

### Performance
- **CPU Usage:** <1% (timer-based polling)
- **Latency:** <100ms (one timer cycle)
- **Thread Safety:** All operations in Qt event loop

---

## Future Enhancements

### Planned Features
- [ ] Footpedal input (digital input on C3)
- [ ] Dual photodiode support (MCP3008 Ch1)
- [ ] Watchdog timer for motor monitoring
- [ ] Power limit enforcement via photodiode
- [ ] Safety event logging
- [ ] Multi-level safety states

### Hardware Integration
- [ ] Laser enable interlock (software check)
- [ ] Emergency stop integration
- [ ] Redundant safety monitoring
- [ ] Session safety recording

---

## References

**Documentation:**
- Adafruit FT232H: https://learn.adafruit.com/adafruit-ft232h-breakout
- Blinka Library: https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h
- MCP3008 Datasheet: https://ww1.microchip.com/downloads/en/DeviceDoc/21295d.pdf
- TOSCA Project Status: `docs/project/PROJECT_STATUS.md`

**Libraries:**
- adafruit-blinka: https://github.com/adafruit/Adafruit_Blinka
- adafruit-circuitpython-mcp3xxx: https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx

---

## Development Notes

**Coding Standards:**
- Minimal code only
- Type hints on all functions
- Comprehensive docstrings
- Follows laser_controller.py pattern
- PyQt6 signal-based architecture

**Safety Critical:**
- Debounced vibration detection
- Fail-safe defaults (motor off)
- Explicit safety checks
- No silent failures
- All states logged

---

**Component Status:** ✅ Complete - Ready for hardware testing
**Phase 2 Status:** ✅ 100% Complete - All 4 HALs implemented
**Next Step:** Hardware testing with FT232H, MCP3008, and safety devices
