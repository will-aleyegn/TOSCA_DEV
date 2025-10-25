# 1. Software Development
## (FDA Pre-Submission Version)

**Purpose of This Document:** This document presents ALeyeGN's planned software architecture and development approach for the TOSCA system for FDA pre-submission feedback. Specific implementation details will be finalized during development based on FDA input, risk analysis results, and verification testing. We seek FDA feedback on the overall approach, safety architecture, and documentation strategy.

---

## 1.1 Purpose of a Separate Software Development Section

Software is a critical component of the TOSCA system. It is subject to IEC 62304 lifecycle requirements, which are recognized by the FDA and international regulators. This section ensures that software planning, development, verification & validation (V&V), and maintenance are documented, controlled, and integrated into ALeyeGN's Quality Management System (QMS).

The Design History File (DHF) deliverables related to software are documented in FDA guidance "Content of Premarket Submissions for Device Software Functions". This guidance defines two levels of documentation: Basic and Enhanced. The guidance states that "Enhanced Documentation should be provided for any premarket submission that includes device software function(s) where a failure or flaw of any device software function(s) could present a hazardous situation with a probable risk of death or serious injury, either to a patient, user of the device, or others in the environment of use".

## 1.2 Documentation Level Evaluation

Based on preliminary hazard analysis, a failure in the TOSCA control software could expose the patient eye to excessive laser irradiance, presenting potential for serious injury. This determination is sufficient to prescribe an Enhanced Documentation Level.

As an independent reasonableness check, we reviewed publicly available information about recently cleared selective laser trabeculoplasty (SLT) devices. Three SLT devices cleared by the FDA in 2022-2023 stated Major Level of Concern in their 510(k) Summary Letters:
• Belkin Eagle, K230722
• Ellex Tango, K222395
• Lumenis Selecta, K220877

Major Level of Concern (legacy terminology) is analogous to Enhanced Documentation Level requirement. This comparison supports our determination that TOSCA requires Enhanced Documentation.

**FDA Question:** Does the FDA agree with our assessment that Enhanced Documentation Level is appropriate for TOSCA software?

The sections below follow the Recommended Documentation table in FDA guidance "Content of Premarket Submissions for Device Software Functions" for Enhanced Documentation Level.

---

## 1.3 Software Description - Planned Architecture

The TOSCA software will implement a layered architecture that separates user interface, treatment control, device management, and safety functions. Software development will follow IEC 62304 and will incorporate both commercial off-the-shelf (OTS) components and in-house developed software (IDS) as appropriate for device functionality.

The planned software architecture is depicted in Figure 1 below. Each block represents a functional software module. **Note:** This architecture is conceptual and subject to refinement during detailed design based on FDA feedback, risk analysis findings, and development considerations.

### Figure 1: TOSCA Planned Software Architecture (Conceptual)

```
[See software_block_diagram.mmd for detailed visual diagram]

Simplified view:

┌────────────────────────────────────────────────────────────┐
│              User Interface Layer                          │
│  • Treatment control  • Video display  • Patient mgmt      │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│           Application Logic Layer                          │
│  • Session Control  • Protocol Management                  │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│        ╔═══════════════════════════════╗                   │
│        ║   Safety Management Module    ║                   │
│        ║   (Central Safety Authority)  ║                   │
│        ╚════════════════┬══════════════╝                   │
│                         │                                   │
│    ┌────────────────────┼────────────────────┐            │
│    │                    │                    │            │
│    ▼                    ▼                    ▼            │
│ ┌────────┐      ┌─────────────┐      ┌──────────┐        │
│ │ Laser  │      │   Camera &  │      │   GPIO   │        │
│ │Control │      │   Image     │      │ Hardware │        │
│ │        │      │ Processing  │      │Interlocks│        │
│ └────────┘      └─────────────┘      └──────────┘        │
│                                                             │
│           Device Control Layer                             │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│         Data Management & Logging                          │
└─────────────────────────────────────────────────────────────┘
```

