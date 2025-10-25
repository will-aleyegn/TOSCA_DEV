# TOSCA Code Review Findings
**Review Date:** 2025-10-25
**Review Type:** Comprehensive (Quality, Architecture, Safety, Performance)
**Files Reviewed:** 15 core files across hardware, UI, and core systems

---

## Executive Summary

This comprehensive code review identified **11 major issues** across the TOSCA laser control system codebase. The most critical findings relate to **safety concerns** (missing watchdog timer, placeholder safety checks), **architectural coupling** (tight dependencies in MainWindow), and **configuration management** (hardcoded constants throughout).

### Severity Distribution
- **🔴 CRITICAL:** 4 issues (immediate attention required)
- **🟠 HIGH:** 2 issues (address in next sprint)
- **🟡 MEDIUM:** 4 issues (plan for upcoming releases)
- **🟢 LOW:** 1 issue (technical debt)

### Top 3 Priority Fixes
1. **Implement Real Safety Checks** - Protocol engine bypasses all interlocks
2. **Decouple MainWindow** - Implement dependency injection
3. **Centralize Configuration** - Move hardcoded values to Pydantic settings

---

## 🔴 CRITICAL Issues

### 1. Placeholder Safety Checks (SAFETY CRITICAL)
**Location:** `src/core/protocol_engine.py:463-471`
**Severity:** 🔴 CRITICAL

**Problem:**
The `_perform_safety_checks()` method always returns `True`, completely bypassing hardware and software interlocks:

```python
def _perform_safety_checks(self) -> tuple[bool, str]:
    logger.debug("Performing safety checks...")
    return True, "Safety checks passed"  # ❌ Always passes!
```

**Impact:**
- Protocols can execute in unsafe states
- Laser could activate without safety interlocks satisfied
- Operator and equipment at risk

**Solution:**
Integrate with `SafetyManager` to verify all interlocks before protocol execution:

```python
class ProtocolEngine:
    def __init__(
        self,
        safety_manager: SafetyManager,  # Add dependency
        laser_controller: Optional[Any] = None,
        actuator_controller: Optional[Any] = None,
    ) -> None:
        self.safety_manager = safety_manager
        # ...

    def _perform_safety_checks(self) -> tuple[bool, str]:
        """Perform pre-execution safety checks."""
        logger.debug("Performing safety checks...")

        if not self.safety_manager.is_laser_enable_permitted():
            return False, self.safety_manager.get_safety_status_text()

        return True, "Safety checks passed"
```

---

### 2. Missing Watchdog Timer (SAFETY CRITICAL)
**Location:** `src/core/safety.py`
**Severity:** 🔴 CRITICAL

**Problem:**
No watchdog timer exists to detect system freezes. If the GUI or main thread freezes, the laser could remain ON indefinitely.

**Impact:**
- System freeze goes undetected
- Laser remains active during freeze
- No automatic safety shutdown

**Solution:**
Implement multi-level watchdog system:

```python
class SafetyManager(QObject):
    # Add watchdog signals
    watchdog_timeout = pyqtSignal()
    heartbeat_missed = pyqtSignal(int)  # missed count

    def __init__(self) -> None:
        super().__init__()

        # Watchdog configuration
        self.watchdog_interval_ms = 1000  # 1 second heartbeat
        self.max_missed_heartbeats = 3
        self.missed_heartbeat_count = 0

        # Watchdog timer
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self._check_heartbeat)
        self.watchdog_timer.start(self.watchdog_interval_ms)

        # Heartbeat timer (must be refreshed by application)
        self.last_heartbeat = datetime.now()

    def refresh_heartbeat(self) -> None:
        """Call this regularly from main application loop."""
        self.last_heartbeat = datetime.now()
        self.missed_heartbeat_count = 0

    def _check_heartbeat(self) -> None:
        """Check if heartbeat is current."""
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()

        if elapsed > (self.watchdog_interval_ms / 1000.0):
            self.missed_heartbeat_count += 1
            self.heartbeat_missed.emit(self.missed_heartbeat_count)

            if self.missed_heartbeat_count >= self.max_missed_heartbeats:
                logger.critical("WATCHDOG TIMEOUT - System freeze detected!")
                self.trigger_emergency_stop()
                self.watchdog_timeout.emit()
```

