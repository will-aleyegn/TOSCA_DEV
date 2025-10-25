# Actuator HAL Critical Fix - AUTO_SEND_SETTINGS

**Date:** 2025-10-23
**Status:** ✅ RESOLVED - Homing now working perfectly
**Hardware:** Xeryon XLA-5-125-10MU linear actuator

---

## 🎯 The Problem

The actuator homing (index finding) procedure was failing with:
- Persistent thermal protection errors (STAT bits 2 & 3)
- Motor unable to move despite ENBL=1 commands
- Index search starting but aborting after 100ms
- Error: "Index is not found, but stopped searching for index"

## 🔑 The Critical Fix

**File:** `components/actuator_module/Xeryon.py`
**Line:** 36
**Change:** `AUTO_SEND_SETTINGS = False` (was `True`)

```python
# BEFORE (BROKEN):
AUTO_SEND_SETTINGS = True  # Overwrites device settings with settings_user.txt

# AFTER (WORKING):
AUTO_SEND_SETTINGS = False  # Use device's stored settings
```

## 💡 Why This Works

### Root Cause
The device already has **correct, working settings** stored in its internal memory, configured via Windows Interface. When `AUTO_SEND_SETTINGS = True`, the Python library:

1. Reads settings from `settings_user.txt`
2. Sends ALL these settings to the hardware during `start()`
3. One or more of these settings are **incompatible** with this specific hardware
4. Hardware triggers thermal protection as a safety mechanism
5. Motor cannot move while thermal protection is active
6. Homing fails because motor can't search for index

### The Solution
By setting `AUTO_SEND_SETTINGS = False`:
- Library skips sending settings from files
- Device uses its internal stored settings (from Windows Interface)
- These settings are known-good and hardware-compatible
- No thermal protection errors triggered
- Motor can move freely
- Homing succeeds

## 📊 Evidence

### Before Fix (FAILING)
```
5. Checking status BEFORE reset:
   STAT: 17
   Thermal1: False
   Thermal2: False

6. Sending settings (without reset)...

8. Checking status AFTER settings (no reset):
   STAT: 29              ← Thermal errors!
   Thermal1: True        ← Triggered by sendSettings()
   Thermal2: True

11. Attempting to find index...
    [0.0s] STAT=1117, searching=False  ← Motor can't move
```

### After Fix (WORKING)
```
Attempting connection on COM3...
Connected to actuator on COM3
Auto-homing actuator (blocking until complete)...
Starting index search (direction=0, bidirectional)...
Searching index for axis X.
Index of axis X found.              ← SUCCESS!
Auto-homing complete - actuator ready

Status:
  connected: True
  homed: True                        ← HOMED!
  position_um: 1.25
  encoder_valid: True                ← ENCODER VALID!
  status: ready
```

**Zero thermal errors! Perfect operation!**

## 🔧 Additional Fixes Applied

While debugging, several other improvements were made:

### 1. Stage Type (src/hardware/actuator_controller.py:120)
```python
# Changed to match 5 Newton motor specification
self.axis = self.controller.addAxis(Stage.XLA_1250_5N, "X")
```

### 2. findIndex() Grace Period (Xeryon.py:388)
```python
# Added 500ms delay for STAT register to update
time.sleep(0.5)  # Grace period for command processing
```

### 3. DISABLE_WAITING (Xeryon.py:29)
```python
# Set to False for reliable blocking during homing
DISABLE_WAITING = False  # Keep False for reliable homing operation
```

### 4. Removed Redundant Commands (actuator_controller.py:134-141)
```python
# Removed manual SSPD, LLIM, HLIM commands
# These were overriding device settings unnecessarily
```

## 📖 Lessons Learned

### 1. **Trust Device Settings**
When hardware has working settings configured via manufacturer software (Windows Interface), those settings are authoritative. Don't override them with file-based configurations.

### 2. **Hardware Protection Mechanisms**
Thermal protection can trigger for reasons other than actual overheating:
- Incompatible frequency settings
- Wrong amplitude values for motor type
- Incorrect control factors
- Hardware safety checks failing

### 3. **Systematic Debugging**
The fix was found by:
1. Monitoring STAT register in real-time (debug_homing.py)
2. Isolating initialization steps (test_no_reset.py)
3. Testing minimal configurations
4. Identifying exact trigger (sendSettings())

### 4. **STAT Register Timing**
Hardware status updates aren't instantaneous:
- Serial communication at 9600 baud: ~10ms per command
- Hardware processing: ~40ms
- STAT polling interval (POLI): 97ms
- **Minimum update latency: ~150ms**

## ✅ Verification

To verify the fix works on your system:

```bash
# Quick connection test
python test_actuator_connection.py

# Full movement test
python test_actuator_hal.py
```

Expected output:
```
Searching index for axis X.
Index of axis X found.
Auto-homing complete - actuator ready
Status: ready
```

## 🚀 Next Steps

With homing now working, the next development tasks are:

1. **Position Control**
   - Absolute positioning (`set_position()`)
   - Relative movement (`make_step()`)
   - Position validation and limits

2. **Speed Control**
   - Variable speed settings
   - Acceleration/deceleration
   - Movement profiling

3. **Integration**
   - Connect to GUI controls
   - Session-based position tracking
   - Safety interlocks

## 📝 Configuration Reference

### Working Configuration (Xeryon.py)
```python
DISABLE_WAITING = False          # Blocking mode for homing
AUTO_SEND_SETTINGS = False       # Use device settings (CRITICAL!)
AUTO_SEND_ENBL = True            # Auto-clear thermal errors
OUTPUT_TO_CONSOLE = True         # Show debug messages
```

### Device Settings (stored internally)
- Configured via: Windows Interface (Xeryon_Dialog_v4_2_59.exe)
- Baudrate: 9600
- Stage type: XLA3=1250 (5N motor)
- Motor parameters: Optimized for XLA-5-125-10MU
- Frequency, amplitude, control factors: Hardware-specific

## 📄 Related Files

- `src/hardware/actuator_controller.py` - Main HAL implementation
- `components/actuator_module/Xeryon.py` - Library configuration
- `test_actuator_connection.py` - Connection test
- `test_actuator_hal.py` - Full movement test
- `debug_homing.py` - STAT register diagnostic tool

---

**Document Status:** Complete
**Hardware Status:** ✅ OPERATIONAL
**Homing Status:** ✅ PASSING
**Next Milestone:** Position control implementation
