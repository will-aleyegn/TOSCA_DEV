# TOSCA Project Context for AI Assistants

**Last Updated:** 2025-10-31
**Project:** TOSCA Laser Control System
**Version:** 0.9.11-alpha
**Mode:** RESEARCH MODE - NOT for Clinical Use
**Purpose:** Essential context for AI assistants working on this medical device software project

---

## RESEARCH MODE WARNING

**CRITICAL:** This system is currently configured for RESEARCH USE ONLY.

The system includes:
- Research mode warning dialog on startup (requires explicit acknowledgment)
- Title bar watermark: "TOSCA v0.9.11-alpha - RESEARCH MODE ONLY"
- Status bar watermark: Red label "RESEARCH MODE - NOT FOR CLINICAL USE"

**Why Research Mode:**
- Database encryption NOT implemented (all data in plaintext)
- User authentication NOT implemented (no access controls)
- NOT FDA-cleared or approved for clinical use
- NOT suitable for protected health information (PHI)
- NOT suitable for patient treatment

This system is intended for:
- Research and development
- Hardware testing and calibration
- Algorithm development
- Educational purposes

---

## Project Overview

TOSCA is a **medical device laser control system** combining:
- Precision laser power control (0-10W diode laser)
- Linear actuator positioning (0-20mm range)
- Machine vision integration (Allied Vision 1800 U-158c camera)
- Multi-layer safety architecture with hardware interlocks
- Comprehensive session and event logging
- Configurable treatment protocols with automated execution

**Critical Context:** This is **medical device software under development**. While designed for eventual clinical use, it is currently in research mode. Safety, traceability, and compliance are paramount.

---

## Technology Stack

### Core Technologies
- **Python 3.12+** - Primary language (actual: 3.12.10)
- **PyQt6 6.9.0** - GUI framework (NOT PyQt5!)
- **SQLite 3.x** - Embedded database (unencrypted in current phase)
- **OpenCV** - Image processing
- **NumPy** - Numerical operations

### Hardware Communication
- **pyserial** - Arroyo laser/TEC and Arduino GPIO communication
- **Xeryon API** - Linear actuator control
- **VmbPy** - Allied Vision camera SDK (Python wrapper for Vimba X)

### Supporting Libraries
- **pyqtgraph** - Real-time plotting
- **SQLAlchemy** - Database ORM
- **Pydantic** - Configuration validation

---

## Critical Safety Architecture

### Hardware Interlocks (Primary Safety Layer)
1. **Footpedal Deadman Switch** - Active-high requirement (Arduino digital input)
2. **Smoothing Device Health** - Dual-signal validation (motor D2 + vibration D3)
3. **Photodiode Power Verification** - Continuous output monitoring (Arduino A0)
4. **Hardware Watchdog Timer** - 1000ms timeout, 500ms heartbeat (Arduino firmware)

### Software Interlocks (Secondary Layer)
1. **Emergency Stop (E-Stop)** - Global button, highest priority, locks system
2. **Power Limit Enforcement** - Configurable maximum laser power
3. **Session Validation** - Active session required for laser operation
4. **State Machine Control** - 5-state safety model (SAFE, ARMED, TREATING, UNSAFE, EMERGENCY_STOP)
   - Normal transitions: SAFE → ARMED → TREATING → ARMED → SAFE
   - Safety violations: ANY → UNSAFE
   - Emergency stop: ANY → EMERGENCY_STOP

### Selective Shutdown Policy
**CRITICAL:** When safety fault occurs:
- [DONE] **DISABLE:** Treatment laser only (immediate power-off)
- [DONE] **PRESERVE:** Camera, actuator, monitoring, aiming laser
- [DONE] **RATIONALE:** Allow diagnosis while maintaining safety

Reference: `docs/architecture/SAFETY_SHUTDOWN_POLICY.md`

---

## Hardware Configuration

### Device List
1. **Laser Driver:** Arroyo 6300 Controller (COM10, 38400 baud)
2. **TEC Controller:** Arroyo 5305 Controller (COM9, 38400 baud)
3. **Linear Actuator:** Xeryon linear stage (COM3, 9600 baud)
4. **Camera:** Allied Vision 1800 U-158c (USB 3.0, VmbPy SDK)
5. **GPIO Controller:** Arduino Uno (ATmega328P) with custom watchdog firmware (COM4, 115200 baud)
6. **Footpedal:** Normally-open momentary switch (active-high)
7. **Smoothing Motor:** DC coreless motor 7x25mm (D2) with MPU6050 accelerometer (I2C 0x68, D3)
8. **Photodiode:** Analog voltage monitoring (A0, 0-5V, 10-bit ADC)
9. **Aiming Laser:** 650nm red laser diode (D4)

