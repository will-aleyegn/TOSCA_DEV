# Actuator Test Scripts

This directory contains test and diagnostic scripts for the Xeryon XLA-5-125-10MU linear actuator.

---

## Test Scripts

### `test_actuator_connection.py`
**Purpose:** Quick connection test
**Usage:** `python test_actuator_connection.py`
**Tests:**
- COM port connectivity
- Controller initialization
- Auto-homing procedure
- Status reporting

**Expected Output:**
```
Connection successful!
Status: ready
homed: True
encoder_valid: True
```

---

### `test_actuator_hal.py`
**Purpose:** Interactive full movement test
**Usage:** `python test_actuator_hal.py`
**Tests:**
- Connection and homing
- Absolute positioning (50 µm)
- Relative movement (+25 µm)
- Status monitoring

**Safety:** Uses very slow speed (100) and short movements (<100 µm total)

---

## Diagnostic Tools

### `debug_homing.py`
**Purpose:** Real-time STAT register monitoring during homing
**Usage:** `python debug_homing.py`
**Features:**
- Displays STAT register values and bit states
- Monitors thermal protection flags
- Tracks encoder status changes
- 10-second monitoring window after INDX command

**Use When:** Debugging homing failures, investigating hardware state

---

### `test_no_reset.py`
**Purpose:** Test initialization without reset() call
**Usage:** `python test_no_reset.py`
**Features:**
- Bypasses normal start() procedure
- Manually controls initialization sequence
- Monitors thermal protection trigger points
- Tests homing without reset

**Use When:** Isolating initialization issues, testing thermal error triggers

---

### `test_thermal_clearing.py`
**Purpose:** Test different thermal protection clearing strategies
**Usage:** `python test_thermal_clearing.py`
**Tests:**
- Wait for auto-clear
- Multiple ENBL=1 commands
- RSET then ENBL sequence
- Movement with thermal errors present

**Use When:** Debugging persistent thermal protection errors

---

### `test_minimal_settings.py`
**Purpose:** Identify which setting triggers thermal protection
**Usage:** `python test_minimal_settings.py`
**Tests:** Sends settings one-by-one:
- XLA3=1250 (stage type)
- FREQ, FRQ2 (frequencies)
- AMPL, MAMP, MIMP (amplitudes)
- PROP, PRO2, INTF (control factors)
- ENCO (encoder offset)

**Use When:** Investigating which settings are incompatible with hardware

---

## Hardware Configuration

**Device:** Xeryon XLA-5-125-10MU
**Connection:** COM3, 9600 baud
**Stage Type:** XLA_1250_5N (5 Newton motor)
**Encoder Resolution:** 1250 nm (1.25 µm)

---

## Critical Configuration

**File:** `components/actuator_module/Xeryon.py`

**Required Settings:**
```python
DISABLE_WAITING = False          # Blocking mode for reliable homing
AUTO_SEND_SETTINGS = False       # Use device's stored settings (CRITICAL!)
AUTO_SEND_ENBL = True            # Auto-clear thermal errors
```

**Why AUTO_SEND_SETTINGS = False?**
The device has correct settings stored internally (configured via Windows Interface). Overwriting these with file-based settings triggers thermal protection errors.

---

## Common Issues

### Issue: "Index is not found, but stopped searching for index"
**Cause:** Thermal protection preventing motor movement
**Solution:** Verify AUTO_SEND_SETTINGS = False
**Diagnostic:** Run `debug_homing.py` to monitor STAT register

### Issue: Persistent thermal protection errors
**Cause:** Incompatible settings being sent to hardware
**Solution:** Use device's stored settings (AUTO_SEND_SETTINGS = False)
**Diagnostic:** Run `test_minimal_settings.py` to identify culprit

### Issue: Homing takes too long or times out
**Cause:** DISABLE_WAITING = True prevents proper status monitoring
**Solution:** Set DISABLE_WAITING = False
**Diagnostic:** Check timing with `debug_homing.py`

---

## Test Results Archive

**Latest Test:** 2025-10-23
**Result:** ✅ PASSING

```
Index of axis X found.
Auto-homing complete - actuator ready
homed: True
encoder_valid: True
position_um: 1.25
status: ready
```

**Configuration:**
- AUTO_SEND_SETTINGS = False (CRITICAL FIX)
- DISABLE_WAITING = False
- AUTO_SEND_ENBL = True
- Stage: XLA_1250_5N

---

## Documentation

For comprehensive troubleshooting guide, see:
`docs/actuator-control/ACTUATOR_HAL_CRITICAL_FIX.md`

For development progress and decisions, see:
`docs/project/WORK_LOG.md`
