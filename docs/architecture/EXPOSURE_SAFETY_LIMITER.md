# Exposure Safety Limiter - Implementation Guide

**Date:** 2025-10-30
**Version:** 0.9.9-alpha (pending)
**Feature:** Prevent accidental frame drops from long exposure times

---

## Overview

The exposure safety limiter prevents users from accidentally setting exposure times longer than the camera frame period, which would cause frame drops and unexpected behavior during live viewing.

**Key Safety Principle:** Medical device software should prevent misconfiguration that could cause operator confusion during treatment procedures.

---

## Problem Statement

### Before: Unprotected Exposure Control ⚠️

**Issue:** Users could set any exposure time up to camera maximum (often 10+ seconds)
- Long exposures (>33ms at 30 FPS) cause frame drops
- Live view becomes choppy and unresponsive
- Operator confusion during critical treatment procedures
- No warning or feedback about frame rate impact

**Example:**
```
User sets exposure to 100ms
Expected: Smooth 30 FPS live view
Actual: 10 FPS with severe stuttering (frame drops)
Operator: "Is the camera broken?"
```

### After: Protected Exposure Control ✅

**Solution:** Exposure limiter with explicit override
- **Default:** Exposure limited to 33ms (safe for 30 FPS)
- **Override:** Checkbox must be checked for longer exposures
- **Warning:** Clear feedback about frame rate impact
- **Informational:** Expected FPS shown when long exposure enabled

---

## Implementation Details

### 1. Safety Checkpoint in Exposure Change Handler

**Location:** `camera_widget.py:605-632`

```python
def _on_exposure_changed(self, value: int) -> None:
    """Handle exposure slider change with safety check."""

    # Safety check: prevent long exposures without permission
    if not self._is_exposure_safe(value):
        # Revert to safe value (33ms at 30 FPS)
        safe_value = 33000  # microseconds
        self.exposure_slider.blockSignals(True)
        self.exposure_slider.setValue(safe_value)
        self.exposure_slider.blockSignals(False)

        # Show warning
        self.exposure_warning_label.setText(
            "⚠️ Exposure limited to 33ms (30 FPS). "
            "Enable 'Allow Long Exposure' for longer times."
        )
        return  # Block the change

    # Safe - send to camera
    self.camera_controller.set_exposure(float(value))
```

### 2. Safety Check Logic

**Location:** `camera_widget.py:964-981`

```python
def _is_exposure_safe(self, exposure_us: int) -> bool:
    """Check if exposure is safe for 30 FPS."""
    # Frame period at 30 FPS = 33.33ms = 33,333 microseconds
    max_safe_exposure_us = 33000  # Slightly under for margin

    # Allow if:
    # 1. Under safe limit (< 33ms), OR
    # 2. Long exposure mode explicitly enabled
    return (exposure_us <= max_safe_exposure_us or
            self.allow_long_exposure_check.isChecked())
```

### 3. Warning Label Update

**Location:** `camera_widget.py:983-1013`

**Three states:**

1. **Safe exposure (<33ms):** No warning
   ```
   [No message displayed]
   ```

