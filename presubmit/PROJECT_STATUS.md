# TOSCA Project Status & AI Onboarding

**Last Updated:** 2025-10-24 07:15
**Current Phase:** Phase 3 IN PROGRESS - Core Business Logic
**Project Status:** Initial Setup ✓ → Camera HAL ✓ → Actuator HAL ✓ → Laser HAL ✓ → GPIO HAL ✓ → Safety (95%) → Session Mgmt (60%)

---

## Quick Start for New AI Session

1. **Read this file first** - Current project state
2. **Review** `CODING_STANDARDS.md` - Development rules
3. **Check** `docs/DEVELOPMENT_ENVIRONMENT_SETUP.md` - Setup reference
4. **Verify** Git status and latest commits
5. **Continue** from "Next Immediate Tasks" section below

---

## Project Overview

**Name:** TOSCA Medical Laser Control System
**Type:** FDA-Enhanced Documentation Level Medical Device Software
**Compliance:** IEC 62304, Enhanced Documentation Level
**Repository:** https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development

**Purpose:** Clinical laser control system with:
- Laser power control (Arroyo TEC Controller)
- Linear actuator (Xeryon) for ring sizing
- Camera system (Allied Vision) for alignment
- GPIO safety interlocks (FT232H)
- Patient management database
- Treatment protocol engine
- Session video recording

---

## Critical Development Rules

**MUST READ:** `CODING_STANDARDS.md`

**Key Principles:**
1. **Minimal code only** - Write only what is explicitly requested
2. **No decorative elements** - No emojis, no extra comments, no flourishes
3. **No placeholder functions** - Only implement what's needed now
4. **Type hints required** - All functions must have type annotations
5. **Safety-critical documentation** - Hardware operations need detailed docstrings
6. **Pre-commit hooks active** - Code must pass Black, Flake8, MyPy, isort

**When installing packages:**
- Always add to `requirements.txt`
- Document in appropriate category

**When creating output files:**
- Use designated output directories
- Never litter repository root
- Add to `.gitignore` if test data

---

## Current Directory Structure

```
TOSCA-dev/
├── .github/                           # GitHub config
├── components/                         # Hardware API exploration & docs
│   ├── camera_module/                 # ✓ Camera API (VmbPy)
│   ├── actuator_module/               # ✓ Actuator API (Xeryon)
│   ├── laser_control/                 # ✓ Laser API (Arroyo)
│   └── gpio_safety/                   # ✓ GPIO API (FT232H + MCP3008)
├── docs/
│   ├── architecture/                  # Complete architecture docs
│   └── project/                       # Project management docs
│       ├── PROJECT_STATUS.md         # Canonical status (Phase 2 complete)
│       ├── CODING_STANDARDS.md       # Development rules
│       └── WORK_LOG.md               # Session tracking (gitignored)
├── src/                               # ✓ PHASE 2 COMPLETE
│   ├── main.py                        # ✓ PyQt6 launcher
│   ├── ui/                            # ✓ GUI with 4 tabs
│   │   ├── main_window.py            # 4-tab layout
│   │   └── widgets/
│   │       ├── subject_widget.py     # ✓ Patient selection
│   │       ├── camera_widget.py      # ✓ Camera streaming/controls
│   │       ├── treatment_widget.py   # ✓ Laser/actuator controls
│   │       ├── actuator_widget.py    # ✓ Sequence builder
│   │       ├── laser_widget.py       # ✓ Laser power/TEC controls
│   │       ├── gpio_widget.py        # ✓ Safety interlocks
│   │       └── safety_widget.py      # ✓ Safety monitoring
│   ├── hardware/                      # ✓ ALL 4 HALs COMPLETE
│   │   ├── camera_controller.py      # ✓ Allied Vision camera
│   │   ├── actuator_controller.py    # ✓ Xeryon linear stage
│   │   ├── actuator_sequence.py      # ✓ Sequence data model
│   │   ├── laser_controller.py       # ✓ Arroyo laser driver
│   │   └── gpio_controller.py        # ✓ FT232H safety interlocks
│   ├── core/                          # 🔄 PHASE 3 IN PROGRESS
│   │   ├── protocol.py               # ✓ Protocol data model
│   │   ├── protocol_engine.py        # ✓ Execution engine
│   │   ├── safety.py                 # ✓ Safety system (95% complete)
│   │   ├── session_manager.py        # ✓ Session lifecycle manager (60% - backend done)
│   │   └── event_logger.py           # TODO: Event logging
│   ├── database/                      # ✓ Database models and manager (complete)
│   │   ├── models.py                 # ✓ SQLAlchemy ORM models
│   │   └── db_manager.py             # ✓ Database operations
│   └── image_processing/              # TODO: Phase 3
├── tests/                             # TODO: Test suite
├── data/                              # Git-ignored
│   └── logs/                          # Application logs
├── presubmit/                         # AI onboarding docs (gitignored)
├── venv/                              # Virtual environment
├── README.md                          # Updated with Phase 2 status
└── requirements.txt
```

