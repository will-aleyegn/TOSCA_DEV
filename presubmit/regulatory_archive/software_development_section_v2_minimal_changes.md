# 1 Software Development

## 1.1 Purpose of a Separate Software Development Section

Software is a critical component of the TOSCA system. It is subject to IEC 62304 lifecycle requirements, which are recognized by the FDA and international regulators. This section ensures that software planning, development, V&V, and maintenance are documented, controlled, and integrated into ALeyeGN's QMS.

The DHF deliverables that are related to SW are documented in an FDA guidance document titled "Content of Premarket Submissions for Device Software Functions ". This guidance defines two levels of documentation: Basic and Enhanced. The guidance states that "Enhanced Documentation should be provided for any premarket submission that includes device software function(s) where a failure or flaw of any device software function(s) could present a hazardous situation with a probable risk of death or serious injury, either to a patient, user of the device, or others in the environment of use".

For background: the terms "Enhanced Documentation" and "Major Level of Concern" were introduced in a 2023 update of the FDA guidance document titled "Content of Premarket Submissions for Device Software Functions". Prior to that update the FDA used three Levels of Concern (Minor, Moderate, Major) for device SW. In the 2023 update these three levels of concern were replaced with two Documentation Levels (Basic, Enhanced).

## 1.2 Documentation Level Evaluation

While the Risk Analysis activities are not yet completed, we can say that a failure in the TOSCA control SW may expose the patient eye to excessive laser irradiance thus presenting potential for serious injury. This single item is sufficient to prescribe an Enhanced Documentation Level.

As an independent reasonableness check, we compare the conclusion driving Enhanced Documentation to publicly available information about several recently cleared devices. We note that three SLT devices cleared by the FDA in 2022 and 2023 stated in their 510(k) Summary Letters that their Level of Concern is Major. The three devices are:
    • Belkin Eagle, K230722
    • Ellex Tango, K222395
    • Lumenis Selecta: K220877

From the Risk Analysis perspective, Major Level of Concern is prescribed when a failure may result in serious injury or death. These are the same conditions that prescribe Enhanced Documentation Level.

This information supports that "Enhanced Documentation" requirement for TOSCA.

The sections below follow the Recommended Documentation table in "Content of Premarket Submissions for Device Software Functions" for Enhanced Documentation Level.

## 1.3 Software Description

The TOSCA software implements a layered architecture that separates user interface, treatment control, device management, and safety functions. The software will be developed and validated according to appropriate medical device software standards and will incorporate both commercial off-the-shelf components and custom developed modules as needed for device functionality. The software block diagram is depicted in Figure 1 below. Each block represents a functional SW module, and the main communications between the various blocks are also shown.

### Figure 1: TOSCA Software Block Diagram

```
[Visual Mermaid diagram available in: docs/architecture/software_block_diagram.mmd]

Simplified representation:

┌────────────────────────────────────────────────────────────────┐
│                  GUI (User Interface)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Treatment │ │  Live    │ │ Patient  │ │ Safety   │         │
│  │ Control  │ │  Video   │ │  Mgmt    │ │ Status   │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└───────┬──────────────────────────────────────────────┬────────┘
        │                                              │
        ↓                                              ↓
┌───────────────────┐                        ┌──────────────────┐
│ Operator Input    │                        │  Monitoring &    │
│    Devices        │                        │    Alerting      │
└─────────┬─────────┘                        └─────────┬────────┘
          │                                            │
          ↓                                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Session Control                            │
│              (Treatment Management)                          │
└────┬────────────────────────────────────────────────┬────────┘
     │                                                 │
     ↓                                                 ↓
┌────────────────┐                            ┌───────────────┐
│      Data      │◄──────────────────────────►│   Logging &   │
│  Management    │                            │   Reporting   │
└────────┬───────┘                            └───────┬───────┘
         │                                            │
         │      ┌─────────────────────────┐          │
         └─────►│  Laser Control & TEC    │◄─────────┘
                └────────────┬────────────┘
                             │
       ┌─────────────────────┼────────────────────┐
       │                     │                    │
       ↓                     ↓                    ↓
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  Actuator &  │   │    Camera &      │   │   GPIO Safety    │
│ Peripheral   │   │     Image        │   │   Interlocks     │
│   Control    │   │   Processing     │   │  • Footpedal     │
└──────┬───────┘   │ • Ring detect    │   │  • Smoothing Dev │
       │           │ • Focus measure  │   │  • Photodiode    │
       │           │ • Recording      │   └─────────┬────────┘
       │           └─────────┬────────┘             │
       └─────────────────────┼──────────────────────┘
                             │
                             ↓
                   ┌──────────────────┐
                   │      Safety      │◄────── HIGHEST PRIORITY
                   │   Management     │        OVERRIDE AUTHORITY
                   └─────────┬────────┘
                             │
                             ↓
                   ┌──────────────────┐
                   │  Error Handling  │
                   └──────────────────┘
```

