# Import Path Standardization Plan

## Problem Statement

The codebase currently uses **inconsistent import styles** across different modules:
- **Widget files** use absolute imports with `src.` prefix
- **Controller files** use relative imports with `..` notation

This inconsistency creates confusion and can cause issues during refactoring.

---

## Current State Analysis

### Files Using Absolute Imports (from src.)
```python
# src/ui/widgets/laser_widget.py:23
from src.hardware.laser_controller import LaserController

# src/ui/widgets/actuator_widget.py
from src.hardware.actuator_controller import ActuatorController

# src/ui/widgets/gpio_widget.py
from src.hardware.gpio_controller import GPIOController
```

### Files Using Relative Imports (from ..)
```python
# src/hardware/laser_controller.py:99, 128, 162
from ..core.event_logger import EventType

# src/hardware/actuator_controller.py:144
from ..core.event_logger import EventType

# src/hardware/camera_controller.py:255
from ..core.event_logger import EventType
```

---

## Impact Assessment

### Development Issues
- **Confusion** - New developers unsure which style to use
- **Code Reviews** - Inconsistency flags in reviews
- **Refactoring** - Mixed styles complicate automated refactoring

### Technical Issues
- **Module Resolution** - `from src.` can fail when package not installed
- **Testing** - Different import paths may behave differently in tests
- **IDE Support** - Some IDEs struggle with mixed import styles

---

## Recommended Solution

### Adopt Relative Imports Throughout

**Rationale:**
1. **PEP 8 Recommendation** - Relative imports preferred for intra-package references
2. **Package Independence** - Works regardless of package installation
3. **Refactoring Safety** - Easier to move modules within package
4. **Consistency** - One clear pattern to follow

### Standard Import Pattern

```python
# ✅ CORRECT - Relative imports for intra-package
from ..hardware.laser_controller import LaserController
from ..core.event_logger import EventType, EventSeverity
from ..database.db_manager import DatabaseManager

# ✅ CORRECT - Absolute imports for external packages
from PyQt6.QtCore import QObject, pyqtSignal
import logging
from typing import Optional, Any

# ❌ AVOID - Absolute imports with src. prefix
from src.hardware.laser_controller import LaserController
from src.core.event_logger import EventType
```

---

## Implementation Plan

### Phase 1: Automated Conversion (1 day)
Run automated script to convert all `from src.` imports to relative imports.

**Script:**
```python
# tools/fix_imports.py
import re
from pathlib import Path

def convert_to_relative_import(file_path: Path, src_root: Path):
    """Convert absolute src. imports to relative imports."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Calculate relative depth from src root
    depth = len(file_path.relative_to(src_root).parents) - 1
    parent_prefix = '..' * depth if depth > 0 else '.'

    # Replace src. imports with relative imports
    pattern = r'from src\.(\w+)'
    replacement = f'from {parent_prefix}.\\1'
    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Run for all Python files
src_root = Path('src')
for py_file in src_root.rglob('*.py'):
    if convert_to_relative_import(py_file, src_root):
        print(f"Converted: {py_file}")
```

### Phase 2: Manual Review (1 day)
1. Review all automated changes
2. Fix any edge cases
3. Ensure imports resolve correctly

### Phase 3: Testing (1 day)
1. Run full test suite
2. Manually test all UI widgets
3. Verify all controllers connect properly

### Phase 4: Documentation Update (0.5 days)
Update developer guidelines with import standards.

---

## Import Style Guide

### Rule 1: Use Relative Imports for Intra-Package References
```python
# Within src/ package
from ..core.protocol import Protocol
from ..hardware.laser_controller import LaserController
from .widgets import ActuatorWidget  # Same-level package
```

### Rule 2: Use Absolute Imports for External Packages
```python
# External packages
from PyQt6.QtWidgets import QMainWindow
import numpy as np
from pathlib import Path
```

### Rule 3: Organize Imports by Category
```python
# 1. Standard library
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

# 2. Third-party packages
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

# 3. Local package (relative imports)
from ..core.protocol import Protocol
from ..hardware.laser_controller import LaserController
from .actuator_widget import ActuatorWidget
```

### Rule 4: Avoid Circular Imports
```python
# Use TYPE_CHECKING to avoid runtime circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..hardware.gpio_controller import GPIOController

class LaserWidget(QWidget):
    def set_gpio_controller(self, controller: "GPIOController") -> None:
        self.gpio_controller = controller
```

---

## Files Requiring Changes

### UI Widgets (3 files)
- `src/ui/widgets/laser_widget.py`
- `src/ui/widgets/actuator_widget.py`
- `src/ui/widgets/gpio_widget.py`

### Expected Changes
```diff
# laser_widget.py
- from src.hardware.laser_controller import LaserController
+ from ...hardware.laser_controller import LaserController

# TYPE_CHECKING imports
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
-     from src.hardware.gpio_controller import GPIOController
+     from ...hardware.gpio_controller import GPIOController
```

---

## Validation Checklist

- [ ] All `from src.` imports converted to relative imports
- [ ] No import errors when running application
- [ ] All tests pass
- [ ] Pre-commit hooks updated to enforce style
- [ ] Developer documentation updated
- [ ] Team trained on new standard

---

## Pre-commit Hook Configuration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-imports
        name: Check import style
        entry: python tools/check_imports.py
        language: system
        types: [python]
```

Create `tools/check_imports.py`:
```python
#!/usr/bin/env python3
"""Check for absolute src. imports."""
import re
import sys
from pathlib import Path

def check_file(file_path: Path) -> list[str]:
    """Check for src. imports in file."""
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if re.match(r'from src\.', line):
                errors.append(f"{file_path}:{line_num}: Use relative import instead of 'from src.'")
    return errors

if __name__ == "__main__":
    errors = []
    for file_path in sys.argv[1:]:
        errors.extend(check_file(Path(file_path)))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
```

---

## Timeline

| Phase | Duration | Owner |
|-------|----------|-------|
| Automated conversion | 1 day | Developer |
| Manual review | 1 day | Developer + Code Reviewer |
| Testing | 1 day | QA Team |
| Documentation | 0.5 days | Tech Writer |
| **Total** | **3.5 days** | |

---

## Success Criteria

1. ✅ Zero `from src.` imports in codebase
2. ✅ All imports use relative notation
3. ✅ Application runs without import errors
4. ✅ All tests pass
5. ✅ Pre-commit hook prevents regressions
6. ✅ Team understands and follows new standard

---

**Status:** 📋 Ready for Implementation
**Priority:** 🟠 HIGH (Medium-High)
**Effort:** 3.5 days
**Risk:** Low (automated with manual review)
