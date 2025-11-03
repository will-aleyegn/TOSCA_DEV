# Xeryon Actuator Module - API Documentation

**Purpose:** Explore and document the Xeryon linear actuator API for TOSCA integration

**Hardware:** Xeryon Linear Stage (Piezoelectric)
**Communication:** USB Serial (pyserial)
**Library:** Xeryon.py (v1.88)

---

## Quick Reference

### Hardware Not Connected Yet
This module is prepared for when the Xeryon actuator is connected via USB. All test scripts are ready to run.

### Key Capabilities
- **Position Control:** Absolute positioning with µm/nm precision
- **Speed Control:** Adjustable movement speed
- **Index Finding:** Home position detection
- **Movement:** Relative and absolute positioning
- **Units:** mm, µm, nm, encoder units, degrees, radians
- **Safety:** Position limits, error detection, thermal protection

---

## Xeryon API Overview

### 1. Initialization

```python
from Xeryon import Xeryon, Axis, XLS_Stage, Units

# Create Xeryon controller object
controller = Xeryon(COM_port="COM3", baudrate=115200)

# Create axis (single axis system for TOSCA)
axis = Axis(controller, "A", XLS_Stage.XLS_312)

# Start the system
controller.start()

# Find index (home) position
axis.findIndex()
```

### 2. Movement Commands

#### Absolute Positioning
```python
# Set desired position (DPOS)
axis.setDPOS(1000)  # Move to 1000 µm in current units

# Specify units explicitly
axis.setDPOS(1.5, Units.mm)  # Move to 1.5 mm
axis.setDPOS(500, Units.mu)  # Move to 500 µm
axis.setDPOS(5000, Units.nm)  # Move to 5000 nm
```

#### Relative Movement
```python
# Make relative step from current position
axis.makeStep(100)  # Step +100 µm forward
axis.makeStep(-50)  # Step -50 µm backward
```

#### Continuous Movement
```python
# Start continuous movement
axis.move(1)   # Move forward continuously
axis.move(-1)  # Move backward continuously
axis.move(0)   # Stop movement
```

### 3. Position Reading

```python
# Get current encoder position (EPOS)
current_pos = axis.getEPOS()  # Returns position in current units

# Get desired position (DPOS)
target_pos = axis.getDPOS()

# Get position in specific units
pos_mm = axis.getEPOS(Units.mm)
pos_um = axis.getEPOS(Units.mu)
pos_nm = axis.getEPOS(Units.nm)
```

### 4. Speed Control

```python
# Set scan speed (SSPD) - encoder units per control cycle
axis.sendCommand("SSPD=100")  # Slower movement
axis.sendCommand("SSPD=500")  # Faster movement

# Query current speed
axis.sendCommand("SSPD=?")
```

### 5. Status Checking

```python
# Check if encoder is valid (index found)
is_homed = axis.isEncoderValid()

# Check if position reached
reached = axis.isPositionReached()

# Check if searching for index
searching = axis.isSearchingIndex()

# Check if in safe mode (error state)
safe_mode = axis.isInSafeMode()

# Get full status word
status = axis.getSTAT()
```

### 6. Settings and Limits

```python
# Set position limits
axis.sendCommand("HLIM=3000")  # High limit in encoder units
axis.sendCommand("LLIM=0")     # Low limit in encoder units

# Set maximum amplitude (voltage limit)
axis.sendCommand("MAMP=36400")  # Limit to 25V (max is 45V at 65535)

# Position tolerance (when position is "reached")
axis.sendCommand("PTOL=2")  # Tolerance in encoder units

# Timeout settings
axis.sendCommand("TOUT=50")   # Position timeout in ms
axis.sendCommand("TOU2=60")   # Safety timeout in seconds
```

### 7. Error Handling

```python
# Reset controller
axis.reset()

# Enable after error
axis.sendCommand("ENBL=1")

# Check for specific errors
status = axis.getSTAT()
# Bit 2-3: Thermal protection
# Bit 16: Error limit exceeded
# Bit 18: Safety timeout

# Stop all movement
controller.stopMovements()
```

### 8. Cleanup

```python
# Stop and close connection
controller.stop()
```

---

## Units System

The Xeryon API supports multiple unit systems:

```python
Units.mm      # Millimeters
Units.mu      # Micrometers (µm)
Units.nm      # Nanometers
Units.enc     # Encoder units (raw)
Units.inch    # Inches
Units.minch   # Milli-inches
Units.deg     # Degrees (for rotary stages)
Units.rad     # Radians
Units.mrad    # Milliradians
```

**For TOSCA:** We'll primarily use `Units.mu` (micrometers) for ring size control (0-3000 µm).

---

## Command Reference

### Essential Commands (Serial Protocol)

| Command | Description | Example |
|---------|-------------|---------|
| `INDX=0` | Find index position | `INDX=0` (bidirectional search) |
| `DPOS=N` | Set desired position | `DPOS=1000` (move to encoder position 1000) |
| `EPOS=?` | Query current position | Returns current encoder position |
| `STEP=N` | Relative step | `STEP=100` (step +100 from current) |
| `MOVE=D` | Continuous movement | `MOVE=1` (forward), `MOVE=-1` (back), `MOVE=0` (stop) |
| `SSPD=N` | Set scan speed | `SSPD=500` |
| `HLIM=N` | High position limit | `HLIM=3000` |
| `LLIM=N` | Low position limit | `LLIM=0` |
| `STAT=?` | Query status | Returns 32-bit status word |
| `STOP=0` | Stop movement | Immediate stop |
| `ZERO=0` | Force zero signal | Emergency stop |
| `RSET=0` | Reset controller | Clear errors |
| `ENBL=1` | Enable after error | Re-enable amplifier |
| `PTOL=N` | Position tolerance | `PTOL=2` (reached when within ±2 encoder units) |
| `MAMP=N` | Max amplitude | `MAMP=65535` (45V max), `MAMP=36400` (25V) |

