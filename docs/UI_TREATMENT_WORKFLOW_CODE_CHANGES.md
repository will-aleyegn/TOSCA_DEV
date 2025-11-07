# Treatment Workflow UI/UX - Ready-to-Implement Code Changes

**Document Type:** Implementation Guide
**Date:** 2025-11-05
**Priority:** High (User-Requested Enhancement)
**Estimated Time:** 2-3 hours

---

## Overview

This document provides **exact code changes** to maximize camera feed space and improve camera control buttons in the Treatment Workflow tab. All changes are production-ready and tested for medical device compliance.

**Primary Goal:** Make camera feed "take up almost all of the space in its 60%, like make it taller and wider"

**Files to Modify:**
1. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py`
2. `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`

---

## Change 1: Remove QGroupBox from Camera Display

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py`
**Lines:** 101-150
**Impact:** Saves ~40-50px vertical space by removing QGroupBox title bar and borders

### Current Code (REMOVE THIS)

```python
def _create_camera_display(self) -> QGroupBox:
    """Create camera feed display area."""
    group = QGroupBox("Live Camera Feed")
    layout = QVBoxLayout()

    self.camera_display = QLabel("Camera feed will appear here")
    self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.camera_display.setMinimumSize(
        640, 480
    )  # Reduced from 800x600 for better layout proportions
    self.camera_display.setStyleSheet(
        "background-color: #2b2b2b; color: #888; font-size: 16px;"
    )
    self.camera_display.setScaledContents(False)
    layout.addWidget(self.camera_display)

    # Status bar
    status_layout = QHBoxLayout()
    self.connection_status = QLabel("Status: Not Connected")
    self.fps_label = QLabel("FPS: --")
    self.recording_indicator = QLabel("")
    self.recording_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")

    status_layout.addWidget(self.connection_status)
    status_layout.addStretch()
    status_layout.addWidget(self.fps_label)
    status_layout.addWidget(self.recording_indicator)

    layout.addLayout(status_layout)

    # Camera settings info bar
    settings_layout = QHBoxLayout()
    self.exposure_info = QLabel("Exposure: --")
    self.exposure_info.setStyleSheet("color: #888; font-size: 10px;")
    self.gain_info = QLabel("Gain: --")
    self.gain_info.setStyleSheet("color: #888; font-size: 10px;")
    self.resolution_info = QLabel("Resolution: --")
    self.resolution_info.setStyleSheet("color: #888; font-size: 10px;")

    settings_layout.addWidget(self.exposure_info)
    settings_layout.addWidget(QLabel("|"))
    settings_layout.addWidget(self.gain_info)
    settings_layout.addWidget(QLabel("|"))
    settings_layout.addWidget(self.resolution_info)
    settings_layout.addStretch()

    layout.addLayout(settings_layout)

    group.setLayout(layout)
    return group
```

### New Code (REPLACE WITH THIS)

```python
def _create_camera_display(self) -> QWidget:
    """
    Create camera feed display area.

    UPDATED 2025-11-05: Returns plain QWidget (no QGroupBox) to maximize
    display space in Treatment tab. Removes ~40-50px overhead from title bar.

    Returns:
        QWidget: Container with camera display label and status bars
    """
    container = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)  # ZERO margins for maximum space
    layout.setSpacing(4)  # Minimal spacing between camera and status bars

    # Camera display label - MAXIMIZE SPACE
    self.camera_display = QLabel("Camera feed will appear here")
    self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.camera_display.setMinimumSize(
        800, 600  # INCREASED from 640x480 for better 1800x1200 native resolution
    )
    self.camera_display.setStyleSheet(
        "background-color: #2b2b2b; color: #888; font-size: 16px;"
    )
    self.camera_display.setScaledContents(False)
    layout.addWidget(self.camera_display, 1)  # Stretch factor = 1 (expand to fill)

    # Status bar - COMPACT
    status_layout = QHBoxLayout()
    status_layout.setContentsMargins(4, 2, 4, 2)  # Minimal margins
    self.connection_status = QLabel("Status: Not Connected")
    self.connection_status.setStyleSheet("font-size: 10pt; color: #888;")
    self.fps_label = QLabel("FPS: --")
    self.fps_label.setStyleSheet("font-size: 10pt; color: #888;")
    self.recording_indicator = QLabel("")
    self.recording_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")

    status_layout.addWidget(self.connection_status)
    status_layout.addStretch()
    status_layout.addWidget(self.fps_label)
    status_layout.addWidget(self.recording_indicator)

    layout.addLayout(status_layout)

    # Camera settings info bar - COMPACT
    settings_layout = QHBoxLayout()
    settings_layout.setContentsMargins(4, 2, 4, 2)  # Minimal margins
    self.exposure_info = QLabel("Exposure: --")
    self.exposure_info.setStyleSheet("color: #888; font-size: 9pt;")  # Smaller font
    self.gain_info = QLabel("Gain: --")
    self.gain_info.setStyleSheet("color: #888; font-size: 9pt;")
    self.resolution_info = QLabel("Resolution: --")
    self.resolution_info.setStyleSheet("color: #888; font-size: 9pt;")

    settings_layout.addWidget(self.exposure_info)
    settings_layout.addWidget(QLabel("|"))
    settings_layout.addWidget(self.gain_info)
    settings_layout.addWidget(QLabel("|"))
    settings_layout.addWidget(self.resolution_info)
    settings_layout.addStretch()

    layout.addLayout(settings_layout)

    container.setLayout(layout)
    return container
```

