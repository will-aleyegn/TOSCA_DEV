# Camera Module - Manufacturer Documentation

**Last Updated:** 2025-10-25
**Hardware:** Allied Vision 1800 U-158c Camera
**SDK:** Vimba 6.0 with VmbPy Python API

---

## Folder Structure

```
manufacturer_docs/
├── README.md                    (this file)
├── vimba_manuals/              Allied Vision Vimba SDK documentation
│   ├── Vimba Manual.pdf        (832 KB - comprehensive SDK manual)
│   ├── Vimba Quickstart Guide.pdf (377 KB - quick start)
│   ├── Vimba Tour.pdf          (914 KB - SDK tour)
│   ├── Vimba Viewer Guide.pdf  (1.5 MB - viewer application guide)
│   └── Terms_and_Conditions_Vimba_Downloads-EN_1.0.1.pdf
│
└── vmbpy_api_reference/        VmbPy Python API reference
    ├── Camera.txt              Camera class API reference
    ├── Feature.txt             Feature class API reference
    ├── Frame.txt               Frame class API reference
    ├── Interface.txt           Interface class API reference
    ├── LocalDevice.txt         LocalDevice class API reference
    ├── Stream.txt              Stream class API reference
    ├── TransportLayer.txt      TransportLayer class API reference
    ├── VmbSystem.txt           VmbSystem class API reference
    ├── Error.txt               Error handling reference
    ├── genindex.txt            General index
    ├── index.txt               Main index
    └── search.txt              Search index
```

---

## Quick Reference

### Start Here

**For quick setup:**
→ Read `vimba_manuals/Vimba Quickstart Guide.pdf`

**For comprehensive understanding:**
→ Read `vimba_manuals/Vimba Manual.pdf`

**For Python API:**
→ Read `vmbpy_api_reference/Camera.txt` and `Feature.txt`

---

## Vimba Manuals

### Vimba Manual.pdf (832 KB)
**Purpose:** Complete Vimba SDK documentation
**Contents:**
- SDK architecture overview
- Feature access and control
- Image acquisition concepts
- Transport layer interfaces
- Advanced features (triggers, events, chunks)

**Use when:** Understanding SDK architecture, implementing advanced features

---

### Vimba Quickstart Guide.pdf (377 KB)
**Purpose:** Get started quickly with Vimba
**Contents:**
- Installation instructions
- First steps with SDK
- Basic configuration
- Common workflows

**Use when:** First time setup, quick reference for basic operations

---

### Vimba Tour.pdf (914 KB)
**Purpose:** Guided tour of Vimba SDK capabilities
**Contents:**
- Feature exploration
- Camera configuration examples
- Image acquisition patterns
- Performance optimization

**Use when:** Learning what the SDK can do, exploring capabilities

---

### Vimba Viewer Guide.pdf (1.5 MB)
**Purpose:** Guide to Vimba Viewer application
**Contents:**
- Viewer interface overview
- Camera discovery and connection
- Feature adjustment
- Image capture and save
- Troubleshooting

**Use when:** Testing camera manually, verifying camera configuration

---

## VmbPy API Reference

### Camera.txt (15 KB)
**Contents:**
- Camera class methods and properties
- Connection/disconnection
- Feature access
- Frame acquisition
- Streaming control

**Key methods:**
- `get_id()` - Get camera ID
- `get_all_features()` - List all features
- `get_feature_by_name(name)` - Access specific feature
- `start_streaming(callback)` - Start frame streaming
- `stop_streaming()` - Stop streaming

---

### Feature.txt (36 KB)
**Contents:**
- Feature class (most important for camera control)
- Feature types (Integer, Float, String, Boolean, Enum, Command)
- Getting and setting feature values
- Feature constraints and ranges
- Feature access modes

**Key methods:**
- `get()` - Read feature value
- `set(value)` - Write feature value
- `get_range()` - Get valid value range
- `is_readable()` / `is_writeable()` - Check access
- `get_name()` - Get feature name

---

### Frame.txt (14 KB)
**Contents:**
- Frame class for acquired images
- Frame buffer management
- Image data access
- Frame metadata (timestamp, frame ID)
- Conversion to numpy arrays

**Key methods:**
- `get_buffer()` - Get image buffer
- `get_timestamp()` - Get frame timestamp
- `get_frame_id()` - Get frame ID
- `convert_pixel_format()` - Convert pixel format
- `as_numpy_ndarray()` - Convert to NumPy array

---

### VmbSystem.txt (11 KB)
**Contents:**
- VmbSystem singleton class
- Camera discovery
- System-level configuration
- Transport layer access

**Key methods:**
- `get_all_cameras()` - List all cameras
- `get_camera_by_id(id)` - Get specific camera
- `get_all_interfaces()` - List interfaces
- `get_version()` - Get SDK version

---

## Common Use Cases

### Use Case 1: Camera Discovery
**Documentation:** VmbSystem.txt
**Example code location:** `../examples/01_list_cameras.py`

### Use Case 2: Camera Feature Control
**Documentation:** Camera.txt, Feature.txt
**Example code location:** `../examples/04_explore_features.py`

### Use Case 3: Frame Streaming
**Documentation:** Camera.txt, Frame.txt, Stream.txt
**Example code location:** `../examples/05_continuous_stream.py`

### Use Case 4: Auto Features (Exposure, Gain)
**Documentation:** Feature.txt (Auto feature section)
**Example code location:** `../examples/06_set_auto_exposure.py`

---

## Integration with TOSCA

### Where This is Used

**Production code:**
- `src/hardware/camera_controller.py` - Main camera HAL implementation
- Uses VmbPy API for all camera operations

**Testing code:**
- `components/camera_module/examples/` - Example scripts
- `components/camera_module/tests/` - Unit tests

**Documentation:**
- `components/camera_module/README.md` - Module overview
- `components/camera_module/LESSONS_LEARNED.md` - API quirks and discoveries

---

## Important Notes

### VmbPy API Quirks (See LESSONS_LEARNED.md)

1. **British spelling:** `is_writeable()` not `is_writable()`
2. **Frame callback signature:** Requires 3 parameters `(cam, stream, frame)`
3. **Feature access:** Use `get_feature_by_name()` instead of direct attribute access
4. **Frame rate:** `AcquisitionFrameRate` range is dynamic, query before setting

---

## External Resources

**Allied Vision Website:**
- https://www.alliedvision.com/en/support/software-downloads/

**VmbPy GitHub:**
- https://github.com/alliedvision/VmbPy

**Allied Vision Support:**
- https://www.alliedvision.com/en/support/

---

## Version Information

- **Vimba SDK:** 6.0
- **VmbPy:** Included with Vimba 6.0
- **Camera Model:** Allied Vision 1800 U-158c
- **Interface:** USB 3.0

---

**Last Updated:** 2025-10-25
**Location:** components/camera_module/manufacturer_docs/README.md
