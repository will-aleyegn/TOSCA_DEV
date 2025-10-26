# TOSCA Hardware Mocks - Testing Guide

**Purpose:** Comprehensive hardware mocking layer for testing TOSCA controllers without physical devices

**Status:** Complete - 4 mocks, 54 tests passing, mypy zero errors

---

## Overview

The TOSCA hardware mock layer provides realistic simulation of all four hardware controllers:
- **Camera** (Allied Vision 1800 U-158c)
- **Laser** (Arroyo Instruments TEC Controller)
- **Actuator** (Xeryon Linear Stage)
- **GPIO** (Arduino Nano Safety Interlocks)

**Architecture:**
```
MockHardwareBase (QObject + ABC)     MockQObjectBase (QObject)
        ↓                                    ↓
   [Not used]                         MockCameraController
                                      MockLaserController
                                      MockActuatorController
                                      MockGPIOController
```

---

## Quick Start

### Basic Usage

```python
import sys
from pathlib import Path
from PyQt6.QtCore import QCoreApplication

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import MockLaserController

# Create QCoreApplication (required for PyQt6)
app = QCoreApplication.instance() or QCoreApplication(sys.argv)

# Create mock
mock = MockLaserController()

# Connect
assert mock.connect(com_port="COM4") is True
assert mock.is_connected is True

# Control laser
mock.set_output(True)
mock.set_power(1000.0)  # 1000 mW

# Verify behavior
assert mock.is_output_enabled is True
assert mock.power_setpoint_mw == 1000.0
assert ("set_power", {"power_mw": 1000.0}) in mock.call_log
```

---

## Architecture

### Two Base Classes

**1. MockHardwareBase** (for HardwareControllerBase descendants)
- Inherits from `HardwareControllerBase` (QObject + ABC)
- Implements abstract methods: `connect()`, `disconnect()`, `get_status()`
- **Currently unused** - Camera/Laser/Actuator/GPIO inherit from QObject directly

**2. MockQObjectBase** (for QObject descendants)
- Lightweight base for all current mocks
- Provides: call logging, delay simulation, error injection, reset
- **All 4 current mocks extend this**

### Design Patterns

**Factory Pattern:** Device-specific mocks extend common base
**Observer Pattern:** PyQt6 signals for state changes
**Template Method:** `reset()` chain for test isolation
**DRY Principle:** Shared functionality in base classes

---

## Mock Controllers

### 1. MockCameraController

**Simulates:** Allied Vision 1800 U-158c camera

**Features:**
- Frame generation via QTimer at configurable FPS (default 30)
- Streaming control (start/stop)
- Recording simulation
- Exposure and gain settings
- Configurable frame shape (default 480x640x3)

**Signals:**
- `frame_ready(np.ndarray)` - New frame available
- `fps_update(float)` - FPS update
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message
- `recording_status_changed(bool)` - Recording state

**Example:**
```python
from tests.mocks import MockCameraController

mock = MockCameraController()
mock.connect(camera_id="CAM123")
mock.start_streaming()

# Manually trigger frame (or wait for timer)
mock._generate_frame()
assert mock.latest_frame is not None
assert mock.latest_frame.shape == (480, 640, 3)
```

### 2. MockLaserController

**Simulates:** Arroyo Instruments laser driver

**Features:**
- Power control (0-2000 mW with limit enforcement)
- Current control (0-2000 mA with limit enforcement)
- TEC temperature control (15-35°C range)
- Output enable/disable (affects readings)
- Automatic output disable on disconnect
- Safety limit warnings

**Signals:**
- `power_changed(float)` - Power in mW
- `current_changed(float)` - Current in mA
- `temperature_changed(float)` - Temperature in °C
- `output_changed(bool)` - Output state
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message
- `status_changed(str)` - Status description
- `limit_warning(str)` - Limit violation warning

