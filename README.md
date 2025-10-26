# TOSCA Laser Control System

## Overview

This is a comprehensive laser control system. The system integrates:

- **Laser Control** - Arroyo Instruments TEC Controller (serial communication)
- **Linear Actuator** - Xeryon actuator for ring size control
- **Camera System** - Allied Vision camera with VmbPy SDK for alignment and monitoring
- **GPIO Safety Interlocks** - Arduino Nano with StandardFirmata for footpedal, smoothing device, and photodiode monitoring
- **Session Management** - SQLite database for longitudinal subject tracking
- **Treatment Protocols** - Configurable treatment plans with power ramping and ring sizing
- **Video Recording** - Complete session recording and event logging

## Key Features

### Safety-First Design
- **Footpedal Deadman Switch** - Active requirement for laser operation
- **Hotspot Smoothing Device Interlock** - Signal health monitoring
- **Photodiode Feedback** - Real-time power verification
- **Multiple Software Interlocks** - E-stop, power limits, session validation
- **Comprehensive Event Logging** - Complete audit trail

### Treatment Capabilities
- Pre-defined protocol templates
- Custom protocol builder with multi-step sequences
- Power ramping (constant, linear, logarithmic, exponential)
- Adjustable ring size via actuator control
- Real-time protocol adjustments
- In-treatment monitoring and recording

### Image Processing
- Laser ring detection (circle finding algorithm)
- Focus quality measurement
- Live video feed with overlays
- Session video recording
- Snapshot capture

### Session Management
- Anonymized subject profiles
- Multi-session longitudinal tracking
- Technician/operator authentication
- Complete session history

## Architecture Documentation

Comprehensive technical documentation is available in `docs/architecture/`:

### 1. [System Overview](docs/architecture/01_system_overview.md)
- Complete system architecture
- Technology stack
- Hardware components
- Software layers
- Development phases

### 2. [Database Schema](docs/architecture/02_database_schema.md)
- Complete SQLite schema
- Entity relationships
- Table definitions
- Common queries
- Migration strategy

### 3. [Safety System](docs/architecture/03_safety_system.md)
- Safety philosophy and principles
- Hardware interlocks (footpedal, smoothing device, photodiode)
- Software interlocks (e-stop, power limits)
- Safety state machine
- Fault handling procedures
- Testing requirements

### 4. [Treatment Protocols](docs/architecture/04_treatment_protocols.md)
- Protocol data model and JSON schema
- Example protocols (constant power, ramping, multi-step)
- Protocol execution engine
- Ring size control and calibration
- Protocol builder UI

### 5. [Image Processing](docs/architecture/05_image_processing.md)
- Camera system integration
- Ring detection algorithm (Hough Circle Transform)
- Focus measurement (Laplacian variance)
- Video recording
- Calibration procedures

## Technology Stack

### Core
- **Python 3.10+**
- **PyQt6** - GUI framework
- **SQLite** - Database
- **OpenCV (cv2)** - Image processing
- **NumPy** - Numerical operations

### Hardware Libraries
- **pyserial** - Arroyo laser and Arduino communication
- **Xeryon API** - Linear actuator control
- **VmbPy** - Allied Vision camera SDK
- **pyfirmata2** - Arduino Firmata protocol (Python 3.12+ compatible)

### Supporting Libraries
- **pyqtgraph** - Real-time plotting
- **sqlalchemy** - Database ORM
- **alembic** - Database migrations
- **pydantic** - Configuration validation

## Hardware Components
1. **Laser Controller:** Arroyo Instruments laser driver and TEC Controller (COM4)
2. **Linear Actuator:** Xeryon linear stage (COM3)
3. **Camera:** Allied Vision 1800 U-158c (USB 3.0)
4. **GPIO Controller:** Arduino Nano (ATmega328P) with StandardFirmata (COM4)
5. **Footpedal:** Normally-open momentary switch (D2)
6. **Hotspot Smoothing Device:** Motor (D2) and vibration sensor (D3)
7. **Photodiode circuit:** Analog voltage output (A0, 0-5V range)


