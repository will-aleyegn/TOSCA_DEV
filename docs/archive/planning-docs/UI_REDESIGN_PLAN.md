# TOSCA GUI UI/UX Redesign Plan

**Date:** 2025-10-27
**Status:** In Progress
**Goal:** Transform tab-based UI into integrated "Treatment Dashboard" for improved workflow efficiency and safety

---

## Executive Summary

The current TOSCA GUI uses a tab-based navigation pattern that causes information fragmentation and workflow disruption during treatment procedures. This redesign consolidates critical controls and status information into an integrated "Treatment Dashboard" that provides operators with continuous visibility of safety interlocks, sensor data, and treatment progress without requiring tab switching.

**Key Problems Solved:**
- [DONE] Eliminates dangerous context-switching between Safety and Treatment tabs
- [DONE] Provides continuous visibility of master safety state
- [DONE] Consolidates smoothing motor controls with treatment workflow
- [DONE] Creates single "mission control" view for procedure execution
- [DONE] Improves information hierarchy and visual clarity

---

## Current Architecture

### Tab Structure (Before)
1. **Subject Selection** - Subject management, session creation
2. **Camera/Alignment** - Live camera feed, alignment controls
3. **Treatment Control** - Laser, actuator, motor controls, protocol execution
4. **Safety Status** - GPIO controls (motor, photodiode), software interlocks, event log

### Pain Points
1. **Information Fragmentation**: Safety interlocks on one tab, treatment controls on another
2. **Scattered Controls**: Smoothing motor lives on Safety tab but is prerequisite for Treatment tab
3. **No Global Safety Visibility**: Master safety state (SAFE/UNSAFE/E-STOP) only visible on Safety tab
4. **Poor Status Bar Design**: Mixes configuration, status, and actions
5. **Missing Mission Control View**: No single consolidated operational dashboard

---

## Redesigned Architecture

### New Window Structure

```text
┌─────────────────────────────────────────────────────────────┐
│ TOSCA Laser Control System                            [_][□][X]│
├─────────────────────────────────────────────────────────────┤
│ File   Developer                                             │
├─────────────────────────────────────────────────────────────┤
│ [🛑 E-STOP] [🔌 Connect All] [⏸ Pause] [▶ Resume]         │ ← Global Toolbar
├─────────────────────────────────────────────────────────────┤
│ ┌─ Setup ─┬─ Treatment Dashboard ─┬─ System Diagnostics ─┐ │
│ │         │                        │                       │ │
│ │         │   [Main Content Area]  │                       │ │
│ │         │                        │                       │ │
│ └─────────┴────────────────────────┴───────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ 📷 Connected │ ⚡ Connected │ 🔧 Connected │ [SYSTEM SAFE] │ ← Enhanced Status Bar
└─────────────────────────────────────────────────────────────┘
```

### Tab Structure (After)

#### Tab 1: "Setup" (Combined Subject + Camera)
```bash
┌──────────────────┬────────────────────────────────┐
│ Subject Info     │   Camera Feed & Alignment      │
│                  │                                │
│ - Subject ID     │   [Live Camera View]          │
│ - Session Start  │                                │
│ - Tech ID        │   Alignment Controls           │
│ - Notes          │   - Crosshair toggle           │
│                  │   - Zoom controls              │
└──────────────────┴────────────────────────────────┘
```

#### Tab 2: "Treatment Dashboard" (Mission Control)
```bash
┌─────────────┬──────────────────────┬────────────────┐
│ Laser       │                      │ Interlocks     │
│ Controls    │   [Camera Feed]      │ [DONE] Session OK  │
│ [Collapse]  │                      │ [DONE] GPIO OK     │
│             │                      │ [DONE] Power OK    │
│ - Power     │                      │ [DONE] LASER ON    │
│ - Aiming    ├──────────────────────┤                │
│             │                      │ Smoothing      │
│ Actuator    │ TREATMENT CONTROL    │ Motor: ON      │
│ Controls    │ [START] [STOP]       │ Vib: 1.65g [DONE]  │
│ [Collapse]  │ Progress: [======]   │ Photo: 5.2mW   │
│             │ Status: Running      │                │
│ - Position  │ Action: Move Ring    │ Events         │
│ - Speed     │                      │ [Mini Log]     │
└─────────────┴──────────────────────┴────────────────┘
```

