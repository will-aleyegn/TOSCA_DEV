# Manufacturer Documentation Index

**Last Updated:** 2025-10-25
**Purpose:** Central index for all hardware manufacturer documentation
**Total Documentation:** ~8.3 MB organized across 3 components

---

## Quick Navigation

| Component | Hardware | Documentation Location | Size |
|-----------|----------|----------------------|------|
| **Camera** | Allied Vision 1800 U-158c | `camera_module/manufacturer_docs/` | 3.8 MB |
| **Actuator** | Xeryon XLA-5-125-10MU | `actuator_module/manufacturer_docs/` | 2.3 MB |
| **Laser** | Arroyo 4320 Series | `laser_control/manufacturer_docs/` | 2.2 MB |

**Total:** 8.3 MB of manufacturer manuals, API references, and SDK documentation

---

## Camera Module Documentation

**Location:** `components/camera_module/manufacturer_docs/`

### Vimba Manuals (3.7 MB)
- [DONE] Vimba Manual.pdf (832 KB) - Complete SDK documentation
- [DONE] Vimba Quickstart Guide.pdf (377 KB) - Quick start guide
- [DONE] Vimba Tour.pdf (914 KB) - SDK capabilities tour
- [DONE] Vimba Viewer Guide.pdf (1.5 MB) - Viewer application guide
- [DONE] Terms and Conditions (117 KB)

### VmbPy API Reference (138 KB)
- [DONE] Camera.txt - Camera class reference
- [DONE] Feature.txt - Feature control reference (most important)
- [DONE] Frame.txt - Frame acquisition reference
- [DONE] Stream.txt - Streaming reference
- [DONE] VmbSystem.txt - System-level reference
- [DONE] Interface.txt, LocalDevice.txt, TransportLayer.txt
- [DONE] Error.txt - Error handling
- [DONE] Index files (genindex, index, search)

**README:** `camera_module/manufacturer_docs/README.md`

---

## Actuator Module Documentation

**Location:** `components/actuator_module/manufacturer_docs/`

### Xeryon Manuals (2.1 MB)
- [DONE] Controller Manual.pdf (1.8 MB) - Complete command reference
- [DONE] XLA5.pdf (283 KB) - Stage specifications

### Xeryon Library (163 KB)
- [DONE] Xeryon.py (60 KB) - v1.88 official Python library
- [DONE] Xeryon Python-Matlab Library - Complete library with examples
- [DONE] Jupyter notebooks with examples
- [DONE] README.md - Library usage guide

**README:** `actuator_module/manufacturer_docs/README.md`

---

## Laser Control Documentation

**Location:** `components/laser_control/manufacturer_docs/`

### Arroyo Manuals (2.1 MB)
- [DONE] Arroyo_4320_Manual.pdf (851 KB) - Device operation manual
- [DONE] ArroyoComputerInterfacingManual.pdf (1.3 MB) - Programming guide

### Arroyo SDK (141 KB)
- [DONE] arroyo_tec/ - Official Python SDK package
- [DONE] ARROYO_SDK_README.md - SDK usage guide

**README:** `laser_control/manufacturer_docs/README.md`

---

## Documentation Organization

### Folder Structure Pattern

Each component follows this structure:

```
components/<component_name>/
├── manufacturer_docs/
│   ├── README.md              ← Navigation guide (start here)
│   ├── <vendor>_manuals/      ← PDF manuals and datasheets
│   └── <vendor>_library/      ← SDK, Python libraries, API references
│
├── examples/                  ← Custom test scripts
├── docs/                      ← Custom documentation
└── README.md                  ← Component overview
```

---

## What's Included vs Excluded

### [DONE] Included (Organized)

**Manuals:**
- Device operation manuals
- Programming/interfacing guides
- Quickstart guides
- Datasheets and specifications

**API Documentation:**
- Python API reference files
- SDK documentation
- Command references
- Example code from manufacturers

**Libraries:**
- Official Python libraries
- SDK packages
- Manufacturer-provided code

### [FAILED] Not Included

