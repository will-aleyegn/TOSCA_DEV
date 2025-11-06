# Hardware Tab Functional Grouping Design Proposals

**Date:** 2025-11-06
**Project:** TOSCA Laser Control System v0.9.14-alpha
**Purpose:** Three layout options for Hardware Tab functional grouping (Phase 4A)
**Status:** PENDING USER APPROVAL

---

## APPROVAL GATE: Choose Your Preferred Design

**Signal/Slot Audit Status:** ✅ PASSED (all 91 connections validated, safe to proceed)
**Decision Required:** Select Option A, B, or C below

---

## Current State vs. Proposed Changes

### Current Problems (From UI/UX Analysis)

**Problem 1: Laser System Fragmentation**
Laser-related controls scattered across 5 separate widgets:
- Treatment Laser (left column)
- TEC Temperature (left column, same widget)
- Aiming Laser (left column, same widget, requires GPIO)
- GPIO Connection (right column, top) - enables aiming laser
- Smoothing Motor (right column, second widget) - improves beam quality

**Problem 2: Cross-Column Dependencies**
User must navigate between left/right columns to activate related hardware:
1. Right column → Connect GPIO (enables aiming + smoothing)
2. Left column → Connect treatment laser
3. Left column → Connect TEC (same widget)
4. Left column → Turn on aiming laser (requires GPIO from step 1)
5. Right column → Start smoothing motor (requires GPIO from step 1)

**Problem 3: Unclear Hardware Dependencies**
No visual indication that:
- Aiming laser requires GPIO connection
- Smoothing motor requires GPIO connection
- TEC should be enabled before treatment laser (thermal stabilization)
- Photodiode monitors treatment laser output

---

## OPTION A: Task-Based Workflow Grouping

**Concept:** Reorganize by operator workflow stages (Setup → Calibrate → Treat → Monitor)

