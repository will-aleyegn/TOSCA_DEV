# Quick Start Guide - Using Zen Tools in New Sessions

**Purpose:** Simple step-by-step guide for starting new AI sessions and using zen MCP tools

**For:** Developers new to the zen tool workflow

**Reading Time:** 5 minutes

---

## 🚀 Starting a New Session

### What Happens Automatically

When you start a new AI session, the AI will:

1. **Check for SESSION_STATE.md** - If it exists, the AI knows this is a RESUMING session
2. **Read ONBOARDING.md** - The AI gets project context automatically
3. **Determine session type** - Either FRESH START or RESUMING

**You don't need to do anything special - just start asking questions!**

---

## 📋 Three Ways to Use Zen Tools

### Method 1: Let AI Suggest (RECOMMENDED for beginners)

**How it works:** Just describe what you want. The AI will suggest appropriate tools if needed.

**Example:**
```
You: "I want to review the protocol worker code for thread safety issues"

AI: "I'll help you review the protocol worker for thread safety. Since this
     requires deep analysis, I recommend using the zen:codereview tool which
     will give you expert validation from GPT-5.

     Let me call zen_codereview with full project context..."

[AI automatically calls the tool with proper context]
```

**When to use:** When you're not sure which tool is best, or just want to work naturally.

---

### Method 2: Request a Specific Tool (EXPLICIT)

**How it works:** Directly ask for a specific zen tool by name.

**Example:**
```
You: "Use zen:debug to investigate why the GUI freezes during protocol execution"

AI: "I'll use the zen:debug tool to systematically investigate the GUI freezing issue."

[AI calls zen_debug with appropriate parameters]
```

**When to use:** When you know exactly which tool you want (after reading the guide).

---

### Method 3: Use Helper Functions (ADVANCED)

**How it works:** Give the AI specific function calls with parameters.

**Example:**
```
You: "Call zen_codereview with these parameters:
     - step: 'Review protocol worker implementation'
     - code_files: ['src/ui/workers/protocol_worker.py']
     - model: 'gpt-5-pro'
     - review_type: 'full'"

AI: "I'll call zen_codereview with those exact parameters..."

[AI executes the function call as specified]
```

**When to use:** When you want precise control over parameters.

---

## 🎯 Step-by-Step Scenarios

### Scenario 1: Code Review (Most Common)

**Step 1: Start Fresh**
```
You: "I just finished implementing the protocol selector widget.
      Can you review it for quality and best practices?"
```

**Step 2: AI Responds**
```
AI: "I'll review your protocol selector widget implementation. Since this
     is a code quality review, I'll use zen:codereview which provides expert
     analysis from GPT-5 with full project context.

     Let me review:
     - src/ui/widgets/protocol_selector_widget.py

     The tool will automatically include:
     - Your coding standards (CODING_STANDARDS.md)
     - Architecture decisions (DECISIONS.md)
     - Current project state (SESSION_STATE.md)

     Starting code review..."
```

**Step 3: AI Calls Tool Automatically**
```python
[Behind the scenes:]
from presubmit.zen_context_helper import zen_codereview

zen_codereview(
    step="Review protocol selector widget implementation for code quality",
    code_files=["src/ui/widgets/protocol_selector_widget.py"],
    findings="Widget provides dual loading (list + file browser), preview panel",
    model="gpt-5-pro",
    review_type="full"
)
```

**Step 4: AI Presents Results**
```
AI: "Code review complete! Here are the findings:

✅ Strengths:
- Well-structured signal/slot architecture
- Good error handling for missing files
- Clear separation of UI and logic

⚠️ Issues Found:
- [MEDIUM] Missing type hints on 3 methods
- [LOW] Could benefit from more comprehensive docstrings

Recommendations:
1. Add type hints to _load_protocol(), _preview_protocol(), _refresh_list()
2. Document the protocol validation logic in docstrings
3. Consider adding unit tests for error conditions

Overall: Good implementation with minor improvements needed."
```

---

### Scenario 2: Debugging a Problem

**Step 1: Describe the Bug**
```
You: "The GUI freezes for 5-10 seconds when I click Start Treatment,
      and the E-stop button doesn't respond. Can you help debug this?"
```

