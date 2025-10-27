# TOSCA Coding Standards

**Project:** FDA-Enhanced Documentation Level Medical Device Software
**Principle:** Minimal, Precise, Safety-Critical Code Only

## Core Principles

1. **Write only what is required** - No speculative features, no helper functions "just in case"
2. **No decorative elements** - No emojis, no ASCII art, no flourishes
3. **Documentation is functional** - Comments explain WHY, not WHAT. Code should be self-documenting.
4. **Every line must have a purpose** - If it doesn't contribute to functionality or safety, remove it

## ⚠️ HARDWARE API USAGE - CRITICAL RULE ⚠️

**ALWAYS use native hardware API capabilities before implementing software workarounds.**

### Rule

When working with hardware devices (cameras, actuators, sensors):

1. **FIRST**: Research what the hardware API provides natively
2. **SECOND**: Implement using native hardware features
3. **LAST RESORT**: Only implement software workarounds if hardware doesn't support the feature

### Rationale

- Hardware-level features are more reliable, efficient, and precise
- Software workarounds add complexity, introduce timing jitter, and waste CPU
- Hardware APIs are tested by manufacturers and designed for the use case
- Software workarounds can mask underlying hardware capabilities

### Examples

#### ✅ CORRECT: Use Hardware API

```python
# Camera frame rate control - use hardware feature
def start_streaming(self) -> bool:
    # Set camera acquisition frame rate at hardware level
    self.set_acquisition_frame_rate(30.0)
    self.camera.start_streaming(callback)
```

#### ❌ INCORRECT: Software Workaround

```python
# DON'T: Throttle frames in software when hardware supports rate control
def frame_callback(frame):
    if time_since_last_frame >= throttle_interval:
        process_frame(frame)  # Throws away frames unnecessarily
```

#### ✅ CORRECT: Use Hardware API

```python
# Actuator position control - use hardware feature
def move_to_position(self, target_mm: float) -> None:
    # Use actuator's built-in positioning system
    self.actuator.set_target_position(target_mm)
    self.actuator.move_absolute()
```

#### ❌ INCORRECT: Software Workaround

```python
# DON'T: Implement motion control in software when hardware has it
def move_to_position(self, target_mm: float) -> None:
    while abs(current_pos - target_mm) > tolerance:
        step = calculate_step()  # Reinventing hardware features
        self.actuator.move_relative(step)
```

### How to Apply This Rule

1. **Before implementing any feature**, read the hardware API documentation
2. **Search for relevant features**: Look for keywords like:
   - Frame rate, acquisition rate, trigger mode (cameras)
   - Position control, velocity control, acceleration (actuators)
   - Sampling rate, trigger mode, buffering (sensors)
3. **Check manufacturer examples** for how they solve similar problems
4. **Document in LESSONS_LEARNED.md** when you discover native features you initially missed

### Manufacturer Documentation Locations

**CRITICAL:** All manufacturer manuals and API references are organized in component folders.

**Camera (Allied Vision):**
→ `components/camera_module/manufacturer_docs/README.md` - Navigation guide
→ `components/camera_module/manufacturer_docs/vimba_manuals/` - Vimba SDK manuals
→ `components/camera_module/manufacturer_docs/vmbpy_api_reference/` - VmbPy API text files

**Actuator (Xeryon):**
→ `components/actuator_module/manufacturer_docs/README.md` - Navigation guide
→ `components/actuator_module/manufacturer_docs/xeryon_manuals/` - Controller + stage manuals
→ `components/actuator_module/manufacturer_docs/xeryon_library/` - Official Python library

**Laser (Arroyo):**
→ `components/laser_control/manufacturer_docs/README.md` - Navigation guide
→ `components/laser_control/manufacturer_docs/arroyo_manuals/` - Device + programming manuals
→ `components/laser_control/manufacturer_docs/arroyo_sdk/` - Official Python SDK

**Central Index:**
→ `components/MANUFACTURER_DOCS_INDEX.md` - Complete documentation overview

**ALWAYS read manufacturer documentation BEFORE implementing hardware control.**

