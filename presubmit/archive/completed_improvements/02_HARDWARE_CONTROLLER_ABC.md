# Hardware Controller Abstract Base Class Design

## Problem Statement

All hardware controllers (`LaserController`, `ActuatorController`, `CameraController`, `GPIOController`) implement nearly identical patterns but share **no common interface**. This leads to code duplication, inconsistency, and difficulty managing hardware devices polymorphically.

---

## Current State Analysis

### Common Patterns Across All Controllers

| Feature | Laser | Actuator | Camera | GPIO |
|---------|-------|----------|--------|------|
| `connect()` method | ✅ | ✅ | ✅ | ✅ |
| `disconnect()` method | ✅ | ✅ | ✅ | ✅ |
| `is_connected` state | ✅ | ✅ | ✅ | ✅ |
| `connection_changed` signal | ✅ | ✅ | ✅ | ✅ |
| `error_occurred` signal | ✅ | ✅ | ✅ | ✅ |
| `event_logger` integration | ✅ | ✅ | ✅ | ✅ |
| Inherits from `QObject` | ✅ | ✅ | ✅ | ✅ |
| Monitoring timer | ✅ | ✅ | ✅ | ✅ |

### Duplicated Code Example

**LaserController:**
```python
class LaserController(QObject):
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()
        self.is_connected = False
        self.event_logger = event_logger
```

**ActuatorController:**
```python
class ActuatorController(QObject):
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()
        self.is_connected = False
        self.event_logger = event_logger
```

**Pattern repeats 4 times!**

---

## Impact Assessment

### Code Duplication
- **80+ lines** of duplicated initialization code
- **50+ lines** of duplicated connection handling
- **40+ lines** of duplicated event logging

### Maintenance Issues
- Bug fixes must be applied to 4 files
- New features require 4 implementations
- Inconsistencies creep in over time

### Architectural Limitations
- Cannot manage controllers polymorphically
- No common interface for testing
- Difficult to add new hardware controllers

---

## Proposed Solution

### Create Hardware Controller Hierarchy

```
HardwareControllerBase (ABC)
├── LaserController
├── ActuatorController
├── CameraController
└── GPIOController
```

---

## Detailed Design

### Base Class: `HardwareControllerBase`

**File:** `src/hardware/base_controller.py`