**Key Architectural Principles:**
1. **Safety First:** Safety Management module has authority to override all other functions
2. **Modularity:** Clear separation of concerns for testability and maintainability
3. **Layered Design:** UI, logic, device control, and data layers with defined interfaces
4. **Fail-Safe:** Any fault or uncertainty results in safe state (laser disabled)
5. **Audit Trail:** Comprehensive logging for regulatory compliance and incident investigation

The modules shown in Figure 1 are described below. **Note:** Module descriptions represent planned functionality; specific implementation details will be refined during development.

### 1.3.1 GUI (User Interface)

The GUI module will manage user interactions and information display through a tabbed or multi-panel interface. Planned functions include real-time camera video display, patient information management, treatment session controls, system status indicators, and alert notifications.

Safety-critical information (interlock status, emergency stop, fault conditions) will be designed with high visual prominence per human factors engineering principles. The specific UI design will be informed by human factors studies and user feedback during development.

**Anticipated Implementation:** OTS GUI framework (candidates include PyQt6, Tkinter, or similar) with IDS for medical device-specific workflows and safety displays.

### 1.3.2 Operator Input Devices

This module will manage non-safety-critical operator inputs including joysticks, keyboards, and mouse controls. These devices support clinical workflow but are not safety-critical.

**Important Distinction:** Safety-critical operator inputs (such as footpedal if implemented as deadman switch, or emergency stop button) will be handled directly by the Safety Management module through dedicated hardware interfaces. This maintains clear architectural separation between operational and safety-critical functions.

**Anticipated Implementation:** OTS device drivers with IDS for command validation and workflow integration.

### 1.3.3 Camera & Image Processing

This module will manage the camera system and perform image analysis to support alignment, monitoring, and documentation functions.

**Planned Functions:**
• Live video feed acquisition and display
• Laser ring or spot detection to assist with alignment
• Image quality assessment (focus, exposure, etc.)
• Treatment video recording for documentation
• Real-time visual monitoring during treatment

**Safety Integration:** The camera system is being considered as part of the safety architecture. One approach under evaluation is to require valid camera feed as a prerequisite for laser operation, ensuring that visual monitoring capability is present throughout treatment. The specific role of camera monitoring in the safety system will be determined based on risk analysis and FDA feedback.

**Image Processing Algorithms:** We plan to use established computer vision techniques (e.g., edge detection, circle/shape finding) to detect laser patterns in the image. Specific algorithms will be selected and validated during development.

**Anticipated Implementation:** OTS camera SDK (Allied Vision VmbPy or similar) and image processing library (OpenCV or similar) with IDS for medical-specific algorithms and treatment documentation features.

**FDA Question:** Does FDA have feedback on the appropriate role of camera/visual monitoring in the safety architecture? Should loss of camera feed trigger treatment interruption?

### 1.3.4 Data Management (Patient & Session Data)

This module will manage patient records, treatment session data, and associated files including video recordings. The system will provide database operations for patient information and treatment histories while maintaining data integrity.

**Planned Database Architecture:**
• Patient records (anonymized with coded identifiers - no PHI stored on device)
• Treatment sessions (protocol, parameters, outcomes)
• Treatment events (detailed log of all actions)
• Safety events (dedicated logging for safety-related occurrences)
• Protocols (saved treatment templates)
• Operator/technician records (for authentication and audit trail)
• Calibration data

**Audit Trail:** The database will implement comprehensive event logging with immutability for safety-critical logs. All treatment actions, parameter changes, and safety events will be logged with timestamps and operator identification.

**High-Frequency Data Handling:** For high-rate data (if sampling occurs faster than database can efficiently handle), we are considering a buffered approach where data is initially captured to files and then imported to database post-session. This maintains control loop performance while ensuring complete documentation.

**Anticipated Implementation:** SQLite database (local storage, single-user) with IDS for medical data model, audit trail requirements, and regulatory compliance features.

### 1.3.5 Actuator & Peripheral Control

This module will provide control interfaces for motorized components used in treatment delivery, including the linear actuator that adjusts optical characteristics affecting laser beam size/shape.

