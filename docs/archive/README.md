# Archive Directory - TOSCA Project

Historical artifacts, superseded code, and completed work documentation.

**Purpose:** Maintain complete audit trail for medical device FDA compliance
**Policy:** Never delete, always archive
**Last Updated:** 2025-11-06

---

## Directory Structure

### screenshots-2025-11/
**Hardware Tab UI redesign screenshots (Nov 5-6, 2025)**
- 11 screenshots documenting UI/UX improvements
- Initialization sequence badges (1→2→3)
- Widget spacing standardization
- Connection status indicators
- **Related:** docs/UI_HARDWARE_TAB_ANALYSIS_2025-11-06.md

### wsl-migration/
**Claude Code WSL migration package (Oct 2025)**
- Complete migration from Windows to WSL environment
- MCP server configurations
- Memory graph preservation
- **Status:** Migration completed ✅
- **Related:** Self-contained migration package

### 2025-11-reports/
**Historical reports from November 2025**
- CAMERA_SETTINGS_FIX_REPORT.md - Camera configuration fixes
- Issues resolved and integrated into v0.9.15-alpha
- **Related:** src/hardware/camera_controller.py

### 2025-11-pre-completion/
**Pre-v0.9.12 completion documentation**
- CAMERA_PERFORMANCE_FIXES.md
- EXPOSURE_SAFETY_LIMITER.md
- INTEGRATION_COMPLETE.md
- LINE_PROTOCOL_BUILDER.md
- MOTOR_GUI_INTEGRATION.md
- REFACTORING_LOG.md
- UI_CHANGES_2025-10-29.md
- dead_code_removal_log.md
- **Status:** Historical record of development phases

### code-reviews/
**Historical code reviews and analysis**
- safety_code_review.md - Safety system review
- signal_connections_report.md - Signal/slot analysis
- widget_integration_matrix.md - Widget connectivity
- **Status:** Superseded by comprehensive reviews in main docs/

### planning-docs/
**Superseded planning documents**
- CODE_REVIEW_ACTION_PLAN.md
- UI_REDESIGN_PLAN.md
- **Status:** Plans completed, archived for reference

---

## Archive Policy

### When to Archive

**Immediate archiving:**
- Completed work documentation (task finished, integrated)
- Superseded code files (replaced by refactoring)
- Historical screenshots (older than 1 month)
- Completed migration packages
- Resolved bug reports

**Keep in main docs/:**
- Current architecture documentation
- Active development plans
- Regulatory compliance docs
- Current code review reports
- In-progress work

### Archive Structure

**Required elements:**
1. Use dated folders (YYYY-MM format)
2. Include README.md in each subdirectory
3. Reference related current documentation
4. Document archive date and reason
5. Preserve git commit links for traceability

**README template:**
```markdown
# [Archive Name]

[Brief description]

**Date:** YYYY-MM
**Status:** [Completed/Superseded/Historical]
**Related:** [Links to current docs or code]

## Contents
[List of files with brief descriptions]

## Archive Notes
[Why archived, what replaced it, context]

**Archived:** YYYY-MM-DD
```

### Retention Policy

**Indefinite retention:**
- Medical device audit trail requirement (FDA 21 CFR Part 11)
- All archived materials kept permanently
- Never delete without documented justification
- Use git history for version control, not file deletion

**Access:**
- All archive contents remain searchable
- Git history preserves when files were active
- README files provide navigation and context

---

## Navigation

**Finding archived content:**
1. Check this README for directory list
2. Read subdirectory README for details
3. Use git log to see when files were archived
4. Check main docs/INDEX.md for current versions

**Restoring archived content:**
1. If need to restore, copy from archive back to active location
2. Document why restored in git commit
3. Update relevant README files
4. Consider if restoration indicates missing functionality

---

## Maintenance

**Quarterly review:**
- Verify all archived subdirectories have READMEs
- Update this index with new archives
- Check for obsolete archives that could be compressed
- Ensure git commit links still valid

**Archive additions:**
1. Create dated subdirectory
2. Move files to archive
3. Create README in subdirectory
4. Update this main README
5. Commit with detailed message
6. Document in cleanup report

---

**Archive Created:** 2025-11-06
**Total Subdirectories:** 6
**Total Archived Files:** 40+
**Compliance:** FDA 21 CFR Part 11 (Audit Trail)