**Example:**
```python
from tests.mocks import MockLaserController

mock = MockLaserController()
mock.connect()

# Set power and current
mock.set_power(1500.0)  # 1500 mW
mock.set_current(1200.0)  # 1200 mA

# Enable output
mock.set_output(True)
assert mock.read_power() == 1500.0
assert mock.read_current() == 1200.0

# Disable output - readings go to zero
mock.set_output(False)
assert mock.read_power() == 0.0
```

### 3. MockActuatorController

**Simulates:** Xeryon linear stage

**Features:**
- Position tracking with stateful simulation
- Homing sequence via QTimer (configurable delay)
- Absolute position movement (`set_position`)
- Relative step movement (`make_step`)
- Continuous scanning with auto-stop at limits
- Hardware limit validation (-45000 to +45000 µm)
- Limit proximity warnings (within 1mm)
- Speed control (µm/s)

**Signals:**
- `position_changed(float)` - Current position in µm
- `position_reached(float)` - Target reached
- `status_changed(str)` - Status: homing, moving, ready, error
- `homing_progress(str)` - Homing status updates
- `limits_changed(float, float)` - Low/high limits
- `limit_warning(str, float)` - Direction, distance from limit
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message

**Example:**
```python
from tests.mocks import MockActuatorController

mock = MockActuatorController()
mock.connect(auto_home=False)

# Home the actuator
mock.find_index()
mock._complete_homing()  # Simulate completion
assert mock.is_homed is True

# Move to position
mock.set_position(10000.0)  # 10mm
mock._complete_movement()  # Simulate completion
assert mock.current_position_um == 10000.0
```

### 4. MockGPIOController

**Simulates:** Arduino Nano safety interlocks

**Features:**
- Watchdog heartbeat tracking (count + timestamp)
- Smoothing motor control (start/stop)
- Vibration detection (correlated with motor state)
- Aiming laser control (start/stop)
- Photodiode voltage simulation (0-5V)
- Photodiode power calculation (voltage × 400 mW/V)
- Safety interlock status (motor AND vibration required)
- QTimer-based sensor monitoring (100ms)

**Signals:**
- `smoothing_motor_changed(bool)` - Motor state
- `smoothing_vibration_changed(bool)` - Vibration detected
- `photodiode_voltage_changed(float)` - Voltage in V
- `photodiode_power_changed(float)` - Power in mW
- `aiming_laser_changed(bool)` - Aiming laser state
- `safety_interlock_changed(bool)` - Safety OK status
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message

**Example:**
```python
from tests.mocks import MockGPIOController

mock = MockGPIOController()
mock.connect(port="COM4")

# Start motor - vibration auto-detected
mock.start_smoothing_motor()
assert mock.motor_enabled is True
assert mock.vibration_detected is True

# Check safety status (requires both)
assert mock.get_safety_status() is True

# Send watchdog heartbeat
mock.send_watchdog_heartbeat()
assert mock.heartbeat_count == 1
```

---

## Common Patterns

### 1. Call Logging

All mocks log method calls for test verification:

```python
mock = MockLaserController()
mock.connect(com_port="COM4", baudrate=38400)

assert ("connect", {"com_port": "COM4", "baudrate": 38400}) in mock.call_log
```

### 2. Error Simulation

```python
mock = MockCameraController()
mock.simulate_connection_failure = True

result = mock.connect()
assert result is False
assert mock.is_connected is False
```

### 3. Response Delay Simulation

```python
import time

mock = MockLaserController()
mock.response_delay_s = 0.5  # 500ms delay

start = time.time()
mock.connect()
elapsed = time.time() - start
assert elapsed >= 0.5
```

### 4. Operation Error Simulation

```python
mock = MockActuatorController()
mock.connect()
mock.simulate_operation_error = True
mock.error_message = "Simulated hardware fault"

result = mock.set_position(1000.0)
assert result is False
```

### 5. Test Isolation with Reset

```python
def test_example():
    mock = MockLaserController()
    mock.connect()
    mock.set_power(1000.0)

    # Reset for next test
    mock.reset()
    assert mock.is_connected is False
    assert mock.power_setpoint_mw == 0.0
    assert len(mock.call_log) == 0
```

### 6. Signal Testing

