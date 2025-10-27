# Full Session Prompt - Complete Onboarding

**Purpose:** Comprehensive file-reading onboarding for new sessions
**Use When:** First session, major changes, need complete context
**Time:** 5-10 minutes

---

## Copy-Paste This Entire Prompt

```
I'm working on the TOSCA Laser Control System.

⚠️ **CRITICAL FIRST:** Read `presubmit/reference/GIT_CONTENT_POLICY.md`
Never include AI/medical/FDA references in git-tracked files.

**Please do the following in order:**

1. Read `presubmit/README.md` (navigation hub - explains entire presubmit system)
2. Read `presubmit/reference/GIT_CONTENT_POLICY.md` (MANDATORY - content rules)
3. Read `presubmit/START_HERE.md` (quick 5-step setup)
4. Read `presubmit/active/PROJECT_STATUS.md` (current project state)
5. Read `presubmit/reference/CODING_STANDARDS.md` (development rules including TodoWrite)
6. Check current git status and recent commits
7. Review `presubmit/active/WORK_LOG.md` (recent work)
8. Search MCP memory for "TOSCA Project" and "TodoWrite Workflow"
9. Tell me what we were last working on and ask if we should continue

**Critical Development Rules:**

**Content Policy:**
- NO AI/medical/FDA refs in git-tracked files (see GIT_CONTENT_POLICY.md)
- Repository framing: "TOSCA Laser Control System" (generic)
- Internal docs in presubmit/ can contain AI/medical context

**Code Standards:**
- Write minimal code only (no extras, no decorative elements, NO emojis)
- ⚠️ HARDWARE API RULE: ALWAYS use native hardware features before software workarounds
- Check manufacturer documentation FIRST before implementing hardware control
- All code must pass pre-commit hooks (Black, Flake8, MyPy, isort)
- Type hints on all functions, comprehensive docstrings for safety-critical code

**Task Tracking (TodoWrite):**
- Use TodoWrite for multi-step tasks (3+ steps), complex debugging, or user-provided lists
- Skip todos for single-step tasks, trivial changes, or pure conversation
- Only ONE todo in_progress at a time
- Mark todos completed IMMEDIATELY after finishing each step
- See presubmit/reference/TODO_GUIDELINES.md for detailed examples

**Documentation Updates:**
- Update `presubmit/active/WORK_LOG.md` after every significant action
- Update `presubmit/active/PROJECT_STATUS.md` when milestones reached
- Update LESSONS_LEARNED.md when discovering API quirks or fixing bugs
- Pre-commit reminder will show (but won't block commits)

**Tool Usage (PROACTIVE):**
Use specialized tools automatically when triggers occur:
- `mcp__memory__search_nodes` - Session start (REQUIRED - faster than file reading)
- `Task(Explore)` - Codebase exploration (not manual Grep for open-ended searches)
- `mcp__zen__codereview` - After module completion (REQUIRED for quality)
- `mcp__zen__debug` - Bug investigation (systematic approach)
- `mcp__zen__planner` - Complex features (plan before implementing)
- `mcp__zen__precommit` - Before safety-critical commits (validation)
- `mcp__memory__add_observations` - After milestones (update knowledge graph)
- See `presubmit/reference/TOOL_USAGE_GUIDE.md` for complete trigger list

**Post-Action Checklist:**
After completing work, verify:
- [ ] Todos marked completed (if used TodoWrite)
- [ ] Used appropriate specialized tools (codereview, testgen, etc.)
- [ ] Memory updated if milestone reached
- [ ] WORK_LOG.md updated with action entry
- [ ] PROJECT_STATUS.md updated if milestone reached
- [ ] LESSONS_LEARNED.md updated if discovered API quirks
- [ ] Pre-commit hooks pass
- [ ] Hardware API usage rule followed
- [ ] No prohibited content in git-tracked files

**Repository:** https://github.com/will-aleyegn/TOSCA_DEV.git
**Working Directory:** C:\Users\wille\Desktop\TOSCA-dev

**Internal Context (OK in gitignored files):**
This is an FDA-Enhanced Documentation Level medical device project,
but we keep that framing in internal docs only. Public repo is generic.
```

---

**Last Updated:** 2025-10-25
**Location:** presubmit/onboarding/FULL_SESSION_PROMPT.md