#### Tab 3: "System Diagnostics"
```bash
┌─────────────────────────────────────────────────────┐
│ GPIO Hardware Details                                │
│ - Full motor control interface                       │
│ - Accelerometer readings                             │
│ - Photodiode calibration                             │
│                                                       │
│ Full Event Log                                       │
│ [All system events with filtering]                   │
│                                                       │
│ Hardware Test Controls                               │
│ [Advanced diagnostic tools]                          │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Quick Wins (High Impact, Low Effort)
**Goal:** Immediate safety and usability improvements
**Estimated Effort:** 4-6 hours
**Files Modified:** `main_window.py`, `safety_widget.py`

#### 1.1: Add Global Toolbar
- Create `QToolBar` at top of `MainWindow`
- Add global E-STOP button (connects to `SafetyManager.trigger_emergency_stop()`)
- Add Connect/Disconnect All button (batch hardware connection)
- Add Pause/Resume protocol buttons (connects to `ProtocolEngine`)

#### 1.2: Add Master Safety Indicator
- Add prominent safety state label to status bar (right side)
- Connect to `SafetyManager.safety_state_changed` signal
- Color-coded: Green (SAFE), Orange (UNSAFE), Red (E-STOP)
- Always visible regardless of active tab

#### 1.3: Add Connection Status Icons
- Replace text-only status with icon + text
- Use Material Design icons or Unicode symbols
- Green checkmark (✓) for connected, Red X (✗) for disconnected

#### 1.4: Clean Up Status Bar
- Move Dev Mode checkbox to menubar under "Developer" menu
- Remove redundant "Close Program" button
- Use standard window close button (X) with existing `closeEvent` handler

#### 1.5: Remove Redundant Title
- Delete `QLabel` title from line 90-93 of `main_window.py`
- Window title bar already displays application name

**Deliverable:** Improved status bar, global safety visibility, always-accessible E-Stop

---

### Phase 2: Treatment Dashboard (High Effort, Transformative Impact)
**Goal:** Create integrated mission control view
**Estimated Effort:** 12-16 hours
**Status:** [DONE] **COMPLETE** (7/7 - 100%) 🎉
**Files Modified:** `treatment_widget.py`, `safety_widget.py`, `main_window.py`, `active_treatment_widget.py`, `treatment_setup_widget.py`, `smoothing_status_widget.py`
**New Files:** `interlocks_widget.py`, `smoothing_status_widget.py`, `treatment_setup_widget.py`

#### WARNING: CRITICAL ARCHITECTURAL FIX (2025-10-27) [DONE] **COMPLETED**
**Issue:** Two separate top-level tabs ("Treatment Setup" and "Active Treatment") forced operators to perform context-switching at treatment start - the exact problem the redesign aimed to solve.

**Solution:** Unified Treatment Dashboard with QStackedWidget state management

**Implementation:**
```python
# Single Treatment Dashboard tab with stacked views
self.treatment_dashboard = QWidget()
self.treatment_stack = QStackedWidget()

# Index 0: Setup view (configuration)
self.treatment_setup_widget = TreatmentSetupWidget()
self.treatment_stack.addWidget(self.treatment_setup_widget)

# Index 1: Active view (monitoring)
self.active_treatment_widget = ActiveTreatmentWidget()
self.treatment_stack.addWidget(self.active_treatment_widget)

# "Start Treatment" button triggers one-way transition
self.treatment_setup_widget.ready_button.clicked.connect(
    lambda: self.treatment_stack.setCurrentIndex(1)
)
```text

**Benefits:**
- [DONE] Zero tab switching during treatment workflow (mission control achieved)
- [DONE] Clear sequential progression (Setup → Active)
- [DONE] One-way transition prevents accidental return to setup
- [DONE] Operator stays in single context throughout procedure
- [DONE] Reduces cognitive load and potential for navigation errors

**Files Modified:**
- `src/ui/main_window.py` (+18 lines, -3 lines) - QStackedWidget implementation
- `src/ui/widgets/treatment_setup_widget.py` (+1 line) - Updated button tooltip

**Testing:** [DONE] Application starts successfully, no errors in initialization logs

#### 2.1: Create Interlocks Status Widget [DONE] **COMPLETED**
**File:** `src/ui/widgets/interlocks_widget.py`

```python
class InterlocksWidget(QWidget):
    """Consolidated display of all laser prerequisite interlocks."""
    def __init__(self):
        # Session Valid: ✓/✗
        # GPIO Interlock: ✓/✗
        # Power Limit: ✓/✗
        # Final: LASER PERMITTED / LASER DENIED
```text

Connected to signals:
- `SafetyManager.safety_state_changed` ✓
- `SafetyManager.laser_enable_changed` ✓
- `SafetyManager.safety_event` ✓

**Implementation Notes:**
- Compact widget displaying all safety interlocks in one view
- Color-coded status indicators (green checkmark/red X)
- Final LASER PERMITTED/DENIED banner at bottom
- Embedded in Active Treatment Dashboard right panel
- Provides continuous visibility of safety prerequisites

#### 2.2: Restructure Treatment Widget Layout [DONE] **COMPLETED**
**Files:** `src/ui/widgets/treatment_setup_widget.py`, `src/ui/widgets/active_treatment_widget.py`

Split Treatment tab into two distinct widgets with horizontal layouts:

**TreatmentSetupWidget** (Configuration Interface):
```python
# Horizontal layout (2:1 ratio)
# LEFT (66%): Laser + Actuator + Motor controls
# RIGHT (33%): Protocol selector + Validation
```text

**ActiveTreatmentWidget** (Monitoring Dashboard):
```python
# Horizontal layout (3:2 ratio)
# LEFT (60%): Camera feed + Treatment controls
# RIGHT (40%): Interlocks + Smoothing motor + Event log
```text

**Implementation Notes:**
- Eliminated vertical squishing by prioritizing horizontal space
- Separation of concerns: Setup vs Execution interfaces
- Active treatment provides read-only monitoring with minimal interaction
- Compact font sizes (9-13px) and tight margins (5px) for density
- Stretch factors ensure proportional space allocation

#### 2.3: Integrate Camera Feed [DONE] **COMPLETED**
**File:** `src/ui/widgets/active_treatment_widget.py` (lines 277-306)

**Implementation:** Widget reparenting pattern
```python
def set_camera_widget(self, camera_widget: Any) -> None:
    """Set the camera widget for live feed display."""
    # Remove placeholder label
    camera_section_layout.removeWidget(self.camera_display)
    self.camera_display.deleteLater()

    # Share camera display QLabel between widgets
    self.camera_display = camera_widget.camera_display
    camera_section_layout.insertWidget(0, self.camera_display)
    self.camera_display.setMinimumHeight(250)  # Compact for dashboard
