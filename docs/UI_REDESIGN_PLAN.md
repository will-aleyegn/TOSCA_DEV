# TOSCA GUI UI/UX Redesign Plan

**Date:** 2025-10-27
**Status:** In Progress
**Goal:** Transform tab-based UI into integrated "Treatment Dashboard" for improved workflow efficiency and safety

---

## Executive Summary

The current TOSCA GUI uses a tab-based navigation pattern that causes information fragmentation and workflow disruption during treatment procedures. This redesign consolidates critical controls and status information into an integrated "Treatment Dashboard" that provides operators with continuous visibility of safety interlocks, sensor data, and treatment progress without requiring tab switching.

**Key Problems Solved:**
- ✅ Eliminates dangerous context-switching between Safety and Treatment tabs
- ✅ Provides continuous visibility of master safety state
- ✅ Consolidates smoothing motor controls with treatment workflow
- ✅ Creates single "mission control" view for procedure execution
- ✅ Improves information hierarchy and visual clarity

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

```
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
```
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
```
┌─────────────┬──────────────────────┬────────────────┐
│ Laser       │                      │ Interlocks     │
│ Controls    │   [Camera Feed]      │ ✅ Session OK  │
│ [Collapse]  │                      │ ✅ GPIO OK     │
│             │                      │ ✅ Power OK    │
│ - Power     │                      │ ✅ LASER ON    │
│ - Aiming    ├──────────────────────┤                │
│             │                      │ Smoothing      │
│ Actuator    │ TREATMENT CONTROL    │ Motor: ON      │
│ Controls    │ [START] [STOP]       │ Vib: 1.65g ✅  │
│ [Collapse]  │ Progress: [======]   │ Photo: 5.2mW   │
│             │ Status: Running      │                │
│ - Position  │ Action: Move Ring    │ Events         │
│ - Speed     │                      │ [Mini Log]     │
└─────────────┴──────────────────────┴────────────────┘
```

#### Tab 3: "System Diagnostics"
```
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
**Files Modified:** `treatment_widget.py`, `safety_widget.py`, `main_window.py`
**New Files:** `interlocks_widget.py`, `smoothing_status_widget.py`

#### 2.1: Create Interlocks Status Widget
**File:** `src/ui/widgets/interlocks_widget.py`

```python
class InterlocksWidget(QWidget):
    """Consolidated display of all laser prerequisite interlocks."""
    def __init__(self):
        # Session Valid: ✓/✗
        # GPIO Interlock: ✓/✗
        # Power Limit: ✓/✗
        # Final: LASER PERMITTED / LASER DENIED
```

Connect to signals:
- `SafetyManager.safety_state_changed`
- `SafetyManager.laser_enable_changed`
- `SafetyManager.safety_event`

#### 2.2: Restructure Treatment Widget Layout
**File:** `src/ui/widgets/treatment_widget.py`

Change from horizontal 3-column layout to integrated dashboard:
```python
# Current: QHBoxLayout (left, middle, right)
# New: QGridLayout or nested splitters
#   - Center: Camera feed (spans rows)
#   - Bottom: Treatment controls (full width)
#   - Left: Collapsible hardware controls
#   - Right: Interlocks + Smoothing + Mini event log
```

#### 2.3: Integrate Camera Feed
- Move `CameraWidget` from separate tab into Treatment Dashboard center panel
- Camera must be visible during treatment for safety monitoring
- Use `QSplitter` to allow size adjustment

#### 2.4: Create Collapsible Control Panels
- Wrap `LaserWidget` in collapsible `QGroupBox` with title bar button
- Wrap `ActuatorWidget` in collapsible `QGroupBox`
- Allows operators to tuck away detailed controls when not needed
- Default state: Collapsed (showing only summary info)

#### 2.5: Move Smoothing Motor Controls
**Source:** `gpio_widget.py` lines 111-155
**Destination:** Right panel of Treatment Dashboard

Move these controls:
- Motor Enable/Disable buttons
- Voltage spinbox + Apply button
- Keep connected to `GPIOController` via existing signals
- Display live readings: Vibration magnitude, Photodiode power

Create new `SmoothingStatusWidget`:
```python
class SmoothingStatusWidget(QWidget):
    """Compact smoothing device control and monitoring."""
    # Motor control buttons
    # Voltage control
    # Live status: Vibration (X.XX g), Photodiode (X.X mW)
