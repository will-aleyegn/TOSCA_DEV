# Archive Index - Keyword Search

**Purpose:** Fast keyword-based lookup for historical project information
**Coverage:** Archived documentation (15-60+ days old)
**Recent History:** See `WORK_LOG.md` (0-14 days) and `HISTORY.md` (15-60 days)

---

## How to Use This Index

### Search by Keyword
1. Use browser find (Ctrl+F / Cmd+F) to search for keywords
2. Find relevant category or file reference
3. Open referenced file for full details

### Search by Date
- **0-14 days:** Check `WORK_LOG.md` (root directory)
- **15-60 days:** Check `HISTORY.md` (root directory)
- **60+ days:** Check this archive (monthly summaries)

### Search by Topic
Navigate to topic section below for relevant keywords

---

## Quick Reference

| Date Range | Location | Content |
|------------|----------|---------|
| 0-14 days | `WORK_LOG.md` | Detailed recent history (uncompressed) |
| 15-60 days | `HISTORY.md` | Monthly compressed summaries |
| Oct 2025 | `HISTORY.md` | UI Redesign, GPIO, safety systems |
| Oct 22-27 | `presubmit/archive/WORK_LOG_*.md` | Historical work logs |
| Sep-Oct 2025 | `presubmit/archive/PHASE_*` | Phase completion details |

---

## Keyword Categories

### UI/UX Keywords
**Primary Keywords:** UI redesign, PyQt6, QStackedWidget, widgets, treatment dashboard, mission control, tab layout, user experience, workflow, context switching

**Related Files:**
- `HISTORY.md` - October 2025 (Week 2-3: UI Redesign Phase 1-3)
- `WORK_LOG_2025-10-27_1400.md` - Treatment tab refactoring
- `PROJECT_STATUS_2025-10-27_1254.md` - UI redesign milestone tracking

**Key Implementations:**
- QStackedWidget pattern (single-tab workflow)
- Protocol selector widget (visual library browser)
- Manual override widget (dev-mode safety controls)
- Interlocks widget (real-time safety status)
- Treatment dashboard (setup → active transition)

---

### Safety & Hardware Keywords
**Primary Keywords:** safety, interlocks, GPIO, Arduino, watchdog, selective shutdown, E-stop, emergency stop, photodiode, vibration detection, motor control, safety manager, state machine

**Related Files:**
- `HISTORY.md` - October 2025 (Week 1: GPIO Module, Safety Watchdog)
- `WORK_LOG_2025-10-26_archived.md` - GPIO controller implementation
- `PROJECT_STATUS_2025-10-27_1254.md` - Safety system milestones

**Key Implementations:**
- Safety Manager (multi-condition interlock logic)
- GPIO Controller (Arduino serial communication)
- Safety Watchdog (heartbeat monitoring, timeout detection)
- Selective Shutdown Policy (treatment laser disabled, diagnostics preserved)
- Vibration detection (accelerometer, 0.8g threshold)
- Photodiode monitoring (laser power verification)

---

### Threading & Concurrency Keywords
**Primary Keywords:** threading, QThread, signals, slots, moveToThread, worker pattern, thread safety, protocol worker, GUI freezing, event loop, background thread

**Related Files:**
- `HISTORY.md` - October 2025 (Week 2: Thread Safety Fix)
- `WORK_LOG_2025-10-27_1400.md` - ProtocolWorker implementation

**Key Patterns:**
- Worker + moveToThread() pattern (safe threading)
- Signal/slot architecture (cross-thread communication)
- Watchdog heartbeat thread (500ms interval)
- Thread-safe command execution (threading.RLock)
- Avoided: Direct QThread subclassing with run() override

---

### Camera & Image Processing Keywords
**Primary Keywords:** camera, VmbPy, Allied Vision, frame capture, snapshot, image processing, stream, continuous acquisition, camera widget

**Related Files:**
- `WORK_LOG_2025-10-22_camera-module.md` - Camera module exploration
- `CAMERA_FIX_SUMMARY.md` - Camera integration fixes
- `CAMERA_FIX_INSTRUCTIONS.md` - Camera troubleshooting guide
- `apply_camera_fix.py` - Automated camera fix script

**Key Implementations:**
- Camera snapshot feature (automatic directory creation)
- Continuous streaming (frame rate control)
- VmbPy integration (Allied Vision 1800 U-158c)
- Image display widget (QLabel with pixmap)

---

### Actuator & Motion Control Keywords
**Primary Keywords:** actuator, Xeryon, linear stage, positioning, motion control, waypoints, homing, calibration, movement, micrometers

**Related Files:**
- `WORK_LOG_2025-10-23_actuator-gui.md` - Actuator GUI development
- `HISTORY.md` - October 2025 (calibration protocol)
- `PROJECT_STATUS_2025-10-27_1254.md` - Actuator module status

