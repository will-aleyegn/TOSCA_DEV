# Architecture Documentation Fixes - Implementation Plan

**Created:** 2025-10-26
**Status:** IN PROGRESS
**Related:** presubmit/reviews/ARCHITECTURE_REVIEW_2025-10-26.md

---

## User Confirmation

✅ **CONFIRMED:** For e-stop shutdown, **laser only** is correct (selective shutdown policy)

This confirms `SAFETY_SHUTDOWN_POLICY.md` is canonical and `03_safety_system.md` needs updating.

---

## Quick Wins (Do First - 30 Minutes)

### 1. Fix File Naming Collision ✅
**Task:** Rename `06_safety_watchdog.md` → `07_safety_watchdog.md`
**Effort:** 5 minutes
**Commands:**
```bash
git mv docs/architecture/06_safety_watchdog.md docs/architecture/07_safety_watchdog.md
```

### 2. Add Deprecation Warning ✅
**Task:** Mark old protocol doc as deprecated
**Effort:** 10 minutes
**File:** `docs/architecture/04_treatment_protocols.md`
**Add at top:**
```markdown
> ⚠️ **DEPRECATED DOCUMENT**
>
> This document describes an older step-based protocol model that has been superseded.
>
> **Current Design:** See `06_protocol_builder.md` for the action-based protocol engine (current implementation).
>
> **Status:** Kept for historical reference only. Do not implement new features based on this document.
>
> **Last Updated:** 2025-10-26 (marked as deprecated)

---
```

### 3. Update Status Field ✅
**Task:** Fix outdated status in system overview
**Effort:** 5 minutes
**File:** `docs/architecture/01_system_overview.md`
**Changes:**
- Line 4: `**Date:** 2025-10-15` → `**Date:** 2025-10-26`
- Line 5: `**Status:** Planning Phase` → `**Status:** Phase 5 - Testing & Quality Assurance`
- Line 601: Update "Last Updated"

### 4. Add Policy Cross-Reference ✅
**Task:** Link to canonical shutdown policy
**Effort:** 10 minutes
**File:** `docs/architecture/03_safety_system.md`
**Add after line 323:**
```markdown

**IMPORTANT:** This implementation follows the **Selective Shutdown Policy**.

See `SAFETY_SHUTDOWN_POLICY.md` for the complete canonical policy:
- Treatment laser: DISABLED immediately
- Camera: MAINTAINED (for visual assessment)
- Actuator: MAINTAINED (for safe repositioning)
- Aiming laser: MAINTAINED (Class 2, low power)
- GPIO monitoring: MAINTAINED (for diagnostics)

Only the treatment laser is shut down on safety fault.
```

---

## P0: Critical Fixes (Before Phase 6)

### Fix 1: Harmonize Shutdown Policy Documentation
**Effort:** 2 hours
**Priority:** CRITICAL

#### Part A: Update emergency_stop code in 03_safety_system.md

**Location:** Lines 296-339

**Current Code (WRONG):**
```python
def _emergency_shutdown(self, reason: str):
    """Immediate hardware shutdown"""
    try:
        # 1. Laser OFF (highest priority)
        self.hardware.laser.emergency_stop()
        self.hardware.laser.set_power(0)

        # 2. Stop actuator motion
        self.hardware.actuator.stop()  # ← WRONG - violates selective shutdown
```

**New Code (CORRECT):**
```python
def _emergency_shutdown(self, reason: str):
    """
    Selective emergency shutdown - TREATMENT LASER ONLY.

    Per SAFETY_SHUTDOWN_POLICY.md:
    - Treatment laser: DISABLED
    - Camera: MAINTAINED (for assessment)
    - Actuator: MAINTAINED (for repositioning)
    - Aiming laser: MAINTAINED (Class 2 safe)
    - GPIO monitoring: MAINTAINED (for diagnostics)
    """
    try:
        # 1. IMMEDIATE: Disable treatment laser only
        self.hardware.laser.emergency_stop()
        self.hardware.laser.set_power(0)
        logger.info("Treatment laser disabled (selective shutdown)")

        # 2. MAINTAIN: Other systems remain operational
        # - Camera continues streaming (for visual assessment)
        # - Actuator remains controllable (for safe repositioning)
        # - Aiming laser stays available (Class 2, inherently safe)
        # - GPIO monitoring continues (for diagnostics)
        # - Event logging active
```

#### Part B: Update SafetyManager.disable_laser method

**Location:** Lines 585-592

Add clarification that this is selective:
```python
def disable_laser(self, reason: str = "Normal"):
    """
    Disable treatment laser only (selective shutdown).

    Other systems (camera, actuator, GPIO) remain operational.
    """
    self.hardware.laser.set_power(0)
    self.laser_enabled = False
    self.system_state = SystemState.READY

    log_safety_event('laser_disabled', 'info',
                     f"Treatment laser disabled (selective): {reason}")
```

#### Part C: Update FaultHandler documentation

**Location:** Lines 748-820

Update recovery procedures to clarify selective shutdown.

### Fix 2: Update Protocol Engine References
**Effort:** 1 hour

**File:** `docs/architecture/01_system_overview.md`

