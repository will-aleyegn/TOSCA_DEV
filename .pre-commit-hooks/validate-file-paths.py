#!/usr/bin/env python3
"""
Pre-commit hook: Validate file paths against medical device repository whitelist.

Medical device repositories should only contain approved file types and paths
for regulatory compliance and audit trail clarity.

Usage:
    Called automatically by pre-commit framework
    Exits with code 1 if unapproved files found (blocks commit)
    Exits with code 0 if all files approved (allows commit)

Bypass (use with justification only):
    git commit --no-verify -m "message"
"""
import re
import sys
from typing import List

# Approved file patterns (production and development)
APPROVED_PATTERNS = [
    # Source code
    r"^src/.*\.py$",
    r"^src/.*\.pyi$",  # Type stubs
    # Components (hardware modules)
    r"^components/.*\.py$",
    r"^components/.*/manufacturer_docs/.*",  # Vendor documentation
    r"^components/.*/examples/.*\.py$",
    # Firmware
    r"^firmware/.*\.ino$",  # Arduino
    r"^firmware/.*\.c$",
    r"^firmware/.*\.h$",
    r"^firmware/.*\.cpp$",
    # Tests
    r"^tests/.*\.py$",
    r"^tests/mocks/.*\.py$",
    r"^tests/.*/README\.md$",
    # Documentation
    r"^docs/.*\.md$",
    r"^README\.md$",
    r"^LESSONS_LEARNED\.md$",
    r"^LICENSE$",
    r"^CONTRIBUTING\.md$",
    # Configuration files
    r"^pyproject\.toml$",
    r"^requirements.*\.txt$",
    r"^setup\.py$",
    r"^setup\.cfg$",
    r"^\.python-version$",
    r"^config\.yaml$",
    r"^config\.example\.yaml$",
    # Git files
    r"^\.gitignore$",
    r"^\.gitattributes$",
    # Pre-commit hooks
    r"^\.pre-commit-config\.yaml$",
    r"^\.pre-commit-hooks/.*\.py$",
    # Scripts (utilities)
    r"^scripts/.*\.py$",
    r"^scripts/.*\.sh$",
    # Data directories (structure only, not data)
    r"^data/\.gitkeep$",
    r"^data/logs/\.gitkeep$",
    # Audit reports
    r"^audit_reports/.*\.md$",
    r"^audit_reports/\.gitkeep$",
    r"^\.vulture_whitelist\.py$",
    # GitHub workflows (if CI/CD added)
    r"^\.github/workflows/.*\.ya?ml$",
    # IDE settings (minimal, project-wide only)
    r"^\.vscode/settings\.json$",
    r"^\.vscode/launch\.json$",
]

# Explicitly forbidden patterns (should never be committed)
FORBIDDEN_PATTERNS = [
    # Credentials and secrets
    (r".*\.env$", "Environment files with secrets"),
    (r".*\.key$", "Cryptographic keys"),
    (r".*\.pem$", "Certificate files"),
    (r".*credentials.*\.json$", "Credential files"),
    (r".*secret.*", "Secret files"),
    (r".*password.*", "Password files"),
    # Binary/compiled files
    (r".*\.pyc$", "Python compiled files"),
    (r".*\.pyo$", "Python optimized files"),
    (r".*__pycache__/.*", "Python cache"),
    (r".*\.so$", "Shared object files"),
    (r".*\.dll$", "Windows DLL files"),
    (r".*\.exe$", "Executable files"),
    # IDE/editor files
    (r".*\.swp$", "Vim swap files"),
    (r".*\.swo$", "Vim swap files"),
    (r".*~$", "Backup files"),
    (r".*\.DS_Store$", "macOS metadata"),
    (r".*Thumbs\.db$", "Windows metadata"),
    # Build artifacts
    (r"^build/.*", "Build directory"),
    (r"^dist/.*", "Distribution directory"),
    (r".*\.egg-info/.*", "Python egg info"),
    # Logs and temporary files
    (r".*\.log$", "Log files"),
    (r".*\.tmp$", "Temporary files"),
    (r".*\.temp$", "Temporary files"),
    # AI tool configurations
    (r"^\.claude/.*", "Claude Code configuration"),
    (r"^\.gemini/.*", "Gemini configuration"),
    (r"^\.taskmaster/.*", "Task Master configuration"),
    (r"^\.cursor/.*", "Cursor configuration"),
    (r"^\.mcp\.json$", "MCP configuration"),
    (r"^CLAUDE\.md$", "Claude context file"),
    (r"^presubmit/.*", "Presubmit planning files"),
    # Virtual environments
    (r"^venv/.*", "Virtual environment"),
    (r"^\.venv/.*", "Virtual environment"),
    (r"^env/.*", "Virtual environment"),
]

