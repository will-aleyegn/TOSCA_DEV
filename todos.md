# TOSCA Project To-Do List

**Last Updated:** 2025-10-31
**Source:** Comprehensive Code Review (Milestone 5.17)
**Report:** `presubmit/reviews/COMPREHENSIVE_CODE_REVIEW_2025-10-31.md`

---

## 🔴 CRITICAL (P0) - Immediate Action Required

**None currently** - All critical issues resolved ✅

---

## 🟡 HIGH PRIORITY (P1) - This Week

### 1. Clean Obsolete Compiled Files ⏱️ **5 minutes**

**Issue:** 6 `.pyc` files exist without corresponding source files

**Files:**
```
src/ui/widgets/__pycache__/
├── actuator_widget.cpython-312.pyc       ❌
├── camera_connection_widget.cpython-312.pyc ❌
├── manual_override_widget.cpython-312.pyc   ❌
├── motor_widget.cpython-312.pyc            ❌
└── treatment_widget.cpython-312.pyc        ❌

src/hardware/__pycache__/
└── actuator_sequence.cpython-312.pyc       ❌
```

**Action:**
```bash
# Clean all __pycache__ directories
cd C:/Users/wille/Desktop/TOSCA-dev
find src -type d -name "__pycache__" -exec rm -rf {} +

# Verify cleanup
find src -name "*.pyc" | wc -l  # Should return 0

# Update .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore

# Commit
git add .gitignore
git commit -m "chore: clean obsolete .pyc files and update .gitignore"
```

**Status:** ⏳ Pending

---

### 2. Delete Unused Logger Module ⏱️ **30 minutes**

**Issue:** `src/utils/logger.py` (92 lines) completely unused

**Analysis:**
- `get_logger()` function never imported anywhere
- All modules use standard `logging.getLogger()` instead
- Entire module is dead code

**Decision:** **DELETE** (YAGNI principle - "You Aren't Gonna Need It")

**Action:**
```bash
# Remove unused module
rm src/utils/logger.py

# Check if utils/ directory is now empty
ls src/utils/

# If only __init__.py remains, optionally remove entire package
# (Evaluate if any future utility modules are planned)

# Commit
git add src/utils/logger.py
git commit -m "chore: remove unused logger module (YAGNI principle)"
```

**Alternative:** If team wants to adopt this module, migrate all 40+ files to use it (2-3 hours effort)

**Status:** ⏳ Pending

---

## 🟠 MEDIUM PRIORITY (P2) - Next Sprint

### 3. Refactor High-Complexity Functions ⏱️ **8-10 hours**

**Issue:** 6 functions exceed cyclomatic complexity threshold (>10)

**Priority 1: camera_controller.run() - Complexity 24** ⏱️ **4 hours**

**File:** `src/hardware/camera_controller.py:67`

**Problem:**
- Mixed concerns: frame acquisition, format conversion, error handling
- 100+ lines in single method
- Difficult to test, high bug risk

**Refactoring Strategy:**
```python
# BEFORE: Complexity 24
def run(self) -> None:
    # 100+ lines mixing all concerns

# AFTER: Complexity 8
def run(self) -> None:
    """Main loop - simplified."""
    while self.running:
        try:
            frame = self._acquire_frame()
            if frame:
                pixmap = self._process_frame(frame)
                self._emit_frame(pixmap)
                self._record_frame(frame)
        except Exception as e:
            self._handle_error(e)

# Extract methods:
def _acquire_frame(self) -> Optional[np.ndarray]: ...
def _process_frame(self, frame: np.ndarray) -> QPixmap: ...
def _emit_frame(self, pixmap: QPixmap) -> None: ...
def _record_frame(self, frame: np.ndarray) -> None: ...
def _handle_error(self, error: Exception) -> None: ...
```

**Benefits:**
- Each method has single responsibility
- Easier to unit test
- Reduced bug risk
- Better readability

**Status:** ⏳ Pending

---

**Priority 2: camera_controller.frame_callback() - Complexity 21** ⏱️ **3 hours**

**File:** `src/hardware/camera_controller.py:76`

**Refactoring Strategy:**
- Extract pixel format converter
- Separate frame validation logic
- Isolate queue management

