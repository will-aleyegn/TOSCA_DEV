# TOSCA Project TODO List

**Last Updated:** 2025-10-23
**Current Phase:** Phase 2 - Hardware Abstraction Layer (44% Complete)

---

## Legend

- ✅ **Completed**
- 🚧 **In Progress**
- ⏳ **Planned**
- ❌ **Blocked/On Hold**

---

## Phase 1: Foundation and Planning ✅ COMPLETE

### Project Structure & Setup ✅
- ✅ Repository initialization and structure
- ✅ Development environment setup (venv, dependencies)
- ✅ Pre-commit hooks (Black, Flake8, MyPy, isort)
- ✅ Git configuration and .gitignore
- ✅ README and project documentation

### Architecture & Design ✅
- ✅ System architecture documentation
- ✅ Component specifications
- ✅ Configuration guide
- ✅ Coding standards and style guide
- ✅ Hardware API usage rules
- ✅ Safety requirements documentation

### GUI Foundation ✅
- ✅ PyQt6 main window with 5-tab layout
- ✅ Subject Info tab UI
- ✅ Camera Control tab UI
- ✅ Treatment Control tab UI
- ✅ Protocol Builder tab UI
- ✅ Safety Monitor tab UI
- ✅ Tab navigation and state management

### Protocol Engine ✅
- ✅ Protocol data model (5 action types)
- ✅ Protocol execution engine
- ✅ Async execution with pause/resume/stop
- ✅ State machine for protocol playback
- ✅ Action validation and error handling

### Hardware API Exploration ✅
- ✅ Camera API exploration (VmbPy SDK)
  - ✅ 6 custom test scripts
  - ✅ 12 official examples analyzed
  - ✅ 24+ unit tests reviewed
- ✅ Actuator API exploration (Xeryon SDK)
  - ✅ 6 test scripts created
  - ✅ API documentation review
  - ✅ Hardware communication tested

---

## Phase 2: Hardware Abstraction Layer 🚧 IN PROGRESS (44% Complete)

### 1. Camera Controller HAL ✅ COMPLETE (100%)
- ✅ PyQt6-integrated camera controller
- ✅ Async frame acquisition with signals
- ✅ Exposure control (10-200000 µs)
- ✅ Gain control (0-24 dB)
- ✅ Frame rate monitoring
- ✅ Image capture to disk
- ✅ Video recording (MP4/AVI)
- ✅ Temperature monitoring
- ✅ Status feedback
- ✅ Error handling and recovery
- ✅ Camera widget with live streaming
- ✅ Frame throttling for GUI performance (30 FPS)
- ✅ Settings metadata display

**Test Status:** ✅ All tests passing with physical hardware

### 2. Actuator Controller HAL 🚧 IN PROGRESS (75%)
- ✅ PyQt6-integrated actuator controller
- ✅ Hardware connection (COM3, 9600 baud)
- ✅ Xeryon XLA-5-125-10MU support
- ✅ Status monitoring with signals
- ✅ Error handling (thermal protection)
- ✅ **Homing procedures (index finding)** 🎯 WORKING!
- ✅ **Critical fix: AUTO_SEND_SETTINGS=False**
- ⏳ Absolute position control (`set_position()`)
- ⏳ Relative movement (`make_step()`)
- ⏳ Speed control and profiling
- ⏳ Position limits and validation
- ⏳ Movement safety checks
- ⏳ Integration with GUI controls

**Test Status:** ✅ Connection and homing passing with physical hardware

**Remaining Tasks:**
1. Implement and test absolute positioning
2. Implement and test relative movements
3. Add speed control and acceleration
4. Validate position limits
5. Create actuator widget for GUI
6. Integration testing with protocol engine

### 3. Laser Controller HAL ⏳ PLANNED (0%)
- ⏳ PyQt6-integrated laser controller
- ⏳ Power control (0-100%)
- ⏳ Pulse mode configuration
- ⏳ Continuous mode support
- ⏳ Safety interlocks
- ⏳ Temperature monitoring
- ⏳ Status feedback
- ⏳ Emergency shutdown
- ⏳ Integration with safety system

