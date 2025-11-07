# TOSCA Laser Control System - UI/UX Analysis Report

**Date:** 2025-11-05
**Version:** 0.9.12-alpha
**Analyst:** UI/UX Design Review
**Context:** Medical Device Software (Research Mode)

---

## Executive Summary

This report provides a comprehensive UI/UX analysis of the TOSCA laser control system, a medical device application for laser treatment control. The analysis evaluates the interface against medical device usability standards, safety-critical design requirements, and general UX best practices.

**Overall Grade: B+ (Good, with room for improvement)**

The system demonstrates strong safety-critical design patterns and logical information architecture. However, there are opportunities to improve visual hierarchy, reduce cognitive load, and enhance workflow efficiency.

---

## 1. Main Window Architecture Analysis

### 1.1 Overall Structure

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`

**Current Layout:**
- 3-tab interface: Hardware & Diagnostics, Treatment Workflow, Protocol Builder
- Global toolbar with safety controls
- Status bar with connection indicators and safety status
- Window size: 1200x900 (Lines 130)

**Strengths:**
1. **Logical separation of concerns** - Hardware setup, treatment execution, and protocol building are clearly separated
2. **Persistent safety controls** - E-Stop button always accessible in global toolbar
3. **Clear visual hierarchy** - Tabs organize complex functionality into digestible sections
4. **Dependency injection pattern** - Hardware controllers centrally managed (Lines 139-158)

**Weaknesses:**
1. **Tab names could be more user-centric**
   - Current: "Hardware & Diagnostics" (engineer-focused)
   - Better: "Setup & Connection" or "System Setup"

2. **No workflow guidance for new users**
   - Missing: Step indicators showing "Connect → Configure → Treat"
   - No visual cue for which tab to start with

3. **Window size may be too large for some displays**
   - Fixed 1200x900 may not fit laptop screens (common in clinical settings)
   - No minimum window size constraints

### 1.2 Toolbar Design

**Location:** Lines 521-593

**Current Toolbar:**
```
[EMERGENCY STOP] | [Connect All] [Disconnect All] | [Test All] | [Pause] [Resume]
```

**Strengths:**
1. **E-Stop prominence** - Red, large, always visible
2. **Bulk operations** - Connect/Disconnect All reduces clicks
3. **Visual separation** - Separators group related functions

**Weaknesses:**
1. **Button size inconsistency**
   - E-Stop: 40px height (good)
   - Other buttons: 35px height (less prominent than needed)

2. **Pause/Resume buttons disabled by default**
   - Takes up space when not in use
   - Could be hidden until protocol starts

3. **Color coding could be stronger**
   - "Connect All" uses blue (#1976D2) - good
   - "Test All" uses purple (#6A1B9A) - less intuitive
   - Suggest: Green for Connect, Red for Disconnect, Blue for Test

### 1.3 Status Bar Design

**Location:** Lines 595-661

**Current Indicators:**
```
[RESEARCH MODE WARNING] | [CAM] Camera [X] | [LSR] Laser [X] | [ACT] Actuator [X] | [SYSTEM SAFE]
```

**Strengths:**
1. **Research mode warning highly visible** - Red background, bold text (Lines 605-614)
2. **Master safety indicator** - Always visible, color-coded (Lines 638-647)
3. **Connection status at a glance** - All critical hardware visible

**Weaknesses:**
1. **Information density too high**
   - 4-5 elements in status bar feels cluttered
   - Text labels may be too verbose for limited space

2. **Inconsistent formatting**
   - Uses bracketed prefixes [CAM], [LSR], [ACT]
   - Could use icons instead for space efficiency

3. **Missing critical info**
   - No session status (which subject, which technician)
   - No active protocol name when running

**Recommendation:**
```
[RESEARCH MODE] | [Camera icon] [Laser icon] [Actuator icon] | Session: P-2025-0001 | [SYSTEM SAFE]
```

---

## 2. Tab-by-Tab Widget Analysis

### 2.1 Tab 1: Hardware & Diagnostics

**Layout:** 2-column split (50% controls | 50% diagnostics) with independent scrolling

**Left Column Widgets:**
- Camera System (CameraHardwarePanel)
- Linear Actuator (ActuatorConnectionWidget)
- Laser Systems (LaserWidget, TECWidget)

**Right Column Widgets:**
- GPIO Diagnostics (SafetyWidget)
- System Configuration (ConfigDisplayWidget)

**Strengths:**
1. **Collapsible section headers** - Color-coded by system (Lines 263-805)
   - Blue for camera, green for actuator, yellow for laser - excellent visual coding
2. **Independent scrolling** - Prevents one column from blocking the other
3. **Hardware grouped by function** - Logical organization

**Weaknesses:**
1. **50/50 split may not be optimal**
   - Left column (controls) often has less content than right (diagnostics)
   - Suggest 40/60 split to give diagnostics more space

2. **Too many sub-sections**
   - Camera, Actuator, Laser Driver, TEC, GPIO, Config = 6 sections
   - Users may scroll past important info
   - Consider collapsible accordions instead of static groups

3. **No quick status overview**
   - Users must scroll through all sections to see connection status
   - Suggest: Connection summary panel at top

### 2.2 Tab 2: Treatment Workflow

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/subject_widget.py`

