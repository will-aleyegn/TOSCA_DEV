# Laser Control Component

**Status:** Complete - Ready for hardware testing
**Last Updated:** 2025-10-24

---

## Overview

Hardware abstraction layer (HAL) for Arroyo Instruments laser driver control.

**Features:**
- PyQt6-integrated controller with signals
- Serial communication via ASCII commands
- Power and current control
- TEC temperature monitoring
- Safety limits and interlocks
- Real-time status monitoring

---

## Hardware

**Device:** Arroyo Instruments Laser Diode Driver (e.g., 4320, 4321)
**Interface:** RS232 serial / USB virtual COM port
**Communication:** 38400 baud, 8-N-1, ASCII text commands

---

## Implementation Files

### Core Controller
- **Location:** `src/hardware/laser_controller.py`
- **Class:** `LaserController(QObject)`
- **Purpose:** Hardware abstraction with PyQt6 signals

### GUI Widget
- **Location:** `src/ui/widgets/laser_widget.py`
- **Class:** `LaserWidget(QWidget)`
- **Purpose:** User interface for laser control

### Documentation
- **API Reference:** `components/laser_control/ARROYO_API_REFERENCE.md`
- **External Resources:** `C:\Users\wille\Desktop\arroyo_laser_control\`

---

## Key Features

### 1. Connection Management
```python
from src.hardware.laser_controller import LaserController

controller = LaserController()
controller.connect("COM4", baudrate=38400)
```

### 2. Power Control
```python
# Set laser current
controller.set_current(500.0)  # 500 mA

# Enable output
controller.set_output(True)

# Read actual current
current = controller.read_current()  # Returns mA
```

### 3. Temperature Control
```python
# Set TEC temperature
controller.set_temperature(25.0)  # 25°C

# Read actual temperature
temp = controller.read_temperature()  # Returns °C
```

### 4. Signal Monitoring
```python
# Connect to signals
controller.current_changed.connect(on_current_update)
controller.temperature_changed.connect(on_temp_update)
controller.output_changed.connect(on_output_state)
controller.error_occurred.connect(on_error)
```

---

## PyQt6 Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `power_changed` | `float` | Power in mW |
| `current_changed` | `float` | Current in mA |
| `temperature_changed` | `float` | Temperature in °C |
| `connection_changed` | `bool` | Connection status |
| `output_changed` | `bool` | Output enable state |
| `error_occurred` | `str` | Error message |
| `status_changed` | `str` | Status description |
| `limit_warning` | `str` | Limit warning message |

---

## Safety Features

### 1. Current Limits
- Maximum current enforced before setting
- Read from device on connection
- Warning signal on limit approach

### 2. Temperature Limits
- High and low temperature limits
- Automatic shutdown on overtemperature
- Real-time monitoring (500ms updates)

### 3. Output Control
- Always disabled on disconnect
- Explicit enable required
- State verification after commands

---

## Serial Command Reference

See `ARROYO_API_REFERENCE.md` for complete command set.

### Essential Commands
```
*IDN?                    # Device identification
LAS:LDI <value>          # Set current (A)
LAS:LDI?                 # Read current (A)
LAS:OUT <0|1>            # Enable/disable output
TEC:T <value>            # Set temperature (°C)
TEC:T?                   # Read temperature (°C)
LAS:LIM:LDI <value>      # Set current limit (A)
TEC:LIM:THI <value>      # Set high temp limit (°C)
TEC:LIM:TLO <value>      # Set low temp limit (°C)
```

---

## Integration with TOSCA

### Treatment Widget Integration
The laser widget is integrated into the Treatment Control tab:

**Location:** `src/ui/widgets/treatment_widget.py`

**Layout:**
- Left: Laser controls (connection, power, temperature)
- Middle: Treatment controls (start/stop)
- Right: Actuator controls (positioning, sequences)

### Sequence Integration
Laser power can be set for each actuator sequence step:

```python
# In actuator_widget.py
params = {
    "position": 1000.0,
    "speed": 2000,
    "laser_power": 500.0,  # mW
    "acceleration": 65500,
    "deceleration": 65500
}
```

When sequence executes:
1. Set acceleration/deceleration
2. Set laser power
3. Execute movement
4. Laser power displayed in sequence list

---

## Testing

### Hardware Required
- Arroyo laser driver (e.g., 4320)
- USB-to-Serial adapter (if needed)
- Laser diode (for actual output testing)

### Test Procedure
1. **Connection Test**
   - Connect to COM port
   - Verify device ID query
   - Check status updates

2. **Current Control Test**
   - Set current to safe level (e.g., 100 mA)
   - Verify setpoint
   - Read actual current

3. **Output Control Test**
   - Enable output
   - Verify LED/indicator
   - Disable output

4. **Temperature Test**
   - Set TEC setpoint
   - Monitor temperature convergence
   - Verify limits

5. **Safety Test**
   - Attempt to exceed current limit
   - Attempt to exceed temperature limits
   - Verify warnings emitted

### Test Without Hardware
GUI can be tested in "dry run" mode:
- Connection will fail gracefully
- Controls will be disabled
- No actual hardware commands sent

---

## Common Issues

### 1. Connection Fails
**Symptom:** "Failed to connect to laser driver"

**Solutions:**
- Check COM port number (Windows Device Manager)
- Verify baud rate (38400 default)
- Check USB cable connection
- Try different USB port
- Restart device

### 2. No Response from Device
**Symptom:** Commands timeout, no status updates

**Solutions:**
- Check serial cable
- Verify device is powered
- Check baud rate matches device setting
- Try manual connection with terminal program

### 3. Current Won't Set
**Symptom:** Current setpoint fails

**Solutions:**
- Check if current exceeds device limit
- Verify device is in current mode
- Check for interlock conditions
- Read error status from device

---

## Future Enhancements

### Planned Features
- [ ] Power mode implementation (if supported by hardware)
- [ ] Photodiode feedback integration
- [ ] Automatic power ramping sequences
- [ ] Power vs time profiles
- [ ] Modulation control
- [ ] Data logging and plotting

### Hardware Integration
- [ ] GPIO safety interlocks (footpedal, photodiode)
- [ ] Synchronization with camera and actuator
- [ ] Treatment protocol execution
- [ ] Session recording

---

## References

**Documentation:**
- `ARROYO_API_REFERENCE.md` - Complete command reference
- `C:\Users\wille\Desktop\arroyo_laser_control\` - Downloaded resources
  - Computer Interfacing Manual
  - Device Manual (4320)
  - Python SDK examples

**External Resources:**
- Arroyo Instruments: https://www.arroyoinstruments.com/
- GitHub API: https://github.com/ArroyoInst/arroyo_tec
- TOSCA Project Status: `docs/project/PROJECT_STATUS.md`

---

## Development Notes

**Coding Standards:**
- Minimal code only
- Type hints on all functions
- Comprehensive docstrings
- Follows actuator_controller.py pattern
- PyQt6 signal-based architecture

**Safety Critical:**
- Every line matters
- All commands verified
- Graceful error handling
- No silent failures

---

**Component Status:** ✅ Complete - Ready for hardware testing
**Next Step:** Connect to actual Arroyo laser driver and test with hardware
