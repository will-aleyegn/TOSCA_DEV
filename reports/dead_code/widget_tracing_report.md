# TOSCA UI Widget Tracing Report

**Date:** 2025-10-31
**Task:** Subtask 3.2 - Trace widget imports and instantiation in main_window.py
**Purpose:** Map how each widget is imported, instantiated, and placed in the UI
**File Analyzed:** src/ui/main_window.py

---

## Widget Instantiation Summary

### ✅ Integrated Widgets (10 widgets + 1 sub-component)

| # | Widget Class | Line | Import Type | Instantiation Location | Layout/Tab |
|---|-------------|------|-------------|----------------------|------------|
| 1 | CameraWidget | 407 | Top-level import (line 34) | Treatment Tab (right column) | treatment_tab → right_content |
| 2 | SafetyWidget | 324 | Top-level import (line 35) | Hardware Tab (right column) | hardware_tab → right_content |
| 3 | SubjectWidget | 370 | Top-level import (line 36) | Treatment Tab (left column) | treatment_tab → left_content |
| 4 | TreatmentSetupWidget | 379 | Top-level import (line 37) | Treatment Tab (stacked widget, index 0) | treatment_stack |
| 5 | ActiveTreatmentWidget | 383 | Top-level import (line 33) | Treatment Tab (stacked widget, index 1) | treatment_stack |
| 6 | LaserWidget | 299 | Lazy import (line 297) | Hardware Tab (left column) | hardware_tab → left_content |
| 7 | TECWidget | 305 | Lazy import (line 303) | Hardware Tab (left column) | hardware_tab → left_content |
| 8 | ConfigDisplayWidget | 340 | Lazy import (line 338) | Hardware Tab (right column) | hardware_tab → right_content |
| 9 | ActuatorConnectionWidget | 472 | Lazy import (line 470) | Hardware Tab (left column) | hardware_tab → left_content |
| 10 | LineProtocolBuilderWidget | 449 | Lazy import (line 447) | Protocol Builder Tab | protocol_builder_tab |
| 11 | CameraHardwarePanel | 271 | Lazy import (line 269) | Hardware Tab (left column, sub-component) | hardware_tab → left_content |

---

## Detailed Widget Tracing

### TAB 1: Hardware & Diagnostics Tab

**Structure:** 2-column layout (50% left | 50% right) with independent scrolling

#### Left Column (Core Hardware Controls)

1. **CameraHardwarePanel** (Sub-Component)
   - **Import:** Line 269 (lazy import in `_init_ui()`)
   - **Instantiation:** Line 271
     ```python
     from ui.widgets.camera_hardware_panel import CameraHardwarePanel
     self.camera_hardware_panel = CameraHardwarePanel(None)  # Will set camera_live_view later
     ```
   - **Layout:** `hardware_left_layout.addWidget(self.camera_hardware_panel)`
   - **Purpose:** Lightweight camera status + connect/disconnect controls
   - **Controller:** camera_controller (linked later)
   - **Section Header:** "📷 Camera System ✗" (line 261)

2. **ActuatorConnectionWidget**
   - **Import:** Line 470 (lazy import later in setup)
   - **Instantiation:** Line 472-473
     ```python
     from ui.widgets.actuator_connection_widget import ActuatorConnectionWidget
     self.actuator_connection_widget = ActuatorConnectionWidget(
         controller=self.actuator_controller
     )
     ```
   - **Layout:** Inserted after actuator_header (deferred insertion)
   - **Purpose:** Xeryon linear actuator connection and positioning controls
   - **Controller:** actuator_controller (passed at instantiation)
   - **Section Header:** "🔧 Linear Actuator Controller ✗" (line 275)

