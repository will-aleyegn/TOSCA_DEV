# ADR-007: Allied Vision 1800 U-158c Camera Selection

**Status:** Accepted
**Date:** 2025-11-05
**Deciders:** System Architect, Clinical Advisors, Hardware Engineer
**Technical Story:** Machine vision system for laser treatment guidance

## Context and Problem Statement

TOSCA requires a machine vision system to provide:
1. Real-time visual feedback during laser treatment positioning
2. Session recording for treatment documentation and audit trail
3. Post-treatment analysis capabilities (focus measurement, ring detection)
4. Integration with PyQt6 GUI for live streaming at acceptable frame rates

The system must balance image quality, frame rate, ease of integration, cost, and medical device compliance considerations. Which camera platform should TOSCA use?

## Decision Drivers

* **Frame Rate:** Minimum 15 FPS for smooth real-time positioning feedback, target 30 FPS
* **Resolution:** Sufficient detail for laser ring alignment and tissue imaging (target 1-2 MP)
* **Python Integration:** Native Python SDK for seamless PyQt6 GUI integration
* **USB 3.0:** High-speed data transfer without requiring frame grabber hardware
* **Cross-Platform:** Must work on Windows/Linux for development and deployment
* **SDK Quality:** Well-documented API, active support, reliable frame acquisition
* **Medical Device Friendly:** Industrial/scientific camera (not consumer webcam)
* **Budget:** Cost-effective for research prototype ($500-$1500 range)
* **Triggering Capability:** Software/hardware trigger modes for synchronized acquisition
* **Pixel Format Flexibility:** Support for BGR8/RGB8/Mono8 for different use cases

## Considered Options

* **Option A: Allied Vision 1800 U-158c** - Industrial GigE/USB 3.0 camera with VmbPy SDK
* **Option B: Basler ace USB 3.0** - Industrial camera with pypylon SDK
* **Option C: FLIR Blackfly S USB3** - Scientific camera with PySpin SDK
* **Option D: Consumer Webcam** - Logitech C920/C930e with OpenCV VideoCapture

## Decision Outcome

Chosen option: "Allied Vision 1800 U-158c (Option A)", because it provides the best balance of image quality (1456x1088 resolution), Python integration quality (VmbPy SDK), USB 3.0 performance, and cost-effectiveness. The VmbPy API is well-documented with clear examples, and the camera supports all required features (triggering, pixel formats, exposure/gain control).

### Positive Consequences

* **High Resolution:** 1456x1088 pixels provides excellent detail for laser ring alignment
* **USB 3.0 Performance:** 30 FPS achievable at reduced resolution (software downsampling)
* **VmbPy SDK Quality:** Clean Python API with context managers, enum support, proper error handling
* **PyQt6 Integration:** Straightforward QImage/QPixmap conversion from NumPy arrays
* **Thread Safety:** Frame callbacks work well with PyQt6 signal/slot architecture
* **Pixel Format Support:** BGR8/RGB8/Mono8 all supported (BGR8 prioritized for OpenCV compatibility)
* **Industrial Quality:** Robust build quality, suitable for medical device environment
* **Triggering Modes:** Continuous, Software, Hardware trigger modes supported
* **Exposure/Gain Control:** Programmable exposure (100-10000 µs) and gain (0-40 dB) ranges
* **Cross-Platform:** Works on Windows and Linux (critical for development workflow)
* **Cost-Effective:** ~$800-$1200 range (reasonable for research prototype)

### Negative Consequences

* **Learning Curve:** VmbPy API more complex than OpenCV VideoCapture (requires context managers)
* **Frame Rate Limitations:** Full resolution limited to ~1.6 FPS (mitigated by software downsampling)
* **Hardware Binning:** Binning configuration caused corrupted frames (disabled in favor of software downsampling)
* **Dependency Management:** Requires Vimba X SDK installation (not just pip install)
* **Documentation Gaps:** Some VmbPy features underdocumented (e.g., binning pixel format changes)
* **USB 3.0 Required:** Older USB 2.0 ports insufficient for high frame rates

## Pros and Cons of the Options

### Option A: Allied Vision 1800 U-158c (CHOSEN)