```python
from PyQt6.QtCore import QSignalSpy

mock = MockLaserController()
spy = QSignalSpy(mock.power_changed)

mock.connect()
mock.set_power(1500.0)
mock.set_output(True)

assert len(spy) == 1
assert spy[0][0] == 1500.0
```

---

## Testing Best Practices

### PyQt6 Application Required

All tests must create a `QCoreApplication`:

```python
from PyQt6.QtCore import QCoreApplication
import sys

app = QCoreApplication.instance() or QCoreApplication(sys.argv)
```

### Use Reset Between Tests

Ensure test isolation:

```python
def test_feature_a():
    mock = MockLaserController()
    # ... test ...
    mock.reset()

def test_feature_b():
    mock = MockLaserController()
    # ... test ...
    mock.reset()
```

### Verify Both Return Value and State

```python
# Good - checks both
result = mock.set_power(1000.0)
assert result is True
assert mock.power_setpoint_mw == 1000.0

# Incomplete - only checks return
result = mock.set_power(1000.0)
assert result is True
```

### Test Failure Modes

```python
# Test limit enforcement
mock.connect()
result = mock.set_power(5000.0)  # Exceeds 2000 mW limit
assert result is False

# Test requires-connection
mock2 = MockLaserController()
result = mock2.set_power(1000.0)  # Not connected
assert result is False
```

---

## API Reference

### MockQObjectBase (Base Class)

**Configuration Attributes:**
- `simulate_connection_failure: bool` - Fail connect() calls
- `simulate_operation_error: bool` - Fail operation calls
- `error_message: str` - Custom error message
- `response_delay_s: float` - Simulated delay (seconds)

**State Tracking:**
- `call_log: list[tuple[str, dict]]` - All method calls recorded

**Methods:**
- `reset() -> None` - Reset to clean state
- `_log_call(func_name: str, **kwargs) -> None` - Log method call
- `_apply_delay() -> None` - Apply configured delay

### MockCameraController

**Additional Attributes:**
- `simulated_fps: int` - Frame generation rate (default: 30)
- `simulated_frame_shape: tuple[int, int, int]` - Frame dimensions (default: 480x640x3)
- `is_connected: bool` - Connection state
- `is_streaming: bool` - Streaming state
- `is_recording: bool` - Recording state
- `latest_frame: Optional[np.ndarray]` - Last generated frame
- `exposure_us: float` - Exposure time in microseconds
- `gain_db: float` - Gain in dB

**Methods:**
- `connect(camera_id: str = "CAM000") -> bool`
- `disconnect() -> None`
- `start_streaming() -> bool`
- `stop_streaming() -> bool`
- `start_recording(filename: str) -> bool`
- `stop_recording() -> bool`
- `set_exposure(exposure_us: float) -> bool`
- `set_gain(gain_db: float) -> bool`
- `_generate_frame() -> None` - Manual frame generation

### MockLaserController

**Additional Attributes:**
- `is_connected: bool` - Connection state
- `is_output_enabled: bool` - Output state
- `current_setpoint_ma: float` - Current setpoint (mA)
- `power_setpoint_mw: float` - Power setpoint (mW)
- `temperature_setpoint_c: float` - TEC setpoint (°C)
- `max_current_ma: float` - Current limit (default: 2000.0)
- `max_power_mw: float` - Power limit (default: 2000.0)
- `max_temperature_c: float` - Max temp (default: 35.0)
- `min_temperature_c: float` - Min temp (default: 15.0)

**Methods:**
- `connect(com_port: str = "COM4", baudrate: int = 38400) -> bool`
- `disconnect() -> None`
- `set_output(enabled: bool) -> bool`
- `set_current(current_ma: float) -> bool`
- `set_power(power_mw: float) -> bool`
- `set_temperature(temperature_c: float) -> bool`
- `read_current() -> Optional[float]`
- `read_power() -> Optional[float]`
- `read_temperature() -> Optional[float]`

### MockActuatorController

