# TOSCA Test Improvement Roadmap

**Date:** 2025-11-01
**Current Coverage:** 9.03% (8,404/9,311 statements missed)
**Target Coverage (Pre-Clinical):** 85% overall, 100% safety-critical
**Estimated Effort:** 400-600 new test cases, 8-12 weeks of development

---

## Executive Summary

This roadmap provides a **prioritized, phased approach** to achieving FDA-compliant test coverage for the TOSCA medical device software. Current coverage of 9.03% represents a **critical compliance risk** that must be addressed before clinical deployment.

### Key Priorities

1. **Phase 1 (IMMEDIATE):** Safety-critical modules (0% → 100% coverage)
2. **Phase 2 (HIGH):** Core business logic (33% → 95% coverage)
3. **Phase 3 (HIGH):** Hardware controllers (0% → 85% coverage)
4. **Phase 4 (MEDIUM):** UI components (0% → 70% coverage)
5. **Phase 5 (LOWER):** Configuration & utilities (0% → 60% coverage)

---

## Phase 1: Safety-Critical Testing (IMMEDIATE PRIORITY)

**Timeline:** Week 1-2
**Target:** 100% statement coverage, 100% branch coverage on all safety modules
**Estimated Effort:** 80-100 test cases

### 1.1 Emergency Stop Testing

**File:** `tests/test_safety/test_emergency_stop.py` (NEW)
**Target Module:** `src/core/safety.py:trigger_emergency_stop()`

**Test Cases:**

```python
# Priority: CRITICAL
def test_emergency_stop_disables_laser_immediately():
    """Verify emergency stop immediately disables laser enable."""
    # Setup: Safety manager with laser enabled
    # Action: Trigger emergency stop
    # Assert: laser_enable_permitted = False within 1ms

def test_emergency_stop_transitions_to_emergency_state():
    """Verify emergency stop transitions state machine to EMERGENCY_STOP."""
    # Assert: state == SafetyState.EMERGENCY_STOP
    # Assert: emergency_stop_active == True

def test_emergency_stop_emits_safety_state_changed_signal():
    """Verify signal emission for UI updates."""
    # Use QSignalSpy to capture signal
    # Assert: safety_state_changed emitted with EMERGENCY_STOP

def test_emergency_stop_from_all_states():
    """Test emergency stop works from SAFE, ARMED, TREATING, UNSAFE states."""
    # Parameterized test across all states
    # Assert: All transitions succeed

def test_emergency_stop_locks_system():
    """Verify system cannot be re-armed without clearing emergency stop."""
    # Assert: arm_system() fails after emergency stop
    # Assert: start_treatment() fails after emergency stop
```

**Line Numbers to Cover:** src/core/safety.py:95-110 (16 statements)

---

### 1.2 GPIO Safety Interlock Testing

**File:** `tests/test_hardware/test_gpio_safety_interlocks.py` (NEW)
**Target Module:** `src/hardware/gpio_controller.py`

**Test Cases:**

```python
# Priority: CRITICAL
def test_footpedal_active_high_requirement():
    """Verify footpedal must be HIGH for laser enable."""
    # Mock GPIO read: footpedal = LOW
    # Assert: safety_interlock_status['footpedal_ok'] = False
    # Mock GPIO read: footpedal = HIGH
    # Assert: safety_interlock_status['footpedal_ok'] = True

def test_photodiode_power_verification():
    """Verify photodiode power matches expected laser output."""
    # Mock laser power = 5.0W, photodiode = 4.8W (96% match)
    # Assert: photodiode_ok = True
    # Mock laser power = 5.0W, photodiode = 0.2W (4% match)
    # Assert: photodiode_ok = False, safety fault triggered

def test_smoothing_motor_dual_signal_validation():
    """Verify smoothing motor requires both motor signal AND vibration."""
    # Mock motor_running = True, vibration_detected = False
    # Assert: smoothing_motor_ok = False
    # Mock motor_running = True, vibration_detected = True
    # Assert: smoothing_motor_ok = True

def test_safety_interlock_changed_signal_emission():
    """Verify signal emitted on interlock status change."""
    # Use QSignalSpy
    # Change footpedal state
    # Assert: safety_interlock_changed emitted with updated dict

def test_hardware_watchdog_heartbeat():
    """Verify watchdog heartbeat sent every 500ms."""
    # Mock serial connection
    # Wait 500ms
    # Assert: "PING" command sent to Arduino

def test_watchdog_timeout_detection():
    """Verify watchdog timeout triggers safety fault after 1000ms."""
    # Mock serial connection with no response
    # Wait 1050ms
    # Assert: watchdog_timeout_detected signal emitted
```

