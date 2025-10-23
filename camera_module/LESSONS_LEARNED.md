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
