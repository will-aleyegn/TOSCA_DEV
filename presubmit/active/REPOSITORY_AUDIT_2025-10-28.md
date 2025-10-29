# TOSCA Repository Organization Audit

**Date:** 2025-10-28
**Auditor:** AI Assistant (Claude)
**Scope:** Complete repository structure, files, and organization
**Based On:** REPOSITORY_REORGANIZATION_PLAN.md, README.md, presubmit/README.md

---

## Executive Summary

**Status:** ✅ Generally well-organized, but **90MB of unnecessary cache files** + minor duplicates found

**Critical Issues:** 4 (cache folders to delete)
**High Priority:** 2 (GPIO consolidation, old data folder)
**Medium Priority:** 1 (presubmit documentation review)
**Low Priority:** 0 (structure is good)

**Total Wasted Space:** ~90.3 MB (cache) + 304 KB (duplicate data)

---

## ✅ What's Working Well

### Excellent Organization

1. **Manufacturer Documentation** ✅
   - Properly organized in `components/*/manufacturer_docs/`
   - PDFs successfully tracked in git (8.3 MB across 3 components)
   - .gitignore fix from reorganization plan was implemented
   - Clear README.md files in each manufacturer_docs folder

2. **Source Code Structure** ✅
   - Clean `src/` organization: ui, core, hardware, database, config
   - Consistent naming conventions
   - No duplicate code files found
   - Proper separation of concerns

3. **Testing Infrastructure** ✅
   - Well-organized `tests/` structure
   - Mock infrastructure properly documented
   - Test categories clearly separated

4. **Documentation** ✅
   - `docs/architecture/` contains technical docs
   - Component READMEs are unique and purposeful
   - No duplicate READMEs found

5. **Presubmit System** ✅
   - Clean folder structure (active, onboarding, reference, reviews, archive)
   - Archives properly organized by date
   - Session tracking functional

---

## 🔴 CRITICAL Issues (Delete Immediately)

### Issue 1: .mypy_cache/ - 86 MB
**Location:** `.mypy_cache/`
**Size:** 86 MB
**Status:** Gitignored (line 98) but exists in filesystem
**Impact:** Wastes 86 MB of disk space

**Analysis:**
- MyPy type checking cache
- Already in .gitignore
- Regenerates automatically when mypy runs
- Safe to delete

**Recommendation:**
```bash
rm -rf .mypy_cache/
```

**Priority:** CRITICAL - Large space waste

---

### Issue 2: htmlcov/ - 3.5 MB
**Location:** `htmlcov/`
**Size:** 3.5 MB
**Status:** Gitignored (line 40) but exists in filesystem
**Impact:** Wastes 3.5 MB of disk space

**Analysis:**
- Test coverage HTML reports (from pytest-cov)
- Already in .gitignore
- Regenerates with `pytest --cov-report=html`
- Safe to delete

**Recommendation:**
```bash
rm -rf htmlcov/
```

**Priority:** CRITICAL - Space waste

---

### Issue 3: .pytest_cache/ - 15 KB
**Location:** `.pytest_cache/`
**Size:** 15 KB
**Status:** Gitignored (line 38) but exists in filesystem
**Impact:** Minor space waste, repo clutter

**Analysis:**
- Pytest cache for faster test reruns
- Already in .gitignore
- Regenerates automatically
- Safe to delete

**Recommendation:**
```bash
rm -rf .pytest_cache/
```

**Priority:** CRITICAL - Cleanup

---

### Issue 4: .backups/ - Empty Folder
**Location:** `.backups/`
**Size:** Empty
**Status:** Not documented anywhere
**Impact:** Repository clutter

**Analysis:**
- Empty folder with no contents
- Not mentioned in any documentation
- Not in .gitignore (but should be)
- Purpose unknown

**Recommendation:**
```bash
rm -rf .backups/
```

**Priority:** CRITICAL - Undocumented folder

---

## 🟠 HIGH Priority Issues

### Issue 5: src/data/ - Old Duplicate Data Folder
**Location:** `src/data/`
**Size:** 304 KB (old tosca.db: 98 KB + logs + videos folders)
**Current:** `data/` at root (4.6 MB, active database)

**Analysis:**
- `src/data/` contains OLD database file (98 KB) from previous location
- Current correct location is `data/` at root per README.md
- `src/data/` has old logs/ and videos/ folders
- Database in `src/data/` is outdated (Oct 27) vs. current (Oct 28)

**Recommendation:**
```bash
# VERIFY first that data/ at root is the active one
ls -la data/tosca.db       # Should be 106 KB, Oct 28
ls -la src/data/tosca.db   # Should be 98 KB, Oct 27 (OLD)

# If confirmed, delete old location
rm -rf src/data/
```