**Line Numbers to Cover:** src/hardware/gpio_controller.py:50-346 (296+ statements)

---

### 1.3 State Machine Testing

**File:** `tests/test_safety/test_state_machine.py` (NEW)
**Target Module:** `src/core/safety.py`

**Test Cases:**

```python
# Priority: CRITICAL
def test_valid_transition_safe_to_armed():
    """Test SAFE → ARMED transition with all interlocks satisfied."""
    # Setup: All interlocks OK, active session
    # Action: arm_system()
    # Assert: state == SafetyState.ARMED
    # Assert: laser_enable_permitted = False (still not treating)

def test_valid_transition_armed_to_treating():
    """Test ARMED → TREATING transition enables laser."""
    # Setup: State = ARMED
    # Action: start_treatment()
    # Assert: state == SafetyState.TREATING
    # Assert: laser_enable_permitted = True

def test_invalid_transition_safe_to_treating_blocked():
    """Verify cannot skip ARMED state."""
    # Setup: State = SAFE
    # Action: start_treatment()
    # Assert: state == SafetyState.SAFE (unchanged)
    # Assert: Error logged

def test_safety_fault_triggers_unsafe_state():
    """Test ANY state → UNSAFE on interlock failure."""
    # Parameterized test: Start from SAFE, ARMED, TREATING
    # Trigger footpedal release
    # Assert: state == SafetyState.UNSAFE
    # Assert: laser_enable_permitted = False

def test_recovery_from_unsafe_state():
    """Test UNSAFE → SAFE after interlock restoration."""
    # Setup: State = UNSAFE due to footpedal
    # Action: Restore footpedal, call check_safety()
    # Assert: state == SafetyState.SAFE

def test_state_machine_prevents_reentrancy():
    """Verify concurrent state transitions are serialized."""
    # Use threading to call arm_system() and trigger_emergency_stop() simultaneously
    # Assert: State machine remains consistent
```

**Line Numbers to Cover:** src/core/safety.py:150-500 (state machine methods)

---

### 1.4 Protocol Engine Safety Integration

**File:** `tests/test_core/test_protocol_engine_safety.py` (NEW)
**Target Module:** `src/core/protocol_engine.py`

**Test Cases:**

```python
# Priority: CRITICAL
def test_protocol_execution_requires_armed_state():
    """Verify protocol cannot execute unless safety armed."""
    # Setup: State = SAFE
    # Action: Execute protocol
    # Assert: Execution blocked, error raised

def test_protocol_aborts_on_safety_fault():
    """Verify protocol aborts mid-execution on interlock failure."""
    # Setup: Protocol executing (state = TREATING)
    # Action: Trigger footpedal release mid-execution
    # Assert: Protocol execution halted
    # Assert: Laser disabled
    # Assert: State = UNSAFE

def test_protocol_respects_laser_power_limits():
    """Verify protocol cannot exceed configured max power."""
    # Setup: config.laser.max_power = 8.0W
    # Create protocol with 10.0W action
    # Assert: Validation error raised during protocol load

def test_emergency_stop_during_protocol_execution():
    """Verify emergency stop immediately halts protocol."""
    # Setup: Protocol executing
    # Action: Trigger emergency stop
    # Assert: Protocol halted within 10ms
    # Assert: Laser disabled
    # Assert: State = EMERGENCY_STOP
```