**Layout:** 2-column split (40% controls | 60% camera)

**Left Column:**
- Subject selection (SubjectWidget)
- Treatment setup/active stack (TreatmentSetupWidget / ActiveTreatmentWidget)

**Right Column:**
- Camera live feed (CameraWidget)

**Strengths:**
1. **Camera prominence** - 60% width ensures clear visualization
2. **Stacked widget pattern** - Setup transitions to Active view (Lines 379-391)
3. **Subject ID auto-prefixing** - Reduces data entry errors (Lines 80-82)
4. **Technician dropdown** - Forces selection, prevents typos (Lines 125-134)

**Weaknesses:**
1. **Subject search workflow confusing**
   - User enters "last 4 digits" but field shows "P-2025-" prefix
   - Input field only 80px wide (Line 91) - hard to click
   - Better: Show full format "P-2025-____" with underscores

2. **Technician selection timing unclear**
   - Required for subject creation but not shown until session start
   - Should be at top of workflow

3. **Start Session button state unclear**
   - Says "Start Session" but also says "Ready" in tooltip
   - Button appears both in SubjectWidget and TreatmentSetupWidget
   - Suggest: Single "Begin Treatment" button after all checks pass

**Subject Widget Deep Dive:**

**Search/Create Pattern (Lines 175-309):**
```python
[Subject ID:] P-2025-[____]
[Search Subject] [Create New Subject] [View Sessions]
```

**Issues:**
1. **Three buttons of equal visual weight**
   - Primary action (Search) not distinguished from secondary (Create/View)
   - Suggest: Make "Search" primary button (blue), others secondary (gray)

2. **Subject info display**
   - Uses QTextEdit (read-only) for simple key-value display (Lines 109-113)
   - Could be cleaner as QLabel or QFormLayout
   - Current: Multi-line text blob
   - Better: Structured layout with labels

**Session Control Pattern (Lines 140-156):**
```
[Start Session] [End Session]
```

**Issues:**
1. **Buttons side-by-side with equal size**
   - "Start" (green) and "End" (red) same height/width
   - Risk: User might click wrong button in stress
   - Suggest: Different sizes - Start (large), End (smaller, requires confirmation)

### 2.3 Camera Widget Analysis

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py`

**Layout:** Horizontal split (75% display | 25% controls)

**Strengths:**
1. **Pre-configuration enabled** - Users can set exposure/gain before streaming (Lines 538-559)
2. **Hardware feedback loop** - UI updates reflect actual camera values (Lines 728-786)
3. **Exposure safety limiter** - Prevents frame drops with long exposures (Lines 621-641)
4. **Display scale options** - Performance optimization with visual trade-off info (Lines 366-383)

**Weaknesses:**
1. **Control panel too wide** - 350px max width (Line 152) takes significant horizontal space
   - Suggest: 280px max width

2. **Exposure warning implementation poor**
   - Uses emoji in production code (Line 1000: "ℹ️")
   - Warning label appears/disappears - causes layout shift
   - Better: Fixed-height warning area that changes color

3. **Developer mode controls confusing**
   - "Custom Save Path" groups hidden by default (Lines 400-476)
   - When visible, they interrupt capture/record flow
   - Suggest: Dev mode indicator at top, settings in separate dialog

4. **Image capture workflow inefficient**
   - User must type filename every time
   - Default "capture" becomes "capture_1", "capture_2" etc.
   - Better: Auto-increment counter visible, editable prefix

**Camera Settings Section:**

**Exposure Control (Lines 272-320):**
```
Exposure (µs):  [Auto]
[Allow Long Exposure checkbox]
[Slider 100-1000000]
Value: 10000 µs (10.0 ms) [Input box]
[Warning label - variable height]
```

**Issues:**
1. **Two input methods** - Slider AND text input box
   - Redundant - most users will use one or the other
   - Suggest: Keep slider, make input box "Advanced" only

2. **Long exposure checkbox placement**
   - Appears before slider, but affects slider behavior
   - Should be adjacent to slider as a lock/unlock toggle

3. **Warning text too verbose** (Line 989-991)
   - "WARNING: Exposure 50.0ms > 33ms frame period. Enable 'Allow Long Exposure' or reduce exposure."
   - Better: Icon + short message + "Details" link

### 2.4 Treatment Setup Widget

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/treatment_setup_widget.py`

**Layout:** Single column, max width 600px

**Strengths:**
1. **Clear instructions** - 3-step workflow displayed (Lines 75-82)
2. **Protocol-centric design** - Removed hardware controls to focus on treatment (Lines 52-53)
3. **Visual feedback** - Protocol info shows line count, duration (Lines 196-198)

**Weaknesses:**
1. **Ready Check section unclear** (Lines 120-152)
   - Shows checklist with "#" and "⚠" symbols
   - Hard-coded status text (Lines 127-132)
   - Not connected to actual hardware state
   - Suggest: Live status indicators connected to hardware

2. **Start Treatment button ambiguous**
   - Says "▶ Start Treatment" but just transitions view
   - Doesn't actually start treatment execution
   - Better: "Continue to Monitoring" or "Ready to Execute"

