# TOSCA UI Widget Inventory

**Date:** 2025-10-31
**Task:** Subtask 3.1 - Inventory and catalog all UI widgets
**Purpose:** Complete catalog of all widgets in src/ui/widgets/ directory
**Total Widgets Found:** 18 widget files

---

## Widget Inventory by File

### 1. active_treatment_widget.py
**Class:** `ActiveTreatmentWidget(QWidget)`
**File Size:** 13,366 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Real-time treatment monitoring dashboard
**Import Status:** ✅ Imported in main_window.py:33
**Integration Status:** ✅ Integrated

###  2. actuator_connection_widget.py
**Class:** `ActuatorConnectionWidget(QWidget)`
**File Size:** 20,645 bytes
**Last Modified:** 2025-10-30 20:56
**Purpose:** Xeryon linear actuator connection and positioning controls
**Import Status:** ✅ Imported in main_window.py:470 (lazy import)
**Integration Status:** ✅ Integrated

### 3. camera_hardware_panel.py
**Class:** `CameraHardwarePanel(QWidget)`
**File Size:** 5,922 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Camera hardware diagnostics panel (sub-component)
**Import Status:** ⚠️ Not directly imported in main_window.py (used by camera_widget.py)
**Integration Status:** ✅ Integrated (sub-widget of CameraWidget)

### 4. camera_widget.py
**Class:** `CameraWidget(QWidget)`
**File Size:** 41,412 bytes (largest widget)
**Last Modified:** 2025-10-30 20:55
**Purpose:** Allied Vision camera live streaming, controls, and diagnostics
**Import Status:** ✅ Imported in main_window.py:34
**Integration Status:** ✅ Integrated

### 5. config_display_widget.py
**Class:** `ConfigDisplayWidget(QWidget)`
**File Size:** 11,523 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Display current system configuration (YAML settings)
**Import Status:** ✅ Imported in main_window.py:338 (lazy import)
**Integration Status:** ✅ Integrated

### 6. gpio_widget.py
**Class:** `GPIOWidget(QWidget)`
**File Size:** 23,373 bytes
**Last Modified:** 2025-10-30 20:56
**Purpose:** Arduino GPIO safety interlock status display
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED

### 7. interlocks_widget.py
**Class:** `InterlocksWidget(QGroupBox)`
**File Size:** 9,175 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Consolidated safety interlock status display
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED

### 8. laser_widget.py
**Class:** `LaserWidget(QWidget)`
**File Size:** 14,797 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Arroyo 6300 treatment laser power controls
**Import Status:** ✅ Imported in main_window.py:297 (lazy import)
**Integration Status:** ✅ Integrated

### 9. line_protocol_builder.py
**Class:** `LineProtocolBuilderWidget(QWidget)`
**File Size:** 39,240 bytes (second largest)
**Last Modified:** 2025-10-31 15:49
**Purpose:** Line-based protocol builder (concurrent actions per line)
**Import Status:** ✅ Imported in main_window.py:447 (lazy import)
**Integration Status:** ✅ Integrated

### 10. performance_dashboard_widget.py
**Classes:**
- `WorkerSignals(QObject)`
- `VacuumWorker(QRunnable)`
- `PerformanceDashboardWidget(QWidget)`

**File Size:** 17,294 bytes
**Last Modified:** 2025-10-31 13:08
**Purpose:** System performance monitoring dashboard (CPU, memory, camera FPS)
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED

### 11. protocol_builder_widget.py
**Class:** `ProtocolBuilderWidget(QWidget)`
**File Size:** 29,095 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Action-based protocol builder (sequential actions)
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED (replaced by line_protocol_builder?)

### 12. protocol_selector_widget.py
**Class:** `ProtocolSelectorWidget(QWidget)`
**File Size:** 10,434 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Visual protocol library browser
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED

### 13. safety_widget.py
**Class:** `SafetyWidget(QWidget)`
**File Size:** 12,292 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Safety status dashboard and event logging
**Import Status:** ✅ Imported in main_window.py:35
**Integration Status:** ✅ Integrated

### 14. smoothing_status_widget.py
**Class:** `SmoothingStatusWidget(QWidget)`
**File Size:** 7,721 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Smoothing motor control and health monitoring
**Import Status:** ❌ NOT imported in main_window.py
**Integration Status:** ❌ NOT INTEGRATED

### 15. subject_widget.py
**Class:** `SubjectWidget(QWidget)`
**File Size:** 17,255 bytes
**Last Modified:** 2025-10-31 20:57
**Purpose:** Subject selection and session creation
**Import Status:** ✅ Imported in main_window.py:36
**Integration Status:** ✅ Integrated

### 16. tec_widget.py
**Class:** `TECWidget(QWidget)`
**File Size:** 14,294 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Arroyo 5305 TEC (thermoelectric cooler) temperature controls
**Import Status:** ✅ Imported in main_window.py:303 (lazy import)
**Integration Status:** ✅ Integrated

### 17. treatment_setup_widget.py
**Class:** `TreatmentSetupWidget(QWidget)`
**File Size:** 8,642 bytes
**Last Modified:** 2025-10-31 15:53
**Purpose:** Treatment protocol selection and setup
**Import Status:** ✅ Imported in main_window.py:37
**Integration Status:** ✅ Integrated

### 18. view_sessions_dialog.py
**Class:** `ViewSessionsDialog(QDialog)`
**File Size:** 5,606 bytes
**Last Modified:** 2025-10-30 20:55
**Purpose:** Session history viewer dialog
**Import Status:** ❌ NOT imported in main_window.py (may be launched from menu)
**Integration Status:** ⚠️ Dialog (not widget) - may be launched dynamically

---

## Summary Statistics

