# TOSCA Widget Integration Matrix

**Generated:** 2025-11-01
**Purpose:** Comprehensive documentation of all UI widgets, their integration status, locations, and signal connections
**Author:** AI Assistant (Task 3.4)

---

## Summary Statistics

- **Total Widget Files:** 19 (including dialogs)
- **Integrated Widgets:** 16
- **Orphaned/Unused Widgets:** 1
- **Dialog Widgets:** 2 (special category)

---

## Widget Integration Matrix

### Core Treatment Workflow Widgets

| Widget File | Class Name | Integrated | Location | Signals Connected | Purpose | Notes |
|-------------|-----------|------------|----------|-------------------|---------|-------|
| `subject_widget.py` | `SubjectWidget` | ✓ | Treatment Workflow > Left Column | `session_started` → `MainWindow._on_session_started` | Subject selection and session management | Manages DB and session manager references |
| `camera_widget.py` | `CameraWidget` | ✓ | Treatment Workflow > Right Column | `pixmap_ready` (internal), camera connection signals | Live camera view with streaming controls | Instantiated as `camera_live_view`, connected to CameraController |
| `treatment_setup_widget.py` | `TreatmentSetupWidget` | ✓ | Treatment Workflow > QStackedWidget[0] | `ready_button.clicked` → `MainWindow._on_start_treatment` | Protocol selection and treatment readiness check | Contains protocol selector widget |
| `active_treatment_widget.py` | `ActiveTreatmentWidget` | ✓ | Treatment Workflow > QStackedWidget[1] | Receives protocol engine and safety manager refs | Real-time treatment monitoring dashboard | Displays during active treatment |

### Hardware & Diagnostics Widgets

| Widget File | Class Name | Integrated | Location | Signals Connected | Purpose | Notes |
|-------------|-----------|------------|----------|-------------------|---------|-------|
| `camera_hardware_panel.py` | `CameraHardwarePanel` | ✓ | Hardware & Diagnostics > Left Column | Wired to `camera_live_view` for status | Camera connection/diagnostic controls | Lightweight connection panel separate from main camera view |
| `laser_widget.py` | `LaserWidget` | ✓ | Hardware & Diagnostics > Left Column | Laser controller signals, safety manager refs | Laser driver (COM10) controls | Treatment laser power control, safety-critical |
| `tec_widget.py` | `TECWidget` | ✓ | Hardware & Diagnostics > Left Column | TEC controller signals | TEC controller (COM9) temperature management | Temperature stabilization for laser diode |
| `actuator_connection_widget.py` | `ActuatorConnectionWidget` | ✓ | Hardware & Diagnostics > Left Column | Actuator controller connection signals | Linear actuator connection and positioning | Direct controller injection pattern |
| `safety_widget.py` | `SafetyWidget` | ✓ | Hardware & Diagnostics > Right Column | Safety manager state changes, GPIO interlock signals | Safety status and event log display | Composite widget containing GPIO and interlocks |
| `gpio_widget.py` | `GPIOWidget` | ✓ | Safety Widget (nested) | `gpio_connection_changed` → `MainWindow._on_gpio_connection_changed` | GPIO safety interlock monitoring | Footpedal, photodiode, smoothing motor status |
| `interlocks_widget.py` | `InterlocksWidget` | ✓ | Safety Widget (nested) | Safety manager interlock status signals | Consolidated safety interlock status display | Embedded within SafetyWidget |
| `smoothing_status_widget.py` | `SmoothingStatusWidget` | ✓ | Active Treatment Widget (nested) | GPIO controller smoothing motor signals | Smoothing motor control and vibration monitoring | Used during active treatment |
| `config_display_widget.py` | `ConfigDisplayWidget` | ✓ | Hardware & Diagnostics > Right Column | None (read-only display) | System configuration display (config.yaml) | Static configuration viewer |

### Protocol Builder Widgets