The modules shown in Figure 1 are explained below.

### 1.3.1 GUI (User Interface)

The GUI module manages all user interactions and display functions through a tabbed interface. This includes real-time display of camera streams, patient information management, treatment session controls, system status indicators, and alert notifications. The module provides operator controls for treatment parameters and displays system feedback to ensure proper operation.

Implementation: Combines OTS GUI frameworks with IDS for device-specific functionality.

### 1.3.2 Operator Input Devices

This module manages external input devices used by clinical and service personnel including joysticks, keyboards, and mouse controls. The module processes input events and translates them into appropriate system commands.

**Note on Safety-Critical Inputs:** Safety-critical operator inputs such as the footpedal (if used as a deadman switch) and emergency stop button are handled directly by the Safety Management module (Section 1.3.9) through dedicated hardware interfaces, not through this Operator Input Devices module. This architectural separation ensures that safety-critical inputs are independent from general operator interface functions.

Implementation: Utilizes OTS device drivers.

### 1.3.3 Camera & Image Processing

This module manages the Allied Vision camera system via VmbPy SDK and performs real-time image analysis. Functions include:
• Live video feed display and recording
• Laser ring detection (circle finding algorithm) for alignment verification
• Focus quality measurement for optical readiness assessment
• Treatment session video capture for documentation

The camera system provides essential visual monitoring during treatment setup and delivery. Ring detection algorithms assist operators with alignment, and focus measurement provides objective assessment of optical system readiness. All treatment sessions are recorded for regulatory documentation and quality review.

**Safety Integration:** The camera feed validity is monitored by the Safety Management module. A valid image stream (frame age <1 second) is required as a prerequisite for laser operation, ensuring visual monitoring capability is maintained throughout treatment.

Implementation: Combines OTS camera SDK (VmbPy) with IDS for medical image processing algorithms and treatment documentation.

### 1.3.4 Data Management (Patient & Session Data)

This module manages comprehensive patient records, treatment session data, and associated media files. Provides database operations for creating, retrieving, updating patient information and treatment histories. Handles data import/export functions and maintains data integrity throughout the treatment workflow.

**Database Architecture:** Uses SQLite for local storage with tables for patients (anonymized with coded IDs), sessions, treatment events, safety events, protocols, technicians, and calibrations.

**Audit Trail:** The database implements comprehensive event logging with immutability for safety-critical records. Critical safety events are logged to a dedicated safety_log table separate from operational logs. High-frequency treatment data (sampled at 10-100 Hz) is initially buffered to JSON files during active treatment to avoid impacting the real-time control loop (10ms cycle time), then imported to the database post-session for long-term storage and analysis.

**Patient Privacy:** All patient data is anonymized using coded patient identifiers (e.g., P-2025-0001) with no PHI stored in the device database.

Implementation: SQLite database with IDS for medical data handling and regulatory compliance.

### 1.3.5 Actuator & Peripheral Control

This module provides unified control interface for motorized components and auxiliary equipment used in treatment delivery.

**Primary Functions:**
• Linear actuator control (Xeryon API) for laser ring size adjustment (2-5mm diameter range)
• Position command execution with smooth motion profiles
• Actuator position feedback monitoring
• Calibration management for position-to-ring-size mapping
• Auxiliary equipment coordination

The linear actuator adjusts optical path length to modify the laser ring diameter at the treatment plane. Ring size is a treatment protocol parameter that affects energy distribution. The module receives ring size commands from Session Control and executes calibrated position moves.

**Ring Size Calibration:** The relationship between actuator position (micrometers) and laser ring diameter (millimeters) is established through calibration where the actuator is moved to multiple positions and the camera measures actual ring diameter. A calibration curve is computed and stored in the database.

Implementation: Combines OTS device drivers (Xeryon library for linear stage control) with IDS for treatment-specific functions including calibration curve implementation, position validation, and coordination with treatment protocols.

### 1.3.6 Laser Control & Thermal Management