---

## Completed Work

### ✓ Phase 0: Initial Setup (Complete)

**Repository & Git:**
- [x] GitHub repository created and connected
- [x] `.gitignore` configured for medical device security
- [x] Pre-commit hooks installed (Black, Flake8, MyPy, isort)
- [x] Pull request template with coding standards checklist

**Python Environment:**
- [x] Virtual environment created (Python 3.12.10)
- [x] All dependencies installed (100+ packages)
- [x] Project structure created (`src/`, `tests/`, `data/`)
- [x] Package configuration (`setup.py`, `pyproject.toml`, `pytest.ini`)

**Configuration Files:**
- [x] `.flake8` - Linting rules
- [x] `.pylintrc` - Code analysis rules
- [x] `.pre-commit-config.yaml` - Automated checks
- [x] `.env.example` - Environment variable template

**Documentation:**
- [x] `CODING_STANDARDS.md` - Development rules
- [x] `DEVELOPMENT_ENVIRONMENT_SETUP.md` - Complete setup guide
- [x] Architecture docs in `docs/architecture/`

### ✓ Phase 2: Hardware Abstraction Layer (COMPLETE) 🎉

**All 4 Hardware Controllers Implemented with PyQt6 Integration**

#### 1. Camera HAL (Complete)
- [x] VmbPy API integration with Allied Vision 1800 U-158c
- [x] Thread-safe streaming with CameraStreamThread
- [x] Live video display with Qt signals
- [x] Exposure, gain, white balance controls
- [x] Still image capture and video recording
- [x] Hardware frame rate control (40 FPS)
- [x] CameraWidget with full GUI controls

#### 2. Actuator HAL (Complete)
- [x] Xeryon linear stage integration
- [x] Position control (absolute and relative)
- [x] Homing procedures (index finding)
- [x] Speed control (0.5-400 mm/s)
- [x] Sequence builder with 6 action types
- [x] Loop support (1-100 iterations)
- [x] ActuatorWidget with sequence GUI
- [x] Hardware tested and operational

#### 3. Laser HAL (Complete)
- [x] Arroyo Instruments serial communication (38400 baud)
- [x] Current control (0-2000 mA) with safety limits
- [x] TEC temperature control and monitoring
- [x] Output enable/disable with verification
- [x] Real-time status polling (500ms)
- [x] LaserWidget with power and TEC controls
- [x] Comprehensive API documentation

#### 4. GPIO HAL (Complete)
- [x] FT232H integration with Adafruit Blinka
- [x] Smoothing device motor control (digital output)
- [x] Vibration sensor monitoring (digital input, debounced)
- [x] Photodiode power monitoring (MCP3008 ADC via SPI)
- [x] Safety interlock logic (motor ON + vibration detected)
- [x] GPIOWidget with safety status display
- [x] Complete hardware documentation

**Enhanced Features:**
- [x] Sequence builder with laser power per step
- [x] Acceleration/deceleration control per step
- [x] Treatment tab 3-column layout (laser, treatment, actuator)
- [x] Safety tab 2-column layout (GPIO, software interlocks)
- [x] Integration specification complete (736 lines)

**Test Scripts - All Working:**
- [x] `01_list_cameras.py` - Camera detection ✓
- [x] `02_camera_info.py` - Camera details ✓
- [x] `03_capture_single_frame.py` - Frame capture with timestamps ✓
- [x] `04_explore_features.py` - Feature exploration (223/313 features) ✓
- [x] `05_continuous_stream.py` - Streaming (39.4 FPS) ✓
- [x] `06_set_auto_exposure.py` - Auto exposure control ✓

