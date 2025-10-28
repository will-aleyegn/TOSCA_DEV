# Hardware Tab Enhancements - Implementation Plan

**Created:** 2025-10-28
**Status:** Planning Phase (Implementation Pending User Feedback)
**Related Files:** `src/ui/main_window.py`, `src/ui/widgets/*_widget.py`

---

## Overview

Three enhancements to improve Hardware & Diagnostics tab usability and diagnostics:
1. **Connection Status Indicators** - Visual feedback on section headers
2. **Test All Button** - Automated hardware diagnostic check
3. **Hardware Info Cards** - Display device details and metadata

---

## Enhancement 1: Connection Status Indicators in Headers

### Goal
Add real-time connection status to each section header (✓ connected, ✗ disconnected) with color changes.

### Visual Design

**Before:**
```
📷 Camera System
```

**After (Disconnected):**
```
📷 Camera System ✗
[Gray/Red background]
```

**After (Connected):**
```
📷 Camera System ✓
[Green background]
```

### Implementation Tasks

#### Task 1.1: Modify Section Headers
**File:** `src/ui/main_window.py`

**Current code (line 120):**
```python
camera_header = QLabel("📷 Camera System")
```

**New code:**
```python
self.camera_header = QLabel("📷 Camera System ✗")
self.camera_header.setObjectName("camera_header")  # For easy reference
```

**Apply to all 5 headers:**
- `self.camera_header` - Camera System
- `self.actuator_header` - Linear Actuator Controller
- `self.laser_header` - Laser Systems
- `self.smoothing_header` - Laser Spot Smoothing Device
- `self.photodiode_header` - Photodiode Power Monitor

#### Task 1.2: Create Header Update Methods
**File:** `src/ui/main_window.py`

```python
def _update_camera_header_status(self, connected: bool) -> None:
    """Update camera section header with connection status."""
    if connected:
        self.camera_header.setText("📷 Camera System ✓")
        self.camera_header.setStyleSheet(
            "font-size: 13px; font-weight: bold; padding: 8px; margin-top: 4px; "
            "background-color: #2E7D32; color: white; border-radius: 3px;"  # Green
        )
    else:
        self.camera_header.setText("📷 Camera System ✗")
        self.camera_header.setStyleSheet(
            "font-size: 13px; font-weight: bold; padding: 8px; margin-top: 4px; "
            "background-color: #37474F; color: #64B5F6; border-radius: 3px;"  # Gray
        )

# Repeat for _update_actuator_header_status, _update_laser_header_status, etc.
```

#### Task 1.3: Wire Connection Signals
**File:** `src/ui/main_window.py`

**In existing connection methods:**
```python
# In camera connection handler:
self._update_camera_header_status(connected)

# In laser widget connection signal:
self.laser_widget.connection_changed.connect(self._update_laser_header_status)

# In actuator widget connection signal:
self.actuator_widget.connection_changed.connect(self._update_actuator_header_status)

# In GPIO connection handler:
# Update both smoothing and photodiode headers (same connection)
self._update_smoothing_header_status(connected)
self._update_photodiode_header_status(connected)
```

### Files to Modify
- `src/ui/main_window.py` (primary changes)
- Possibly add connection signals to widgets that don't have them

### Estimated Effort
- **Complexity:** Low-Medium
- **Lines of Code:** ~100-150
- **Time:** 30-45 minutes

---

## Enhancement 2: Test All Button

### Goal
Single-click hardware diagnostic that tests all components sequentially and reports status.

### Visual Design

**Button Location:** Global toolbar (after Disconnect All button)

```
[🔌 Connect All] [Disconnect All] | [🧪 Test All Hardware]
```

**Test Results Dialog:**
```
┌─────────────────────────────────────────┐
│   Hardware Diagnostic Results          │
├─────────────────────────────────────────┤
│ 📷 Camera System          ✓ PASS        │
│    - Resolution: 1920x1080              │
│    - FPS: 30.0                          │
│                                         │
│ 🔧 Linear Actuator        ✓ PASS        │
│    - Position: 0.0 mm                   │
│    - Range: 0-50 mm                     │
│                                         │
│ ⚡ Laser Systems           ✗ FAIL        │
│    - Aiming: Connected                  │
│    - Treatment: Not connected           │
│                                         │
│ 🌀 Smoothing Device       ✓ PASS        │
│    - Voltage: 1.5V                      │
│    - Vibration: 2.1g                    │
│                                         │
│ 📡 Photodiode Monitor     ✓ PASS        │
│    - Voltage: 0.02V                     │
│    - Power: 0.5 µW                      │
│                                         │
│ Overall: 4/5 PASSED                     │
├─────────────────────────────────────────┤
│              [Close]                    │
└─────────────────────────────────────────┘
```

### Implementation Tasks