### Module-Specific Requirements

#### Camera Module (VmbPy API)
**Documentation:** `components/camera_module/manufacturer_docs/`
- Use `AcquisitionFrameRate` for frame rate control (see Feature.txt)
- Use `ExposureAuto`, `GainAuto`, `BalanceWhiteAuto` for automatic adjustments
- Use trigger modes for synchronized capture
- Read `vmbpy_api_reference/Camera.txt` and `Feature.txt` for API details
- Read `vimba_manuals/Vimba Manual.pdf` for comprehensive SDK guide
- Check Allied Vision examples before implementing any camera control feature

**API Reference:** Feature.txt has complete feature list with get/set methods
**Command Reference:** Vimba Manual.pdf Chapter 5 - Feature Access

#### Actuator Module (Xeryon)
**Documentation:** `components/actuator_module/manufacturer_docs/`
- Use actuator's built-in positioning system (absolute/relative moves)
- Use hardware acceleration/deceleration profiles (1000-65500 range)
- Use hardware limit switches and home position features
- Read `xeryon_manuals/Controller Manual.pdf` for serial command reference
- Read `xeryon_library/Xeryon.py` for Python API
- Velocity range: 0.5-400 mm/s (see XLA5.pdf specifications)

**API Reference:** Xeryon.py v1.88 official library
**Command Reference:** Controller Manual.pdf has complete ASCII command set

#### Laser Module (Arroyo)
**Documentation:** `components/laser_control/manufacturer_docs/`
- Use hardware current control (0-2000 mA with 0.1 mA resolution)
- Use hardware TEC temperature control
- Use hardware safety interlocks and limits
- Read `arroyo_manuals/ArroyoComputerInterfacingManual.pdf` for command syntax
- Read `arroyo_sdk/` for official Python SDK
- Current range: 0-2000 mA, query limits before setting

**API Reference:** arroyo_sdk/arroyo_tec package
**Command Reference:** ArroyoComputerInterfacingManual.pdf has complete ASCII command set

### Verification

Before committing any hardware control code, ask:
- ✓ Did I check the hardware API documentation?
- ✓ Did I look at manufacturer examples?
- ✓ Am I using native hardware features where available?
- ✓ Is my software workaround truly necessary?

**If you implement a software workaround, document in code comments WHY the hardware doesn't support the feature.**

## Code Requirements

### Functions

- Write ONLY functions that are immediately needed
- No placeholder functions
- No "convenience" wrappers unless explicitly required
- Each function must have a single, clear purpose

### Comments

**Required:**
- Safety-critical sections
- Complex algorithms requiring explanation
- Regulatory compliance notes
- Type hints and parameter descriptions in docstrings

**Prohibited:**
- Obvious comments (e.g., `# increment counter` above `counter += 1`)
- Decorative separators
- TODO comments without ticket numbers
- Commented-out code

### Documentation

**Docstrings must include:**
```python
def function_name(param: type) -> return_type:
    """
    Brief one-line description.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception occurs
    """
```

**Omit if:**
- Function name and type hints make purpose obvious
- Simple property getters/setters

### Naming

- Use descriptive names: `laser_power_watts` not `lpw`
- Avoid abbreviations except standard units (ms, kg, W)
- No "magic numbers" - use named constants

### Structure

**Required:**
- Type hints on all function signatures
- Return type annotations
- Explicit error handling for hardware operations

**Prohibited:**
- Multiple blank lines (max 1)
- Trailing whitespace
- Lines over 100 characters

## Safety-Critical Code

### Requirements

1. All safety functions MUST have docstrings explaining:
   - What safety condition is being checked
   - What happens if check fails
   - Expected behavior

2. Hardware interactions MUST have error handling

3. State transitions MUST be logged

4. No silent failures in safety systems

### Example

```python
def check_footpedal_active(self) -> bool:
    """
    Verify footpedal deadman switch is actively pressed.

    Safety-critical: Laser cannot fire without active footpedal signal.

    Returns:
        True if footpedal pressed, False otherwise

    Raises:
        HardwareError: If footpedal GPIO cannot be read
    """
    try:
        state = self.gpio_footpedal.value
        if not state:
            self.logger.warning("Footpedal released - laser interlock active")
        return state
    except Exception as e:
        self.logger.error(f"Footpedal read failed: {e}")
        raise HardwareError("Cannot verify footpedal state") from e
```