3. **LaserWidget**
   - **Import:** Line 297 (lazy import in `_init_ui()`)
   - **Instantiation:** Line 299
     ```python
     from ui.widgets.laser_widget import LaserWidget
     self.laser_widget = LaserWidget(controller=self.laser_controller)
     ```
   - **Layout:** `hardware_left_layout.addWidget(self.laser_widget)`
   - **Purpose:** Arroyo 6300 laser diode current control (treatment laser)
   - **Controller:** laser_controller (passed at instantiation)
   - **Section Header:** "⚡ Laser Systems (Driver + TEC) ✗" (line 289)

4. **TECWidget**
   - **Import:** Line 303 (lazy import in `_init_ui()`)
   - **Instantiation:** Line 305
     ```python
     from ui.widgets.tec_widget import TECWidget
     self.tec_widget = TECWidget(controller=self.tec_controller)
     ```
   - **Layout:** `hardware_left_layout.addWidget(self.tec_widget)`
   - **Purpose:** Arroyo 5305 TEC temperature control
   - **Controller:** tec_controller (passed at instantiation)
   - **Section Header:** Same as LaserWidget (both under "Laser Systems")

#### Right Column (Diagnostics & Safety)

5. **SafetyWidget**
   - **Import:** Line 35 (top-level import)
   - **Instantiation:** Line 324-326
     ```python
     self.safety_widget = SafetyWidget(
         db_manager=self.db_manager, gpio_controller=self.gpio_controller
     )
     ```
   - **Layout:** `hardware_right_layout.addWidget(self.safety_widget)`
   - **Purpose:** Safety status dashboard + GPIO interlock monitoring + event logging
   - **Dependencies:** db_manager, gpio_controller
   - **Section:** Standalone (no header)

6. **ConfigDisplayWidget**
   - **Import:** Line 338 (lazy import in `_init_ui()`)
   - **Instantiation:** Line 340
     ```python
     from ui.widgets.config_display_widget import ConfigDisplayWidget
     self.config_display_widget = ConfigDisplayWidget()
     ```
   - **Layout:** `hardware_right_layout.addWidget(self.config_display_widget)`
   - **Purpose:** Display current system configuration (YAML settings)
   - **Controller:** None (reads config directly)
   - **Section:** Standalone (no header)

---

### TAB 2: Treatment Tab

**Structure:** 2-column layout (40% left | 60% right) with scrolling

#### Left Column (Subject + Protocol Controls)

7. **SubjectWidget**
   - **Import:** Line 36 (top-level import)
   - **Instantiation:** Line 370-372
     ```python
     self.subject_widget = SubjectWidget()
     self.subject_widget.set_managers(self.db_manager, self.session_manager)
     self.subject_widget.session_started.connect(self._on_session_started)
     ```
   - **Layout:** `left_layout.addWidget(self.subject_widget)`
   - **Purpose:** Subject selection and session creation
   - **Dependencies:** db_manager, session_manager
   - **Signals:** `session_started` → `_on_session_started()`

8. **TreatmentSetupWidget** (Stacked Widget - Index 0)
   - **Import:** Line 37 (top-level import)
   - **Instantiation:** Line 379-380
     ```python
     self.treatment_stack = QStackedWidget()
     self.treatment_setup_widget = TreatmentSetupWidget()
     self.treatment_stack.addWidget(self.treatment_setup_widget)
     ```
   - **Layout:** Inside `treatment_stack` (QStackedWidget) at index 0
   - **Purpose:** Treatment protocol selection and setup (pre-treatment)
   - **Visibility:** Shown when no treatment is active
   - **Stacked Switch:** Switches to ActiveTreatmentWidget (index 1) when treatment starts

9. **ActiveTreatmentWidget** (Stacked Widget - Index 1)
   - **Import:** Line 33 (top-level import)
   - **Instantiation:** Line 383-384
     ```python
     self.active_treatment_widget = ActiveTreatmentWidget()
     self.treatment_stack.addWidget(self.active_treatment_widget)
     ```
   - **Layout:** Inside `treatment_stack` (QStackedWidget) at index 1
   - **Purpose:** Real-time treatment monitoring dashboard (during treatment)
   - **Visibility:** Shown when treatment is active
   - **Stacked Switch:** Switches back to TreatmentSetupWidget (index 0) when treatment ends

