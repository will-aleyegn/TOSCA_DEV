# TOSCA Documentation Maintenance Guide

**Version:** 1.0
**Last Updated:** 2025-11-04
**Purpose:** Comprehensive guide for maintaining TOSCA project documentation quality

---

## Overview

The TOSCA project uses an automated documentation maintenance system to ensure:
- Consistent quality across all documentation
- Up-to-date content and metadata
- Valid links and references
- Standardized formatting and style
- Regular quality audits

**Current Quality Score:** 47/100 (needs improvement)

---

## Maintenance Tools

### 1. Full Documentation Audit

**Script:** `scripts/doc_maintenance.py`

Performs comprehensive quality analysis including:
- File discovery and categorization
- Content analysis (word count, structure, metadata)
- Link validation (internal and external)
- Style consistency checking
- Stale documentation detection

**Usage:**
```bash
# Run full audit
python3 scripts/doc_maintenance.py

# Check score only
python3 scripts/doc_maintenance.py --score-only

# Custom output directory
python3 scripts/doc_maintenance.py --output-dir custom/path
```text

**Output:**
- JSON results: `docs/reports/doc_audit_TIMESTAMP.json`
- Markdown report: `docs/DOCUMENTATION_MAINTENANCE_REPORT.md`

### 2. Automated Date Addition

**Script:** `scripts/doc_fix_dates.py`

Adds "Last Updated" metadata to documentation files that lack dates.

**Usage:**
```bash
# Dry run (preview changes)
python3 scripts/doc_fix_dates.py --dry-run

# Apply changes
python3 scripts/doc_fix_dates.py
```text

**What it does:**
- Scans all markdown files
- Detects files without date metadata
- Adds "Last Updated: YYYY-MM-DD" after first heading
- Preserves existing content structure

### 3. Code Block Language Specification

**Script:** `scripts/doc_fix_code_blocks.py`

Automatically adds language specifications to code blocks.

**Usage:**
```bash
# Dry run (preview changes)
python3 scripts/doc_fix_code_blocks.py --dry-run

# Apply changes
python3 scripts/doc_fix_code_blocks.py
```bash

