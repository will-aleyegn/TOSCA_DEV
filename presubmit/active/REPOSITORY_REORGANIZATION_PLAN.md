# TOSCA Repository Reorganization Plan

**Date:** 2025-10-25
**Purpose:** Clean up duplicate folders, fix gitignore conflicts, remove outdated content
**Priority:** HIGH - Critical gitignore issues blocking manufacturer documentation tracking

---

## Executive Summary

**Critical Issues Found:**
1. `.gitignore` excludes `presubmit/` and `*.pdf` - contradicts user directive to version control everything
2. Duplicate folders: `camera_module/` (empty), `actuator_module/manuals/` (duplicate PDFs)
3. Orphaned git deletions from previous reorganization
4. Empty folder with cache: `docs/actuator-control/`

**Impact:** 8.3 MB of manufacturer documentation is untracked and won't commit to git.

---

## Issue Details

### 1. CRITICAL: .gitignore Conflicts

**Problem:**
```
Line 117: presubmit/          # Blocks workflow documentation
Line 121: *.pdf               # Blocks ALL PDFs including manufacturer docs
```

**User Directive:**
"dont (though gitignored for size) i want all this on git"

**Git Status Confirms Untracked Files:**
```
?? components/MANUFACTURER_DOCS_INDEX.md
?? components/actuator_module/manufacturer_docs/
?? components/camera_module/manufacturer_docs/
?? components/laser_control/manufacturer_docs/
```

**Why This is Critical:**
- Manufacturer documentation (8.3 MB) cannot be committed
- Presubmit workflow documentation is excluded
- Violates FDA traceability requirements
- Documentation versioning doesn't match code versions

---

### 2. Duplicate Folders

#### a) Root `camera_module/` - EMPTY
**Location:** `C:/Users/wille/Desktop/TOSCA-dev/camera_module/`
**Contents:** Empty `examples/` subfolder only
**Correct Location:** `components/camera_module/` (full organization with docs, tests, examples)
**Action:** Delete entire `camera_module/` folder

#### b) `actuator_module/manuals/` - DUPLICATE
**Location:** `C:/Users/wille/Desktop/TOSCA-dev/components/actuator_module/manuals/`
**Contents:**
- Controller Manual.pdf (1.8 MB)
- XLA5.pdf (283 KB)

**Duplicate Of:** `components/actuator_module/manufacturer_docs/xeryon_manuals/`
**Action:** Delete `manuals/` folder (keep `manufacturer_docs/`)

---

### 3. Orphaned Git Deletions

**Problem:** Git tracking old file locations after reorganization

**Deleted Files Still in Git:**
```
D presubmit/FUTURE_WORK.md
D presubmit/PROJECT_STATUS.md
D presubmit/WORK_LOG.md
```

**Current Locations:**
- `presubmit/active/FUTURE_WORK.md`
- `presubmit/active/PROJECT_STATUS.md`
- `presubmit/active/WORK_LOG.md`

**Action:** Formally remove old paths from git tracking

---

### 4. Empty Folder with Cache

**Location:** `docs/actuator-control/`
**Contents:** Only `__pycache__/` subfolder
**Analysis:** Old code location, files were moved, cache remained
**Action:** Delete entire `docs/actuator-control/` folder

---

## Reorganization Actions

### PHASE 1: Critical Fixes (DO IMMEDIATELY)

#### Action 1.1: Fix .gitignore
**Priority:** CRITICAL
**File:** `.gitignore`

**Changes:**
```diff
- # AI Documentation and Session Files (local use only)
- presubmit/

- # Regulatory/FDA Strategy Documents (archive only)
- docs/regulatory_archive/
- *.pdf
```

**Replacement:**
```
# Regulatory/FDA Strategy Documents (archive only)
docs/regulatory_archive/
```

**Rationale:**
- Remove `presubmit/` exclusion (user wants it version controlled)
- Remove `*.pdf` blanket exclusion (blocks manufacturer docs)
- Keep `docs/regulatory_archive/` exclusion if needed for archived files

**Verification:**
```bash
git status | grep "components/.*manufacturer_docs"
# Should show manufacturer_docs/ as changes to be staged
```

---

#### Action 1.2: Delete Empty camera_module/ Folder
**Priority:** HIGH

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
rm -rf camera_module/
```

**Verification:**
```bash
ls -la camera_module/
# Should show: No such file or directory
```

**Reason:** Empty duplicate of `components/camera_module/`

---

#### Action 1.3: Delete Duplicate actuator_module/manuals/
**Priority:** HIGH

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
rm -rf components/actuator_module/manuals/
```

**Verification:**
```bash
ls -la components/actuator_module/manuals/
# Should show: No such file or directory

ls -la components/actuator_module/manufacturer_docs/xeryon_manuals/
# Should show: Controller Manual.pdf, XLA5.pdf (originals preserved)
```

**Reason:** Duplicate PDFs - keep organized `manufacturer_docs/` version

---

#### Action 1.4: Clean Git Orphaned Deletions
**Priority:** MEDIUM

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
git rm presubmit/FUTURE_WORK.md
git rm presubmit/PROJECT_STATUS.md
git rm presubmit/WORK_LOG.md
```

**Verification:**
```bash
git status | grep "presubmit/FUTURE_WORK\|presubmit/PROJECT_STATUS\|presubmit/WORK_LOG"
# Should show: deleted: presubmit/FUTURE_WORK.md (etc.)
```

**Note:** This commits the deletions that were already done in filesystem

---

#### Action 1.5: Delete Empty docs/actuator-control/
**Priority:** LOW

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
rm -rf docs/actuator-control/
```

