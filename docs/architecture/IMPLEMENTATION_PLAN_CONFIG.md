# Configuration Management Implementation Plan

**Priority:** HIGH
**Timeline:** 2-3 days
**Dependencies:** None (can be done in parallel with watchdog)

---

## Overview

Replace scattered hardcoded constants with validated Pydantic configuration system.

**Problem:** Safety limits and calibration constants are hardcoded across multiple files with no validation or audit trail.

**Solution:** Centralized YAML configuration files with Pydantic validation, version control, and type safety.

---

## Current State Analysis

### Hardcoded Constants Inventory

**gpio_controller.py:**
```python
Line 91: self.photodiode_voltage_to_power = 400.0  # mW per volt
Line 93: self.vibration_debounce_threshold = 3  # Require 3 consecutive readings
```

**laser_controller.py:**
```python
Line 59-62:
self.max_current_ma = 2000.0
self.max_power_mw = 2000.0
self.max_temperature_c = 35.0
self.min_temperature_c = 15.0
```

**safety.py:**
```python
(Need to audit for safety thresholds)
```

**Total Constants to Migrate:** ~15-20

---

## Target Architecture

### Configuration File Structure

```
config/
├── hardware.yaml          # Hardware calibration and limits
├── safety.yaml            # Safety thresholds and timeouts
├── application.yaml       # GUI settings, paths
└── schemas/
    ├── hardware_schema.json    # JSON schema for validation
    └── safety_schema.json
```

### Pydantic Settings Classes

```python
# src/core/config.py
from pydantic import BaseSettings, Field, validator
from typing import Optional

class PhotodiodeConfig(BaseSettings):
    """Photodiode sensor calibration."""
    mw_per_volt: float = Field(
        default=400.0,
        gt=0.0,
        le=1000.0,
        description="Photodiode calibration: milliwatts per volt"
    )
    calibration_date: Optional[str] = Field(
        default=None,
        description="Last calibration date (YYYY-MM-DD)"
    )
    calibration_certificate: Optional[str] = Field(
        default=None,
        description="Calibration certificate number"
    )

class LaserConfig(BaseSettings):
    """Laser driver safety limits."""
    max_current_ma: float = Field(
        default=2000.0,
        gt=0.0,
        le=3000.0,
        description="Maximum safe laser diode current (mA)"
    )
    max_power_mw: float = Field(
        default=2000.0,
        gt=0.0,
        le=3000.0,
        description="Maximum safe laser power output (mW)"
    )
    max_temperature_c: float = Field(
        default=35.0,
        gt=0.0,
        le=50.0,
        description="Maximum safe TEC temperature (°C)"
    )
    min_temperature_c: float = Field(
        default=15.0,
        gt=0.0,
        le=30.0,
        description="Minimum safe TEC temperature (°C)"
    )

    @validator('max_temperature_c')
    def validate_temperature_range(cls, v, values):
        if 'min_temperature_c' in values and v <= values['min_temperature_c']:
            raise ValueError('max_temperature_c must be greater than min_temperature_c')
        return v

class GPIOConfig(BaseSettings):
    """GPIO controller settings."""
    vibration_debounce_threshold: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Consecutive readings required for vibration detection"
    )
    monitor_interval_ms: int = Field(
        default=100,
        ge=50,
        le=500,
        description="GPIO monitoring update interval (ms)"
    )

class HardwareConfig(BaseSettings):
    """Combined hardware configuration."""
    photodiode: PhotodiodeConfig = PhotodiodeConfig()
    laser: LaserConfig = LaserConfig()
    gpio: GPIOConfig = GPIOConfig()

    class Config:
        env_prefix = "TOSCA_"
        env_nested_delimiter = "__"
        # Allow overrides like: TOSCA_LASER__MAX_CURRENT_MA=1500

class SafetyConfig(BaseSettings):
    """Safety system thresholds and timeouts."""
    watchdog_timeout_ms: int = Field(
        default=1000,
        ge=500,
        le=5000,
        description="Watchdog timer timeout (ms)"
    )
    watchdog_heartbeat_interval_ms: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Watchdog heartbeat send interval (ms)"
    )
    max_treatment_duration_sec: int = Field(
        default=300,
        gt=0,
        le=3600,
        description="Maximum single treatment duration (seconds)"
    )
    require_session: bool = Field(
        default=True,
        description="Require valid session for treatment"
    )

    @validator('watchdog_heartbeat_interval_ms')
    def validate_heartbeat_interval(cls, v, values):
        if 'watchdog_timeout_ms' in values:
            # Heartbeat must be at least 2x faster than timeout
            if v >= values['watchdog_timeout_ms'] / 2:
                raise ValueError(
                    'Heartbeat interval must be less than half of timeout '
                    'for safety margin'
                )
        return v

class ApplicationConfig(BaseSettings):
    """Application-level settings."""
    log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    data_directory: str = Field(default="./data")
    session_video_directory: str = Field(default="./data/sessions")

class Config:
    """Root configuration object."""
    def __init__(self):
        self.hardware = HardwareConfig()
        self.safety = SafetyConfig()
        self.application = ApplicationConfig()

    @classmethod
    def load_from_files(cls, base_path: str = "config") -> "Config":
        """
        Load configuration from YAML files.

        Args:
            base_path: Directory containing config files

        Returns:
            Validated Config object

        Raises:
            ValidationError: If config files invalid
            FileNotFoundError: If config files missing
        """
        import yaml
        from pathlib import Path

        config_dir = Path(base_path)

        # Load YAML files
        with open(config_dir / "hardware.yaml") as f:
            hardware_yaml = yaml.safe_load(f)

        with open(config_dir / "safety.yaml") as f:
            safety_yaml = yaml.safe_load(f)

        with open(config_dir / "application.yaml") as f:
            app_yaml = yaml.safe_load(f)

        # Create config object with loaded values
        config = cls()
        config.hardware = HardwareConfig(**hardware_yaml)
        config.safety = SafetyConfig(**safety_yaml)
        config.application = ApplicationConfig(**app_yaml)

        return config
```

