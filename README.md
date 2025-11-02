# TOSCA Laser Control System

Version: 0.9.12-alpha
Status: RESEARCH MODE - NOT for Clinical Use
Date: 2025-11-02

## RESEARCH MODE WARNING

This system is configured for RESEARCH USE ONLY.

CRITICAL WARNINGS:
- This software is NOT FDA-cleared or approved for clinical use
- Database encryption is NOT implemented - all data stored in plaintext
- User authentication is NOT implemented - no access controls
- NOT suitable for protected health information (PHI)
- NOT suitable for patient treatment

This system is intended for:
- Research and development
- Hardware testing and calibration
- Algorithm development
- Educational purposes

Do NOT use this system for:
- Clinical patient treatment
- Protected health information (PHI) storage
- Production medical device operation
- Any regulated medical environment

---

## System Description

TOSCA is a laser control system integrating:
- Precision laser power control (0-10W diode laser)
- Linear actuator positioning (0-20mm range)
- Machine vision (Allied Vision 1800 U-158c camera, 30 FPS)
- Multi-layer safety architecture with hardware interlocks
- Comprehensive session and event logging
- Configurable treatment protocols with automated execution

### Recent Achievements (November 2025)

**Hardware-Free Testing Infrastructure Complete:**
- 5 comprehensive mock controllers (Camera, Laser, TEC, Actuator, GPIO)
- 148+ tests across all hardware subsystems (85% pass rate)
- 9 failure simulation modes for robustness testing
- Complete test documentation (1,255 lines in tests/mocks/README.md)
- **Impact:** Continuous integration enabled, no physical hardware required for testing

**Documentation Unified:**
- All core documentation updated to v0.9.12-alpha
- Historical content archived to docs/archive/
- Comprehensive task completion report (20/20 tasks done)

---

## Hardware Configuration

### Primary Devices

| Component | Model | Interface | Configuration |
|-----------|-------|-----------|---------------|
| Laser Driver | Arroyo 6300 | RS-232 Serial | COM10, 38400 baud |
| TEC Controller | Arroyo 5305 | RS-232 Serial | COM9, 38400 baud |
| Linear Actuator | Xeryon linear stage | RS-232 Serial | COM3, 9600 baud |
| Camera | Allied Vision 1800 U-158c | USB 3.0 | VmbPy SDK |
| GPIO Controller | Arduino Uno (ATmega328P) | USB Serial | COM4, 115200 baud |

### Safety Hardware

| Component | Connection | Specification |
|-----------|------------|---------------|
| Footpedal | Arduino D5 (planned) | Normally-open momentary switch |
| Smoothing Motor | Arduino D9 (PWM) | DC coreless motor 7x25mm, 0-153 PWM (0-3.0V max) |
| Accelerometer | Arduino I2C (A4/A5) | MPU6050 at 0x68 or ADXL345 at 0x53 |
| Photodiode | Arduino A0 (ADC) | 0-5V analog voltage, 10-bit ADC |
| Aiming Laser | Arduino D4 | 650nm red laser diode |

---

## Technology Stack

Core Platform:
- Python 3.10+
- PyQt6
- Windows 10/11 (64-bit)
- SQLite 3.x (unencrypted)

Key Libraries:
- SQLAlchemy (Database ORM)
- Pydantic (Configuration validation)
- OpenCV (Image processing)
- NumPy (Numerical operations)
- pyqtgraph (Real-time plotting)
- pyserial (Serial communication)
- VmbPy (Allied Vision camera SDK)

---

## Project Structure

