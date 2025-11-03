#!/usr/bin/env python3
"""Pre-commit hook: Detect hardcoded secrets and credentials."""
import re
import sys
from pathlib import Path
from typing import List, Tuple

PRODUCTION_PATHS = ["src/", "tests/", "components/", "firmware/", "config/"]
EXCLUDED_PATHS = ["tests/test_", ".example"]  # Test files and examples OK

# Secret patterns
SECRET_PATTERNS = [
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
    (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
    (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret"),
    (r"token\s*=\s*['\"][^'\"]+['\"]", "Hardcoded token"),
    (r"['\"][A-Za-z0-9]{32,}['\"]", "Potential API key (32+ chars)"),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private key"),
    (r"mongodb://[^'\"\s]+:[^'\"\s]+@", "MongoDB connection string with creds"),
    (r"mysql://[^'\"\s]+:[^'\"\s]+@", "MySQL connection string with creds"),
]


def should_check_file(filepath: str) -> bool:
    path_str = filepath.replace("\\", "/")
    for excluded in EXCLUDED_PATHS:
        if excluded in path_str:
            return False
    for production_path in PRODUCTION_PATHS:
        if path_str.startswith(production_path):
            return True
    return False


def find_secrets(filepath: str) -> List[Tuple[int, str, str]]:
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern, description in SECRET_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip(), description))
    except Exception:
        pass
    return violations


def main(filenames: List[str]) -> int:
    violations_found = False
    for filename in filenames:
        filepath = filename.replace("\\", "/")
        if not should_check_file(filepath):
            continue
        violations = find_secrets(filename)
        if violations:
            violations_found = True
            print(f"\n[X] Potential secret detected in: {filepath}")
            print("=" * 70)
            for line_num, line, pattern in violations:
                clean_line = line.encode("ascii", "replace").decode("ascii")
                print(f"  Line {line_num}: {clean_line[:60]}...")
                print(f"  Issue: {pattern}")
            print()

    if violations_found:
        print("=" * 70)
        print("[!] COMMIT BLOCKED: Potential secrets found")
        print()
        print("Actions:")
        print("  1. Remove hardcoded secrets from code")
        print("  2. Use environment variables or config files")
        print("  3. Add config files to .gitignore")
        print("=" * 70)
        return 1
    return 0


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