### COM Port Summary
- COM3: Xeryon actuator (9600 baud)
- COM4: Arduino GPIO (115200 baud)
- COM9: Arroyo TEC controller (38400 baud)
- COM10: Arroyo laser driver (38400 baud)

---

## Project Structure

```
src/
├── ui/
│   ├── main_window.py              [DONE] 3-tab interface with toolbar (Setup, Treatment, Safety)
│   └── widgets/
│       ├── subject_widget.py       [DONE] Subject selection, session creation
│       ├── camera_widget.py        [DONE] Live streaming, controls
│       ├── camera_hardware_panel.py [DONE] Hardware diagnostics panel
│       ├── treatment_setup_widget.py [DONE] Protocol selector
│       ├── active_treatment_widget.py [DONE] Treatment monitoring dashboard
│       ├── laser_widget.py         [DONE] Laser power controls (treatment laser only)
│       ├── tec_widget.py           [DONE] TEC temperature controls
│       ├── actuator_connection_widget.py [DONE] Actuator connection and positioning
│       ├── safety_widget.py        [DONE] Safety status, event logging
│       ├── gpio_widget.py          [DONE] GPIO safety interlock display
│       ├── interlocks_widget.py    [DONE] Consolidated safety interlock status
│       ├── smoothing_status_widget.py [DONE] Smoothing motor control and monitoring
│       ├── protocol_selector_widget.py [DONE] Visual protocol library browser
│       ├── protocol_builder_widget.py [DONE] Action-based protocol builder
│       ├── line_protocol_builder.py [DONE] Line-based protocol builder (concurrent actions)
│       ├── config_display_widget.py [DONE] Configuration display
│       └── view_sessions_dialog.py  [DONE] Session history viewer
│
├── core/
│   ├── protocol.py                 [DONE] Action-based data model
│   ├── protocol_line.py            [DONE] Line-based protocol data model (concurrent actions)
│   ├── protocol_engine.py          [DONE] Async execution engine
│   ├── safety.py                   [DONE] Central safety manager with state machine
│   ├── safety_watchdog.py          [DONE] Hardware watchdog heartbeat
│   ├── session.py                  [DONE] Session data model
│   ├── session_manager.py          [DONE] Session lifecycle management
│   └── event_logger.py             [DONE] Immutable event logging
│
├── hardware/
│   ├── hardware_controller_base.py [DONE] ABC with QObject integration
│   ├── camera_controller.py        [DONE] Allied Vision HAL (thread-safe, VmbPy API compliant)
│   ├── laser_controller.py         [DONE] Arroyo 6300 laser HAL (COM10, thread-safe)
│   ├── tec_controller.py           [DONE] Arroyo 5305 TEC HAL (COM9, thread-safe)
│   ├── actuator_controller.py      [DONE] Xeryon actuator HAL (thread-safe)
│   ├── actuator_sequence.py        [DONE] Sequence builder data model
│   └── gpio_controller.py          [DONE] Arduino Uno GPIO HAL (thread-safe)
│
├── database/
│   ├── models.py                   [DONE] SQLAlchemy ORM models
│   └── db_manager.py               [DONE] Database manager with CRUD
│
├── config/
│   ├── models.py                   [DONE] Pydantic configuration models
│   └── config_loader.py            [DONE] YAML configuration loader
│
├── image_processing/
│   ├── ring_detector.py            [FUTURE] Hough circle detection
│   ├── focus_measure.py            [FUTURE] Laplacian variance
│   └── video_recorder.py           [DONE] OpenCV recording (implemented in camera_controller)
│
└── ui/dialogs/
    ├── hardware_test_dialog.py     [DONE] Hardware testing interface
    └── (other dialogs as needed)
```

---

## Current Development Phase

**Phase:** v0.9.11-alpha - Architecture Analysis & Production Readiness Assessment
**Status:** Active Development
**Focus:** Code quality validation, architecture assessment, security hardening roadmap

### Recent Milestones (October 2025)
1. [DONE] **Comprehensive Architecture Analysis** (Oct 30)
   - **Overall Grade: A (Excellent)** - Production-ready architecture
   - 10 core files analyzed in depth (safety, hardware, protocol, UI layers)
   - Safety-critical design validated (selective shutdown, state machine)
   - Thread safety patterns verified (RLock, signal/slot architecture)
   - Performance optimizations confirmed (QPixmap architecture, 30 FPS sustained)
   - Medical device compliance assessment (FDA/HIPAA considerations)
   - Security hardening roadmap defined for production deployment
   - **Key Finding:** No significant overengineering, appropriate complexity for medical device
   - **Recommendation:** Database encryption + authentication before clinical use

