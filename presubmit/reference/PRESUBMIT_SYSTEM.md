# Presubmit Documentation System

**Last Updated:** 2025-10-23
**Purpose:** Automated reminder system to update documentation before commits

---

## Overview

The presubmit system ensures documentation (WORK_LOG.md and PROJECT_STATUS.md)
stays current by displaying a reminder on every git commit.

**Key Features:**
- ✓ Displays reminder before every commit
- ✓ Never blocks commits (always passes)
- ✓ No "AI" references in public repo
- ✓ All session files gitignored

---

## How It Works

### 1. File Structure

```
TOSCA-dev/
├── .pre-commit-config.yaml              # Pre-commit hook config (public repo)
├── .pre-commit-hooks/
│   └── show-presubmit-reminder.py       # Reminder display script (public repo)
├── .gitignore                           # Ignores presubmit/ folder
└── presubmit/                           # THIS FOLDER (gitignored)
    ├── REMINDER.txt                     # Message displayed on commits
    ├── WORK_LOG.md                      # Real-time action tracking
    ├── PROJECT_STATUS.md                # Complete project state
    ├── NEW_SESSION_GUIDE.md             # How to start sessions
    ├── SESSION_PROMPT.md                # Session prompt template
    └── PRESUBMIT_SYSTEM.md              # This file
```

### 2. Pre-Commit Hook Configuration

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: presubmit-reminder
        name: Documentation Reminder
        entry: python .pre-commit-hooks/show-presubmit-reminder.py
        language: system
        always_run: true
        pass_filenames: false
        stages: [pre-commit]
        verbose: true
```

**What it does:**
- Runs on every commit (`always_run: true`)
- Executes Python script to display reminder
- Uses `verbose: true` to show output even when passing
- Never blocks commits (script always exits 0)

### 3. Reminder Display Script

**File:** `.pre-commit-hooks/show-presubmit-reminder.py`

```python
#!/usr/bin/env python3
"""Display presubmit documentation reminder before commits."""
import sys
from pathlib import Path

reminder_file = Path("presubmit/REMINDER.txt")

if reminder_file.exists():
    print(reminder_file.read_text(encoding="utf-8"))
    print()

sys.exit(0)  # Always succeed (don't block commit)
```

**What it does:**
- Reads `presubmit/REMINDER.txt`
- Prints it to console
- Always exits with success (0)
- Uses UTF-8 encoding to avoid Windows CP1252 issues

### 4. Reminder Message

**File:** `presubmit/REMINDER.txt`

```
================================================================
                 DOCUMENTATION REMINDER
================================================================

Before committing code changes:

  * Read files in presubmit/ folder
  * Update WORK_LOG.md with new action entry
  * Update PROJECT_STATUS.md if milestone reached
  * Verify documentation reflects current work state

This is a REMINDER ONLY - commit will proceed regardless.

================================================================
```

**Note:** Uses only ASCII characters (no Unicode) to avoid encoding issues on Windows.

---

## What Gets Committed to Public Repo

### ✅ Files in Public Repo (Safe - No Session Context)

1. **`.pre-commit-config.yaml`**
   - Generic "Documentation Reminder" name
   - No mention of AI or session tracking
   - Just references presubmit folder

2. **`.pre-commit-hooks/show-presubmit-reminder.py`**
   - Simple display script
   - References "presubmit" (generic folder name)
   - No session-specific content

3. **`.gitignore`**
   - Line 111: `presubmit/` (ignores entire folder)

### ❌ Files NOT in Public Repo (Gitignored)

Everything in `presubmit/` folder:
- WORK_LOG.md - Session action tracking
- PROJECT_STATUS.md - Complete project state
- NEW_SESSION_GUIDE.md - Session start instructions
- SESSION_PROMPT.md - Prompt templates
- REMINDER.txt - Reminder message content
- This file (PRESUBMIT_SYSTEM.md)
- All session-specific files

---

## Example Commit Flow

### Step 1: Make Code Changes
```bash
# Edit some code
nano src/hardware/camera_controller.py
```

### Step 2: Stage Changes
```bash
git add src/hardware/camera_controller.py
```

### Step 3: Commit (Reminder Displays)
```bash
git commit -m "Add camera feature"
```

**Output:**
```
Documentation Reminder...................................................Passed
- hook id: presubmit-reminder
- duration: 0.06s

================================================================
                 DOCUMENTATION REMINDER
================================================================