#### Task 2.1: Add Test All Button
**File:** `src/ui/main_window.py` (in `_init_toolbar()`)

```python
# After disconnect_all_btn
toolbar.addSeparator()

self.test_all_btn = QPushButton("🧪 Test All Hardware")
self.test_all_btn.setMinimumHeight(35)
self.test_all_btn.setStyleSheet(
    "QPushButton { background-color: #6A1B9A; color: white; "
    "padding: 6px 12px; font-weight: bold; }"
    "QPushButton:hover { background-color: #4A148C; }"
)
self.test_all_btn.setToolTip("Run diagnostic check on all hardware components")
self.test_all_btn.clicked.connect(self._on_test_all_clicked)
toolbar.addWidget(self.test_all_btn)
```

#### Task 2.2: Implement Test Sequence
**File:** `src/ui/main_window.py`

```python
def _on_test_all_clicked(self) -> None:
    """Run diagnostic test on all hardware."""
    logger.info("Starting hardware diagnostic test...")

    # Create results dict
    test_results = {
        "camera": self._test_camera(),
        "actuator": self._test_actuator(),
        "laser": self._test_laser(),
        "gpio": self._test_gpio(),
    }

    # Show results dialog
    self._show_test_results_dialog(test_results)

def _test_camera(self) -> dict:
    """Test camera system."""
    result = {
        "name": "📷 Camera System",
        "passed": False,
        "details": []
    }

    if self.camera_widget and self.camera_widget.is_connected:
        result["passed"] = True
        if hasattr(self.camera_widget, "current_fps"):
            result["details"].append(f"FPS: {self.camera_widget.current_fps:.1f}")
        # Add more details...
    else:
        result["details"].append("Not connected")

    return result

# Similar methods: _test_actuator(), _test_laser(), _test_gpio()
```

#### Task 2.3: Create Test Results Dialog
**File:** `src/ui/dialogs/hardware_test_dialog.py` (NEW FILE)

```python
class HardwareTestDialog(QDialog):
    """Display hardware diagnostic test results."""

    def __init__(self, test_results: dict, parent=None):
        super().__init__(parent)
        self.test_results = test_results
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Hardware Diagnostic Results")
        layout = QVBoxLayout()

        # Add result for each component
        for component, result in self.test_results.items():
            layout.addWidget(self._create_result_widget(result))

        # Add overall summary
        layout.addWidget(self._create_summary())

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
```

### Files to Create
- `src/ui/dialogs/hardware_test_dialog.py` (NEW)

### Files to Modify
- `src/ui/main_window.py`

### Estimated Effort
- **Complexity:** Medium
- **Lines of Code:** ~200-250
- **Time:** 60-90 minutes

---

## Enhancement 3: Hardware Info Cards

### Goal
Display device metadata (serial numbers, firmware versions, last calibration) below each section header.

### Visual Design

**Camera Section Example:**
```
┌──────────────────────────────────────────────┐
│ 📷 Camera System ✓                           │
├──────────────────────────────────────────────┤
│ Model: Allied Vision 1800 U-158c             │
│ Serial: AV158C-20231015-001                  │
│ Firmware: v2.1.3                             │
│ Resolution: 1920x1080                        │
│ Last Calibration: 2025-10-15                 │
└──────────────────────────────────────────────┘
[Connect] [Disconnect]
```

### Implementation Tasks

#### Task 3.1: Create HardwareInfoCard Widget
**File:** `src/ui/widgets/hardware_info_card.py` (NEW FILE)

```python
class HardwareInfoCard(QWidget):
    """
    Display hardware device information.

    Shows:
    - Model name
    - Serial number
    - Firmware version
    - Device-specific info
    - Last calibration date
    """

    def __init__(self, component_name: str):
        super().__init__()
        self.component_name = component_name
        self.info_labels = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        # Info fields (initially empty)
        self.model_label = QLabel("Model: --")
        self.serial_label = QLabel("Serial: --")
        self.firmware_label = QLabel("Firmware: --")
        self.calibration_label = QLabel("Last Calibration: --")

        layout.addWidget(self.model_label)
        layout.addWidget(self.serial_label)
        layout.addWidget(self.firmware_label)
        layout.addWidget(self.calibration_label)

        self.setLayout(layout)
        self.setStyleSheet(
            "QWidget { background-color: #2b2b2b; border-radius: 3px; padding: 4px; }"
            "QLabel { color: #aaa; font-size: 11px; }"
        )

    def update_info(self, info: dict):
        """Update info card with device details."""
        if "model" in info:
            self.model_label.setText(f"Model: {info['model']}")
        if "serial" in info:
            self.serial_label.setText(f"Serial: {info['serial']}")
        if "firmware" in info:
            self.firmware_label.setText(f"Firmware: {info['firmware']}")
        if "calibration" in info:
            self.calibration_label.setText(f"Last Calibration: {info['calibration']}")
```