**Planned Functions:**
• Motorized component control (position commands, motion execution)
• Position feedback monitoring
• Calibration management (mapping between position and optical parameters)
• Coordination with treatment protocols

The relationship between actuator position and resulting optical characteristics (e.g., ring diameter) will be established through calibration procedures and stored in the database.

**Anticipated Implementation:** OTS device-specific libraries (Xeryon API or similar) with IDS for treatment-specific functions, calibration implementation, and safety validation.

### 1.3.6 Laser Control & Thermal Management

This module will interface with the laser controller (Arroyo Instruments TEC Controller) via serial communication to manage laser power, emission control, and thermal regulation.

**Planned Functions:**
• Laser power level commands
• Laser emission enable/disable
• Temperature control and monitoring
• Laser system status monitoring

**Safety Integration:** This module will operate under governance of the Safety Management module. Laser commands will be validated against safety conditions before execution. The specific validation sequence and interlocking mechanism will be defined during detailed safety design.

All laser control commands will be logged for regulatory audit trail and incident investigation.

**Anticipated Implementation:** OTS serial communication libraries with IDS for Arroyo-specific protocol, safety integration, and command validation framework.

### 1.3.7 Session Control (Treatment Management)

This module will orchestrate treatment sessions from initiation through completion, managing protocol execution, timing, and coordination between system components.

**Planned Session Workflow:**
1. Session initialization (operator authentication, patient selection)
2. Treatment setup (protocol selection, parameter validation)
3. Treatment execution (protocol step sequencing, progress tracking)
4. Session completion (data finalization, notes, archival)

**Protocol Management:** The system will support pre-defined treatment protocols and may allow customization. Protocols will define power levels, durations, and optical parameters. All protocol parameters will be validated against safety limits before use.

**Operator Adjustments:** The design will consider allowing real-time treatment adjustments (e.g., power changes, pause/resume) with appropriate logging as protocol deviations for regulatory documentation.

**Anticipated Implementation:** IDS designed for medical treatment workflows, protocol execution logic, and coordination with hardware control modules.

### 1.3.8 Monitoring and Alerting (System Surveillance)

This module will provide operator-facing status information and guidance. Functions include system status display, treatment progress indicators, maintenance reminders, and operator guidance messages.

**Scope:** This module focuses on operational monitoring and workflow support. Safety-critical parameter monitoring (described in Section 1.3.9) is architecturally separate to ensure that safety functions are independent from user interface elements.

**Alert Presentation:** Alerts will be classified by severity (informational, warning, critical, safety) with appropriate visual presentation. Safety-related alerts will be prioritized for immediate operator awareness.

**Anticipated Implementation:** IDS with GUI framework integration for status display and alert presentation.

### 1.3.9 Safety Management (Safety Systems) - Planned Approach

The Safety Management module is the highest-priority software component and will implement comprehensive safety monitoring and intervention capabilities. This module will have override authority over all treatment functions.

**FDA Note:** This section describes our planned safety architecture. We seek FDA feedback on this approach, particularly regarding interlock requirements, monitoring strategies, and fault response expectations.

---

**SAFETY ARCHITECTURE PHILOSOPHY**

The planned safety architecture is based on these principles:
• **Multiple independent interlocks** - Both hardware-based and software-based safety checks
• **Positive permission required** - Laser operation requires active confirmation of safe conditions (not merely absence of faults)
• **Continuous monitoring** - Safety parameters monitored continuously during operation
• **Immediate fault response** - Rapid transition to safe state upon fault detection
• **Fail-safe design** - System defaults to safe state (laser off) on any uncertainty or component failure
• **Complete audit trail** - All safety events immutably logged

---

**HARDWARE SAFETY INTERLOCKS - PLANNED APPROACH**

We plan to implement hardware-based safety interlocks using GPIO (General Purpose Input/Output) interfaces to monitor physical conditions and device states. Current design concepts include:

**1. Footpedal or Operator Control Input**

We are considering implementing a footpedal or similar operator-controlled input as a "deadman switch" or enabling control. Under this concept:
• Laser operation would require continuous active control by the operator
• Release of control would immediately disable laser
• Physical switch state would be monitored via hardware interface