# Paths that require special approval (review carefully)
NEEDS_REVIEW = [
    (r"^data/tosca\.db$", "Production database - ensure no PHI"),
    (r"^data/.*\.db$", "Database files - ensure no PHI"),
    (r"^components/.*/manufacturer_docs/.*\.pdf$", "Large vendor PDFs"),
]


def check_approved(filepath: str) -> bool:
    """Check if file matches approved patterns."""
    for pattern in APPROVED_PATTERNS:
        if re.match(pattern, filepath, re.IGNORECASE):
            return True
    return False


def check_forbidden(filepath: str) -> tuple[bool, str]:
    """
    Check if file matches forbidden patterns.

    Returns:
        (is_forbidden, reason) tuple
    """
    for pattern, reason in FORBIDDEN_PATTERNS:
        if re.match(pattern, filepath, re.IGNORECASE):
            return True, reason
    return False, ""


def check_needs_review(filepath: str) -> tuple[bool, str]:
    """
    Check if file needs special review.

    Returns:
        (needs_review, reason) tuple
    """
    for pattern, reason in NEEDS_REVIEW:
        if re.match(pattern, filepath, re.IGNORECASE):
            return True, reason
    return False, ""


def main(filenames: List[str]) -> int:  # noqa: C901
    """
    Main hook entry point.

    Args:
        filenames: List of files being committed

    Returns:
        0 if all files approved, 1 if violations found
    """
    forbidden_files = []
    unapproved_files = []
    review_files = []

    for filename in filenames:
        # Convert to forward slashes for consistent matching
        filepath = filename.replace("\\", "/")

        # Check forbidden patterns first (highest priority)
        is_forbidden, reason = check_forbidden(filepath)
        if is_forbidden:
            forbidden_files.append((filepath, reason))
            continue

        # Check if needs review
        needs_review, reason = check_needs_review(filepath)
        if needs_review:
            review_files.append((filepath, reason))
            continue

        # Check approved patterns
        if not check_approved(filepath):
            unapproved_files.append(filepath)

    # Report findings
    violations_found = False

    if forbidden_files:
        violations_found = True
        print("\n[X] FORBIDDEN FILES DETECTED")
        print("=" * 70)
        print("\nThese files should NEVER be committed:")
        print()
        for filepath, reason in forbidden_files:
            print(f"  {filepath}")
            print(f"  Reason: {reason}")
            print()

    if unapproved_files:
        violations_found = True
        print("\n[X] UNAPPROVED FILE PATHS DETECTED")
        print("=" * 70)
        print("\nThese files don't match approved patterns:")
        print()
        for filepath in unapproved_files:
            print(f"  {filepath}")
        print()

    if review_files:
        print("\n[!] FILES REQUIRING REVIEW")
        print("=" * 70)
        print("\nThese files require special review before commit:")
        print()
        for filepath, reason in review_files:
            print(f"  {filepath}")
            print(f"  Reason: {reason}")
        print()
        print("If you've verified these files are appropriate, proceed.")
        print()

    if violations_found:
        print("=" * 70)
        print("[!] COMMIT BLOCKED: File validation failed")
        print()
        print("Medical device repository whitelist enforcement:")
        print()
        print("Actions:")
        print("  1. Remove forbidden files from commit")
        print("  2. Ensure files are in approved locations")
        print("  3. Update .gitignore to prevent future violations")
        print("  4. See docs/DEVELOPMENT_STANDARDS.md for file policies")
        print()
        print("If this is a legitimate new file type:")
        print("  1. Add pattern to APPROVED_PATTERNS in validate-file-paths.py")
        print("  2. Document reason in commit message")
        print()
        print("To bypass (with justification):")
        print("  git commit --no-verify -m 'message'")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    # Arguments from pre-commit are the staged files
    exit(main(sys.argv[1:]))