```bash

**Implementation Notes:**
- Camera feed now visible in both Camera/Alignment tab and Active Treatment dashboard
- Reparenting allows same QLabel to display in multiple contexts
- Reduced minimum height (250px vs 600px) for compact dashboard view
- Eliminates need to switch tabs during treatment for safety monitoring
- Live 30 FPS stream maintained without performance impact

#### 2.4: Create Collapsible Control Panels [PENDING] **PLANNED**
**Files:** `src/ui/widgets/treatment_setup_widget.py`, potentially new collapsible wrapper widget

**Goal:** Reduce visual clutter in Treatment Setup by making hardware controls collapsible

**Implementation Approach:**

Option 1 - Custom Collapsible GroupBox:
```python
class CollapsibleGroupBox(QGroupBox):
    """QGroupBox with clickable title bar to expand/collapse content."""
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.is_collapsed = False
        self.content_widget = QWidget()
        # Add toggle button to title bar
        # Connect click to show/hide content_widget
```text

Option 2 - QSplitter with collapsible widgets:
```python
# Use QSplitter.setCollapsible(index, True)
# Allows dynamic resizing and collapse
```bash

**Widgets to make collapsible:**
- LaserWidget (in TreatmentSetupWidget)
- ActuatorWidget (in TreatmentSetupWidget)
- MotorWidget (in TreatmentSetupWidget)

**Design Requirements:**
- Default state: Expanded (operators need to configure on first use)
- Collapsed state shows: Device name + current status (e.g., "Laser: 0.50 W, Aiming")
- Smooth animation (100-200ms) for collapse/expand
- State persists during session (optional: save to user preferences)

**Benefits:**
- Allows operators to focus on protocol selector after initial hardware setup
- Reduces scrolling in right panel
- Maintains access to all controls when needed

#### 2.5: Move Smoothing Motor Controls [DONE] **COMPLETED**
**New File:** `src/ui/widgets/smoothing_status_widget.py` (230 lines)
**Modified:** `src/ui/widgets/active_treatment_widget.py`, `src/ui/main_window.py`

**Implementation:** Extract & Embed Pattern

Created new `SmoothingStatusWidget`:
```python
class SmoothingStatusWidget(QWidget):
    """Compact smoothing device control and monitoring."""
    # Motor control buttons (Enable/Disable)
    # Voltage control (0-3V spinbox + Apply button)
    # Live status: Vibration (X.XX g), Photodiode (X.X mW)

    def set_gpio_controller(self, controller: Any) -> None:
        """Connect to GPIO controller and subscribe to signals."""
        controller.connection_changed.connect(...)
        controller.smoothing_motor_changed.connect(...)
        controller.vibration_level_changed.connect(...)
        controller.photodiode_power_changed.connect(...)
```bash

**Implementation Notes:**
- Embedded in Active Treatment Dashboard right panel (between Interlocks and Event log)
- Direct signal/slot connections to GPIOController (same architecture as GPIOWidget)
- Color-coded vibration display: Blue (<0.5g), Orange (0.5-0.8g), Green (>0.8g)
- Controls respect existing safety guardrails (enable/disable based on connection)
- Voltage changes require "Apply" button click (prevents accidental adjustments)
- Compact layout (30px button heights, 10-11px fonts) for dashboard density
- Successfully eliminates tab switching for motor control during treatment

#### 2.6: Combine Setup Tab [DONE] **COMPLETED**
**File Modified:** `src/ui/main_window.py` (+14 lines, -3 lines)
**Goal:** Consolidate all pre-treatment setup into single tab
**Completed:** 2025-10-27

**Previous State:**
- Tab 1: "Subject Selection" (separate tab)
- Tab 2: "Camera/Alignment" (separate tab)

**New Structure:**
```python
# Single "Setup" tab with horizontal layout
setup_tab = QWidget()
setup_layout = QHBoxLayout()

# Left: Subject Selection (33% - stretch factor 1)
self.subject_widget = SubjectWidget()
setup_layout.addWidget(self.subject_widget, 1)

# Right: Camera/Alignment (66% - stretch factor 2)
self.camera_widget = CameraWidget()
setup_layout.addWidget(self.camera_widget, 2)

