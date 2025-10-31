# TOSCA Master Project Roadmap

**Last Updated:** 2025-10-30
**Current Version:** v0.9.11-alpha
**Target:** Production-Ready v1.0 (FDA/HIPAA Compliant)

---

## Overview

**Current Status:** 15% Production Ready
**Total Effort:** 16 weeks (4 months) with 2-3 engineers
**Budget Estimate:** $78,000 (labor only)

### Phase Timeline

```
Phase 6 (Weeks 1-8): Security + Testing + Compliance
Phase 7 (Weeks 9-12): Architecture + Performance
Phase 8+ (Post-Production): Code Quality + Developer Experience
```

---

## Current Sprint Status

**Active Phase:** Planning
**Next Milestone:** Begin Phase 6 Week 1 (Security Hardening)

### Todo List Status: 20 tasks

**By Priority:**
- P0 (CRITICAL): 5 tasks (security blockers)
- P1 (HIGH): 10 tasks (testing + documentation)
- P2 (MEDIUM): 4 tasks (architecture + performance)
- P3 (LOW): 6 tasks (code quality + developer experience)

**By Phase:**
- Phase 6 (Weeks 1-8): 14 tasks
- Phase 7 (Weeks 9-12): 4 tasks
- Phase 8+ (Post-Production): 2 tasks

---

## Phase 6: Security + Testing + Compliance (8 weeks)

**Objective:** Achieve FDA 21 CFR Part 11 and HIPAA compliance
**Team:** 2 engineers + 1 security specialist + 1 regulatory consultant

### Week 1-2: Critical Security Fixes (P0)

#### ✅ Week 1 Tasks

**[ ] Task 1.1: Database Encryption (5 days)**
- Priority: P0 (CRITICAL)
- Owner: Senior Engineer
- Effort: 40 hours
- Deliverables:
  - [ ] SQLCipher integration
  - [ ] AES-256-CBC encryption enabled
  - [ ] Windows DPAPI key storage
  - [ ] Database migration script
  - [ ] Performance validation (<10% overhead)
- Files Modified:
  - `src/database/db_manager.py`
  - `requirements.txt`
  - `config/config.yaml`
- Acceptance Criteria:
  - [ ] Database file unreadable without key
  - [ ] All CRUD operations work
  - [ ] Key recovery procedure documented

**[ ] Task 1.2: User Authentication (Days 1-5)**
- Priority: P0 (CRITICAL)
- Owner: Senior Engineer
- Effort: 35 hours
- Deliverables:
  - [ ] TechUser model with password_hash field
  - [ ] Bcrypt password hashing (12 rounds)
  - [ ] Login dialog UI
  - [ ] Session management
  - [ ] Account lockout (3 failed attempts)
  - [ ] Forced password change on first login
- Files Created:
  - `src/ui/dialogs/login_dialog.py`
  - `src/ui/dialogs/change_password_dialog.py`
- Files Modified:
  - `src/database/models.py`
  - `src/database/db_manager.py`
  - `src/main.py`
  - `src/core/session_manager.py`
- Acceptance Criteria:
  - [ ] No access without authentication
  - [ ] Passwords hashed with bcrypt
  - [ ] Account lockout after 3 failures
  - [ ] All actions attributed to user

#### ✅ Week 2 Tasks

**[ ] Task 1.3: Video Encryption (3 days)**
- Priority: P0 (CRITICAL)
- Owner: Senior Engineer
- Effort: 24 hours
- Deliverables:
  - [ ] VideoEncryptor class (AES-256-GCM)
  - [ ] Automatic encryption on recording stop
  - [ ] Video viewer with decryption
  - [ ] Temporary file cleanup
- Files Created:
  - `src/core/video_encryptor.py`
  - `src/ui/dialogs/video_viewer_dialog.py`
- Files Modified:
  - `src/hardware/camera_controller.py`
  - `requirements.txt` (add cryptography)