#### Right Column (Camera Live View)

10. **CameraWidget**
    - **Import:** Line 34 (top-level import)
    - **Instantiation:** Line 407
      ```python
      self.camera_live_view = CameraWidget(camera_controller=self.camera_controller)
      ```
    - **Layout:** `right_layout.addWidget(self.camera_live_view)`
    - **Purpose:** Allied Vision camera live streaming, controls, and image capture
    - **Controller:** camera_controller (passed at instantiation)
    - **Note:** Visible streaming controls NOT hidden - users need during treatment

---

### TAB 3: Line-Based Protocol Builder Tab

**Structure:** Single-column layout with LineProtocolBuilderWidget

11. **LineProtocolBuilderWidget**
    - **Import:** Line 447 (lazy import in `_init_ui()`)
    - **Instantiation:** Line 449-450
      ```python
      from ui.widgets.line_protocol_builder import LineProtocolBuilderWidget
      self.line_protocol_builder = LineProtocolBuilderWidget()
      ```
    - **Layout:** `builder_layout.addWidget(self.line_protocol_builder)`
    - **Purpose:** Line-based protocol builder (concurrent actions per line)
    - **Configuration:** Safety limits configured from TOSCA defaults (lines 451-467)
    - **Tab:** Dedicated full-screen protocol builder tab

---

## Import Strategy Analysis

### Top-Level Imports (Loaded at startup)
**Count:** 5 widgets

Benefits:
- Immediate availability
- No runtime import overhead
- Predictable startup performance

Widgets:
1. ActiveTreatmentWidget (line 33)
2. CameraWidget (line 34)
3. SafetyWidget (line 35)
4. SubjectWidget (line 36)
5. TreatmentSetupWidget (line 37)

**Rationale:** Core treatment flow widgets that are always needed

### Lazy Imports (Imported in `_init_ui()`)
**Count:** 6 widgets

Benefits:
- Reduced startup time
- Lower initial memory footprint
- Widgets loaded just before use

Widgets:
1. CameraHardwarePanel (line 269)
2. LaserWidget (line 297)
3. TECWidget (line 303)
4. ConfigDisplayWidget (line 338)
5. LineProtocolBuilderWidget (line 447)
6. ActuatorConnectionWidget (line 470)

**Rationale:** Hardware control widgets loaded during UI construction, not critical path

---

## Controller Dependencies

| Widget | Controller/Manager | Passed How | Connection |
|--------|-------------------|------------|------------|
| CameraWidget | camera_controller | Constructor param | Direct |
| CameraHardwarePanel | camera_controller | Set later via `set_camera_live_view()` | Indirect |
| LaserWidget | laser_controller | Constructor param | Direct |
| TECWidget | tec_controller | Constructor param | Direct |
| ActuatorConnectionWidget | actuator_controller | Constructor param | Direct |
| SafetyWidget | db_manager, gpio_controller | Constructor params | Direct |
| SubjectWidget | db_manager, session_manager | `set_managers()` method | Method call |
| TreatmentSetupWidget | None | N/A | Standalone |
| ActiveTreatmentWidget | None | N/A | Standalone |
| LineProtocolBuilderWidget | None | N/A | Standalone |
| ConfigDisplayWidget | None | Reads config directly | Standalone |

**Pattern:** Hardware control widgets receive controllers at instantiation for thread-safe communication.

---

## Signal/Slot Connections

### SubjectWidget Signals
```python
self.subject_widget.session_started.connect(self._on_session_started)
```
- **Signal:** `session_started`
- **Slot:** `MainWindow._on_session_started()`
- **Purpose:** Notify main window when new session created

### Other Widget Signals
- Most widgets emit signals handled by their respective controllers
- Main window connects to controller signals, not widget signals directly
- **Design Pattern:** Controller-mediated communication (loose coupling)

