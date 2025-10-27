# How to Start a New Claude Code Session

**Purpose:** Exact steps to get a new AI instance up to speed on TOSCA project

---

## ⚠️ CRITICAL: Git Content Policy

**READ FIRST:** `presubmit/reference/GIT_CONTENT_POLICY.md`

**NEVER include in git-tracked files:**
- ❌ Any AI/Claude/assistant references
- ❌ "Medical device", "FDA", "clinical", "healthcare"
- ❌ Any use designation (research, clinical, etc.)

**Repository framing:**
- ✅ "TOSCA Laser Control System" (generic)
- ✅ "Safety-critical laser system"
- ✅ No mention of development methodology or intended use

**These rules ONLY apply to gitignored files** (this file, presubmit/, .claude/, etc.)

---

## 🚀 NEW: Fast Start with MCP Memory System

**Fastest onboarding method** - Project context stored in persistent memory graph!

### Quick Start (30 seconds)

**Copy-paste from:** `presubmit/onboarding/QUICK_SESSION_PROMPT.md`

The quick prompt uses MCP memory to instantly load:
- Current project status
- Critical development rules (Git Content, Hardware API, TodoWrite)
- **AI Tool Usage guidelines** (NEW - specialized tool triggers)
- What was last worked on
- Next recommended steps

### What You Get Instantly

The MCP memory system provides immediate access to:
- **Project overview:** Tech stack, current phase, completion status
- **Critical rules:** Git Content Policy, Hardware API Usage Rule, Coding Standards
- **AI Tool Usage:** When to use specialized tools proactively
- **Tool Workflows:** Session start, module development, bug investigation patterns
- **Required vs Optional:** Which tools are mandatory vs recommended
- **Module status:** Camera HAL (complete), Laser HAL (next priority), Actuator HAL (pending)
- **Lessons learned:** VmbPy API quirks, common pitfalls
- **Development workflow:** Before/during/after work checklists

### Example Queries

```
"Search nodes for Camera HAL"
"What are the critical development rules?"
"What's the status of Laser Controller HAL?"
"Show me VmbPy API quirks"
"What is the Hardware API Usage Rule?"
"Search nodes for AI Tool Usage"
"What tool workflows should I use?"
"Which tools are required vs optional?"
```

### When to Use Memory vs Full Docs

**Use Memory System (30 sec):**
- Quick status check
- Reminder of critical rules
- Module status overview
- Starting a coding session

**Read Full Docs (5-10 min):**
- First time onboarding
- Major architecture changes
- Deep dive into specific module
- Understanding detailed specifications

---

## Step 1: Traditional Onboarding (Read Full Docs)

**Use this if:** First session, need detailed context, or memory system unavailable

### Copy-Paste From File

**Copy-paste from:** `presubmit/onboarding/FULL_SESSION_PROMPT.md`

This comprehensive prompt includes:
- All 9 file reading steps in order
- Critical development rules (Git Content Policy, Hardware API, TodoWrite)
- Post-action checklist
- Repository and directory information

After reading, tell me:
- What we were last working on
- Current project status
- What you recommend as next steps

Critical rules:
- NO AI/medical/FDA refs in git-tracked files (see GIT_CONTENT_POLICY.md)
- Minimal code only (no extras, no decorative elements, no emojis)
- Always add new packages to requirements.txt
- Test outputs go to designated directories only
- Update presubmit/active/WORK_LOG.md after each significant action
- All code must pass pre-commit hooks (Black, Flake8, MyPy, isort)

Repository: https://github.com/will-aleyegn/TOSCA_DEV.git
Working Directory: C:\Users\wille\Desktop\TOSCA-dev
```

---

## Step 2: Wait for AI to Read and Summarize

The AI will:
- Read all 4 files
- Summarize current project state
- Tell you what was last being worked on
- Suggest next steps

---

## Step 3: Give Your Direction

Examples:
- "Continue with that work"
- "Actually, I want to work on [specific task]"
- "Let's start the actuator module"
- "Debug the camera feature exploration issue"

---

## That's It!

The AI now has:
- Complete project context
- Development standards
- Recent work history
- All documentation locations

---

## Alternative: If AI Doesn't Auto-Read

If the AI doesn't automatically read the files, you can be more explicit:

```
Please use the Read tool to read these files:
- presubmit/START_HERE.md
- presubmit/active/PROJECT_STATUS.md
- presubmit/reference/CODING_STANDARDS.md
- presubmit/active/WORK_LOG.md