**Camera Test Results:**
```
Camera ID: DEV_1AB22C04E780
Model: Allied Vision 1800 U-158c
Resolution: 1456 x 1088 pixels
Format: RGB8 (3 channels)
Exposure: 5ms (manual) or auto-adjust
Frame Rate: 39.4 FPS sustained
Features: 223 of 313 readable
Interface: USB
Status: Fully validated ✓
```

### ✓ GUI Shell - Phase 1 (Complete)

**PyQt6 Main Window:**
- [x] 4-tab layout created (Subject, Camera, Treatment, Protocol Builder, Safety)
- [x] Status bar with hardware connection indicators
- [x] Main window with proper title and sizing (1400x900)
- [x] Logging integration for all UI actions
- [x] Dev mode toggle in status bar

**Widget Components:**
- [x] SubjectWidget - Subject ID search, session initiation
- [x] CameraWidget - Live camera feed (800x600), full controls
- [x] TreatmentWidget - Laser power (0-2000mW), ring size (0-3000um)
- [x] ProtocolBuilderWidget - Protocol creation and action sequences
- [x] SafetyWidget - Hardware/software interlocks, E-stop button

**Technical Quality:**
- [x] All methods type annotated (mypy compliant)
- [x] Pre-commit hooks passing (black, flake8, isort, mypy)
- [x] Follows CODING_STANDARDS.md minimal approach
- [x] GUI launches and renders correctly

**Status:** GUI shell complete ✓

### ✓ Camera HAL Integration (Complete)

**Hardware Abstraction Layer:**
- [x] src/hardware/camera_controller.py (449 lines)
  - CameraStreamThread for background streaming
  - VideoRecorder for MP4 video capture
  - CameraController with PyQt6 signals
  - VmbPy API integration
- [x] Enhanced camera widget (498 lines)
  - Live camera feed with real-time updates
  - Exposure control (slider, input box, auto checkbox)
  - Gain control (slider, input box, auto checkbox)
  - Auto white balance checkbox
  - Still image capture controls (pending implementation)
  - Video recording controls with status indicators
  - FPS display and connection status

**Features:**
- [x] Real-time streaming at ~40 FPS
- [x] Thread-safe Qt signal communication
- [x] Bidirectional control sync (slider ↔ input)
- [x] Video recording to MP4 files
- [x] Custom filename support with timestamps
- [x] PROJECT_ROOT path resolution for consistent saving
- [x] Unicode compatibility fixes (us instead of µs)

**Testing:**
- [x] Camera connection working
- [x] Live view functional
- [x] Video recording to data/videos/
- [x] All controls responsive
- [x] Pre-commit hooks passing

**Status:** Camera integration complete ✓

### ✓ Developer Mode (Complete)

**Dev Mode Features:**
- [x] Dev mode toggle checkbox in status bar
- [x] Window title changes to show "DEVELOPER MODE"
- [x] Subject selection disabled in dev mode
- [x] Custom save path selection for videos and images
- [x] Browse button dialogs for directory selection
- [x] Treatment controls enabled without session
- [x] Visual indicators (orange text, title change)
- [x] Automatic cleanup when exiting dev mode

**Implementation:**
- [x] Main window emits dev_mode_changed signal
- [x] Camera widget responds with set_dev_mode()
- [x] Treatment widget responds with set_dev_mode()
- [x] Optional output_dir parameter in camera controller
- [x] Custom paths hidden in normal mode
- [x] All type annotations passing mypy

**Benefits:**
- [x] Test features without session management
- [x] Save files to custom locations
- [x] Run protocols independently
- [x] Faster development iteration

**Status:** Dev mode operational ✓

### ✓ Actuator HAL API Compliance (Complete)

**Xeryon API Verification:**
- [x] Complete API reference documentation (642 lines)
- [x] All API calls verified against official Xeryon.py v1.88
- [x] Critical speed API bug fixed
- [x] TOSCA hardware configuration documented
- [x] API compliance comments added to all methods

