# TOSCA UI/UX Implementation Task List

**Date:** 2025-11-05
**Version:** 0.9.12-alpha
**Purpose:** Prioritized implementation tasks for UI/UX improvements
**Reference:** UI_UX_ANALYSIS_REPORT.md, UI_UX_MOCKUPS.md

---

## Overview

This document provides a prioritized, actionable task list for implementing UI/UX improvements identified in the analysis. Tasks are organized by priority level with time estimates, dependencies, file locations, and acceptance criteria.

**Total Estimated Time:** 23 hours
**Recommended Sprint:** 3-5 days (with testing)

---

## Priority Definitions

- **CRITICAL:** Safety-related or regulatory compliance issues. Must be implemented before clinical use.
- **HIGH:** Significant usability improvements that reduce errors and improve efficiency.
- **MEDIUM:** Quality-of-life improvements that enhance user experience.
- **LOW:** Polish and minor refinements.

---

## Task Summary

| ID | Task | Priority | Time | Dependencies |
|----|------|----------|------|--------------|
| T1 | Enlarge E-Stop Button | HIGH | 30 min | None |
| T2 | Improve Subject ID Input | HIGH | 2 hours | None |
| T3 | Persistent Session Indicator | CRITICAL | 3 hours | None |
| T4 | Always-Visible Safety Panel | CRITICAL | 5 hours | T3 (optional) |
| T5 | Workflow Step Indicator | MEDIUM | 4 hours | None |
| T6 | Design Token System | MEDIUM | 8.5 hours | None (recommended first) |

**Recommended Implementation Order:**
1. T6 (Design Tokens) - Foundation for consistency
2. T1 (E-Stop) - Quick win, safety improvement
3. T2 (Subject ID) - Quick win, usability improvement
4. T3 (Session Indicator) - Critical for traceability
5. T4 (Safety Panel) - Critical for safety monitoring
6. T5 (Workflow Steps) - Medium priority, nice-to-have

---

## TASK T1: Enlarge E-Stop Button

### Priority: HIGH (Safety)

### Time Estimate: 30 minutes

### Description
Increase E-Stop button size from 40px to 60px height for better emergency accessibility. This aligns with medical device safety standards for critical control prominence.

### Dependencies
- None (standalone change)

### Files to Modify
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py` (Lines 527-537)

### Implementation Steps

#### Step 1: Update Button Dimensions (5 min)
**Location:** `main_window.py`, Lines 528-529

**Current Code:**
```python
self.global_estop_btn = QPushButton("[STOP] EMERGENCY STOP")
self.global_estop_btn.setMinimumHeight(40)
```

**Updated Code:**
```python
self.global_estop_btn = QPushButton("[STOP] EMERGENCY STOP")
self.global_estop_btn.setFixedSize(200, 60)  # Width: 200px, Height: 60px
```

#### Step 2: Update Button Styling (15 min)
**Location:** `main_window.py`, Lines 530-536

**Current Code:**
```python
self.global_estop_btn.setStyleSheet(
    "QPushButton { background-color: #d32f2f; color: white; "
    "padding: 8px 16px; font-weight: bold; font-size: 14px; }"
    "QPushButton:hover { background-color: #b71c1c; }"
)
```

**Updated Code:**
```python
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

#### Step 3: Test Button States (10 min)
- [ ] Normal state: Red background, white text, 60px height
- [ ] Hover state: Darker red background
- [ ] Pressed state: Medium red background
- [ ] Disabled state (after E-Stop activated): Gray background

### Acceptance Criteria
- [ ] E-Stop button height increased from 40px to 60px
- [ ] Button width fixed at 200px
- [ ] Font size increased from 14px to 18px
- [ ] Padding increased to 12px vertical, 20px horizontal
- [ ] Border: 2px solid, slightly darker red
- [ ] Border radius: 4px
- [ ] Hover state clearly visible (darker red)
- [ ] Disabled state (gray) after activation works correctly
- [ ] Button remains leftmost in toolbar
- [ ] No layout issues in toolbar (other buttons still visible)

### Testing Checklist
- [ ] Launch application, verify E-Stop button size visually
- [ ] Hover over button, confirm color change
- [ ] Click button, verify disabled state and gray color
- [ ] Restart app, verify button returns to enabled state
- [ ] Test on different screen resolutions (1920x1080, 1280x800)

### Rollback Plan
If issues occur:
1. Revert changes in `main_window.py` Lines 528-536
2. Restore original code from git: `git diff HEAD main_window.py`
3. Verify application launches without errors

---

## TASK T2: Improve Subject ID Input

### Priority: HIGH (Usability)

### Time Estimate: 2 hours

### Description
Widen subject ID input field, add real-time validation, and improve button hierarchy. This reduces data entry errors and provides immediate feedback to users.

### Dependencies
- None (standalone change)

### Files to Modify
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/subject_widget.py` (Lines 73-107)

### Implementation Steps

#### Step 1: Update Input Field (30 min)
**Location:** `subject_widget.py`, Lines 88-92

**Current Code:**
```python
self.subject_id_input = QLineEdit()
self.subject_id_input.setPlaceholderText("0001")
self.subject_id_input.setMaxLength(4)
self.subject_id_input.setFixedWidth(80)
```

**Updated Code:**
```python
self.subject_id_input = QLineEdit()
self.subject_id_input.setPlaceholderText("____")  # Format hint: 4 digits
self.subject_id_input.setMaxLength(4)
self.subject_id_input.setFixedWidth(200)  # Increased from 80px
self.subject_id_input.setMinimumHeight(40)  # Touch-friendly
self.subject_id_input.textChanged.connect(self._validate_subject_id_input)  # Real-time validation
```

#### Step 2: Add Helper Text (10 min)
**Location:** `subject_widget.py`, after Line 92

**Add Code:**
```python
# Helper text below input field
self.subject_id_helper = QLabel("Enter last 4 digits (e.g., 0001)")
self.subject_id_helper.setStyleSheet(
    "font-size: 10pt; font-style: italic; color: #757575; margin-top: 4px;"
)
layout.addWidget(self.subject_id_helper)

