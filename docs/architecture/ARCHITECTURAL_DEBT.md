# Architectural Debt and Improvements

**Date Identified:** 2025-10-25
**Current Phase:** Phase 3 (95% complete)
**Priority:** Safety-Critical items must be completed before clinical testing

---

## Overview

Five architectural improvements identified during aiming laser implementation:

1. **Safety Watchdog Timer** (CRITICAL - Priority 1)
2. **Configuration Management** (HIGH - Priority 2)
3. **Hardware Controller ABC** (MEDIUM - Priority 3)
4. **Import Path Standardization** (LOW - Priority 4)
5. **Dependency Injection** (DEFERRED - Not recommended)

---

## 1. Safety Watchdog Timer ⚠️ CRITICAL

### Current Risk

**Hazard:** Python GUI freeze (infinite loop, deadlock, OS crash) leaves hardware in last commanded state.

**Scenario:**
- Treatment laser ON at 1500mA
- GUI freezes due to software bug
- Laser remains ON indefinitely
- **Patient harm risk: Thermal injury**

**Regulatory Requirement:** FDA 21 CFR 820.30(g) requires risk analysis for foreseeable software failures.

### Required Implementation

**Hardware Watchdog:**
- Arduino built-in watchdog timer (1000ms timeout)
- If no heartbeat received for 1000ms → emergency shutdown
- Emergency shutdown: All GPIO outputs LOW (lasers OFF, motors OFF)

**Software Heartbeat:**
- MainWindow sends heartbeat every 500ms (50% safety margin)
- Heartbeat = GPIO pin toggle or serial command
- If GUI responsive → heartbeat sent → watchdog reset
- If GUI frozen → no heartbeat → watchdog expires → hardware shutdown

**Files to Create:**
- `src/core/safety_watchdog.py` - Python watchdog manager
- `firmware/arduino_watchdog/arduino_watchdog.ino` - Arduino firmware with WDT
- `docs/architecture/06_safety_watchdog.md` - Design documentation

**Success Criteria:**
- Simulated GUI freeze triggers emergency shutdown within 1000ms
- All hardware outputs confirm LOW state after watchdog timeout
- System recovers gracefully after watchdog reset

**Timeline:** ASAP - Must complete before any clinical testing

---

## 2. Configuration Management - HIGH Priority

### Current Problem

Safety limits and calibration constants scattered across codebase:

```python
# gpio_controller.py:91
self.photodiode_voltage_to_power = 400.0  # mW per volt - hardcoded

# laser_controller.py:59-62
self.max_current_ma = 2000.0  # Hardcoded safety limit
self.max_power_mw = 2000.0
self.max_temperature_c = 35.0

# safety.py - thresholds embedded in code
```

**Risks:**
- No validation of calibration constants
- No audit trail for safety limit changes
- No version control for hardware configurations
- Different limits for different hardware units not supported

### Required Implementation

**Pydantic Settings System:**

```python
# src/core/config.py
from pydantic_settings import BaseSettings

class HardwareConfig(BaseSettings):
    """Hardware calibration constants with validation."""

    # Photodiode calibration
    photodiode_mw_per_volt: float = Field(
        default=400.0,
        gt=0,
        description="Photodiode calibration: mW per volt"
    )

    # Laser limits
    laser_max_current_ma: float = Field(
        default=2000.0,
        gt=0,
        le=3000.0,
        description="Maximum safe laser current"
    )

    class Config:
        env_prefix = "TOSCA_"
        validate_assignment = True

class SafetyConfig(BaseSettings):
    """Safety thresholds and timeouts."""

    watchdog_timeout_ms: int = Field(default=1000, ge=500, le=5000)
    max_treatment_duration_sec: int = Field(default=300, gt=0)
```

**Configuration Files:**

```yaml
# config/hardware.yaml
photodiode:
  mw_per_volt: 400.0
  calibration_date: "2025-10-25"
  calibration_certificate: "CAL-2025-1001"

laser:
  max_current_ma: 2000.0
  max_power_mw: 2000.0
  max_temperature_c: 35.0
  model: "Arroyo 4210"
  serial_number: "ABC123"

# config/safety.yaml
watchdog:
  timeout_ms: 1000
  heartbeat_interval_ms: 500

treatment:
  max_duration_sec: 300
  require_session: true
```