Industrial camera with VmbPy Python SDK (wrapper for Vimba X)

* Good, because 1456x1088 resolution provides excellent image quality
* Good, because VmbPy SDK has clean Pythonic API with context managers
* Good, because USB 3.0 provides sufficient bandwidth for 30 FPS (with downsampling)
* Good, because supports BGR8/RGB8/Mono8 pixel formats (OpenCV compatible)
* Good, because PyQt6 integration straightforward (NumPy → QImage → QPixmap)
* Good, because industrial build quality suitable for medical device
* Good, because triggering modes support synchronized acquisition
* Good, because cross-platform (Windows/Linux) for development flexibility
* Good, because cost-effective (~$800-$1200 for research prototype)
* Bad, because full resolution limited to 1.6 FPS (requires downsampling)
* Bad, because hardware binning configuration issues (corrupted frames)
* Bad, because Vimba X SDK installation required (not just pip)
* Bad, because some API features underdocumented (binning, advanced features)

### Option B: Basler ace USB 3.0

Industrial camera with pypylon Python SDK

* Good, because pypylon SDK well-established and documented
* Good, because similar resolution options (1920x1200 available)
* Good, because industrial quality and medical device track record
* Good, because USB 3.0 performance comparable to Allied Vision
* Bad, because pypylon API more C++-like (less Pythonic than VmbPy)
* Bad, because slightly higher cost (~$900-$1400)
* Bad, because team has no prior Basler experience (learning curve)
* Bad, because Linux support sometimes problematic (reported issues)

### Option C: FLIR Blackfly S USB3

Scientific camera with PySpin Python SDK

* Good, because excellent image quality and scientific-grade sensors
* Good, because PySpin SDK comprehensive and well-documented
* Good, because strong Linux support (better than Basler)
* Good, because medical device track record (FLIR Systems reputation)
* Bad, because significantly higher cost (~$1500-$2500)
* Bad, because PySpin API complex (very C++-centric)
* Bad, because team has no FLIR experience (steeper learning curve)
* Bad, because overkill for current application (scientific features not needed)

### Option D: Consumer Webcam (Logitech C920/C930e)

Consumer webcam with OpenCV VideoCapture

* Good, because very low cost (~$50-$150)
* Good, because trivial OpenCV integration (VideoCapture.read())
* Good, because USB 2.0 sufficient (lower bandwidth requirements)
* Good, because zero learning curve (standard OpenCV API)
* Bad, because limited resolution (1080p maximum, ~2 MP)
* Bad, because no manual exposure/gain control (automatic only)
* Bad, because no triggering support (continuous only)
* Bad, because consumer-grade quality (plastic build, not robust)
* Bad, because not suitable for medical device (FDA submission concerns)
* Bad, because compressed video stream (MJPEG/H.264, not raw frames)
* Bad, because limited pixel format options (YUV422/RGB only)

## Links

