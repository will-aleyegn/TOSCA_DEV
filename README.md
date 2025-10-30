# TOSCA Laser Control System

**Version:** 0.9.11-alpha (Architecture Analysis & Production Readiness Assessment)
**Last Updated:** 2025-10-30

A comprehensive laser control system integrating hardware control, machine vision, safety interlocks, and treatment protocol execution for precision laser applications.

---

## Overview

This system provides real-time control and monitoring of a diode laser system with integrated positioning, imaging, and safety features. The software architecture emphasizes reliability and safety through multi-layered hardware and software interlocks, comprehensive event logging, and a robust hardware abstraction layer.

**Key Capabilities:**
- Precision laser power control with real-time feedback
- Linear actuator positioning for automated sequences
- Machine vision integration for alignment and monitoring
- Multi-layer safety architecture with hardware interlocks
- Comprehensive session and event logging
- Configurable treatment protocols with automated execution

---

## Hardware Components

### Primary Devices
1. **Laser Driver:** Arroyo 6300 Controller (COM10, 38400 baud)
2. **TEC Controller:** Arroyo 5305 Controller (COM9, 38400 baud)
3. **Linear Actuator:** Xeryon linear stage (COM3, 9600 baud)
4. **Camera:** Allied Vision 1800 U-158c (USB 3.0, VmbPy SDK)
5. **GPIO Controller:** Arduino Uno (ATmega328P) with custom watchdog firmware (COM4, 115200 baud)

### Safety Hardware
6. **Footpedal:** Normally-open momentary switch (active-high interlock)
7. **Smoothing Device:** Motor control (D2) with vibration sensor (D3)
8. **Photodiode:** Analog voltage monitoring (A0, 0-5V, 10-bit ADC)
9. **Aiming Laser:** 650nm red laser diode for alignment (D4)

---

## Safety Architecture

### Hardware Interlocks
The following hardware-based safety interlocks provide the foundational safety layer:

1. **Footpedal Deadman Switch**
   - Type: Active-high requirement (positive permission)
   - Behavior: Laser can only fire while footpedal is actively depressed
   - Implementation: Digital input monitoring via Arduino Uno
   - Fail-safe: Releasing pedal immediately disables laser

2. **Smoothing Device Health Monitoring**
   - Type: Dual-signal validation (motor + vibration)
   - Behavior: Both motor activation AND vibration detection required
   - Implementation: Digital output (D2) and input (D3) via Arduino Uno
   - Fail-safe: Loss of either signal triggers immediate shutdown

3. **Photodiode Power Verification**
   - Type: Continuous output monitoring
   - Behavior: Measured power must match commanded power
   - Implementation: Analog input (A0) via Arduino Uno
   - Fail-safe: Power deviation beyond threshold triggers shutdown

4. **Hardware Watchdog Timer**
   - Type: Independent firmware-based timeout
   - Behavior: Requires continuous heartbeat from main application
   - Implementation: Custom Arduino Uno watchdog firmware (1000ms timeout)
   - Fail-safe: Software freeze or crash triggers automatic laser disable

### Software Interlocks
Secondary software-based safety validation:

1. **Emergency Stop (E-Stop)**
   - Large physical button in Safety tab
   - Immediate treatment halt with highest priority
   - Bypasses all queues and state checks
   - Locks system until manually cleared

2. **Power Limit Enforcement**
   - Configurable maximum laser power threshold
   - Real-time validation during protocol execution
   - Automatic shutdown if limit exceeded
   - Event logging for all limit violations

3. **Session Validation**
   - Active session required for laser operation
   - Ensures all operations are logged and attributed
   - Prevents accidental firing outside treatment context
   - Database persistence for audit trail

4. **State Machine Control**
   - Strict state transitions (SAFE → ARMED → TREATING)
   - Operations only permitted in valid states
   - Any interlock failure → immediate FAULT transition
   - Comprehensive state change logging

---

## Technology Stack

### Core
- **Python 3.10+** - Primary language
- **PyQt6** - GUI framework
- **SQLite** - Embedded database
- **OpenCV** - Image processing
- **NumPy** - Numerical operations

### Hardware Communication
- **pyserial** - Arroyo laser and Arduino communication
- **Xeryon API** - Linear actuator control
- **VmbPy** - Allied Vision camera SDK

### Supporting Libraries
- **pyqtgraph** - Real-time plotting
- **SQLAlchemy** - Database ORM
- **Pydantic** - Configuration validation

---

## Architecture Documentation

Comprehensive technical documentation is available in `docs/architecture/`:

1. **[System Overview](docs/architecture/01_system_overview.md)** - Complete architecture, technology stack, hardware integration
2. **[Database Schema](docs/architecture/02_database_schema.md)** - SQLite schema, entity relationships, common queries
3. **[Safety System](docs/architecture/03_safety_system.md)** - Safety philosophy, interlock architecture, fault handling
4. **[Treatment Protocols](docs/architecture/04_treatment_protocols.md)** - Protocol data model, execution engine, builder UI
5. **[Image Processing](docs/architecture/05_image_processing.md)** - Camera integration, ring detection, focus measurement
6. **[Safety Watchdog](docs/architecture/06_safety_watchdog.md)** - Hardware watchdog implementation and firmware

---

## Development Guidelines

### Code Quality
- Follow PEP 8 style guidelines
- Type hints required on all functions
- Comprehensive docstrings for safety-critical code
- Pre-commit hooks enforce: Black, Flake8, MyPy, isort
- Use `git commit --no-verify` for known MyPy false positives (documented in coding standards)

### Safety Requirements
- All safety-critical code must have unit tests
- Safety interlocks cannot be bypassed in production
- All safety events must be logged immutably
- Regular code reviews for safety-related modules

### Testing Strategy
- **Unit Tests:** Hardware abstraction, protocol engine, database operations
- **Integration Tests:** Hardware communication, safety coordination, UI integration
- **Safety Tests:** Footpedal response, photodiode accuracy, E-stop effectiveness, multi-fault scenarios
- **Thread Safety Tests:** Concurrent hardware access validation

---

## Project Structure

```
components/
├── camera_module/          [DONE] VmbPy API integration (6 test scripts)
├── actuator_module/        [DONE] Xeryon API integration (6 test scripts)
├── laser_control/          [DONE] Arroyo API documentation and examples
└── gpio_safety/            [DONE] Arduino Uno firmware and GPIO examples

src/
├── ui/
│   ├── main_window.py      [DONE] 4-tab interface with toolbar, global E-stop
│   └── widgets/
│       ├── subject_widget.py                [DONE] Subject selection and session creation
│       ├── camera_live_view.py              [DONE] Live streaming, controls (renamed)
│       ├── camera_hardware_panel.py         [DONE] Hardware diagnostics panel
│       ├── treatment_setup_widget.py        [DONE] Protocol selector
│       ├── active_treatment_widget.py       [DONE] Treatment monitoring dashboard
│       ├── laser_widget.py                  [DONE] Laser power controls (treatment only)
│       ├── tec_widget.py                    [DONE] TEC temperature controls
│       ├── actuator_widget.py               [DONE] Actuator sequences and positioning
│       ├── safety_widget.py                 [DONE] Safety status with event logging
│       ├── gpio_widget.py                   [DONE] GPIO safety interlock display
│       ├── interlocks_widget.py             [DONE] Consolidated safety status
│       └── protocol_selector_widget.py      [DONE] Visual protocol library browser
│
├── core/
│   ├── protocol.py         [DONE] Action-based data model
│   ├── protocol_engine.py  [DONE] Async execution engine
│   ├── safety.py           [DONE] Central safety manager with state machine
│   ├── safety_watchdog.py  [DONE] Hardware watchdog heartbeat manager
│   ├── session_manager.py  [DONE] Session lifecycle management
│   └── event_logger.py     [DONE] Immutable event logging system
│
├── hardware/
│   ├── hardware_controller_base.py   [DONE] ABC with QObject integration
│   ├── camera_controller.py          [DONE] Allied Vision HAL (thread-safe, VmbPy API compliant)
│   ├── laser_controller.py           [DONE] Arroyo 6300 laser HAL (COM10, thread-safe)
│   ├── tec_controller.py             [DONE] Arroyo 5305 TEC HAL (COM9, thread-safe)
│   ├── actuator_controller.py        [DONE] Xeryon actuator HAL (thread-safe)
│   ├── actuator_sequence.py          [DONE] Sequence builder data model
│   └── gpio_controller.py            [DONE] Arduino Uno GPIO HAL (thread-safe)
│
├── database/
│   ├── models.py           [DONE] SQLAlchemy ORM models
│   └── db_manager.py       [DONE] Database manager with CRUD operations
│
├── config/
│   ├── models.py           [DONE] Pydantic configuration models
│   └── config_loader.py    [DONE] YAML configuration loader
│
└── image_processing/
    ├── ring_detector.py    [TODO] Hough circle detection
    ├── focus_measure.py    [TODO] Laplacian variance
    └── video_recorder.py   [TODO] OpenCV recording

data/
├── protocols/              [DONE] Protocol JSON storage
├── logs/                   [DONE] Application logs, event JSONL files
├── sessions/               [DONE] Session folders (auto-created per session)
└── tosca.db                [DONE] SQLite database (auto-created)

tests/
├── mocks/                  [DONE] Hardware mock infrastructure
│   ├── mock_hardware_base.py      Base class for hardware mocks
│   ├── mock_qobject_base.py       Base class for QObject mocks
│   ├── mock_camera_controller.py  Camera mock (7 tests)
│   ├── mock_laser_controller.py   Laser mock (12 tests)
│   ├── mock_actuator_controller.py Actuator mock (16 tests)
│   ├── mock_gpio_controller.py    GPIO mock (14 tests)
│   └── examples/           Usage examples
├── test_thread_safety.py   [DONE] Thread safety validation (7 tests)
├── test_realtime_safety_monitoring.py [DONE] Safety system tests (6 tests)
└── test_mock_hardware_base.py [DONE] Mock infrastructure tests

firmware/
└── arduino_watchdog/       [DONE] Custom Arduino Uno watchdog firmware
    └── arduino_watchdog.ino        AVR WDT implementation with serial protocol
```

