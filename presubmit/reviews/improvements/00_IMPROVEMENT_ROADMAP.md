# TOSCA Improvement Roadmap

**Date:** 2025-10-25
**Status:** Ready for Execution
**Total Effort:** ~23 days (4.6 weeks)

---

## Executive Summary

This roadmap addresses **11 identified issues** across the TOSCA laser control system, prioritized by safety criticality and architectural impact. The improvements are organized into **4 phases** over approximately **1 month** of development effort.

### Priority Distribution
- **🔴 CRITICAL:** 4 issues (17.5 days total)
- **🟠 HIGH:** 2 issues (8.5 days total)
- **🟡 MEDIUM:** 4 issues (tracked in backlog)
- **🟢 LOW:** 1 issue (technical debt)

### Key Outcomes
✅ **Safety Hardening** - Watchdog timer prevents freeze-induced hazards
✅ **Architectural Improvement** - Decoupled, testable, maintainable code
✅ **Configuration Management** - Environment-specific deployments
✅ **Code Quality** - Consistent patterns, reduced duplication

---

## Phase 1: Critical Safety & Infrastructure (Week 1-2, 10 days)

**Focus:** Address safety-critical issues and foundational architecture.

### 1.1 Watchdog Timer Implementation 🔴 CRITICAL
**Priority:** P0 (Highest)
**Effort:** 4.5 days
**Risk:** Medium

**Tasks:**
- [ ] Design multi-level watchdog architecture
- [ ] Implement application watchdog in `SafetyManager`
- [ ] Add heartbeat mechanism to `MainWindow`
- [ ] Integrate watchdog with laser controller
- [ ] Write comprehensive tests (unit + integration)
- [ ] Perform freeze simulation testing
- [ ] Document watchdog behavior for operators

**Deliverables:**
- `src/core/safety.py` (enhanced with watchdog)
- `src/ui/main_window.py` (heartbeat integration)
- Test suite for watchdog
- Operator documentation

**Dependencies:** Configuration management (for watchdog settings)

---

### 1.2 Configuration Management with Pydantic 🔴 CRITICAL
**Priority:** P0
**Effort:** 5.5 days
**Risk:** Low

**Tasks:**
- [ ] Create `src/config/` directory structure
- [ ] Implement Pydantic settings classes:
  - `hardware.py` (actuator, laser, camera, GPIO)
  - `safety.py` (watchdog, interlocks)
  - `protocol.py` (execution parameters)
  - `settings.py` (main configuration)
- [ ] Migrate hardcoded values from all controllers
- [ ] Create default `.env` file
- [ ] Create environment-specific configs (dev, test, prod)
- [ ] Update all 20+ locations using hardcoded values
- [ ] Write configuration tests
- [ ] Create configuration documentation

**Deliverables:**
- Complete `src/config/` module
- `.env` configuration file
- Migration of all hardcoded constants
- Configuration documentation

**Dependencies:** None

---

## Phase 2: Architectural Improvements (Week 2-3, 9 days)

**Focus:** Decouple components and establish clean architecture patterns.

### 2.1 Dependency Injection & Service Architecture 🔴 CRITICAL
**Priority:** P1
**Effort:** 3.5 days
**Risk:** Medium

**Tasks:**
- [ ] Create `src/core/services.py` module
- [ ] Implement `ApplicationServices` container
- [ ] Implement `ServiceFactory` with service creation
- [ ] Refactor `main.py` to use service factory
- [ ] Refactor `MainWindow` to accept injected services
- [ ] Remove all service instantiation from `MainWindow`
- [ ] Update all widgets to use injected services
- [ ] Create mock services for testing
- [ ] Update all existing tests
- [ ] Write integration tests

**Deliverables:**
- `src/core/services.py`
- Refactored `src/main.py`
- Refactored `src/ui/main_window.py`
- Mock services for testing
- Updated test suite

**Dependencies:** Configuration management

---

### 2.2 Hardware Controller ABC 🟠 HIGH
**Priority:** P2
**Effort:** 5 days
**Risk:** Medium

**Tasks:**
- [ ] Design `HardwareControllerBase` abstract base class
- [ ] Create `src/hardware/base_controller.py`
- [ ] Implement base class with common functionality:
  - Connection lifecycle
  - Event logging
  - Signal handling
  - Context manager support
- [ ] Refactor `LaserController` to inherit from base (day 1)
- [ ] Refactor `ActuatorController` to inherit from base (day 2)
- [ ] Refactor `CameraController` to inherit from base (day 3)
- [ ] Refactor `GPIOController` to inherit from base (day 4)
- [ ] Test all controllers thoroughly
- [ ] Update documentation