3. **No protocol validation feedback**
   - User loads protocol, but no indication if it's valid
   - Safety limits not shown until execution
   - Suggest: Validation panel showing limits compliance

### 2.5 Active Treatment Widget

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/active_treatment_widget.py`

**Layout:** Horizontal split (60% camera+controls | 40% safety panel)

**Strengths:**
1. **Read-only monitoring focus** - Minimal interactive controls (Line 45)
2. **Real-time parameter display** - Laser, position, vibration (Lines 111-119)
3. **Compact progress bar** - 20px height, clear percentage (Lines 198-218)
4. **Safety interlocks prominent** - Right panel dedicated to safety (Lines 149-186)

**Weaknesses:**
1. **Camera display placeholder** (Lines 95-106)
   - Shows "Camera Feed (Monitoring)" text by default
   - Should show actual feed from camera widget
   - Signal connection exists (Line 259) but may fail silently

2. **Status displays too small** (Lines 125-147)
   - 11px font for labels, 13px for values
   - Medical staff may have poor lighting conditions
   - Suggest: 12px labels, 16px values

3. **Stop button not prominent enough**
   - 45px height, 120px width (Lines 234-237)
   - Same size as regular buttons
   - Suggest: Match E-Stop size (60px height minimum)

4. **Event log limited** (Lines 169-177)
   - 200px max height in scrollable area
   - May not show enough history during long treatments
   - No export/save functionality

### 2.6 Safety Widget (System Diagnostics)

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/safety_widget.py`

**Layout:** Horizontal split (66% GPIO diagnostics | 33% software interlocks)

**Strengths:**
1. **Engineering-focused header** - Clear target audience (Lines 58-62)
2. **Separate E-Stop button** - 80px height, very prominent (Lines 98-102)
3. **Database event loading** - Allows review of historical events (Lines 295-341)

**Weaknesses:**
1. **Duplicate E-Stop buttons**
   - One in toolbar (40px), one here (80px)
   - Confusing which to use
   - Suggest: Remove from this tab, keep only in toolbar

2. **Status indicators use background color** (Lines 151-152)
   - Background: #f0f0f0 (light gray) - poor contrast
   - Text: Bold - but hard to read on light background
   - Suggest: Colored border or icon instead

3. **Event log styling inconsistent** (Lines 286-292)
   - Uses inline HTML for urgent events (`<span style="...">`)
   - Non-urgent events use plain text
   - Better: Use QTextEdit with rich text formatting consistently

---

## 3. UX Evaluation

### 3.1 Information Hierarchy

**Critical Information Visibility:**

| Information | Location | Visibility Score | Notes |
|-------------|----------|------------------|-------|
| Safety status | Status bar (bottom right) | 9/10 | Always visible, color-coded |
| E-Stop button | Toolbar (top left) | 10/10 | Large, red, prominent |
| Hardware connection | Status bar + tab headers | 7/10 | Small icons, text-heavy |
| Active session | Not visible | 0/10 | **CRITICAL ISSUE** |
| Current protocol | Not visible | 2/10 | Only in Setup widget |
| Treatment progress | Active widget only | 6/10 | Not visible in other tabs |

**Major Finding:** No persistent session indicator showing:
- Current subject ID
- Technician name
- Session start time
- Session duration

**Recommendation:** Add session panel to status bar or toolbar:
```
Session: P-2025-0001 | Tech: Will | Duration: 00:15:32 | [End Session]
```

### 3.2 Visual Affordances

**What's Clickable?**

**Good:**
- Buttons have clear hover states (Lines 531-533: color changes on hover)
- Disabled buttons grayed out consistently
- Sliders have clear grab handles

**Poor:**
- QLabel widgets used for status displays look like text (Lines 146-151)
  - Could add borders or background to show they're dynamic
- Checkboxes not always clear (Lines 100-104: no visual hierarchy)
- Some QGroupBox titles look like headers, not groupings

**Recommendation:**
- Add hover effects to all interactive elements
- Use icons for button functions where possible
- Add visual depth (subtle shadows) to interactive controls

### 3.3 Feedback Mechanisms

**Connection Feedback:**
- Green/red status labels (Line 896, 901)
- Status bar indicators update
- Header backgrounds change color (Lines 764-805)

**Good:** Multi-level feedback (widget, tab header, status bar)

**Error Feedback:**
- QMessageBox for critical errors (Lines 224-228)
- Status labels turn red (Line 932)
- Error logged to console

**Poor:** No persistent error panel. Errors may be missed if user not watching.

**Treatment Progress Feedback:**
- Progress bar (Lines 198-218)
- Status label updates (Line 222)
- Event log entries (Line 341)

**Good:** Multiple feedback channels

**Recommendation:**
- Add toast notifications for non-critical events
- Create persistent notifications panel for errors
- Add audio feedback for critical safety events (optional, configurable)

### 3.4 Safety-Critical Element Prominence

**Safety Elements Ranking:**

1. **Emergency Stop Button** - 10/10
   - 40px height, red background, always visible
   - Clear label, high contrast
   - Excellent

2. **Master Safety Indicator** - 9/10
   - Bottom right status bar
   - Large, color-coded (green/orange/red)
   - Good, but could be larger

