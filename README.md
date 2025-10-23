# TOSCA Laser Control System

**Project Status:** Phase 1 Complete - GUI Shell & Camera Module ✓
**Date:** 2025-10-22

## Overview

This is a comprehensive laser control system. The system integrates:

- **Laser Control** - Arroyo Instruments TEC Controller (serial communication)
- **Linear Actuator** - Xeryon actuator for ring size control
- **Camera System** - Allied Vision camera with VmbPy SDK for alignment and monitoring
- **GPIO Safety Interlocks** - Adafruit FT232H breakouts for footpedal, smoothing device, and photodiode monitoring
- **Patient Management** - SQLite database for longitudinal patient tracking
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

### Patient Management
- Anonymized patient profiles
- Multi-session longitudinal tracking
- Technician/operator authentication
- Complete treatment history

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

## Project Directory Structure

**Status Legend:**
- ✓ Complete and tested
- ⏳ In progress
- ⚪ Not started
- 📝 Documentation only

```
TOSCA-dev/
│
├── 📁 .github/                                 ✓ GitHub Configuration
│   └── PULL_REQUEST_TEMPLATE.md               ✓ PR template with coding standards
│
├── 📁 camera_module/                           ✓ Camera Exploration Module (COMPLETE)
│   ├── README.md                               ✓ VmbPy API documentation (500+ lines)
│   ├── INTEGRATION_FEATURES.md                 ✓ Integration spec (736 lines)
│   ├── LESSONS_LEARNED.md                      ✓ API quirks documented (3 issues)
│   ├── 📁 examples/                            ✓ Test Scripts
│   │   ├── 01_list_cameras.py                  ✓ Camera detection (Allied Vision 1800 U-158c)
│   │   ├── 02_camera_info.py                   ✓ Camera specs (1456x1088, RGB8)
│   │   ├── 03_capture_single_frame.py          ✓ Frame capture with timestamps
│   │   ├── 04_explore_features.py              ✓ Feature exploration (223/313 features)
│   │   ├── 05_continuous_stream.py             ✓ Streaming (39.4 FPS sustained)
│   │   └── 06_set_auto_exposure.py             ✓ Auto exposure control
│   └── 📁 output/                              ✓ Test images (git-ignored)
│
├── 📁 actuator_module/                         ✓ Actuator Exploration Module (COMPLETE)
│   ├── README.md                               ✓ Xeryon API documentation (500+ lines)
│   ├── LESSONS_LEARNED.md                      ✓ API quirks documented (10 issues)
│   ├── Xeryon.py                               ✓ Vendor library v1.88 (excluded from linting)
│   ├── settings_default.txt                    ✓ Default stage parameters
│   ├── 📁 examples/                            ✓ Test Scripts (ready for hardware)
│   │   ├── 01_list_ports.py                    ✓ List available COM ports
│   │   ├── 02_connect_actuator.py              ✓ Connect and display stage info
│   │   ├── 03_find_index.py                    ✓ Find home position (required for positioning)
│   │   ├── 04_absolute_positioning.py          ✓ Test setDPOS() 0-3000 µm TOSCA range
│   │   ├── 05_relative_movement.py             ✓ Test step() incremental movement
│   │   └── 06_speed_and_limits.py              ✓ Test SSPD speed control and HLIM/LLIM safety
│   └── 📁 output/                              ✓ Test data (git-ignored)
│
├── 📁 docs/                                    ⏳ Documentation
│   │
│   ├── 📁 architecture/                        ✓ Technical Architecture (COMPLETE)
│   │   ├── 01_system_overview.md               ✓ System design and technology stack
│   │   ├── 02_database_schema.md               ✓ Database schema and models
│   │   ├── 03_safety_system.md                 ✓ Safety interlocks and state machine
│   │   ├── 04_treatment_protocols.md           ✓ Protocol engine design
│   │   └── 05_image_processing.md              ✓ Ring detection and focus measurement
│   │
│   ├── 📁 project/                             ✓ Project Management
│   │   ├── WORK_LOG.md                         ✓ Current session tracking
│   │   ├── PROJECT_STATUS.md                   ✓ Current project state
│   │   ├── START_HERE.md                       ✓ Quick start for AI sessions
│   │   ├── SESSION_PROMPT.md                   ✓ Session initialization template
│   │   ├── CODING_STANDARDS.md                 ✓ Development rules and standards
│   │   ├── CONFIGURATION.md                    ✓ Config file reference (11 files)
│   │   ├── README.md                           ✓ Documentation index
│   │   └── 📁 archive/                         ✓ Archived work logs
│   │       └── WORK_LOG_2025-10-22_camera-module.md  ✓ Camera module session
│   │
│   └── DEVELOPMENT_ENVIRONMENT_SETUP.md        ✓ Complete setup guide
│
├── 📁 src/                                     ⏳ Main Application
│   │
│   ├── main.py                                 ✓ Application entry point (PyQt6 launcher)
│   │
│   ├── 📁 ui/                                  ✓ User Interface (Phase 1 Complete)
│   │   ├── __init__.py                         ✓ Package init
│   │   ├── main_window.py                      ✓ Main window with 4-tab layout
│   │   └── 📁 widgets/                         ✓ UI Widgets
│   │       ├── __init__.py                     ✓ Package init
│   │       ├── patient_widget.py               ✓ Patient selection and session initiation
│   │       ├── camera_widget.py                ✓ Camera feed placeholder and controls
│   │       ├── treatment_widget.py             ✓ Laser power and ring size controls
│   │       └── safety_widget.py                ✓ Safety interlocks and E-stop
│   │
│   ├── 📁 hardware/                            ⚪ Hardware Abstraction Layer (Next: Phase 2)
│   │   ├── __init__.py                         ⚪ Not started
│   │   ├── camera_controller.py                ⚪ Camera HAL (spec ready in camera_module/)
│   │   ├── laser_controller.py                 ⚪ Arroyo TEC Controller HAL
│   │   ├── actuator_controller.py              ⚪ Xeryon actuator HAL
│   │   └── gpio_controller.py                  ⚪ FT232H GPIO/ADC HAL
│   │
│   ├── 📁 core/                                ⚪ Business Logic
│   │   ├── __init__.py                         ⚪ Not started
│   │   ├── safety.py                           ⚪ Safety interlock manager (Phase 3)
│   │   ├── session.py                          ⚪ Session management
│   │   ├── protocol_engine.py                  ⚪ Treatment protocol execution
│   │   └── event_logger.py                     ⚪ Event logging system
│   │
│   ├── 📁 database/                            ⚪ Database Layer
│   │   ├── __init__.py                         ⚪ Not started
│   │   ├── models.py                           ⚪ SQLAlchemy models (Phase 4)
│   │   ├── operations.py                       ⚪ CRUD operations
│   │   └── migrations/                         ⚪ Alembic migrations
│   │
│   ├── 📁 image_processing/                    ⚪ Computer Vision
│   │   ├── __init__.py                         ⚪ Not started
│   │   ├── ring_detector.py                    ⚪ Hough Circle Transform
│   │   ├── focus_measure.py                    ⚪ Laplacian variance
│   │   ├── frame_processor.py                  ⚪ Unified pipeline
│   │   └── video_recorder.py                   ⚪ OpenCV VideoWriter
│   │
│   ├── 📁 config/                              ⚪ Configuration
│   │   └── __init__.py                         ⚪ Not started
│   │
│   └── 📁 utils/                               ⚪ Utilities
│       └── __init__.py                         ⚪ Not started
│
├── 📁 tests/                                   ⚪ Test Suite
│   ├── __init__.py                             ⚪ Not started
│   ├── 📁 test_hardware/                       ⚪ Hardware tests
│   ├── 📁 test_core/                           ⚪ Business logic tests
│   ├── 📁 test_ui/                             ⚪ UI tests
│   └── 📁 test_integration/                    ⚪ Integration tests
│
├── 📁 data/                                    ✓ Application Data (git-ignored)
│   ├── 📁 logs/                                ✓ Application logs
│   │   └── tosca.log                           ✓ Main log file
│   ├── 📁 sessions/                            ⚪ Session recordings
│   └── laser_control.db                        ⚪ SQLite database
│
├── 📁 venv/                                    ✓ Virtual Environment (git-ignored)
│
├── 📄 Configuration Files                      ✓ Project Configuration
│   ├── .gitignore                              ✓ Git ignore rules
│   ├── .pre-commit-config.yaml                 ✓ Pre-commit hooks (black, flake8, mypy, isort)
│   ├── .flake8                                 ✓ Linting configuration
│   ├── .pylintrc                               ✓ Pylint configuration
│   ├── pyproject.toml                          ✓ Black and project settings
│   ├── pytest.ini                              ✓ Pytest configuration
│   ├── setup.py                                ✓ Package setup
│   ├── requirements.txt                        ✓ Python dependencies (100+ packages)
│   └── .env.example                            ✓ Environment variables template
│
├── 📄 Documentation Files                      ✓ Root Documentation
│   ├── README.md                               ✓ This file (you are here)
│   └── NEW_SESSION_GUIDE.md                    ✓ AI session onboarding guide
│
└── 📄 Hidden Files
    └── .mcp.json                               ✓ MCP server config (git-ignored)
```