**Additional Attributes:**
- `is_connected: bool` - Connection state
- `is_homed: bool` - Homing state
- `is_scanning: bool` - Scanning state
- `current_position_um: float` - Current position (µm)
- `target_position_um: float` - Target position (µm)
- `low_limit_um: float` - Low limit (default: -45000.0)
- `high_limit_um: float` - High limit (default: 45000.0)
- `speed_um_per_s: int` - Movement speed (default: 10000)
- `homing_delay_ms: int` - Homing simulation delay (default: 200)

**Methods:**
- `connect(com_port: str = "COM3", baudrate: int = 9600, auto_home: bool = True) -> bool`
- `disconnect() -> None`
- `find_index() -> bool` - Start homing
- `set_position(position_um: float) -> bool` - Absolute move
- `make_step(step_um: float) -> bool` - Relative move
- `get_position() -> Optional[float]`
- `set_speed(speed: int) -> bool`
- `start_scan(direction: int) -> bool` - Continuous scanning
- `stop_scan() -> bool`
- `stop_movement() -> bool`
- `set_position_limits(low_um: float, high_um: float) -> bool`
- `get_limits() -> tuple[float, float]`
- `validate_position(target_position_um: float) -> tuple[bool, str]`
- `_complete_homing() -> None` - Manual homing completion
- `_complete_movement() -> None` - Manual movement completion

### MockGPIOController

**Additional Attributes:**
- `is_connected: bool` - Connection state
- `motor_enabled: bool` - Motor state
- `aiming_laser_enabled: bool` - Aiming laser state
- `vibration_detected: bool` - Vibration sensor state
- `photodiode_voltage: float` - Photodiode voltage (V)
- `photodiode_power_mw: float` - Calculated power (mW)
- `photodiode_voltage_to_power: float` - Calibration (default: 400.0)
- `heartbeat_count: int` - Watchdog heartbeat counter
- `last_heartbeat_time: Optional[float]` - Last heartbeat timestamp
- `simulate_vibration_when_motor_on: bool` - Realistic behavior (default: True)

**Methods:**
- `connect(port: str = "COM4") -> bool`
- `disconnect() -> None`
- `send_watchdog_heartbeat() -> bool`
- `start_smoothing_motor() -> bool`
- `stop_smoothing_motor() -> bool`
- `start_aiming_laser() -> bool`
- `stop_aiming_laser() -> bool`
- `get_safety_status() -> bool` - Returns motor AND vibration
- `get_photodiode_voltage() -> float`
- `get_photodiode_power() -> float`
- `_update_status() -> None` - Manual sensor update

---

## Test Examples

See the following test files for complete examples:
- `tests/test_mock_hardware_base.py` - Base class tests
- `tests/test_mock_camera.py` - Camera mock tests (7 tests)
- `tests/test_mock_laser.py` - Laser mock tests (12 tests)
- `tests/test_mock_actuator.py` - Actuator mock tests (16 tests)
- `tests/test_mock_gpio.py` - GPIO mock tests (14 tests)

**Total: 54 tests, all passing**

---

## Future Enhancements (Nice-to-Have)

The following enhancements would improve the mock layer but are not currently implemented:

### 1. Pytest Fixtures
Create `tests/conftest.py` with reusable fixtures:
```python
@pytest.fixture
def camera_mock():
    """Provide connected camera mock."""
    mock = MockCameraController()
    mock.connect()
    yield mock
    mock.reset()
```

### 2. Advanced Patterns Guide
Document complex scenarios:
- Multi-device coordination testing
- Timing simulation for protocol execution
- Race condition testing
- Error recovery testing

### 3. Comparison with Real Hardware
Document behavioral differences:
- Timing accuracy (mocks are faster)
- Edge cases (real hardware may have quirks)
- Physical limits (real hardware has inertia, latency)

### 4. Mock Performance Profiling
Add timing measurements:
- Call overhead
- Signal emission latency
- Memory usage per mock

---

## Version Information

**Created:** 2025-10-26
**Status:** Complete
**Test Coverage:** 54/54 passing
**Type Safety:** mypy zero errors
**Dependencies:** PyQt6, numpy (camera only)

---

**End of Mock Documentation**