*Design considerations:*
- Monitoring approach (polling rate, timeout detection)
- Debouncing strategy to prevent false triggers
- Fail-safe hardware design (pull-down resistors, default-off state)

**FDA Question:** Is a footpedal-type deadman switch appropriate for this device class? Are there alternative operator control approaches FDA has seen in similar devices that we should consider?

**2. Beam Conditioning Device Monitoring**

The TOSCA optical system includes a beam conditioning/homogenization element (hotspot smoothing device). We are evaluating whether to implement monitoring of this device's operational status as a safety interlock.

*Approach under consideration:*
• Device could output a "healthy" signal (digital or analog)
• Loss of signal could indicate device failure or disconnection
• System would require valid device signal before permitting laser operation

*Design considerations:*
- Signal type (digital presence, analog voltage level, etc.)
- Monitoring frequency and fault detection timing
- Validation of signal integrity

**FDA Question:** What is FDA's expectation regarding monitoring of beam conditioning elements? Is real-time monitoring of homogenization device status appropriate for an interlock, or is pre-treatment verification sufficient?

**3. Output Power Monitoring**

We plan to implement real-time laser output power monitoring using a photodiode sensor in the optical path. This would provide closed-loop verification that delivered power matches commanded power.

*Planned approach:*
• Photodiode voltage sampled via analog-to-digital converter (ADC)
• Voltage converted to power using calibration curve
• Measured power compared to commanded power
• Deviation beyond threshold(s) would trigger alerts or shutdowns

*Design considerations:*
- Graduated thresholds (e.g., warning threshold for minor deviations, fault threshold for major deviations)
- Sampling rate and response time
- Calibration requirements and validation
- False alarm prevention while maintaining safety

**FDA Question:** What level of power deviation should trigger automatic shutdown vs. operator warning? Are there established standards or FDA expectations for photodiode monitoring in medical lasers?

---

**SOFTWARE SAFETY INTERLOCKS - PLANNED APPROACH**

In addition to hardware interlocks, we plan software-based safety validations:

**4. Emergency Stop Function**

User-initiated immediate shutdown capability via UI button and/or keyboard shortcut. This provides operator override for any situation requiring immediate laser cessation.

*Design considerations:*
- Immediate execution (highest priority)
- Reset/recovery requirements (supervisor authentication?)
- Logging and documentation

**5. Power Limit Enforcement**

Software validation that commanded power does not exceed:
• Absolute hardware limits
• Protocol-specific limits
• Session or patient-specific limits (if applicable)
• Ramp rate limits (rate of power change)

Multiple limit layers provide defense-in-depth protection against inadvertent over-power conditions.

**6. Session State Validation**

Laser operation only permitted during active, documented treatment session with:
• Patient association
• Operator authentication
• Proper session state

This ensures complete traceability and prevents laser use outside documented context.

**7. Visual Monitoring Validation**

Under consideration: Requiring valid camera feed as prerequisite for laser operation to ensure visual monitoring capability throughout treatment.

*Design question:* Should camera feed loss during treatment trigger immediate shutdown, or should operator be alerted with option to continue based on clinical judgment?

---

**SAFETY STATE MANAGEMENT**

We plan to implement a formal safety state machine governing system operational modes. Conceptual states might include:
• System Off / Initializing
• Ready (standby)
• Armed (ready to treat, awaiting operator control)
• Treating (laser emission authorized)
• Paused (temporary suspension)
• Fault (safety issue detected, requires resolution)

State transitions would be strictly controlled, with safety checks governing entry into treatment states. Any safety interlock failure would trigger transition to fault state.

The specific states, transitions, and validation requirements will be defined during detailed safety design based on risk analysis and FDA guidance.

**FDA Question:** Are there specific state machine architectures or safety state requirements FDA has seen that work well for medical laser systems?

---

**FAULT HANDLING - PLANNED APPROACH**

When a safety condition is violated, the system will:
1. Execute immediate protective action (laser disable)
2. Classify fault severity and source
3. Log fault details immutably
4. Present operator notification with fault information
5. Provide guidance for fault resolution
6. Require appropriate clearance before resuming operation

