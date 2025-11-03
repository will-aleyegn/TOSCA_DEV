# TOSCA Research & Development Roadmap

**Last Updated:** 2025-10-30
**Current Version:** v0.9.11-alpha
**Mode:** RESEARCH/DEVELOPMENT ONLY
**Target:** Feature-complete research system (NOT for clinical use)

---

## ⚠️ IMPORTANT: Research Mode

**THIS ROADMAP IS FOR RESEARCH AND DEVELOPMENT ONLY**

This system is **NOT** approved for:
- Clinical use with real patients
- Collection of real patient data (PHI/PII)
- FDA-regulated medical device operation
- HIPAA-covered healthcare environments

**Security features NOT implemented:**
- ❌ Database encryption
- ❌ User authentication
- ❌ Video encryption
- ❌ Audit trail integrity protection
- ❌ FDA 21 CFR Part 11 compliance
- ❌ HIPAA compliance

**For clinical deployment, see:** `CLINICAL_DEPLOYMENT_ROADMAP.md`

---

## Overview

**Current Status:** Research & Development
**Focus:** Feature development, architecture improvements, safety testing
**Timeline:** 6-8 weeks (flexible, no regulatory pressure)
**Team:** 1-2 developers

### Goals

1. **Complete safety architecture** - 4-state safety model, comprehensive testing
2. **Optimize performance** - Video compression, database maintenance
3. **Improve code quality** - Refactoring, modularization, type hints
4. **Document thoroughly** - Architecture, concurrency, developer guides
5. **Validate stability** - 72-hour soak test, stress testing

---

## Research Mode Protection

### Immediate Task: Mark System as Research-Only

**Priority:** P0 (Do this first!)
**Effort:** 1 day

#### Task 1: Add Research Mode Warning Dialog

```python
# src/ui/research_mode_warning.py
from PyQt6.QtWidgets import QMessageBox, QCheckBox
from PyQt6.QtCore import Qt

class ResearchModeWarning(QMessageBox):
    """Warning dialog shown on startup in research mode."""

    def __init__(self):
        super().__init__()
        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowTitle("⚠️ RESEARCH MODE - NOT FOR CLINICAL USE")

        warning_text = """
<h2 style='color: red;'>⚠️ RESEARCH AND DEVELOPMENT MODE</h2>

<p><b>DO NOT USE WITH REAL PATIENT DATA</b></p>

<p>This software is for research and development only.</p>

<h3>Security Limitations:</h3>
<ul>
<li>❌ No database encryption (data stored in plaintext)</li>
<li>❌ No user authentication (anyone can access)</li>
<li>❌ No video encryption (recordings unprotected)</li>
<li>❌ No audit trail integrity (logs can be modified)</li>
</ul>

<h3>Not Compliant With:</h3>
<ul>
<li>❌ FDA 21 CFR Part 11 (Electronic Records)</li>
<li>❌ HIPAA Privacy Rule (PHI Protection)</li>
<li>❌ IEC 62304 Class C (Medical Device Software)</li>
</ul>

<p><b style='color: red;'>Use ONLY with de-identified test data!</b></p>

<p>For clinical deployment, see CLINICAL_DEPLOYMENT_ROADMAP.md</p>
        """

        self.setText(warning_text)
        self.setTextFormat(Qt.TextFormat.RichText)

        # Add "I understand" checkbox
        self.checkbox = QCheckBox("I understand this is research-only and will NOT use real patient data")
        self.setCheckBox(self.checkbox)

        self.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        self.setDefaultButton(QMessageBox.StandardButton.Cancel)

        # Disable OK until checkbox is checked
        ok_button = self.button(QMessageBox.StandardButton.Ok)
        ok_button.setEnabled(False)
        self.checkbox.stateChanged.connect(
            lambda state: ok_button.setEnabled(state == Qt.CheckState.Checked)
        )

    @staticmethod
    def show_and_confirm() -> bool:
        """Show warning and return True if user accepts."""
        dialog = ResearchModeWarning()
        return dialog.exec() == QMessageBox.StandardButton.Ok
```

**Integration in main.py:**

