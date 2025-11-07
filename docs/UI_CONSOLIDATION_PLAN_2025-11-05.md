# UI Consolidation: Unified Top Header Implementation Plan

**Date:** 2025-11-05
**Version:** v0.9.14-alpha (planned)
**Risk Level:** MEDIUM-HIGH (major architectural change, safety-critical)
**Status:** PLANNING COMPLETE - Awaiting Approval

---

## Executive Summary

**Goal:** Replace fragmented persistent UI elements (toolbar, right panel, status bar) with a single unified top header containing all critical information.

**Impact:**
- Reclaim ~400px of screen space (80px toolbar + 300px right panel + 25px statusbar → 80px header)
- Consolidate scattered information into ONE authoritative location
- Cleaner, more focused interface for medical device operators

**Timeline:** 9 hours estimated (can be split across multiple sessions)

---

## Current Architecture Problems

```
┌─────────────────────────────────────────────────────────────┐
│  TOOLBAR (80px) - E-Stop, Connect All, Test All            │
└─────────────────────────────────────────────────────────────┘
┌──────────────────────────────────┬──────────────────────────┐
│                                  │  RIGHT PANEL (300px)     │
│  TAB CONTENT                     │  - Safety Status         │
│                                  │  - Interlocks            │
│                                  │  - Event Log             │
└──────────────────────────────────┴──────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  STATUS BAR (25px) - Hardware status, Research mode        │
└─────────────────────────────────────────────────────────────┘

PROBLEMS:
- Information scattered across 3 locations (top, right, bottom)
- Screen space fragmented
- Toolbar buttons rarely used
- Right panel takes 20% of horizontal space
- Status bar too prominent for minor info
```

---

## Desired End State

```
┌─────────────────────────────────────────────────────────────┐
│  UNIFIED HEADER (80px height)                               │
│  [E-STOP] | Workflow Steps | Safety Status | Research Mode │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Tabs: [Hardware Diagnostics] [Treatment] [Protocol]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         FULL-WIDTH CONTENT                                  │
│         (Maximum vertical + horizontal space)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

BENEFITS:
- All persistent info in ONE location (top)
- Maximum work area (full width, full height)
- Consistent header across all tabs
- Cleaner, more professional appearance
```

---

## Component Breakdown

### Unified Header Widget (80px height, full width)

```
┌────────────┬─────────────────┬─────────────────┬──────────────┐
│  E-STOP    │  WORKFLOW       │  SAFETY STATUS  │  RESEARCH    │
│  (120px)   │  (350px)        │  (300px)        │  (150px)     │
│            │                 │                 │              │
│ [EMERGENCY │  Step 1 → 2 → 3 │  UNSAFE         │  ⚠ Research │
│  STOP]     │  Hardware       │  X Footpedal    │  Mode Only   │
│            │  Treatment      │  X Smoothing    │              │
│            │  Protocol       │  X Photodiode   │              │
│            │                 │  X Watchdog     │              │
└────────────┴─────────────────┴─────────────────┴──────────────┘
       ↑              ↑                 ↑               ↑
    #C62828      Click to      Updates in         Static
   (muted red)   navigate       real-time         warning
```

---

## Implementation Phases

### PHASE 1: Preparation

**Step 1:** Create Design Tokens File
```python
# File: src/ui/design_tokens.py

class Colors:
    # Muted Color Palette (Professional Medical Device Theme)
    CRITICAL_RED = "#C62828"      # E-Stop, critical errors
    UNSAFE_RED = "#D32F2F"        # Unsafe state
    WARNING_ORANGE = "#F57C00"    # Research mode, warnings
    SAFE_GREEN = "#388E3C"        # Safe state, valid
    INFO_BLUE = "#1976D2"         # Active controls, info
    TREATING_BLUE = "#0277BD"     # Treating state
    BG_DARK = "#1E1E1E"           # Main background
    BG_PANEL = "#2B2B2B"          # Panel background
    TEXT_PRIMARY = "#E0E0E0"      # Primary text
    TEXT_SECONDARY = "#9E9E9E"    # Secondary text
    DISABLED_GRAY = "#616161"     # Disabled controls
```

**Step 2:** Test design tokens import in main_window.py

**Step 3:** Verify no import conflicts

---

### PHASE 2: Build UnifiedHeaderWidget

**File:** `src/ui/widgets/unified_header_widget.py`

