# Session Checkpoint System Guide

## Overview

The SESSION_STATE.md checkpoint system enables automatic session recovery, crash resilience, and seamless continuity across AI sessions.

**Purpose:**
- Resume work after unclean terminations (crashes, timeouts, network loss)
- Provide compact context for <30 second session startup
- Track project state without reading entire history
- Enable stateful AI development experience

**Location:** `presubmit/active/SESSION_STATE.md`

---

## Checkpoint Update Triggers

### Trigger Category 1: Phase Boundaries (CRITICAL - Always Checkpoint)

**When:** TodoWrite marks phase or major task complete

**Examples:**
- User completes "Phase 3.6: Commit and push"
- Major milestone reached ("UI Redesign Complete")
- Sprint/iteration boundary crossed

**Actions:**
1. Read current TodoWrite state
2. Capture git status (HEAD, branch, uncommitted files)
3. Extract "next recommended action" from PROJECT_STATUS.md
4. Write complete SESSION_STATE.md
5. Commit SESSION_STATE.md with descriptive message

**Trigger Condition:**
```python
if all_phase_tasks_complete():
    update_session_state(
        status="CLEAN",
        last_action="Completed Phase X",
        next_action="Begin Phase Y"
    )
```

---

### Trigger Category 2: Git Operations (HIGH PRIORITY - Checkpoint on Commit)

**When:** Git commit successfully created

**Actions:**
1. Capture new HEAD commit hash
2. Update "Last Action" with commit message summary
3. Mark associated todos as complete
4. Update SESSION_STATE.md
5. DO NOT commit SESSION_STATE immediately (wait for phase boundary)

**Rationale:** Git commits represent logical work units, ideal checkpoint moments

**Trigger Condition:**
```python
# After successful git commit
update_session_state(
    status="CLEAN",
    last_action=f"Committed: {commit_message[:50]}",
    commit_state=False  # Don't spam commits
)
```

---

### Trigger Category 3: Work Session Boundaries (MEDIUM - User-Triggered)

**When:** User signals session end

**Examples:**
- User types `/checkpoint` command
- Before user leaves (if they remember)
- After long coding session (user discretion)
- Before risky operation (manual safety checkpoint)

**Actions:**
1. Full state capture (git, todos, uncommitted files)
2. Prompt for "session summary" (optional)
3. Write SESSION_STATE.md
4. Commit with timestamp

**Trigger Condition:**
```bash
# User command
/checkpoint "Completed widget integration, ready for testing"
```

---

### Trigger Category 4: Error/Interruption Detection (AUTOMATIC - Safety Net)

**When:** Detecting potential termination signals

**Examples:**
- Long operations starting (>5 min estimated)
- Before risky git operations (rebase, merge)
- Periodic heartbeat (every 30 min during active work)

**Actions:**
1. Quick checkpoint (current state only)
2. Mark status as "IN_PROGRESS" with operation name
3. Update SESSION_STATE.md (in-memory, no commit)
4. If operation completes, update to "CLEAN"

**Rationale:** Safety net for crashes, timeouts, network loss

**Trigger Condition:**
```python
# Periodic safety net
if time_since_last_checkpoint() > 30_minutes:
    update_session_state(
        status="IN_PROGRESS",
        last_action="Automatic safety checkpoint",
        commit_state=False
    )
```

---

## Update Algorithm

### Function Signature

```python
def update_session_state(
    trigger: str,      # "phase_complete" | "git_commit" | "user_checkpoint" | "auto_safety"
    status: str,       # "CLEAN" | "IN_PROGRESS" | "INTERRUPTED"
    last_action: str,  # Human-readable description
    next_action: str = None,  # Recommended next step (optional, inferred if None)
    commit_state: bool = True # Whether to git commit SESSION_STATE.md
) -> None:
    """
    Update SESSION_STATE.md with current context.

    Args:
        trigger: What caused this update
        status: Current work state
        last_action: What was just completed
        next_action: What to do next (inferred from PROJECT_STATUS if None)
        commit_state: Whether to commit the file (default True for CLEAN status)
    """
```

### Step-by-Step Process

**Step 1: Gather Current State**
```python
# Get git information
git_info = {
    'head': git rev-parse HEAD,
    'branch': git branch --show-current,
    'unstaged': git diff --name-only,
    'staged': git diff --cached --name-only
}

# Get todo state (from last TodoWrite call)
todos = [current todo list with statuses]

# Generate metadata
timestamp = current UTC timestamp
session_id = f"{YYYY-MM-DD-HHMM}"
```

**Step 2: Infer Next Action (if not provided)**
```python
if next_action is None:
    if status == "CLEAN":
        # Read PROJECT_STATUS.md to find next phase
        next_action = infer_from_project_status()
    elif status == "IN_PROGRESS":
        next_action = f"Complete {last_action}"
    else:
        next_action = "Review uncommitted changes and decide next step"
```

**Step 3: Extract Recent Context**
```python
# Get recent decisions (from WORK_LOG.md or memory)
recent_decisions = extract_last_5_decisions()

# Get recent commits
recent_commits = git log -5 --format="%h: %s"

# Check for known issues/blockers
known_issues = check_for_active_blockers()
```

**Step 4: Build SESSION_STATE Content**
```python
content = f"""# SESSION_STATE.md

## Session Metadata
- Session ID: {session_id}
- Timestamp: {timestamp}
- Git HEAD: {git_info.head[:7]}
- Current Branch: {git_info.branch}
- Status: {status}

## Current Context
Phase: {get_current_phase()}
Sprint: {get_current_sprint()}
Last Action: {last_action}

## Active Work
Todos (from TodoWrite):
{format_todos(todos)}

Unstaged Changes: {format_files(git_info.unstaged) or "NONE"}
Staged Changes: {format_files(git_info.staged) or "NONE"}

## Next Recommended Action
{next_action}

## Recent Decisions
{format_decisions(recent_decisions)}

## Recent Commits (Last 5)
{format_commits(recent_commits)}

## Known Issues
{format_issues(known_issues) or "NONE"}

---

**Last Updated:** {timestamp}
**Session Status:** {status}
"""
```

