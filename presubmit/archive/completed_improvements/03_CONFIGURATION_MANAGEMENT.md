# Configuration Management with Pydantic Settings

## Problem Statement

Configuration values are **hardcoded throughout the codebase** as default arguments, class attributes, and module-level constants. This makes the application:
- Difficult to deploy in different environments
- Impossible to reconfigure without code changes
- Hard to test with different configurations
- Brittle when hardware changes

---

## Current Hardcoded Values Audit

### Hardware Configuration
| Setting | Location | Current Value |
|---------|----------|---------------|
| Actuator COM Port | `actuator_widget.py:167` | `"COM3"` |
| Actuator Baudrate | `actuator_controller.py:87` | `9600` |
| Laser COM Port | `laser_widget.py:271`, `laser_controller.py:66` | `"COM4"` |
| Laser Baudrate | `laser_controller.py:66` | `38400` |
| GPIO COM Port | `gpio_controller.py:104` | `"COM4"` |
| Motor Pin | `gpio_controller.py:73` | `2` |
| Vibration Pin | `gpio_controller.py:74` | `3` |
| Aiming Laser Pin | `gpio_controller.py:75` | `4` |
| Photodiode Pin | `gpio_controller.py:76` | `0` |

### Safety & Limits
| Setting | Location | Current Value |
|---------|----------|---------------|
| Max Laser Current | `laser_controller.py:59` | `2000.0 mA` |
| Max Laser Power | `laser_controller.py:60` | `2000.0 mW` |
| Laser Timeout | `laser_controller.py:84-85` | `1.0 s` |
| Photodiode Calibration | `gpio_controller.py:98` | `400.0 mW/V` |

### Protocol Execution
| Setting | Location | Current Value |
|---------|----------|---------------|
| Max Retries | `protocol_engine.py:26` | `3` |
| Retry Delay | `protocol_engine.py:27` | `1.0 s` |
| Action Timeout | `protocol_engine.py:28` | `60.0 s` |

### Monitoring
| Setting | Location | Current Value |
|---------|----------|---------------|
| Laser Monitor Interval | `laser_controller.py:51` | `500 ms` |
| Actuator Monitor Interval | `actuator_controller.py:70` | `100 ms` |
| GPIO Monitor Interval | `gpio_controller.py:95` | `100 ms` |

**Total:** 20+ hardcoded configuration values across 10+ files

---

## Proposed Solution: Pydantic Settings

### Why Pydantic Settings?

✅ **Type Validation** - Automatic validation of config values
✅ **Environment Variables** - Load from `.env` files and environment
✅ **Default Values** - Fallback to sensible defaults
✅ **Documentation** - Self-documenting with type hints
✅ **IDE Support** - Autocomplete and type checking
✅ **Nested Config** - Hierarchical configuration structure

---

## Configuration Architecture

```
config/
├── __init__.py          # Export settings instances
├── settings.py          # Main settings classes
├── hardware.py          # Hardware-specific settings
├── safety.py            # Safety and limits
└── protocol.py          # Protocol execution settings
```

---

## Detailed Implementation

### 1. Hardware Settings

**File:** `src/config/hardware.py`

```python
"""Hardware device configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ActuatorSettings(BaseSettings):
    """Xeryon actuator configuration."""

    com_port: str = Field(default="COM3", description="Serial port for actuator")
    baudrate: int = Field(default=9600, description="Communication baudrate")
    auto_home_on_connect: bool = Field(default=True, description="Auto-home after connection")

    low_limit_um: float = Field(default=-45000.0, description="Low position limit (µm)")
    high_limit_um: float = Field(default=45000.0, description="High position limit (µm)")

    monitor_interval_ms: int = Field(default=100, description="Position monitoring interval")

    class Config:
        env_prefix = "TOSCA_ACTUATOR_"
        env_file = ".env"


class LaserSettings(BaseSettings):
    """Arroyo laser driver configuration."""

    com_port: str = Field(default="COM4", description="Serial port for laser")
    baudrate: int = Field(default=38400, description="Communication baudrate")

    max_current_ma: float = Field(default=2000.0, description="Maximum laser current (mA)")
    max_power_mw: float = Field(default=2000.0, description="Maximum laser power (mW)")

    timeout_s: float = Field(default=1.0, description="Serial communication timeout")
    write_timeout_s: float = Field(default=1.0, description="Serial write timeout")

    monitor_interval_ms: int = Field(default=500, description="Status monitoring interval")

    class Config:
        env_prefix = "TOSCA_LASER_"
        env_file = ".env"


class CameraSettings(BaseSettings):
    """Allied Vision camera configuration."""

    camera_id: str | None = Field(default=None, description="Specific camera ID (None = first available)")
    target_fps: float = Field(default=30.0, description="Target framerate")
    gui_fps_limit: float = Field(default=30.0, description="GUI update rate limit")

    class Config:
        env_prefix = "TOSCA_CAMERA_"
        env_file = ".env"


class GPIOSettings(BaseSettings):
    """Arduino Nano GPIO configuration."""

    com_port: str = Field(default="COM4", description="Serial port for Arduino")

    # Pin assignments
    motor_pin: int = Field(default=2, description="Smoothing motor control pin")
    vibration_pin: int = Field(default=3, description="Vibration sensor input pin")
    aiming_laser_pin: int = Field(default=4, description="Aiming laser control pin")
    photodiode_pin: int = Field(default=0, description="Photodiode analog input pin")

    # Calibration
    photodiode_voltage_to_power: float = Field(
        default=400.0, description="Photodiode calibration (mW per volt)"
    )

    # Debouncing
    vibration_debounce_threshold: int = Field(
        default=3, description="Vibration detection debounce count"
    )

    monitor_interval_ms: int = Field(default=100, description="Sensor monitoring interval")

    class Config:
        env_prefix = "TOSCA_GPIO_"
        env_file = ".env"


class HardwareSettings(BaseSettings):
    """Complete hardware configuration."""

    actuator: ActuatorSettings = ActuatorSettings()
    laser: LaserSettings = LaserSettings()
    camera: CameraSettings = CameraSettings()
    gpio: GPIOSettings = GPIOSettings()
```

