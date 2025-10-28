# TOSCA Laser Control System - AI Onboarding

> **Session Detection:** [Check for presubmit/active/SESSION_STATE.md]
> - If EXISTS → **RESUMING MODE**
> - If NOT EXISTS → **FRESH START MODE**

---

## 🚀 Quick Start (30 seconds)

### Session Status Check [AUTOMATED]

**If RESUMING:**
1. Read `presubmit/active/SESSION_STATE.md`
2. Verify git status matches checkpoint
3. Load active todos from session state
4. Check for uncommitted changes or conflicts

**If FRESH START:**
1. Read this document (ONBOARDING.md)
2. Read `PROJECT_STATUS.md` for current phase
3. Check git status for recent activity
4. Create initial SESSION_STATE.md

### What You Need to Know RIGHT NOW

**[RESUMING MODE]**
- ✅ Last session: [timestamp from SESSION_STATE]
- 📋 Active todos: [X/Y complete]
- 🎯 Next action: [from SESSION_STATE.next_action]
- ⚠️ Uncommitted work: [from git status]
- 📍 Current phase: [from SESSION_STATE.phase]

**[FRESH START MODE]**
- 📍 Current milestone: UI/UX Redesign (Phase 3 Complete)
- 🏗️ Project at: Version 0.9.5-alpha
- 📊 Recent activity: Phase 3 completion (protocol selector, manual overrides)
- 🎯 Recommended focus: Begin Phase 4 (Integration & Validation)

---

## 📚 Essential Context (2 minutes)

### Project Overview (30 seconds)

**What:** Medical device laser control system (FDA/HIPAA compliant)
- Safety-critical medical device software
- PyQt6 GUI for treatment laser control
- Multi-interlock safety system with hardware watchdog
- Automated protocol execution engine

**Tech Stack:**
- **Language:** Python 3.12 (type hints mandatory)
- **GUI:** PyQt6 with asyncio integration
- **Database:** SQLite (sessions, events, subjects)
- **Hardware:** Serial (Arduino GPIO), USB (laser/actuator)
- **Safety:** Multi-layer interlocks, E-Stop, selective shutdown

**Architecture:** Layered design
- **UI Layer:** PyQt6 widgets (src/ui/)
- **Core Layer:** Protocol engine, safety manager (src/core/)
- **HAL Layer:** Hardware abstraction (src/hardware/)
- **Hardware Layer:** Laser, actuator, GPIO, camera

**Safety Philosophy:**
- All hardware operations validated by safety manager
- Emergency stop accessible from any UI state
- Laser enable requires multiple interlocks satisfied
- Treatment laser shutdown on safety violations (selective policy)

### Current State (30 seconds)

**Version:** 0.9.5-alpha
**Active Phase:** UI/UX Redesign (Phases 1-3 Complete)
**Recent Completions:**
- ✅ Phase 1: Global toolbar, master safety indicator
- ✅ Phase 2: Treatment Dashboard with QStackedWidget
- ✅ Phase 3: Protocol selector, manual overrides

**Upcoming Work:** Phase 4 (Integration & Validation)
- Integrate ProtocolSelectorWidget into Treatment Setup
- Add ManualOverrideWidget to System Diagnostics tab
- Wire signals for protocol loading workflow
- Test complete treatment workflow

**Key Metrics:**
- Lines of Code: ~15,000
- Test Coverage: 80% average
- Recent Commits (Oct 2025): 25+
- Open Milestones: 2 (Clinical Testing, Regulatory Docs)

### Critical Policies (1 minute)

**Git Content Policy:** (Full doc: `presubmit/reference/GIT_CONTENT_POLICY.md`)
- **Atomic commits:** One logical change per commit
- **Descriptive messages:** "feat/fix/docs: What and why"
- **Update docs:** WORK_LOG and PROJECT_STATUS with code changes
- **Archive completed work:** Move to presubmit/archive/ with timestamps
- **No secrets:** Never commit .env, credentials, API keys

**Coding Standards:** (Full doc: `presubmit/reference/CODING_STANDARDS.md`)
- **Type hints mandatory:** All function signatures, public APIs
- **Docstrings required:** Public classes, methods, complex functions
- **Pre-commit hooks:** Black (format), isort (imports), flake8 (lint), mypy (types)
- **Safety-critical validation:** Extra review for hardware control code
- **Test coverage:** Aim for 80%+, mandatory for safety-critical

**Known Issues:**
- MyPy path resolution: Use `--no-verify` after manual validation
  * Not blocking: Code quality validated, tooling config issue only

---

## 🎯 Where to Find Things