**Architecture:**
```python
class UnifiedHeaderWidget(QWidget):
    # Signals
    e_stop_clicked = pyqtSignal()
    step_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_estop_section()      # 120px
        self._create_workflow_section()   # 350px
        self._create_safety_section()     # 300px
        self._create_research_badge()     # 150px
        self._setup_layout()

    # Slots
    @pyqtSlot(SafetyState)
    def update_safety_state(self, state):
        """Update safety status display"""

    @pyqtSlot(dict)
    def update_interlock_status(self, interlocks):
        """Update interlock indicators"""

    @pyqtSlot(int)
    def set_workflow_step(self, step):
        """Update current workflow step"""
```

**Sub-Components:**

1. **E-Stop Button Section**
   - QPushButton: "EMERGENCY STOP"
   - Size: 120x60px
   - Background: #C62828 (muted red)
   - Tooltip: "Emergency stop - press F12 or click"
   - Signal: clicked → e_stop_clicked

2. **Workflow Step Indicator**
   - Reuse existing WorkflowStepIndicator
   - 3 steps: Hardware → Treatment → Protocol
   - Clickable for navigation
   - Current step highlighted in blue

3. **Safety Status Section**
   - Compact display of SafetyStatusPanel
   - State text (SAFE/UNSAFE/TREATING)
   - 4 interlock icons: Footpedal, Smoothing, Photodiode, Watchdog
   - Color-coded background (green/orange/red)

4. **Research Mode Badge**
   - Static QLabel
   - Text: "⚠ Research Mode Only"
   - Background: #F57C00 (muted orange)
   - Tooltip: "NOT for clinical use - v0.9.14-alpha"

**Layout:**
```python
layout = QHBoxLayout()
layout.addWidget(self.estop_button)     # 120px fixed
layout.addSpacing(10)
layout.addWidget(self.workflow_widget)  # 350px fixed
layout.addStretch()                     # Flexible space
layout.addWidget(self.safety_widget)    # 300px fixed
layout.addSpacing(10)
layout.addWidget(self.research_badge)   # 150px fixed
```

---

### PHASE 3: Refactor main_window.py

**Critical Steps (Sequential Order):**

**Step 13:** BACKUP main_window.py
```bash
cp src/ui/main_window.py src/ui/main_window.py.backup_20251105
```

**Step 14-16:** Comment out old components
```python
# COMMENTED OUT - Toolbar
# def _create_toolbar(self):
#     toolbar = QToolBar()
#     ... [~100 lines]

# COMMENTED OUT - Right Panel
# def _create_right_panel(self):
#     panel = SafetyStatusPanel()
#     ... [~50 lines]

# COMMENTED OUT - Status Bar
# self.statusBar().addWidget(...)
# ... [~20 lines]
```

**Step 17:** Add unified header to layout
```python
def __init__(self):
    # ... existing code ...

    # Create unified header
    self.unified_header = UnifiedHeaderWidget()

    # Add to main layout (at top)
    main_layout = QVBoxLayout()
    main_layout.addWidget(self.unified_header)  # NEW
    main_layout.addWidget(self.tab_widget)

    central_widget.setLayout(main_layout)
```

**Step 18:** Wire signals
```python
# E-Stop
self.unified_header.e_stop_clicked.connect(self._on_global_estop_clicked)

# Workflow navigation
self.unified_header.step_changed.connect(self._on_workflow_step_clicked)

# Safety updates
self.safety_manager.safety_state_changed.connect(
    self.unified_header.update_safety_state
)
self.safety_manager.interlock_status_changed.connect(
    self.unified_header.update_interlock_status
)

# Tab changes update workflow
self.tab_widget.currentChanged.connect(
    lambda idx: self.unified_header.set_workflow_step(idx + 1)
)
```

**Step 19:** Update tab layout
```python
# Remove right panel from splitter
# OLD:
splitter = QSplitter(Qt.Horizontal)
splitter.addWidget(tab_content)
splitter.addWidget(right_panel)
splitter.setSizes([700, 300])

# NEW:
layout.addWidget(tab_content)  # Full width
```

**Step 20:** Test application startup

**Step 21:** Remove commented code if everything works

**Step 22:** Move connection buttons to Hardware tab
```python
# In hardware_diagnostics_tab.py
connection_buttons_layout = QHBoxLayout()
connection_buttons_layout.addWidget(QPushButton("[CONN] Connect All"))
connection_buttons_layout.addWidget(QPushButton("Disconnect All"))
connection_buttons_layout.addWidget(QPushButton("[TEST] Test All"))
tab_layout.insertLayout(0, connection_buttons_layout)  # At top of tab
```

---

### PHASE 4: Update Tab Layouts

**Files to Modify:**

1. **treatment_setup_widget.py**
   - Remove right panel from layout
   - Expand camera feed to full width
   - Benefits: Larger camera view, more control space

2. **hardware_diagnostics_tab** (in main_window.py)
   - Remove right panel from layout
   - Add connection buttons at top
   - Expand diagnostic panel to full width