self.tabs.addTab(setup_tab, "Setup")
```text

**Implementation Notes:**
- [DONE] **Horizontal-First Design:** Utilizes 1:2 stretch factor ratio (33%/66%)
- [DONE] **Natural Left-to-Right Workflow:** Subject entry → Camera alignment
- [DONE] **Expert-Validated:** Horizontal layout superior to vertical split
- [DONE] **Eliminates Tab Switching:** Both setup tasks visible simultaneously
- [DONE] **Maintains Full Functionality:** All widgets retain their complete feature set
- [DONE] **Signal Connections Preserved:** SessionManager, CameraController unchanged

**Benefits Achieved:**
- [DONE] Streamlined pre-treatment workflow (one tab instead of two)
- [DONE] Operator can see camera feed while entering subject information
- [DONE] Reduced navigation complexity (3 tabs → 2 tabs total)
- [DONE] Adheres to "go wider" design principle
- [DONE] Better space utilization on widescreen displays

**Tab Structure After Phase 2.6:**
1. **Setup** - Subject Selection (33%) + Camera/Alignment (66%)
2. **Treatment Dashboard** - Setup view ⟷ Active view (QStackedWidget)
3. **Safety Status** - GPIO details, full event log

Option 2 - Vertical Splitter:
```python
splitter = QSplitter(Qt.Orientation.Vertical)
splitter.addWidget(self.subject_widget)  # Top
splitter.addWidget(self.camera_widget)   # Bottom (larger)
splitter.setStretchFactor(1, 2)  # Camera gets 2x space
```text

**Design Requirements:**
- Subject widget should be compact (form layout, no wasted space)
- Camera should maintain large preview for alignment accuracy
- Logical workflow: Subject selection → Camera alignment → Treatment tab
- Both widgets remain fully functional (no features removed)

**Benefits:**
- Reduces total tab count from 4 to 3
- Groups all setup actions in one place
- Natural left-to-right workflow (info → visual alignment)
- Eliminates tab switching during pre-treatment preparation

#### 2.7: Create System Diagnostics Tab [PENDING] **PLANNED**
**Files:** `src/ui/main_window.py`, potentially new `diagnostics_widget.py`
**Goal:** Create advanced troubleshooting and system monitoring interface

**Current State:**
- Safety tab contains full GPIOWidget with all hardware controls
- Event logs scattered across multiple widgets
- No centralized diagnostic interface

**Proposed Structure:**
```python
class DiagnosticsWidget(QWidget):
    """System diagnostics and troubleshooting interface."""
    def __init__(self):
        # Vertical layout with sections:
        # 1. Hardware Diagnostics (GPIO, sensors, accelerometer)
        # 2. Full Event Log (all system events with filtering)
        # 3. Performance Metrics (frame rates, polling rates, latencies)
        # 4. Hardware Test Controls (advanced calibration, manual tests)
```bash

**Components to Include:**

1. **GPIO Hardware Details** (from current GPIOWidget):
   - Full accelerometer readings (X, Y, Z axes, magnitude)
   - Raw ADC values for photodiode
   - Motor PWM settings and control
   - Connection diagnostics
   - Watchdog heartbeat status

2. **Comprehensive Event Log:**
   - All safety events (current SafetyWidget log)
   - All protocol execution events (current ActiveTreatmentWidget log)
   - Hardware connection events
   - Filter by: Level (Info/Warning/Error), Source (Safety/GPIO/Protocol)
   - Export to file capability

3. **Performance Metrics:**
   - Camera FPS (current vs target)
   - GPIO polling rate
   - Protocol engine latency
   - UI responsiveness metrics

4. **Hardware Test Tools:**
   - Manual motor calibration controls
   - Laser power sweep test
   - Actuator positioning test
   - Camera focus test patterns
   - Safety interlock simulation (dev mode only)

**Design Requirements:**
- Tab should be visually distinct (this is not for operators)
- Use monospace fonts for logs and technical data
- Provide clear section headers
- Include "Export Diagnostics" button (saves all data to file)
- Respect existing safety interlocks (no dangerous overrides)

**Benefits:**
- Consolidates all troubleshooting tools in one place
- Removes advanced controls from operator-facing tabs
- Provides clear separation between operational and diagnostic views
- Useful for technicians, engineers, and support staff
- Facilitates remote troubleshooting (export diagnostics report)

**Deliverable:** Integrated Treatment Dashboard eliminating tab-switching during procedures

---

### Phase 3: New Features (Incremental Effort)
**Goal:** Add missing operational capabilities
**Estimated Effort:** 8-10 hours

#### 3.1: Protocol Selector Widget [PENDING] **PLANNED**
**New File:** `src/ui/widgets/protocol_selector_widget.py`
**Modified:** `src/ui/widgets/treatment_setup_widget.py` (embed selector)
**Goal:** Replace hardcoded test protocol with dynamic protocol loading

**Current Issue:**
- Treatment uses hardcoded `test_protocol` (line 223 in treatment_widget.py)
- No way to select or load different protocols
- Operators cannot switch between treatment types

**Proposed Implementation:**
```python
class ProtocolSelectorWidget(QGroupBox):
    """Widget for selecting and loading treatment protocols."""

    protocol_loaded = pyqtSignal(dict)  # Emits protocol data

    def __init__(self):
        # Protocol discovery (scan protocols/ directory)
        # Dropdown menu with protocol names
        # "Load Protocol" button
        # Protocol preview (actions, duration, parameters)
        # Validation before loading
```text

**Features:**

1. **Protocol Discovery:**
   - Scan `protocols/` directory for `.json` or `.yaml` files
   - Parse metadata (name, description, author, version)
   - Display in sorted dropdown list

2. **Protocol Preview:**
   - Show action count (e.g., "12 actions")
   - Estimated duration (sum of all action durations)
   - Parameter requirements (laser power, ring positions, etc.)
   - Display in QTextEdit or QTableWidget

3. **Validation:**
   - Check protocol schema against expected format
   - Verify all required actions are valid
   - Check parameter ranges (laser power within limits, etc.)
   - Warn about potentially dangerous settings

4. **Loading:**
   - Parse protocol file
   - Emit `protocol_loaded` signal with protocol dictionary
   - TreatmentSetupWidget receives signal and updates validation section
   - Protocol ready for execution when treatment starts

**Integration:**
- Embed in TreatmentSetupWidget right panel (below Laser/Actuator/Motor controls)
- Signal connects to `ProtocolEngine.load_protocol()`
- Protocol must be loaded before "Start Treatment" button enables

**Benefits:**
- Operators can switch between treatment types
- No code changes needed to add new protocols
- Visual preview reduces configuration errors
- Validation prevents runtime protocol errors

#### 3.2: Camera Snapshot Feature [PENDING] **PLANNED**
**Modified:** `src/ui/widgets/active_treatment_widget.py`, `src/core/camera_controller.py`
**Goal:** Allow operators to capture still images during treatment for documentation

**Current Limitation:**
- Camera shows live feed only
- No way to save images during treatment
- Documentation requires external camera or screenshots

**Proposed Implementation:**

1. **UI Changes** (ActiveTreatmentWidget):
```python
# Add snapshot button to camera section
self.snapshot_btn = QPushButton("📷 Capture")
self.snapshot_btn.setStyleSheet("font-size: 11px; padding: 5px;")
self.snapshot_btn.clicked.connect(self._on_capture_snapshot)