**Location:** Lines 302-348 (Treatment Protocol Engine section)

**Current:** References step-based model

**Update to:** Reference action-based model from `06_protocol_builder.md`

### Fix 3: Verify Implementation Matches Policy
**Effort:** 1 hour

Check actual implementation:
1. Read `src/core/safety.py` (if exists)
2. Verify emergency_stop only disables laser
3. Verify camera/actuator remain operational
4. Document any discrepancies

---

## P1: High Priority Fixes (Before Next Phase)

### Fix 1: Update Hardware References
**Effort:** 2 hours

#### Files to Update:

**A. docs/architecture/01_system_overview.md**

Lines 42-45:
```python
# Hardware Interfaces
pyserial               # Arroyo laser serial communication
# pyfirmata            # REMOVED - was for FT232H (obsolete)
# Custom Arduino Nano firmware with serial protocol (COM4)
# Xeryon library       # Linear actuator control (existing)
# VmbPy SDK            # Allied Vision camera interface (existing)
```

Lines 128-143:
```markdown
### 4. GPIO Controller - Safety Interlocks and Monitoring (Arduino Nano)
- **Device:** Arduino Nano (ATmega328P) on COM4
- **Migration Note:** Replaced FT232H in October 2025
- **Firmware:** Custom watchdog firmware with serial protocol
- **Communication:** USB serial (115200 baud)
```

**B. docs/architecture/03_safety_system.md**

Lines 48-55:
```markdown
**Connection:**
- Arduino Nano on COM4 (replaced FT232H October 2025)
- Custom firmware monitors footpedal via serial protocol
- Hardware debouncing in firmware
```

### Fix 2: Document Encryption Strategy
**Effort:** 2 hours

Create section in `03_safety_system.md` or new file `08_security_architecture.md`

### Fix 3: Create Test Architecture Doc
**Effort:** 2 hours

Create `docs/architecture/08_test_architecture.md` documenting:
- MockHardwareController pattern
- Actual test structure
- Test coverage approach

### Fix 4: Update Last Modified Dates
**Effort:** 1 hour

Update all architecture docs to 2025-10-26

---

## P2: Quality Improvements (Before Production)

### Create Missing Documentation

1. `09_event_logging.md` - Event logging architecture
2. `10_recording_manager.md` - Recording system design
3. `11_calibration_procedures.md` - Calibration workflow
4. `08_concurrency_model.md` - Threading model (from P1)

---

## Implementation Order

### Session 1: Quick Wins (NOW - 30 min)
1. ✅ Fix file naming
2. ✅ Add deprecation warning
3. ✅ Update status field
4. ✅ Add policy cross-reference

### Session 2: Shutdown Policy Fix (1-2 hours)
1. ✅ Update emergency_stop code
2. ✅ Update SafetyManager methods
3. ✅ Update fault handler docs
4. ✅ Verify implementation

### Session 3: Protocol Engine Updates (1 hour)
1. ✅ Update system overview
2. ✅ Add cross-references

### Session 4: Hardware Documentation (2 hours)
1. ✅ Update all FT232H references
2. ✅ Add migration notes
3. ✅ Update pin references

### Session 5: Quality Docs (varies)
1. ✅ Create concurrency model doc
2. ✅ Create test architecture doc
3. ✅ Document encryption strategy

---

## Verification Checklist

After all fixes:

- [ ] `03_safety_system.md` shows selective shutdown (laser only)
- [ ] `SAFETY_SHUTDOWN_POLICY.md` is referenced as canonical
- [ ] No file naming collisions
- [ ] Deprecation warnings are clear
- [ ] Status fields show Phase 5
- [ ] All hardware references are Arduino Nano COM4
- [ ] Last updated dates are 2025-10-26
- [ ] Cross-references work correctly
- [ ] Implementation code matches documented policy

---

## Git Commit Strategy

**Quick Wins:**
```
docs: Fix critical architecture documentation issues

- Rename 07_safety_watchdog.md (fix naming collision)
- Mark 04_treatment_protocols.md as deprecated
- Update 01_system_overview.md status to Phase 5
- Add cross-reference to SAFETY_SHUTDOWN_POLICY.md

Addresses P0 quick wins from architecture review 2025-10-26
```

**Shutdown Policy:**
```
docs: Harmonize shutdown policy to selective shutdown (laser only)

- Update 03_safety_system.md emergency_stop to match SAFETY_SHUTDOWN_POLICY.md
- Clarify that only treatment laser is disabled on fault
- Camera, actuator, GPIO monitoring remain operational
- Add policy references throughout safety documentation

CONFIRMED: Selective shutdown (laser only) is correct behavior
Closes critical finding #1 from architecture review 2025-10-26
```

**Hardware Updates:**
```
docs: Update hardware references from FT232H to Arduino Nano COM4

- Update all references to reflect Arduino Nano migration
- Remove pyfirmata references (obsolete)
- Add migration notes and timeline
- Update GPIO pin descriptions

Closes finding #2 from architecture review 2025-10-26
```

---

**Status:** Ready to implement
**Next Action:** Start with Quick Wins
**Estimated Total Time:** 8-10 hours for P0 + P1
