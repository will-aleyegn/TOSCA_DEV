# TOSCA UI/UX Improvement Mockups

**Date:** 2025-11-05
**Version:** 0.9.12-alpha
**Purpose:** Detailed visual mockups and specifications for UI/UX improvements
**Reference:** UI_UX_ANALYSIS_REPORT.md

---

## Table of Contents

1. [Mockup 1: Persistent Session Indicator](#mockup-1-persistent-session-indicator)
2. [Mockup 2: Always-Visible Safety Panel](#mockup-2-always-visible-safety-panel)
3. [Mockup 3: Enlarged E-Stop Button](#mockup-3-enlarged-e-stop-button)
4. [Mockup 4: Improved Subject ID Input](#mockup-4-improved-subject-id-input)
5. [Mockup 5: Workflow Step Indicator](#mockup-5-workflow-step-indicator)
6. [Design Token Implementation](#design-token-implementation)

---

## Mockup 1: Persistent Session Indicator

### Priority: CRITICAL (Safety/Traceability)

### Problem
No persistent session indicator showing current subject, technician, and session duration. This is a critical issue for medical device traceability.

### Current State (Status Bar)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ [RESEARCH MODE] | [CAM] Camera [X] | [LSR] Laser [X] | [ACT] Actuator [X] | [SYSTEM SAFE] │
└─────────────────────────────────────────────────────────────────────────┘
```

**Issues:**
- No session information visible
- Cluttered with bracketed prefixes
- Information density too high

### Proposed Design
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [RESEARCH MODE] | [icon] [icon] [icon] | SESSION: P-2025-0001 | Tech: Will | 00:15:32 | [SYSTEM SAFE] │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Improvements:**
- Hardware status uses icons instead of text (saves space)
- Session panel shows subject, technician, and live duration timer
- Clear visual separation between sections
- Always visible when session is active

### Detailed Mockup

#### Session Panel (When Active)
```
┌─────────────────────────────────────────────────────┐
│ SESSION: P-2025-0001 | Tech: Will | Duration: 00:15:32 │
└─────────────────────────────────────────────────────┘
```

**Visual Specifications:**
- Background: Light blue (#E3F2FD)
- Text color: Dark blue (#1976D2)
- Font: 11pt, bold
- Padding: 4px vertical, 8px horizontal
- Border radius: 3px
- Icon: Person icon (16x16px) before session text

#### Session Panel (When Inactive)
```
┌──────────────────────┐
│ No active session    │
└──────────────────────┘
```

**Visual Specifications:**
- Background: Light gray (#F5F5F5)
- Text color: Gray (#757575)
- Font: 11pt, regular
- Hidden by default, shown when user hovers status bar

### Implementation Details

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Location:** Lines 595-661 (`_init_status_bar()` method)

**Code Changes:**

1. **Replace hardware status labels with icons** (Lines 617-633)
2. **Add session panel widget** (after line 634, before master safety indicator)
3. **Connect session manager signals** (Lines 1046-1056)
4. **Add duration timer** (QTimer updating every second)

**Measurements:**
- Session panel width: Auto (fits content)
- Session panel height: 32px (matches status bar)
- Icon size: 16x16px
- Spacing between elements: 8px

**Color Specifications:**
```python
# Session active
BACKGROUND = "#E3F2FD"  # Light blue
TEXT = "#1976D2"        # Dark blue
BORDER = "#90CAF9"      # Lighter blue border

# Session inactive
BACKGROUND_INACTIVE = "#F5F5F5"  # Light gray
TEXT_INACTIVE = "#757575"        # Gray
```

### Acceptance Criteria
- [ ] Session panel visible in status bar at all times when session active
- [ ] Shows subject code, technician name, and live duration
- [ ] Duration updates every second (HH:MM:SS format)
- [ ] Panel hidden when no session active
- [ ] Panel has distinct background color (light blue) for visibility
- [ ] Hardware icons replace text labels to save space

---

## Mockup 2: Always-Visible Safety Panel

### Priority: CRITICAL (Safety)

### Problem
Safety information (interlocks, power limits) only visible in specific tabs. Users must switch tabs to see critical safety status.

### Current State
Safety information split across:
- Status bar: Master safety indicator (bottom right)
- Active Treatment tab: Interlock panel (right side)
- Safety tab: Detailed diagnostics

**Issue:** Not always visible during hardware setup and treatment.

### Proposed Design: Docked Safety Panel (Right Side)

```
┌────────────────────────────────────────────┬──────────────────────────┐
│                                            │ SAFETY STATUS            │
│                                            │ ─────────────────────    │
│  [Main Content Area - Tabs]               │ State: SAFE              │
│                                            │ ✓ All Interlocks OK      │
│  - Hardware & Diagnostics                  │                          │
│  - Treatment Workflow                      │ ─────────────────────    │
│  - Protocol Builder                        │ INTERLOCKS               │
│                                            │ ✓ Footpedal: PRESSED     │
│                                            │ ✓ Smoothing: HEALTHY     │
│                                            │ ✓ Photodiode: OK         │
│                                            │ ✓ Watchdog: ACTIVE       │
│                                            │                          │
│                                            │ ─────────────────────    │
│                                            │ POWER STATUS             │
│                                            │ Current: 2.5W            │
│                                            │ Limit: 10.0W             │
│                                            │ [████████░░] 25%         │
│                                            │                          │
│                                            │ ─────────────────────    │
│                                            │ SESSION                  │
│                                            │ P-2025-0001              │
│                                            │ Tech: Will               │
│                                            │ Duration: 00:15:32       │
└────────────────────────────────────────────┴──────────────────────────┘
```

**Dimensions:**
- Panel width: 240px (fixed)
- Panel background: White (#FFFFFF)
- Border: 1px solid #E0E0E0 (left edge)
- Main content: Reduced by 240px width

### Alternative Design: Collapsible Bottom Panel

```
┌───────────────────────────────────────────────────────────────────────┐
│  [Main Content Area - Tabs]                                           │
│                                                                        │
│  Full height when collapsed                                           │
│                                                                        │
├───────────────────────────────────────────────────────────────────────┤
│ [⯆] SAFETY STATUS | State: SAFE | ✓ Interlocks OK | Power: 2.5/10W | Session: P-2025-0001 │
└───────────────────────────────────────────────────────────────────────┘

[User clicks expand button ⯆]

┌───────────────────────────────────────────────────────────────────────┐
│  [Main Content Area - Tabs]                                           │
│                                                                        │
│  Reduced height                                                        │
│                                                                        │
├─────────────────────────┬─────────────────────────┬──────────────────┤
│ [⯅] SAFETY STATUS       │ INTERLOCKS              │ POWER STATUS     │
│ State: SAFE             │ ✓ Footpedal: PRESSED    │ Current: 2.5W    │
│ ✓ All OK                │ ✓ Smoothing: HEALTHY    │ Limit: 10.0W     │
│                         │ ✓ Photodiode: OK        │ [████████░░] 25% │
│                         │ ✓ Watchdog: ACTIVE      │                  │
└─────────────────────────┴─────────────────────────┴──────────────────┘
```

**Dimensions:**
- Collapsed height: 40px (single line)
- Expanded height: 120px (detailed view)
- Toggle button: [⯆] (down arrow) / [⯅] (up arrow)

### Recommended: Right Panel (Medical Device Standard)

**Rationale:**
- Medical devices typically use persistent side panels for critical monitoring
- Always visible without user interaction
- Doesn't reduce vertical space (important for camera feed)
- Clear visual hierarchy (safety = right side)

### Detailed Visual Specifications

#### Section Headers
```
┌──────────────────────────┐
│ SAFETY STATUS            │
│ ─────────────────────    │
```
- Font: 11pt, bold, uppercase
- Color: #37474F (dark blue-gray)
- Divider: 1px solid #E0E0E0
- Padding: 8px top/bottom

#### State Indicator
```
┌──────────────────────────┐
│ State: SAFE              │  <- Green circle + text
└──────────────────────────┘

┌──────────────────────────┐
│ State: UNSAFE            │  <- Orange triangle + text
└──────────────────────────┘

┌──────────────────────────┐
│ State: EMERGENCY STOP    │  <- Red square + text
└──────────────────────────┘
```

**Visual Specs:**
- Circle/Triangle/Square: 12x12px shape indicator
- Font: 12pt, bold
- Colors:
  - SAFE: #4CAF50 (green)
  - UNSAFE: #FF9800 (orange)
  - E-STOP: #F44336 (red)

#### Interlock Status Items
```
✓ Footpedal: PRESSED     (green checkmark)
✗ Smoothing: FAULT       (red X)
⚠ Photodiode: WARNING    (orange warning)
```

**Visual Specs:**
- Icon: 14x14px (✓ checkmark, ✗ X, ⚠ triangle)
- Label: 10pt, regular
- Status: 10pt, bold
- Line height: 24px
- Colors:
  - OK: #4CAF50 (green)
  - Fault: #F44336 (red)
  - Warning: #FF9800 (orange)

#### Power Status Bar
```
┌──────────────────────────┐
│ Current: 2.5W            │
│ Limit: 10.0W             │
│ [████████░░] 25%         │
└──────────────────────────┘
```

**Visual Specs:**
- Progress bar: 200px width, 20px height
- Filled: #4CAF50 (green) when < 80%, #FF9800 (orange) when 80-100%, #F44336 (red) if exceeded
- Background: #E0E0E0 (light gray)
- Border radius: 4px
- Percentage text: 11pt, bold, centered

### Implementation Details

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Location:** Lines 231-243 (`_init_ui()` method)

**New Widget:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/always_visible_safety_panel.py`

**Code Changes:**

1. **Create AlwaysVisibleSafetyPanel widget**
2. **Add to main window layout** (right side dock)
3. **Connect safety manager signals**
4. **Connect GPIO interlock signals**
5. **Add power monitoring from laser controller**

**Layout Structure:**
```python
main_layout = QHBoxLayout()
main_layout.addWidget(tabs, stretch=4)  # 80% width
main_layout.addWidget(safety_panel, stretch=1)  # 20% width (240px min)
```

### Acceptance Criteria
- [ ] Safety panel visible on right side of window at all times
- [ ] Shows current safety state with color coding
- [ ] Displays all 4 interlocks with real-time status
- [ ] Shows current laser power vs. limit with progress bar
- [ ] Shows active session information
- [ ] Updates in real-time (no manual refresh needed)
- [ ] Panel width: 240px fixed, doesn't resize with window
- [ ] Scrollable if content exceeds vertical space

---

## Mockup 3: Enlarged E-Stop Button

### Priority: HIGH (Safety)

### Problem
Current E-Stop button is 40px height, which is good but could be larger for emergency situations. Medical device standard recommends 60-80px for critical safety actions.

### Current Design (Toolbar)
```
┌───────────────────────────────────────────────────────────────────┐
│ [EMERGENCY STOP] | [Connect All] [Disconnect All] | [Test All]    │  <- 40px height
└───────────────────────────────────────────────────────────────────┘
```

### Proposed Design
```
┌───────────────────────────────────────────────────────────────────┐
│                    │                                               │
│ [EMERGENCY STOP]   │ [Connect All] [Disconnect All] | [Test All]  │  <- 60px height
│                    │                                               │
└───────────────────────────────────────────────────────────────────┘
```

**Improvements:**
- Height increased from 40px to 60px (50% larger)
- Width increased from auto to 200px (more prominent)
- Larger font size (14px → 18px)
- More padding (8px → 12px)
- Slightly raised appearance (box shadow)

### Detailed Visual Specifications

#### Before (Current)
```
┌─────────────────────┐
│  EMERGENCY STOP     │  40px height
└─────────────────────┘
```

#### After (Proposed)
```
┌─────────────────────┐
│                     │
│  EMERGENCY STOP     │  60px height
│                     │
└─────────────────────┘
```

**Dimensions:**
- Width: 200px (fixed)
- Height: 60px (up from 40px)
- Padding: 12px vertical, 20px horizontal
- Border radius: 4px
- Box shadow: 0 2px 4px rgba(0,0,0,0.2)

**Colors:**
```python
# Normal state
BACKGROUND = "#D32F2F"  # Dark red
TEXT = "#FFFFFF"        # White
SHADOW = "rgba(0,0,0,0.2)"

# Hover state
BACKGROUND_HOVER = "#B71C1C"  # Darker red
SHADOW_HOVER = "rgba(0,0,0,0.3)"

# Pressed state
BACKGROUND_PRESSED = "#C62828"  # Medium red
SHADOW_PRESSED = "inset 0 2px 4px rgba(0,0,0,0.3)"

# Disabled state (after activation)
BACKGROUND_DISABLED = "#9E9E9E"  # Gray
TEXT_DISABLED = "#616161"       # Dark gray
```

**Typography:**
- Font size: 18px (up from 14px)
- Font weight: Bold
- Text transform: Uppercase
- Letter spacing: 1px (improved readability)

### Visual States

#### Normal
```
┌─────────────────────────────┐
│  [STOP]                     │
│  EMERGENCY STOP             │
│                             │  Red background, white text, subtle shadow
└─────────────────────────────┘
```

#### Hover
```
┌─────────────────────────────┐
│  [STOP]                     │
│  EMERGENCY STOP             │
│                             │  Darker red, stronger shadow, slight scale up
└─────────────────────────────┘
```

#### Pressed
```
┌─────────────────────────────┐
│  [STOP]                     │
│  EMERGENCY STOP             │
│                             │  Inset shadow, looks "pushed in"
└─────────────────────────────┘
```

#### Active (After Activation)
```
┌─────────────────────────────┐
│  [STOP]                     │
│  E-STOP ACTIVE              │
│                             │  Gray background, disabled appearance
└─────────────────────────────┘
```

### Implementation Details

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Location:** Lines 527-537 (`_init_toolbar()` method)

**Code Changes:**

Replace lines 528-536:
```python
# OLD
self.global_estop_btn = QPushButton("[STOP] EMERGENCY STOP")
self.global_estop_btn.setMinimumHeight(40)
self.global_estop_btn.setStyleSheet(
    "QPushButton { background-color: #d32f2f; color: white; "
    "padding: 8px 16px; font-weight: bold; font-size: 14px; }"
    "QPushButton:hover { background-color: #b71c1c; }"
)
```

**NEW:**
```python
self.global_estop_btn = QPushButton("[STOP] EMERGENCY STOP")
self.global_estop_btn.setFixedSize(200, 60)  # Fixed size for prominence
self.global_estop_btn.setStyleSheet(
    "QPushButton { "
    "  background-color: #D32F2F; "
    "  color: white; "
    "  padding: 12px 20px; "
    "  font-weight: bold; "
    "  font-size: 18px; "
    "  border-radius: 4px; "
    "  border: 2px solid #B71C1C; "
    "  text-transform: uppercase; "
    "  letter-spacing: 1px; "
    "}"
    "QPushButton:hover { "
    "  background-color: #B71C1C; "
    "  border-color: #9C1C1C; "
    "}"
    "QPushButton:pressed { "
    "  background-color: #C62828; "
    "}"
    "QPushButton:disabled { "
    "  background-color: #9E9E9E; "
    "  color: #616161; "
    "  border-color: #757575; "
    "}"
)
```

### Touch-Friendly Variant (Optional)

For touchscreen operation:
```
┌─────────────────────────────┐
│                             │
│  [STOP]                     │
│  EMERGENCY                  │
│  STOP                       │  80px height
│                             │
└─────────────────────────────┘
```

**Dimensions:**
- Width: 200px
- Height: 80px (even larger for gloved fingers)
- Text: Multi-line for better readability

### Acceptance Criteria
- [ ] E-Stop button height increased to 60px (from 40px)
- [ ] Button width fixed at 200px
- [ ] Font size increased to 18px
- [ ] Hover state clearly visible
- [ ] Button has subtle shadow for depth
- [ ] Disabled state (gray) after activation
- [ ] Button remains leftmost in toolbar
- [ ] Passes touch-friendly test: minimum 40x40px target (exceeds at 200x60px)

---

## Mockup 4: Improved Subject ID Input

### Priority: HIGH (Usability)

### Problem
- Input field too narrow (80px) - hard to click
- No real-time validation feedback
- Format hint not clear until after error

### Current Design
```
Subject ID (last 4 digits):
[P-2025-] [____]  <- 80px wide input

[Search Subject]  [Create New Subject]  [View Sessions]
```

**Issues:**
- Tiny input field
- No visual guidance for 4-digit format
- All buttons equal weight (no primary action distinction)

### Proposed Design

#### Layout
```
Subject ID:
┌─────────────────────────┐
│ P-2025-[____]           │  <- 200px wide, shows format hint
└─────────────────────────┘
Enter last 4 digits (e.g., 0001)

[Search Subject (Primary)]  [Create New]  [View Sessions]
```

**Improvements:**
- Wider input field (200px, up from 80px)
- Format hint integrated into field (underscores show 4 digits needed)
- Real-time validation (red border if invalid)
- Primary button styling (blue) for "Search"
- Helper text below input

### Detailed Visual Specifications

#### Input Field States

**Empty (Initial)**
```
┌─────────────────────────────────────┐
│ P-2025-____                         │  <- Placeholder shows format
└─────────────────────────────────────┘
```
- Width: 200px (up from 80px)
- Height: 40px (comfortable click target)
- Border: 1px solid #BDBDBD (gray)
- Background: White
- Placeholder text: Gray (#9E9E9E)

**Typing (Valid)**
```
┌─────────────────────────────────────┐
│ P-2025-0001 ✓                       │  <- Green checkmark appears
└─────────────────────────────────────┘
```
- Border: 2px solid #4CAF50 (green)
- Checkmark icon: 16x16px, green
- Background: Light green tint (#E8F5E9)

**Typing (Invalid)**
```
┌─────────────────────────────────────┐
│ P-2025-1 ✗                          │  <- Red X appears
└─────────────────────────────────────┘
Must be exactly 4 digits
```
- Border: 2px solid #F44336 (red)
- X icon: 16x16px, red
- Error text: 10pt, red, below field
- Background: Light red tint (#FFEBEE)

**Focused (User clicked)**
```
┌─────────────────────────────────────┐
│ P-2025-|                            │  <- Cursor blinking
└─────────────────────────────────────┘
```
- Border: 2px solid #1976D2 (blue) - focus ring
- Box shadow: 0 0 4px rgba(25,118,210,0.3)

#### Button Hierarchy

**Before (Equal Weight)**
```
[Search Subject]  [Create New Subject]  [View Sessions]
```
All gray, same size, no distinction.

**After (Primary/Secondary)**
```
[Search Subject]  [Create New]  [View Sessions]
     ↑ Blue            ↑ Gray        ↑ Text link
   Primary         Secondary        Tertiary
```

**Primary Button (Search):**
- Background: #1976D2 (blue)
- Color: White
- Height: 40px
- Width: 150px
- Font: 12pt, bold
- Border radius: 4px

**Secondary Button (Create):**
- Background: #F5F5F5 (light gray)
- Color: #424242 (dark gray)
- Border: 1px solid #BDBDBD
- Height: 40px
- Width: 120px
- Font: 12pt, regular

**Tertiary Button (View):**
- Background: Transparent
- Color: #1976D2 (blue)
- Underline on hover
- Height: 40px
- Width: Auto
- Font: 12pt, regular

### Validation Logic

#### Real-Time Validation Rules
1. **Character count:**
   - 0 chars: Neutral state (gray border)
   - 1-3 chars: Invalid (red border, error text)
   - 4 chars: Valid if all digits (green border, checkmark)
   - 5+ chars: Invalid (should not happen with maxLength=4, but handle gracefully)

2. **Character type:**
   - Only digits 0-9 allowed
   - Reject letters, symbols, spaces

3. **Visual feedback:**
   - Update on every keystroke (real-time)
   - Show checkmark when valid
   - Show X and error message when invalid
   - No blocking dialogs until user clicks Search

#### Helper Text
```
Enter last 4 digits (e.g., 0001)
```
- Font: 10pt, italic
- Color: #757575 (medium gray)
- Position: Below input field
- Margin top: 4px

### Implementation Details

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/subject_widget.py`
**Location:** Lines 73-99 (`_create_subject_group()` method)

**Code Changes:**

1. **Replace lines 88-92** (input field):
```python
# OLD
self.subject_id_input = QLineEdit()
self.subject_id_input.setPlaceholderText("0001")
self.subject_id_input.setMaxLength(4)
self.subject_id_input.setFixedWidth(80)
```

**NEW:**
```python
self.subject_id_input = QLineEdit()
self.subject_id_input.setPlaceholderText("____")  # Format hint
self.subject_id_input.setMaxLength(4)
self.subject_id_input.setFixedWidth(200)  # Wider for easier clicking
self.subject_id_input.setMinimumHeight(40)  # Touch-friendly
self.subject_id_input.textChanged.connect(self._validate_subject_id_input)  # Real-time validation

# Add helper text
helper_label = QLabel("Enter last 4 digits (e.g., 0001)")
helper_label.setStyleSheet("font-size: 10pt; font-style: italic; color: #757575;")
layout.addWidget(helper_label)
```

2. **Add validation method:**
```python
def _validate_subject_id_input(self, text: str) -> None:
    """Real-time validation of subject ID input."""
    if len(text) == 0:
        # Neutral state
        self.subject_id_input.setStyleSheet(
            "border: 1px solid #BDBDBD; padding: 8px;"
        )
    elif len(text) < 4:
        # Invalid - too short
        self.subject_id_input.setStyleSheet(
            "border: 2px solid #F44336; background-color: #FFEBEE; padding: 8px;"
        )
    elif len(text) == 4 and text.isdigit():
        # Valid
        self.subject_id_input.setStyleSheet(
            "border: 2px solid #4CAF50; background-color: #E8F5E9; padding: 8px;"
        )
    else:
        # Invalid - non-digit characters
        self.subject_id_input.setStyleSheet(
            "border: 2px solid #F44336; background-color: #FFEBEE; padding: 8px;"
        )
```

3. **Update button styling** (Lines 97-107):
```python
# Primary button (Search)
self.search_button = QPushButton("Search Subject")
self.search_button.clicked.connect(self._on_search_subject)
self.search_button.setStyleSheet(
    "QPushButton { background-color: #1976D2; color: white; "
    "font-size: 12pt; font-weight: bold; padding: 10px 20px; "
    "border-radius: 4px; min-height: 40px; min-width: 150px; }"
    "QPushButton:hover { background-color: #1565C0; }"
)
layout.addWidget(self.search_button)

# Secondary button (Create)
self.create_button = QPushButton("Create New")
self.create_button.clicked.connect(self._on_create_subject)
self.create_button.setStyleSheet(
    "QPushButton { background-color: #F5F5F5; color: #424242; "
    "border: 1px solid #BDBDBD; font-size: 12pt; "
    "padding: 10px 20px; border-radius: 4px; min-height: 40px; min-width: 120px; }"
    "QPushButton:hover { background-color: #EEEEEE; }"
)
layout.addWidget(self.create_button)

# Tertiary button (View Sessions)
self.view_sessions_button = QPushButton("View Sessions")
self.view_sessions_button.clicked.connect(self._on_view_sessions)
self.view_sessions_button.setStyleSheet(
    "QPushButton { background-color: transparent; color: #1976D2; "
    "font-size: 12pt; text-decoration: underline; border: none; "
    "padding: 10px 20px; min-height: 40px; }"
    "QPushButton:hover { color: #1565C0; }"
)
layout.addWidget(self.view_sessions_button)
```

### Acceptance Criteria
- [ ] Input field width increased to 200px
- [ ] Input field height: 40px (touch-friendly)
- [ ] Placeholder shows format hint: "____"
- [ ] Helper text below field: "Enter last 4 digits (e.g., 0001)"
- [ ] Real-time validation on every keystroke
- [ ] Green border + checkmark when 4 valid digits entered
- [ ] Red border + error text when invalid
- [ ] Search button has primary styling (blue background)
- [ ] Create button has secondary styling (gray background)
- [ ] View Sessions button has tertiary styling (text link)

---

## Mockup 5: Workflow Step Indicator

### Priority: MEDIUM (Usability)

### Problem
No visual guidance for treatment workflow. Users don't know what order to follow:
- Connect hardware → Select subject → Load protocol → Start treatment

### Current Design (Treatment Workflow Tab)
```
┌────────────────────────────────────────────────────────┐
│  [Treatment Workflow Tab]                              │
│                                                         │
│  Subject Selection                                     │
│  Treatment Setup                                       │
│  Camera View                                           │
│                                                         │
└────────────────────────────────────────────────────────┘
```

No indication of current step or what comes next.

### Proposed Design: Top-of-Tab Step Indicator

```
┌────────────────────────────────────────────────────────┐
│  [Treatment Workflow Tab]                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Select    →    2. Load      →    3. Begin  │  │
│  │  Subject           Protocol          Treatment  │  │
│  │  [ACTIVE]          [PENDING]         [PENDING]  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Subject Selection (Step 1)                            │
│  ...                                                    │
└────────────────────────────────────────────────────────┘
```

**Visual Progression:**

#### Step 1 Active (Select Subject)
```
┌─────────────────────────────────────────────────────────────┐
│  1. Select Subject  →  2. Load Protocol  →  3. Begin        │
│  [████████████]        [            ]        [            ]  │
│  ACTIVE                PENDING               PENDING         │
└─────────────────────────────────────────────────────────────┘
```

#### Step 2 Active (Load Protocol)
```
┌─────────────────────────────────────────────────────────────┐
│  1. Select Subject  →  2. Load Protocol  →  3. Begin        │
│  [✓ COMPLETE]          [████████████]        [            ]  │
│  COMPLETE              ACTIVE                PENDING         │
└─────────────────────────────────────────────────────────────┘
```

#### Step 3 Active (Begin Treatment)
```
┌─────────────────────────────────────────────────────────────┐
│  1. Select Subject  →  2. Load Protocol  →  3. Begin        │
│  [✓ COMPLETE]          [✓ COMPLETE]          [████████████] │
│  COMPLETE              COMPLETE              ACTIVE          │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Visual Specifications

#### Step Container
```
┌───────────────────────────────────────────────────────────────┐
│  Step N: [Title]                                              │
│  [Progress Bar or Status Icon]                                │
│  [Status Text: PENDING / ACTIVE / COMPLETE]                   │
└───────────────────────────────────────────────────────────────┘
```

**Dimensions:**
- Container width: 200px per step
- Container height: 80px
- Padding: 12px
- Border radius: 6px
- Gap between steps: 16px (with arrow)

#### Step States

**1. Pending (Not Started)**
- Background: #F5F5F5 (light gray)
- Border: 1px solid #E0E0E0
- Title color: #9E9E9E (gray)
- Icon: Empty circle (○)
- Progress bar: Empty

**2. Active (In Progress)**
- Background: #E3F2FD (light blue)
- Border: 2px solid #1976D2 (blue)
- Title color: #1976D2 (blue)
- Icon: Filled circle with animation (●)
- Progress bar: Animated stripes

**3. Complete (Finished)**
- Background: #E8F5E9 (light green)
- Border: 1px solid #4CAF50 (green)
- Title color: #2E7D32 (dark green)
- Icon: Green checkmark (✓)
- Progress bar: Full (100%)

#### Arrow Connectors
```
Step 1  →  Step 2  →  Step 3
```

**Specifications:**
- Arrow: Unicode character "→" or SVG icon
- Size: 24px
- Color: #BDBDBD (gray) for pending connections
- Color: #1976D2 (blue) for completed connections
- Vertical alignment: Center of step container

### Implementation Details

**File:** Create new widget
**Path:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/workflow_step_indicator.py`

**Integration Point:**
**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Location:** Lines 355-427 (Treatment Workflow tab)

**Code Structure:**

```python
class WorkflowStepIndicator(QWidget):
    """
    Visual workflow step indicator for treatment workflow.

    Shows progression through:
    1. Select Subject
    2. Load Protocol
    3. Begin Treatment
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 1
        self._init_ui()

    def _init_ui(self):
        """Create step indicator UI."""
        layout = QHBoxLayout()
        layout.setSpacing(16)

        # Step 1: Select Subject
        self.step1 = self._create_step_widget(
            number=1,
            title="Select Subject",
            status="pending"
        )
        layout.addWidget(self.step1)

        # Arrow
        layout.addWidget(self._create_arrow())

        # Step 2: Load Protocol
        self.step2 = self._create_step_widget(
            number=2,
            title="Load Protocol",
            status="pending"
        )
        layout.addWidget(self.step2)

        # Arrow
        layout.addWidget(self._create_arrow())

        # Step 3: Begin Treatment
        self.step3 = self._create_step_widget(
            number=3,
            title="Begin Treatment",
            status="pending"
        )
        layout.addWidget(self.step3)

        layout.addStretch()
        self.setLayout(layout)

    def set_step(self, step: int):
        """Update current step (1, 2, or 3)."""
        self.current_step = step
        # Update step widget styling based on step number
        # Step 1: Active/Complete based on step value
        # Step 2: Pending/Active/Complete
        # Step 3: Pending/Active

    def _create_step_widget(self, number: int, title: str, status: str) -> QWidget:
        """Create individual step widget."""
        # Return QWidget with:
        # - Step number
        # - Title
        # - Status indicator (pending/active/complete)
        pass

    def _create_arrow(self) -> QLabel:
        """Create arrow connector between steps."""
        arrow = QLabel("→")
        arrow.setStyleSheet("font-size: 24px; color: #BDBDBD;")
        return arrow
```

**Integration:**
```python
# In main_window.py, Treatment Workflow tab section

# Add step indicator at top of left column
self.workflow_steps = WorkflowStepIndicator()
left_layout.addWidget(self.workflow_steps)

# Connect to workflow events
self.subject_widget.session_started.connect(
    lambda: self.workflow_steps.set_step(2)
)
self.treatment_setup_widget.protocol_loaded.connect(
    lambda: self.workflow_steps.set_step(3)
)
```

### Acceptance Criteria
- [ ] Step indicator visible at top of Treatment Workflow tab
- [ ] Shows 3 steps: Select Subject, Load Protocol, Begin Treatment
- [ ] Current step highlighted with blue background
- [ ] Completed steps show green checkmark
- [ ] Future steps grayed out
- [ ] Arrows connect steps visually
- [ ] Indicator updates automatically when user progresses
- [ ] Each step is 200px wide, 80px tall
- [ ] Responsive to window resize (steps remain visible)

---

## Design Token Implementation

### Purpose
Centralize all color, typography, and spacing values to ensure consistency across the application.

### File Location
**Path:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/design_tokens.py`

### Code Implementation

```python
"""
Design tokens for TOSCA UI - central source of truth for colors, typography, spacing.

Usage:
    from ui.design_tokens import Colors, Typography, Spacing, ButtonSizes

    button.setStyleSheet(f"background-color: {Colors.PRIMARY}; {Typography.BUTTON_PRIMARY}")
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
    PRIMARY_HOVER = "#1565C0"  # Darker blue - hover state
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

    # Borders
    BORDER_DEFAULT = "#E0E0E0" # Light gray
    BORDER_FOCUS = "#1976D2"   # Blue - focus ring
    BORDER_ERROR = "#F44336"   # Red - validation error
    BORDER_SUCCESS = "#4CAF50" # Green - validation success

    # Session indicator
    SESSION_ACTIVE_BG = "#E3F2FD"    # Light blue background
    SESSION_ACTIVE_TEXT = "#1976D2"  # Blue text
    SESSION_INACTIVE_BG = "#F5F5F5"  # Light gray
    SESSION_INACTIVE_TEXT = "#757575" # Gray text

    # Validation states
    VALID_BG = "#E8F5E9"       # Light green tint
    VALID_BORDER = "#4CAF50"   # Green border
    INVALID_BG = "#FFEBEE"     # Light red tint
    INVALID_BORDER = "#F44336" # Red border


class Typography:
    """Typography scale for consistent text sizing."""

    H1 = "font-size: 18pt; font-weight: bold; line-height: 1.2;"
    H2 = "font-size: 14pt; font-weight: bold; line-height: 1.3;"
    H3 = "font-size: 12pt; font-weight: bold; line-height: 1.4;"
    BODY = "font-size: 11pt; line-height: 1.5;"
    BODY_BOLD = "font-size: 11pt; font-weight: bold; line-height: 1.5;"
    SMALL = "font-size: 10pt; line-height: 1.5;"
    SMALL_ITALIC = "font-size: 10pt; font-style: italic; line-height: 1.5;"
    MONO = "font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt;"

    # Button text
    BUTTON_PRIMARY = "font-size: 14pt; font-weight: bold;"
    BUTTON_SECONDARY = "font-size: 11pt; font-weight: normal;"
    BUTTON_LARGE = "font-size: 18pt; font-weight: bold; letter-spacing: 1px;"

    # Status bar
    STATUS_BAR = "font-size: 11pt; font-weight: bold;"
    STATUS_BAR_SMALL = "font-size: 10pt;"


class Spacing:
    """Spacing scale for consistent layouts."""

    TIGHT = 4      # Minimal spacing
    NORMAL = 8     # Default spacing
    RELAXED = 12   # Comfortable spacing
    LOOSE = 16     # Generous spacing
    SECTION = 24   # Between major sections

    # Padding values
    PADDING_SMALL = "4px"
    PADDING_NORMAL = "8px"
    PADDING_LARGE = "12px"
    PADDING_XLARGE = "16px"


class ButtonSizes:
    """Standardized button dimensions."""

    EMERGENCY = 60   # E-Stop height (increased from 40px)
    PRIMARY = 50     # Important actions
    SECONDARY = 40   # Regular actions
    TERTIARY = 30    # Minor actions

    # Touch-friendly minimum
    TOUCH_MIN = 40   # Minimum 40x40px for touch targets


class BorderRadius:
    """Border radius values for consistent rounded corners."""

    SMALL = "3px"
    MEDIUM = "4px"
    LARGE = "6px"


class Shadows:
    """Box shadow values for depth and focus."""

    SUBTLE = "0 2px 4px rgba(0, 0, 0, 0.1)"
    MODERATE = "0 2px 4px rgba(0, 0, 0, 0.2)"
    STRONG = "0 4px 8px rgba(0, 0, 0, 0.3)"
    FOCUS = "0 0 4px rgba(25, 118, 210, 0.3)"  # Blue glow
    INSET = "inset 0 2px 4px rgba(0, 0, 0, 0.3)"  # Pressed state


# Helper functions for building stylesheets
def button_style(
    bg_color: str,
    text_color: str = Colors.TEXT_PRIMARY,
    hover_color: str = None,
    size: str = "secondary"
) -> str:
    """
    Generate button stylesheet with consistent styling.

    Args:
        bg_color: Background color hex
        text_color: Text color hex (default: Colors.TEXT_PRIMARY)
        hover_color: Hover background color (default: darker version of bg_color)
        size: "primary", "secondary", "tertiary", or "emergency"

    Returns:
        Complete QPushButton stylesheet string
    """
    if hover_color is None:
        # Darken background by 10% for hover
        hover_color = bg_color  # Simplified - use same color

    height = {
        "emergency": ButtonSizes.EMERGENCY,
        "primary": ButtonSizes.PRIMARY,
        "secondary": ButtonSizes.SECONDARY,
        "tertiary": ButtonSizes.TERTIARY
    }.get(size, ButtonSizes.SECONDARY)

    return (
        f"QPushButton {{ "
        f"  background-color: {bg_color}; "
        f"  color: {text_color}; "
        f"  border-radius: {BorderRadius.MEDIUM}; "
        f"  padding: {Spacing.PADDING_NORMAL} {Spacing.PADDING_LARGE}; "
        f"  min-height: {height}px; "
        f"  {Typography.BUTTON_SECONDARY} "
        f"}} "
        f"QPushButton:hover {{ "
        f"  background-color: {hover_color}; "
        f"}} "
        f"QPushButton:disabled {{ "
        f"  background-color: {Colors.DISCONNECTED}; "
        f"  color: {Colors.TEXT_DISABLED}; "
        f"}}"
    )


def input_style(state: str = "default") -> str:
    """
    Generate input field stylesheet with validation states.

    Args:
        state: "default", "focus", "valid", "invalid"

    Returns:
        Complete QLineEdit stylesheet string
    """
    styles = {
        "default": (
            f"QLineEdit {{ "
            f"  border: 1px solid {Colors.BORDER_DEFAULT}; "
            f"  border-radius: {BorderRadius.MEDIUM}; "
            f"  padding: {Spacing.PADDING_NORMAL}; "
            f"  background-color: {Colors.PANEL}; "
            f"}}"
        ),
        "focus": (
            f"QLineEdit {{ "
            f"  border: 2px solid {Colors.BORDER_FOCUS}; "
            f"  border-radius: {BorderRadius.MEDIUM}; "
            f"  padding: {Spacing.PADDING_NORMAL}; "
            f"  background-color: {Colors.PANEL}; "
            f"}}"
        ),
        "valid": (
            f"QLineEdit {{ "
            f"  border: 2px solid {Colors.VALID_BORDER}; "
            f"  border-radius: {BorderRadius.MEDIUM}; "
            f"  padding: {Spacing.PADDING_NORMAL}; "
            f"  background-color: {Colors.VALID_BG}; "
            f"}}"
        ),
        "invalid": (
            f"QLineEdit {{ "
            f"  border: 2px solid {Colors.INVALID_BORDER}; "
            f"  border-radius: {BorderRadius.MEDIUM}; "
            f"  padding: {Spacing.PADDING_NORMAL}; "
            f"  background-color: {Colors.INVALID_BG}; "
            f"}}"
        ),
    }
    return styles.get(state, styles["default"])
```

### Usage Examples

#### Before (Hard-coded colors)
```python
button.setStyleSheet(
    "background-color: #1976D2; color: white; "
    "padding: 8px 16px; font-weight: bold; font-size: 14px;"
)
```

#### After (Design tokens)
```python
from ui.design_tokens import Colors, Typography, button_style

button.setStyleSheet(
    button_style(
        bg_color=Colors.PRIMARY,
        text_color=Colors.PANEL,
        hover_color=Colors.PRIMARY_HOVER,
        size="primary"
    )
)
```

### Migration Plan

1. **Phase 1:** Create `design_tokens.py` file (1 hour)
2. **Phase 2:** Update E-Stop button to use tokens (30 min)
3. **Phase 3:** Update subject input field to use tokens (1 hour)
4. **Phase 4:** Update all buttons in main_window.py (2 hours)
5. **Phase 5:** Update all widgets to use tokens (4 hours)

**Total estimated time:** 8.5 hours

### Acceptance Criteria
- [ ] design_tokens.py file created with all color/typography/spacing constants
- [ ] Helper functions (button_style, input_style) implemented
- [ ] At least 3 widgets migrated to use design tokens
- [ ] No hard-coded color values in migrated widgets
- [ ] Visual appearance unchanged (tokens match current colors exactly)

---

## Summary Table

| Mockup | Priority | Estimated Time | Files Modified | New Files |
|--------|----------|----------------|----------------|-----------|
| 1. Persistent Session Indicator | CRITICAL | 3 hours | main_window.py | None |
| 2. Always-Visible Safety Panel | CRITICAL | 5 hours | main_window.py | always_visible_safety_panel.py |
| 3. Enlarged E-Stop Button | HIGH | 30 min | main_window.py | None |
| 4. Improved Subject ID Input | HIGH | 2 hours | subject_widget.py | None |
| 5. Workflow Step Indicator | MEDIUM | 4 hours | main_window.py | workflow_step_indicator.py |
| 6. Design Tokens | MEDIUM | 8.5 hours | All widgets | design_tokens.py |
| **TOTAL** | | **23 hours** | 3 files | 3 files |

---

## Next Steps

1. Review mockups with development team
2. Prioritize implementation order (recommend: 3 → 4 → 1 → 2 → 5 → 6)
3. Create implementation tasks (see UI_UX_IMPLEMENTATION_TASKS.md)
4. Begin implementation with quick wins (E-Stop button resize)
5. Test with actual users (technicians) for feedback

---

**Document Version:** 1.0
**Last Updated:** 2025-11-05
**Author:** UI/UX Design Team
