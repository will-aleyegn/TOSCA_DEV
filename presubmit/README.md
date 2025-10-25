# Presubmit Folder - Internal Development Documentation

**Last Updated:** 2025-10-25
**Purpose:** Internal knowledge base for TOSCA development methodology and session management
**Status:** Git-ignored (never appears in public repository)

---

## What is This Folder?

The `presubmit/` folder is the **private internal knowledge base** for the TOSCA project. It contains all development methodology, session tracking, and planning documents that should never be exposed in the public repository.

### Why It Exists

1. **Session Continuity** - Enable AI sessions to maintain context across time
2. **Private Methodology** - Document development process without exposing it publicly
3. **Progress Tracking** - Track work without cluttering the public repo
4. **Code Quality** - Store reviews, architectural debt analysis, and improvement plans
5. **Compliance** - Maintain regulatory submissions privately

### What Makes It Different

- **Git-Ignored:** Line 117 in `.gitignore` ensures this folder never commits
- **Policy Compliant:** Adheres to Git Content Policy (no AI/FDA references in public repo)
- **Session Hub:** Central location for all internal project knowledge

---

## Quick Navigation

### New to the Project?

**Start here** (in order):
1. `START_HERE.md` - Quick 5-minute entry point
2. `onboarding/NEW_SESSION_GUIDE.md` - Complete onboarding guide
3. Copy-paste prompt from:
   - `onboarding/FULL_SESSION_PROMPT.md` (comprehensive, 5-10 min)
   - `onboarding/QUICK_SESSION_PROMPT.md` (MCP memory, 30 sec)
4. `active/PROJECT_STATUS.md` - Current project state

### During Active Development

**Update frequently:**
- `active/WORK_LOG.md` - Real-time action tracking
- `active/PROJECT_STATUS.md` - Milestone updates
- `active/sessions/` - Session summaries

### Need to Look Something Up?

**Reference documentation:**
- `reference/CODING_STANDARDS.md` - Development rules
- `reference/GIT_CONTENT_POLICY.md` - Public vs private content rules
- `reference/CONFIGURATION.md` - Config file explanations
- `reference/FUTURE_WORK.md` - Future enhancement ideas

### Code Quality & Reviews

**Improvement tracking:**
- `reviews/CODE_REVIEW_SUMMARY.md` - Latest review summary
- `reviews/CODE_REVIEW_FINDINGS.md` - Detailed findings
- `reviews/improvements/` - Detailed improvement plans (6 documents)
- `reviews/plans/` - Implementation plans

---

## Folder Structure

```
presubmit/
|
+-- README.md                        (This file - navigation hub)
+-- START_HERE.md                    (Quick entry point)
|
+-- onboarding/                      Session setup & prompts
|   +-- NEW_SESSION_GUIDE.md         (Complete onboarding)
|   +-- FULL_SESSION_PROMPT.md       (Copy-paste comprehensive prompt)
|   +-- QUICK_SESSION_PROMPT.md      (Copy-paste quick prompt)
|   +-- DEVELOPMENT_ENVIRONMENT_SETUP.md
|
+-- active/                          Current state (update often!)
|   +-- PROJECT_STATUS.md            (Complete project state)
|   +-- WORK_LOG.md                  (Action-by-action tracking)
|   +-- NEXT_STEPS.md                (Current roadmap)
|   +-- sessions/                    (Session summaries)
|       +-- SESSION_SUMMARY_2025-10-25.md
|
+-- reference/                       Stable lookup docs
|   +-- CODING_STANDARDS.md          (Minimal code philosophy)
|   +-- TODO_GUIDELINES.md           (TodoWrite comprehensive guide)
|   +-- CONFIGURATION.md             (Config file guide)
|   +-- GIT_CONTENT_POLICY.md        (Public/private rules)
|   +-- PRESUBMIT_SYSTEM.md          (Pre-commit reminder system)
|   +-- FUTURE_WORK.md               (Enhancement ideas)
|
+-- reviews/                         Code quality & improvements
|   +-- CODE_REVIEW_SUMMARY.md       (Latest review)
|   +-- CODE_REVIEW_FINDINGS.md      (Detailed findings)
|   +-- ARCHITECTURAL_DEBT.md        (Architectural issues)
|   +-- 00_ARCHITECTURE_REVIEW.md
|   +-- improvements/                (6 detailed improvement plans)
|   |   +-- 00_IMPROVEMENT_ROADMAP.md
|   |   +-- 01_IMPORT_PATH_STANDARDIZATION.md
|   |   +-- 02_HARDWARE_CONTROLLER_ABC.md
|   |   +-- 03_CONFIGURATION_MANAGEMENT.md
|   |   +-- 04_WATCHDOG_TIMER_IMPLEMENTATION.md
|   |   +-- 05_DEPENDENCY_INJECTION.md
|   +-- plans/                       (Implementation plans)
|       +-- IMPLEMENTATION_PLAN_CONFIG.md
|       +-- IMPLEMENTATION_PLAN_WATCHDOG.md
|
+-- regulatory_archive/              FDA submission documents
+-- archive/                         Historical sessions & deprecated docs
    +-- REMINDER.txt                 (Pre-commit reminder message)
```

