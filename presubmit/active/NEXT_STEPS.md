# TOSCA - Next Steps & Roadmap

**Last Updated:** 2025-10-25
**Current Phase:** Phase 3 (Core Business Logic) - 60% complete
**Priority:** Code quality improvements and hardware command review

---

## Immediate Priority: Hardware Command Review

**Purpose:** Cross-reference all hardware commands in code with manufacturer documentation

**Why Critical:**
- Ensure Hardware API Usage Rule compliance
- Verify we're using native hardware features correctly
- Catch any software workarounds that should use hardware features
- Document command syntax matches manufacturer specifications

### Task: Review Camera Commands

**What:** Cross-reference camera_controller.py with VmbPy API documentation

**Files to Review:**
- `src/hardware/camera_controller.py` - Camera HAL implementation
- `components/camera_module/manufacturer_docs/vmbpy_api_reference/Feature.txt`
- `components/camera_module/manufacturer_docs/vmbpy_api_reference/Camera.txt`

**Check:**
- [ ] All features used are documented in Feature.txt
- [ ] Feature names match API reference exactly
- [ ] Using hardware `AcquisitionFrameRate` (not software throttling)
- [ ] Auto features (ExposureAuto, GainAuto) used correctly
- [ ] Frame streaming follows Camera.txt patterns
- [ ] Error handling matches Error.txt guidelines

**Document findings in:** `components/camera_module/LESSONS_LEARNED.md`

---

### Task: Review Actuator Commands

**What:** Cross-reference actuator_controller.py with Xeryon command reference

**Files to Review:**
- `src/hardware/actuator_controller.py` - Actuator HAL implementation
- `components/actuator_module/manufacturer_docs/xeryon_manuals/Controller Manual.pdf`
- `components/actuator_module/manufacturer_docs/xeryon_library/Xeryon.py`

**Check:**
- [ ] Position commands match Controller Manual (P, R commands)
- [ ] Velocity commands use correct range (0.5-400 mm/s)
- [ ] Acceleration/deceleration use correct range (1000-65500)
- [ ] Homing command (H) implemented per manual
- [ ] Status queries match manual syntax
- [ ] Using hardware acceleration profiles (not software ramping)

**Document findings in:** `components/actuator_module/LESSONS_LEARNED.md`

---

### Task: Review Laser Commands

**What:** Cross-reference laser_controller.py with Arroyo command reference

**Files to Review:**
- `src/hardware/laser_controller.py` - Laser HAL implementation
- `components/laser_control/manufacturer_docs/arroyo_manuals/ArroyoComputerInterfacingManual.pdf`
- `components/laser_control/manufacturer_docs/arroyo_sdk/arroyo_tec/`

**Check:**
- [ ] Current commands match ArroyoComputerInterfacingManual.pdf syntax
- [ ] `LAS:SET:CURRent` used correctly with range validation
- [ ] `LAS:OUT` enable/disable follows protocol
- [ ] TEC commands (`TEC:SET:TEMPerature`) match manual
- [ ] Status queries (`*IDN?`, `LAS:LIM:CURRent?`) implemented
- [ ] Error handling uses `SYSTem:ERRor?` as documented
- [ ] Command terminators correct (CR+LF for send, LF for receive)

**Document findings in:** `components/laser_control/ARROYO_API_REFERENCE.md`

---

### Task: Create Hardware Command Matrix

**What:** Create comprehensive matrix of all hardware commands vs documentation

**Create file:** `components/HARDWARE_COMMAND_CROSS_REFERENCE.md`

**Format:**
```markdown
| Hardware | Command | Code Location | Manual Reference | Status |
|----------|---------|---------------|------------------|--------|
| Camera | AcquisitionFrameRate | camera_controller.py:235 | Feature.txt:1250 | ✓ Verified |
| Actuator | P<pos> | actuator_controller.py:142 | Controller Manual p.23 | ✓ Verified |
| Laser | LAS:SET:CURRent | laser_controller.py:178 | ArroyoManual p.45 | ✓ Verified |
```

**Include:**
- Every hardware command/feature used in production code
- Exact file location (file:line)
- Exact manual reference (file:page or section)
- Verification status

---

## Current Phase 3 Work

### In Progress (60% Complete)

**Safety System (95%):**
- [x] SafetyManager core implementation
- [x] GPIO interlock integration
- [x] Session validity checking
- [x] Emergency stop functionality
- [x] SafetyWidget event display
- [ ] Hardware integration testing (Arduino GPIO)

