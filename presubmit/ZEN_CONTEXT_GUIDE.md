# Zen Context Helper - Usage Guide

**Purpose:** Automatically load project context when using Zen MCP tools

**Philosophy:** External models (GPT-5, Gemini, etc.) get FULL project understanding by default

**Location:** `presubmit/zen_context_helper.py`

---

## Quick Start

### Import and Use

```python
# Import the helper
from presubmit.zen_context_helper import (
    zen_codereview, zen_debug, zen_consensus,
    zen_secaudit, zen_planner, zen_analyze,
    zen_refactor, zen_testgen, zen_chat
)

# Use with automatic context loading
result = zen_codereview(
    step="Review protocol worker for thread safety",
    code_files=["src/ui/workers/protocol_worker.py"],
    model="gpt-5-pro"
)

# Result contains all parameters ready for mcp__zen__codereview
# Automatically includes: ONBOARDING, SESSION_STATE, DECISIONS, CODING_STANDARDS, GIT_POLICY
```

---

## Context Packages

### Full Context (DEFAULT)

**8 files, ~1200 lines - Maximum understanding**

Includes:
- ✅ `ONBOARDING.md` - Project overview, tech stack
- ✅ `SESSION_STATE.md` - Current phase, recent commits
- ✅ `DECISIONS.md` - Architecture decision records
- ✅ `HISTORY.md` - Compressed monthly summaries
- ✅ `WORK_LOG.md` - Detailed recent history (14 days)
- ✅ `docs/architecture/01_system_overview.md`
- ✅ `docs/architecture/03_safety_system.md`
- ✅ `docs/architecture/04_treatment_protocols.md`

**When to use:** Default for all operations (erring on side of more info)

---

### Code Review Context

**5 files, ~900 lines - Optimized for code quality**

Full Context PLUS:
- ✅ `CODING_STANDARDS.md` - Code quality requirements
- ✅ `GIT_CONTENT_POLICY.md` - Git workflow standards

**Auto-used by:** `zen_codereview()`

---

### Security Context

**9 files, ~1300 lines - Maximum security analysis**

Full Context PLUS:
- ✅ Extra emphasis on safety architecture

**Auto-used by:** `zen_secaudit()`

---

### Planning Context

**6 files, ~1000 lines - Strategic planning**

Core Context PLUS:
- ✅ `HISTORY.md` - Historical evolution
- ✅ Architecture overview and protocols

**Auto-used by:** `zen_planner()`, `zen_consensus()`

---

### Core Context

**3 files, ~700 lines - Essential minimum**

- ✅ `ONBOARDING.md`
- ✅ `SESSION_STATE.md`
- ✅ `DECISIONS.md`

**Auto-used by:** `zen_chat()`

---

### Lightweight Context

**1 file, ~163 lines - Quick operations only**

- ✅ `SESSION_STATE.md` only

**When to use:** Token budget constraints, very quick questions

---

## Tool-by-Tool Guide

### 1. Code Review (zen_codereview)

**Auto-loads:** Code Review Context (5 files, ~900 lines)

```python
from presubmit.zen_context_helper import zen_codereview

result = zen_codereview(
    step="Review protocol worker for thread safety and signal handling",
    code_files=[
        "src/ui/workers/protocol_worker.py",
        "src/ui/widgets/active_treatment_widget.py"
    ],
    findings="Worker pattern implemented, need to validate signal connections",
    model="gpt-5-pro",
    review_type="full",  # or "security", "performance", "quick"
    step_number=1,
    total_steps=2
)

# Automatically includes:
# - ONBOARDING, SESSION_STATE, DECISIONS (core)
# - CODING_STANDARDS, GIT_POLICY (code review specific)
# - Your code files
```

**Parameters:**
- `step`: Review plan/findings (required)
- `code_files`: Files to review (required)
- `findings`: Current findings (default: "")
- `model`: "gpt-5-pro", "gemini-2.5-pro", etc. (default: "gpt-5-pro")
- `review_type`: "full", "security", "performance", "quick" (default: "full")
- `context_level`: "code_review", "full", "core" (default: "code_review")

---

### 2. Debug Investigation (zen_debug)

**Auto-loads:** Full Context (8 files, ~1200 lines)