---

### 3. Tight Coupling in MainWindow
**Location:** `src/ui/main_window.py:56-118`
**Severity:** 🔴 CRITICAL

**Problem:**
`MainWindow` directly instantiates all core services, violating Dependency Inversion Principle:

```python
def __init__(self) -> None:
    # ❌ Tightly coupled - creates all dependencies
    self.db_manager = DatabaseManager()
    self.session_manager = SessionManager(self.db_manager)
    self.event_logger = EventLogger(self.db_manager)
    self.safety_manager = SafetyManager()
    self.camera_controller = CameraController()
```

**Impact:**
- Impossible to unit test MainWindow in isolation
- Cannot swap implementations for testing
- Difficult to manage service lifecycle
- Violates SOLID principles

**Solution:**
Move service instantiation to `main.py` and use dependency injection:

```python
# src/main.py
def main() -> int:
    logger = setup_logging()

    try:
        from PyQt6.QtWidgets import QApplication
        from core.event_logger import EventLogger
        from core.safety import SafetyManager
        from core.session_manager import SessionManager
        from database.db_manager import DatabaseManager
        from ui.main_window import MainWindow

        app = QApplication(sys.argv)

        # Initialize services (Application Service pattern)
        db_manager = DatabaseManager()
        db_manager.initialize()
        session_manager = SessionManager(db_manager)
        event_logger = EventLogger(db_manager)
        safety_manager = SafetyManager()

        # Inject dependencies into MainWindow
        window = MainWindow(
            db_manager=db_manager,
            session_manager=session_manager,
            event_logger=event_logger,
            safety_manager=safety_manager,
        )
        window.show()

        return app.exec()
```

---

### 4. Hardcoded Configuration Values
**Location:** Multiple files
**Severity:** 🔴 CRITICAL

**Problem:**
Configuration constants are hardcoded throughout the codebase:

- **COM Ports:** `"COM3"` (actuator_widget.py:167), `"COM4"` (laser_widget.py:271, gpio_controller.py:104)
- **Baudrates:** `9600` (actuator_controller.py:87), `38400` (laser_controller.py:66)
- **Timeouts:** `RETRY_DELAY=1.0`, `ACTION_TIMEOUT=60.0` (protocol_engine.py:27-28)
- **Safety Limits:** `max_current_ma=2000.0`, `max_power_mw=2000.0` (laser_controller.py:59-60)
- **Pin Numbers:** motor_pin=2, vibration_pin=3 (gpio_controller.py:73-76)
- **Calibration:** `photodiode_voltage_to_power=400.0` (gpio_controller.py:98)

**Impact:**
- Difficult to deploy in different environments
- Cannot reconfigure without code changes
- Testing requires code modification
- Hardware changes require code updates

**Solution:**
Create centralized configuration with Pydantic settings:

```python
# src/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class HardwareSettings(BaseSettings):
    """Hardware device configuration."""

    # Actuator settings
    actuator_com_port: str = "COM3"
    actuator_baudrate: int = 9600
    actuator_low_limit_um: float = -45000.0
    actuator_high_limit_um: float = 45000.0

    # Laser settings
    laser_com_port: str = "COM4"
    laser_baudrate: int = 38400
    laser_max_current_ma: float = 2000.0
    laser_max_power_mw: float = 2000.0
    laser_timeout_s: float = 1.0

    # GPIO settings
    gpio_com_port: str = "COM4"
    gpio_motor_pin: int = 2
    gpio_vibration_pin: int = 3
    gpio_aiming_laser_pin: int = 4
    gpio_photodiode_pin: int = 0
    gpio_photodiode_calibration: float = 400.0  # mW per volt

    class Config:
        env_prefix = "TOSCA_"  # Read from environment variables
        env_file = ".env"

class ProtocolSettings(BaseSettings):
    """Protocol execution configuration."""
    max_retries: int = 3
    retry_delay_s: float = 1.0
    action_timeout_s: float = 60.0

    class Config:
        env_prefix = "TOSCA_"

# Global settings instance
HARDWARE = HardwareSettings()
PROTOCOL = ProtocolSettings()
```