# Validation error label (hidden by default)
self.subject_id_error = QLabel("")
self.subject_id_error.setStyleSheet(
    "font-size: 10pt; color: #F44336; margin-top: 4px;"
)
self.subject_id_error.setVisible(False)
layout.addWidget(self.subject_id_error)
```

#### Step 3: Add Validation Method (30 min)
**Location:** `subject_widget.py`, add new method after `_create_session_group()`

**Add Code:**
```python
def _validate_subject_id_input(self, text: str) -> None:
    """
    Real-time validation of subject ID input.

    Updates input field styling based on validation state:
    - Neutral: Gray border (empty or partial entry)
    - Valid: Green border with checkmark (4 digits)
    - Invalid: Red border with error message (non-digits or too long)

    Args:
        text: Current input text
    """
    # Clear error message
    self.subject_id_error.setVisible(False)

    if len(text) == 0:
        # Neutral state - empty field
        self.subject_id_input.setStyleSheet(
            "QLineEdit { "
            "  border: 1px solid #BDBDBD; "
            "  border-radius: 4px; "
            "  padding: 8px; "
            "  background-color: white; "
            "}"
        )
        return

    if len(text) < 4:
        # Invalid - too short
        self.subject_id_input.setStyleSheet(
            "QLineEdit { "
            "  border: 2px solid #F44336; "
            "  border-radius: 4px; "
            "  padding: 8px; "
            "  background-color: #FFEBEE; "
            "}"
        )
        self.subject_id_error.setText("Must be exactly 4 digits")
        self.subject_id_error.setVisible(True)
        return

    if text.isdigit() and len(text) == 4:
        # Valid - 4 digits
        self.subject_id_input.setStyleSheet(
            "QLineEdit { "
            "  border: 2px solid #4CAF50; "
            "  border-radius: 4px; "
            "  padding: 8px; "
            "  background-color: #E8F5E9; "
            "}"
        )
        return

    # Invalid - non-digit characters
    self.subject_id_input.setStyleSheet(
        "QLineEdit { "
        "  border: 2px solid #F44336; "
        "  border-radius: 4px; "
        "  padding: 8px; "
        "  background-color: #FFEBEE; "
        "}"
    )
    self.subject_id_error.setText("Only digits 0-9 allowed")
    self.subject_id_error.setVisible(True)
```

#### Step 4: Update Button Styling (30 min)
**Location:** `subject_widget.py`, Lines 97-107

**Current Code:**
```python
self.search_button = QPushButton("Search Subject")
self.search_button.clicked.connect(self._on_search_subject)
layout.addWidget(self.search_button)

self.create_button = QPushButton("Create New Subject")
self.create_button.clicked.connect(self._on_create_subject)
layout.addWidget(self.create_button)

self.view_sessions_button = QPushButton("View Sessions")
self.view_sessions_button.clicked.connect(self._on_view_sessions)
layout.addWidget(self.view_sessions_button)
```

**Updated Code:**
```python
# Button layout for proper spacing
button_layout = QHBoxLayout()
button_layout.setSpacing(8)

# Primary button (Search) - Blue background
self.search_button = QPushButton("Search Subject")
self.search_button.clicked.connect(self._on_search_subject)
self.search_button.setStyleSheet(
    "QPushButton { "
    "  background-color: #1976D2; "
    "  color: white; "
    "  font-size: 12pt; "
    "  font-weight: bold; "
    "  padding: 10px 20px; "
    "  border-radius: 4px; "
    "  min-height: 40px; "
    "  min-width: 140px; "
    "}"
    "QPushButton:hover { "
    "  background-color: #1565C0; "
    "}"
    "QPushButton:disabled { "
    "  background-color: #BDBDBD; "
    "  color: #757575; "
    "}"
)
button_layout.addWidget(self.search_button)

# Secondary button (Create) - Gray background
self.create_button = QPushButton("Create New")
self.create_button.clicked.connect(self._on_create_subject)
self.create_button.setStyleSheet(
    "QPushButton { "
    "  background-color: #F5F5F5; "
    "  color: #424242; "
    "  border: 1px solid #BDBDBD; "
    "  font-size: 12pt; "
    "  padding: 10px 20px; "
    "  border-radius: 4px; "
    "  min-height: 40px; "
    "  min-width: 120px; "
    "}"
    "QPushButton:hover { "
    "  background-color: #EEEEEE; "
    "}"
    "QPushButton:disabled { "
    "  background-color: #FAFAFA; "
    "  color: #BDBDBD; "
    "}"
)
button_layout.addWidget(self.create_button)

button_layout.addStretch()
layout.addLayout(button_layout)