| Widget File | Class Name | Integrated | Location | Signals Connected | Purpose | Notes |
|-------------|-----------|------------|----------|-------------------|---------|-------|
| `line_protocol_builder.py` | `LineProtocolBuilderWidget` | ✓ | Protocol Builder Tab | `protocol_ready` → `MainWindow._on_line_protocol_ready` | Line-based protocol editor (concurrent actions) | Primary protocol builder, executes via `LineProtocolWorker` |
| `protocol_selector_widget.py` | `ProtocolSelectorWidget` | ✓ | Treatment Setup Widget (nested) | Protocol selection signals to parent widget | Visual protocol library browser | Embedded in TreatmentSetupWidget |
| `protocol_builder_widget.py` | `ProtocolBuilderWidget` | ✗ | **NOT INTEGRATED** | None | Legacy action-based protocol builder | **ORPHANED** - Replaced by LineProtocolBuilderWidget |

### Dialog Widgets (Special Category)

| Widget File | Class Name | Integrated | Location | Signals Connected | Purpose | Notes |
|-------------|-----------|------------|----------|-------------------|---------|-------|
| `view_sessions_dialog.py` | `ViewSessionsDialog` | ✓ (Dialog) | N/A (On-demand dialog) | None (modal dialog) | Session history viewer | Launched from SubjectWidget, not part of main layout |
| `performance_dashboard_widget.py` | `PerformanceDashboardWidget` | ✗ (Unused) | N/A | None | Performance metrics dashboard | **NOT CURRENTLY USED** - May be future feature |

---

## Signal Connection Details

### Critical Safety Signals

**GPIO → Safety Manager:**
- `gpio_widget.controller.safety_interlock_changed` → `safety_manager.set_gpio_interlock_status`
- Purpose: Real-time safety interlock status propagation

**Safety Manager → UI Widgets:**
- `safety_manager.safety_state_changed` → `MainWindow._update_master_safety_indicator`
- `safety_manager.laser_enable_changed` → Laser widget enable state
- `safety_manager.safety_event` → Event logging and UI display

**Watchdog → Safety System:**
- `safety_watchdog.heartbeat_failed` → Logger
- `safety_watchdog.watchdog_timeout_detected` → `MainWindow._handle_watchdog_timeout`

### Hardware Connection Signals

**Camera Controller:**
- `camera_controller.connection_changed` → `MainWindow._update_hardware_button_states`
- `camera_controller.connection_changed` → Status bar updates

**Actuator Controller:**
- `actuator_controller.connection_changed` → `MainWindow._update_hardware_button_states`
- `actuator_controller.connection_changed` → Status bar updates

**Laser Controller:**
- Laser connection signals → Status bar and header updates

### Workflow Signals

**Session Management:**
- `subject_widget.session_started` → `MainWindow._on_session_started`
- `session_manager.session_started` → `MainWindow._on_event_logger_session_started`
- `session_manager.session_ended` → `MainWindow._on_event_logger_session_ended`

**Treatment Workflow:**
- `treatment_setup_widget.ready_button.clicked` → `MainWindow._on_start_treatment`
- Purpose: Transition from Setup view (QStackedWidget[0]) to Active view (QStackedWidget[1])

**Protocol Execution:**
- `line_protocol_builder.protocol_ready` → `MainWindow._on_line_protocol_ready`
- `line_protocol_engine` callbacks:
  - `on_line_start` → `MainWindow._on_protocol_line_start`
  - `on_line_complete` → `MainWindow._on_protocol_line_complete`
  - `on_progress_update` → `MainWindow._on_protocol_progress_update`
  - `on_state_change` → `MainWindow._on_protocol_state_change`

**Developer Mode:**
- `MainWindow.dev_mode_changed` → `camera_live_view.set_dev_mode`
- `MainWindow.dev_mode_changed` → `treatment_setup_widget.set_dev_mode`

---

## Widget Hierarchy