### Integration Status
| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Integrated | 9 widgets | 50% |
| ❌ NOT Integrated | 8 widgets | 44% |
| ⚠️ Sub-component or Dialog | 1 widget | 6% |
| **Total** | **18 files** | **100%** |

### File Size Distribution
| Range | Count | Widgets |
|-------|-------|---------|
| 0-10 KB | 6 | camera_hardware_panel, view_sessions_dialog, interlocks_widget, treatment_setup_widget, protocol_selector_widget, smoothing_status_widget |
| 10-20 KB | 8 | active_treatment_widget, config_display_widget, safety_widget, laser_widget, tec_widget, performance_dashboard_widget, subject_widget, actuator_connection_widget |
| 20-30 KB | 2 | gpio_widget, protocol_builder_widget |
| 30-50 KB | 2 | line_protocol_builder, camera_widget |

**Largest Widgets:**
1. camera_widget.py (41,412 bytes)
2. line_protocol_builder.py (39,240 bytes)
3. protocol_builder_widget.py (29,095 bytes)

---

## Integrated Widgets (9 total)

### Primary Widgets (Imported at top-level)
1. ✅ **ActiveTreatmentWidget** - Treatment monitoring dashboard
2. ✅ **CameraWidget** - Camera live streaming and controls
3. ✅ **SafetyWidget** - Safety status and event logging
4. ✅ **SubjectWidget** - Subject selection and session creation
5. ✅ **TreatmentSetupWidget** - Protocol selection and setup

### Lazy-Loaded Widgets (Imported when needed)
6. ✅ **LaserWidget** - Laser power controls (lazy)
7. ✅ **TECWidget** - TEC temperature controls (lazy)
8. ✅ **ConfigDisplayWidget** - Configuration display (lazy)
9. ✅ **ActuatorConnectionWidget** - Actuator controls (lazy)
10. ✅ **LineProtocolBuilderWidget** - Line-based protocol builder (lazy)

### Sub-Components (Imported by other widgets)
11. ✅ **CameraHardwarePanel** - Used by CameraWidget

---

## NOT Integrated Widgets (8 total)

### Safety/Monitoring Widgets
1. ❌ **GPIOWidget** - Arduino GPIO interlock display
   - **Status:** 23,373 bytes, NOT imported
   - **Potential Reason:** Replaced by InterlocksWidget or SafetyWidget?

2. ❌ **InterlocksWidget** - Consolidated safety interlock status
   - **Status:** 9,175 bytes, NOT imported
   - **Potential Reason:** Functionality integrated into SafetyWidget?

3. ❌ **SmoothingStatusWidget** - Smoothing motor monitoring
   - **Status:** 7,721 bytes, NOT imported
   - **Potential Reason:** Functionality integrated into SafetyWidget or not yet needed?

### Protocol/Treatment Widgets
4. ❌ **ProtocolBuilderWidget** - Action-based protocol builder
   - **Status:** 29,095 bytes, NOT imported
   - **Potential Reason:** Replaced by LineProtocolBuilderWidget? (line-based > action-based)

5. ❌ **ProtocolSelectorWidget** - Visual protocol library browser
   - **Status:** 10,434 bytes, NOT imported
   - **Potential Reason:** Functionality integrated into TreatmentSetupWidget?

### System Monitoring Widgets
6. ❌ **PerformanceDashboardWidget** - CPU/memory/FPS monitoring
   - **Status:** 17,294 bytes, NOT imported
   - **Potential Reason:** Development tool not needed in production UI?

### Dialogs (May be launched dynamically)
7. ⚠️ **ViewSessionsDialog** - Session history viewer
   - **Status:** 5,606 bytes, NOT imported in main_window.py
   - **Note:** May be launched from menu/toolbar, not embedded in main window

---

## Questions to Investigate

### 1. Orphaned or Replaced Widgets?
- Is **ProtocolBuilderWidget** obsolete after **LineProtocolBuilderWidget** was created?
- Is **GPIOWidget** replaced by **InterlocksWidget** or **SafetyWidget**?
- Is **ProtocolSelectorWidget** functionality now in **TreatmentSetupWidget**?

### 2. Intentionally Unused Widgets?
- Is **PerformanceDashboardWidget** a development/debug tool?
- Is **SmoothingStatusWidget** planned for future integration?
- Is **InterlocksWidget** a newer replacement waiting to be integrated?

### 3. Dialog vs Widget Confusion?
- Should **ViewSessionsDialog** be considered a widget or dialog?
- Are there other dialogs that should be in ui/dialogs/ instead?

---

## Recommendations for Next Subtask (3.2)

### High Priority Investigation
1. **GPIOWidget vs InterlocksWidget vs SafetyWidget** - Determine which provides safety interlock display
2. **ProtocolBuilderWidget vs LineProtocolBuilderWidget** - Verify which is the current protocol builder
3. **ProtocolSelectorWidget vs TreatmentSetupWidget** - Check if protocol selection is duplicated

### Medium Priority Investigation
4. **SmoothingStatusWidget** - Determine if smoothing motor monitoring is needed
5. **PerformanceDashboardWidget** - Verify if this is development-only or production feature
6. **ViewSessionsDialog** - Check if this is launched from menus/toolbar

### Low Priority
7. **CameraHardwarePanel** - Already integrated as sub-component, no action needed

---

## Next Steps

1. ✅ **Subtask 3.1 Complete** - Widget inventory cataloged
2. ⏭️ **Subtask 3.2** - Trace widget imports and instantiation in main_window.py
3. ⏭️ **Subtask 3.3** - Validate widget placement and signal connections
4. ⏭️ **Subtask 3.4** - Create comprehensive widget integration matrix

---

**Inventory Completed:** 2025-10-31
**Analyst:** AI Agent (Claude Code)
**Task Master Task:** 3.1 - Inventory and catalog all UI widgets