2. [DONE] **Camera Thread Safety** (Oct 30)
   - Thread-safe exposure/gain controls with RLock
   - Hardware feedback loop (emit actual camera values)
   - Signal-based UI updates to prevent infinite loops

3. [DONE] **Allied Vision API Compliance** (Oct 30)
   - Explicit pixel format configuration (Bgr8 > Rgb8 > Mono8 priority)
   - Fixed enum naming (Rgb8/Bgr8 not RGB8)
   - Context manager cleanup on connection failures
   - 30 FPS hardware frame rate control working

3. [DONE] **TEC/Laser Integration** (Oct 29)
   - Separated TEC and laser driver controllers
   - Dual-device architecture (COM9 + COM10)
   - Protocol builder with laser power ramping

4. [DONE] **UI/UX Redesign** (Oct 27-28)
   - Global toolbar with E-Stop button
   - Treatment Dashboard with consolidated status
   - Protocol selector with visual library browser
   - Manual override widget (dev mode only)

---

## Code Quality Standards

### Medical Device Requirements
- **All safety-critical code must have unit tests**
- **Safety interlocks cannot be bypassed in production**
- **All safety events must be logged immutably**
- **Regular code reviews for safety-related modules**

### Style Guidelines
- Follow **PEP 8** style guidelines
- **Type hints required** on all functions
- **Comprehensive docstrings** for safety-critical code
- Pre-commit hooks enforce: Black, Flake8, MyPy, isort

### Thread Safety Pattern
```python
class HardwareController(QObject):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def set_value(self, value):
        with self._lock:
            # Thread-safe hardware operation
            self.hardware.set(value)
            self.value_changed.emit(value)  # PyQt6 signal
```

### Git Commit Pattern
```bash
# Use --no-verify when MyPy has known false positives
git commit --no-verify -m "commit message"

# This is documented and acceptable for TOSCA project
```

---

## Key Lessons Learned

### 1. QImage Memory Lifetime Bug (CRITICAL)
**Problem:** QImage constructor creates shallow copy of numpy array data. When frame goes out of scope, QImage becomes invalid.

**Solution:** Always copy frame data before QImage construction:
```python
# BROKEN
q_image = QImage(frame.data, width, height, bytes_per_line, format)

# FIXED
frame_copy = frame.copy()  # Deep copy ensures data persists
q_image = QImage(frame_copy.data, width, height, bytes_per_line, format)
```

Reference: `LESSONS_LEARNED.md #1`

### 2. Widget Reparenting Anti-Pattern (CRITICAL)
**Problem:** Directly reparenting widgets between components breaks Qt object hierarchy.

**Solution:** Use signal/slot architecture for widget communication:
```python
# BROKEN - Widget reparenting
self.camera_display = other_widget.camera_display  # Steal QLabel!

# FIXED - Signal/slot architecture
other_widget.pixmap_ready.connect(self._on_camera_frame_ready)
def _on_camera_frame_ready(self, pixmap):
    self.camera_display.setPixmap(pixmap)  # Update OWN label
```

Reference: `LESSONS_LEARNED.md #12`

### 3. Hardware Binning vs Software Downsampling
**Current:** Software downsampling (cv2.resize) for camera display
**Reason:** Hardware binning caused corrupted frames (configuration issues)
**Future:** Investigate Allied Vision binning API for potential 4-15× FPS improvement

Reference: `LESSONS_LEARNED.md #13`

### 4. Requirements Clarification
**Always clarify requirements before implementation:**
- Use questioning techniques: "Just to clarify, do you want X or Y?"
- Create simple mockups/diagrams for user validation
- Document requirements decisions in ADRs

Reference: `LESSONS_LEARNED.md #4`

---

## Testing Infrastructure

### Mock Pattern (MockHardwareBase)
```python
from tests.mocks.mock_hardware_base import MockHardwareBase

class MockCameraController(MockHardwareBase):
    def __init__(self):
        super().__init__(
            connection_signal=self.connection_changed,
            error_signal=self.error_occurred
        )
        self.is_streaming = False
```

**Benefits:**
- Consistent mock behavior across all hardware types
- Built-in connection state management
- Automatic signal emission validation
- Failure mode simulation

Reference: `tests/mocks/README.md`

