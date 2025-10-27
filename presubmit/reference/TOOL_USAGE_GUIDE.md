# Tool Usage Guide - Quick Reference

**Last Updated:** 2025-10-26
**Purpose:** Quick triggers for when AI should use specialized tools proactively
**Read Time:** 2 minutes

---

## Core Principle

**Use specialized tools proactively** instead of manual processes when specific triggers occur.

**Detailed Reference:** See `AI_TOOL_USAGE_RECOMMENDATIONS.md` for comprehensive guide.

---

## Session Startup (EVERY SESSION)

### ⚡ Quick Start (30 seconds)

**ALWAYS use these at session start:**

```javascript
// 1. Get project context from memory
mcp__memory__search_nodes("TOSCA Project")
mcp__memory__search_nodes("Development Workflow")

// 2. Check git state (parallel)
Bash("git log --oneline -10")
Bash("git status")
```

**Why:** 90% faster than reading 6+ files manually.

**Skip file reading** unless memory search fails or you need specific details.

---

## Tool Triggers - When to Use What

### 🔍 Code Understanding

| Trigger | Use This Tool | Example |
|---------|---------------|---------|
| Need to explore codebase | `Task(Explore)` | "Where are errors handled in camera module?" |
| Need systematic analysis | `mcp__zen__analyze` | "Analyze HAL architecture" |
| Need execution flow | `mcp__zen__tracer` | "Trace laser enable flow from GUI to hardware" |
| Need library docs | `mcp__context7__get-library-docs` | "Get latest PyQt6 signals documentation" |

**Stop using:** Manual Grep for exploration (use for specific needle queries only)

### 🛠️ Implementation

| Trigger | Use This Tool | Example |
|---------|---------------|---------|
| Complex feature (3+ steps) | `mcp__zen__planner` | "Plan watchdog timer implementation" |
| Following existing patterns | `Task(code-architect)` | "Design GPIO controller following HAL patterns" |
| Major decision needed | `mcp__zen__consensus` | "Evaluate threading approach for controllers" |

**Stop using:** Direct implementation for complex features (plan first)

### 🐛 Debugging

| Trigger | Use This Tool | Example |
|---------|---------------|---------|
| Mystery bug | `mcp__zen__debug` | "Camera drops frames intermittently" |
| Complex issue | `mcp__zen__thinkdeep` | "Analyze thread safety across modules" |
| User questions approach | `mcp__zen__challenge` | "The API doesn't support that feature" |

**Stop using:** Print statements and ad-hoc debugging for non-trivial issues

### ✅ Quality & Testing

| Trigger | Use This Tool | Example |
|---------|---------------|---------|
| **After implementing module** | `mcp__zen__codereview` | Review before marking module complete |
| Need tests | `mcp__zen__testgen` | Generate test suite for new controller |
| **Before safety-critical commit** | `mcp__zen__precommit` | Validate laser controller changes |
| Security check needed | `mcp__zen__secaudit` | Audit safety system implementation |

