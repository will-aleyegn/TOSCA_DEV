# Configuration Files Reference

**Purpose:** Complete guide to all configuration files in the TOSCA project

**Last Updated:** 2025-10-23

---

## Configuration File Organization

### Root Directory (Required Location)

These files MUST stay in root directory due to tool requirements:

#### Python Package Configuration
- **`setup.py`** - Package metadata and installation config
- **`pyproject.toml`** - Modern Python project configuration (PEP 518)
- **`requirements.txt`** - All project dependencies

#### Version Control
- **`.gitignore`** - Files to exclude from Git
- **`.git/`** - Git repository data (hidden)

#### Linting & Formatting (Root Required)
- **`.flake8`** - Flake8 linting rules
- **`.pylintrc`** - Pylint configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks

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
**Purpose:** All project dependencies
**Location:** Root (required)
**Used By:** pip install -r requirements.txt

**Structure:**
```
# Category comments for organization
PyQt6>=6.6.0
opencv-python>=4.8.0
vmbpy>=1.1.1
# ... more packages
```

**When to Edit:**
- Adding new dependencies (ALWAYS)
- Updating package versions
- Removing unused packages

**Important:** Keep categorized with comments for clarity

---

### 4. .gitignore
**Purpose:** Exclude files from version control
**Location:** Root (required)
**Used By:** Git

**Critical Sections:**
```
# Python
__pycache__/
*.pyc
venv/

# Data and Logs - DO NOT COMMIT
data/
*.db
*.log

# Development Session Files (Local Only)
presubmit/

# Secrets
.env
*.key
```

**When to Edit:**
- Adding new output directories
- Excluding new file types
- Protecting sensitive data

**Important Notes:**
- Never commit data files or logs
- `presubmit/` folder contains local development documentation
- Always protect secrets and sensitive configuration

---

### 5. .flake8
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

### 6. .pylintrc
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

### 7. .pre-commit-config.yaml
**Purpose:** Automated code quality checks
**Location:** Root (required)
**Used By:** pre-commit hooks

**Hooks Configured:**
- presubmit-reminder (documentation reminder - displays before every commit)
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

**Note:** The `presubmit-reminder` hook displays a reminder to update documentation
in the `presubmit/` folder before each commit. This hook always passes and never
blocks commits. See `.pre-commit-hooks/show-presubmit-reminder.py` for details.

---

## Configuration Best Practices

### 1. Version Control
- ✓ Commit all configuration files (except gitignored items)
- ✗ Never commit data files, logs, or session documentation
- ✓ `presubmit/` folder stays local (gitignored)
- ✓ Document all configuration changes

### 2. Consistency
- Use consistent line length (100) across all tools
- Keep formatting rules aligned (Black + Flake8 + Pylint)
- Document why rules are disabled

### 3. Security
- Never commit data files or logs
- Keep `.gitignore` strict for sensitive data
- Review `.gitignore` before adding new data types
- `presubmit/` folder contains session documentation (gitignored)

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
  └─ Lists all project dependencies
     └─ Referenced by: setup.py

.pre-commit-config.yaml
  └─ Defines pre-commit hooks
     └─ Runs: Presubmit reminder, Black, Flake8, isort, MyPy
        └─ Configured by: pyproject.toml, .flake8, .pylintrc
        └─ Reminder reads: presubmit/REMINDER.txt (gitignored)
```

---

## Quick Reference Table

| File | Purpose | Edit Frequency | Tool |
|------|---------|----------------|------|
| `setup.py` | Package metadata | Rare | pip, setuptools |
| `pyproject.toml` | Multi-tool config | Rare | Black, isort, MyPy |
| `requirements.txt` | All dependencies | Often | pip |
| `.gitignore` | Exclude files | Sometimes | Git |
| `.flake8` | Linting rules | Rare | flake8 |
| `.pylintrc` | Analysis rules | Rare | pylint |
| `.pre-commit-config.yaml` | Git hooks & reminders | Sometimes | pre-commit |

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
- [ ] Run tests if applicable
- [ ] Update documentation if needed
- [ ] Commit with descriptive message
- [ ] Update session documentation in `presubmit/` folder (reminder will prompt)

---

**End of Configuration Reference**
**Keep this file updated when adding new configuration!**
