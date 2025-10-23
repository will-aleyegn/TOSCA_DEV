# Allied Vision Camera Module

**Camera:** Allied Vision Camera
**API:** VmbPy 1.1.1 (Vimba X SDK Python API)
**Purpose:** Camera control and image acquisition for TOSCA Laser Control System

---

## Overview

This module provides isolated camera testing and exploration scripts to fully understand the VmbPy API before integration into the main TOSCA application.

---

## Directory Structure

```
camera_module/
├── README.md              # This file
├── examples/              # Test scripts
│   ├── 01_list_cameras.py
│   ├── 02_camera_info.py
│   ├── 03_capture_single_frame.py
│   ├── 04_explore_features.py
│   └── 05_continuous_stream.py
├── tests/                 # Unit tests (to be created)
└── docs/                  # Additional documentation
```

---

## Prerequisites

**VmbPy Installation:**
```bash
pip install vmbpy
```

**Optional Dependencies:**
```bash
pip install opencv-python  # For image saving in examples
pip install numpy          # Frame array conversion
```

**Camera Requirements:**
- Allied Vision camera connected via USB or GigE
- Camera powered on
- Appropriate drivers installed

---

## Example Scripts

### 01_list_cameras.py

**Purpose:** Detect and list all connected cameras

**Usage:**
```bash
python camera_module/examples/01_list_cameras.py
```

**Output:**
```
Found 1 camera(s):

Camera 1:
  ID:        DEV_1AB2000017B5
  Model:     Alvium 1800 U-158c
  Interface: USB
```

**What it tests:**
- VmbSystem initialization
- Camera detection
- Basic camera properties

---

### 02_camera_info.py

**Purpose:** Display detailed camera information and capabilities

**Usage:**
```bash
python camera_module/examples/02_camera_info.py [camera_id]
```

**Output:**
```
Camera Information:
  ID:              DEV_1AB2000017B5
  Model:           Alvium 1800 U-158c
  Serial Number:   50-0536519516
  Interface:       USB

Image Format:
  Width:           1936
  Height:          1216
  Pixel Format:    Mono8

Exposure Settings:
  Exposure Time:   10000 µs
  Exposure Auto:   Off

Gain Settings:
  Gain:            0.0
```

**What it tests:**
- Camera opening/closing
- Feature access (Width, Height, PixelFormat)
- Exposure and gain settings
- Error handling for missing features

---

### 03_capture_single_frame.py

**Purpose:** Capture a single frame and save as image

**Usage:**
```bash
python camera_module/examples/03_capture_single_frame.py [camera_id] [output_file]
```

**Default output:** `captured_frame.png`

**Output:**
```
Using camera: DEV_1AB2000017B5

Frame Information:
  Width:        1936
  Height:       1216
  Pixel Format: Mono8
  Frame ID:     1
  Timestamp:    123456789

NumPy Array Shape: (1216, 1936)
Data Type: uint8

Image saved to: captured_frame.png
```

**What it tests:**
- Single frame acquisition
- Frame data access
- NumPy array conversion
- Image file saving

---

### 04_explore_features.py

**Purpose:** List all available camera features and their values

**Usage:**
```bash
python camera_module/examples/04_explore_features.py [camera_id]
```

**Output:**
```
Found 247 features:

=== Readable Features ===

AcquisitionFrameRate       [R/W] = 30.0
  Category: Acquisition Control

AcquisitionMode            [R/W] = Continuous
  Category: Acquisition Control

ExposureTime               [R/W] = 10000
  Category: Acquisition Control

...

=== Summary ===
Total Features:     247
Readable Features:  198
Writable Features:  142
```

**What it tests:**
- Feature enumeration
- Feature accessibility (readable/writable)
- Feature values and categories

---

### 05_continuous_stream.py

**Purpose:** Capture continuous frames and measure frame rate

**Usage:**
```bash
python camera_module/examples/05_continuous_stream.py [camera_id] [duration_seconds]
```

**Default duration:** 10 seconds

**Output:**
```
Using camera: DEV_1AB2000017B5

Streaming for 10 seconds...
Press Ctrl+C to stop early.

Elapsed: 5.0s, Frames: 150, FPS: 30.00
Elapsed: 10.0s, Frames: 300, FPS: 30.00

Capture Complete:
  Duration:  10.00 seconds
  Frames:    300
  Avg FPS:   30.00
```

**What it tests:**
- Continuous frame streaming
- Streaming callbacks
- Frame rate measurement
- Graceful stop

---

## VmbPy API Key Concepts

### 1. Context Manager Pattern

VmbPy uses Python context managers for proper resource management:

```python
vmb = vmbpy.VmbSystem.get_instance()
with vmb:
    # VmbSystem initialized here
    cameras = vmb.get_all_cameras()
    with cameras[0]:
        # Camera opened here
        frame = camera.get_frame()
        # Camera automatically closed after with block
    # VmbSystem automatically cleaned up after with block
```

