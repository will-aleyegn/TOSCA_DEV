# Code Review Addendum - README Update

**Date:** 2025-10-26

## Add to README.md

Insert this section after "## Safety & Compliance Development Guidelines":

---

## ⚠️ Code Review Findings (2025-10-26)

**Comprehensive code review completed** - See `docs/CODE_REVIEW_2025-10-26.md` for full report.

### Critical Issues Identified (17 total)
**CRITICAL (6):**
1. Safety watchdog initialization race condition
2. No real-time safety monitoring during protocol execution
3. Dev mode bypasses safety in production code
4. Watchdog failure doesn't initiate laser shutdown
5. Insufficient test coverage (~13 files for ~10,500 LOC)
6. No hardware mock layer for testing

**HIGH (5):**
- MainWindow God Object (SRP violation)
- QTimer threading risk (GUI freeze potential)
- Tests excluded from mypy type checking
- Serial communication not thread-safe

**MEDIUM (6) + LOW (2)**

### Selective Shutdown Policy Clarified

**IMPORTANT:** When safety fails, **only treatment laser** shuts down:
- ✅ Camera continues (monitoring)
- ✅ Actuator controllable (repositioning)
- ✅ Aiming laser available (alignment)
- ✅ GPIO monitoring active (diagnostics)

See: `docs/architecture/SAFETY_SHUTDOWN_POLICY.md`

### Action Plan
**Week 1:** Fix CRITICAL safety issues
**Week 2:** Build comprehensive test suite
**Week 3-4:** Architecture improvements
**Week 5:** Code quality
**Week 6:** Integration testing

---

## Updated Development Guidelines

### Safety First (Updated)
- **Selective shutdown:** Only treatment laser disabled on fault
- **Real-time monitoring:** Safety checks during all operations, not just at start
- All safety-critical code needs 100% test coverage
- Safety interlocks cannot be bypassed in production builds
- Comprehensive event logging for audit trail

### Code Quality (Updated)
- Type hints for ALL functions (including tests - now enforced)
- Thread-safe serial communication (add locking)
- Hardware mock interfaces required
- Target: 80%+ overall coverage, **100% for safety systems**

---
