# TOSCA Documentation Inventory

**Generated:** 2025-11-02
**Purpose:** Comprehensive catalog for documentation cleanup and archival
**Total Files:** 45 markdown files

---

## Classification Legend

- **ETERNAL**: Core documentation, always current (architecture, guidelines)
- **LIVING**: Regularly updated (status, lessons learned)
- **TEMPORAL**: Point-in-time snapshots (reports, reviews, plans)
- **ORPHANED**: Superseded or duplicate content

**Actions:**
- **KEEP**: Active documentation, update to current
- **ARCHIVE**: Historical value, move to archive/
- **CONSOLIDATE**: Merge with another document
- **DELETE**: No value, remove entirely

---

## ROOT LEVEL (5 files)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| README.md | 2025-11-01 | ETERNAL | KEEP | Core project overview - UPDATE |
| LESSONS_LEARNED.md | 2025-10-31 | LIVING | KEEP | Active bug/solution catalog |
| todos.md | Current | TEMPORAL | KEEP | Active task tracking |

---

## DOCS/ ROOT (6 files)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| TASK_COMPLETION_REPORT.md | 2025-11-02 | TEMPORAL | KEEP | Just created - current |
| CODE_REVIEW_ACTION_PLAN.md | ~2025-10-31 | TEMPORAL | ARCHIVE | Completed action plan |
| UI_REDESIGN_PLAN.md | ~2025-10-27 | TEMPORAL | ARCHIVE | Plan complete, superseded |
| REFACTORING_LOG.md | Unknown | TEMPORAL | ARCHIVE | Historical refactoring notes |
| hardware_controller_base_usage.md | Unknown | ORPHANED | CHECK | May be duplicate of architecture doc |
| LINE_PROTOCOL_BUILDER_SUMMARY.md | ~2025-10-31 | TEMPORAL | ARCHIVE | Feature complete, summary doc |
| TECHNICIAN_SETUP.md | Unknown | LIVING | KEEP | Setup instructions |
| UI_CHANGES_2025-10-29.md | 2025-10-29 | TEMPORAL | ARCHIVE | Point-in-time change log |

---

## DOCS/ARCHITECTURE/ (24 files)

### Core Architecture (KEEP - Update dates/versions)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| 01_system_overview.md | 2025-10-30 | ETERNAL | KEEP | UPDATE with Tasks 19-20 |
| 02_database_schema.md | Old | ETERNAL | KEEP | Check if current |
| 03_safety_system.md | Old | ETERNAL | KEEP | Check if current |
| 04_treatment_protocols.md | Old | ETERNAL | KEEP | Check if current |
| 05_image_processing.md | Old | ETERNAL | KEEP | Check if current |
| 06_protocol_builder.md | Old | ETERNAL | KEEP | Check if current |
| 07_safety_watchdog.md | Old | ETERNAL | KEEP | Check if current |
| 08_security_architecture.md | Old | ETERNAL | KEEP | Check if current |
| 09_test_architecture.md | Old | ETERNAL | KEEP | UPDATE with Tasks 19-20 details |
| 10_concurrency_model.md | Old | ETERNAL | KEEP | Check if current |
| 11_event_logging.md | Old | ETERNAL | KEEP | Check if current |
| 12_recording_manager.md | Old | ETERNAL | KEEP | Check if current |
| 13_calibration_procedures.md | Old | ETERNAL | KEEP | Check if current |

### Support Documents (Mixed)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| 00_IMPLEMENTATION_STATUS.md | Unknown | LIVING | CONSOLIDATE | Merge into PROJECT_STATUS? |
| 11_asyncio_pyqt6_integration.md | Old | ETERNAL | KEEP | Numbered duplicate (11) - check |
| ADR-001-protocol-consolidation.md | Old | ETERNAL | KEEP | Architecture decision record |
| ADR-002-dependency-injection-pattern.md | Old | ETERNAL | KEEP | Architecture decision record |
| SAFETY_SHUTDOWN_POLICY.md | 2025-10-30 | ETERNAL | KEEP | Critical safety doc - current |

### Code Reviews & Reports (ARCHIVE)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| safety_code_review.md | Old | TEMPORAL | ARCHIVE | Historical code review |
| CAMERA_PERFORMANCE_FIXES.md | ~2025-10-30 | TEMPORAL | ARCHIVE | Completed fixes documentation |
| EXPOSURE_SAFETY_LIMITER.md | Old | TEMPORAL | ARCHIVE | Feature documentation |
| LINE_PROTOCOL_BUILDER.md | ~2025-10-31 | TEMPORAL | ARCHIVE | Feature documentation |
| signal_connections_report.md | Old | TEMPORAL | ARCHIVE | Point-in-time analysis |
| widget_integration_matrix.md | Old | TEMPORAL | ARCHIVE | Point-in-time mapping |
| dead_code_removal_log.md | Old | TEMPORAL | ARCHIVE | Historical cleanup log |

