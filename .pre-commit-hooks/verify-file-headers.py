#!/usr/bin/env python3
"""Pre-commit hook: Verify file headers on TOSCA Python files."""
import re
import sys
from pathlib import Path
from typing import List

PRODUCTION_PATHS = ["src/", "firmware/"]  # Require headers in TOSCA code only
EXCLUDED_PATHS = ["tests/", "examples/", "components/"]  # Not required

# Required header elements
REQUIRED_PATTERNS = [
    (r'"""[\s\S]*?"""', "Module docstring"),
    (r"Project:\s*TOSCA", "Project identifier"),
]


def should_check_file(filepath: str) -> bool:
    path_str = filepath.replace("\\", "/")
    if not path_str.endswith(".py"):
        return False
    for excluded in EXCLUDED_PATHS:
        if path_str.startswith(excluded):
            return False
    for production_path in PRODUCTION_PATHS:
        if path_str.startswith(production_path):
            return True
    return False


def verify_header(filepath: str) -> List[str]:
    """Return list of missing header elements."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(500)  # Check first 500 chars
    except Exception:
        return []

    missing = []
    for pattern, description in REQUIRED_PATTERNS:
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(description)
    return missing


def main(filenames: List[str]) -> int:
    violations_found = False
    for filename in filenames:
        filepath = filename.replace("\\", "/")
        if not should_check_file(filepath):
            continue
        missing = verify_header(filename)
        if missing:
            violations_found = True
            print(f"\n[X] Missing header elements in: {filepath}")
            for element in missing:
                print(f"  - {element}")

    if violations_found:
        print("\n" + "=" * 70)
        print("[!] COMMIT BLOCKED: File headers incomplete")
        print()
        print("Required header format for src/ files:")
        print('"""')
        print("Module: [name]")
        print("Project: TOSCA Laser Control System")
        print()
        print("Purpose: [Brief description]")
        print("Safety Critical: [Yes/No]")
        print('"""')
        print("=" * 70)
        return 1
    return 0


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
