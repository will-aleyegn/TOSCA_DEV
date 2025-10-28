# Start Here - Quick Project Setup

⚠️ **DEPRECATION NOTICE:** This document is being replaced by the new streamlined onboarding system.

**Please use instead:** `presubmit/ONBOARDING.md` (single entry point, 2-minute read)

**Why the change:**
- Reduces onboarding from 6 documents to 1
- Automatic session resume from checkpoints
- <30 second recovery after crashes
- Better organized, machine-readable format

**This document will remain for reference during transition period.**

---

**Purpose:** Fast 5-step setup guide for new development sessions (LEGACY)

**Last Updated:** 2025-10-23

---

## Quick Start (5 Steps)

### 1. Read Git Content Policy (MANDATORY)

**File:** presubmit/reference/GIT_CONTENT_POLICY.md

**Critical Rule:** Never include AI/medical/FDA references in git-tracked files.

This is a public repository - content must be appropriate for public viewing.

---

### 2. Understand Project Context

**Project:** TOSCA Laser Control System

**What it is:** Safety-critical laser control system with:
- Laser power control (Arroyo Instruments)
- Linear actuator (Xeryon)
- Camera system (Allied Vision)
- GPIO safety interlocks (footpedal, smoothing device, photodiode)
- Session management (SQLite database)
- Treatment protocols with configurable power ramping

**Current Phase:** Phase 1 complete - UI shell, camera module, actuator module, protocol core

---

### 3. Check Current Status

**File:** presubmit/active/PROJECT_STATUS.md

Shows complete project state:
- What's done
- What's in progress
- What's next
- Module status
- Recent work

---

### 4. Review Coding Standards

**File:** presubmit/reference/CODING_STANDARDS.md

**Key Principles:**
- **⚠️ CRITICAL: Always use native hardware API features before software workarounds**
- Minimal code only (no extras, no decorative elements)
- Type hints on all functions
- Comprehensive docstrings for safety-critical code
- All code must pass pre-commit hooks (Black, Flake8, MyPy, isort)
- Update LESSONS_LEARNED.md for API quirks

**Hardware API Rule:** Before implementing any camera, actuator, or sensor control:
1. Read hardware API documentation
2. Check manufacturer examples
3. Use native hardware features (frame rate, positioning, etc.)
4. Only use software workarounds if hardware doesn't support the feature

**Safety-Critical:** Every line matters. This is safety-critical software.

---

### 5. Check Recent Work

**File:** presubmit/active/WORK_LOG.md

Real-time tracking of:
- Recent actions and changes
- Current focus areas
- Decisions made
- Issues discovered

---

## Architecture Documentation

Comprehensive technical docs in `docs/architecture/`:

1. **01_system_overview.md** - Complete system architecture
2. **02_database_schema.md** - Database design
3. **03_safety_system.md** - Safety architecture (critical)
4. **04_treatment_protocols.md** - Protocol design
5. **05_image_processing.md** - Camera and image processing
6. **06_protocol_builder.md** - Protocol Builder specification

---

## Configuration Files

**File:** presubmit/reference/CONFIGURATION.md

Complete guide to all 11 configuration files:
- setup.py, pyproject.toml, requirements.txt
- .gitignore, .flake8, .pylintrc
- .pre-commit-config.yaml

---

## Development Workflow

### Before Starting Work

1. Read GIT_CONTENT_POLICY.md
2. Check PROJECT_STATUS.md for current state
3. Review WORK_LOG.md for recent work
4. Check git status and recent commits

### During Work

1. **Check hardware API documentation FIRST** (camera, actuator, sensor controls)
2. Follow CODING_STANDARDS.md principles
3. Write minimal code only
4. Update LESSONS_LEARNED.md for API quirks
5. Keep WORK_LOG.md updated
6. Test thoroughly

### Before Committing

1. Run pre-commit hooks: `pre-commit run --all-files`
2. Verify no prohibited content (see GIT_CONTENT_POLICY.md)
3. Update WORK_LOG.md
4. Update PROJECT_STATUS.md if milestone reached
5. Write clear, concise commit message

---

## Key Directories

```
TOSCA-dev/
├── src/                    # Main application code
│   ├── ui/                # PyQt6 GUI
│   ├── core/              # Business logic
│   ├── hardware/          # Hardware abstraction
│   ├── database/          # SQLAlchemy models
│   └── image_processing/  # Camera and vision
├── components/            # Hardware API exploration
│   ├── camera_module/     # VmbPy testing (DONE)
│   └── actuator_module/   # Xeryon testing (DONE)
├── docs/                  # Documentation
│   ├── architecture/      # System design docs
│   └── project/           # Project management docs
├── data/                  # Runtime data (gitignored)
│   ├── protocols/         # Protocol JSON files
│   ├── logs/              # Application logs
│   └── sessions/          # Session recordings
├── tests/                 # Test suite
└── presubmit/            # Internal docs (gitignored)
```

---

## Hardware Components

1. **Laser Controller:** Arroyo Instruments laser driver and TEC Controller (serial)
2. **Linear Actuator:** Xeryon linear stage
3. **Camera:** Allied Vision 1800 U-158c (USB 3.0)
4. **GPIO Controllers:** 2x Adafruit FT232H Breakout (USB-C)
5. **Footpedal:** Normally-open momentary switch
6. **Hotspot Smoothing Device:** With digital signal output
7. **Photodiode circuit:** With voltage output (0-5V range)

---

## Technology Stack

**Core:**
- Python 3.10+
- PyQt6 (GUI)
- SQLite (database)
- OpenCV (image processing)
- NumPy (numerical operations)

**Hardware Libraries:**
- pyserial (Arroyo laser)
- Xeryon API (actuator)
- VmbPy (Allied Vision camera)
- adafruit-blinka (FT232H GPIO/ADC)

---

## Common Commands

### Development

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run pre-commit hooks
pre-commit run --all-files

# Run main application
python main.py
```

### Testing

```bash
# Run camera tests
cd components/camera_module/examples
python 01_list_cameras.py
python 05_continuous_stream.py

# Run actuator tests
cd components/actuator_module/examples
python 01_test_connection.py

# Run unit tests (when available)
pytest
```

### Git

```bash
# Check status
git status
git log --oneline -10

# Create commit
git add <files>
git commit -m "message"

# Push to remote
git push origin main
```

---

## Getting Help

**Documentation:**
- Start with this file for quick orientation
- PROJECT_STATUS.md for current state
- CODING_STANDARDS.md for development rules
- Architecture docs for technical details

**Common Issues:**
- Check LESSONS_LEARNED.md in relevant module
- Review git commit history for context
- Check pre-commit hook failures

---

## Remember

1. **Git Content Policy:** No AI/medical/FDA refs in git-tracked files
2. **Minimal Code:** Only write what's needed
3. **Safety First:** This is safety-critical software
4. **Document Quirks:** Update LESSONS_LEARNED.md
5. **Update Logs:** Keep WORK_LOG.md current

---

**Repository:** https://github.com/will-aleyegn/TOSCA_DEV.git
**Working Directory:** C:\Users\wille\Desktop\TOSCA-dev
**Python Version:** 3.10+
**License:** (To be determined)

---

**You're ready to start developing!**

If this is a new session, check PROJECT_STATUS.md to see what was last worked on,
then decide whether to continue that work or start something new.
