# Software Development Section - Version Comparison

**Date:** 2025-10-15

## Three Versions Created

You now have three versions of the Software Development section, each optimized for different purposes:

| Version | Size | Lines | Use Case |
|---------|------|-------|----------|
| **Minimal Changes** | 29 KB | 452 | **Direct replacement** of your current document - keeps original structure |
| **Pre-Submission** | 37 KB | 659 | FDA Pre-Sub meeting - flexible, seeks feedback |
| **Detailed** | 81 KB | 1,250 | Final 510(k) submission - complete specification |

---

## Version 1: Minimal Changes (RECOMMENDED FOR NOW)
**File:** `docs/software_development_section_v2_minimal_changes.md`

### Purpose
Direct replacement for your current Section 1 with minimal disruption while incorporating today's architectural decisions.

### What Was Changed
1. ✅ **Added Section 1.3.3** - Camera & Image Processing (new module - essential addition)
2. ✅ **Expanded Section 1.3.9** - Safety Management with hardware interlocks detail
3. ✅ **Updated Section 1.3.2** - Clarified footpedal is safety interlock, not "accessory"
4. ✅ **Enhanced Section 1.3.4** - Data Management with audit trail architecture
5. ✅ **Renamed Section 1.3.5** - "Actuator & Peripheral Control" with ring size calibration
6. ✅ **Updated block diagram** - Shows all components including GPIO interlocks

### What Was NOT Changed
- ✅ Sections 1.1, 1.2 kept EXACTLY as you wrote them
- ✅ Section 1.3 introduction kept verbatim
- ✅ Sections 1.4-1.8 kept EXACTLY as written, including "Will, I will prepare a draft"
- ✅ Your writing style and tone preserved throughout
- ✅ Your bullet formatting and structure maintained
- ✅ Original module descriptions kept where still accurate

### Module Numbering Changes
Because Camera & Image Processing was inserted as 1.3.3, subsequent modules shifted:

| Your Original | Minimal Changes Version | Change |
|---------------|------------------------|--------|
| 1.3.1 GUI | 1.3.1 GUI | Same |
| 1.3.2 Accessories Control | 1.3.2 Operator Input Devices | Renamed |
| 1.3.3 Data Management | **1.3.3 Camera & Image Processing** | **NEW** |
| (new section) | 1.3.4 Data Management | Moved from 1.3.3 |
| 1.3.4 Embedded Devices | 1.3.5 Actuator & Peripheral Control | Moved/renamed |
| 1.3.5 Laser Control | 1.3.6 Laser Control & TEC | Moved |
| 1.3.6 Session Control | 1.3.7 Session Control | Moved |
| 1.3.7 Monitoring | 1.3.8 Monitoring and Alerting | Moved |
| 1.3.8 Safety Management | 1.3.9 Safety Management | Moved, EXPANDED |
| 1.3.9 Logging | 1.3.10 Logging and Reporting | Moved |
| 1.3.10 Error Handling | 1.3.11 Error Handling | Moved |

**Result:** 10 modules became 11 modules (Camera added)

### Safety Management Expansion Detail
Your original 1.3.8 Safety Management was about 50 words (very brief).
The updated 1.3.9 Safety Management is now approximately 1,500 words with:
- Architecture philosophy clearly stated
- Three hardware interlocks fully specified (footpedal, smoothing device, photodiode)
- Four software interlocks described
- Safety state machine explained
- Fault response procedures outlined
- Watchdog timer documented
- Safety logging requirements specified

**Why this expansion was necessary:** Enhanced Documentation Level requires detailed safety architecture. This was the most critical gap in the original document.

### When to Use This Version
- **Now:** Replace your current Section 1 in Product Development Plan
- **Internal reviews:** Share with your team for architecture alignment
- **Development planning:** Use as foundation for SRS and SDS development

---

## Version 2: Pre-Submission (FLEXIBLE)
**File:** `docs/software_development_section_presub.md`

### Purpose
FDA Pre-Submission meeting document that shows competence without locking you into specific implementations.

### Key Characteristics
- **Flexible language:** "We plan to...", "Under consideration...", "Anticipated approach..."
- **Seeks feedback:** 15 embedded FDA questions throughout
- **Shows competence:** Demonstrates understanding of safety requirements
- **Avoids commitments:** No hard numbers that become requirements (100 Hz → "high frequency")
- **Conceptual architecture:** Explicitly noted as "subject to refinement"

### Example Language Differences

**Minimal Changes version (prescriptive):**
> "Monitored at ≥100 Hz (every 10ms or faster)"

**Pre-Sub version (flexible):**
> "High-frequency monitoring approach under evaluation"

**Minimal Changes version:**
> "20ms debounce period prevents false triggers"

**Pre-Sub version:**
> "Debouncing strategy under consideration to prevent false triggers"

### FDA Questions Embedded
The pre-sub version includes 15 questions such as:
1. Is a footpedal-type deadman switch appropriate for this device class?
2. What is FDA's expectation regarding monitoring of beam conditioning elements?
3. What level of power deviation should trigger automatic shutdown vs. operator warning?
4. Should camera feed loss trigger immediate shutdown or operator alert with option to continue?
5. What level of detail does FDA expect in Software Design Specification?
...and 10 more

### When to Use This Version
- **FDA Pre-Sub meeting:** Submit this version when seeking FDA feedback
- **Before design lock:** Use when architecture is still being refined
- **Risk mitigation:** Prevents committing to implementations before validation

---