```python
# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.research_mode_warning import ResearchModeWarning

def main():
    app = QApplication(sys.argv)

    # RESEARCH MODE WARNING (MANDATORY)
    if not ResearchModeWarning.show_and_confirm():
        print("User declined research mode terms. Exiting.")
        sys.exit(0)

    # Continue with normal startup
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

**Files Created:**
- `src/ui/research_mode_warning.py`

**Files Modified:**
- `src/main.py`

---

#### Task 2: Add Research Mode Watermark

```python
# src/ui/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ... existing init

        # Add RESEARCH MODE watermark to title bar
        self.setWindowTitle("TOSCA Laser Control System v0.9.11-alpha [RESEARCH MODE - NOT FOR CLINICAL USE]")

        # Add research mode indicator to status bar
        self.research_mode_label = QLabel("⚠️ RESEARCH MODE - NO REAL PATIENT DATA")
        self.research_mode_label.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; padding: 5px;"
        )
        self.statusBar().addPermanentWidget(self.research_mode_label)
```

---

#### Task 3: Update Documentation

**README.md:**
```markdown
# TOSCA Laser Control System

**Version:** v0.9.11-alpha
**Status:** ⚠️ **RESEARCH AND DEVELOPMENT ONLY**

## ⚠️ WARNING: NOT FOR CLINICAL USE

This software is in RESEARCH MODE and is NOT approved for:
- Clinical use with real patients
- Collection of real patient data (PHI/PII)
- FDA-regulated medical device operation
- HIPAA-covered healthcare environments

**Security features NOT implemented:**
- Database encryption
- User authentication
- Video encryption
- Audit trail integrity protection

**Use ONLY with de-identified test data.**

For clinical deployment requirements, see `review_reports/CLINICAL_DEPLOYMENT_ROADMAP.md`.

## Installation

... existing installation instructions ...

## Usage

**IMPORTANT:** When prompted with the research mode warning:
1. Acknowledge you understand limitations
2. Use ONLY test subject codes (TEST001, TEST002, etc.)
3. Use ONLY fake dates of birth (1900-01-01)
4. Do NOT record real patient faces

... existing usage instructions ...
```

**CLAUDE.md update:**
```markdown
# TOSCA Project Context for AI Assistants

**Project:** TOSCA Laser Control System
**Version:** 0.9.11-alpha
**Mode:** ⚠️ RESEARCH/DEVELOPMENT ONLY

## ⚠️ CRITICAL: Research Mode

**This system is NOT for clinical use.**

Current limitations:
- No database encryption (PHI exposed if stolen)
- No user authentication (anyone can operate)
- No video encryption (patient faces visible)
- No audit trail integrity (logs can be tampered)

**When assisting with development:**
- Assume test data only (TEST001, TEST002, etc.)
- Focus on features and safety architecture
- Do NOT implement HIPAA compliance features (deferred)
- Do NOT implement FDA compliance features (deferred)

**For clinical deployment, see:** `review_reports/CLINICAL_DEPLOYMENT_ROADMAP.md`

