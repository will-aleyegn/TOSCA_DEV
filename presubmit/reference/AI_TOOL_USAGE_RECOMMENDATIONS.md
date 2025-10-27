# AI Tool Usage Recommendations - TOSCA Project

**Created:** 2025-10-26
**Purpose:** Strategic guide for leveraging AI tools effectively in TOSCA development
**Audience:** AI assistants working on TOSCA project

---

## Executive Summary

This document provides **actionable recommendations** for how AI assistants can better leverage the 80+ available tools in Claude Code to work more effectively on the TOSCA project. It's organized by development phase and workflow, with specific tool combinations and usage patterns.

**Key Insight:** The project has excellent documentation and workflow systems, but tool usage could be significantly optimized through:
1. Proactive use of specialized agents (Zen MCP, Task system)
2. Strategic memory system updates
3. Automated testing and quality checks
4. Better integration of analysis tools

---

## Table of Contents

1. [Session Startup Tools](#session-startup-tools)
2. [Code Analysis & Understanding](#code-analysis--understanding)
3. [Development & Implementation](#development--implementation)
4. [Testing & Quality Assurance](#testing--quality-assurance)
5. [Debugging & Problem Solving](#debugging--problem-solving)
6. [Documentation & Knowledge Management](#documentation--knowledge-management)
7. [Git Workflow Optimization](#git-workflow-optimization)
8. [Advanced Workflows](#advanced-workflows)

---

## Session Startup Tools

### Current Approach
- Manual file reading (6-9 files)
- Git status check
- Manual context building
- Takes 5-10 minutes

### Recommended Optimization

#### 1. Use MCP Memory for Fast Context Loading

**Tool:** `mcp__memory__search_nodes`

**When:** Start of EVERY session

**How:**
```javascript
// Query key project entities
mcp__memory__search_nodes("TOSCA Project")
mcp__memory__search_nodes("Git Content Policy")
mcp__memory__search_nodes("Hardware API Usage Rule")
mcp__memory__search_nodes("Development Workflow")
mcp__memory__search_nodes("Camera HAL")
mcp__memory__search_nodes("Laser Controller")
```

**Benefits:**
- Reduces startup time from 5-10 min to 30 seconds
- Gets current module status instantly
- Retrieves critical rules without file reading
- Provides lessons learned automatically

#### 2. Parallel Information Gathering

**Tools:** Multiple Read calls in single message

**When:** Need detailed context beyond memory

**How:**
```javascript
// Single message with parallel reads
Read("presubmit/active/PROJECT_STATUS.md", offset=1, limit=100)
Read("presubmit/active/WORK_LOG.md", offset=1, limit=50)
Bash("git log --oneline -10")
Bash("git status")
```

**Benefits:**
- Faster than sequential reads
- Gets complete picture immediately
- More efficient token usage

#### 3. Use Repomix for Architecture Understanding

**Tool:** `mcp__plugin_repomix-mcp_repomix__attach_packed_output`

**When:** First session or major architecture changes

**How:**
```javascript
// Attach packed codebase for analysis
mcp__plugin_repomix-mcp_repomix__attach_packed_output(
  path: "C:/Users/wille/Desktop/TOSCA-dev"
)

// Then grep for specific patterns
mcp__plugin_repomix-mcp_repomix__grep_repomix_output(
  outputId: "<id>",
  pattern: "class.*Controller",
  contextLines: 3
)
```

**Benefits:**
- Quick codebase overview
- Pattern analysis across all files
- Architectural understanding without reading every file

---

## Code Analysis & Understanding

### Current Approach
- Manual Grep/Glob searches
- Sequential file reading
- Ad-hoc code exploration

### Recommended Optimization

#### 1. Use Zen Analyze for Comprehensive Code Analysis

**Tool:** `mcp__zen__analyze`

**When:** Need to understand architecture, performance, or quality

**How:**
```javascript
mcp__zen__analyze(
  step: "Analyze the hardware abstraction layer architecture",
  step_number: 1,
  total_steps: 2,
  next_step_required: true,
  findings: "Starting systematic analysis of HAL modules",
  model: "gemini-2.5-pro",
  analysis_type: "architecture",
  relevant_files: [
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/camera_controller.py",
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/laser_controller.py",
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/actuator_controller.py"
  ]
)
```

**When to use:**
- Understanding module architecture
- Performance analysis
- Code quality assessment
- Identifying patterns and anti-patterns

**Benefits:**
- Systematic multi-step analysis
- Expert model validation
- Structured findings
- Confidence tracking

#### 2. Use Zen Tracer for Execution Flow Analysis

**Tool:** `mcp__zen__tracer`

**When:** Need to understand how code executes or dependencies

**How:**
```javascript
// Trace execution flow
mcp__zen__tracer(
  step: "Trace the laser enable flow from GUI button to hardware",
  step_number: 1,
  total_steps: 3,
  next_step_required: true,
  findings: "Starting trace from LaserWidget.enable_button_clicked",
  target_description: "Laser enable flow - need to understand all safety checks",
  trace_mode: "precision",  // or "dependencies"
  model: "gemini-2.5-pro"
)
```

**When to use:**
- Understanding execution paths
- Mapping dependencies
- Analyzing call chains
- Safety-critical flow verification

#### 3. Use Task Tool with Explore Agent

**Tool:** `Task` with `subagent_type: "Explore"`

**When:** Need to explore codebase for patterns or features

**How:**
```javascript
Task(
  subagent_type: "Explore",
  description: "Find error handling patterns",
  prompt: "Search the codebase for error handling patterns in hardware controllers. I need to understand how errors are currently handled across camera, laser, and actuator controllers."
)
```

**When to use:**
- Open-ended codebase exploration
- Finding implementation patterns
- Understanding feature implementations
- Not searching for specific needle (class/function)

**Benefits:**
- More thorough than manual Grep
- Specialized for exploration
- Understands context better
- Provides structured findings

---

## Development & Implementation

### Current Approach
- Direct code writing
- Manual testing
- Sequential implementation

### Recommended Optimization

#### 1. Use Zen Planner for Complex Features

**Tool:** `mcp__zen__planner`

**When:** Implementing multi-step features or architectural changes

**How:**
```javascript
mcp__zen__planner(
  step: "Plan implementation of watchdog timer for hardware controllers",
  step_number: 1,
  total_steps: 5,
  next_step_required: true,
  model: "gpt-5-pro"
)
```

**When to use:**
- Complex features (3+ modules affected)
- Architectural changes
- Migration planning
- System redesign

**Benefits:**
- Structured planning with revision capability
- Branching for alternative approaches
- Expert validation
- Prevents implementation oversights

#### 2. Proactive Code Review with Zen

**Tool:** `mcp__zen__codereview`

**When:** AFTER writing significant code (don't wait for user request)

**How:**
```javascript
// After implementing laser controller
mcp__zen__codereview(
  step: "Review laser controller implementation for safety and quality",
  step_number: 1,
  total_steps: 2,
  next_step_required: true,
  findings: "Reviewing LaserController for safety-critical compliance",
  model: "gemini-2.5-pro",
  review_type: "full",
  relevant_files: [
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/laser_controller.py",
    "C:/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/laser_widget.py"
  ]
)
```

**When to use:**
- After implementing safety-critical code
- Before marking module complete
- After major refactoring
- Before creating PR

**Benefits:**
- Catches issues early
- Ensures safety compliance
- Validates architecture
- Identifies security concerns

#### 3. Use Zen Refactor for Code Improvements

**Tool:** `mcp__zen__refactor`

**When:** Identifying improvement opportunities

**How:**
```javascript
mcp__zen__refactor(
  step: "Analyze hardware controllers for refactoring opportunities",
  step_number: 1,
  total_steps: 2,
  next_step_required: true,
  findings: "Looking for code smells and modernization opportunities",
  model: "gpt-5-codex",
  refactor_type: "codesmells",
  style_guide_examples: [
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/camera_controller.py"
  ]
)
```

**Refactor types:**
- `codesmells` - Identify anti-patterns
- `decompose` - Break down large functions
- `modernize` - Update to modern Python
- `organization` - Improve structure

---

## Testing & Quality Assurance

### Current Approach
- Manual test creation
- Ad-hoc testing
- No automated test generation

### Recommended Optimization

#### 1. Use Zen Testgen for Comprehensive Test Suites

**Tool:** `mcp__zen__testgen`

**When:** After implementing new functionality

**How:**
```javascript
mcp__zen__testgen(
  step: "Generate comprehensive tests for LaserController",
  step_number: 1,
  total_steps: 2,
  next_step_required: true,
  findings: "Analyzing LaserController for test scenarios",
  model: "gemini-2.5-pro",
  relevant_files: [
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/laser_controller.py"
  ]
)
```

**Benefits:**
- Edge case identification
- Comprehensive coverage
- Failure mode analysis
- Framework-specific tests

#### 2. Use Playwright for GUI Testing

**Tools:** `mcp__plugin_testing-suite_playwright-server__*`

**When:** Testing PyQt6 GUI functionality

**How:**
```javascript
// Navigate to local app
mcp__plugin_testing-suite_playwright-server__browser_navigate(
  url: "http://localhost:8000"  // if web-based
)

// Take snapshot for analysis
mcp__plugin_testing-suite_playwright-server__browser_snapshot()

// Interact with elements
mcp__plugin_testing-suite_playwright-server__browser_click(
  element: "Enable Laser button",
  ref: "<ref from snapshot>"
)

// Verify state
mcp__plugin_testing-suite_playwright-server__browser_console_messages()
```

**Benefits:**
- Automated UI testing
- Regression testing
- Accessibility validation
- Visual verification

#### 3. Use Task Tool with Testing Suite Agent

**Tool:** `Task` with `subagent_type: "testing-suite:generate-tests"`

**When:** Need complete test coverage for module

**How:**
```javascript
Task(
  subagent_type: "testing-suite:generate-tests",
  description: "Generate test suite",
  prompt: "Generate comprehensive unit, integration, and edge case tests for src/hardware/laser_controller.py"
)
```

---

## Debugging & Problem Solving

### Current Approach
- Manual debugging
- Print statements
- Sequential investigation

### Recommended Optimization

#### 1. Use Zen Debug for Systematic Debugging

**Tool:** `mcp__zen__debug`

**When:** Encountering bugs or mysterious errors

**How:**
```javascript
mcp__zen__debug(
  step: "Investigate why camera sometimes drops frames",
  step_number: 1,
  total_steps: 4,
  next_step_required: true,
  findings: "User reports intermittent frame drops during streaming",
  hypothesis: "Possible frame rate mismatch or buffer overflow",
  model: "gpt-5-codex",
  confidence: "exploring",
  relevant_files: [
    "C:/Users/wille/Desktop/TOSCA-dev/src/hardware/camera_controller.py"
  ]
)
```

**Benefits:**
- Systematic investigation
- Hypothesis tracking
- Evidence-based debugging
- Root cause analysis

#### 2. Use Zen Challenge for Assumption Verification

**Tool:** `mcp__zen__challenge`

**When:** User questions your conclusions or approach

**How:**
```javascript
mcp__zen__challenge(
  prompt: "The camera API doesn't support frame rate control"
)
```

**Benefits:**
- Prevents reflexive agreement
- Forces critical thinking
- Validates assumptions
- Catches errors early

#### 3. Use Zen ThinkDeep for Complex Problems

**Tool:** `mcp__zen__thinkdeep`

**When:** Architecture decisions, performance issues, security analysis

**How:**
```javascript
mcp__zen__thinkdeep(
  step: "Analyze thread safety in hardware controllers",
  step_number: 1,
  total_steps: 3,
  next_step_required: true,
  findings: "Need to verify thread safety of concurrent hardware access",
  hypothesis: "Camera and laser operations may have race conditions",
  model: "gemini-2.5-pro",
  confidence: "exploring",
  focus_areas: ["architecture", "performance", "security"]
)
```

---

## Documentation & Knowledge Management

### Current Approach
- Manual WORK_LOG.md updates
- Ad-hoc PROJECT_STATUS.md updates
- Memory system underutilized

### Recommended Optimization

#### 1. Proactive Memory System Updates

**Tools:** `mcp__memory__create_entities`, `mcp__memory__add_observations`, `mcp__memory__create_relations`

**When:** After major milestones or discoveries

**How:**
```javascript
// After completing Laser HAL
mcp__memory__add_observations(
  observations: [
    {
      entityName: "Laser Controller HAL",
      contents: [
        "Implementation complete - 100%",
        "Using Arroyo serial protocol with PyQt6 signal integration",
        "Hardware safety interlocks integrated",
        "Tested with hardware - all functions working"
      ]
    }
  ]
)

// Create relation
mcp__memory__create_relations(
  relations: [
    {
      from: "Laser Controller HAL",
      to: "Safety System",
      relationType: "integrates with"
    }
  ]
)
```

**When to update:**
- Module status changes (0% → 100%)
- New lessons learned
- Critical rule discoveries
- Architecture decisions
- Phase transitions

#### 2. Use Zen Consensus for Major Decisions

**Tool:** `mcp__zen__consensus`

**When:** Making important architectural or technology choices

**How:**
```javascript
mcp__zen__consensus(
  step: "Evaluate threading approach for hardware controllers",
  step_number: 1,
  total_steps: 3,
  next_step_required: true,
  findings: "Need to decide between QThread vs threading.Thread",
  models: [
    {model: "gemini-2.5-pro", stance: "for"},
    {model: "gpt-5-pro", stance: "against"},
    {model: "gpt-5-codex", stance: "neutral"}
  ]
)
```

**Benefits:**
- Multi-perspective analysis
- Reduces bias
- Better decisions
- Documented rationale

#### 3. Use Context7 for Library Documentation

**Tool:** `mcp__context7__get-library-docs`

**When:** Need up-to-date API documentation

**How:**
```javascript
// Resolve library first
mcp__context7__resolve-library-id(
  libraryName: "PyQt6"
)

// Get documentation
mcp__context7__get-library-docs(
  context7CompatibleLibraryID: "/PyQt/PyQt6",
  topic: "signals and slots",
  tokens: 5000
)
```

**Benefits:**
- Latest API documentation
- Breaking changes awareness
- Migration guides
- Official examples

---

## Git Workflow Optimization

### Current Approach
- Manual git commands
- Pre-commit hooks for validation
- Manual reminder to update docs

### Recommended Optimization

#### 1. Use Zen Precommit for Change Validation

**Tool:** `mcp__zen__precommit`

**When:** Before creating commits (especially for safety-critical code)

**How:**
```javascript
mcp__zen__precommit(
  step: "Validate changes before committing laser controller",
  step_number: 1,
  total_steps: 3,
  next_step_required: true,
  findings: "Reviewing staged changes for safety and completeness",
  model: "gemini-2.5-pro",
  path: "C:/Users/wille/Desktop/TOSCA-dev",
  include_staged: true,
  include_unstaged: true,
  precommit_type: "external"
)
```

**Benefits:**
- Change impact assessment
- Security review
- Missing test detection
- Documentation verification

#### 2. Use GitHub Integration for Issues/PRs

**Tools:** `mcp__github__*`

**When:** Working with GitHub repository

**How:**
```javascript
// Create issue for bug tracking
mcp__github__create_issue(
  owner: "will-aleyegn",
  repo: "TOSCA_DEV",
  title: "Camera frame drops during high-speed streaming",
  body: "Description of issue...",
  labels: ["bug", "camera-hal"]
)

// Create PR after feature
mcp__github__create_pull_request(
  owner: "will-aleyegn",
  repo: "TOSCA_DEV",
  title: "Implement Laser Controller HAL",
  head: "feature/laser-hal",
  base: "main",
  body: "Complete implementation with tests"
)
```

**Benefits:**
- Better issue tracking
- Code review workflow
- Collaboration support
- Change documentation

---

## Advanced Workflows

### 1. Comprehensive Code Review Workflow

**When:** Completing a major module or phase

**Steps:**
```javascript
// 1. Security audit
mcp__zen__secaudit(
  step: "Security audit of laser controller",
  step_number: 1,
  total_steps: 2,
  findings: "Checking for security vulnerabilities",
  model: "gemini-2.5-pro",
  audit_focus: "owasp",
  threat_level: "high"
)

// 2. Code review
mcp__zen__codereview(
  step: "Full code review",
  step_number: 1,
  total_steps: 2,
  findings: "Comprehensive quality review",
  model: "gpt-5-codex",
  review_type: "full"
)

// 3. Architecture review
mcp__zen__analyze(
  step: "Architecture analysis",
  step_number: 1,
  total_steps: 2,
  findings: "Validating architectural patterns",
  model: "gpt-5-pro",
  analysis_type: "architecture"
)

// 4. Pre-commit validation
mcp__zen__precommit(
  step: "Pre-commit validation",
  step_number: 1,
  total_steps: 3,
  findings: "Final check before commit",
  model: "gemini-2.5-pro"
)
```

### 2. New Module Development Workflow

**When:** Starting a new hardware controller or major feature

**Steps:**
```javascript
// 1. Plan with planner
mcp__zen__planner(
  step: "Plan GPIO controller implementation",
  model: "gpt-5-pro"
)

// 2. Analyze existing patterns
mcp__zen__analyze(
  step: "Analyze existing HAL patterns",
  analysis_type: "architecture"
)

// 3. Implement with Task tool
Task(
  subagent_type: "feature-dev:code-architect",
  prompt: "Design GPIO controller following existing HAL patterns"
)

// 4. Generate tests
mcp__zen__testgen(
  step: "Generate tests for GPIO controller"
)

// 5. Review implementation
mcp__zen__codereview(
  step: "Review GPIO controller implementation"
)

// 6. Update memory
mcp__memory__create_entities(
  entities: [{
    name: "GPIO Controller HAL",
    entityType: "Module",
    observations: ["Implementation complete", "Tests passing"]
  }]
)
```

### 3. Debugging Complex Issues Workflow

**When:** Encountering mysterious bugs or system issues

**Steps:**
```javascript
// 1. Systematic debugging
mcp__zen__debug(
  step: "Debug camera frame drop issue",
  hypothesis: "Frame rate mismatch",
  confidence: "exploring"
)

// 2. Trace execution if needed
mcp__zen__tracer(
  step: "Trace frame acquisition flow",
  trace_mode: "precision"
)

// 3. Deep analysis if still stuck
mcp__zen__thinkdeep(
  step: "Deep analysis of frame handling",
  focus_areas: ["performance", "architecture"]
)

// 4. Challenge assumptions
mcp__zen__challenge(
  prompt: "The hardware supports the frame rate we're requesting"
)

// 5. Document lesson learned
mcp__memory__add_observations(
  observations: [{
    entityName: "Camera HAL",
    contents: ["Lesson: Always check hardware max frame rate before setting"]
  }]
)
```

---

## Tool Selection Decision Tree

### When to Use What

```
Need to understand code?
├─ Quick exploration → Task(Explore agent)
├─ Systematic analysis → mcp__zen__analyze
├─ Execution flow → mcp__zen__tracer
└─ Full codebase → Repomix

Need to implement feature?
├─ Simple (1-2 files) → Direct implementation
├─ Complex (3+ steps) → mcp__zen__planner first
├─ Following patterns → Task(code-architect)
└─ Major architecture → mcp__zen__consensus

Found a bug?
├─ Simple fix → Direct fix
├─ Mystery bug → mcp__zen__debug
├─ Complex issue → mcp__zen__thinkdeep
└─ Assumption check → mcp__zen__challenge

Need tests?
├─ Generate suite → mcp__zen__testgen
├─ GUI testing → Playwright tools
└─ Setup testing → Task(test-automator)

Ready to commit?
├─ Safety-critical → mcp__zen__precommit
├─ Major changes → mcp__zen__precommit
├─ Simple fix → Standard pre-commit hooks
└─ Create PR → GitHub tools

Need documentation?
├─ Library docs → Context7
├─ Update memory → MCP memory tools
├─ Session notes → WORK_LOG.md
└─ Status update → PROJECT_STATUS.md
```

---

## Recommended Tool Combinations

### 1. Session Start (Fast)
```
mcp__memory__search_nodes + Bash(git status/log)
Total time: 30 seconds
```

### 2. New Feature Implementation
```
mcp__zen__planner
→ Task(code-architect) or direct implementation
→ mcp__zen__testgen
→ mcp__zen__codereview
→ mcp__memory__add_observations
Total time: Varies, but systematic
```

### 3. Bug Investigation
```
mcp__zen__debug
→ mcp__zen__tracer (if needed)
→ mcp__zen__thinkdeep (if complex)
→ Fix implementation
→ mcp__memory__add_observations (lesson learned)
```

### 4. Code Quality Sprint
```
mcp__zen__codereview (all modules)
→ mcp__zen__refactor (identify improvements)
→ mcp__zen__secaudit (security check)
→ Implementation of fixes
→ mcp__zen__precommit (validate changes)
```

---

## Integration with Existing Workflow

### Before Work (5 minutes)
1. ✅ `mcp__memory__search_nodes` - Get context
2. ✅ `Bash(git status)` + `Bash(git log)` - Check repo state
3. ✅ Read `WORK_LOG.md` (last 50 lines) - Recent work
4. ⭐ **NEW:** Read `TODO_GUIDELINES.md` - TodoWrite refresher

### During Work
1. ✅ Use `TodoWrite` for multi-step tasks
2. ⭐ **NEW:** Use `Task(Explore)` instead of manual Grep for exploration
3. ⭐ **NEW:** Use `mcp__zen__planner` for complex features
4. ⭐ **NEW:** Use `mcp__zen__analyze` to understand code
5. ✅ Update `WORK_LOG.md` after significant actions

### After Work (10 minutes)
1. ⭐ **NEW:** `mcp__zen__codereview` - Proactive review
2. ⭐ **NEW:** `mcp__zen__testgen` - Generate tests
3. ⭐ **NEW:** `mcp__zen__precommit` - Validate changes
4. ✅ Update `PROJECT_STATUS.md` if milestone
5. ⭐ **NEW:** `mcp__memory__add_observations` - Update memory
6. ✅ Git commit with clear message

---

## Metrics for Success

### Current State (Estimated)
- Tool usage: ~10 tools regularly (Read, Write, Edit, Bash, Grep, Glob, TodoWrite)
- Session startup: 5-10 minutes
- Manual debugging: High
- Proactive review: Low
- Memory updates: Rare

### Target State
- Tool usage: 20+ tools regularly (add Zen suite, Task agents, Memory, Context7)
- Session startup: 30 seconds (memory-based)
- Manual debugging: Low (systematic with Zen tools)
- Proactive review: High (after every module)
- Memory updates: After every milestone

### Key Performance Indicators
- ✅ Session startup time < 1 minute
- ✅ Proactive code review after each module
- ✅ Memory updated within 24h of milestone
- ✅ All complex features use planner
- ✅ All bugs investigated with mcp__zen__debug
- ✅ Test generation for all new code

---

## Implementation Priority

### Phase 1: Quick Wins (Immediate)
1. ✅ Start using `mcp__memory__search_nodes` for session startup
2. ✅ Use `Task(Explore)` instead of manual Grep for exploration
3. ✅ Enable `mcp__zen__challenge` when user questions approach
4. ✅ Use `Context7` for library documentation

### Phase 2: Workflow Integration (1 week)
1. ✅ Use `mcp__zen__codereview` proactively after modules
2. ✅ Use `mcp__zen__debug` for all bug investigations
3. ✅ Use `mcp__zen__planner` for complex features
4. ✅ Update memory after each milestone

### Phase 3: Advanced Optimization (2 weeks)
1. ✅ Implement comprehensive review workflow
2. ✅ Use `mcp__zen__testgen` for all new code
3. ✅ Use `mcp__zen__precommit` before safety-critical commits
4. ✅ Regular `mcp__zen__secaudit` for security

### Phase 4: Full Integration (1 month)
1. ✅ All workflows documented with tool combinations
2. ✅ Memory system fully populated and maintained
3. ✅ Automated quality gates with Zen tools
4. ✅ GitHub integration for issues/PRs

---

## Examples of Tool Usage in Context

### Example 1: Starting New Session

**Current:**
```
User: "Continue working on TOSCA"
AI: "Let me read PROJECT_STATUS.md, WORK_LOG.md, git status..."
[5-10 minutes of file reading]
```

**Optimized:**
```
User: "Continue working on TOSCA"
AI: [Parallel tool calls in single message]
  - mcp__memory__search_nodes("TOSCA Project")
  - mcp__memory__search_nodes("Development Workflow")
  - Bash("git log --oneline -10")
  - Bash("git status")
AI: "Based on memory: You're in Phase 5 Testing (Week 1 complete). Last work was real-time safety monitoring. Recommend continuing with Week 2: Unit Test Coverage. Ready to proceed?"
[30 seconds total]
```

### Example 2: Implementing New Feature

**Current:**
```
User: "Implement GPIO controller"
AI: [Writes code directly]
AI: "Here's the GPIO controller implementation"
```

**Optimized:**
```
User: "Implement GPIO controller"
AI: [Uses planner first]
  mcp__zen__planner(
    step: "Plan GPIO controller matching existing HAL patterns",
    model: "gpt-5-pro"
  )
AI: "I've planned the GPIO controller implementation. Here's the approach:
     1. Follow camera/laser/actuator HAL patterns
     2. Use FT232H for digital I/O
     3. MCP3008 for analog (photodiode)
     4. PyQt6 signals for events
     5. Thread-safe operation
     Ready to implement?"
User: "Yes"
AI: [Implements with confidence, following plan]
AI: [After implementation]
  mcp__zen__codereview(relevant_files: ["gpio_controller.py"])
AI: "Implementation complete and reviewed. Found 2 minor improvements..."
```

### Example 3: Debugging Issue

**Current:**
```
User: "Camera sometimes drops frames"
AI: "Let me look at the camera controller code..."
[Manual investigation, adding prints, testing]
AI: "I think it might be the frame rate..."
```

**Optimized:**
```
User: "Camera sometimes drops frames"
AI: [Uses systematic debugging]
  mcp__zen__debug(
    step: "Investigate camera frame drops",
    hypothesis: "Frame rate mismatch or buffer overflow",
    confidence: "exploring"
  )
AI: [Systematic investigation over 3 steps]
  - Check logs and configuration
  - Trace frame acquisition flow
  - Test hardware capabilities
AI: "Root cause identified: Hardware max frame rate is 30 FPS, but we were requesting 60 FPS. Fix: Add validation before setting frame rate."
AI: [Updates memory]
  mcp__memory__add_observations(
    observations: [{
      entityName: "Camera HAL",
      contents: ["Always validate requested frame rate against hardware max (get_info().get_max_frame_rate())"]
    }]
  )
```

---

## Conclusion

The TOSCA project has excellent documentation and workflows. The main optimization opportunity is **proactive use of specialized tools** rather than relying on manual processes.

**Key Recommendations:**
1. ✅ Use MCP memory for fast session startup
2. ✅ Use Zen tools (debug, codereview, analyze, planner) proactively
3. ✅ Use Task agents for exploration and specialized work
4. ✅ Update memory system after every milestone
5. ✅ Leverage Context7 for library documentation
6. ✅ Use GitHub integration for better collaboration

**Expected Benefits:**
- 90% reduction in session startup time (10 min → 30 sec)
- Better code quality through proactive review
- Faster debugging through systematic approach
- Better knowledge retention through memory updates
- More efficient codebase understanding through specialized tools

---

**Last Updated:** 2025-10-26
**Next Review:** After implementing Phase 1 recommendations
**Owner:** Development Team
**Status:** Active recommendations for continuous improvement
