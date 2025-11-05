# TOSCA Laser Control System

**Version:** 0.9.12-alpha
**Status:** Research Mode - Not for Clinical Use
**Platform:** Windows 10/11, Python 3.12+

## System Overview

TOSCA is a laser control system integrating precision laser power control, linear actuator positioning, machine vision, and multi-layer safety interlocks for research and development applications.

### Key Capabilities

- Precision laser power control (5W diode laser)
- Linear actuator positioning (45mm range)
- Machine vision integration (Allied Vision 1800 U-158c camera)
- Multi-layer safety architecture with hardware interlocks
- Comprehensive session and event logging
- Configurable treatment protocols with automated execution
- Real-time monitoring and data acquisition

### Current Limitations

**WARNING: Research Mode Only**

This system is NOT approved for clinical use. Current limitations:

- Database encryption NOT implemented (all data in plaintext)
- User authentication NOT implemented (no access controls)
- Not approved for clinical or production use
- Not suitable for protected health information (PHI)

Intended for research and development, hardware testing and calibration, algorithm development, and educational purposes only.

## Architecture

### Technology Stack

**Core**
- Python 3.12+ (actual: 3.12.10)
- PyQt6 6.9.0 (GUI framework)
- SQLite 3.x (embedded database, unencrypted)
- OpenCV (image processing)
- NumPy (numerical operations)

**Hardware Communication**
- pyserial (Arroyo laser/TEC, Arduino GPIO)
- Xeryon API (linear actuator control)
- VmbPy (Allied Vision camera SDK)

**Supporting Libraries**
- pyqtgraph (real-time plotting)
- SQLAlchemy (database ORM)
- Pydantic (configuration validation)

### System Layers

```
┌─────────────────────────────────────────────────────────┐
│  User Interface (PyQt6)                                 │
│  - 3-tab interface (Setup, Treatment, Safety)           │
│  - Protocol builder and selector                        │
│  - Live camera feed and controls                        │
│  - Real-time monitoring dashboards                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Application Core                                       │
│  - Session Manager (subject/session lifecycle)          │
│  - Safety Manager (5-state safety FSM)                  │
│  - Protocol Engine (async execution)                    │
│  - Event Logger (immutable logging)                     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Hardware Abstraction Layer (HAL)                       │
│  - Thread-safe controllers (RLock pattern)              │
│  - PyQt6 signal/slot architecture                       │
│  - Consistent connect/disconnect interface              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Physical Hardware                                      │
│  - Laser driver (Arroyo 6300)                           │
│  - TEC controller (Arroyo 5305)                         │
│  - Linear actuator (Xeryon)                             │
│  - Camera (Allied Vision 1800, USB 3.0)                 │
│  - GPIO controller (Arduino Uno)                        │
└─────────────────────────────────────────────────────────┘
```

### Hardware Configuration

| Component | Model | Interface | Purpose |
|-----------|-------|-----------|---------|
| Laser Driver | Arroyo 6300 | Serial @ 38400 | Treatment laser power control |
| TEC Controller | Arroyo 5305 | Serial @ 38400 | Laser temperature control |
| Linear Actuator | Xeryon | Serial @ 9600 | Laser ring positioning |
| Camera | Allied Vision 1800 | USB 3.0 | Live imaging, alignment |
| GPIO Controller | Arduino Uno | Serial @ 115200 | Safety interlocks |

**Safety Interlocks (Arduino GPIO):**

The Arduino Uno acts as a dedicated safety controller, continuously monitoring critical signals and requiring active heartbeat communication from the control software:

- **Footpedal deadman switch:** Active-high requirement (laser only fires while depressed)
- **Laser spot smoothing module:** Dual-signal validation (motor control + vibration detection)
- **Photodiode power verification:** Continuous analog monitoring (A0, 0-5V, 10-bit ADC)
- **Hardware watchdog timer:** 1000ms timeout requiring 500ms heartbeat intervals
  - Control software must send heartbeat every 500ms
  - Missed heartbeat triggers automatic laser shutdown
  - Prevents software hang or crash from leaving laser enabled
  - Independent failsafe layer beyond software interlocks
- **Aiming beam control:** SEMINEX integrated aiming beam via MCP4725 DAC (I2C address 0x62, Arduino A4/A5)
  - 12-bit digital control (0-4095) via LDD200 200mA driver
  - Continuous power adjustment for optimal alignment visibility

### Safety Architecture

**Two-Layer Safety System:**

1. **Hardware Interlocks (Primary)**
   - Footpedal deadman switch
   - Laser spot smoothing module health monitoring
   - Photodiode power verification (continuous)
   - Hardware watchdog timer (Arduino firmware)