### 2. Safety Settings

**File:** `src/config/safety.py`

```python
"""Safety system configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SafetySettings(BaseSettings):
    """Safety interlock and watchdog configuration."""

    # Watchdog
    watchdog_enabled: bool = Field(default=True, description="Enable watchdog timer")
    watchdog_interval_ms: int = Field(default=1000, description="Watchdog check interval")
    max_missed_heartbeats: int = Field(default=3, description="Heartbeats before timeout")

    # Safety interlocks
    require_session: bool = Field(default=True, description="Require valid session")
    require_gpio_interlock: bool = Field(default=True, description="Require GPIO interlocks")
    require_power_limit: bool = Field(default=True, description="Enforce power limits")

    class Config:
        env_prefix = "TOSCA_SAFETY_"
        env_file = ".env"
```

### 3. Protocol Settings

**File:** `src/config/protocol.py`

```python
"""Protocol execution configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ProtocolSettings(BaseSettings):
    """Protocol execution engine configuration."""

    max_retries: int = Field(default=3, description="Max retries for hardware operations")
    retry_delay_s: float = Field(default=1.0, description="Delay between retries")
    action_timeout_s: float = Field(default=60.0, description="Timeout for single action")

    # Power conversion (laser-specific)
    watts_to_milliamps: float = Field(
        default=1000.0, description="W to mA conversion (calibration required)"
    )

    class Config:
        env_prefix = "TOSCA_PROTOCOL_"
        env_file = ".env"
```

### 4. Main Settings Module

**File:** `src/config/settings.py`

```python
"""Main TOSCA configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings

from .hardware import HardwareSettings
from .safety import SafetySettings
from .protocol import ProtocolSettings


class TOSCASettings(BaseSettings):
    """Complete TOSCA application configuration."""

    # Application metadata
    app_name: str = Field(default="TOSCA Laser Control", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")

    # Development mode
    dev_mode: bool = Field(default=False, description="Enable development mode")
    debug_logging: bool = Field(default=False, description="Enable debug logging")

    # Nested configuration
    hardware: HardwareSettings = HardwareSettings()
    safety: SafetySettings = SafetySettings()
    protocol: ProtocolSettings = ProtocolSettings()

    class Config:
        env_prefix = "TOSCA_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = TOSCASettings()
```

### 5. Package Exports

**File:** `src/config/__init__.py`

```python
"""TOSCA configuration module."""

from .settings import settings, TOSCASettings

__all__ = ["settings", "TOSCASettings"]
```

---

## Usage Examples

### In Controllers

```python
# src/hardware/laser_controller.py
from ..config import settings

class LaserController(HardwareControllerBase):
    def __init__(self, event_logger: Optional[Any] = None) -> None:
        super().__init__(event_logger)

        # ✅ Use configuration instead of hardcoded values
        self.max_current_ma = settings.hardware.laser.max_current_ma
        self.max_power_mw = settings.hardware.laser.max_power_mw

        self.monitor_timer = QTimer()
        self.monitor_timer.setInterval(settings.hardware.laser.monitor_interval_ms)

    def connect(self) -> bool:
        # ✅ Use configuration for connection parameters
        com_port = settings.hardware.laser.com_port
        baudrate = settings.hardware.laser.baudrate
        timeout = settings.hardware.laser.timeout_s

        self.ser = serial.Serial(
            port=com_port,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=settings.hardware.laser.write_timeout_s,
        )
        # ...
```

### In Protocol Engine

```python
# src/core/protocol_engine.py
from ..config import settings

# ✅ Configuration constants at module level
MAX_RETRIES = settings.protocol.max_retries
RETRY_DELAY = settings.protocol.retry_delay_s
ACTION_TIMEOUT = settings.protocol.action_timeout_s
```

### In Safety Manager

```python
# src/core/safety.py
from ..config import settings

class SafetyManager(QObject):
    def __init__(self) -> None:
        super().__init__()

        # ✅ Configure watchdog from settings
        self.watchdog_enabled = settings.safety.watchdog_enabled
        self.watchdog_interval_ms = settings.safety.watchdog_interval_ms
        self.max_missed_heartbeats = settings.safety.max_missed_heartbeats
```