```

#### 2.6: Combine Setup Tab
- Merge Subject Selection and Camera/Alignment into single "Setup" tab
- Use vertical `QSplitter`:
  - Top: `SubjectWidget` (compact view)
  - Bottom: `CameraWidget` (alignment mode)
- Workflow: Select subject → Align camera → Switch to Treatment Dashboard

#### 2.7: Create System Diagnostics Tab
- Move full `GPIOWidget` (all hardware details) here
- Move full event log viewer here
- Add any other diagnostic/troubleshooting tools
- This becomes the "advanced" view for engineers

**Deliverable:** Integrated Treatment Dashboard eliminating tab-switching during procedures

---

### Phase 3: New Features (Incremental Effort)
**Goal:** Add missing operational capabilities
**Estimated Effort:** 8-10 hours

#### 3.1: Protocol Selector Widget
**File:** `src/ui/widgets/protocol_selector_widget.py`

Replace hardcoded test protocol (`treatment_widget.py:223`) with:
- `QComboBox` showing available protocols from `protocols/` directory
- "Load Protocol" button to select `.json` or `.yaml` files
- Protocol preview showing actions and estimated duration
- Validation before loading

#### 3.2: Camera Snapshot Feature
Add to Treatment Dashboard camera panel:
- "📷 Snapshot" button next to camera feed
- Saves PNG to current session directory: `sessions/{session_id}/snapshots/`
- Auto-generates filename: `snapshot_{timestamp}.png`
- Shows confirmation toast/message

#### 3.3: Manual Interlock Overrides (Dev Mode)
Add to Developer menubar menu:
- "Override Software Interlocks" submenu (only enabled in dev mode)
- Checkboxes for each interlock:
  - ☐ Bypass Session Requirement
  - ☐ Bypass GPIO Interlock
  - ☐ Bypass Power Limit
- Clear warning dialog before enabling
- All overrides automatically clear when dev mode disabled

**Deliverable:** Enhanced operational capabilities and testing tools

---

## Design Specifications

### Color Scheme (Dark Theme)
- **Background:** `#2b2b2b` (dark gray)
- **Surface:** `#3c3c3c` (lighter gray)
- **Success:** `#4CAF50` (green)
- **Warning:** `#FF9800` (orange)
- **Error:** `#F44336` (red)
- **Primary:** `#2196F3` (blue)
- **Text:** `#FFFFFF` (white)

### Typography
- **Headings:** 14-18px, bold
- **Body:** 12px, regular
- **Status:** 14px, bold
- **Critical:** 16-24px, bold (E-Stop, safety indicators)

### Spacing
- **Padding:** 10px standard, 5px compact
- **Margins:** 10px between sections
- **Button heights:** 40px standard, 60-80px critical actions

### Icons
Use Material Design icons or Unicode symbols:
- ✓ (U+2713) - Success/Connected
- ✗ (U+2717) - Error/Disconnected
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
```

### Safety Manager → Status Bar Master Indicator
```python
self.safety_manager.safety_state_changed.connect(self._update_master_safety_indicator)
```

### Safety Manager → Interlocks Widget
```python
self.safety_manager.safety_state_changed.connect(self.interlocks_widget.update_state)
self.safety_manager.laser_enable_changed.connect(self.interlocks_widget.update_laser_enable)
self.safety_manager.safety_event.connect(self.interlocks_widget.update_interlock)
```

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
- ✓ Reduced tab switches during treatment (from 3-5 to 0)
- ✓ Global safety state always visible
- ✓ All critical controls accessible without navigation

### Safety
- ✓ E-Stop accessible from any tab
- ✓ Master safety indicator provides instant situational awareness
- ✓ Treatment prerequisites visible before starting

### Efficiency
- ✓ Faster treatment setup (consolidated view)
- ✓ Reduced cognitive load (no context switching)
- ✓ Improved information hierarchy

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

- Original analysis: Zen MCP gemini-2.5-pro consultation (2025-10-27)
- Current codebase: `src/ui/main_window.py`, `src/ui/widgets/*`
- Safety architecture: `docs/architecture/SAFETY_SHUTDOWN_POLICY.md`
- GPIO module: `components/gpio_module/CODE_REVIEW_2025-10-27.md`

---

**Document Status:** Active
**Last Updated:** 2025-10-27
**Next Review:** After Phase 2 completion
