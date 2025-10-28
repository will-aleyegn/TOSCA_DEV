# TOSCA Development History

Compressed monthly summaries for long-term context (15-60 days old).

**Purpose:** Provides lightweight historical context without reading full WORK_LOG.md
**Update Frequency:** Monthly (automated compression from WORK_LOG.md)
**Full Details:** See `presubmit/archive/YYYY-MM_summary.md` for complete archives (60+ days)

---

## October 2025 - UI/UX Redesign Initiative (Summary)

**Duration:** 2025-10-25 through 2025-10-28
**Focus:** UI redesign, safety systems, GPIO integration, protocol management
**Outcome:** ✅ UI Redesign Phases 1-3 complete, version 0.9.5-alpha achieved

### Week 1: Foundation (10-25 to 10-26)
- **Safety Manager** - Multi-condition interlock system (GPIO, session, power, E-stop) with SAFE/UNSAFE/EMERGENCY_STOP state machine
- **Database Schema** - SQLite with subjects, sessions, events, technicians tables
- **GPIO Controller** - Arduino serial communication with watchdog heartbeat (500ms), motor control, vibration detection, photodiode monitoring
- **Safety Watchdog** - Background thread with selective shutdown policy (treatment laser disabled, camera/actuator preserved)
- **Key Patterns Documented** - I2C initialization, watchdog heartbeat, PyQt6 signal/slot integration

### Week 2: UI Redesign Phase 1 & 2 (10-27)
- **Phase 1 (Quick Wins)** - Global toolbar with E-STOP, master safety indicator, connection status icons, dev mode in menubar
- **Phase 2 (Treatment Dashboard)** - QStackedWidget refactoring for single-tab workflow, eliminated context-switching between setup/active views
- **Thread Safety Fix** - Replaced dangerous `ProtocolExecutionThread` with safe `ProtocolWorker` + `QThread` pattern (prevents GUI freezing)
- **New Widgets** - `SmoothingStatusWidget`, `ActuatorConnectionWidget`, `InterlocksWidget` for treatment dashboard
- **Repository Cleanup** - 8 unused imports fixed, 5 docs archived, test files organized, duplicates consolidated
- **Architecture Evolution** - "Mission control" concept fully realized with QStackedWidget state management

### Week 3: UI Redesign Phase 3 (10-28)
- **Protocol Selector Widget** - Visual protocol library with automatic scanning, preview panel, dual loading (list + custom files)
- **Example Protocols** - Created `basic_test.json`, `calibration.json`, `power_ramp.json` for testing
- **Manual Override Widget** - Dev-mode-only safety override controls for testing (requires `dev_mode: true` in config)
- **Camera Snapshot** - Verified existing implementation (already functional in `camera_widget.py`)
- **Completion** - All UI Redesign phases (1-3) complete, system ready for integration & validation

### Technical Milestones
- **Version:** 0.9.0-alpha → 0.9.5-alpha
- **Lines of Code:** ~15,000
- **Test Coverage:** 80% average
- **Commits:** 25+ commits in October
- **Architecture Patterns:** QStackedWidget workflows, signal/slot integration, selective shutdown policy

### Key Decisions
- **UI Pattern:** Single-tab "mission control" dashboard over multi-tab context-switching
- **Thread Safety:** Workers + signals over direct thread manipulation
- **Safety Philosophy:** Selective shutdown preserves diagnostic capabilities
- **Protocol Management:** Visual library + file browsing over manual file selection only

### Files Created (October)
- `src/hardware/gpio_controller.py` - Arduino GPIO integration
- `src/core/safety_watchdog.py` - Safety monitoring system
- `src/ui/widgets/protocol_selector_widget.py` - Protocol library browser
- `src/ui/widgets/manual_override_widget.py` - Dev-mode safety overrides
- `src/ui/widgets/smoothing_status_widget.py` - Hotspot smoothing status
- `src/ui/widgets/actuator_connection_widget.py` - Actuator connectivity
- `protocols/examples/*.json` - Example treatment protocols

---

## Archive Information

**Compression Ratio:** 40:1 (1541 lines → 38 lines)
**Full Archive Location:** `presubmit/archive/2025-10_summary.md` (after 60 days)
**Keyword Index:** See `presubmit/archive/INDEX.md` for searchable keyword lookup
**Recent Detailed History:** See `WORK_LOG.md` (last 14 days, uncompressed)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-28
**Next Update:** 2025-11-28 (monthly compression schedule)