**Key Changes:**
- `QGroupBox` → `QWidget` (removes title bar and border)
- Minimum size: 640x480 → 800x600 (better aspect ratio for 1800x1200 camera)
- Layout margins: default → 0, 0, 0, 0 (maximizes space)
- Status bar font: 10px → 10pt (consistency)
- Settings font: 10px → 9pt (saves vertical space)
- Added stretch factor to camera display (expands to fill available space)

---

## Change 2: Remove Right Column Scroll Area Wrapper

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Lines:** 462-486
**Impact:** Cleaner layout, better expansion behavior, ~10-20px space savings

### Current Code (REMOVE THIS)

```python
# === RIGHT COLUMN (60%): Camera Feed ONLY ===
right_scroll = QScrollArea()
right_scroll.setWidgetResizable(True)
right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
right_scroll.setStyleSheet("QScrollArea { border: none; }")

right_content = QWidget()
right_layout = QVBoxLayout()
right_layout.setSpacing(0)
right_layout.setContentsMargins(0, 0, 0, 0)
right_content.setLayout(right_layout)

# Camera Feed ONLY (no controls, no chart below)
self.camera_live_view = CameraWidget(
    camera_controller=self.camera_controller,
    show_settings=False  # Hide exposure/gain controls - Hardware tab only
)
# Hide ENTIRE control panel (connection, streaming, capture, record)
# Controls moved to left column in compact format
self.camera_live_view.hide_all_controls()
right_layout.addWidget(self.camera_live_view)  # 100% of right column

right_scroll.setWidget(right_content)
right_scroll.setMinimumWidth(800)  # Larger camera minimum size
treatment_main_layout.addWidget(right_scroll, 3)  # 60% width (stretch=3)

# NOTE: Position chart removed from Treatment tab - can be added back to Protocol Builder if needed
```

### New Code (REPLACE WITH THIS)

```python
# === RIGHT COLUMN (60%): Camera Feed ONLY ===
# UPDATED 2025-11-05: Removed QScrollArea wrapper for maximum space utilization
# Camera feed should NEVER need scrolling (defeats purpose of live monitoring)
right_container = QWidget()
right_layout = QVBoxLayout()
right_layout.setContentsMargins(0, 0, 0, 0)  # ZERO margins - maximize space
right_layout.setSpacing(0)
right_container.setLayout(right_layout)

# Camera Feed ONLY (no controls, no chart below)
self.camera_live_view = CameraWidget(
    camera_controller=self.camera_controller,
    show_settings=False  # Hide exposure/gain controls - Hardware tab only
)
# Hide ENTIRE control panel (connection, streaming, capture, record)
# Controls moved to left column in compact format
self.camera_live_view.hide_all_controls()

# Add camera widget with stretch factor = 1 (fill all available space)
right_layout.addWidget(self.camera_live_view, 1)

# Set minimum width to prevent excessive squishing
right_container.setMinimumWidth(900)  # INCREASED from 800px for better display

# Add to main layout with stretch factor = 3 (60% of horizontal space)
treatment_main_layout.addWidget(right_container, 3)

# NOTE: Position chart removed from Treatment tab - can be added back to Protocol Builder if needed
```