```python
"""
Abstract base class for all hardware controllers.

Provides common interface and functionality for hardware lifecycle management.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime
import logging

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class HardwareControllerBase(QObject, ABC):
    """
    Abstract base class for hardware controllers.

    Defines common interface for:
    - Connection lifecycle (connect, disconnect, cleanup)
    - State management (is_connected)
    - Event signaling (connection_changed, error_occurred)
    - Event logging integration
    - Context manager support

    All hardware controllers must inherit from this class.
    """

    # Common signals
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected
    error_occurred = pyqtSignal(str)  # Error message
    status_changed = pyqtSignal(str)  # Status description

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        """
        Initialize hardware controller.

        Args:
            event_logger: Optional EventLogger instance for logging hardware events
        """
        super().__init__()

        # Common state
        self.is_connected = False
        self.event_logger = event_logger
        self.device_name = self._get_device_name()
        self.connection_time: Optional[datetime] = None

        logger.info(f"{self.device_name} controller initialized")

    @abstractmethod
    def _get_device_name(self) -> str:
        """
        Get human-readable device name for logging.

        Returns:
            Device name (e.g., "Arroyo Laser Driver", "Xeryon Linear Stage")
        """
        pass

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to hardware device.

        Subclasses must implement device-specific connection logic.
        Should call _on_connect_success() on successful connection.

        Args:
            **kwargs: Device-specific connection parameters

        Returns:
            True if connected successfully, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from hardware device.

        Subclasses must implement device-specific disconnection logic.
        Should call _on_disconnect() after cleanup.
        """
        pass

    def cleanup(self) -> None:
        """
        Cleanup resources (default implementation calls disconnect).

        Subclasses can override for additional cleanup.
        """
        if self.is_connected:
            self.disconnect()

    def _on_connect_success(self, connection_info: str = "") -> None:
        """
        Called by subclasses after successful connection.

        Args:
            connection_info: Additional connection information for logging
        """
        self.is_connected = True
        self.connection_time = datetime.now()
        self.connection_changed.emit(True)

        logger.info(f"{self.device_name} connected: {connection_info}")

        # Log event
        if self.event_logger:
            from ..core.event_logger import EventType
            self.event_logger.log_hardware_event(
                event_type=self._get_connect_event_type(),
                description=f"{self.device_name} connected: {connection_info}",
                device_name=self.device_name,
            )

    def _on_disconnect(self) -> None:
        """Called by subclasses after disconnection."""
        self.is_connected = False
        self.connection_time = None
        self.connection_changed.emit(False)

        logger.info(f"{self.device_name} disconnected")

        # Log event
        if self.event_logger:
            from ..core.event_logger import EventType
            self.event_logger.log_hardware_event(
                event_type=self._get_disconnect_event_type(),
                description=f"{self.device_name} disconnected",
                device_name=self.device_name,
            )

    def _emit_error(self, error_message: str, log_to_event_logger: bool = True) -> None:
        """
        Emit error signal and optionally log to event logger.

        Args:
            error_message: Error description
            log_to_event_logger: Whether to log to event logger
        """
        logger.error(f"{self.device_name}: {error_message}")
        self.error_occurred.emit(error_message)

        if log_to_event_logger and self.event_logger:
            from ..core.event_logger import EventType, EventSeverity
            self.event_logger.log_event(
                event_type=EventType.HARDWARE_ERROR,
                description=f"{self.device_name}: {error_message}",
                severity=EventSeverity.WARNING,
                details={"device": self.device_name},
            )

    @abstractmethod
    def _get_connect_event_type(self):
        """Get EventType for connection (subclass must implement)."""
        pass

    @abstractmethod
    def _get_disconnect_event_type(self):
        """Get EventType for disconnection (subclass must implement)."""
        pass

    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.cleanup()
        return False

    def get_connection_status(self) -> dict:
        """
        Get comprehensive connection status.

        Returns:
            Dictionary with connection information
        """
        uptime = None
        if self.is_connected and self.connection_time:
            uptime = (datetime.now() - self.connection_time).total_seconds()

        return {
            "device_name": self.device_name,
            "is_connected": self.is_connected,
            "connection_time": self.connection_time.isoformat() if self.connection_time else None,
            "uptime_seconds": uptime,
        }
```

---

## Controller Refactoring Examples

### LaserController Refactoring

**Before:**
```python
class LaserController(QObject):
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__()
        self.is_connected = False
        self.event_logger = event_logger
        # ... (80 lines of init code)
```

**After:**
```python
from .base_controller import HardwareControllerBase

class LaserController(HardwareControllerBase):
    # Device-specific signals
    power_changed = pyqtSignal(float)
    current_changed = pyqtSignal(float)
    temperature_changed = pyqtSignal(float)

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__(event_logger)  # Handles common init

        # Device-specific initialization only
        self.ser: Optional[serial.Serial] = None
        self.is_output_enabled = False
        self.monitor_timer = QTimer()
        # ...

    def _get_device_name(self) -> str:
        return "Arroyo Laser Driver"

    def _get_connect_event_type(self):
        from ..core.event_logger import EventType
        return EventType.HARDWARE_LASER_CONNECT

    def _get_disconnect_event_type(self):
        from ..core.event_logger import EventType
        return EventType.HARDWARE_LASER_DISCONNECT

    def connect(self, com_port: str = "COM4", baudrate: int = 38400) -> bool:
        try:
            # Device-specific connection logic
            self.ser = serial.Serial(port=com_port, baudrate=baudrate, ...)

            if self.ser.is_open:
                response = self._write_command("*IDN?")
                if response:
                    # ✅ Call base class method for common handling
                    self._on_connect_success(response.strip())
                    return True

        except Exception as e:
            # ✅ Use base class error handling
            self._emit_error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        if self.ser and self.ser.is_open:
            self.set_output(False)
            self.monitor_timer.stop()
            self.ser.close()

        # ✅ Call base class method
        self._on_disconnect()
```

**Lines Saved:** ~50 lines per controller × 4 controllers = **200 lines removed**

---

## Benefits

### Code Reduction
- **200+ lines** of duplicated code removed
- **Single source of truth** for common patterns
- **Easier to maintain** - bug fixes in one place