### Status Bits (STAT register)

```
Bit 0:  Encoder valid (index found)
Bit 1:  Searching for index
Bit 2:  Thermal protection 1
Bit 3:  Thermal protection 2
Bit 4:  Position reached
Bit 10: Moving
Bit 16: Error limit exceeded
Bit 18: Safety timeout (TOU2)
Bit 28: Safe mode active
```

---

## Communication Protocol

### Serial Settings
- **Baud Rate:** 115200 (default)
- **Data Bits:** 8
- **Stop Bits:** 1
- **Parity:** None
- **Flow Control:** None

### Command Format
```
{axis_letter}{COMMAND}={VALUE}\r\n
```

Examples:
```
AINDX=0\r\n      # Axis A: Find index
ADPOS=1000\r\n   # Axis A: Move to position 1000
AEPOS=?\r\n      # Axis A: Query current position
```

For single-axis systems, the axis letter defaults to "A".

---

## Safety Features

### Thermal Protection
- **Issue:** Piezo stages can overheat with continuous operation
- **Protection:** Automatic shutdown if thermal limits exceeded
- **Recovery:** Power cycle hardware (30+ seconds), then `ENBL=1`

### Position Limits
- **HLIM:** High limit prevents over-travel
- **LLIM:** Low limit prevents under-travel
- **ELIM:** Error limit - following error threshold

### Timeouts
- **TOUT:** Position landing timeout (50ms default)
- **TOU2:** Safety timeout - motor on time limit (60s default)
- **TOU3:** Position landing attempt timeout

### Safe Mode
- **Trigger:** Error limit, thermal protection, timeout
- **Behavior:** Motor signals disabled
- **Recovery:** `RSET=0` or `ENBL=1`

---

## Typical Workflow for TOSCA

```python
# 1. Initialize
controller = Xeryon(COM_port="COM3")
axis = Axis(controller, "A", XLS_Stage.XLS_312)
controller.start()

# 2. Home the stage
axis.findIndex()

# 3. Set working units
axis.setUnit(Units.mu)  # Work in micrometers

# 4. Set safety limits (0-3000 µm for TOSCA)
axis.sendCommand("HLIM=3000")
axis.sendCommand("LLIM=0")

# 5. Move to starting position
axis.setDPOS(1500)  # Start at middle (1.5mm)

# 6. During treatment - adjust ring size
axis.setDPOS(ring_size_um)  # Move to desired ring size

# 7. Check position
current_pos = axis.getEPOS(Units.mu)
is_there = axis.isPositionReached()

# 8. Cleanup
controller.stop()
```

---

## Key Differences from Camera API

| Feature | Camera (VmbPy) | Actuator (Xeryon) |
|---------|----------------|-------------------|
| Connection | USB with VmbPy context manager | Serial port (pyserial) |
| Initialization | `with Vimba.get_instance()` | `controller.start()` |
| Homing | Not required | **Required** (findIndex) before movement |
| Units | Pixels | mm, µm, nm, encoder units |
| Continuous Operation | Frame streaming | Position control |
| Primary Concern | Frame rate, exposure | Position accuracy, speed |
| Safety | None (passive) | Thermal, limits, timeouts |
| Cleanup | Context manager auto-closes | Must call `controller.stop()` |

---

## Known Limitations

1. **Index Required:** Must find index before absolute positioning works correctly
2. **Thermal Limits:** Cannot run continuously at high speed without cooldown
3. **Single Thread:** Xeryon.py uses threading internally - don't create external threads
4. **Settings File:** Requires `settings_default.txt` in same directory as script
5. **Encoder Units:** Conversion from encoder to real units depends on stage model

---

## Testing Strategy (When Hardware Connected)

### Phase 1: Basic Connection (01, 02)
1. Detect available COM ports
2. Connect to controller
3. Read stage information
4. Verify communication

### Phase 2: Index Finding (03)
1. Find index position
2. Verify encoder valid bit
3. Test bidirectional search
4. Measure index finding time

### Phase 3: Position Control (04, 05)
1. Absolute positioning (setDPOS)
2. Relative movements (makeStep)
3. Position reading (getEPOS)
4. Unit conversions

### Phase 4: Speed and Limits (06)
1. Speed control (SSPD)
2. Position limits (HLIM/LLIM)
3. Safety testing
4. Error recovery

### Phase 5: TOSCA Integration (07)
1. Ring size range testing (0-3000 µm)
2. Position accuracy measurement
3. Response time testing
4. Integration with GUI

---

## TOSCA Ring Size Requirements

**Range:** 0 - 3000 µm (0 - 3 mm)
**Resolution:** 1 µm desired
**Speed:** TBD (clinical workflow dependent)
**Accuracy:** ±5 µm acceptable

The Xeryon XLS stage can easily meet these requirements with sub-µm accuracy.

---

## Additional Resources

- **Xeryon Documentation:** https://xeryon.com/software/xeryon-python-library/
- **Command Reference:** `docs/actuator-control/xeryon-stage-usb-commands.txt`
- **Sequence Builder:** `docs/actuator-control/xeryon_sequence_builder.py`
- **Settings File:** `actuator_module/settings_default.txt`

---

**Module Status:** Ready for hardware connection and testing
**Next Steps:** Connect actuator, run test scripts, document actual behavior