## Code Review Checklist

Before committing code, verify:

- [ ] **HARDWARE API**: Used native hardware features instead of software workarounds
- [ ] **HARDWARE API**: Checked manufacturer documentation and examples
- [ ] Every function is necessary for current feature
- [ ] No commented-out code
- [ ] No TODO comments without tickets
- [ ] No placeholder implementations
- [ ] All docstrings are accurate and minimal
- [ ] Type hints present on all functions
- [ ] Error handling present for hardware/IO
- [ ] No debug print statements
- [ ] No emojis or decorative elements
- [ ] Passes all linters (black, flake8, mypy, pylint)

## Testing Standards

- One test file per source file
- Test names describe what is being tested: `test_laser_power_validates_range`
- No test helper functions unless used by 3+ tests
- Safety-critical functions require edge case tests

## Imports

Order:
1. Standard library
2. Third-party packages
3. Local application imports

No unused imports.
No wildcard imports.

## Configuration

See `.pylintrc`, `.flake8`, `pyproject.toml` for enforced rules.

## Enforcement

Pre-commit hooks will check:
- Black formatting
- Flake8 linting
- MyPy type checking
- Trailing whitespace
- File size limits

Commits that fail checks will be rejected.

## Lessons Learned Documentation

**CRITICAL PRACTICE**: Every module must maintain a LESSONS_LEARNED.md file.

### Purpose
Track mistakes, API quirks, and solutions to prevent repeating errors across modules and sessions.

### Location
Each module directory must have: `<module_name>/LESSONS_LEARNED.md`

Examples:
- `camera_module/LESSONS_LEARNED.md`
- `actuator_module/LESSONS_LEARNED.md`
- `safety_module/LESSONS_LEARNED.md`

### When to Document

Document immediately when you discover:
1. **API Quirks** - Third-party library behavior that differs from expectations
2. **Incorrect Assumptions** - Method names, signatures, or behavior you assumed wrong
3. **Tricky Bugs** - Issues that took significant debugging to resolve
4. **Integration Issues** - Problems connecting different components
5. **Tool/Environment Issues** - Problems with dev tools, pre-commit hooks, or dependencies

### Required Format

```markdown
### Issue #N: Brief Description

**Date:** YYYY-MM-DD

**Problem:**
Clear description of what went wrong

**Investigation:**
Steps taken to identify the issue

**Root Cause:**
Why the problem occurred

**Solution:**
How it was fixed (with code examples if relevant)

**Files Affected:**
- List of files that needed changes

**Lesson:**
Key takeaway to avoid repeating this mistake
```

### Integration with Development

- Update LESSONS_LEARNED.md BEFORE committing the fix
- Reference lesson numbers in commit messages when applicable
- New AI sessions should read LESSONS_LEARNED.md files to avoid repeating mistakes
- Review lessons learned during code reviews

## Task Tracking with TodoWrite

**Purpose:** Track multi-step work within a session for transparency and progress monitoring

**Enforcement Level:** Recommended (not required)

### When to Use Todos

**Always create todos for:**
- Multi-step features requiring 3+ distinct steps
- Non-trivial tasks requiring planning or investigation
- User provides list of multiple tasks to complete
- Complex debugging or architectural work
- Code reviews or comprehensive analysis

**Skip todos for:**
- Single straightforward tasks (one file, one change)
- Trivial 1-2 step changes
- Pure conversation, questions, or explanations
- Reading documentation or exploring code

### Todo Lifecycle

**Before starting work:**
1. Break down task into discrete, testable steps
2. Create todos with TodoWrite tool
3. Set first todo to `in_progress` before beginning

**During work:**
1. Mark current todo as `completed` IMMEDIATELY after finishing
2. Set next todo to `in_progress` BEFORE starting it
3. Add new todos if work scope expands during implementation
4. Update todo descriptions if approach changes