**Status:** ⏳ Pending

---

**Priority 3: main_window.closeEvent() - Complexity 19** ⏱️ **2 hours**

**File:** `src/ui/main_window.py:1302`

**Refactoring Strategy:**
- Extract hardware shutdown sequence
- Separate database cleanup
- Isolate worker thread termination

**Status:** ⏳ Pending

---

### 4. Audit Potentially Unused Functions ⏱️ **2-3 hours**

**Issue:** 61 functions defined but never called (29% of codebase)

**Categories:**

#### A. Safety/Session Functions (8 functions) - **KEEP + VERIFY**
```python
core.safety.arm_system()              # May be signal/slot connected
core.safety.disarm_system()           # May be signal/slot connected
core.safety.start_treatment()         # May be signal/slot connected
core.safety.stop_treatment()          # May be signal/slot connected
core.safety.clear_emergency_stop()    # May be signal/slot connected
core.session_manager.abort_session()  # Reserved for UI
core.session_manager.pause_session()  # Reserved for UI
core.session_manager.resume_session() # Reserved for UI
```

**Action:**
- [ ] Verify signal/slot connections (manual inspection)
- [ ] Add comment: `# Reserved for UI controls (future enhancement)`
- [ ] Add unit tests to ensure they work when called

---

#### B. Hardware Status Methods (12 functions) - **KEEP (Standard API)**
```python
hardware.*.get_status()  # Standard pattern across 5 controllers
hardware.camera_controller.get_binning()  # Feature not used
hardware.camera_controller.set_binning()  # Feature not used
```

**Action:**
- [ ] Keep `get_status()` methods (standard API)
- [ ] Decide on binning: Delete if feature abandoned

---

#### C. Experimental Features (3 functions) - **REVIEW + DECIDE**
```python
hardware.actuator_controller.start_scan()       # Line scanning not implemented
core.safety_watchdog.simulate_freeze()          # Testing utility - KEEP
config.models.validate_heartbeat_against_timeout()  # Validator unused
```

**Action:**
- [ ] `start_scan()`: Delete if line scanning abandoned
- [ ] `simulate_freeze()`: Keep (useful for testing)
- [ ] `validate_heartbeat_against_timeout()`: Add decorator or delete

---

#### D. Widget API Methods (10 functions) - **REVIEW**
```python
ui.widgets.camera_widget.set_dev_mode()
ui.widgets.treatment_setup_widget.set_dev_mode()
ui.widgets.camera_widget.hide_connection_controls()
ui.widgets.camera_widget.show_connection_controls()
```

**Action:**
- [ ] Review dev mode methods - May be enabled via config
- [ ] Review UI control methods - Delete if not planned
- [ ] Keep manual update methods - Useful for debugging

---

#### E. Full Audit Checklist

**For each of 61 functions:**
1. [ ] Check if called via signal/slot (manual inspection)
2. [ ] Check if reserved for future feature (roadmap)
3. [ ] Decision:
   - **Keep + Document** → Add comment `# Reserved for [purpose]`
   - **Keep + Test** → Add unit test
   - **Delete** → Remove code

**Deliverable:** Updated codebase with decisions implemented

**Status:** ⏳ Pending

---

### 5. Add Unit Tests for Safety Functions ⏱️ **8 hours**

**Issue:** Safety-critical functions lack tests even if currently unused

**Test Priority:**
1. [ ] `safety.arm_system()` - State machine test
2. [ ] `safety.start_treatment()` - Permission validation test
3. [ ] `safety.stop_treatment()` - State transition test
4. [ ] `safety.clear_emergency_stop()` - Recovery test
5. [ ] `session_manager.abort_session()` - Cleanup test

**Test Framework:** pytest (already in use)

**Test Coverage Target:** 80% for safety-critical modules

**Status:** ⏳ Pending

---

## 📝 LOW PRIORITY (P3) - Next Release

### 6. Reduce main_window.py Coupling ⏱️ **1 day**

**Issue:** MainWindow imports 19 project modules (high coupling)