### Active Work (Read These)
- **SESSION_STATE.md** → `presubmit/active/SESSION_STATE.md`
  * Current session checkpoint (git state, todos, next action)
  * Updated after phase boundaries, commits, checkpoints

- **PROJECT_STATUS.md** → `PROJECT_STATUS.md` (root directory)
  * Milestones, phase tracking, progress metrics
  * High-level project overview

- **WORK_LOG.md** → `WORK_LOG.md` (root directory)
  * Detailed action history (last 14 days)
  * Technical implementation details

### Reference Docs (Read On-Demand)
- **Git Policy** → `presubmit/reference/GIT_CONTENT_POLICY.md`
- **Coding Standards** → `presubmit/reference/CODING_STANDARDS.md`
- **Checkpoint Guide** → `presubmit/reference/SESSION_CHECKPOINT_GUIDE.md`
- **UI Redesign Plan** → `docs/UI_REDESIGN_PLAN.md`
- **Architecture Docs** → `docs/architecture/`

### Archives (Search When Needed)
- **HISTORY.md** → `HISTORY.md` (root directory)
  * Compressed monthly summaries (15-60 days old)

- **Archive Index** → `presubmit/archive/INDEX.md`
  * Keyword search, date-based lookup

- **Monthly Archives** → `presubmit/archive/YYYY-MM_summary.md`
  * Historical milestones (60+ days old)

---

## 🔄 Session Recovery [IF RESUMING]

### Automatic Recovery Process

**Step 1: Read Session State**
```bash
Read: presubmit/active/SESSION_STATE.md
Extract: session_id, timestamp, git_head, status, todos, next_action
```

**Step 2: Verify Git State**
```bash
Current HEAD: $(git rev-parse HEAD)
Expected HEAD: [from SESSION_STATE]
Match status: [CLEAN | DIRTY | DIVERGED]
```

**Step 3: Handle State Scenarios**

**Scenario A: CLEAN RESUME (HEAD matches, no uncommitted files)**
```
✅ Session state restored
✅ Context loaded from SESSION_STATE
✅ Ready to proceed with: [next_action]

Active todos:
[formatted todo list from SESSION_STATE]

Resume immediately with recommended action.
```

**Scenario B: UNCOMMITTED WORK (HEAD matches, but uncommitted files)**
```
⚠️ Uncommitted work detected since last checkpoint

Files changed:
[list from git status]

Options:
1. Review changes and commit
2. Continue work in progress
3. Stash changes and start fresh

Recommend: Review changes first
```