**Task States:**
- `pending` - Not yet started, waiting in queue
- `in_progress` - Currently working (ONLY ONE at a time)
- `completed` - Finished successfully

### Best Practices

**Good todo structure:**
```
✓ "Implement camera HAL with frame streaming"
✓ "Add safety checks to laser enable function"
✓ "Update PROJECT_STATUS.md with Phase 2 completion"
```

**Poor todo structure:**
```
✗ "Work on camera" (too vague)
✗ "Fix stuff" (not actionable)
✗ "Do the thing we discussed" (no context)
```

**activeForm naming:**
- Use present continuous tense
- Match the action in content
- Example: content="Run tests" → activeForm="Running tests"

### Integration with Documentation

Todos complement documentation, not replace it:

| Tool | Purpose | Timing | Audience |
|------|---------|--------|----------|
| **TodoWrite** | Track current session progress | During work | User + AI |
| **WORK_LOG.md** | Permanent record of actions | After actions | Future sessions |
| **PROJECT_STATUS.md** | Overall project state | After milestones | All stakeholders |

**Update both:**
- Todos show current session progress (visible to user in real-time)
- WORK_LOG.md preserves what was done (permanent record)
- Both updated as work proceeds

### Reference

See `presubmit/reference/TODO_GUIDELINES.md` for detailed examples and patterns.

## Post-Action Checklist

**Purpose:** Verify completion and documentation after any significant work

**Use this checklist:** After completing a feature, fix, or milestone

### Task Tracking

**If you used TodoWrite:**
- [ ] All todos marked `completed` or removed if no longer relevant
- [ ] Final todo list matches actual work completed
- [ ] No todos stuck in `in_progress` state
- [ ] Todo descriptions accurately reflect what was done

### Documentation Updates

**Required for significant actions:**
- [ ] `WORK_LOG.md` updated with action entry including:
  - What was done
  - Files changed
  - Testing performed
  - Commit hash
- [ ] `PROJECT_STATUS.md` updated if milestone reached
- [ ] `LESSONS_LEARNED.md` updated if you discovered:
  - API quirks or unexpected behavior
  - Bugs that required significant debugging
  - Integration issues or workarounds
  - Tool/environment problems

**Optional documentation:**
- [ ] `NEXT_STEPS.md` updated if priorities changed
- [ ] Session summary created in `active/sessions/` (for major work)
- [ ] MCP memory updated if major architectural changes

### Code Quality Verification

**Before committing:**
- [ ] Pre-commit hooks pass (Black, Flake8, MyPy, isort)
- [ ] Manual code review checklist completed (see above)
- [ ] Hardware API usage rule followed (checked docs first)
- [ ] All TODO comments have ticket numbers: `# TODO(#123): description`
- [ ] No debug print statements or commented-out code
- [ ] No emojis or decorative elements

**Safety-critical code:**
- [ ] Safety functions have comprehensive docstrings
- [ ] Error handling present for all hardware operations
- [ ] State transitions logged appropriately
- [ ] No silent failures in safety systems

### Git Workflow

**Before pushing:**
- [ ] Commit message is clear and concise
- [ ] Commit references issue/ticket if applicable
- [ ] No prohibited content (see GIT_CONTENT_POLICY.md)
- [ ] Changes grouped logically (not mixing features)

### Testing

**If applicable:**
- [ ] Unit tests added/updated for new functionality
- [ ] Integration tests pass
- [ ] Hardware testing completed (if hardware code changed)
- [ ] Edge cases considered and tested

### Tool Usage

**If applicable:**
- [ ] Used `mcp__zen__codereview` if module completion (REQUIRED)
- [ ] Used `mcp__zen__testgen` if new functionality needs tests
- [ ] Used `mcp__zen__precommit` if safety-critical changes
- [ ] Updated memory with `mcp__memory__add_observations` if milestone

## Specialized Tool Usage (PROACTIVE)

**Purpose:** Use specialized tools automatically when specific triggers occur

**Reference:** See `presubmit/reference/TOOL_USAGE_GUIDE.md` for complete guide