### Type Safety & Polymorphism
```python
# Can now manage controllers polymorphically
from hardware.base_controller import HardwareControllerBase

controllers: list[HardwareControllerBase] = [
    laser_controller,
    actuator_controller,
    camera_controller,
    gpio_controller,
]

# Connect all hardware
for controller in controllers:
    if not controller.connect():
        logger.error(f"Failed to connect {controller.device_name}")

# Disconnect all hardware
for controller in controllers:
    controller.disconnect()
```

### Testing Improvements
```python
# Can create mock hardware controllers for testing
class MockHardwareController(HardwareControllerBase):
    def _get_device_name(self) -> str:
        return "Mock Device"

    def connect(self, **kwargs) -> bool:
        self._on_connect_success("Mock connection")
        return True

    def disconnect(self) -> None:
        self._on_disconnect()
```

### Context Manager Support
```python
# Automatic cleanup with context managers
with LaserController() as laser:
    laser.connect("COM4")
    laser.set_current(1000)
    # Automatically disconnected on exit
```

---

## Implementation Plan

### Phase 1: Create Base Class (1 day)
1. Create `src/hardware/base_controller.py`
2. Implement `HardwareControllerBase` with all common functionality
3. Write unit tests for base class

### Phase 2: Refactor LaserController (1 day)
1. Make `LaserController` inherit from `HardwareControllerBase`
2. Remove duplicated code
3. Test laser controller thoroughly
4. Document changes

### Phase 3: Refactor Remaining Controllers (2 days)
1. Refactor `ActuatorController` (0.5 days)
2. Refactor `CameraController` (0.5 days)
3. Refactor `GPIOController` (0.5 days)
4. Integration testing (0.5 days)

### Phase 4: Update MainWindow (0.5 days)
1. Utilize polymorphic controller management
2. Simplify controller lifecycle code

### Phase 5: Documentation (0.5 days)
1. Update architecture documentation
2. Update developer guidelines
3. Create examples for new controllers

---

## Migration Strategy

### Backward Compatibility
During migration, both old and new patterns will coexist:
- New code uses `HardwareControllerBase`
- Old code continues to work
- Gradual migration controller by controller

### Testing Strategy
For each controller:
1. Refactor to use base class
2. Run existing unit tests
3. Run integration tests
4. Manual hardware testing
5. Only proceed to next controller after validation

---

## Future Enhancements

### 1. Hardware Manager Service
```python
class HardwareManager:
    """Manages all hardware controllers."""

    def __init__(self):
        self.controllers: dict[str, HardwareControllerBase] = {}

    def register(self, name: str, controller: HardwareControllerBase):
        self.controllers[name] = controller

    def connect_all(self) -> bool:
        return all(ctrl.connect() for ctrl in self.controllers.values())

    def disconnect_all(self):
        for ctrl in self.controllers.values():
            ctrl.disconnect()
```

### 2. Connection Retry Logic
Add to base class:
```python
def connect_with_retry(self, max_retries: int = 3, **kwargs) -> bool:
    for attempt in range(max_retries):
        if self.connect(**kwargs):
            return True
        time.sleep(1.0)
    return False
```

### 3. Health Monitoring
```python
class HardwareControllerBase:
    def check_health(self) -> bool:
        """Override in subclasses for health checks."""
        return self.is_connected
```

---

## Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Create base class | 1 day | 1 developer |
| Refactor LaserController | 1 day | 1 developer |
| Refactor remaining controllers | 2 days | 1 developer |
| Update MainWindow | 0.5 days | 1 developer |
| Documentation | 0.5 days | 1 developer |
| **Total** | **5 days** | **1 developer** |

---

## Success Criteria

1. ✅ `HardwareControllerBase` ABC created and tested
2. ✅ All 4 controllers inherit from base class
3. ✅ 200+ lines of code removed
4. ✅ All hardware tests pass
5. ✅ Manual hardware testing successful
6. ✅ Documentation updated
7. ✅ Code review approved

---

**Status:** 📋 Ready for Implementation
**Priority:** 🟠 HIGH
**Effort:** 5 days
**Risk:** Medium (requires careful testing)
**Dependencies:** None
