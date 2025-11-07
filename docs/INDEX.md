# TOSCA Documentation Index

**Last Updated:** 2025-11-06

**Version:** v0.9.15-alpha

---

## Quick Start

**New to TOSCA?** Start here:
1. [README.md](../README.md) - Project overview, installation, hardware setup
2. [docs/TASK_COMPLETION_REPORT.md](TASK_COMPLETION_REPORT.md) - Recent completion status

---

## Core Documentation

### Root Level
- **[README.md](../README.md)** - Project overview, installation instructions, hardware configuration
- **[LESSONS_LEARNED.md](../LESSONS_LEARNED.md)** - Critical bugs, solutions, and prevention strategies
- **[CLAUDE.md](../CLAUDE.md)** - AI assistant context and development guidelines

### Project Status & Reports
- **[PROJECT_STATUS.md](../presubmit/PROJECT_STATUS.md)** - Current milestones, component status, technical debt
- **[TASK_COMPLETION_REPORT.md](TASK_COMPLETION_REPORT.md)** - Task 19-20 completion details, recommendations
- **[DOCUMENTATION_INVENTORY.md](DOCUMENTATION_INVENTORY.md)** - Complete documentation catalog

---

## Architecture Documentation

### Core System Architecture
Located in `docs/architecture/`:

**Numbered Architecture Documents (01-13):**
1. **[01_system_overview.md](architecture/01_system_overview.md)** - Complete system architecture, technology stack
2. **[02_database_schema.md](architecture/02_database_schema.md)** - SQLite schema, entity relationships
3. **[03_safety_system.md](architecture/03_safety_system.md)** - Safety philosophy, interlock architecture
4. **[04_treatment_protocols.md](architecture/04_treatment_protocols.md)** - Protocol data model, execution engine
5. **[05_image_processing.md](architecture/05_image_processing.md)** - Camera processing pipeline
6. **[06_protocol_builder.md](architecture/06_protocol_builder.md)** - Protocol builder UI and workflow
7. **[07_safety_watchdog.md](architecture/07_safety_watchdog.md)** - Hardware watchdog implementation
8. **[08_security_architecture.md](architecture/08_security_architecture.md)** - Security design
9. **[09_test_architecture.md](architecture/09_test_architecture.md)** - Testing infrastructure and patterns
10. **[10_concurrency_model.md](architecture/10_concurrency_model.md)** - Thread safety and async patterns
11. **[11_event_logging.md](architecture/11_event_logging.md)** - Event logging system
12. **[12_recording_manager.md](architecture/12_recording_manager.md)** - Video recording architecture
13. **[13_calibration_procedures.md](architecture/13_calibration_procedures.md)** - Hardware calibration

### Special Architecture Documents
- **[SAFETY_SHUTDOWN_POLICY.md](architecture/SAFETY_SHUTDOWN_POLICY.md)** - Selective shutdown rationale (CRITICAL)
- **[hardware_controller_base_usage.md](architecture/hardware_controller_base_usage.md)** - HAL usage guide
- **[00_IMPLEMENTATION_STATUS.md](architecture/00_IMPLEMENTATION_STATUS.md)** - Implementation tracking

### Architecture Decision Records
- **[ADR-001-protocol-consolidation.md](architecture/ADR-001-protocol-consolidation.md)** - Protocol format decision
- **[ADR-002-dependency-injection-pattern.md](architecture/ADR-002-dependency-injection-pattern.md)** - DI adoption
- **[11_asyncio_pyqt6_integration.md](architecture/11_asyncio_pyqt6_integration.md)** - Async integration patterns

---

## Hardware Documentation

Located in `docs/hardware/`:
- **[HARDWARE_CONFIG_SUMMARY.md](hardware/HARDWARE_CONFIG_SUMMARY.md)** - Device specifications and wiring
- **[HARDWARE_TEST_RESULTS.md](hardware/HARDWARE_TEST_RESULTS.md)** - Hardware validation results

---

## Integration & Setup

Located in `docs/integration/`:
- **[INTEGRATION_QUICK_START.md](integration/INTEGRATION_QUICK_START.md)** - Quick integration guide

---

## Regulatory Documentation

Located in `docs/regulatory/`:
- **[PRODUCT_REQUIREMENTS_DOCUMENT.md](regulatory/PRODUCT_REQUIREMENTS_DOCUMENT.md)** - Core PRD
- **[TECHNICAL_SPECIFICATION.md](regulatory/TECHNICAL_SPECIFICATION.md)** - Technical specs
- **[requirements/SOFTWARE_REQUIREMENTS_SPECIFICATION.md](regulatory/requirements/SOFTWARE_REQUIREMENTS_SPECIFICATION.md)** - SRS document