## Component Status Summary

### ✓ Complete (Ready for Integration)
- Camera module: 6 test scripts, all passing (39.4 FPS)
- Actuator module: 6 test scripts ready for hardware (0-3000 µm range)
- GUI shell: 4-tab interface with all widgets
- Documentation: Architecture specs, coding standards, work logs
- Configuration: Pre-commit hooks, linting, type checking

### ⏳ In Progress
- None currently

### ⚪ Next Priority (Phase 2 - HAL Integration)
- Hardware abstraction layer for camera, laser, actuator
- Safety interlock system
- Database models and operations

### 📊 Overall Progress
- **Phase 0 (Setup):** 100% ✓
- **Phase 1 (Camera + GUI Shell):** 100% ✓
- **Phase 2 (HAL Integration):** 0% ⚪
- **Phase 3 (Safety System):** 0% ⚪
- **Phase 4 (Patient Management):** 0% ⚪

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

## Hardware Requirements

### Components
1. **Laser Controller:** Arroyo Instruments TEC Controller
2. **Linear Actuator:** Xeryon linear stage
3. **Camera:** Allied Vision camera (USB 3.0 / GigE)
4. **GPIO Controllers:** 2x Adafruit FT232H Breakout (USB-C)
5. **Footpedal:** Normally-open momentary switch
6. **Hotspot Smoothing Device:** With digital signal output
7. **Photodiode:** With voltage output (0-5V range)