### Configuration Files

**config/hardware.yaml:**
```yaml
# TOSCA Hardware Configuration
# Version: 1.0
# Last Updated: 2025-10-25

photodiode:
  mw_per_volt: 400.0
  calibration_date: "2025-10-25"
  calibration_certificate: "CAL-2025-1001"

laser:
  max_current_ma: 2000.0
  max_power_mw: 2000.0
  max_temperature_c: 35.0
  min_temperature_c: 15.0

gpio:
  vibration_debounce_threshold: 3
  monitor_interval_ms: 100
```

**config/safety.yaml:**
```yaml
# TOSCA Safety Configuration
# Version: 1.0
# Last Updated: 2025-10-25

watchdog_timeout_ms: 1000
watchdog_heartbeat_interval_ms: 500

max_treatment_duration_sec: 300
require_session: true
```

**config/application.yaml:**
```yaml
# TOSCA Application Configuration
# Version: 1.0

log_level: "INFO"
data_directory: "./data"
session_video_directory: "./data/sessions"
```

---

## Implementation Tasks

### Task 1: Create Configuration System

**File:** `src/core/config.py`

**Steps:**
1. Install Pydantic: `pip install pydantic pydantic-settings PyYAML`
2. Add to requirements.txt
3. Create config.py with all settings classes (see above)
4. Add validation tests

**Testing:**
```python
# tests/test_config.py
import pytest
from pydantic import ValidationError
from src.core.config import Config, LaserConfig

def test_laser_config_valid():
    """Test valid laser configuration."""
    config = LaserConfig(
        max_current_ma=1500.0,
        max_power_mw=1500.0,
        max_temperature_c=30.0,
        min_temperature_c=20.0
    )
    assert config.max_current_ma == 1500.0

def test_laser_config_invalid_current():
    """Test invalid current rejected."""
    with pytest.raises(ValidationError):
        LaserConfig(max_current_ma=-100.0)  # Negative current

def test_laser_config_invalid_temp_range():
    """Test invalid temperature range rejected."""
    with pytest.raises(ValidationError):
        LaserConfig(
            max_temperature_c=20.0,
            min_temperature_c=30.0  # Min > Max
        )

def test_config_load_from_yaml(tmp_path):
    """Test loading config from YAML files."""
    # Create temp config files
    hardware_yaml = tmp_path / "hardware.yaml"
    hardware_yaml.write_text("""
photodiode:
  mw_per_volt: 400.0
laser:
  max_current_ma: 2000.0
  max_power_mw: 2000.0
  max_temperature_c: 35.0
  min_temperature_c: 15.0
gpio:
  vibration_debounce_threshold: 3
  monitor_interval_ms: 100
""")

    config = Config.load_from_files(str(tmp_path))
    assert config.hardware.laser.max_current_ma == 2000.0
```