#### Task 3.2: Add Info Retrieval Methods
**Files:** Various hardware controller files

**Example for CameraController:**
```python
# In hardware/camera_controller.py
def get_device_info(self) -> dict:
    """
    Get camera device information.

    Returns:
        dict: Device info including model, serial, firmware
    """
    if not self.is_connected:
        return {}

    return {
        "model": self._get_model_name(),
        "serial": self._get_serial_number(),
        "firmware": self._get_firmware_version(),
        "resolution": f"{self.width}x{self.height}",
        "calibration": self._get_last_calibration_date()
    }
```

**Repeat for:**
- `hardware/laser_controller.py`
- `hardware/actuator_controller.py` (Zaber)
- `hardware/gpio_controller.py`

#### Task 3.3: Add Info Cards to Hardware Tab
**File:** `src/ui/main_window.py`

```python
# After each section header:

# Camera info card
self.camera_info_card = HardwareInfoCard("camera")
hardware_layout.addWidget(self.camera_info_card)

# Camera connection widget
hardware_layout.addWidget(self.camera_connection_widget)

# Update info when connected
def _on_camera_connected():
    if self.camera_controller:
        info = self.camera_controller.get_device_info()
        self.camera_info_card.update_info(info)
```

### Files to Create
- `src/ui/widgets/hardware_info_card.py` (NEW)

### Files to Modify
- `src/ui/main_window.py`
- `hardware/camera_controller.py`
- `hardware/laser_controller.py`
- `hardware/actuator_controller.py` (Zaber)
- `hardware/gpio_controller.py`

### Estimated Effort
- **Complexity:** Medium-High
- **Lines of Code:** ~300-400
- **Time:** 90-120 minutes

---

## Implementation Order (When Ready)

### Phase 1: Connection Status Indicators (Quickest Win)
- Immediate visual feedback
- Low complexity
- High user value

### Phase 2: Hardware Info Cards (Medium Effort)
- Useful diagnostic information
- Requires controller modifications
- Good for troubleshooting

### Phase 3: Test All Button (Most Complex)
- Most comprehensive feature
- Requires coordination across all controllers
- Highest implementation effort

---

## Testing Checklist (After Implementation)

### Enhancement 1: Connection Indicators
- [ ] All headers show ✗ on startup (disconnected)
- [ ] Camera header turns green with ✓ when connected
- [ ] Actuator header updates on connection
- [ ] Laser header updates on connection
- [ ] GPIO headers (smoothing + photodiode) update together
- [ ] Headers revert to gray ✗ on disconnect
- [ ] Colors are readable and distinct

### Enhancement 2: Test All Button
- [ ] Button appears in toolbar
- [ ] Button runs test sequence without crashing
- [ ] Results dialog shows all components
- [ ] PASS/FAIL status accurate for each
- [ ] Detail info displayed correctly
- [ ] Overall summary accurate
- [ ] Dialog closes properly

### Enhancement 3: Hardware Info Cards
- [ ] Info cards appear below each header
- [ ] Cards show "Model: --" when disconnected
- [ ] Cards populate with real data on connect
- [ ] Serial numbers displayed correctly
- [ ] Firmware versions shown
- [ ] Calibration dates (if available) shown
- [ ] Cards style matches UI theme

---

## Notes for Implementation

### Design Decisions to Confirm:
1. **Header colors:** Green (#2E7D32) vs current dark green, or brighter?
2. **Info card placement:** Above or below connection widgets?
3. **Test All timing:** Sequential (slow, thorough) vs parallel (fast, less detailed)?
4. **Calibration data:** Where to store? Database vs config file?

### Potential Issues:
1. **Hardware controller limitations:** Not all controllers may expose serial numbers/firmware
2. **Connection timing:** May need to add delays in Test All sequence
3. **Thread safety:** Test All must not block UI
4. **Error handling:** What happens if a test hangs?

---

## Files Summary

### New Files to Create:
1. `src/ui/dialogs/hardware_test_dialog.py` (~150 lines)
2. `src/ui/widgets/hardware_info_card.py` (~120 lines)

### Files to Modify:
1. `src/ui/main_window.py` (~200 lines added/modified)
2. `hardware/camera_controller.py` (~50 lines)
3. `hardware/laser_controller.py` (~50 lines)
4. `hardware/actuator_controller.py` (~50 lines)
5. `hardware/gpio_controller.py` (~50 lines)

### Total Estimated Changes:
- **New Code:** ~270 lines
- **Modified Code:** ~400 lines
- **Total Impact:** ~670 lines

---

**Status:** Ready for implementation once user feedback is received on current setup.
**Next Step:** Review testing feedback and adjust plan as needed.