- Acceptance Criteria:
  - [ ] All videos encrypted
  - [ ] No plaintext on disk
  - [ ] Authenticated encryption (tamper detection)
  - [ ] Secure playback

**[ ] Task 1.4: Audit Trail Integrity (2 days)**
- Priority: P0 (CRITICAL)
- Owner: Senior Engineer
- Effort: 16 hours
- Deliverables:
  - [ ] HMAC-SHA256 signing for all events
  - [ ] Signature field added to SafetyLog
  - [ ] Verification tool script
  - [ ] Signing key secure storage (600 permissions)
- Files Modified:
  - `src/core/event_logger.py`
  - `src/database/models.py`
- Files Created:
  - `scripts/verify_audit_trail.py`
- Acceptance Criteria:
  - [ ] All events have signatures
  - [ ] Tampering detected
  - [ ] Key protected

**[ ] Task 1.5: Remove TestSafetyManager (1 day)**
- Priority: P0 (CRITICAL)
- Owner: Senior Engineer
- Effort: 8 hours
- Deliverables:
  - [ ] TestSafetyManager moved to tests/ directory
  - [ ] Test imports updated
  - [ ] Production build excludes test code
- Files Moved:
  - `src/core/safety.py` (TestSafetyManager class) → `tests/mocks/test_safety_manager.py`
- Acceptance Criteria:
  - [ ] Not importable in production
  - [ ] All tests still pass
  - [ ] Import error if attempted

**Week 1-2 Deliverables:**
- ✅ Database encryption implemented
- ✅ User authentication working
- ✅ Video encryption working
- ✅ Audit trail integrity protected
- ✅ Test code separated from production

---

### Week 3-4: Testing & Validation (P1)

#### ✅ Week 3 Tasks

**[ ] Task 2.1: Safety State Machine Unit Tests (5 days)**
- Priority: P1 (HIGH)
- Owner: Senior Engineer
- Effort: 40 hours
- Deliverables:
  - [ ] State transition tests (15 tests)
  - [ ] Interlock failure tests (10 tests)
  - [ ] Selective shutdown tests (5 tests)
  - [ ] Event logging tests (8 tests)
  - [ ] 100% coverage of src/core/safety.py
- Files Created:
  - `tests/core/test_safety_manager.py`
- Test Categories:
  - [ ] Initial state (UNSAFE)
  - [ ] UNSAFE → SAFE transitions
  - [ ] SAFE → UNSAFE on interlock failure
  - [ ] Emergency stop priority
  - [ ] Cannot exit E-STOP without reset
  - [ ] Selective shutdown verification
- Acceptance Criteria:
  - [ ] 100% line coverage
  - [ ] All state transitions tested
  - [ ] All interlocks tested
  - [ ] All tests pass

**[ ] Task 2.2: Protocol Engine Safety Tests (3 days)**
- Priority: P1 (HIGH)
- Owner: Senior Engineer
- Effort: 24 hours
- Deliverables:
  - [ ] Mid-execution interlock failure test
  - [ ] Emergency stop during protocol test
  - [ ] Protocol start validation test
  - [ ] Watchdog timeout test
- Files Created:
  - `tests/core/test_protocol_engine_safety.py`
- Test Scenarios:
  - [ ] Protocol halts on footpedal release
  - [ ] E-stop halts within 100ms
  - [ ] Protocol refuses to start if unsafe
  - [ ] Laser disabled on any failure
- Acceptance Criteria:
  - [ ] Safety paths 100% covered
  - [ ] Halt latency <200ms
  - [ ] Laser disabled immediately

#### ✅ Week 4 Tasks

**[ ] Task 2.3: 72-Hour Soak Test (3 days)**
- Priority: P1 (HIGH)
- Owner: QA Engineer + Senior Engineer
- Effort: 72 hours runtime + 8 hours analysis
- Deliverables:
  - [ ] Soak test script
  - [ ] Monitoring dashboard
  - [ ] Metrics collection (every 5 minutes)
  - [ ] HTML report with graphs