Then summarize what we were working on and ask what I want to do next.
```

---

## Key Files Reference

If you need to reference specific docs during session:

- **START_HERE.md** - Quick 5-step setup
- **PROJECT_STATUS.md** - Complete project state (472 lines)
- **CODING_STANDARDS.md** - Development rules (minimal code philosophy)
- **WORK_LOG.md** - Real-time action tracking
- **CONFIGURATION.md** - All 11 config files explained
- **SESSION_PROMPT.md** - Template prompt (what Step 1 is based on)

Architecture Documentation:
- `docs/architecture/01_system_overview.md` - Complete system architecture
- `docs/architecture/02_database_schema.md` - Database design
- `docs/architecture/03_safety_system.md` - Safety system (critical)
- `docs/architecture/04_treatment_protocols.md` - Protocol engine
- `docs/architecture/05_image_processing.md` - Camera and vision

---

## Tips for Smooth Sessions

1. **Always update WORK_LOG.md** - Tell the AI to update after each significant action
2. **Reference PROJECT_STATUS.md** - Have AI update it when major milestones complete
3. **Point to CODING_STANDARDS.md** - If AI generates extra code, remind it of minimal code rule
4. **Check git status frequently** - Keep commits organized and meaningful
5. **Update MCP memory** - When major milestones reached, ask AI to update memory entities
6. **NEW: Tool Usage Awareness** - AI should use specialized tools proactively (see TOOL_USAGE_GUIDE.md)
7. **NEW: Verify tool usage** - After module completion, check if AI used mcp__zen__codereview

---

## Maintaining the Memory System

**When to Update Memory:**
- Module status changes (e.g., Laser HAL goes from 0% → 100%)
- New critical rules or policies added
- Major architecture decisions
- Important lessons learned
- Phase transitions (Phase 2 → Phase 3)

**How to Update:**

```
"Update the MCP memory for [entity name] with [new information]"

Examples:
"Update Laser Controller HAL status to COMPLETE"
"Add new observation to Hardware API Usage Rule about [discovery]"
"Create new entity for GPIO Controller HAL with initial status"
```

**What's Currently Stored (as of 2025-10-26):**
- TOSCA Project (overview, phase, tech stack)
- Git Content Policy (critical rules)
- Hardware API Usage Rule (development standard)
- **AI Tool Usage (NEW - specialized tool triggers)**
- **Tool Workflow Patterns (NEW - development workflows)**
- **Required vs Optional Tools (NEW - mandatory vs recommended)**
- Camera HAL (complete - 100%)
- Laser Controller HAL (next priority - 0%)
- Actuator Controller HAL (pending - 0%)
- Coding Standards (minimal code philosophy)
- Key Documentation Files (reference guide)
- VmbPy API Quirks (lessons learned)
- Development Workflow (before/during/after process)

---

## Session Prompt Template (Copy-Paste Ready)

**Use this exact prompt to start a new AI session:**

```
I'm working on the TOSCA Laser Control System.

⚠️ **CRITICAL FIRST:** Read `presubmit/reference/GIT_CONTENT_POLICY.md`
Never include AI/medical/FDA references in git-tracked files.

**Please do the following:**

1. Read `presubmit/reference/GIT_CONTENT_POLICY.md` (MANDATORY - content rules)
2. Read `presubmit/START_HERE.md` for quick setup
3. Read `presubmit/active/PROJECT_STATUS.md` for complete project state
4. Read `presubmit/reference/CODING_STANDARDS.md` for development rules
5. Check current git status and latest commits
6. Let me know what we were working on and ask if we should continue

**Critical Rules:**
- NO AI/medical/FDA refs in git-tracked files (see GIT_CONTENT_POLICY.md)
- Write minimal code only (no extras, no decorative elements)
- Always add new packages to requirements.txt
- Test outputs go to designated directories only
- Update presubmit/active/PROJECT_STATUS.md as we work
- All code must pass pre-commit hooks (Black, Flake8, MyPy, isort)

**Repository:** https://github.com/will-aleyegn/TOSCA_DEV.git

**Internal Context (OK in gitignored files):**
This is actually an FDA-Enhanced Documentation Level medical device project,
but we keep that framing in internal docs only. Public repo is generic.
```

**After the AI reads the files, continue with your work!**

---

**Last Updated:** 2025-10-24
**Location:** presubmit/NEW_SESSION_GUIDE.md