**Scenario C: DIVERGED (HEAD doesn't match)**
```
📊 Git history advanced since last session

New commits since checkpoint:
[git log SESSION_HEAD..HEAD]

Session checkpoint: [SESSION_HEAD] ([timestamp])
Current HEAD: [CURRENT_HEAD]

Action: Update SESSION_STATE with current HEAD and continue
```

**Scenario D: CONFLICTS (Git merge/rebase in progress)**
```
⚠️ Git conflicts detected

Repository in MERGING/REBASING state
Conflicted files: [list]

⛔ Cannot proceed until conflicts resolved

Action: Resolve conflicts, then resume session
```

### Recovery Actions [AUTOMATED]

```python
# AI performs these automatically
1. Read SESSION_STATE.md
2. Compare git HEAD
3. Check for uncommitted files
4. Identify scenario (A/B/C/D)
5. Present appropriate status message
6. Load todos from session state
7. Set next action from session state
8. Ready to work (<30 seconds)
```

---

## 📋 TodoWrite Integration

### Automatic Todo Restoration

**From SESSION_STATE:**
```markdown
## Active Work
Todos (from TodoWrite):
- [✅] Completed task 1
- [🔄] In-progress task 2
- [⏳] Pending task 3
```

**AI Action:** Restore todo list automatically
- Read todos from SESSION_STATE
- Restore statuses (completed/in_progress/pending)
- Continue tracking from last checkpoint
- No manual todo management required

### Checkpoint Synchronization

**TodoWrite → SESSION_STATE:**
- When TodoWrite updates, checkpoint triggered (if phase boundary)
- Todos saved to SESSION_STATE automatically
- Session state always reflects current todos

**SESSION_STATE → TodoWrite:**
- On resume, TodoWrite state loaded from SESSION_STATE
- Todos continue from last known state
- Seamless continuation across sessions

---

## ⚡ Common Operations

### Check Current Status
```
1. Read SESSION_STATE.md (if exists)
2. Run: git status
3. Check PROJECT_STATUS.md for current phase
```

### Start New Work
```
1. Identify next task from SESSION_STATE or PROJECT_STATUS
2. Create TodoWrite plan if complex (3+ steps)
3. Begin implementation
4. Update SESSION_STATE at milestones
```

### Manual Checkpoint
```
Command: /checkpoint [optional message]
Creates safety snapshot before risky operations
```

### Commit Changes
```
1. Stage files: git add [files]
2. Commit: git commit -m "type: description"
3. Automatic: SESSION_STATE updated with commit
```

### End Session
```
1. Commit all work (no uncommitted files)
2. SESSION_STATE automatically updated
3. Next session will resume cleanly
```

---

## 🆘 Troubleshooting

### Problem: SESSION_STATE Missing
**Cause:** First session or file deleted
**Solution:** Fresh start mode - read this document, create initial SESSION_STATE

### Problem: SESSION_STATE Corrupted
**Cause:** File edit error, git conflict
**Solution:** Recovery mode - rebuild from git log + PROJECT_STATUS

**Recovery Steps:**
1. Read PROJECT_STATUS.md for current phase
2. Run: git log -10 --oneline (recent commits)
3. Run: git status (current state)
4. Create fresh SESSION_STATE from available info

### Problem: Git Conflicts Detected
**Cause:** Merge/rebase in progress
**Solution:** Resolve conflicts before resuming

**Steps:**
1. List conflicts: git status
2. Open conflicted files
3. Resolve conflicts (keep/remove markers)
4. Stage resolved: git add [files]
5. Complete: git commit or git rebase --continue
6. Then resume normal workflow

### Problem: Uncommitted Changes from Previous Session
**Cause:** Session ended without committing
**Solution:** Review changes and decide

**Options:**
1. **Commit:** If work is complete
   ```bash
   git add .
   git commit -m "Resume from interrupted session"
   ```

2. **Continue:** If work in progress
   ```bash
   Continue editing, commit when ready
   ```

3. **Discard:** If changes unwanted
   ```bash
   git restore [files]  # Discard changes
   ```

### Problem: Stale Checkpoint (7+ days old)
**Cause:** Long time between sessions
**Solution:** Automatic catch-up summary

**AI Action:**
1. Detect staleness (timestamp >7 days)
2. Show: "Last session: [X] days ago"
3. List commits since then: git log
4. Read HISTORY.md for summary
5. Ask: "Review WORK_LOG for details? [y/N]"
6. Update SESSION_STATE with current state

### Problem: Context Not Sufficient
**Cause:** Need more background than Quick Start provides
**Solution:** Read additional documentation

**Suggested Reading Order:**
1. WORK_LOG.md (recent 14 days detailed)
2. HISTORY.md (monthly summaries)
3. PROJECT_STATUS.md (full milestone history)
4. Architecture docs (if needed)

---

## 📖 Additional Resources

### Documentation Structure

```
TOSCA-dev/
├── presubmit/
│   ├── ONBOARDING.md ← YOU ARE HERE (start here)
│   ├── active/
│   │   ├── SESSION_STATE.md (current checkpoint)
│   │   └── DECISIONS.md (architecture choices)
│   ├── reference/
│   │   ├── GIT_CONTENT_POLICY.md (git workflow)
│   │   ├── CODING_STANDARDS.md (code quality)
│   │   └── SESSION_CHECKPOINT_GUIDE.md (checkpoint system)
│   └── archive/
│       ├── INDEX.md (searchable keyword index)
│       └── YYYY-MM_summary.md (historical archives)
├── PROJECT_STATUS.md (milestones, phases, metrics)
├── WORK_LOG.md (detailed recent history)
└── HISTORY.md (compressed monthly summaries)
```

### Slash Commands Available

- **/checkpoint** - Create manual session checkpoint
- **/todo** - Manage todo list
- **/commit** - Guided git commit with validation
- **/code-review** - Comprehensive code review
- **/update-docs** - Update documentation systematically

### Getting Help

**If confused about:**
- **What to work on:** Read SESSION_STATE.next_action or PROJECT_STATUS.md
- **How system works:** Read architecture docs in docs/
- **Git workflow:** Read presubmit/reference/GIT_CONTENT_POLICY.md
- **Code standards:** Read presubmit/reference/CODING_STANDARDS.md
- **Session system:** Read presubmit/reference/SESSION_CHECKPOINT_GUIDE.md

---

## ✅ Onboarding Complete

**You are now ready to work!**

**Next Steps:**
1. If RESUMING: Continue with [next_action from SESSION_STATE]
2. If FRESH START: Begin with [current phase from PROJECT_STATUS]

**Session State:** [CLEAN | IN_PROGRESS | INTERRUPTED]
**Ready to Work:** ✅

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-28
**Purpose:** Single entry point for AI onboarding and session continuity
**Target Reading Time:** 2.5 minutes (Quick Start: 30s, Essential Context: 2min)
