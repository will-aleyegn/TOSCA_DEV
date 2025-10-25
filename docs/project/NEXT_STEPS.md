# TOSCA Project - Next Steps

**Last Updated:** 2025-10-25
**Current Status:** Phase 3 at 95% - Aiming laser control complete
**Next Priority:** Phase 1 Architectural Improvements (Safety Watchdog)

---

## Immediate Completed Work

### Aiming Laser Implementation ✅

**Date Completed:** 2025-10-25

**What Was Done:**
- Added aiming laser control to GPIO controller (Pin D4)
- Created aiming laser UI in LaserWidget (ON/OFF buttons)
- Wired GPIO controller to laser widget in MainWindow
- All code passes pre-commit hooks (Black, Flake8, MyPy, isort)

**Files Modified:**
- `src/hardware/gpio_controller.py` - Added aiming laser hardware control
- `src/ui/widgets/laser_widget.py` - Added aiming laser GUI
- `src/ui/main_window.py` - Wired GPIO to laser widget

**Testing Status:**
- [ ] Hardware test with actual Arduino (pending hardware availability)
- [x] Code quality validation (pre-commit hooks pass)
- [x] Type checking (MyPy) pass

---

## Critical Architectural Improvements Identified

### 5 Key Issues Discovered

During aiming laser implementation, identified 5 architectural improvements:

1. **Safety Watchdog Timer** (CRITICAL - Priority 1)
2. **Configuration Management** (HIGH - Priority 2)
3. **Hardware Controller ABC** (MEDIUM - Priority 3)
4. **Import Path Standardization** (LOW - Priority 4)
5. **Dependency Injection** (DEFERRED - Not recommended)

**Documentation Created:**
- `docs/architecture/ARCHITECTURAL_DEBT.md` - Detailed analysis of all 5 issues
- `docs/architecture/IMPLEMENTATION_PLAN_WATCHDOG.md` - Complete watchdog implementation plan
- `docs/architecture/IMPLEMENTATION_PLAN_CONFIG.md` - Complete config system plan

---

## Phase 1: Safety Watchdog Timer (IMMEDIATE)

**Priority:** CRITICAL - Must complete before clinical testing
**Timeline:** 3-5 days
**Effort:** Medium-High

### Why This Is Critical

**Hazard:** Python GUI freeze (infinite loop, deadlock, OS crash) leaves hardware in dangerous state.

**Example Scenario:**
- Treatment laser ON at 1500mA
- GUI freezes due to software bug
- Laser remains ON indefinitely
- **Patient harm risk: Thermal injury**

**Regulatory:** FDA 21 CFR 820.30(g) requires risk analysis for software failures.

### Implementation Tasks

See `docs/architecture/IMPLEMENTATION_PLAN_WATCHDOG.md` for complete details.

**Summary:**

1. **Arduino Watchdog Firmware**
   - Add watchdog timer to Arduino (1000ms timeout)
   - Emergency shutdown on timeout (all outputs LOW)
   - Heartbeat input via serial or GPIO

2. **SafetyWatchdog Python Class**
   - Send heartbeat every 500ms
   - Monitor watchdog status
   - Emit signals on timeout

3. **MainWindow Integration**
   - Start watchdog after GPIO connects
   - Stop watchdog on shutdown
   - Log all watchdog events

4. **Testing**
   - Simulate GUI freeze
   - Verify hardware shutdown within 1000ms
   - 24-hour stress test

**Files to Create:**
- `firmware/arduino_watchdog/arduino_watchdog.ino`
- `src/core/safety_watchdog.py`
- `docs/architecture/06_safety_watchdog.md`
- `tests/test_watchdog.py`

**Success Criteria:**
- [ ] GUI freeze triggers shutdown within 1000ms
- [ ] All hardware outputs LOW after timeout
- [ ] System recoverable after power cycle
- [ ] <0.1% false positive rate
- [ ] 24-hour continuous operation test passes

---

## Phase 2: Configuration Management (HIGH PRIORITY)

**Priority:** HIGH - Complete before production deployment
**Timeline:** 2-3 days
**Effort:** Medium

### Why This Matters

**Current Problem:** Safety limits hardcoded in multiple files with no validation.

**Example Issues:**
```python
# gpio_controller.py:91
self.photodiode_voltage_to_power = 400.0  # What if this is wrong?

# laser_controller.py:59
self.max_current_ma = 2000.0  # No validation, no audit trail
```

**Risks:**
- Wrong calibration constant → wrong power calculation → patient harm
- No version control for safety limits
- Cannot support different hardware configurations