### Computer
- **OS:** Windows 10
- **Form Factor:** Mini PC
- **Minimum Specs:**
  - Intel i5 or equivalent
  - 8GB RAM
  - 256GB SSD
  - Multiple USB 3.0 ports

## Installation

**Note:** Installation procedures will be documented once development begins.

### Prerequisites
```bash
# Python 3.10 or higher
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Development Phases

### Phase 0: Initial Setup ✓ COMPLETE
- [x] Repository and Git configuration
- [x] Virtual environment (Python 3.12.10)
- [x] Pre-commit hooks (black, flake8, mypy, isort)
- [x] Requirements.txt (100+ packages)
- [x] Project structure created
- [x] Architecture documentation (5 docs)
- [x] Coding standards established
- [x] AI onboarding system (NEW_SESSION_GUIDE.md)

### Phase 1: Camera Module + GUI Shell ✓ COMPLETE
- [x] Camera module exploration (Allied Vision 1800 U-158c)
- [x] VmbPy API documentation (500+ lines)
- [x] 6 camera test scripts (all passing, 39.4 FPS)
- [x] Camera integration specification (736 lines)
- [x] Lessons learned system (API quirks documented)
- [x] Basic GUI shell with PyQt6
- [x] 4-tab interface (Patient, Camera, Treatment, Safety)
- [x] Status bar with hardware indicators
- [x] All widgets with proper layouts

### Phase 2: Hardware Abstraction Layer (HAL) ⏳ NEXT
- [ ] Create src/hardware/ directory structure
- [ ] Implement CameraController HAL
- [ ] Implement LaserController HAL stub
- [ ] Implement ActuatorController HAL stub
- [ ] Implement GPIO controller for safety interlocks
- [ ] Wire up GUI to HAL connections
- [ ] Update status bar based on hardware state

### Phase 3: Safety System ⚪ NOT STARTED
- [ ] Safety interlock manager (src/core/safety.py)
- [ ] Interlock state tracking
- [ ] Enable/disable treatment based on safety
- [ ] Emergency stop functionality
- [ ] Safety event logging to GUI
- [ ] Hardware watchdog implementation

### Phase 4: Patient Management & Database ⚪ NOT STARTED
- [ ] Database schema implementation
- [ ] Patient models (SQLAlchemy)
- [ ] Patient search functionality
- [ ] Session management
- [ ] Treatment history logging
- [ ] Database migrations (Alembic)

### Phase 5: Treatment Protocols ⚪ NOT STARTED
- [ ] Protocol engine implementation
- [ ] Manual treatment control
- [ ] Protocol builder UI
- [ ] Power ramping algorithms
- [ ] Ring size control via actuator
- [ ] Real-time protocol adjustments

### Phase 6: Image Processing ⚪ NOT STARTED
- [ ] Ring detection (Hough Circle Transform)
- [ ] Focus measurement (Laplacian variance)
- [ ] Frame processor pipeline
- [ ] Video recording (OpenCV VideoWriter)
- [ ] Calibration procedures

### Phase 7: Testing & Validation ⚪ NOT STARTED
- [ ] Unit tests (80%+ coverage target)
- [ ] Integration tests
- [ ] Safety tests (FMEA)
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Bug fixes and refinement

## Safety & Compliance

**CRITICAL:** This system controls a laser and includes safety interlocks.

Before operation:
1. **Risk Analysis** - Perform comprehensive safety review
2. **Safety Testing** - Document all safety system tests
3. **Validation** - Independent safety review
4. **User Training** - Complete operator training program
5. **Maintenance Protocol** - Regular safety verification schedule

## Development Guidelines

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

### User Acceptance Testing
- Research workflow validation
- Operator feedback
- Usability assessment

## Contributing

**This is a research system with safety-critical components.** All contributions must:
1. Pass safety review
2. Include comprehensive tests
3. Not compromise any safety features
4. Be thoroughly documented

## License

**TBD** - To be determined based on deployment requirements

## Contact

**Project Lead:** [To be assigned]
**Safety Engineer:** [To be assigned]

## Acknowledgments

- Arroyo Instruments for laser controller documentation
- Xeryon for actuator API
- Allied Vision for VmbPy SDK
- Adafruit for FT232H libraries

---

## Quick Start (Once Development Complete)

```bash
# Clone repository
git clone <repository-url>
cd laser-control-system

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m src.database.init_db

# Run application
python src/main.py
```

## Documentation

**NEW_SESSION_GUIDE.md** ⭐ - How to onboard new AI instances (START HERE)

**Project Management:** `docs/project/`
- START_HERE.md - New AI session quick start
- PROJECT_STATUS.md - Current project state
- WORK_LOG.md - Real-time session tracking
- CODING_STANDARDS.md - Development rules
- CONFIGURATION.md - Config file reference

**Architecture:** `docs/architecture/`

1. **01_system_overview.md** - Start here for complete system architecture
2. **02_database_schema.md** - Database design and schema
3. **03_safety_system.md** - Critical safety architecture
4. **04_treatment_protocols.md** - Protocol design and execution
5. **05_image_processing.md** - Camera and image processing

Additional docs (to be created):
- **user_manual.md** - End-user guide
- **installation.md** - Setup and installation
- **maintenance.md** - Calibration and maintenance procedures
- **troubleshooting.md** - Common issues and solutions

---

**Last Updated:** 2025-10-22 22:40
**Project Status:** Phase 1 Complete - Camera Module (6 scripts) ✓ + GUI Shell (4 tabs) ✓ → Phase 2 HAL Next