**Step 5: Write File**
```python
write_file("presubmit/active/SESSION_STATE.md", content)
```

**Step 6: Commit (if requested)**
```python
if commit_state and status == "CLEAN":
    git add presubmit/active/SESSION_STATE.md
    git commit -m f"chore: Update session state - {last_action}"
```

---

## Checkpoint Frequency Guidelines

### TOO FREQUENT (Avoid)
- After every file edit → Excessive overhead
- After every `git add` → Too granular
- Every 5 minutes → Commit spam
- **Problem:** Clutters git history, wastes time

### TOO RARE (Avoid)
- Only on user request → Forgets to checkpoint
- Only at phase boundaries → Lose in-progress work
- Never automatic → No crash recovery
- **Problem:** Work lost on unclean termination

### OPTIMAL (Recommended)
- **Phase boundaries:** Always (critical work milestones)
- **Git commits:** High value (logical completion points)
- **User request:** Manual safety (/checkpoint command)
- **30-min background:** Safety net (automatic)
- **Result:** 2-4 checkpoints per typical work session

---

## Session Recovery Workflow

### Step 1: Session Start Detection

```python
if SESSION_STATE.md exists:
    mode = "RESUME"
else:
    mode = "FRESH_START"
```

### Step 2: Resume Mode Logic

```python
if mode == "RESUME":
    state = read_session_state()
    current_head = git rev-parse HEAD

    if current_head == state.head:
        # Clean resume
        print(f"Resuming from {state.last_action}")
        print(f"Next: {state.next_action}")
        restore_todos(state.todos)

    elif has_uncommitted_changes():
        # Partial resume (interrupted work)
        print("⚠️ Uncommitted work detected")
        print(f"Files: {list_unstaged_files()}")
        offer_resume_options()

    else:
        # External git activity
        print("Git history advanced since last session")
        list_new_commits()
        ask("Review recent commits? [Y/n]")
        update_session_state(...)
```

### Step 3: Fresh Start Logic

```python
if mode == "FRESH_START":
    read_onboarding_md()
    read_project_status()
    infer_next_action()
    create_initial_session_state()
```

---

## Usage Examples

### Example 1: Phase Completion
```
User completes Phase 3 tasks
→ AI marks all todos complete via TodoWrite
→ Trigger: Phase boundary detected
→ Action: Capture state, write SESSION_STATE, commit
→ Result: Clean checkpoint at phase boundary
```

### Example 2: Mid-Work Crash
```
AI crashes while writing code (no commit yet)
→ SESSION_STATE shows status="IN_PROGRESS"
→ Next session: Read SESSION_STATE
→ Detect uncommitted files
→ Offer: "Resume Phase 4 integration? [Y/n]"
→ Continue from last checkpoint
```

### Example 3: User Manual Checkpoint
```
User types: /checkpoint "Finished testing, ready to commit"
→ Trigger: User-initiated checkpoint
→ Capture full state
→ Write SESSION_STATE with user's message
→ Commit: "chore: Checkpoint - Finished testing, ready to commit"
→ Result: Safe snapshot before important operation
```

### Example 4: Automatic Safety Net
```
30 minutes pass since last checkpoint
→ Trigger: Time-based safety checkpoint
→ Quick state capture (don't commit)
→ Mark status="IN_PROGRESS"
→ If crash: Most recent state available
→ If normal exit: Clean checkpoint at phase boundary
```

---

## Best Practices

### DO:
- ✅ Checkpoint after phase completions
- ✅ Update SESSION_STATE after commits
- ✅ Use /checkpoint before risky operations
- ✅ Keep status accurate (CLEAN vs IN_PROGRESS)
- ✅ Commit checkpoints at natural boundaries

### DON'T:
- ❌ Checkpoint after every file edit
- ❌ Commit SESSION_STATE mid-operation
- ❌ Forget to update after major milestones
- ❌ Leave stale status information
- ❌ Checkpoint too frequently (spam)

---

## Integration with TodoWrite

SESSION_STATE syncs automatically with TodoWrite:

**TodoWrite → SESSION_STATE:**
- When TodoWrite updates, SESSION_STATE captures current todos
- Phase completion triggers checkpoint
- Todo status preserved across sessions

**SESSION_STATE → TodoWrite:**
- On session resume, TodoWrite state restored from SESSION_STATE
- Todos continue from last known state
- No manual todo management required

---

## Troubleshooting

### Problem: SESSION_STATE not updating
**Cause:** No checkpoint triggers firing
**Solution:** Use `/checkpoint` command manually, or wait for natural trigger (commit, phase completion)

### Problem: Stale checkpoint (days old)
**Cause:** Long time between sessions
**Solution:** Session resume detects staleness, shows git history since checkpoint, updates automatically

### Problem: Corrupted SESSION_STATE
**Cause:** File edit error, git conflict
**Solution:** Recovery mode rebuilds from git log + PROJECT_STATUS + current git status

### Problem: Too many commits
**Cause:** Committing SESSION_STATE too frequently
**Solution:** Set `commit_state=False` for mid-phase updates, only commit at phase boundaries

---

**Document Status:** ACTIVE
**Last Updated:** 2025-10-28
**Related Files:**
- presubmit/active/SESSION_STATE.md (checkpoint file)
- presubmit/ONBOARDING.md (uses SESSION_STATE for resume)
- .claude/commands/checkpoint.md (manual checkpoint command)