- Files Created:
  - `tests/integration/test_72hour_soak.py`
  - `tests/integration/soak_test_dashboard.py`
  - `data/soak_test_results/soak_test_report_YYYYMMDD.html`
- Monitored Metrics:
  - [ ] Memory usage (must be <20% growth)
  - [ ] CPU usage (average + peaks)
  - [ ] Session completion rate (≥95%)
  - [ ] Error rate (<5%)
  - [ ] Safety interlock responsiveness
- Acceptance Criteria:
  - [ ] ≥137/144 sessions completed (95%)
  - [ ] <7 errors (5%)
  - [ ] Memory <336 MB (20% growth from 280 MB)
  - [ ] No crashes
  - [ ] All interlocks responsive

**Week 3-4 Deliverables:**
- ✅ 100% safety test coverage
- ✅ Protocol engine safety validated
- ✅ 72-hour stability validated

---

### Week 5-6: Compliance Documentation (P1)

#### ✅ Week 5 Tasks

**[ ] Task 3.1: Risk Management File (ISO 14971) (5 days)**
- Priority: P1 (HIGH)
- Owner: Regulatory Consultant + Senior Engineer
- Effort: 40 hours
- Deliverables:
  - [ ] 30-50 hazards identified
  - [ ] FMEA analysis (severity × probability)
  - [ ] Risk matrix visualization
  - [ ] Mitigation measures documented
  - [ ] Residual risk evaluation
- Files Created:
  - `docs/compliance/RISK_MANAGEMENT_FILE.md`
  - `docs/compliance/FMEA_ANALYSIS.xlsx`
  - `docs/compliance/RISK_MATRIX.png`
- Key Hazards:
  - [ ] Excessive laser power
  - [ ] Laser activation without consent
  - [ ] Database breach (PHI exposure)
  - [ ] Footpedal failure
  - [ ] Vibration sensor failure
  - [ ] Watchdog timeout failure
  - ... (30-50 total)
- Acceptance Criteria:
  - [ ] All hazards documented
  - [ ] All risks evaluated
  - [ ] All mitigations linked
  - [ ] All residual risks acceptable

**[ ] Task 3.2: Software Requirements Specification (5 days)**
- Priority: P1 (HIGH)
- Owner: Senior Engineer + Regulatory Consultant
- Effort: 40 hours
- Deliverables:
  - [ ] 100-200 functional requirements
  - [ ] 30-50 safety requirements
  - [ ] 10-20 performance requirements
  - [ ] Requirements traceability matrix
- Files Created:
  - `docs/compliance/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`
  - `docs/compliance/REQUIREMENTS_TRACEABILITY_MATRIX.xlsx`
- Requirement Categories:
  - [ ] User authentication (FR-001 to FR-010)
  - [ ] Laser control (FR-011 to FR-030)
  - [ ] Safety interlocks (SR-001 to SR-020)
  - [ ] Emergency stop (SR-021 to SR-030)
  - [ ] Performance (PR-001 to PR-010)
- Acceptance Criteria:
  - [ ] All requirements unique IDs
  - [ ] All requirements testable
  - [ ] All requirements traced
  - [ ] All requirements prioritized

#### ✅ Week 6 Tasks

**[ ] Task 3.3: Verification & Validation Protocols (4 days)**
- Priority: P1 (HIGH)
- Owner: QA Engineer + Senior Engineer
- Effort: 32 hours
- Deliverables:
  - [ ] 30-40 test protocols
  - [ ] Safety test protocols (10 protocols)
  - [ ] Functional test protocols (20 protocols)
  - [ ] Performance test protocols (5 protocols)
  - [ ] Security test protocols (8 protocols)