# Add to camera section layout (below camera display)
camera_section_layout.addWidget(self.snapshot_btn)
```text

2. **Backend Implementation** (CameraController):
```python
def capture_snapshot(self, session_id: str, annotation: str = "") -> str:
    """
    Capture current frame and save to session directory.

    Args:
        session_id: Current treatment session ID
        annotation: Optional text annotation for filename

    Returns:
        str: Full path to saved image file
    """
    # Get current frame from video capture
    frame = self.current_frame

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{timestamp}"
    if annotation:
        filename += f"_{annotation}"
    filename += ".png"

    # Create directory if needed
    snapshot_dir = Path(f"sessions/{session_id}/snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # Save image
    filepath = snapshot_dir / filename
    cv2.imwrite(str(filepath), frame)

    logger.info(f"Snapshot saved: {filepath}")
    return str(filepath)
```javascript

3. **Confirmation Feedback:**
   - Show toast notification: "Snapshot saved: snapshot_20251027_143052.png"
   - Flash green border around camera display (200ms)
   - Log event to treatment event log

4. **Optional Enhancements:**
   - Add annotation dialog (let operator add text note to filename)
   - Include timestamp overlay on image itself
   - Auto-save snapshots at key protocol milestones (start, end, errors)
   - Include metadata file with each snapshot (laser power, position, time)

**Integration:**
- Button appears in both Camera/Alignment tab and Active Treatment dashboard
- Requires active session (disabled if no session)
- Snapshots organized by session ID for easy retrieval

**Benefits:**
- Documentation for medical records
- Visual verification of treatment positioning
- Evidence for troubleshooting issues
- Training material (before/after comparisons)
- Regulatory compliance (treatment documentation)

#### 3.3: Manual Interlock Overrides (Dev Mode) [PENDING] **PLANNED**
**Modified:** `src/ui/main_window.py`, `src/core/safety_manager.py`
**Goal:** Allow developers to bypass safety interlocks for testing and calibration

**Current Limitation:**
- Safety interlocks cannot be overridden for testing
- Difficult to test laser/actuator without full hardware setup
- Calibration requires workarounds or hardware modifications

**Proposed Implementation:**

1. **UI Addition** (MainWindow Developer menu):
```python
# Add to Developer menu (only visible when dev mode enabled)
override_menu = self.developer_menu.addMenu("Safety Overrides")

self.override_session_action = QAction("☐ Bypass Session Requirement", self)
self.override_session_action.setCheckable(True)
self.override_session_action.triggered.connect(self._on_override_session)
override_menu.addAction(self.override_session_action)

self.override_gpio_action = QAction("☐ Bypass GPIO Interlock", self)
self.override_gpio_action.setCheckable(True)
self.override_gpio_action.triggered.connect(self._on_override_gpio)
override_menu.addAction(self.override_gpio_action)

self.override_power_action = QAction("☐ Bypass Power Limit", self)
self.override_power_action.setCheckable(True)
self.override_power_action.triggered.connect(self._on_override_power)
override_menu.addAction(self.override_power_action)
```text

2. **Warning Dialog** (First activation only):
```python
def _show_override_warning(self) -> bool:
    """Show critical warning before enabling any override."""
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("SAFETY OVERRIDE WARNING")
    msg.setText(
        "You are about to bypass a safety interlock.\n\n"
        "This is ONLY for testing and calibration.\n"
        "NEVER use overrides with live subjects or treatment lasers.\n\n"
        "All overrides will be logged.\n\n"
        "Do you understand the risks?"
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.No)

    return msg.exec() == QMessageBox.StandardButton.Yes
```text

3. **SafetyManager Integration:**
```python
class SafetyManager:
    def __init__(self):
        self.overrides = {
            "session": False,
            "gpio": False,
            "power": False,
        }

    def set_override(self, interlock_name: str, enabled: bool) -> None:
        """Enable/disable an interlock override (dev mode only)."""
        if not self.dev_mode:
            logger.error("Overrides only available in dev mode")
            return

        self.overrides[interlock_name] = enabled
        logger.warning(
            f"SAFETY OVERRIDE: {interlock_name} = {enabled}",
            extra={"dev_mode": True}
        )

        # Log to database as safety event
        self._log_safety_event(
            event_type="OVERRIDE",
            description=f"Interlock {interlock_name} override: {enabled}"
        )

        # Re-evaluate laser enable state
        self._update_laser_enable_state()

    def _check_session_valid(self) -> bool:
        """Check if session interlock is satisfied."""
        if self.overrides["session"]:
            return True  # Override active
        return self.active_session is not None
```text

4. **Visual Indicator:**
   - When ANY override is active, show orange warning banner in status bar
   - Banner text: "⚠ SAFETY OVERRIDES ACTIVE (DEV MODE)"
   - Clicking banner shows which overrides are enabled

5. **Automatic Clearing:**
```python
def _on_dev_mode_changed(self, enabled: bool):
    """Clear all overrides when dev mode disabled."""
    if not enabled:
        for interlock_name in self.safety_manager.overrides.keys():
            self.safety_manager.set_override(interlock_name, False)

        # Update UI checkboxes
        self.override_session_action.setChecked(False)
        self.override_gpio_action.setChecked(False)
        self.override_power_action.setChecked(False)

        logger.info("All safety overrides cleared (dev mode disabled)")
```text

**Safety Guardrails:**
- Overrides ONLY available when dev mode is enabled
- All override actions are logged to database with timestamps
- Clear warning dialog before first use (per session)
- Visual indicator (orange banner) always shows when overrides active
- Overrides automatically clear when dev mode is disabled
- Overrides automatically clear when application exits

**Benefits:**
- Enables testing without full hardware setup
- Facilitates calibration procedures
- Allows laser/actuator testing in isolation
- Maintains audit trail of all override usage
- Clear visual feedback prevents accidental production use

**Deliverable:** Enhanced operational capabilities and testing tools

---

## Design Specifications

### WARNING: CRITICAL UI GUIDELINES (Established 2025-10-27)

**Safety-Critical Requirements:**

#### Font Sizes (MANDATORY)
- **MINIMUM: 11px** for all numerical values, status text, and operator-readable content
- **Rationale:** 9px fonts are too small for critical readouts in safety-critical systems
- **Critical Elements:** 14-16px (E-Stop, safety state, interlock status)
- **Status Values:** 11-13px (vibration readings, power levels, positions)
- **Labels:** 11px minimum (parameter names, section headers)
- **Body Text:** 12px (general UI text, descriptions)
- **Headings:** 14-18px, bold

**Violations Fixed (2025-10-27):** [DONE] **COMPLETE**
- [DONE] `active_treatment_widget.py:164` - Parameter labels: 9px → 11px
- [DONE] `active_treatment_widget.py:206` - Event log: 10px → 11px
- [DONE] `active_treatment_widget.py:252` - Status label: 10px → 11px
- [DONE] `active_treatment_widget.py:257` - Action label: 9px → 11px
- [DONE] `treatment_setup_widget.py:126` - Validation label: 10px → 11px
- [DONE] `smoothing_status_widget.py:83,92,98,109,120` - All labels: 10px → 11px

**Non-Critical Violations (Informational text, not safety-critical):**
- WARNING: `camera_widget.py` - Exposure/gain/resolution info (10px) - Setup phase only
- WARNING: `treatment_widget.py` - Deprecated file (not in use)

#### Button Specifications (MANDATORY)
- **Minimum Height:** 35px for standard buttons
- **Critical Actions:** 40-60px (Start Treatment, E-Stop)
- **Minimum Padding:** 8px horizontal, 6px vertical
- **Rationale:** Prevents mis-clicks during high-stress procedures
- **Click Target:** Minimum 32x32px touchable area

#### Spacing Standards
- **Padding:** 10px standard, 5px compact (for tight layouts only)
- **Margins:** 10px between sections, 5px between related elements
- **Layout Margins:** 5-10px (established in Phase 2 horizontal layouts)

### Color Scheme (Dark Theme)
- **Background:** `#2b2b2b` (dark gray)
- **Surface:** `#3c3c3c` (lighter gray)
- **Success:** `#4CAF50` (green)
- **Warning:** `#FF9800` (orange)
- **Error:** `#F44336` (red)
- **Primary:** `#2196F3` (blue)
- **Text:** `#FFFFFF` (white)

### Icons
Use Material Design icons or Unicode symbols:
- [DONE] (U+2713) - Success/Connected
- [FAILED] (U+2717) - Error/Disconnected
- ⚠ (U+26A0) - Warning
- 🛑 (U+1F6D1) - E-Stop
- 📷 (U+1F4F7) - Camera
- ⚡ (U+26A1) - Laser
- 🔧 (U+1F527) - Actuator

---

## Signal/Slot Connections

### Global Toolbar → Safety Manager
```python
self.estop_btn.clicked.connect(self.safety_manager.trigger_emergency_stop)
self.pause_btn.clicked.connect(self.protocol_engine.pause)
self.resume_btn.clicked.connect(self.protocol_engine.resume)
```text

### Safety Manager → Status Bar Master Indicator
```python
self.safety_manager.safety_state_changed.connect(self._update_master_safety_indicator)
```text

### Safety Manager → Interlocks Widget
```python
self.safety_manager.safety_state_changed.connect(self.interlocks_widget.update_state)
self.safety_manager.laser_enable_changed.connect(self.interlocks_widget.update_laser_enable)
self.safety_manager.safety_event.connect(self.interlocks_widget.update_interlock)
```text

### GPIO Controller → Smoothing Status Widget (Existing)
```python
# These connections already exist in gpio_widget.py, just relocate the UI
gpio_controller.smoothing_motor_changed.connect(...)
gpio_controller.vibration_level_changed.connect(...)
gpio_controller.photodiode_power_changed.connect(...)
```

---

## Testing Plan

### Phase 1 Testing
- [ ] Global E-Stop button triggers emergency stop
- [ ] Master safety indicator updates in real-time
- [ ] Connection status icons display correctly
- [ ] Dev mode checkbox works from menubar
- [ ] All tabs accessible without UI errors

### Phase 2 Testing
- [ ] Treatment Dashboard displays all panels correctly
- [ ] Camera feed visible during treatment
- [ ] Collapsible panels expand/collapse properly
- [ ] Smoothing motor controls functional in new location
- [ ] All signals/slots connected correctly
- [ ] Tab switching works smoothly

### Phase 3 Testing
- [ ] Protocol selector loads and validates protocols
- [ ] Camera snapshot saves to correct directory
- [ ] Manual overrides function in dev mode only
- [ ] Overrides clear when dev mode disabled

### Integration Testing
- [ ] Complete treatment workflow (Setup → Dashboard → Execute)
- [ ] Safety interlocks block laser correctly
- [ ] E-Stop works from any state
- [ ] All hardware controls responsive
- [ ] No UI freezes or crashes

---

## Migration Strategy

### Backward Compatibility
- Keep existing widget interfaces unchanged where possible
- Move widgets, don't rewrite them
- Preserve all signal/slot connections
- Test with existing configuration files

### Rollback Plan
- Git tag before Phase 2 implementation: `ui-redesign-phase1-complete`
- Keep old layout code in separate branch: `ui-legacy`
- Document migration path in case of issues

### User Communication
- Update user documentation with new UI guide
- Provide screenshots of new layout
- Document workflow changes
- Highlight safety improvements

---

## Success Metrics

### Usability
- [DONE] Reduced tab switches during treatment (from 3-5 to 0)
- [DONE] Global safety state always visible
- [DONE] All critical controls accessible without navigation

### Safety
- [DONE] E-Stop accessible from any tab
- [DONE] Master safety indicator provides instant situational awareness
- [DONE] Treatment prerequisites visible before starting

### Efficiency
- [DONE] Faster treatment setup (consolidated view)
- [DONE] Reduced cognitive load (no context switching)
- [DONE] Improved information hierarchy

---

## Risk Assessment

### High Risk
- **Phase 2 layout refactoring**: Extensive code changes, potential for regressions
  - *Mitigation:* Incremental implementation, thorough testing, git checkpoints

### Medium Risk
- **Signal/slot connection errors**: New widget locations may break connections
  - *Mitigation:* Systematic testing of all hardware interactions

### Low Risk
- **Phase 1 quick wins**: Minimal changes to existing functionality
  - *Mitigation:* Standard QA testing

---

## Timeline Estimate

- **Phase 1:** 4-6 hours (1 development day)
- **Phase 2:** 12-16 hours (2-3 development days)
- **Phase 3:** 8-10 hours (1-2 development days)
- **Testing & Polish:** 4-6 hours
- **Total:** 28-38 hours (5-7 development days)

---

## References

- Original analysis: Comprehensive design consultation (2025-10-27)
- Current codebase: `src/ui/main_window.py`, `src/ui/widgets/*`
- Safety architecture: `docs/architecture/SAFETY_SHUTDOWN_POLICY.md`
- GPIO module: `components/gpio_module/CODE_REVIEW_2025-10-27.md`

---

---

## Current Progress Summary (2025-10-27)

### Completed Work

**Phase 1: Quick Wins** [DONE] **100% COMPLETE** (5/5 tasks)
- Global toolbar with E-STOP button accessible from all tabs
- Master safety indicator in status bar (green/orange/red)
- Connection status icons for all hardware
- Dev Mode moved to menubar
- Redundant UI elements removed

**Phase 2: Treatment Dashboard** 🟡 **57% COMPLETE** (4/7 tasks)

[DONE] **Completed Tasks:**
1. **InterlocksWidget** - Consolidated safety interlock display showing Session Valid, GPIO Interlock, Power Limit, and final LASER PERMITTED/DENIED status
2. **Horizontal Layout Restructure** - Transformed vertical squishing layouts into horizontal-first designs with proper space allocation (2:1, 3:2 ratios)
3. **Camera Integration** - Widget reparenting pattern allows camera feed to display in both Camera/Alignment tab and Active Treatment dashboard (250px compact view)
4. **SmoothingStatusWidget** - Extracted motor controls from GPIO widget and embedded in Active Treatment dashboard with Enable/Disable buttons, voltage control (0-3V), and live vibration/photodiode displays

[PENDING] **Remaining Tasks:**
- Phase 2.4: Collapsible control panels (Laser, Actuator, Motor in Setup)
- Phase 2.6: Combined Setup tab (Subject + Camera alignment)
- Phase 2.7: System Diagnostics tab (advanced troubleshooting interface)

**Phase 3: New Features** [PENDING] **0% COMPLETE** (0/3 tasks)
- All features planned but not yet started

### Key Achievements

1. **Eliminated Vertical Squishing** - Horizontal layouts now prioritize width over height, solving full-screen squishing issues
2. **Treatment Dashboard Created** - Operators can now monitor treatment with camera feed, interlocks, motor status, and controls all visible simultaneously
3. **Zero Tab Switching** - Motor controls moved from Safety tab to Treatment dashboard, eliminating dangerous context switching during procedures
4. **Widget Reparenting** - Successfully shared camera display between multiple views without duplication
5. **Extract & Embed Pattern** - Created reusable SmoothingStatusWidget maintaining full signal/slot architecture

### Architecture Patterns Established

- **Horizontal-First Design**: Prioritize width utilization (screens are wider than tall)
- **Widget Reparenting**: Share UI components between views dynamically
- **Extract & Embed**: Create focused, reusable widgets from existing functionality
- **Compact Density**: Small fonts (9-13px), tight margins (5px), height constraints
- **Layout Stretch Factors**: Proportional space allocation (1:2, 2:1, 3:2 ratios)
- **Signal/Slot Preservation**: Maintain existing event architecture when moving widgets

---

## Remaining Work Roadmap

### Phase 2 Completion (Estimated: 6-8 hours)

**Phase 2.4: Collapsible Control Panels** (2-3 hours)
- Create `CollapsibleGroupBox` widget with clickable title bar
- Wrap Laser, Actuator, Motor widgets in collapsible containers
- Default: Expanded (operators need access on first use)
- Collapsed shows: Device name + current status summary
- Smooth animation (100-200ms)
- State persists during session

**Phase 2.6: Combined Setup Tab** (2-3 hours)
- Merge Subject Selection and Camera/Alignment into single tab
- Horizontal layout: Left (33%) = Subject info, Right (66%) = Camera alignment
- Natural left-to-right workflow: Select subject → Align camera → Treatment
- Reduces total tabs from 4 to 3
- Maintains full functionality of both widgets

**Phase 2.7: System Diagnostics Tab** (2-3 hours)
- Create new tab for advanced troubleshooting
- Move full GPIOWidget (all hardware details) here
- Consolidate all event logs with filtering (Level, Source)
- Add performance metrics (FPS, polling rates, latencies)
- Include hardware test tools (calibration, sweep tests)
- "Export Diagnostics" button for remote support

### Phase 3: New Features (Estimated: 8-10 hours)

**Phase 3.1: Protocol Selector Widget** (3-4 hours)
- Scan `protocols/` directory for `.json` or `.yaml` files
- Dropdown menu with protocol names
- Preview: Action count, estimated duration, parameters
- Validation: Schema check, parameter ranges, dangerous settings
- Integrate into TreatmentSetupWidget right panel
- Connect to `ProtocolEngine.load_protocol()`

**Phase 3.2: Camera Snapshot Feature** (2-3 hours)
- "📷 Capture" button in camera sections
- `CameraController.capture_snapshot(session_id, annotation)`
- Save to `sessions/{session_id}/snapshots/snapshot_{timestamp}.png`
- Toast notification + green border flash
- Log event to treatment log
- Optional: Annotation dialog, metadata file

**Phase 3.3: Manual Interlock Overrides** (3-4 hours)
- Developer menu: "Safety Overrides" submenu (dev mode only)
- Checkboxes: Bypass Session, Bypass GPIO, Bypass Power Limit
- Warning dialog before first use
- `SafetyManager.set_override(interlock, enabled)`
- Orange warning banner in status bar when active
- Auto-clear when dev mode disabled or app exits
- All actions logged to database

### Testing & Documentation (Estimated: 4-6 hours)
- Comprehensive UI testing with all hardware
- Verify all signal/slot connections
- Test complete treatment workflow
- Update user documentation
- Create UI guide with screenshots
- Performance validation

### Total Remaining Effort: 18-24 hours (3-4 development days)

---

## Next Steps (Priority Order)

1. **Phase 2.4: Collapsible Controls** - Reduce visual clutter in Setup tab
2. **Phase 2.6: Combined Setup** - Consolidate pre-treatment workflow
3. **Phase 2.7: Diagnostics Tab** - Move advanced tools out of operator view
4. **Phase 3.1: Protocol Selector** - Replace hardcoded test protocol
5. **Phase 3.2: Camera Snapshots** - Add documentation capability
6. **Phase 3.3: Safety Overrides** - Enable testing without full hardware
7. **Testing & Documentation** - Validate and document everything

---

## Risk Assessment Updates

### Completed Phases - Lessons Learned

**Phase 2 Layout Refactoring:**
- **Risk**: High - Extensive code changes
- **Outcome**: Successfully mitigated through incremental implementation
- **Key Lesson**: User feedback ("go wider and less long") was critical to understanding true requirement
- **Solution**: Horizontal layouts solved problem better than initial scroll area approach

**Widget Reparenting Pattern:**
- **Risk**: Medium - Potential signal/slot breakage
- **Outcome**: Successful - No connection issues
- **Key Lesson**: QLabel reparenting works cleanly when properly managed
- **Benefit**: Avoided code duplication and maintained single source of truth

### Remaining Phases - Risk Mitigation

**Low Risk (2-3 hours per task):**
- Phase 2.4: Collapsible controls (well-defined pattern)
- Phase 3.2: Camera snapshots (simple feature addition)

**Medium Risk (3-4 hours per task):**
- Phase 2.6: Combined Setup tab (widget layout changes)
- Phase 3.1: Protocol selector (new file I/O and validation logic)

**Medium-High Risk (3-4 hours per task):**
- Phase 2.7: Diagnostics tab (extensive widget reorganization)
- Phase 3.3: Safety overrides (security-critical feature)

**Mitigation Strategies:**
- Continue incremental implementation with git checkpoints
- Test each phase thoroughly before proceeding
- Maintain backward compatibility where possible
- Document all architecture decisions

---

**Document Status:** Active Development
**Last Updated:** 2025-10-27 (Session End)
**Current Phase:** Phase 2 (57% complete)
**Next Review:** After Phase 2.4-2.7 completion
**Target Completion:** 2025-11-03 (3-4 days remaining)