---

## Layout Hierarchy

```
MainWindow
└── QWidget (central_widget)
    └── QVBoxLayout
        └── QTabWidget (self.tabs)
            ├── TAB 1: Hardware & Diagnostics (hardware_tab)
            │   └── QHBoxLayout (2 columns)
            │       ├── LEFT COLUMN (QScrollArea → left_content)
            │       │   ├── CameraHardwarePanel
            │       │   ├── ActuatorConnectionWidget
            │       │   ├── LaserWidget
            │       │   └── TECWidget
            │       └── RIGHT COLUMN (QScrollArea → right_content)
            │           ├── SafetyWidget
            │           └── ConfigDisplayWidget
            │
            ├── TAB 2: Treatment (treatment_tab)
            │   └── QHBoxLayout (2 columns)
            │       ├── LEFT COLUMN (QScrollArea → left_content)
            │       │   ├── SubjectWidget
            │       │   └── QStackedWidget (treatment_stack)
            │       │       ├── [0] TreatmentSetupWidget
            │       │       └── [1] ActiveTreatmentWidget
            │       └── RIGHT COLUMN (QScrollArea → right_content)
            │           └── CameraWidget (camera_live_view)
            │
            └── TAB 3: Protocol Builder (protocol_builder_tab)
                └── QVBoxLayout
                    └── LineProtocolBuilderWidget
```

---

## NOT Integrated Widgets (8 widgets)

These widgets exist in `src/ui/widgets/` but are NOT imported or used in main_window.py:

| Widget | Potential Reason |
|--------|-----------------|
| GPIOWidget | Replaced by SafetyWidget (which includes GPIO monitoring) |
| InterlocksWidget | Functionality integrated into SafetyWidget |
| SmoothingStatusWidget | Functionality integrated into SafetyWidget |
| ProtocolBuilderWidget | Replaced by LineProtocolBuilderWidget (line-based > action-based) |
| ProtocolSelectorWidget | Functionality integrated into TreatmentSetupWidget |
| PerformanceDashboardWidget | Development/debug tool, not production feature |
| ViewSessionsDialog | Dialog (not widget), launched dynamically from menu/toolbar |
| (No others) | N/A |

---

## Key Findings

### ✅ Good Practices
1. **Lazy imports** for hardware widgets - reduced startup time
2. **Top-level imports** for core treatment widgets - always available
3. **Controller dependency injection** - clear dependencies, testable
4. **Stacked widget pattern** for TreatmentSetup/ActiveTreatment - clean state transitions
5. **Signal/slot architecture** - loose coupling between widgets

### ⚠️ Potential Issues
1. **8 unused widgets** (44% of total widgets) - significant dead code
2. **Unclear widget replacements** - no documentation of GPIOWidget → SafetyWidget migration
3. **Deferred actuator widget insertion** - complex logic at line 472-473
4. **camera_live_view vs camera_hardware_panel** - two camera widgets, potential confusion

### 📝 Questions for Follow-up
1. Is **ProtocolBuilderWidget** obsolete? Replaced by **LineProtocolBuilderWidget**?
2. Does **SafetyWidget** fully replace **GPIOWidget** + **InterlocksWidget** + **SmoothingStatusWidget**?
3. Is **ProtocolSelectorWidget** functionality now in **TreatmentSetupWidget**?
4. Is **PerformanceDashboardWidget** intended for production or debug only?
5. Should **ViewSessionsDialog** be launched from a menu action?

---

## Next Steps

1. ✅ **Subtask 3.2 Complete** - Widget tracing documented
2. ⏭️ **Subtask 3.3** - Validate widget placement and signal connections (visual inspection + signal tracing)
3. ⏭️ **Subtask 3.4** - Create comprehensive widget integration matrix

---

**Tracing Completed:** 2025-10-31
**Analyst:** AI Agent (Claude Code)
**Task Master Task:** 3.2 - Trace widget imports and instantiation in main_window.py