### Implementation Tasks

See `docs/architecture/IMPLEMENTATION_PLAN_CONFIG.md` for complete details.

**Summary:**

1. **Create Pydantic Config System**
   - Type-safe configuration classes
   - Validation rules (min/max, ranges)
   - Cross-field validation

2. **Create Configuration Files**
   - `config/hardware.yaml` - Hardware calibration
   - `config/safety.yaml` - Safety thresholds
   - `config/application.yaml` - App settings

3. **Migrate Controllers**
   - LaserController uses config limits
   - GPIOController uses config calibration
   - SafetyManager uses config thresholds

4. **Add Validation**
   - Startup config validation
   - Environment variable overrides
   - Config version tracking

**Files to Create:**
- `src/core/config.py`
- `config/hardware.yaml`
- `config/safety.yaml`
- `config/application.yaml`
- `docs/architecture/07_configuration_management.md`
- `tests/test_config.py`

**Success Criteria:**
- [ ] All hardcoded constants migrated
- [ ] Config validation catches errors
- [ ] Environment overrides working
- [ ] Unit tests >95% coverage
- [ ] No regressions in controllers

---

## Phase 3: Hardware Controller ABC (MEDIUM PRIORITY)

**Priority:** MEDIUM - Improve when refactoring controllers
**Timeline:** 1 week
**Effort:** Medium

### What This Improves

**Current:** Each controller has similar methods but no enforced contract.

**Goal:** Abstract base class ensures all controllers have consistent interface.

**Benefits:**
- Type safety (MyPy validation)
- Polymorphism (treat all controllers uniformly)
- Better testing (single mock base class)
- Self-documenting interface

### Implementation Tasks

1. **Create HardwareController ABC**
   - Define required methods (connect, disconnect)
   - Define required signals
   - Define required properties

2. **Refactor Controllers**
   - LaserController inherits from ABC
   - CameraController inherits from ABC
   - ActuatorController inherits from ABC
   - GPIOController inherits from ABC

3. **Update MainWindow**
   - Store controllers in polymorphic list
   - Unified cleanup on shutdown

**Files to Create:**
- `src/hardware/base_controller.py`
- Update all controller files

**Success Criteria:**
- [ ] All 4 controllers inherit from ABC
- [ ] MyPy validation passes
- [ ] No regressions
- [ ] Simplified testing

---

## Phase 4: Import Standardization (LOW PRIORITY)

**Priority:** LOW - Fix opportunistically
**Timeline:** 2 hours (automated)
**Effort:** Low

### What This Fixes

**Current:** Mix of absolute and relative imports.

**Goal:** All imports use absolute `from src.module` style (PEP 8).

### Implementation

```bash
# Run isort with standardization
isort --profile black --force-single-line-imports src/

# Review changes
git diff

# Commit
git commit -m "Standardize imports to absolute paths (PEP 8)"
```

**When to Do:** Opportunistically when touching files, not worth dedicated sprint.

---

## Phase 5: Documentation Updates

**Priority:** PARALLEL - Update as we implement

### Documentation to Create/Update

1. **Architecture Docs:**
   - [x] `docs/architecture/ARCHITECTURAL_DEBT.md`
   - [x] `docs/architecture/IMPLEMENTATION_PLAN_WATCHDOG.md`
   - [x] `docs/architecture/IMPLEMENTATION_PLAN_CONFIG.md`
   - [ ] `docs/architecture/06_safety_watchdog.md` (after implementation)
   - [ ] `docs/architecture/07_configuration_management.md` (after implementation)

2. **Project Status:**
   - [ ] Update `docs/project/PROJECT_STATUS.md` with Phase 3 completion
   - [ ] Add architectural improvements to status
   - [ ] Update completion percentages

3. **Coding Standards:**
   - [ ] Add watchdog testing requirements
   - [ ] Add config management rules
   - [ ] Add import standardization rules

4. **Lessons Learned:**
   - [ ] Create `docs/LESSONS_LEARNED.md` for architectural findings
   - [ ] Document aiming laser implementation experience

---

## Recommended Implementation Order

### Week 1: Safety Watchdog (CRITICAL)

**Days 1-2:**
- [ ] Research Arduino watchdog timer
- [ ] Design watchdog architecture
- [ ] Create SafetyWatchdog Python class
- [ ] Write unit tests

**Days 3-4:**
- [ ] Implement Arduino firmware with WDT
- [ ] Wire watchdog to GPIO controller
- [ ] Integrate into MainWindow
- [ ] Test freeze simulation