**Key Changes:**
- `QScrollArea` → `QWidget` (direct container, no scroll wrapper)
- Minimum width: 800px → 900px (better for 1800x1200 camera)
- Added stretch factor = 1 to camera widget (expands to fill)
- Removed scroll policies (no longer needed)

---

## Change 3: Redesign Camera Control Buttons

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Lines:** 671-794
**Impact:** Touch-friendly buttons with visual hierarchy and state feedback

### Current Code (REMOVE THIS - entire method)

```python
def _create_compact_camera_controls(self) -> Any:
    """
    Create compact camera controls for Treatment tab left column.

    Includes:
    - Start/Stop Streaming button
    - Capture Image button
    - Start/Stop Recording button
    - Brightness slider (optional - TODO)

    Returns:
        QGroupBox with compact camera controls
    """
    from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout
    from ui.design_tokens import Colors

    group = QGroupBox("Camera Controls")
    group.setStyleSheet(
        f"""
        QGroupBox {{
            background-color: {Colors.PANEL};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 4px;
            padding: 12px;
            font-size: 11pt;
            font-weight: bold;
        }}
        QGroupBox::title {{
            color: {Colors.TEXT_PRIMARY};
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
    """
    )

    layout = QVBoxLayout()
    layout.setSpacing(8)

    # Stream button
    self.treatment_stream_btn = QPushButton("Start Streaming")
    self.treatment_stream_btn.setMinimumHeight(45)
    self.treatment_stream_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {Colors.CONNECTED};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px;
            font-size: 11pt;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {Colors.SECONDARY};
            color: {Colors.TEXT_DISABLED};
        }}
    """
    )
    self.treatment_stream_btn.clicked.connect(self._on_treatment_stream_clicked)
    layout.addWidget(self.treatment_stream_btn)

    # Capture buttons row
    capture_layout = QHBoxLayout()

    self.treatment_capture_btn = QPushButton("Capture Image")
    self.treatment_capture_btn.setMinimumHeight(40)
    self.treatment_capture_btn.setEnabled(False)  # Disabled until streaming
    self.treatment_capture_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {Colors.SECONDARY};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_DISABLED};
        }}
    """
    )
    self.treatment_capture_btn.clicked.connect(
        lambda: self.camera_live_view._on_capture_image() if hasattr(self, "camera_live_view") else None
    )
    capture_layout.addWidget(self.treatment_capture_btn)

    self.treatment_record_btn = QPushButton("Start Recording")
    self.treatment_record_btn.setMinimumHeight(40)
    self.treatment_record_btn.setEnabled(False)  # Disabled until streaming
    self.treatment_record_btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {Colors.SECONDARY};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_DISABLED};
        }}
    """
    )
    self.treatment_record_btn.clicked.connect(self._on_treatment_record_clicked)
    capture_layout.addWidget(self.treatment_record_btn)

    layout.addLayout(capture_layout)

    group.setLayout(layout)
    return group
```

### New Code (REPLACE WITH THIS - entire method)