**Supported Languages:**
- Python (auto-detected from imports, def, class)
- Bash/Shell (auto-detected from #!/bin/bash, echo, export)
- JavaScript (auto-detected from function, const, =>)
- YAML (auto-detected from key: value patterns)
- JSON (auto-detected from object structure)
- Text (default fallback)

---

## Maintenance Schedule

### Daily (Automated via Pre-Commit Hooks)
- ✅ Link validation for modified files
- ✅ Style consistency checks
- ✅ Markdown syntax validation

### Weekly (Manual or Automated)
- 📅 Quick audit of recent changes
- 📅 Update dates on modified files
- 📅 Fix any broken links

### Monthly (Required)
- 📊 Full documentation audit
- 📊 Review and address quality issues
- 📊 Update stale documentation
- 📊 Generate and review audit report

### Quarterly (Strategic Review)
- 🔍 Comprehensive content review
- 🔍 Architecture document updates
- 🔍 Documentation structure optimization
- 🔍 Quality score improvement planning

---

## Quality Standards

### Minimum Requirements

Every documentation file MUST have:
- ✅ Clear title (# Heading)
- ✅ Last Updated date
- ✅ Proper heading hierarchy (no skipped levels)
- ✅ Valid internal links
- ✅ Language specifications for code blocks

### Best Practices

Documentation SHOULD include:
- 📝 Brief introduction/purpose statement
- 📝 Table of contents (for files >200 lines)
- 📝 Examples and code samples
- 📝 Cross-references to related docs
- 📝 Update history or changelog

### Content Quality

- **Clarity:** Use clear, concise language
- **Accuracy:** Keep technical details current
- **Completeness:** Cover all relevant aspects
- **Organization:** Use logical structure
- **Accessibility:** Provide context and examples

---

## Common Issues and Fixes

### Issue: Broken Internal Links

**Symptoms:** Link validation reports missing files

**Fixes:**
1. Check if file was renamed or moved
2. Update link path to match current location
3. Use relative paths from document location
4. Test link after fixing

**Example:**
```markdown
# Broken
[Safety System](safety_system.md)

# Fixed
[Safety System](architecture/03_safety_system.md)
```text

### Issue: Missing Dates

**Symptoms:** Audit reports files with "No date"

**Automated Fix:**
```bash
python3 scripts/doc_fix_dates.py
```text

**Manual Fix:**
Add after first heading:
```markdown
# Document Title

**Last Updated:** 2025-11-04

Content starts here...
```text

### Issue: Heading Hierarchy Jumps

**Symptoms:** Style checker reports heading hierarchy violations

**Problem:**
```markdown
# Level 1
### Level 3  ← Skipped level 2!
```text

**Fix:**
```markdown
# Level 1
## Level 2
### Level 3
```text

### Issue: Code Blocks Without Language

**Symptoms:** Style checker reports missing code language

**Automated Fix:**
```bash
python3 scripts/doc_fix_code_blocks.py
```text

**Manual Fix:**
```markdown
# Before
\```python
def example():
    pass
\```

# After
\```python
def example():
    pass
\```text
```

---

## Integration with Development Workflow

### Pre-Commit Validation

Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: doc-maintenance
      name: Documentation Quality Check
      entry: python3 scripts/doc_maintenance.py --score-only
      language: python
      files: \.md$
```text

### Git Commit Guidelines

When modifying documentation:
1. Update "Last Updated" date
2. Run link validation
3. Check style consistency
4. Include doc changes in commit message

**Example commit:**
```bash
git add docs/architecture/03_safety_system.md
git commit -m "docs: update safety system architecture with new GPIO pins

- Added MCP4725 DAC documentation
- Updated pin assignments for aiming beam
- Fixed broken links to hardware specs"
```text

### Pull Request Checklist

Before submitting PRs with documentation changes:
- [ ] Ran full documentation audit
- [ ] Fixed all high-priority issues
- [ ] Updated dates on modified files
- [ ] Validated all links
- [ ] Checked code block languages
- [ ] Quality score maintained or improved

---

## Troubleshooting

### Audit Script Fails

**Problem:** Script crashes or reports errors

**Solutions:**
1. Check Python version (requires 3.9+)
2. Verify file permissions
3. Run from project root directory
4. Check for corrupted markdown files

### False Positive Link Issues

**Problem:** Valid links reported as broken

**Causes:**
- Symlinks or junction points (Windows)
- Case-sensitive file systems
- Relative path calculation errors

**Solutions:**
1. Verify file exists manually
2. Check path casing matches exactly
3. Use absolute paths from project root

### Low Quality Score

**Problem:** Audit reports low quality score (<70)

**Action Plan:**
1. Review audit report details
2. Prioritize high-severity issues
3. Address broken links first
4. Update stale documentation
5. Fix style consistency
6. Re-run audit to verify improvements

---

## Reporting and Metrics

### Quality Score Calculation

```
Base Score: 100
- Broken Links: -5 points each
- Style Issues: -0.2 points each
- Stale Documents: -1 point each
= Final Score (minimum 0)
```text

### Target Scores

- **Excellent:** 90-100 (production-ready)
- **Good:** 75-89 (minor improvements needed)
- **Fair:** 60-74 (attention required)
- **Poor:** <60 (major maintenance needed)

### Tracking Improvements

Monitor quality score over time:
```bash
# Current score
python3 scripts/doc_maintenance.py --score-only

# Compare with previous reports
ls -lt docs/reports/doc_audit_*.json
```

---

## Best Practices

### 1. Update as You Go

Don't let documentation debt accumulate:
- Update docs when changing code
- Fix issues immediately when found
- Keep dates current

### 2. Use Templates

Create templates for common document types:
- Architecture decision records (ADRs)
- Feature documentation
- API documentation
- Testing guides

### 3. Peer Review

Have documentation reviewed by:
- Team members unfamiliar with the feature
- Technical writers (if available)
- Development tools and automated checks

### 4. Version Control

Maintain documentation in sync with code:
- Same version control system (Git)
- Link docs to feature branches
- Include docs in code reviews

### 5. Accessibility

Make documentation accessible to all users:
- Use descriptive link text
- Provide alt text for images
- Organize with clear headings
- Write at appropriate technical level

---

## Resources

### Documentation Files
- **Main Index:** `docs/INDEX.md`
- **Inventory:** `docs/DOCUMENTATION_INVENTORY.md`
- **Audit Report:** `docs/DOCUMENTATION_MAINTENANCE_REPORT.md`
- **Memory Health:** `docs/MEMORY_HEALTH_REPORT.md`

### Maintenance Scripts
- **Full Audit:** `scripts/doc_maintenance.py`
- **Add Dates:** `scripts/doc_fix_dates.py`
- **Fix Code Blocks:** `scripts/doc_fix_code_blocks.py`

### Related Documentation
- **Development Standards:** `docs/DEVELOPMENT_STANDARDS.md`
- **Project Context:** See project root documentation
- **README.md:** Project overview and setup

---

## Support and Feedback

### Getting Help

1. Check this guide for common issues
2. Review audit reports for specific problems
3. Consult project documentation for development guidance
4. Reach out to project maintainers

### Reporting Issues

File issues for:
- Tool bugs or failures
- False positive quality warnings
- Missing features or improvements
- Documentation standard violations

---

**Maintained By:** TOSCA Development Team
**Next Review:** 2025-12-04
**Document Version:** 1.0