```
TOSCA-dev/
│
├── src/
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── dialogs/
│   │   └── widgets/
│   │       ├── subject_widget.py
│   │       ├── camera_widget.py
│   │       ├── camera_hardware_panel.py
│   │       ├── treatment_setup_widget.py
│   │       ├── active_treatment_widget.py
│   │       ├── laser_widget.py
│   │       ├── tec_widget.py
│   │       ├── actuator_connection_widget.py
│   │       ├── safety_widget.py
│   │       ├── gpio_widget.py
│   │       ├── interlocks_widget.py
│   │       ├── smoothing_status_widget.py
│   │       ├── protocol_selector_widget.py
│   │       ├── protocol_builder_widget.py
│   │       ├── line_protocol_builder.py
│   │       ├── config_display_widget.py
│   │       └── view_sessions_dialog.py
│   │
│   ├── core/
│   │   ├── protocol.py
│   │   ├── protocol_line.py
│   │   ├── protocol_engine.py
│   │   ├── safety.py
│   │   ├── safety_watchdog.py
│   │   ├── session.py
│   │   ├── session_manager.py
│   │   └── event_logger.py
│   │
│   ├── hardware/
│   │   ├── hardware_controller_base.py
│   │   ├── camera_controller.py
│   │   ├── laser_controller.py
│   │   ├── tec_controller.py
│   │   ├── actuator_controller.py
│   │   ├── actuator_sequence.py
│   │   └── gpio_controller.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── db_manager.py
│   │
│   ├── config/
│   │   ├── models.py
│   │   └── config_loader.py
│   │
│   └── image_processing/
│       ├── ring_detector.py (not implemented)
│       ├── focus_measure.py (not implemented)
│       └── video_recorder.py (implemented in camera_controller)
│
├── tests/
│   ├── mocks/
│   │   ├── mock_hardware_base.py
│   │   ├── mock_camera_controller.py
│   │   ├── mock_laser_controller.py
│   │   ├── mock_actuator_controller.py
│   │   └── mock_gpio_controller.py
│   ├── hardware/
│   ├── actuator/
│   ├── gpio/
│   ├── test_thread_safety.py
│   └── test_realtime_safety_monitoring.py
│
├── firmware/
│   └── arduino_watchdog/
│       └── arduino_watchdog.ino
│
├── docs/
│   ├── regulatory/
│   │   ├── PRODUCT_REQUIREMENTS_DOCUMENT.md
│   │   └── TECHNICAL_SPECIFICATION.md
│   └── architecture/
│       ├── 01_system_overview.md
│       ├── 02_database_schema.md
│       ├── 03_safety_system.md
│       ├── 04_treatment_protocols.md
│       ├── 06_protocol_builder.md
│       ├── 07_safety_watchdog.md
│       ├── 09_test_architecture.md
│       ├── 10_concurrency_model.md
│       ├── SAFETY_SHUTDOWN_POLICY.md
│       ├── ADR-001-protocol-consolidation.md
│       └── ADR-002-dependency-injection-pattern.md
│
├── data/
│   ├── tosca.db
│   ├── logs/
│   │   └── events_YYYYMMDD.jsonl
│   ├── images/
│   │   └── capture_YYYYMMDD_HHMMSS.png
│   ├── videos/
│   │   └── recording_YYYYMMDD_HHMMSS.mp4
│   └── protocols/
│       └── [protocol_name].json
│
├── review_reports/
│   ├── README.md
│   ├── 01_EXECUTIVE_SUMMARY.md
│   ├── 02_PHASE1_ARCHITECTURE_CODE_QUALITY.md
│   ├── 03_PHASE2_SECURITY_PERFORMANCE.md
│   ├── 04_ACTION_PLAN_RECOMMENDATIONS.md
│   ├── NON_SECURITY_TODO_LIST.md
│   ├── RESEARCH_MODE_ROADMAP.md
│   └── CLINICAL_DEPLOYMENT_ROADMAP.md
│
├── config.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Architecture Implementation Status

### User Interface
- [x] Main window with 4-tab interface
- [x] Global toolbar with E-Stop button
- [x] Subject widget (selection, creation, session management)
- [x] Camera widget (live streaming, controls)
- [x] Camera hardware panel (diagnostics)
- [x] Treatment setup widget (protocol selector)
- [x] Active treatment widget (monitoring dashboard)
- [x] Laser widget (power controls for treatment laser)
- [x] TEC widget (temperature controls)
- [x] Actuator connection widget (positioning)
- [x] Safety widget (status display, event logging)
- [x] GPIO widget (safety interlock display)
- [x] Interlocks widget (consolidated safety status)
- [x] Smoothing status widget (motor control and monitoring)
- [x] Protocol selector widget (visual library browser)
- [x] Protocol builder widget (action-based protocol builder)
- [x] Line protocol builder (concurrent action protocol builder)
- [x] Config display widget (configuration viewer)
- [x] View sessions dialog (session history viewer)

### Core Business Logic
- [x] Protocol data model (action-based)
- [x] Protocol line data model (concurrent actions)
- [x] Protocol engine (async execution)
- [x] Safety manager (central safety state machine)
- [x] Safety watchdog (hardware heartbeat)
- [x] Session data model
- [x] Session manager (lifecycle management)
- [x] Event logger (immutable logging)

### Hardware Abstraction Layer
- [x] Hardware controller base (ABC with QObject integration)
- [x] Camera controller (Allied Vision HAL, thread-safe, VmbPy compliant)
- [x] Laser controller (Arroyo 6300 HAL, thread-safe)
- [x] TEC controller (Arroyo 5305 HAL, thread-safe)
- [x] Actuator controller (Xeryon HAL, thread-safe)
- [x] Actuator sequence builder (data model)
- [x] GPIO controller (Arduino Uno HAL, thread-safe)

### Data Persistence
- [x] SQLAlchemy ORM models (Subject, Session, SafetyLog, TechUser)
- [x] Database manager with CRUD operations
- [x] Dual logging (SQLite + JSONL)
- [ ] Database encryption (NOT IMPLEMENTED - planned Phase 6)

### Configuration Management
- [x] Pydantic configuration models
- [x] YAML configuration loader
- [x] Configuration display widget

### Safety Features
- [x] Multi-layer safety architecture
- [x] Hardware interlocks (smoothing motor + vibration + photodiode + watchdog)
- [x] Software interlocks (E-stop, power limits, session validation, state machine)
- [x] Selective shutdown policy (laser only, preserve diagnostics)
- [x] Safety state machine (SAFE, ARMED, TREATING, UNSAFE, EMERGENCY_STOP) - 5 states
- [x] Emergency stop functionality
- [x] Hardware watchdog timer (1000ms timeout, 500ms heartbeat)
- [x] Vibration detection (0.8g threshold, 5.7x safety margin)
- [x] Photodiode power monitoring (continuous)
- [ ] Footpedal integration (hardware pin assigned, software not implemented)

### Thread Safety
- [x] RLock pattern in all hardware controllers
- [x] PyQt6 signal/slot architecture for cross-thread communication
- [x] QPixmap optimization (copy-on-write, 9 MB/s bandwidth saved)
- [x] Thread-safe signal emission
- [x] No direct widget access across threads

### Testing Infrastructure
- [x] Mock hardware base pattern
- [x] Hardware controller mocks (camera, laser, actuator, GPIO)
- [x] Thread safety tests (7 tests)
- [x] Realtime safety monitoring tests (6 tests)
- [x] Hardware abstraction tests
- [x] Actuator HAL tests
- [x] GPIO calibration tests
- [x] Integration tests
- [ ] Safety state machine unit tests (NOT IMPLEMENTED - planned)
- [ ] Protocol engine safety tests (NOT IMPLEMENTED - planned)
- [ ] 72-hour soak test (NOT IMPLEMENTED - planned)

### Image Processing
- [ ] Ring detection algorithm (stub exists, NOT IMPLEMENTED)
- [ ] Focus measurement (stub exists, NOT IMPLEMENTED)
- [x] Video recording (implemented in camera_controller)

### Security
- [ ] Database encryption (NOT IMPLEMENTED - planned Phase 6)
- [ ] User authentication (NOT IMPLEMENTED - planned Phase 6)
- [ ] Video encryption (NOT IMPLEMENTED - planned Phase 6)
- [ ] Audit trail integrity (HMAC signatures NOT IMPLEMENTED - planned Phase 6)
- [ ] Protocol file signatures (NOT IMPLEMENTED - planned Phase 6)

---

## Functional Capabilities

### Session Management
- Subject record management (create, search, select)
- Treatment session tracking (start, stop)
- Session history review
- Operator identification logging

### Laser Control
- Power setting: 0.0 to 10.0W in 0.1W increments
- Laser enable/disable control
- Real-time power monitoring (500ms intervals)
- Power limit enforcement (configurable maximum)
- Treatment laser and TEC controller operate independently

### Positioning Control
- Position range: 0.0 to 20.0mm
- Position monitoring: 100ms update interval
- Homing sequence at session start
- Multi-position automated sequences
- Position bounds enforcement

### Camera and Visualization
- Live video display at 30 FPS
- Manual exposure control: 50μs to 100ms
- Manual gain control: 0dB to 24dB
- Still image capture (PNG format, timestamped)
- Video recording (MP4 format, 30 FPS, H.264 codec)
- Frame rate monitoring and display

### Protocol Execution
- Action-based protocol model
- Action types: laser_power, move_actuator, wait, log_event
- Laser power ramping during movements
- Protocol save/load from JSON files
- Visual protocol library browser
- Automated multi-action sequences

### Safety Monitoring
- GPIO interlock status (motor + vibration + photodiode)
- Hardware watchdog heartbeat (500ms intervals)
- Emergency stop availability
- Safety state display (SAFE/ARMED/TREATING/UNSAFE/EMERGENCY_STOP)
- Safety event logging (all events timestamped)

### Data Logging
Dual logging system:
1. SQLite Database: Sessions, subjects, events (queryable)
2. JSONL Files: Append-only event logs (data/logs/events_YYYYMMDD.jsonl)

Event types logged:
- Hardware connections/disconnections
- Safety interlock state changes
- Laser power changes
- Emergency stop activations
- Session start/stop
- Protocol execution events
- Software errors and exceptions

---

## Performance Characteristics

Camera:
- GUI FPS: 30 FPS sustained
- Display latency: <100ms typical
- Image capture time: <2 seconds

Laser:
- Power setting response: <100ms
- Monitoring interval: 500ms

Actuator:
- Position update rate: 100ms
- Homing sequence: ~30 seconds typical

Safety:
- GPIO polling rate: 100ms
- Watchdog heartbeat: 500ms (2x safety margin)
- E-Stop response: <50ms measured
- Vibration detection: 100% accuracy at 0.8g threshold

---

## Data Storage

### Database Schema (SQLite)

Location: data/tosca.db

Tables:
- subjects: Subject demographic records
- sessions: Treatment session records
- events: System event log
- technicians: Operator records (no authentication)

### File Storage

Directory: data/

Structure:
```
data/
├── tosca.db (SQLite database, unencrypted)
├── logs/
│   └── events_YYYYMMDD.jsonl (daily event logs)
├── images/
│   └── capture_YYYYMMDD_HHMMSS.png (captured images)
├── videos/
│   └── recording_YYYYMMDD_HHMMSS.mp4 (recorded videos)
└── protocols/
    └── [protocol_name].json (protocol definitions)