**Verification:**
```bash
ls -la docs/actuator-control/
# Should show: No such file or directory
```

**Reason:** Contains only __pycache__, no documentation

---

### PHASE 2: Optional Cleanup (DO WHEN CONVENIENT)

#### Action 2.1: Remove __pycache__ Folders (Optional)
**Priority:** LOW
**Reason:** Already gitignored, regenerate automatically

**Locations Found (11 total):**
```
components/actuator_module/__pycache__
components/camera_module/tests/vmbpy_unit_tests/__pycache__
components/camera_module/tests/vmbpy_unit_tests/basic_tests/__pycache__
components/camera_module/tests/vmbpy_unit_tests/real_cam_tests/__pycache__
src/core/__pycache__
src/database/__pycache__
src/hardware/__pycache__
src/ui/__pycache__
src/ui/widgets/__pycache__
src/__pycache__
```

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} +
```

**Note:** Safe to skip - will regenerate on next Python run

---

#### Action 2.2: Clear output/ Folders (Optional)
**Priority:** LOW
**Reason:** Already gitignored, local test outputs

**Locations:**
```
components/actuator_module/output/
components/camera_module/output/
```

**Commands:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
rm -rf components/actuator_module/output/*
rm -rf components/camera_module/output/*
```

**Note:** Safe to skip - test outputs, already excluded from git

---

## Verification Checklist

After completing Phase 1 actions:

**Git Status Check:**
```bash
cd C:/Users/wille/Desktop/TOSCA-dev
git status
```

**Expected Output:**
```
Changes to be committed:
  deleted:    presubmit/FUTURE_WORK.md
  deleted:    presubmit/PROJECT_STATUS.md
  deleted:    presubmit/WORK_LOG.md

Untracked files:
  .gitignore (modified)
  components/MANUFACTURER_DOCS_INDEX.md
  components/actuator_module/manufacturer_docs/
  components/camera_module/manufacturer_docs/
  components/laser_control/manufacturer_docs/
```

**Folder Verification:**
- [ ] `camera_module/` does not exist (deleted)
- [ ] `components/actuator_module/manuals/` does not exist (deleted)
- [ ] `components/actuator_module/manufacturer_docs/` exists (preserved)
- [ ] `docs/actuator-control/` does not exist (deleted)

**Gitignore Verification:**
- [ ] Line 117 `presubmit/` removed
- [ ] Line 121 `*.pdf` removed
- [ ] Manufacturer docs show as untracked in git status

---

## What Was NOT Changed

**Folders with Good Organization (Preserved):**

✅ **docs/architecture/** - 6 markdown files for system architecture
- 01_system_overview.md
- 02_database_schema.md
- 03_safety_system.md
- 04_treatment_protocols.md
- 05_image_processing.md
- 06_protocol_builder.md

✅ **components/*/docs/** - Component-specific technical documentation
- `components/actuator_module/docs/` - HAL fixes, API reference
- `components/camera_module/docs/` - Camera features

✅ **presubmit/** - Development workflow (recently cleaned)
- `active/`, `onboarding/`, `reference/`, `reviews/` structure

✅ **tests/** - Organized by component
- `tests/actuator/` - Actuator hardware tests
- Root level integration tests

✅ **README.md files** - Each serves unique purpose
- Root README.md - Project overview
- Component README.md - Module documentation
- manufacturer_docs/README.md - Navigation guides
- No duplicates found

---

## Summary of Changes

**Deleted:**
- `camera_module/` (empty folder)
- `components/actuator_module/manuals/` (duplicate PDFs)
- `docs/actuator-control/` (empty with cache)

**Modified:**
- `.gitignore` - Removed `presubmit/` and `*.pdf` exclusions

**Git Cleanup:**
- Formally removed 3 orphaned file deletions

**Space Freed:** ~2.1 MB (duplicate PDFs)
**Files Preserved:** All documentation, code, and tests
**Manufacturer Docs:** Now trackable in git (8.3 MB)

---

## Post-Reorganization Next Steps

After completing reorganization and committing changes:

1. **Add manufacturer documentation to git:**
   ```bash
   git add components/MANUFACTURER_DOCS_INDEX.md
   git add components/actuator_module/manufacturer_docs/
   git add components/camera_module/manufacturer_docs/
   git add components/laser_control/manufacturer_docs/
   ```

2. **Commit changes:**
   ```bash
   git commit -m "Clean up repository organization

   - Remove duplicate folders (camera_module/, actuator_module/manuals/)
   - Fix .gitignore to allow manufacturer docs and presubmit/
   - Clean up orphaned git deletions
   - Delete empty docs/actuator-control/

   Manufacturer documentation (8.3 MB) now version controlled per user directive."
   ```

3. **Update MCP memory** with reorganization completion

4. **Update WORK_LOG.md** with reorganization action entry

---

## Risk Assessment

**Low Risk:**
- All actions are deletions of duplicates or empty folders
- No code changes
- All deleted content exists elsewhere in repository
- Gitignore changes explicitly requested by user

**Rollback Plan:**
If issues arise, restore from git:
```bash
git checkout HEAD -- .gitignore
git reset HEAD presubmit/FUTURE_WORK.md presubmit/PROJECT_STATUS.md presubmit/WORK_LOG.md
```

---

**Created:** 2025-10-25
**Location:** presubmit/active/REPOSITORY_REORGANIZATION_PLAN.md
**Status:** Ready for execution