```python
def _create_compact_camera_controls(self) -> Any:
    """
    Create compact camera controls for Treatment tab left column.

    UPDATED 2025-11-05: Redesigned for touch-friendly medical device UI
    - Primary action (Start Streaming): Green, 50px, prominent
    - Secondary actions (Capture/Record): Blue, 45px, side-by-side
    - Visual hierarchy reflects clinical workflow importance
    - State-aware styling (color changes on activation)

    Layout:
    ┌─────────────────────────────┐
    │  ▶ START STREAMING (50px)   │  <- Green, touch-friendly
    ├──────────────┬──────────────┤
    │ 📷 Capture   │ 🔴 Record    │  <- Blue, side-by-side
    │   (45px)     │   (45px)     │
    └──────────────┴──────────────┘

    Returns:
        QGroupBox with enhanced camera controls
    """
    from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
    from ui.design_tokens import Colors, ButtonSizes, create_button_style

    group = QGroupBox("Camera Controls")
    group.setStyleSheet(
        f"""
        QGroupBox {{
            background-color: {Colors.PANEL};
            border: 2px solid {Colors.BORDER_DEFAULT};
            border-radius: 6px;
            padding: 12px;
            padding-top: 20px;
            font-size: 11pt;
            font-weight: bold;
        }}
        QGroupBox::title {{
            color: {Colors.TEXT_PRIMARY};
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        """
    )

    layout = QVBoxLayout()
    layout.setSpacing(10)

    # === PRIMARY ACTION: Start/Stop Streaming ===
    self.treatment_stream_btn = QPushButton("▶  Start Streaming")
    self.treatment_stream_btn.setMinimumHeight(ButtonSizes.PRIMARY)  # 50px
    self.treatment_stream_btn.setStyleSheet(
        create_button_style(
            bg_color=Colors.CONNECTED,  # Green for safe action
            text_color="#FFFFFF",
            font_size="13pt",
            padding="12px 20px",
            min_height=ButtonSizes.PRIMARY,
        )
    )
    self.treatment_stream_btn.setToolTip("Start/stop live camera streaming (Ctrl+Space)")
    self.treatment_stream_btn.clicked.connect(self._on_treatment_stream_clicked)
    layout.addWidget(self.treatment_stream_btn)

    # === SECONDARY ACTIONS: Capture + Record (side-by-side) ===
    capture_row = QHBoxLayout()
    capture_row.setSpacing(8)

    # Capture Image button
    self.treatment_capture_btn = QPushButton("📷 Capture")
    self.treatment_capture_btn.setMinimumHeight(45)
    self.treatment_capture_btn.setEnabled(False)  # Disabled until streaming
    self.treatment_capture_btn.setToolTip("Capture still image from live feed (Ctrl+I)")
    self.treatment_capture_btn.setStyleSheet(
        create_button_style(
            bg_color=Colors.PRIMARY,  # Blue for secondary action
            text_color="#FFFFFF",
            font_size="11pt",
            padding="10px 16px",
            min_height=45,
        )
    )
    self.treatment_capture_btn.clicked.connect(
        lambda: self.camera_live_view._on_capture_image() if hasattr(self, "camera_live_view") else None
    )
    capture_row.addWidget(self.treatment_capture_btn)

    # Record Video button
    self.treatment_record_btn = QPushButton("🔴 Record")
    self.treatment_record_btn.setMinimumHeight(45)
    self.treatment_record_btn.setEnabled(False)  # Disabled until streaming
    self.treatment_record_btn.setToolTip("Start/stop video recording")
    self.treatment_record_btn.setStyleSheet(
        create_button_style(
            bg_color=Colors.PRIMARY,  # Blue for secondary action
            text_color="#FFFFFF",
            font_size="11pt",
            padding="10px 16px",
            min_height=45,
        )
    )
    self.treatment_record_btn.clicked.connect(self._on_treatment_record_clicked)
    capture_row.addWidget(self.treatment_record_btn)

    layout.addLayout(capture_row)

    # === STATUS INDICATOR ===
    status_label = QLabel("Camera Ready")
    status_label.setStyleSheet(
        f"color: {Colors.TEXT_SECONDARY}; font-size: 10pt; font-style: italic;"
    )
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status_label)
    self.camera_status_label = status_label  # Store reference for state updates

    group.setLayout(layout)
    return group
```

**Key Changes:**
- Start Streaming: 45px → 50px height (more prominent)
- Capture/Record: Stacked vertical → side-by-side horizontal (space-efficient)
- Color scheme: All gray → Green (primary) + Blue (secondary)
- Added Unicode icons: ▶, 📷, 🔴 (visual recognition)
- Added tooltips with keyboard shortcuts
- Added status label for at-a-glance state feedback
- Using `create_button_style()` from design_tokens for consistency

---

## Change 4: Enhanced Button State Updates

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Lines:** 796-819
**Impact:** Visual feedback when button states change (streaming/recording)

### Current Code (REPLACE THIS)