The specific fault response sequences, timing requirements, and recovery procedures will be defined during detailed design informed by FMEA (Failure Mode and Effects Analysis) and risk controls from the Risk Management File.

---

**WATCHDOG / SYSTEM MONITORING**

We are considering implementing a watchdog timer or similar mechanism to detect software failures (hangs, deadlocks, infinite loops) that could prevent safety monitoring from executing. This would provide an independent check that the safety monitoring loop continues running.

Implementation details (timeout values, recovery actions, reset requirements) will be determined during detailed design.

---

**SAFETY EVENT LOGGING**

All safety-related events will be logged with comprehensive information:
• Timestamps
• Event type and severity
• System state at time of event
• All interlock states
• Actions taken
• Session and operator context

Safety logs will be immutable (no updates or deletes) and maintained indefinitely for regulatory compliance, incident investigation, and system reliability analysis.

---

**IMPLEMENTATION APPROACH**

Safety Management will be implemented as In-house Developed Software (IDS) due to its criticality and device-specific requirements. OTS components (GPIO interface libraries, ADC interfaces) will be used for hardware connectivity, but safety logic, validation, and state management will be custom-developed and thoroughly verified.

---

**VERIFICATION & VALIDATION - PLANNED APPROACH**

Safety Management will receive the most rigorous V&V:
• Unit testing of all interlock functions (pass and fail scenarios)
• Integration testing of interlock coordination
• Timing verification (response time measurements)
• Failure mode testing (FMEA-driven scenarios)
• State machine transition validation
• Logging integrity verification

All V&V results will be documented in Software Verification & Validation Plan and traceable to requirements and risk controls.

---

**FDA FEEDBACK REQUESTED**

We request FDA feedback on our planned safety architecture approach:
1. Is the overall multi-layered interlock strategy appropriate?
2. Are there specific safety monitoring requirements or expectations we should incorporate?
3. What level of redundancy is expected for safety functions?
4. What documentation should we plan to provide regarding safety-critical algorithms and timing?
5. Are there reference devices or 510(k) submissions we should review for safety architecture guidance?

---

### 1.3.10 Logging and Reporting (Data Recording)

This module will record system operations, device performance data, and treatment parameters for regulatory compliance, troubleshooting, and quality assurance.

**Planned Logging Architecture:**

We are considering a two-tier approach:
• **High-frequency data** (if needed) buffered to files during treatment to avoid database I/O latency affecting real-time control
• **Event-based data** written immediately to database for real-time access
• **Post-session processing** to import buffered data for long-term storage and analysis

Safety-critical events will be logged immediately to ensure preservation even if session is interrupted.

**Report Generation:** The system will generate reports for clinical review and service activities (session summaries, safety event reports, device performance trends).

**Anticipated Implementation:** IDS for logging framework, database integration, and report generation.

### 1.3.11 Error Handling (Fault Management)

This module will provide centralized error detection, classification, and recovery for non-safety-critical errors. Safety-critical faults will be handled by Safety Management (1.3.9).

**Error Classification:** Errors will be categorized by severity (critical, major, minor, informational) with appropriate responses ranging from immediate escalation to Safety Management (for safety-critical errors) to logging and notification (for minor issues).

**Graceful Degradation:** Where safe, the system will attempt to maintain operation in degraded mode (e.g., continue treatment if video recording fails, but notify operator).

**Anticipated Implementation:** IDS with exception handling, error classification logic, and coordination with Safety Management.

---

## 1.4 Risk Management File

The Risk Management File (RMF) follows ISO 14971 and addresses risks in the complete TOSCA system, including software risks. Software-related risks will be identified through hazard analysis and FMEA, including:
• Laser control errors (excessive power, incorrect duration, unintended emission)
• Interlock failures or bypasses
• User interface errors (incorrect information display)
• Data integrity issues
• Cybersecurity risks

Risk controls implemented in software will be traceable from RMF to Software Requirements Specification to verification test cases.

**Status:** Risk Management File is in development. Preliminary software hazards have been identified; formal FMEA and risk analysis will be completed during development.