Before committing code changes:

  * Read files in presubmit/ folder
  * Update WORK_LOG.md with new action entry
  * Update PROJECT_STATUS.md if milestone reached
  * Verify documentation reflects current work state

This is a REMINDER ONLY - commit will proceed regardless.

================================================================

trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
... (other pre-commit hooks)
```

### Step 4: Update Documentation (If Needed)
```bash
# Edit documentation
nano presubmit/WORK_LOG.md
nano presubmit/PROJECT_STATUS.md

# These files are gitignored, so they won't be committed
```

### Step 5: Commit Proceeds
```
[main abc1234] Add camera feature
 1 file changed, 50 insertions(+)
```

---

## Maintenance

### Updating the Reminder Message

Edit `presubmit/REMINDER.txt` to change what displays:

```bash
nano presubmit/REMINDER.txt
```

Changes take effect immediately on next commit (no reinstall needed).

### Disabling the Reminder (Not Recommended)

Edit `.pre-commit-config.yaml` and comment out the hook:

```yaml
# - repo: local
#   hooks:
#     - id: presubmit-reminder
#       name: Documentation Reminder
#       ...
```

### Re-enabling After Disabling

Uncomment the lines and reinstall:

```bash
venv/Scripts/pre-commit.exe install
```

---

## Troubleshooting

### Reminder Not Showing

**Check 1:** Is verbose enabled?
```bash
grep -A 10 "presubmit-reminder" .pre-commit-config.yaml | grep verbose
```
Should show: `verbose: true`

**Check 2:** Is hook installed?
```bash
cat .git/hooks/pre-commit | grep presubmit
```
Should show reference to pre-commit framework.

**Fix:** Reinstall hooks
```bash
venv/Scripts/pre-commit.exe install
```

### Encoding Errors (UnicodeDecodeError)

**Problem:** REMINDER.txt has non-ASCII characters

**Fix:** Use only ASCII characters in REMINDER.txt
```
✓ → * (asterisk)
⚠️ → WARNING (text)
╔═╗ → === (equals signs)
```

**Script already handles:** UTF-8 encoding specified in script

### Hook Blocking Commits

**Problem:** Script exits with non-zero code

**Check:** Last line of script should be:
```python
sys.exit(0)  # Always succeed
```

**Never should be:** `sys.exit(1)` or any non-zero exit code

---

## Design Decisions

### Why Not Block Commits?

**Decision:** Reminder is informative, not enforcing

**Rationale:**
1. Documentation updates aren't always needed for every commit
2. Sometimes you commit partial work and document later
3. Blocking would be annoying and get bypassed anyway (`--no-verify`)
4. Gentle reminder is more effective than enforcement

### Why "presubmit" Instead of "ai"?

**Decision:** Use generic folder name

**Rationale:**
1. Public repo shouldn't reveal development methodology
2. "presubmit" is generic software engineering term
3. No mention of AI assistants or session tracking
4. Keeps internal process details private

### Why Gitignore the Entire Folder?

**Decision:** All session files stay local

**Rationale:**
1. WORK_LOG.md contains session-specific timestamps and actions
2. PROJECT_STATUS.md has detailed development state
3. Session guides mention AI assistants explicitly
4. No value in publishing development logs to public repo

### Why Python Script Instead of Shell?

**Decision:** Python for cross-platform compatibility

**Rationale:**
1. Works on Windows and Unix-like systems
2. Python available in venv (guaranteed)
3. Better error handling than bash
4. Consistent with other pre-commit hooks

---

## Related Files

**Documentation:**
- `presubmit/WORK_LOG.md` - Action tracking
- `presubmit/PROJECT_STATUS.md` - Project state
- `presubmit/NEW_SESSION_GUIDE.md` - Session start guide
- `presubmit/SESSION_PROMPT.md` - Prompt template

**Implementation:**
- `.pre-commit-config.yaml` - Hook configuration
- `.pre-commit-hooks/show-presubmit-reminder.py` - Display script
- `.gitignore` - Ignores presubmit/ folder

**Reminder:**
- `presubmit/REMINDER.txt` - Message content (ASCII only)

---

## History

**2025-10-23:**
- Created presubmit reminder system
- Renamed ai/ folder to presubmit/
- Added to .gitignore
- Configured pre-commit hook with verbose output
- Fixed Unicode encoding issues (ASCII only in REMINDER.txt)
- Tested and verified working

---

**End of Presubmit System Documentation**
