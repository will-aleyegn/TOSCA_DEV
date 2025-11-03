#!/usr/bin/env python3
"""
Pre-commit hook: Detect informal TODO comments and unprofessional language.

Medical device code requires professional, traceable task management.
TODOs must reference tracked issues (e.g., TODO(#123): description).

Usage:
    Called automatically by pre-commit framework
    Exits with code 1 if violations found (blocks commit)
    Exits with code 0 if all comments are professional (allows commit)
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Paths to check (production TOSCA code only)
PRODUCTION_PATHS = ["src/", "tests/", "firmware/"]

# Exclude vendor/third-party code
EXCLUDED_PATHS = [
    "components/",  # Vendor hardware libraries
    "tests/mocks/",  # Mock test infrastructure (development)
    "examples/",  # Example code
]

# TODO comment patterns (must have issue number)
TODO_PATTERNS = [
    (r"#\s*(TODO|FIXME|HACK|XXX|TEMP|WIP)(?!\(#\d+\))", "TODO without issue number"),
    (r"//\s*(TODO|FIXME|HACK|XXX|TEMP|WIP)(?!\(#\d+\))", "TODO without issue number"),
]

# Informal language patterns (slang, casual speech)
INFORMAL_PATTERNS = [
    (r"\b(gonna|wanna|gotta|kinda|sorta)\b", "Slang term"),
    (r"\b(oops|yikes|ugh|doh|meh|nah|yeah)\b", "Informal expression"),
    (r"\b(wtf|omg|lol|lmao|rofl)\b", "Internet slang"),
    (r"\b(shit|damn|crap|fuck)\b", "Profanity"),
    (r"\b(stupid|dumb|idiotic|moronic)\b", "Unprofessional adjective"),
    (r"\b(broken|busted|borked|janky|hacky)\b", "Informal status"),
]


def should_check_file(filepath: str) -> bool:
    """Check if file should be scanned for informal comments."""
    path = Path(filepath)
    path_str = str(path).replace("\\", "/")

    # Exclude vendor/third-party code
    for excluded in EXCLUDED_PATHS:
        if path_str.startswith(excluded) or excluded in path_str:
            return False

    # Check production paths
    for production_path in PRODUCTION_PATHS:
        if path_str.startswith(production_path):
            return True

    return False


def find_informal_comments(
    filepath: str,
) -> List[Tuple[int, str, str]]:
    """
    Find informal TODO comments and unprofessional language.

    Returns:
        List of (line_number, line_text, pattern_description) tuples
    """
    violations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                # Check TODO patterns
                for pattern, description in TODO_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip(), description))

                # Check informal language patterns (case-insensitive)
                for pattern, description in INFORMAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip(), description))

    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    return violations


def main(filenames: List[str]) -> int:
    """
    Main hook entry point.

    Args:
        filenames: List of files being committed

    Returns:
        0 if all comments are professional, 1 if violations found
    """
    violations_found = False

    for filename in filenames:
        # Convert to forward slashes for consistent matching (Windows/Unix)
        filepath = filename.replace("\\", "/")

        if not should_check_file(filepath):
            continue

        violations = find_informal_comments(filename)

        if violations:
            violations_found = True
            print(f"\n[X] Informal comments detected in: {filepath}")
            print("=" * 70)

            for line_num, line, pattern in violations:
                # Replace non-ASCII chars to prevent Windows encoding errors
                clean_line = line.encode("ascii", "replace").decode("ascii")
                print(f"  Line {line_num}: {clean_line[:80]}...")
                print(f"  Issue: {pattern}")

            print()

    if violations_found:
        print("=" * 70)
        print("[!] COMMIT BLOCKED: Informal comments or language found")
        print()
        print("Medical device code requires professional, traceable comments:")
        print()
        print("TODO Comments:")
        print("  BAD:  # TODO: Fix this later")
        print("  GOOD: # TODO(#127): Implement database persistence")
        print()
        print("Informal Language:")
        print("  BAD:  # This is gonna break")
        print("  GOOD: # This will require refactoring")
        print()
        print("Actions:")
        print("  1. Replace TODO with TODO(#issue_number)")
        print("  2. Create GitHub issue if needed")
        print("  3. Use professional language (avoid slang, profanity)")
        print("  4. See docs/DEVELOPMENT_STANDARDS.md for policy")
        print()
        print("To bypass (with justification):")
        print('  git commit --no-verify -m "message"')
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    # Arguments from pre-commit are the staged files
    exit(main(sys.argv[1:]))