... rest of existing content ...
```

---

## Research Roadmap (6-8 weeks)

### Phase R1: Safety Architecture (Weeks 1-3)

**Focus:** Complete safety features, comprehensive testing

#### Week 1: Research Mode Setup + 4-State Safety Model

**[ ] Day 1-2: Research Mode Protection**
- Add research mode warning dialog
- Add watermark to UI
- Update README and CLAUDE.md
- **Deliverables:**
  - Warning dialog with checkbox
  - Title bar watermark
  - Status bar indicator
  - Updated documentation

**[ ] Day 3-5: Implement 4-State Safety Model**
- Add ARMED and TREATING states to SafetyState enum
- Update state transition logic
- Integrate with UI (safety widget)
- Update documentation
- **Deliverables:**
  - 5 states: SAFE, ARMED, TREATING, UNSAFE, EMERGENCY_STOP
  - State-specific UI indicators
  - Enhanced audit trail

**Files Modified:**
- `src/ui/research_mode_warning.py` (new)
- `src/main.py`
- `src/ui/main_window.py`
- `src/core/safety.py`
- `src/ui/widgets/safety_widget.py`
- `README.md`
- `CLAUDE.md`

---

#### Week 2: Safety State Machine Testing

**[ ] Task: Write Comprehensive Safety Tests**
- State transition tests (15 tests)
- Interlock failure tests (10 tests)
- Selective shutdown tests (5 tests)
- Event logging tests (8 tests)
- Target: 100% coverage of `src/core/safety.py`

**Test Categories:**

1. **State Transitions:**
   ```python
   def test_initial_state_is_unsafe()
   def test_transition_to_safe_when_conditions_met()
   def test_safe_to_armed_when_power_set()
   def test_armed_to_treating_when_footpedal_pressed()
   def test_treating_to_armed_when_footpedal_released()
   ```

2. **Interlock Failures:**
   ```python
   def test_footpedal_release_disables_laser()
   def test_vibration_sensor_failure_disables_laser()
   def test_session_invalidation_disables_laser()
   def test_power_limit_exceeded_disables_laser()
   ```

3. **Emergency Stop:**
   ```python
   def test_emergency_stop_has_highest_priority()
   def test_cannot_exit_estop_without_reset()
   def test_reset_requires_all_conditions()
   ```

4. **Selective Shutdown:**
   ```python
   def test_emergency_stop_preserves_monitoring()
   def test_camera_remains_active_after_estop()
   def test_gpio_polling_continues_after_estop()
   ```

**Files Created:**
- `tests/core/test_safety_manager.py`

**Acceptance Criteria:**
- [ ] 100% line coverage of safety.py
- [ ] All state transitions tested
- [ ] All interlocks tested
- [ ] All tests pass

---

#### Week 3: Protocol Engine Safety Testing

**[ ] Task: Write Protocol Engine Safety Tests**
- Mid-execution interlock failure (3 tests)
- Emergency stop during protocol (2 tests)
- Protocol start validation (2 tests)
- Watchdog timeout simulation (1 test)

**Test Scenarios:**

```python
@pytest.mark.asyncio
async def test_protocol_halts_on_interlock_failure():
    """Protocol stops when footpedal released mid-execution."""
    # Start protocol
    # Wait 1 second
    # Simulate footpedal release
    # Verify protocol halts <200ms
    # Verify laser disabled

@pytest.mark.asyncio
async def test_emergency_stop_during_protocol():
    """E-stop immediately halts protocol."""
    # Start long protocol (10 seconds)
    # Wait 1 second
    # Trigger E-stop
    # Verify halt within 100ms

@pytest.mark.asyncio
async def test_protocol_refuses_to_start_if_unsafe():
    """Protocol won't start without safe state."""
    # Set interlocks to FAIL
    # Attempt to start protocol
    # Verify rejection