3. **protocol_builder_widget.py**
   - Remove right panel from layout
   - Expand protocol sequence list
   - Benefits: More room for action list

---

### PHASE 5: Apply Color Palette

**Update Stylesheets:**

```python
# E-Stop button
self.estop_button.setStyleSheet(f"""
    QPushButton {{
        background-color: {Colors.CRITICAL_RED};
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 4px;
    }}
    QPushButton:hover {{
        background-color: #B71C1C;
    }}
""")

# Safety status (UNSAFE state)
self.safety_widget.setStyleSheet(f"""
    QWidget {{
        background-color: {Colors.WARNING_ORANGE};
        border-radius: 4px;
        padding: 8px;
    }}
""")

# Research badge
self.research_badge.setStyleSheet(f"""
    QLabel {{
        background-color: {Colors.WARNING_ORANGE};
        color: white;
        font-weight: bold;
        padding: 8px;
        border-radius: 4px;
    }}
""")
```

---

### PHASE 6: Testing & Validation

**Test Matrix:**

| Category | Test | Expected Result | Pass/Fail |
|----------|------|-----------------|-----------|
| Visual | Header visible on all tabs | Consistent across 3 tabs | [ ] |
| Visual | Color contrast (WCAG AA) | 4.5:1 minimum ratio | [ ] |
| Visual | Layout on 1366x768 | No overflow, readable | [ ] |
| Visual | Layout on 1920x1080 | Proper spacing, centered | [ ] |
| Functional | E-Stop button click | Triggers safety manager | [ ] |
| Functional | Workflow step click | Navigates to correct tab | [ ] |
| Functional | Safety status updates | Real-time state changes | [ ] |
| Functional | Interlock indicators | Reflect GPIO status | [ ] |
| Safety | E-Stop signal connection | Identical to old toolbar | [ ] |
| Safety | Hardware E-Stop test | Disables laser immediately | [ ] |
| Regression | All tabs load | No crashes or errors | [ ] |
| Regression | Hardware controllers | All work unchanged | [ ] |
| Regression | Protocol execution | Works as before | [ ] |

---

## Risk Mitigation

### Risk 1: Breaking Safety-Critical Signals

**Severity:** CRITICAL
**Probability:** LOW
**Mitigation:**
- Keep all safety_manager signal connections identical to current implementation
- Test E-Stop with actual hardware connected
- Maintain backup of main_window.py for rollback

**Validation:**
```python
# Log all signal connections for debugging
logger.debug(f"E-Stop connected: {self.unified_header.e_stop_clicked.is_connected()}")
logger.debug(f"Safety state connected: {self.safety_manager.safety_state_changed.receivers()}")
```

### Risk 2: Layout Issues on Different Screen Sizes

**Severity:** MEDIUM
**Probability:** MEDIUM
**Mitigation:**
- Use fixed widths for header components (responsive in v2.0)
- Test on minimum supported resolution (1366x768)
- Add scroll bars if content overflows

**Fallback:** Add responsive layout logic if fixed widths cause issues

### Risk 3: Widget Lifecycle/Parent Issues

**Severity:** LOW
**Probability:** LOW
**Mitigation:**
- Properly set parent widgets in all constructors
- Use `deleteLater()` for cleanup
- Monitor widget count for memory leaks

**Validation:**
```python
# Check widget count before/after tab changes
initial_count = len(QApplication.allWidgets())
# ... navigate tabs ...
final_count = len(QApplication.allWidgets())
assert final_count <= initial_count + 10  # Allow some variance
```

### Risk 4: Signal Connection Conflicts

**Severity:** MEDIUM
**Probability:** LOW
**Mitigation:**
- Disconnect old signals before connecting new ones
- Use unique signal names to avoid conflicts
- Log all signal connections for debugging

### Risk 5: Right Panel Removal Breaks Existing Code

**Severity:** HIGH
**Probability:** MEDIUM
**Mitigation:**
- Search codebase for all references to `right_panel`
- Update all dependencies to use `unified_header` instead
- Test each tab individually after changes

**Search Pattern:**
```bash
grep -r "right_panel" src/ui/
grep -r "safety_status_panel" src/ui/
grep -r "getRightPanel" src/ui/
```

---

## File Organization

### Files to Create

```
src/ui/design_tokens.py                    [NEW] Color palette constants (80 lines)
src/ui/widgets/unified_header_widget.py    [NEW] Main header widget (350 lines)
```

### Files to Modify (MAJOR)

```
src/ui/main_window.py                      [MAJOR] Remove toolbar/right panel/statusbar
                                                  (~200 lines removed, ~50 lines added)
```