**Step 2: AI Analyzes and Suggests Tool**
```
AI: "That sounds like a thread safety issue - GUI freezing suggests the main
     thread is blocked. I'll use zen:debug to systematically investigate.

     This will:
     - Analyze the protocol worker implementation
     - Check signal/slot connections
     - Validate Worker + moveToThread pattern
     - Reference our architecture decision (ADR #002) on Worker patterns

     Starting debug investigation..."
```

**Step 3: AI Investigates**
```python
[Behind the scenes:]
from presubmit.zen_context_helper import zen_debug

zen_debug(
    step="Investigate GUI freezing during protocol execution",
    code_files=["src/ui/workers/protocol_worker.py",
                "src/ui/widgets/active_treatment_widget.py"],
    findings="GUI unresponsive for 5-10s after Start Treatment. E-stop doesn't work.",
    hypothesis="Worker not properly moved to thread, or signals blocked",
    confidence="low",
    model="gpt-5-pro"
)
```

**Step 4: AI Reports Findings**
```
AI: "Root cause identified!

🔍 Problem:
- In active_treatment_widget.py line 245, you're calling
  self.worker.execute_protocol() directly instead of using signals
- This runs the protocol in the MAIN THREAD, blocking the GUI

💡 Solution:
Per DECISIONS.md #002 (Worker pattern), you should:
1. Connect worker.start_execution signal to execute_protocol method
2. Use thread.started.connect(worker.start_execution)
3. Never call worker methods directly

Here's the fix: [code snippet]

Confidence: HIGH - This matches the exact pattern described in our
Worker pattern decision."
```

---

### Scenario 3: Architecture Decision

**Step 1: Ask for Multi-Model Input**
```
You: "Should we add automated protocol validation on load, or require
      manual validation by the operator? This is for a medical device,
      so safety is critical. I want input from multiple AI models."
```

**Step 2: AI Recognizes Need for Consensus**
```
AI: "This is an important architectural decision for a safety-critical
     system. I'll use zen:consensus to get input from multiple expert
     models (GPT-5 and Gemini 2.5 Pro) with different perspectives.

     I'll set up:
     - GPT-5 arguing FOR automated validation (consistency/error prevention)
     - Gemini arguing FOR manual validation (operator awareness/control)
     - Objective analysis considering FDA requirements

     Starting multi-model consensus..."
```

**Step 3: AI Orchestrates Consensus**
```python
[Behind the scenes:]
from presubmit.zen_context_helper import zen_consensus

zen_consensus(
    step="""
    Should we implement automated protocol validation on load,
    or require manual validation by operator before execution?

    Context: Medical device, FDA compliance required.
    """,
    models=[
        {"model": "gpt-5-pro", "stance": "for"},
        {"model": "gemini-2.5-pro", "stance": "against"}
    ],
    findings="Current system loads without validation. Risk vs benefit analysis needed.",
    relevant_files=["src/ui/widgets/protocol_selector_widget.py"]
)
```

**Step 4: AI Synthesizes Recommendation**
```
AI: "Consensus reached after analyzing both perspectives:

🤖 GPT-5 Perspective (Automated):
- Consistency: Catches 100% of validation errors
- FDA compliance: Documented validation process
- Reduces human error during busy procedures
- Con: Operator may become complacent

🤖 Gemini Perspective (Manual):
- Operator awareness: Forces engagement with protocol details
- Flexibility: Allows experienced operators to proceed quickly
- Safety culture: Promotes active verification
- Con: Risk of operator fatigue, skipping validation

✅ RECOMMENDATION: Hybrid Approach
1. Automated validation ALWAYS runs (catches errors)
2. Operator MUST acknowledge validation results
3. Display validation summary (forces reading)
4. Log both automated and manual verification for FDA audit trail

This combines safety of automation with awareness of manual checks.

Confidence: HIGH - Both models agreed hybrid approach best for medical devices."
```

---

### Scenario 4: Security Audit

**Step 1: Request Security Review**
```
You: "I need a security audit of the manual override widget. It allows
      bypassing safety interlocks in dev mode, and I want to make sure
      it's properly protected in production."
```

**Step 2: AI Uses Security Tool**
```
AI: "Security audit for safety-critical code - I'll use zen:secaudit with
     the security context package. This includes:
     - OWASP Top 10 analysis
     - FDA compliance checks
     - Safety architecture review

     Starting comprehensive security audit..."
```