**Installers:**
- Full SDK installers (Vimba_v6.0_Windows.exe - 186 MB)
- VimbaX installer (61 MB)
- Keep originals at: `C:\Users\wille\Desktop\allied_vision_software\`

**Full Source:**
- Complete Vimba SDK source (use installer)
- VimbaPy full distribution (use pip install vmbpy)

**Binary Files:**
- DLLs, executables, compiled libraries
- Driver packages (get from manufacturer websites)

---

## Source Directories

Documentation was organized from these external locations:

| Source Directory | Contents | Status |
|-----------------|----------|--------|
| `C:\Users\wille\Desktop\allied_vision_software\` | Vimba SDK, VmbPy | Manuals copied, keep installers |
| `C:\Users\wille\Desktop\VmbPy_Function_Reference\` | VmbPy API HTML/TXT | TXT files copied |
| `C:\Users\wille\Desktop\vmpy\` | VmbPy docs + examples | TXT files copied |
| `C:\Users\wille\Desktop\stage-control\` | Xeryon library + manuals | All useful files copied |
| `C:\Users\wille\Desktop\arroyo_laser_control\` | Arroyo manuals + SDK | All files copied |
| `C:\Users\wille\Desktop\CAMERA-TESTFILES\` | Test scripts | Custom scripts (already in examples/) |

**Original files can be archived or deleted** - all useful content now organized in components/

---

## Usage Guidelines

### Finding Documentation

**"I need to know how to control the camera"**
→ Go to `camera_module/manufacturer_docs/README.md`
→ Read VmbPy API Reference section
→ Check Feature.txt and Camera.txt

**"What are the actuator specifications?"**
→ Go to `actuator_module/manufacturer_docs/README.md`
→ Read xeryon_manuals/XLA5.pdf

**"How do I send commands to the laser?"**
→ Go to `laser_control/manufacturer_docs/README.md`
→ Read arroyo_manuals/ArroyoComputerInterfacingManual.pdf

### Using with TOSCA Code

Each manufacturer_docs/README.md includes:
- Quick reference for common tasks
- Integration points with TOSCA codebase
- Links to production code (`src/hardware/`)
- Links to example code (`examples/`)
- Hardware API usage guidelines

### Following Hardware API Rule

WARNING: **CRITICAL:** Per CODING_STANDARDS.md, ALWAYS check manufacturer documentation BEFORE implementing hardware control.

**Correct workflow:**
1. Read manufacturer documentation first
2. Identify native hardware features
3. Use native features in implementation
4. Only implement software workarounds if hardware doesn't support the feature

**Example:**
- [FAILED] BAD: Implement frame rate throttling in software
- [DONE] GOOD: Use camera's `AcquisitionFrameRate` feature

---

## Maintenance

### When to Update

Update manufacturer documentation when:
- New firmware version released
- Updated manuals available from manufacturer
- New SDK version released
- Discovered better documentation source

### How to Update

1. Download new documentation from manufacturer website
2. Replace files in appropriate `manufacturer_docs/` folder
3. Update README.md if structure changes
4. Update version information in README
5. Document changes in WORK_LOG.md

### Keeping External Directories

**Recommendation:** Archive external directories after verification

```bash
# Verify all documentation copied
find components/*/manufacturer_docs -type f | wc -l

# Archive originals
mkdir ~/Desktop/archived_manufacturer_files
mv ~/Desktop/allied_vision_software ~/Desktop/archived_manufacturer_files/
mv ~/Desktop/stage-control ~/Desktop/archived_manufacturer_files/
mv ~/Desktop/arroyo_laser_control ~/Desktop/archived_manufacturer_files/
# ... etc
```

**Keep installers accessible:**
- Vimba SDK installer may be needed for full installation
- Store in safe location or download fresh from manufacturer

---

## File Size Summary

```
Camera Module:
  vimba_manuals/           3.7 MB (5 PDFs)
  vmbpy_api_reference/     138 KB (12 TXT files)
  README.md                8 KB
  Total:                   ~3.84 MB

Actuator Module:
  xeryon_manuals/          2.1 MB (2 PDFs)
  xeryon_library/          163 KB (Python library + notebooks)
  README.md                8 KB
  Total:                   ~2.27 MB

Laser Control:
  arroyo_manuals/          2.1 MB (2 PDFs)
  arroyo_sdk/              141 KB (Python SDK + README)
  README.md                8 KB
  Total:                   ~2.25 MB

Grand Total:               ~8.36 MB
```

---

## External Resources

### Manufacturer Websites

**Allied Vision (Camera):**
- Website: https://www.alliedvision.com/
- Downloads: https://www.alliedvision.com/en/support/software-downloads/
- VmbPy GitHub: https://github.com/alliedvision/VmbPy

**Xeryon (Actuator):**
- Website: https://www.xeryon.com/
- Product Page: https://www.xeryon.com/product/xla-linear-actuator/

**Arroyo Instruments (Laser):**
- Website: https://www.arroyoinstruments.com/
- Support: https://www.arroyoinstruments.com/support/
- Downloads: https://www.arroyoinstruments.com/downloads/

---

## Notes

**Organization Date:** 2025-10-25
**Organized By:** Manufacturer documentation consolidation project
**Purpose:** Centralize all hardware documentation for easy reference and compliance

**Benefits:**
- [DONE] All documentation in one place (project repository)
- [DONE] Easy navigation with README files
- [DONE] Clear organization by component
- [DONE] Version controlled with git
- [DONE] Supports Hardware API Usage Rule compliance
- [DONE] Facilitates future development and onboarding

---

**Last Updated:** 2025-10-25
**Location:** components/MANUFACTURER_DOCS_INDEX.md