```
MainWindow
├── Global Toolbar
│   ├── Emergency Stop Button
│   ├── Connect All / Disconnect All Buttons
│   ├── Test All Hardware Button
│   └── Pause / Resume Protocol Buttons
│
├── Status Bar
│   ├── Research Mode Watermark
│   ├── Camera Status Indicator
│   ├── Laser Status Indicator
│   ├── Actuator Status Indicator
│   └── Master Safety Indicator
│
└── QTabWidget (3 tabs)
    │
    ├── TAB 1: Hardware & Diagnostics
    │   ├── Left Column (50%) - Hardware Controls
    │   │   ├── Camera System Section
    │   │   │   └── CameraHardwarePanel
    │   │   ├── Linear Actuator Section
    │   │   │   └── ActuatorConnectionWidget
    │   │   └── Laser Systems Section
    │   │       ├── LaserWidget (treatment laser)
    │   │       └── TECWidget (temperature control)
    │   │
    │   └── Right Column (50%) - Diagnostics
    │       ├── SafetyWidget (composite)
    │       │   ├── GPIOWidget (footpedal, photodiode)
    │       │   └── InterlocksWidget (safety status)
    │       └── ConfigDisplayWidget (read-only config)
    │
    ├── TAB 2: Treatment Workflow
    │   ├── Left Column (40%) - Workflow Controls
    │   │   ├── SubjectWidget (session management)
    │   │   └── QStackedWidget (treatment phases)
    │   │       ├── [0] TreatmentSetupWidget (setup phase)
    │   │       │   └── ProtocolSelectorWidget
    │   │       └── [1] ActiveTreatmentWidget (active phase)
    │   │           └── SmoothingStatusWidget
    │   │
    │   └── Right Column (60%) - Camera View
    │       └── CameraWidget (live streaming)
    │
    └── TAB 3: Protocol Builder
        └── LineProtocolBuilderWidget (concurrent action editor)
```

---

## Dependency Injection Pattern

**CRITICAL:** MainWindow follows Hollywood Principle for hardware controllers.

All hardware controllers are instantiated in `MainWindow.__init__()` and injected into widgets:

```python
# MainWindow owns all controllers
self.actuator_controller = ActuatorController()
self.laser_controller = LaserController()
self.tec_controller = TECController()
self.gpio_controller = GPIOController()
self.camera_controller = CameraController(event_logger=self.event_logger)

# Controllers injected into widgets
self.camera_live_view = CameraWidget(camera_controller=self.camera_controller)
self.laser_widget = LaserWidget(controller=self.laser_controller)
self.tec_widget = TECWidget(controller=self.tec_controller)
self.actuator_connection_widget = ActuatorConnectionWidget(controller=self.actuator_controller)
self.safety_widget = SafetyWidget(db_manager=self.db_manager, gpio_controller=self.gpio_controller)
```

**Benefits:**
- Single source of truth for controller lifecycle
- Easier testing (mock controller injection)
- Clear ownership and cleanup on app exit
- Prevents widget reparenting anti-pattern

---

## Orphaned Widgets Analysis

### 1. `protocol_builder_widget.py` (ProtocolBuilderWidget)

**Status:** ✗ ORPHANED
**Reason:** Replaced by LineProtocolBuilderWidget
**Recommendation:**
- **Option A (Remove):** Delete file if no longer needed. Line-based protocol builder is more capable.
- **Option B (Preserve):** Keep as historical reference for action-based protocols if future migration needed.
- **Current Recommendation:** **REMOVE** - LineProtocolBuilderWidget is production-ready and more powerful.

### 2. `performance_dashboard_widget.py` (PerformanceDashboardWidget)

**Status:** ✗ UNUSED
**Reason:** Not integrated into any tab or layout
**Recommendation:**
- **Option A (Future Feature):** If performance metrics are planned, integrate into Developer menu or Hardware tab.
- **Option B (Remove):** Delete if not part of roadmap.
- **Current Recommendation:** **DEFER** - Revisit in Phase 6 (Pre-Clinical Validation) when performance profiling may be needed.

---

## Architecture Strengths