**Documentation Created:**
- [x] components/actuator_module/docs/XERYON_API_REFERENCE.md
  - Complete API reference from official library
  - TOSCA hardware configuration section
  - All stage types and units enumeration
  - Position control, speed control, homing procedures
  - Status monitoring (all 22 status bits)
  - Common usage patterns and examples
  - Quick reference table

**Code Fixes:**
- [x] src/hardware/actuator_controller.py
  - Fixed set_speed() to use axis.setSpeed() API (was bypassing conversion)
  - Added API compliance docstrings to connect()
  - Added API compliance docstrings to find_index()
  - Added API compliance docstrings to set_position()
  - Added API compliance docstrings to make_step()
  - Added detailed speed conversion documentation

**TOSCA Hardware Configuration:**
```
Actuator: Xeryon XLA-5-125-10MU
Baudrate: 9600 (manufacturer pre-configured, NOT library default 115200)
Stage Type: XLA_1250_3N (1.25 µm encoder resolution)
Working Units: Units.mu (micrometers)
Speed Range: 50-500 µm/s
```

**Critical Fixes:**
1. **Speed API Bug:**
   - Was: `self.axis.sendCommand(f"SSPD={speed}")` (no unit conversion)
   - Now: `self.axis.setSpeed(speed)` (official API with µm/s conversion)
   - Impact: GUI speed slider values now correctly interpreted as µm/s

2. **Baudrate Clarification:**
   - Documented TOSCA uses 9600 baud throughout all documentation
   - Added warnings that library default (115200) will NOT work
   - Updated all code examples to show correct 9600 value

3. **API Compliance:**
   - All methods reference official API behavior
   - Unit conversion formulas documented
   - Links to XERYON_API_REFERENCE.md added
   - Hardware API Usage Rule compliance noted

**Testing:**
- [x] All changes verified against official Xeryon.py v1.88
- [x] Speed conversion formula validated
- [x] Pre-commit hooks passing (black, flake8, isort, mypy)
- ⏳ Physical hardware testing pending

**Status:** Actuator HAL API-compliant and documented ✓

---

## Known Issues

**None** - All current modules tested and working

**Previously Resolved:**
1. ✓ Camera feature exploration (VmbPy British spelling issue)
2. ✓ Streaming callback signature (3 params required)
3. ✓ Path-independent file operations (using Path(__file__))

---

## Current Work Session Summary

**Session Date:** 2025-10-23
**Total Actions:** 29 major steps completed (26 from previous + 3 new)
**Duration:** Continued from previous session

**Completed This Session:**
1. ✓ Camera HAL integration (Action 27)
   - Complete camera controller with PyQt6 integration
   - Live streaming at ~40 FPS
   - Video recording to MP4
   - Full exposure/gain controls with auto modes
   - Bidirectional slider/input sync
2. ✓ Developer mode implementation (Action 28)
   - Session-independent testing capability
   - Custom save path selection
   - Treatment controls enabled without session
   - Visual mode indicators
3. ✓ Xeryon API verification and compliance (Action 29)
   - 642-line comprehensive API reference documentation
   - Fixed critical speed API bug (axis.setSpeed() compliance)
   - Clarified TOSCA uses 9600 baud (NOT 115200)
   - Added API compliance comments to all methods
   - Verified all API calls against official Xeryon.py v1.88

**What's working:**
- Camera: Fully integrated with live view and recording
- GUI: All 5 tabs operational (Subject, Camera, Treatment, Protocol, Safety)
- Dev Mode: Session bypass working, custom paths functional
- Actuator HAL: API-compliant, documented, GUI integrated
- Code quality: All pre-commit hooks passing
- Documentation: Comprehensive API references and updated work logs

**Current State:**
- Camera module: ✓ Complete (test scripts)
- GUI shell: ✓ Complete (all widgets)
- Camera HAL: ✓ Complete (live view, recording)
- Dev mode: ✓ Complete (session bypass)
- Actuator HAL: ✓ API-Compliant (verified, documented, GUI integrated)
- Actuator Testing: ⏳ Pending physical hardware test
- Protocol builder: ✓ Data model and engine complete
- Session management: ⏳ Stubs created, not integrated
- Laser HAL: ⏳ Not started

---

## Next Immediate Tasks - PHASE 3: Core Business Logic

