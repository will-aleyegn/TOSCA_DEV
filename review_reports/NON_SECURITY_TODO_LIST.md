# TOSCA Non-Security TODO List

**Generated From:** Comprehensive Code Review (2025-10-30)
**Scope:** Code quality, architecture, performance, testing, and documentation improvements
**Excludes:** Security-related tasks (see `04_ACTION_PLAN_RECOMMENDATIONS.md` for security roadmap)

---

## Priority Classification

- **P0 (CRITICAL):** Blocking issues for production (none in non-security category)
- **P1 (HIGH):** Must complete before Phase 6 pre-clinical validation
- **P2 (MEDIUM):** Should complete during Phase 6 or Phase 7
- **P3 (LOW):** Nice-to-have improvements, can defer to Phase 8+

---

## Table of Contents

1. [Code Quality Improvements](#1-code-quality-improvements)
2. [Architecture Enhancements](#2-architecture-enhancements)
3. [Testing & Validation](#3-testing--validation)
4. [Performance Optimizations](#4-performance-optimizations)
5. [Documentation & Compliance](#5-documentation--compliance)
6. [Developer Experience](#6-developer-experience)

---

## 1. Code Quality Improvements

### P3-CQ-001: Formalize LaserController Inheritance

**Priority:** P3 (Low)
**Effort:** 2 hours
**Module:** `src/hardware/laser_controller.py`

**Current State:**
```python
# laser_controller.py:28
class LaserController(QObject):  # ← Duck typing (works but not formalized)
    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()
        # ... implements compatible interface
```

**Target State:**
```python
from hardware.hardware_controller_base import HardwareControllerBase

class LaserController(HardwareControllerBase):
    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__(event_logger)
        self._lock = threading.RLock()
        # ... rest unchanged
```

**Benefits:**
- Type checker validation (MyPy)
- IDE autocomplete for abstract methods
- Explicit contract documentation
- Consistency with other controllers

**Implementation Steps:**
1. Add import: `from hardware.hardware_controller_base import HardwareControllerBase`
2. Change class declaration: `class LaserController(HardwareControllerBase):`
3. Update `__init__` to call `super().__init__(event_logger)`
4. Run MyPy: `mypy src/hardware/laser_controller.py`
5. Run unit tests: `pytest tests/hardware/test_laser_controller.py`

**Files Modified:**
- `src/hardware/laser_controller.py`

**Acceptance Criteria:**
- [ ] LaserController explicitly inherits from HardwareControllerBase
- [ ] All existing tests pass
- [ ] MyPy reports no new type errors

---

### P3-CQ-002: Refactor Protocol Engine Action Dispatch

**Priority:** P3 (Low)
**Effort:** 1 day
**Module:** `src/core/protocol_engine.py`

**Current State:**
```python
# protocol_engine.py:180-250 (Cyclomatic Complexity: 22)
async def _execute_action_internal(self, action: ProtocolAction):
    if isinstance(action.parameters, SetLaserPowerParams):
        # ... 15 lines
    elif isinstance(action.parameters, RampLaserPowerParams):
        # ... 20 lines
    elif isinstance(action.parameters, MoveActuatorParams):
        # ... 12 lines
    # ... 9 more elif branches (12 action types total)
```

**Target State (Strategy Pattern):**
```python
# protocol_engine.py - Registry-based dispatch
class ActionExecutor(ABC):
    @abstractmethod
    async def execute(self, params: ActionParameters, context: ProtocolContext):
        pass

class SetLaserPowerExecutor(ActionExecutor):
    async def execute(self, params: SetLaserPowerParams, context: ProtocolContext):
        await context.laser_controller.set_power_async(params.power_watts)

class ProtocolEngine:
    def __init__(self, laser_controller, actuator_controller, ...):
        # ... existing init
        self.executors: dict[type, ActionExecutor] = {
            SetLaserPowerParams: SetLaserPowerExecutor(),
            RampLaserPowerParams: RampLaserPowerExecutor(),
            MoveActuatorParams: MoveActuatorExecutor(),
            # ... register all 12 action types
        }

    async def _execute_action_internal(self, action: ProtocolAction):
        executor_type = type(action.parameters)
        executor = self.executors.get(executor_type)

        if not executor:
            raise ValueError(f"No executor registered for {executor_type}")

        await executor.execute(action.parameters, self._get_context())
```

**Benefits:**
- Cyclomatic complexity reduced from 22 → 3
- Easy to add new action types (Open/Closed Principle)
- Each executor is independently testable
- Clear separation of concerns

**Implementation Steps:**
1. Create `src/core/protocol_executors/` directory
2. Create base class: `src/core/protocol_executors/base.py`
3. Extract each action type to separate executor:
   - `set_laser_power_executor.py`
   - `ramp_laser_power_executor.py`
   - `move_actuator_executor.py`
   - ... (12 total)
4. Update `ProtocolEngine.__init__()` to register executors
5. Replace `_execute_action_internal()` with registry lookup
6. Run all protocol tests: `pytest tests/protocol/`
7. Verify integration tests still pass

**Files Created:**
- `src/core/protocol_executors/base.py`
- `src/core/protocol_executors/set_laser_power_executor.py`
- `src/core/protocol_executors/ramp_laser_power_executor.py`
- ... (12 executor files)

**Files Modified:**
- `src/core/protocol_engine.py`

**Acceptance Criteria:**
- [ ] Cyclomatic complexity of `_execute_action_internal()` < 5
- [ ] All 12 action types work identically to before
- [ ] New action types can be added without modifying ProtocolEngine
- [ ] All existing protocol tests pass

---

### P3-CQ-003: Complete Type Hint Coverage

**Priority:** P3 (Low)
**Effort:** 2 hours
**Module:** Various (5% of codebase)

**Current Coverage:** 95%
**Target Coverage:** 100%

**Missing Type Hints:**

1. **`gpio_controller.py:788`**
   ```python
   # BEFORE
   def _calculate_vibration_magnitude(self, ax, ay, az):
       return math.sqrt(ax**2 + ay**2 + az**2)

   # AFTER
   def _calculate_vibration_magnitude(self, ax: float, ay: float, az: float) -> float:
       return math.sqrt(ax**2 + ay**2 + az**2)
   ```

2. **`camera_controller.py:315`** (Lambda callback - acceptable as-is)
   ```python
   # Lambda type hints are inferred from signal, no change needed
   self.camera.queue_frame(lambda frame: self._on_frame(frame))
   ```

3. **2 other private methods** (grep for functions without `->` return type)

**Implementation Steps:**
1. Find all functions missing type hints:
   ```bash
   grep -rn "def [_a-z].*(" src/ | grep -v " -> " | grep -v "@"
   ```
2. Add type hints to each function
3. Run MyPy with strict mode:
   ```bash
   mypy --strict src/
   ```
4. Fix any new type errors revealed

**Files Modified:**
- `src/hardware/gpio_controller.py`
- 2-3 other files (TBD based on grep results)

**Acceptance Criteria:**
- [ ] 100% type hint coverage on public functions
- [ ] 95%+ coverage on private functions
- [ ] MyPy strict mode passes with no errors

---

### P3-CQ-004: Split gpio_controller.py into Modules

**Priority:** P3 (Low)
**Effort:** 4 hours
**Module:** `src/hardware/gpio_controller.py`

**Current State:**
- Single file: 850 lines
- Maintainability Index: 68 (B grade - acceptable but could improve)
- Responsibilities:
  - GPIO command sending/receiving
  - Vibration sensor monitoring
  - Photodiode power monitoring
  - Motor control
  - Interlock status aggregation

**Target State (Modular):**
```
src/hardware/gpio/
├── __init__.py
├── gpio_controller.py (main coordinator, 200 lines)
├── vibration_monitor.py (150 lines)
├── photodiode_monitor.py (100 lines)
├── motor_controller.py (120 lines)
└── interlock_manager.py (280 lines)
```

**Refactored Architecture:**
```python
# gpio/gpio_controller.py
class GPIOController(HardwareControllerBase):
    def __init__(self, event_logger=None):
        super().__init__(event_logger)
        self._lock = threading.RLock()

        # Delegate to specialized components
        self.vibration_monitor = VibrationMonitor(self._send_command, event_logger)
        self.photodiode_monitor = PhotodiodeMonitor(self._send_command, event_logger)
        self.motor_controller = MotorController(self._send_command, event_logger)
        self.interlock_manager = InterlockManager(
            self.vibration_monitor,
            self.photodiode_monitor,
            event_logger
        )

    def get_interlock_status(self) -> dict:
        return self.interlock_manager.get_status()

# gpio/vibration_monitor.py
class VibrationMonitor:
    def __init__(self, send_command_callback, event_logger):
        self.send_command = send_command_callback
        self.event_logger = event_logger
        self.vibration_consecutive_count = 0
        # ... vibration-specific state

    def read_vibration(self) -> tuple[float, float, float]:
        # Read accelerometer (ax, ay, az)
        response = self.send_command("VIBRATION?", "VIBRATION:")
        return self._parse_vibration_response(response)

    def is_vibration_detected(self) -> bool:
        # Debouncing logic (3 consecutive readings)
        # ...
```

**Benefits:**
- Improved maintainability (smaller files)
- Single Responsibility Principle
- Easier unit testing (test each monitor independently)
- Better code organization

**Implementation Steps:**
1. Create `src/hardware/gpio/` directory
2. Extract VibrationMonitor class:
   - Lines 767-784 → `vibration_monitor.py`
   - Add unit tests: `tests/gpio/test_vibration_monitor.py`
3. Extract PhotodiodeMonitor class:
   - Lines 790-800 → `photodiode_monitor.py`
   - Add unit tests: `tests/gpio/test_photodiode_monitor.py`
4. Extract MotorController class:
   - Lines 474-494 → `motor_controller.py`
   - Add unit tests: `tests/gpio/test_motor_controller.py`
5. Extract InterlockManager class:
   - Lines 640-725 → `interlock_manager.py`
   - Add unit tests: `tests/gpio/test_interlock_manager.py`
6. Update imports in `main_window.py`
7. Run all GPIO tests: `pytest tests/gpio/`

**Files Created:**
- `src/hardware/gpio/__init__.py`
- `src/hardware/gpio/gpio_controller.py` (refactored)
- `src/hardware/gpio/vibration_monitor.py`
- `src/hardware/gpio/photodiode_monitor.py`
- `src/hardware/gpio/motor_controller.py`
- `src/hardware/gpio/interlock_manager.py`

**Files Removed:**
- `src/hardware/gpio_controller.py` (replaced by modular structure)

**Acceptance Criteria:**
- [ ] gpio_controller.py reduced to <300 lines
- [ ] Each component <200 lines
- [ ] All existing functionality preserved
- [ ] All GPIO tests pass
- [ ] Integration tests pass

---

## 2. Architecture Enhancements

### P2-ARCH-001: Implement 4-State Safety Model

**Priority:** P2 (Medium)
**Effort:** 3 days
**Module:** `src/core/safety.py`

**Current State (3 states):**
```python
class SafetyState(Enum):
    SAFE = "SAFE"              # All interlocks satisfied
    UNSAFE = "UNSAFE"          # One or more interlocks failed
    EMERGENCY_STOP = "EMERGENCY_STOP"  # Manual E-stop activated
```

**Target State (5 states):**
```python
class SafetyState(Enum):
    SAFE = "SAFE"              # Ready, all interlocks pass, laser power = 0
    ARMED = "ARMED"            # Laser power set >0, awaiting footpedal
    TREATING = "TREATING"      # Active laser output (footpedal pressed)
    UNSAFE = "UNSAFE"          # Interlock failure, recoverable
    EMERGENCY_STOP = "EMERGENCY_STOP"  # Manual stop, requires supervisor reset
```

**Documented Architecture (from `docs/architecture/03_safety_system.md`):**
```
SAFE → ARMED → TREATING → UNSAFE/FAULT → EMERGENCY_STOP
```

**Benefits:**
1. **Finer-grained audit trail:** Distinguish "armed and waiting" from "actively treating"
2. **Better UI feedback:** Can show "Armed - awaiting footpedal" state
3. **Documentation alignment:** Matches architectural diagrams
4. **Regulatory compliance:** More detailed event logging for FDA

**State Transition Logic:**
```python
class SafetyManager:
    def _update_safety_state(self) -> None:
        # Emergency stop has highest priority
        if self.emergency_stop_active:
            new_state = SafetyState.EMERGENCY_STOP

        # Check interlocks
        elif not self.gpio_interlock_ok or not self.session_valid or not self.power_limit_ok:
            new_state = SafetyState.UNSAFE

        # If footpedal pressed AND laser power >0 → TREATING
        elif self.footpedal_pressed and self.laser_power_setpoint > 0:
            new_state = SafetyState.TREATING

        # If laser power >0 but footpedal NOT pressed → ARMED
        elif self.laser_power_setpoint > 0:
            new_state = SafetyState.ARMED

        # Otherwise → SAFE
        else:
            new_state = SafetyState.SAFE

        # Emit state change
        if new_state != self.state:
            logger.info(f"Safety state: {self.state.value} → {new_state.value}")
            self.state = new_state
            self.safety_state_changed.emit(new_state)
```

**Implementation Steps:**

**Day 1: Add States + Transition Logic**
1. Add `ARMED` and `TREATING` to SafetyState enum
2. Add `self.laser_power_setpoint` to SafetyManager (tracked from LaserController)
3. Add `self.footpedal_pressed` to SafetyManager (tracked from GPIOController)
4. Update `_update_safety_state()` with new transition logic
5. Add unit tests for all state transitions

**Day 2: UI Integration**
1. Update `src/ui/widgets/safety_widget.py` to display 5 states
2. Add visual indicators:
   - SAFE: Green
   - ARMED: Yellow (⚠️ icon)
   - TREATING: Red (laser active icon)
   - UNSAFE: Orange (warning icon)
   - EMERGENCY_STOP: Red (stop icon)
3. Update status bar in `main_window.py`

**Day 3: Testing + Documentation**
1. Write comprehensive state machine tests:
   - SAFE → ARMED (when laser power set)
   - ARMED → TREATING (when footpedal pressed)
   - TREATING → ARMED (when footpedal released)
   - TREATING → UNSAFE (when interlock fails mid-treatment)
   - Any state → EMERGENCY_STOP (when E-stop pressed)
2. Update `docs/architecture/03_safety_system.md` with implementation details
3. Update CLAUDE.md to reflect 5-state model

**Files Modified:**
- `src/core/safety.py`
- `src/ui/widgets/safety_widget.py`
- `src/ui/main_window.py` (status bar)
- `docs/architecture/03_safety_system.md`
- `CLAUDE.md`

**Files Created:**
- `tests/core/test_safety_state_machine.py`

**Acceptance Criteria:**
- [ ] All 5 states implemented with correct transitions
- [ ] UI displays current state accurately
- [ ] Audit trail logs state transitions with timestamps
- [ ] 100% test coverage of state machine logic
- [ ] Documentation updated to match implementation

---

### P2-ARCH-002: Document Asyncio Event Loop Integration

**Priority:** P2 (Medium)
**Effort:** 1 day (documentation + validation)
**Module:** `src/core/protocol_engine.py`, `docs/architecture/10_concurrency_model.md`

**Current State:**
- Protocol engine uses `async/await` for protocol execution
- No explicit QEventLoop integration with asyncio visible
- Unclear if using `asyncio.run()` or `qasync` library

**Investigation Needed:**
1. How is async protocol execution triggered from GUI?
2. Is there a running asyncio event loop?
3. Does it integrate with Qt event loop?
4. Are there any blocking calls that could freeze the GUI?

**Implementation Steps:**

**Step 1: Investigate Current Implementation**
```bash
# Search for asyncio usage
grep -rn "asyncio.run\|asyncio.create_task\|asyncio.get_event_loop" src/

# Search for qasync usage
grep -rn "qasync\|QEventLoop" src/

# Check if qasync is in dependencies
grep "qasync" requirements.txt pyproject.toml
```

**Step 2: Document Findings**
Create comprehensive documentation in `docs/architecture/10_concurrency_model.md`:

```markdown
# TOSCA Concurrency Model

## Async Protocol Execution

### Current Implementation

The ProtocolEngine uses Python's `async/await` syntax for protocol execution:

```python
# protocol_engine.py
async def execute_protocol(self, protocol: Protocol) -> tuple[bool, str]:
    for action in protocol.actions:
        await self._execute_action_internal(action)
        await self._pause_event.wait()  # Async pause point
```

### Event Loop Integration

**Option A: If using asyncio.run():**
```python
# CURRENT (if found)
# Called from GUI thread
def start_protocol(self):
    result = asyncio.run(self.protocol_engine.execute_protocol(protocol))
    # WARNING: This blocks GUI thread!
```

**Recommended: qasync Integration**
```python
# RECOMMENDED
import qasync

# main.py
app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

# protocol_engine.py
# Called from GUI thread (non-blocking)
def start_protocol(self):
    task = asyncio.create_task(self.protocol_engine.execute_protocol(protocol))
    # GUI remains responsive!
```

### Benefits of qasync
1. Non-blocking async operations in GUI
2. Proper Qt signal/slot integration
3. Protocol execution doesn't freeze UI
4. Can pause/resume without blocking

### Migration Plan (if needed)
1. Install qasync: `pip install qasync`
2. Modify main.py to use QEventLoop
3. Convert asyncio.run() calls to asyncio.create_task()
4. Test pause/resume functionality
```

**Step 3: Validate Performance**
- Test protocol execution with/without qasync
- Measure GUI responsiveness during long protocols
- Verify pause/resume works correctly

**Step 4: Add to CLAUDE.md**
Update project context with event loop strategy

**Files Modified:**
- `docs/architecture/10_concurrency_model.md`
- `CLAUDE.md`
- Potentially `src/main.py` (if qasync needed)
- Potentially `requirements.txt` (if qasync needed)

**Acceptance Criteria:**
- [ ] Event loop integration strategy documented
- [ ] Known limitations documented (if any)
- [ ] Migration plan provided (if needed)
- [ ] GUI responsiveness validated during protocol execution

---

## 3. Testing & Validation

### P1-TEST-001: Safety State Machine Unit Tests

**Priority:** P1 (HIGH)
**Effort:** 5 days
**Module:** `tests/core/test_safety_manager.py` (new)

**Current Coverage:** 0% (file doesn't exist)
**Target Coverage:** 100% of `src/core/safety.py`

**Test Categories:**

#### 3.1 State Transition Tests

```python
# tests/core/test_safety_manager.py
import pytest
from src.core.safety import SafetyManager, SafetyState
from tests.mocks.mock_gpio_controller import MockGPIOController
from tests.mocks.mock_event_logger import MockEventLogger

class TestSafetyStateTransitions:
    """Test all valid and invalid state transitions."""

    def test_initial_state_is_unsafe(self):
        """System starts in UNSAFE state (fail-safe default)."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )
        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_transition_to_safe_when_all_conditions_met(self):
        """Transition to SAFE when all interlocks pass."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        assert safety.state == SafetyState.SAFE
        assert safety.laser_enable_permitted is True

    def test_transition_to_unsafe_when_gpio_fails(self):
        """Transition to UNSAFE when GPIO interlock fails."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)
        assert safety.state == SafetyState.SAFE

        # GPIO interlock fails (footpedal released)
        safety.set_gpio_interlock_status(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_emergency_stop_has_highest_priority(self):
        """Emergency stop overrides all other states."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)
        assert safety.state == SafetyState.SAFE

        # Trigger emergency stop
        safety.trigger_emergency_stop()

        assert safety.state == SafetyState.EMERGENCY_STOP
        assert safety.laser_enable_permitted is False
        assert safety.emergency_stop_active is True

    def test_cannot_exit_emergency_stop_without_reset(self):
        """Once in E-STOP, cannot exit without explicit reset."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        safety.trigger_emergency_stop()
        assert safety.state == SafetyState.EMERGENCY_STOP

        # Try to satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Should REMAIN in E-STOP
        assert safety.state == SafetyState.EMERGENCY_STOP
        assert safety.emergency_stop_active is True

    def test_reset_emergency_stop_requires_all_conditions(self):
        """Resetting E-STOP requires all interlocks satisfied."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        safety.trigger_emergency_stop()

        # Try to reset WITHOUT satisfying conditions
        with pytest.raises(RuntimeError, match="Cannot reset.*interlocks"):
            safety.reset_emergency_stop()

        # Satisfy all conditions
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Now reset should succeed
        safety.reset_emergency_stop()
        assert safety.state == SafetyState.SAFE
        assert safety.emergency_stop_active is False
```

#### 3.2 Interlock Failure Tests

```python
class TestInterlockFailures:
    """Test individual interlock failures."""

    def test_footpedal_release_disables_laser(self):
        """Footpedal release transitions to UNSAFE."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state with all interlocks OK
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Simulate footpedal release (GPIO interlock fail)
        safety.set_gpio_interlock_status(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_vibration_sensor_failure_disables_laser(self):
        """Vibration sensor failure (smoothing device stopped)."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Vibration sensor detects smoothing device stopped
        safety.set_gpio_interlock_status(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_session_invalidation_disables_laser(self):
        """Session end or invalidation transitions to UNSAFE."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Session ended
        safety.set_session_valid(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False

    def test_power_limit_exceeded_disables_laser(self):
        """Power limit violation transitions to UNSAFE."""
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=MockEventLogger()
        )

        # Start in SAFE state
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Attempt to set laser power above limit
        safety.set_power_limit_ok(False)

        assert safety.state == SafetyState.UNSAFE
        assert safety.laser_enable_permitted is False
```

#### 3.3 Selective Shutdown Tests

```python
class TestSelectiveShutdown:
    """Verify selective shutdown policy (laser only, preserve monitoring)."""

    def test_emergency_stop_preserves_monitoring(self):
        """Emergency stop disables laser only, not monitoring."""
        gpio_controller = MockGPIOController()
        gpio_controller.connect("COM4")  # Connected

        safety = SafetyManager(
            gpio_controller=gpio_controller,
            event_logger=MockEventLogger()
        )

        # Verify GPIO controller connected and polling
        assert gpio_controller.is_connected is True

        # Trigger emergency stop
        safety.trigger_emergency_stop()

        # GPIO controller should STILL be active (selective shutdown)
        assert gpio_controller.is_connected is True
        assert gpio_controller.is_polling is True

        # But laser is disabled
        assert safety.laser_enable_permitted is False
```

#### 3.4 Event Logging Tests

```python
class TestSafetyEventLogging:
    """Verify all safety state changes are logged."""

    def test_state_transitions_logged(self):
        """All state transitions logged to event logger."""
        event_logger = MockEventLogger()
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=event_logger
        )

        # Transition UNSAFE → SAFE
        safety.set_gpio_interlock_status(True)
        safety.set_session_valid(True)
        safety.set_power_limit_ok(True)

        # Check event logged
        assert len(event_logger.events) >= 1
        last_event = event_logger.events[-1]
        assert last_event["event_type"] == "safety_state_changed"
        assert last_event["details"]["old_state"] == "UNSAFE"
        assert last_event["details"]["new_state"] == "SAFE"

    def test_emergency_stop_logged_as_critical(self):
        """Emergency stop logged with CRITICAL severity."""
        event_logger = MockEventLogger()
        safety = SafetyManager(
            gpio_controller=MockGPIOController(),
            event_logger=event_logger
        )

        safety.trigger_emergency_stop()

        # Find emergency stop event
        estop_events = [e for e in event_logger.events if e["event_type"] == "emergency_stop"]
        assert len(estop_events) == 1
        assert estop_events[0]["severity"] == "CRITICAL"
```

**Implementation Steps:**

**Day 1-2:** Write basic state transition tests (15 tests)
**Day 3:** Write interlock failure tests (10 tests)
**Day 4:** Write selective shutdown and event logging tests (8 tests)
**Day 5:** Achieve 100% coverage, fix any found bugs

**Files Created:**
- `tests/core/test_safety_manager.py`
- `tests/mocks/mock_safety_manager.py` (if needed for higher-level tests)

**Acceptance Criteria:**
- [ ] 100% line coverage of `src/core/safety.py`
- [ ] All state transitions tested
- [ ] All interlock failures tested
- [ ] Selective shutdown verified
- [ ] Event logging verified
- [ ] All tests pass

---

### P1-TEST-002: Protocol Engine Safety Tests

**Priority:** P1 (HIGH)
**Effort:** 3 days
**Module:** `tests/core/test_protocol_engine_safety.py` (new)

**Current Coverage:** Partial (basic protocol execution tested, safety integration not tested)
**Target:** Safety-critical paths 100% covered

**Test Scenarios:**

```python
# tests/core/test_protocol_engine_safety.py
import pytest
import asyncio
from src.core.protocol_engine import ProtocolEngine
from src.core.protocol import Protocol, ProtocolAction, SetLaserPowerParams, WaitParams
from tests.mocks.mock_laser_controller import MockLaserController
from tests.mocks.mock_safety_manager import MockSafetyManager

@pytest.mark.asyncio
async def test_protocol_halts_on_interlock_failure():
    """Protocol execution stops when interlock fails mid-execution."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    engine = ProtocolEngine(
        laser_controller=laser,
        actuator_controller=None,
        safety_manager=safety
    )

    # Create protocol with 3 actions
    protocol = Protocol(
        name="Test Protocol",
        actions=[
            ProtocolAction(
                type="set_laser_power",
                parameters=SetLaserPowerParams(power_watts=1.0)
            ),
            ProtocolAction(
                type="wait",
                parameters=WaitParams(duration_sec=2.0)
            ),
            ProtocolAction(
                type="set_laser_power",
                parameters=SetLaserPowerParams(power_watts=2.0)
            ),
        ]
    )

    # Start SAFE
    safety.set_gpio_interlock_status(True)
    safety.set_session_valid(True)
    safety.set_power_limit_ok(True)

    # Start protocol execution
    execution_task = asyncio.create_task(engine.execute_protocol(protocol))

    # Wait 1 second, then FAIL interlock (footpedal released)
    await asyncio.sleep(1.0)
    safety.set_gpio_interlock_status(False)

    # Protocol should halt
    success, message = await execution_task

    assert success is False
    assert "interlock" in message.lower() or "unsafe" in message.lower()
    assert engine.is_running is False

    # Laser should be disabled
    assert laser.output_enabled is False

@pytest.mark.asyncio
async def test_emergency_stop_during_protocol():
    """Emergency stop immediately halts protocol execution."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    engine = ProtocolEngine(
        laser_controller=laser,
        safety_manager=safety
    )

    # Long protocol (10 second wait)
    protocol = Protocol(
        name="Long Protocol",
        actions=[
            ProtocolAction(
                type="wait",
                parameters=WaitParams(duration_sec=10.0)
            )
        ]
    )

    # Start SAFE
    safety.set_gpio_interlock_status(True)
    safety.set_session_valid(True)

    # Start protocol execution
    start_time = asyncio.get_event_loop().time()
    execution_task = asyncio.create_task(engine.execute_protocol(protocol))

    # Wait 1 second, then trigger E-STOP
    await asyncio.sleep(1.0)
    safety.trigger_emergency_stop()

    # Protocol should halt IMMEDIATELY (within 100ms)
    success, message = await execution_task
    halt_time = asyncio.get_event_loop().time() - start_time

    assert success is False
    assert halt_time < 1.2  # Halted within 200ms of E-stop
    assert "emergency" in message.lower() or "stop" in message.lower()
    assert engine.is_running is False

@pytest.mark.asyncio
async def test_protocol_refuses_to_start_if_unsafe():
    """Protocol execution refuses to start if not in SAFE state."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    engine = ProtocolEngine(
        laser_controller=laser,
        safety_manager=safety
    )

    protocol = Protocol(
        name="Test Protocol",
        actions=[
            ProtocolAction(
                type="set_laser_power",
                parameters=SetLaserPowerParams(power_watts=1.0)
            )
        ]
    )

    # Start in UNSAFE state (GPIO interlocks not satisfied)
    safety.set_gpio_interlock_status(False)

    # Attempt to start protocol
    success, message = await engine.execute_protocol(protocol)

    assert success is False
    assert "safe" in message.lower() or "interlock" in message.lower()
    assert engine.is_running is False
    assert laser.output_enabled is False

@pytest.mark.asyncio
async def test_watchdog_timeout_halts_protocol():
    """Watchdog timeout during protocol execution halts safely."""
    laser = MockLaserController()
    safety = MockSafetyManager()
    watchdog = MockWatchdog(safety)
    engine = ProtocolEngine(
        laser_controller=laser,
        safety_manager=safety
    )

    protocol = Protocol(
        name="Long Protocol",
        actions=[
            ProtocolAction(
                type="wait",
                parameters=WaitParams(duration_sec=5.0)
            )
        ]
    )

    # Start SAFE
    safety.set_gpio_interlock_status(True)
    safety.set_session_valid(True)

    # Start protocol execution
    execution_task = asyncio.create_task(engine.execute_protocol(protocol))

    # Wait 2 seconds, then simulate watchdog timeout
    await asyncio.sleep(2.0)
    watchdog.simulate_timeout()  # Triggers emergency stop

    # Protocol should halt
    success, message = await execution_task

    assert success is False
    assert engine.is_running is False
    assert laser.output_enabled is False
```

**Implementation Steps:**

**Day 1:** Write interlock failure tests (5 tests)
**Day 2:** Write emergency stop tests (4 tests)
**Day 3:** Write protocol start validation tests (3 tests)

**Files Created:**
- `tests/core/test_protocol_engine_safety.py`
- `tests/mocks/mock_watchdog.py` (if needed)

**Acceptance Criteria:**
- [ ] All safety-critical paths in ProtocolEngine tested
- [ ] Protocol halts within 200ms of safety failure
- [ ] Protocol refuses to start if not in SAFE state
- [ ] Laser disabled immediately on any safety failure
- [ ] All tests pass

---

### P1-TEST-003: 72-Hour Soak Test

**Priority:** P1 (HIGH)
**Effort:** 3 days (setup + monitoring + analysis)
**Module:** `tests/integration/test_72hour_soak.py` (new)

**Objective:** Validate system stability under extended operation

**Test Setup:**

```python
# tests/integration/test_72hour_soak.py
import time
import psutil
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def test_72hour_continuous_operation():
    """
    Run system for 72 hours with simulated treatment sessions.

    Test Parameters:
    - Duration: 72 hours (259,200 seconds)
    - Session interval: 30 minutes
    - Total sessions: 144 (72 hours × 2 sessions/hour)
    - Protocol duration: 5-10 minutes (randomized)
    - Monitoring interval: 5 minutes

    Pass Criteria:
    - Sessions completed: ≥ 95% (137/144)
    - Error rate: < 5%
    - Memory growth: < 20%
    - No crashes
    - All safety interlocks responsive
    """
    duration_hours = 72
    session_interval_minutes = 30
    monitoring_interval_seconds = 300  # 5 minutes

    total_sessions_expected = int(duration_hours * 60 / session_interval_minutes)

    # Initial metrics
    process = psutil.Process()
    initial_memory_mb = process.memory_info().rss / 1024 / 1024
    initial_cpu_percent = process.cpu_percent(interval=1)

    logger.info(f"Starting 72-hour soak test")
    logger.info(f"Initial memory: {initial_memory_mb:.1f} MB")
    logger.info(f"Initial CPU: {initial_cpu_percent:.1f}%")
    logger.info(f"Expected sessions: {total_sessions_expected}")

    # Test state
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    sessions_completed = 0
    errors = []
    metrics_log = []

    next_session_time = start_time
    next_monitoring_time = start_time + monitoring_interval_seconds

    while time.time() < end_time:
        current_time = time.time()

        # Run session if it's time
        if current_time >= next_session_time:
            try:
                session_id = sessions_completed + 1
                logger.info(f"Starting session {session_id}/{total_sessions_expected}")

                # Create mock session
                session = create_mock_session(subject_code=f"SOAK_{session_id:03d}")

                # Execute protocol (5-10 minutes randomized)
                protocol_duration = execute_mock_protocol(session)

                # End session
                session.end()
                sessions_completed += 1

                logger.info(f"Session {session_id} completed ({protocol_duration:.1f}s)")

                # Schedule next session
                next_session_time = current_time + (session_interval_minutes * 60)

            except Exception as e:
                error_info = {
                    "time": current_time - start_time,
                    "session_id": sessions_completed + 1,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                errors.append(error_info)
                logger.error(f"Session {sessions_completed + 1} failed: {e}")

                # Schedule next session anyway
                next_session_time = current_time + (session_interval_minutes * 60)

        # Collect metrics if it's time
        if current_time >= next_monitoring_time:
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=1)
            memory_growth = ((memory_mb - initial_memory_mb) / initial_memory_mb) * 100

            metrics = {
                "elapsed_hours": (current_time - start_time) / 3600,
                "memory_mb": memory_mb,
                "memory_growth_percent": memory_growth,
                "cpu_percent": cpu_percent,
                "sessions_completed": sessions_completed,
                "errors_count": len(errors)
            }
            metrics_log.append(metrics)

            logger.info(
                f"Metrics at {metrics['elapsed_hours']:.1f}h: "
                f"Memory={memory_mb:.1f}MB ({memory_growth:+.1f}%), "
                f"CPU={cpu_percent:.1f}%, "
                f"Sessions={sessions_completed}/{total_sessions_expected}, "
                f"Errors={len(errors)}"
            )

            next_monitoring_time = current_time + monitoring_interval_seconds

        # Sleep briefly to avoid busy loop
        time.sleep(1)

    # Test complete - analyze results
    elapsed_time = time.time() - start_time
    final_memory_mb = process.memory_info().rss / 1024 / 1024
    memory_growth_percent = ((final_memory_mb - initial_memory_mb) / initial_memory_mb) * 100

    completion_rate = (sessions_completed / total_sessions_expected) * 100
    error_rate = (len(errors) / total_sessions_expected) * 100

    logger.info("=" * 80)
    logger.info("72-HOUR SOAK TEST COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Elapsed time: {elapsed_time / 3600:.1f} hours")
    logger.info(f"Sessions completed: {sessions_completed}/{total_sessions_expected} ({completion_rate:.1f}%)")
    logger.info(f"Errors: {len(errors)} ({error_rate:.1f}%)")
    logger.info(f"Initial memory: {initial_memory_mb:.1f} MB")
    logger.info(f"Final memory: {final_memory_mb:.1f} MB ({memory_growth_percent:+.1f}% growth)")
    logger.info("=" * 80)

    # Write detailed report
    write_soak_test_report(
        metrics_log=metrics_log,
        errors=errors,
        sessions_completed=sessions_completed,
        total_sessions_expected=total_sessions_expected
    )

    # Assertions
    assert sessions_completed >= total_sessions_expected * 0.95, \
        f"Only {completion_rate:.1f}% of sessions completed (≥95% required)"

    assert len(errors) < total_sessions_expected * 0.05, \
        f"Error rate {error_rate:.1f}% exceeds 5% threshold"

    assert memory_growth_percent < 20, \
        f"Memory grew by {memory_growth_percent:.1f}% (>20% indicates leak)"

    logger.info("✅ 72-HOUR SOAK TEST PASSED")

def create_mock_session(subject_code: str):
    """Create a mock treatment session."""
    # Implementation details...
    pass

def execute_mock_protocol(session) -> float:
    """Execute a randomized protocol (5-10 minutes)."""
    # Implementation details...
    pass

def write_soak_test_report(metrics_log, errors, sessions_completed, total_sessions_expected):
    """Write detailed HTML report."""
    # Implementation details...
    pass
```

**Monitoring Dashboard:**

Create real-time dashboard to monitor soak test progress:

```python
# tests/integration/soak_test_dashboard.py
import dash
from dash import html, dcc
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("TOSCA 72-Hour Soak Test Dashboard"),

    # Metrics graphs
    dcc.Graph(id='memory-graph'),
    dcc.Graph(id='cpu-graph'),
    dcc.Graph(id='sessions-graph'),

    # Update interval
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)
])

# Update graphs every minute
@app.callback(...)
def update_graphs(n):
    # Read latest metrics from log file
    # Update graphs
    pass

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
```

**Implementation Steps:**

**Day 1: Setup**
- Write soak test script
- Create monitoring dashboard
- Configure logging
- Dry run (1 hour test)

**Day 2-3: Execution**
- Start 72-hour soak test
- Monitor dashboard every 4-6 hours
- Collect screenshots of metrics
- Note any anomalies

**Day 4: Analysis**
- Generate HTML report
- Analyze error patterns
- Identify memory leaks (if any)
- Document findings

**Files Created:**
- `tests/integration/test_72hour_soak.py`
- `tests/integration/soak_test_dashboard.py`
- `data/soak_test_results/soak_test_report_YYYYMMDD.html`

**Acceptance Criteria:**
- [ ] ≥95% session completion rate (137/144 sessions)
- [ ] <5% error rate (<7 errors)
- [ ] <20% memory growth (final < 336 MB if initial = 280 MB)
- [ ] No crashes
- [ ] All safety interlocks responsive throughout test
- [ ] Detailed report generated

---

## 4. Performance Optimizations

### P1-PERF-001: Implement Video Compression Tuning

**Priority:** P1 (HIGH)
**Effort:** 1 day
**Module:** `src/hardware/camera_controller.py`

**Current State:**
- Video codec: H.264 (default settings)
- File size: ~4 MB per 3-minute video
- Quality: Good (but potentially over-optimized)

**Target State:**
- Video codec: H.264 with CRF 28
- File size: ~2 MB per 3-minute video (50% reduction)
- Quality: Still acceptable for medical documentation

**Implementation:**

```python
# camera_controller.py
import cv2

class CameraController:
    def start_recording(self, output_path: str):
        """Start video recording with optimized compression."""
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        fps = 30
        frame_size = (self.frame_width, self.frame_height)

        # Create video writer with CRF quality control
        self.video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            frame_size,
            isColor=True
        )

        # Set CRF parameter (Constant Rate Factor)
        # CRF 0 = lossless, CRF 51 = worst quality
        # CRF 23 = default, CRF 28 = good quality at smaller size
        self.video_writer.set(cv2.VIDEOWRITER_PROP_QUALITY, 28)

        logger.info(f"Recording started: {output_path} (H.264 CRF 28)")
```

**Quality Validation:**
1. Record 3-minute test video with CRF 23 (default)
2. Record same video with CRF 28 (optimized)
3. Compare side-by-side for visible quality loss
4. Measure file sizes
5. Get clinical user feedback on acceptability

**Expected Results:**
- CRF 23: 4 MB, excellent quality
- CRF 28: 2 MB, good quality (acceptable trade-off)

**Files Modified:**
- `src/hardware/camera_controller.py`

**Acceptance Criteria:**
- [ ] File size reduced by ~50%
- [ ] Quality acceptable for medical documentation (clinician approval)
- [ ] No frame drops during recording
- [ ] Encrypted videos still play correctly

---

### P1-PERF-002: Add Database Vacuum Schedule

**Priority:** P1 (HIGH)
**Effort:** 2 hours
**Module:** `src/database/db_manager.py`

**Current State:**
- Database grows indefinitely (deleted data leaves empty pages)
- No automated VACUUM operation
- Database file size: 139 KB (20 sessions, 500 events)

**Target State:**
- Automatic VACUUM on application shutdown
- Manual VACUUM via admin menu
- Reclaim deleted space, optimize indices

**Implementation:**

```python
# database/db_manager.py
class DatabaseManager:
    def __init__(self, db_path="data/tosca.db"):
        # ... existing init

        # Enable incremental vacuum
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA auto_vacuum = INCREMENTAL"))
            conn.commit()

    def vacuum_database(self) -> dict:
        """
        Reclaim deleted space and optimize database.

        Returns:
            dict: Statistics (size_before, size_after, space_reclaimed)
        """
        import os

        # Get size before vacuum
        size_before = os.path.getsize(self.db_path) / 1024  # KB

        logger.info(f"Starting database VACUUM (size: {size_before:.1f} KB)")

        # Execute VACUUM
        with self.engine.connect() as conn:
            conn.execute(text("VACUUM"))
            conn.commit()

        # Get size after vacuum
        size_after = os.path.getsize(self.db_path) / 1024  # KB
        space_reclaimed = size_before - size_after

        logger.info(f"VACUUM complete: {size_before:.1f} KB → {size_after:.1f} KB (reclaimed {space_reclaimed:.1f} KB)")

        return {
            "size_before_kb": size_before,
            "size_after_kb": size_after,
            "space_reclaimed_kb": space_reclaimed
        }

    def close(self):
        """Close database connection with automatic vacuum."""
        logger.info("Closing database (automatic VACUUM)")
        self.vacuum_database()
        # ... existing close logic

# ui/main_window.py
class MainWindow(QMainWindow):
    def closeEvent(self, event):
        """Application shutdown with database vacuum."""
        logger.info("Application closing...")

        # Vacuum database (reclaim space)
        stats = self.db_manager.vacuum_database()
        logger.info(f"Database optimized: {stats['space_reclaimed_kb']:.1f} KB reclaimed")

        # ... existing closeEvent logic
```

**Add to Admin Menu:**

```python
# ui/main_window.py
def _create_menu_bar(self):
    # ... existing menus

    # Admin menu
    admin_menu = self.menuBar().addMenu("Admin")

    vacuum_action = QAction("Optimize Database (VACUUM)", self)
    vacuum_action.triggered.connect(self._vacuum_database)
    admin_menu.addAction(vacuum_action)

def _vacuum_database(self):
    """Manual database vacuum."""
    reply = QMessageBox.question(
        self,
        "Optimize Database",
        "This will optimize the database and reclaim deleted space.\n\n"
        "This may take a few seconds. Continue?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        stats = self.db_manager.vacuum_database()

        QMessageBox.information(
            self,
            "Optimization Complete",
            f"Database optimized successfully.\n\n"
            f"Size before: {stats['size_before_kb']:.1f} KB\n"
            f"Size after: {stats['size_after_kb']:.1f} KB\n"
            f"Space reclaimed: {stats['space_reclaimed_kb']:.1f} KB"
        )
```

**Files Modified:**
- `src/database/db_manager.py`
- `src/ui/main_window.py`

**Acceptance Criteria:**
- [ ] VACUUM executes on application shutdown
- [ ] Admin menu item triggers manual VACUUM
- [ ] Database size reduced after deleting old sessions
- [ ] No performance degradation during VACUUM

---

### P2-PERF-003: Implement Log Rotation

**Priority:** P2 (Medium)
**Effort:** 1 day
**Module:** `src/core/event_logger.py`

**Current State:**
- Single `events.jsonl` file (grows indefinitely)
- No automated rotation
- File size: ~50 KB (500 events)

**Target State:**
- Daily log rotation
- Compressed old logs (gzip)
- 7-year retention policy (FDA requirement)

**Implementation:**

See detailed implementation in `04_ACTION_PLAN_RECOMMENDATIONS.md` Task 4.3

**Files Modified:**
- `src/core/event_logger.py`
- `src/core/log_rotator.py` (new)
- `src/ui/main_window.py` (schedule rotation timer)

**Acceptance Criteria:**
- [ ] Logs rotate daily at midnight
- [ ] Old logs compressed with gzip
- [ ] Logs older than 7 years deleted automatically
- [ ] Rotation doesn't lose any events

---

### P2-PERF-004: Add Performance Monitoring Dashboard

**Priority:** P2 (Medium)
**Effort:** 2 days
**Module:** `src/ui/widgets/performance_dashboard.py` (new)

**Objective:** Real-time performance monitoring for troubleshooting

**Features:**
1. Frame rate gauge (camera FPS)
2. Memory usage graph (trend over time)
3. CPU usage meter (current + average)
4. Disk space warning (database + videos)
5. Event log rate (events/minute)

**Implementation:**

```python
# ui/widgets/performance_dashboard.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QTimer
import psutil

class PerformanceDashboard(QWidget):
    def __init__(self, camera_controller, db_manager):
        super().__init__()
        self.camera_controller = camera_controller
        self.db_manager = db_manager
        self.process = psutil.Process()

        self._setup_ui()
        self._start_monitoring()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Frame Rate Gauge
        self.fps_label = QLabel("Camera FPS: --")
        self.fps_progress = QProgressBar()
        self.fps_progress.setRange(0, 30)
        layout.addWidget(self.fps_label)
        layout.addWidget(self.fps_progress)

        # Memory Usage Gauge
        self.memory_label = QLabel("Memory: -- MB")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 1000)  # 0-1000 MB
        layout.addWidget(self.memory_label)
        layout.addWidget(self.memory_progress)

        # CPU Usage Gauge
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_progress)

        # Disk Space Warning
        self.disk_label = QLabel("Disk Space: OK")
        layout.addWidget(self.disk_label)

        self.setLayout(layout)

    def _start_monitoring(self):
        """Update metrics every 1 second."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(1000)  # 1 second interval

    def _update_metrics(self):
        """Update all performance metrics."""
        # Camera FPS
        fps = self.camera_controller.get_current_fps()
        self.fps_label.setText(f"Camera FPS: {fps:.1f}")
        self.fps_progress.setValue(int(fps))

        # Memory usage
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.memory_label.setText(f"Memory: {memory_mb:.0f} MB")
        self.memory_progress.setValue(int(memory_mb))

        # CPU usage
        cpu_percent = self.process.cpu_percent(interval=None)
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        self.cpu_progress.setValue(int(cpu_percent))

        # Disk space
        disk = psutil.disk_usage('.')
        free_gb = disk.free / (1024**3)
        if free_gb < 5:  # Less than 5 GB free
            self.disk_label.setText(f"⚠️ Disk Space: {free_gb:.1f} GB free (LOW)")
            self.disk_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.disk_label.setText(f"Disk Space: {free_gb:.1f} GB free")
            self.disk_label.setStyleSheet("color: green;")
```

**Add to Main Window:**

```python
# ui/main_window.py
from ui.widgets.performance_dashboard import PerformanceDashboard

class MainWindow(QMainWindow):
    def _setup_ui(self):
        # ... existing UI setup

        # Add performance dashboard (dev mode only)
        if self.config.enable_developer_mode:
            self.performance_dashboard = PerformanceDashboard(
                camera_controller=self.camera_controller,
                db_manager=self.db_manager
            )
            # Add to status bar or dockable widget
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.performance_dashboard)
```

**Files Created:**
- `src/ui/widgets/performance_dashboard.py`

**Files Modified:**
- `src/ui/main_window.py`

**Acceptance Criteria:**
- [ ] Dashboard shows real-time FPS
- [ ] Dashboard shows memory usage trend
- [ ] Dashboard shows CPU usage
- [ ] Disk space warning when <5 GB free
- [ ] Dashboard only visible in developer mode

---

## 5. Documentation & Compliance

### P1-DOC-001: Create Risk Management File (ISO 14971)

**Priority:** P1 (HIGH)
**Effort:** 5 days
**Module:** `docs/compliance/RISK_MANAGEMENT_FILE.md`

See detailed implementation in `04_ACTION_PLAN_RECOMMENDATIONS.md` Task 3.1

**Files Created:**
- `docs/compliance/RISK_MANAGEMENT_FILE.md`
- `docs/compliance/FMEA_ANALYSIS.xlsx`
- `docs/compliance/RISK_MATRIX.png`

**Acceptance Criteria:**
- [ ] 30-50 hazards identified and documented
- [ ] FMEA analysis complete with severity × probability ratings
- [ ] All residual risks evaluated as acceptable
- [ ] Mitigation measures documented with traceability

---

### P1-DOC-002: Create Software Requirements Specification (SRS)

**Priority:** P1 (HIGH)
**Effort:** 5 days
**Module:** `docs/compliance/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`

See detailed implementation in `04_ACTION_PLAN_RECOMMENDATIONS.md` Task 3.2

**Files Created:**
- `docs/compliance/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`
- `docs/compliance/REQUIREMENTS_TRACEABILITY_MATRIX.xlsx`

**Acceptance Criteria:**
- [ ] 100-200 functional requirements documented
- [ ] 30-50 safety requirements documented
- [ ] All requirements have unique IDs
- [ ] All requirements linked to test cases
- [ ] All requirements linked to implementation

---

### P1-DOC-003: Create Verification & Validation (V&V) Protocols

**Priority:** P1 (HIGH)
**Effort:** 4 days
**Module:** `docs/compliance/VERIFICATION_VALIDATION_PROTOCOLS/`

See detailed implementation in `04_ACTION_PLAN_RECOMMENDATIONS.md` Task 3.3

**Files Created:**
- `docs/compliance/VV_PROTOCOLS/TP-SAFETY-001.md` (Emergency stop test)
- `docs/compliance/VV_PROTOCOLS/TP-SAFETY-002.md` (Footpedal test)
- ... (30-40 test protocols total)

**Acceptance Criteria:**
- [ ] All safety requirements have test protocols
- [ ] All test protocols executed with documented results
- [ ] Pass/fail criteria clearly defined
- [ ] Test data recorded for traceability

---

## 6. Developer Experience

### P3-DX-001: Add Pre-Commit Hook Documentation

**Priority:** P3 (Low)
**Effort:** 1 hour
**Module:** `docs/development/PRE_COMMIT_HOOKS.md`

**Objective:** Document pre-commit hooks and `--no-verify` usage

**Content:**

```markdown
# Pre-Commit Hooks

TOSCA uses pre-commit hooks to enforce code quality standards.

## Configured Hooks

1. **Black** - Code formatter (PEP 8)
2. **Flake8** - Linter (style violations)
3. **MyPy** - Type checker (type hints)
4. **isort** - Import sorter

## Usage

### Normal Commit (Recommended)
```bash
git add .
git commit -m "feat: add new feature"
# Hooks run automatically
```

### Skip Hooks (When Necessary)
```bash
git commit --no-verify -m "fix: known MyPy false positive"
```

**⚠️ IMPORTANT:** Only use `--no-verify` when:
1. MyPy has known false positives
2. Type stub file is missing for third-party library
3. Emergency hotfix deployment

**Document the reason in commit message!**

## MyPy Known Issues

### Issue 1: PyQt6 Signal Type Hints
MyPy doesn't recognize PyQt6 signal types correctly.

**False Positive:**
```
error: "pyqtSignal" not callable  [misc]
```

**Solution:** Use `--no-verify` for commits with signal definitions.

### Issue 2: VmbPy Type Stubs Missing
Allied Vision VmbPy library has no type stubs.

**False Positive:**
```
error: Skipping analyzing "vmbpy": module is installed, but missing library stubs  [import]
```

**Solution:** Use `# type: ignore` comments or `--no-verify`.

## Running Hooks Manually

```bash
# Run all hooks on staged files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```
```

**Files Created:**
- `docs/development/PRE_COMMIT_HOOKS.md`

**Acceptance Criteria:**
- [ ] Pre-commit hooks documented
- [ ] `--no-verify` usage justified
- [ ] MyPy known issues listed

---

### P3-DX-002: Add Development Environment Setup Guide

**Priority:** P3 (Low)
**Effort:** 2 hours
**Module:** `docs/development/SETUP_GUIDE.md`

**Objective:** Streamline onboarding for new developers

**Content:**

```markdown
# TOSCA Development Environment Setup

## Prerequisites

- Python 3.12+ (actual: 3.12.10)
- Git
- Windows 10+ (required for hardware controllers)

## 1. Clone Repository

```bash
git clone https://github.com/will-aleyegn/TOSCA_DEV.git
cd TOSCA_DEV
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install Pre-Commit Hooks

```bash
pre-commit install
```

## 5. Configure Hardware (Optional)

If you have hardware connected:

1. Edit `config.yaml`:
   ```yaml
   laser:
     com_port: "COM10"  # Update to your port
   gpio:
     com_port: "COM4"   # Update to your port
   ```

2. Test hardware connection:
   ```bash
   python scripts/test_hardware.py
   ```

## 6. Run Tests

```bash
# All tests
pytest

# Specific test category
pytest tests/hardware/
pytest tests/core/

# With coverage
pytest --cov=src --cov-report=html
```

## 7. Run Application

```bash
python src/main.py
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Activate virtual environment first.

### Issue: COM port not found
**Solution:** Check Device Manager, update `config.yaml`.

### Issue: Camera not detected
**Solution:** Install VmbPy SDK, check USB 3.0 connection.
```

**Files Created:**
- `docs/development/SETUP_GUIDE.md`

**Acceptance Criteria:**
- [ ] New developer can set up environment in <15 minutes
- [ ] All common issues documented

---

## Summary by Priority

### P0 (CRITICAL) - 0 tasks
*All critical tasks are security-related (see `04_ACTION_PLAN_RECOMMENDATIONS.md`)*

### P1 (HIGH) - 10 tasks
1. P1-TEST-001: Safety State Machine Unit Tests (5 days)
2. P1-TEST-002: Protocol Engine Safety Tests (3 days)
3. P1-TEST-003: 72-Hour Soak Test (3 days)
4. P1-PERF-001: Video Compression Tuning (1 day)
5. P1-PERF-002: Database Vacuum Schedule (2 hours)
6. P1-DOC-001: Risk Management File (5 days)
7. P1-DOC-002: Software Requirements Specification (5 days)
8. P1-DOC-003: V&V Protocols (4 days)

**Total P1 Effort:** ~28 days (6 weeks)

### P2 (MEDIUM) - 3 tasks
1. P2-ARCH-001: Implement 4-State Safety Model (3 days)
2. P2-ARCH-002: Document Asyncio Event Loop (1 day)
3. P2-PERF-003: Implement Log Rotation (1 day)
4. P2-PERF-004: Performance Monitoring Dashboard (2 days)

**Total P2 Effort:** ~7 days (1.5 weeks)

### P3 (LOW) - 7 tasks
1. P3-CQ-001: Formalize LaserController Inheritance (2 hours)
2. P3-CQ-002: Refactor Protocol Engine (1 day)
3. P3-CQ-003: Complete Type Hint Coverage (2 hours)
4. P3-CQ-004: Split gpio_controller.py (4 hours)
5. P3-DX-001: Pre-Commit Hook Documentation (1 hour)
6. P3-DX-002: Development Setup Guide (2 hours)

**Total P3 Effort:** ~3 days

---

## Recommended Execution Order

### Phase 6 (Weeks 1-8) - Security + Testing + Compliance

**Weeks 1-2: Security fixes** (see `04_ACTION_PLAN_RECOMMENDATIONS.md`)

**Weeks 3-4: High-Priority Testing**
- Week 3: P1-TEST-001 (Safety tests) + P1-TEST-002 (Protocol tests)
- Week 4: P1-TEST-003 (72-hour soak test)

**Weeks 5-6: Compliance Documentation**
- Week 5: P1-DOC-001 (Risk file) + P1-DOC-002 (SRS)
- Week 6: P1-DOC-003 (V&V protocols)

**Weeks 7-8: Performance + Final Hardening**
- Week 7: P1-PERF-001 (Video compression) + P1-PERF-002 (DB vacuum)
- Week 8: Security penetration testing (see `04_ACTION_PLAN_RECOMMENDATIONS.md`)

### Phase 7 (Weeks 9-12) - Medium Priority

**Weeks 9-10: Architecture Enhancements**
- P2-ARCH-001 (4-state safety model)
- P2-ARCH-002 (Asyncio documentation)

**Weeks 11-12: Performance Enhancements**
- P2-PERF-003 (Log rotation)
- P2-PERF-004 (Performance dashboard)

### Phase 8+ (Post-Production) - Low Priority

**Anytime: Code Quality & Developer Experience**
- P3-CQ-001 to P3-CQ-004 (Code refactoring)
- P3-DX-001 to P3-DX-002 (Developer documentation)

---

## Tracking Progress

Use this checklist to track completion:

```markdown
## Phase 6 Progress

### Week 1-2: Security (see separate action plan)
- [ ] Database encryption
- [ ] User authentication
- [ ] Video encryption
- [ ] Audit trail integrity
- [ ] Remove TestSafetyManager

### Week 3-4: Testing
- [ ] P1-TEST-001: Safety state machine tests
- [ ] P1-TEST-002: Protocol engine safety tests
- [ ] P1-TEST-003: 72-hour soak test

### Week 5-6: Documentation
- [ ] P1-DOC-001: Risk management file
- [ ] P1-DOC-002: Software requirements spec
- [ ] P1-DOC-003: V&V protocols

### Week 7-8: Performance + Final
- [ ] P1-PERF-001: Video compression
- [ ] P1-PERF-002: Database vacuum
- [ ] Security penetration testing
```

---

**END OF NON-SECURITY TODO LIST**

For security-related tasks, see: `04_ACTION_PLAN_RECOMMENDATIONS.md`

For comprehensive review findings, see: `01_EXECUTIVE_SUMMARY.md`