This module controls laser power output, beam parameters, and thermal management systems via the Arroyo Instruments TEC Controller using RS-232 serial communication. Receives treatment parameters from Session Control and safety inputs from the Safety Management module. Manages laser temperature regulation and power stability for consistent treatment delivery.

**Key Functions:**
• Laser power level commands (0-10W range)
• Laser emission enable/disable control
• TEC temperature setpoint and monitoring
• Laser diode temperature monitoring and regulation
• Power stability maintenance
• Laser system status and fault monitoring

**Safety Architecture:** All laser control commands are validated by the Safety Management module before execution. Commands are only executed when all safety interlocks are satisfied (footpedal depressed, smoothing device healthy, photodiode reading valid, session active, camera feed present). The module responds to safety shutdown commands with highest priority (<100ms target).

Implementation: Combines OTS serial communication libraries (pyserial) with IDS for Arroyo-specific protocol implementation, medical device safety integration, and command validation framework.

### 1.3.7 Session Control (Treatment Management)

This module orchestrates complete treatment sessions from initiation through completion. Manages treatment protocols, parameter validation, session timing, and coordinates between all system components. Maintains current session status including treatment phase, progress tracking, and system operational readiness to ensure proper sequence of operations.

**Session Workflow:**
1. Session initialization (technician authentication, patient selection)
2. Pre-treatment setup (protocol selection, parameter validation)
3. Treatment execution (protocol step sequencing, real-time control, progress monitoring)
4. Session completion (data finalization, video file association, session notes)

**Protocol Management:** Loads treatment protocols from database and validates parameters against safety limits. Protocols define treatment steps with power levels (constant or ramping), durations, and ring sizes. Supports real-time operator adjustments with appropriate logging as protocol deviations.

Implementation: IDS designed for medical treatment workflows.

### 1.3.8 Monitoring and Alerting (System Surveillance)

This module continuously monitors system performance, device status, and operational parameters. Generates alerts for operator attention regarding system conditions, maintenance needs, or operational guidance. Provides real-time feedback on treatment progress and system health.

**Scope Clarification:** This module handles operational monitoring and user information. Critical safety parameter monitoring is performed independently by the Safety Management module (Section 1.3.9). When safety thresholds are exceeded, Safety Management handles immediate protective actions while Monitoring & Alerting presents operator-appropriate information about the event.

Implementation: IDS with integrated monitoring algorithms.

### 1.3.9 Safety Management (Safety Systems)

This module implements comprehensive safety monitoring and intervention capabilities. Monitors critical parameters and system states, executes safety shutdowns when necessary, and maintains safety interlocks. Provides independent safety oversight of all treatment operations.

**The Safety Management module is the highest-priority software component with override authority over all other system functions. It operates on a fail-safe design philosophy where any fault or uncertainty results in safe state (laser disabled).**

---

**Architecture Philosophy:**
• Multiple independent hardware and software interlocks
• Positive permission required (laser cannot operate unless all conditions pass)
• Continuous high-frequency monitoring (≥100 Hz)
• Immediate response to faults (<100ms shutdown time)
• Redundant safety mechanisms with no single point of failure
• Immutable safety event logging

---

**HARDWARE INTERLOCKS**

The module monitors three critical hardware safety interlocks via Adafruit FT232H USB-to-GPIO/ADC interfaces:

**1. Footpedal Deadman Switch (GPIO-1, Digital Input)**

The footpedal implements a deadman switch safety strategy for laser emission control.

*Interlock Behavior:*
• Active-high requirement: laser can only operate while footpedal is physically depressed
• Release of footpedal triggers immediate laser shutdown
• Monitored at ≥100 Hz (every 10ms or faster)
• Timeout detection: if no valid GPIO reading within 100ms, fault is triggered
• 20ms debounce period prevents false triggers
• Fail-safe hardware: GPIO pin with pull-down resistor ensures LOW (laser disabled) on connection fault

*Rationale:* The footpedal ensures laser emission requires continuous active operator control. If operator removes foot pressure for any reason, laser immediately disables.

**2. Hotspot Smoothing Device Monitor (GPIO-1, Digital + Optional Analog)**

The hotspot smoothing device homogenizes the laser beam profile. This device must be operational for safe laser delivery.

*Interlock Behavior:*
• Active-high signal requirement: device must output valid "healthy" signal
• Signal loss triggers immediate laser shutdown
• Optional voltage level monitoring (2.5-5.0V range validation)
• Monitored at ≥100 Hz
• Fault conditions: signal absent, voltage out of range, communication timeout

