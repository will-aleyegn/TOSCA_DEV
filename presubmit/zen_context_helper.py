"""
Zen MCP Context Helper - Automatically include project context in zen tool calls

This module provides convenience functions that automatically load project
onboarding and context files when using Zen MCP tools, ensuring external
models have full project understanding.

Philosophy: Err on the side of MORE context rather than less.
Default: FULL context package for comprehensive understanding.

Usage:
    from presubmit.zen_context_helper import zen_codereview, zen_debug, get_full_context

    # Automatic context loading
    zen_codereview(
        step="Review protocol worker implementation",
        code_files=["src/ui/workers/protocol_worker.py"],
        model="gpt-5-pro"
    )

    # Or manually get context files
    context = get_full_context()
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# PROJECT PATHS - Update these if directory structure changes
# ============================================================================

# Detect project root (where this file is located relative to project)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent  # Go up one level from presubmit/

# Context file paths (all absolute paths)
ONBOARDING_PATH = PROJECT_ROOT / "presubmit" / "ONBOARDING.md"
SESSION_STATE_PATH = PROJECT_ROOT / "presubmit" / "active" / "SESSION_STATE.md"
DECISIONS_PATH = PROJECT_ROOT / "presubmit" / "active" / "DECISIONS.md"
HISTORY_PATH = PROJECT_ROOT / "HISTORY.md"
WORK_LOG_PATH = PROJECT_ROOT / "WORK_LOG.md"

# Architecture documentation
ARCH_OVERVIEW = PROJECT_ROOT / "docs" / "architecture" / "01_system_overview.md"
ARCH_SAFETY = PROJECT_ROOT / "docs" / "architecture" / "03_safety_system.md"
ARCH_PROTOCOLS = PROJECT_ROOT / "docs" / "architecture" / "04_treatment_protocols.md"

# Reference documentation
CODING_STANDARDS = PROJECT_ROOT / "presubmit" / "reference" / "CODING_STANDARDS.md"
GIT_POLICY = PROJECT_ROOT / "presubmit" / "reference" / "GIT_CONTENT_POLICY.md"
CHECKPOINT_GUIDE = PROJECT_ROOT / "presubmit" / "reference" / "SESSION_CHECKPOINT_GUIDE.md"

# ============================================================================
# CONTEXT PACKAGES
# ============================================================================


def get_core_context() -> List[str]:
    """
    Core context - The absolute minimum for any zen tool call.

    Returns 3 files (~700 lines):
    - ONBOARDING.md: Project overview, tech stack, current state
    - SESSION_STATE.md: Current phase, recent commits, next actions
    - DECISIONS.md: Architecture decision records
    """
    return [
        str(ONBOARDING_PATH.resolve()),
        str(SESSION_STATE_PATH.resolve()),
        str(DECISIONS_PATH.resolve()),
    ]


def get_full_context() -> List[str]:
    """
    Full context - DEFAULT for all tools. Maximum project understanding.

    Returns 8 files (~1200 lines):
    - Core context (3 files)
    - HISTORY.md: Compressed monthly summaries
    - WORK_LOG.md: Detailed recent history (last 14 days)
    - Architecture docs (3 files): System overview, safety, protocols

    Philosophy: External models benefit from comprehensive context.
    Token cost justified by quality of analysis.
    """
    context = get_core_context() + [
        str(HISTORY_PATH.resolve()),
        str(WORK_LOG_PATH.resolve()),
    ]

    # Add architecture docs if they exist
    if ARCH_OVERVIEW.exists():
        context.append(str(ARCH_OVERVIEW.resolve()))
    if ARCH_SAFETY.exists():
        context.append(str(ARCH_SAFETY.resolve()))
    if ARCH_PROTOCOLS.exists():
        context.append(str(ARCH_PROTOCOLS.resolve()))

    return context


def get_lightweight_context() -> List[str]:
    """
    Lightweight context - For quick operations or token budget constraints.

    Returns 1 file (~163 lines):
    - SESSION_STATE.md only: Current state, recent commits

    Use when: Token budget tight, quick questions, non-critical operations
    """
    return [str(SESSION_STATE_PATH.resolve())]


def get_code_review_context() -> List[str]:
    """
    Code review context - Optimized for code quality analysis.

    Returns 5 files (~900 lines):
    - Core context (3 files)
    - CODING_STANDARDS.md: Code quality requirements
    - GIT_POLICY.md: Git workflow and commit standards
    """
    context = get_core_context()

    if CODING_STANDARDS.exists():
        context.append(str(CODING_STANDARDS.resolve()))
    if GIT_POLICY.exists():
        context.append(str(GIT_POLICY.resolve()))

    return context


def get_security_context() -> List[str]:
    """
    Security context - For security audits and compliance checks.

    Returns 9 files (~1300 lines):
    - Full context (8 files)
    - Safety architecture documentation

    Critical for: Medical device compliance, FDA requirements, safety-critical code
    """
    context = get_full_context()

    # Ensure safety architecture is included
    if ARCH_SAFETY.exists() and str(ARCH_SAFETY.resolve()) not in context:
        context.append(str(ARCH_SAFETY.resolve()))

    return context


def get_planning_context() -> List[str]:
    """
    Planning context - For strategic planning and architectural decisions.

    Returns 6 files (~1000 lines):
    - Core context (3 files)
    - HISTORY.md: Historical evolution and patterns
    - Architecture overview and protocols
    """
    context = get_core_context() + [str(HISTORY_PATH.resolve())]

    if ARCH_OVERVIEW.exists():
        context.append(str(ARCH_OVERVIEW.resolve()))
    if ARCH_PROTOCOLS.exists():
        context.append(str(ARCH_PROTOCOLS.resolve()))

    return context


# ============================================================================
# HELPER FUNCTIONS - Combine context with task-specific files
# ============================================================================


def combine_context(
    task_files: List[str],
    context_level: str = "full",
    additional_context: Optional[List[str]] = None,
) -> List[str]:
    """
    Combine context package with task-specific files.

    Args:
        task_files: Files specific to the task (code to review, debug, etc.)
        context_level: "full" (default), "core", "lightweight", "code_review",
                       "security", or "planning"
        additional_context: Extra context files to include

    Returns:
        List of absolute file paths with context first, then task files

    Example:
        files = combine_context(
            task_files=["src/ui/widgets/protocol_selector.py"],
            context_level="full",
            additional_context=["docs/ui_guidelines.md"]
        )
    """
    # Get base context
    context_map = {
        "full": get_full_context,
        "core": get_core_context,
        "lightweight": get_lightweight_context,
        "code_review": get_code_review_context,
        "security": get_security_context,
        "planning": get_planning_context,
    }

    context_func = context_map.get(context_level, get_full_context)
    context = context_func()

    # Add additional context if provided
    if additional_context:
        context.extend([str(Path(f).resolve()) for f in additional_context])

    # Add task-specific files (ensure absolute paths)
    task_files_abs = [str(Path(f).resolve()) for f in task_files]

    # Return: context first, then task files
    return context + task_files_abs


def validate_context_files() -> Dict[str, bool]:
    """
    Check which context files exist. Useful for debugging.

    Returns:
        Dict mapping file names to existence status
    """
    files = {
        "ONBOARDING.md": ONBOARDING_PATH,
        "SESSION_STATE.md": SESSION_STATE_PATH,
        "DECISIONS.md": DECISIONS_PATH,
        "HISTORY.md": HISTORY_PATH,
        "WORK_LOG.md": WORK_LOG_PATH,
        "System Overview": ARCH_OVERVIEW,
        "Safety Architecture": ARCH_SAFETY,
        "Protocol Architecture": ARCH_PROTOCOLS,
        "Coding Standards": CODING_STANDARDS,
        "Git Policy": GIT_POLICY,
        "Checkpoint Guide": CHECKPOINT_GUIDE,
    }

    return {name: path.exists() for name, path in files.items()}


# ============================================================================
# CONVENIENCE WRAPPERS - Auto-context zen tool calls
# ============================================================================


def zen_codereview(
    step: str,
    code_files: List[str],
    step_number: int = 1,
    total_steps: int = 2,
    findings: str = "",
    model: str = "gpt-5-pro",
    review_type: str = "full",
    context_level: str = "code_review",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Code review with automatic context loading.

    Args:
        step: Review plan/findings
        code_files: Files to review (relative or absolute paths)
        step_number: Current step
        total_steps: Expected total steps (2 = analysis + summary)
        findings: Current findings
        model: Model to use (gpt-5-pro, gemini-2.5-pro, etc.)
        review_type: "full", "security", "performance", or "quick"
        context_level: "code_review" (default), "full", or "core"
        **kwargs: Additional parameters for mcp__zen__codereview

    Returns:
        Dict with review results and continuation_id

    Example:
        result = zen_codereview(
            step="Review protocol worker for thread safety",
            code_files=["src/ui/workers/protocol_worker.py"],
            findings="Worker pattern implemented, validating signal connections",
            model="gpt-5-pro"
        )
    """
    relevant_files = combine_context(code_files, context_level)

    return {
        "tool": "mcp__zen__codereview",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "relevant_files": relevant_files,
            "review_type": review_type,
            "model": model,
            "confidence": kwargs.get("confidence", "exploring"),
            **kwargs,
        },
    }