```

---

## Configuration

Configuration file: config.yaml

Camera Settings:
- gui_fps_target: 30.0
- hardware_fps: 30.0
- fps_update_interval: 30 frames

Actuator Settings:
- com_port: COM3
- baudrate: 9600
- position_timer_ms: 100

Laser Settings:
- com_port: COM10
- baudrate: 38400
- timeout_s: 1.0
- monitor_timer_ms: 500

TEC Settings:
- com_port: COM9
- baudrate: 38400

GPIO Settings:
- com_port: COM4
- baudrate: 115200
- motor_pwm_max: 153 (3.0V - DO NOT EXCEED)
- motor_default_speed: 100 (2.0V)
- vibration_threshold: 0.8g (calibrated)
- watchdog_timeout_ms: 1000

Safety Settings:
- watchdog_enabled: true
- watchdog_heartbeat_ms: 500
- emergency_stop_enabled: true
- laser_enable_requires_interlocks: true

GUI Settings:
- enable_developer_mode: false

---

## Known Limitations

### Security (CRITICAL)
- NO database encryption (all data stored in plaintext)
- NO user authentication (any technician ID accepted)
- NO access controls (all users have full permissions)
- NO audit trail protection (database can be modified externally)
- NOT suitable for protected health information (PHI)
- NOT suitable for clinical use

### Hardware
- Footpedal not yet integrated (Arduino pin assigned, software ready)
- Camera frame rate drops during video recording (30→17→8→5→2 FPS due to H.264 encoding)
- UI thread blocks for 2 seconds during GPIO connection
- Only supports Allied Vision cameras (VmbPy SDK dependency)
- Fixed to specific Arroyo laser/TEC models

### Software
- No protocol pause/resume functionality
- No built-in data export tools
- No automated backups
- No network or cloud features
- Image processing algorithms incomplete (ring detection, focus measurement)

### Development Status
- Alpha version (active development, breaking changes possible)
- Not FDA-cleared (no regulatory submissions planned until Phase 6+)
- Test coverage incomplete (some modules <80% coverage)

---

## Installation

Prerequisites:
- Python 3.10 or higher
- Windows 10/11 (64-bit)
- Virtual environment (recommended)
- Arduino IDE (for firmware upload)
- All hardware devices connected

Installation Steps:

1. Clone repository:
```bash
git clone https://github.com/will-aleyegn/TOSCA_DEV.git
cd TOSCA_DEV
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Upload Arduino firmware:
- Open firmware/arduino_watchdog/arduino_watchdog.ino in Arduino IDE
- Select Board: Arduino Uno
- Select appropriate COM port
- Upload firmware

5. Configure hardware connections:
- Edit config.yaml with correct COM ports
- Verify baud rates match hardware settings
- Check GPIO pin assignments match wiring

6. Run application:
```bash
python src/main.py
```

---

## Testing

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/test_thread_safety.py
pytest tests/test_realtime_safety_monitoring.py
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

---

## Development Standards

Code Quality:
- PEP 8 style guidelines (enforced by Black)
- Type hints required on all functions
- Comprehensive docstrings for safety-critical code
- Pre-commit hooks: Black, Flake8, MyPy, isort

Safety Requirements:
- All safety-critical code must have unit tests
- Safety interlocks cannot be bypassed in production
- All safety events must be logged immutably
- Regular code reviews required for safety-related modules

Thread Safety Pattern:
- All hardware controllers use threading.RLock()
- All cross-thread communication uses PyQt6 signals
- No direct widget access from hardware threads
