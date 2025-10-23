# TOSCA Coding Standards

**Project:** FDA-Enhanced Documentation Level Medical Device Software
**Principle:** Minimal, Precise, Safety-Critical Code Only

## Core Principles

1. **Write only what is required** - No speculative features, no helper functions "just in case"
2. **No decorative elements** - No emojis, no ASCII art, no flourishes
3. **Documentation is functional** - Comments explain WHY, not WHAT. Code should be self-documenting.
4. **Every line must have a purpose** - If it doesn't contribute to functionality or safety, remove it

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

**This is medical device software. Every line of code can impact patient safety.**

**When in doubt, ask before adding. It's easier to add than to remove from FDA documentation.**