**Reference:** Risk Management File [Document Number TBD]

## 1.5 Software Requirements Specification (Planned)

The Software Requirements Specification (SRS) will describe software needs and expectations at the software level, with traceability to product requirements, risk controls, and design.

The SRS will include:
• Functional requirements (what the software shall do)
• Performance requirements (timing, throughput, response)
• Interface requirements (hardware, software, user interfaces)
• Safety requirements (interlock monitoring, fault response)
• Security requirements (access control, audit trail)
• Reliability requirements

Requirements will be uniquely identified and traced to sources (product requirements, risk controls, regulatory requirements) and to verification methods.

**Status:** SRS will be developed after FDA pre-submission feedback is incorporated into architecture and preliminary risk analysis is complete.

**Reference:** Software Requirements Specification [Document Number TBD - to be developed]

## 1.6 Software Architecture Design

The planned software architecture is documented in Section 1.3 above. Figure 1 provides the system-level block diagram showing major modules and their relationships.

Detailed architecture documentation including class diagrams, sequence diagrams, and state machine diagrams will be provided in the Software Design Specification (Section 1.7).

**Note:** The architecture presented in this pre-submission is conceptual. We anticipate refinements based on:
• FDA feedback from this pre-submission meeting
• Risk analysis findings
• Detailed design activities
• Verification testing results
• OTS component evaluation

We do not consider this architecture "locked in" but rather a starting point for discussion and refinement.

## 1.7 Software Design Specification (Planned)

The Software Design Specification (SDS) will present detailed technical design showing how software implements requirements.

The SDS will include:
• Detailed design for each module
• Class diagrams and object-oriented structure
• Sequence diagrams for key use cases
• State machine diagrams (safety states, session states)
• Data flow diagrams
• Interface specifications (APIs, hardware protocols, database schema)
• Algorithm descriptions with rationale
• Error handling designs

Safety-critical designs will receive enhanced documentation with additional detail on:
• Interlock monitoring implementation
• Fault detection and response sequences
• State machine logic and validation
• Timing analysis and worst-case scenarios
• Verification approach for safety functions

**Status:** SDS will be developed after SRS is complete and FDA pre-submission feedback is incorporated.

**Reference:** Software Design Specification [Document Number TBD - to be developed]

## 1.8 Software Development, Configuration Management, and Maintenance Practices

ALeyeGN's software development process will follow IEC 62304 and align with 21 CFR § 820.30 (FDA Design Controls).

### Planned Development Lifecycle

**1. Requirements Development**
• Develop SRS based on product requirements, risk controls, standards, and regulatory requirements
• Requirements review and approval
• Establish requirements baseline under configuration control

**2. Design**
• Develop SDS based on SRS
• Architecture and detailed design
• Design reviews for completeness and traceability
• Establish design baseline

**3. Implementation**
• Coding per design specifications and coding standards
• Peer code reviews
• Unit testing
• Static analysis

**4. Integration**
• Module integration per integration plan
• Integration testing
• Interface validation

**5. Verification (System Testing)**
• Execute verification tests per V&V Plan
• Functional, performance, safety, usability, robustness testing
• Document test results
• Requirements traceability verification

**6. Validation**
• System-level validation in representative environment
• Clinical workflow simulation with representative users
• Demonstrate device meets intended use

**7. Release**
• Release documentation package including scope, contents, verification summary, risk assessment, approvals
• Version control and configuration identification
• Deployment procedures

**8. Maintenance**
• Anomaly tracking and resolution
• Patches and updates
• Obsolescence management

### Configuration Management (Planned)

**Source Code Management:**
• Version control system (Git or similar)
• Branch strategy (main/develop/feature branches)
• Code review requirements
• Release tagging

**Artifact Management:**
• Secure storage of built software
• Release archival with documentation
• Traceability to source code baseline

**Document Control:**
• All controlled documents versioned and tracked
• Change control process with impact assessment and approval
• Configuration audits before releases