```

**Files Created:**
- `tests/core/test_protocol_engine_safety.py`

**Acceptance Criteria:**
- [ ] Safety paths 100% covered
- [ ] Halt latency <200ms
- [ ] Laser disabled immediately
- [ ] All tests pass

---

### Phase R2: Performance & Architecture (Weeks 4-5)

**Focus:** Optimize performance, document architecture

#### Week 4: Performance Optimizations

**[ ] Task 4.1: Video Compression Tuning (1 day)**
- Implement H.264 CRF 28 encoding
- Compare quality vs file size
- Measure performance impact
- **Goal:** 50% file size reduction (4 MB → 2 MB)

**[ ] Task 4.2: Database Vacuum Schedule (2 hours)**
- Add auto VACUUM on shutdown
- Add manual VACUUM in admin menu
- Enable incremental vacuum
- **Goal:** Reclaim deleted space automatically

**[ ] Task 4.3: Log Rotation (1 day)**
- Implement daily log rotation
- Add gzip compression
- Implement 7-year retention policy (research data retention)
- **Goal:** Prevent log files from growing indefinitely

**Files Modified:**
- `src/hardware/camera_controller.py`
- `src/database/db_manager.py`
- `src/ui/main_window.py`

**Files Created:**
- `src/core/log_rotator.py`

---

#### Week 5: Architecture Documentation

**[ ] Task 5.1: Document Asyncio Event Loop Integration (1 day)**
- Investigate current implementation
- Document findings in `docs/architecture/10_concurrency_model.md`
- Create migration plan for qasync (if needed)
- Validate GUI responsiveness

**[ ] Task 5.2: Performance Monitoring Dashboard (2 days)**
- Create PerformanceDashboard widget
- Add FPS gauge
- Add memory usage graph
- Add CPU usage meter
- Add disk space warning
- **Goal:** Real-time performance monitoring for debugging

**Files Created:**
- `src/ui/widgets/performance_dashboard.py`

**Files Modified:**
- `src/ui/main_window.py` (add dock widget)
- `docs/architecture/10_concurrency_model.md`

---

### Phase R3: Code Quality & Stability (Weeks 6-8)

**Focus:** Code refactoring, stability testing

#### Week 6: Code Quality Improvements

**[ ] Task 6.1: Refactor Protocol Engine (1 day)**
- Extract action dispatch to strategy pattern
- Create ActionExecutor base class
- Create 12 executor classes (one per action type)
- **Goal:** Reduce cyclomatic complexity from 22 → <5

**[ ] Task 6.2: Modularize GPIO Controller (4 hours)**
- Split 850-line file into 5 modules
- Extract VibrationMonitor
- Extract PhotodiodeMonitor
- Extract MotorController
- Extract InterlockManager
- **Goal:** Improve maintainability

**[ ] Task 6.3: Complete Type Hints (2 hours)**
- Add type hints to remaining 5% of functions
- Run MyPy strict mode
- Fix any new type errors
- **Goal:** 100% type hint coverage

**Files Created:**
- `src/core/protocol_executors/base.py`
- `src/core/protocol_executors/set_laser_power_executor.py`
- ... (12 executor files)
- `src/hardware/gpio/vibration_monitor.py`
- `src/hardware/gpio/photodiode_monitor.py`
- `src/hardware/gpio/motor_controller.py`
- `src/hardware/gpio/interlock_manager.py`

**Files Modified:**
- `src/core/protocol_engine.py`
- `src/hardware/gpio_controller.py` → `src/hardware/gpio/gpio_controller.py`

---

#### Week 7: Stability Testing (OPTIONAL)

**[ ] Task 7.1: 72-Hour Soak Test**
- Run system continuously for 72 hours
- Monitor memory usage
- Monitor error rate
- **Goal:** Validate stability (≥95% success rate, <20% memory growth)

**Note:** This is optional for research mode, but highly recommended if you plan to use the system extensively.

**Files Created:**
- `tests/integration/test_72hour_soak.py`
- `tests/integration/soak_test_dashboard.py`

---

#### Week 8: Developer Documentation

**[ ] Task 8.1: Pre-Commit Hook Documentation (1 hour)**
- Document MyPy known issues
- Document --no-verify usage
- Document hook configuration

**[ ] Task 8.2: Development Setup Guide (2 hours)**
- Write step-by-step setup instructions
- Document troubleshooting
- Add hardware connection guide

**[ ] Task 8.3: Formalize LaserController Inheritance (2 hours)**
- Change `class LaserController(QObject)` → `class LaserController(HardwareControllerBase)`
- **Goal:** Type checking, explicit contract

**Files Created:**
- `docs/development/PRE_COMMIT_HOOKS.md`
- `docs/development/SETUP_GUIDE.md`

**Files Modified:**
- `src/hardware/laser_controller.py`

---

## Research Mode Checklist

### Week 1 Deliverables
- [ ] Research mode warning dialog functional
- [ ] UI shows "RESEARCH MODE" watermark
- [ ] README.md updated with warnings
- [ ] CLAUDE.md updated with limitations
- [ ] 4-state safety model implemented
- [ ] UI displays all 5 states correctly

### Week 2 Deliverables
- [ ] 38 safety tests written and passing
- [ ] 100% coverage of safety.py
- [ ] All state transitions validated

### Week 3 Deliverables
- [ ] 8 protocol safety tests passing
- [ ] Halt latency <200ms verified
- [ ] Laser disables immediately on failure

### Week 4 Deliverables
- [ ] Video compression optimized (50% reduction)
- [ ] Database vacuum automated
- [ ] Log rotation implemented

### Week 5 Deliverables
- [ ] Asyncio integration documented
- [ ] Performance dashboard functional

### Week 6 Deliverables
- [ ] Protocol engine refactored (CC <5)
- [ ] GPIO controller modularized
- [ ] 100% type hint coverage

### Week 7 Deliverables (Optional)
- [ ] 72-hour soak test passed

### Week 8 Deliverables
- [ ] Developer documentation complete
- [ ] LaserController inheritance formalized

---

## Success Metrics (Research Mode)

**Safety:**
- ✅ 100% safety test coverage
- ✅ All interlocks tested
- ✅ Selective shutdown validated
- ✅ State machine fully tested

**Performance:**
- ✅ 30 FPS camera streaming maintained
- ✅ Video files 50% smaller
- ✅ Database auto-maintenance working
- ✅ Log rotation preventing infinite growth

**Code Quality:**
- ✅ Protocol engine CC <5
- ✅ GPIO controller <200 lines per module
- ✅ 100% type hint coverage
- ✅ All MyPy checks passing

**Stability (Optional):**
- ✅ 72-hour soak test ≥95% completion
- ✅ <20% memory growth
- ✅ <5% error rate

**Documentation:**
- ✅ Architecture docs complete
- ✅ Developer setup guide functional
- ✅ Pre-commit hooks documented

---

## When to Switch to Clinical Deployment

**Triggers for Clinical Roadmap:**

1. **IRB approval** for clinical study
2. **Funding secured** for FDA submission
3. **Partnership** with clinical site
4. **6 months before** first human use

**When triggered, follow:** `CLINICAL_DEPLOYMENT_ROADMAP.md`

**Estimated transition effort:** 8 weeks + $78,000 budget

---

## Test Data Guidelines

**For Research Mode, use ONLY:**

### Subject Codes
- ✅ TEST001, TEST002, TEST003, ...
- ✅ DEMO-A, DEMO-B, DEMO-C, ...
- ✅ RESEARCH-001, RESEARCH-002, ...
- ❌ NEVER real patient identifiers

### Dates of Birth
- ✅ 1900-01-01 (clearly fake)
- ✅ 2000-01-01 (clearly fake)
- ❌ NEVER real patient DOB

### Names
- ✅ "Test Subject", "Demo Patient"
- ✅ Fictional names (John Doe, Jane Smith)
- ❌ NEVER real patient names

### Video Recordings
- ✅ Record test objects (mannequins, inanimate objects)
- ✅ Record consenting research team members
- ❌ NEVER record identifiable patient faces

---

## Budget (Research Mode)

**Total Estimated Cost:** $12,000 - $24,000

| Resource | Hours | Rate | Cost |
|----------|-------|------|------|
| Senior Engineer | 160-320 hrs | $75-150/hr | $12,000-$48,000 |
| QA Engineer (optional) | 40 hrs | $60/hr | $2,400 |

**Note:** Much cheaper than clinical roadmap ($78,000) because:
- No security specialist needed
- No regulatory consultant needed
- No penetration testing
- No compliance documentation overhead

**Funding Sources:**
- Research grants
- University funding
- Internal R&D budget

---

## Risks (Research Mode)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Someone uses with real data | Medium | Critical | Warning dialog, watermarks, documentation |
| Data breach (no encryption) | Low | High | Test data only, no PHI exposure |
| Feature creep delays research | Medium | Medium | Stick to roadmap, defer non-essentials |
| 72-hour soak test fails | Low | Medium | Fix issues, re-run (optional test) |

---

## Next Steps

**This Week:**
1. Add research mode warning dialog
2. Update README and CLAUDE.md
3. Start 4-state safety model

**Next 2 Weeks:**
- Complete safety architecture
- Write comprehensive safety tests

**Weeks 4-8:**
- Performance optimizations
- Code quality improvements
- Optional: 72-hour soak test

---

**Document Version:** 1.0 (Research Mode)
**Last Updated:** 2025-10-30
**For Clinical Deployment:** See `CLINICAL_DEPLOYMENT_ROADMAP.md`