def zen_debug(
    step: str,
    code_files: List[str],
    findings: str,
    hypothesis: str,
    step_number: int = 1,
    total_steps: int = 3,
    model: str = "gpt-5-pro",
    confidence: str = "low",
    context_level: str = "full",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Debug investigation with automatic context loading.

    Args:
        step: Investigation plan
        code_files: Files related to the bug
        findings: Current discoveries and evidence
        hypothesis: Current theory about root cause
        step_number: Current investigation step
        total_steps: Expected steps (adjust as investigation progresses)
        model: Model to use
        confidence: "exploring", "low", "medium", "high", "very_high", "almost_certain", "certain"
        context_level: "full" (default), "core", or "lightweight"
        **kwargs: Additional parameters

    Returns:
        Dict with debug parameters

    Example:
        result = zen_debug(
            step="Investigate GUI freezing during protocol execution",
            code_files=["src/ui/workers/protocol_worker.py"],
            findings="GUI unresponsive for 5-10s after Start Treatment clicked",
            hypothesis="Worker not properly moved to thread",
            confidence="low"
        )
    """
    relevant_files = combine_context(code_files, context_level)

    return {
        "tool": "mcp__zen__debug",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "hypothesis": hypothesis,
            "relevant_files": relevant_files,
            "files_checked": relevant_files,
            "model": model,
            "confidence": confidence,
            **kwargs,
        },
    }


def zen_consensus(
    step: str,
    models: List[Dict[str, str]],
    findings: str = "",
    relevant_files: Optional[List[str]] = None,
    step_number: int = 1,
    context_level: str = "planning",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Multi-model consensus with automatic context loading.

    Args:
        step: Question or proposal to evaluate
        models: List of models with stances, e.g.:
                [{"model": "gpt-5-pro", "stance": "for"},
                 {"model": "gemini-2.5-pro", "stance": "against"}]
        findings: Your independent analysis
        relevant_files: Task-specific files (optional)
        step_number: Current step (1 = your analysis, 2+ = model responses)
        context_level: "planning" (default), "full", or "core"
        **kwargs: Additional parameters

    Returns:
        Dict with consensus parameters

    Example:
        result = zen_consensus(
            step="Should we use REST API or WebSocket for real-time sensor data?",
            models=[
                {"model": "gpt-5-pro", "stance": "for"},
                {"model": "gemini-2.5-pro", "stance": "against"}
            ],
            findings="Current system uses PyQt6 signals, need remote access",
            relevant_files=["src/hardware/gpio_controller.py"]
        )
    """
    task_files = relevant_files if relevant_files else []
    combined_files = combine_context(task_files, context_level)

    total_steps = len(models) + 1  # Your analysis + each model + synthesis

    return {
        "tool": "mcp__zen__consensus",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "models": models,
            "relevant_files": combined_files,
            **kwargs,
        },
    }