*Rationale:* Smoothing device failure could result in laser hotspots (localized high intensity) that exceed safe irradiance levels and cause unintended tissue effects.

**3. Photodiode Power Monitor (GPIO-2, Analog ADC Input)**

A photodiode in the laser optical path measures actual output power in real-time.

*Interlock Behavior:*
• Real-time power measurement via ADC with voltage-to-power conversion using calibration curve
• Two-tier threshold system:
  - Warning (15% deviation): logged and displayed, treatment continues with increased monitoring
  - Fault (30% deviation): immediate laser shutdown
• Sampled at ≥100 Hz during laser operation
• Off-state validation: photodiode must read near-zero when laser is commanded off
• Detects power delivery failures (optical blockage, controller malfunction)

*Thresholds Justification:*
• 15% warning: allows for normal system variations while alerting operator
• 30% fault: represents clinically significant power deviation requiring shutdown

---

**SOFTWARE INTERLOCKS**

**4. Emergency Stop**
• User-initiated via UI button or keyboard shortcut (ESC key)
• Highest priority interrupt, bypasses all queues
• Execution time <50ms from trigger to laser disabled
• Requires supervisor authentication to reset

**5. Power Limit Enforcer**
• Absolute hardware limit (10W maximum)
• Protocol-specific limits (per treatment protocol)
• Session-specific limits (optional patient restrictions)
• Power ramp rate limiting (prevents abrupt power changes)
• Commands validated before transmission to Laser Control

**6. Session State Validator**
• Laser operation only during active treatment session
• Requires: patient selected, technician authenticated, session status "in_progress"
• Prevents laser emission outside documented treatment context

**7. Camera Feed Validator**
• Valid camera frame must be received within timeout (1 second)
• Ensures visual monitoring capability present
• Loss of feed during treatment triggers shutdown

---

**SAFETY STATE MACHINE**

States: SYSTEM_OFF, INITIALIZING, READY, ARMED, TREATING, PAUSED, FAULT, SAFE_SHUTDOWN

State transitions are strictly controlled. Any interlock failure from any state (except SYSTEM_OFF) immediately transitions to FAULT state.

**Fault Response Sequence (target <100ms):**
1. Immediate laser disable (highest priority command)
2. Actuator motion stop
3. Fault classification and logging to safety_log (immutable)
4. UI alert with fault description
5. State transition to FAULT
6. Recovery guidance displayed based on fault type

**Fault Recovery Procedures:**
• Footpedal fault: Check connections, verify GPIO readings, supervisor reset if valid
• Smoothing device fault: Check power/connections; if device fault, do NOT resume - contact service
• Photodiode fault: Check alignment/connections, run calibration test, contact service if test fails
• Camera fault: Check USB, restart camera driver, verify stream before reset
• Emergency stop: Supervisor reviews circumstances and authorizes reset if safe

---

**WATCHDOG TIMER**

Separate monitoring thread checks that main control loop calls heartbeat function at least once per timeout period (1 second). If timeout occurs, watchdog triggers emergency shutdown. This protects against software hangs or deadlocks.

---

**SAFETY EVENT LOGGING**

All safety events logged to safety_log database table with:
• Timestamp (microsecond precision)
• Event type and severity
• System state and all interlock states
• Action taken
• Session context

Safety logs are immutable (no updates/deletes) and maintained indefinitely.

---

**IMPLEMENTATION**

IDS with comprehensive safety logic including:
• Hardware interlock monitoring (GPIO reading, ADC sampling, threshold validation)
• Software interlock validation
• Safety state machine
• Fault classification and response
• Emergency shutdown prioritization
• Watchdog timer
• Safety event logging

OTS: Adafruit libraries for FT232H GPIO/ADC hardware interface

**VERIFICATION & VALIDATION**

Safety Management receives the most rigorous V&V:
• Unit tests for each interlock (pass and fail scenarios)
• Integration tests for multi-fault conditions
• Response time measurements (<100ms verification)
• State machine transition validation
• Failure mode testing (FMEA-driven)
• All tests documented in Software V&V Plan

---

Implementation: IDS with redundant safety mechanisms.

### 1.3.10 Logging and Reporting (Data Recording)

This module records comprehensive system operations, device performance data, and treatment parameters for regulatory compliance, troubleshooting, and quality assurance. Generates standardized reports for clinical and service activities.