### Visual Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ Hardware & Diagnostics Tab                                       │
├────────────────────────────┬─────────────────────────────────────┤
│ LEFT: WORKFLOW STAGES      │ RIGHT: SAFETY & DIAGNOSTICS         │
├────────────────────────────┼─────────────────────────────────────┤
│                            │                                     │
│ ┌──────────────────────┐   │ ┌──────────────────────────────┐   │
│ │ STAGE 1: SYSTEM SETUP│   │ │ SAFETY MONITORING            │   │
│ ├──────────────────────┤   │ ├──────────────────────────────┤   │
│ │ • GPIO Connection    │   │ │ • Footpedal Status (D5)      │   │
│ │ • TEC Connection     │   │ │   - Pressed/Released         │   │
│ │ • TEC Enable         │   │ │   - Safety interlock         │   │
│ │ • TEC Setpoint       │   │ │                              │   │
│ │ • Wait for thermal   │   │ │ • Photodiode Power (A0)      │   │
│ │   stabilization      │   │ │   - Voltage: 0-5V            │   │
│ └──────────────────────┘   │ │   - Calculated power (mW)    │   │
│                            │ │                              │   │
│ ┌──────────────────────┐   │ │ • Overall Safety Status      │   │
│ │ STAGE 2: CALIBRATION │   │ │   - State machine            │   │
│ │ & ALIGNMENT          │   │ │   - Laser enable permission  │   │
│ ├──────────────────────┤   │ └──────────────────────────────┘   │
│ │ • Camera Connection  │   │                                     │
│ │ • Exposure/Gain      │   │ ┌──────────────────────────────┐   │
│ │ • Actuator Connect   │   │ │ SAFETY EVENT LOG             │   │
│ │ • Actuator Homing    │   │ │ • Filtered event display     │   │
│ │ • Aiming Laser ON    │   │ │ • Severity levels            │   │
│ │   (requires GPIO)    │   │ │ • Search functionality       │   │
│ │ • Position Actuator  │   │ └──────────────────────────────┘   │
│ └──────────────────────┘   │                                     │
│                            │ ┌──────────────────────────────┐   │
│ ┌──────────────────────┐   │ │ CONFIGURATION                │   │
│ │ STAGE 3: TREATMENT   │   │ │ • Collapsible display        │   │
│ │ EXECUTION            │   │ │ • System settings            │   │
│ ├──────────────────────┤   │ └──────────────────────────────┘   │
│ │ • Laser Connection   │   │                                     │
│ │ • Laser Current      │   │                                     │
│ │ • ENABLE OUTPUT      │   │                                     │
│ │ • Smoothing Motor ON │   │                                     │
│ │   (requires GPIO)    │   │                                     │
│ │ • Protocol Execution │   │                                     │
│ │ • Real-time Monitor  │   │                                     │
│ │   - Photodiode power │   │                                     │
│ │   - Smoothing health │   │                                     │
│ └──────────────────────┘   │                                     │
│                            │                                     │
└────────────────────────────┴─────────────────────────────────────┘
```

### Implementation Approach

**Left Column Changes:**
- Group existing widgets into 3 collapsible QGroupBox sections
- Each section shows/hides based on workflow stage
- Progressive disclosure reduces cognitive load

**Right Column Changes:**
- Consolidate safety interlocks into one master group
- Move footpedal, photodiode, safety status together
- Clear visual hierarchy: Safety → Events → Config

### Pros
- Clear workflow progression (1 → 2 → 3)
- Reduced cognitive load (only see relevant controls)
- Natural operator training path
- Encourages proper thermal stabilization (TEC before laser)

### Cons
- Requires user to expand/collapse sections
- More complex layout implementation
- May hide controls user wants visible simultaneously
- Departures from hardware-based mental model

---

## OPTION B: Hardware-Based with Dependency Indicators

**Concept:** Keep current hardware grouping, add visual dependency indicators

### Visual Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ Hardware & Diagnostics Tab                                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────────┐          ┌─────────────┐                     │
│    │ IMAGING     │          │ GPIO        │ (1) CONNECT FIRST   │
│    │ SYSTEM      │          │ CONNECTION  │     ↓ ↓ ↓           │
│    │             │          │ (Arduino)   │     │ │ │           │
│    │ Camera      │          └─────────────┘     │ │ │           │
│    │ • Connect   │                              │ │ │           │
│    │ • Exposure  │          ┌──────────────────┴─┘ │           │
│    │ • Gain      │          │ AIMING LASER       │ │ (requires  │
│    └─────────────┘          │ • ON / OFF         │ │  GPIO)     │
│                             └────────────────────┘ │           │
│    ┌─────────────┐                                │           │
│    │ LASER       │          ┌────────────────────┴──┐         │
│    │ SYSTEMS     │ (2)      │ SMOOTHING MODULE     │         │
│    │             │          │ • Motor control      │ (requires│
│    │ TEC         │ ↓        │ • Vibration monitor  │  GPIO)   │
│    │ • Connect   │          └──────────────────────┘         │
│    │ • Setpoint  │                                           │
│    │ • Enable    │                                           │
│    │             │          ┌─────────────┐                  │
│    │ Treatment   │ (3)      │ PHOTODIODE  │                  │
│    │ • Connect   │          │ MONITOR     │ (monitors laser) │
│    │ • Current   │ ↓        │ • Voltage   │                  │
│    │ • ENABLE    │          │ • Power     │                  │
│    └─────────────┘          └─────────────┘                  │
│                                                               │
│    ┌─────────────┐          ┌─────────────┐                  │
│    │ MOTION      │          │ FOOTPEDAL   │                  │
│    │ CONTROL     │          │ DEADMAN     │                  │
│    │             │          │ SWITCH      │                  │
│    │ Actuator    │          │ • Status    │                  │
│    │ • Connect   │          │ • Safety    │                  │
│    │ • Home      │          └─────────────┘                  │
│    │ • Position  │                                           │
│    └─────────────┘                                           │
│                                                               │
└──────────────────────────────────────────────────────────────────┘

LEGEND:
(1), (2), (3) = Recommended initialization order
→ = Dependency arrow (requires X before Y)
```

### Implementation Approach