```python
from presubmit.zen_context_helper import zen_debug

result = zen_debug(
    step="Investigate GUI freezing during protocol execution",
    code_files=["src/ui/workers/protocol_worker.py"],
    findings="GUI unresponsive for 5-10s after Start Treatment clicked. E-stop button doesn't work.",
    hypothesis="Worker not properly moved to thread, or signals blocked",
    confidence="low",  # Will increase as investigation progresses
    model="gpt-5-pro",
    step_number=1,
    total_steps=3
)

# Automatically includes:
# - Full context (8 files) for comprehensive debugging
# - Your code files
```

**Parameters:**
- `step`: Investigation plan (required)
- `code_files`: Files related to bug (required)
- `findings`: Current discoveries (required)
- `hypothesis`: Current theory (required)
- `confidence`: "exploring", "low", "medium", "high", "very_high", "almost_certain", "certain" (default: "low")
- `model`: Model to use (default: "gpt-5-pro")
- `context_level`: "full", "core", "lightweight" (default: "full")

---

### 3. Multi-Model Consensus (zen_consensus)

**Auto-loads:** Planning Context (6 files, ~1000 lines)

```python
from presubmit.zen_context_helper import zen_consensus

result = zen_consensus(
    step="Should we use REST API or WebSocket for real-time sensor data?",
    models=[
        {"model": "gpt-5-pro", "stance": "for"},        # Advocate for REST
        {"model": "gemini-2.5-pro", "stance": "against"},  # Advocate for WebSocket
        {"model": "gpt-5-codex", "stance": "neutral"}   # Objective analysis
    ],
    findings="Current system uses PyQt6 signals. Need remote monitoring capability.",
    relevant_files=["src/hardware/gpio_controller.py"],
    step_number=1
)

# Automatically includes:
# - Planning context (6 files) for strategic decisions
# - Your relevant files
```

**Parameters:**
- `step`: Question or proposal (required)
- `models`: List with model/stance pairs (required)
- `findings`: Your independent analysis (default: "")
- `relevant_files`: Task-specific files (optional)
- `context_level`: "planning", "full", "core" (default: "planning")

---

### 4. Security Audit (zen_secaudit)

**Auto-loads:** Security Context (9 files, ~1300 lines)

```python
from presubmit.zen_context_helper import zen_secaudit

result = zen_secaudit(
    step="Security audit of manual override widget for FDA compliance",
    security_files=["src/ui/widgets/manual_override_widget.py"],
    security_scope="Medical device with FDA and HIPAA compliance requirements",
    findings="Dev-mode widget allows safety overrides, need to validate protection",
    audit_focus="compliance",  # or "owasp", "infrastructure", "dependencies"
    threat_level="critical",   # Medical device - high stakes
    compliance_requirements=["FDA", "HIPAA"],
    model="gpt-5-pro",
    step_number=1,
    total_steps=3
)

# Automatically includes:
# - Security context (9 files) including all safety architecture
# - Your security-critical files
```

**Parameters:**
- `step`: Audit plan (required)
- `security_files`: Files to audit (required)
- `security_scope`: Context description (required)
- `findings`: Current findings (default: "")
- `audit_focus`: "owasp", "compliance", "infrastructure", "dependencies", "comprehensive" (default: "comprehensive")
- `threat_level`: "low", "medium", "high", "critical" (default: "medium")
- `context_level`: "security", "full" (default: "security")

---

### 5. Strategic Planning (zen_planner)

**Auto-loads:** Planning Context (6 files, ~1000 lines)

```python
from presubmit.zen_context_helper import zen_planner

result = zen_planner(
    step="Plan refactoring of camera module to use VmbPy 2.0 API",
    model="gemini-2.5-pro",  # Excellent for planning
    relevant_files=["src/hardware/camera_controller.py"],
    step_number=1,
    total_steps=5  # Iterative planning
)

# Automatically includes:
# - Planning context (6 files) for strategic decisions
# - Historical evolution and patterns
```

**Parameters:**
- `step`: Planning content (required)
- `model`: Model to use (default: "gemini-2.5-pro")
- `relevant_files`: Additional context (optional)
- `context_level`: "planning", "full" (default: "planning")

---

### 6. Code Analysis (zen_analyze)

**Auto-loads:** Full Context (8 files, ~1200 lines)

```python
from presubmit.zen_context_helper import zen_analyze

result = zen_analyze(
    step="Analyze safety manager architecture and interlock logic",
    analysis_files=[
        "src/core/safety.py",
        "src/core/safety_watchdog.py"
    ],
    findings="Need to understand state machine transitions and failure modes",
    analysis_type="architecture",  # or "performance", "security", "quality", "general"
    model="gemini-2.5-pro",  # Great for analysis
    step_number=1,
    total_steps=3
)

# Automatically includes:
# - Full context (8 files) for comprehensive understanding
```

