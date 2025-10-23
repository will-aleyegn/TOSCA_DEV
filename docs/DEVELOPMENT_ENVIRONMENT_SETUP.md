# TOSCA Development Environment Setup Guide

**Project:** TOSCA Laser Control System
**Status:** Pre-Alpha Development
**Date:** 2025-10-22
**Python Version:** 3.10+

This document provides a complete, step-by-step guide to set up the development environment for the TOSCA project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Repository Setup](#initial-repository-setup)
3. [Project Structure Creation](#project-structure-creation)
4. [Python Virtual Environment](#python-virtual-environment)
5. [Dependencies Installation](#dependencies-installation)
6. [Configuration Files](#configuration-files)
7. [Coding Standards Setup](#coding-standards-setup)
8. [Pre-Commit Hooks](#pre-commit-hooks)
9. [Verification](#verification)
10. [Daily Development Workflow](#daily-development-workflow)

---

## 1. Prerequisites

### Required Software

**Python 3.10 or higher:**
```bash
python --version
# Should output: Python 3.10.x or higher
```

**Git:**
```bash
git --version
# Should output: git version 2.x.x or higher
```

**GitHub Account:**
- Personal access token with `repo`, `workflow`, `read:org` permissions
- Generate at: GitHub → Settings → Developer settings → Personal access tokens

**Node.js (for MCP servers):**
```bash
node --version
npm --version
```

### System Requirements

- **OS:** Windows 10 (recommended for hardware compatibility)
- **RAM:** 8GB minimum
- **Storage:** 5GB free space minimum
- **USB Ports:** Multiple USB 3.0 ports for hardware

---

## 2. Initial Repository Setup

### Step 1: Create GitHub Repository

Repository created at:
```
https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development
```

### Step 2: Clone or Initialize Local Repository

**Option A: Clone existing repository:**
```bash
cd C:\Users\wille\Desktop
git clone https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development.git TOSCA-dev
cd TOSCA-dev
```

**Option B: Initialize new repository:**
```bash
cd C:\Users\wille\Desktop\TOSCA-dev
git init
git remote add origin https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development.git
```

### Step 3: Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 4: Create .gitignore

Created comprehensive `.gitignore` file to exclude:
- Python artifacts (`__pycache__`, `*.pyc`, `*.egg-info`)
- Virtual environment (`venv/`, `.venv/`)
- Application data (`data/`, `*.db`, `sessions/`, `logs/`)
- Patient data (critical security requirement)
- IDE files (`.vscode/`, `.idea/`)
- Environment variables (`.env`, `.mcp.json`)
- Temporary files

**File location:** `.gitignore`

---

## 3. Project Structure Creation

### Directory Structure

Created the following directory hierarchy:

```
TOSCA-dev/
├── .claude/                    # Claude Code configuration
│   ├── agents/                # Specialized AI agents
│   ├── commands/              # Custom slash commands
│   ├── scripts/               # Utility scripts
│   ├── skills/                # Custom skills
│   └── settings.json          # Claude settings
├── .github/                   # GitHub configuration
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                      # Documentation
│   ├── architecture/          # Architecture specifications
│   └── DEVELOPMENT_ENVIRONMENT_SETUP.md
├── src/                       # Source code
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── config/               # Configuration management
│   ├── core/                 # Business logic
│   ├── database/             # Database operations
│   ├── hardware/             # Hardware abstraction layer
│   ├── image_processing/     # Computer vision
│   ├── ui/                   # PyQt6 user interface
│   └── utils/                # Utility functions
├── tests/                     # Test suite
│   ├── test_core/
│   ├── test_database/
│   ├── test_hardware/
│   ├── test_image_processing/
│   ├── test_integration/
│   └── test_safety/
├── data/                      # Application data (git-ignored)
│   ├── sessions/             # Video recordings
│   └── logs/                 # Application logs
└── venv/                      # Virtual environment (git-ignored)
```

### Commands Used

```bash
# Create source directories
mkdir -p src/config src/ui src/core src/hardware src/image_processing src/database src/utils

# Create test directories
mkdir -p tests/test_hardware tests/test_core tests/test_safety tests/test_integration tests/test_image_processing tests/test_database

# Create data directories
mkdir -p data/sessions data/logs

# Create GitHub directory
mkdir -p .github
```

### __init__.py Files Created

Created `__init__.py` in all Python package directories:
- `src/__init__.py` - Main package initialization
- `src/config/__init__.py` - Configuration package
- `src/ui/__init__.py` - UI package
- `src/core/__init__.py` - Core logic package
- `src/hardware/__init__.py` - Hardware abstraction package
- `src/image_processing/__init__.py` - Image processing package
- `src/database/__init__.py` - Database package
- `src/utils/__init__.py` - Utilities package
- `tests/__init__.py` - Test package

---

## 4. Python Virtual Environment

### Step 1: Create Virtual Environment

```bash
cd C:\Users\wille\Desktop\TOSCA-dev
python -m venv venv
```

This creates an isolated Python environment in the `venv/` directory.

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

When activated, your prompt will show `(venv)` prefix.

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

**Result:**
- pip upgraded to version 25.2
- setuptools upgraded to version 80.9.0
- wheel upgraded to version 0.45.1

---

## 5. Dependencies Installation

### Step 1: Create requirements.txt

Created `requirements.txt` with categorized dependencies:

**GUI Framework & Visualization:**
- PyQt6 >= 6.6.0
- pyqtgraph >= 0.13.3

**Image Processing & Computer Vision:**
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- Pillow >= 10.0.0

**Hardware Interfaces:**
- pyserial >= 3.5
- adafruit-blinka >= 8.20.0
- adafruit-circuitpython-busdevice >= 5.2.0

**Database & ORM:**
- sqlalchemy >= 2.0.0
- alembic >= 1.12.0

**Data Validation & Configuration:**
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- jsonschema >= 4.19.0

**Logging & Utilities:**
- python-dateutil >= 2.8.2
- loguru >= 0.7.0
- python-dotenv >= 1.0.0

**Development & Testing:**
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-qt >= 4.2.0
- pytest-mock >= 3.11.0
- black >= 23.7.0
- flake8 >= 6.1.0
- mypy >= 1.5.0
- pylint >= 2.17.0

**Safety & Security Analysis:**
- safety >= 2.3.0
- bandit >= 1.7.5

**Documentation:**
- sphinx >= 7.1.0
- sphinx-rtd-theme >= 1.3.0

### Step 2: Create requirements-dev.txt

Created `requirements-dev.txt` for development-only tools:
- ipython >= 8.14.0
- ipdb >= 0.13.13
- pre-commit >= 3.3.0

### Step 3: Install All Dependencies

```bash
python -m pip install -r requirements.txt
```

**Installation Summary:**
- Total packages installed: 100+
- Installation time: ~2-3 minutes
- Total size: ~500 MB

**Key packages verified:**
```bash
python -c "import PyQt6; import cv2; import numpy; print('All core dependencies imported successfully')"
```

---

## 6. Configuration Files

### setup.py

Created package metadata and distribution configuration:

**File location:** `setup.py`

**Key configurations:**
- Package name: `tosca-laser-control`
- Version: `0.1.0-alpha`
- Python requirement: `>=3.10`
- Entry point: `tosca-control=main:main`
- Development dependencies in `extras_require`

### pyproject.toml

Created tool configuration for development tools:

**File location:** `pyproject.toml`

**Configured tools:**

**Black (code formatter):**
- Line length: 100
- Target versions: Python 3.10, 3.11, 3.12

**isort (import sorter):**
- Profile: black (compatible with Black)
- Line length: 100
- Multi-line output: 3

**MyPy (type checker):**
- Python version: 3.10
- Strict type checking enabled
- Ignore missing imports for third-party libraries (cv2, pyqtgraph, serial)

**Pylint (code analyzer):**
- Max line length: 100
- Disabled checks: C0103, C0114, R0913, R0801

### pytest.ini

Created test configuration:

**File location:** `pytest.ini`

**Key configurations:**
- Test paths: `tests/`
- Coverage reporting: HTML and terminal
- Coverage requirement: 80% minimum
- Custom markers: unit, integration, safety, hardware, slow, gui

**Test discovery patterns:**
- `test_*.py`
- `*_test.py`
- `Test*` classes
- `test_*` functions

### .env.example

Created environment variable template:

**File location:** `.env.example`

**Categories:**
- Application settings (environment, log level)
- Database configuration
- Hardware settings (laser, actuator, camera, GPIO)
- Safety configuration
- Session recording settings
- Development/testing options

**Usage:**
```bash
cp .env.example .env
# Edit .env with actual values
```

---

## 7. Coding Standards Setup

### CODING_STANDARDS.md

Created comprehensive coding standards document:

**File location:** `CODING_STANDARDS.md`

**Core principles:**
1. Write only what is required
2. No decorative elements
3. Documentation is functional
4. Every line must have a purpose

**Key requirements:**
- Type hints on all functions
- Docstrings for safety-critical code
- No commented-out code
- No TODO comments without tickets
- No placeholder functions
- Max line length: 100 characters

### .flake8

Created Flake8 linting configuration:

**File location:** `.flake8`

**Configuration:**
- Max line length: 100
- Max complexity: 10
- Ignored errors: E203 (whitespace before ':'), W503 (line break before binary operator)
- Per-file ignores: `__init__.py:F401` (unused imports allowed in __init__ files)

### .pylintrc

Created Pylint configuration:

**File location:** `.pylintrc`

**Key limits:**
- Max arguments: 7
- Max attributes: 10
- Max locals: 15
- Max returns: 6
- Max branches: 12
- Max statements: 50

**Disabled messages:**
- C0103: Invalid name (allows Qt naming conventions)
- C0114: Missing module docstring
- R0913: Too many arguments
- R0801: Similar lines in multiple files

### .github/PULL_REQUEST_TEMPLATE.md

Created pull request template with coding standards checklist:

**File location:** `.github/PULL_REQUEST_TEMPLATE.md`

**Includes:**
- Description section
- Type of change checkboxes
- Coding standards checklist (14 items)
- Safety review checklist
- Testing requirements
- Documentation requirements

---

## 8. Pre-Commit Hooks

### Step 1: Create .pre-commit-config.yaml

Created pre-commit hooks configuration:

**File location:** `.pre-commit-config.yaml`

**Configured hooks:**

**pre-commit-hooks (v4.5.0):**
- trailing-whitespace: Remove trailing whitespace
- end-of-file-fixer: Ensure files end with newline
- check-yaml: Validate YAML files
- check-added-large-files: Prevent large files (max 1000 KB)
- check-merge-conflict: Detect merge conflict markers
- debug-statements: Prevent debug imports (pdb, ipdb)
- mixed-line-ending: Ensure consistent line endings

**Black (24.3.0):**
- Automatic code formatting
- Line length: 100

**Flake8 (7.0.0):**
- Linting checks
- Max line length: 100

**isort (5.13.2):**
- Import sorting
- Black-compatible profile

**MyPy (v1.8.0):**
- Type checking
- Ignore missing imports

### Step 2: Install pre-commit

```bash
python -m pip install pre-commit
```

### Step 3: Install Git Hooks

```bash
pre-commit install
```

**Result:**
```
pre-commit installed at .git\hooks\pre-commit
```

### Step 4: Test Pre-Commit (Optional)

```bash
pre-commit run --all-files
```

This runs all hooks on all files to verify configuration.

---

## 9. Verification

### Step 1: Verify Python Environment

```bash
# Check Python version
python --version

# Check pip
pip --version

# Check virtual environment is activated
which python  # Linux/Mac
where python  # Windows
# Should point to venv/Scripts/python.exe or venv/bin/python
```

### Step 2: Verify Core Dependencies

```bash
python -c "import PyQt6; print('PyQt6:', PyQt6.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
```

### Step 3: Verify Development Tools

```bash
black --version
flake8 --version
mypy --version
pylint --version
pytest --version
```

### Step 4: Verify Pre-Commit

```bash
pre-commit --version
```

### Step 5: Verify Git Configuration

```bash
git status
git remote -v
git branch
```

### Step 6: Run Application Entry Point

```bash
python src/main.py
```

**Expected output:**
```
INFO - TOSCA Laser Control System Starting
WARNING - Main window not yet implemented - placeholder mode
INFO - Application ready. Press Ctrl+C to exit.
```

---

## 10. Daily Development Workflow

### Starting Development

```bash
# Navigate to project
cd C:\Users\wille\Desktop\TOSCA-dev

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Pull latest changes
git pull origin main
```

### Before Writing Code

1. Create feature branch:
```bash
git checkout -b feature/feature-name
```

2. Review coding standards:
```bash
cat CODING_STANDARDS.md
```

### While Writing Code

Run formatters and linters frequently:

```bash
# Format code
black src/

# Check imports
isort src/

# Lint code
flake8 src/

# Type check
mypy src/

# Run tests
pytest
```

### Before Committing

1. Run all quality checks:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=src
```

2. Stage changes:
```bash
git add .
```

3. Commit (pre-commit hooks run automatically):
```bash
git commit -m "Descriptive commit message"
```

If pre-commit hooks fail:
- Review the errors
- Fix the issues
- Stage fixes: `git add .`
- Commit again

4. Push to GitHub:
```bash
git push origin feature/feature-name
```

5. Create pull request on GitHub

### Updating Dependencies

```bash
# Update specific package
pip install --upgrade package-name

# Update all packages (carefully)
pip list --outdated

# Update requirements.txt
pip freeze > requirements.txt
```

---

## Configuration File Summary

| File | Purpose | Location |
|------|---------|----------|
| `.gitignore` | Files to exclude from Git | Root |
| `requirements.txt` | Production dependencies | Root |
| `requirements-dev.txt` | Development dependencies | Root |
| `setup.py` | Package metadata | Root |
| `pyproject.toml` | Tool configurations | Root |
| `pytest.ini` | Test configuration | Root |
| `.env.example` | Environment variable template | Root |
| `.flake8` | Flake8 linting rules | Root |
| `.pylintrc` | Pylint configuration | Root |
| `.pre-commit-config.yaml` | Pre-commit hooks | Root |
| `CODING_STANDARDS.md` | Coding standards | Root |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template | `.github/` |

---

## MCP Configuration

### .mcp.json

GitHub token configured for GitHub MCP server:

**File location:** `.mcp.json`

**Configured servers:**
- context7: Documentation lookup
- memory: Knowledge graph
- github: GitHub API integration
- filesystem: File operations

**GitHub token setup:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

---

## Troubleshooting

### Virtual Environment Issues

**Issue:** Cannot activate venv
**Solution:**
```bash
# Windows: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Recreate venv if corrupted
rm -rf venv
python -m venv venv
```

### Dependency Installation Failures

**Issue:** Specific package fails to install
**Solution:**
```bash
# Install problem package separately
pip install package-name

# Check for system dependencies (Windows users may need Visual C++ build tools)
```

### Pre-Commit Hook Failures

**Issue:** Hooks fail on commit
**Solution:**
```bash
# Run hooks manually to see errors
pre-commit run --all-files

# Skip hooks if absolutely necessary (not recommended)
git commit --no-verify -m "message"

# Update hooks
pre-commit autoupdate
```

### Import Errors

**Issue:** Module not found
**Solution:**
```bash
# Ensure venv is activated
# Reinstall requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## Hardware-Specific Setup (Future)

When ready to connect hardware:

1. **Arroyo Laser Controller:**
   - Install serial drivers
   - Configure COM port in `.env`
   - Test connection: `python -m serial.tools.list_ports`

2. **Xeryon Actuator:**
   - Install Xeryon SDK
   - Configure connection string in `.env`

3. **Allied Vision Camera:**
   - Install Vimba SDK
   - Install VmbPy Python wrapper
   - Test: `python -c "from vmbpy import *"`

4. **FT232H GPIO:**
   - Install libusb drivers
   - Configure I2C/SPI/GPIO pins in `.env`
   - Test: `python -c "import board; print(dir(board))"`

---

## Next Steps

1. **Begin Phase 1 Development:**
   - Hardware abstraction layer
   - Safety interlock system
   - Basic GUI shell

2. **Set up CI/CD (optional):**
   - GitHub Actions for automated testing
   - Automated deployment

3. **Configure Documentation Generation:**
   - Sphinx auto-documentation
   - API reference generation

---

## References

- Python Virtual Environments: https://docs.python.org/3/library/venv.html
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Pre-commit Hooks: https://pre-commit.com/
- Black Code Formatter: https://black.readthedocs.io/
- Pytest Documentation: https://docs.pytest.org/

---

**Document Version:** 1.0
**Last Updated:** 2025-10-22
**Maintained By:** Development Team