# Tertiary button (View Sessions) - Text link style
self.view_sessions_button = QPushButton("View Sessions")
self.view_sessions_button.clicked.connect(self._on_view_sessions)
self.view_sessions_button.setStyleSheet(
    "QPushButton { "
    "  background-color: transparent; "
    "  color: #1976D2; "
    "  font-size: 11pt; "
    "  border: none; "
    "  padding: 8px 16px; "
    "  text-align: left; "
    "  text-decoration: underline; "
    "}"
    "QPushButton:hover { "
    "  color: #1565C0; "
    "}"
)
layout.addWidget(self.view_sessions_button)
```

#### Step 5: Testing (20 min)
- [ ] Type 1 digit: Red border, error message
- [ ] Type 2-3 digits: Red border, error message
- [ ] Type 4 digits: Green border, no error
- [ ] Type letter: Prevented by input validation (should not appear)
- [ ] Clear field: Returns to neutral gray border
- [ ] Search button: Blue primary styling
- [ ] Create button: Gray secondary styling
- [ ] View Sessions button: Text link styling

### Acceptance Criteria
- [ ] Input field width increased to 200px (from 80px)
- [ ] Input field height: 40px (touch-friendly)
- [ ] Placeholder shows format hint: "____"
- [ ] Helper text visible below field: "Enter last 4 digits (e.g., 0001)"
- [ ] Real-time validation on every keystroke
- [ ] Green border + background tint when 4 valid digits entered
- [ ] Red border + background tint + error text when invalid
- [ ] Gray border when empty (neutral state)
- [ ] Search button: Blue background (primary)
- [ ] Create button: Gray background with border (secondary)
- [ ] View Sessions button: Text link style (tertiary)
- [ ] No console errors during typing
- [ ] Validation does not block typing (non-intrusive)

### Testing Checklist
- [ ] Test input validation with various inputs (0-4 digits, letters, symbols)
- [ ] Verify error messages appear/disappear correctly
- [ ] Test button hover states
- [ ] Test button disabled states
- [ ] Test on different screen sizes
- [ ] Test with keyboard navigation (Tab key)
- [ ] Test copy-paste behavior (4 digits from clipboard)

### Rollback Plan
If issues occur:
1. Revert `subject_widget.py` changes
2. Remove `_validate_subject_id_input()` method
3. Restore original button styling
4. Verify no validation errors on startup

---

## TASK T3: Persistent Session Indicator

### Priority: CRITICAL (Traceability)

### Time Estimate: 3 hours

### Description
Add persistent session status panel to the status bar showing current subject, technician, and live session duration. This is critical for medical device traceability and audit requirements.

### Dependencies
- None (standalone change)
- Optional: T6 (Design Tokens) for color consistency

### Files to Modify
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py` (Lines 595-661)

### Implementation Steps

#### Step 1: Replace Hardware Status Text with Icons (30 min)
**Location:** `main_window.py`, Lines 617-633

**Current Code:**
```python
self.camera_status = QLabel("[CAM] Camera [X]")
self.camera_status.setToolTip("Camera connection status")
self.camera_status.setStyleSheet("color: #f44336;")  # Red when disconnected

self.laser_status = QLabel("[LSR] Laser [X]")
self.laser_status.setToolTip("Laser controller connection status")
self.laser_status.setStyleSheet("color: #f44336;")  # Red when disconnected

self.actuator_status = QLabel("[ACT] Actuator [X]")
self.actuator_status.setToolTip("Actuator controller connection status")
self.actuator_status.setStyleSheet("color: #f44336;")  # Red when disconnected
```

**Updated Code (Icon-based):**
```python
# Camera status (icon only)
self.camera_status = QLabel("●")  # Circle for camera
self.camera_status.setToolTip("Camera: Disconnected")
self.camera_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot

# Laser status (icon only)
self.laser_status = QLabel("●")  # Circle for laser
self.laser_status.setToolTip("Laser: Disconnected")
self.laser_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot

# Actuator status (icon only)
self.actuator_status = QLabel("●")  # Circle for actuator
self.actuator_status.setToolTip("Actuator: Disconnected")
self.actuator_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red dot
```

**Update connection status methods:**
```python
# In update_camera_status() method (Line 1530-1540)
def update_camera_status(self, connected: bool) -> None:
    """Update camera connection status indicator."""
    if connected:
        self.camera_status.setText("●")
        self.camera_status.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green
        self.camera_status.setToolTip("Camera: Connected")
    else:
        self.camera_status.setText("●")
        self.camera_status.setStyleSheet("color: #f44336; font-size: 16px;")  # Red
        self.camera_status.setToolTip("Camera: Disconnected")

    # Update hardware tab header
    self._update_camera_header_status(connected)
```

Repeat for `update_laser_status()` and `update_actuator_status()`.

#### Step 2: Add Session Status Panel Widget (60 min)
**Location:** `main_window.py`, after Line 634 (after hardware status labels, before master safety indicator)

**Add Code:**
```python
# Session status panel (persistent when session active)
self.session_panel = QWidget()
session_panel_layout = QHBoxLayout()
session_panel_layout.setContentsMargins(8, 4, 8, 4)
session_panel_layout.setSpacing(8)

# Session icon
session_icon = QLabel("👤")  # Person icon (or use Qt icon: QStyle.SP_FileDialogInfoView)
session_icon.setStyleSheet("font-size: 14px;")
session_panel_layout.addWidget(session_icon)

# Session info label
self.session_info_label = QLabel("No active session")
self.session_info_label.setStyleSheet(
    "font-size: 11pt; padding: 4px 8px; color: #757575; "
    "background-color: #F5F5F5; border-radius: 3px;"
)
session_panel_layout.addWidget(self.session_info_label)

self.session_panel.setLayout(session_panel_layout)
self.session_panel.setVisible(False)  # Hidden by default until session starts
status_layout.addWidget(self.session_panel)
```

#### Step 3: Add Session Duration Timer (30 min)
**Location:** `main_window.py`, in `__init__()` method after line 173

**Add Code:**
```python
# Session duration timer (updates every second)
from PyQt6.QtCore import QTimer

self.session_timer = QTimer(self)
self.session_timer.timeout.connect(self._update_session_duration)
self.session_start_time = None  # Will be set when session starts
```

**Add Timer Update Method:**
```python
def _update_session_duration(self) -> None:
    """Update session duration display every second."""
    if self.session_start_time is None:
        return

    from datetime import datetime

    # Calculate elapsed time
    elapsed = datetime.now() - self.session_start_time
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    seconds = int(elapsed.total_seconds() % 60)

    # Get current session info
    session = self.session_manager.get_current_session()
    if session:
        # Update session info label with live duration
        info_text = (
            f"SESSION: {session.subject_code} | "
            f"Tech: {session.tech_name} | "
            f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        self.session_info_label.setText(info_text)
```

#### Step 4: Connect Session Signals (30 min)
**Location:** `main_window.py`, modify `_on_session_started()` method (Lines 1046-1056)

**Current Code:**
```python
def _on_session_started(self, session_id: int) -> None:
    """
    Handle session started event.

    Args:
        session_id: ID of started session
    """
    logger.info(f"Session {session_id} started - updating safety system")
    # Mark session as valid for safety system
    self.safety_manager.set_session_valid(True)
```

