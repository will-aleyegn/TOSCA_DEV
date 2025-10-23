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

### Module-Specific Requirements

#### Camera Module (VmbPy API)
- Use `AcquisitionFrameRate` for frame rate control
- Use `ExposureAuto`, `GainAuto`, `BalanceWhiteAuto` for automatic adjustments
- Use trigger modes for synchronized capture
- Check Allied Vision examples before implementing any camera control feature

#### Actuator Module
- Use actuator's built-in positioning system (absolute/relative moves)
- Use hardware acceleration/deceleration profiles
- Use hardware limit switches and home position features
- Check actuator SDK documentation before implementing motion control

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

## Remember

**This is safety-critical software. Every line of code matters.**

**When in doubt, ask before adding. It's easier to add than to remove from FDA documentation.**