**PROACTIVE:** Use codereview after EVERY module completion (don't wait for user request)

### 📝 Documentation

| Trigger | Use This Tool | Example |
|---------|---------------|---------|
| **After milestone** | `mcp__memory__add_observations` | Update "Laser HAL" status to complete |
| Discovered API quirk | `mcp__memory__add_observations` | Add lesson to "Camera HAL" entity |
| Major decision made | `mcp__memory__create_entities` | Document new architecture pattern |

**PROACTIVE:** Update memory within 24h of milestone completion

---

## Required Tool Usage (Mandatory)

These tools **must be used** in specific situations:

### 1. Session Startup
✅ **REQUIRED:** `mcp__memory__search_nodes` at start of every session
- Faster than file reading
- Gets latest project state
- No exceptions

### 2. After Module Completion
✅ **REQUIRED:** `mcp__zen__codereview` before marking module complete
- Proactive quality check
- Catches issues early
- Safety-critical requirement

### 3. Safety-Critical Code
✅ **REQUIRED:** `mcp__zen__precommit` before committing safety code
- Validates changes
- Security review
- Impact assessment

### 4. Complex Features
✅ **REQUIRED:** `mcp__zen__planner` for features affecting 3+ modules
- Prevents implementation oversights
- Documents approach
- Expert validation

---

## Tool Selection Quick Reference

```
SITUATION → TOOL TO USE

Session start → mcp__memory__search_nodes
Codebase exploration → Task(Explore)
Understand code → mcp__zen__analyze
Mystery bug → mcp__zen__debug
Complex feature → mcp__zen__planner (then implement)
Module complete → mcp__zen__codereview
Need tests → mcp__zen__testgen
Before commit (safety) → mcp__zen__precommit
Milestone reached → mcp__memory__add_observations
Library docs → mcp__context7__get-library-docs
User questions you → mcp__zen__challenge
```

---

## Integration with Existing Workflow

### Before Work (Add to existing checklist)
1. ✅ Existing: Read files or use memory
2. ⭐ **NEW:** Use `mcp__memory__search_nodes` INSTEAD of file reading
3. ✅ Existing: Check git status
4. ✅ Existing: Review WORK_LOG.md

### During Work (Add to existing checklist)
1. ✅ Existing: Use TodoWrite for multi-step tasks
2. ⭐ **NEW:** Use `Task(Explore)` for codebase exploration
3. ⭐ **NEW:** Use `mcp__zen__planner` for complex features
4. ⭐ **NEW:** Use `mcp__zen__debug` for bugs
5. ✅ Existing: Update WORK_LOG.md

### After Work (Add to existing checklist)
1. ⭐ **NEW:** Use `mcp__zen__codereview` (REQUIRED for modules)
2. ⭐ **NEW:** Use `mcp__zen__testgen` for test generation
3. ⭐ **NEW:** Use `mcp__zen__precommit` for safety-critical commits
4. ⭐ **NEW:** Use `mcp__memory__add_observations` for milestones
5. ✅ Existing: Update PROJECT_STATUS.md if milestone
6. ✅ Existing: Git commit

---

## Common Workflow Patterns

### Pattern 1: New Module Implementation

```
1. mcp__zen__planner → Plan approach
2. Implement code (with TodoWrite if complex)
3. mcp__zen__testgen → Generate tests
4. mcp__zen__codereview → Review implementation
5. mcp__memory__add_observations → Update memory
6. Update WORK_LOG.md and PROJECT_STATUS.md
```

### Pattern 2: Bug Investigation

```
1. mcp__zen__debug → Systematic investigation
2. mcp__zen__tracer → If need execution flow
3. Implement fix
4. mcp__memory__add_observations → Document lesson
5. Update WORK_LOG.md
```

### Pattern 3: Code Quality Sprint

```
1. mcp__zen__codereview → Review all modules
2. mcp__zen__refactor → Identify improvements
3. mcp__zen__secaudit → Security check
4. Implement fixes
5. mcp__zen__precommit → Validate changes
```

---

## What NOT to Change

**Keep using as-is:**
- ✅ Read, Write, Edit, Bash, Grep, Glob (core file operations)
- ✅ TodoWrite (task tracking within session)
- ✅ WORK_LOG.md updates (permanent record)
- ✅ PROJECT_STATUS.md updates (milestone tracking)
- ✅ CODING_STANDARDS.md compliance
- ✅ Pre-commit hooks

**What's changing:**
- ⭐ Use memory INSTEAD of file reading at startup
- ⭐ Use Task(Explore) INSTEAD of manual Grep for exploration
- ⭐ Use Zen tools PROACTIVELY (not waiting for user request)
- ⭐ Update memory REGULARLY (not just occasionally)

---

## Decision Tree

```
Starting session?
└─ Use mcp__memory__search_nodes (not file reading)

Need to understand code?
├─ Exploration → Task(Explore)
├─ Systematic → mcp__zen__analyze
└─ Execution → mcp__zen__tracer

Implementing feature?
├─ Simple → Direct implementation
└─ Complex → mcp__zen__planner first

Found bug?
├─ Simple → Fix directly
└─ Mystery → mcp__zen__debug

Module complete?
└─ MUST use mcp__zen__codereview

Milestone reached?
└─ MUST use mcp__memory__add_observations
```

---

## Gradual Adoption

Don't try to use all tools immediately. **Adopt in phases:**

### Week 1: Startup Only
- ✅ Use `mcp__memory__search_nodes` at session start
- ✅ Use `Task(Explore)` when exploring code
- Track success rate

### Week 2: Quality Tools
- ✅ Use `mcp__zen__codereview` after modules
- ✅ Use `mcp__zen__debug` for bugs
- Track issues caught

### Week 3: Proactive Tools
- ✅ Use `mcp__zen__planner` for complex features
- ✅ Use `mcp__zen__precommit` before commits
- Track time saved

### Week 4: Full Integration
- ✅ Update memory regularly
- ✅ Use full workflow patterns
- Measure overall improvement

---

## Success Metrics

Track these to measure effectiveness:

| Metric | Before | Target |
|--------|--------|--------|
| Session startup time | 5-10 min | <1 min |
| Bugs caught before commit | Low | High |
| Code review frequency | Rare | Every module |
| Memory updates | Rare | Every milestone |
| Tool usage diversity | ~10 tools | 20+ tools |

---

## When to Read Full Recommendations

Read `AI_TOOL_USAGE_RECOMMENDATIONS.md` when:
- Need detailed examples of tool usage
- Want to understand tool capabilities deeply
- Creating new workflow patterns
- Troubleshooting tool issues
- Learning advanced combinations

**This guide:** Quick triggers and workflows (read in 2 min)
**Full recommendations:** Deep dive and examples (read in 20 min)

---

## Quick Reference Card

**Save these queries for instant use:**

```javascript
// Session start
mcp__memory__search_nodes("TOSCA Project")

// Code exploration
Task(subagent_type: "Explore", prompt: "...")

// Bug investigation
mcp__zen__debug(step: "Investigate...", model: "gemini-2.5-pro")

// Module review
mcp__zen__codereview(step: "Review...", relevant_files: [...])

// Update memory
mcp__memory__add_observations(observations: [{entityName: "...", contents: [...]}])

// Get library docs
mcp__context7__resolve-library-id(libraryName: "PyQt6")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/PyQt/PyQt6")
```

---

## Questions?

**"When do I use Grep vs Task(Explore)?"**
- Grep: Searching for specific needle (class name, function, pattern)
- Task(Explore): Understanding feature implementation or patterns

**"When do I use Read vs mcp__zen__analyze?"**
- Read: Need to see specific file contents
- Analyze: Need systematic code analysis

**"Do I still update WORK_LOG.md?"**
- YES! Memory supplements documentation, doesn't replace it

**"Can I skip codereview if simple change?"**
- Small fixes: Optional
- Module completion: REQUIRED
- Safety-critical: REQUIRED

---

**Last Updated:** 2025-10-26
**Location:** presubmit/reference/TOOL_USAGE_GUIDE.md
**Status:** Quick reference for tool usage triggers
**Companion:** AI_TOOL_USAGE_RECOMMENDATIONS.md (detailed guide)
