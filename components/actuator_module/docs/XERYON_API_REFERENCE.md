# Xeryon Python Library API Reference

**Library Version**: v1.88
**Hardware**: XLA Linear Actuators (TOSCA uses XLA-5-125-10MU)
**Official Documentation Source**: `C:\Users\wille\Desktop\stage-control\Xeryon.py`
**Last Updated**: 2025-10-23

---

## WARNING: CRITICAL: TOSCA Hardware Configuration

**TOSCA XLA-5-125-10MU Actuator is configured with:**
- **Baudrate**: `9600` (NOT the library default of 115200)
- **Encoder Resolution**: 1.25 µm (1250 nm)
- **Working Units**: Micrometers (µm)
- **Speed Range**: 50-500 µm/s

**Why the different baudrate?**
- The official Xeryon library default is 115200
- TOSCA hardware has been pre-configured by the manufacturer for 9600
- Using 115200 will result in communication failure
- Always use 9600 for TOSCA hardware

---

## Table of Contents

1. [Critical Configuration Constants](#critical-configuration-constants)
2. [Connection and Initialization](#connection-and-initialization)
3. [Stage Types (Enum)](#stage-types-enum)
4. [Units (Enum)](#units-enum)
5. [Position Control](#position-control)
6. [Speed Control](#speed-control)
7. [Homing (Index Finding)](#homing-index-finding)
8. [Status Monitoring](#status-monitoring)
9. [Data Conversion](#data-conversion)
10. [Common Patterns](#common-patterns)

---

## Critical Configuration Constants

**Location**: `Xeryon.py:9-38`

```python
# Library Configuration (Line 10-38)
LIBRARY_VERSION = "v1.88"

# DEBUG MODE
DEBUG_MODE = False  # Set True for testing without hardware

# OUTPUT_TO_CONSOLE
OUTPUT_TO_CONSOLE = True  # Print commands and responses

# DISABLE WAITING
DISABLE_WAITING = False  # If True, library won't wait for position reached

# AUTO_SEND_SETTINGS WARNING: CRITICAL
AUTO_SEND_SETTINGS = True  # Default: Send settings_default.txt on startup
# WARNING: For TOSCA: Set to False to use device-stored settings

# AUTO_SEND_ENBL
AUTO_SEND_ENBL = False  # Auto-send ENBL=1 on thermal/error events
```

### CRITICAL: AUTO_SEND_SETTINGS

**Default**: `True` - Library sends settings from `settings_default.txt` to device
**TOSCA Requirement**: `False` - Use device's stored settings (already configured)

**Why This Matters**:
- XLA actuators store optimized settings in non-volatile memory
- `settings_default.txt` may override device settings with incorrect values
- Homing and movement rely on correct settings (speed, limits, tolerances)

**TOSCA Implementation Strategy (Device-Stored Settings)**:

TOSCA uses **device-stored settings** approach for medical device reliability:

1. **No settings_default.txt required** - Device ships with manufacturer-calibrated settings
2. **Settings stored in non-volatile memory** - Persist across power cycles
3. **Graceful degradation** - Code falls back to conservative defaults if settings unavailable
4. **No file I/O during operation** - Eliminates potential failure point

**Benefits**:
- [DONE] Guaranteed manufacturer calibration for specific hardware unit
- [DONE] No file synchronization issues between code and device
- [DONE] Simplified deployment (no external config files needed)
- [DONE] Settings survive firmware updates and power cycles

**Implementation**:
```python
# ActuatorController does NOT modify AUTO_SEND_SETTINGS constant
# Instead, code handles None values from getSetting() gracefully:

low_str = self.axis.getSetting("LLIM")
if low_str is not None:
    self.low_limit_um = float(low_str)  # Use device value
else:
    # Use conservative default (already initialized in __init__)
    logger.debug("LLIM not available from device, using default")
```

**When getSetting() Returns None**:
- Device still initializing
- settings_default.txt missing (expected for TOSCA)
- Serial communication interrupted
- Setting not supported by hardware

**TOSCA Default Values** (used when device settings unavailable):
```python
self.low_limit_um = -45000.0   # -45 mm (conservative for XLA-5-125)
self.high_limit_um = 45000.0   # +45 mm (conservative for XLA-5-125)
self.acceleration = 65500      # From Xeryon defaults
self.deceleration = 65500      # From Xeryon defaults
```

**TOSCA Actual Device-Stored Values** (verified 2025-10-29):
After homing completes, `query_device_settings()` retrieves:
```python
# Retrieved (5/9 settings):
LLIM = -36000 µm   # -36 mm (actual hardware limit)
HLIM = 36000 µm    # +36 mm (actual hardware limit)
SSPD = 100000 µm/s # 100 mm/s (fast positioning speed)
PTOL = 2           # encoder units (primary tolerance)
PTO2 = 4           # encoder units (secondary tolerance)

# Not available (4/9 settings):
ACCE = None  # Uses default: 65500
DECE = None  # Uses default: 65500
TOUT = None  # Device default
ELIM = None  # Device default
```

**Critical Finding**: The device reports **±36mm limits**, not ±45mm. Using device-stored settings prevents commands beyond hardware travel range.

**Implementation**: `ActuatorController` automatically re-queries settings after homing completes, updating cached values (`low_limit_um`, `high_limit_um`) with manufacturer-calibrated parameters.

---

## Connection and Initialization

### 1. Create Controller

```python
from Xeryon import Xeryon, Stage, Units

# Official library default (for most hardware)
controller = Xeryon(COM_port="COM3", baudrate=115200)

# WARNING: TOSCA HARDWARE - Use 9600!
controller = Xeryon(COM_port="COM3", baudrate=9600)
```

**Parameters**:
- `COM_port` (str): Serial port name (e.g., "COM3", "COM4")
- `baudrate` (int): Communication speed
  - **Library Default**: `115200`
  - **TOSCA Hardware**: `9600` WARNING: (manufacturer pre-configured)
  - **CRITICAL**: Must match hardware configuration or communication fails

### 2. Add Axis

```python
# Add linear actuator axis
axis = controller.addAxis(Stage.XLA_1250_3N, "X")
```

**Parameters**:
- `stage` (Stage enum): Stage type with encoder resolution
- `axis_letter` (str): Axis identifier ("X", "Y", "Z", etc.)

### 3. Start Communication

```python
# Start communication thread and configure settings
controller.start()
```

**What This Does** (Line 73-115):
1. Starts serial communication thread
2. Sends RSET (reset) to all axes
3. Reads `settings_default.txt` (if AUTO_SEND_SETTINGS=True)
4. Sends settings to device
5. Enables all axes (ENBL=1)
6. Queries limits (HLIM, LLIM, SSPD, PTO2, PTOL)

### 4. Stop/Disconnect

```python
# Stop movements and close communication
controller.stop()
```

**What This Does** (Line 117-127):
1. Sends ZERO=0 to all axes
2. Sends STOP=0 to all axes
3. Closes serial communication
4. Prints "Program stopped running."

---

## Stage Types (Enum)

**Location**: `Xeryon.py:1278-1530`

### XLA Linear Actuators (1.25 µm encoder)

```python
# 3rd Generation
Stage.XLA_1250_3N = (True, "XLA3=1250", 1250, 1000)

# 5th Generation
Stage.XLA_1250_5N = (True, "XLA3=1250", 1250, 1000)

# 10th Generation
Stage.XLA_1250_10N = (True, "XLA3=1250", 1250, 1000)
```

**Tuple Structure**:
```python
(isLinear, encoderResolutionCommand, encoderResolution_nm, speedMultiplier)
```

- `isLinear` (bool): True for linear stages, False for rotary
- `encoderResolutionCommand` (str): Command to set encoder resolution
- `encoderResolution` (float): Resolution in **nanometers** (nm)
- `speedMultiplier` (int): Multiplier for speed settings (1000 for linear)

### Other XLA Variants

```python
# 312.5 nm encoder resolution
Stage.XLA_312_3N = (True, "XLA3=312", 312.5, 1000)

# 78.125 nm encoder resolution
Stage.XLA_78_3N = (True, "XLA3=78", 78.125, 1000)

# Open loop (no encoder)
Stage.XLA_OL_3N = (True, "XLA3=0", 1, 1000)
```

### TOSCA Hardware

**Model**: XLA-5-125-10MU
**Interpreted As**:
- **XLA**: Linear actuator type
- **5**: 5mm travel range (?)
- **125**: 1.25 µm encoder resolution
- **10MU**: 10th generation, micrometer units (?)

**Recommended Stage Type**: `Stage.XLA_1250_10N` (pending verification)

---

## Units (Enum)

**Location**: `Xeryon.py` (Units class)

```python
Units.mm   # Millimeters
Units.mu   # Micrometers (µm) ← TOSCA uses this
Units.nm   # Nanometers
Units.inch # Inches
Units.minch # Milli-inches
Units.enc  # Encoder units (native)
Units.deg  # Degrees (rotary stages)
Units.rad  # Radians (rotary stages)
Units.mrad # Milliradians (rotary stages)
```

### Set Working Units

```python
# Set axis working units
axis.setUnits(Units.mu)  # Micrometers for TOSCA

# Check current units
current_units = axis.units  # Returns Units enum
```

**Default Units**:
- Linear stages: `Units.mm` (millimeters)
- Rotary stages: `Units.deg` (degrees)

---

## Position Control

### Get Current Position

```python
# Get encoder position (EPOS) in current units
position = axis.getEPOS()  # Returns float in current units
```

**Returns**: Current position in `axis.units` (e.g., µm if units=Units.mu)

### Absolute Positioning

```python
# Move to absolute position
axis.setDPOS(100.0)  # Move to 100 µm (if units=Units.mu)
```

**What This Does** (internal):
1. Converts position from current units to encoder units
2. Sends `DPOS=<encoder_units>` command
3. Waits for position reached (unless DISABLE_WAITING=True)
4. Prints progress to console (if OUTPUT_TO_CONSOLE=True)

**Parameters**:
- `position` (float): Target position in current units
- `units` (Units, optional): Override current units for this command

**Blocking Behavior**: Waits until `isPositionReached()` returns True

### Relative Movement (Step)

```python
# Step relative to current position
axis.step(50.0)  # Move +50 µm from current position
axis.step(-25.0) # Move -25 µm from current position
```

**Parameters**:
- `distance` (float): Relative distance in current units
  - Positive: Move in positive direction
  - Negative: Move in negative direction

**Internal Implementation**:
```python
def step(self, distance):
    current = self.getEPOS()
    target = current + distance
    self.setDPOS(target)
```

---

## Speed Control

### Set Speed

```python
# Set movement speed
axis.setSpeed(100)  # 100 µm/s if units=Units.mu
```

**API Specification** (Line 665-678):

```python
def setSpeed(self, speed):
    """
    :param speed: The new speed this axis needs to operate on.
                  The speed is specified in the current units/second.
    :type speed: int
    """
    if self.stage.isLinear:
        # Convert to micrometers/second
        speed = int(self.convertEncoderUnitsToUnits(
            self.convertUnitsToEncoder(speed, self.units), Units.mu))
    else:
        # Convert to degrees (for rotary stages)
        speed = self.convertEncoderUnitsToUnits(
            self.convertUnitsToEncoder(speed, self.units), Units.deg)
        speed = int(speed) * 100  # *100 conversion factor

    self.setSetting("SSPD", str(speed))
```

**Key Points**:
- Input: Speed in **current units per second** (e.g., mm/s, µm/s)
- Internal conversion: Always stored as µm/s (linear) or deg (rotary)
- Sets the `SSPD` (speed) setting

**Examples**:
```python
# With units=Units.mu (micrometers)
axis.setSpeed(100)   # 100 µm/s
axis.setSpeed(500)   # 500 µm/s
axis.setSpeed(1000)  # 1000 µm/s = 1 mm/s

# With units=Units.mm (millimeters)
axis.setUnits(Units.mm)
axis.setSpeed(1)     # 1 mm/s = 1000 µm/s
```

### Get Current Speed

```python
# Get current speed setting (SSPD)
speed = axis.getSetting("SSPD")  # Returns string
```

**Note**: SSPD is stored in µm/s for linear stages

---

## Homing (Index Finding)

### Find Index (Home)

```python
# Find encoder index (homing procedure)
axis.findIndex(direction=0)
```

**Parameters**:
- `direction` (int):
  - `0`: Bidirectional search (default, fastest)
  - `1`: Search in positive direction only
  - `-1`: Search in negative direction only

**What This Does**:
1. Sends `INDX=<direction>` command
2. Waits for encoder index flag (`isEncoderAtIndex()`)
3. Sets encoder as valid
4. Prints "Index of axis X found." to console

**Blocking Behavior**: Waits until homing complete

### Check If Homed

```python
# Check if encoder is valid (homed)
is_homed = axis.isEncoderValid()  # Returns bool

# Check if at index position
at_index = axis.isEncoderAtIndex()  # Returns bool
```

---

## Status Monitoring

### Status Bits

All status checking methods take optional `external_stat` parameter:

```python
# Use current status (queries device)
status = axis.isThermalProtection1()

# Use external status value
status = axis.isThermalProtection1(external_stat=12345)
```

### Available Status Checks

**Location**: `Xeryon.py:726-826`

```python
# Thermal and Safety
axis.isThermalProtection1()      # Bit 2: Thermal error 1
axis.isThermalProtection2()      # Bit 3: Thermal error 2
axis.isErrorLimit()              # Bit 16: Error limit reached
axis.isSafetyTimeoutTriggered()  # Bit 18: Safety timeout (TOU2)
axis.isPositionFailTriggered()   # Bit 21: Position fail (TOU3)

# Motor State
axis.isForceZero()               # Bit 4: Force zero active
axis.isMotorOn()                 # Bit 5: Motor enabled
axis.isClosedLoop()              # Bit 6: Closed-loop control active

# Encoder
axis.isEncoderAtIndex()          # Bit 7: At encoder index
axis.isEncoderValid()            # Bit 8: Encoder homed/valid ← Important!
axis.isEncoderError()            # Bit 12: Encoder error

# Movement
axis.isSearchingIndex()          # Bit 9: Finding index (homing)
axis.isPositionReached()         # Bit 10: At target position ← Important!
axis.isScanning()                # Bit 13: Scanning mode active
axis.isSearchingOptimalFrequency() # Bit 17: Tuning frequency

# Limits
axis.isAtLeftEnd()               # Bit 14: Left limit switch
axis.isAtRightEnd()              # Bit 15: Right limit switch
```

### Get Raw Status

```python
# Get raw STAT value
stat = axis.getData("STAT")  # Returns string (integer value)
```

---

## Data Conversion

### Units to Encoder Conversion

```python
# Convert position from units to encoder units
encoder_pos = axis.convertUnitsToEncoder(value=100.0, units=Units.mu)
```

**Formula for Micrometers** (Line 1062-1063):
```python
encoder_units = round(value_mu * 10^3 * 1 / encoderResolution_nm)
```

**Example** (XLA-1250, resolution = 1250 nm):
```python
# 100 µm to encoder units
100 * 1000 / 1250 = 80 encoder units
```

### Encoder to Units Conversion

```python
# Convert encoder units to position
position_um = axis.convertEncoderUnitsToUnits(value=80, units=Units.mu)
```

**Formula for Micrometers** (Line 1093-1094):
```python
value_mu = encoder_units / (10^3 * 1 / encoderResolution_nm)
```

**Example** (XLA-1250, resolution = 1250 nm):
```python
# 80 encoder units to µm
80 / (1000 / 1250) = 100 µm
```

---

## Common Patterns

### Basic Movement Sequence

```python
from Xeryon import Xeryon, Stage, Units

# 1. Initialize (TOSCA hardware uses 9600 baud)
controller = Xeryon("COM3", 9600)
axis = controller.addAxis(Stage.XLA_1250_3N, "X")
controller.start()

# 2. Set working units
axis.setUnits(Units.mu)

# 3. Home the actuator
axis.findIndex()

# 4. Set speed
axis.setSpeed(100)  # 100 µm/s

# 5. Move to position
axis.setDPOS(500.0)  # Move to 500 µm

# 6. Get current position
pos = axis.getEPOS()
print(f"Current position: {pos} µm")

# 7. Make relative step
axis.step(50.0)  # Step +50 µm

# 8. Return to zero
axis.setDPOS(0.0)

# 9. Cleanup
controller.stop()
```

### Non-Blocking Movement

```python
# Disable automatic waiting
DISABLE_WAITING = True  # Set at top of file

# Move command returns immediately
axis.setDPOS(1000.0)

# Check position manually
while not axis.isPositionReached():
    current_pos = axis.getEPOS()
    print(f"Moving... {current_pos} µm")
    time.sleep(0.1)

print("Position reached!")
```

### Error Handling

```python
# Check for errors before movement
if axis.isEncoderValid():
    if not axis.isThermalProtection1() and not axis.isThermalProtection2():
        if not axis.isErrorLimit():
            # Safe to move
            axis.setDPOS(target)
        else:
            print("Error limit reached! Send ENBL=1")
            axis.sendCommand("ENBL=1")
    else:
        print("Thermal protection triggered!")
else:
    print("Encoder not valid - home first!")
    axis.findIndex()
```

### Speed Control Example

```python
# Demo from xeryon_demo.py (Line 104-105)
axis.setUnits(Units.mm)
axis.setSpeed(1)  # 1 mm/s

# Perform scan
axis.startScan(direction=1, duration=2)  # Positive dir, 2 seconds

# Equivalent in micrometers
axis.setUnits(Units.mu)
axis.setSpeed(1000)  # 1000 µm/s = 1 mm/s
```

---

## TOSCA-Specific Implementation Notes

### 1. Device-Stored Settings (CRITICAL)

**TOSCA uses manufacturer-calibrated settings stored in device non-volatile memory.**

**No settings_default.txt Required**:
- Device ships pre-configured with optimized settings
- Settings persist across power cycles and firmware updates
- Code gracefully handles None values from `getSetting()`
- Falls back to conservative defaults if device settings unavailable

**Implementation Pattern**:
```python
# Read device settings, fall back to defaults if None
low_str = axis.getSetting("LLIM")
if low_str is not None:
    low_limit = float(low_str)  # Use device-stored value
else:
    low_limit = -45000.0  # Conservative default
```

**See**: Section "CRITICAL: AUTO_SEND_SETTINGS" above for full details.

### 2. Baudrate

**CRITICAL**: TOSCA hardware uses `9600`, NOT the library default of `115200`

```python
# [DONE] Correct for TOSCA XLA-5-125-10MU
controller = Xeryon("COM3", 9600)

# [FAILED] Wrong for TOSCA - library default doesn't work
controller = Xeryon("COM3", 115200)
```

**Why 9600?**
- TOSCA XLA-5-125-10MU was pre-configured by manufacturer for 9600 baud
- This is stored in device non-volatile memory
- Official library default (115200) does NOT work with TOSCA hardware
- Always verify baudrate with actual hardware before changing code

### 3. Working Units

**TOSCA uses micrometers** for precise laser positioning:

```python
axis.setUnits(Units.mu)  # Always use micrometers
```

### 4. Speed Range

**Recommended range**: 50-500 µm/s
- 50 µm/s: Very slow, high precision
- 100 µm/s: Slow, default for TOSCA
- 500 µm/s: Fast positioning

```python
# GUI slider: 50-500 maps to µm/s
axis.setSpeed(slider_value)  # Direct mapping
```

### 5. Position Tolerance

**Default tolerance**: ±5 µm acceptable for TOSCA

```python
# Check position reached with tolerance
target = 100.0
current = axis.getEPOS()
error = abs(current - target)

if error <= 5.0:  # Within ±5 µm
    print("Position reached!")
```

### 6. Homing Strategy

**Auto-home on connect** vs **Manual homing**:

```python
# Option 1: Auto-home (original)
def connect(auto_home=True):
    controller.start()
    if auto_home:
        axis.findIndex()

# Option 2: Manual homing (current GUI)
def connect(auto_home=False):
    controller.start()
    # User clicks "Find Home" button later
```

---

## Reference Files

1. **Official Library**: `C:\Users\wille\Desktop\stage-control\Xeryon.py`
2. **Demo Script**: `C:\Users\wille\Desktop\stage-control\xeryon_demo.py`
3. **TOSCA HAL**: `C:\Users\wille\Desktop\TOSCA-dev\src\hardware\actuator_controller.py`
4. **TOSCA GUI**: `C:\Users\wille\Desktop\TOSCA-dev\src\ui\widgets\actuator_widget.py`

---

## Quick Reference Table

| Operation | API Call | Units | Notes |
|-----------|----------|-------|-------|
| **Connection** | `Xeryon("COM3", 9600)` | - | WARNING: TOSCA uses 9600 (NOT 115200) |
| **Add Axis** | `addAxis(Stage.XLA_1250_3N, "X")` | - | Use correct stage type |
| **Start** | `controller.start()` | - | Reads settings, enables axes |
| **Set Units** | `axis.setUnits(Units.mu)` | µm | TOSCA uses micrometers |
| **Home** | `axis.findIndex()` | - | Bidirectional search (fastest) |
| **Get Position** | `axis.getEPOS()` | Current units | Returns float |
| **Absolute Move** | `axis.setDPOS(100.0)` | Current units | Blocking by default |
| **Relative Move** | `axis.step(50.0)` | Current units | Positive or negative |
| **Set Speed** | `axis.setSpeed(100)` | units/s | 100 µm/s if units=Units.mu |
| **Check Homed** | `axis.isEncoderValid()` | - | Returns bool |
| **Check At Target** | `axis.isPositionReached()` | - | Returns bool |
| **Stop** | `controller.stop()` | - | Stops all axes, closes comm |

---

**End of Xeryon API Reference**
