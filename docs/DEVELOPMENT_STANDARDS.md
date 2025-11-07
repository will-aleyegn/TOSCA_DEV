# TOSCA Development Standards

**Last Updated:** 2025-11-02
**Version:** v0.9.12-alpha
**Purpose:** Development guidelines and policies for TOSCA medical device software

---

## Table of Contents

1. [AI Tool Reference Policy](#ai-tool-reference-policy)
2. [Code Review Attribution](#code-review-attribution)
3. [Documentation Standards](#documentation-standards)
4. [Git Commit Guidelines](#git-commit-guidelines)
5. [Professional Comment Standards](#professional-comment-standards)
6. [Professional Language Standards](#professional-language-standards)
7. [File Header Requirements](#file-header-requirements)
8. [Security Standards](#security-standards)
9. [Pre-commit Hook System](#pre-commit-hook-system)
10. [Quarterly Audit Process](#quarterly-audit-process)

---

## AI Tool Reference Policy

### Rationale

TOSCA is FDA-regulated medical device software under development. While AI-powered development tools (Claude Code, Task Master, GitHub Copilot, etc.) are valuable during development, their references must not appear in production code or documentation submitted for regulatory review.

**Regulatory Requirements:**
- FDA 21 CFR Part 11 requires accurate attribution and audit trails
- IEC 62304 mandates professional documentation practices
- Documentation must reflect human accountability and oversight

### Policy Statement

**All code, documentation, and comments committed to the git repository MUST NOT contain references to:**
- AI assistants or chatbots (Claude, ChatGPT, Gemini, etc.)
- AI development tools (Claude Code, Task Master, Zen MCP, etc.)
- AI-powered or AI-assisted attributions

**Exceptions:**
1. Development tool configuration files (`.claude/`, `.taskmaster/`, `.cursor/`, etc.) - excluded from git tracking
2. Internal development scripts in `scripts/` directory (not part of deliverable)
3. Test files in `tests/` directory (documentation context only)
4. This DEVELOPMENT_STANDARDS.md document (explains the policy)

### Implementation

**Automated Enforcement:**
- Pre-commit hook (`detect-ai-references.py`) scans all production files
- Hook blocks commits containing AI tool references
- Provides clear remediation guidance

**Manual Practices:**
- Use generic terms: "Code Review" not "AI Code Review"
- Use professional attribution: "Code Review - October 2025" not "Reviewed by Claude"
- Document decisions, not tools used to make them

### Examples

❌ **INCORRECT:**
```python
# This function was written by Claude AI assistant
def calculate_dose(power, duration):
    ...
```text

✅ **CORRECT:**
```python
# Calculate laser dose based on power and duration
# Implements dose calculation per IEC 60601-2-22
def calculate_dose(power, duration):
    ...
```text

❌ **INCORRECT (Documentation):**
```markdown
## Code Review Report

**Reviewer:** AI Code Review (Gemini 2.5 Pro)
**Date:** 2025-10-27
```text

✅ **CORRECT (Documentation):**
```markdown
## Code Review Report

**Reviewer:** Code Review - October 27, 2025
**Focus:** Safety architecture validation
```text

### Bypass Procedure

If you must commit content with AI references (rare, requires justification):

```bash
git commit --no-verify -m "docs: add AI tool usage guide"
```bash

**When to bypass:**
- Documenting AI tool usage policies (this file)
- Adding development workflow documentation
- Committing configuration for AI tools (should be in excluded paths)

**Required:** Document justification in commit message.

---

## Code Review Attribution

### Professional Attribution Standards

All code reviews must use professional, auditable attribution:

**Format:**
```
**Reviewer:** Code Review - [Month Day, Year]
**Focus:** [Review scope]
**Findings:** [Key findings]
```text

**Example:**
```
**Reviewer:** Code Review - October 30, 2025
**Focus:** Safety interlock architecture
**Findings:** Selective shutdown policy correctly implemented
```text

### Review Documentation

Code reviews should document:
1. **Scope:** What was reviewed (files, components, features)
2. **Focus:** Primary review objectives (safety, security, performance)
3. **Findings:** Key observations (strengths, concerns, recommendations)
4. **Actions:** Required follow-up items

### Review Types

- **Safety Review:** Safety-critical code, interlocks, state machines
- **Security Review:** Authentication, encryption, data protection
- **Performance Review:** Real-time processing, memory usage, threading
- **Architecture Review:** Design patterns, modularity, maintainability
- **Compliance Review:** FDA/IEC requirements, documentation completeness

---

## Documentation Standards

### File Metadata

All documentation files must include:

```markdown
# Document Title

**Last Updated:** YYYY-MM-DD
**Version:** v0.9.12-alpha
**Purpose:** Brief description
```text

### Version Format

- Development: `v0.9.x-alpha`
- Pre-clinical validation: `v1.0.x-beta`
- Production: `v1.x.x`

### Date Format

- ISO 8601: `YYYY-MM-DD` (e.g., `2025-11-02`)

### Documentation Categories

1. **ETERNAL:** Core architecture, always current
   - `docs/architecture/XX_*.md`
   - Update during major architectural changes

2. **LIVING:** Regularly updated operational docs
   - `README.md`
   - `LESSONS_LEARNED.md`
   - `PROJECT_STATUS.md`

3. **TEMPORAL:** Point-in-time reports, archive when superseded
   - Code review reports
   - Completion reports
   - Planning documents

### Archival Policy

**When to Archive:**
- Planning documents after completion
- Point-in-time reports when superseded
- Feature-specific documentation after integration

**Archive Location:**
- `docs/archive/YYYY-MM-description/`

**Archival Process:**
1. Use `git mv` to preserve history (do NOT copy)
2. Update INDEX.md to reference archived location
3. Commit with descriptive message

---

## Git Commit Guidelines

### Commit Message Format

```
<type>: <subject>

[optional body]

[optional footer]
```text

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or updates
- `refactor:` Code restructuring (no functional change)
- `chore:` Maintenance tasks (dependencies, config)

**Examples:**
```
feat: implement selective shutdown for safety faults

Disable treatment laser only on safety violation.
Preserve camera, actuator, and monitoring for diagnosis.
Addresses safety architecture requirement SA-003.

fix: correct Windows path handling in pre-commit hook

Convert backslashes to forward slashes for consistent path
comparison across Windows/Unix platforms.

test: add hardware controller thread safety tests

85% pass rate (68/80 tests). Remaining failures are minor
mock configuration issues, not production code defects.
```python

### Pre-commit Validation

All commits automatically validated for:
- ✅ Trailing whitespace removal
- ✅ End-of-file newline enforcement
- ✅ YAML syntax validation
- ✅ Large file detection (>1MB)
- ✅ Merge conflict markers
- ✅ Debug statement detection
- ✅ Black code formatting (Python)
- ✅ Flake8 linting (Python)
- ✅ isort import sorting (Python)
- ✅ MyPy type checking (Python)
- ✅ **AI reference detection (custom hook)**

### Bypass Hooks (Use Sparingly)

```bash
git commit --no-verify -m "message"
```text

**Valid reasons to bypass:**
- MyPy false positives (document in commit message)
- Committing AI tool policy documentation
- Emergency hotfixes (with proper justification)

**Document bypass reason** in commit message.

---

## Pre-commit Hook System

### Hook Configuration

Location: `.pre-commit-config.yaml`

### AI Reference Detection Hook

**Purpose:** Prevent AI tool references from entering production code/docs

**Scanned Paths:**
- `src/` (all production code)
- `docs/` (all documentation)
- `components/` (hardware modules)
- `firmware/` (Arduino firmware)
- `README.md`, `LESSONS_LEARNED.md`

**Excluded Paths:**
- `tests/` (development context allowed)
- `scripts/` (internal tools)
- `.git/`, `.pre-commit-hooks/`
- `.claude/`, `.taskmaster/`, `.gemini/`, `.cursor/` (AI tool configs)

**Detected Patterns:**
- `Claude` (except "Claude Code" in comments)
- `Anthropic`
- `Task Master`, `task-master`
- `Gemini` (except "Gemini SDK" for hardware)
- `Zen MCP`, `zen-powered`
- `AI Code Review`, `AI assistant`, `AI-powered`, `AI-assisted`
- `ChatGPT`, `GPT-4`, `GPT-3.5`
- `OpenAI`

**Whitelisted Phrases:**
- `main function` (programming term)
- `HIPAA-compliant` (regulatory term)
- `Gemini protocol` (cryptocurrency reference)
- `Do not use Claude/ChatGPT/AI` (policy explanations)
- `CONTRIBUTING.md` (can document AI tool usage)

### Manual Testing

Test hook directly:

```bash
python .pre-commit-hooks/detect-ai-references.py path/to/file.py
```text

### Updating Hook

After modifying `detect-ai-references.py`:

```bash
git add .pre-commit-hooks/detect-ai-references.py
pre-commit run --all-files  # Test on all files
```text

---

## Quarterly Audit Process

### Purpose

Periodic manual review to:
1. Verify pre-commit hooks are functioning
2. Catch any AI references that bypassed hooks
3. Review documentation quality and currency
4. Ensure regulatory compliance readiness

### Audit Schedule

- **Frequency:** Quarterly (every 3 months)
- **Recommended:** End of each quarter (March, June, September, December)
- **Duration:** 1-2 hours

### Audit Procedure

**See:** `docs/QUARTERLY_AUDIT_CHECKLIST.md` for detailed steps

**Automated Audit Script:**

```bash
python scripts/audit_ai_references.py
```text

This script:
- Scans all git-tracked files for AI references
- Reports any violations (should be zero)
- Generates audit report in `audit_reports/`
- Flags outdated documentation (>6 months old)

### Remediation Process

If violations found:

1. **Immediate:** Remove AI references from affected files
2. **Investigate:** How did they bypass the hook?
3. **Fix:** Update hook patterns or whitelist if needed
4. **Document:** Record findings in audit report
5. **Commit:** Clean files with proper commit message

### Audit Report

Generate quarterly audit report:

```bash
python scripts/audit_ai_references.py --output audit_reports/YYYY-QX-audit-report.md
```text

**Report includes:**
- Files scanned count
- Violations found (with line numbers)
- Outdated documentation list
- Recommendations
- Sign-off section

**Archive:** Keep all audit reports in `audit_reports/` directory

---

## Enforcement

### Pre-commit Hooks

**Primary enforcement mechanism** - automated validation before commits.

### Code Review

**Secondary validation** - human review of all changes before merge.

### Quarterly Audits

**Tertiary validation** - periodic comprehensive review.

### CI/CD Pipeline

**Future enhancement** - automated testing on all pull requests.

---

## Questions and Support

### Hook Issues

If pre-commit hook has false positives:

1. Check if phrase is legitimately needed (e.g., "main function")
2. Add to `WHITELIST_PATTERNS` in `detect-ai-references.py`
3. Document reason in commit message
4. Update this standards doc if pattern is common

### Policy Questions

Refer to:
- This document (DEVELOPMENT_STANDARDS.md)
- `README.md` for project overview
- `CLAUDE.md` for AI tool usage during development
- FDA 21 CFR Part 11 for regulatory context

### Reporting Violations

If you discover AI references in production code:

1. **Do not bypass hook** - fix the violation
2. Create issue in GitHub if systematic problem
3. Document in `LESSONS_LEARNED.md` if valuable learning
4. Notify team if affects deliverable documentation

---

## Version History

- **v1.0 (2025-11-02):** Initial standards document
  - AI tool reference policy
  - Pre-commit hook system
  - Quarterly audit process
  - Code review attribution standards

---

**Document Status:** Active
**Next Review:** 2026-02-01 (quarterly)
**Owner:** Development Team

## Professional Comment Standards

### TODO Comment Policy

**Rationale:** Medical device code requires traceable task management. Informal TODO comments create technical debt without accountability.

**Policy:**
- All TODO comments MUST reference a tracked issue number
- Format: `TODO(#issue): description`
- Applies to: `src/`, `tests/`, `firmware/` directories
- Exceptions: Vendor code in `components/*/manufacturer_docs/`

**Examples:**

❌ **INCORRECT:**
```python
# TODO: Fix this later
# FIXME: This doesn't work right
# HACK: Temporary workaround
```text

✅ **CORRECT:**
```python
# TODO(#127): Implement database persistence for protocol execution
# TODO(#128): Add power mode support when hardware available
```text

**Enforcement:** Pre-commit hook `detect-informal-comments.py` blocks commits with untracked TODOs.

**Creating Issues:**
1. Create GitHub issue with detailed description
2. Add TODO comment with issue number
3. Link commit to issue in commit message

---

## Professional Language Standards

**Rationale:** Medical device documentation must maintain professional tone for regulatory review.

**Prohibited in Code/Comments:**
- Slang: gonna, wanna, kinda, sorta
- Informal expressions: oops, yikes, ugh, meh
- Internet slang: wtf, lol, omg
- Profanity: any profane language
- Unprofessional adjectives: stupid, dumb, idiotic
- Informal status terms: broken, busted, borked, janky

**Examples:**

❌ **INCORRECT:**
```python
# This is gonna break if we're not careful
# WTF is this code doing?
# Stupid bug that keeps happening
```text

✅ **CORRECT:**
```python
# This will fail if input validation is bypassed
# Investigate unexpected behavior in edge cases
# Persistent defect requiring root cause analysis
```text

**Enforcement:** Pre-commit hook `detect-informal-comments.py` scans for informal language patterns.

---

## File Header Requirements

**Rationale:** FDA 21 CFR Part 11 and IEC 62304 require clear attribution and purpose documentation.

**Required Elements (for src/ files):**
```python
"""
Module: [module_name]
Project: TOSCA Laser Control System

Purpose: [Brief description of module's role]
Safety Critical: [Yes/No]
"""
```text

**Optional Elements:**
- Author: (use git history for attribution)
- License: (if applicable)
- References: (standards, requirements)

**Examples:**

```python
"""
Module: safety_manager
Project: TOSCA Laser Control System

Purpose: Central safety state machine and interlock coordination.
Manages transitions between SAFE, ARMED, TREATING, UNSAFE states
and enforces hardware interlock requirements.

Safety Critical: Yes
"""
import threading
from enum import Enum
...
```bash

**Enforcement:** Pre-commit hook `verify-file-headers.py` checks src/ files for required elements.

**Migration:** Add headers to existing files during normal maintenance. Not required immediately for legacy code.

---

## Security Standards

### Hardcoded Secrets Policy

**Rationale:** Credentials in code create security vulnerabilities and compliance violations.

**Prohibited:**
- Hardcoded passwords, API keys, tokens
- Connection strings with embedded credentials
- Private keys or certificates in code
- Encryption keys in source files

**Examples:**

❌ **INCORRECT:**
```python
API_KEY = "sk_live_abcdef123456789"
password = "admin123"
db_url = "mysql://root:password123@localhost/tosca"
```text

✅ **CORRECT:**
```python
import os
API_KEY = os.environ.get("TOSCA_API_KEY")
password = os.environ.get("TOSCA_DB_PASSWORD")
db_url = config_loader.get_database_url()  # From config.yaml (in .gitignore)
```

**Configuration Management:**
1. Use environment variables for secrets
2. Store configs in `.gitignore`d files (config.yaml)
3. Provide example configs without secrets (config.example.yaml)
4. Document required environment variables in README

**Enforcement:** Pre-commit hook `detect-secrets.py` scans for common secret patterns.

**Testing:** Use test fixtures and mock credentials in test files (allowed exception).