**Parameters:**
- `step`: Analysis plan (required)
- `analysis_files`: Files to analyze (required)
- `findings`: Current findings (default: "")
- `analysis_type`: "architecture", "performance", "security", "quality", "general" (default: "general")
- `model`: Model to use (default: "gemini-2.5-pro")

---

### 7. Refactoring Analysis (zen_refactor)

**Auto-loads:** Full Context (8 files, ~1200 lines)

```python
from presubmit.zen_context_helper import zen_refactor

result = zen_refactor(
    step="Analyze main_window.py for decomposition opportunities",
    refactor_files=["src/ui/main_window.py"],
    findings="File has 800 lines, multiple responsibilities, needs decomposition",
    refactor_type="decompose",  # or "codesmells", "modernize", "organization"
    confidence="incomplete",
    model="gpt-5-codex",  # Good for code patterns
    step_number=1,
    total_steps=2
)

# Automatically includes:
# - Full context (8 files) including patterns to follow
```

**Parameters:**
- `step`: Refactoring plan (required)
- `refactor_files`: Files to refactor (required)
- `findings`: Opportunities found (default: "")
- `refactor_type`: "codesmells", "decompose", "modernize", "organization" (default: "codesmells")
- `confidence`: "exploring", "incomplete", "partial", "complete" (default: "incomplete")

---

### 8. Test Generation (zen_testgen)

**Auto-loads:** Full Context (8 files, ~1200 lines)

```python
from presubmit.zen_context_helper import zen_testgen

result = zen_testgen(
    step="Generate comprehensive tests for protocol selector with edge cases",
    test_files=["src/ui/widgets/protocol_selector_widget.py"],
    findings="Need tests for: file not found, invalid JSON, empty directory, missing protocols",
    model="gpt-5-codex",  # Excellent for test generation
    step_number=1,
    total_steps=2
)

# Automatically includes:
# - Full context (8 files) including test patterns
```

**Parameters:**
- `step`: Test plan (required)
- `test_files`: Files needing tests (required)
- `findings`: Test scenarios identified (default: "")
- `model`: Model to use (default: "gpt-5-codex")

---

### 9. Casual Chat (zen_chat)

**Auto-loads:** Core Context (3 files, ~700 lines)

```python
from presubmit.zen_context_helper import zen_chat

# First conversation
result1 = zen_chat(
    prompt="Explain the pros and cons of QStackedWidget vs QTabWidget for medical device UIs",
    task_files=["src/ui/main_window.py"],
    model="gemini-2.5-pro"
)

# Follow-up (reuse context)
result2 = zen_chat(
    prompt="Now explain how to test the QStackedWidget transitions",
    continuation_id=result1["continuation_id"],  # Preserves context!
    model="gemini-2.5-pro"
)

# Automatically includes:
# - Core context (3 files) for chat
```

**Parameters:**
- `prompt`: Your question (required)
- `task_files`: Optional files for context
- `model`: Model to use (default: "gemini-2.5-pro")
- `context_level`: "core", "full", "lightweight" (default: "core")
- `continuation_id`: Reuse previous conversation (optional)

---

## Manual Context Control

### Get Context Packages Directly

```python
from presubmit.zen_context_helper import (
    get_full_context,
    get_core_context,
    get_lightweight_context,
    get_code_review_context,
    get_security_context,
    get_planning_context
)

# Get specific context package
full = get_full_context()  # Returns list of 8 absolute file paths

# Manually combine with your files
my_files = ["src/my_file.py"]
all_files = full + my_files
```

---

### Combine Context with Custom Files

```python
from presubmit.zen_context_helper import combine_context

files = combine_context(
    task_files=["src/ui/widgets/protocol_selector.py"],
    context_level="full",  # or "core", "lightweight", etc.
    additional_context=["docs/ui_guidelines.md"]  # Extra files
)

# Returns: [context files...] + [additional...] + [task files...]
```

---

### Validate Context Files

```python
from presubmit.zen_context_helper import validate_context_files

# Check which context files exist
validation = validate_context_files()

for name, exists in validation.items():
    status = "✅" if exists else "❌"
    print(f"{status} {name}")

# Output:
# ✅ ONBOARDING.md
# ✅ SESSION_STATE.md
# ✅ DECISIONS.md
# ✅ HISTORY.md
# etc.
```