def zen_secaudit(
    step: str,
    security_files: List[str],
    security_scope: str,
    findings: str = "",
    step_number: int = 1,
    total_steps: int = 3,
    model: str = "gpt-5-pro",
    audit_focus: str = "comprehensive",
    threat_level: str = "medium",
    context_level: str = "security",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Security audit with automatic context loading.

    Args:
        step: Audit plan
        security_files: Security-critical files to audit
        security_scope: Context (web, mobile, API, medical device, etc.)
        findings: Current security findings
        step_number: Current audit step
        total_steps: Expected steps
        model: Model to use
        audit_focus: "owasp", "compliance", "infrastructure", "dependencies", "comprehensive"
        threat_level: "low", "medium", "high", "critical"
        context_level: "security" (default), "full"
        **kwargs: Additional parameters (compliance_requirements, etc.)

    Returns:
        Dict with security audit parameters

    Example:
        result = zen_secaudit(
            step="Audit manual override widget for FDA compliance",
            security_files=["src/ui/widgets/manual_override_widget.py"],
            security_scope="Medical device with FDA compliance requirements",
            audit_focus="compliance",
            threat_level="critical",
            compliance_requirements=["FDA", "HIPAA"]
        )
    """
    relevant_files = combine_context(security_files, context_level)

    return {
        "tool": "mcp__zen__secaudit",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "security_scope": security_scope,
            "relevant_files": relevant_files,
            "files_checked": relevant_files,
            "audit_focus": audit_focus,
            "threat_level": threat_level,
            "model": model,
            **kwargs,
        },
    }


def zen_planner(
    step: str,
    step_number: int = 1,
    total_steps: int = 5,
    model: str = "gemini-2.5-pro",
    context_level: str = "planning",
    relevant_files: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Strategic planning with automatic context loading.

    Args:
        step: Planning content (step 1: describe task, later: updates/revisions)
        step_number: Current planning step
        total_steps: Expected steps (adjust as plan evolves)
        model: Model to use (gemini-2.5-pro excellent for planning)
        context_level: "planning" (default), "full"
        relevant_files: Additional context files
        **kwargs: Additional parameters (is_branch_point, branch_id, etc.)

    Returns:
        Dict with planner parameters

    Example:
        result = zen_planner(
            step="Plan refactoring of camera module to use VmbPy 2.0 API",
            model="gemini-2.5-pro",
            relevant_files=["src/hardware/camera_controller.py"]
        )
    """
    task_files = relevant_files if relevant_files else []
    # Planner doesn't use relevant_files, but we prepare them for reference in prompt
    context = combine_context(task_files, context_level)

    # Add context note to step if this is step 1
    if step_number == 1 and task_files:
        step = (
            f"{step}\n\nRelevant context files loaded: {', '.join([Path(f).name for f in context])}"
        )

    return {
        "tool": "mcp__zen__planner",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "model": model,
            **kwargs,
        },
    }