**Updated Code:**
```python
def _on_session_started(self, session_id: int) -> None:
    """
    Handle session started event.

    Updates safety system and session status display.

    Args:
        session_id: ID of started session
    """
    logger.info(f"Session {session_id} started - updating safety system and UI")

    # Mark session as valid for safety system
    self.safety_manager.set_session_valid(True)

    # Get session details
    session = self.session_manager.get_current_session()
    if session:
        # Store session start time for duration timer
        self.session_start_time = session.start_time

        # Update session panel display
        info_text = (
            f"SESSION: {session.subject_code} | "
            f"Tech: {session.tech_name} | "
            f"Duration: 00:00:00"
        )
        self.session_info_label.setText(info_text)
        self.session_info_label.setStyleSheet(
            "font-size: 11pt; padding: 4px 8px; font-weight: bold; "
            "background-color: #E3F2FD; color: #1976D2; border-radius: 3px;"
        )
        self.session_panel.setVisible(True)

        # Start duration timer (updates every second)
        self.session_timer.start(1000)  # 1000ms = 1 second

        logger.info(f"Session status panel updated: {info_text}")
```

**Add Session End Handler:**
```python
# Connect session ended signal (in _init_ui or _connect_event_logger)
self.subject_widget.session_ended.connect(self._on_session_ended)

def _on_session_ended(self) -> None:
    """Handle session ended event."""
    # Stop timer
    self.session_timer.stop()
    self.session_start_time = None

    # Reset session panel to inactive state
    self.session_info_label.setText("No active session")
    self.session_info_label.setStyleSheet(
        "font-size: 11pt; padding: 4px 8px; color: #757575; "
        "background-color: #F5F5F5; border-radius: 3px;"
    )
    self.session_panel.setVisible(False)  # Hide panel when no session

    # Update safety system
    self.safety_manager.set_session_valid(False)

    logger.info("Session ended - status panel hidden")
```

#### Step 5: Testing (30 min)
- [ ] Launch app: Session panel hidden
- [ ] Start session: Panel appears with subject/tech/duration
- [ ] Verify duration updates every second (00:00:01, 00:00:02, ...)
- [ ] End session: Panel hides, timer stops
- [ ] Restart session: Timer resets to 00:00:00
- [ ] Switch tabs: Panel remains visible in status bar