**Session Management (100%):**
- [x] Database models (TechUser, Subject, Protocol, Session)
- [x] SessionManager core implementation
- [x] Automatic folder creation
- [x] SubjectWidget GUI complete
- [x] Database persistence working

**Event Logging (50%):**
- [x] EventLogger core implementation
- [x] 25+ event types defined
- [x] Dual persistence (database + JSONL)
- [x] Session association
- [ ] Hardware controller integration
- [ ] Event display in Safety tab
- [ ] Event export functionality

---

## Phase 4 Preview: Integration & Testing

### Prerequisites
- [ ] Phase 3 reaches 100% completion
- [ ] Hardware command review complete
- [ ] All code quality improvements from review implemented

### Phase 4 Tasks (Not Started)

**1. Hardware Integration Testing:**
- Test all 4 HALs together
- Verify safety interlocks with real hardware
- Test protocol execution end-to-end
- Validate session management with hardware

**2. GUI Polish:**
- Final UI/UX improvements
- Accessibility compliance
- Error message clarity
- Loading states and progress indicators

**3. Performance Optimization:**
- Profile application performance
- Optimize database queries
- Reduce GUI latency
- Improve camera streaming efficiency

**4. Documentation:**
- User manual
- Operator training guide
- Maintenance procedures
- Troubleshooting guide

---

## Code Quality Improvements

### From Recent Code Review (2025-10-24)

**Critical Issues Addressed:**
- ✓ Emergency stop now disables laser output
- ✓ Removed blocking time.sleep() calls (replaced with QTimer)
- ✓ Fixed placeholder code with NotImplementedError
- ✓ Added issue references to TODO comments
- ✓ Added logging to silent exception handlers

**Remaining Improvements (Optional):**
See `presubmit/reviews/improvements/` for detailed implementation plans:
- 01_IMPORT_PATH_STANDARDIZATION.md
- 02_HARDWARE_CONTROLLER_ABC.md
- 03_CONFIGURATION_MANAGEMENT.md (CRITICAL)
- 04_WATCHDOG_TIMER_IMPLEMENTATION.md (CRITICAL)
- 05_DEPENDENCY_INJECTION.md (CRITICAL)

---

## Documentation Updates Completed (2025-10-25)

**TodoWrite Documentation:**
- ✓ Added TodoWrite section to CODING_STANDARDS.md
- ✓ Created TODO_GUIDELINES.md comprehensive guide
- ✓ Updated pre-commit REMINDER.txt
- ✓ Added post-action checklist to CODING_STANDARDS.md
- ✓ Updated MCP memory with todo workflow

**Presubmit Folder Reorganization:**
- ✓ Merged duplicate files
- ✓ Created clear folder hierarchy (onboarding, active, reference, reviews)
- ✓ Updated all cross-references
- ✓ Created FULL_SESSION_PROMPT.md and QUICK_SESSION_PROMPT.md
- ✓ Cleaned onboarding folder (removed redundancy)

**Manufacturer Documentation:**
- ✓ Organized all manufacturer docs into component folders
- ✓ Created manufacturer_docs/README.md for each component
- ✓ Created MANUFACTURER_DOCS_INDEX.md central index
- ✓ Updated CODING_STANDARDS.md with doc references
- ✓ Total: 8.3 MB of organized documentation

---

## Weekly Goals

### This Week
- [ ] Complete hardware command cross-reference review
- [ ] Create HARDWARE_COMMAND_CROSS_REFERENCE.md
- [ ] Update LESSONS_LEARNED.md files with findings
- [ ] Address any hardware API usage violations found
- [ ] Complete Event Logging hardware integration

### Next Week
- [ ] Finish Phase 3 (reach 100%)
- [ ] Hardware integration testing
- [ ] Begin Phase 4 planning

---

## Long-Term Roadmap

### Phase 3: Core Business Logic (CURRENT - 60%)
**Target:** Complete by end of month
- Finish event logging integration
- Complete safety system hardware testing

### Phase 4: Integration & Testing (Next - 0%)
**Target:** 4-6 weeks
- End-to-end hardware testing
- GUI polish
- Performance optimization
- User documentation

### Phase 5: Regulatory Preparation (Future - 0%)
**Target:** TBD
- FDA documentation compilation
- Validation testing
- Regulatory submission preparation

---

**Last Updated:** 2025-10-25
**Location:** presubmit/active/NEXT_STEPS.md