### Test Categories
1. **Unit Tests:** Hardware abstraction, protocol engine, database operations
2. **Integration Tests:** Hardware communication, safety coordination, UI integration
3. **Safety Tests:** Footpedal response, photodiode accuracy, E-stop effectiveness
4. **Thread Safety Tests:** Concurrent hardware access validation

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

---

## Common Development Tasks

### Adding a New Hardware Controller

1. **Inherit from HardwareControllerBase:**
   ```python
   from src.hardware.hardware_controller_base import HardwareControllerBase

   class MyController(HardwareControllerBase):
       def __init__(self):
           super().__init__()
           self._lock = threading.RLock()
   ```

2. **Define PyQt6 Signals:**
   ```python
   value_changed = pyqtSignal(float)
   ```

3. **Implement Thread-Safe Methods:**
   ```python
   def set_value(self, value: float) -> bool:
       with self._lock:
           self.hardware.set(value)
           self.value_changed.emit(value)
           return True
   ```

4. **Create Mock:**
   ```python
   class MockMyController(MockHardwareBase):
       # Implement mock behavior
   ```

5. **Add Unit Tests:**
   ```python
   def test_my_controller_thread_safety():
       # Test concurrent access
   ```

### Adding a New UI Widget

1. **Create Widget File:**
   ```python
   from PyQt6.QtWidgets import QWidget

   class MyWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self._setup_ui()
           self._connect_signals()
   ```

2. **Connect to Hardware Signals:**
   ```python
   self.hardware.value_changed.connect(self._on_value_changed)
   ```

3. **Block Signals During Hardware Updates:**
   ```python
   def _on_value_changed(self, value):
       self.slider.blockSignals(True)
       self.slider.setValue(int(value))
       self.slider.blockSignals(False)
   ```

4. **Add to Main Window:**
   ```python
   self.my_widget = MyWidget()
   layout.addWidget(self.my_widget)
   ```

### Adding a Protocol Action

1. **Define ActionParameters:**
   ```python
   @dataclass
   class MyActionParams(ActionParameters):
       value: float
       duration_sec: float
   ```

2. **Add to ActionType Enum:**
   ```python
   class ActionType(str, Enum):
       MY_ACTION = "my_action"
   ```

3. **Implement in ProtocolEngine:**
   ```python
   async def _execute_my_action(self, params: MyActionParams):
       await self.hardware.set_value_async(params.value)
   ```

4. **Add to Protocol Builder UI:**
   ```python
   self.action_combo.addItem("My Action", ActionType.MY_ACTION)
   ```

---

## Documentation Resources

### Architecture Documentation
- `docs/architecture/01_system_overview.md` - Complete architecture, technology stack
- `docs/architecture/02_database_schema.md` - SQLite schema, entity relationships
- `docs/architecture/03_safety_system.md` - Safety philosophy, interlock architecture
- `docs/architecture/04_treatment_protocols.md` - Protocol data model, execution engine
- `docs/architecture/06_protocol_builder.md` - Protocol builder UI and workflow
- `docs/architecture/07_safety_watchdog.md` - Hardware watchdog implementation
- `docs/architecture/09_test_architecture.md` - Testing infrastructure and patterns
- `docs/architecture/10_concurrency_model.md` - Thread safety and async patterns
- `docs/architecture/SAFETY_SHUTDOWN_POLICY.md` - Selective shutdown rationale

### Project Management
- `presubmit/PROJECT_STATUS.md` - Current milestones, component status, technical debt
- `presubmit/WORK_LOG.md` - Detailed development history and decisions
- `LESSONS_LEARNED.md` - Critical bugs, solutions, prevention strategies
- `README.md` - Installation, setup, testing instructions

### Hardware Documentation
- `docs/hardware/HARDWARE_CONFIG_SUMMARY.md` - Device specifications and wiring
- `docs/hardware/HARDWARE_TEST_RESULTS.md` - Hardware validation results
- `components/camera_module/` - Allied Vision camera API examples
- `components/actuator_module/` - Xeryon actuator API examples
- `components/laser_control/` - Arroyo laser/TEC API documentation
- `components/gpio_safety/` - Arduino GPIO examples and firmware

### Testing Documentation
- `tests/mocks/README.md` - Mock infrastructure usage guide
- `docs/architecture/09_test_architecture.md` - Testing strategy and patterns

---

## Key Design Patterns

### 1. Hardware Abstraction Layer (HAL)
All hardware controllers inherit from `HardwareControllerBase` and provide:
- Thread-safe operations (RLock pattern)
- PyQt6 signal emission for state changes
- Consistent connect/disconnect interface
- Error handling and logging