**Line Numbers to Cover:** src/core/protocol_engine.py:100-300 (safety check integration)

---

### Phase 1 Summary

| Test Suite | Test Cases | Statements Covered | Priority |
|------------|------------|-------------------|----------|
| Emergency Stop | 5 | 16 | CRITICAL |
| GPIO Interlocks | 6 | 296 | CRITICAL |
| State Machine | 6 | 350 | CRITICAL |
| Protocol Safety | 4 | 200 | CRITICAL |
| **TOTAL** | **21** | **862** | **CRITICAL** |

**Expected Coverage Gain:** 0% → 95%+ on safety-critical modules

---

## Phase 2: Core Business Logic Testing (HIGH PRIORITY)

**Timeline:** Week 3-4
**Target:** 95% coverage on core modules
**Estimated Effort:** 100-120 test cases

### 2.1 Session Manager Testing

**File:** `tests/test_core/test_session_manager_comprehensive.py` (EXPAND EXISTING)
**Target Module:** `src/core/session_manager.py` (currently 0% coverage)

**Test Cases:**

```python
# Fix existing failing tests first
def test_create_session_success_creates_db_and_folder_FIXED():
    """Fix Path.mkdir mock error from current failing test."""
    # Use tmp_path fixture instead of mocking Path

def test_create_session_emits_session_started_signal_FIXED():
    """Fix signal emission assertion."""
    # Use QSignalSpy correctly

# Add new comprehensive tests
def test_create_session_generates_unique_folder_name():
    """Verify session folder naming: data/sessions/P-YYYY-NNNN/YYYY-MM-DD_HHMMSS"""

def test_create_session_with_database_failure_rollback():
    """Verify transaction rollback if database insert fails."""

def test_end_session_updates_database():
    """Verify end_session() updates status and end_time."""

def test_get_active_session_returns_current():
    """Test active session tracking."""

def test_session_duration_calculation():
    """Test get_session_duration() accuracy."""
```

**Expected Coverage:** 0% → 90%+ (224 statements)

---

### 2.2 Protocol Execution Testing

**File:** `tests/test_core/test_protocol_engine_execution.py` (NEW)
**Target Module:** `src/core/protocol_engine.py` (currently 0% coverage)

**Test Cases:**

```python
def test_execute_laser_power_action():
    """Test LaserPowerAction execution with mock laser controller."""

def test_execute_wait_action_timing_accuracy():
    """Verify WaitAction waits correct duration (±10ms tolerance)."""

def test_execute_actuator_move_action():
    """Test ActuatorMoveAction with mock actuator controller."""

def test_execute_concurrent_line_actions():
    """Test LineProtocol with multiple simultaneous actions."""

def test_protocol_progress_callbacks():
    """Verify on_progress_update callback invoked correctly."""

def test_protocol_error_handling_continues_or_aborts():
    """Test error handling strategy (continue vs abort)."""
```

**Expected Coverage:** 0% → 85% (489 statements)

---

### 2.3 Database Manager Expansion

**File:** `tests/test_database/test_db_manager_comprehensive.py` (EXPAND)
**Target Module:** `src/database/db_manager.py` (currently 49% coverage)

**Test Cases:**

```python
# Fix existing vacuum test failures
def test_vacuum_reduces_size_FIXED():
    """Fix Subject model schema mismatch (first_name → subject_id)."""

# Add new CRUD tests
def test_create_technician():
    """Test add_technician() with all fields."""

def test_get_all_subjects_with_search_filter():
    """Test search functionality."""

def test_delete_subject_cascade():
    """Verify cascade delete of related sessions."""

def test_concurrent_database_access():
    """Test thread safety with multiple simultaneous queries."""
```

**Expected Coverage:** 49% → 90% (303 statements, +124 new coverage)

---

