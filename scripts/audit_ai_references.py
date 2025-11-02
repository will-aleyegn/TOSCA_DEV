#!/usr/bin/env python3
"""
Quarterly Audit Script: AI Reference Detection

Comprehensive audit of git-tracked files for AI tool references.
Run quarterly to ensure pre-commit hooks are functioning and no
references have bypassed automated checks.

Usage:
    python scripts/audit_ai_references.py [--output report.md]

Output:
    - Console report with violations (if any)
    - Optional markdown report file
    - Exit code 0 if no violations, 1 if violations found

Author: TOSCA Development Team
Last Updated: 2025-11-02
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# AI tool patterns (same as pre-commit hook)
AI_PATTERNS = [
    (r"\bClaude\b(?!.*Code)", "Claude (not Code)"),
    (r"\bAnthropic\b", "Anthropic"),
    (r"\bTask Master\b", "Task Master"),
    (r"\btask-master\b", "task-master"),
    (r"\bGemini\b(?!.*SDK)", "Gemini (not SDK)"),
    (r"\bZen MCP\b", "Zen MCP"),
    (r"\bzen-powered\b", "zen-powered"),
    (r"\bAI Code Review\b", "AI Code Review"),
    (r"\bAI assistant\b", "AI assistant"),
    (r"\bAI-powered\b", "AI-powered"),
    (r"\bAI-assisted\b", "AI-assisted"),
    (r"\bChatGPT\b", "ChatGPT"),
    (r"\bGPT-\d+\b", "GPT-X"),
    (r"\bOpenAI\b", "OpenAI"),
]

# Paths to check (production code and documentation)
PRODUCTION_PATHS = ["src/", "docs/", "components/", "firmware/", "README.md", "LESSONS_LEARNED.md"]

# Paths to exclude (development/testing contexts)
EXCLUDED_PATHS = [
    "tests/",
    "scripts/",
    "archive/",
    ".git/",
    ".pre-commit-hooks/",
    ".taskmaster/",
    ".claude/",
    ".cursor/",
    ".gemini/",
]

# Whitelisted phrases (legitimate uses)
WHITELIST_PATTERNS = [
    r"main\s+function",
    r"HIPAA[\-\s]compliant",
    r"Gemini\s+protocol",
    r"Do not use.*(?:Claude|ChatGPT|AI)",
    r"CONTRIBUTING\.md",
    r"DEVELOPMENT_STANDARDS\.md",  # This file documents the policy
]


def get_git_tracked_files() -> List[str]:
    """Get all files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error getting git files: {e}")
        sys.exit(1)


def should_check_file(filepath: str) -> bool:
    """Check if file should be scanned for AI references."""
    path = Path(filepath)
    # Convert to forward slashes for consistent comparison (Windows/Unix)
    path_str = str(path).replace("\\", "/")

    # Exclude development/test paths
    for excluded in EXCLUDED_PATHS:
        if path_str.startswith(excluded) or excluded in path_str:
            return False

    # Check production paths
    for production_path in PRODUCTION_PATHS:
        if path_str.startswith(production_path):
            return True
        # Check root markdown files
        if path.suffix == ".md" and len(path.parts) == 1:
            return True

    return False


def is_whitelisted(line: str) -> bool:
    """Check if line contains whitelisted AI references."""
    for pattern in WHITELIST_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def scan_file(filepath: str) -> List[Tuple[int, str, str]]:
    """
    Scan file for AI references.

    Returns:
        List of (line_number, line_content, pattern_name) tuples
    """
    violations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for line_num, line in enumerate(content.splitlines(), 1):
            # Skip whitelisted lines
            if is_whitelisted(line):
                continue

            # Check each AI pattern
            for pattern, pattern_name in AI_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append((line_num, line.strip(), pattern_name))
                    break  # Only report first match per line

    except Exception:
        # Skip binary files or files we can't read
        pass

    return violations