---

## Real-World Examples

### Example 1: Code Review Before Commit

```python
from presubmit.zen_context_helper import zen_codereview

# Review recent changes
result = zen_codereview(
    step="Review protocol worker implementation before committing",
    code_files=[
        "src/ui/workers/protocol_worker.py",
        "src/ui/widgets/active_treatment_widget.py"
    ],
    findings="""
    Implemented Worker + moveToThread pattern per DECISIONS.md #002.
    Signals: progress_update, action_complete, protocol_complete, error_occurred.
    Need validation of thread lifecycle and signal connections.
    """,
    review_type="full",
    model="gpt-5-pro"
)

# Result includes all parameters ready for mcp__zen__codereview
# Model gets full context: decisions (why Worker pattern), standards, current state
```

---

### Example 2: Debug Investigation

```python
from presubmit.zen_context_helper import zen_debug

# Step 1: Initial investigation
result1 = zen_debug(
    step="Investigate GPIO timeout causing false safety shutdown",
    code_files=[
        "src/hardware/gpio_controller.py",
        "src/core/safety_watchdog.py"
    ],
    findings="Watchdog timeout after 2 seconds of motor operation. Motor takes 3s to stabilize.",
    hypothesis="Missing heartbeat chunks during motor acceleration",
    confidence="low",
    step_number=1,
    total_steps=3
)

# Step 2: Deeper investigation (after model analysis)
result2 = zen_debug(
    step="Verified hypothesis - motor acceleration uses time.sleep(3.0) without heartbeat chunks",
    code_files=[
        "src/hardware/gpio_controller.py"
    ],
    findings="Found sleep(3.0) in _accelerate_motor() method. Per DECISIONS.md #006, must chunk delays.",
    hypothesis="Need to implement chunked delay pattern: sleep(0.4) with heartbeat after each chunk",
    confidence="high",
    step_number=2,
    total_steps=3
)

# Model knows about Watchdog Heartbeat Pattern (DECISIONS.md #006) automatically!
```

---

### Example 3: Architecture Decision

```python
from presubmit.zen_context_helper import zen_consensus

# Get multi-model input on important decision
result = zen_consensus(
    step="""
    Should we implement automated protocol validation checks on load,
    or require manual validation by operator before execution?

    Context: Medical device safety-critical system.
    FDA requires validation, but question is automated vs manual.
    """,
    models=[
        {
            "model": "gpt-5-pro",
            "stance": "for",
            "stance_prompt": "Argue for automated validation - consistency and error prevention"
        },
        {
            "model": "gemini-2.5-pro",
            "stance": "against",
            "stance_prompt": "Argue for manual validation - operator awareness and control"
        },
        {
            "model": "gpt-5-codex",
            "stance": "neutral",
            "stance_prompt": "Objective analysis considering FDA requirements"
        }
    ],
    findings="""
    Current system loads protocols without validation.
    Risk: Invalid protocols could reach execution.
    Benefit of auto: Catches errors early.
    Benefit of manual: Operator stays engaged with protocol details.
    """,
    relevant_files=[
        "src/ui/widgets/protocol_selector_widget.py",
        "src/core/protocol_engine.py"
    ]
)

# Models get full context including:
# - Medical device safety philosophy (ONBOARDING)
# - Past safety decisions (DECISIONS)
# - Current architecture
```

---

### Example 4: Security Audit

```python
from presubmit.zen_context_helper import zen_secaudit

result = zen_secaudit(
    step="""
    Comprehensive security audit of manual override system.
    Focus on production protection and dev-mode isolation.
    """,
    security_files=[
        "src/ui/widgets/manual_override_widget.py",
        "src/core/safety.py",
        "config.yaml"
    ],
    security_scope="""
    Medical device laser control system (FDA Class II).
    Manual overrides for development/testing only.
    Must be completely disabled in production builds.
    Safety interlocks protect against misuse.
    HIPAA compliant for patient data.
    """,
    findings="""
    Widget checks config.dev_mode flag.
    Override buttons disabled if dev_mode=false.
    Need to verify: config protection, build-time checks, audit logging.
    """,
    audit_focus="compliance",
    threat_level="critical",
    compliance_requirements=["FDA 21 CFR Part 820", "HIPAA", "IEC 60601"],
    model="gpt-5-pro",
    step_number=1,
    total_steps=3
)

# Model gets full security context including:
# - Selective shutdown policy (DECISIONS.md #003)
# - Safety architecture documentation
# - All compliance requirements
```