**Benefits:**
- **Type safety** - Pydantic validates on load
- **Single source of truth** - One config file per category
- **Audit trail** - Git tracks all config changes
- **Environment overrides** - `TOSCA_LASER_MAX_CURRENT_MA=1500` for testing
- **Documentation** - Field descriptions embedded in code

**Files to Create:**
- `src/core/config.py` - Pydantic settings classes
- `config/hardware.yaml` - Hardware calibration
- `config/safety.yaml` - Safety thresholds
- `docs/architecture/07_configuration_management.md` - System design

**Migration Strategy:**
1. Create config system with defaults matching current hardcoded values
2. Load configs at startup, validate, log any errors
3. Incrementally migrate controllers to use config values
4. Remove hardcoded constants
5. Add config validation tests

**Timeline:** Next sprint (2-3 days implementation)

---

## 3. Hardware Controller ABC - MEDIUM Priority

### Current Problem

Four hardware controllers (Camera, Laser, Actuator, GPIO) share similar patterns but no enforced contract:

```python
# All have these, but no guarantee:
def connect(self, port: str) -> bool
def disconnect(self) -> None
connection_changed = pyqtSignal(bool)
error_occurred = pyqtSignal(str)
is_connected: bool
```

**Issues:**
- No compile-time enforcement of interface
- MainWindow uses duck typing to access controllers
- MyPy can't validate controller usage
- Testing requires mocking each controller differently

### Required Implementation

**Abstract Base Class:**

```python
# src/hardware/base_controller.py
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal

class HardwareController(QObject, ABC):
    """
    Abstract base class for all hardware controllers.

    Enforces consistent interface for connection, monitoring, and cleanup.
    All hardware controllers must inherit from this class.
    """

    # Required signals
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to hardware device.

        Args:
            **kwargs: Device-specific connection parameters

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from hardware and cleanup resources."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Current connection status."""
        pass

    @property
    @abstractmethod
    def device_name(self) -> str:
        """Human-readable device name for logging."""
        pass
```

**Refactored Controller:**

```python
# src/hardware/laser_controller.py
class LaserController(HardwareController):
    """Arroyo laser driver controller."""

    def connect(self, port: str = "COM4", baudrate: int = 38400) -> bool:
        # Implementation here
        pass

    def disconnect(self) -> None:
        # Implementation here
        pass

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def device_name(self) -> str:
        return "Arroyo Laser Driver"
```

**MainWindow Usage:**

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # Store all controllers polymorphically
        self.controllers: List[HardwareController] = []

        self.laser_controller = LaserController()
        self.camera_controller = CameraController()
        self.actuator_controller = ActuatorController()
        self.gpio_controller = GPIOController()

        self.controllers.extend([
            self.laser_controller,
            self.camera_controller,
            self.actuator_controller,
            self.gpio_controller
        ])

    def cleanup_all_hardware(self) -> None:
        """Disconnect all hardware on shutdown."""
        for controller in self.controllers:
            if controller.is_connected:
                logger.info(f"Disconnecting {controller.device_name}")
                controller.disconnect()
```

**Benefits:**
- **Type safety** - MyPy enforces interface compliance
- **Polymorphism** - Treat all controllers uniformly
- **Documentation** - Interface is self-documenting
- **Testing** - Single mock base class

**Migration Strategy:**
1. Create `HardwareController` ABC
2. Refactor one controller at a time (start with simplest: GPIO)
3. Update tests to use new interface
4. Update MainWindow to use polymorphic list
5. Remove duck typing assumptions

**Timeline:** Medium-term (1 week implementation)

---

## 4. Import Path Standardization - LOW Priority

### Current Problem

Inconsistent import styles across codebase:

```python
# Absolute imports (preferred)
from src.hardware.laser_controller import LaserController
from src.core.event_logger import EventLogger