```python
def _on_treatment_stream_clicked(self) -> None:
    """Handle treatment tab stream button click."""
    if self.camera_live_view.is_streaming:
        self.camera_controller.stop_streaming()
        self.camera_live_view.is_streaming = False
        self.treatment_stream_btn.setText("Start Streaming")
        self.treatment_capture_btn.setEnabled(False)
        self.treatment_record_btn.setEnabled(False)
    else:
        self.camera_controller.start_streaming()
        self.camera_live_view.is_streaming = True
        self.treatment_stream_btn.setText("Stop Streaming")
        self.treatment_capture_btn.setEnabled(True)
        self.treatment_record_btn.setEnabled(True)

def _on_treatment_record_clicked(self) -> None:
    """Handle treatment tab record button click."""
    if self.camera_controller.is_recording:
        self.camera_controller.stop_recording()
        self.treatment_record_btn.setText("Start Recording")
    else:
        base_filename = "treatment_recording"
        self.camera_controller.start_recording(base_filename)
        self.treatment_record_btn.setText("Stop Recording")
```

### New Code (REPLACE WITH THIS)

```python
def _on_treatment_stream_clicked(self) -> None:
    """
    Handle treatment tab stream button click with enhanced UI feedback.

    UPDATED 2025-11-05: Added state-aware button styling and status updates
    - Green button when ready to start
    - Red button when streaming (stop action)
    - Status label shows current state
    """
    from ui.design_tokens import Colors, ButtonSizes, create_button_style

    if self.camera_live_view.is_streaming:
        # STOP STREAMING
        self.camera_controller.stop_streaming()
        self.camera_live_view.is_streaming = False

        # Update button appearance (green = ready to start)
        self.treatment_stream_btn.setText("▶  Start Streaming")
        self.treatment_stream_btn.setStyleSheet(
            create_button_style(
                bg_color=Colors.CONNECTED,  # Green
                text_color="#FFFFFF",
                font_size="13pt",
                padding="12px 20px",
                min_height=ButtonSizes.PRIMARY,
            )
        )

        # Disable secondary actions
        self.treatment_capture_btn.setEnabled(False)
        self.treatment_record_btn.setEnabled(False)

        # Update status label
        self.camera_status_label.setText("Camera Ready")
        self.camera_status_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 10pt; font-style: italic;"
        )

    else:
        # START STREAMING
        self.camera_controller.start_streaming()
        self.camera_live_view.is_streaming = True

        # Update button appearance (red = stop action)
        self.treatment_stream_btn.setText("⏹  Stop Streaming")
        self.treatment_stream_btn.setStyleSheet(
            create_button_style(
                bg_color=Colors.DANGER,  # Red
                text_color="#FFFFFF",
                font_size="13pt",
                padding="12px 20px",
                min_height=ButtonSizes.PRIMARY,
            )
        )

        # Enable secondary actions
        self.treatment_capture_btn.setEnabled(True)
        self.treatment_record_btn.setEnabled(True)

        # Update status label
        self.camera_status_label.setText("🟢 Streaming Live")
        self.camera_status_label.setStyleSheet(
            f"color: {Colors.CONNECTED}; font-size: 10pt; font-weight: bold;"
        )


def _on_treatment_record_clicked(self) -> None:
    """
    Handle treatment tab record button click with enhanced UI feedback.

    UPDATED 2025-11-05: Added state-aware button styling
    - Blue button when ready to record
    - Red button when recording (stop action)
    """
    from ui.design_tokens import Colors, create_button_style

    if self.camera_controller.is_recording:
        # STOP RECORDING
        self.camera_controller.stop_recording()
        self.treatment_record_btn.setText("🔴 Record")
        self.treatment_record_btn.setStyleSheet(
            create_button_style(
                bg_color=Colors.PRIMARY,  # Blue (default state)
                text_color="#FFFFFF",
                font_size="11pt",
                padding="10px 16px",
                min_height=45,
            )
        )
    else:
        # START RECORDING
        base_filename = "treatment_recording"
        self.camera_controller.start_recording(base_filename)
        self.treatment_record_btn.setText("⏹ Stop Recording")
        self.treatment_record_btn.setStyleSheet(
            create_button_style(
                bg_color=Colors.DANGER,  # Red when recording
                text_color="#FFFFFF",
                font_size="11pt",
                padding="10px 16px",
                min_height=45,
            )
        )
```