* Related: [ADR-003 PyQt6 GUI Framework](ADR-003-pyqt6-gui-framework.md) - Camera must integrate with PyQt6
* Supersedes: Initial webcam prototype (never documented)
* External: [Allied Vision VmbPy Documentation](https://www.alliedvision.com/en/products/software/)
* External: [Vimba X SDK](https://www.alliedvision.com/en/products/software/vimba-x-sdk/)

## Implementation Notes

### Current Implementation (v0.9.13-alpha)

**File:** `src/hardware/camera_controller.py` (1,365 lines)

**Key Implementation Details:**

1. **Thread Safety:** RLock pattern for all hardware operations
```python
   self._lock = threading.RLock()
   with self._lock:
       # Thread-safe camera operations
```

2. **Signal/Slot Architecture:** PyQt6 signals for frame emission
```python
   frame_ready = pyqtSignal(np.ndarray)  # NumPy array → GUI thread
   fps_update = pyqtSignal(float)         # Real-time FPS feedback
```

3. **Pixel Format Configuration:** Explicit priority (Bgr8 > Rgb8 > Mono8)
```python
   # VmbPy enum names: Bgr8/Rgb8/Mono8 (NOT RGB8!)
   format_priorities = [PixelFormat.Bgr8, PixelFormat.Rgb8, PixelFormat.Mono8]
```

4. **QImage Memory Management:** Deep copy to prevent QImage lifetime bugs
```python
   frame_copy = frame.copy()  # CRITICAL: prevents QImage invalidation
   q_image = QImage(frame_copy.data, width, height, bytes_per_line, format)
```

5. **Software Downsampling:** cv2.resize instead of hardware binning
```python
   # Hardware binning disabled due to corrupted frames
   downsampled = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
```

6. **30 FPS Hardware Control:** Explicit frame rate setting
```python
   camera.AcquisitionFrameRate.set(30.0)  # VmbPy feature access
```

7. **Recording Manager:** OpenCV VideoWriter integration
```python
   fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Motion JPEG for recording
   writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
```

### Performance Characteristics

| Configuration | Resolution | FPS | Notes |
|---------------|-----------|-----|-------|
| Full Resolution | 1456x1088 | 1.6 | USB 3.0 bandwidth limit |
| Software Downsampled (640x480) | 640x480 | 30 | Real-time display |
| Software Downsampled (320x240) | 320x240 | 30 | Positioning mode |
| Hardware Binning (2x2) | 728x544 | **DISABLED** | Corrupted frames |

### Known Issues & Workarounds

1. **Hardware Binning Corruption:**
   - **Issue:** VmbPy binning causes corrupted frame data
   - **Workaround:** Software downsampling with cv2.resize()
   - **Future:** Investigate Allied Vision binning API (potential 4-15× FPS improvement)

2. **QImage Lifetime Bug:**
   - **Issue:** QImage shallow copy causes invalid data when NumPy array deallocated
   - **Solution:** Always copy frame before QImage construction (`frame.copy()`)
   - **Reference:** `LESSONS_LEARNED.md #1`

3. **Pixel Format Enum Naming:**
   - **Issue:** VmbPy uses `Bgr8` not `BGR8` or `bgr8`
   - **Solution:** Explicit enum names in code (avoid string matching)
   - **Impact:** Test compatibility requires string/enum handling in mocks

### Testing Infrastructure

**Mock:** `tests/mocks/mock_camera_controller.py` (467 lines)
**Tests:** `tests/test_hardware/test_camera_controller.py` (46 tests, 100% pass rate)

**Key Test Coverage:**
- Connection/disconnection lifecycle
- Streaming start/stop with frame generation
- Exposure/gain control (100 µs - 10000 µs, 0-40 dB)
- Pixel format switching (Bgr8/Rgb8/Mono8)
- Hardware binning (1x/2x/4x - mock only, disabled in real hardware)
- Trigger modes (Continuous/Software/Hardware)
- Frame rate control (1-120 FPS)
- Recording lifecycle
- Error handling (connection failures, operation errors)
- Thread safety (concurrent exposure/gain changes)

### Medical Device Compliance Considerations

1. **FDA 21 CFR Part 820:** Industrial camera suitable for medical device submission
2. **Image Quality Validation:** 1456x1088 resolution exceeds minimum requirements
3. **Frame Rate Validation:** 30 FPS (downsampled) meets real-time positioning needs
4. **Audit Trail:** All frames timestamped and optionally recorded for treatment documentation
5. **Reproducibility:** Deterministic exposure/gain settings ensure consistent imaging
6. **Safety:** Camera failure does not affect laser safety (selective shutdown policy)

### Future Enhancements

1. **Hardware Binning Investigation:** Debug VmbPy binning API for improved performance
2. **Auto-Exposure:** Implement automatic exposure adjustment for varying tissue reflectivity
3. **HDR Imaging:** Multi-exposure capture for high dynamic range treatment site imaging
4. **Calibration:** Distortion correction and spatial calibration for measurement accuracy
5. **AI Integration:** Ring detection and focus measurement for automated alignment

## Review History

| Date | Reviewer | Notes |
|------|----------|-------|
| 2025-11-05 | System Architect | Initial creation and implementation documentation |

---

**Template Version:** 1.0 (based on MADR 3.0)
**Last Updated:** 2025-11-05