---

## Environment Variable Configuration

### .env File Example

Create `.env` in project root:

```bash
# TOSCA Configuration
TOSCA_DEV_MODE=false
TOSCA_DEBUG_LOGGING=false

# Hardware - Actuator
TOSCA_ACTUATOR_COM_PORT=COM3
TOSCA_ACTUATOR_BAUDRATE=9600
TOSCA_ACTUATOR_LOW_LIMIT_UM=-45000
TOSCA_ACTUATOR_HIGH_LIMIT_UM=45000

# Hardware - Laser
TOSCA_LASER_COM_PORT=COM4
TOSCA_LASER_BAUDRATE=38400
TOSCA_LASER_MAX_CURRENT_MA=2000.0
TOSCA_LASER_MAX_POWER_MW=2000.0

# Hardware - GPIO
TOSCA_GPIO_COM_PORT=COM4
TOSCA_GPIO_MOTOR_PIN=2
TOSCA_GPIO_VIBRATION_PIN=3
TOSCA_GPIO_AIMING_LASER_PIN=4
TOSCA_GPIO_PHOTODIODE_PIN=0
TOSCA_GPIO_PHOTODIODE_VOLTAGE_TO_POWER=400.0

# Safety
TOSCA_SAFETY_WATCHDOG_ENABLED=true
TOSCA_SAFETY_WATCHDOG_INTERVAL_MS=1000
TOSCA_SAFETY_MAX_MISSED_HEARTBEATS=3

# Protocol
TOSCA_PROTOCOL_MAX_RETRIES=3
TOSCA_PROTOCOL_RETRY_DELAY_S=1.0
TOSCA_PROTOCOL_ACTION_TIMEOUT_S=60.0
```

### Environment-Specific Configurations

```bash
# .env.development
TOSCA_DEV_MODE=true
TOSCA_DEBUG_LOGGING=true
TOSCA_LASER_COM_PORT=COM4  # Development laser

# .env.production
TOSCA_DEV_MODE=false
TOSCA_DEBUG_LOGGING=false
TOSCA_LASER_COM_PORT=COM1  # Production laser
```

---

## Testing with Configuration

### Unit Tests

```python
# tests/test_laser_controller.py
import pytest
from src.config import settings

def test_laser_controller_with_custom_config(monkeypatch):
    """Test laser controller with custom configuration."""

    # Override settings for test
    monkeypatch.setattr(settings.hardware.laser, "max_current_ma", 1000.0)
    monkeypatch.setattr(settings.hardware.laser, "com_port", "COM_MOCK")

    controller = LaserController()
    assert controller.max_current_ma == 1000.0
```

### Integration Tests

```python
# tests/integration/test_hardware.py
def test_all_hardware_with_test_config():
    """Test all hardware with test configuration."""

    # Load test-specific .env
    test_settings = TOSCASettings(_env_file=".env.test")

    # Use test settings
    laser = LaserController()
    assert laser.max_current_ma == test_settings.hardware.laser.max_current_ma
```

---

## Migration Strategy

### Phase 1: Create Configuration Module (1 day)
1. Create `src/config/` directory structure
2. Implement Pydantic settings classes
3. Create default `.env` file
4. Write configuration documentation

### Phase 2: Migrate Hardware Controllers (2 days)
1. Update `LaserController` to use settings
2. Update `ActuatorController` to use settings
3. Update `CameraController` to use settings
4. Update `GPIOController` to use settings

### Phase 3: Migrate Core Systems (1 day)
1. Update `ProtocolEngine` to use settings
2. Update `SafetyManager` to use settings
3. Remove hardcoded constants

### Phase 4: Testing (1 day)
1. Unit tests for each migrated component
2. Integration tests with different configurations
3. Manual testing with production config

### Phase 5: Documentation (0.5 days)
1. Configuration guide for operators
2. Developer documentation
3. Deployment guide

---

## Benefits

### Deployment
✅ **Environment-Specific Config** - Different settings per environment
✅ **No Code Changes** - Reconfigure via `.env` file
✅ **Docker-Friendly** - Environment variables for containers

### Development
✅ **Type Safety** - Pydantic validates all values
✅ **IDE Support** - Autocomplete for settings
✅ **Self-Documenting** - Field descriptions built-in

### Testing
✅ **Easy Mocking** - Override settings for tests
✅ **Reproducible** - Same config = same behavior
✅ **Isolated Tests** - Each test can use different config

### Maintenance
✅ **Single Source** - All config in one place
✅ **Validation** - Invalid values rejected at startup
✅ **Defaults** - Sensible fallbacks provided

---

## Success Criteria

1. ✅ All hardcoded values moved to configuration
2. ✅ Settings validated with Pydantic
3. ✅ Environment variables supported
4. ✅ Application runs with default config
5. ✅ Application runs with custom config
6. ✅ All tests pass with test config
7. ✅ Documentation complete

---

**Status:** 📋 Ready for Implementation
**Priority:** 🔴 CRITICAL
**Effort:** 5.5 days
**Risk:** Low (gradual migration)
**Dependencies:** None
