# Calibration Procedures

**Document Version:** 1.0
**Last Updated:** 2025-10-26
**Status:** ⚠️ **NOT IMPLEMENTED** - Planning Only (Phase 6+)
**Priority:** CRITICAL - Required for treatment accuracy and FDA compliance

---

> **⚠️ WARNING - No Calibration Procedures Implemented:**
>
> **Current Status:** ALL calibration procedures documented here are **PLANNED ONLY**.
>
> **NO calibration workflows are implemented** in the current codebase:
> - ❌ Photodiode calibration - NOT implemented
> - ❌ Actuator calibration - NOT implemented
> - ❌ Camera pixel calibration - NOT implemented
> - ❌ Power verification - NOT implemented
> - ❌ Calibration database storage - NOT implemented
>
> **Current Operation:** System operates with factory defaults (no field calibration)
>
> **Implementation Target:** Phase 6 (before clinical testing)
>
> **This document serves as:**
> - Design specification for future calibration workflows
> - FDA submission documentation (planned procedures)
> - NIST traceability requirements documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Calibration Requirements](#calibration-requirements)
3. [Photodiode Calibration](#photodiode-calibration)
4. [Actuator Calibration](#actuator-calibration)
5. [Camera Calibration](#camera-calibration)
6. [Power Measurement Verification](#power-measurement-verification)
7. [Calibration Schedule](#calibration-schedule)
8. [Documentation & Audit Trail](#documentation--audit-trail)

---

## Overview

### Purpose

TOSCA requires regular calibration of all measurement systems to ensure treatment accuracy and patient safety. This document defines calibration procedures, schedules, and documentation requirements.

**Regulatory Context:**
- **FDA 21 CFR Part 820:** Quality System Regulation (Design Controls)
- **ISO 13485:** Medical devices — Quality management systems
- **IEC 60601-1:** Medical electrical equipment safety
- **ISO 10012:** Measurement management systems

### Calibration Objectives

1. **Accuracy:** Ensure all measurements are within specification
2. **Traceability:** Link calibration to NIST standards
3. **Safety:** Verify safety systems function correctly
4. **Compliance:** Meet FDA requirements for calibration
5. **Audit Trail:** Document all calibration activities

---

## Calibration Requirements

### Calibration Hierarchy

```
┌────────────────────────────────────────────────────────┐
│            NIST Traceable Standards                     │
│   (National Institute of Standards and Technology)      │
└────────────────────────────────────────────────────────┘
                         │
                Calibration Certificate
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│         Reference Equipment (Certified)                 │
│  - Laser power meter (certified annually)               │
│  - Micrometer (certified annually)                      │
│  - Oscilloscope (certified every 2 years)               │
└────────────────────────────────────────────────────────┘
                         │
            Used to calibrate TOSCA
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│              TOSCA Components                           │
│  - Photodiode (power measurement)                       │
│  - Actuator (position accuracy)                         │
│  - Camera (focus measurement)                           │
│  - GPIO timing (watchdog intervals)                     │
└────────────────────────────────────────────────────────┘
```

### Components Requiring Calibration

| Component | Parameter | Tolerance | Frequency | Method |
|-----------|-----------|-----------|-----------|--------|
| **Photodiode** | Power measurement | ±5% | Monthly | Certified power meter |
| **Actuator** | Position accuracy | ±10 µm | Quarterly | Micrometer + reference block |
| **Camera** | Pixel calibration | ±1 pixel | Annually | Calibration target |
| **Laser** | Output power | ±10% | Weekly | Photodiode feedback loop |
| **Watchdog** | Timeout interval | ±50 ms | Annually | Oscilloscope |

---

## Photodiode Calibration

### Purpose

Verify photodiode accurately measures laser power (0-10W range).

**Safety Critical:** YES - Incorrect power measurement could exceed safety limits

### Equipment Required

1. **Certified laser power meter** (Ophir or Thorlabs, NIST traceable)
2. **Laser controller** (Arroyo 1064nm laser)
3. **TOSCA system** (photodiode under test)

### Procedure

**Step 1: Setup**
```
1. Connect certified power meter to laser output
2. Connect TOSCA photodiode to secondary measurement port
3. Allow laser to warm up for 10 minutes
4. Zero both power meters with laser off
```

**Step 2: Calibration Points**

Test at 5 power levels across range:

| Target Power (W) | Certified Meter (W) | TOSCA Photodiode (V) | Acceptable Range |
|-----------------|---------------------|---------------------|------------------|
| 0.0 | 0.00 ± 0.01 | 0.00 ± 0.05 | -0.05 to +0.05 V |
| 2.5 | 2.50 ± 0.05 | TBD | ±5% of certified |
| 5.0 | 5.00 ± 0.05 | TBD | ±5% of certified |
| 7.5 | 7.50 ± 0.05 | TBD | ±5% of certified |
| 10.0 | 10.00 ± 0.10 | TBD | ±5% of certified |

**Step 3: Calibration Curve**

```python
# Calculate calibration curve (voltage → watts)
def calibrate_photodiode(calibration_points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate calibration curve from voltage/power pairs.

    Args:
        calibration_points: List of (voltage_v, power_w) tuples

    Returns:
        (slope, intercept) for power = slope * voltage + intercept
    """
    import numpy as np

    voltages = np.array([v for v, p in calibration_points])
    powers = np.array([p for v, p in calibration_points])

    # Linear regression
    slope, intercept = np.polyfit(voltages, powers, deg=1)

    return (slope, intercept)

# Example usage
cal_points = [
    (0.0, 0.0),    # 0V → 0W
    (0.5, 2.5),    # 0.5V → 2.5W
    (1.0, 5.0),    # 1.0V → 5.0W
    (1.5, 7.5),    # 1.5V → 7.5W
    (2.0, 10.0),   # 2.0V → 10.0W
]

slope, intercept = calibrate_photodiode(cal_points)
# slope ≈ 5.0 (W/V), intercept ≈ 0.0

# Save to config
config.photodiode_slope = slope
config.photodiode_intercept = intercept
```

**Step 4: Verification**

```python
# Verify calibration accuracy
def verify_calibration(slope, intercept, test_points):
    """Test calibration at intermediate points."""
    max_error = 0.0

    for voltage, expected_power in test_points:
        calculated_power = slope * voltage + intercept
        error = abs(calculated_power - expected_power) / expected_power

        if error > max_error:
            max_error = error

    return max_error

# Test at 3.75W (mid-point)
test_points = [(0.75, 3.75)]
max_error = verify_calibration(slope, intercept, test_points)

assert max_error < 0.05  # Must be within ±5%
```

**Step 5: Documentation**

```python
# Log calibration to database
calibration_record = {
    "component": "photodiode",
    "date": datetime.now().isoformat(),
    "technician_id": current_user.id,
    "reference_equipment": "Ophir Nova II P/N 12345 (Cert: NIST-2025-001)",
    "calibration_points": cal_points,
    "slope": slope,
    "intercept": intercept,
    "max_error_percent": max_error * 100,
    "pass_fail": "PASS" if max_error < 0.05 else "FAIL",
    "notes": "Annual photodiode calibration"
}

db.save_calibration_record(calibration_record)
```

**Acceptance Criteria:**
- ✅ All 5 points within ±5% of certified meter
- ✅ Linear fit R² > 0.99
- ✅ Verification point within ±5%

---

## Actuator Calibration

### Purpose

Verify actuator position accuracy (±10 µm tolerance).

**Safety Critical:** NO - Position errors do not directly harm patient

### Equipment Required

1. **Digital micrometer** (0-25mm, ±1 µm accuracy, NIST traceable)
2. **Gauge block** (10.000 mm ± 0.5 µm, calibrated)
3. **TOSCA actuator** (Xeryon linear stage)

### Procedure

**Step 1: Homing**
```python
# Home actuator to establish reference
actuator.home()
assert actuator.is_homed
```

**Step 2: Position Verification**

Test at 5 positions across range:

| Commanded Position (mm) | Micrometer Reading (mm) | Error (µm) | Acceptable? |
|------------------------|------------------------|-----------|-------------|
| 0.000 | 0.000 ± 0.001 | 0 | ✅ <10 µm |
| 5.000 | 5.002 ± 0.001 | +2 | ✅ <10 µm |
| 10.000 | 10.001 ± 0.001 | +1 | ✅ <10 µm |
| 15.000 | 14.998 ± 0.001 | -2 | ✅ <10 µm |
| 20.000 | 20.003 ± 0.001 | +3 | ✅ <10 µm |

**Step 3: Calibration Adjustment**

```python
# If systematic error detected, apply offset
def adjust_actuator_offset(measured_errors: List[float]) -> float:
    """Calculate position offset from calibration errors."""
    mean_error = np.mean(measured_errors)  # Average error in µm

    if abs(mean_error) > 5.0:  # If >5 µm average error
        return -mean_error  # Correction offset
    else:
        return 0.0  # No correction needed

# Example
errors = [0, +2, +1, -2, +3]  # µm
offset = adjust_actuator_offset(errors)  # offset = -0.8 µm

config.actuator_position_offset_um = offset
```

**Acceptance Criteria:**
- ✅ All positions within ±10 µm
- ✅ No systematic drift (error should average ~0)

---

## Camera Calibration

### Purpose

Verify pixel-to-micron calibration for ring detection.

**Safety Critical:** NO - Measurement only, not treatment control

### Equipment Required

1. **Calibration target** (1951 USAF resolution chart or grid)
2. **Known dimensions** (e.g., 1.00 mm grid spacing)
3. **TOSCA camera** (Allied Vision)

### Procedure

**Step 1: Image Calibration Target**
```python
# Capture image of calibration target
frame = camera.capture_frame()
```

**Step 2: Measure Pixel Spacing**
```python
# Detect grid lines in image
grid_spacing_pixels = detect_grid_spacing(frame)  # e.g., 100 pixels

# Known physical spacing
grid_spacing_mm = 1.00  # 1 mm grid

# Calculate microns per pixel
um_per_pixel = (grid_spacing_mm * 1000) / grid_spacing_pixels
# Example: 1000 µm / 100 pixels = 10 µm/pixel

config.camera_um_per_pixel = um_per_pixel
```

**Acceptance Criteria:**
- ✅ Calculated µm/pixel within ±1% of expected
- ✅ Distortion <2% across image

---

## Power Measurement Verification

### Purpose

Verify laser power measurement accuracy during treatment.

**Safety Critical:** YES - Power limits enforced by this measurement

### Procedure (Weekly)

```python
# Quick verification using internal photodiode
def weekly_power_check():
    """Weekly verification of power measurement."""

    # Set laser to 5.0W
    laser.set_power(5.0)
    time.sleep(1.0)  # Allow stabilization

    # Read photodiode
    measured_power = photodiode.get_power()

    # Verify within ±10%
    error = abs(measured_power - 5.0) / 5.0

    if error > 0.10:
        logger.error(f"Power measurement out of spec: {error*100:.1f}%")
        return False

    logger.info(f"Power check passed: {measured_power:.2f}W")
    return True
```

**Acceptance Criteria:**
- ✅ Measured power within ±10% of commanded

---

## Calibration Schedule

### Routine Calibration

| Component | Frequency | Duration | Technician Required |
|-----------|-----------|----------|---------------------|
| **Photodiode** | Monthly | 1 hour | Qualified technician |
| **Actuator** | Quarterly | 30 min | Qualified technician |
| **Camera** | Annually | 1 hour | Qualified technician |
| **Power Check** | Weekly | 5 min | Operator |
| **Watchdog** | Annually | 30 min | Qualified technician |

### Calibration Records

**Required Documentation:**
1. Calibration date and time
2. Technician name and ID
3. Reference equipment used (with certification numbers)
4. Calibration data (measurements, calculations)
5. Pass/Fail status
6. Next calibration due date

**Database Schema:**
```sql
CREATE TABLE calibration_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL,
    calibration_date TEXT NOT NULL,
    technician_id INTEGER NOT NULL,
    reference_equipment TEXT NOT NULL,
    calibration_data TEXT,  -- JSON
    pass_fail TEXT NOT NULL,
    next_due_date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (technician_id) REFERENCES technicians(id)
);
```

---

## Documentation & Audit Trail

### FDA Requirements

**21 CFR Part 820.72 - Inspection, Measuring, and Test Equipment:**

> Each manufacturer shall ensure that all inspection, measuring, and test equipment... is routinely calibrated, inspected, checked, and maintained.

**TOSCA Compliance:**
- ✅ Written calibration procedures (this document)
- ✅ Calibration schedule defined
- ✅ NIST traceable standards
- ✅ Documented calibration records
- ✅ Out-of-calibration handling procedures

### Calibration Certificate Example

```
═══════════════════════════════════════════════════════
           TOSCA CALIBRATION CERTIFICATE
═══════════════════════════════════════════════════════

Component:        Photodiode Power Measurement
Serial Number:    TOSCA-PD-001
Calibration Date: 2025-10-26
Technician:       John Smith (Tech ID: 005)

Reference Equipment:
  - Ophir Nova II Power Meter (S/N 12345)
  - NIST Calibration Certificate: NIST-2025-001
  - Expiration: 2026-10-15

Calibration Results:
  - Test Points: 5 (0W, 2.5W, 5W, 7.5W, 10W)
  - Maximum Error: 3.2% at 7.5W
  - Calibration Curve: P = 5.02V + 0.01
  - R²: 0.9997

Status: PASS (all points within ±5%)

Next Calibration Due: 2025-11-26

Signature: _______________________  Date: __________
═══════════════════════════════════════════════════════
```

---

## References

### Standards

- **ISO 10012:** Measurement management systems
- **ISO 13485:** Medical devices — Quality management
- **FDA 21 CFR Part 820:** Quality System Regulation
- **NIST Handbook 150:** NVLAP Procedures and General Requirements

---

**Document Owner:** Quality Assurance Manager
**Last Updated:** 2025-10-26
**Next Review:** Before Phase 6 (calibration implementation)
**Status:** Planning - Procedures defined, implementation pending