**Keep Current Layout:**
- No widget reorganization required
- Minimal code changes

**Add Visual Indicators:**
- Numbered badges (1, 2, 3) showing initialization order
- Arrows or lines showing dependencies
- Grayed-out controls when dependency not met
- Tooltip explanations ("Requires GPIO connection")

### Pros
- Minimal implementation effort
- Familiar hardware-based grouping preserved
- Visual cues guide operator without enforcing workflow
- User can still access all controls simultaneously

### Cons
- Doesn't solve cross-column navigation problem
- Laser system still fragmented (GPIO, aiming, smoothing separate)
- Visual clutter from arrows/indicators
- Doesn't reduce cognitive load

---

## OPTION C: Hybrid Approach (Persistent Safety + Collapsible Workflow)

**Concept:** Safety always visible at top, collapsible workflow sections below

### Visual Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ Hardware & Diagnostics Tab                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ SAFETY MONITORING (Always Visible)                         │  │
│ ├────────────────────────────────────────────────────────────┤  │
│ │ [E-Stop] │ Footpedal: PRESSED │ Photodiode: 2.3V/15mW │   │  │
│ │          │ Safety: SAFE        │ Smoothing: HEALTHY    │   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ > SYSTEM INITIALIZATION (Click to Expand/Collapse)         │  │
│ └────────────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │ 1. GPIO Connection (Arduino)                             │ │
│   │    Port: [COM4 ▼] [Refresh] [Connect] [Disconnect]      │ │
│   │    Status: Connected                                     │ │
│   │                                                          │ │
│   │ 2. TEC Temperature Control                               │ │
│   │    [Connect] [Disconnect]  Status: Connected             │ │
│   │    Current: 25.0°C  Setpoint: [25.0 ▼]°C [Set]         │ │
│   │    [ENABLE TEC] [DISABLE TEC]                            │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ > CALIBRATION & ALIGNMENT (Click to Expand/Collapse)      │  │
│ └────────────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │ 1. Camera (Allied Vision 1800 U-158c)                    │ │
│   │    [Connect] [Disconnect]  Live feed: Active             │ │
│   │    Exposure: [slider] 10.0ms  Auto                       │ │
│   │    Gain: [slider] 5.0dB  Auto                            │ │
│   │                                                          │ │
│   │ 2. Actuator (Xeryon Linear Stage)                        │ │
│   │    Port: [COM3 ▼] [Refresh] [Connect] [Disconnect]      │ │
│   │    [Find Home] [Query Settings]                          │ │
│   │    Position: 22.5mm / 45.0mm                             │ │
│   │                                                          │ │
│   │ 3. Aiming Laser (requires GPIO)                          │ │
│   │    [Aiming ON] [Aiming OFF]  Status: OFF                │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ > TREATMENT EXECUTION (Click to Expand/Collapse)           │  │
│ └────────────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │ 1. Treatment Laser (Arroyo 6300)                         │ │
│   │    [Connect] [Disconnect]  Status: Connected             │ │
│   │    Current: [slider] 1000mA (0-2000mA)                   │ │
│   │    [ENABLE OUTPUT] [DISABLE OUTPUT]  Output: OFF         │ │
│   │                                                          │ │
│   │ 2. Smoothing Motor (requires GPIO)                       │ │
│   │    Speed: [slider] 100 PWM (2.0V)  Range: 0-153         │ │
│   │    [Start Motor] [Stop Motor]  Motor: OFF                │ │
│   │    Vibration: 0.00g  Threshold: [0.10]g  Health: OK     │ │
│   │                                                          │ │
│   │ 3. Real-time Monitoring                                  │ │
│   │    Photodiode: 0.00V / 0.0mW                            │ │
│   │    Smoothing: X:0.00g Y:0.00g Z:1.00g                   │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ > DIAGNOSTICS & LOGS (Click to Expand/Collapse)            │  │
│ └────────────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │ Safety Event Log                                         │ │
│   │ [INFO] 2025-11-06 09:30:15 - System initialized         │ │
│   │ [WARN] 2025-11-06 09:32:01 - TEC temperature unstable   │ │
│   │ [Filter: All ▼] [Search...]                             │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Implementation Approach