---

## Quick Start

### For AI Assistants / New Developers
**START HERE:** Read `presubmit/ONBOARDING.md` for comprehensive project context and standards.
- **Fast Start:** 2.5 minutes to full context
- **Project Standards:** Coding patterns, safety requirements, medical device compliance
- **AI Integration:** Zen MCP context helpers for advanced workflows

### For End Users

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)
- Arduino IDE (for firmware upload)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/will-aleyegn/TOSCA_DEV.git
   cd TOSCA_DEV
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Upload Arduino firmware:**
   - Open `firmware/arduino_watchdog/arduino_watchdog.ino` in Arduino IDE
   - Select Board: Arduino Uno
   - Select Port: (appropriate COM port)
   - Upload firmware

5. **Configure hardware connections:**
   - Edit `config.yaml` with correct COM ports
   - Verify baud rates match hardware settings

### Running the Application

```bash
python src/main.py
```

---

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Thread safety tests
pytest tests/test_thread_safety.py

# Safety monitoring tests
pytest tests/test_realtime_safety_monitoring.py

# Mock infrastructure tests
pytest tests/test_mock_hardware_base.py
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

---

## License

[License information to be determined]

---

## Documentation

### Core Documentation (Root Directory)
- **`CLAUDE.md`** - AI assistant context and project overview (single source of truth)
- **`PROJECT_STATUS.md`** - Current milestones, component status, roadmap
- **`LESSONS_LEARNED.md`** - Critical bugs, solutions, prevention strategies
- **`WORK_LOG.md`** - Chronological development log (last 14 days)
- **`HISTORY.md`** - Compressed monthly archive (60+ days)

### Architecture Documentation (`docs/architecture/`)
- **`01_system_overview.md`** - Complete architecture and technology stack
- **`02_database_schema.md`** - SQLite schema and entity relationships
- **`03_safety_system.md`** - Safety philosophy and interlock architecture
- **`SAFETY_SHUTDOWN_POLICY.md`** - Selective shutdown rationale (medical device design)
- **`CAMERA_PERFORMANCE_FIXES.md`** - Camera optimization strategies
- **`EXPOSURE_SAFETY_LIMITER.md`** - Exposure time safety implementation
- **`ADR-001-protocol-consolidation.md`** - Architecture Decision Records
- **`ADR-002-dependency-injection-pattern.md`** - Dependency injection adoption

### Onboarding & Standards (`presubmit/`)
- **`ONBOARDING.md`** - **START HERE** - Comprehensive project context (2.5 min read)
- **`QUICKSTART_GUIDE.md`** - 4 workflow scenarios with zen MCP integration
- **`ZEN_CONTEXT_GUIDE.md`** - Tool-by-tool guide for advanced AI workflows
- **`zen_context_helper.py`** - Automated context loading for zen MCP tools

### Hardware Documentation (`components/`)
- `camera_module/README.md` - Allied Vision camera API and examples
- `actuator_module/README.md` - Xeryon actuator API and examples
- `laser_control/README.md` - Arroyo laser/TEC API documentation
- `gpio_safety/README.md` - Arduino GPIO examples and firmware

### Testing Documentation
- **`tests/mocks/README.md`** - Mock infrastructure usage guide
- **`docs/architecture/09_test_architecture.md`** - Testing strategy and patterns