**🎯 Phase 3 IN PROGRESS - Priority 1 at 95%**

**Priority 1: Safety System Integration** ✅ NEARLY COMPLETE
1. ✅ Create `src/core/safety.py` - Central safety manager (DONE)
2. ✅ Integrate GPIO interlocks with laser enable (DONE)
3. ✅ Implement safety state machine (SAFE/UNSAFE/EMERGENCY_STOP) (DONE)
4. ✅ Wire up laser enable to safety status (DONE)
5. ✅ Add emergency stop functionality (DONE)
6. ✅ Implement safety event logging display (DONE)
7. ⏳ Hardware integration testing (pending GPIO hardware)

**Priority 2: Session Management System** 🔄 60% COMPLETE
1. ✅ Create `src/database/models.py` - SQLAlchemy models (DONE)
2. ✅ Create `src/database/db_manager.py` - Database manager (DONE)
3. ✅ Implement subject CRUD operations (DONE)
4. ✅ Create `src/core/session_manager.py` - Session lifecycle manager (DONE)
5. ⏳ Wire up subject_widget to database and session creation (NEXT)
6. ⏳ Add session-based file organization for recordings (pending)

**Priority 3: Event Logging System**
1. Create `src/core/event_logger.py` - Immutable audit trail
2. Implement event types (safety, treatment, hardware, user)
3. Integrate with all hardware controllers
4. Add event display in Safety tab
5. Implement session event association
6. Add event export functionality

**Priority 4: Hardware Integration Testing**
1. Test all 4 HALs with physical hardware
2. Verify safety interlocks work correctly
3. Test laser enable/disable with GPIO
4. Validate actuator sequences with laser power
5. Test camera recording during treatment
6. Document hardware test results

**Priority 5: Treatment Protocol Execution**
1. Wire up protocol engine to hardware controllers
2. Implement protocol-to-sequence conversion
3. Add real-time protocol monitoring
4. Integrate with safety system
5. Add session recording during protocol execution

---

## Hardware Status

### Hardware Abstraction Layers: ALL COMPLETE ✅

**Camera HAL:** ✅ Software Complete, Hardware Tested
- Allied Vision 1800 U-158c (USB)
- Detection: ✓ | Streaming: ✓ | Recording: ✓
- Exposure/Gain Control: ✓ | Auto-features: ✓

**Actuator HAL:** ✅ Software Complete, Hardware Tested
- Xeryon Linear Stage (Serial)
- Connection: ✓ | Homing: ✓ | Position Control: ✓
- Sequences: ✓ | Tested with physical hardware: ✓

**Laser HAL:** ✅ Software Complete, Awaiting Hardware Test
- Arroyo Instruments Laser Driver (Serial, COM4)
- Current control: ✓ | TEC control: ✓ | Safety limits: ✓
- Ready for physical hardware connection

**GPIO HAL:** ✅ Software Complete, Awaiting Hardware Test
- FT232H + MCP3008 ADC (USB + SPI)
- Motor control: ✓ | Vibration sensor: ✓ | Photodiode: ✓
- Safety interlocks: ✓ | Ready for hardware connection

### Hardware Testing Status:
- ✅ Camera: Fully tested and operational
- ✅ Actuator: Fully tested and operational
- ⏳ Laser: Software ready, awaiting device connection (COM4)
- ⏳ GPIO: Software ready, awaiting FT232H + MCP3008 setup
- ⏳ Smoothing Device: Software ready, awaiting motor/accelerometer setup
- ⏳ Photodiode: Software ready, awaiting circuit connection

---

## Key Decisions Made

1. **Modular Exploration Approach:**
   - Decided to create separate exploration modules (camera_module, actuator_module)
   - Fully understand APIs before integration
   - Test scripts demonstrate capabilities
   - Prevents polluting main application

2. **Coding Standards Enforcement:**
   - Strict "minimal code only" policy
   - No decorative elements or extra functions
   - Pre-commit hooks enforce quality automatically
   - Type hints required on all functions

3. **Output Organization:**
   - Test outputs go to module-specific output directories
   - Git-ignored to keep repository clean
   - No files in repository root

4. **Documentation First:**
   - README in each module explains API completely
   - Test scripts serve as usage examples
   - Integration plans documented before implementation

---