---

## How to Use This Folder

### Starting a New Session

1. **Read** `START_HERE.md` for quick orientation
2. **Follow** to `onboarding/NEW_SESSION_GUIDE.md` for complete setup
3. **Review** `active/PROJECT_STATUS.md` to understand current state
4. **Check** `active/WORK_LOG.md` for recent work
5. **Begin working** and update docs as you go

### During Development

**Every significant action:**
1. Update `active/WORK_LOG.md` with what you did
2. If milestone reached, update `active/PROJECT_STATUS.md`
3. Commit code changes to git
4. Pre-commit hook will remind you (but won't block)

**When planning:**
- Use `active/NEXT_STEPS.md` for roadmap
- Create session summaries in `active/sessions/`

**When stuck:**
- Check `reference/` for standards and policies
- Review `reviews/` for architectural guidance

### Ending a Session

1. Final update to `active/WORK_LOG.md`
2. Update `active/PROJECT_STATUS.md` if needed
3. Optional: Create session summary in `active/sessions/`

---

## File Update Frequency

| File | Update Frequency | Purpose |
|------|------------------|---------|
| `active/WORK_LOG.md` | After every significant action | Action tracking |
| `active/PROJECT_STATUS.md` | After major milestones | Complete state |
| `active/NEXT_STEPS.md` | When priorities change | Roadmap |
| `reference/*.md` | Rarely (only when policies change) | Stable reference |
| `reviews/*.md` | After code reviews | Quality tracking |
| `onboarding/*.md` | Rarely (only when process changes) | Session setup |

---

## Important Notes

### Git-Ignored

This entire folder is in `.gitignore` (line 117). **Nothing here will ever commit** to the public repository.

Verify with:
```bash
git ls-files | grep presubmit  # Should return nothing except .pre-commit-hooks/
```

### Public vs Private

**This folder (presubmit/):** Can contain:
- AI/Claude references
- FDA/medical device context
- Development methodology
- Internal planning
- Session tracking

**Public repo (git-tracked):** Cannot contain:
- Any AI tool references
- FDA/regulatory context
- Medical device designation
- Development methodology

See `reference/GIT_CONTENT_POLICY.md` for complete rules.

### Do Not Reference Publicly

Never mention this folder's existence or contents in:
- Public README.md
- Git-tracked documentation
- Code comments in src/
- Public architecture docs

---

## Pre-Commit Reminder System

Every git commit shows a reminder to update documentation:

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

This is generated by:
- `.pre-commit-config.yaml` (public, git-tracked)
- `.pre-commit-hooks/show-presubmit-reminder.py` (public, git-tracked)
- `REMINDER.txt` (this folder, gitignored)

See `reference/PRESUBMIT_SYSTEM.md` for details.

---

## Maintenance

### Regular Updates Needed
- `active/WORK_LOG.md` - Every session
- `active/PROJECT_STATUS.md` - After milestones
- `active/NEXT_STEPS.md` - When roadmap changes

### Periodic Cleanup
- Move old work logs to `archive/`
- Archive completed session summaries
- Update `reference/` docs when policies change

### Never Delete
- `onboarding/` guides (needed for future sessions)
- `reference/` policies (stable documents)
- `reviews/` findings (historical context)

---

## Related Public Files

These files ARE in the public repo and work with presubmit/:

- `.gitignore` - Line 117 ignores this folder
- `.pre-commit-config.yaml` - Configures reminder hook
- `.pre-commit-hooks/show-presubmit-reminder.py` - Displays reminder

They contain no session-specific information, just generic references to "presubmit" folder.

---

## Questions?

If you can't find something:
1. Check this README first
2. Look in `onboarding/` for setup guides
3. Check `reference/` for policies
4. Review `active/PROJECT_STATUS.md` for current context

---

**Last Updated:** 2025-10-25
**Location:** `presubmit/README.md`
**Status:** Living document (update as structure evolves)
