# TOSCA Quarterly Audit Checklist

**Purpose:** Manual audit process to verify AI reference policy compliance and documentation quality

**Frequency:** Quarterly (every 3 months)

**Recommended Schedule:**
- Q1: End of March
- Q2: End of June
- Q3: End of September
- Q4: End of December

**Duration:** 1-2 hours

**Auditor:** [Development Team Member]

---

## Pre-Audit Preparation

- [ ] Ensure git repository is up-to-date (`git pull`)
- [ ] Confirm all local changes are committed
- [ ] Verify pre-commit hooks are installed (`pre-commit install`)
- [ ] Check Python 3.12+ is available for audit script

---

## Step 1: Automated Scan (15 minutes)

### Run Audit Script

```bash
cd /path/to/TOSCA-dev
python scripts/audit_ai_references.py --output audit_reports/YYYY-QX-audit-report.md
```bash

Replace `YYYY-QX` with current year and quarter (e.g., `2025-Q4-audit-report.md`)

### Review Output

- [ ] **Files Scanned:** ______ (expected: 100-150 production files)
- [ ] **Violations Found:** ______ (expected: 0)
- [ ] **Outdated Documentation:** ______ files (expected: 0-5)

### If Violations Found (should be zero):

**STOP - Remediation Required**

1. [ ] Document violation details in audit report
2. [ ] Remove AI references from affected files
3. [ ] Investigate how violations bypassed pre-commit hook
4. [ ] Update hook patterns if systematic gap identified
5. [ ] Re-run audit script to confirm clean state
6. [ ] Commit fixes with message: `fix: remove AI references (quarterly audit)`

---

## Step 2: Pre-commit Hook Verification (10 minutes)

### Check Hook Status

```bash
pre-commit run --all-files
```text

Expected: All hooks pass

- [ ] **trailing-whitespace:** Passed
- [ ] **end-of-file-fixer:** Passed
- [ ] **check-yaml:** Passed
- [ ] **check-added-large-files:** Passed
- [ ] **check-merge-conflict:** Passed
- [ ] **debug-statements:** Passed
- [ ] **mixed-line-ending:** Passed
- [ ] **black:** Passed
- [ ] **flake8:** Passed
- [ ] **isort:** Passed
- [ ] **mypy:** Passed
- [ ] **detect-ai-references:** Passed ✅ (CRITICAL)

### Test AI Detection Hook

Create test file with AI reference:

```bash
echo "This was reviewed by Claude AI assistant." > test_violation.md
git add test_violation.md
git commit -m "test: verify hook"
```text

Expected: Commit blocked with clear error message

- [ ] Commit blocked (exit code 1)
- [ ] Clear error message displayed
- [ ] Line number and pattern shown
- [ ] Remediation steps provided

Clean up:

```bash
git restore --staged test_violation.md
rm test_violation.md
```text

---

## Step 3: Documentation Review (20-30 minutes)

### Core Documentation Currency

Review key files for accuracy (spot check):

- [ ] **README.md:** Reflects current version, features, installation
- [ ] **LESSONS_LEARNED.md:** Contains recent bug fixes and solutions
- [ ] **PROJECT_STATUS.md:** Current milestones and technical debt
- [ ] **CLAUDE.md:** Development context is current (version, recent work)

### Architecture Documentation

Verify architecture docs match current implementation:

- [ ] **docs/architecture/01_system_overview.md:** Technology stack current
- [ ] **docs/architecture/09_test_architecture.md:** Test infrastructure accurate
- [ ] **docs/architecture/SAFETY_SHUTDOWN_POLICY.md:** Implementation correct

### Outdated Documentation

From audit script output, review files >6 months old:

For each outdated file:
- [ ] **Option 1 - Update:** Content still relevant, update dates and details
- [ ] **Option 2 - Archive:** Content superseded, move to `docs/archive/`
- [ ] **Option 3 - Delete:** Content no longer needed, remove entirely

Document decisions in audit report.

---

## Step 4: Regulatory Compliance Check (10-15 minutes)

### Deliverable Documentation

Verify no AI references in regulatory docs:

```bash
grep -ri "claude\|chatgpt\|AI assistant\|task master\|gemini" docs/regulatory/
```text

Expected: No matches (exit code 1)

- [ ] **PRODUCT_REQUIREMENTS_DOCUMENT.md:** Clean
- [ ] **TECHNICAL_SPECIFICATION.md:** Clean
- [ ] **SOFTWARE_REQUIREMENTS_SPECIFICATION.md:** Clean

### Code Attribution

Spot check recent code reviews:

```bash
find docs -name "*CODE_REVIEW*.md" -type f | head -5
```text

Verify attribution format:

- [ ] Uses generic terms: "Code Review - [Date]"
- [ ] No AI tool references
- [ ] Professional attribution standards followed

---

## Step 5: Git History Audit (10 minutes)

### Recent Commits Review

Check last 20 commits for AI references in messages:

```bash
git log -20 --oneline --all
```text

- [ ] No commit messages with AI tool names
- [ ] Professional commit message format
- [ ] Bypass hooks (`--no-verify`) used appropriately

### Bypass Hook Usage

Search for bypass instances:

```bash
git log --all --grep="--no-verify" --oneline
```text