def zen_analyze(
    step: str,
    analysis_files: List[str],
    findings: str = "",
    step_number: int = 1,
    total_steps: int = 3,
    model: str = "gemini-2.5-pro",
    analysis_type: str = "general",
    context_level: str = "full",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Code analysis with automatic context loading.

    Args:
        step: Analysis plan
        analysis_files: Files to analyze
        findings: Current analysis findings
        step_number: Current step
        total_steps: Expected steps
        model: Model to use (gemini-2.5-pro great for analysis)
        analysis_type: "architecture", "performance", "security", "quality", "general"
        context_level: "full" (default)
        **kwargs: Additional parameters

    Returns:
        Dict with analyze parameters

    Example:
        result = zen_analyze(
            step="Analyze safety manager architecture and interlock logic",
            analysis_files=["src/core/safety.py", "src/core/safety_watchdog.py"],
            findings="Need to understand state machine and failure modes",
            analysis_type="architecture"
        )
    """
    relevant_files = combine_context(analysis_files, context_level)

    return {
        "tool": "mcp__zen__analyze",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "relevant_files": relevant_files,
            "files_checked": relevant_files,
            "analysis_type": analysis_type,
            "model": model,
            **kwargs,
        },
    }


def zen_refactor(
    step: str,
    refactor_files: List[str],
    findings: str = "",
    step_number: int = 1,
    total_steps: int = 2,
    model: str = "gpt-5-codex",
    refactor_type: str = "codesmells",
    confidence: str = "incomplete",
    context_level: str = "full",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Refactoring analysis with automatic context loading.

    Args:
        step: Refactoring plan
        refactor_files: Files to analyze for refactoring
        findings: Current refactoring opportunities found
        step_number: Current step
        total_steps: Expected steps
        model: Model to use (gpt-5-codex good for code patterns)
        refactor_type: "codesmells", "decompose", "modernize", "organization"
        confidence: "exploring", "incomplete", "partial", "complete"
        context_level: "full" (default)
        **kwargs: Additional parameters (style_guide_examples, focus_areas, etc.)

    Returns:
        Dict with refactor parameters

    Example:
        result = zen_refactor(
            step="Analyze main_window.py for decomposition opportunities",
            refactor_files=["src/ui/main_window.py"],
            findings="File has 800 lines, multiple responsibilities",
            refactor_type="decompose"
        )
    """
    relevant_files = combine_context(refactor_files, context_level)

    return {
        "tool": "mcp__zen__refactor",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "relevant_files": relevant_files,
            "files_checked": relevant_files,
            "refactor_type": refactor_type,
            "confidence": confidence,
            "model": model,
            **kwargs,
        },
    }