### Phase 2 Summary

| Module | Current Coverage | Target Coverage | New Tests | Priority |
|--------|------------------|-----------------|-----------|----------|
| session_manager.py | 0% | 90% | 30 | HIGH |
| protocol_engine.py | 0% | 85% | 40 | HIGH |
| db_manager.py | 49% | 90% | 30 | HIGH |
| protocol_line.py | 47% | 85% | 20 | MEDIUM |
| **TOTAL** | **~25%** | **~88%** | **120** | **HIGH** |

---

## Phase 3: Hardware Controller Testing (HIGH PRIORITY)

**Timeline:** Week 5-6
**Target:** 85% coverage on all hardware modules
**Estimated Effort:** 120-150 test cases

### 3.1 Expand MockHardwareBase Usage

**Current Status:** MockHardwareBase exists in `tests/mocks/` but underutilized

**Strategy:** Create comprehensive mocks for all hardware controllers

```python
# tests/mocks/mock_camera_controller.py (EXPAND EXISTING)
class MockCameraController(MockHardwareBase):
    def __init__(self):
        super().__init__(
            connection_signal=self.connection_changed,
            error_signal=self.error_occurred
        )
        self.is_streaming = False
        self.exposure_time = 50000  # μs
        self.gain = 0.0  # dB

    def start_streaming(self):
        """Mock streaming with frame generation."""
        self.is_streaming = True
        self.connection_changed.emit(True)
```

---

### 3.2 Camera Controller Testing

**File:** `tests/test_hardware/test_camera_controller.py` (NEW)
**Target Module:** `src/hardware/camera_controller.py` (currently 0% coverage)

**Test Cases:**

```python
def test_camera_connect_success():
    """Test camera connection with VmbPy mock."""

def test_camera_start_streaming_emits_frames():
    """Verify frame emission at configured FPS."""

def test_exposure_control_feedback_loop():
    """Test exposure setting with hardware feedback (RLock pattern)."""

def test_gain_control_feedback_loop():
    """Test gain setting with hardware feedback."""

def test_camera_disconnect_during_streaming():
    """Verify graceful handling of mid-stream disconnect."""

def test_frame_processing_qpixmap_conversion():
    """Test QPixmap conversion (QImage memory lifetime fix from LESSONS_LEARNED #1)."""

def test_camera_thread_safety_concurrent_controls():
    """Test concurrent exposure/gain changes from multiple threads."""
```

**Expected Coverage:** 0% → 85% (587 statements, ~500 new coverage)

---

### 3.3 Laser Controller Testing

**File:** `tests/test_hardware/test_laser_controller.py` (NEW)
**Target Module:** `src/hardware/laser_controller.py` (currently 0% coverage)

**Test Cases:**

```python
def test_laser_connect_to_com10():
    """Test serial connection to Arroyo 6300 on COM10."""

def test_set_laser_power_within_limits():
    """Verify power setting respects 0-10W range."""

def test_set_laser_power_exceeds_max_blocked():
    """Verify power > max_power is rejected."""

def test_laser_power_ramping():
    """Test gradual power increase (0 → 5W over 2 seconds)."""

def test_laser_serial_timeout_handling():
    """Test recovery from serial communication timeout."""

def test_laser_state_tracking():
    """Verify is_enabled and current_power tracking."""
```

**Expected Coverage:** 0% → 85% (227 statements)

---

### 3.4 TEC, Actuator, GPIO Controller Testing

**Files:**
- `tests/test_hardware/test_tec_controller.py` (NEW)
- `tests/test_hardware/test_actuator_controller.py` (EXPAND - fix import errors)
- `tests/test_hardware/test_gpio_controller.py` (NEW)

**Expected Coverage:** 0% → 85% for each (860 statements total)

---

### Phase 3 Summary