def check_documentation_age() -> List[Tuple[str, int]]:
    """
    Check for documentation files that haven't been updated in >6 months.

    Returns:
        List of (filepath, days_old) tuples
    """
    old_docs = []
    six_months_days = 180

    try:
        result = subprocess.run(
            ["git", "ls-files", "docs/"],
            capture_output=True,
            text=True,
            check=True,
        )
        doc_files = result.stdout.strip().split("\n")

        for doc_file in doc_files:
            if not doc_file.endswith(".md"):
                continue

            # Get last modification date from git
            result = subprocess.run(
                ["git", "log", "-1", "--format=%at", doc_file],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                timestamp = int(result.stdout.strip())
                days_old = (datetime.now().timestamp() - timestamp) / (60 * 60 * 24)

                if days_old > six_months_days:
                    old_docs.append((doc_file, int(days_old)))

    except subprocess.CalledProcessError:
        pass

    return old_docs


def generate_console_report(
    violations: Dict[str, List[Tuple[int, str, str]]],
    old_docs: List[Tuple[str, int]],
    files_scanned: int,
) -> None:
    """Print audit report to console."""
    print("=" * 80)
    print("TOSCA QUARTERLY AUDIT REPORT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    print(f"Files Scanned: {files_scanned}")
    print(f"Violations Found: {sum(len(v) for v in violations.values())}")
    print(f"Outdated Documentation: {len(old_docs)} files")
    print()

    if violations:
        print("[!] AI REFERENCE VIOLATIONS DETECTED")
        print("=" * 80)
        for filepath, file_violations in violations.items():
            print(f"\nFile: {filepath}")
            print("-" * 80)
            for line_num, line, pattern_name in file_violations:
                print(f"  Line {line_num} [{pattern_name}]: {line[:70]}...")
        print()
        print("REMEDIATION REQUIRED:")
        print("  1. Remove AI references from files listed above")
        print("  2. Update pre-commit hook if patterns were missed")
        print("  3. Document findings in audit report")
        print()
    else:
        print("[OK] No AI reference violations found")
        print()

    if old_docs:
        print("[WARNING] OUTDATED DOCUMENTATION")
        print("=" * 80)
        print("The following documentation hasn't been updated in >6 months:")
        print()
        for doc_file, days_old in sorted(old_docs, key=lambda x: x[1], reverse=True):
            print(f"  {doc_file}: {days_old} days old")
        print()
        print("RECOMMENDATIONS:")
        print("  1. Review each file for accuracy")
        print("  2. Update or archive as appropriate")
        print("  3. Consider if architectural changes require updates")
        print()

    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


def generate_markdown_report(
    violations: Dict[str, List[Tuple[int, str, str]]],
    old_docs: List[Tuple[str, int]],
    files_scanned: int,
    output_file: str,
) -> None:
    """Generate markdown audit report."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# TOSCA Quarterly Audit Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Quarter:** Q{(datetime.now().month - 1) // 3 + 1} {datetime.now().year}\n")
        f.write("**Auditor:** [Your Name]\n\n")
        f.write("---\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"- **Files Scanned:** {files_scanned}\n")
        f.write(f"- **AI Reference Violations:** {sum(len(v) for v in violations.values())}\n")
        f.write(f"- **Outdated Documentation:** {len(old_docs)} files (>6 months)\n")
        f.write(f"- **Overall Status:** {'PASS' if not violations else 'FAIL'}\n\n")

        if violations:
            f.write("## AI Reference Violations\n\n")
            f.write("**Status:** ❌ VIOLATIONS FOUND\n\n")
            for filepath, file_violations in violations.items():
                f.write(f"### {filepath}\n\n")
                f.write("| Line | Pattern | Content |\n")
                f.write("|------|---------|----------|\n")
                for line_num, line, pattern_name in file_violations:
                    # Escape pipe characters in content
                    safe_line = line[:60].replace("|", "\\|")
                    f.write(f"| {line_num} | {pattern_name} | `{safe_line}...` |\n")
                f.write("\n")

            f.write("**Required Actions:**\n")
            f.write("1. Remove all AI references from files listed above\n")
            f.write("2. Investigate how these bypassed pre-commit hooks\n")
            f.write("3. Update hook patterns if systematic gap identified\n")
            f.write("4. Re-run audit after remediation\n\n")
        else:
            f.write("## AI Reference Violations\n\n")
            f.write("**Status:** ✅ NO VIOLATIONS\n\n")
            f.write("Pre-commit hooks are functioning correctly. No AI tool references ")
            f.write("found in production code or documentation.\n\n")

        if old_docs:
            f.write("## Outdated Documentation\n\n")
            f.write("The following documentation files haven't been updated in >6 months:\n\n")
            f.write("| File | Age (days) | Action |\n")
            f.write("|------|------------|--------|\n")
            for doc_file, days_old in sorted(old_docs, key=lambda x: x[1], reverse=True):
                f.write(f"| {doc_file} | {days_old} | [Review/Update/Archive] |\n")
            f.write("\n")
            f.write("**Recommendations:**\n")
            f.write("- Review each file for technical accuracy\n")
            f.write("- Update with recent changes or archive if superseded\n")
            f.write("- Ensure architectural documentation reflects current state\n\n")

        f.write("## Pre-commit Hook Status\n\n")
        f.write("- **Last Hook Update:** [Check git log for .pre-commit-hooks/]\n")
        f.write(f"- **Patterns Detected:** {len(AI_PATTERNS)}\n")
        f.write(f"- **Production Paths:** {', '.join(PRODUCTION_PATHS)}\n")
        f.write(f"- **Excluded Paths:** {', '.join(EXCLUDED_PATHS)}\n\n")

        f.write("## Recommendations\n\n")
        if not violations and not old_docs:
            f.write("- Continue current practices\n")
            f.write("- No action required\n")
        else:
            if violations:
                f.write("- **HIGH PRIORITY:** Remediate AI reference violations\n")
            if old_docs:
                f.write("- **MEDIUM PRIORITY:** Review and update outdated documentation\n")
        f.write("- Schedule next quarterly audit for [Date + 3 months]\n\n")

        f.write("## Sign-Off\n\n")
        f.write("**Auditor Signature:** _________________________\n\n")
        f.write("**Date:** _________________________\n\n")
        f.write("**Notes:**\n\n")
        f.write("---\n\n")
        f.write("*This report generated by scripts/audit_ai_references.py*\n")

    print(f"\n[OK] Markdown report written to: {output_file}")


def main() -> None:
    """Main audit entry point."""
    parser = argparse.ArgumentParser(
        description="Quarterly audit for AI tool references in TOSCA codebase"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output markdown report to file",
        default=None,
    )
    args = parser.parse_args()

    # Get all git-tracked files
    all_files = get_git_tracked_files()

    # Filter to production files
    files_to_check = [f for f in all_files if should_check_file(f)]

    # Scan each file
    violations: Dict[str, List[Tuple[int, str, str]]] = {}
    for filepath in files_to_check:
        file_violations = scan_file(filepath)
        if file_violations:
            violations[filepath] = file_violations

    # Check documentation age
    old_docs = check_documentation_age()

    # Generate console report
    generate_console_report(violations, old_docs, len(files_to_check))

    # Generate markdown report if requested
    if args.output:
        generate_markdown_report(violations, old_docs, len(files_to_check), args.output)

    # Exit with appropriate code
    if violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