## Safety & Compliance Development Guidelines

### Safety First
- All safety-critical code must have unit tests
- Safety interlocks cannot be bypassed in production builds
- Any safety event must be logged immutably
- Regular code reviews for safety-related modules

### Code Quality
- Follow PEP 8 style guidelines
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for all modules (target: 80%+ coverage)

### Documentation
- Keep architecture docs updated
- Document all hardware interfaces
- Maintain change log
- User-facing docs must be clear and comprehensive

## Testing Strategy

### Unit Tests
- Hardware abstraction layer
- Protocol engine
- Image processing algorithms
- Database operations

### Integration Tests
- Hardware communication
- Safety interlock coordination
- UI to backend integration

### Safety Tests
- Footpedal response time
- Photodiode monitoring accuracy
- E-stop effectiveness
- Watchdog timer functionality
- Multi-fault scenarios

## Documentation

**Architecture:** `docs/architecture/`
- 01_system_overview.md - Complete system architecture
- 02_database_schema.md - Database design
- 03_safety_system.md - Safety architecture
- 04_treatment_protocols.md - Protocol design
- 05_image_processing.md - Camera and image processing
- 06_protocol_builder.md - Protocol Builder specification

---

## Project Structure

```
components/
├── camera_module/          [DONE] VmbPy API integration (6 test scripts)
├── actuator_module/        [DONE] Xeryon API integration (6 test scripts)
└── laser_control/          [DONE] Arroyo API documentation and examples

src/
├── ui/
│   ├── main_window.py      [DONE] 4-tab interface with database, event logging
│   └── widgets/
│       ├── subject_widget.py         [DONE] Subject selection and session creation
│       ├── camera_widget.py          [DONE] Live camera streaming, controls
│       ├── treatment_widget.py       [DONE] Integrated laser/actuator controls
│       ├── laser_widget.py           [DONE] Laser power and TEC controls
│       ├── actuator_widget.py        [DONE] Actuator sequences and positioning
│       ├── protocol_builder_widget.py [DEPRECATED] Replaced by sequence builder
│       ├── safety_widget.py          [DONE] Safety status with event logging
│       └── gpio_widget.py            [DONE] GPIO safety interlock display
│
├── core/
│   ├── protocol.py         [DONE] Action-based data model
│   ├── protocol_engine.py  [DONE] Async execution engine
│   ├── safety.py           [DONE] Safety interlock manager (95% complete)
│   ├── session_manager.py  [DONE] Session lifecycle management
│   └── event_logger.py     [DONE] Event logging (50% - core done, hw integration pending)
│
├── hardware/
│   ├── camera_controller.py       [DONE] Camera HAL with PyQt6 integration
│   ├── laser_controller.py        [DONE] Laser HAL with Arroyo protocol
│   ├── actuator_controller.py     [DONE] Actuator HAL with Xeryon API
│   ├── actuator_sequence.py       [DONE] Sequence builder data model
│   └── gpio_controller.py         [DONE] GPIO HAL with Arduino Nano StandardFirmata
│
├── database/
│   ├── models.py           [DONE] SQLAlchemy ORM models
│   └── db_manager.py       [DONE] Database manager with CRUD operations
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

tests/                      [TODO] Test suite
```

---

## Architecture Status

### Phase 2: Hardware Integration ✅ COMPLETE
- **Camera API Exploration** ✅ - VmbPy integration with 6 test scripts
- **Actuator API Exploration** ✅ - Xeryon integration with 6 test scripts
- **Laser API Documentation** ✅ - Arroyo manuals and Python SDK
- **Camera Hardware Abstraction Layer** ✅ - PyQt6 integration with streaming, recording, controls
- **Laser Hardware Abstraction Layer** ✅ - Arroyo serial communication with PyQt6 signals
- **Actuator Hardware Abstraction Layer** ✅ - Xeryon PyQt integration with sequence builder
- **GPIO Hardware Abstraction Layer** ✅ - Arduino Nano with StandardFirmata, tested on COM4

### Phase 3: Core Business Logic ✅ 100% COMPLETE