**Day 5:**
- [ ] 24-hour stress test
- [ ] Documentation
- [ ] Code review and approval

### Week 2: Configuration Management (HIGH)

**Days 1-2:**
- [ ] Create Pydantic config system
- [ ] Create YAML config files
- [ ] Write validation tests
- [ ] Test environment overrides

**Day 3:**
- [ ] Migrate LaserController to config
- [ ] Migrate GPIOController to config
- [ ] Test controller integration

**Day 4:**
- [ ] Migrate remaining controllers
- [ ] Add startup validation
- [ ] Integration testing

**Day 5:**
- [ ] Documentation
- [ ] Code review and approval
- [ ] Deploy to test environment

### Week 3: Hardware ABC + Documentation

**Days 1-3:**
- [ ] Create HardwareController ABC
- [ ] Refactor controllers one-by-one
- [ ] Update tests
- [ ] MyPy validation

**Days 4-5:**
- [ ] Complete all documentation
- [ ] Update PROJECT_STATUS.md
- [ ] Update CODING_STANDARDS.md
- [ ] Create LESSONS_LEARNED.md
- [ ] Final code review

---

## Success Metrics

### Safety Watchdog
- [x] Design complete
- [ ] Implementation complete
- [ ] All tests passing
- [ ] 24-hour stress test passed
- [ ] Documentation complete

### Configuration Management
- [x] Design complete
- [ ] Implementation complete
- [ ] All tests passing
- [ ] All constants migrated
- [ ] Documentation complete

### Hardware ABC
- [ ] Design complete
- [ ] Implementation complete
- [ ] All controllers refactored
- [ ] MyPy validation passing
- [ ] Documentation complete

### Overall Project
- [ ] Phase 3 documented as 100% complete
- [ ] Architectural debt addressed
- [ ] Code quality maintained
- [ ] No regressions introduced
- [ ] Ready for clinical testing

---

## Deferred Items

### Dependency Injection - NOT RECOMMENDED

**Decision:** Do not implement dependency injection pattern.

**Reasoning:**
- Adds complexity without clear benefit for GUI application
- PyQt Designer incompatible (expects zero-arg constructors)
- Current pattern is appropriate for ~5 managers
- Testing needs can be met with factory functions

**Alternative:** Use factory functions for testing:
```python
def create_main_window_for_testing():
    window = MainWindow()
    window.db_manager = MockDatabaseManager()
    return window
```

---

## Risk Management

### High-Risk Items

1. **Watchdog Implementation**
   - **Risk:** False positives cause unnecessary shutdowns
   - **Mitigation:** Extensive testing, tunable timeout values
   - **Rollback:** Software disable flag, non-watchdog firmware

2. **Config Migration**
   - **Risk:** Breaking existing controller behavior
   - **Mitigation:** Migrate one controller at a time, extensive testing
   - **Rollback:** Config fallback to hardcoded values

3. **Hardware ABC Refactor**
   - **Risk:** Introducing bugs in working controllers
   - **Mitigation:** Refactor one at a time, comprehensive test suite
   - **Rollback:** Git revert individual controller changes

---

## Questions for Team Discussion

1. **Watchdog Timeout Value:**
   - Current plan: 1000ms timeout, 500ms heartbeat
   - Is this appropriate for system? Too fast? Too slow?

2. **Config File Location:**
   - Current plan: `config/` directory in repo
   - Should configs be external (e.g., `/etc/tosca/`)?
   - How to handle per-device configs?

3. **Testing Requirements:**
   - 24-hour watchdog stress test sufficient?
   - Need for longer testing (week-long)?
   - Testing on all target hardware?

4. **Deployment Timeline:**
   - Can we afford 3 weeks for all improvements?
   - Which items are truly blocking for clinical testing?
   - Can some be done post-deployment?

---

## How to Use This Document

**For starting a new session:**
1. Read this document to understand current state
2. Check todo list in Claude Code for task details
3. Refer to implementation plans for detailed steps

**For project status:**
1. Check completion checkboxes
2. See PROJECT_STATUS.md for overall project state
3. See ARCHITECTURAL_DEBT.md for detailed analysis

**For implementation:**
1. Follow recommended week-by-week order
2. Use implementation plan documents for details
3. Update checkboxes as you complete tasks

---

**Status:** Active Planning
**Next Action:** Begin Phase 1 (Watchdog) implementation
**Owner:** Development Team
**Review Date:** After each phase completion