**Alternative:** Check if any code references `src/data/` first:
```bash
grep -r "src/data" src/ config/ --include="*.py"
```

**Priority:** HIGH - Old duplicate data location

---

### Issue 6: Three GPIO Component Folders - Consolidation Needed
**Locations:**
1. `components/gpio_arduino/` - ARDUINO_SETUP.md (8 KB)
2. `components/gpio_module/` - CODE_REVIEW + LESSONS_LEARNED (21 KB)
3. `components/gpio_safety/` - README.md + README_FT232H_DEPRECATED.md (12 KB)

**Analysis:**
- **gpio_arduino:** Current implementation documentation
- **gpio_module:** Code review artifacts (Oct 27, 2025)
- **gpio_safety:** Deprecated FT232H implementation + README pointing to gpio_arduino

**Current Situation:**
- `gpio_safety/README.md` says: "Current GPIO implementation uses Arduino Nano"
- Points to `gpio_arduino/ARDUINO_SETUP.md`
- `gpio_module/` has recent code reviews but unclear what it's for

**Recommendation:**

**Option A: Consolidate into components/gpio/ (RECOMMENDED)**
```bash
mkdir components/gpio
mv components/gpio_arduino/ARDUINO_SETUP.md components/gpio/
mv components/gpio_module/CODE_REVIEW_2025-10-27.md components/gpio/docs/
mv components/gpio_module/LESSONS_LEARNED.md components/gpio/docs/
mv components/gpio_safety/README_FT232H_DEPRECATED.md components/gpio/DEPRECATED_FT232H.md

# Create new README
cat > components/gpio/README.md <<EOF
# GPIO Safety Interlocks

Current implementation: Arduino Nano with PyFirmata

See:
- ARDUINO_SETUP.md - Current setup guide
- docs/ - Code reviews and lessons learned
- DEPRECATED_FT232H.md - Legacy FT232H documentation
EOF

# Delete old folders
rm -rf components/gpio_arduino components/gpio_module components/gpio_safety
```