2. **Software Interlocks (Secondary)**
   - Emergency stop (E-Stop) button
   - Power limit enforcement
   - Session validation
   - State machine control (5-state FSM)

**Safety State Machine:**

```
SAFE → ARMED → TREATING → ARMED → SAFE
  ↓      ↓         ↓
  ← UNSAFE/FAULT ←
        ↓
  EMERGENCY_STOP (locked)
```

**Selective Shutdown Policy:**

When safety fault occurs:
- Treatment laser: DISABLED (immediate power-off)
- Camera: MAINTAINED (visual feedback)
- Actuator: MAINTAINED (controlled retraction)
- Aiming beam: MAINTAINED (SEMINEX integrated, low power)
- GPIO monitoring: MAINTAINED (diagnostics)
- Event logging: MAINTAINED (audit trail)

Only the treatment laser is shut down on safety fault. All other systems remain operational to support safe assessment and recovery.

### Project Structure

```
src/
├── ui/                  # PyQt6 user interface
│   ├── main_window.py          # 3-tab interface (Setup, Treatment, Safety)
│   └── widgets/                # UI widgets (camera, laser, TEC, actuator, safety)
├── core/                # Business logic
│   ├── safety.py               # Central safety manager with state machine
│   ├── protocol_engine.py      # Async protocol execution
│   ├── session_manager.py      # Session lifecycle management
│   └── event_logger.py         # Immutable event logging
├── hardware/            # Hardware abstraction layer
│   ├── hardware_controller_base.py  # ABC with QObject integration
│   ├── camera_controller.py    # Allied Vision HAL (thread-safe, VmbPy)
│   ├── laser_controller.py     # Arroyo 6300 HAL (thread-safe)
│   ├── tec_controller.py       # Arroyo 5305 HAL (thread-safe)
│   ├── actuator_controller.py  # Xeryon HAL (thread-safe)
│   └── gpio_controller.py      # Arduino GPIO HAL (thread-safe)
├── database/            # Data persistence
│   ├── models.py               # SQLAlchemy ORM models
│   └── db_manager.py           # Database manager with CRUD
└── config/              # Configuration
    ├── models.py               # Pydantic configuration models
    └── config_loader.py        # YAML configuration loader

tests/                   # Test suite
├── mocks/                      # MockHardwareBase infrastructure
├── test_hardware/              # Hardware controller tests
└── test_safety/                # Safety system tests

data/                    # Runtime data
├── tosca.db                    # SQLite database (unencrypted)
├── sessions/                   # Per-session data folders
└── logs/                       # JSONL event logs (append-only)

docs/architecture/       # Architecture documentation
firmware/                # Arduino firmware
protocols/               # Treatment protocol definitions
```

## Operation

### Session Workflow

1. **Application Launch**
   - Hardware connection and self-test
   - Tech ID entry (required for all operations)

2. **Subject Selection**
   - Select existing subject (search by code)
   - OR create new subject (generate code, enter demographics)

3. **Session Creation**
   - Log subject ID, tech ID, start time
   - Initialize session recording

4. **Pre-Treatment Setup**
   - Display live camera feed
   - Manual focus and alignment by operator
   - Software assistance (focus indicator, ring detection overlay)

5. **Treatment Execution**
   - Select or create treatment protocol
   - Safety pre-checks (hardware, interlocks, camera, session)
   - Operator initiates treatment
   - System transitions: SAFE → ARMED → TREATING
   - Continuous monitoring during treatment
   - Comprehensive data logging

6. **Session Closure**
   - Save recordings and event logs
   - Add session notes
   - Mark session complete
   - Update subject record

### Protocol Engine

**Action-Based Protocol Model:**

Protocols consist of sequential or concurrent actions:
- Laser power control (set power, ramp power)
- Position control (move actuator, set ring size)
- Timing control (wait, delay)
- Conditional logic
- Real-time adjustments

**Execution:**
- Asynchronous execution engine
- Real-time monitoring
- Power limit enforcement
- Photodiode feedback validation
- Comprehensive event logging

### Data Management

**Two-Tier Logging:**

1. **High-frequency data** (100Hz+): JSONL files in session folder
   - Photodiode readings
   - Camera frame metadata
   - Real-time interlock states

2. **Event-based data**: SQLite database
   - Protocol steps
   - Power changes
   - Position adjustments
   - Safety triggers
   - User actions

**Database Schema:**
- subjects (anonymized subject records)
- sessions (treatment sessions)
- treatment_events (detailed event log)
- protocols (saved treatment protocols)
- calibrations (device calibration data)
- safety_log (safety events and faults)
- tech_users (technician/operator accounts)

## Key Design Patterns

### Hardware Abstraction Layer

All hardware controllers inherit from `HardwareControllerBase`:
- Thread-safe operations (RLock pattern)
- PyQt6 signal emission for state changes
- Consistent connect/disconnect interface
- Error handling and logging