### Files to Modify (MINOR)

```
src/ui/widgets/treatment_setup_widget.py   [MINOR] Remove right panel layout (~10 lines)
src/ui/widgets/protocol_builder_widget.py  [MINOR] Remove right panel layout (~10 lines)
```

### Files to Reference (Read-Only)

```
src/ui/widgets/workflow_step_indicator.py  [READ] Reuse design pattern
src/ui/widgets/safety_status_panel.py      [READ] Adapt for compact version
src/core/safety.py                         [READ] Safety signals/states
```

---

## Success Criteria

### Must Have (v1.0)

- [x] Single unified top header across all tabs
- [x] E-Stop button accessible and functional
- [x] Workflow steps visible and clickable
- [x] Safety status always visible
- [x] Research mode warning visible
- [x] Full-width tab content
- [x] No crashes or errors
- [x] All safety signals working

### Nice to Have (v1.1+)

- [ ] Keyboard shortcut for E-Stop (F12)
- [ ] Responsive header layout (adapts to small screens)
- [ ] Animated workflow step transitions
- [ ] Tooltip guidance for new users
- [ ] Session ID display in header
- [ ] Hardware connection icons (camera, laser, actuator)

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review plan with stakeholders
- [ ] Create git backup branch: `git checkout -b ui-consolidation-backup`
- [ ] Backup main_window.py manually
- [ ] Verify test environment ready

### Phase 1: Preparation
- [ ] Create design_tokens.py with color palette
- [ ] Test import in main_window.py
- [ ] Verify no conflicts

### Phase 2: Build Widget
- [ ] Create unified_header_widget.py
- [ ] Implement E-Stop section
- [ ] Implement Workflow section
- [ ] Implement Safety section
- [ ] Implement Research badge
- [ ] Wire layout
- [ ] Add signals/slots
- [ ] Test widget in isolation

### Phase 3: Refactor Main Window
- [ ] Comment out toolbar code
- [ ] Comment out right panel code
- [ ] Comment out status bar code
- [ ] Add unified header to layout
- [ ] Wire E-Stop signal
- [ ] Wire workflow signals
- [ ] Wire safety signals
- [ ] Test application startup
- [ ] Remove commented code
- [ ] Move connection buttons

### Phase 4: Update Tabs
- [ ] Update treatment tab layout
- [ ] Update hardware tab layout
- [ ] Update protocol tab layout
- [ ] Add connection buttons to hardware tab
- [ ] Test each tab individually

### Phase 5: Colors
- [ ] Apply colors to E-Stop
- [ ] Apply colors to safety status
- [ ] Apply colors to research badge
- [ ] Test contrast (WCAG AA)

### Phase 6: Testing
- [ ] Visual regression (screenshots)
- [ ] Functional testing (all features)
- [ ] Safety testing (E-Stop, interlocks)
- [ ] Edge case testing (errors, failures)
- [ ] Performance testing (startup, responsiveness)

### Post-Implementation
- [ ] Take screenshots for documentation
- [ ] Update UI_UX_DESIGN_GUIDE.md
- [ ] Create PR with detailed description
- [ ] Request code review
- [ ] Merge to main after approval

---

## Rollback Plan

**If critical issues found:**

1. **Stop implementation immediately**
2. **Restore backup:**
   ```bash
   cp src/ui/main_window.py.backup_20251105 src/ui/main_window.py
   git checkout -- src/ui/widgets/unified_header_widget.py
   git checkout -- src/ui/design_tokens.py
   ```
3. **Clean Python cache:**
   ```bash
   find src -name "*.pyc" -delete
   find src -type d -name "__pycache__" -exec rm -rf {} +
   ```
4. **Test application:**
   ```bash
   ./venv/Scripts/python.exe src/main.py
   ```
5. **Document issue in GitHub**
6. **Schedule bug fix session**

---

## Next Steps

1. **Review this plan** - Ensure all stakeholders agree
2. **Set implementation session** - Block 9 hours or split across days
3. **Begin Phase 1** - Create design tokens
4. **Checkpoint after each phase** - Test before moving forward
5. **Document changes** - Screenshot before/after for each phase

---

**Plan Status:** READY FOR APPROVAL
**Estimated Duration:** 9 hours (split across sessions recommended)
**Risk Level:** MEDIUM-HIGH (major change, but well-planned)
**Confidence:** HIGH (detailed plan with clear rollback)

---

**Document Version:** 1.0
**Created:** 2025-11-05
**Author:** AI Assistant (Claude Code) + Zen Planner (Gemini 2.5 Pro)
**Reviewed:** [Pending]
**Approved:** [Pending]