**User Interface**
- **Main Window & Tab Navigation** ✅ - 4-tab interface with database and event logging
- **Subject Selection Widget** ✅ - Subject search/create, session management, database integration
- **Camera/Alignment Widget** ✅ - Live streaming, exposure/gain controls, capture, recording
- **Treatment Control Widget** ✅ - Integrated 3-column layout (laser, treatment, actuator)
- **Laser Widget** ✅ - Connection, current control, TEC temperature, output enable, **aiming laser control**
- **Actuator Widget** ✅ - Sequence builder with 6 action types, homing, positioning
- **Safety Status Widget** ✅ - Safety status, event logging, emergency stop, GPIO interlock display
- **GPIO Widget** ✅ - Motor control, vibration monitoring, photodiode display
- **Protocol Builder Widget** ⚠️ [DEPRECATED] - Replaced by actuator sequence builder

**Core Business Logic**
- **Protocol Data Model** ✅ - 5 action types with validation
- **Protocol Execution Engine** ✅ - Async engine with pause/resume/stop, hardware integration, retry logic
- **Actuator Sequence Model** ✅ - 6 action types with accel/decel, laser power
- **Safety System** ✅ (100%) - SafetyManager with state machine, GPIO integration, laser enforcement
- **Session Management** ✅ (100%) - Complete session lifecycle, database persistence, folder creation
- **Event Logger** ✅ (100%) - EventLogger with 25+ event types, database + file persistence, hardware integration

**Data Layer**
- **Database Schema Design** ✅ - Comprehensive schema documented
- **Database Models** ✅ - SQLAlchemy ORM models (TechUser, Subject, Protocol, Session, SafetyLog)
- **Database Operations** ✅ - DatabaseManager with CRUD operations
- **Database Migrations** ⏳ - Alembic setup pending

**Image Processing** ⏳ TODO
- **Ring Detection** ⏳ - Hough circle transform
- **Focus Measurement** ⏳ - Laplacian variance
- **Video Recording** ⏳ - OpenCV integration
- **Frame Processing Pipeline** ⏳ - Real-time processing

**Testing & Quality** ⏳ TODO
- **Test Framework** ⏳ - Pytest configuration
- **Unit Tests** ⏳ - Component tests
- **Integration Tests** ⏳ - System tests
- **Safety Tests** ⏳ - FMEA and validation

---

## Recent Updates (2025-10-25)

### Latest: Aiming Laser Control ✅ NEW
- Added separate aiming laser control to GPIO controller (Pin D4)
- Aiming laser ON/OFF buttons in Laser Widget
- Independent control from treatment laser (Arroyo)
- Event logging integration for aiming laser state changes

### Phase 2: Hardware Abstraction Layer - COMPLETE ✅
All 4 hardware controllers fully implemented with PyQt6 integration:

1. **Camera HAL** ✅
   - VmbPy API integration with Allied Vision 1800 U-158c
   - Thread-safe streaming with Qt signals
   - Live video display, exposure/gain controls, capture, recording

2. **Laser HAL** ✅
   - Arroyo Instruments serial communication (38400 baud)
   - Current control (0-2000 mA), TEC temperature control
   - Output enable/disable with verification
   - 8 PyQt6 signals for real-time monitoring

3. **Actuator HAL** ✅
   - Xeryon linear stage integration
   - Position control, homing procedures
   - Sequence builder with 6 action types, loop support
   - Acceleration/deceleration control per step

4. **GPIO HAL** ✅
   - **Migrated to Arduino Nano** with StandardFirmata (from FT232H)
   - pyfirmata2 library for Python 3.12 compatibility
   - Smoothing device motor control (D2 digital output)
   - Vibration sensor monitoring (D3 digital input, debounced)
   - **Aiming laser control (D4 digital output)** - NEW!
   - Photodiode power monitoring (A0 analog input, 0-5V)
   - Safety interlock logic (motor ON + vibration detected)
   - Hardware tested and validated on COM4

### Phase 3: Core Business Logic - 100% COMPLETE ✅