def zen_testgen(
    step: str,
    test_files: List[str],
    findings: str = "",
    step_number: int = 1,
    total_steps: int = 2,
    model: str = "gpt-5-codex",
    context_level: str = "full",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Test generation with automatic context loading.

    Args:
        step: Test plan
        test_files: Files that need tests
        findings: Test scenarios and edge cases identified
        step_number: Current step
        total_steps: Expected steps
        model: Model to use (gpt-5-codex excellent for test generation)
        context_level: "full" (default)
        **kwargs: Additional parameters

    Returns:
        Dict with testgen parameters

    Example:
        result = zen_testgen(
            step="Generate tests for protocol selector with edge cases",
            test_files=["src/ui/widgets/protocol_selector_widget.py"],
            findings="Need tests for: file not found, invalid JSON, empty directory"
        )
    """
    relevant_files = combine_context(test_files, context_level)

    return {
        "tool": "mcp__zen__testgen",
        "params": {
            "step": step,
            "step_number": step_number,
            "total_steps": total_steps,
            "next_step_required": step_number < total_steps,
            "findings": findings,
            "relevant_files": relevant_files,
            "files_checked": relevant_files,
            "model": model,
            **kwargs,
        },
    }


def zen_chat(
    prompt: str,
    task_files: Optional[List[str]] = None,
    model: str = "gemini-2.5-pro",
    context_level: str = "core",
    continuation_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Casual chat with automatic context loading.

    Args:
        prompt: Your question or discussion topic
        task_files: Optional files for context
        model: Model to use (gemini-2.5-pro good for chat)
        context_level: "core" (default), "full", or "lightweight"
        continuation_id: Reuse previous conversation context
        **kwargs: Additional parameters (temperature, thinking_mode, images)

    Returns:
        Dict with chat parameters

    Example:
        result = zen_chat(
            prompt="Explain the pros and cons of QStackedWidget vs QTabWidget",
            task_files=["src/ui/main_window.py"],
            model="gemini-2.5-pro"
        )
    """
    files = task_files if task_files else []
    absolute_file_paths = combine_context(files, context_level)

    return {
        "tool": "mcp__zen__chat",
        "params": {
            "prompt": prompt,
            "absolute_file_paths": absolute_file_paths,
            "working_directory_absolute_path": str(PROJECT_ROOT.resolve()),
            "model": model,
            "continuation_id": continuation_id,
            **kwargs,
        },
    }


# ============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# ============================================================================

if __name__ == "__main__":
    """
    Example usage and validation of context helper.
    """
    print("Zen Context Helper - Validation\n")
    print("=" * 70)

    # Validate context files
    print("\n1. Context File Validation:")
    validation = validate_context_files()
    for name, exists in validation.items():
        status = "✅" if exists else "❌"
        print(f"   {status} {name}")

    # Show context packages
    print("\n2. Context Package Sizes:")
    packages = {
        "Lightweight": get_lightweight_context(),
        "Core": get_core_context(),
        "Code Review": get_code_review_context(),
        "Planning": get_planning_context(),
        "Full": get_full_context(),
        "Security": get_security_context(),
    }

    for name, files in packages.items():
        print(f"   {name}: {len(files)} files")
        for f in files:
            filename = Path(f).name
            print(f"      - {filename}")

    # Example usage
    print("\n3. Example Usage:")
    print("\n   # Code Review with auto-context:")
    print("   result = zen_codereview(")
    print("       step='Review protocol worker implementation',")
    print("       code_files=['src/ui/workers/protocol_worker.py'],")
    print("       model='gpt-5-pro'")
    print("   )")
    print("   # Automatically includes: ONBOARDING, SESSION_STATE, DECISIONS,")
    print("   #                        CODING_STANDARDS, GIT_POLICY")

    print("\n" + "=" * 70)
    print("Ready to use! Import functions from this module.")