| Module | Statements | Current | Target | New Tests |
|--------|------------|---------|--------|-----------|
| camera_controller.py | 587 | 0% | 85% | 40 |
| laser_controller.py | 227 | 0% | 85% | 25 |
| tec_controller.py | 226 | 0% | 85% | 25 |
| actuator_controller.py | 288 | 0% | 85% | 30 |
| gpio_controller.py | 346 | 0% | 85% | 30 |
| **TOTAL** | **1,674** | **0%** | **85%** | **150** |

---

## Phase 4: UI Component Testing (MEDIUM PRIORITY)

**Timeline:** Week 7-9
**Target:** 70% coverage on UI widgets and main window
**Estimated Effort:** 100-120 test cases

### 4.1 MainWindow Testing

**File:** `tests/test_ui/test_main_window.py` (NEW)
**Target Module:** `src/ui/main_window.py` (currently 0% coverage)

**Test Cases:**

```python
def test_main_window_initialization(qtbot):
    """Test MainWindow initializes all widgets without errors."""
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.isVisible()

def test_hardware_controllers_injected_to_widgets():
    """Verify dependency injection pattern (CLAUDE.md #Dependency Injection)."""
    window = MainWindow()
    assert window.camera_live_view.camera_controller is window.camera_controller
    assert window.laser_widget.controller is window.laser_controller

def test_emergency_stop_button_triggers_safety_manager():
    """Test E-Stop button click handler."""
    window = MainWindow()
    qtbot.mouseClick(window.emergency_stop_button, Qt.LeftButton)
    # Assert: safety_manager.trigger_emergency_stop() called

def test_tab_switching():
    """Test switching between Hardware, Treatment, Protocol tabs."""
    window = MainWindow()
    window.tab_widget.setCurrentIndex(1)  # Treatment tab
    assert window.tab_widget.currentIndex() == 1
```

**Expected Coverage:** 0% → 70% (748 statements, ~520 new coverage)

---

### 4.2 Critical Widget Testing

**Focus Widgets (highest usage):**
- `tests/test_ui/test_camera_widget.py` (NEW) - 587 statements
- `tests/test_ui/test_laser_widget.py` (NEW) - 227 statements
- `tests/test_ui/test_safety_widget.py` (NEW) - 164 statements
- `tests/test_ui/test_subject_widget.py` (NEW) - 228 statements

**Test Pattern:**

```python
def test_widget_initialization(qtbot):
    """Test widget initializes without errors."""

def test_widget_signal_slot_connections():
    """Verify all connections established (use signal_introspection.py from Task 4)."""

def test_widget_updates_on_controller_signal():
    """Test reactive UI updates when hardware state changes."""

def test_widget_user_interaction():
    """Test button clicks, slider changes, etc."""
```

**Expected Coverage:** 0% → 70% per widget (~700 statements total)

---

### Phase 4 Summary

| Component | Statements | Target Coverage | New Tests |
|-----------|------------|-----------------|-----------|
| main_window.py | 748 | 70% | 30 |
| Critical Widgets | 1,206 | 70% | 60 |
| Other Widgets | 2,000+ | 50% | 30 |
| **TOTAL** | **~4,000** | **~65%** | **120** |

---

## Phase 5: Configuration & Utilities (LOWER PRIORITY)

**Timeline:** Week 10-11
**Target:** 60% coverage on configuration and utility modules
**Estimated Effort:** 40-60 test cases

### 5.1 Configuration Testing

**File:** `tests/test_config/test_config_loader.py` (NEW)
**Target Module:** `src/config/config_loader.py` (currently 0% coverage)

**Test Cases:**

```python
def test_load_config_valid_yaml():
    """Test loading valid config.yaml."""

def test_load_config_invalid_yaml_syntax():
    """Test error handling for malformed YAML."""

def test_load_config_missing_required_fields():
    """Test Pydantic validation errors."""

def test_load_config_out_of_range_values():
    """Test hardware parameter validation (e.g., laser_power > 10W)."""
```

**Expected Coverage:** 0% → 80% (73 statements)

---

