# TOSCA Laser Control System

## Overview

This is a comprehensive laser control system. The system integrates:

- **Laser Control** - Arroyo Instruments TEC Controller (serial communication)
- **Linear Actuator** - Xeryon actuator for ring size control
- **Camera System** - Allied Vision camera with VmbPy SDK for alignment and monitoring
- **GPIO Safety Interlocks** - Adafruit FT232H breakouts for footpedal, smoothing device, and photodiode monitoring
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
- **pyserial** - Arroyo laser communication
- **Xeryon API** - Linear actuator control
- **VmbPy** - Allied Vision camera SDK
- **adafruit-blinka** - FT232H GPIO/ADC

### Supporting Libraries
- **pyqtgraph** - Real-time plotting
- **sqlalchemy** - Database ORM
- **alembic** - Database migrations
- **pydantic** - Configuration validation

## Hardware Components
1. **Laser Controller:** Arroyo Instruments laser driver and TEC Controller
2. **Linear Actuator:** Xeryon linear stage
3. **Camera:** Allied Vision camera (USB 3.0 / GigE)
4. **GPIO Controllers:** 2x Adafruit FT232H Breakout (USB-C)
5. **Footpedal:** Normally-open momentary switch
6. **Hotspot Smoothing Device:** With digital signal output
7. **Photodiode circuit:** With voltage output (0-5V range)


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
└── actuator_module/        [DONE] Xeryon API integration (6 test scripts)

src/
├── ui/
│   ├── main_window.py      [DONE] 5-tab interface
│   └── widgets/
│       ├── subject_widget.py         [DONE] Subject selection
│       ├── camera_widget.py          [DONE] Live camera streaming, controls
│       ├── treatment_widget.py       [DONE] Manual controls
│       ├── protocol_builder_widget.py [DONE] Protocol creation UI
│       └── safety_widget.py          [DONE] Safety status
│
├── core/
│   ├── protocol.py         [DONE] Action-based data model
│   ├── protocol_engine.py  [DONE] Async execution engine
│   ├── safety.py           [TODO] Safety interlock manager
│   ├── session.py          [TODO] Session management
│   └── event_logger.py     [TODO] Event logging
│
├── hardware/
│   ├── camera_controller.py    [DONE] Camera HAL with PyQt6 integration
│   ├── laser_controller.py     [TODO] Laser HAL
│   ├── actuator_controller.py  [TODO] Actuator HAL
│   └── gpio_controller.py      [TODO] GPIO HAL
│
├── database/
│   ├── models.py           [TODO] SQLAlchemy models
│   └── operations.py       [TODO] CRUD operations
│
└── image_processing/
    ├── ring_detector.py    [TODO] Hough circle detection
    ├── focus_measure.py    [TODO] Laplacian variance
    └── video_recorder.py   [TODO] OpenCV recording

data/
├── protocols/              [DONE] Protocol JSON storage
├── logs/                   [DONE] Application logs
└── sessions/               [TODO] Session recordings

tests/                      [TODO] Test suite
```

**Legend:** [DONE] Complete | [TODO] Not started

**Current Status:** Phase 2 in progress (25% complete) - Camera HAL complete

---

## Architecture Status

### Hardware Integration
- **Camera API Exploration** [DONE] - VmbPy integration with 6 test scripts
- **Actuator API Exploration** [DONE] - Xeryon integration with 6 test scripts
- **Camera Hardware Abstraction Layer** [DONE] - PyQt6 integration with streaming, recording, controls
- **Laser Hardware Abstraction Layer** [TODO] - Arroyo serial communication
- **Actuator Hardware Abstraction Layer** [TODO] - Xeryon PyQt integration
- **GPIO Hardware Abstraction Layer** [TODO] - FT232H safety interlocks

### User Interface
- **Main Window & Tab Navigation** [DONE] - 5-tab interface
- **Subject Selection Widget** [DONE] - Subject search and session start
- **Camera/Alignment Widget** [DONE] - Live camera streaming, exposure/gain controls, capture, recording
- **Treatment Control Widget** [DONE] - Manual laser/actuator controls (placeholders)
- **Protocol Builder Widget** [DONE] - Action-based protocol creation
- **Safety Status Widget** [DONE] - Safety indicator placeholder

### Core Business Logic
- **Protocol Data Model** [DONE] - 5 action types with validation
- **Protocol Execution Engine** [DONE] - Async engine with pause/resume/stop
- **Safety System** [TODO] - Interlock manager and state machine
- **Session Management** [TODO] - Session lifecycle and tracking
- **Event Logger** [TODO] - Immutable audit trail

### Data Layer
- **Database Schema Design** [DONE] - Documented in architecture docs
- **Database Models** [TODO] - SQLAlchemy ORM models
- **Database Operations** [TODO] - CRUD operations
- **Database Migrations** [TODO] - Alembic setup

### Image Processing
- **Ring Detection** [TODO] - Hough circle transform
- **Focus Measurement** [TODO] - Laplacian variance
- **Video Recording** [TODO] - OpenCV integration
- **Frame Processing Pipeline** [TODO] - Real-time processing

### Testing & Quality
- **Test Framework** [TODO] - Pytest configuration
- **Unit Tests** [TODO] - Component tests
- **Integration Tests** [TODO] - System tests
- **Safety Tests** [TODO] - FMEA and validation

---

## Recent Updates (2025-10-23)

### Camera Hardware Abstraction Layer - COMPLETE ✅

The camera system is now fully operational with:
- **Live Streaming**: 30 FPS camera feed with hardware frame rate control
- **Manual Controls**: Exposure time, gain, white balance
- **Auto Features**: Auto-exposure, auto-gain, auto-white-balance
- **Image Capture**: Timestamped PNG capture with custom paths
- **Video Recording**: MP4 video recording with codec support
- **Real-time Metadata**: Live display of exposure, gain, resolution, FPS
- **Testing Documentation**: 17 test procedures + automated validation script

### New Project Standard: Hardware API Usage Rule

All hardware control implementations must now:
1. Check hardware API documentation FIRST
2. Use native hardware features (frame rate, positioning, etc.)
3. Only use software workarounds if hardware doesn't support the feature
4. Document why software solutions are used

See `docs/project/CODING_STANDARDS.md` for complete details.

---

**Last Updated:** 2025-10-23 (Camera HAL Complete)