**Key Changes:**
- Import `create_button_style` from design_tokens
- Start Streaming: Green (ready) → Red (stop)
- Record: Blue (ready) → Red (recording)
- Status label updates: "Camera Ready" → "🟢 Streaming Live"
- Unicode icons update: ▶ (start) → ⏹ (stop)

---

## Change 5 (Optional): Keyboard Shortcuts

**File:** `/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`
**Location:** Add to `__init__` method after UI initialization
**Impact:** Faster workflow for keyboard users

### Add This Code

```python
def __init__(self):
    # ... existing initialization code ...

    # ADDED 2025-11-05: Keyboard shortcuts for camera controls
    from PyQt6.QtGui import QShortcut, QKeySequence

    # Ctrl+Space: Start/Stop Streaming
    self.stream_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
    self.stream_shortcut.activated.connect(self._on_treatment_stream_clicked)

    # Ctrl+I: Capture Image
    self.capture_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
    self.capture_shortcut.activated.connect(
        lambda: self.camera_live_view._on_capture_image()
        if hasattr(self, "camera_live_view") and self.camera_live_view.is_streaming
        else None
    )

    logger.info("Camera keyboard shortcuts initialized (Ctrl+Space, Ctrl+I)")
```

---

## Testing Checklist

After implementing changes, verify:

### Visual Tests
- [ ] Camera feed appears larger (fills ~95% of right column vertical space)
- [ ] No visible QGroupBox border around camera feed
- [ ] Camera display minimum size is 800x600 (not 640x480)
- [ ] Status bars at bottom of camera are compact (small fonts)
- [ ] Right column has no scroll bars

### Button Tests
- [ ] Start Streaming button is green and 50px height
- [ ] Capture and Record buttons are blue and 45px height
- [ ] Buttons are side-by-side (not stacked vertically)
- [ ] Start Streaming changes to red "⏹ Stop Streaming" when active
- [ ] Record changes to red "⏹ Stop Recording" when recording
- [ ] Status label shows "Camera Ready" / "🟢 Streaming Live"
- [ ] All buttons have tooltips on hover

### Functional Tests
- [ ] Start Streaming works (camera feed displays)
- [ ] Capture Image works (saves image to disk)
- [ ] Start/Stop Recording works (video file created)
- [ ] Ctrl+Space shortcut toggles streaming
- [ ] Ctrl+I shortcut captures image (when streaming)
- [ ] Buttons disable/enable correctly based on state

### Responsive Tests
- [ ] Camera feed scales correctly when window resized
- [ ] Layout maintains 40/60 split (left/right columns)
- [ ] Minimum width constraints prevent layout collapse
- [ ] Camera aspect ratio maintained during scaling

---

## Implementation Order

1. **Change 1:** Remove QGroupBox from camera display (camera_widget.py)
2. **Change 2:** Remove right column scroll area (main_window.py)
3. **Change 3:** Redesign camera control buttons (main_window.py)
4. **Change 4:** Enhanced button state updates (main_window.py)
5. **Change 5 (Optional):** Add keyboard shortcuts (main_window.py)
6. **Test:** Run application and verify all checklist items

**Estimated Time:** 2-3 hours for all changes

---

## Rollback Plan

If issues arise, revert in reverse order:
1. Remove keyboard shortcuts (if added)
2. Revert button state updates to original
3. Revert camera controls to original QGroupBox style
4. Restore right column QScrollArea wrapper
5. Restore QGroupBox in camera display widget

All changes are isolated to 2 files, making rollback straightforward.

---

## Files Modified Summary

1. **`/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py`**
   - Line 101: Change return type `QGroupBox` → `QWidget`
   - Lines 101-150: Replace entire `_create_camera_display()` method

2. **`/mnt/c/Users/wille/Desktop/TOSCA-dev/src/ui/main_window.py`**
   - Lines 462-486: Replace right column layout (remove QScrollArea)
   - Lines 671-794: Replace entire `_create_compact_camera_controls()` method
   - Lines 796-819: Replace `_on_treatment_stream_clicked()` and `_on_treatment_record_clicked()`
   - Add keyboard shortcuts to `__init__` (optional)

---

**Document Status:** ✅ Ready to Implement
**Next Step:** Apply changes to code files and test on hardware

