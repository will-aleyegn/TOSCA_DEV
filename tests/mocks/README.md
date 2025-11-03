# TOSCA Hardware Mocks - Comprehensive Testing Guide

**Purpose:** Production-ready hardware mocking layer for testing TOSCA controllers without physical devices

**Status:** Complete - 5 mock controllers, 100+ tests passing, mypy zero errors

**Last Updated:** 2025-11-02

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Mock Controllers](#mock-controllers)
   - [MockCameraController](#1-mockcameracontroller)
   - [MockLaserController](#2-mocklasercontroller)
   - [MockTECController](#3-mockteccontroller)
   - [MockActuatorController](#4-mockactuatorcontroller)
   - [MockGPIOController](#5-mockgpiocontroller)
5. [Advanced Features](#advanced-features)
   - [VmbPy API Compliance](#vmbpy-api-compliance)
   - [Failure Mode Simulation](#failure-mode-simulation)
   - [Signal Validation Framework](#signal-validation-framework)
6. [Common Patterns](#common-patterns)
7. [Testing Best Practices](#testing-best-practices)
8. [API Reference](#api-reference)
9. [Test Examples](#test-examples)

---

## Overview

The TOSCA hardware mock layer provides realistic simulation of all five hardware controllers:
- **Camera** (Allied Vision 1800 U-158c with VmbPy API)
- **Laser** (Arroyo Instruments Laser Driver)
- **TEC** (Arroyo Instruments TEC Controller)
- **Actuator** (Xeryon Linear Stage)
- **GPIO** (Arduino Nano Safety Interlocks)

**Architecture:**
```
MockHardwareBase (QObject + ABC)     MockQObjectBase (QObject)
        ↓                                    ↓
   [Not used]                         MockCameraController
                                      MockLaserController
                                      MockTECController
                                      MockActuatorController
                                      MockGPIOController
```

**Key Features:**
- ✅ **Full VmbPy API compliance** - Pixel formats, binning, trigger modes
- ✅ **Advanced failure simulation** - 9 failure modes with realistic behavior
- ✅ **Signal validation framework** - Comprehensive signal emission tracking
- ✅ **Thermal simulation** - Realistic TEC temperature lag modeling
- ✅ **Thread-safe** - Designed for concurrent testing
- ✅ **Type-safe** - Full type hints, mypy verified

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
- **Currently unused** - All mocks inherit from QObject directly

**2. MockQObjectBase** (for QObject descendants)
- Lightweight base for all current mocks
- Provides: call logging, delay simulation, advanced failure modes, signal tracking
- **All 5 current mocks extend this**

### Design Patterns

**Factory Pattern:** Device-specific mocks extend common base
**Observer Pattern:** PyQt6 signals for state changes
**Template Method:** `reset()` chain for test isolation
**Strategy Pattern:** Configurable failure modes and behaviors

---

## Mock Controllers

### 1. MockCameraController

**Simulates:** Allied Vision 1800 U-158c camera with VmbPy API compliance

**Features:**
- ✅ **VmbPy API Compliance** - Full pixel format, binning, trigger mode support
- Frame generation via QTimer at configurable FPS (1-120 FPS)
- Pixel format support (Bgr8, Rgb8, Mono8) with correct array shapes
- Hardware binning simulation (1x, 2x, 4x, 8x)
- Trigger modes (Continuous, Software, Hardware)
- Acquisition modes (Continuous, SingleFrame, MultiFrame)
- Streaming control (start/stop)
- Recording simulation
- Exposure and gain settings (with hardware feedback)
- Memory-contiguous frame generation (QImage compatible)

**Signals:**
- `frame_ready(np.ndarray)` - New frame available
- `fps_update(float)` - FPS update
- `pixel_format_changed(str)` - Pixel format changed
- `binning_changed(int)` - Binning factor changed
- `trigger_mode_changed(str)` - Trigger mode changed
- `acquisition_mode_changed(str)` - Acquisition mode changed
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message
- `recording_status_changed(bool)` - Recording state

**Example:**
```python
from tests.mocks import MockCameraController

mock = MockCameraController()
mock.connect(camera_id="CAM123")

# Configure pixel format and binning
mock.set_pixel_format("Bgr8")  # 3-channel BGR
mock.set_binning(2)  # 2x2 binning

# Start streaming
mock.start_streaming()

# Manually trigger frame (or wait for timer)
mock._generate_frame()
assert mock.latest_frame is not None
assert mock.latest_frame.shape == (240, 320, 3)  # Half size due to 2x binning
```

---

### 2. MockLaserController

**Simulates:** Arroyo Instruments laser driver (COM10, 38400 baud)

**Features:**
- Power control (0-2000 mW with limit enforcement)
- Current control (0-2000 mA with limit enforcement)
- Output enable/disable (affects readings)
- Automatic output disable on disconnect
- Safety limit warnings

**Signals:**
- `power_changed(float)` - Power in mW
- `current_changed(float)` - Current in mA
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

---

### 3. MockTECController

**Simulates:** Arroyo 5305 TEC (Thermoelectric Cooler) controller (COM9, 38400 baud)

**Features:**
- Temperature setpoint control (15-35°C range)
- Realistic thermal lag simulation (exponential decay model)
- PID control simulation (proportional control)
- Output enable/disable
- Current and voltage monitoring (simulated from temperature error)
- Ambient temperature drift when output disabled
- Configurable thermal time constant (default: 5 seconds)
- Safety limit enforcement

**Signals:**
- `temperature_changed(float)` - Actual temperature in °C
- `temperature_setpoint_changed(float)` - Setpoint temperature in °C
- `output_changed(bool)` - Output enabled/disabled
- `current_changed(float)` - TEC current in A
- `voltage_changed(float)` - TEC voltage in V
- `status_changed(str)` - Status description
- `limit_warning(str)` - Limit warning message
- `connection_changed(bool)` - Connection status
- `error_occurred(str)` - Error message

**Thermal Simulation Model:**
```
T(t) = T_setpoint + (T_initial - T_setpoint) × exp(-t/τ)
```
Where τ is the thermal time constant (time to reach 63% of target).

**Example:**
```python
from tests.mocks import MockTECController
import time

mock = MockTECController()
mock.connect(com_port="COM9")

# Set temperature and enable output
mock.set_temperature(20.0)  # Target: 20°C
mock.set_output(True)

# Read temperature - starts at ambient (25°C)
temp = mock.read_temperature()
assert temp == 25.0

# Wait for thermal response (exponential approach)
time.sleep(1.0)
temp = mock.read_temperature()
assert temp < 25.0  # Cooling toward 20°C

# Check TEC power consumption
current = mock.read_current()
voltage = mock.read_voltage()
assert current > 0.0  # Active cooling draws current
```

**Advanced Configuration:**
```python
# Adjust thermal simulation parameters
mock.set_thermal_time_constant(10.0)  # Slower thermal response
mock.set_ambient_temperature(30.0)  # Higher ambient temp

# Force specific temperature for edge case testing
mock.force_temperature(15.5)  # Test at lower limit
```

---

### 4. MockActuatorController

**Simulates:** Xeryon linear stage (COM3, 9600 baud)

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

---

### 5. MockGPIOController

**Simulates:** Arduino Nano safety interlocks (COM4, 115200 baud)

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

## Advanced Features

### VmbPy API Compliance

MockCameraController fully implements VmbPy API patterns used in production:

#### Pixel Formats
```python
from tests.mocks import MockCameraController

mock = MockCameraController()
mock.connect()

# Bgr8 - 3-channel BGR (default, preferred format)
mock.set_pixel_format("Bgr8")
frame = mock.latest_frame
assert frame.shape == (480, 640, 3)  # Height × Width × Channels

# Rgb8 - 3-channel RGB (fallback)
mock.set_pixel_format("Rgb8")
frame = mock.latest_frame
assert frame.shape == (480, 640, 3)

# Mono8 - Single-channel grayscale
mock.set_pixel_format("Mono8")
frame = mock.latest_frame
assert frame.shape == (480, 640)  # 2D array
```

#### Hardware Binning
```python
# 1x1 binning - Full resolution (default)
mock.set_binning(1)
assert mock.get_frame_shape() == (480, 640, 3)

# 2x2 binning - Half resolution
mock.set_binning(2)
assert mock.get_frame_shape() == (240, 320, 3)

# 4x4 binning - Quarter resolution
mock.set_binning(4)
assert mock.get_frame_shape() == (120, 160, 3)

# 8x8 binning - Eighth resolution
mock.set_binning(8)
assert mock.get_frame_shape() == (60, 80, 3)
```

#### Trigger Modes
```python
# Continuous mode - Auto-generate frames at configured FPS
mock.set_trigger_mode("Continuous")
mock.start_streaming()
# Frames emit automatically via QTimer

# Software trigger - Generate frames on demand
mock.set_trigger_mode("Software")
mock.start_streaming()
mock.trigger_frame()  # Manually trigger single frame

# Hardware trigger - Simulate external trigger
mock.set_trigger_mode("Hardware")
mock.start_streaming()
mock._simulate_hardware_trigger()  # Simulate trigger signal
```

#### Acquisition Modes
```python
# Continuous - Stream indefinitely
mock.set_acquisition_mode("Continuous")

# SingleFrame - Capture one frame then stop
mock.set_acquisition_mode("SingleFrame")
mock.start_streaming()
# Automatically stops after one frame

# MultiFrame - Capture N frames then stop
mock.set_acquisition_mode("MultiFrame")
mock.set_frame_count(10)
mock.start_streaming()
# Automatically stops after 10 frames
```

#### Frame Rate Control
```python
# Hardware FPS control (1-120 FPS)
mock.set_hardware_fps(60)  # 60 FPS
# QTimer automatically adjusts to 16.67ms intervals

mock.set_hardware_fps(30)  # 30 FPS (default)
# QTimer automatically adjusts to 33.33ms intervals
```

#### Memory-Contiguous Frames
All generated frames use `np.ascontiguousarray()` to ensure compatibility with Qt's QImage constructor:

```python
frame = mock.latest_frame
assert frame.flags['C_CONTIGUOUS'] is True  # C-contiguous memory layout
```

---

### Failure Mode Simulation

MockQObjectBase provides advanced failure simulation with 9 distinct failure modes:

#### Available Failure Modes

```python
from tests.mocks.mock_qobject_base import FailureMode

class FailureMode(Enum):
    NONE = "none"                                    # No failures
    CONNECTION_FAILURE = "connection_failure"        # Connection fails
    OPERATION_ERROR = "operation_error"              # Operations fail
    TIMEOUT = "timeout"                              # Operations time out
    DEVICE_BUSY = "device_busy"                      # Device temporarily unavailable
    COMMUNICATION_ERROR = "communication_error"      # Serial comm errors
    POWER_FAILURE = "power_failure"                  # Insufficient power
    CALIBRATION_ERROR = "calibration_error"          # Calibration required
    HARDWARE_LIMIT_VIOLATION = "hardware_limit_violation"  # Physical limits exceeded
    INTERMITTENT_FAILURE = "intermittent_failure"    # Random failures
```

#### Basic Failure Simulation (Backward Compatible)

```python
from tests.mocks import MockLaserController

mock = MockLaserController()

# Connection failure
mock.simulate_connection_failure = True
result = mock.connect()
assert result is False

# Operation error
mock.connect()
mock.simulate_operation_error = True
mock.error_message = "Simulated hardware fault"
result = mock.set_power(1000.0)
assert result is False
```

#### Advanced Failure Modes

**1. Intermittent Failures (Random Failure Injection)**
```python
mock = MockLaserController()
mock.connect()

# 30% chance of failure on each operation
mock.failure_mode = FailureMode.INTERMITTENT_FAILURE
mock.intermittent_failure_probability = 0.3

# Operations randomly fail
for i in range(10):
    result = mock.set_power(1000.0)
    # ~3 of 10 operations will fail

# Check failure statistics
stats = mock.get_failure_statistics()
assert stats['failure_count'] > 0
```

**2. Timeout Simulation**
```python
mock = MockActuatorController()
mock.connect()

# Operations timeout after 2 seconds
mock.failure_mode = FailureMode.TIMEOUT
mock.timeout_threshold_s = 2.0

# Start long operation
mock._start_operation()
time.sleep(2.5)

# Next operation will timeout
result = mock.set_position(10000.0)
assert result is False
```

**3. Device Busy State**
```python
mock = MockCameraController()
mock.connect()

# Device busy for 3 seconds
mock.failure_mode = FailureMode.DEVICE_BUSY
mock.device_busy_duration_s = 3.0
mock._set_busy_state()

# Operations fail while busy
result = mock.start_streaming()
assert result is False

# Wait for device to become available
time.sleep(3.0)
result = mock.start_streaming()
assert result is True
```

**4. Power Supply Failure**
```python
mock = MockLaserController()
mock.connect()

# Simulate low power supply voltage
mock.failure_mode = FailureMode.POWER_FAILURE
mock.power_supply_voltage_v = 9.0  # Below minimum
mock.min_power_voltage_v = 10.0

# Operations fail due to insufficient power
result = mock.set_output(True)
assert result is False
```

**5. Calibration Error**
```python
mock = MockActuatorController()
mock.connect()

# Require calibration
mock.failure_mode = FailureMode.CALIBRATION_ERROR
mock.calibration_required = True

# Operations fail until calibrated
result = mock.set_position(1000.0)
assert result is False

# Perform calibration
mock.perform_calibration()
result = mock.set_position(1000.0)
assert result is True
```

**6. Hardware Limit Violations**
```python
mock = MockLaserController()
mock.connect()

# Set hardware limits
mock.hardware_limits['power_mw'] = (0.0, 1000.0)  # Max 1000 mW

# Exceeding limits fails
result = mock.set_power(1500.0)
assert result is False

# Within limits succeeds
result = mock.set_power(800.0)
assert result is True
```

**7. Error State Persistence**
```python
mock = MockTECController()
mock.connect()

# Enable persistent error states
mock.persist_error_state = True
mock._set_error_state("Temperature sensor malfunction")

# All subsequent operations fail with same error
assert mock.set_temperature(25.0) is False
assert mock.set_output(True) is False

# Must explicitly clear error
mock._clear_error_state()
assert mock.set_output(True) is True
```

#### Failure Statistics

```python
# Get comprehensive failure statistics
stats = mock.get_failure_statistics()

print(stats)
# {
#     'failure_count': 5,
#     'failure_mode': 'intermittent_failure',
#     'current_error_state': None,
#     'device_busy': False,
#     'operation_in_progress': False,
#     'calibration_required': False,
#     'power_voltage_v': 12.0,
#     'call_count': 25
# }
```

---

### Signal Validation Framework

MockQObjectBase provides comprehensive signal emission tracking and validation:

#### Signal Logging

```python
from tests.mocks import MockLaserController

mock = MockLaserController()
mock.connect()

# Enable signal logging (enabled by default)
mock.enable_signal_logging = True

# Perform operations that emit signals
mock.set_power(1500.0)
mock.set_output(True)

# Get all signal emissions
emissions = mock.get_signal_emissions()
for signal_name, args, timestamp in emissions:
    print(f"{signal_name}({args}) at {timestamp}")

# Filter by signal name
power_emissions = mock.get_signal_emissions("power_changed")
assert len(power_emissions) >= 1
```

#### Signal Verification Methods

**1. Check if Signal Was Emitted**
```python
assert mock.was_signal_emitted("power_changed")
assert mock.was_signal_emitted("output_changed")
assert not mock.was_signal_emitted("temperature_changed")  # Not emitted
```

**2. Get Emission Count**
```python
count = mock.get_signal_emission_count("power_changed")
assert count == 1

mock.set_power(2000.0)
count = mock.get_signal_emission_count("power_changed")
assert count == 2
```

**3. Get Last Signal Arguments**
```python
mock.set_power(1234.5)
args = mock.get_last_signal_args("power_changed")
assert args == (1234.5,)

mock.set_output(True)
args = mock.get_last_signal_args("output_changed")
assert args == (True,)
```

**4. Verify Signal Sequence**
```python
# Verify signals were emitted in correct order
mock.set_power(1000.0)
mock.set_output(True)
mock.set_power(1500.0)

assert mock.verify_signal_sequence(
    "power_changed",
    "output_changed",
    "power_changed"
)
```

**5. Signal Timing Analysis**
```python
# Get timestamp of last emission
timestamp = mock.get_signal_timing("power_changed")

# Get interval between last two emissions
interval = mock.get_signal_interval("power_changed")
assert interval < 1.0  # Less than 1 second between emissions
```

**6. Parameter Validation**
```python
# Verify signal was emitted with specific parameters
mock.set_power(1500.0)

assert mock.verify_signal_parameters(
    "power_changed",
    lambda args: args[0] == 1500.0
)

assert mock.verify_signal_parameters(
    "power_changed",
    lambda args: 1000.0 <= args[0] <= 2000.0
)
```

**7. Signal Statistics**
```python
# Get comprehensive signal statistics
stats = mock.get_signal_statistics()

print(stats)
# {
#     'total_signals': 15,
#     'unique_signals': 5,
#     'signal_counts': {
#         'power_changed': 4,
#         'output_changed': 2,
#         'current_changed': 3,
#         'connection_changed': 2,
#         'status_changed': 4
#     },
#     'first_signal': 'connection_changed',
#     'last_signal': 'power_changed',
#     'logging_enabled': True
# }
```

#### Integration with QSignalSpy

For more advanced testing, combine with Qt's QSignalSpy:

```python
from PyQt6.QtCore import QSignalSpy

mock = MockLaserController()

# Use QSignalSpy for Qt-native signal testing
spy = QSignalSpy(mock.power_changed)

mock.connect()
mock.set_power(1500.0)
mock.set_output(True)

# QSignalSpy captures emissions
assert len(spy) == 1
assert spy[0][0] == 1500.0

# MockQObjectBase also tracks them
assert mock.was_signal_emitted("power_changed")
assert mock.get_signal_emission_count("power_changed") == 1
```

---

## Common Patterns

### 1. Call Logging

All mocks log method calls for test verification:

```python
mock = MockLaserController()
mock.connect(com_port="COM4", baudrate=38400)
mock.set_power(1000.0)

assert ("connect", {"com_port": "COM4", "baudrate": 38400}) in mock.call_log
assert ("set_power", {"power_mw": 1000.0}) in mock.call_log
```

### 2. Response Delay Simulation

```python
import time

mock = MockLaserController()
mock.response_delay_s = 0.5  # 500ms delay

start = time.time()
mock.connect()
elapsed = time.time() - start
assert elapsed >= 0.5
```

### 3. Test Isolation with Reset

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
    assert len(mock.signal_log) == 0
```

### 4. Pytest Fixtures

Create reusable fixtures for common mock setups:

```python
import pytest
from tests.mocks import MockLaserController, MockCameraController

@pytest.fixture
def connected_laser():
    """Provide connected laser mock."""
    mock = MockLaserController()
    mock.connect()
    yield mock
    mock.reset()

@pytest.fixture
def streaming_camera():
    """Provide streaming camera mock."""
    mock = MockCameraController()
    mock.connect()
    mock.start_streaming()
    yield mock
    mock.stop_streaming()
    mock.reset()

def test_laser_power(connected_laser):
    assert connected_laser.set_power(1000.0) is True
    assert connected_laser.power_setpoint_mw == 1000.0
```

### 5. Multi-Device Coordination

Test interactions between multiple devices:

```python
from tests.mocks import MockLaserController, MockTECController

laser = MockLaserController()
tec = MockTECController()

# Connect both
laser.connect()
tec.connect()

# Enable TEC cooling
tec.set_temperature(20.0)
tec.set_output(True)

# Enable laser only after TEC is active
if tec.is_output_enabled:
    laser.set_output(True)
    laser.set_power(1500.0)
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

### Use Signal Validation

```python
mock = MockLaserController()
mock.connect()

# Clear signal log before test
mock.clear_signal_log()

# Perform operation
mock.set_power(1500.0)

# Verify signal emission
assert mock.was_signal_emitted("power_changed")
args = mock.get_last_signal_args("power_changed")
assert args == (1500.0,)
```

### Test Thread Safety

```python
import threading

def set_power_repeatedly(mock, power):
    for _ in range(100):
        mock.set_power(power)

mock = MockLaserController()
mock.connect()

# Create multiple threads
threads = [
    threading.Thread(target=set_power_repeatedly, args=(mock, 1000.0)),
    threading.Thread(target=set_power_repeatedly, args=(mock, 1500.0)),
]

# Run concurrently
for t in threads:
    t.start()
for t in threads:
    t.join()

# Verify no corruption
assert mock.power_setpoint_mw in [1000.0, 1500.0]
```

---

## API Reference

### MockQObjectBase (Base Class)

**Configuration Attributes:**

*Basic Failure Simulation (Backward Compatible):*
- `simulate_connection_failure: bool` - Fail connect() calls
- `simulate_operation_error: bool` - Fail operation calls
- `error_message: str` - Custom error message
- `response_delay_s: float` - Simulated delay (seconds)

*Advanced Failure Simulation:*
- `failure_mode: FailureMode` - Active failure mode
- `intermittent_failure_probability: float` - Random failure chance (0.0-1.0)
- `timeout_threshold_s: float` - Operation timeout threshold
- `device_busy_duration_s: float` - Busy state duration
- `calibration_required: bool` - Requires calibration
- `power_supply_voltage_v: float` - Supply voltage (nominal: 12.0V)
- `min_power_voltage_v: float` - Minimum required voltage
- `hardware_limits: dict[str, tuple[float, float]]` - Parameter limits
- `persist_error_state: bool` - Keep error state across calls
- `current_error_state: Optional[str]` - Active error message

*Signal Validation:*
- `signal_log: list[tuple[str, tuple, float]]` - Signal emission log
- `enable_signal_logging: bool` - Enable/disable logging

**State Tracking:**
- `call_log: list[tuple[str, dict]]` - All method calls recorded

**Methods:**
- `reset() -> None` - Reset to clean state
- `_log_call(func_name: str, **kwargs) -> None` - Log method call
- `_apply_delay() -> None` - Apply configured delay
- `_should_fail() -> tuple[bool, Optional[str]]` - Check failure conditions
- `_set_busy_state() -> None` - Set device busy
- `_start_operation() -> None` - Start operation timer
- `_end_operation() -> None` - End operation timer
- `_set_error_state(error_message: str) -> None` - Set persistent error
- `_clear_error_state() -> None` - Clear persistent error
- `perform_calibration() -> bool` - Perform calibration
- `get_failure_statistics() -> dict` - Get failure stats

*Signal Validation Methods:*
- `_log_signal_emission(signal_name: str, *args) -> None` - Log signal
- `get_signal_emissions(signal_name: Optional[str]) -> list` - Get emissions
- `get_signal_emission_count(signal_name: str) -> int` - Count emissions
- `was_signal_emitted(signal_name: str) -> bool` - Check if emitted
- `get_last_signal_args(signal_name: str) -> Optional[tuple]` - Get last args
- `get_signal_timing(signal_name: str) -> Optional[float]` - Get timestamp
- `get_signal_interval(signal_name: str) -> Optional[float]` - Get interval
- `verify_signal_sequence(*signal_names: str) -> bool` - Verify order
- `verify_signal_parameters(signal_name: str, validator: callable) -> bool` - Validate args
- `clear_signal_log() -> None` - Clear signal log
- `get_signal_statistics() -> dict` - Get signal stats

### MockCameraController

*See [MockCameraController section](#1-mockcameracontroller) for full API*

**Key Methods:**
- `connect(camera_id: str) -> bool`
- `set_pixel_format(format: str) -> bool` - "Bgr8", "Rgb8", "Mono8"
- `set_binning(factor: int) -> bool` - 1, 2, 4, 8
- `set_trigger_mode(mode: str) -> bool` - "Continuous", "Software", "Hardware"
- `set_acquisition_mode(mode: str) -> bool` - "Continuous", "SingleFrame", "MultiFrame"
- `set_hardware_fps(fps: int) -> bool` - 1-120 FPS
- `start_streaming() -> bool`
- `stop_streaming() -> bool`
- `trigger_frame() -> None` - Manual software trigger

### MockLaserController

*See [MockLaserController section](#2-mocklasercontroller) for full API*

**Key Methods:**
- `connect(com_port: str, baudrate: int) -> bool`
- `set_output(enabled: bool) -> bool`
- `set_current(current_ma: float) -> bool`
- `set_power(power_mw: float) -> bool`
- `read_current() -> Optional[float]`
- `read_power() -> Optional[float]`

### MockTECController

*See [MockTECController section](#3-mockteccontroller) for full API*

**Key Methods:**
- `connect(com_port: str, baudrate: int) -> bool`
- `set_output(enabled: bool) -> bool`
- `set_temperature(temperature_c: float) -> bool`
- `read_temperature() -> Optional[float]`
- `read_current() -> Optional[float]`
- `read_voltage() -> Optional[float]`
- `set_thermal_time_constant(tau_seconds: float) -> None`
- `set_ambient_temperature(temperature_c: float) -> None`
- `force_temperature(temperature_c: float) -> None`

### MockActuatorController

*See [MockActuatorController section](#4-mockactuatorcontroller) for full API*

**Key Methods:**
- `connect(com_port: str, baudrate: int, auto_home: bool) -> bool`
- `find_index() -> bool` - Start homing
- `set_position(position_um: float) -> bool`
- `make_step(step_um: float) -> bool`
- `get_position() -> Optional[float]`
- `set_speed(speed: int) -> bool`
- `start_scan(direction: int) -> bool`
- `stop_scan() -> bool`
- `_complete_homing() -> None` - Manual completion
- `_complete_movement() -> None` - Manual completion

### MockGPIOController

*See [MockGPIOController section](#5-mockgpiocontroller) for full API*

**Key Methods:**
- `connect(port: str) -> bool`
- `send_watchdog_heartbeat() -> bool`
- `start_smoothing_motor() -> bool`
- `stop_smoothing_motor() -> bool`
- `start_aiming_laser() -> bool`
- `stop_aiming_laser() -> bool`
- `get_safety_status() -> bool`
- `get_photodiode_voltage() -> float`
- `get_photodiode_power() -> float`

---

## Test Examples

Comprehensive test suites demonstrate all features:

### Test Files

- `tests/test_mocks/test_mock_qobject_base.py` - Base class tests
- `tests/test_mocks/test_mock_qobject_base_failures.py` - Failure mode tests (42 tests)
- `tests/test_mocks/test_signal_validation.py` - Signal validation tests (32 tests)
- `tests/test_mocks/test_mock_camera_controller.py` - Camera tests (62 tests)
- `tests/test_mocks/test_mock_tec_controller.py` - TEC tests
- `tests/test_mock_laser.py` - Laser mock tests (12 tests)
- `tests/test_mock_actuator.py` - Actuator mock tests (16 tests)
- `tests/test_mock_gpio.py` - GPIO mock tests (14 tests)

**Total: 100+ tests, all passing**

### Example Test Suite

```python
import pytest
from tests.mocks import MockLaserController
from tests.mocks.mock_qobject_base import FailureMode

class TestLaserController:
    def test_connection(self):
        mock = MockLaserController()
        assert mock.connect() is True
        assert mock.is_connected is True

    def test_power_control(self):
        mock = MockLaserController()
        mock.connect()
        assert mock.set_power(1500.0) is True
        assert mock.power_setpoint_mw == 1500.0

    def test_limit_enforcement(self):
        mock = MockLaserController()
        mock.connect()
        assert mock.set_power(5000.0) is False  # Exceeds limit

    def test_intermittent_failure(self):
        mock = MockLaserController()
        mock.connect()
        mock.failure_mode = FailureMode.INTERMITTENT_FAILURE
        mock.intermittent_failure_probability = 0.5

        failures = 0
        for _ in range(100):
            if not mock.set_power(1000.0):
                failures += 1

        # Expect ~50 failures with 50% probability
        assert 30 < failures < 70

    def test_signal_emission(self):
        mock = MockLaserController()
        mock.connect()
        mock.clear_signal_log()

        mock.set_power(1234.5)

        assert mock.was_signal_emitted("power_changed")
        args = mock.get_last_signal_args("power_changed")
        assert args == (1234.5,)
```

---

## TestSafetyManager - Test-Only Safety Manager

**Location:** `tests/test_safety_manager.py`
**Purpose:** Hardware experimentation with relaxed safety interlocks
**Status:** Test-only code (NOT a mock)

### ⚠️ CRITICAL WARNING

**TestSafetyManager is NOT a mock** - it's a REAL safety manager that bypasses interlocks.

- **NEVER use in production or clinical environments**
- **ONLY for offline hardware testing and calibration**
- Requires explicit environment variable: `TOSCA_ENABLE_TEST_SAFETY=1`
- Import blocked by default (raises `ImportError` without environment variable)

### Usage Example

```python
import os
os.environ['TOSCA_ENABLE_TEST_SAFETY'] = '1'

from tests.test_safety_manager import TestSafetyManager

# Create test safety manager
tsm = TestSafetyManager(bypass_gpio=True)

# Session validation automatically satisfied
assert tsm.session_valid is True

# GPIO interlocks can be bypassed
assert tsm.gpio_interlock_ok is True
```

---

## Version Information

**Created:** 2025-10-26
**Last Updated:** 2025-11-02
**Status:** Complete - Production Ready
**Test Coverage:** 100+ tests passing
**Type Safety:** mypy zero errors
**Dependencies:** PyQt6, numpy (camera only)

---

**End of Mock Documentation**
