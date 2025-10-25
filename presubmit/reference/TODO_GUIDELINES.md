# TodoWrite Guidelines - Detailed Reference

**Last Updated:** 2025-10-25
**Purpose:** Comprehensive guide to using TodoWrite tool effectively
**Enforcement Level:** Recommended (not required)

---

## Document Structure

1. [Overview](#overview)
2. [When to Use TodoWrite](#when-to-use-todowrite)
3. [When to Skip TodoWrite](#when-to-skip-todowrite)
4. [Todo Lifecycle](#todo-lifecycle)
5. [Examples](#examples)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Integration with Documentation](#integration-with-documentation)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**What is TodoWrite?**
- Tool for tracking multi-step tasks within a single session
- Provides transparency to user on current progress
- Helps AI stay organized and focused
- Complements (doesn't replace) WORK_LOG.md

**Key Principles:**
- Use for complex tasks, skip for simple ones
- One todo `in_progress` at a time
- Mark `completed` immediately after finishing
- Update descriptions if approach changes

---

## When to Use TodoWrite

### Automatic: Always Create Todos

**1. Multi-step features (3+ distinct steps)**
```
User: "Add laser safety interlocks with hardware checks and GUI display"

Todos created:
1. Implement safety check logic in SafetyManager
2. Add GPIO hardware integration for interlocks
3. Create safety status display widget
4. Integrate with laser enable button
5. Test with hardware
```

**Why:** Breaking down into steps shows progress and prevents missing pieces.

**2. User provides explicit list**
```
User: "Please do the following:
1. Fix camera frame rate bug
2. Update documentation
3. Run tests and commit"

Todos created:
1. Fix camera frame rate bug in camera_controller.py
2. Update WORK_LOG.md and PROJECT_STATUS.md
3. Run pre-commit tests and create git commit
```

**Why:** User expects each item to be tracked individually.

**3. Complex investigation/debugging**
```
User: "The actuator is moving to wrong positions, figure out why"

Todos created:
1. Review actuator command logs
2. Check position calculation logic
3. Test with known positions
4. Identify root cause
5. Implement fix
6. Verify with hardware
```

**Why:** Investigation work benefits from structured approach and progress visibility.

**4. Code review or comprehensive analysis**
```
User: "Review the safety system code for issues"

Todos created:
1. Analyze SafetyManager architecture
2. Check interlock implementation
3. Review error handling
4. Verify logging completeness
5. Generate findings report
```

**Why:** Systematic review requires tracking multiple areas.

**5. Multiple independent tasks**
```
User: "Update all HAL modules to use new error handling pattern"

Todos created:
1. Update CameraController error handling
2. Update LaserController error handling
3. Update ActuatorController error handling
4. Update GPIOController error handling
5. Test all modules
```

**Why:** Tracking prevents missing modules.

---

## When to Skip TodoWrite

### Skip: Simple/Trivial Tasks

**1. Single file, single change**
```
User: "Add a docstring to the laser_enable function"

No todos needed - straightforward one-step task.
```

**2. Reading/exploring code**
```
User: "Show me how the camera streaming works"

No todos needed - information gathering, no implementation.
```

**3. Answering questions**
```
User: "What's the current project status?"

No todos needed - conversational response.
```

**4. Quick fixes (1-2 steps)**
```
User: "Fix the typo in README.md"

No todos needed - trivial change.
```

**5. Documentation-only tasks**
```
User: "Update the WORK_LOG with what we just did"

No todos needed - single documentation update.
```

---

## Todo Lifecycle

### Phase 1: Planning (Before Starting Work)

**Step 1: Analyze the request**
- What are the distinct steps?
- What's the logical order?
- Are there dependencies?

**Step 2: Create todo list**
```python
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "pending", "activeForm": "Doing step 1"},
    {"content": "Step 2 description", "status": "pending", "activeForm": "Doing step 2"},
    {"content": "Step 3 description", "status": "pending", "activeForm": "Doing step 3"}
])
```

**Step 3: Start first todo**
```python
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "in_progress", "activeForm": "Doing step 1"},
    {"content": "Step 2 description", "status": "pending", "activeForm": "Doing step 2"},
    {"content": "Step 3 description", "status": "pending", "activeForm": "Doing step 3"}
])
```

### Phase 2: Execution (During Work)

**When finishing current step:**
```python
# Mark current step completed
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "completed", "activeForm": "Doing step 1"},
    {"content": "Step 2 description", "status": "in_progress", "activeForm": "Doing step 2"},
    {"content": "Step 3 description", "status": "pending", "activeForm": "Doing step 3"}
])
```

**If work scope expands:**
```python
# Add new todos discovered during work
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "completed", "activeForm": "Doing step 1"},
    {"content": "Step 2 description", "status": "completed", "activeForm": "Doing step 2"},
    {"content": "Step 2.5 - Additional work needed", "status": "in_progress", "activeForm": "Doing step 2.5"},
    {"content": "Step 3 description", "status": "pending", "activeForm": "Doing step 3"}
])
```

**If approach changes:**
```python
# Update description to match reality
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "completed", "activeForm": "Doing step 1"},
    {"content": "Step 2 - Changed approach to use hardware API instead", "status": "completed", "activeForm": "Doing step 2"},
    {"content": "Step 3 description", "status": "in_progress", "activeForm": "Doing step 3"}
])
```

### Phase 3: Completion (After Finishing)

**All work complete:**
```python
# All todos completed
TodoWrite(todos=[
    {"content": "Step 1 description", "status": "completed", "activeForm": "Doing step 1"},
    {"content": "Step 2 description", "status": "completed", "activeForm": "Doing step 2"},
    {"content": "Step 3 description", "status": "completed", "activeForm": "Doing step 3"}
])
```

**Clean up if needed:**
- Remove todos that became irrelevant
- Ensure descriptions match what was actually done
- No todos stuck in `in_progress`

---

## Examples

### Example 1: Feature Implementation

**User Request:**
> "Implement laser power ramping feature with configurable rate and GUI controls"

**Todo Breakdown:**
```
1. Add power ramping logic to LaserController
2. Create GUI controls in LaserWidget (rate slider, start/stop buttons)
3. Connect GUI to controller with signals
4. Test ramping with different rates
5. Update WORK_LOG.md with implementation details
```

**Why this works:**
- Clear steps with distinct deliverables
- Logical order (backend → frontend → integration → testing)
- Each step is testable independently

### Example 2: Bug Investigation

**User Request:**
> "The camera sometimes drops frames, find out why"

**Todo Breakdown:**
```
1. Review camera logs for dropped frame events
2. Check frame rate settings vs hardware capabilities
3. Monitor CPU usage during streaming
4. Test with different frame rates
5. Identify root cause (hardware limit vs software throttling)
6. Implement fix based on findings
7. Verify fix with extended testing
```

**Why this works:**
- Systematic investigation approach
- Each step builds on previous findings
- Clear completion criteria for each step

### Example 3: Code Review

**User Request:**
> "Review the protocol engine code for potential issues"

**Todo Breakdown:**
```
1. Review ProtocolEngine architecture and design patterns
2. Analyze error handling and edge cases
3. Check safety integration and validation
4. Review database interactions
5. Check for TODO comments and incomplete implementations
6. Generate findings document with recommendations
```

**Why this works:**
- Covers different aspects methodically
- Ensures comprehensive review
- Final deliverable (findings document)

### Example 4: Multi-Module Update

**User Request:**
> "Add error logging to all hardware controllers"

**Todo Breakdown:**
```
1. Add error logging to CameraController
2. Add error logging to LaserController
3. Add error logging to ActuatorController
4. Add error logging to GPIOController
5. Test error logging in each module
6. Update documentation with logging details
```

**Why this works:**
- Parallel tasks that can be tracked independently
- Easy to see progress (3 of 6 complete)
- Prevents missing a module

---

## Best Practices

### Naming Conventions

**Good Content (imperative form):**
```
✓ "Implement camera frame streaming"
✓ "Add safety checks to laser enable"
✓ "Update PROJECT_STATUS.md with Phase 2"
✓ "Fix actuator position calculation bug"
✓ "Run integration tests and verify"
```

**Poor Content:**
```
✗ "Camera stuff" (too vague)
✗ "Make it work" (not specific)
✗ "The laser thing we talked about" (no context)
✗ "TODO" (not descriptive)
```

**Good ActiveForm (present continuous):**
```
✓ "Implementing camera frame streaming"
✓ "Adding safety checks"
✓ "Updating PROJECT_STATUS.md"
✓ "Fixing actuator bug"
✓ "Running integration tests"
```

**Poor ActiveForm:**
```
✗ "Camera" (not a verb phrase)
✗ "Laser work" (too vague)
✗ "Implement camera frame streaming" (should be present continuous)
```

### Granularity Guidelines

**Too granular (over-splitting):**
```
✗ 1. Open camera_controller.py
✗ 2. Find the streaming function
✗ 3. Add error handling line 45
✗ 4. Add error handling line 67
✗ 5. Save file
```

**Good granularity:**
```
✓ 1. Add error handling to camera streaming functions
✓ 2. Test error scenarios
✓ 3. Update documentation
```

**Too coarse (under-splitting):**
```
✗ 1. Implement entire camera module with all features
```

**Good granularity:**
```
✓ 1. Implement basic camera connection
✓ 2. Add frame streaming capability
✓ 3. Add exposure/gain controls
✓ 4. Create camera GUI widget
✓ 5. Test with hardware
```

### Timing Guidelines

**Mark completed IMMEDIATELY:**
```
Good flow:
1. Finish implementing feature
2. Mark todo as completed ← Do this right away
3. Start next todo

Bad flow:
1. Finish implementing feature A
2. Implement feature B
3. Implement feature C
4. Mark all three completed ← Too late!
```

**Why:** User sees real-time progress, not batch updates at end.

### State Management

**CRITICAL RULE: Only ONE todo `in_progress` at a time**

**Good:**
```
1. [completed] Implement camera HAL
2. [in_progress] Implement laser HAL  ← Currently working
3. [pending] Implement actuator HAL
4. [pending] Implement GPIO HAL
```

**Bad:**
```
1. [completed] Implement camera HAL
2. [in_progress] Implement laser HAL    ← Two in progress!
3. [in_progress] Implement actuator HAL ← Confusing!
4. [pending] Implement GPIO HAL
```

---

## Common Patterns

### Pattern 1: Sequential Implementation

**Use for:** Features with dependencies

```
1. Design data model
2. Implement backend logic
3. Create database schema
4. Build GUI components
5. Connect GUI to backend
6. Test end-to-end
```

### Pattern 2: Parallel Tasks

**Use for:** Independent modules

```
1. Update CameraController
2. Update LaserController
3. Update ActuatorController
4. Update GPIOController
5. Integration testing
```

### Pattern 3: Investigation + Fix

**Use for:** Bug fixing

```
1. Reproduce the bug
2. Add logging to narrow down issue
3. Identify root cause
4. Implement fix
5. Verify fix resolves issue
6. Add regression test
```

### Pattern 4: Review + Improve

**Use for:** Code quality work

```
1. Analyze current implementation
2. Identify improvement opportunities
3. Create improvement plan
4. Implement improvements
5. Verify improvements work
6. Update documentation
```

### Pattern 5: Plan + Execute + Document

**Use for:** Major features

```
1. Research and plan approach
2. Implement core functionality
3. Add error handling
4. Create tests
5. Update documentation
6. Update PROJECT_STATUS.md
```

---

## Integration with Documentation

### TodoWrite vs WORK_LOG.md

| Aspect | TodoWrite | WORK_LOG.md |
|--------|-----------|-------------|
| **Purpose** | Track current session | Permanent record |
| **Audience** | User + current AI | Future AI sessions |
| **Timing** | Real-time during work | After actions complete |
| **Lifecycle** | Session-only | Permanent |
| **Format** | Structured list | Narrative entries |
| **Visibility** | UI todo list | Markdown file |

### When to Update Both

**During a session:**
1. Create todos at start
2. Update todos in real-time
3. After completing significant action → Update WORK_LOG.md
4. Mark todo completed
5. Continue to next todo

**Example flow:**
```
[10:00] Create todos for laser HAL implementation
[10:05] Mark "Design laser controller class" as in_progress
[10:30] Complete design
[10:31] Update WORK_LOG.md: "Designed LaserController class..."
[10:32] Mark design todo as completed
[10:33] Mark "Implement laser controller" as in_progress
... continue ...
```

### TodoWrite vs PROJECT_STATUS.md

**Todos:** Granular steps within a feature
**PROJECT_STATUS.md:** High-level module completion

**Example:**
```
Todos for Laser HAL:
1. [completed] Design LaserController class
2. [completed] Implement serial communication
3. [completed] Add PyQt6 signal integration
4. [completed] Create LaserWidget GUI
5. [completed] Test with hardware

When all todos completed:
→ Update PROJECT_STATUS.md: "Laser Controller HAL: COMPLETE (100%)"
```

---

## Troubleshooting

### Problem: Todos becoming stale

**Symptoms:**
- Todos don't match actual work
- Many todos stuck in `in_progress`
- User confused about real progress

**Solutions:**
1. Update todos when approach changes
2. Mark completed immediately
3. Remove irrelevant todos
4. Add new todos if work expands

### Problem: Too many todos

**Symptoms:**
- 10+ todos for simple task
- User overwhelmed
- Hard to track progress

**Solutions:**
1. Combine related steps
2. Use higher-level descriptions
3. Skip todos if task became simple

### Problem: Too few todos

**Symptoms:**
- One vague todo for complex work
- User can't see progress
- Work seems to take forever

**Solutions:**
1. Break down into logical steps
2. Aim for 3-7 todos for complex tasks
3. Each todo should be completable in reasonable time

### Problem: Todos not being updated

**Symptoms:**
- All todos stay `pending` throughout work
- Updates come in batch at end
- User doesn't see real-time progress

**Solutions:**
1. Mark `in_progress` before starting step
2. Mark `completed` immediately after finishing
3. Don't batch updates

---

## Quick Reference

### TodoWrite Decision Tree

```
Is the task complex (3+ steps)?
├─ YES → Create todos
│   ├─ Break into logical steps
│   ├─ Use clear descriptions
│   └─ Update in real-time
│
└─ NO → Skip todos
    ├─ Is it a single file change?
    ├─ Is it reading/exploring?
    ├─ Is it answering a question?
    └─ If any YES → No todos needed
```

### State Transition Rules

```
pending → in_progress: When starting work
in_progress → completed: When finishing work
pending → removed: If no longer relevant
(Never: completed → in_progress)
```

### Checklist After Using Todos

- [ ] All work reflected in todo list
- [ ] Only one or zero todos `in_progress`
- [ ] Completed todos match what was done
- [ ] No stale or irrelevant todos
- [ ] WORK_LOG.md also updated

---

## Related Documentation

**Core Reference:**
- `presubmit/reference/CODING_STANDARDS.md` - TodoWrite section
- `presubmit/README.md` - File update frequency

**Workflow:**
- `presubmit/active/WORK_LOG.md` - Permanent action log
- `presubmit/active/PROJECT_STATUS.md` - Overall project state

**MCP Memory:**
- "Development Workflow" entity - Contains todo workflow

---

**Last Updated:** 2025-10-25
**Location:** presubmit/reference/TODO_GUIDELINES.md
**Status:** Active guidelines for todo usage
