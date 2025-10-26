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
│   ├── camera_controller.py       [DONE] Camera HAL with PyQt6 integration (thread-safe)
│   ├── laser_controller.py        [DONE] Laser HAL with Arroyo protocol (thread-safe)
│   ├── actuator_controller.py     [DONE] Actuator HAL with Xeryon API (thread-safe)
│   ├── actuator_sequence.py       [DONE] Sequence builder data model
│   └── gpio_controller.py         [DONE] GPIO HAL with Arduino Nano StandardFirmata (thread-safe)
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

**Testing & Quality** 🔄 IN PROGRESS (75% Complete)
- **Test Framework** ✅ - Pytest configured with hardware mocks
- **Hardware Mock Layer** ✅ - All 4 controllers mocked (54/54 tests passing)
- **Thread Safety** ✅ - All controllers protected with RLock (7/7 tests passing)
- **Unit Tests** 🔄 - In progress (mock layer complete)
- **Integration Tests** ⏳ - System tests pending
- **Safety Tests** ⏳ - FMEA and validation pending