**Priority 1: Safety System** (100% complete) ✅
- Central SafetyManager with state machine (SAFE/UNSAFE/EMERGENCY_STOP)
- GPIO interlock integration
- Laser enable enforcement
- Safety event logging display
- Emergency stop UI wiring
- Session validity checking

**Priority 2: Session Management** (100% complete) ✅
- SQLite database with SQLAlchemy ORM
- Database models: TechUser, Subject, Protocol, Session, SafetyLog
- Session lifecycle manager with automatic folder creation
- Subject widget GUI integration (search/create subjects, start sessions)
- Session folders: data/sessions/P-YYYY-NNNN/TIMESTAMP/
- Safety system integration (session valid flag)

**Priority 3: Event Logging** (100% complete) ✅
- EventLogger with 25+ event types (safety, hardware, treatment, user, system)
- Dual persistence: Database (SafetyLog table) + JSONL file backup
- Session and technician association
- PyQt6 signals for real-time UI updates
- System startup/shutdown event logging
- Complete hardware controller integration
- Safety widget database event display with severity-based formatting

**Priority 4: Protocol Execution** (100% complete) ✅
- ProtocolEngine wired to MainWindow and hardware controllers
- Hardware integration for laser power and actuator movement
- Real-time execution feedback with progress bar and status updates
- Comprehensive error handling with retry logic (3 retries, 1s delay, 60s timeout)
- Pause/resume/stop functionality tested and validated
- Complete test suite: basic execution, pause/resume, emergency stop

### Treatment Tab Reorganization ✅
- 3-column layout: Laser (left), Treatment (middle), Actuator (right)
- Integrated laser and actuator controls in single view
- Removed redundant Protocol Builder tab

---

---

## Phase 4: Architectural Improvements - 100% COMPLETE ✅

All architectural improvements completed (2025-10-25):

**Priority 1: Safety Watchdog Timer** (100%) ✅
- Arduino AVR hardware watchdog (1000ms timeout, ISR emergency shutdown)
- Python SafetyWatchdog class with 500ms heartbeat (50% safety margin)
- Custom serial protocol for GPIO controller
- MainWindow integration with automatic start/stop lifecycle
- Complete architecture documentation (`docs/architecture/06_safety_watchdog.md`)

**Priority 2: Configuration Management** (100%) ✅
- Pydantic-based type-safe configuration models (`src/config/models.py`)
- YAML configuration file (`config.yaml`) with hardware/safety/GUI sections
- Centralized config loader with singleton pattern (`src/config/config_loader.py`)
- Field validation with ge/le constraints (e.g., FPS 1.0-60.0)
- Environment variable override support

**Priority 3: Session Management UI** (100%) ✅
- End Session button with confirmation dialog
- View Sessions dialog (900x600) with color-coded status table
- Session history browser with filtering by subject
- Database query methods in DatabaseManager
- Complete UI state management and cleanup handlers

**Priority 4: UI Enhancements** (100%) ✅
- Close Program button in status bar with confirmation
- Hardware-independent sequence building (works offline)
- Clear status messages for hardware requirements
- Improved developer experience for offline development

**Priority 5: Hardware Controller ABC** (100%) ✅
- Abstract base class combining QObject + ABC (QObjectABCMeta metaclass)
- Enforced interface: connect(), disconnect(), get_status()
- Required signals: connection_changed, error_occurred
- Type-safe with Python 3.12+ annotations
- Backward compatible with existing controllers
- Complete usage documentation (`docs/hardware_controller_base_usage.md`)

---

**Last Updated:** 2025-10-25
**Project Phase:** Phase 4 COMPLETE (100%), Phase 5 Planning
**Next Priority:** Testing & Quality Assurance (pytest framework, unit tests, integration tests)

**For current project status and detailed progress, see:**
- `docs/project/NEXT_STEPS.md` - Week-by-week roadmap for Phase 4
- `docs/architecture/ARCHITECTURAL_DEBT.md` - Complete analysis of improvements
- `docs/project/PROJECT_STATUS.md` - Complete project state
- `presubmit/WORK_LOG.md` - Real-time session tracking