### Signal/Slot Architecture

All cross-thread and widget communication uses PyQt6 signals:
- Thread-safe by design
- Prevents tight coupling
- Enables reactive UI updates
- No direct widget access from other components

### State Machine Safety Control

Safety state transitions are strictly controlled:
- Normal: SAFE → ARMED → TREATING → ARMED → SAFE
- Fault: ANY → UNSAFE (selective shutdown)
- Emergency: ANY → EMERGENCY_STOP (locked)

### Two-Tier Logging

Events are logged to both:
1. JSONL files (data/logs/) - Append-only, immutable
2. SQLite database (data/tosca.db) - Queryable, relational

## Testing Infrastructure

### Mock Architecture

**MockHardwareBase Pattern:**
- Consistent mock behavior across all hardware types
- Built-in connection state management
- Automatic signal emission validation
- Failure mode simulation

### Test Coverage

Comprehensive test infrastructure covers:
- Hardware abstraction layer (thread safety, signal emissions)
- Safety interlock coordination (watchdog heartbeat, GPIO monitoring)
- Protocol execution engine (concurrent actions, safety validation)
- Database operations (session management, event logging)

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest tests/test_thread_safety.py
pytest tests/test_realtime_safety_monitoring.py

# With coverage
pytest --cov=src --cov-report=html
```

## Code Quality Standards

### Safety Requirements

- All safety-critical code must have unit tests
- Safety interlocks cannot be bypassed in production mode
- All safety events must be logged immutably
- Regular code reviews for safety-related modules

### Style Guidelines

- Follow PEP 8 style guidelines
- Type hints required on all functions
- Comprehensive docstrings for safety-critical code
- Pre-commit hooks enforce: Black, Flake8, MyPy, isort

### Thread Safety Pattern

```python
class HardwareController(QObject):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()  # Reentrant lock

    def set_value(self, value):
        with self._lock:
            self.hardware.set(value)
            self.value_changed.emit(value)
```

## Documentation

### Architecture
- `docs/architecture/01_system_overview.md` - Complete architecture
- `docs/architecture/02_database_schema.md` - Database schema
- `docs/architecture/03_safety_system.md` - Safety system details
- `docs/architecture/04_treatment_protocols.md` - Protocol engine
- `docs/architecture/SAFETY_SHUTDOWN_POLICY.md` - Shutdown policy

### Hardware
- `docs/hardware/HARDWARE_CONFIG_SUMMARY.md` - Device specs
- `components/camera_module/` - Camera API examples
- `components/actuator_module/` - Actuator API examples
- `components/laser_control/` - Laser/TEC API docs
- `components/gpio_safety/` - Arduino examples and firmware

### Testing
- `tests/mocks/README.md` - Mock infrastructure guide
- `docs/architecture/09_test_architecture.md` - Testing strategy

## Installation

**Prerequisites:**
- Python 3.12+ (tested on 3.12.10)
- Windows 10/11
- Hardware devices (or run in mock mode)

**Setup:**

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m src.database.db_manager

# Run application
python -m src.main

# Run tests
pytest
```

## Configuration

**Primary config:** `config.yaml`
- Hardware COM ports and baud rates
- Safety thresholds and limits
- Camera settings
- Protocol defaults

**Example:**
```yaml
hardware:
  laser:
    port: COM_PORT  # Configure in config.yaml
    baud_rate: 38400
  tec:
    port: COM_PORT  # Configure in config.yaml
    baud_rate: 38400
  actuator:
    port: COM_PORT  # Configure in config.yaml
    baud_rate: 9600
  gpio:
    port: COM_PORT  # Configure in config.yaml
    baud_rate: 115200

safety:
  max_laser_power_watts: 5.0
  watchdog_timeout_ms: 1000
  photodiode_deviation_threshold_percent: 30.0
```

## Critical Notes

### Safety-Critical Context

This is safety-critical laser control software under development. Safety, traceability, and compliance are paramount. All safety-critical code requires unit tests. All safety events are logged immutably. Architectural decisions affecting safety are documented.

### Research Mode

The system includes:
- Research mode warning dialog on startup
- Title bar watermark: "TOSCA v0.9.12-alpha - RESEARCH MODE ONLY"
- Status bar watermark: "RESEARCH MODE - NOT FOR CLINICAL USE"

### Known Limitations

**QImage Memory Lifetime:** QImage constructor creates shallow copy of numpy array data. Always copy frame data before QImage construction.

**Widget Reparenting Anti-Pattern:** Never reparent widgets between components. Use signal/slot architecture for widget communication.

**Hardware Binning:** Currently using software downsampling. Hardware binning caused corrupted frames (configuration issues under investigation).