**Option B: Keep gpio_arduino, move reviews to presubmit/**
```bash
mv components/gpio_module/CODE_REVIEW_2025-10-27.md presubmit/reviews/
mv components/gpio_module/LESSONS_LEARNED.md presubmit/reviews/
rm -rf components/gpio_module components/gpio_safety
```

**Priority:** HIGH - Three folders for one component creates confusion

---

## 🟡 MEDIUM Priority Issues

### Issue 7: __pycache__ Folders - 10 instances
**Locations:** Throughout src/, components/, tests/
**Size:** Small (varies)
**Status:** Gitignored (line 2) but exist in filesystem

**Analysis:**
- Python bytecode cache folders
- Already in .gitignore
- Regenerate automatically when Python runs
- Safe to delete periodically

**Recommendation:**
```bash
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
```

**Priority:** MEDIUM - Low impact, but cleanup is good practice

---

### Issue 8: data/protocols/ - Empty Folder
**Location:** `data/protocols/`
**Contents:** Only `.gitkeep` file
**Correct Location:** `protocols/` at root

**Analysis:**
- Root `protocols/` folder contains actual protocol examples (basic_test.json, etc.)
- `data/protocols/` is empty except for .gitkeep
- Per README.md, protocols should be in `protocols/` at root
- `data/` is for runtime data (db, logs, sessions)

**Recommendation:**
```bash
# Verify protocols/ has the actual files
ls -la protocols/examples/  # Should show JSON files

# Remove empty data/protocols/
rm -rf data/protocols/
```

**Priority:** MEDIUM - Empty folder, minor confusion

---

## 🟢 LOW Priority / Informational

### Issue 9: Presubmit Active Documentation Review
**Location:** `presubmit/active/`
**Files:** 12 markdown files

**Current Files:**
- CLEANUP_SUMMARY_2025-10-27.md
- DECISIONS.md
- HARDWARE_METADATA_SOURCES.md
- HARDWARE_TAB_ENHANCEMENTS_PLAN.md
- NEXT_STEPS.md
- README_CODE_REVIEW_ADDENDUM.md
- REPOSITORY_REORGANIZATION_PLAN.md (THIS document was used for audit)
- SESSION_STATE.md
- TOOL_INTEGRATION_SUMMARY.md
- UI_CODE_ANALYSIS_REPORT.md
- UI_FEATURES_SUMMARY.md

**Analysis:**
- Some files may be outdated (planning docs after implementation complete)
- Examples:
  - HARDWARE_TAB_ENHANCEMENTS_PLAN.md - Enhancements completed in Milestone 5.6
  - REPOSITORY_REORGANIZATION_PLAN.md - Partially executed (some items done, some not)
  - CLEANUP_SUMMARY_2025-10-27.md - May be superseded by this audit

**Recommendation:**
- Review each file for current relevance
- Move completed planning docs to `presubmit/archive/`
- Keep reference docs (DECISIONS.md, UI_CODE_ANALYSIS_REPORT.md)
- Keep SESSION_STATE.md (always current)

**Priority:** LOW - Documentation organization, no technical impact

---

## 📊 Summary Statistics

### Disk Space Analysis

| Category | Size | Status |
|----------|------|--------|
| Cache folders to delete | 89.5 MB | 🔴 CRITICAL |
| Old data duplicate | 304 KB | 🟠 HIGH |
| Empty folders | Minimal | 🔴 CRITICAL |
| **Total Recoverable** | **~90 MB** | |

### File Organization

| Category | Count | Status |
|----------|-------|--------|
| Properly organized components | 4 | ✅ GOOD |
| GPIO folders needing consolidation | 3 | 🟠 HIGH |
| Duplicate data folders | 1 | 🟠 HIGH |
| Cache folders to delete | 4 | 🔴 CRITICAL |
| Empty/unnecessary folders | 2 | 🔴 CRITICAL |

### Manufacturer Documentation

| Component | Size | Status |
|-----------|------|--------|
| Actuator (Xeryon) | 2.3 MB | ✅ Tracked |
| Camera (Allied Vision) | 3.8 MB | ✅ Tracked |
| Laser (Arroyo) | 2.2 MB | ✅ Tracked |
| **Total** | **8.3 MB** | ✅ **Properly organized** |

---

## 🎯 Recommended Cleanup Sequence

### Phase 1: Critical Deletions (5 minutes)
**Impact:** Recovers 90 MB, removes clutter

```bash
cd C:/Users/wille/Desktop/TOSCA-dev

# 1. Delete cache folders (safe, regenerate automatically)
rm -rf .mypy_cache/
rm -rf htmlcov/
rm -rf .pytest_cache/

# 2. Delete empty backups folder
rm -rf .backups/

# 3. Delete Python cache folders
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null

# 4. Verify data locations before deleting src/data/
ls -la data/tosca.db       # Should be 106 KB (current)
ls -la src/data/tosca.db   # Should be 98 KB (old)

# Check if any code references src/data
grep -r "src/data" src/ config/ --include="*.py"

# If safe (no references), delete old data folder
rm -rf src/data/

# 5. Delete empty data/protocols/
rm -rf data/protocols/
```

**Verification:**
```bash
# Should all return "No such file"
ls -la .mypy_cache/
ls -la htmlcov/
ls -la .pytest_cache/
ls -la .backups/
ls -la src/data/
ls -la data/protocols/

# Should show 0 results
find . -type d -name "__pycache__" -not -path "./venv/*"
```

---

### Phase 2: GPIO Consolidation (15 minutes)
**Impact:** Reduces confusion, improves organization

**Choose Option A or B from Issue 6 above**

Recommended: **Option B** (simpler, less refactoring)
```bash
# Move code review docs to presubmit
mv components/gpio_module/CODE_REVIEW_2025-10-27.md presubmit/reviews/GPIO_CODE_REVIEW_2025-10-27.md
mv components/gpio_module/LESSONS_LEARNED.md presubmit/reviews/GPIO_LESSONS_LEARNED.md

# Delete gpio_module and gpio_safety
rm -rf components/gpio_module/
rm -rf components/gpio_safety/

# Update gpio_arduino README to clarify it's the main GPIO folder
# (Manual step - add note that deprecated FT232H docs are in presubmit/archive/)
```

---

### Phase 3: Documentation Review (30 minutes, optional)
**Impact:** Cleaner documentation structure

Review `presubmit/active/` files:
1. Archive completed planning docs
2. Keep reference/analysis docs
3. Update SESSION_STATE.md after cleanup

---

## 🔍 Additional Findings (Positive)

### Properly Implemented from Previous Reorganization

✅ **`.gitignore` Fixed**
- Line 117: `presubmit/` exclusion ✅ **REMOVED**
- Line 121: `*.pdf` exclusion ✅ **REMOVED**
- Manufacturer PDFs are now tracked in git ✅

✅ **No Root-Level Duplicate Folders**
- No `camera_module/` at root (was in plan as issue)
- No `actuator_module/manuals/` duplicate (was in plan as issue)
- No `docs/actuator-control/` empty folder (was in plan as issue)

✅ **Components Folder Organization**
- All hardware components in `components/`
- Consistent structure across components
- README files properly placed

---

## 📝 Post-Cleanup Verification Checklist

After completing Phase 1 and 2, verify:

- [ ] .mypy_cache/, htmlcov/, .pytest_cache/ do not exist
- [ ] .backups/ does not exist
- [ ] src/data/ does not exist (if deleted)
- [ ] data/protocols/ does not exist
- [ ] No __pycache__ folders exist outside venv/
- [ ] GPIO folders reduced from 3 to 1
- [ ] `git status` shows no unexpected changes
- [ ] All tests still pass: `pytest`
- [ ] Application still runs: `python src/main.py`

---

## 🚨 Important Notes

### Safety Precautions

1. **Before deleting src/data/**, verify no code references it:
   ```bash
   grep -r "src/data" src/ config/ --include="*.py"
   ```
   If any references found, update them to use `data/` at root first.

2. **Backup before GPIO consolidation:**
   ```bash
   cp -r components/gpio_* /tmp/gpio_backup_2025-10-28/
   ```

3. **Run tests after each phase:**
   ```bash
   pytest
   ```

### What NOT to Delete

❌ **DO NOT delete these (they look like cache but aren't):**
- `venv/` - Python virtual environment
- `data/` - Runtime data folder (database, logs, sessions)
- `protocols/` - Protocol JSON templates
- `calibration_data/` - Hardware calibration data
- `.git/` - Git repository
- `.github/` - GitHub Actions workflows
- `.claude/` - Claude Code configuration
- `.pre-commit-hooks/` - Pre-commit hook scripts

---

## 📋 Estimated Time & Impact

| Phase | Time | Disk Space Recovered | Risk Level |
|-------|------|---------------------|------------|
| Phase 1: Critical Deletions | 5 min | 90 MB | 🟢 LOW (all cached/old data) |
| Phase 2: GPIO Consolidation | 15 min | ~50 KB | 🟡 MEDIUM (file moves) |
| Phase 3: Doc Review | 30 min | 0 KB | 🟢 LOW (docs only) |
| **Total** | **50 min** | **~90 MB** | |

---

## 🎓 Lessons Learned

### Good Practices Already in Place

1. **Comprehensive .gitignore** - Well-maintained, catches most artifacts
2. **Clear folder structure** - README.md accurately reflects structure
3. **Presubmit system** - Excellent internal documentation organization
4. **Manufacturer docs** - Successfully transitioned from gitignored to tracked

### Opportunities for Improvement

1. **Cache cleanup automation** - Consider adding to pre-commit hooks
2. **GPIO naming** - Consolidate multiple folders for single component
3. **Regular audits** - Quarterly repository organization reviews
4. **Documentation lifecycle** - Move completed planning docs to archive

---

## 📁 Appendix: Complete Folder Structure (Post-Cleanup)

```
TOSCA-dev/
├── .claude/                    ✅ Claude Code config
├── .git/                       ✅ Git repository
├── .github/                    ✅ GitHub Actions
├── .pre-commit-hooks/          ✅ Pre-commit scripts
├── calibration_data/           ✅ Hardware calibration
├── components/
│   ├── actuator_module/        ✅ Xeryon actuator
│   ├── camera_module/          ✅ Allied Vision camera
│   ├── gpio_arduino/           ✅ Arduino GPIO (consolidated)
│   └── laser_control/          ✅ Arroyo laser
├── config/                     ✅ Config files
├── data/                       ✅ Runtime data (db, logs, sessions)
├── docs/
│   ├── architecture/           ✅ Technical docs
│   └── hardware/               ✅ Hardware docs
├── firmware/
│   └── arduino_watchdog/       ✅ Arduino firmware
├── presubmit/                  ✅ Internal docs
│   ├── active/                 ✅ Current state
│   ├── archive/                ✅ Historical
│   ├── onboarding/             ✅ Session setup
│   ├── reference/              ✅ Policies
│   └── reviews/                ✅ Code reviews
├── protocols/                  ✅ Protocol templates
│   └── examples/               ✅ Example protocols
├── src/                        ✅ Source code
│   ├── config/
│   ├── core/
│   ├── database/
│   ├── hardware/
│   ├── image_processing/
│   ├── ui/
│   └── utils/
├── tests/                      ✅ Test suite
│   ├── actuator/
│   ├── gpio/
│   ├── hardware/
│   └── mocks/
├── venv/                       ✅ Python virtual environment
├── .gitignore                  ✅ Git exclusions
├── PROJECT_STATUS.md           ✅ Project state
├── WORK_LOG.md                 ✅ Action log
├── HISTORY.md                  ✅ Compressed history
└── README.md                   ✅ Project overview
```

---

**Audit Complete**
**Total Issues Found:** 9 (4 critical, 2 high, 2 medium, 1 low)
**Recommended Action:** Execute Phase 1 immediately (5 minutes, 90 MB recovered)
**Next Steps:** Review this report, execute cleanup phases, update SESSION_STATE.md

---

**Document Status:** COMPLETE
**Created:** 2025-10-28
**Location:** `presubmit/active/REPOSITORY_AUDIT_2025-10-28.md`