---

## 🟠 HIGH Priority Issues

### 5. Missing Hardware Controller ABC
**Location:** `src/hardware/` (all controller files)
**Severity:** 🟠 HIGH

**Problem:**
All hardware controllers (`LaserController`, `ActuatorController`, `CameraController`, `GPIOController`) duplicate common patterns without a shared interface:

- All have `connect()` and `disconnect()` methods
- All have `is_connected` state
- All emit `connection_changed` and `error_occurred` signals
- All integrate with event_logger

**Impact:**
- Code duplication across 4 controllers
- No polymorphic hardware management
- Difficult to add new controllers
- Inconsistent interfaces

**Solution:**
Create abstract base class for all hardware controllers:

```python
# src/hardware/base_controller.py
from abc import ABC, abstractmethod
from typing import Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

class HardwareControllerBase(QObject, ABC):
    """
    Abstract base class for all hardware controllers.

    Defines common interface for hardware lifecycle management.
    """

    # Common signals
    connection_changed = pyqtSignal(bool)  # True=connected
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()
        self.is_connected = False
        self.event_logger = event_logger

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to hardware device.

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from hardware device and cleanup resources."""
        pass

    def cleanup(self) -> None:
        """Default cleanup implementation."""
        self.disconnect()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.cleanup()
        return False
```

---

### 6. Actuator Movement Uses Sleep Instead of Signal
**Location:** `src/core/protocol_engine.py:414-418`
**Severity:** 🟠 HIGH

**Problem:**
Actuator movement uses `asyncio.sleep()` with estimated duration instead of waiting for the `position_reached` signal:

```python
# ❌ Unreliable - uses estimated time
assumed_current = 1500.0
distance = abs(params.target_position_um - assumed_current)
move_time = distance / params.speed_um_per_sec
await asyncio.sleep(move_time)
```

**Impact:**
- Movement timing unreliable
- Doesn't account for acceleration/deceleration
- May proceed before position actually reached
- No error detection if move fails

**Solution:**
Convert PyQt signal to asyncio Future:

```python
# Utility function
def qt_signal_to_future(signal: pyqtSignal) -> asyncio.Future:
    """Create asyncio.Future that completes when PyQt signal emits."""
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def on_signal(*args):
        if not future.done():
            loop.call_soon_threadsafe(future.set_result, args or True)
        try:
            signal.disconnect(on_signal)
        except TypeError:
            pass

    signal.connect(on_signal)
    return future

# Usage in protocol engine
async def _execute_move_actuator(self, params: MoveActuatorParams) -> None:
    if self.actuator:
        # Set speed and initiate move
        self.actuator.set_speed(int(params.speed_um_per_sec))
        self.actuator.set_position(params.target_position_um)

        # ✅ Wait for actual position_reached signal
        pos_reached = qt_signal_to_future(self.actuator.position_reached)
        await pos_reached
        logger.info("Actuator move complete")
```

---

## 🟡 MEDIUM Priority Issues

### 7. Inconsistent Import Paths
**Location:** Multiple files
**Severity:** 🟡 MEDIUM

**Problem:**
- **Widgets** use absolute imports: `from src.hardware.laser_controller import LaserController`
- **Controllers** use relative imports: `from ..core.event_logger import EventType`

**Impact:**
- Confusing for developers
- Inconsistent code style
- Can break during refactoring

**Solution:**
Standardize on relative imports throughout:

```python
# ✅ Preferred - relative imports
from ..hardware.laser_controller import LaserController
from ..core.event_logger import EventType

# ❌ Avoid - absolute imports with src. prefix
from src.hardware.laser_controller import LaserController
```

---

### 8. Duplicate SessionManager Classes
**Location:** `src/core/session_manager.py`, `src/core/session.py`
**Severity:** 🟡 MEDIUM