### 2. Signal/Slot Architecture
All cross-thread and widget communication uses PyQt6 signals:
- Thread-safe by design
- Prevents tight coupling
- Enables reactive UI updates
- No direct widget access from other components

### 3. State Machine (Safety Manager)
Safety state transitions are strictly controlled:
```
SAFE → ARMED → TREATING
  ↓      ↓         ↓
  ← UNSAFE/FAULT ←
        ↓
  EMERGENCY_STOP (locked)
```

### 4. Selective Shutdown
When safety fault occurs, only treatment laser is disabled:
- Camera: [DONE] Keep running (visual feedback)
- Actuator: [DONE] Keep running (controlled retraction)
- Monitoring: [DONE] Keep running (diagnosis)
- Laser: [FAILED] Disable immediately (safety)

### 5. Two-Tier Logging
Events are logged to both:
1. **JSONL files** (data/logs/) - Append-only, immutable
2. **SQLite database** (data/tosca.db) - Queryable, relational

---

## Important Notes for AI Assistants

### DO:
- [DONE] Always use type hints on functions
- [DONE] Add docstrings to safety-critical code
- [DONE] Use threading.RLock for hardware controllers
- [DONE] Emit PyQt6 signals on state changes
- [DONE] Copy numpy arrays before QImage construction
- [DONE] Use signal/slot for widget communication
- [DONE] Block signals during hardware-triggered UI updates
- [DONE] Log safety events immutably
- [DONE] Clarify requirements before implementation
- [DONE] Test thread safety for hardware operations

### DON'T:
- [FAILED] Never reparent widgets between components
- [FAILED] Never bypass safety interlocks in production
- [FAILED] Never use QThread.run() override (use QRunnable instead)
- [FAILED] Never mix asyncio and QThread directly
- [FAILED] Never skip type hints on public functions
- [FAILED] Never hardcode COM ports (use config or UI selection)
- [FAILED] Never use blocking operations in GUI thread
- [FAILED] Never modify safety events after creation (immutability)
- [FAILED] Never commit without running pre-commit hooks (unless --no-verify is justified)

### Medical Device Context:
- This is **FDA-regulated medical device software**
- Safety is paramount - never compromise on safety features
- All safety-critical code requires unit tests
- Maintain comprehensive audit trail (event logging)
- Document architectural decisions affecting safety
- Follow medical device software validation practices (IEC 62304)

---

## Quick Reference: Key Files

### Most Important Files
1. `src/core/safety.py` - Central safety manager
2. `src/hardware/camera_controller.py` - Allied Vision camera HAL
3. `src/hardware/laser_controller.py` - Arroyo laser driver HAL
4. `src/hardware/gpio_controller.py` - Arduino GPIO and safety interlocks
5. `src/core/protocol_engine.py` - Treatment protocol execution
6. `src/ui/main_window.py` - Main application window
7. `LESSONS_LEARNED.md` - Critical bugs and solutions
8. `docs/architecture/SAFETY_SHUTDOWN_POLICY.md` - Safety rationale

### Configuration Files
- `config.yaml` - Hardware configuration (COM ports, baud rates)
- `pyproject.toml` - Python project configuration, dependencies
- `requirements.txt` - Python dependencies

### Firmware
- `firmware/arduino_watchdog/arduino_watchdog.ino` - Arduino watchdog firmware

---

## Version History

**v0.9.11-alpha (2025-10-30):** Comprehensive architecture analysis - Grade A (Excellent)
**v0.9.10-alpha (2025-10-30):** QPixmap optimization + image capture + video recording
**v0.9.9-alpha (2025-10-30):** Status bar bug fixes + dependency injection pattern
**v0.9.8-alpha (2025-10-30):** Production-ready camera + Allied Vision API compliance
**v0.9.7-alpha (2025-10-29):** TEC/Laser integration + protocol builder enhancements
**v0.9.6-alpha (2025-10-28):** Hardware tab enhancements + code cleanup
**v0.9.5-alpha (2025-10-28):** Development workflow optimization
**v0.9.4-alpha (2025-10-27):** UI/UX redesign Phase 3 complete
**v0.9.3-alpha (2025-10-27):** UI/UX redesign Phase 2 complete
**v0.9.2-alpha (2025-10-27):** UI/UX redesign Phase 1 complete

---

## Contact & Resources

**Project Repository:** https://github.com/will-aleyegn/TOSCA_DEV
**Documentation:** `docs/architecture/`
**Issue Tracker:** GitHub Issues
**Development Team:** [User/Team Name]

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Next Review:** Upon Phase 6 (Pre-Clinical Validation) start