---

## Pro Tips

### 1. Use Continuation IDs for Multi-Turn Conversations

```python
# First call
result1 = zen_chat(
    prompt="Explain Worker pattern in our codebase",
    task_files=["src/ui/workers/protocol_worker.py"],
    model="gpt-5-pro"
)

# Follow-up (context preserved!)
result2 = zen_chat(
    prompt="Now show how to test Worker pattern",
    continuation_id=result1["continuation_id"],  # Reuse context
    model="gpt-5-pro"
)

# Third follow-up
result3 = zen_chat(
    prompt="What about error handling in Workers?",
    continuation_id=result2["continuation_id"],
    model="gpt-5-pro"
)
```

---

### 2. Override Context Level When Needed

```python
# Use lightweight for quick question
result = zen_chat(
    prompt="Quick: what's the current project version?",
    context_level="lightweight",  # Just SESSION_STATE
    model="gpt-5-mini"  # Cheaper model
)

# Use full for important analysis
result = zen_analyze(
    step="Deep analysis of safety architecture",
    analysis_files=["src/core/safety.py"],
    context_level="full",  # All 8 files
    model="gpt-5-pro"
)
```

---

### 3. Model Selection by Task

```python
# Planning: gemini-2.5-pro (1M context window, excellent strategic thinking)
zen_planner(step="Plan Phase 4 implementation", model="gemini-2.5-pro")

# Code review: gpt-5-pro (strong analysis, good at finding issues)
zen_codereview(code_files=["..."], model="gpt-5-pro")

# Test generation: gpt-5-codex (specialized for code)
zen_testgen(test_files=["..."], model="gpt-5-codex")

# Chat: gemini-2.5-pro (conversational, handles complex questions)
zen_chat(prompt="...", model="gemini-2.5-pro")

# Security: gpt-5-pro (thorough analysis)
zen_secaudit(security_files=["..."], model="gpt-5-pro")
```

---

### 4. Reference Decisions in Prompts

```python
# Explicitly reference architectural decisions
zen_codereview(
    step="""
    Review Worker implementation against DECISIONS.md #002 requirements:
    - Worker is QObject (not QThread)
    - moveToThread() pattern used
    - Signals for cross-thread communication
    - Proper lifecycle management
    """,
    code_files=["src/ui/workers/protocol_worker.py"]
)

# Model has DECISIONS.md in context and can validate against it!
```

---

## Troubleshooting

### Problem: "File not found" errors

**Solution:** Validate context files exist

```python
from presubmit.zen_context_helper import validate_context_files

validation = validate_context_files()
for name, exists in validation.items():
    if not exists:
        print(f"Missing: {name}")
```

---

### Problem: Want different context for specific tool

**Solution:** Override `context_level` parameter

```python
# Default is "full", but you can change it
zen_debug(
    step="Quick debug check",
    code_files=["..."],
    context_level="core"  # Use core instead of full
)
```

---

### Problem: Need additional context files

**Solution:** Use `combine_context()` manually

```python
from presubmit.zen_context_helper import combine_context

custom_files = combine_context(
    task_files=["src/my_file.py"],
    context_level="full",
    additional_context=[
        "docs/custom_guidelines.md",
        "specs/requirements.txt"
    ]
)

# Use custom_files with manual MCP call if needed
```

---

## Summary

✅ **Default behavior:** FULL context (8 files, ~1200 lines) - erring on side of more info

✅ **Automatic:** Just call `zen_*()` functions, context loaded automatically

✅ **Customizable:** Override `context_level` if needed

✅ **Optimized:** Each tool gets appropriate context (code_review, security, planning, etc.)

✅ **Continuation:** Use `continuation_id` to preserve conversation context

✅ **Validation:** Check which context files exist with `validate_context_files()`

---

**Next Step:** Try it out!

```python
from presubmit.zen_context_helper import zen_chat

result = zen_chat(
    prompt="What's the current state of the project?",
    model="gemini-2.5-pro"
)

# Model automatically gets: ONBOARDING, SESSION_STATE, DECISIONS
# Knows: Architecture, recent work, current phase, why things are the way they are
```

---

**Document Version:** 1.0.0
**Created:** 2025-10-28
**Purpose:** Comprehensive guide for using Zen Context Helper
**Philosophy:** External models deserve same fast context you get