2. **Unsafe attempt (user didn't check box):** Red warning
   ```
   ⚠️ Exposure 50.0ms > 33ms frame period.
   Enable 'Allow Long Exposure' or reduce exposure.
   ```

3. **Long exposure enabled (intentional):** Orange info
   ```
   ℹ️ Long exposure active (100.0ms).
   Expect ~10.0 FPS (frame drops normal).
   ```

### 4. UI Components

**New checkbox:** `camera_widget.py:280-290`
```python
self.allow_long_exposure_check = QCheckBox(
    "Allow Long Exposure (>33ms, may drop frames)"
)
self.allow_long_exposure_check.setToolTip(
    "Enable to set exposure times longer than frame period.\n"
    "Warning: Exposures >33ms at 30 FPS will cause frame drops.\n"
    "Only use for still imaging, not live viewing."
)
self.allow_long_exposure_check.setStyleSheet(
    "color: #ff8800; font-weight: bold;"
)
```

**Warning label:** `camera_widget.py:312-316`
```python
self.exposure_warning_label = QLabel("")
self.exposure_warning_label.setStyleSheet(
    "color: #ff5555; font-weight: bold; font-size: 10px;"
)
self.exposure_warning_label.setWordWrap(True)
```

### 5. Updated Exposure Range

**Previous range:** 100 µs - 100,000 µs (0.1ms - 100ms)
**New range:** 100 µs - 1,000,000 µs (0.1ms - 1 second)

**Rationale:**
- User-friendly maximum (1 second is intuitive)
- Useful for still image capture in low light
- Protected by safety limiter (requires checkbox for >33ms)

---

## User Experience Flow

### Scenario 1: Safe Exposure (Normal Operation)

```
1. User starts streaming
2. User moves exposure slider to 20ms
   → Slider moves freely
   → No warning displayed
   → Live view remains smooth at 30 FPS ✅
```

### Scenario 2: Attempted Long Exposure (Protected)

```
1. User starts streaming
2. User moves exposure slider to 50ms
   → Slider snaps back to 33ms (automatic)
   → Warning appears: "⚠️ Exposure limited to 33ms..."
   → Console log: "Exposure change blocked: 50000µs exceeds frame period"
   → User sees checkbox is unchecked ❌
```

### Scenario 3: Intentional Long Exposure (Override)

```
1. User starts streaming
2. User checks "Allow Long Exposure" checkbox
3. User moves exposure slider to 100ms
   → Slider moves to 100ms ✅
   → Info appears: "ℹ️ Long exposure active (100.0ms). Expect ~10.0 FPS"
   → Live view drops to ~10 FPS (expected behavior)
   → User understands this is intentional
```

### Scenario 4: Auto Exposure (Bypasses Limiter)

```
1. User starts streaming
2. User checks "Auto Exposure"
   → Manual controls disabled (including "Allow Long Exposure")
   → Warning label cleared
   → Camera manages exposure automatically
   → No user intervention possible ✅
```

---

## Safety Calculations

### Frame Period Calculation

**Frame rate → Frame period:**
```
30 FPS → 1000ms / 30 = 33.33ms per frame
25 FPS → 1000ms / 25 = 40.00ms per frame
60 FPS → 1000ms / 60 = 16.67ms per frame
```

**Safe exposure threshold:**
```python
# At 30 FPS, frame period = 33.33ms
# Safety margin: Set limit slightly under to account for processing
max_safe_exposure_us = 33000  # 33.0ms (0.33ms margin)
```

### Expected FPS Calculation

**Long exposure → Expected FPS:**
```python
fps_estimate = 1000.0 / exposure_ms

Examples:
- 50ms exposure → ~20 FPS
- 100ms exposure → ~10 FPS
- 200ms exposure → ~5 FPS
- 1000ms (1 sec) → ~1 FPS
```

---

## Testing Instructions

### Test 1: Safe Exposure Range ✅

**Objective:** Verify normal operation within safe range

**Steps:**
1. Start camera streaming
2. Move exposure slider from 1ms to 33ms
3. Observe slider moves freely
4. Check FPS counter

**Expected:**
- ✅ Slider moves without restriction
- ✅ No warnings displayed
- ✅ FPS remains at 30.0 (±0.5)
- ✅ Live view smooth and responsive

### Test 2: Exposure Limiter (Protection) 🛡️

**Objective:** Verify limiter blocks unsafe exposures

**Steps:**
1. Start camera streaming
2. Ensure "Allow Long Exposure" checkbox is **UNCHECKED**
3. Try to move slider to 50ms
4. Observe slider behavior

**Expected:**
- ✅ Slider **snaps back** to 33ms (automatic clamp)
- ✅ Warning appears: "⚠️ Exposure limited to 33ms..."
- ✅ Console log: "Exposure change blocked: 50000µs exceeds frame period"
- ✅ FPS remains at 30.0
- ✅ User cannot set long exposure

### Test 3: Override with Checkbox ⚙️

**Objective:** Verify intentional long exposure works

**Steps:**
1. Start camera streaming
2. Check "Allow Long Exposure" checkbox
3. Move slider to 100ms
4. Observe FPS and warning

**Expected:**
- ✅ Slider moves to 100ms (no snap-back)
- ✅ Info message: "ℹ️ Long exposure active (100.0ms). Expect ~10.0 FPS"
- ✅ FPS drops to ~10.0 (expected)
- ✅ Warning is **orange** (informational), not red (error)
- ✅ Live view choppy but functional

### Test 4: Checkbox Toggle Behavior 🔄

**Objective:** Verify checkbox state handling

**Steps:**
1. Set exposure to 100ms (with checkbox enabled)
2. Uncheck "Allow Long Exposure" checkbox
3. Observe behavior

**Expected:**
- ✅ Warning changes to: "⚠️ Exposure 100.0ms > 33ms frame period..."
- ✅ User sees they need to either:
  - Re-check checkbox, OR
  - Manually reduce exposure to <33ms
- ✅ Current exposure preserved (not auto-clamped)
- ✅ Future changes will be blocked until checkbox re-enabled

### Test 5: Auto Exposure Interaction 🤖

**Objective:** Verify auto mode bypasses limiter

**Steps:**
1. Set manual exposure to 20ms (safe)
2. Enable "Auto Exposure" checkbox
3. Observe UI state

**Expected:**
- ✅ Exposure slider **disabled**
- ✅ "Allow Long Exposure" checkbox **disabled**
- ✅ Warning label **cleared**
- ✅ Camera adjusts exposure automatically
- ✅ No user intervention possible (correct behavior)

**Disable auto exposure:**
- ✅ Controls re-enabled
- ✅ Safety check runs on current exposure
- ✅ Warning appears if exposure > 33ms

### Test 6: Edge Cases 🔬

**Test 6a: Boundary value (33ms exact)**
```
Set exposure to exactly 33000 µs
Expected: Passes safety check (≤ threshold)
```

**Test 6b: Boundary value (33.001ms)**
```
Set exposure to 33001 µs
Expected: Blocked (> threshold)
```

**Test 6c: Very long exposure (1 second)**
```
Enable checkbox → Set to 1,000,000 µs
Expected: Info shows "~1.0 FPS"
```

**Test 6d: Minimum exposure (0.1ms)**
```
Set to 100 µs
Expected: Works, ~10,000 FPS theoretical (limited by camera hardware)
```

---

## UI Layout

```
┌────────────────────────────────────────────────────────┐
│ Camera Settings                                         │
├────────────────────────────────────────────────────────┤
│ Exposure (µs):                    [✓] Auto            │
│ [✓] Allow Long Exposure (>33ms, may drop frames)      │  ← NEW CHECKBOX
│ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬●▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬          │  ← Slider (0.1ms - 1s)
│ 10000 µs (10.0 ms)              [Enter µs_____]       │
│ ⚠️ Exposure limited to 33ms (30 FPS).                 │  ← Warning label
│    Enable 'Allow Long Exposure' for longer times.     │
│                                                        │
│ Gain (dB):                        [✓] Auto            │
│ ▬▬▬●▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬          │
│ 0.0 dB                          [Enter dB_____]       │
└────────────────────────────────────────────────────────┘
```

**Visual States:**

1. **Safe exposure (<33ms):**
   - Checkbox: Available, unchecked
   - Warning: Hidden
   - Style: Normal

2. **Blocked long exposure:**
   - Checkbox: Available, unchecked
   - Warning: Red, visible
   - Style: Error state

3. **Allowed long exposure:**
   - Checkbox: Available, checked
   - Warning: Orange, visible (info)
   - Style: Warning state

4. **Auto exposure mode:**
   - Checkbox: Disabled (grayed out)
   - Warning: Hidden
   - Style: Auto mode

---

## Code Architecture

```
User Action (Slider)
        ↓
_on_exposure_changed(value)
        ↓
   _is_exposure_safe(value)?
        ├─ NO → Clamp to 33ms, show warning, BLOCK change
        └─ YES → Send to camera controller
                   ↓
           camera.ExposureTime.set(value)
                   ↓
           Hardware confirms change
                   ↓
           exposure_changed signal
                   ↓
       _on_exposure_hardware_changed(value)
                   ↓
           Update UI + run _check_exposure_safety()
                   ↓
           Update warning label based on state
```

---

## Medical Device Compliance Notes

### FDA Human Factors (21 CFR Part 820.30)

**Requirement:** Prevent use errors that could affect safety or effectiveness

**Implementation:**
- ✅ Guard rail prevents accidental misconfiguration
- ✅ Clear warning messages explain consequences
- ✅ Explicit user acknowledgment required (checkbox)
- ✅ Visual distinction (color coding: red = error, orange = warning)

### IEC 62366-1 (Usability Engineering)

**Requirement:** Risk control through user interface design

**Implementation:**
- ✅ Progressive disclosure (checkbox hidden until needed)
- ✅ Immediate feedback (warning appears instantly)
- ✅ Reversible actions (checkbox can be unchecked)
- ✅ Predictable behavior (consistent with checkbox state)

### Design Rationale (ADR Format)

**Context:** Users need exposure control for image quality, but long exposures cause frame drops during live viewing.

**Decision:** Implement two-tier exposure control:
1. **Default mode:** Limit exposure to frame period (33ms at 30 FPS)
2. **Override mode:** Explicit checkbox enables long exposures

**Consequences:**
- ✅ Prevents accidental frame drops
- ✅ Maintains smooth live view by default
- ✅ Still allows long exposures for still imaging
- ✅ Clear user intent required for risky operations

**Alternatives Considered:**
1. **No limiter:** Rejected (too easy to misconfigure)
2. **Hard limit:** Rejected (removes valid use cases)
3. **Modal dialog:** Rejected (too intrusive for repeated use)
4. **Automatic FPS adjustment:** Rejected (too complex, unpredictable)

---

## Future Enhancements

### 1. Dynamic FPS-Based Limiting

**Current:** Fixed 33ms limit (assumes 30 FPS)
**Enhancement:** Calculate limit based on actual camera FPS

```python
def _get_max_safe_exposure_us(self) -> int:
    """Calculate safe exposure for current FPS."""
    if self.camera_controller:
        fps_info = self.camera_controller.get_acquisition_frame_rate_info()
        frame_period_ms = 1000.0 / fps_info["current_fps"]
        # 90% of frame period for processing margin
        safe_period_ms = frame_period_ms * 0.9
        return int(safe_period_ms * 1000)  # ms → µs
    return 33000  # fallback
```

### 2. Exposure Presets

**Add quick-access buttons:**
- Fast (10ms) - Live viewing
- Medium (20ms) - Balanced
- Slow (50ms) - Low light (requires checkbox)
- Still (200ms) - High quality capture (requires checkbox)

### 3. Auto-Disable Long Exposure on Streaming Start

**Behavior:** When starting streaming, automatically uncheck "Allow Long Exposure" if checked
**Rationale:** Streaming session should start in safe mode by default

---

## Rollback Plan

If issues arise, temporarily disable the safety feature:

```python
# In camera_widget.py:964
def _is_exposure_safe(self, exposure_us: int) -> bool:
    # TEMPORARY: Disable safety limiter
    return True  # Always allow any exposure

    # Original code:
    # max_safe_exposure_us = 33000
    # return (exposure_us <= max_safe_exposure_us or
    #         self.allow_long_exposure_check.isChecked())
```

---

## Related Documentation

- **CAMERA_PERFORMANCE_FIXES.md** - Camera optimization context
- **LESSONS_LEARNED.md** - Camera-related lessons
- **CLAUDE.md** - Project overview and safety philosophy

---

**Document Version:** 1.0
**Author:** AI Assistant (Claude Code)
**Review Required:** Usability testing with target users
**Compliance Review:** FDA human factors validation