**Refactoring Strategy:**
```python
# Create HardwareManager facade
class HardwareManager:
    """Manages all hardware controller lifecycle."""
    def __init__(self):
        self.laser = LaserController()
        self.tec = TECController()
        self.camera = CameraController()
        self.actuator = ActuatorController()
        self.gpio = GPIOController()

    def connect_all(self) -> Dict[str, bool]:
        """Connect all hardware, return status."""
        ...

    def disconnect_all(self) -> None:
        """Disconnect all hardware."""
        ...

# Simplify MainWindow
class MainWindow:
    def __init__(self):
        self.hardware = HardwareManager()  # Single import!
        self._init_widgets()
        self._init_safety()
```

**Benefits:**
- Reduced coupling (19 imports → 1)
- Easier testing (mock single facade)
- Cleaner initialization

**Status:** ⏳ Pending

---

### 7. Add Architecture Decision Records (ADRs) ⏱️ **2 hours**

**Issue:** Major architectural decisions lack documentation

**ADRs to Create:**
```
docs/architecture/adr/
├── ADR-001-selective-shutdown-policy.md
├── ADR-002-qpixmap-architecture.md
├── ADR-003-thread-safety-strategy.md
└── ADR-004-camera-downsampling.md
```

**Template:**
```markdown
# ADR-XXX: Decision Title

## Status
Accepted / Deprecated / Superseded

## Context
What was the problem?

## Decision
What did we decide?

## Consequences
What are the trade-offs?

## References
Links to related docs, issues, or code
```

**Status:** ⏳ Pending

---

### 8. Establish Code Quality Policy ⏱️ **1 hour**

**Issue:** No formal complexity limits or testing requirements

**Policy to Create:** `docs/CODE_QUALITY_POLICY.md`

**Contents:**
```markdown
# Code Quality Standards

## Complexity Limits
- Maximum cyclomatic complexity: 15 (hard limit)
- Target complexity: < 10
- Functions exceeding 10: require justification comment

## Testing Requirements
- All public functions must have:
  - At least one unit test OR
  - Comment explaining why untested (e.g., "Reserved for UI")
- Safety-critical functions: 100% branch coverage

## Documentation Requirements
- All public functions: docstring with parameters
- All classes: docstring with purpose
- All modules: module-level docstring

## Dead Code Policy
- No function may exist >6 months without:
  - Being called OR
  - Having unit test OR
  - Being documented as "Reserved for [purpose]"
```

**Status:** ⏳ Pending

---

## 📊 Progress Tracking

**Immediate Actions (Week 1):**
- [ ] Task 1: Clean obsolete .pyc files (5 min)
- [ ] Task 2: Delete unused logger module (30 min)
- **Total:** 35 minutes
- **Progress:** 0/2 complete (0%)

**Short-Term Actions (Sprint 1):**
- [ ] Task 3: Refactor high-complexity functions (8-10 hours)
- [ ] Task 4: Audit 61 unused functions (2-3 hours)
- [ ] Task 5: Add safety function tests (8 hours)
- **Total:** ~20 hours
- **Progress:** 0/3 complete (0%)

**Long-Term Actions (Release 1):**
- [ ] Task 6: Reduce main_window.py coupling (1 day)
- [ ] Task 7: Add Architecture Decision Records (2 hours)
- [ ] Task 8: Establish code quality policy (1 hour)
- **Total:** ~2 days
- **Progress:** 0/3 complete (0%)

**Overall Progress:** 0/8 tasks complete (0%)

---

## 📈 Success Metrics

**Code Quality:**
- ✅ Security vulnerabilities: 0 (maintained)
- ⏳ Average complexity: 4.2 → target 3.5
- ⏳ Unused functions: 61 → target <10
- ⏳ Test coverage: Unknown → target 80%

**Production Readiness:**
- ⏳ Critical issues: 0 (maintained)
- ⏳ High priority issues: 2 → target 0
- ⏳ Medium priority issues: 2 → target 0

---

## 📝 Notes

- **Code Review Report:** Full details in `presubmit/reviews/COMPREHENSIVE_CODE_REVIEW_2025-10-31.md`
- **Project Status:** Updated in `presubmit/PROJECT_STATUS.md` (Milestone 5.17)
- **Work Log:** Updated in `presubmit/WORK_LOG.md` (2025-10-31 entry)

**Next Review:** Recommended after Phase 6 (Pre-clinical validation with encryption + authentication)