### Acceptance Criteria
- [ ] Hardware status uses icons (●) instead of text labels
- [ ] Icons tooltip shows connection status
- [ ] Session panel visible in status bar when session active
- [ ] Session panel shows: "SESSION: P-2025-XXXX | Tech: Name | Duration: HH:MM:SS"
- [ ] Duration updates every second
- [ ] Session panel has light blue background (#E3F2FD) when active
- [ ] Session panel hidden when no session active
- [ ] Panel remains visible across all tabs
- [ ] No layout issues (status bar items don't overlap)
- [ ] Timer stops when session ends
- [ ] Timer resets to 00:00:00 on new session start

### Testing Checklist
- [ ] Start application, verify panel hidden
- [ ] Create subject and start session
- [ ] Verify panel appears with correct info
- [ ] Wait 10 seconds, verify duration increments correctly
- [ ] Switch between tabs, verify panel remains visible
- [ ] End session, verify panel hides and timer stops
- [ ] Start new session, verify timer resets
- [ ] Test with long session names (>30 characters)
- [ ] Test on different screen resolutions

### Rollback Plan
If issues occur:
1. Revert `main_window.py` status bar changes
2. Remove session timer and `_update_session_duration()` method
3. Restore original hardware status text labels
4. Verify status bar displays correctly

---

## TASK T4: Always-Visible Safety Panel

### Priority: CRITICAL (Safety Monitoring)

### Time Estimate: 5 hours

### Description
Create a persistent right-side safety panel showing real-time interlock status, power monitoring, and session info. This ensures critical safety information is always visible, regardless of active tab.

### Dependencies
- T3 (Session Indicator) - Optional, but recommended for session display in safety panel

### Files to Create
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/always_visible_safety_panel.py` (new file)

### Files to Modify
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py` (Lines 231-243)

### Implementation Steps

#### Step 1: Create AlwaysVisibleSafetyPanel Widget (120 min)
**Location:** New file `always_visible_safety_panel.py`

**Full Widget Code:**
```python
"""
Always-visible safety panel widget.

Displays critical safety information persistently on right side of main window.
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from core.safety import SafetyManager, SafetyState

logger = logging.getLogger(__name__)


class AlwaysVisibleSafetyPanel(QWidget):
    """
    Persistent safety status panel for right side of main window.

    Displays:
    - Safety state (SAFE/UNSAFE/E-STOP)
    - Hardware interlock status (footpedal, smoothing, photodiode, watchdog)
    - Laser power monitoring (current vs. limit)
    - Active session information

    This panel remains visible across all tabs.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.safety_manager: Optional[SafetyManager] = None
        self.gpio_controller = None
        self.laser_controller = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Panel title
        title = QLabel("SAFETY STATUS")
        title.setStyleSheet(
            "font-size: 12pt; font-weight: bold; color: #37474F; "
            "padding-bottom: 8px; border-bottom: 1px solid #E0E0E0;"
        )
        layout.addWidget(title)

        # Safety state indicator
        layout.addWidget(self._create_state_section())

        # Interlock status
        layout.addWidget(self._create_interlock_section())

        # Power monitoring
        layout.addWidget(self._create_power_section())

        # Session information
        layout.addWidget(self._create_session_section())

        layout.addStretch()
        self.setLayout(layout)

        # Panel styling
        self.setStyleSheet(
            "QWidget { background-color: white; }"
            "QGroupBox { border: 1px solid #E0E0E0; border-radius: 4px; "
            "padding: 12px; margin-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; "
            "padding: 4px 8px; font-weight: bold; color: #37474F; }"
        )

        # Fixed width
        self.setFixedWidth(240)

    def _create_state_section(self) -> QGroupBox:
        """Create safety state indicator section."""
        group = QGroupBox("Current State")
        layout = QVBoxLayout()

        # State indicator (shape + text)
        state_layout = QHBoxLayout()
        self.state_icon = QLabel("●")  # Circle for SAFE, will update for others
        self.state_icon.setStyleSheet("font-size: 14px; color: #4CAF50;")  # Green
        state_layout.addWidget(self.state_icon)

        self.state_label = QLabel("SAFE")
        self.state_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4CAF50;")
        state_layout.addWidget(self.state_label)
        state_layout.addStretch()

        layout.addLayout(state_layout)
        group.setLayout(layout)
        return group

    def _create_interlock_section(self) -> QGroupBox:
        """Create interlock status section."""
        group = QGroupBox("Interlocks")
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Footpedal
        self.footpedal_status = self._create_status_item("Footpedal", "NOT READY")
        layout.addWidget(self.footpedal_status)

        # Smoothing motor
        self.smoothing_status = self._create_status_item("Smoothing", "NOT READY")
        layout.addWidget(self.smoothing_status)

        # Photodiode
        self.photodiode_status = self._create_status_item("Photodiode", "NOT READY")
        layout.addWidget(self.photodiode_status)

        # Watchdog
        self.watchdog_status = self._create_status_item("Watchdog", "NOT READY")
        layout.addWidget(self.watchdog_status)

        group.setLayout(layout)
        return group

    def _create_status_item(self, label: str, initial_status: str) -> QWidget:
        """
        Create a status item widget (icon + label + status).

        Args:
            label: Item name (e.g., "Footpedal")
            initial_status: Initial status text (e.g., "NOT READY")

        Returns:
            QWidget containing status item layout
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Status icon (checkmark/X/warning)
        icon = QLabel("✗")  # Red X by default
        icon.setStyleSheet("font-size: 14px; color: #F44336;")
        icon.setObjectName(f"{label}_icon")
        layout.addWidget(icon)

        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setStyleSheet("font-size: 10pt; color: #424242;")
        layout.addWidget(label_widget)

        # Status text
        status = QLabel(initial_status)
        status.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F44336;")
        status.setObjectName(f"{label}_status")
        layout.addWidget(status)

        layout.addStretch()
        widget.setLayout(layout)

        # Store references for updates
        setattr(self, f"{label.lower()}_icon", icon)
        setattr(self, f"{label.lower()}_status_text", status)

        return widget

    def _create_power_section(self) -> QGroupBox:
        """Create laser power monitoring section."""
        group = QGroupBox("Power Status")
        layout = QVBoxLayout()

        # Current power
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current:"))
        self.current_power_label = QLabel("0.0W")
        self.current_power_label.setStyleSheet("font-weight: bold;")
        current_layout.addWidget(self.current_power_label)
        current_layout.addStretch()
        layout.addLayout(current_layout)

        # Limit power
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Limit:"))
        self.limit_power_label = QLabel("10.0W")
        self.limit_power_label.setStyleSheet("font-weight: bold;")
        limit_layout.addWidget(self.limit_power_label)
        limit_layout.addStretch()
        layout.addLayout(limit_layout)

        # Progress bar
        self.power_progress = QProgressBar()
        self.power_progress.setMinimum(0)
        self.power_progress.setMaximum(100)
        self.power_progress.setValue(0)
        self.power_progress.setTextVisible(True)
        self.power_progress.setFormat("%p%")
        self.power_progress.setStyleSheet(
            "QProgressBar { "
            "  border: 1px solid #BDBDBD; "
            "  border-radius: 4px; "
            "  background-color: #E0E0E0; "
            "  text-align: center; "
            "  height: 20px; "
            "}"
            "QProgressBar::chunk { "
            "  background-color: #4CAF50; "
            "  border-radius: 3px; "
            "}"
        )
        layout.addWidget(self.power_progress)

        group.setLayout(layout)
        return group

    def _create_session_section(self) -> QGroupBox:
        """Create session information section."""
        group = QGroupBox("Session")
        layout = QVBoxLayout()

        self.session_info_label = QLabel("No active session")
        self.session_info_label.setStyleSheet(
            "font-size: 10pt; color: #757575; padding: 4px;"
        )
        self.session_info_label.setWordWrap(True)
        layout.addWidget(self.session_info_label)

        group.setLayout(layout)
        return group

    def set_safety_manager(self, manager: SafetyManager) -> None:
        """Connect safety manager and subscribe to signals."""
        self.safety_manager = manager
        manager.safety_state_changed.connect(self._update_safety_state)
        logger.info("Safety panel connected to safety manager")

    def set_gpio_controller(self, controller) -> None:
        """Connect GPIO controller for interlock monitoring."""
        self.gpio_controller = controller
        # Connect interlock signals
        controller.safety_interlock_changed.connect(self._update_interlock_status)
        logger.info("Safety panel connected to GPIO controller")

    def set_laser_controller(self, controller) -> None:
        """Connect laser controller for power monitoring."""
        self.laser_controller = controller
        # Connect power change signal
        controller.power_changed.connect(self._update_power_status)
        logger.info("Safety panel connected to laser controller")

    @pyqtSlot(object)
    def _update_safety_state(self, state: SafetyState) -> None:
        """Update safety state display."""
        if state == SafetyState.SAFE:
            self.state_icon.setText("●")  # Circle
            self.state_icon.setStyleSheet("font-size: 14px; color: #4CAF50;")
            self.state_label.setText("SAFE")
            self.state_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4CAF50;")
        elif state == SafetyState.UNSAFE:
            self.state_icon.setText("▲")  # Triangle
            self.state_icon.setStyleSheet("font-size: 14px; color: #FF9800;")
            self.state_label.setText("UNSAFE")
            self.state_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FF9800;")
        else:  # EMERGENCY_STOP
            self.state_icon.setText("■")  # Square
            self.state_icon.setStyleSheet("font-size: 14px; color: #F44336;")
            self.state_label.setText("E-STOP")
            self.state_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F44336;")

    @pyqtSlot(dict)
    def _update_interlock_status(self, interlocks: dict) -> None:
        """Update interlock status display."""
        # Update footpedal
        if interlocks.get("footpedal", False):
            self.footpedal_icon.setText("✓")
            self.footpedal_icon.setStyleSheet("font-size: 14px; color: #4CAF50;")
            self.footpedal_status_text.setText("PRESSED")
            self.footpedal_status_text.setStyleSheet("font-size: 10pt; font-weight: bold; color: #4CAF50;")
        else:
            self.footpedal_icon.setText("✗")
            self.footpedal_icon.setStyleSheet("font-size: 14px; color: #F44336;")
            self.footpedal_status_text.setText("NOT PRESSED")
            self.footpedal_status_text.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F44336;")

        # Update smoothing (similar pattern)
        # Update photodiode (similar pattern)
        # Update watchdog (similar pattern)

    @pyqtSlot(float)
    def _update_power_status(self, power_watts: float) -> None:
        """Update laser power display."""
        self.current_power_label.setText(f"{power_watts:.1f}W")

        # Update progress bar (assuming 10W limit)
        limit = 10.0
        percentage = int((power_watts / limit) * 100)
        self.power_progress.setValue(percentage)

        # Change color based on percentage
        if percentage < 80:
            color = "#4CAF50"  # Green
        elif percentage < 100:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red

        self.power_progress.setStyleSheet(
            f"QProgressBar {{ border: 1px solid #BDBDBD; border-radius: 4px; "
            f"background-color: #E0E0E0; text-align: center; height: 20px; }} "
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}"
        )

    def update_session_info(self, session_text: str) -> None:
        """Update session information display."""
        self.session_info_label.setText(session_text)
        if "No active session" in session_text:
            self.session_info_label.setStyleSheet("font-size: 10pt; color: #757575; padding: 4px;")
        else:
            self.session_info_label.setStyleSheet("font-size: 10pt; color: #1976D2; font-weight: bold; padding: 4px;")
```

#### Step 2: Integrate Safety Panel into Main Window (60 min)
**Location:** `main_window.py`, Lines 231-243 (`_init_ui()` method)

**Current Code:**
```python
layout = QVBoxLayout()
central_widget.setLayout(layout)

# Title removed - redundant with window title bar

self.tabs = QTabWidget()
layout.addWidget(self.tabs)
```

**Updated Code:**
```python
# Main layout with horizontal split (tabs | safety panel)
main_layout = QHBoxLayout()
central_widget.setLayout(main_layout)

# Tab container (left side - 80% width)
self.tabs = QTabWidget()
main_layout.addWidget(self.tabs, stretch=4)  # 80% width

# Always-visible safety panel (right side - 20% width)
from ui.widgets.always_visible_safety_panel import AlwaysVisibleSafetyPanel

self.safety_panel = AlwaysVisibleSafetyPanel()
main_layout.addWidget(self.safety_panel, stretch=0)  # Fixed width (240px)
```

#### Step 3: Connect Safety Panel Signals (30 min)
**Location:** `main_window.py`, in `_connect_safety_system()` method (Lines 807-838)

**Add after Line 826:**
```python
# Connect safety panel to system components
if hasattr(self, "safety_panel") and self.safety_panel:
    # Connect safety manager
    self.safety_panel.set_safety_manager(self.safety_manager)

    # Connect GPIO controller (when available)
    if hasattr(self.safety_widget, "gpio_widget") and self.safety_widget.gpio_widget:
        gpio_controller = self.safety_widget.gpio_widget.controller
        if gpio_controller:
            self.safety_panel.set_gpio_controller(gpio_controller)

    # Connect laser controller
    if hasattr(self, "laser_controller") and self.laser_controller:
        self.safety_panel.set_laser_controller(self.laser_controller)

    logger.info("Safety panel connected to all system components")
```

#### Step 4: Update Safety Panel on Session Changes (30 min)
**Location:** `main_window.py`, modify `_on_session_started()` method

**Add after session start logic:**
```python
# Update safety panel session display
if hasattr(self, "safety_panel") and self.safety_panel:
    session_text = (
        f"Subject: {session.subject_code}\n"
        f"Tech: {session.tech_name}\n"
        f"Duration: 00:00:00"
    )
    self.safety_panel.update_session_info(session_text)
```

**Add to `_on_session_ended()` handler:**
```python
# Reset safety panel session display
if hasattr(self, "safety_panel") and self.safety_panel:
    self.safety_panel.update_session_info("No active session")
```

#### Step 5: Testing (60 min)
- [ ] Launch app: Safety panel visible on right side
- [ ] Panel width: 240px (fixed, doesn't resize)
- [ ] Safety state: Shows "SAFE" with green circle initially
- [ ] Interlocks: All show red X and "NOT READY"
- [ ] Power: Shows 0.0W current, 10.0W limit, 0% progress bar
- [ ] Session: Shows "No active session"
- [ ] Start session: Session section updates with subject/tech/duration
- [ ] Connect GPIO: Interlocks update to reflect actual status
- [ ] Enable laser: Power section updates with current power
- [ ] Trigger E-Stop: Safety state changes to red square "E-STOP"
- [ ] Switch tabs: Panel remains visible and unchanged
- [ ] End session: Session section resets to "No active session"

### Acceptance Criteria
- [ ] Safety panel visible on right side at all times (240px width)
- [ ] Panel shows current safety state with color-coded icon
- [ ] Displays all 4 interlocks (footpedal, smoothing, photodiode, watchdog)
- [ ] Shows current laser power vs. limit with progress bar
- [ ] Shows active session information (subject, tech, duration)
- [ ] Updates in real-time when safety state changes
- [ ] Updates in real-time when interlocks change
- [ ] Updates in real-time when laser power changes
- [ ] Panel scrollable if content exceeds vertical space
- [ ] No layout issues (tabs still fully functional)
- [ ] Panel uses consistent styling (white background, grouped sections)

### Testing Checklist
- [ ] Launch app, verify panel visible and positioned correctly
- [ ] Test with different window sizes (1920x1080, 1280x800)
- [ ] Connect hardware, verify interlock updates
- [ ] Start session, verify session info appears
- [ ] Enable laser, verify power monitoring works
- [ ] Trigger E-Stop, verify state changes immediately
- [ ] Switch between all 3 tabs, verify panel remains visible
- [ ] End session, verify session info clears
- [ ] Test with long subject IDs/tech names (text wrapping)

### Rollback Plan
If issues occur:
1. Remove import of `AlwaysVisibleSafetyPanel` from `main_window.py`
2. Revert main layout changes (restore QVBoxLayout)
3. Remove signal connections in `_connect_safety_system()`
4. Delete `always_visible_safety_panel.py` file
5. Verify application launches without the panel

---

## TASK T5: Workflow Step Indicator

### Priority: MEDIUM (Usability Enhancement)

### Time Estimate: 4 hours

### Description
Add visual step indicator at the top of Treatment Workflow tab showing progression through:
1. Select Subject
2. Load Protocol
3. Begin Treatment

This improves user guidance and reduces workflow confusion.

### Dependencies
- None (standalone feature)

### Files to Create
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/workflow_step_indicator.py` (new file)

### Files to Modify
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py` (Lines 355-427)
2. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/treatment_setup_widget.py` (add protocol_loaded signal)

### Implementation Steps

#### Step 1: Create WorkflowStepIndicator Widget (120 min)
**Location:** New file `workflow_step_indicator.py`

See Mockup #5 for full widget implementation details.

**Key Methods:**
- `__init__()`: Create 3 step widgets with arrows
- `set_step(step: int)`: Update visual state based on current step (1, 2, or 3)
- `_create_step_widget()`: Build individual step container
- `_update_step_styling()`: Apply pending/active/complete styling

#### Step 2: Add protocol_loaded Signal to TreatmentSetupWidget (30 min)
**Location:** `treatment_setup_widget.py`

**Add Signal:**
```python
class TreatmentSetupWidget(QWidget):
    protocol_loaded = pyqtSignal(str)  # protocol_path
```

**Emit Signal When Protocol Loaded:**
```python
# In load protocol method (after successful load)
self.protocol_loaded.emit(protocol_path)
logger.info(f"Protocol loaded signal emitted: {protocol_path}")
```

#### Step 3: Integrate Step Indicator into Treatment Tab (60 min)
**Location:** `main_window.py`, Lines 355-427

**Add after Line 370:**
```python
# Workflow step indicator at top of left column
from ui.widgets.workflow_step_indicator import WorkflowStepIndicator

self.workflow_steps = WorkflowStepIndicator()
left_layout.addWidget(self.workflow_steps)

# Add spacing
left_layout.addSpacing(16)
```

#### Step 4: Connect Workflow Signals (30 min)
**Location:** `main_window.py`, after widget creation

**Add Connections:**
```python
# Connect workflow progression signals
self.subject_widget.session_started.connect(
    lambda: self.workflow_steps.set_step(2)  # Move to step 2 (Load Protocol)
)

self.treatment_setup_widget.protocol_loaded.connect(
    lambda: self.workflow_steps.set_step(3)  # Move to step 3 (Begin Treatment)
)

# Reset to step 1 when session ends
self.subject_widget.session_ended.connect(
    lambda: self.workflow_steps.set_step(1)
)
```

#### Step 5: Testing (30 min)
- [ ] Launch app: Step indicator shows all 3 steps, step 1 active
- [ ] Create subject and start session: Step 2 becomes active, step 1 shows checkmark
- [ ] Load protocol: Step 3 becomes active, step 2 shows checkmark
- [ ] End session: All steps reset to pending, step 1 active
- [ ] Switch tabs: Indicator only visible in Treatment Workflow tab

### Acceptance Criteria
- [ ] Step indicator visible at top of Treatment Workflow tab
- [ ] Shows 3 steps: "Select Subject", "Load Protocol", "Begin Treatment"
- [ ] Step 1 active by default (blue background)
- [ ] Step 2 becomes active after session starts
- [ ] Step 3 becomes active after protocol loads
- [ ] Completed steps show green checkmark icon
- [ ] Arrows connect steps visually
- [ ] Each step is approximately 200px wide, 80px tall
- [ ] Indicator updates automatically based on user actions
- [ ] Steps reset to pending when session ends

### Testing Checklist
- [ ] Launch app, verify indicator shows step 1 active
- [ ] Start session, verify step 2 becomes active
- [ ] Load protocol, verify step 3 becomes active
- [ ] End session, verify all steps reset
- [ ] Test with rapid session start/end cycles
- [ ] Verify no console errors during step transitions

### Rollback Plan
If issues occur:
1. Remove `workflow_step_indicator.py` import from `main_window.py`
2. Remove step indicator widget creation and signal connections
3. Remove `protocol_loaded` signal from `treatment_setup_widget.py`
4. Verify Treatment Workflow tab still functions normally

---

## TASK T6: Design Token System

### Priority: MEDIUM (Foundation for Consistency)

### Time Estimate: 8.5 hours

### Description
Create centralized design token system (colors, typography, spacing) and migrate existing widgets to use it. This establishes foundation for visual consistency and easier theming.

### Dependencies
- None (can be implemented independently)
- Recommended first for other tasks to build upon

### Files to Create
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/design_tokens.py` (new file)

### Files to Modify (Migration)
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py` (toolbar buttons, status bar)
2. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/subject_widget.py` (buttons, input fields)
3. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py` (buttons, labels)

### Implementation Steps

#### Phase 1: Create design_tokens.py (60 min)
See Mockup #6 for full token definitions.

**Key Components:**
- `Colors` class: All color constants
- `Typography` class: Font size/weight scales
- `Spacing` class: Margin/padding values
- `ButtonSizes` class: Standard button heights
- `button_style()` helper function
- `input_style()` helper function

#### Phase 2: Migrate E-Stop Button (30 min)
**Location:** `main_window.py`, Lines 527-537

**Replace hard-coded colors:**
```python
from ui.design_tokens import Colors, ButtonSizes, button_style

self.global_estop_btn.setStyleSheet(
    button_style(
        bg_color=Colors.EMERGENCY,
        text_color=Colors.PANEL,
        hover_color="#B71C1C",
        size="emergency"
    )
)
```

#### Phase 3: Migrate Toolbar Buttons (60 min)
**Location:** `main_window.py`, Lines 541-591

**Migrate Connect All, Disconnect All, Test All buttons to use tokens.**

#### Phase 4: Migrate Subject Widget Buttons (60 min)
**Location:** `subject_widget.py`, Lines 97-107

**Migrate Search, Create, View Sessions buttons to use tokens.**

#### Phase 5: Migrate Camera Widget (90 min)
**Location:** `camera_widget.py`

**Migrate all button styling and color definitions to use tokens.**

#### Phase 6: Documentation and Testing (90 min)
- Document token usage patterns
- Test all migrated widgets for visual consistency
- Verify no regressions in styling

### Acceptance Criteria
- [ ] `design_tokens.py` created with all token classes
- [ ] Helper functions `button_style()` and `input_style()` working
- [ ] E-Stop button migrated to use tokens (visual appearance unchanged)
- [ ] Toolbar buttons migrated to use tokens
- [ ] Subject widget buttons migrated to use tokens
- [ ] Camera widget buttons migrated to use tokens
- [ ] No hard-coded color values in migrated code
- [ ] Application launches without errors
- [ ] All UI elements render correctly with tokens

### Testing Checklist
- [ ] Launch app, verify all buttons render correctly
- [ ] Test button hover states
- [ ] Test button disabled states
- [ ] Verify no visual regressions (compare before/after screenshots)
- [ ] Test with different themes (if applicable)
- [ ] Verify console shows no import errors

### Migration Guidelines

**Before:**
```python
button.setStyleSheet(
    "background-color: #1976D2; color: white; padding: 8px 16px;"
)
```

**After:**
```python
from ui.design_tokens import Colors, button_style

button.setStyleSheet(
    button_style(bg_color=Colors.PRIMARY, text_color=Colors.PANEL, size="secondary")
)
```

### Rollback Plan
If issues occur:
1. Remove `design_tokens.py` import from migrated files
2. Restore original hard-coded styling
3. Delete `design_tokens.py` file
4. Verify application functions with original styling

---

## Implementation Timeline

### Sprint 1 (Days 1-2): Quick Wins + Foundation
- **Day 1 Morning:** T6 - Create design token system (4 hours)
- **Day 1 Afternoon:** T1 - Enlarge E-Stop button (30 min) + T6 - Migrate E-Stop to tokens (30 min)
- **Day 2 Morning:** T2 - Improve Subject ID input (2 hours)
- **Day 2 Afternoon:** T6 - Continue token migration (2 hours)

**Deliverables:** E-Stop enlarged, Subject ID improved, design tokens established

### Sprint 2 (Days 3-4): Critical Safety Features
- **Day 3 Morning:** T3 - Persistent session indicator (3 hours)
- **Day 3 Afternoon:** T4 - Always-visible safety panel (Part 1: 2.5 hours)
- **Day 4:** T4 - Always-visible safety panel (Part 2: 2.5 hours + testing)

**Deliverables:** Session traceability, always-visible safety monitoring

### Sprint 3 (Day 5): Polish + Testing
- **Day 5 Morning:** T5 - Workflow step indicator (4 hours)
- **Day 5 Afternoon:** Final integration testing, bug fixes

**Deliverables:** Complete UI/UX improvements, tested and validated

---

## Success Metrics

### Usability Improvements
- [ ] Subject ID input errors reduced by >50% (fewer validation errors)
- [ ] Session traceability: 100% of sessions have visible indicators
- [ ] E-Stop activation time: <1 second (larger button improves speed)

### Safety Improvements
- [ ] Critical safety info visible: 100% uptime (always-visible panel)
- [ ] Interlock status visibility: Improved from 1 tab to all tabs

### Developer Experience
- [ ] Design consistency: >90% of widgets use design tokens
- [ ] Code maintainability: Single source of truth for colors/spacing
- [ ] Reduced technical debt: No hard-coded style values in new code

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Layout issues with right panel | High | Medium | Test on multiple resolutions, add minimum width constraints |
| Timer performance issues (session duration) | Low | Low | Use lightweight QTimer with 1-second interval |
| Signal connection failures | Medium | Low | Add try-except blocks, log connection attempts |
| Hard-coded color migration incomplete | Low | Medium | Audit code for #hex values after token migration |
| Validation logic breaks existing input | Medium | Low | Preserve existing validation, add real-time layer on top |

---

## Post-Implementation Tasks

1. **User Testing** (2 hours)
   - Test with actual technicians
   - Collect feedback on workflow improvements
   - Identify any remaining usability issues

2. **Documentation Updates** (1 hour)
   - Update UI screenshots in docs
   - Update TECHNICIAN_SETUP.md with new workflows
   - Document design token usage patterns

3. **Code Review** (2 hours)
   - Review all changed files
   - Verify no regressions
   - Check for remaining hard-coded values

4. **Performance Testing** (1 hour)
   - Measure UI responsiveness
   - Check timer CPU usage (session duration)
   - Verify no memory leaks from new widgets

---

## Appendix: File Modification Summary

### Files Created (3 new files)
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/design_tokens.py`
2. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/always_visible_safety_panel.py`
3. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/workflow_step_indicator.py`

### Files Modified (3 existing files)
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
   - Lines 527-537: E-Stop button (T1)
   - Lines 595-661: Status bar with session indicator (T3)
   - Lines 231-243: Main layout with safety panel (T4)
   - Lines 355-427: Treatment tab with workflow steps (T5)

2. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/subject_widget.py`
   - Lines 73-107: Subject ID input and buttons (T2)

3. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/treatment_setup_widget.py`
   - Add `protocol_loaded` signal (T5)

### Total Lines of Code
- **New code:** ~800 lines (3 new widgets + token system)
- **Modified code:** ~150 lines (existing file updates)
- **Total:** ~950 lines

---

**Document Version:** 1.0
**Last Updated:** 2025-11-05
**Author:** UI/UX Implementation Team