- Files Created:
  - `docs/compliance/VV_PROTOCOLS/TP-SAFETY-001.md` (Emergency stop)
  - `docs/compliance/VV_PROTOCOLS/TP-SAFETY-002.md` (Footpedal)
  - `docs/compliance/VV_PROTOCOLS/TP-SAFETY-003.md` (Vibration sensor)
  - ... (30-40 total)
- Test Protocol Template:
  - [ ] Objective
  - [ ] Prerequisites
  - [ ] Test procedure (step-by-step)
  - [ ] Expected results
  - [ ] Pass criteria
  - [ ] Test data table
  - [ ] Result (PASS/FAIL)
- Acceptance Criteria:
  - [ ] All safety requirements have protocols
  - [ ] All protocols executed
  - [ ] Pass/fail criteria clear
  - [ ] Test data recorded

**Week 5-6 Deliverables:**
- ✅ ISO 14971 risk file complete
- ✅ SRS with 100+ requirements
- ✅ 30+ V&V protocols documented

---

### Week 7-8: Performance + Final Hardening (P1-P2)

#### ✅ Week 7 Tasks

**[ ] Task 4.1: Video Compression Tuning (1 day)**
- Priority: P1 (HIGH)
- Owner: Senior Engineer
- Effort: 8 hours
- Deliverables:
  - [ ] H.264 CRF 28 implementation
  - [ ] Side-by-side quality comparison
  - [ ] File size measurements
  - [ ] Clinical user approval
- Files Modified:
  - `src/hardware/camera_controller.py`
- Expected Results:
  - [ ] File size: 4 MB → 2 MB (50% reduction)
  - [ ] Quality: Acceptable for documentation
- Acceptance Criteria:
  - [ ] 50% file size reduction
  - [ ] Quality clinically acceptable
  - [ ] No frame drops

**[ ] Task 4.2: Database Vacuum Schedule (2 hours)**
- Priority: P1 (HIGH)
- Owner: Senior Engineer
- Effort: 2 hours
- Deliverables:
  - [ ] Auto VACUUM on shutdown
  - [ ] Manual VACUUM via admin menu
  - [ ] Incremental vacuum enabled
- Files Modified:
  - `src/database/db_manager.py`
  - `src/ui/main_window.py`
- Acceptance Criteria:
  - [ ] VACUUM runs on shutdown
  - [ ] Admin menu triggers VACUUM
  - [ ] Space reclaimed after deletes

**[ ] Task 4.3: Protocol File HMAC Signatures (2 days)**
- Priority: P2 (MEDIUM)
- Owner: Senior Engineer
- Effort: 16 hours
- Deliverables:
  - [ ] HMAC signature on protocol save
  - [ ] Signature verification on protocol load
  - [ ] Tamper detection alerts
- Files Modified:
  - `src/core/protocol.py`
- Acceptance Criteria:
  - [ ] All protocols signed
  - [ ] Tampering detected
  - [ ] Load fails if invalid

**[ ] Task 4.4: Multi-Factor Authentication (3 days)**
- Priority: P2 (MEDIUM)
- Owner: Security Specialist
- Effort: 24 hours
- Deliverables:
  - [ ] TOTP-based MFA (pyotp)
  - [ ] QR code setup dialog
  - [ ] MFA verification on login
  - [ ] Backup codes generation
- Files Created:
  - `src/ui/dialogs/mfa_setup_dialog.py`
  - `src/ui/dialogs/mfa_verification_dialog.py`
- Files Modified:
  - `src/database/models.py` (add mfa_secret field)
  - `src/ui/dialogs/login_dialog.py`
- Acceptance Criteria:
  - [ ] MFA setup via QR code
  - [ ] Login requires TOTP code
  - [ ] Backup codes work

#### ✅ Week 8 Tasks

