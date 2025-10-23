# Camera Test Suite

**Location:** `components/camera_module/`
**Camera:** Allied Vision 1800 U-158c
**Purpose:** Comprehensive test scripts and examples for camera validation and development

---

## Directory Structure

```
camera_module/
├── examples/                     # Test scripts and examples
│   ├── 01-06_*.py               # Custom test scripts
│   ├── test_camera_performance.py
│   └── official_allied_vision/  # Official Vimba 6.0 examples
├── tests/
│   └── vmbpy_unit_tests/        # VmbPy SDK unit tests
├── docs/                         # Documentation and feature info
└── output/                       # Captured images and videos
```

---

## Custom Test Scripts (examples/)

### 1. `01_list_cameras.py`
**Purpose:** Detect connected cameras
**What it does:**
- Lists all VmbPy-compatible cameras
- Shows camera IDs and models
- Verifies camera is detected by system

**Run:**
```bash
python 01_list_cameras.py
```

---

### 2. `02_camera_info.py`
**Purpose:** Display detailed camera information
**What it does:**
- Shows camera model and ID
- Displays sensor resolution
- Lists available pixel formats
- Shows interface type (USB, GigE, etc.)

**Run:**
```bash
python 02_camera_info.py
```

---

### 3. `03_capture_single_frame.py`
**Purpose:** Capture single frame and save to file
**What it does:**
- Connects to camera
- Captures one frame
- Saves as image file with timestamp
- Outputs to current directory

**Run:**
```bash
python 03_capture_single_frame.py
```

**Output:** `frame_YYYYMMDD_HHMMSS.png`

---

### 4. `04_explore_features.py`
**Purpose:** List all camera features and capabilities
**What it does:**
- Queries all camera features
- Shows readable features
- Displays feature values
- Identifies which features are writable

**Run:**
```bash
python 04_explore_features.py
```

**Note:** Some features may not be readable depending on camera state

---

### 5. `05_continuous_stream.py`
**Purpose:** Test continuous streaming performance
**What it does:**
- Streams frames continuously
- Displays live FPS
- Saves sample frames periodically
- Measures actual throughput

**Run:**
```bash
python 05_continuous_stream.py
```

**Expected:** ~39-40 FPS for Allied Vision 1800 U-158c

---

### 6. `06_set_auto_exposure.py`
**Purpose:** Test auto exposure feature
**What it does:**
- Enables auto exposure mode
- Captures frames with auto exposure
- Compares to manual exposure
- Shows exposure adjustment over time

**Run:**
```bash
python 06_set_auto_exposure.py
```

---

### 7. `test_camera_performance.py`
**Purpose:** Measure streaming performance metrics
**What it does:**
- Streams for 5 seconds
- Measures FPS
- Calculates frame processing time
- Provides performance assessment

**Run:**
```bash
python test_camera_performance.py
```

**Metrics:**
- Average FPS
- Frame processing time (min/avg/max/95th percentile)
- Performance rating

---

## Official Allied Vision Examples (examples/official_allied_vision/)

### `list_cameras.py`
**Purpose:** Allied Vision official camera listing example
**Similar to:** 01_list_cameras.py

### `list_features.py`
**Purpose:** List all camera features
**Similar to:** 04_explore_features.py

### `synchronous_grab.py`
**Purpose:** Synchronous frame capture example
**Similar to:** 03_capture_single_frame.py

### `asynchronous_grab.py`
**Purpose:** Asynchronous frame capture with callbacks
**Advanced version of:** 05_continuous_stream.py

### `asynchronous_grab_opencv.py`
**Purpose:** Async grab with OpenCV display
**Features:** Real-time display with OpenCV window

### `multithreading_opencv.py`
**Purpose:** Multithreaded frame capture with OpenCV
**Features:** Producer-consumer pattern for frame processing

### `event_handling.py`
**Purpose:** Camera event handling examples
**Features:** Event callbacks and notifications

### `action_commands.py`
**Purpose:** Action command examples
**Features:** Trigger modes and action commands

### `user_set.py`
**Purpose:** Camera user set management
**Features:** Save/load camera configurations