## Development Workflow

**Starting a Session:**
```bash
cd C:\Users\wille\Desktop\TOSCA-dev
venv\Scripts\activate
git pull origin main
```

**Before Writing Code:**
```bash
# Review coding standards
cat CODING_STANDARDS.md
```

**Testing:**
```bash
# Run specific test script
python camera_module/examples/01_list_cameras.py

# Run all tests
pytest
```

**Before Committing:**
```bash
# Pre-commit hooks run automatically on commit
git add .
git commit -m "message"  # Hooks will validate code
git push origin main
```

---

## Important File Locations

**Critical Documents:**
- `PROJECT_STATUS.md` - This file (session state)
- `CODING_STANDARDS.md` - Development rules
- `docs/DEVELOPMENT_ENVIRONMENT_SETUP.md` - Setup guide

**Architecture:**
- `docs/architecture/01_system_overview.md` - System design
- `docs/architecture/02_database_schema.md` - Database design
- `docs/architecture/03_safety_system.md` - Safety requirements
- `docs/architecture/04_treatment_protocols.md` - Protocol specs
- `docs/architecture/05_image_processing.md` - Image processing specs

**Camera Module:**
- `camera_module/README.md` - VmbPy API documentation
- `camera_module/examples/` - Test scripts
- `camera_module/output/` - Test images

**Configuration:**
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `.pre-commit-config.yaml` - Code quality hooks

---

## Questions to Ask at Session Start

1. **What are we working on?**
   - Continue camera module?
   - Start actuator module?
   - Begin hardware abstraction layer?

2. **Any issues with current code?**
   - Review git status
   - Check for uncommitted changes
   - Review latest commits

3. **New hardware connected?**
   - Update "Hardware Status" section
   - Add to this document

4. **Any decisions made?**
   - Document in "Key Decisions Made"
   - Update relevant sections

---

## Git Commit History Summary

**Latest commits:**
```
561257c - Fix speed API and add comprehensive API compliance documentation
8cf072a - Add comprehensive Xeryon API reference documentation
a4db7c8 - Fix actuator widget UI stability issues
288e82c - Complete Actuator HAL and GUI integration - Phase 2 at 50%
076ad96 - Fix circular import in treatment_widget
d3bdc05 - Add developer/tech mode for session-independent operation
7839c69 - Enhance camera controls and fix save paths
```

**Full archive:** See WORK_LOG.md and archive/ for complete history

---

## Environment Details

**Python:** 3.12.10
**Virtual Environment:** `venv/` (activated with `venv\Scripts\activate`)
**OS:** Windows 10

**Key Packages:**
- PyQt6 6.10.0 (GUI)
- OpenCV 4.12.0 (Image processing)
- NumPy 2.2.6 (Arrays)
- VmbPy 1.1.1 (Camera)
- SQLAlchemy 2.0.44 (Database)
- pytest 8.4.2 (Testing)

**Development Tools:**
- Black (formatting)
- Flake8 (linting)
- MyPy (type checking)
- Pylint (analysis)
- Pre-commit (hooks)

---

## MCP Configuration

**GitHub Token:** Configured in `.mcp.json` (git-ignored)
**MCP Servers Active:**
- github: GitHub API integration
- memory: Knowledge graph
- context7: Documentation lookup

---

## Session Handoff Template

**When ending a session, update this section:**

**Date:** YYYY-MM-DD
**What was completed:**
- Item 1
- Item 2

**What needs attention:**
- Issue 1
- Issue 2

**Next session should:**
- Task 1
- Task 2

**Notes:**
- Any important context

---

## Notes for AI Assistant

**User Preferences:**
1. **Minimal code** - Only what's requested, no extras
2. **No decorative elements** - No emojis, clean code only
3. **Ask before adding** - Don't assume features needed
4. **Document as you go** - Keep this file updated
5. **Test outputs in designated directories** - No littering

**When user requests new work:**
1. Review this file first
2. Check CODING_STANDARDS.md
3. Verify current git status
4. Continue from documented state

**Update this file when:**
- Completing major tasks
- Making architectural decisions
- Changing directory structure
- Adding new modules
- Discovering issues
- Connecting new hardware

---

**End of Project Status Document**
**Remember: Update this file as work progresses!**