**Key Implementations:**
- Actuator controller (serial communication)
- Position tracking (real-time display)
- Calibration protocol (waypoint validation)
- Movement commands (absolute/relative positioning)

---

### Protocol & Treatment Keywords
**Primary Keywords:** protocol, treatment, execution, power ramping, protocol builder, protocol selector, JSON protocol, action sequence, calibration protocol, power limits

**Related Files:**
- `HISTORY.md` - October 2025 (Week 3: Protocol Selector)
- `WORK_LOG_2025-10-27_1400.md` - Protocol management
- `PHASE_0_2_COMPLETION_DETAILS.md` - Early protocol work

**Key Implementations:**
- Protocol Selector Widget (visual library browser)
- Example protocols (basic_test, calibration, power_ramp)
- Protocol loading (dual mode: list + file browser)
- Protocol validation (JSON schema, safety limits)
- Action sequencing (move, wait, laser on/off, power ramp)

---

### Database & Session Keywords
**Primary Keywords:** database, SQLite, sessions, subjects, technicians, events, session manager, ORM, SQLAlchemy, data persistence

**Related Files:**
- `HISTORY.md` - October 2025 (Week 1: Database Schema)
- `WORK_LOG_2025-10-26_archived.md` - Session management
- `PROJECT_STATUS_2025-10-27_1254.md` - Database milestones

**Key Schema:**
- `subjects` table (patient information)
- `sessions` table (treatment sessions with timestamps)
- `events` table (safety and system events log)
- `technicians` table (user authentication)

---

### Architecture & Patterns Keywords
**Primary Keywords:** architecture, design patterns, layered architecture, HAL, hardware abstraction, signal/slot, state machine, selective shutdown, mission control, worker pattern

**Related Files:**
- `HISTORY.md` - October 2025 (Key Patterns section)
- `WORK_LOG_2025-10-27_1400.md` - Architectural decisions
- `PROJECT_STATUS_2025-10-27_1254.md` - Architecture milestones

**Key Patterns:**
- I2C Device Initialization (auto-init + manual recovery)
- Watchdog Heartbeat (<400ms chunks, never >500ms)
- PyQt6 Signal/Slot (reactive UI updates)
- QStackedWidget Workflows (sequential state management)
- Selective Shutdown Policy (preserve diagnostics)
- Worker + moveToThread (safe threading)

---

### Testing & Quality Keywords
**Primary Keywords:** testing, unit tests, integration tests, test coverage, pytest, pre-commit hooks, black, flake8, isort, mypy, linting, code quality

**Related Files:**
- `COMPLETED_TASKS.md` - Test completion tracking
- `PHASE_0_2_COMPLETION_DETAILS.md` - Phase testing results
- `HISTORY.md` - October 2025 (Metrics section)

**Quality Metrics:**
- Test Coverage: 80% average
- Lines of Code: ~15,000
- Static Analysis: Passing (Black, flake8, isort, mypy)
- Pre-commit hooks: 11 checks configured

---

### Configuration & Setup Keywords
**Primary Keywords:** configuration, config.yaml, setup, environment, dependencies, requirements.txt, pyproject.toml, virtual environment, installation

**Related Files:**
- `AI_UPDATE_ENFORCEMENT_REFERENCE.md` - AI documentation update policy
- `PROJECT_STATUS_2025-10-27_1254.md` - Project setup status

**Configuration Files:**
- `config.yaml` - Main application configuration
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Package configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration

---

### Documentation & Process Keywords
**Primary Keywords:** documentation, onboarding, session state, checkpoint, work log, history, archive, memory optimization, git content policy, coding standards

**Related Files:**
- `HISTORY.md` - Monthly compressed summaries (NEW as of 2025-10-28)
- `SESSION_STATE.md` - Session checkpoint (NEW as of 2025-10-28)
- `ONBOARDING.md` - AI onboarding system (NEW as of 2025-10-28)
- `AI_UPDATE_ENFORCEMENT_REFERENCE.md` - Documentation update enforcement

**Recent Improvements (October 2025):**
- Onboarding time reduced: 5-10 minutes → 2.5 minutes (60% reduction)
- Session recovery: <30 seconds from checkpoint
- WORK_LOG compression: 1541 → 253 lines (84% smaller)
- HISTORY.md: 40:1 compression ratio for monthly summaries

---

### Error & Debugging Keywords
**Primary Keywords:** error, bug fix, troubleshooting, debugging, exception handling, validation, error messages, logging, stack trace

**Related Files:**
- `CAMERA_FIX_CHECKLIST.md` - Camera troubleshooting
- `CAMERA_FIX_INSTRUCTIONS.md` - Step-by-step camera fixes
- `WORK_LOG_2025-10-26_archived.md` - GPIO error handling

