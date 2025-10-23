# Configuration Files Reference

**Purpose:** Complete guide to all configuration files in the TOSCA project

**Last Updated:** 2025-10-22

---

## Configuration File Organization

### Root Directory (Required Location)

These files MUST stay in root directory due to tool requirements:

#### Python Package Configuration
- **`setup.py`** - Package metadata and installation config
- **`pyproject.toml`** - Modern Python project configuration (PEP 518)
- **`requirements.txt`** - Production dependencies
- **`requirements-dev.txt`** - Development dependencies

#### Version Control
- **`.gitignore`** - Files to exclude from Git
- **`.git/`** - Git repository data (hidden)

#### Testing
- **`pytest.ini`** - Pytest configuration

#### Linting & Formatting (Root Required)
- **`.flake8`** - Flake8 linting rules
- **`.pylintrc`** - Pylint configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks

#### Environment
- **`.env.example`** - Environment variable template
- **`.env`** - Actual environment variables (git-ignored)

#### MCP Configuration
- **`.mcp.json`** - MCP server configuration (git-ignored)

---

## Detailed Configuration Guide

### 1. setup.py
**Purpose:** Package metadata for distribution
**Location:** Root (required)
**Used By:** pip, setuptools, build tools

**Key Settings:**
```python
name = "tosca-laser-control"
version = "0.1.0-alpha"
python_requires = ">=3.10"
entry_points = {"console_scripts": ["tosca-control=main:main"]}
```

**When to Edit:**
- Changing package version
- Adding new dependencies
- Modifying entry points
- Updating package metadata

---

### 2. pyproject.toml
**Purpose:** Modern Python project configuration
**Location:** Root (required)
**Used By:** Black, isort, MyPy, Pylint, build tools

**Sections:**
- `[build-system]` - Build requirements
- `[project]` - Project metadata
- `[tool.black]` - Black formatter settings
- `[tool.isort]` - Import sorting settings
- `[tool.mypy]` - Type checker settings
- `[tool.pylint]` - Pylint settings

**Key Settings:**
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.mypy]
python_version = "3.10"
warn_return_any = true
disallow_untyped_defs = true
```

**When to Edit:**
- Changing code formatting rules
- Modifying type checking strictness
- Updating linter configuration

---

### 3. requirements.txt
**Purpose:** Production dependencies
**Location:** Root (required)
**Used By:** pip install -r requirements.txt

**Structure:**
```
# Category comments for organization
PyQt6>=6.6.0
opencv-python>=4.8.0
# ... more packages
```

**When to Edit:**
- Adding new dependencies (ALWAYS)
- Updating package versions
- Removing unused packages

**Important:** Keep categorized with comments

---

### 4. requirements-dev.txt
**Purpose:** Development-only dependencies
**Location:** Root (required)
**Used By:** pip install -r requirements-dev.txt

**Contents:**
```
-r requirements.txt  # Include production deps
ipython>=8.14.0
ipdb>=0.13.13
pre-commit>=3.3.0
```

**When to Edit:**
- Adding development tools
- Never for production dependencies

---

### 5. .gitignore
**Purpose:** Exclude files from version control
**Location:** Root (required)
**Used By:** Git

**Critical Sections:**
```
# Python
__pycache__/
*.pyc
venv/

# Medical Device Data - DO NOT COMMIT
data/
*.db
*patient*

# Secrets
.env
.mcp.json
*.key
```

**When to Edit:**
- Adding new output directories
- Excluding new file types
- Protecting sensitive data

**Security Critical:** Never commit patient data or secrets

---

### 6. pytest.ini
**Purpose:** Test configuration
**Location:** Root (required)
**Used By:** pytest

**Key Settings:**
```ini
[pytest]
testpaths = tests
addopts = -v --cov=src --cov-fail-under=80

markers =
    unit: Unit tests
    integration: Integration tests
    safety: Safety-critical tests
    hardware: Hardware tests
```

**When to Edit:**
- Adding custom test markers
- Changing coverage requirements
- Modifying test paths

---

### 7. .flake8
**Purpose:** Linting rules
**Location:** Root (required by flake8)
**Used By:** flake8, pre-commit

**Key Settings:**
```ini
[flake8]
max-line-length = 100
max-complexity = 10
extend-ignore = E203, W503
```

**When to Edit:**
- Adjusting line length
- Changing complexity limits
- Adding ignored error codes

---

### 8. .pylintrc
**Purpose:** Advanced code analysis
**Location:** Root (required by pylint)
**Used By:** pylint, pre-commit

**Key Settings:**
```ini
[MESSAGES CONTROL]
disable = C0103, C0114, R0913