**Why:** Ensures proper initialization order and cleanup.

### 2. Camera Discovery

**Get all cameras:**
```python
cameras = vmb.get_all_cameras()
```

**Get specific camera by ID:**
```python
camera = vmb.get_camera_by_id("DEV_1AB2000017B5")
```

### 3. Frame Acquisition

**Single frame:**
```python
with camera:
    frame = camera.get_frame()
    data = frame.as_numpy_ndarray()
```

**Continuous streaming:**
```python
def frame_callback(cam, stream_stats):
    # Process frame here
    pass

with camera:
    camera.start_streaming(frame_callback)
    # ... streaming happens ...
    camera.stop_streaming()
```

### 4. Feature Access

**Read feature:**
```python
exposure = camera.get_feature_by_name("ExposureTime")
value = exposure.get()
```

**Write feature:**
```python
exposure = camera.get_feature_by_name("ExposureTime")
exposure.set(15000)  # Set to 15ms
```

**Check accessibility:**
```python
if feature.is_readable():
    value = feature.get()
if feature.is_writable():
    feature.set(new_value)
```

### 5. Error Handling

**Common exceptions:**
- `vmbpy.VmbCameraError` - Camera operation failed
- `vmbpy.VmbFeatureError` - Feature access failed
- `vmbpy.VmbTimeout` - Operation timed out
- `vmbpy.VmbFrameError` - Frame invalid or incomplete

**Example:**
```python
try:
    frame = camera.get_frame()
except vmbpy.VmbTimeout:
    print("Frame capture timed out")
except vmbpy.VmbCameraError as e:
    print(f"Camera error: {e}")
```

---

## Key Camera Features

Based on Allied Vision cameras, typical features include:

**Acquisition Control:**
- `AcquisitionMode`: Continuous, SingleFrame, MultiFrame
- `AcquisitionFrameRate`: Frame rate in Hz
- `ExposureTime`: Exposure time in microseconds
- `ExposureAuto`: Off, Once, Continuous

**Image Format:**
- `Width`: Image width in pixels
- `Height`: Image height in pixels
- `PixelFormat`: Mono8, Mono12, RGB8, etc.

**Analog Control:**
- `Gain`: Sensor gain
- `GainAuto`: Auto gain control
- `BlackLevel`: Black level offset

**Trigger:**
- `TriggerMode`: On, Off
- `TriggerSource`: Software, Line0, etc.
- `TriggerSelector`: FrameStart, etc.

---

## Testing Checklist

Run these scripts in order to verify camera functionality:

- [ ] **01_list_cameras.py** - Verify camera is detected
- [ ] **02_camera_info.py** - Verify camera opens and features are accessible
- [ ] **03_capture_single_frame.py** - Verify frame capture works
- [ ] **04_explore_features.py** - Document available features for TOSCA
- [ ] **05_continuous_stream.py** - Verify streaming and frame rate

---

## Integration Plan

### Phase 1: Hardware Abstraction Layer

Create `src/hardware/camera.py`:

**Responsibilities:**
- Camera initialization and configuration
- Single frame capture
- Continuous streaming with callbacks
- Exposure and gain control
- Error handling and recovery

**Interface:**
```python
class AlliedVisionCamera:
    def __init__(self, camera_id: str = None):
        pass

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def capture_frame(self) -> np.ndarray:
        pass

    def start_streaming(self, callback) -> None:
        pass

    def stop_streaming(self) -> None:
        pass

    def set_exposure(self, microseconds: int) -> None:
        pass

    def set_gain(self, gain: float) -> None:
        pass
```

### Phase 2: Image Processing Integration

Connect camera to `src/image_processing/`:
- Ring detection
- Focus measurement
- Real-time display

### Phase 3: Session Recording

Connect camera to session management:
- Video recording
- Timestamped frame logging
- Event correlation

---

## Known Issues

**Issue:** Camera not detected
**Solution:**
- Check camera is powered on
- Check USB/network cable
- Check drivers installed
- Run `01_list_cameras.py` to diagnose

**Issue:** Frame capture timeout
**Solution:**
- Camera may be in use by another application
- Restart camera power
- Check USB bandwidth (USB 3.0 required)

**Issue:** Feature not available
**Solution:**
- Run `04_explore_features.py` to see available features
- Feature may be model-specific
- Check camera firmware version

---

## Next Steps

1. **Run all example scripts** with physical camera connected
2. **Document camera-specific features** found in 04_explore_features.py
3. **Identify required features** for TOSCA application:
   - Exposure time range
   - Gain range
   - Pixel format options
   - Trigger capabilities
4. **Create hardware abstraction layer** in main application
5. **Write unit tests** for camera module

---

## References

- VmbPy GitHub: https://github.com/alliedvision/VmbPy
- Allied Vision Documentation: https://www.alliedvision.com/en/support/software-downloads.html
- Vimba X SDK Manual: (Included with SDK installation)

---

**Last Updated:** 2025-10-22
**VmbPy Version:** 1.1.1