# Relative imports
from ..core.event_logger import EventLogger
from .laser_controller import LaserController
```

**PEP 8:** Absolute imports preferred for clarity.

### Required Implementation

**Standard:** All imports use absolute `from src.module` style.

**Tools:**
```yaml
# .pre-commit-config.yaml - add isort configuration
- repo: https://github.com/PyCQA/isort
  hooks:
    - id: isort
      args: ['--profile', 'black', '--force-single-line-imports']
```

**Migration:**
1. Run `isort --profile black --force-single-line-imports src/`
2. Manually review changes
3. Commit with message: "Standardize imports to absolute paths"

**Timeline:** Opportunistic - fix when touching files, not worth dedicated sprint

---

## 5. Dependency Injection - DEFERRED ❌

### Analysis

**Proposed Pattern:**
```python
class ApplicationService:
    """Central service locator."""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager(self.db_manager)
        # ... all services

class MainWindow(QMainWindow):
    def __init__(self, services: ApplicationService):
        self.services = services  # Injected
```

**Why NOT Recommended:**

1. **PyQt incompatibility** - Qt Designer expects zero-arg `__init__`
2. **Complexity vs benefit** - Only ~5 managers, current pattern is fine
3. **Refactoring risk** - Touches every file, high chance of introducing bugs
4. **Testing alternative** - Factory functions work fine:

```python
# tests/conftest.py
def create_main_window_for_testing():
    window = MainWindow()
    window.db_manager = MockDatabaseManager()  # Override after construction
    return window
```

**Decision:** Do not implement. Current pattern is appropriate for GUI application.

---

## Implementation Priority

### Phase 1: Safety-Critical (IMMEDIATE)
- **Safety Watchdog Timer** - Complete before clinical testing
- Est: 3-5 days

### Phase 2: Configuration (NEXT SPRINT)
- **Pydantic Configuration System** - Improve safety and maintainability
- Est: 2-3 days

### Phase 3: Code Quality (ONGOING)
- **Hardware Controller ABC** - Improve when refactoring controllers
- Est: 1 week
- **Import Standardization** - Fix opportunistically
- Est: 2 hours (automated with isort)

### Phase 4: Documentation (PARALLEL)
- Document watchdog design
- Document config system
- Update CODING_STANDARDS.md

---

## Success Metrics

### Safety Watchdog
- [ ] GUI freeze triggers shutdown within 1000ms
- [ ] All hardware outputs LOW after watchdog timeout
- [ ] System recoverable after watchdog reset
- [ ] Watchdog tested with 100+ freeze simulations

### Configuration
- [ ] All safety limits loaded from config
- [ ] All calibration constants loaded from config
- [ ] Invalid config detected at startup
- [ ] Config changes require git commit

### Hardware ABC
- [ ] All 4 controllers inherit from HardwareController
- [ ] MyPy validation passes
- [ ] MainWindow uses polymorphic controller list
- [ ] Mock testing simplified

### Imports
- [ ] All imports absolute (from src.module)
- [ ] isort pre-commit hook enforces standard
- [ ] No relative imports remain

---

## Risk Assessment

| Item | Risk if NOT Fixed | Severity | Probability |
|------|------------------|----------|-------------|
| Watchdog Timer | GUI freeze → laser stays ON → patient harm | CRITICAL | Medium |
| Configuration | Wrong calibration → wrong power → harm | HIGH | Low-Medium |
| Hardware ABC | Code inconsistency, harder testing | LOW | N/A (quality) |
| Import Standard | Cosmetic only | MINIMAL | N/A |
| Dependency Injection | N/A - not doing | N/A | N/A |

---

## Next Steps

1. **Review this document** with development team
2. **Approve Phase 1 (Watchdog)** and begin implementation
3. **Create GitHub issues** for each phase
4. **Update PROJECT_STATUS.md** with new tasks
5. **Schedule architectural review** after Phase 1 complete

---

**Last Updated:** 2025-10-25
**Author:** Development Team
**Status:** Proposed - Awaiting Approval