**Common Issues:**
- I2C device initialization failures (auto-retry pattern)
- Camera frame acquisition timeout (hardware not ready)
- MyPy path resolution (use --no-verify workaround)
- Arduino watchdog timeout (break delays into <400ms chunks)

---

### Milestone & Version Keywords
**Primary Keywords:** milestone, version, release, phase completion, sprint, UI redesign, 0.9.5-alpha, project status, roadmap

**Related Files:**
- `PHASE_0_2_COMPLETION_DETAILS.md` - Early phase completions
- `COMPLETED_TASKS.md` - Task completion tracking
- `PROJECT_STATUS_2025-10-27_1254.md` - Version history
- `HISTORY.md` - October 2025 milestones

**Version History:**
- 0.9.5-alpha (October 2025): UI Redesign complete, GPIO integration
- 0.9.0-alpha (September 2025): Core functionality, camera/actuator modules
- Earlier versions: See archived PROJECT_STATUS files

---

## Archive File Reference

### Work Log Archives
| File | Date Range | Primary Topics |
|------|-----------|----------------|
| `WORK_LOG_2025-10-27_1400.md` | Oct 27, 2025 | UI redesign, repository cleanup, QStackedWidget |
| `WORK_LOG_2025-10-26_archived.md` | Oct 25-26, 2025 | GPIO module, safety watchdog, database schema |
| `WORK_LOG_2025-10-23_actuator-gui.md` | Oct 23, 2025 | Actuator GUI development |
| `WORK_LOG_2025-10-22_camera-module.md` | Oct 22, 2025 | Camera module exploration, VmbPy integration |

### Status Archives
| File | Date | Primary Topics |
|------|------|----------------|
| `PROJECT_STATUS_2025-10-27_1254.md` | Oct 27, 2025 | Version 0.9.5-alpha status, UI redesign tracking |

### Phase Completion
| File | Phase | Primary Topics |
|------|-------|----------------|
| `PHASE_0_2_COMPLETION_DETAILS.md` | Phase 0-2 | Early milestones, foundational work |
| `COMPLETED_TASKS.md` | Various | Task completion checklist |

### Camera-Specific Archives
| File | Purpose | Primary Topics |
|------|---------|----------------|
| `CAMERA_FIX_SUMMARY.md` | Summary | Camera integration issues resolved |
| `CAMERA_FIX_INSTRUCTIONS.md` | Guide | Step-by-step camera troubleshooting |
| `CAMERA_FIX_CHECKLIST.md` | Checklist | Camera fix verification steps |
| `apply_camera_fix.py` | Script | Automated camera fix application |

### Subdirectories
| Directory | Purpose | Contents |
|-----------|---------|----------|
| `completed_improvements/` | Archived plans | Completed improvement documents |

---

## Monthly Summaries (60+ Days)

**Format:** `YYYY-MM_summary.md`

**Current Status:** No monthly summaries yet (project started October 2025)

**Future Structure:**
- `2025-10_summary.md` - October 2025 full archive (available after Nov 28, 2025)
- `2025-11_summary.md` - November 2025 archive (available after Dec 28, 2025)
- And so on...

**Note:** HISTORY.md currently contains October 2025 summary (15-60 day range). Will migrate to monthly archive after 60 days.

---

## Search Tips

### Finding Specific Information

**By Technology:**
- Search: "PyQt6" → UI/UX section
- Search: "Arduino" → Safety & Hardware section
- Search: "SQLite" → Database & Session section

**By Problem:**
- Search: "error" + topic → Error & Debugging section
- Search: "fix" + component → Relevant fix files
- Search: "troubleshooting" → CAMERA_FIX files

**By Date:**
- Last 2 weeks → `WORK_LOG.md`
- Last 2 months → `HISTORY.md`
- Specific date → Search archives by filename

**By Feature:**
- Search: "protocol" → Protocol & Treatment section
- Search: "safety" → Safety & Hardware section
- Search: "widget" → UI/UX section

---

## Maintenance Schedule

**Weekly:** WORK_LOG.md updated with new actions
**Monthly:** HISTORY.md compressed summary added
**Quarterly:** Archive INDEX.md keyword additions
**Annual:** Major milestone summaries

**Last Updated:** 2025-10-28
**Next Review:** 2025-11-28 (add November summary to HISTORY.md)

---

## Document Statistics

**Total Archived Files:** 14 files + 1 subdirectory
**Date Range:** October 22-28, 2025
**Total Archive Size:** ~240 KB
**Keyword Categories:** 12 major categories
**Searchable Keywords:** 100+ terms

---

**Index Version:** 1.0.0
**Created:** 2025-10-28
**Purpose:** Enable fast keyword-based historical lookup without reading full archives