**Dependencies:** Safety system must be implemented first

### 4. GPIO Controller HAL ⏳ PLANNED (0%)
- ⏳ FT232H interface integration
- ⏳ Footpedal monitoring
- ⏳ Smoothing device signal monitoring
- ⏳ Photodiode ADC reading
- ⏳ Event detection and debouncing
- ⏳ Signal conditioning
- ⏳ Integration with protocol engine

---

## Phase 3: Core Business Logic ⏳ PLANNED (0%)

### Safety System ⏳ HIGH PRIORITY
- ⏳ Safety interlock manager
- ⏳ Safety state machine
- ⏳ Emergency stop functionality
- ⏳ Hardware safety checks
- ⏳ Laser safety protocols
- ⏳ Footpedal integration
- ⏳ Safety monitor UI updates
- ⏳ Safety event logging

**Critical for:** Laser operation, production use

### Session Management ⏳
- ⏳ Session lifecycle management
- ⏳ Session data model
- ⏳ Session state persistence
- ⏳ Subject information management
- ⏳ Session start/stop controls
- ⏳ Session history tracking

### Event Logger ⏳
- ⏳ Immutable audit trail
- ⏳ Event types and categories
- ⏳ Timestamp precision
- ⏳ Log storage and retrieval
- ⏳ Log viewer UI
- ⏳ Log export functionality

### Database Layer ⏳
- ⏳ SQLAlchemy models
- ⏳ Database schema design
- ⏳ Migration system
- ⏳ Data access layer
- ⏳ Query optimization
- ⏳ Backup and recovery

---

## Phase 4: GUI Integration ⏳ PLANNED (0%)

### Subject Info Tab ⏳
- ⏳ Connect to session management
- ⏳ Subject data validation
- ⏳ Session creation workflow
- ⏳ Historical data display

### Camera Control Tab ⏳
- ⏳ Connect to camera HAL
- ⏳ Live preview implementation
- ⏳ Settings controls (exposure, gain)
- ⏳ Capture and recording controls
- ⏳ Image gallery/history

### Treatment Control Tab ⏳
- ⏳ Connect to actuator HAL
- ⏳ Connect to laser HAL
- ⏳ Position control UI
- ⏳ Laser power control UI
- ⏳ Real-time status display
- ⏳ Manual control mode

### Protocol Builder Tab ⏳
- ⏳ Visual protocol editor
- ⏳ Action drag-and-drop
- ⏳ Parameter configuration
- ⏳ Protocol validation
- ⏳ Save/load protocols
- ⏳ Protocol templates

### Safety Monitor Tab ⏳
- ⏳ Connect to safety system
- ⏳ Real-time status indicators
- ⏳ Safety checklist
- ⏳ Emergency stop controls
- ⏳ Alert notifications
- ⏳ Safety log viewer

---

## Phase 5: Testing & Quality Assurance ⏳ PLANNED (0%)

### Unit Tests ⏳
- ⏳ HAL layer tests
- ⏳ Business logic tests
- ⏳ Data model tests
- ⏳ Utility function tests
- ⏳ Target: 80%+ code coverage

### Integration Tests ⏳
- ⏳ Hardware integration tests
- ⏳ GUI integration tests
- ⏳ Protocol execution tests
- ⏳ Safety system tests
- ⏳ End-to-end workflows

### Hardware Tests ⏳
- ⏳ Camera stress testing
- ⏳ Actuator movement validation
- ⏳ Laser calibration
- ⏳ GPIO reliability
- ⏳ System timing validation

### User Acceptance Testing ⏳
- ⏳ Clinical workflow testing
- ⏳ Usability evaluation
- ⏳ Performance benchmarking
- ⏳ Safety validation
- ⏳ Documentation review

---

## Phase 6: Deployment & Documentation ⏳ PLANNED (0%)

### User Documentation ⏳
- ⏳ User manual
- ⏳ Quick start guide
- ⏳ Safety procedures
- ⏳ Troubleshooting guide
- ⏳ Video tutorials