### 5.2 Utility Module Testing

**Files:**
- `tests/test_utils/test_signal_introspection.py` (ALREADY EXISTS - 18 tests, 100% coverage ✅)
- `tests/test_utils/test_connection_parser.py` (ALREADY EXISTS - 22 tests, 100% coverage ✅)

**Status:** Utility modules created in Task 4 already have excellent test coverage!

---

### Phase 5 Summary

| Module | Statements | Target | New Tests |
|--------|------------|--------|-----------|
| config_loader.py | 73 | 80% | 15 |
| models.py (config) | 222 | 60% | 25 |
| **TOTAL** | **295** | **~68%** | **40** |

**Note:** Signal introspection and connection parser utilities already at 100% coverage from Task 4.

---

## Implementation Timeline

### Week 1-2: Phase 1 - Safety-Critical (IMMEDIATE)
- [ ] Fix 9 failing tests
- [ ] Emergency stop tests (5 cases)
- [ ] GPIO interlock tests (6 cases)
- [ ] State machine tests (6 cases)
- [ ] Protocol safety tests (4 cases)
- **Milestone:** Safety-critical modules at 95%+ coverage

### Week 3-4: Phase 2 - Core Business Logic
- [ ] Session manager tests (30 cases)
- [ ] Protocol engine execution tests (40 cases)
- [ ] Database manager expansion (30 cases)
- [ ] Protocol line tests (20 cases)
- **Milestone:** Core business logic at 88%+ coverage

### Week 5-6: Phase 3 - Hardware Controllers
- [ ] Camera controller tests (40 cases)
- [ ] Laser controller tests (25 cases)
- [ ] TEC controller tests (25 cases)
- [ ] Actuator controller tests (30 cases)
- [ ] GPIO controller tests (30 cases)
- **Milestone:** Hardware controllers at 85%+ coverage

### Week 7-9: Phase 4 - UI Components
- [ ] MainWindow tests (30 cases)
- [ ] Critical widget tests (60 cases)
- [ ] Other widget tests (30 cases)
- **Milestone:** UI components at 65%+ coverage

### Week 10-11: Phase 5 - Configuration & Utilities
- [ ] Configuration loader tests (15 cases)
- [ ] Configuration model tests (25 cases)
- **Milestone:** Configuration at 68%+ coverage

### Week 12: Final Validation
- [ ] Run full regression test suite
- [ ] Generate final coverage report
- [ ] Document coverage achievements
- [ ] Prepare for FDA validation documentation

---

## Test Infrastructure Improvements

### Required Before Starting

1. **Fix Environment Issues:**
   - Install missing dependency: `pyfirmata2`
   - Fix actuator test imports (ModuleNotFoundError: src)
   - Clean up duplicate test files (test_safety_manager.py)
   - Fix COM port mocking for hardware tests

2. **pytest-qt Integration:**
   - Expand use of `qtbot` fixture for widget testing
   - Add `QSignalSpy` usage examples
   - Document widget testing patterns

3. **Mock Infrastructure:**
   - Expand MockHardwareBase for all controllers
   - Create MockHardwareFactory for test setup
   - Document mock usage patterns

---

## Success Metrics

### Coverage Targets

| Category | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Final Target |
|----------|---------|---------|---------|---------|---------|---------|--------------|
| **Safety-Critical** | 0% | 95% | 95% | 95% | 95% | 95% | **100%** |
| **Core Logic** | 33% | 35% | 88% | 88% | 88% | 88% | **95%** |
| **Hardware** | 0% | 0% | 0% | 85% | 85% | 85% | **85%** |
| **UI** | 0% | 0% | 0% | 0% | 65% | 65% | **70%** |
| **Config/Utils** | 0% | 0% | 0% | 0% | 0% | 68% | **60%** |
| **OVERALL** | **9%** | **28%** | **42%** | **63%** | **73%** | **80%** | **85%** |

### Quality Metrics

