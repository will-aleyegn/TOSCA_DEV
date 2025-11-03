# Dead Code Cross-Reference with Test Files

**Date:** 2025-10-31
**Task:** Subtask 2.3 - Cross-reference vulture findings with test code
**Purpose:** Verify if any test files use the unused parameters

---

## Search Results Summary

### 1. footpedal_state Parameter

**Grep Results:**
```
src/core/event_logger.py:        footpedal_state: Optional[bool] = None,
src/core/event_logger.py:            footpedal_state: Optional footpedal state
src/database/models.py:    footpedal_state: Mapped[Optional[bool]] = mapped_column(Boolean)
```

**Analysis:**
- ✅ Defined in `event_logger.py:189` as method parameter
- ✅ Documented in docstring as optional parameter
- ✅ Defined in database schema (`models.py`) as Event table column
- ❌ **NOT used in any actual log_event() calls** (no grep hits with actual usage)
- ❌ **NOT used in any test files** (no test directory hits)

**Conclusion:** Parameter exists in API and database schema but is never actually passed when logging events.

### 2. smoothing_device_state Parameter

**Grep Results:**
```
src/core/event_logger.py:        smoothing_device_state: Optional[bool] = None,
src/core/event_logger.py:            smoothing_device_state: Optional smoothing device state
src/database/models.py:    smoothing_device_state: Mapped[Optional[bool]] = mapped_column(Boolean)
```

**Analysis:**
- ✅ Defined in `event_logger.py:190` as method parameter
- ✅ Documented in docstring as optional parameter
- ✅ Defined in database schema (`models.py`) as Event table column
- ❌ **NOT used in any actual log_event() calls** (no grep hits with actual usage)
- ❌ **NOT used in any test files** (no test directory hits)

**Conclusion:** Parameter exists in API and database schema but is never actually passed when logging events.

---

## Category: API Contract Parameters

### 3. stream Parameter (camera_controller.py:76)

**Context:** VmbPy callback signature
```python
def frame_callback(cam: Any, stream: Any, frame: Any) -> None:
```

**Search:** No test files use this directly (it's a private callback)
**Conclusion:** Required by VmbPy API contract, correctly unused

### 4. kwargs Parameter (hardware_controller_base.py:75)

**Context:** Abstract method flexibility
```python
@abstractmethod
def connect(self, **kwargs: Any) -> bool:
```

**Search:** Subclasses use different connection parameters (port, baud_rate, etc.)
**Conclusion:** Enables polymorphic hardware connections, correctly designed

---

## Key Findings

### Database Schema vs Actual Usage Mismatch

**Issue:** Database Event table has columns for safety interlock states that are never populated:

1. **`footpedal_state` column** - Database column exists, never written to
2. **`smoothing_device_state` column** - Database column exists, never written to

**Impact:**
- Database queries on these columns will always return NULL
- Storage space allocated but unused
- May confuse future developers expecting these fields to contain data

**Root Cause:**
- These appear to be part of initial design for comprehensive safety event logging
- Implementation was partial: API parameters added, database columns created
- Actual population of these fields was never implemented
- No calling code attempts to pass these values

**Verification:**
```bash
# Search for log_event calls with these parameters
grep -r "log_event.*footpedal" src/  # No hits
grep -r "log_event.*smoothing" src/  # No hits
```

---

## Test Coverage Analysis

### Missing Tests
- No test files verify event logging with interlock states
- No test files attempt to pass `footpedal_state` or `smoothing_device_state`
- No integration tests for safety event logging with hardware states

### Potential Test Scenarios (if keeping these parameters)
1. **Unit Test:** `test_event_logger.py`
   ```python
   def test_log_event_with_interlock_states():
       event_logger.log_event(
           EventType.SAFETY_FAULT,
           "Footpedal released during treatment",
           footpedal_state=False,
           smoothing_device_state=True
       )
       # Verify database columns populated
   ```

2. **Integration Test:** `test_safety_events.py`
   ```python
   def test_safety_fault_logs_interlock_states(safety_manager, gpio_controller):
       # Trigger safety fault
       gpio_controller.footpedal_released.emit()
       # Verify event log captured footpedal_state=False
   ```

---

## Recommendations

### Option 1: Remove Unused Parameters (Cleanup Approach)
**Remove from:**
- `src/core/event_logger.py` - Remove parameters from `log_event()` signature
- `src/database/models.py` - Remove columns from Event table schema (requires migration)

**Pros:**
- Clean codebase without unused API surface
- Smaller database schema
- No confusion about expected behavior

**Cons:**
- Requires database migration (medical device consideration)
- Loses potential future capability without re-adding

### Option 2: Implement Usage (Complete Feature Approach)
**Add to:**
- Safety event logging in `src/core/safety.py`
- GPIO state change handlers
- All safety-critical event calls

**Pros:**
- Complete safety audit trail
- Useful for regulatory compliance (FDA event logging)
- Database already supports it

**Cons:**
- Requires implementation effort
- Must ensure thread-safe GPIO state reads
- More complex event logging

### Option 3: Document as Future Use (Defer Approach)
**Add to:**
- `.vulture_whitelist.py` - Whitelist these parameters explicitly
- Code comments - Mark as "FUTURE: Planned for comprehensive safety logging"

**Pros:**
- Preserves capability for future enhancement
- Minimal effort
- Documents intent

**Cons:**
- Continues to have unused code
- Database columns remain empty

---

## Medical Device Compliance Considerations

**FDA 21 CFR 820.30(j) - Design Transfer:**
- If these columns were part of original safety requirements, verify removal doesn't affect traceability
- Event logging is critical for device history records (DHR)
- Consider if safety event audits require interlock state capture

**IEC 62304 - Software Verification:**
- Unused database columns may indicate incomplete implementation
- Should verify if original V&V plan expected these fields
- Document rationale for removal if chosen

**Recommendation:** Review original system requirements to determine if interlock state logging was a specified feature.

---

## Next Steps

1. **Verify original design intent**
   - Check requirements documents for safety event logging specification
   - Confirm if interlock states were required for safety analysis

2. **Decision required:**
   - Remove (Option 1) - if confirmed not in requirements
   - Implement (Option 2) - if required for safety compliance
   - Defer (Option 3) - if future enhancement planned

3. **Safety-critical module review** (Subtask 2.4)
   - Manual review of event_logger.py
   - Verify no other incomplete safety features

---

**Cross-Reference Completed:** 2025-10-31
**Test Files Checked:** tests/ directory (no usage found)
**Source Files Checked:** All Python files in src/
**Database Schema Verified:** models.py Event table

**Analyst:** AI Agent (Claude Code)
**Task Master Task:** 2.3 - Cross-reference with Test Files