**Step 3: AI Performs Audit**
```python
[Behind the scenes:]
from presubmit.zen_context_helper import zen_secaudit

zen_secaudit(
    step="Security audit of manual override widget for FDA compliance",
    security_files=["src/ui/widgets/manual_override_widget.py",
                    "src/core/safety.py",
                    "config.yaml"],
    security_scope="Medical device (FDA Class II) with dev-mode overrides",
    findings="Widget checks dev_mode flag. Need to verify protection.",
    audit_focus="compliance",
    threat_level="critical",
    compliance_requirements=["FDA 21 CFR Part 820", "HIPAA"]
)
```

**Step 4: AI Reports Security Findings**
```
AI: "Security audit complete:

🔒 CRITICAL FINDINGS:
1. ❌ config.yaml is version controlled - dev_mode flag could be modified
2. ❌ No runtime verification that build is production (could be bypassed)
3. ⚠️ No audit logging when overrides are used

🔒 GOOD PRACTICES FOUND:
✅ Widget checks dev_mode flag correctly
✅ Override buttons disabled when dev_mode=false
✅ Visual indicators show override state

📋 RECOMMENDATIONS:
1. Remove config.yaml from git (use config.yaml.example)
2. Add build-time flag: PRODUCTION_BUILD=True (hardcoded in binary)
3. Implement audit logging: All override attempts logged to secure DB
4. Add startup check: Verify production build matches expected signature
5. Physical security: Require key switch or supervisor code for dev mode

FDA Compliance: Current implementation FAILS 21 CFR Part 820.70(i) -
Production devices must not contain debug/override features.

ACTION REQUIRED: Implement production build system before clinical use."
```

---

## 🎨 Quick Reference: When to Use Each Tool

| Tool | Use When | Example Prompt |
|------|----------|---------------|
| `zen:codereview` | Reviewing code quality | "Review my protocol worker implementation" |
| `zen:debug` | Investigating bugs | "Debug the GUI freezing issue" |
| `zen:consensus` | Important decisions needing multiple perspectives | "Should we use REST or WebSocket? Get multi-model input" |
| `zen:secaudit` | Security/compliance reviews | "Audit the manual override widget for FDA compliance" |
| `zen:planner` | Planning complex features | "Plan the refactoring of the camera module" |
| `zen:analyze` | Understanding existing code | "Analyze the safety manager architecture" |
| `zen:refactor` | Finding refactoring opportunities | "Find code smells in main_window.py" |
| `zen:testgen` | Generating tests | "Generate tests for protocol selector with edge cases" |
| `zen:chat` | Quick questions | "Quick: what's the Worker pattern we use?" |

---

## 💬 Example Prompts That Work Well

### ✅ Good Prompts (Clear Intent)

```
"Review the protocol worker code for thread safety issues"
→ AI uses zen:codereview with thread safety focus

"Debug why the watchdog timeout is triggering after 2 seconds"
→ AI uses zen:debug to investigate timing issue

"I need to decide between QStackedWidget and QTabWidget for the treatment UI.
 Get input from multiple models."
→ AI uses zen:consensus with architecture focus

"Audit the authentication system for HIPAA compliance"
→ AI uses zen:secaudit with compliance focus

"What's the current project status and what should I work on next?"
→ AI reads SESSION_STATE.md (no tool needed)
```

### ❌ Unclear Prompts (AI will ask for clarification)

```
"Fix the bug"
→ Which bug? AI will ask for details

"Make it better"
→ What specifically? AI will ask for scope

"Use zen"
→ Which zen tool? AI will suggest options
```

---

## 🔧 Advanced: Controlling Tool Parameters

### Specifying Model

```
You: "Use zen:codereview with gemini-2.5-pro model to review protocol_worker.py"

AI: "I'll use Gemini 2.5 Pro for the code review..."

[Calls zen_codereview with model="gemini-2.5-pro"]
```

### Specifying Context Level

```
You: "Use zen:chat with lightweight context to quickly answer: what's the current version?"

AI: "Using lightweight context (SESSION_STATE only) for quick lookup..."

[Calls zen_chat with context_level="lightweight"]
```

### Specifying Review Type

```
You: "Use zen:codereview with security review type on the authentication code"

AI: "Performing security-focused code review..."

[Calls zen_codereview with review_type="security"]
```

---

## 🎯 Best Practices

### DO:
✅ **Describe what you want** - "Review my code for quality issues"
✅ **Mention context** - "This is safety-critical medical device code"
✅ **Ask for specific tools** if you know which one - "Use zen:debug to investigate"
✅ **Request multiple models** for important decisions - "Get multi-model consensus"
✅ **Specify concerns** - "Focus on thread safety and memory leaks"