**Deliverables:**
- `src/hardware/base_controller.py`
- All 4 controllers refactored
- 200+ lines of code removed
- Updated architecture documentation

**Dependencies:** None

---

## Phase 3: Safety & Execution Improvements (Week 3-4, 4 days)

**Focus:** Fix placeholder implementations and improve reliability.

### 3.1 Real Safety Checks in Protocol Engine 🔴 CRITICAL
**Priority:** P0
**Effort:** 0.5 days
**Risk:** Low

**Tasks:**
- [ ] Update `ProtocolEngine.__init__()` to accept `SafetyManager`
- [ ] Implement real `_perform_safety_checks()` method
- [ ] Integrate with `SafetyManager.is_laser_enable_permitted()`
- [ ] Add detailed safety status reporting
- [ ] Write safety check tests
- [ ] Update protocol execution documentation

**Deliverables:**
- `src/core/protocol_engine.py` (real safety checks)
- Safety check tests
- Updated documentation

**Dependencies:** Dependency Injection (SafetyManager injection)

---

### 3.2 Actuator Movement Signal-Based Waiting 🟠 HIGH
**Priority:** P2
**Effort:** 1 day
**Risk:** Low

**Tasks:**
- [ ] Create `qt_signal_to_future()` utility function
- [ ] Update `_execute_move_actuator()` to await `position_reached` signal
- [ ] Remove estimated time-based sleep logic
- [ ] Add timeout protection
- [ ] Write tests for signal-based waiting
- [ ] Update protocol engine documentation

**Deliverables:**
- Signal-to-future utility
- Updated `src/core/protocol_engine.py`
- Actuator movement tests

**Dependencies:** None

---

### 3.3 Import Path Standardization 🟡 MEDIUM
**Priority:** P3
**Effort:** 3.5 days
**Risk:** Low

**Tasks:**
- [ ] Create automated import conversion script
- [ ] Run script on all Python files
- [ ] Manual review of all changes
- [ ] Test application startup
- [ ] Run full test suite
- [ ] Create pre-commit hook for import style
- [ ] Update developer guidelines

**Deliverables:**
- All imports standardized to relative imports
- Pre-commit hook for enforcement
- Updated developer documentation

**Dependencies:** None

---

## Phase 4: Code Quality & Technical Debt (Ongoing)

**Focus:** Address medium/low priority issues as capacity allows.

### 4.1 Remove Duplicate SessionManager 🟡 MEDIUM
**Priority:** P4
**Effort:** 0.5 days
**Risk:** Low

**Tasks:**
- [ ] Identify which `SessionManager` is actively used
- [ ] Remove unused implementation
- [ ] Update imports
- [ ] Run tests

**Deliverables:**
- Single `SessionManager` implementation

---

### 4.2 Implement Protocol Execution Persistence 🟡 MEDIUM
**Priority:** P4
**Effort:** 2 days
**Risk:** Low

**Tasks:**
- [ ] Design protocol execution database schema
- [ ] Implement `_save_execution_record()` method
- [ ] Store protocol execution logs
- [ ] Create audit trail queries
- [ ] Write persistence tests

**Deliverables:**
- Protocol execution persistence
- Audit trail capability

---

### 4.3 Context Manager Support for Hardware 🟢 LOW
**Priority:** P5
**Effort:** Included in Phase 2.2
**Risk:** Low

**Note:** This is automatically addressed when creating `HardwareControllerBase` ABC.

---

## Implementation Schedule

### Gantt Chart (4-Week Timeline)

```
Week 1:
├── Day 1-2: Configuration Management (2.5 days)
├── Day 3-5: Watchdog Timer (3 days)

Week 2:
├── Day 1-2: Configuration Management Complete (1.5 days)
├── Day 3-5: Dependency Injection (3 days)

Week 3:
├── Day 1: Hardware ABC - LaserController (1 day)
├── Day 2: Hardware ABC - ActuatorController (1 day)
├── Day 3: Hardware ABC - CameraController (1 day)
├── Day 4: Hardware ABC - GPIOController (1 day)
├── Day 5: Hardware ABC - Testing & Docs (1 day)

Week 4:
├── Day 1: Watchdog Timer Complete (1.5 days)
├── Day 2: Safety Checks + Actuator Signal (1.5 days)
├── Day 3-5: Import Standardization (3 days)
```

---

## Resource Requirements

### Development Team
- **1 Senior Developer** (Phases 1-2, critical work)
- **1 Mid-Level Developer** (Phase 3-4, quality improvements)
- **1 QA Engineer** (Testing throughout)