**[ ] Task 4.5: Security Penetration Testing (5 days)**
- Priority: P0 (CRITICAL)
- Owner: External Security Consultant
- Effort: 40 hours
- Test Scenarios:
  - [ ] SQL injection attempts
  - [ ] Authentication bypass attempts
  - [ ] Session hijacking attempts
  - [ ] Encryption verification
  - [ ] Privilege escalation attempts
  - [ ] Physical security testing
- Deliverables:
  - [ ] Penetration test report
  - [ ] Vulnerability list with severity
  - [ ] Remediation recommendations
  - [ ] Re-test verification
- Acceptance Criteria:
  - [ ] No critical vulnerabilities
  - [ ] All high vulnerabilities fixed
  - [ ] Re-test confirms fixes

**Week 7-8 Deliverables:**
- ✅ Video compression optimized
- ✅ Database maintenance automated
- ✅ Protocol tampering prevented
- ✅ MFA implemented
- ✅ Security testing complete

---

## Phase 7: Architecture + Performance (4 weeks)

**Objective:** Enhance architecture and optimize performance
**Team:** 1 senior engineer

### Week 9-10: Architecture Enhancements (P2)

#### ✅ Week 9 Tasks

**[ ] Task 5.1: Implement 4-State Safety Model (3 days)**
- Priority: P2 (MEDIUM)
- Owner: Senior Engineer
- Effort: 24 hours
- Current: 3 states (SAFE, UNSAFE, EMERGENCY_STOP)
- Target: 5 states (SAFE, ARMED, TREATING, UNSAFE, EMERGENCY_STOP)
- Deliverables:
  - [ ] Add ARMED and TREATING states
  - [ ] Update state transition logic
  - [ ] Update UI to show 5 states
  - [ ] Update documentation
  - [ ] 100% state machine test coverage
- Files Modified:
  - `src/core/safety.py`
  - `src/ui/widgets/safety_widget.py`
  - `src/ui/main_window.py`
  - `docs/architecture/03_safety_system.md`
- Acceptance Criteria:
  - [ ] All 5 states implemented
  - [ ] UI shows current state
  - [ ] Audit trail logs transitions
  - [ ] 100% test coverage

**[ ] Task 5.2: Document Asyncio Event Loop Integration (1 day)**
- Priority: P2 (MEDIUM)
- Owner: Senior Engineer
- Effort: 8 hours
- Deliverables:
  - [ ] Investigation of current implementation
  - [ ] Event loop integration documented
  - [ ] qasync migration plan (if needed)
  - [ ] Performance validation
- Files Modified:
  - `docs/architecture/10_concurrency_model.md`
  - `CLAUDE.md`
  - Potentially `src/main.py` (if qasync needed)
- Acceptance Criteria:
  - [ ] Event loop strategy documented
  - [ ] Limitations documented
  - [ ] GUI responsiveness validated

#### ✅ Week 10 Tasks (Buffer + Code Quality)

**[ ] Task 5.3: Split gpio_controller.py into Modules (4 hours)**
- Priority: P3 (LOW)
- Owner: Senior Engineer
- Effort: 4 hours
- Current: Single 850-line file
- Target: Modular structure (5 files, <200 lines each)
- Files Created:
  - `src/hardware/gpio/__init__.py`
  - `src/hardware/gpio/gpio_controller.py` (200 lines)
  - `src/hardware/gpio/vibration_monitor.py` (150 lines)
  - `src/hardware/gpio/photodiode_monitor.py` (100 lines)
  - `src/hardware/gpio/motor_controller.py` (120 lines)
  - `src/hardware/gpio/interlock_manager.py` (280 lines)
- Acceptance Criteria:
  - [ ] gpio_controller.py <300 lines
  - [ ] Each component <200 lines
  - [ ] All functionality preserved
  - [ ] All tests pass

**Week 9-10 Deliverables:**
- ✅ 4-state safety model implemented
- ✅ Asyncio integration documented
- ✅ GPIO controller modularized

---

### Week 11-12: Performance Enhancements (P2)

#### ✅ Week 11 Tasks

