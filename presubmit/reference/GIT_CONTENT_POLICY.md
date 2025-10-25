# Git Content Policy

**Purpose:** Define what content is allowed in git-tracked files vs gitignored files

**Critical Rule:** This is a public repository. Content must be appropriate for public viewing.

---

## NEVER Include in Git-Tracked Files

**Prohibited Content:**
- References to development methodology or tools (AI assistants, Claude, GPT, etc.)
- Medical device classification or intended use
- FDA references or regulatory designations
- Clinical or healthcare context
- Research methodology references
- Any proprietary or confidential information

**Why:**
This repository is public and must maintain a generic, professional appearance without revealing:
- Development process details
- Intended use cases
- Regulatory pathways
- Internal project context

---

## Always OK in Git-Tracked Files

**Allowed Content:**
- Technical descriptions: "TOSCA Laser Control System"
- Generic framing: "Safety-critical laser system"
- Hardware specifications and interfaces
- Software architecture and implementation details
- Code, tests, and technical documentation
- Standard software development practices
- Performance metrics and optimization details

---

## Internal Documentation (Gitignored Only)

**Location:** `presubmit/` folder (gitignored)

**Purpose:** Session management and internal development documentation

**Can Include:**
- Development methodology references
- Session setup instructions
- Project context and background
- Work logs and progress tracking
- References to tools and assistants
- Regulatory context (FDA, medical device, etc.)

**Files in presubmit/:**
- SESSION_PROMPT.md - Template for starting new sessions
- NEW_SESSION_GUIDE.md - How to onboard new sessions
- REMINDER.txt - Pre-commit reminder text
- Any other internal documentation

---

## Verification Checklist

Before committing git-tracked files, verify:

- [ ] No AI/assistant references (Claude, GPT, etc.)
- [ ] No medical device classification
- [ ] No FDA or regulatory references
- [ ] No clinical or healthcare context
- [ ] No research methodology mentions
- [ ] Only generic technical descriptions used
- [ ] Documentation appropriate for public viewing

---

## Examples

### Good (Git-Tracked)

```python
# Laser power control with safety interlocks
class LaserController:
    """Controls laser output with hardware safety interlocks."""
```

```markdown
# TOSCA Laser Control System

A safety-critical laser control system with hardware interlocks,
session management, and real-time monitoring.
```

### Bad (Would Violate Policy)

```python
# FDA Class II medical device laser controller
# Developed with AI assistance for clinical applications
class LaserController:
```

```markdown
# Medical Laser System

This FDA-regulated medical device was developed using Claude AI
for ophthalmic clinical treatments.
```

---

## Repository Framing

**Use:** "TOSCA Laser Control System"
**Avoid:** Medical device, clinical system, FDA-regulated device

**Use:** "Safety-critical laser system"
**Avoid:** Medical laser, clinical laser, therapeutic laser

**Use:** "Session management for subject tracking"
**Avoid:** Patient tracking, clinical records, medical data

---

## When in Doubt

If you're uncertain whether content is appropriate for git-tracked files:
1. Ask if it would be appropriate for public GitHub viewing
2. Check if it reveals internal development processes
3. Verify it doesn't mention intended use or regulatory context
4. Put it in `presubmit/` folder instead (gitignored)

---

**Last Updated:** 2025-10-25
**Location:** presubmit/reference/GIT_CONTENT_POLICY.md
**Status:** Active policy for all git commits