### Required Tool Usage

These tools MUST be used in specific situations (not optional):

**1. Session Startup**
```javascript
// REQUIRED at start of every session
mcp__memory__search_nodes("TOSCA Project")
mcp__memory__search_nodes("Development Workflow")
```
- 90% faster than reading files
- Gets latest project state
- No exceptions

**2. Module Completion**
```javascript
// REQUIRED before marking module complete
mcp__zen__codereview(
  step: "Review [module name] implementation",
  relevant_files: ["path/to/module.py"]
)
```
- Proactive quality check
- Catches issues early
- Safety-critical requirement

**3. Safety-Critical Commits**
```javascript
// REQUIRED before committing safety code
mcp__zen__precommit(
  step: "Validate changes before commit",
  path: "C:/Users/wille/Desktop/TOSCA-dev"
)
```
- Change impact assessment
- Security review
- Documentation verification

**4. Complex Features (3+ modules)**
```javascript
// REQUIRED for complex features
mcp__zen__planner(
  step: "Plan [feature name] implementation"
)
```
- Prevents implementation oversights
- Documents approach
- Expert validation

### Recommended Tool Usage

Use these tools when appropriate triggers occur:

**Codebase Exploration**
```javascript
// Use Task(Explore) instead of manual Grep
Task(
  subagent_type: "Explore",
  prompt: "Find error handling patterns in hardware controllers"
)
```

**Bug Investigation**
```javascript
// Use systematic debugging
mcp__zen__debug(
  step: "Investigate [bug description]",
  hypothesis: "Initial theory about cause"
)
```

**Milestone Completion**
```javascript
// Update knowledge graph
mcp__memory__add_observations(
  observations: [{
    entityName: "Module Name",
    contents: ["Status: Complete", "Key learnings..."]
  }]
)
```

**Library Documentation**
```javascript
// Get latest API docs
mcp__context7__resolve-library-id(libraryName: "PyQt6")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/PyQt/PyQt6")
```

### Tool Selection Quick Reference

| Situation | Tool to Use |
|-----------|-------------|
| Session start | `mcp__memory__search_nodes` (REQUIRED) |
| Codebase exploration | `Task(Explore)` |
| Complex feature | `mcp__zen__planner` (REQUIRED if 3+ modules) |
| Bug investigation | `mcp__zen__debug` |
| Module complete | `mcp__zen__codereview` (REQUIRED) |
| Need tests | `mcp__zen__testgen` |
| Safety commit | `mcp__zen__precommit` (REQUIRED) |
| Milestone reached | `mcp__memory__add_observations` (REQUIRED) |
| Library docs | `mcp__context7__get-library-docs` |

### Integration with Workflow

**Before Work:**
- ✅ Use `mcp__memory__search_nodes` for context (REQUIRED)
- ✅ Check git status with Bash

**During Work:**
- ✅ Use `Task(Explore)` for codebase understanding
- ✅ Use `mcp__zen__planner` for complex features
- ✅ Use TodoWrite for multi-step tasks

**After Work:**
- ✅ Use `mcp__zen__codereview` for module completion (REQUIRED)
- ✅ Use `mcp__zen__testgen` for test generation
- ✅ Use `mcp__zen__precommit` for safety commits (REQUIRED)
- ✅ Use `mcp__memory__add_observations` for milestones
- ✅ Update WORK_LOG.md and PROJECT_STATUS.md

### Gradual Adoption

**Week 1:** Session startup optimization
- Use `mcp__memory__search_nodes` at every session start
- Use `Task(Explore)` for code exploration

**Week 2:** Quality tools
- Use `mcp__zen__codereview` after module completion
- Use `mcp__zen__debug` for bug investigation

**Week 3:** Proactive tools
- Use `mcp__zen__planner` for complex features
- Use `mcp__zen__precommit` before safety commits

**Week 4:** Full integration
- Update memory regularly
- Use complete workflow patterns

## Remember

**This is safety-critical software. Every line of code matters.**

**When in doubt, ask before adding. It's easier to add than to remove from FDA documentation.**
