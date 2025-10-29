# UI Changes: Treatment Workflow Camera Integration

**Date:** 2025-10-29
**Issue:** Camera integration on Treatment Workflow tab
**Status:** ✅ Complete

---

## Problem Statement

The Treatment Workflow tab had several usability issues with camera integration:

1. **No streaming controls** - Start/Stop streaming button was hidden
2. **Cramped layout** - Camera feed shared horizontal space with subject selection (33%/66% split)
3. **Poor visibility** - Small camera display area
4. **Controls squished** - Camera controls panel too narrow, especially on window resize
5. **No scrolling** - Content could get squished when window resized

## Solution: 2-Column Scrollable Layout

### Layout Transformation

**Before:**
```
┌─────────────────────────────────────────┐
│ [Subject 33%] [Camera 66%]             │ ← Horizontal, sharing top
│─────────────────────────────────────────│
│ [Treatment Setup/Active]                 │
└─────────────────────────────────────────┘
```

**After:**
```
┌──────────────────┬─────────────────────────────┐
│ Left Column 40%  │ Right Column 60%            │
│ [Scrollable]     │ [Scrollable]                │
│                  │                             │
│ Subject          │ ┌───────────────────────┐   │
│ Selection        │ │                       │   │
│                  │ │   LARGE CAMERA FEED   │   │
│ Treatment        │ │                       │   │
│ Setup/Active     │ │   (Full column)       │   │
│                  │ └───────────────────────┘   │
│                  │ [Connect Camera]            │
│                  │ [Start/Stop Streaming] ✓    │
│                  │ Camera Settings             │
│                  │ Capture Controls            │
└──────────────────┴─────────────────────────────┘
```

### Implementation Details

**File Modified:** `src/ui/main_window.py` (lines 187-267)

**Key Changes:**

1. **2-Column Layout with Scroll Areas**
   ```python
   # Left Column (40% width, stretch=2)
   left_scroll = QScrollArea()
   left_scroll.setMinimumWidth(400)
   treatment_main_layout.addWidget(left_scroll, 2)

   # Right Column (60% width, stretch=3)
   right_scroll = QScrollArea()
   right_scroll.setMinimumWidth(640)  # Camera minimum
   treatment_main_layout.addWidget(right_scroll, 3)
   ```

2. **Streaming Controls Visible**
   ```python
   # Before:
   self.camera_live_view.hide_connection_controls()

   # After:
   # NOT hiding controls - users need streaming during treatment
   ```

3. **Hardware Tab Scrolling Pattern**
   ```python
   scroll.setWidgetResizable(True)
   scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
   scroll.setStyleSheet("QScrollArea { border: none; }")
   ```

### Benefits

✅ **Camera prominence** - Full 60% column dedicated to camera feed
✅ **Streaming controls** - Start/Stop streaming button now visible
✅ **No squishing** - Scroll areas prevent controls from being compressed
✅ **Responsive** - Minimum widths prevent excessive compression
✅ **Consistent pattern** - Matches Hardware tab scrolling implementation

### Widget Organization

**Left Column:**
- Subject Selection Widget
- Treatment Stack (Setup ↔ Active views)
- Independent scrolling

**Right Column:**
- Camera Widget (full height)
  - Large feed display (640x480 minimum)
  - Connection controls (Connect Camera)
  - Streaming controls (Start/Stop Streaming)
  - Camera settings (exposure, gain)
  - Capture/recording controls
- Independent scrolling

### Technical Notes

**Layout Hierarchy:**
```
TreatmentWorkflowTab
└── QHBoxLayout (main)
    ├── QScrollArea (left, stretch=2)
    │   └── QVBoxLayout
    │       ├── SubjectWidget
    │       ├── QStackedWidget (treatment_stack)
    │       │   ├── TreatmentSetupWidget (index 0)
    │       │   └── ActiveTreatmentWidget (index 1)
    │       └── addStretch()
    └── QScrollArea (right, stretch=3)
        └── QVBoxLayout
            ├── CameraWidget (with visible controls)
            └── addStretch()
```

**Preserved Functionality:**
- Subject selection and session management
- Treatment setup → active transition (QStackedWidget)
- Camera controller integration
- Dev mode signals
- Active treatment monitoring
- All existing signals/slots

### User Workflow Impact

**Improved:**
- Camera feed much more prominent during treatment
- Users can start/stop streaming without switching tabs
- Better visibility for alignment verification
- No need to resize window to see camera properly

**Unchanged:**
- Subject selection process
- Protocol loading and execution
- Session management
- Hardware connection (still managed in Hardware tab)

---

## Testing

**Verified:**
- ✅ Application launches without errors
- ✅ 2-column layout renders correctly (40:60 ratio)
- ✅ Scrolling works when window resized small
- ✅ Streaming controls visible (Connect + Start/Stop buttons)
- ✅ Camera feed displays prominently
- ✅ All workflow functionality preserved

---

## Related Documentation

- `docs/architecture/01_system_overview.md` - System architecture
- `src/ui/main_window.py` - Main window implementation
- `src/ui/widgets/camera_widget.py` - Camera widget
- `PROJECT_STATUS.md` - Project milestones

---

**Status:** ✅ Complete
**Committed:** 2025-10-29
**Tested:** ✅ Application launches and renders correctly