For each bypass commit:
- [ ] Justification provided in commit message
- [ ] Bypass was appropriate (MyPy false positive, policy docs, emergency)

---

## Step 6: Configuration Validation (5 minutes)

### .gitignore Verification

```bash
cat .gitignore | grep -E "claude|taskmaster|gemini|cursor|mcp"
```text

Expected entries:
- [ ] `.claude/`
- [ ] `.gemini/`
- [ ] `.taskmaster/`
- [ ] `.cursor/`
- [ ] `.mcp.json`
- [ ] `CLAUDE.md`
- [ ] `presubmit/`

### Pre-commit Config

```bash
cat .pre-commit-config.yaml | grep -A 5 "detect-ai-references"
```text

Verify:
- [ ] Hook is enabled
- [ ] Correct entry point (`python .pre-commit-hooks/detect-ai-references.py`)
- [ ] Correct stage (`pre-commit`)
- [ ] Passes filenames (`pass_filenames: true`)

---

## Step 7: Documentation Standards Compliance (5-10 minutes)

### File Metadata

Spot check 5 random documentation files:

```bash
find docs -name "*.md" -type f | shuf | head -5
```text

For each file, verify metadata presence:
- [ ] **Last Updated:** Date present and recent
- [ ] **Version:** Matches current version (v0.9.12-alpha or later)
- [ ] **Purpose:** Brief description present

### Version Consistency

```bash
grep -r "v0\\.9\\." docs/ README.md CLAUDE.md | wc -l
```text

- [ ] Version references are consistent across documentation
- [ ] No references to outdated versions (v0.8.x or earlier)

---

## Step 8: Audit Report Finalization (10 minutes)

### Complete Markdown Report

Edit generated report file: `audit_reports/YYYY-QX-audit-report.md`

- [ ] Add auditor name
- [ ] Update sign-off section
- [ ] Add any additional notes or observations
- [ ] Document remediation actions taken (if any)

### Commit Audit Report

```bash
git add audit_reports/YYYY-QX-audit-report.md
git add docs/DEVELOPMENT_STANDARDS.md  # If updated
git commit -m "docs: quarterly audit report Q[X] YYYY"
```text

### Archive Old Audit Reports

If >4 quarters of reports exist, move old reports to archive:

```bash
mkdir -p audit_reports/archive/
git mv audit_reports/YYYY-QX-*.md audit_reports/archive/
git commit -m "chore: archive old audit reports"
```text

---

## Step 9: Follow-up Actions (As needed)

### If Issues Found:

- [ ] Create GitHub issues for systematic problems
- [ ] Update `LESSONS_LEARNED.md` if valuable learning
- [ ] Schedule team discussion if policy updates needed
- [ ] Re-run full audit after remediation

### Process Improvements:

- [ ] Update audit checklist based on findings
- [ ] Enhance pre-commit hook patterns if gaps found
- [ ] Improve documentation standards if inconsistencies found

---

## Step 10: Schedule Next Audit

- [ ] Add calendar reminder for next quarter
- [ ] Update `docs/DEVELOPMENT_STANDARDS.md` with next review date
- [ ] Notify team of audit completion

**Next Audit Date:** _____________ (3 months from today)

---

## Audit Summary

**Date Completed:** _____________

**Auditor:** _____________

**Overall Status:** [ ] PASS  [ ] FAIL  [ ] PASS WITH RECOMMENDATIONS

**Violations Found:** _______

**Remediation Required:** [ ] Yes  [ ] No

**Documentation Issues:** _______

**Recommendations:**

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**Sign-off:** _______________________________

---

## Quick Reference Commands

```bash
# Run automated audit
python scripts/audit_ai_references.py --output audit_reports/YYYY-QX-audit-report.md

# Check pre-commit hooks
pre-commit run --all-files

# Test AI detection hook
echo "Test by Claude AI" > test.md && git add test.md && git commit -m "test"
git restore --staged test.md && rm test.md

# Search for AI references
grep -ri "claude\|chatgpt\|AI assistant" docs/ src/ components/

# Check outdated docs (>180 days)
find docs -name "*.md" -type f -mtime +180

# Verify .gitignore
cat .gitignore | grep -E "claude|taskmaster|gemini|cursor"

# Recent commits check
git log -20 --oneline --all

# Bypass hook usage
git log --all --grep="--no-verify" --oneline
```text

---

## Troubleshooting

### Audit Script Errors

**Problem:** Script not found

```bash
# Verify script exists
ls -la scripts/audit_ai_references.py

# Make executable if needed
chmod +x scripts/audit_ai_references.py
```text

**Problem:** Unicode errors on Windows

```bash
# Use UTF-8 encoding
python -X utf8 scripts/audit_ai_references.py --output report.md
```text

### Pre-commit Hook Failures

**Problem:** Hook not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Force run all hooks
pre-commit run --all-files
```

**Problem:** False positives

- Check if phrase is legitimate (e.g., "main function")
- Add to `WHITELIST_PATTERNS` in both:
  - `.pre-commit-hooks/detect-ai-references.py`
  - `scripts/audit_ai_references.py`
- Document in audit report

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Next Review:** 2026-02-01 (with quarterly audit)