3. **Research Mode Warning** - 8/10
   - Startup dialog (Lines 190-229)
   - Status bar watermark (Lines 605-614)
   - Good, but watermark could be more prominent

4. **Safety Interlock Status** - 6/10
   - Hidden in Active Treatment widget (right panel)
   - Only visible in Treatment tab
   - **ISSUE:** Not visible during hardware setup

5. **Power Limit Warning** - 4/10
   - Only in Safety Widget (not visible by default)
   - No visual indicator when limit approached
   - **ISSUE:** Should be always visible

**Recommendation:**
- Add safety sidebar always visible (like a dock)
- Show interlock status in all tabs, not just treatment
- Add power meter to toolbar showing current vs. limit

### 3.5 Workflow Efficiency

**Common Tasks Analysis:**

**Task 1: Connect to all hardware**

Current workflow:
1. Click "Hardware & Diagnostics" tab
2. Scroll to Camera section, click "Connect"
3. Scroll to Actuator section, click "Connect"
4. Scroll to Laser section, click "Connect"
5. Scroll to GPIO section, click "Connect"

**Clicks:** 5 | **Time:** ~30 seconds

Alternative (using toolbar):
1. Click "Connect All" button

**Clicks:** 1 | **Time:** ~5 seconds

**Grade:** A (toolbar optimization excellent)

**Task 2: Start new treatment session**

Current workflow:
1. Click "Treatment Workflow" tab
2. Enter subject last 4 digits (e.g., "0001")
3. Click "Search Subject"
4. Select technician from dropdown
5. Click "Start Session"
6. Load protocol (click "Load Protocol", browse, select)
7. Click "Start Treatment" button

**Clicks:** 7+ | **Time:** ~45-60 seconds

**Issues:**
- Technician selection should be earlier
- Protocol should be selected before subject (reusable protocols)
- No workflow guidance

**Recommendation:**
Wizard-style workflow:
```
Step 1: Select Technician → Step 2: Select Protocol → Step 3: Select Subject → Step 4: Begin
```

**Task 3: Adjust camera exposure during treatment**

Current workflow:
1. Stay in Treatment Workflow tab (camera visible)
2. Locate exposure slider in right panel (controls)
3. Drag slider OR enter value in text box
4. Observe feedback in camera feed

**Clicks:** 1 | **Time:** ~5 seconds

**Grade:** A (excellent real-time feedback)

**Task 4: Emergency stop**

Current workflow:
1. Click red "EMERGENCY STOP" button in toolbar
2. (System halts, laser disabled)

**Clicks:** 1 | **Time:** <1 second

**Grade:** A+ (optimal for safety-critical action)

### 3.6 Error Prevention Design Patterns

**Good Patterns:**

1. **Confirmation dialogs for destructive actions** (Lines 396-405)
   - End Session requires Yes/No confirmation
   - Good practice

2. **Disabled state for unsafe actions**
   - Start Session disabled until subject selected (Line 141)
   - Laser enable disabled unless safety checks pass (Lines 310-319)
   - Excellent

3. **Auto-prefixing for subject ID** (Lines 80-82)
   - Prevents format errors (P-YYYY-XXXX)
   - Reduces data entry errors

4. **Exposure safety limiter** (Lines 621-641)
   - Prevents long exposures without explicit permission
   - Requires checkbox to override
   - Excellent medical device pattern

**Missing Patterns:**

1. **No undo for subject creation**
   - Once created, can't be deleted from UI
   - Should add "Archive Subject" function

2. **No session timeout warning**
   - User might forget to end session
   - Recommend: Auto-warning after 4 hours of inactivity

3. **No protocol validation before execution**
   - User loads protocol, no safety check shown
   - Should validate against hardware capabilities

---

## 4. Medical Device Compliance Evaluation

### 4.1 Safety Warnings - FDA 21 CFR 820 Requirements

**Requirement:** Warnings must be clear, conspicuous, and require acknowledgment.

**Research Mode Warning Dialog:**

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/dialogs/research_mode_warning_dialog.py`

**Strengths:**
1. **Large warning icon** - 64x64 px standard warning icon (Lines 57-60)
2. **Bold, red title** - 18pt font, #D32F2F color (Line 64)
3. **Comprehensive warning text** - Lists all limitations (Lines 71-89)
4. **Explicit acknowledgment required** - Checkbox must be checked (Lines 100-105)
5. **Cannot bypass** - OK button disabled until acknowledged (Lines 118, 142)

**Grade: A+**

This is an excellent implementation of medical device warning standards.

**Recommendation:** None needed. This is production-ready.

### 4.2 Critical Information Always Visible

**FDA Expectation:** Safety-critical information must be persistently visible.

**Current Implementation:**

| Critical Info | Always Visible? | Location | Grade |
|---------------|-----------------|----------|-------|
| Safety state | Yes | Status bar | A |
| E-Stop button | Yes | Toolbar | A |
| Hardware status | Yes | Status bar | B |
| Active session | **No** | Only in Subject widget | **F** |
| Power limit | **No** | Only in Safety tab | **D** |
| Interlock status | **No** | Only in Active Treatment | **D** |

**Major Findings:**

1. **Active session info missing** - Users can't see subject/tech in other tabs
2. **Power limit not visible** - Critical safety parameter hidden
3. **Interlocks only in one tab** - Should be always visible

**Recommendation:**

Add persistent safety panel (docked on right or bottom):
```
┌─────────────────────────────┐
│ SAFETY STATUS               │
│ Session: P-2025-0001        │
│ Technician: Will            │
│ Power: 2.5W / 10.0W (25%)  │
│ Interlocks: ✓ All OK        │
│ State: SAFE                 │
└─────────────────────────────┘
```

### 4.3 Dangerous Operations Protected

**Required:** Laser enable must have multiple safeguards.

**Current Implementation (LaserWidget):**

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/laser_widget.py`