### Testing Requirements
- **Unit Tests:** All new code >80% coverage
- **Integration Tests:** End-to-end workflows
- **Hardware Tests:** Manual testing with real devices
- **Safety Tests:** Freeze simulation, watchdog validation

---

## Risk Assessment

### High Risk Items
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Watchdog timer bugs | Medium | Critical | Extensive testing, peer review |
| Service refactoring breaks UI | Medium | High | Incremental migration, rollback plan |
| Hardware ABC breaks controllers | Low | High | Test each controller before moving to next |

### Medium Risk Items
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Configuration migration errors | Low | Medium | Automated script + manual review |
| Test coverage gaps | Medium | Medium | Mandatory code review, coverage reports |

---

## Success Metrics

### Code Quality Metrics
- [ ] Test coverage > 80%
- [ ] No critical or high severity linter warnings
- [ ] All pre-commit hooks passing
- [ ] Code review approval for all changes

### Safety Metrics
- [ ] Watchdog triggers within 3 seconds
- [ ] Laser disables on freeze simulation
- [ ] All safety interlocks validated
- [ ] Zero safety regressions

### Architectural Metrics
- [ ] MainWindow 200+ lines shorter
- [ ] Hardware controllers 50+ lines shorter each
- [ ] Zero hardcoded configuration values
- [ ] All services injectable for testing

---

## Dependencies Graph

```
Configuration Management (5.5d)
   ├──> Watchdog Timer (4.5d) ──┐
   │                             │
   └──> Dependency Injection (3.5d) ──> Safety Checks (0.5d)
                                        │
Hardware Controller ABC (5d) ───────────┘
                │
                └──> Actuator Signal Waiting (1d)

Import Standardization (3.5d) ── Independent

Medium/Low Priority ── As Capacity Allows
```

---

## Phase Completion Criteria

### Phase 1 Complete When:
✅ Watchdog timer operational and tested
✅ All configuration migrated to Pydantic settings
✅ Application runs with `.env` configuration
✅ Safety tests passing

### Phase 2 Complete When:
✅ Services created in `main.py`, not `MainWindow`
✅ All hardware controllers inherit from ABC
✅ 200+ lines of duplicated code removed
✅ Integration tests passing

### Phase 3 Complete When:
✅ Protocol engine validates real safety checks
✅ Actuator waits for `position_reached` signal
✅ All imports use relative paths
✅ Pre-commit hooks enforcing standards

### Phase 4 Complete When:
✅ Single `SessionManager` implementation
✅ Protocol execution persisted to database
✅ Technical debt backlog cleared

---

## Communication Plan

### Weekly Status Reports
**Every Friday:** Status update including:
- Completed tasks
- Blockers and risks
- Next week's plan
- Test results

### Code Reviews
**Required for:**
- All critical safety changes
- Architectural refactoring
- Public API changes

### Documentation Updates
**Required for:**
- Each completed phase
- Configuration changes
- New developer onboarding materials

---

## Rollback Plan

For each phase:
1. **Feature Branch:** All work in dedicated branch
2. **Backup:** Tag before starting phase
3. **Rollback Trigger:** Critical bug or failed safety test
4. **Rollback Process:** Revert to tagged version, investigate issue

---

## Post-Implementation Review

### Week 5: Stabilization & Review
- [ ] Full system testing
- [ ] Performance benchmarking
- [ ] Safety audit
- [ ] Code quality review
- [ ] Documentation review
- [ ] Team retrospective

---

## Next Steps

1. **Immediate (Today):**
   - Review and approve this roadmap
   - Assign team members
   - Setup development branches

2. **This Week:**
   - Begin Phase 1: Configuration Management
   - Setup test infrastructure
   - Create development environment

3. **Month 1:**
   - Execute Phases 1-3
   - Weekly status meetings
   - Continuous testing

4. **Month 2:**
   - Complete Phase 4
   - Stabilization
   - Documentation
   - Launch

---

## Document References

- [Code Review Findings](./CODE_REVIEW_FINDINGS.md)
- [Import Path Standardization](./01_IMPORT_PATH_STANDARDIZATION.md)
- [Hardware Controller ABC](./02_HARDWARE_CONTROLLER_ABC.md)
- [Configuration Management](./03_CONFIGURATION_MANAGEMENT.md)
- [Watchdog Timer](./04_WATCHDOG_TIMER_IMPLEMENTATION.md)
- [Dependency Injection](./05_DEPENDENCY_INJECTION.md)

---

**Roadmap Version:** 1.0
**Last Updated:** 2025-10-25
**Status:** ✅ Ready for Execution
**Approval:** Pending