**Traceability:**
• Requirements traceability matrix
• Forward traceability (requirements → design → tests)
• Backward traceability (design elements → requirements)
• Risk control traceability

### Quality Management System Integration

Software development activities will be integrated into ALeyeGN's QMS:
• Development follows QMS procedures
• Design reviews at defined milestones
• Records maintained in Design History File (DHF)
• Change control for all modifications
• Software release records in Device Master Record (DMR)

### Development Tools (Anticipated)

**Programming:** Python 3.10+ (subject to evaluation)
**IDE:** Visual Studio Code or PyCharm
**Version Control:** Git
**Testing:** pytest or similar framework
**Documentation:** Sphinx or similar for API documentation
**Build/Deployment:** Automated build and installer creation

**Note:** Final tool selections will be made during development based on compatibility with OTS components, team expertise, and regulatory documentation needs.

---

## FDA PRE-SUBMISSION QUESTIONS - SOFTWARE

We request FDA feedback on the following:

### Architecture and Safety
1. Does the proposed layered architecture with centralized Safety Management meet FDA expectations for Enhanced Documentation Level?
2. Is the planned combination of hardware and software interlocks appropriate for this device risk profile?
3. Are there specific safety monitoring approaches or standards FDA recommends we review?
4. Should camera monitoring be considered a safety-critical interlock, or is it acceptable as an operational aid?

### Documentation
5. What level of detail does FDA expect in the Software Design Specification for safety-critical modules?
6. Are there specific diagrams or documentation formats FDA finds particularly useful for understanding safety architecture?
7. Should we plan to provide algorithm pseudocode or source code for safety-critical functions in our submission?

### OTS Software
8. What is FDA's expectation regarding validation of OTS components (GUI frameworks, image processing libraries, etc.)?
9. Should we plan to provide detailed OTS Software documentation (Level of Concern assessment, validation records) for commonly used libraries like Python standard library, or is summary-level documentation acceptable?

### Testing and Verification
10. What types of safety testing does FDA expect to see documented (fault injection, timing analysis, FMEA-driven scenarios, etc.)?
11. Are there specific test coverage metrics or analysis approaches FDA recommends for safety-critical software?

### Risk Management Integration
12. How should software risk controls be documented - in the Risk Management File, in the SRS, or both with cross-references?
13. Are there software-specific risks FDA commonly sees that we should ensure we address?

### Reference Devices
14. Are there specific cleared devices (510(k)s) with software documentation that FDA considers exemplary that we should review for guidance?
15. Are there any recent changes to FDA software guidance or expectations that we should incorporate beyond the 2023 "Content of Premarket Submissions for Device Software Functions" guidance?

---

## Summary and Path Forward

This Software Development section presents ALeyeGN's planned approach to TOSCA software development, emphasizing:
• Enhanced Documentation Level based on device risk profile
• Layered architecture with safety as highest priority
• Multiple hardware and software safety interlocks
• Fail-safe design principles
• Comprehensive audit trail for regulatory compliance
• IEC 62304 compliant development process

**Important Note:** The architecture and approaches described in this document are conceptual and represent our current planning. We recognize that:
• Specific implementation details will be refined during development
• FDA feedback may require architectural adjustments
• Risk analysis may identify additional safety requirements
• Verification testing may reveal needed design changes

We do not consider ourselves locked into specific implementations described here, but rather seek FDA feedback on our overall approach, safety strategy, and documentation plans to ensure we are on the right path before committing to detailed design and implementation.

We appreciate FDA's review and feedback on this software development approach.

---

**Document Control:**
• **Document Title:** TOSCA Product Development Plan - Section 1: Software Development (Pre-Submission Version)
• **Document Number:** [TBD]
• **Version:** 1.0 Pre-Sub
• **Date:** 2025-10-15
• **Prepared by:** Will [Last Name], Systems Architect
• **Reviewed by:** [Regulatory Affairs, Quality Assurance - TBD]
• **Approved by:** [Engineering Manager, Quality Manager - TBD]
• **Purpose:** FDA Pre-Submission Meeting - Seeking Feedback

---

**End of Software Development Section - FDA Pre-Submission Version**