1. **Connection check** - Laser must be connected (Line 250)
2. **Safety manager check** - Interlocks must pass (Lines 310-317)
3. **Session validation** - Active session required (via safety manager)
4. **Separate enable button** - Not tied to power slider (Lines 174-179)

**Grade: A**

**Workflow:**
```
Connect → Set Power → Enable Output → (Safety checks) → Laser On
```

**Strengths:**
- Multi-step process prevents accidental enable
- Safety manager consulted before every enable
- Clear visual feedback (green/red buttons)

**Weaknesses:**
- No "Are you sure?" confirmation for first enable
- No countdown or "hold to confirm" pattern

**Recommendation:**
- Add confirmation dialog: "Enable laser at X.X watts? [Yes] [No]"
- Or use "hold for 2 seconds" pattern for Enable button

### 4.4 Clinical Environment Suitability

**Considerations:**
- Lighting conditions may vary
- Staff may wear gloves
- Stress during emergency situations
- Multiple operators (handoff scenarios)

**Current UI Evaluation:**

1. **Font sizes:**
   - Main UI: 10-14pt (good)
   - Status labels: 11-13pt (acceptable)
   - Small text: 10px (too small for some users)
   - **Grade: B**

2. **Button sizes:**
   - E-Stop: 40px height (good, but could be larger)
   - Primary actions: 35-50px (good)
   - Secondary actions: default (~25px) (acceptable)
   - **Grade: B+**

3. **Touch-friendly (if used on touchscreen):**
   - Slider knobs: Small, hard to grab with gloves
   - Spinboxes: Arrows too small for fat fingers
   - Buttons: Adequate size
   - **Grade: C**

4. **Color contrast:**
   - Red on white: Excellent
   - Green on white: Excellent
   - Gray on light gray: Poor (status indicators)
   - **Grade: B-**

**Recommendation:**
- Increase minimum font size to 11pt everywhere
- Add "Large UI Mode" option (1.5x scale)
- Make all interactive elements minimum 40x40px (touch-friendly)
- Improve contrast for disabled/inactive states

---

## 5. Accessibility Considerations

### 5.1 Color Blindness

**Current color usage:**
- Green: Safe, OK, Connected
- Red: Unsafe, Error, Disconnected, E-Stop
- Orange: Warning, Power limit
- Blue: Information, Primary actions
- Gray: Disabled, Inactive

**Issue:** Red/green color blindness affects ~8% of males.

**Affected elements:**
- Status bar connection indicators (green OK, red X)
- Safety state (green SAFE, red UNSAFE)
- Enable/Disable buttons (green enable, red disable)

**Current mitigation:**
- Text labels accompany colors ("Connected", "Disconnected")
- Icons used ([OK], [X])
- Multiple feedback channels (color + text + position)

**Grade: B+**

Good text labeling, but could add more non-color indicators.

**Recommendation:**
- Add shape coding (circle=OK, triangle=warning, square=error)
- Use icons more consistently
- Add pattern fills as backup (stripes for warning, solid for error)

### 5.2 Keyboard Navigation

**Not evaluated** - GUI code doesn't show tab order or keyboard shortcuts.

**Recommendation for future:**
- Add keyboard shortcuts for critical actions (F1=E-Stop, etc.)
- Set logical tab order for all input fields
- Add keyboard focus indicators (blue outline)

### 5.3 Screen Reader Compatibility

**Not evaluated** - PyQt6 supports screen readers, but no ARIA labels visible in code.

**Recommendation for future:**
- Add accessible names to all interactive elements
- Provide text descriptions for icon-only buttons
- Test with NVDA or JAWS screen reader

---

## 6. Visual Design Recommendations

### 6.1 Color Scheme - Medical Device Context

**Current palette (inferred from code):**
- Background: Default Qt (light gray)
- Panels: #424242 (dark gray)
- Safety: #4CAF50 (green), #f44336 (red), #FF9800 (orange)
- Primary actions: #2196F3 (blue)
- Hardware: #1976D2 (blue), #81C784 (green), #FFD54F (yellow)

**Evaluation:**

**Strengths:**
- Clear safety color coding (green/red/orange)
- Consistent use of blue for informational
- Dark panel headers create visual hierarchy

**Weaknesses:**
- Light gray background feels dated
- No branded color scheme (medical device should feel professional)
- Color usage not codified in constants (scattered throughout code)

**Recommendation:**