---

## DOCS/HARDWARE/ (3 files)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| HARDWARE_CONFIG_SUMMARY.md | Old | LIVING | KEEP | Hardware reference - verify current |
| HARDWARE_TEST_RESULTS.md | Old | TEMPORAL | KEEP | Test results - check if superseded |
| MOTOR_GUI_INTEGRATION.md | Old | TEMPORAL | ARCHIVE | Feature integration doc |

---

## DOCS/INTEGRATION/ (2 files)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| INTEGRATION_COMPLETE.md | Old | TEMPORAL | ARCHIVE | Milestone completion doc |
| INTEGRATION_QUICK_START.md | Old | LIVING | KEEP | Quick start guide - verify current |

---

## DOCS/REGULATORY/ (3 files)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| PRODUCT_REQUIREMENTS_DOCUMENT.md | Old | ETERNAL | KEEP | Core regulatory doc - verify current |
| TECHNICAL_SPECIFICATION.md | Old | ETERNAL | KEEP | Core regulatory doc - verify current |
| requirements/SOFTWARE_REQUIREMENTS_SPECIFICATION.md | Old | ETERNAL | KEEP | Core regulatory doc - verify current |

---

## TESTS/MOCKS/ (1 file)

| File | Last Modified | Category | Action | Notes |
|------|---------------|----------|--------|-------|
| README.md | Recent | ETERNAL | KEEP | Just updated for Task 19 - current |

---

## Summary Statistics

**By Category:**
- ETERNAL: 20 files (core architecture, guidelines)
- LIVING: 6 files (regularly updated)
- TEMPORAL: 16 files (point-in-time docs)
- ORPHANED: 3 files (duplicate/superseded)

**Recommended Actions:**
- KEEP (update): 26 files
- ARCHIVE: 16 files
- CONSOLIDATE: 1 file
- DELETE: 1 file
- CHECK: 1 file

---

## High-Priority Actions

### Immediate Updates Needed (Step 4)
1. README.md - Update to v0.9.12-alpha, add Task 19-20 summary
2. docs/architecture/01_system_overview.md - Update with current state
3. docs/architecture/09_test_architecture.md - Add Tasks 19-20 details

### Archive Candidates (Step 5)
1. docs/CODE_REVIEW_ACTION_PLAN.md → archive/planning-docs/
2. docs/UI_REDESIGN_PLAN.md → archive/planning-docs/
3. docs/UI_CHANGES_2025-10-29.md → archive/2025-11-pre-completion/
4. docs/LINE_PROTOCOL_BUILDER_SUMMARY.md → archive/2025-11-pre-completion/
5. docs/architecture/safety_code_review.md → archive/code-reviews/
6. docs/architecture/CAMERA_PERFORMANCE_FIXES.md → archive/2025-11-pre-completion/
7. docs/architecture/EXPOSURE_SAFETY_LIMITER.md → archive/2025-11-pre-completion/
8. docs/architecture/LINE_PROTOCOL_BUILDER.md → archive/2025-11-pre-completion/
9. docs/architecture/signal_connections_report.md → archive/code-reviews/
10. docs/architecture/widget_integration_matrix.md → archive/code-reviews/
11. docs/architecture/dead_code_removal_log.md → archive/2025-11-pre-completion/
12. docs/hardware/MOTOR_GUI_INTEGRATION.md → archive/2025-11-pre-completion/
13. docs/integration/INTEGRATION_COMPLETE.md → archive/2025-11-pre-completion/
14. docs/REFACTORING_LOG.md → archive/2025-11-pre-completion/

### Investigation Needed
1. docs/hardware_controller_base_usage.md - Check for duplication with architecture docs
2. docs/architecture/00_IMPLEMENTATION_STATUS.md - Consider consolidating into PROJECT_STATUS.md

---

## Cross-Reference Analysis (Preliminary)

**High Cross-Reference Count** (Referenced frequently, do NOT archive):
- SAFETY_SHUTDOWN_POLICY.md - Referenced by source code
- 01_system_overview.md - Referenced by README.md
- 09_test_architecture.md - Referenced by test files

**Low Cross-Reference Count** (Safe to archive if temporal):
- UI_REDESIGN_PLAN.md - Planning doc, now complete
- CODE_REVIEW_ACTION_PLAN.md - Action plan, now complete
- Various feature-specific docs (LINE_PROTOCOL_BUILDER.md, etc.)

---

**Next Step:** Proceed to Step 4 (Update core documentation) or Step 5 (Execute archival plan)