## Version 3: Detailed (COMPREHENSIVE)
**File:** `docs/software_development_section_v2.md`

### Purpose
Final 510(k) submission document with complete specifications and verification approach.

### Key Characteristics
- **Prescriptive specifications:** Exact numbers, timing requirements, thresholds
- **Complete implementation details:** Every module fully documented
- **Safety Management:** 2,000+ words with exhaustive specification
- **Verification requirements:** Test expectations for each module
- **Regulatory-ready:** Definitive statements of implemented functionality

### Example Language Differences

**Pre-Sub version:**
> "We are considering implementing a footpedal"

**Detailed version:**
> "The footpedal deadman switch is monitored at ≥100 Hz with 20ms debounce and <100ms shutdown response time"

**Pre-Sub version:**
> "Graduated threshold approach under evaluation"

**Detailed version:**
> "Two-tier threshold system: 15% deviation triggers warning, 30% deviation triggers fault with immediate shutdown"

### Additional Content vs. Minimal Changes
The detailed version adds approximately 800 lines beyond the minimal changes version, including:
- Rationale sections for critical design decisions
- Algorithm descriptions with implementation notes
- Verification and validation approaches for each module
- Failure mode considerations
- Traceability expectations
- Configuration management procedures
- Complete OTS vs IDS classification

### When to Use This Version
- **510(k) submission:** Use after design is finalized and verified
- **After FDA pre-sub feedback:** Incorporate FDA comments and update to this version
- **Post-verification:** Update with actual test results and verified performance
- **Design freeze:** Use when ready to commit to specific implementations

---

## Recommended Workflow

### Phase 1: Now (Use Minimal Changes)
1. Replace your current Section 1 with **Minimal Changes version**
2. Share with your team for architectural alignment
3. Begin SRS development based on this architecture
4. Conduct internal design reviews

### Phase 2: FDA Pre-Submission (Use Pre-Sub)
1. Switch to **Pre-Submission version** when ready for FDA meeting
2. Submit to FDA with your pre-sub package
3. Present architecture showing safety awareness
4. Ask embedded questions and collect FDA feedback
5. Document FDA responses and recommendations

### Phase 3: Development (Evolve from Minimal Changes)
1. Continue using **Minimal Changes version** as living document
2. Incorporate FDA feedback from pre-sub meeting
3. Refine based on risk analysis findings
4. Update as design decisions are made
5. Add verification results as testing completes

### Phase 4: Submission (Use Detailed)
1. Transition to **Detailed version** for 510(k) submission
2. Update with finalized specifications
3. Include actual verification test results
4. Add real performance data (not targets)
5. Ensure traceability to requirements and risk controls

---

## Quick Reference: Which Version When?

| Situation | Use This Version | Why |
|-----------|-----------------|-----|
| Replacing current doc | Minimal Changes | Preserves your structure with essential updates |
| Team reviews | Minimal Changes | Clear, concise, good foundation for SRS/SDS |
| SRS/SDS development starts | Minimal Changes | Stable architecture to design from |
| FDA Pre-Sub meeting | Pre-Submission | Flexible, seeks feedback, avoids commitments |
| Design still evolving | Pre-Submission | Doesn't lock you in |
| Risk analysis in progress | Minimal Changes | Can refine as hazards identified |
| Design frozen | Detailed | Documents actual implementation |
| Verification complete | Detailed | Includes test results, proven performance |
| 510(k) submission | Detailed | Complete specification, regulatory-ready |

---

## File Locations

All versions saved in `docs/` directory:

```
docs/
├── software_development_section_v2_minimal_changes.md    # 29 KB - Use now
├── software_development_section_presub.md                # 37 KB - Use for FDA pre-sub
└── software_development_section_v2.md                    # 81 KB - Use for 510(k)
```

Supporting files:
```
docs/architecture/
├── software_block_diagram.mmd                  # Visual diagram source (Mermaid)
└── diagram_rendering_instructions.md           # How to render diagram
```

---

## Summary of Today's Architectural Decisions Captured

All three versions capture these key decisions from today's planning session:

1. ✅ **Camera & Image Processing** is a major module (not buried in "embedded devices")
2. ✅ **GPIO Hardware Interlocks** are explicit and detailed:
   - Footpedal deadman switch (GPIO-1 digital)
   - Hotspot smoothing device monitor (GPIO-1 digital/analog)
   - Photodiode power monitor (GPIO-2 ADC)
3. ✅ **Safety Management** is highest priority with override authority
4. ✅ **Footpedal is NOT an "accessory"** - it's a safety-critical interlock
5. ✅ **Actuator controls ring size** (2-5mm) - treatment parameter, requires calibration
6. ✅ **Two-tier logging** - high-freq buffered to JSON, events to database
7. ✅ **Complete audit trail** with immutable safety_log table
8. ✅ **Fail-safe design** - any uncertainty → laser disabled
9. ✅ **Multiple independent interlocks** - hardware + software
10. ✅ **Camera feed validity** - prerequisite for laser operation

---

## Recommendation

**Start with Minimal Changes version** (`software_development_section_v2_minimal_changes.md`) as your working document. It:
- Preserves your original structure and style
- Incorporates all of today's decisions
- Is immediately usable as replacement for current Section 1
- Provides solid foundation for SRS and SDS development
- Can evolve as design progresses

**Switch to Pre-Sub version** when ready for FDA meeting - you have it ready to go.

**Evolve to Detailed version** as design finalizes and verification completes.

---

**Created:** 2025-10-15
**Purpose:** Guide for selecting appropriate software documentation version