Create design system constants:
```python
# /mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/design_tokens.py
class Colors:
    # Safety
    SAFE = "#4CAF50"
    WARNING = "#FF9800"
    DANGER = "#f44336"
    EMERGENCY = "#D32F2F"

    # Status
    CONNECTED = "#4CAF50"
    DISCONNECTED = "#9E9E9E"

    # UI
    PRIMARY = "#1976D2"
    SECONDARY = "#757575"
    BACKGROUND = "#FAFAFA"  # Softer than white
    PANEL = "#FFFFFF"
    HEADER = "#37474F"  # Blue-gray
```

### 6.2 Typography

**Current usage:**
- Headers: 13-18pt, bold
- Body: 10-11pt, regular
- Status: 11-14pt, bold
- Monospace: For event logs

**Evaluation:**

**Strengths:**
- Consistent use of bold for emphasis
- Monospace for logs (good)
- Size variation creates hierarchy

**Weaknesses:**
- No system-wide font definition
- Some text too small (10px in places)
- No line-height specifications (may cause cramping)

**Recommendation:**

Define typography scale:
```python
class Typography:
    H1 = "font-size: 18pt; font-weight: bold;"
    H2 = "font-size: 14pt; font-weight: bold;"
    H3 = "font-size: 12pt; font-weight: bold;"
    BODY = "font-size: 11pt;"
    SMALL = "font-size: 10pt;"
    MONO = "font-family: 'Consolas', monospace; font-size: 10pt;"
```

### 6.3 Spacing and Layout

**Current spacing:**
- Widget margins: 5-10px (inconsistent)
- Group box padding: 5px
- Layout spacing: 2-20px (varies)
- Window margins: 10px

**Evaluation:**

**Weaknesses:**
- No spacing constants
- Inconsistent margins (Lines 61, 98, 159, 260 - different values)
- Some layouts too cramped (2px spacing)

**Recommendation:**

Define spacing scale:
```python
class Spacing:
    TIGHT = 4
    NORMAL = 8
    RELAXED = 12
    LOOSE = 16
    SECTION = 24
```

Use consistently throughout UI.

---

## 7. Specific File-Level Findings

### 7.1 main_window.py

**Lines 263-268:** Camera header status update
```python
self.camera_header.setText("[CAM] Camera System [OK]")
self.camera_header.setStyleSheet(
    "font-size: 13px; font-weight: bold; padding: 8px; margin-top: 4px; "
    "background-color: #2E7D32; color: white; border-radius: 3px;"
)
```

**Issue:** Hard-coded color values scattered throughout file.

**Fix:** Extract to design tokens.

---

**Lines 528-537:** E-Stop button styling
```python
self.global_estop_btn.setStyleSheet(
    "QPushButton { background-color: #d32f2f; color: white; "
    "padding: 8px 16px; font-weight: bold; font-size: 14px; }"
    "QPushButton:hover { background-color: #b71c1c; }"
)
```

**Positive:** Has hover state defined.

**Issue:** Button height 40px may be too small for emergency use.

**Recommendation:** Increase to 50-60px height for better finger target.

---

**Lines 605-614:** Research mode watermark
```python
self.research_mode_label = QLabel("RESEARCH MODE - NOT FOR CLINICAL USE")
self.research_mode_label.setStyleSheet(
    "QLabel { background-color: #D32F2F; color: white; "
    "padding: 8px 16px; font-weight: bold; font-size: 12px; "
    "border-radius: 3px; margin-right: 10px; }"
)
```

**Positive:** High contrast, bold, rounded corners for visibility.

**Issue:** Font size 12px may be too small for critical warning.

**Recommendation:** Increase to 14px for status bar prominence.

---

### 7.2 subject_widget.py

**Lines 88-92:** Subject ID input
```python
self.subject_id_input = QLineEdit()
self.subject_id_input.setPlaceholderText("0001")
self.subject_id_input.setMaxLength(4)  # Only 4 digits
self.subject_id_input.setFixedWidth(80)
```

**Issue:** 80px width very small, hard to click.

**Fix:** Increase to 120px minimum.

---

**Lines 188-194:** Subject ID validation
```python
if not re.match(r"^\d{4}$", last_four):
    QMessageBox.warning(
        self,
        "Invalid Format",
        "Subject ID must be exactly 4 digits\n\nExample: 0001",
    )
```

**Positive:** Clear error message with example.

**Issue:** User only sees error AFTER clicking Search.

**Better:** Real-time validation as user types (red border if invalid).

---

**Lines 256-265:** Technician requirement for subject creation
```python
tech_username = self.technician_id_input.currentData()
if not tech_username:
    QMessageBox.warning(
        self,
        "Technician Required",
        "Please select a Technician before creating subjects.\n\n"
        "This ensures proper audit trail for regulatory compliance.",
    )
```

**Positive:** Explains WHY technician is required (regulatory compliance).

**Issue:** Error shown after user tried to create subject.

**Better:** Disable "Create" button until technician selected.

---

### 7.3 camera_widget.py

**Lines 283-292:** Allow long exposure checkbox
```python
self.allow_long_exposure_check = QCheckBox("Allow Long Exposure (>33ms, may drop frames)")
self.allow_long_exposure_check.setEnabled(False)
self.allow_long_exposure_check.setToolTip(
    "Enable to set exposure times longer than frame period.\n"
    "Warning: Exposures >33ms at 30 FPS will cause frame drops.\n"
    "Only use for still imaging, not live viewing."
)
self.allow_long_exposure_check.setStyleSheet("color: #ff8800; font-weight: bold;")
```

