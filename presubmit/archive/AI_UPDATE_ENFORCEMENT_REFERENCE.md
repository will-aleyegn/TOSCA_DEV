# Enforcing AI Documentation Updates

**Purpose:** Automate reminders for AI to update WORK_LOG.md and PROJECT_STATUS.md

---

## The Problem

Unlike pre-commit hooks (which run automatically), AI documentation updates require the AI assistant to remember to update files after significant work. This can be forgotten during long sessions.

---

## Solution 1: Git Pre-Commit Hook (Recommended)

Create a pre-commit hook that checks if AI documentation was updated.

### Implementation

1. Create `.git/hooks/pre-commit-ai-docs` (already have pre-commit, extend it):

```bash
#!/bin/bash

# Check if code changes were made
if git diff --cached --name-only | grep -qE "^src/|^camera_module/|^actuator_module/"; then
    # Check if AI docs were updated
    if ! git diff --cached --name-only | grep -qE "^ai/WORK_LOG.md|^ai/PROJECT_STATUS.md"; then
        echo "ERROR: Code changes detected but AI documentation not updated!"
        echo ""
        echo "Please update one of:"
        echo "  - ai/WORK_LOG.md (add new action entry)"
        echo "  - ai/PROJECT_STATUS.md (update status)"
        echo ""
        echo "To bypass this check (not recommended):"
        echo "  git commit --no-verify"
        exit 1
    fi
fi

exit 0
```

2. Make it executable:
```bash
chmod +x .git/hooks/pre-commit-ai-docs
```

### How It Works

- Runs before every `git commit`
- Checks if code files were changed
- If yes, requires WORK_LOG.md or PROJECT_STATUS.md to also be staged
- Blocks commit if documentation not updated
- Can be bypassed with `--no-verify` if needed

---

## Solution 2: Claude Code Custom Instructions

Add to your session prompt that forces the AI to check these files.

### In SESSION_PROMPT.md

Add this to the critical rules section:

```markdown
**After EVERY significant action, you MUST:**
1. Update ai/WORK_LOG.md with new action entry
2. Update ai/PROJECT_STATUS.md if major milestone reached
3. Stage both files with git add before committing code

**Significant actions include:**
- Creating new modules/files
- Implementing major features
- Fixing important bugs
- Completing integration work
- Any work that takes >30 minutes
```

---

## Solution 3: MCP Memory Integration

Use the MCP memory server to track session state and remind.

### Setup

1. Create memory entities for current work:
```bash
mcp__memory__create_entities([
    {
        "name": "CurrentWorkSession",
        "entityType": "session",
        "observations": [
            "Started: 2025-10-23",
            "Last documented action: 28",
            "Work log updated: False",
            "Project status updated: False"
        ]
    }
])
```

2. AI checks memory before each commit:
```python
# Pseudo-code for AI logic
if about_to_commit():
    session = check_memory("CurrentWorkSession")
    if session["work_log_updated"] == False:
        remind("Update WORK_LOG.md first!")
    if major_milestone and session["project_status_updated"] == False:
        remind("Update PROJECT_STATUS.md too!")
```

---

## Solution 4: Automated Checklist (Simplest)

Add a checklist to your workflow that the AI must complete.

### In NEW_SESSION_GUIDE.md

Add this section:

```markdown
## Before Every Commit Checklist

AI MUST verify:
- [ ] Work completed and tested
- [ ] ai/WORK_LOG.md updated with new action
- [ ] ai/PROJECT_STATUS.md updated if milestone reached
- [ ] All files staged (git add)
- [ ] Pre-commit hooks will pass
- [ ] Commit message is descriptive

If any item is unchecked, DO NOT commit yet.
```

---

## Solution 5: GitHub Actions (Post-Commit)

Create a GitHub Action that checks commits and comments if docs weren't updated.

### .github/workflows/check-ai-docs.yml

```yaml
name: Check AI Documentation

on:
  push:
    branches: [ main ]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 2

      - name: Check if AI docs updated
        run: |
          # Get changed files
          CHANGED=$(git diff --name-only HEAD~1 HEAD)

          # Check if code changed
          if echo "$CHANGED" | grep -qE "^src/|^camera_module/"; then
            # Check if docs updated
            if ! echo "$CHANGED" | grep -qE "^ai/WORK_LOG.md|^ai/PROJECT_STATUS.md"; then
              echo "WARNING: Code changed but AI documentation not updated!"
              echo "Please update ai/WORK_LOG.md or ai/PROJECT_STATUS.md"
              exit 1
            fi
          fi
```

This will fail the build if docs weren't updated, creating a visible reminder.

---

## Recommended Approach

**Use Solution 1 (Git Hook) + Solution 4 (Checklist)**

Why?
1. **Git hook** catches it before commit (prevents mistakes)
2. **Checklist** reminds AI during work (proactive)
3. Simple to implement
4. No external dependencies
5. Works offline

---

## Implementation Steps

1. **Add git hook:**
   ```bash
   # Edit .git/hooks/pre-commit
   # Add the AI docs check script above
   ```

2. **Update SESSION_PROMPT.md:**
   ```markdown
   CRITICAL: After every significant action:
   1. Update ai/WORK_LOG.md (add action entry)
   2. Update ai/PROJECT_STATUS.md (if milestone)
   3. Stage files before committing
   ```

3. **Update NEW_SESSION_GUIDE.md:**
   Add the checklist section

4. **Test it:**
   ```bash
   # Make a code change
   echo "test" >> src/test.py
   git add src/test.py

   # Try to commit (should fail)
   git commit -m "test"

   # Update docs
   echo "updated" >> ai/WORK_LOG.md
   git add ai/WORK_LOG.md

   # Now commit (should succeed)
   git commit -m "test"
   ```

---

## Limitations

**What this CAN'T do:**
- Force AI to update docs in the middle of work (only at commit time)
- Validate that the update is meaningful (only checks if file changed)
- Remind AI during long sessions before committing

**Workarounds:**
- Add reminder comments in code: `# TODO: Update WORK_LOG.md`
- Set a timer reminder for yourself to prompt AI
- Use MCP memory to track when last update was

---

## Best Practice

**Workflow for AI:**
```
1. User requests feature
2. AI plans work
3. AI implements feature
4. AI updates WORK_LOG.md with action entry
5. AI updates PROJECT_STATUS.md if major milestone
6. AI stages all files (code + docs)
7. AI commits with descriptive message
8. Git hook validates docs were included
9. Commit succeeds ✓
```

---

**Last Updated:** 2025-10-23
**Status:** Documented, not yet implemented