- **All safety-critical code:** 100% statement + branch coverage
- **Zero failing tests:** Fix all 9 current failures + maintain 100% pass rate
- **Thread safety validation:** All hardware controllers tested with concurrent access
- **Performance tests:** Frame processing, protocol execution timing
- **Integration tests:** End-to-end treatment workflow

---

## Risk Mitigation

### High-Risk Areas Requiring Special Attention

1. **Hardware Communication:**
   - Serial port mocking may not catch all real hardware issues
   - Plan for hardware-in-the-loop (HIL) testing before clinical trials

2. **Threading/Concurrency:**
   - Difficult to test all race conditions
   - Use ThreadSanitizer or similar tools for validation

3. **UI Testing:**
   - pytest-qt may not catch all visual/layout issues
   - Plan for manual UI testing alongside automated tests

4. **Real-Time Requirements:**
   - Test timing constraints (e.g., emergency stop < 10ms)
   - Use time mocking carefully to avoid false confidence

---

## FDA Validation Considerations

### IEC 62304 Level C Requirements

**Required Test Documentation:**
- Test plan with traceability matrix (requirements → tests)
- Test case specifications with expected results
- Test execution records with pass/fail status
- Coverage analysis reports (statement + branch)
- Anomaly reports for any test failures

**TOSCA Roadmap Compliance:**
- ✅ This roadmap provides test plan framework
- ✅ Phase 1 addresses safety-critical requirements (100% coverage)
- ✅ Coverage targets align with IEC 62304 Level C
- ⚠️ Traceability matrix still needed (requirements → tests)
- ⚠️ Test case specifications need formal review

---

## Ongoing Maintenance

### After Achieving Target Coverage

1. **Coverage Monitoring:**
   - Add pytest coverage threshold check to CI/CD
   - Require 80% coverage for all new code
   - Block PRs that decrease coverage

2. **Regression Testing:**
   - Run full test suite on every commit
   - Automated nightly builds with coverage reports
   - Monthly coverage trend analysis

3. **Test Maintenance:**
   - Update tests when requirements change
   - Retire tests for removed features
   - Refactor tests to match code evolution

---

## Quick Start Guide

### Immediate Next Steps (Week 1)

1. **Fix Failing Tests:**
   ```bash
   # Install missing dependency
   pip install pyfirmata2

   # Fix session manager tests
   pytest tests/test_core/test_session_manager.py -v

   # Fix vacuum tests
   pytest tests/test_database/test_db_vacuum.py -v
   ```

2. **Create Emergency Stop Tests:**
   ```bash
   # Create new test file
   touch tests/test_safety/test_emergency_stop.py

   # Implement 5 critical test cases
   # Run tests: pytest tests/test_safety/test_emergency_stop.py -v
   ```

3. **Verify Coverage Improvement:**
   ```bash
   # Run coverage analysis
   pytest --cov=src/core/safety --cov-report=term-missing

   # Target: safety.py coverage > 20% after emergency stop tests
   ```

---

## Resources and References

### Documentation
- `docs/architecture/safety_code_review.md` - Safety module analysis (Task 7)
- `reports/test_coverage_analysis.md` - Detailed coverage breakdown (Task 6.2)
- `tests/mocks/README.md` - Mock infrastructure documentation
- `LESSONS_LEARNED.md` - Critical bug patterns to test for

### Test Patterns
- `tests/test_core/test_event_logger.py` - Well-tested module example (81% coverage)
- `tests/test_utils/test_signal_introspection.py` - 100% coverage example
- `tests/test_database/test_db_manager.py` - Partial coverage example (49%)

### FDA Guidance
- IEC 62304:2006 - Medical device software lifecycle processes
- FDA Guidance: "General Principles of Software Validation"
- FDA Guidance: "Cybersecurity in Medical Devices"

---

**Roadmap Version:** 1.0
**Next Review:** After Phase 1 completion (Week 2)
**Status:** APPROVED FOR IMPLEMENTATION