**Positive:**
- Clear warning in label
- Detailed tooltip
- Orange color indicates caution

**Issue:** Checkbox appears before the slider it affects (confusing order).

**Recommendation:** Move checkbox next to slider with lock icon.

---

**Lines 366-383:** Display scale dropdown
```python
self.scale_combo.addItems([
    "Full (1×) - High detail, slower",
    "Half (½×) - Balanced",
    "Quarter (¼×) - Fast, smooth (30 FPS)",
])
```

**Positive:** Descriptive labels explain trade-offs.

**Issue:** Technical terms (FPS, bandwidth) may confuse non-technical users.

**Recommendation:** Simpler labels: "Best Quality", "Balanced", "Smoothest"

---

**Lines 999-1002:** Emoji usage in production code
```python
self.exposure_warning_label.setText(
    f"ℹ️ Long exposure active ({exposure_ms:.1f}ms). "
    f"Expect ~{fps_estimate:.1f} FPS (frame drops normal)."
)
```

**Issue:** Emoji (ℹ️) may not render on all systems, unprofessional for medical device.

**Fix:** Use text "[INFO]" or icon from Qt resources.

---

### 7.4 active_treatment_widget.py

**Lines 95-106:** Camera placeholder
```python
self.camera_display = QLabel("Camera Feed\n(Monitoring)")
self.camera_display.setStyleSheet(
    "QLabel { "
    "background-color: #2b2b2b; "
    "color: #666; "
    "font-size: 16px; "
    "border: 2px solid #444; "
    "}"
)
```

**Issue:** Placeholder text may persist if camera feed connection fails.

**Recommendation:** Add connection status indicator within placeholder.

---

**Lines 111-119:** Parameter display labels
```python
self.laser_power_label = self._create_status_display("Laser", "0.00 W")
self.actuator_pos_label = self._create_status_display("Pos", "0 μm")
self.motor_vibration_label = self._create_status_display("Vib", "0.00 g")
```

**Issue:**
- "Pos" abbreviation unclear (position of what?)
- "Vib" abbreviation unclear
- Units shown but no context

**Recommendation:** Full labels: "Actuator Position", "Motor Vibration"

---

### 7.5 laser_widget.py

**Lines 174-179:** Enable output button
```python
self.enable_btn = QPushButton("ENABLE OUTPUT")
self.enable_btn.setMinimumHeight(50)
self.enable_btn.setStyleSheet(
    "font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;"
)
```

**Positive:** Large button, green color, clear label.

**Issue:** No confirmation required before enabling.

**Recommendation:** Add confirmation dialog (see section 4.3).

---

**Lines 310-317:** Safety check before enable
```python
if enable:
    if hasattr(self, "safety_manager") and self.safety_manager:
        if not self.safety_manager.is_laser_enable_permitted():
            status = self.safety_manager.get_safety_status_text()
            logger.error(f"Laser enable denied: {status}")
            self.controller.error_occurred.emit(f"Safety check failed: {status}")
            return
```

**Positive:** Safety manager consulted before enable.

**Issue:** Error message shown via signal emission - user may miss it.

**Recommendation:** Show modal dialog: "Cannot enable laser: {status}"

---

## 8. Summary of Recommendations

### 8.1 High Priority (Safety-Critical)

1. **Add persistent session indicator**
   - Status bar or dedicated panel
   - Shows subject, technician, duration
   - Always visible

2. **Increase E-Stop button size**
   - From 40px to 60px height
   - Make it larger than any other button

3. **Add always-visible safety panel**
   - Show interlock status in all tabs
   - Display power limit and current usage
   - Color-coded status indicators

4. **Add confirmation for laser enable**
   - "Enable laser at X.X watts? [Yes] [No]"
   - Prevents accidental activation

5. **Improve contrast for status indicators**
   - Replace light gray backgrounds with borders/icons
   - Ensure WCAG AA compliance (4.5:1 contrast)

### 8.2 Medium Priority (Usability)

6. **Redesign subject ID input**
   - Make input field wider (120px)
   - Show format hint: "P-2025-____"
   - Real-time validation

7. **Improve workflow guidance**
   - Add step indicators (1→2→3→4)
   - Show current step in treatment workflow
   - Disable future steps until current complete

8. **Create design system**
   - Extract colors to constants
   - Define typography scale
   - Standardize spacing

9. **Improve Ready Check section**
   - Connect to actual hardware status
   - Real-time updates (not hard-coded)
   - Clear pass/fail indicators

10. **Enhance error feedback**
    - Add toast notifications for non-critical
    - Create persistent error panel
    - Better error message formatting

### 8.3 Low Priority (Polish)

11. **Remove emoji from production code**
    - Replace "ℹ️" with "[INFO]" text
    - Use Qt icons instead

12. **Optimize camera control panel width**
    - Reduce from 350px to 280px
    - Gives more space to camera feed

13. **Add Large UI mode**
    - 1.5x scale for all elements
    - Better for low-light clinical environments