---

### Task 2: Create Configuration Files

**Steps:**
1. Create `config/` directory
2. Create hardware.yaml, safety.yaml, application.yaml
3. Populate with current hardcoded values
4. Add to git (these ARE part of the codebase)

---

### Task 3: Migrate Controllers to Use Config

**Migration Strategy:** One controller at a time, test after each.

#### 3a. Migrate LaserController

**Before:**
```python
# laser_controller.py:59-62
self.max_current_ma = 2000.0
self.max_power_mw = 2000.0
self.max_temperature_c = 35.0
self.min_temperature_c = 15.0
```

**After:**
```python
# laser_controller.py
from src.core.config import Config

class LaserController(QObject):
    def __init__(self, event_logger=None, config: Config = None):
        super().__init__()

        # Load config (use default if not provided)
        if config is None:
            config = Config.load_from_files()

        self.config = config

        # Use config values instead of hardcoded
        self.max_current_ma = config.hardware.laser.max_current_ma
        self.max_power_mw = config.hardware.laser.max_power_mw
        self.max_temperature_c = config.hardware.laser.max_temperature_c
        self.min_temperature_c = config.hardware.laser.min_temperature_c
```

**Testing:**
```python
# tests/test_laser_controller_config.py
def test_laser_controller_uses_config():
    """Test laser controller loads limits from config."""
    custom_config = Config()
    custom_config.hardware.laser.max_current_ma = 1000.0

    controller = LaserController(config=custom_config)

    assert controller.max_current_ma == 1000.0
```

#### 3b. Migrate GPIOController

**Before:**
```python
# gpio_controller.py:91-93
self.photodiode_voltage_to_power = 400.0
self.vibration_debounce_threshold = 3
```

**After:**
```python
from src.core.config import Config

class GPIOController(QObject):
    def __init__(self, event_logger=None, config: Config = None):
        super().__init__()

        if config is None:
            config = Config.load_from_files()

        self.config = config

        # Use config values
        self.photodiode_voltage_to_power = config.hardware.photodiode.mw_per_volt
        self.vibration_debounce_threshold = config.hardware.gpio.vibration_debounce_threshold
        self.monitor_timer.setInterval(config.hardware.gpio.monitor_interval_ms)
```

#### 3c. Migrate SafetyManager

**Migrate all safety thresholds to safety.yaml**

---

### Task 4: Update MainWindow to Load Config

**File:** `src/ui/main_window.py`

**Changes:**
```python
from src.core.config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load configuration
        try:
            self.config = Config.load_from_files("config")
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.critical(f"Failed to load configuration: {e}")
            # Show error dialog to user
            QMessageBox.critical(
                None,
                "Configuration Error",
                f"Failed to load system configuration:\n{e}\n\n"
                "Please check config files in config/ directory."
            )
            sys.exit(1)

        # Pass config to controllers
        # (Updated in later task when connecting controllers)
```

---

### Task 5: Configuration Validation on Startup

**Add startup validation:**

