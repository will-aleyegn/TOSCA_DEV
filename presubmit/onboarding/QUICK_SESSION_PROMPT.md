# Quick Session Prompt - MCP Memory Fast Path

**Purpose:** Fast onboarding using MCP memory instead of file reading
**Use When:** Daily sessions, continuing recent work, quick context refresh
**Time:** 30 seconds

---

## Copy-Paste This Entire Prompt

```
I'm working on the TOSCA Laser Control System.

Search the MCP knowledge graph for:
1. "TOSCA Project" - Get current project status and phase
2. "TodoWrite Workflow" - Learn task tracking guidelines
3. "Git Content Policy" - Understand content rules
4. "Hardware API Usage Rule" - Critical development rule
5. "Development Workflow" - Get workflow guidelines
6. "Presubmit Folder" - Understand documentation system
7. "AI Tool Usage" - Learn specialized tool triggers

Then tell me:
- Current project status and what we were last working on
- What you recommend as next steps
- Confirm you understand the critical rules (Hardware API, Git Content, TodoWrite)

**Tool Usage Awareness:**
- Use `mcp__memory__search_nodes` at session start (you just did this ✓)
- Use `Task(Explore)` for codebase exploration (not manual Grep)
- Use `mcp__zen__codereview` AFTER completing modules (proactive)
- Use `mcp__zen__debug` for non-trivial bugs (systematic)
- Use `mcp__zen__planner` for complex features (plan first)
- See `presubmit/reference/TOOL_USAGE_GUIDE.md` for triggers

**Repository:** https://github.com/will-aleyegn/TOSCA_DEV.git
**Working Directory:** C:\Users\wille\Desktop\TOSCA-dev
```

---

**Last Updated:** 2025-10-25
**Location:** presubmit/onboarding/QUICK_SESSION_PROMPT.md