**[ ] Task 6.1: Implement Log Rotation (1 day)**
- Priority: P2 (MEDIUM)
- Owner: Senior Engineer
- Effort: 8 hours
- Deliverables:
  - [ ] Daily log rotation
  - [ ] Gzip compression of old logs
  - [ ] 7-year retention policy
  - [ ] Automatic cleanup
- Files Created:
  - `src/core/log_rotator.py`
- Files Modified:
  - `src/ui/main_window.py` (schedule timer)
- Acceptance Criteria:
  - [ ] Logs rotate daily
  - [ ] Old logs compressed
  - [ ] 7-year retention enforced
  - [ ] No events lost

**[ ] Task 6.2: Performance Monitoring Dashboard (2 days)**
- Priority: P2 (MEDIUM)
- Owner: Senior Engineer
- Effort: 16 hours
- Deliverables:
  - [ ] Frame rate gauge (camera FPS)
  - [ ] Memory usage graph
  - [ ] CPU usage meter
  - [ ] Disk space warning
  - [ ] Event log rate monitor
- Files Created:
  - `src/ui/widgets/performance_dashboard.py`
- Files Modified:
  - `src/ui/main_window.py` (add dock widget)
- Acceptance Criteria:
  - [ ] Real-time FPS display
  - [ ] Memory trend graph
  - [ ] Disk warning <5 GB
  - [ ] Dev mode only

#### ✅ Week 12 Tasks (Code Quality)

**[ ] Task 7.1: Refactor Protocol Engine Action Dispatch (1 day)**
- Priority: P3 (LOW)
- Owner: Senior Engineer
- Effort: 8 hours
- Current: if/elif chain (CC=22)
- Target: Strategy pattern (CC<5)
- Deliverables:
  - [ ] ActionExecutor base class
  - [ ] 12 executor classes (one per action type)
  - [ ] Registry-based dispatch
- Files Created:
  - `src/core/protocol_executors/base.py`
  - `src/core/protocol_executors/set_laser_power_executor.py`
  - ... (12 total)
- Acceptance Criteria:
  - [ ] Cyclomatic complexity <5
  - [ ] All tests pass
  - [ ] Easy to add new actions

**[ ] Task 7.2: Complete Type Hint Coverage (2 hours)**
- Priority: P3 (LOW)
- Owner: Senior Engineer
- Effort: 2 hours
- Current: 95% coverage
- Target: 100% coverage
- Deliverables:
  - [ ] Add type hints to remaining 5%
  - [ ] Run MyPy strict mode
  - [ ] Fix any new type errors
- Acceptance Criteria:
  - [ ] 100% public function coverage
  - [ ] 95%+ private function coverage
  - [ ] MyPy strict passes

**Week 11-12 Deliverables:**
- ✅ Log rotation implemented
- ✅ Performance dashboard added
- ✅ Protocol engine refactored
- ✅ Type hints complete

---

## Phase 8+: Post-Production Enhancements

**Objective:** Continuous improvement and developer experience
**Team:** 1 engineer (part-time)

### Code Quality (P3)

**[ ] Task 8.1: Formalize LaserController Inheritance (2 hours)**
- Priority: P3 (LOW)
- Change: `class LaserController(QObject)` → `class LaserController(HardwareControllerBase)`
- Benefit: Type checking, explicit contract
- Files Modified: `src/hardware/laser_controller.py`

### Developer Experience (P3)

**[ ] Task 8.2: Pre-Commit Hook Documentation (1 hour)**
- Priority: P3 (LOW)
- Deliverable: `docs/development/PRE_COMMIT_HOOKS.md`
- Content: MyPy known issues, --no-verify usage

**[ ] Task 8.3: Development Setup Guide (2 hours)**
- Priority: P3 (LOW)
- Deliverable: `docs/development/SETUP_GUIDE.md`
- Content: Environment setup, troubleshooting

---

## Success Metrics

