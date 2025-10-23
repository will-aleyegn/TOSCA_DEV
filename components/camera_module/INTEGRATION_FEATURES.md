# Camera Module - Integration Feature Specification

**Module:** Camera Module (VmbPy - Allied Vision)
**Target System:** TOSCA Laser Control System
**Hardware:** Allied Vision 1800 U-158c (USB 3.0)
**Status:** Exploration Complete, Ready for Integration
**Last Updated:** 2025-10-22

---

## Table of Contents

1. [Validated Features](#validated-features)
2. [Required Features for Integration](#required-features-for-integration)
3. [Hardware Abstraction Layer API](#hardware-abstraction-layer-api)
4. [Image Processing Pipeline](#image-processing-pipeline)
5. [Integration Points](#integration-points)
6. [Implementation Phases](#implementation-phases)
7. [Testing Requirements](#testing-requirements)

---

## Validated Features

**Status:** ✓ Tested and Working with Physical Hardware

### Camera Discovery and Connection
- **Script:** `01_list_cameras.py`
- **Status:** ✓ Working
- **Capabilities:**
  - Automatic camera detection
  - Camera ID retrieval
  - Model/interface identification
  - Multiple camera support (if needed)
- **Validated Hardware:** Allied Vision 1800 U-158c (DEV_1AB22C04E780)

### Camera Information Retrieval
- **Script:** `02_camera_info.py`
- **Status:** ✓ Working
- **Capabilities:**
  - Resolution: 1456x1088 pixels
  - Pixel format: RGB8
  - Exposure settings: 5ms - 455ms (auto-adjustable)
  - Gain settings: 0.0 dB (configurable)
- **Performance:** Settings retrieved in <100ms

### Single Frame Capture
- **Script:** `03_capture_single_frame.py`
- **Status:** ✓ Working
- **Capabilities:**
  - Single frame acquisition
  - NumPy array conversion
  - PNG image export
  - Timestamped filenames (no overwriting)
  - Path-independent operation
- **Performance:** ~50-100ms per capture
- **Output:** 1456x1088 RGB images (~600-650KB)

### Feature Exploration
- **Script:** `04_explore_features.py`
- **Status:** ✓ Working
- **Capabilities:**
  - 313 total camera features discovered
  - 223 readable features (71%)
  - Feature categories: Acquisition, Image Format, Analog Control, etc.
  - Read/write access detection
- **Key Features Identified:**
  - ExposureAuto: Off/Once/Continuous
  - ExposureTime: 36-9000014 µs range
  - Gain: 0-48 dB range
  - Frame rate control: 39.92 FPS max
  - White balance: Manual/Auto
  - Binning: Digital/Sum modes
  - ROI: Configurable region of interest

### Continuous Streaming
- **Script:** `05_continuous_stream.py`
- **Status:** ✓ Working
- **Capabilities:**
  - Continuous frame acquisition
  - Callback-based frame handling
  - Frame queue management
  - FPS monitoring
- **Performance:** 39.4 FPS sustained (matches spec)
- **Latency:** <30ms per frame

### Auto Exposure Control
- **Script:** `06_set_auto_exposure.py`
- **Status:** ✓ Working
- **Capabilities:**
  - Exposure modes: Off, Once, Continuous
  - Automatic brightness adjustment
  - Real-time setting changes
- **Validation:** Adjusted 5ms → 455ms automatically for dark scene

---

## Required Features for Integration

**Status:** Planned, based on Architecture Documentation

### 1. Hardware Abstraction Layer (HAL)

#### CameraController Class
**Purpose:** Provide unified interface for main application

**Required Methods:**
```python
class CameraController:
    def connect(camera_id: str = None) -> tuple[bool, str]
    def disconnect() -> None
    def configure(settings: CameraSettings) -> bool
    def start_streaming(callback: Callable) -> bool
    def stop_streaming() -> None
    def get_latest_frame() -> np.ndarray
    def capture_single_frame() -> np.ndarray
    def set_exposure(mode: str, value: float = None) -> bool
    def set_gain(gain_db: float) -> bool
    def set_resolution(width: int, height: int) -> bool
    def set_roi(x: int, y: int, width: int, height: int) -> bool
    def get_camera_info() -> CameraInfo
    def get_current_settings() -> CameraSettings
```

**Status:** Not yet implemented (requires src/hardware/camera_hal.py)

### 2. Ring Detection System

**Purpose:** Locate laser ring for alignment verification

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 153-358)

**Required Classes:**
- `RingDetector`: Hough Circle Transform implementation
- `DetectedRing`: Data class for ring properties

**Features Needed:**
- Circle detection using OpenCV HoughCircles
- ROI-based processing for performance
- Confidence scoring (ring brightness vs interior)
- Calibration: pixel radius → physical size mapping
- Visual overlay for live display

**Performance Target:** <50ms per frame @ 1456x1088

**Status:** Algorithm specified, not yet implemented

### 3. Focus Measurement System

**Purpose:** Quantify image sharpness for alignment

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 360-492)

**Required Classes:**
- `FocusAnalyzer`: Laplacian variance measurement
- Focus scoring: 0-100% scale

**Features Needed:**
- Laplacian variance calculation
- Threshold-based focus determination
- Calibration procedure for thresholds
- Visual focus indicator overlay

**Performance Target:** <10ms per frame

**Status:** Algorithm specified, not yet implemented

### 4. Video Recording System

**Purpose:** Record complete treatment sessions

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 494-629)

**Required Classes:**
- `VideoRecorder`: OpenCV VideoWriter wrapper
- Recording metadata tracking

**Features Needed:**
- Start/stop recording control
- Frame buffering and writing
- Timestamped video files
- Compression: XVID/H.264
- Snapshot capture during recording
- Recording metadata: duration, frame count, FPS

**Storage Requirements:** ~1GB per 10-minute session @ 30 FPS

**Status:** Not yet implemented

### 5. Complete Frame Processor

**Purpose:** Unified pipeline for all image processing

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 631-700)

**Required Class:**
- `FrameProcessor`: Orchestrates all processing steps

**Features Needed:**
- Ring detection + overlay
- Focus measurement + indicator
- Video recording
- Real-time metadata output
- Enable/disable processing steps
- Performance monitoring

**Status:** Not yet implemented

### 6. PyQt6 UI Integration

**Purpose:** Display live camera feed in main application

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 702-765)

**Required Widgets:**
- `VideoDisplayWidget`: QWidget for live display
- Frame rate: 30 FPS UI updates
- Metadata display: ring position, focus score
- Recording controls: start/stop, snapshot

**Integration Points:**
- Main treatment window
- Setup/alignment window
- Calibration window

**Status:** Not yet implemented

### 7. Calibration Procedures

**Purpose:** Configure system for specific hardware setup

**Architecture Reference:** `docs/architecture/05_image_processing.md` (Lines 767-858)

**Required Calibrations:**

#### A. Ring Size Calibration
- Map actuator position (µm) to ring size (pixels)
- Capture frames at multiple actuator positions
- User-provided physical measurements
- Store calibration curve in database

#### B. Focus Threshold Calibration
- Capture in-focus samples
- Capture out-of-focus samples
- Calculate threshold between ranges
- Store thresholds in database

**UI Required:** Calibration wizard dialogs

**Status:** Procedures specified, not yet implemented

---

## Hardware Abstraction Layer API

### Proposed API Structure

**Location:** `src/hardware/camera_controller.py`

```python
from dataclasses import dataclass
from typing import Optional, Callable, Tuple
import numpy as np
import vmbpy

@dataclass
class CameraSettings:
    """Camera configuration settings"""
    resolution: Tuple[int, int] = (1456, 1088)
    exposure_auto: str = "Continuous"  # Off, Once, Continuous
    exposure_time_us: Optional[float] = None  # Only if auto=Off
    gain_db: float = 0.0
    fps: float = 30.0
    pixel_format: str = "RGB8"

@dataclass
class CameraInfo:
    """Camera identification and capabilities"""
    camera_id: str
    model: str
    serial_number: str
    interface: str
    max_resolution: Tuple[int, int]
    max_fps: float
    supported_formats: list[str]

class CameraController:
    """
    Hardware abstraction layer for Allied Vision camera.

    Provides simplified interface for main application,
    hiding VmbPy SDK complexity.
    """

    def __init__(self):
        self.vmb = vmbpy.VmbSystem.get_instance()
        self.camera: Optional[vmbpy.Camera] = None
        self.is_connected: bool = False
        self.is_streaming: bool = False
        self.frame_callback: Optional[Callable] = None
        self.current_settings: CameraSettings = CameraSettings()

    # Core connection methods
    def connect(self, camera_id: Optional[str] = None) -> Tuple[bool, str]:
        """Connect to camera and configure initial settings"""
        pass

    def disconnect(self) -> None:
        """Disconnect camera and clean up resources"""
        pass

    # Configuration methods
    def configure(self, settings: CameraSettings) -> bool:
        """Apply camera settings"""
        pass

    def set_exposure(self, mode: str, value_us: Optional[float] = None) -> bool:
        """Set exposure mode and value"""
        pass

    def set_gain(self, gain_db: float) -> bool:
        """Set camera gain"""
        pass

    def set_roi(self, x: int, y: int, width: int, height: int) -> bool:
        """Set region of interest"""
        pass

    # Streaming methods
    def start_streaming(self, callback: Callable[[np.ndarray], None]) -> bool:
        """Start continuous frame acquisition"""
        pass

    def stop_streaming(self) -> None:
        """Stop frame acquisition"""
        pass

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get most recent frame (non-blocking)"""
        pass

    # Single capture methods
    def capture_single_frame(self, timeout_ms: int = 1000) -> Optional[np.ndarray]:
        """Capture single frame (blocking)"""
        pass

    # Information methods
    def get_camera_info(self) -> CameraInfo:
        """Get camera identification and capabilities"""
        pass

    def get_current_settings(self) -> CameraSettings:
        """Get current camera configuration"""
        pass

    def get_available_features(self) -> dict:
        """Get all readable camera features and values"""
        pass
```

**Implementation Priority:** HIGH (required for Phase 1 integration)

---

## Image Processing Pipeline

### Processing Flow

```
Camera Frame
    ↓
[Frame Acquisition]
    ↓
[Color Conversion] (if needed)
    ↓
[Ring Detection] ←─ Enable/Disable
    ↓
[Focus Measurement] ←─ Enable/Disable
    ↓
[Overlay Drawing]
    ↓
[Video Recording] ←─ If active
    ↓
[PyQt Display]
    ↓
[Metadata Emit] → (ring position, focus score, etc.)
```

### Performance Budget (per frame @ 30 FPS)

- **Total Budget:** 33ms per frame
- **Frame Acquisition:** 5ms
- **Ring Detection:** 15ms (with ROI)
- **Focus Measurement:** 3ms
- **Overlay Drawing:** 2ms
- **Video Recording:** 5ms
- **Qt Display Update:** 3ms
- **Margin:** 5ms

### Optimization Strategies

1. **ROI Processing:** Only process center region for ring detection
2. **Frame Skipping:** Process every 2nd or 3rd frame if needed
3. **Threading:** Run processing in separate thread from UI
4. **Downscaling:** Process at 728x544 instead of 1456x1088
5. **Caching:** Cache detector parameters between frames

---

## Integration Points

### 1. Main Application Startup

**Location:** `src/main.py`

```python
# Initialize camera controller
camera = CameraController()
success, message = camera.connect()

if not success:
    show_error_dialog(f"Camera Error: {message}")
    # Fall back to no-camera mode or exit
```

### 2. Treatment Session

**Location:** `src/core/session_manager.py`

```python
def start_treatment_session():
    # Start camera streaming
    camera.start_streaming(frame_callback)

    # Start video recording
    video_recorder.start_recording(session_id)

    # Enable ring detection
    frame_processor.enable_ring_detection = True
```

### 3. Live Display

**Location:** `src/ui/treatment_window.py`

```python
# Video display widget
video_widget = VideoDisplayWidget(camera, frame_processor)

# Connect metadata signal
video_widget.frame_processed.connect(self.on_frame_metadata)

def on_frame_metadata(self, metadata: dict):
    # Update UI with ring position, focus score, etc.
    self.update_alignment_indicators(metadata)
```

### 4. Calibration Procedures

**Location:** `src/ui/calibration_wizard.py`

```python
def calibrate_ring_size():
    # Interactive calibration
    for position_um in calibration_positions:
        actuator.move_to(position_um)
        frame = camera.capture_single_frame()
        ring = ring_detector.detect(frame)
        # Collect calibration points
```

### 5. Safety Interlocks

**Location:** `src/core/safety_manager.py`

```python
def check_alignment():
    # Get latest frame metadata
    metadata = frame_processor.get_latest_metadata()

    if not metadata['ring']['detected']:
        trigger_safety_interlock("RING_NOT_DETECTED")

    if not metadata['focus']['is_focused']:
        show_warning("Poor focus detected")
```

---

## Implementation Phases

### Phase 1: Core HAL (Week 1)
**Goal:** Basic camera control in main application

**Tasks:**
- [ ] Create `src/hardware/camera_controller.py`
- [ ] Implement CameraController class
- [ ] Implement CameraSettings/CameraInfo dataclasses
- [ ] Unit tests for HAL
- [ ] Integration test with main application

**Deliverable:** Camera streaming in main UI

### Phase 2: Ring Detection (Week 2)
**Goal:** Laser ring detection and overlay

**Tasks:**
- [ ] Create `src/image_processing/ring_detector.py`
- [ ] Implement RingDetector class
- [ ] Tune Hough Circle parameters for laser ring
- [ ] Implement overlay rendering
- [ ] Create ring detection test suite

**Deliverable:** Live ring detection display

### Phase 3: Focus Measurement (Week 2-3)
**Goal:** Focus quality indication

**Tasks:**
- [ ] Create `src/image_processing/focus_analyzer.py`
- [ ] Implement FocusAnalyzer class
- [ ] Calibrate focus thresholds
- [ ] Implement focus indicator overlay
- [ ] Create focus measurement test suite

**Deliverable:** Live focus quality display

### Phase 4: Video Recording (Week 3)
**Goal:** Session recording capability

**Tasks:**
- [ ] Create `src/image_processing/video_recorder.py`
- [ ] Implement VideoRecorder class
- [ ] Integrate with session management
- [ ] Implement snapshot capture
- [ ] Create recording controls in UI

**Deliverable:** Complete session recording

### Phase 5: Frame Processor (Week 3-4)
**Goal:** Unified processing pipeline

**Tasks:**
- [ ] Create `src/image_processing/frame_processor.py`
- [ ] Implement FrameProcessor class
- [ ] Integrate all processing components
- [ ] Performance optimization
- [ ] End-to-end testing

**Deliverable:** Complete image processing pipeline

### Phase 6: PyQt Integration (Week 4)
**Goal:** Polished UI integration

**Tasks:**
- [ ] Create `src/ui/widgets/video_display_widget.py`
- [ ] Implement VideoDisplayWidget
- [ ] Integrate with treatment window
- [ ] Add recording controls
- [ ] Add metadata display

**Deliverable:** Production-ready camera UI

### Phase 7: Calibration (Week 5)
**Goal:** System calibration tools

**Tasks:**
- [ ] Create `src/ui/calibration_wizard.py`
- [ ] Implement ring size calibration
- [ ] Implement focus calibration
- [ ] Store calibration in database
- [ ] Create calibration documentation

**Deliverable:** Complete calibration procedures

---

## Testing Requirements

### Unit Tests

**Location:** `tests/test_camera/`

```
tests/test_camera/
├── test_camera_controller.py      # HAL tests
├── test_ring_detector.py          # Ring detection tests
├── test_focus_analyzer.py         # Focus measurement tests
├── test_video_recorder.py         # Recording tests
└── test_frame_processor.py        # Pipeline tests
```

**Coverage Target:** 80%+ for all camera modules

### Integration Tests

**Location:** `tests/test_integration/`

```
test_integration/
├── test_camera_ui_integration.py         # UI integration
├── test_camera_session_integration.py    # Session recording
└── test_camera_safety_integration.py     # Safety interlock integration
```

### Hardware Tests

**Location:** `camera_module/examples/` (existing test scripts)

```
examples/
├── 01_list_cameras.py            # ✓ Validated
├── 02_camera_info.py             # ✓ Validated
├── 03_capture_single_frame.py    # ✓ Validated
├── 04_explore_features.py        # ✓ Validated
├── 05_continuous_stream.py       # ✓ Validated
└── 06_set_auto_exposure.py       # ✓ Validated
```

**Status:** All hardware tests passing with physical camera

### Performance Tests

**Requirements:**
- Streaming: Sustain 30 FPS for 10+ minutes
- Ring Detection: <50ms per frame
- Focus Measurement: <10ms per frame
- Total Pipeline: <33ms per frame (30 FPS target)
- Memory: <500MB for 10-minute session

### Safety Tests

**Critical Tests:**
- Camera disconnection during treatment
- Frame acquisition timeout handling
- Ring detection failure scenarios
- Recording failure handling
- Memory overflow protection

---

## Dependencies

### Python Packages (Already in requirements.txt)
```python
vmbpy>=1.1.0              # Allied Vision SDK
opencv-python>=4.8.0      # Image processing
numpy>=1.24.0             # Array operations
PyQt6>=6.6.0              # UI framework
pillow>=10.0.0            # Image I/O
```

### Hardware Requirements
- Allied Vision camera (USB 3.0 or GigE)
- USB 3.0 port (for camera)
- Windows 10 (64-bit)
- 8GB RAM minimum
- 256GB storage minimum

### Software Requirements
- Vimba SDK installed (VmbPy dependency)
- Python 3.10+
- OpenCV with full codecs

---

## Risk Mitigation

### Risk: Camera Disconnection During Treatment

**Mitigation:**
- Implement connection monitoring
- Automatic reconnection attempts
- Graceful degradation (continue without camera)
- User notification

### Risk: Processing Latency

**Mitigation:**
- ROI-based processing
- Frame skipping if needed
- Separate processing thread
- Performance monitoring

### Risk: Storage Capacity

**Mitigation:**
- Video compression
- Configurable recording quality
- Storage space monitoring
- Automatic cleanup of old sessions

### Risk: Ring Detection Failures

**Mitigation:**
- Confidence threshold tuning
- Manual override capability
- Multiple detection attempts
- User alignment guidance

---

## Success Criteria

### Phase 1 Complete
- [ ] Camera streaming in main UI at 30 FPS
- [ ] Start/stop camera control
- [ ] Camera settings configuration
- [ ] Zero crashes in 1-hour test

### Phase 7 Complete (Full Integration)
- [ ] Ring detection accuracy >95%
- [ ] Focus measurement reliable
- [ ] Session recording functional
- [ ] Calibration procedures documented
- [ ] All tests passing
- [ ] User documentation complete
- [ ] Performance targets met

---

## Documentation References

- **System Architecture:** `docs/architecture/01_system_overview.md`
- **Image Processing:** `docs/architecture/05_image_processing.md`
- **VmbPy API:** `camera_module/README.md`
- **Lessons Learned:** `camera_module/LESSONS_LEARNED.md`
- **Test Scripts:** `camera_module/examples/`

---

**Document Status:** Complete
**Next Step:** Begin Phase 1 implementation (CameraController HAL)
**Estimated Total Implementation Time:** 5 weeks (1 developer)

**Camera module exploration is complete and ready for integration.**