### Technical Documentation ⏳
- ⏳ API documentation
- ⏳ Deployment guide
- ⏳ Maintenance procedures
- ⏳ Hardware setup guide
- ⏳ Configuration reference

### Deployment ⏳
- ⏳ Installer creation
- ⏳ Dependencies packaging
- ⏳ Configuration management
- ⏳ Update mechanism
- ⏳ Backup procedures

### Training ⏳
- ⏳ Operator training materials
- ⏳ Administrator guide
- ⏳ Safety training
- ⏳ Maintenance training

---

## Critical Issues & Blockers

### Resolved ✅
- ✅ Camera frame rate limitation (dynamic range issue)
- ✅ Actuator homing failure (AUTO_SEND_SETTINGS fix)
- ✅ Thermal protection errors (device settings conflict)
- ✅ Code formatting and linting setup

### Active 🚧
- None currently

### Known Issues ⏳
- ⏳ Need laser hardware for HAL development
- ⏳ GPIO hardware (FT232H) needs testing
- ⏳ Safety system requirements need validation

---

## Near-Term Priorities (Next 2 Weeks)

### High Priority 🔥
1. **Complete Actuator HAL** (25% remaining)
   - Absolute positioning
   - Relative movement
   - Speed control
   - Integration testing

2. **Start Laser Controller HAL** (requires hardware)
   - Hardware acquisition/setup
   - Basic control implementation
   - Safety interlocks

3. **Safety System Design**
   - Define safety requirements
   - Design state machine
   - Plan interlock architecture

### Medium Priority ⚡
4. **GUI Integration - Treatment Tab**
   - Connect actuator controls
   - Position display
   - Manual control mode

5. **Session Management**
   - Basic data model
   - Session lifecycle
   - Subject information

### Low Priority 📋
6. **Documentation Updates**
   - Keep WORK_LOG.md current
   - Update architecture docs
   - API documentation

---

## Long-Term Goals (Next 3 Months)

1. **Complete Phase 2** (Hardware Abstraction Layer)
   - All 4 HALs operational
   - Hardware integration tested
   - GUI controls connected

2. **Complete Phase 3** (Core Business Logic)
   - Safety system operational
   - Session management working
   - Event logging functional

3. **Begin Phase 4** (GUI Integration)
   - All tabs connected to backend
   - Protocol builder functional
   - Safety monitor operational

4. **Testing & Validation**
   - Unit test suite
   - Integration tests
   - Hardware validation

---

## Success Metrics

### Phase 2 (Current)
- **Target Completion:** End of November 2025
- **Current Progress:** 44%
- **Remaining Tasks:** 56%

**Component Status:**
- Camera HAL: 100% ✅
- Actuator HAL: 75% 🚧
- Laser HAL: 0% ⏳
- GPIO HAL: 0% ⏳

### Overall Project
- **Phase 1:** 100% ✅
- **Phase 2:** 44% 🚧
- **Phase 3:** 0% ⏳
- **Phase 4:** 0% ⏳
- **Phase 5:** 0% ⏳
- **Phase 6:** 0% ⏳

**Overall Completion:** ~24% (Phase 1 complete + Phase 2 partial)

---

## Notes

### Recent Achievements 🎉
- **2025-10-23:** Actuator homing breakthrough with AUTO_SEND_SETTINGS fix
- **2025-10-22:** Camera HAL completed with live streaming
- **2025-10-21:** Hardware API exploration completed

### Key Learnings 📚
- Use device's stored settings instead of overwriting from files
- Hardware protection mechanisms can trigger for configuration errors
- STAT register timing requires grace periods for updates
- Frame throttling essential for GUI performance with high-speed cameras

### Dependencies 🔗
- Python 3.10+
- PyQt6
- VmbPy SDK (Allied Vision)
- Xeryon Python library
- FT232H drivers (pending GPIO work)

---

**Document Status:** Active
**Review Frequency:** Weekly
**Owner:** Development Team