### `load_save_settings.py`
**Purpose:** Save and restore camera settings
**Features:** XML configuration export/import

### `list_ancillary_data.py`
**Purpose:** List ancillary frame data
**Features:** Metadata and frame information

### `create_trace_log.py`
**Purpose:** Enable VmbPy trace logging
**Features:** Debug logging configuration

---

## VmbPy Unit Tests (tests/vmbpy_unit_tests/)

Official VmbPy SDK unit tests for comprehensive camera testing.

### Basic Tests (`basic_tests/`)
- `c_binding_test.py` - Tests VmbC API bindings
- `camera_test.py` - Camera object functionality
- `feature_test.py` - Feature access and manipulation
- `frame_test.py` - Frame handling and conversion
- `interface_test.py` - Interface enumeration
- `stream_test.py` - Streaming functionality
- `transport_layer_test.py` - Transport layer tests
- `vmbsystem_test.py` - VmbSystem singleton tests
- And more...

### Real Camera Tests (`real_cam_tests/`)
Tests that require actual camera hardware connected.

**Run all unit tests:**
```bash
cd tests/vmbpy_unit_tests
python -m pytest
```

**Run specific test:**
```bash
cd tests/vmbpy_unit_tests
python -m pytest basic_tests/camera_test.py
```

---

## Documentation Files

### `README.md`
Complete VmbPy API documentation (500+ lines)
- Camera initialization
- Frame capture methods
- Feature access patterns
- Error handling

### `INTEGRATION_FEATURES.md`
Integration specification (736 lines)
- PyQt6 integration patterns
- Thread-safe streaming
- Video recording
- GUI controls design

### `LESSONS_LEARNED.md`
API quirks and best practices
- VmbPy specific behaviors
- Common pitfalls
- Performance tips

---

## Quick Start

**Run custom tests in sequence:**
```bash
cd examples
python 01_list_cameras.py
python 02_camera_info.py
python 03_capture_single_frame.py
python 04_explore_features.py
python 05_continuous_stream.py
python 06_set_auto_exposure.py
python test_camera_performance.py
```

**Try Allied Vision official examples:**
```bash
cd examples/official_allied_vision
python list_cameras.py
python asynchronous_grab_opencv.py
python multithreading_opencv.py
```

**Run unit tests:**
```bash
cd tests/vmbpy_unit_tests
python -m pytest
```

**Just check camera is working:**
```bash
cd examples
python 01_list_cameras.py
python 05_continuous_stream.py
```

**Performance validation:**
```bash
cd examples
python test_camera_performance.py
```

**Test with OpenCV display:**
```bash
cd examples/official_allied_vision
python asynchronous_grab_opencv.py
```

---

## Troubleshooting

### Camera Not Detected
```bash
python 01_list_cameras.py
```
If no cameras found:
- Check USB connection
- Verify VmbPy installed: `pip install vmbpy`
- Try different USB port

### Camera In Use Error
```
Camera 'DEV_XXX' is already in use
```

**Fix:** Close all other camera applications and try again

### Low Frame Rate
Expected: ~39-40 FPS
Actual: <20 FPS

**Possible causes:**
- USB bandwidth limitations
- Other USB devices on same bus
- Exposure time too high
- CPU overload

**Solutions:**
- Use dedicated USB 3.0 port
- Reduce exposure time
- Close other applications

---

## Development Notes

**These tests are standalone** - They don't depend on the main TOSCA application.

**Integration with TOSCA:**
- Camera HAL: `src/hardware/camera_controller.py`
- GUI Widget: `src/ui/widgets/camera_widget.py`
- Uses same VmbPy API patterns

**Recent Performance Improvements:**
- Removed unnecessary `.copy()` on frames
- Changed GUI scaling from `SmoothTransformation` to `FastTransformation`
- Reduced per-frame overhead by ~45ms

---

**Last Updated:** 2025-10-23
**Location:** `components/camera_module/`
**Total Resources:**
- 7 custom test scripts
- 12 Allied Vision official examples
- 24+ VmbPy unit tests
- 4 comprehensive documentation files

**Source:** Vimba 6.0 SDK + VmbPy SDK + custom TOSCA development scripts