[DESIGN]
max-args = 7
max-branches = 12
```

**When to Edit:**
- Adjusting code complexity limits
- Disabling specific warnings
- Changing naming conventions

---

### 9. .pre-commit-config.yaml
**Purpose:** Automated code quality checks
**Location:** Root (required)
**Used By:** pre-commit hooks

**Hooks Configured:**
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- black (formatting)
- flake8 (linting)
- isort (import sorting)
- mypy (type checking)

**When to Edit:**
- Adding new hooks
- Updating hook versions
- Changing hook arguments

**Commands:**
```bash
pre-commit install          # Install hooks
pre-commit run --all-files  # Run manually
pre-commit autoupdate       # Update versions
```

---

### 10. .env.example
**Purpose:** Environment variable template
**Location:** Root
**Used By:** Documentation reference

**Structure:**
```bash
# Application Settings
APP_ENV=development
LOG_LEVEL=DEBUG

# Hardware Configuration
LASER_SERIAL_PORT=COM3
CAMERA_ID=DEV_...
```

**When to Edit:**
- Adding new environment variables
- Documenting configuration options

**Usage:**
```bash
cp .env.example .env
# Edit .env with actual values
```

**Important:** `.env` is git-ignored (contains secrets)

---

### 11. .mcp.json
**Purpose:** MCP server configuration
**Location:** Root
**Used By:** Claude Code MCP integration
**Status:** Git-ignored (contains tokens)

**Structure:**
```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "token_here"
      }
    }
  }
}
```

**When to Edit:**
- Configuring MCP servers
- Adding GitHub token
- Enabling new MCP features

---

## Configuration Best Practices

### 1. Version Control
- ✓ Commit all configuration files
- ✗ Never commit `.env` or `.mcp.json`
- ✓ Keep `.env.example` updated
- ✓ Document all configuration changes

### 2. Consistency
- Use consistent line length (100) across all tools
- Keep formatting rules aligned (Black + Flake8 + Pylint)
- Document why rules are disabled

### 3. Security
- Never commit secrets
- Use `.env` for sensitive data
- Keep `.gitignore` strict for medical device data
- Review `.gitignore` before adding new data types

### 4. Maintainability
- Comment configuration choices
- Document non-obvious settings
- Keep tools updated (pre-commit autoupdate)
- Test configuration changes

---

## Configuration Validation

### Check All Configurations
```bash
# Test formatting
black --check src/

# Test linting
flake8 src/

# Test type checking
mypy src/

# Test imports
isort --check src/

# Run all pre-commit hooks
pre-commit run --all-files

# Run tests
pytest
```

### Verify Installation
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list

# Check pre-commit
pre-commit --version
```

---

## Configuration File Dependencies

**Dependency Chain:**
```
setup.py
  └─ Defines package metadata
     └─ Used by: pip, build tools

pyproject.toml
  └─ Configures: Black, isort, MyPy, Pylint
     └─ Referenced by: .pre-commit-config.yaml

requirements.txt
  └─ Lists production dependencies
     └─ Referenced by: setup.py, Docker, CI/CD

pytest.ini
  └─ Configures test execution
     └─ Used by: pytest, coverage tools

.pre-commit-config.yaml
  └─ Defines pre-commit hooks
     └─ Runs: Black, Flake8, isort, MyPy
        └─ Configured by: pyproject.toml, .flake8, .pylintrc
```

---

## Quick Reference Table

| File | Purpose | Edit Frequency | Tool |
|------|---------|----------------|------|
| `setup.py` | Package metadata | Rare | pip, setuptools |
| `pyproject.toml` | Multi-tool config | Rare | Black, isort, MyPy |
| `requirements.txt` | Dependencies | Often | pip |
| `requirements-dev.txt` | Dev dependencies | Sometimes | pip |
| `.gitignore` | Exclude files | Sometimes | Git |
| `pytest.ini` | Test config | Rare | pytest |
| `.flake8` | Linting rules | Rare | flake8 |
| `.pylintrc` | Analysis rules | Rare | pylint |
| `.pre-commit-config.yaml` | Git hooks | Sometimes | pre-commit |
| `.env.example` | Env template | Sometimes | Documentation |

---

## Troubleshooting

### Pre-commit Hooks Failing
1. Run manually: `pre-commit run --all-files`
2. Check specific hook output
3. Fix issues or update configuration
4. Re-run hooks

### Dependency Conflicts
1. Check `requirements.txt` for version constraints
2. Update with: `pip install --upgrade package-name`
3. Test thoroughly after updates
4. Update `requirements.txt`

### Configuration Conflicts
1. Ensure Black and Flake8 agree on line length
2. Check isort profile is "black"
3. Verify MyPy ignores match actual issues
4. Test with: `pre-commit run --all-files`

---

## Configuration Change Checklist

When modifying configurations:

- [ ] Update relevant configuration file(s)
- [ ] Test with pre-commit hooks
- [ ] Run full test suite
- [ ] Update documentation if needed
- [ ] Commit with descriptive message
- [ ] Update WORK_LOG.md

---

**End of Configuration Reference**
**Keep this file updated when adding new configuration!**
