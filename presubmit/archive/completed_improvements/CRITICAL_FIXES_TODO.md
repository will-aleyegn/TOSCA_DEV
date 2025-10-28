# CRITICAL FIXES TODO - UI Redesign Code Review

**Generated:** 2025-10-27
**Priority:** IMMEDIATE ACTION REQUIRED
**Risk Level:** HIGH - Thread safety violation could cause crashes

---

## 🔴 DAY 1 - CRITICAL FIX (Do First!)

### Fix Thread Safety Violation

**FILE:** `src/ui/widgets/active_treatment_widget.py`
**LINES:** 49-55 (ProtocolExecutionThread class)

**STEPS:**
1. [ ] Create `src/ui/workers/protocol_worker.py` with QRunnable pattern
2. [ ] Remove ProtocolExecutionThread class entirely
3. [ ] Update ActiveTreatmentWidget to use ProtocolWorker
4. [ ] Add proper cleanup() method
5. [ ] Test with mock protocol execution
6. [ ] Verify no crashes under stress

**TEST COMMAND:**
```bash
python tests/test_protocol_worker.py
python -m pytest tests/integration/test_protocol_execution.py
```

---

## 🟠 DAY 2-3 - HIGH PRIORITY

### Add Protocol Validation

**FILE:** `src/ui/widgets/treatment_setup_widget.py`
**LINES:** 180-199 (_on_load_protocol_clicked method)

**STEPS:**
1. [ ] Create `src/core/protocol_schema.py` with JSON schema
2. [ ] Add jsonschema to requirements.txt
3. [ ] Update _on_load_protocol_clicked with validation
4. [ ] Add safety limit checks (max power, duration)
5. [ ] Test with valid and invalid protocols
6. [ ] Create example valid protocols in `protocols/examples/`

**VALIDATION RULES:**
- Max laser power: 5.0W
- Max duration: 3600 seconds (1 hour)
- Required fields: name, version, actions
- Version format: X.Y.Z (semantic)

### Fix UI Thread Blocking

**FILES:**
- `src/ui/widgets/gpio_widget.py:295`
- `src/ui/widgets/laser_widget.py:274`
- `src/ui/widgets/actuator_widget.py:170`

**STEPS:**
1. [ ] Create `src/ui/workers/connection_worker.py`
2. [ ] Update GPIO widget with ConnectionWorker
3. [ ] Update Laser widget with ConnectionWorker
4. [ ] Update Actuator widget with ConnectionWorker
5. [ ] Add progress signals for user feedback
6. [ ] Test all connections work without freezing

**SUCCESS CRITERIA:**
- UI remains responsive during connections
- Progress feedback shown to user
- Proper error handling for failed connections

---

## 🟠 DAY 4-5 - RESOURCE MANAGEMENT

### Implement Proper Cleanup

**FILES NEEDING CLEANUP:**
- [ ] `src/ui/widgets/active_treatment_widget.py`
- [ ] `src/ui/widgets/camera_widget.py`
- [ ] `src/ui/widgets/treatment_setup_widget.py`
- [ ] `src/ui/widgets/gpio_widget.py`
- [ ] `src/ui/widgets/laser_widget.py`
- [ ] `src/ui/widgets/actuator_widget.py`

**CLEANUP TEMPLATE:**
```python
def cleanup(self) -> None:
    """Clean up resources on shutdown."""
    logger.info(f"Cleaning up {self.__class__.__name__}...")

    # Stop operations
    if self.worker:
        self.worker.cancel()

    # Stop timers
    if self.timer and self.timer.isActive():
        self.timer.stop()

    # Disconnect hardware
    if self.controller and self.controller.is_connected:
        self.controller.disconnect()

    # Wait for threads
    QThreadPool.globalInstance().waitForDone(1000)

    logger.info(f"{self.__class__.__name__} cleanup complete")
```

---

## 🟡 WEEK 2 - MEDIUM PRIORITY

### Fix Exception Handling

**PATTERN TO REPLACE:**
```python
# BAD
except Exception as e:
    logger.error(f"Error: {e}")

# GOOD
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
except SerialException as e:
    logger.error(f"Serial error: {e}")
```

### Decouple Widgets

**FILE:** `src/ui/main_window.py:691-712`

**ADD PUBLIC METHODS:**
```python
# In each widget
def connect_hardware(self) -> None:
    """Public connection method."""

def disconnect_hardware(self) -> None:
    """Public disconnection method."""

def is_connected(self) -> bool:
    """Check connection status."""
```

---

## 🟢 WEEK 3 - LOW PRIORITY

### Create Constants Module

**FILE TO CREATE:** `src/ui/constants.py`

**CONTENTS:**
- Window dimensions
- Font sizes (min 11px)
- Colors (safety appropriate)
- Timeouts
- Safety thresholds
- Protocol limits

---

## Testing Checklist

### After Each Fix:
- [ ] Run existing unit tests
- [ ] Create new tests for fix
- [ ] Manual testing of affected features
- [ ] Check for regressions
- [ ] Update documentation

### Integration Tests:
- [ ] Full protocol execution
- [ ] Hardware connection sequence
- [ ] Emergency stop during protocol
- [ ] Clean application shutdown
- [ ] 100 protocol runs without crash

### Performance Tests:
- [ ] UI responsiveness < 100ms
- [ ] Memory usage stable over time
- [ ] No thread deadlocks
- [ ] Clean shutdown < 2 seconds

---

## Git Commits

**IMPORTANT:** Follow commit message format:

```
fix: Replace dangerous asyncio-in-QThread with QRunnable pattern

- Remove ProtocolExecutionThread class
- Add ProtocolWorker using QRunnable
- Implement proper cleanup in ActiveTreatmentWidget
- Add tests for thread safety

Fixes critical thread safety violation that could cause crashes
during treatment execution.
```

**Branch Strategy:**
```bash
git checkout -b fix/critical-thread-safety
# Make fixes
git commit -m "fix: ..."
git push origin fix/critical-thread-safety
# Create PR for review
```

---

## Definition of Done

Each fix is complete when:
1. ✅ Code implemented according to plan
2. ✅ Unit tests written and passing
3. ✅ Integration tests passing
4. ✅ Manual testing completed
5. ✅ Documentation updated
6. ✅ Code reviewed (if team available)
7. ✅ Merged to main branch

---

## Questions/Blockers

**If blocked on:**
- Hardware access → Use mock controllers
- Testing equipment → Use simulation mode
- Dependencies → Check requirements.txt first

**Contact for help:**
- Thread safety → PyQt6 documentation
- Medical device standards → FDA guidance
- Protocol validation → JSON Schema docs

---

**Status:** Ready for implementation
**Owner:** Development team
**Deadline:** Thread safety fix - IMMEDIATE