```python
# src/core/config.py
class Config:
    def validate(self) -> List[str]:
        """
        Perform additional cross-field validation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate watchdog timing
        if self.safety.watchdog_heartbeat_interval_ms >= self.safety.watchdog_timeout_ms / 2:
            errors.append(
                "Watchdog heartbeat interval must be less than half of timeout "
                f"(heartbeat: {self.safety.watchdog_heartbeat_interval_ms}ms, "
                f"timeout: {self.safety.watchdog_timeout_ms}ms)"
            )

        # Validate laser temperature range
        if self.hardware.laser.min_temperature_c >= self.hardware.laser.max_temperature_c:
            errors.append(
                f"Laser min temperature ({self.hardware.laser.min_temperature_c}°C) "
                f"must be less than max temperature ({self.hardware.laser.max_temperature_c}°C)"
            )

        return errors

# In main.py or main_window.py
config = Config.load_from_files()
errors = config.validate()
if errors:
    logger.critical(f"Configuration validation failed:\n" + "\n".join(errors))
    sys.exit(1)
```

---

### Task 6: Environment Variable Overrides

**Testing/Development overrides:**

```bash
# Override laser max current for testing
export TOSCA_LASER__MAX_CURRENT_MA=1000

# Override log level
export TOSCA_LOG_LEVEL=DEBUG

python src/main.py
```

Pydantic automatically loads these environment variables.

---

### Task 7: Configuration Versioning

**Add version tracking to config files:**

```yaml
# config/hardware.yaml
config_version: "1.0"
schema_version: "1.0"
last_updated: "2025-10-25"
updated_by: "Development Team"

# ... rest of config
```

**Add migration system:**

```python
# src/core/config_migration.py
def migrate_config_if_needed(config_path: str) -> None:
    """
    Migrate config files to latest version if needed.

    Args:
        config_path: Path to config directory
    """
    with open(f"{config_path}/hardware.yaml") as f:
        data = yaml.safe_load(f)

    current_version = data.get("config_version", "0.0")

    if current_version == "1.0":
        return  # Already latest

    # Migration logic here
    if current_version == "0.0":
        migrate_0_to_1(data, f"{config_path}/hardware.yaml")
```

---

## Testing Plan

### Unit Tests

1. **Config Loading:**
   - Valid YAML files load successfully
   - Invalid YAML rejected with clear error
   - Missing files raise FileNotFoundError

2. **Validation:**
   - Invalid values rejected (negative, out of range)
   - Cross-field validation works (min < max)
   - Type checking enforced

3. **Environment Overrides:**
   - Environment variables override YAML
   - Nested config overrides work (`TOSCA_LASER__MAX_CURRENT_MA`)

### Integration Tests

1. **Controller Integration:**
   - LaserController uses config limits
   - GPIOController uses config calibration
   - SafetyManager uses config thresholds

2. **Startup Validation:**
   - Invalid config prevents startup
   - Error messages are user-friendly
   - Config errors logged to event log

### Manual Tests

1. **Config File Editing:**
   - Edit hardware.yaml, restart app
   - Verify new values loaded
   - Verify validation catches errors

2. **Environment Override:**
   - Set `TOSCA_LASER__MAX_CURRENT_MA=1000`
   - Start app
   - Verify laser controller uses 1000mA limit

---

## Documentation

### Files to Create/Update

1. **docs/configuration/README.md:**
   - Configuration file format
   - How to modify configs
   - Validation rules
   - Environment overrides

2. **config/README.md:**
   - Config file descriptions
   - Version history
   - Migration guide

3. **docs/project/CODING_STANDARDS.md:**
   - Add: "All constants must be in config files"
   - Add: "Config changes require justification in commit message"

---

## Rollback Plan

If config system causes issues:

1. **Temporary Fallback:**
   ```python
   # In each controller
   def __init__(self, config: Config = None):
       if config is None:
           # Fallback to hardcoded values
           self.max_current_ma = 2000.0  # Hardcoded fallback
       else:
           self.max_current_ma = config.hardware.laser.max_current_ma
   ```

2. **Full Rollback:**
   - Git revert config system commits
   - Restore hardcoded values
   - Remove config files

---

## Success Criteria

- [ ] All hardcoded constants migrated to config
- [ ] Config validation catches all error types
- [ ] Unit tests pass (>95% coverage)
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] Config files version controlled
- [ ] Environment overrides working
- [ ] No regressions in controller behavior

---

**Status:** Ready for implementation
**Estimated Effort:** 2-3 days
**Priority:** HIGH - Complete before production deployment