**Problem:**
Two `SessionManager` implementations exist:
- `session_manager.py:20` - QObject-based, used in MainWindow
- `session.py:150` - Non-QObject, appears unused

**Impact:**
- Confusion about which to use
- Potential import errors
- Code duplication

**Solution:**
Consolidate into single implementation:
1. Keep QObject-based version in `session_manager.py`
2. Remove duplicate from `session.py`
3. Keep only `Session` dataclass in `session.py`

---

### 9. Missing Protocol Execution Persistence
**Location:** `src/core/protocol_engine.py:473-477`
**Severity:** 🟡 MEDIUM

**Problem:**
Database persistence for protocol execution is not implemented:

```python
def _save_execution_record(self) -> None:
    """Save execution record to database."""
    # TODO(#127): Implement database persistence
    logger.debug("Database persistence not yet implemented")
```

**Impact:**
- No audit trail for treatments
- Cannot review past protocol executions
- Compliance issues

**Solution:**
Implement database persistence using existing models.

---

### 10. Empty Config Directory
**Location:** `src/config/`
**Severity:** 🟡 MEDIUM

**Problem:**
Config directory contains only `__init__.py` - no actual configuration module.

**Solution:**
Create `settings.py` with Pydantic settings (see Issue #4 solution).

---

## 🟢 LOW Priority Issues

### 11. No Context Manager Support for Hardware
**Location:** `src/hardware/` (all controllers)
**Severity:** 🟢 LOW

**Problem:**
Hardware controllers don't implement `__enter__`/`__exit__` for context manager support.

**Impact:**
- Cleanup relies on `closeEvent` being called
- No guarantee of resource cleanup on crash
- Cannot use `with` statement

**Solution:**
Add to `HardwareControllerBase` (see Issue #5 solution).

---

## Positive Aspects ✅

The codebase demonstrates several strengths:

1. **Excellent Hardware Abstraction** - Each device has dedicated controller class
2. **Effective PyQt Signals** - Good event-driven architecture
3. **Comprehensive Logging** - Well-configured and consistent
4. **Clear Data Models** - Protocol dataclasses are well-designed
5. **Good Documentation** - Hardware controllers well-documented

---

## Files Reviewed

| File | Lines | Issues Found |
|------|-------|--------------|
| `src/core/protocol_engine.py` | 530 | 3 (Critical: 1, High: 1, Medium: 1) |
| `src/ui/main_window.py` | 330 | 1 (Critical: 1) |
| `src/core/safety.py` | 214 | 1 (Critical: 1) |
| `src/hardware/laser_controller.py` | 485 | 2 (Critical: 1, High: 1) |
| `src/hardware/actuator_controller.py` | 794 | 2 (Critical: 1, High: 1) |
| `src/hardware/camera_controller.py` | 739 | 2 (Critical: 1, High: 1) |
| `src/hardware/gpio_controller.py` | 449 | 2 (Critical: 1, High: 1) |
| `src/core/session_manager.py` | 300 | 1 (Medium: 1) |
| `src/core/session.py` | 150 | 1 (Medium: 1) |
| Others | - | - |

---

## Recommendations

### Immediate Actions (This Week)
1. ✅ Fix placeholder safety checks in protocol engine
2. ✅ Implement watchdog timer in SafetyManager
3. ✅ Create configuration settings module

### Short-term (Next Sprint)
4. ✅ Refactor MainWindow for dependency injection
5. ✅ Create HardwareControllerBase ABC
6. ✅ Fix actuator movement to use position_reached signal

### Medium-term (Next Release)
7. ✅ Standardize import paths across codebase
8. ✅ Remove duplicate SessionManager
9. ✅ Implement protocol execution persistence

### Long-term (Technical Debt)
10. ✅ Add context manager support to hardware controllers
11. ✅ Comprehensive integration testing
12. ✅ Performance optimization

---

**Review Conducted By:** Claude Code with zen MCP Code Review Tool
**Review Methodology:** Systematic analysis with expert validation
**Files Examined:** 15 core files
**Total Issues:** 11 (Critical: 4, High: 2, Medium: 4, Low: 1)