### DON'T:
❌ **Be too vague** - "Fix it" (too unclear)
❌ **Skip context** - "Review this code" without saying what code
❌ **Assume AI knows** - Always mention the file/feature you're working on
❌ **Overthink it** - Just describe what you need naturally

---

## 📊 Complete Example Session

```
[Session Start - New AI Session]

You: "Hi, I'm continuing work on the TOSCA laser control project."

AI: "Welcome back! I've loaded your project context from SESSION_STATE.md.

Current state:
- Phase: UI_Redesign_Phase_3_Complete
- Last work: Completed protocol selector and manual override widgets
- Next recommended: Begin Phase 4 (Integration & Validation)
- Recent commits: 34+ in October 2025

What would you like to work on?"

---

You: "I want to integrate the protocol selector widget into the main treatment
     setup view. Can you help plan this?"

AI: "I'll help you plan the integration. Since this involves architectural
     changes and signal connections, I'll use zen:planner to create a
     systematic approach with full project context.

     Starting planning session..."

[AI calls zen_planner]

AI: "Integration plan created:

Phase 1: Add widget to treatment_setup_widget.py
- Import ProtocolSelectorWidget
- Add to layout (below subject info)
- Size: 400x300px

Phase 2: Connect signals
- protocol_selector.protocol_loaded → treatment_setup.load_protocol
- Handle protocol data (JSON → Protocol object)
- Update UI with protocol info

Phase 3: Handle errors
- Protocol load failures
- Invalid protocol data
- Missing protocol directory

Phase 4: Testing
- Manual test: Load protocol from list
- Manual test: Load protocol from file browser
- Manual test: Error cases (missing file, invalid JSON)

Estimated time: 2-3 hours

Ready to start implementation?"

---

You: "Yes, let's start with Phase 1. After I implement it, can you review the code?"

AI: "Perfect! Go ahead and implement Phase 1 (adding widget to layout).

     When you're done, just say 'review my changes' and I'll use zen:codereview
     to verify the implementation against our architecture decisions and coding
     standards."

---

[You implement Phase 1]

---

You: "Done! Review my changes to treatment_setup_widget.py"

AI: "I'll review your changes using zen:codereview with our coding standards
     and architecture context.

     Starting code review..."

[AI calls zen_codereview]

AI: "Code review complete!

✅ Implementation looks good:
- Widget properly imported
- Added to layout correctly
- Signal connection follows our signal/slot pattern (ADR #005)
- Type hints present

⚠️ Minor suggestions:
- Add docstring to _on_protocol_loaded method (line 156)
- Consider adding try/except around protocol loading

Overall: APPROVED - Good to proceed to Phase 2!"

---

You: "Great! Before I continue, can you get consensus from multiple models
     on whether I should load protocols synchronously or asynchronously?"

AI: "Good question - protocol loading could block the UI if files are large.
     I'll use zen:consensus to get input from GPT-5 and Gemini on this.

     Starting multi-model consensus..."

[AI calls zen_consensus]

AI: "Consensus reached:

📊 Analysis:
- Current protocol files: <10KB (very small)
- Loading time: <10ms (negligible)
- Complexity added by async: Significant

✅ RECOMMENDATION: Keep synchronous loading
- File sizes too small to justify async complexity
- Can always refactor later if protocol files grow
- KISS principle (Keep It Simple, Stupid)

Both models agreed: Premature optimization. Stay synchronous.

Proceed with synchronous loading in Phase 2!"
```

---

## ✅ Summary

**Starting a Session:**
1. Just start talking - AI loads context automatically
2. Describe what you want naturally
3. AI suggests appropriate tools if needed

**Using Tools:**
- **Automatic:** AI calls tools based on your description (RECOMMENDED)
- **Explicit:** Request specific tools by name
- **Advanced:** Specify exact parameters

**Best Approach:**
```
"I want to [action] for [reason], focusing on [concerns]"

Example: "I want to review the protocol worker for thread safety,
          focusing on the Worker pattern implementation"
```

**The AI handles everything else** - tool selection, context loading, parameter setup.

---

**Document Version:** 1.0.0
**Created:** 2025-10-28
**Purpose:** Beginner-friendly guide for using zen tools in new sessions
**Reading Time:** 5 minutes