---

## Test Documentation

- **[tests/mocks/README.md](../tests/mocks/README.md)** - Mock infrastructure guide (1,255 lines)
  - MockCameraController, MockLaserController, MockTECController, MockActuatorController, MockGPIOController
  - Failure simulation patterns
  - Signal validation framework
  - Integration examples

### Test Files (tests/)
Located in `tests/test_hardware/`:
- test_camera_controller.py (46 tests)
- test_laser_controller.py (18 tests)
- test_tec_actuator_controllers.py (7 tests)
- test_gpio_controller_tests.py (6 tests)
- test_thread_safety_integration.py (3 tests)

**Total:** 148+ tests, 85% pass rate

---

## Historical Documentation (Archive)

**Location:** `docs/archive/`

Preserved for audit trail and regulatory compliance. Not actively maintained.

### Archive Categories:
- **[code-reviews/](archive/code-reviews/)** - Historical code review reports
- **[planning-docs/](archive/planning-docs/)** - Historical planning documents
- **[historical/](archive/)** - Historical project documents

See individual archive README files for details.

---

## Cleanup Documentation (2025-11-06)

### Repository Cleanup Reports

**Comprehensive 3-phase cleanup completed November 6, 2025:**

1. **[GUI_CLEANUP_2025-11-06.md](GUI_CLEANUP_2025-11-06.md)** - GUI code cleanup
   - Archived 9 unused widgets (~2,700 lines)
   - Fixed session_duration_timer initialization bug
   - Removed 5 commented code blocks from main_window.py
   - Code quality improved to A+

2. **[REPOSITORY_CLEANUP_2025-11-06.md](REPOSITORY_CLEANUP_2025-11-06.md)** - Repository-wide cleanup
   - Installed ruff linter and removed 66 unused imports
   - Verified Python cache files not tracked
   - Removed 3 commented code blocks
   - Enhanced code quality across 53 files

3. **[PROJECT_CLEANUP_COMPLETE_2025-11-06.md](PROJECT_CLEANUP_COMPLETE_2025-11-06.md)** - Master cleanup report (to be created)
   - File system organization (archived 10+ screenshots, migration package)
   - Memory graph pruning (lean, current entities only)
   - .gitignore prevention patterns
   - Complete audit trail and statistics

### Code Review

**[CODE_REVIEW_COMPREHENSIVE_2025-11-06.md](CODE_REVIEW_COMPREHENSIVE_2025-11-06.md)** - 40-page comprehensive review
- Security analysis (OWASP Top 10)
- FDA/HIPAA compliance checklist
- Thread safety validation (305 signal connections analyzed)
- Performance review
- Prioritized recommendations

### Cleanup Impact

**Total cleanup statistics:**
- **4,247+ lines removed** (dead code, unused imports, commented blocks)
- **79+ items cleaned** (widgets, imports, files, comments)
- **54+ files modified**
- **Code quality: A-** → **A+ (Excellent)**

All cleanup work maintains complete audit trail for FDA compliance.

---

## Finding Documentation

### By Topic:

**Safety:**
- architecture/03_safety_system.md
- architecture/SAFETY_SHUTDOWN_POLICY.md
- architecture/07_safety_watchdog.md

**Testing:**
- architecture/09_test_architecture.md
- tests/mocks/README.md
- TASK_COMPLETION_REPORT.md

**Hardware:**
- hardware/HARDWARE_CONFIG_SUMMARY.md
- architecture/hardware_controller_base_usage.md
- README.md (Hardware Configuration section)

**Protocol Development:**
- architecture/04_treatment_protocols.md
- architecture/06_protocol_builder.md

**Threading & Async:**
- architecture/10_concurrency_model.md
- architecture/11_asyncio_pyqt6_integration.md

---

## Documentation Standards

**Version Format:** v0.9.12-alpha

**File Naming:**
- Numbered architecture docs: 01_topic_name.md through 13_topic_name.md
- ADRs: ADR-001-decision-name.md
- Special docs: SCREAMING_SNAKE_CASE.md
- Regular docs: regular_snake_case.md

---

## Contributing to Documentation

1. Maintain version consistency (v0.9.12-alpha currently)
2. Add to this index when creating new documentation
3. Archive temporal documents (reports, plans) when superseded
4. Preserve git history for regulatory compliance (use `git mv`, not manual moves)

---

**Need Help?**
- For developers: See README.md
- For regulators: See docs/regulatory/
- For testing: See tests/mocks/README.md