14. **Improve status bar layout**
    - Use icons instead of text for hardware
    - Add session info
    - Reduce clutter

15. **Standardize button sizes**
    - Primary: 50px height
    - Secondary: 40px height
    - Tertiary: 30px height

---

## 9. Conclusion

The TOSCA laser control system demonstrates **strong safety-critical design** with persistent E-Stop access, multi-level safety interlocks, and comprehensive event logging. The 3-tab architecture provides logical separation of hardware setup, treatment execution, and protocol building.

**Key Strengths:**
- Excellent research mode warning implementation
- Multiple feedback channels for critical events
- Hardware abstraction with dependency injection
- Signal-based widget communication (no reparenting)

**Key Weaknesses:**
- No persistent session indicator (critical for medical traceability)
- Safety information not always visible (interlocks only in one tab)
- Inconsistent visual design (scattered color values, spacing)
- Some workflows require too many steps (subject selection)

**Overall Assessment:** The system is functionally complete and safe for research use, but would benefit from UI polish and consistency improvements before clinical deployment. The foundation is solid - the recommendations in this report focus on refinement rather than fundamental redesign.

**Grade: B+ (Good, production-ready with improvements)**

---

## Appendix A: Design Token Proposal

Create `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/design_tokens.py`:

```python
"""
Design tokens for TOSCA UI - central source of truth for colors, typography, spacing.
"""

class Colors:
    """Color palette for TOSCA medical device UI."""

    # Safety states (primary semantic colors)
    SAFE = "#4CAF50"           # Green - system safe
    WARNING = "#FF9800"        # Orange - warning state
    DANGER = "#f44336"         # Red - unsafe/error
    EMERGENCY = "#D32F2F"      # Dark red - emergency stop

    # Connection states
    CONNECTED = "#4CAF50"      # Green - hardware connected
    DISCONNECTED = "#9E9E9E"   # Gray - hardware offline

    # UI structure
    PRIMARY = "#1976D2"        # Blue - primary actions
    SECONDARY = "#757575"      # Gray - secondary actions
    BACKGROUND = "#FAFAFA"     # Off-white - main background
    PANEL = "#FFFFFF"          # White - panel background
    HEADER = "#37474F"         # Blue-gray - section headers

    # Hardware subsystems
    CAMERA = "#64B5F6"         # Light blue
    ACTUATOR = "#81C784"       # Light green
    LASER = "#FFD54F"          # Yellow

    # Text
    TEXT_PRIMARY = "#212121"   # Near-black
    TEXT_SECONDARY = "#666666" # Gray
    TEXT_DISABLED = "#BDBDBD"  # Light gray

class Typography:
    """Typography scale for consistent text sizing."""

    H1 = "font-size: 18pt; font-weight: bold; line-height: 1.2;"
    H2 = "font-size: 14pt; font-weight: bold; line-height: 1.3;"
    H3 = "font-size: 12pt; font-weight: bold; line-height: 1.4;"
    BODY = "font-size: 11pt; line-height: 1.5;"
    SMALL = "font-size: 10pt; line-height: 1.5;"
    MONO = "font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt;"

    # Button text
    BUTTON_PRIMARY = "font-size: 14pt; font-weight: bold;"
    BUTTON_SECONDARY = "font-size: 11pt; font-weight: normal;"

class Spacing:
    """Spacing scale for consistent layouts."""

    TIGHT = 4      # Minimal spacing
    NORMAL = 8     # Default spacing
    RELAXED = 12   # Comfortable spacing
    LOOSE = 16     # Generous spacing
    SECTION = 24   # Between major sections

class ButtonSizes:
    """Standardized button dimensions."""

    EMERGENCY = 60   # E-Stop height
    PRIMARY = 50     # Important actions
    SECONDARY = 40   # Regular actions
    TERTIARY = 30    # Minor actions
```

---

## Appendix B: Proposed Session Status Panel

Add to status bar (right side, before safety indicator):

```python
# In main_window.py, _init_status_bar() method

# Session status panel (always visible when session active)
self.session_panel = QWidget()
session_layout = QHBoxLayout()
session_layout.setContentsMargins(8, 4, 8, 4)

session_icon = QLabel("👤")  # Or use Qt icon
session_layout.addWidget(session_icon)

self.session_info_label = QLabel("No active session")
self.session_info_label.setStyleSheet(
    "font-size: 11pt; padding: 4px; color: #666;"
)
session_layout.addWidget(self.session_info_label)

self.session_panel.setLayout(session_layout)
self.session_panel.setVisible(False)  # Hidden by default
status_layout.addWidget(self.session_panel)

# Update when session starts:
def _on_session_started(self, session_id: int):
    session = self.session_manager.get_current_session()
    if session:
        info_text = (
            f"Subject: {session.subject_code} | "
            f"Tech: {session.tech_name} | "
            f"Duration: {self._format_duration(session.start_time)}"
        )
        self.session_info_label.setText(info_text)
        self.session_info_label.setStyleSheet(
            "font-size: 11pt; padding: 4px; background-color: #E3F2FD; "
            "border-radius: 3px; color: #1976D2; font-weight: bold;"
        )
        self.session_panel.setVisible(True)
```

---

**End of Report**