### Phase 6 Exit Criteria

**Security:**
- ✅ Database encrypted (SQLCipher)
- ✅ User authentication working
- ✅ Video encryption working
- ✅ Audit trail integrity protected
- ✅ Penetration testing passed

**Testing:**
- ✅ 100% safety test coverage
- ✅ 72-hour soak test passed (≥95% completion)
- ✅ <5% error rate

**Documentation:**
- ✅ Risk Management File complete
- ✅ SRS with 100+ requirements
- ✅ 30+ V&V protocols

**Compliance:**
- ✅ FDA 21 CFR Part 11: 5/5 PASS
- ✅ HIPAA: 3/3 PASS
- ✅ IEC 62304: 6/6 PASS

### Phase 7 Exit Criteria

**Architecture:**
- ✅ 4-state safety model implemented
- ✅ Asyncio integration documented

**Performance:**
- ✅ Log rotation working
- ✅ Performance dashboard functional
- ✅ Video compression optimized
- ✅ Database vacuum automated

### Production Ready Checklist

- [ ] All P0 security issues resolved
- [ ] All P1 testing complete
- [ ] All P1 documentation complete
- [ ] FDA 21 CFR Part 11 compliant
- [ ] HIPAA compliant
- [ ] IEC 62304 documentation complete
- [ ] Penetration testing passed
- [ ] 72-hour soak test passed
- [ ] Risk file approved
- [ ] SRS approved
- [ ] V&V protocols executed

---

## Resource Allocation

### Phase 6 (Weeks 1-8)

| Week | Senior Engineer | Security Specialist | Regulatory Consultant | QA Engineer |
|------|----------------|---------------------|----------------------|-------------|
| 1-2  | Security fixes | Security review | - | - |
| 3    | Testing | - | - | Testing |
| 4    | Soak test monitoring | - | - | Soak test |
| 5    | Risk file + SRS | - | Risk file + SRS | - |
| 6    | V&V protocols | - | V&V review | V&V protocols |
| 7    | Performance | - | - | - |
| 8    | - | Penetration testing | - | - |

### Phase 7 (Weeks 9-12)

| Week | Senior Engineer |
|------|----------------|
| 9-10 | Architecture enhancements |
| 11-12 | Performance + Code quality |

### Budget Breakdown

| Role | Hourly Rate | Hours | Cost |
|------|-------------|-------|------|
| Senior Software Engineer | $150/hr | 320 hrs | $48,000 |
| Security Specialist | $175/hr | 80 hrs | $14,000 |
| Regulatory Consultant | $200/hr | 80 hrs | $16,000 |
| **Total** | - | **480 hrs** | **$78,000** |

---

## Risk Management

### Top Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SQLCipher performance issues | Medium | High | Benchmark early, optimize |
| 72-hour soak test failures | Medium | High | Fix incrementally, re-run |
| FDA regulatory delays | High | High | Engage consultant early |
| Penetration test finds criticals | Medium | High | Budget 1-week buffer |
| Authentication UX complexity | Low | Medium | User testing with technicians |

### Contingency Plans

**If security tasks take longer than 2 weeks:**
- Extend Phase 6 by 1 week
- Delay Phase 7 start

**If 72-hour soak test fails:**
- Analyze failures
- Fix issues
- Re-run test (add 1 week)

**If penetration test finds critical vulnerabilities:**
- Allocate 1 week for remediation
- Re-test before proceeding

---

## Weekly Check-ins

**Format:** 30-minute standup every Monday
**Attendees:** Engineering team + stakeholders

**Agenda:**
1. Previous week accomplishments
2. Current week goals
3. Blockers/risks
4. Budget status
5. Timeline adjustments (if needed)

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-30 | Initial roadmap created from comprehensive review |

---

**Next Action:** Review with stakeholders, confirm budget, begin Phase 6 Week 1

**Questions/Concerns:** Contact project lead or review team