**Two-Tier Logging Architecture:**

**High-Frequency Data (10-100 Hz):**
During treatment, time-critical data buffered to JSON files in session folder:
• Photodiode voltage (100 Hz)
• Laser commands
• Actuator position (10 Hz)
• Interlock states (100 Hz)
• Camera timestamps (30 Hz)

**Event-Based Data:**
Significant events written immediately to database:
• Protocol step transitions
• Power changes
• Safety events (immediate logging)
• User actions
• System state changes

**Post-Session Processing:**
JSON files parsed and imported to database treatment_events table after session completion. Original files retained as backup.

**Separate Safety Log:**
The safety_log table maintains immutable records with no updates/deletes permitted, enforced by database constraints.

Implementation: IDS with structured logging and reporting capabilities.

### 1.3.11 Error Handling (Fault Management)

This module provides centralized error detection, classification, and recovery mechanisms. Implements graceful degradation strategies to maintain safe operation when possible. Coordinates error reporting and system recovery procedures across all modules.

**Error Classification:**
• Critical: preventing safe operation (escalated to Safety Management)
• Major: preventing treatment but not immediate safety risk
• Minor: degrading functionality but allowing operation
• Informational: logged but no action required

**Graceful Degradation Examples:**
• Video recording failure: treatment continues, operator notified
• Actuator communication failure: treatment continues at fixed ring size if safe
• Report generation failure: data preserved, report regenerated later

Implementation: IDS with comprehensive error management framework.

---

## 1.4 Risk Management File

The Risk Management File (RMF) is a separate document addressing the risks in the complete system, including but not limited to SW risks. See section [TBD].

## 1.5 Software Requirements Specification

The Software Requirements Specification (SRS) describes the needs or expectations for the software, presented in an organized format, at the software level, and with sufficient information to understand the traceability of the information with respect to the other software documentation elements (e.g., PRD, risk management file, software design specification, device and software architecture chart, etc).

It is captured in a separate document. Will, I will prepare a draft. The draft will need your review and improvements.

## 1.6 Software Architecture Design

Refer to the information in section 1.3.

## 1.7 Software Design Specification

The SW Design Specification (SDS) presents sufficient information that would allow FDA to understand the technical design details of how the software functions, and how the software design traces to the SRS in terms of intended use, functionality, safety, and effectiveness.

It is captured in a separate document. Will, I will prepare a draft. The draft will need your review and improvements.

## 1.8 Software Development, Configuration Management, and Maintenance Practices

ALeyeGN Software development process follows IEC 62304 and is aligned with 21 CFR § 820.30 (FDA Design Controls). The development activities are:
    • Requirements, yielding the SRS document as per section 1.5.
    • Design, yielding the SDS document as per section 1.7.
    • Coding & Unit testing
    • Verification will be done at a Device level.
    • Validation will be done at a Device level.
    • Release – Will, have you thought about this? Revision tracking, release documentation, …? Every major release must be accompanied by the following documentation:
        ◦ Scope & Purpose – what the release covers.
        ◦ Roles & Responsibilities – who develops, reviews, approves.
        ◦ Release Identification – version number, baseline reference.
        ◦ Contents – features, fixes, known issues.
        ◦ Verification & Validation – test summary, traceability, anomalies.
        ◦ Risk Management – updated risk file, residual risk acceptability.
        ◦ Configuration & Change Control – approved changes, packaging, archiving.
        ◦ Deployment & Distribution – delivery method, supported platforms, rollback plan.
        ◦ Post-Market & Maintenance – anomaly tracking, patching, feedback loop.
        ◦ Approvals – signatures from Dev, QA, Regulatory, Mgmt.
    • Maintenance – The source code is maintained in XXX (Git, Jira, …). The binary code is maintained in YYY (or XXX). Need to make sure that only the current release is available for device build. May be (but not necessary) another use for the QMS repository.

---

**Document Control:**
• **Version:** 2.0 (Minimal Changes from v1.0)
• **Date:** 2025-10-15
• **Changes from v1.0:** Added Camera & Image Processing module (1.3.3), expanded Safety Management module (1.3.9) with detailed hardware interlocks specification, clarified footpedal as safety interlock (not accessory), added two-tier logging architecture detail, renamed Embedded Devices Control to Actuator & Peripheral Control with ring size calibration detail, added audit trail and high-frequency data handling to Data Management.

---

**End of Section 1: Software Development**
