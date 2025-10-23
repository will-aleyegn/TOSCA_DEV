# Camera Module - Lessons Learned

**Purpose:** Document mistakes, API quirks, and solutions discovered during development to avoid repeating them.

**Last Updated:** 2025-10-22

---

## VmbPy API Issues

### Issue #1: Feature Writability Check Method Name

**Date:** 2025-10-22

**Problem:**
- Assumed the method was `is_writable()` based on common Python conventions
- Script 04_explore_features.py found 313 features but read 0
- Features returned `'EnumFeature' object has no attribute 'is_writable'` error

**Investigation:**
- Created debug script to inspect feature objects
- Ran method inspection on actual feature object
- Found method is spelled `is_writeable()` (with extra 'e')

**Root Cause:**
VmbPy API uses British spelling: `is_writeable()` not `is_writable()`

**Solution:**
Use `feature.is_writeable()` instead of `feature.is_writable()`

**Files Affected:**
- camera_module/examples/04_explore_features.py

**Lesson:**
When working with third-party APIs, always verify method names by inspecting actual objects rather than assuming based on conventions. VmbPy may use British English spellings in some methods.

---

### Issue #2: Streaming Callback Signature

**Date:** 2025-10-22

**Problem:**
- Assumed streaming callback used `vmbpy.StreamStats` parameter
- Script 05_continuous_stream.py failed with: `AttributeError: module 'vmbpy' has no attribute 'StreamStats'`
- Callback function signature was incorrect

**Investigation:**
- Error occurred when defining callback type hints
- Need to verify actual VmbPy streaming callback signature

**Root Cause:**
VmbPy streaming API does not have a `StreamStats` class. The callback signature was incorrect - it requires THREE parameters (Camera, Stream, Frame) not two.

**Solution:**
Correct callback signature:
```python
def on_frame(cam: Any, stream: Any, frame: Any) -> None:
    counter.increment()
    cam.queue_frame(frame)
```

The error message from VmbPy was helpful: `Expected type: typing.Callable[[vmbpy.camera.Camera, vmbpy.stream.Stream, vmbpy.frame.Frame], NoneType]`

**Files Affected:**
- camera_module/examples/05_continuous_stream.py

**Lesson:**
- Do not assume callback signatures - read error messages carefully as they often provide exact type requirements
- Use `typing.Any` for type hints when exact types are unknown
- Test callback-based code immediately to catch signature mismatches
- Error messages from typed APIs are valuable - they tell you exactly what's expected

---

### Issue #3: Relative Path in Script Breaks When Run from Different Directory

**Date:** 2025-10-22

**Problem:**
- Script 03_capture_single_frame.py used relative path: `camera_module/output/captured_frame.png`
- File didn't update when running script from `camera_module/examples/` directory
- User couldn't see new captures because file was being saved to wrong location

**Investigation:**
- Checked file timestamp - showed old capture time
- Script worked when run from project root but not from examples directory
- Relative path assumed script was run from project root

**Root Cause:**
Relative paths in scripts are fragile - they depend on the current working directory when the script is executed, not the script's actual location.

**Solution:**
Use `Path(__file__)` to get the script's location and build absolute paths:

```python
from pathlib import Path

script_dir = Path(__file__).parent          # camera_module/examples/
output_dir = script_dir.parent / "output"   # camera_module/output/
output_dir.mkdir(exist_ok=True)             # Create if doesn't exist
output_file = str(output_dir / "captured_frame.png")
```

**Files Affected:**
- camera_module/examples/03_capture_single_frame.py

**Lesson:**
- Always use `Path(__file__)` to build paths relative to the script's location, not the current working directory
- Test scripts by running them from different directories
- Relative paths are only safe for imports, not for file I/O
- Use `mkdir(exist_ok=True)` to ensure output directories exist

---

### Issue #4: Using Software Frame Throttling Instead of Hardware Frame Rate Control

**Date:** 2025-10-23

**Problem:**
- Implemented software-based frame throttling in `CameraStreamThread.frame_callback()` to limit GUI updates to 30 FPS
- Camera was capturing at 39-40 FPS, causing slow/stuttering GUI updates
- Software solution wasted CPU cycles converting and discarding ~25% of frames

**Investigation:**
- Initially assumed throttling had to be done in software
- User asked: "does the api not have built in commands for this"
- Checked Allied Vision official examples and VmbPy API documentation
- Found `AcquisitionFrameRateEnable` and `AcquisitionFrameRate` features

**Root Cause:**
Failed to check hardware API capabilities before implementing software workaround. VmbPy provides native frame rate control through the camera's acquisition settings.

**Solution:**
Added `set_acquisition_frame_rate()` method using hardware features:

```python
def set_acquisition_frame_rate(self, fps: float) -> bool:
    """Set camera's acquisition frame rate at hardware level."""
    try:
        # Enable frame rate control
        self.camera.get_feature_by_name("AcquisitionFrameRateEnable").set(True)
        # Set frame rate
        self.camera.get_feature_by_name("AcquisitionFrameRate").set(fps)
        logger.info(f"Camera acquisition frame rate set to {fps} FPS")
        return True
    except Exception as e:
        logger.error(f"Failed to set acquisition frame rate: {e}")
        return False
```

Called in `start_streaming()`:
```python
def start_streaming(self) -> bool:
    # Set camera acquisition frame rate to 30 FPS for smooth GUI performance
    self.set_acquisition_frame_rate(30.0)
    # ... rest of streaming setup
```

**Benefits of Hardware Solution:**
- Camera captures exactly 30 FPS (not 40 FPS with 10 discarded)
- No frame conversion overhead for discarded frames
- No timing jitter from software throttling
- More reliable and predictable performance
- Simpler code

**Files Affected:**
- `src/hardware/camera_controller.py` - Added `set_acquisition_frame_rate()` method
- `src/hardware/camera_controller.py:293-294` - Call in `start_streaming()`

**Lesson:**
**ALWAYS check hardware API documentation FIRST before implementing software workarounds.** Hardware-level features are more efficient, reliable, and appropriate than software alternatives. This applies to all hardware modules (cameras, actuators, sensors).

See CODING_STANDARDS.md "Hardware API Usage" section for the project-wide rule.

---

### Issue #5: Camera Frame Rate Limited by Hardware Configuration

**Date:** 2025-10-23

**Problem:**
- Attempted to set camera acquisition frame rate to 30 FPS using hardware API
- Camera rejected value with error: `30.0 is not within [1.0369063602411188e-05, 0.451884925365448]`
- Camera's maximum frame rate was only 0.45 FPS despite being capable of 40+ FPS

**Investigation:**
- Camera was successfully streaming at 39-40 FPS before attempting rate control
- `AcquisitionFrameRate` feature reported extremely low max value (0.45 FPS)
- This suggests camera is in a mode or configuration that limits frame rate range
- Could be related to: exposure time, pixel format, acquisition mode, or other features

**Root Cause:**
Camera's frame rate range is dynamic and depends on other settings (exposure, resolution, pixel format, etc.). The `AcquisitionFrameRate` feature reflects the currently achievable range given the camera's state.

**Solution:**
Implemented graceful handling with fallback:

```python
def start_streaming(self) -> bool:
    # Check if hardware supports desired frame rate
    fps_info = self.get_acquisition_frame_rate_info()
    if fps_info["max_fps"] >= 30.0:
        # Use hardware frame rate control
        self.set_acquisition_frame_rate(30.0)
        logger.info("Using hardware frame rate control (30 FPS)")
    else:
        # Fall back to software throttling
        logger.warning(
            f"Camera max FPS ({fps_info['max_fps']:.2f}) < 30. "
            f"Using software throttling instead"
        )
```

Also added range clamping in `set_acquisition_frame_rate()`:
```python
# Get valid range and clamp request
fps_feature = self.camera.get_feature_by_name("AcquisitionFrameRate")
min_fps, max_fps = fps_feature.get_range()
clamped_fps = max(min_fps, min(fps, max_fps))
```

**Files Affected:**
- `src/hardware/camera_controller.py:584-605` - Added `get_acquisition_frame_rate_info()`
- `src/hardware/camera_controller.py:607-643` - Updated `set_acquisition_frame_rate()` with clamping
- `src/hardware/camera_controller.py:301-312` - Smart fallback in `start_streaming()`

**Lesson:**
**Hardware API features may have dynamic ranges that depend on other settings.** Always:
1. Query the valid range before setting values
2. Clamp or validate against the actual range
3. Have a fallback strategy if hardware doesn't support desired values
4. Log clearly which method is being used (hardware vs software)

This still follows the "hardware API first" principle - we try hardware, but gracefully fall back when hardware limitations exist.

---

## Template for New Entries

```markdown
### Issue #N: Brief Description

**Date:** YYYY-MM-DD

**Problem:**
Clear description of what went wrong

**Investigation:**
Steps taken to identify the issue

**Root Cause:**
Why the problem occurred

**Solution:**
How it was fixed

**Files Affected:**
- List of files that needed changes

**Lesson:**
Key takeaway to avoid repeating this mistake
```

---

**Note:** This file should be updated whenever we discover API quirks, make incorrect assumptions, or find solutions to tricky problems.