**Persistent Top Bar:**
- Always-visible safety monitoring strip
- Condensed status displays (footpedal, photodiode, smoothing health)
- E-Stop button always accessible

**Collapsible Sections:**
- 4 QGroupBox sections with expand/collapse triangles
- Each section contains related widgets from current layout
- User can expand multiple sections simultaneously
- Sections remember expand/collapse state (user preferences)

### Pros
- Best of both worlds: safety always visible + workflow organization
- User control (can expand all sections if desired)
- Clear workflow progression via section ordering
- Persistent safety visibility (critical for medical device)

### Cons
- Most complex implementation (new persistent top bar + collapsible sections)
- Requires significant UI refactoring
- Vertical space consumed by section headers

---

## Decision Matrix

| Criteria | Option A (Workflow) | Option B (Indicators) | Option C (Hybrid) |
|----------|---------------------|----------------------|-------------------|
| **Implementation Effort** | Medium (4-6 hours) | Low (2-3 hours) | High (8-12 hours) |
| **Workflow Clarity** | ✅ Excellent | ⚠️ Good | ✅ Excellent |
| **Safety Visibility** | ⚠️ Good | ✅ Excellent | ✅✅ Outstanding |
| **User Control** | ⚠️ Limited (progressive disclosure) | ✅ Excellent (all visible) | ✅ Excellent (user choice) |
| **Dependency Clarity** | ✅ Excellent (enforced order) | ✅ Good (visual indicators) | ✅ Excellent (grouped + order) |
| **Learning Curve** | ⚠️ Moderate (new workflow) | ✅ Minimal (familiar layout) | ⚠️ Moderate (new sections) |
| **FDA Compliance** | ✅ Good (workflow validation) | ⚠️ Fair (no workflow guidance) | ✅✅ Excellent (safety + workflow) |
| **Maintainability** | ✅ Good (clear separation) | ✅ Excellent (minimal changes) | ⚠️ Fair (complex structure) |

---

## Recommendation

**Recommended: Option C (Hybrid Approach)**

**Rationale:**
1. **Safety-First Design:** Persistent safety monitoring aligns with medical device best practices
2. **User Flexibility:** Collapsible sections give operators control while suggesting optimal workflow
3. **FDA Compliance:** Clear workflow guidance + always-visible safety status supports regulatory documentation
4. **Long-term Value:** Initial implementation effort pays off in reduced training time and fewer operator errors

**Alternative if time-constrained: Option B (Hardware-Based with Indicators)**
- Fastest implementation (2-3 hours)
- Preserves familiar layout
- Visual indicators improve clarity without radical changes

---

## USER DECISION REQUIRED

Please select your preferred option:

**[ ] OPTION A: Task-Based Workflow Grouping**
- Workflow-focused
- Progressive disclosure
- Medium implementation effort

**[ ] OPTION B: Hardware-Based with Dependency Indicators**
- Minimal changes
- Keep current layout
- Low implementation effort

**[ ] OPTION C: Hybrid Approach (Persistent Safety + Collapsible Workflow)** ⭐ RECOMMENDED
- Best of both worlds
- Safety always visible
- High implementation effort

**Additional Questions:**

1. **Dependency Indicators:** Do you want visual arrows/labels showing hardware dependencies? (Yes/No)

2. **Progressive Disclosure:** Should sections start collapsed or expanded by default? (Collapsed/Expanded)

3. **Wizard Mode (Future):** Interest in wizard-style guided setup? (Yes/No/Later)

4. **Specific Workflow Concerns:** Any specific pain points in current layout we should address?

---

**Next Steps After Approval:**

1. Implement approved design (Phase 4B)
2. Apply design tokens (spacing, GroupBox styling)
3. Re-test all signal/slot connections
4. Visual regression testing (before/after screenshots)
5. Update documentation
6. Create commit

---

**End of Design Proposals**