### 1. **Signal/Slot Architecture** ✅
All cross-widget communication uses PyQt6 signals/slots:
- Thread-safe by design
- Loose coupling between components
- No direct widget access violations
- Prevents widget reparenting anti-pattern (Lesson Learned #12)

### 2. **Composite Widgets** ✅
Logical grouping of related functionality:
- `SafetyWidget` contains `GPIOWidget` + `InterlocksWidget`
- `TreatmentSetupWidget` contains `ProtocolSelectorWidget`
- `ActiveTreatmentWidget` contains `SmoothingStatusWidget`

**Benefits:** Clear ownership, logical separation of concerns

### 3. **Dependency Injection** ✅
All hardware controllers managed centrally by MainWindow:
- Prevents circular dependencies
- Simplifies testing (mock injection)
- Clear lifecycle management
- Consistent with medical device architecture best practices

### 4. **QStackedWidget for Workflow** ✅
Treatment phases (Setup → Active) use QStackedWidget:
- Clean UI transitions without destroying widgets
- Preserves widget state during phase changes
- One-way workflow enforcement (prevents accidental reverse transitions)

---

## Recommendations for Architecture Improvements

### 1. **High Priority: Remove Orphaned Widgets**
- **Action:** Delete `protocol_builder_widget.py` (confirmed unused, replaced by LineProtocolBuilder)
- **Justification:** Reduces maintenance burden, prevents confusion
- **Risk:** Low (legacy widget, no active dependencies)

### 2. **Medium Priority: Performance Dashboard Integration Decision**
- **Action:** Either integrate `performance_dashboard_widget.py` or mark as deferred/remove
- **Options:**
  - **A)** Add to Developer menu for FPS/resource monitoring
  - **B)** Remove if not in roadmap
  - **C)** Document as Phase 6 feature (pre-clinical validation)
- **Recommendation:** **Option C** - Defer to Phase 6 when performance profiling becomes critical

### 3. **Low Priority: Widget Signal Documentation**
- **Action:** Add inline docstrings to all widget classes documenting their emitted signals
- **Justification:** Improves maintainability, helps onboard new developers
- **Example:**
  ```python
  class SubjectWidget(QWidget):
      """
      Subject selection and session management widget.

      Signals:
          session_started(int): Emitted when new session starts (session_id)
          session_ended(int): Emitted when session ends (session_id)
      """
      session_started = pyqtSignal(int)
      session_ended = pyqtSignal(int)
  ```

### 4. **Low Priority: Widget Connection Diagram**
- **Action:** Create PlantUML or Graphviz diagram showing all signal/slot connections
- **Justification:** Visual reference for debugging signal propagation issues
- **Benefit:** Especially helpful when debugging safety interlocks

---

## Integration Validation Checklist

For each new widget added to TOSCA:

- [ ] Widget file added to `src/ui/widgets/`
- [ ] Widget class inherits from `QWidget` or appropriate PyQt6 base class
- [ ] Widget imported in `main_window.py`
- [ ] Widget instantiated in `MainWindow.__init__()` or layout method
- [ ] Widget added to appropriate tab/layout
- [ ] Hardware controllers injected via dependency injection (not created in widget)
- [ ] All signals connected to appropriate slots
- [ ] Signal connections documented in widget docstring
- [ ] Widget added to this integration matrix
- [ ] Widget cleanup method called in `MainWindow.closeEvent()`
- [ ] Widget tested with mock hardware controllers

---

## Cross-Reference to Architecture Documentation

Related documentation:
- `docs/architecture/01_system_overview.md` - Overall architecture
- `docs/architecture/03_safety_system.md` - Safety signal flow
- `docs/architecture/10_concurrency_model.md` - Thread safety and signals
- `LESSONS_LEARNED.md #12` - Widget reparenting anti-pattern
- `LESSONS_LEARNED.md #4` - Requirements clarification before implementation

---

## Conclusion

The TOSCA widget architecture is **well-structured** with:
- ✅ Consistent dependency injection pattern
- ✅ Strong signal/slot architecture (thread-safe)
- ✅ Logical widget hierarchy matching workflow
- ✅ Good separation of concerns (composite widgets)
- ⚠️ Minor cleanup needed (1 orphaned widget, 1 unused widget)

**Overall Assessment:** Production-ready architecture with minimal technical debt.

**Next Steps:**
1. Remove `protocol_builder_widget.py` (confirmed obsolete)
2. Document decision on `performance_dashboard_widget.py` (defer vs. integrate vs. remove)
3. Update widget docstrings with signal documentation
4. Consider creating visual signal/slot connection diagram for onboarding

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Next Review:** Upon addition of new widgets or Phase 6 planning
