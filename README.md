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

**Project Management:** `docs/project/`
- PROJECT_STATUS.md - Current project state
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
