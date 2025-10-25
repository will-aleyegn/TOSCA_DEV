# 1. Software Development

## 1.1 Purpose of a Separate Software Development Section

Software is a critical component of the TOSCA system. It is subject to IEC 62304 lifecycle requirements, which are recognized by the FDA and international regulators. This section ensures that software planning, development, verification & validation (V&V), and maintenance are documented, controlled, and integrated into ALeyeGN's Quality Management System (QMS).

The Design History File (DHF) deliverables that are related to software are documented in an FDA guidance document titled "Content of Premarket Submissions for Device Software Functions". This guidance defines two levels of documentation: Basic and Enhanced. The guidance states that "Enhanced Documentation should be provided for any premarket submission that includes device software function(s) where a failure or flaw of any device software function(s) could present a hazardous situation with a probable risk of death or serious injury, either to a patient, user of the device, or others in the environment of use".

**Background:** The terms "Enhanced Documentation" and "Major Level of Concern" were introduced in a 2023 update of the FDA guidance document titled "Content of Premarket Submissions for Device Software Functions". Prior to that update, the FDA used three Levels of Concern (Minor, Moderate, Major) for device software. In the 2023 update these three levels of concern were replaced with two Documentation Levels (Basic, Enhanced).

## 1.2 Documentation Level Evaluation

While Risk Analysis activities are not yet completed, we can reasonably conclude that a failure in the TOSCA control software may expose the patient eye to excessive laser irradiance, thus presenting potential for serious injury. This single determination is sufficient to prescribe an Enhanced Documentation Level.

As an independent reasonableness check, we compare this conclusion to publicly available information about several recently cleared selective laser trabeculoplasty (SLT) devices. We note that three SLT devices cleared by the FDA in 2022 and 2023 stated in their 510(k) Summary Letters that their Level of Concern is Major:
• Belkin Eagle, K230722
• Ellex Tango, K222395
• Lumenis Selecta, K220877

From a Risk Analysis perspective, Major Level of Concern is prescribed when a failure may result in serious injury or death. These are the same conditions that prescribe Enhanced Documentation Level.

This information supports the "Enhanced Documentation" requirement for TOSCA.

The sections below follow the Recommended Documentation table in "Content of Premarket Submissions for Device Software Functions" for Enhanced Documentation Level.

## 1.3 Software Description

The TOSCA software implements a layered architecture that separates user interface, treatment control, device management, and safety functions. The software is developed and validated according to medical device software standards (IEC 62304) and incorporates both commercial off-the-shelf (OTS) components and in-house developed software (IDS) as needed for device functionality.

The software architecture is depicted in Figure 1 below. Each block represents a functional software module, and the primary communications between modules are shown by arrows. Safety-critical data paths are emphasized, showing that the Safety Management module has override authority over treatment delivery.

### Figure 1: TOSCA Software Architecture Block Diagram

```
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
│ (joystick, etc.)  │                        └─────────┬────────┘
└─────────┬─────────┘                                  │
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
│  (Patient DB)  │                            └───────┬───────┘
└────────┬───────┘                                    │
         │                                            │
         │      ┌─────────────────────────┐          │
         └─────►│  Laser Control & TEC    │◄─────────┘
                │  (Arroyo Interface)     │
                └────────────┬────────────┘
                             │
       ┌─────────────────────┼────────────────────┐
       │                     │                    │
       ↓                     ↓                    ↓
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  Actuator &  │   │    Camera &      │   │   GPIO Safety    │
│ Peripheral   │   │     Image        │   │   Interlocks     │
│   Control    │   │   Processing     │   │  • Footpedal     │
│  (Xeryon)    │   │ • Ring detect    │   │  • Smoothing Dev │
└──────┬───────┘   │ • Focus measure  │   │  • Photodiode    │
       │           │ • Video record   │   └────────┬─────────┘
       │           └─────────┬────────┘            │
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ↓
                   ┌──────────────────┐
                   │      Safety      │◄────── HIGHEST PRIORITY
                   │   Management     │        OVERRIDE AUTHORITY
                   │ (Master Control) │
                   └─────────┬────────┘
                             │
                             ↓
                   ┌──────────────────┐
                   │  Error Handling  │
                   │ (Fault Mgmt)     │
                   └──────────────────┘

Legend:
──► Operational commands and data flow
═══► Safety-critical interlock signals
```

The modules shown in Figure 1 are explained in detail below.

### 1.3.1 GUI (User Interface)

The GUI module manages all user interactions and display functions through a tabbed interface. This includes real-time display of camera video streams, patient information management, treatment session controls, system status indicators, and alert notifications. The module provides operator controls for treatment parameters and displays system feedback including safety interlock status to ensure proper operation.

The GUI presents safety status with high visual prominence per human factors engineering principles. Critical safety indicators (footpedal status, interlocks, emergency stop) are displayed with color coding (green = safe, red = fault) and positioned for immediate operator awareness.

**Implementation:** Combines OTS GUI framework (PyQt6) with IDS for device-specific clinical workflow, safety status display, and regulatory-compliant user interface design.

**Verification:** User interface testing includes usability evaluation, workflow validation, and safety information display verification per human factors requirements.

### 1.3.2 Operator Input Devices

This module manages non-safety-critical operator input devices including joysticks for positioning adjustments, keyboards, and mouse controls for system navigation and data entry. These devices support clinical workflow and system operation but are not required for safety functions. The module processes input events and translates them into appropriate system commands.

**Important Note:** Safety-critical operator inputs (footpedal deadman switch, emergency stop button) are handled directly by the Safety Management module (Section 1.3.9) through dedicated hardware interfaces and are subject to enhanced validation requirements. These safety-critical inputs are not processed through this module to maintain clear separation between operational and safety-critical functions.

**Implementation:** Utilizes OTS device drivers and input handling libraries. Input validation and command translation for clinical workflows implemented as IDS.

**Verification:** Input device testing validates command translation accuracy, responsiveness, and proper segregation from safety-critical input paths.

### 1.3.3 Camera & Image Processing

This module manages the Allied Vision camera system and performs real-time image analysis supporting both operational and safety functions. The module integrates with the VmbPy SDK for camera hardware control and the OpenCV (cv2) library for image processing algorithms.

**Key Functions:**
• **Live video feed** acquisition and display at 30 frames per second (FPS) with 1920×1080 resolution
• **Laser ring detection** using Hough Circle Transform algorithm for alignment verification and treatment area identification
• **Image focus quality measurement** using Laplacian variance method to assess optical system readiness and image clarity
• **Treatment session video recording** for regulatory documentation, quality assurance, and post-treatment review
• **Real-time visual monitoring** to verify proper laser positioning and provide operator feedback during treatment setup

**Safety Integration:**
The Camera Valid interlock (monitored by Safety Management module, Section 1.3.9) ensures that a valid image stream is present before laser operation is permitted. The system validates that fresh camera frames are being received (frame age <1 second) as a prerequisite for treatment. Loss of camera feed during treatment triggers immediate safety shutdown to ensure that visual monitoring capability is maintained throughout laser delivery.

Ring detection results are used by operators for manual alignment verification prior to treatment initiation. The algorithm detects the circular laser ring pattern and provides visual overlay guidance. Focus quality metrics provide objective assessment of optical system readiness, with real-time feedback to the operator during alignment procedures.

**Implementation:** Combines OTS components (VmbPy SDK for camera interface, OpenCV library for basic image processing operations) with IDS for medical-specific algorithms including:
• Ring detection algorithm tuning and validation for TOSCA's specific optical characteristics
• Focus quality thresholds calibrated to the optical system performance requirements
• Treatment documentation video recording with embedded metadata (timestamp, treatment parameters, session information)
• Image processing pipeline optimization for real-time performance

**Verification:**
• Ring detection algorithm validated against known test patterns with defined circle parameters (radius, position, contrast)
• Focus measurement algorithm calibrated using focused and defocused reference images spanning the expected optical range
• Video recording verified for frame rate consistency, resolution accuracy, timestamp synchronization, and file integrity
• Real-time performance validated to maintain ≥30 FPS without frame drops during simultaneous treatment control operations

### 1.3.4 Data Management (Patient & Session Data)

This module manages comprehensive patient records, treatment session data, and associated media files. The module provides database operations for creating, retrieving, updating, and querying patient information and treatment histories. It handles data import/export functions and maintains data integrity throughout the treatment workflow.

**Database Architecture:**
The system uses SQLite for local data storage with the following key tables:
• **patients** - Anonymized patient records using coded identifiers (e.g., P-2025-0001)
• **sessions** - Treatment session records with protocol parameters and outcomes
• **treatment_events** - Detailed event log of all actions during treatment
• **safety_log** - Dedicated table for safety-related events (immutable, highest integrity)
• **protocols** - Saved treatment protocol templates
• **tech_users** - Operator authentication and audit trail
• **calibrations** - Device calibration data and history

**Audit Trail Implementation:**
The database implements a comprehensive audit trail architecture with immutable event logging. Critical safety events are logged to the dedicated safety_log table, which is separate from operational logs and enforces write-once semantics (no updates or deletes permitted). Each safety log entry includes:
• Timestamp with microsecond precision
• Event type and severity classification
• Complete system state snapshot
• All interlock states at time of event
• Action taken by safety system
• Session context (session ID, patient ID, technician ID)

**High-Frequency Data Handling:**
High-frequency treatment data (sampled at 10-100 Hz including photodiode readings, laser commands, actuator position, and interlock states) is initially buffered to JSON files during active treatment to avoid database I/O latency impacting the real-time control loop (10 millisecond cycle time requirement). After session completion, this buffered data is parsed and imported to the SQLite treatment_events table for long-term storage, analysis, and regulatory documentation. This two-tier approach ensures real-time control loop performance while maintaining complete regulatory documentation.

**Patient Data Privacy:**
All patient data is anonymized using a coded patient identification system with no Protected Health Information (PHI) stored in the device database. The patient code format (P-YYYY-NNNN) provides unique identification for longitudinal tracking across multiple treatment sessions while maintaining privacy. Linkage to identifiable patient information is maintained externally to the device in the clinic's practice management system.

**Session Documentation:**
Each treatment session creates an immutable record including:
• Protocol parameters (commanded power, duration, ring size)
• Actual delivered parameters (measured power, timestamps)
• Any deviations from protocol
• All safety events and operator interventions
• Video recording file path
• Post-treatment notes

**Implementation:** Utilizes OTS SQLite database engine and SQLAlchemy ORM framework with IDS for medical data model design, audit trail implementation, high-frequency data buffering architecture, and regulatory compliance features.

**Verification:** Database integrity validated through stress testing, concurrent access testing, and data recovery procedures. Immutability of safety_log verified through attempted modification testing. Backup and restore procedures validated.

### 1.3.5 Actuator & Peripheral Control

This module provides control interface for motorized positioning components and auxiliary peripheral devices used in treatment delivery.

**Primary Functions:**
• **Linear actuator control** using Xeryon API for laser ring size adjustment (2-5 mm diameter range)
• **Position command execution** with smooth motion profiles to avoid optical disturbances
• **Actuator position feedback monitoring** for closed-loop position control
• **Calibration management** for position-to-ring-size mapping using stored calibration curves
• **Auxiliary equipment coordination** (positioning aids, motorized components)

The linear actuator adjusts the optical path length to modify the laser ring diameter at the treatment plane. Ring size is a treatment protocol parameter that affects energy distribution per unit area. The module receives ring size commands from Session Control (Section 1.3.7) and executes calibrated position moves to achieve the commanded ring diameter.

**Ring Size Calibration:**
The relationship between actuator position (micrometers) and laser ring diameter (millimeters) is established through a calibration procedure where:
1. Actuator is moved to multiple positions spanning the operational range
2. Camera image processing measures the actual ring diameter at each position
3. Calibration curve (typically linear or polynomial fit) is computed and stored in database
4. During treatment, commanded ring size is converted to actuator position using the calibration curve

Calibration data is maintained in the calibrations table with version control and traceability to calibration procedures.

**Implementation:** Combines OTS device driver (Xeryon library for linear stage control providing low-level motion commands) with IDS for treatment-specific functions including:
• Calibration curve implementation and interpolation
• Position validation against safety limits
• Coordination with treatment protocol execution
• Ring size command translation

Safety position limits are enforced by both the Xeryon controller firmware (hardware limits) and software bounds checking (validated range: 0-2500 micrometers corresponding to approximately 2-5 mm ring diameter range).

**Verification:**
• Actuator position accuracy validated against external position measurement (laser interferometer or calibrated displacement sensor)
• Ring size calibration verified using camera-based image analysis at multiple actuator positions
• Position repeatability tested over multiple move cycles
• Motion profile smoothness validated for absence of sudden accelerations that could cause optical misalignment

### 1.3.6 Laser Control & Thermal Management

This module controls the Arroyo Instruments TEC Controller via RS-232 serial communication protocol, managing laser power output, emission timing, and thermal regulation. The module provides the direct hardware interface to the laser system while operating under governance of the Safety Management module.

**Key Functions:**
• **Laser power level commands** (0-10 Watt range) transmitted via Arroyo serial protocol
• **Laser emission enable/disable control** with explicit on/off commands
• **Thermal Electric Cooler (TEC) temperature setpoint** configuration and monitoring
• **Laser diode temperature monitoring** for thermal regulation feedback
• **Power stability maintenance** during treatment delivery to ensure consistent dosimetry
• **Laser system status and fault monitoring** including temperature alarms and hardware faults

**Safety Architecture:**
All laser control commands are validated by the Safety Management module (Section 1.3.9) before execution. The module implements a command validation layer that checks the following conditions before any laser command is transmitted:
• Active treatment session exists and is in appropriate state
• All hardware interlocks satisfied (footpedal depressed, smoothing device healthy, photodiode reading valid)
• Commanded power is within protocol limits and absolute safety limits
• No active safety faults or emergency stop condition

If any validation fails, laser commands are blocked and the laser is maintained in safe (disabled, zero power) state. The module responds to safety shutdown commands with highest priority, immediately setting power to zero and disabling emission. The target shutdown time is <100 milliseconds from safety trigger to laser off.

**Thermal Management:**
The TEC control maintains stable laser diode temperature for consistent output power and wavelength. Temperature monitoring provides continuous feedback for fault detection. Out-of-range temperature conditions (overheating indicating cooling system failure, or temperature below setpoint indicating TEC malfunction) trigger safety shutdown to protect the laser diode and prevent unpredictable laser output.

TEC setpoint is established during system characterization and stored in configuration. Temperature is monitored continuously during laser operation with fault thresholds set to ±5°C from setpoint.

**Serial Communication Protocol:**
The Arroyo controller uses an ASCII-based serial protocol at 9600 baud, 8-N-1 configuration. Commands include:
• Power set: "LASER:POWER <value>"
• Laser enable: "LASER:OUTPUT ON"
• Laser disable: "LASER:OUTPUT OFF"
• Temperature set: "TEC:TEMP <value>"
• Status query: "LASER:STATUS?"
• Temperature query: "TEC:TEMP?"

All serial communications are logged with timestamps for regulatory audit trail and troubleshooting.

**Implementation:** Combines OTS serial communication library (pyserial for RS-232 interface) with IDS for:
• Arroyo-specific protocol implementation and command formatting
• Medical device safety integration and command validation framework
• Temperature monitoring and fault detection logic
• Serial communication error handling and retry mechanisms

All serial communications are logged with timestamps for regulatory audit trail.

**Verification:**
• Serial protocol implementation validated against Arroyo Instruments specifications and test sequences
• Power control accuracy measured with calibrated photodiode at multiple power levels (0.5W, 1W, 2W, 5W, 8W, 10W)
• Thermal control performance validated over operational temperature range (15-35°C ambient)
• Safety shutdown response time verified to be <100 milliseconds from shutdown command to measured power at zero
• Communication error handling validated through fault injection testing (cable disconnect, noise injection)

### 1.3.7 Session Control (Treatment Management)

This module orchestrates complete treatment sessions from initiation through completion. It manages treatment protocol selection and loading, parameter validation, session timing, and coordinates between all system components. The module maintains current session status including treatment phase, progress tracking, and system operational readiness to ensure proper sequence of operations.

**Session Workflow:**
1. **Session Initialization** - Technician authentication, patient selection (existing or new patient), session creation in database
2. **Pre-Treatment Setup** - Protocol selection or customization, parameter validation, system readiness checks
3. **Treatment Execution** - Protocol step sequencing, real-time parameter control, progress monitoring, operator intervention handling
4. **Session Completion** - Data finalization, video file association, session notes, database commit

**Protocol Management:**
The module loads treatment protocols from the database (Section 1.3.4) and validates all parameters against safety limits before execution. Protocols define:
• Treatment steps (one or more sequential phases)
• Power levels (start and end power for each step, supporting constant power or power ramping)
• Duration (time for each step in seconds)
• Ring size (target ring diameter in millimeters)
• Ramp type (constant, linear, logarithmic, exponential)

Real-time protocol execution includes:
• Step timing and transition management
• Power interpolation for ramping protocols (linear, logarithmic, exponential curves)
• Ring size changes between steps (coordinated with Actuator Control module)
• Progress calculation and display updates
• Support for operator-initiated pause/resume

**Operator Adjustments:**
The module supports real-time treatment adjustments with appropriate logging:
• Power level modifications during treatment (logged as protocol deviations)
• Treatment pause/resume
• Early termination
• Emergency stop (coordinated with Safety Management)

All deviations from the original protocol are logged with timestamp, old value, new value, and operator rationale for regulatory documentation and quality assurance review.

**Implementation:** IDS designed for medical treatment workflows including protocol parsing and validation, step sequencing logic, timing control, parameter interpolation algorithms, and coordination with hardware control modules.

**Verification:** Protocol execution validated against test protocols with known timing and parameters. Timing accuracy verified to ±100 milliseconds. Parameter interpolation algorithms validated against calculated expected values. Deviation logging verified for completeness and accuracy.

### 1.3.8 Monitoring and Alerting (System Surveillance)

This module provides operator-facing system status information, operational guidance, and non-critical alert notifications. It focuses on usability and workflow support rather than safety-critical monitoring (which is handled by Safety Management module, Section 1.3.9).

**Functions:**
• **System operational status display** - Device connection status, system state, readiness indicators
• **Treatment progress indicators** - Elapsed time, time remaining, step progression, energy delivered
• **Maintenance reminders** - Service due dates, calibration expiration, consumable replacement
• **Operator guidance messages** - Workflow prompts (e.g., "Align laser ring to target area", "Verify patient positioning")
• **Performance metrics** - Treatment statistics, system utilization, operator efficiency metrics
• **Device connection status** - Camera, laser, actuator, GPIO controllers connection and health

**Scope Clarification:**
This module handles operational monitoring and user information display. Critical safety parameter monitoring (interlock states, photodiode power measurement, fault detection) is performed independently by the Safety Management module. This separation ensures that safety functions are not dependent on operator interface components.

When safety thresholds are exceeded, Safety Management handles immediate protective actions (laser shutdown, state transition to fault), while Monitoring & Alerting receives notification and presents operator-appropriate information about the event (fault description, recovery guidance).

**Alert Classifications:**
• **Informational** - Status updates, workflow guidance (blue indicator)
• **Warning** - Non-critical issues requiring attention but not preventing operation (yellow indicator)
• **Critical** - Issues preventing safe operation, displayed prominently (red indicator)
• **Safety** - Safety system events, displayed with highest visual priority (red, flashing if appropriate)

**Implementation:** IDS with PyQt6-based UI components for status display, alert presentation, and information logging. Receives status updates from other modules via signal/slot mechanism but has no control authority over device functions. Display logic implemented to prioritize safety information over operational information per human factors principles.

**Verification:** Alert display validated for correct prioritization, visual prominence, and operator comprehension through usability testing. Alert timing verified to be <500 milliseconds from event occurrence to display update.

### 1.3.9 Safety Management (Safety Systems)

The Safety Management module is the highest-priority software component, implementing comprehensive safety monitoring and immediate intervention capabilities. This module has override authority over all other system functions and operates with a fail-safe design philosophy where any fault or uncertainty results in safe state (laser disabled, zero power).

**Architecture Philosophy:**
• **Multiple independent hardware and software interlocks** - No single interlock failure allows unsafe laser operation
• **Positive permission required** - Laser cannot operate unless all conditions explicitly pass (not merely absence of fault)
• **Continuous high-frequency monitoring** - All interlocks checked at ≥100 Hz to ensure rapid fault detection
• **Immediate response** to any interlock failure - Target shutdown time <100 milliseconds
• **Redundant safety mechanisms** with no single point of failure
• **Immutable safety event logging** for complete audit trail and regulatory compliance

---

**HARDWARE INTERLOCKS**

The module monitors three critical hardware safety interlocks via Adafruit FT232H USB-to-GPIO/ADC interfaces. Two FT232H devices are used: GPIO-1 for digital interlocks (footpedal and smoothing device), GPIO-2 for analog photodiode monitoring.

**1. Footpedal Deadman Switch (GPIO-1, Digital Input)**

The footpedal is the primary operator control for laser emission and implements a deadman switch safety strategy.

*Interlock Behavior:*
• **Active-high requirement** - Laser can only operate while footpedal is physically depressed by the operator
• **Immediate shutdown** - Release of footpedal triggers immediate laser disable command
• **Continuous monitoring** - Footpedal state polled at ≥100 Hz (every 10 milliseconds or faster)
• **Timeout detection** - If no valid GPIO reading is received within 100 milliseconds, timeout fault is triggered
• **Debouncing** - 20 millisecond debounce period prevents false triggers from electrical noise or mechanical switch bounce
• **Fail-safe hardware design** - GPIO pin has pull-down resistor ensuring LOW state (laser disabled) on any connection fault, cable disconnect, or power loss to footpedal

*Rationale:*
The footpedal deadman switch ensures that laser emission requires continuous active operator control. If the operator removes foot pressure for any reason (distraction, emergency, incapacitation), the laser immediately disables. This is a fundamental safety principle for operator-controlled medical lasers.

*Implementation:*
GPIO digital input pin (e.g., D4 on FT232H) configured with internal pull-down resistor. Footpedal switch connects pin to +3.3V when depressed. Software polls pin state at 100 Hz minimum within main safety loop.

**2. Hotspot Smoothing Device Monitor (GPIO-1, Digital + Optional Analog)**

The hotspot smoothing device is a beam conditioning element that homogenizes the laser beam profile for uniform energy distribution. This device must be operational for safe laser delivery.

*Interlock Behavior:*
• **Active-high signal requirement** - Device must output valid "healthy" digital signal for laser operation
• **Signal loss triggers shutdown** - Absence of signal indicates device failure or disconnection, triggering immediate laser shutdown
• **Optional voltage level monitoring** - If analog signal is available, voltage level is validated to be within acceptable range (e.g., 2.5-5.0 VDC)
• **Continuous monitoring** - Device signal polled at ≥100 Hz
• **Fault conditions** include: signal absent, voltage out of specified range, communication timeout
• **Purpose** - Ensures beam conditioning device is operational before laser emission is permitted, preventing potential hotspots that could cause concentrated tissue damage

*Rationale:*
The smoothing device transforms the Gaussian laser beam profile into a more uniform "top-hat" distribution. Failure of this device could result in laser hotspots (localized high-intensity regions) that exceed safe irradiance levels and cause unintended tissue effects. This interlock ensures the device is functioning before laser emission.

*Implementation:*
GPIO digital input pin (e.g., D5 on FT232H) receives signal from smoothing device. Optional ADC input (if analog health signal available) monitors voltage level. Software validates both signal presence and (if applicable) voltage level at 100 Hz within main safety loop.

**3. Photodiode Power Monitor (GPIO-2, Analog ADC Input)**

A photodiode sensor in the laser optical path (pickoff or transmitted beam sampling) measures actual laser output power in real-time for verification and safety monitoring.

*Interlock Behavior:*
• **Real-time power measurement** - Photodiode voltage is sampled via ADC and converted to watts using calibration curve
• **Voltage-to-power conversion** using calibration curve stored in database (typical relationship: linear, P = k × V + offset)
• **Two-tier threshold system:**
  - **Warning threshold (15% deviation)** - If measured power differs from commanded power by >15%, warning is logged and displayed to operator. Laser continues operation with increased monitoring frequency.
  - **Fault threshold (30% deviation)** - If measured power differs from commanded power by >30%, immediate laser shutdown is triggered. Fault is logged and supervisor reset is required.
• **Sampling rate** - Photodiode voltage sampled at ≥100 Hz during laser operation
• **Off-state validation** - When laser is commanded off, photodiode must read near-zero (< 0.1W equivalent). Detection of power when laser should be off indicates errant emission or measurement fault, triggering immediate fault state.
• **Fault detection** - Detects power delivery failures (optical path blockage, laser controller malfunction, beam steering errors) and excess power conditions

*Rationale:*
The photodiode provides closed-loop verification that commanded laser power matches delivered laser power. This detects:
• Laser controller failures (commanded 5W but emitting 8W)
• Optical path blockages (commanded 5W but only 2W reaching target)
• Measurement system failures (photodiode fault, ADC failure)
• Errant laser emission (laser on when commanded off)

Two-tier threshold system provides graduated response: minor deviations trigger warnings allowing operator intervention, while major deviations trigger automatic protective shutdown.

*Thresholds Justification:*
• 15% warning threshold: Allows for normal system variations (measurement noise, laser stability, photodiode linearity) while alerting operator to investigate potential issues
• 30% fault threshold: Represents clinically significant power deviation that could result in under-treatment or over-treatment, requiring immediate shutdown

*Implementation:*
Photodiode outputs voltage (typically 0-5 VDC corresponding to 0-10 W laser power) connected to FT232H ADC input. Software samples ADC at ≥100 Hz, applies calibration curve (voltage → watts), compares measured power to commanded power, and evaluates against warning and fault thresholds. Calibration data (slope, intercept, validation date) retrieved from database calibrations table.

---

**SOFTWARE INTERLOCKS**

In addition to hardware interlocks, the module implements several software-based safety validations that are evaluated before permitting laser operation.

**4. Emergency Stop**

User-initiated immediate shutdown capability provides manual override for any situation where operator determines laser must be stopped immediately.

*Interlock Behavior:*
• **Activation methods** - Large red UI button labeled "EMERGENCY STOP" and keyboard shortcut (ESC key with global capture)
• **Highest priority interrupt** - Bypasses all command queues and delays
• **Immediate execution** - Emergency stop code path executes in <50 milliseconds
• **System response:**
  1. Laser power set to zero
  2. Laser disable command sent to Arroyo controller
  3. Actuator motion stopped
  4. System transitions to FAULT state
  5. Event logged to safety_log with timestamp and trigger source
• **Reset requirement** - After emergency stop activation, system requires supervisor authentication (password or PIN) to reset from FAULT state
• **Logging** - Emergency stop events include trigger source (UI button, keyboard, programmatic call), timestamp, operator ID, session context

*Rationale:*
Emergency stop provides human oversight capability. Regardless of automated safety interlocks, the operator may observe conditions (patient movement, unexpected tissue response, equipment anomaly) requiring immediate laser shutdown. This control must be immediately accessible and highly reliable.

**5. Power Limit Enforcer**

Software-enforced power limits provide multiple layers of protection against excessive laser power.

*Interlock Behavior:*
• **Absolute hardware limit** - 10 Watts maximum (set based on laser hardware specifications and maximum credible therapeutic power)
• **Protocol-specific limits** - Each treatment protocol defines maximum power for that protocol (e.g., protocol max = 6W even though hardware supports 10W)
• **Session-specific limits** - Optional patient-specific power restrictions (e.g., for patients with sensitivities or special considerations)
• **Power ramp rate limiting** - Maximum allowed power change rate (e.g., 2 W/second) prevents abrupt power jumps that could cause thermal shock
• **Validation timing** - All power commands validated before transmission to Laser Control module
• **Response to violation** - If commanded power exceeds any applicable limit, command is rejected, fault is logged, and (if during treatment) laser is disabled

*Limits Hierarchy:*
```
Commanded Power must satisfy:
  Commanded Power ≤ Absolute Hardware Limit (10W) AND
  Commanded Power ≤ Protocol Maximum Power AND
  Commanded Power ≤ Session Maximum Power (if set) AND
  Power Change Rate ≤ Ramp Rate Limit
```

If any limit is violated, the most restrictive limit is applied and violation is logged.

*Rationale:*
Multiple power limit layers provide defense-in-depth protection:
• Absolute limit prevents hardware damage and gross over-treatment
• Protocol limits ensure each treatment type stays within validated parameters
• Session limits allow clinician judgment for individual patient needs
• Ramp rate limit prevents thermal shock and allows gradual tissue response

**6. Session State Validator**

Laser operation is only permitted during an active, documented treatment session with proper authentication and patient association.

*Interlock Behavior:*
• **Active session required** - Laser commands are only processed when session exists with status = "in_progress"
• **Requirements for active session:**
  - Patient selected (patient_id assigned to session)
  - Technician authenticated (tech_id assigned to session)
  - Session created in database with start timestamp
  - Session status set to "in_progress" (not "pending", "paused", "completed", or "aborted")
• **Validation timing** - Session state checked before each laser enable command
• **Prevents** any laser emission outside documented treatment context, ensuring all laser use is attributed to a patient and operator for regulatory audit trail

*Rationale:*
Medical device regulations require complete documentation of when and how devices are used, and on which patients. The session state interlock ensures that no laser operation occurs without proper documentation, preventing:
• Accidental laser activation during non-treatment activities (setup, cleaning, testing)
• Laser use without patient association (untraceable treatment)
• Laser use without operator identification (accountability gap)

**7. Camera Feed Validator**

Valid camera image stream must be present during treatment to ensure visual monitoring capability.

*Interlock Behavior:*
• **Fresh frame requirement** - Valid camera frame must have been received within timeout period (default: 1 second)
• **Frame validation** - Camera frame must have expected resolution, valid pixel data (not all zeros), and valid timestamp
• **Pre-treatment check** - Camera feed validity verified before treatment session start
• **Continuous monitoring** - Frame freshness checked continuously during treatment (every control loop cycle)
• **Loss of feed response** - If camera feed is lost during treatment (frame age exceeds timeout), immediate laser shutdown triggered
• **Purpose** - Ensures visual monitoring and documentation capability throughout treatment

*Rationale:*
Camera feed provides essential functions:
• Operator visual monitoring of treatment area during laser delivery
• Ring detection for alignment verification
• Video recording for treatment documentation and quality review
• Post-treatment verification of treatment effect

Loss of camera feed removes a critical monitoring and safety verification layer. If camera feed is lost, treatment cannot proceed safely and must be stopped immediately.

---

**SAFETY STATE MACHINE**

The module implements a state machine governing system safety status and enforcing valid state transitions:

**States:**
• **SYSTEM_OFF** - Application not running, all hardware powered down
• **INITIALIZING** - Application starting, hardware connection and self-test in progress
• **READY** - All hardware connected and healthy, standing by for session initiation
• **ARMED** - Active session exists, all interlocks satisfied, awaiting footpedal depression
• **TREATING** - Footpedal depressed, laser emission authorized, treatment in progress
• **PAUSED** - Treatment temporarily suspended by operator, laser off, awaiting resume command
• **FAULT** - One or more interlocks failed, laser disabled, supervisor reset required before operation can resume
• **SAFE_SHUTDOWN** - Controlled shutdown sequence in progress, transitioning to READY or SYSTEM_OFF

**State Transition Rules:**
```
SYSTEM_OFF → INITIALIZING: Application starts
INITIALIZING → READY: All hardware connected, self-tests pass
INITIALIZING → FAULT: Hardware connection failure or self-test failure

READY → ARMED: Session created/activated, all interlocks pass
ARMED → TREATING: Footpedal depressed (while all other interlocks still pass)
ARMED → READY: Session ended/closed

TREATING → ARMED: Footpedal released (normal pause between treatment intervals)
TREATING → PAUSED: Operator pauses treatment (footpedal may be released)
TREATING → FAULT: Any interlock failure detected

PAUSED → TREATING: Operator resumes, footpedal depressed, all interlocks pass
PAUSED → READY: Treatment session ended
PAUSED → FAULT: Interlock failure during pause

FAULT → SAFE_SHUTDOWN: Fault acknowledged, fault condition cleared
SAFE_SHUTDOWN → READY: Supervisor authentication provided, system reset complete

ANY STATE → FAULT: Emergency stop activated OR critical interlock failure
```

**State Machine Properties:**
• State transitions are strictly controlled and validated
• Invalid transition requests are rejected and logged
• FAULT state is "sticky" - requires supervisor authentication to exit
• Only one active state at any time (no compound states)
• State changes logged with timestamp, old state, new state, trigger reason

*Rationale:*
State machine provides formal structure ensuring system cannot reach unsafe configurations. For example:
• Cannot reach TREATING state without first validating ARMED state (all interlocks satisfied)
• Cannot exit FAULT state without supervisor oversight (prevents automatic recovery from potentially dangerous conditions)
• Any abnormal condition immediately transitions to FAULT state (fail-safe)

---

**FAULT HANDLING**

When a fault condition is detected (any interlock failure, emergency stop, or watchdog timeout), the module executes a prioritized shutdown sequence:

**Fault Response Sequence (target execution time: <100 milliseconds):**
1. **Immediate laser disable** - Highest priority command sent to Laser Control module (Section 1.3.6): power = 0, emission = OFF
2. **Actuator motion stop** - Stop command sent to Actuator Control (Section 1.3.5) to prevent continued motion during fault
3. **Fault classification** - Fault source identified (which interlock triggered, or emergency stop, or watchdog)
4. **Event logging** - Immutable record written to safety_log database table including:
   - Timestamp (microsecond precision)
   - Fault type and severity
   - System state at fault detection
   - All interlock states (footpedal, smoothing device, photodiode reading, etc.)
   - Session context (session_id, patient_id, tech_id)
   - Action taken
5. **State transition** - System state set to FAULT
6. **UI alert** - Prominent fault notification displayed to operator with fault description
7. **Recovery guidance** - Recovery procedure steps displayed to operator based on fault type (see recovery procedures below)

**Fault Classification:**
• **Transient** - Brief interruption that may self-clear (e.g., momentary photodiode noise spike)
• **Sustained** - Persistent fault requiring intervention (e.g., footpedal cable disconnected)
• **Critical** - Fault indicating potential equipment malfunction or safety system failure (e.g., photodiode reads power when laser commanded off)

**Recovery Procedures (by fault type):**

*Footpedal Fault:*
1. Check footpedal cable connection to FT232H GPIO controller
2. Test footpedal operation (depress and release, verify visual indicator)
3. Verify GPIO pin reading in system diagnostics display
4. If readings valid, supervisor reset to clear fault
5. If readings invalid, do not resume treatment - contact service technician

*Smoothing Device Fault:*
1. Check smoothing device power supply and connections
2. Verify device status indicator LED or display (if equipped)
3. Check GPIO cable connection to FT232H
4. If device indicates fault, do NOT resume treatment - contact service technician
5. If device is healthy and connections verified, supervisor reset to clear fault

*Photodiode Fault:*
1. Check optical pickoff alignment (may have shifted due to vibration or impact)
2. Verify photodiode cable connection to FT232H ADC input
3. Run photodiode calibration verification test in system diagnostics
4. Review recent photodiode readings in treatment log (trending toward failure?)
5. If calibration test passes, supervisor reset to clear fault
6. If calibration test fails or readings erratic, contact service technician - do not resume treatment

*Camera Fault:*
1. Check camera USB connection to computer
2. Check camera power LED (if equipped)
3. Use system diagnostics to restart camera driver/SDK
4. Verify camera image stream in diagnostics display
5. If camera stream restored, supervisor reset to clear fault
6. If camera unresponsive, treatment cannot continue - contact service technician

*Emergency Stop Reset:*
1. Operator explains reason for emergency stop activation to supervisor
2. Supervisor reviews circumstances and determines appropriate action
3. If safe to proceed: supervisor authentication provided, system reset
4. If unsafe to proceed: session terminated, incident documented

**Supervisor Authentication:**
Supervisor-level user credentials (username and password or PIN) required to reset from FAULT state. This ensures oversight and accountability for fault recovery decisions. Authentication is logged with fault reset event.

---

**WATCHDOG TIMER**

A software watchdog timer monitors the main control loop for responsiveness to detect software hangs, deadlocks, or infinite loops that could prevent safety monitoring.

*Watchdog Behavior:*
• **Heartbeat requirement** - Main safety control loop must call watchdog "heartbeat" function at least once per timeout period (default: 1 second)
• **Monitoring thread** - Separate thread checks heartbeat freshness every 100 milliseconds
• **Timeout detection** - If no heartbeat received within timeout period, watchdog triggers emergency fault
• **Emergency shutdown** - Watchdog timeout executes same shutdown sequence as other faults (laser disable, state = FAULT, logging)
• **Timeout value justification** - 1 second timeout is sufficiently long to avoid false triggers from normal processing delays, but short enough to prevent extended unsafe operation if control loop stalls

*Rationale:*
Software failures (infinite loops, deadlocks, memory corruption, exceptions in critical code) could prevent the safety monitoring from executing. If safety checks stop running, interlocks are not being evaluated and unsafe conditions could go undetected. The watchdog timer provides independent detection of control loop failure and triggers emergency shutdown if the loop stops running.

---

**SAFETY EVENT LOGGING**

All safety-related events are logged to the safety_log database table (Section 1.3.4) with comprehensive information for regulatory audit trail, incident investigation, and system reliability analysis.

**Logged Events:**
• Interlock state changes (footpedal depressed/released, smoothing device healthy/fault, photodiode warning/fault)
• Emergency stop activation and reset
• Power limit violations
• Session state validation failures
• Camera feed loss and restoration
• System state changes (particularly transitions to/from FAULT state)
• Watchdog timeouts
• Hardware communication errors
• Self-test results

**Log Entry Format:**
Each safety_log entry includes:
```
{
  "timestamp": "2025-10-15T14:32:18.472Z",  // Microsecond precision
  "event_type": "photodiode_fault",
  "severity": "critical",
  "description": "Photodiode power mismatch: commanded 5.0W, measured 2.1W (58% deviation)",
  "session_id": 42,
  "tech_id": 3,
  "system_state": "treating",
  "interlock_states": {
    "footpedal": true,
    "smoothing_device": true,
    "photodiode_ok": false,
    "camera_valid": true,
    "session_active": true,
    "e_stop": false
  },
  "laser_power_commanded": 5.0,
  "laser_power_measured": 2.1,
  "photodiode_voltage": 1.05,
  "action_taken": "Immediate laser shutdown, state transition to FAULT"
}
```

**Log Properties:**
• **Immutable** - No updates or deletes permitted on safety_log entries (enforced by database constraints)
• **Comprehensive** - Sufficient information to reconstruct system state at time of event
• **High precision timestamps** - Microsecond resolution for accurate event sequencing
• **Indexed** - Database indexes on timestamp, severity, session_id for efficient querying

---

**IMPLEMENTATION**

The Safety Management module is implemented entirely as In-house Developed Software (IDS) due to its criticality and medical device-specific requirements.

**IDS Components:**
• Hardware interlock monitoring (GPIO digital input reading, ADC sampling, threshold validation, timeout detection)
• Software interlock validation logic (session state checking, power limit enforcement, camera validation)
• Safety state machine implementation (state tracking, transition validation, state-specific behaviors)
• Fault classification and response procedures (fault source identification, appropriate response selection)
• Emergency shutdown command prioritization (highest-priority command path to laser controller)
• Safety event logging (safety_log table interface, comprehensive event data capture)
• Watchdog timer (separate monitoring thread, timeout detection, emergency shutdown trigger)
• Recovery procedure guidance (fault-type-specific instructions for operators)

**OTS Components:**
• Adafruit libraries (board, busio, digitalio, analogio) for FT232H GPIO/ADC hardware interface
• Threading library (Python standard library) for watchdog timer thread

**Module Structure:**
```
src/core/safety_manager.py (main module)
├── FootpedalInterlock class
├── SmoothingDeviceInterlock class
├── PhotodiodeMonitor class
├── EmergencyStop class
├── PowerLimitEnforcer class
├── SessionInterlock class
├── CameraInterlock class
├── SafetyStateMachine class
├── FaultHandler class
└── SafetyWatchdog class
```

---

**VERIFICATION & VALIDATION**

Safety Management module receives the most rigorous verification and validation due to its criticality:

**Unit Testing:**
• Each interlock class tested independently with pass and fail scenarios
• State machine transitions tested for all valid and invalid transitions
• Fault classification tested with all fault types
• Watchdog timer tested for timeout detection and false trigger prevention
• Power limit enforcement tested at boundaries and out-of-range values

**Integration Testing:**
• Multi-interlock scenarios (e.g., photodiode fault during footpedal release)
• Safety Manager coordination with Laser Control (command validation, shutdown execution)
• Safety Manager coordination with GUI (status display, fault notification)
• Database logging under high event rate (no event loss)

**Performance Testing:**
• Interlock monitoring rate verified ≥100 Hz
• Shutdown response time measured from fault detection to laser power = 0 (target: <100 milliseconds)
• Watchdog timeout accuracy verified
• Control loop timing under various system loads

**Failure Mode Testing (FMEA-driven):**
• Simulated hardware faults:
  - Footpedal cable disconnect
  - Smoothing device power loss
  - Photodiode cable disconnect
  - FT232H USB disconnect
  - Camera USB disconnect
• Simulated software faults:
  - Control loop hang (infinite loop injection)
  - Memory corruption
  - Exception in critical code path
• Multi-fault scenarios:
  - Multiple simultaneous faults
  - Cascading faults (one fault triggering secondary failures)
  - Fault during recovery from previous fault

**Safety Requirements Traceability:**
All Safety Management requirements (from Software Requirements Specification) traced to:
• Design elements (in Software Design Specification)
• Test cases (in Software Verification & Validation Plan)
• Risk controls (in Risk Management File)

**Test Documentation:**
All test protocols, test results, pass/fail criteria, and traceability matrices documented in Software Verification & Validation Plan (separate document) and maintained in Design History File (DHF).

**Acceptance Criteria:**
• All unit tests pass (100% pass rate required)
• All integration tests pass
• All shutdown response times <100 milliseconds
• All state machine transitions behave as specified
• All fault scenarios result in safe state (laser disabled)
• Watchdog timer detects control loop hangs within timeout period
• Zero events lost during logging stress test
• Independent safety review approval

---

**SUMMARY**

The Safety Management module implements a comprehensive, multi-layered safety architecture with:
• **Three hardware interlocks** (footpedal, smoothing device, photodiode) monitored continuously at high frequency
• **Four software interlocks** (emergency stop, power limits, session state, camera feed) validated before each laser command
• **Fail-safe design** where any fault or uncertainty results in laser disabled
• **Immediate response** to faults (target <100 milliseconds shutdown time)
• **Independent monitoring** (watchdog timer) for software failure detection
• **Complete audit trail** through immutable safety event logging
• **Formal state machine** preventing unsafe system configurations

This module represents the highest software risk and receives the most rigorous verification, validation, and regulatory scrutiny. All design decisions prioritize safety over convenience, performance, or functionality.

### 1.3.10 Logging and Reporting (Data Recording)

This module records comprehensive system operations, device performance data, and treatment parameters for regulatory compliance, troubleshooting, quality assurance, and clinical documentation. The module generates standardized reports for clinical review and service activities.

**Two-Tier Logging Architecture:**

The module implements a two-tier logging architecture optimized for both real-time control loop performance and regulatory compliance:

**High-Frequency Data (10-100 Hz):**
During active treatment, time-critical data is buffered to JSON files in the session folder to avoid database I/O latency impacting the real-time control loop (which operates on a 10 millisecond cycle time):
• Photodiode voltage readings (sampled at 100 Hz)
• Laser power commands (every command change logged)
• Actuator position (sampled at 10 Hz)
• All interlock states (footpedal, smoothing device, camera valid - sampled at 100 Hz)
• Frame timestamps from camera (30 Hz)

JSON files are organized by data type and timestamped:
```
data/sessions/session_20251015_143210_042/
├── photodiode_log.json
├── laser_commands.json
├── interlock_states.json
└── camera_timestamps.json
```

Each JSON entry includes timestamp and data:
```json
{"timestamp": "2025-10-15T14:32:18.472Z", "voltage": 2.51, "power_watts": 5.02}
```

**Event-Based Data:**
Significant events are written immediately to SQLite database for real-time access and display:
• Protocol step transitions (step start/end, step number, parameters)
• Power level changes (commanded power, reason for change)
• Ring size adjustments (target ring size, actuator position)
• Safety events and faults (all safety-related events logged immediately)
• User actions and commands (pause, resume, emergency stop, protocol modifications)
• System state changes (state machine transitions)

Immediate database logging of safety events ensures that even if treatment session is interrupted or system fails, safety event records are preserved.

**Post-Session Processing:**
After treatment session completion, high-frequency JSON data files are parsed and imported into the database treatment_events table for long-term storage, analysis, trending, and regulatory audit trail. Import process validates data integrity, checks for timestamp gaps, and associates all data with session_id. Original JSON files are retained as backup.

**Separate Safety Log:**
The safety_log table (Section 1.3.4) maintains an immutable record of all safety-related events with highest integrity requirements:
• No updates or deletes permitted (enforced by database schema and access controls)
• Foreign key constraints enforced for data integrity
• Automatic timestamp generation at database level
• Separate from operational logs to ensure safety data isolation

**Report Generation:**
The module generates standardized reports:
• **Session Summary Report** - Treatment parameters, duration, energy delivered, any deviations, operator notes
• **Safety Event Report** - All safety events for a session or date range, for quality review
• **Device Performance Report** - System uptime, fault frequency, calibration status, for service planning
• **Patient Treatment History** - All sessions for a patient, for longitudinal clinical assessment

**Implementation:** IDS with structured logging framework, JSON file writing and parsing, database import procedures, and report generation templates. Uses Python logging library for application-level logs (separate from treatment data logs).

**Verification:**
• Logging performance tested under high data rate (100 Hz sustained) without frame loss
• JSON file integrity verified (valid JSON syntax, complete records)
• Database import accuracy validated (JSON data matches database after import)
• Timestamp consistency verified across all logging tiers
• Report generation tested for accuracy and completeness

### 1.3.11 Error Handling (Fault Management)

This module provides centralized error detection, classification, and recovery mechanisms for non-safety-critical errors (safety-critical faults are handled by Safety Management module, Section 1.3.9). The module implements graceful degradation strategies to maintain safe operation when possible and coordinates error reporting and system recovery procedures across all modules.

**Error Classification:**
• **Critical** - Errors preventing safe system operation, requiring immediate shutdown (escalated to Safety Management)
• **Major** - Errors preventing treatment but not posing immediate safety risk (e.g., database write failure, video recording failure)
• **Minor** - Errors degrading functionality but allowing operation (e.g., report generation failure, non-critical sensor unavailable)
• **Informational** - Issues requiring logging but no action (e.g., transient communication retry, GUI element rendering delay)

**Error Sources:**
• Hardware communication errors (serial timeout, USB disconnect, GPIO read failure)
• Database errors (write failure, disk full, corruption detection)
• File system errors (disk full, permission denied, file not found)
• Software errors (unexpected exceptions, validation failures, resource exhaustion)

**Error Response Strategy:**
1. **Detection** - Error condition identified (exception caught, validation failed, timeout occurred)
2. **Classification** - Error severity determined based on impact to safety and functionality
3. **Immediate Response** - For critical errors, escalate to Safety Management; for others, execute appropriate mitigation
4. **Logging** - Error details logged to application log and database (if database accessible)
5. **User Notification** - Error presented to operator with appropriate severity indication and guidance
6. **Recovery** - Automatic recovery attempted if safe (e.g., communication retry); otherwise, operator guidance provided
7. **Graceful Degradation** - If full functionality cannot be restored, system continues in degraded mode if safe

**Graceful Degradation Examples:**
• If video recording fails (disk full, codec error), treatment can continue but operator is notified that video will not be available
• If actuator communication fails, treatment can continue at fixed ring size (if safe), but ring size adjustment is disabled
• If report generation fails, session data is preserved and report can be regenerated later

**Coordination with Safety Management:**
Error Handler coordinates with Safety Management for critical errors:
• Hardware communication failures affecting safety interlocks → escalated to Safety Management for immediate shutdown
• Database write failures during treatment → session data buffered, treatment continues if safe, operator notified
• GUI errors → treatment continues (GUI is display-only, not control), operator notified, GUI restart attempted

**Implementation:** IDS with comprehensive error management framework including exception handling, error classification logic, retry mechanisms, user notification, and recovery procedures. Coordinates with all other modules via error reporting interface.

**Verification:**
• Error detection tested with fault injection (simulated errors in all categories)
• Error classification validated for correct severity assignment
• Recovery mechanisms tested for effectiveness (automatic recovery when appropriate)
• Escalation to Safety Management tested for critical errors
• User notifications tested for clarity and appropriate guidance

---

## 1.4 Risk Management File

The Risk Management File (RMF) is a separate document addressing risks in the complete TOSCA system, including but not limited to software risks. The RMF follows ISO 14971 (Medical Devices - Application of Risk Management to Medical Devices) and includes:
• Hazard identification
• Risk analysis (severity and probability estimation)
• Risk evaluation (acceptability determination)
• Risk control measures (design controls, protective measures, information for safety)
• Residual risk evaluation
• Risk management report

Software-related risks documented in the RMF include:
• Laser power control errors (excessive power, incorrect duration, unintended emission)
• Interlock failures (footpedal malfunction, photodiode measurement error, smoothing device failure undetected)
• User interface errors (incorrect parameter display, misleading status information)
• Data integrity risks (treatment log corruption, calibration data loss)
• Cybersecurity risks (unauthorized access, malware, data tampering)

Risk controls implemented in software are traceable from RMF to Software Requirements Specification (SRS) to Software Design Specification (SDS) to verification test cases.

**Reference:** Risk Management File [Document Number TBD]

## 1.5 Software Requirements Specification

The Software Requirements Specification (SRS) describes the needs and expectations for the software, presented in an organized format at the software level, with sufficient information to understand traceability with respect to other software documentation elements (Product Requirements Document, Risk Management File, Software Design Specification, architecture diagrams, etc.).

The SRS includes:
• Functional requirements (what the software shall do)
• Performance requirements (timing, throughput, response time)
• Interface requirements (hardware interfaces, software interfaces, user interfaces)
• Safety requirements (interlock monitoring, fault response, shutdown timing)
• Security requirements (access control, audit trail, data protection)
• Reliability requirements (availability, error rates, recovery time)

Requirements are organized by module (corresponding to Section 1.3 architecture) and are uniquely identified (e.g., REQ-SAFETY-001, REQ-LASER-015) for traceability.

Each requirement is traced to:
• Source (Product Requirement, Risk Control, Regulatory Requirement, Standard)
• Design element (which software module and function implements this requirement)
• Verification method (test case, inspection, analysis)
• Risk control (which risk this requirement mitigates, if applicable)

**Status:** Separate document in development. Draft will be prepared for review and refinement.

**Reference:** Software Requirements Specification [Document Number TBD]

## 1.6 Software Architecture Design

The software architecture is documented in Section 1.3 above (Software Description). Figure 1 provides the system-level block diagram showing all major software modules and their interconnections. Section 1.3 subsections provide detailed descriptions of each module's purpose, functions, implementation approach (OTS vs. IDS), and verification strategy.

The architecture follows a layered design pattern:
• **User Interface Layer** (GUI, Monitoring & Alerting) - Operator interaction and information display
• **Application Logic Layer** (Session Control, Safety Management, Error Handling) - Treatment orchestration and safety oversight
• **Device Control Layer** (Laser Control, Actuator Control, Camera & Image Processing, GPIO Interlocks) - Hardware interfaces
• **Data Management Layer** (Database, Logging & Reporting) - Persistent storage and audit trail

The Safety Management module is architecturally positioned with override authority over treatment delivery, reflecting its highest-priority role in the system.

Detailed software architecture diagrams including class diagrams, sequence diagrams, and state machine diagrams are provided in the Software Design Specification (Section 1.7).

## 1.7 Software Design Specification

The Software Design Specification (SDS) presents sufficient information to allow FDA reviewers to understand the technical design details of how the software functions, and how the software design traces to the Software Requirements Specification in terms of intended use, functionality, safety, and effectiveness.

The SDS includes:
• Detailed design for each software module
• Class diagrams (object-oriented structure)
• Sequence diagrams (module interactions for key use cases)
• State machine diagrams (safety state machine, session state machine, treatment protocol state machine)
• Data flow diagrams (treatment data, safety data, audit trail data)
• Interface specifications (APIs between modules, hardware interface protocols, database schema)
• Algorithm descriptions (ring detection, focus measurement, power interpolation, calibration curve fitting)
• Error handling designs (fault detection, classification, recovery procedures)

Design elements are traced to requirements (from SRS) using unique identifiers. This traceability ensures that all requirements are implemented and all design elements serve a specified requirement.

The SDS emphasizes safety-critical designs:
• Safety Management module detailed design (interlock monitoring loops, fault response sequences, state machine implementation)
• Laser Control command validation (pre-execution safety checks, power limit enforcement)
• Photodiode monitoring algorithm (calibration curve application, threshold evaluation, fault detection timing)
• Emergency shutdown sequences (command prioritization, execution timing, verification)

**Status:** Separate document in development. Draft will be prepared for review and refinement.

**Reference:** Software Design Specification [Document Number TBD]

## 1.8 Software Development, Configuration Management, and Maintenance Practices

ALeyeGN's software development process follows IEC 62304 (Medical Device Software - Software Life Cycle Processes) and is aligned with 21 CFR § 820.30 (FDA Design Controls). The development lifecycle includes the following activities:

### Software Development Activities

**1. Requirements**
• Develop Software Requirements Specification (SRS, Section 1.5)
• Requirements derived from Product Requirements Document, Risk Management File, standards (IEC 60601-1, IEC 60601-2-22), and regulatory requirements
• Requirements reviewed and approved before proceeding to design
• Requirements baseline established and placed under configuration control

**2. Design**
• Develop Software Design Specification (SDS, Section 1.7) based on SRS
• Architecture design (Section 1.3) defines module structure and interfaces
• Detailed design specifies algorithms, data structures, and module implementations
• Design reviews conducted for completeness, correctness, and traceability to requirements
• Design baseline established and placed under configuration control

**3. Implementation (Coding & Unit Testing)**
• Software modules coded per design specifications
• Coding standards applied (PEP 8 for Python code style, naming conventions, documentation requirements)
• Peer code reviews conducted for quality and compliance with standards
• Unit tests developed and executed for each module (target: ≥80% code coverage)
• Unit test results documented and reviewed
• Static analysis tools applied (linters, type checkers) to identify potential defects

**4. Integration**
• Software modules integrated according to integration plan (bottom-up approach, hardware abstraction layer first, then safety systems, then application logic, then UI)
• Integration testing validates module interfaces and coordination
• Integration issues documented, resolved, and retested

**5. System Testing (Verification)**
• System-level verification tests executed per Software Verification & Validation Plan
• Tests verify that software implements all requirements correctly
• Tests include:
  - Functional testing (all features, all use cases)
  - Performance testing (timing, throughput, response time)
  - Safety testing (interlock function, fault response, shutdown timing)
  - Usability testing (human factors evaluation)
  - Robustness testing (error handling, boundary conditions, stress testing)
• Test results documented with pass/fail determination
• Requirements traceability matrix updated showing all requirements verified

**6. Validation**
• System-level validation tests executed in clinically representative environment
• Validation demonstrates that the complete TOSCA device (hardware + software) meets user needs and intended use
• Validation includes clinical workflow simulation with representative users (clinicians)
• Validation tests cover normal use, edge cases, and use errors
• Validation results documented and reviewed

**7. Release**
Every major software release must be accompanied by the following documentation:

a. **Scope & Purpose**
   - What the release covers (new features, bug fixes, enhancements)
   - Intended use and any limitations
   - Differences from previous release

b. **Roles & Responsibilities**
   - Who develops, reviews, approves (names and titles)
   - Release approval authority (Engineering Manager, Quality Manager, Regulatory Affairs)

c. **Release Identification**
   - Version number (semantic versioning: MAJOR.MINOR.PATCH)
   - Baseline reference (Git commit hash, tag)
   - Build identifier and build date
   - Configuration identification (which requirements version, design version, test plan version)

d. **Contents**
   - Features included in this release
   - Bug fixes (with issue tracking IDs)
   - Known issues and limitations
   - Resolved issues from previous releases

e. **Verification & Validation**
   - Test summary (number of tests executed, passed, failed)
   - Traceability to requirements (requirements verification matrix)
   - Anomalies and their resolution
   - Regression testing results (verification that previous functionality still works)

f. **Risk Management**
   - Updated Risk Management File (if changes affect risks)
   - Residual risk acceptability assessment
   - New risks identified and controlled

g. **Configuration & Change Control**
   - List of approved change requests included in this release
   - Software packaging and archiving procedures
   - Software Bill of Materials (SBOM) - list of all OTS components and versions

h. **Deployment & Distribution**
   - Software delivery method (USB drive, download, service technician installation)
   - Supported platforms (Windows 10, specific hardware configuration)
   - Installation procedure and installation verification
   - Rollback plan (procedure to revert to previous version if needed)

i. **Post-Market & Maintenance**
   - Anomaly tracking plan (how issues are reported and tracked)
   - Patching procedures (how urgent fixes are deployed)
   - User feedback loop (how customer feedback is collected and addressed)
   - Next release planning

j. **Approvals**
   - Signatures from Development Lead, Quality Assurance Manager, Regulatory Affairs, Management
   - Date of approval
   - Approval recorded in Design History File

**8. Maintenance**
Ongoing software maintenance activities include:
• **Anomaly tracking** - Issues reported from field use logged, prioritized, and resolved
• **Patches** - Urgent bug fixes released as patch versions (X.Y.Z where Z increments)
• **Updates** - Enhancements and non-urgent fixes released as minor versions (X.Y.Z where Y increments)
• **Major releases** - Significant new features or architectural changes released as major versions (X.Y.Z where X increments)
• **Obsolescence management** - OTS component versions monitored for end-of-life, replacements planned

### Configuration Management

**Source Code Management:**
• Source code maintained in Git version control system
• Repository hosted on [GitHub / GitLab / internal server - TBD]
• Branch strategy:
  - `main` branch: Production-ready code, always stable
  - `develop` branch: Integration branch for ongoing development
  - Feature branches: `feature/description` for new features
  - Bugfix branches: `bugfix/description` for bug fixes
  - Release branches: `release/version` for release candidates
• Commit messages follow standardized format (issue ID, description, change type)
• Pull requests required for all changes, with code review approval before merge
• Tags mark all releases: `v1.0.0`, `v1.0.1`, `v1.1.0`, etc.

**Artifact Management:**
• Compiled/built software (binaries, executables, installers) maintained in secure artifact repository
• Each release archived with:
  - Executable files
  - Installation package
  - Release documentation
  - Verification test results
  - Configuration identification (source code commit hash)
• Only current approved release available for production device builds
• Previous releases archived for traceability and potential rollback

**Configuration Control:**
• All controlled documents (SRS, SDS, test plans, etc.) versioned and tracked
• Document changes follow change control procedure:
  1. Change request submitted and reviewed
  2. Impact assessment (what else is affected by this change?)
  3. Approval by Change Control Board
  4. Implementation and verification
  5. Documentation updated
  6. Change closed with verification evidence
• Configuration audits conducted before each release to verify:
  - All design inputs properly documented
  - All design outputs traceable to inputs
  - All changes properly approved and implemented
  - All verification activities completed

**Traceability:**
• Requirements traceability matrix maintains linkages:
  - Product Requirement → Software Requirement → Design Element → Test Case → Risk Control
• Traceability ensures:
  - All requirements implemented (forward traceability)
  - All design elements serve a requirement (backward traceability)
  - All risk controls verified (risk traceability)

### Quality Management System Integration

Software development activities are integrated into ALeyeGN's QMS:
• Software development follows QMS procedures (document control, change control, design control)
• Design reviews conducted at requirements, design, and pre-release milestones
• Software development records maintained in Design History File (DHF)
• Software anomalies tracked in QMS issue tracking system
• Software release records maintained in Device Master Record (DMR)
• Software verification and validation results maintained in DHF
• Software changes undergo change control with impact assessment and approval

### Tools and Environment

**Development Tools:**
• Programming language: Python 3.10+
• IDE: Visual Studio Code or PyCharm
• Static analysis: pylint, mypy (type checking)
• Unit testing: pytest framework
• Code coverage: pytest-cov
• Documentation: Sphinx (API documentation generation)

**Build and Deployment:**
• Build automation: Python setuptools / PyInstaller for executable generation
• Continuous integration: [Jenkins / GitHub Actions / GitLab CI - TBD] for automated build and test
• Installer creation: Inno Setup or NSIS for Windows installer package
• Installation validation: Automated tests verify correct installation

**Development Environment:**
• Operating system: Windows 10 development machines
• Hardware: Development systems with representative hardware (camera, GPIO controllers, actuator - or simulators)
• Test fixtures: Hardware simulators for interlock testing, calibrated test equipment for verification

---

## Summary

This Software Development section documents TOSCA's software architecture, development process, and compliance with IEC 62304 and FDA Enhanced Documentation Level requirements. The software implements a comprehensive safety architecture with multiple hardware and software interlocks, fail-safe design principles, and complete audit trail for regulatory compliance.

The safety-critical nature of TOSCA software is recognized through Enhanced Documentation Level, extensive safety interlock monitoring, formal safety state machine, immediate fault response (<100 milliseconds), and rigorous verification and validation activities.

All software development activities are conducted under ALeyeGN's Quality Management System with full configuration management, traceability, change control, and Design History File documentation as required for medical device regulatory submissions.

---

**Document Control:**
• **Document Title:** TOSCA Product Development Plan - Section 1: Software Development
• **Document Number:** [TBD]
• **Version:** 2.0
• **Date:** 2025-10-15
• **Prepared by:** Will [Last Name], Systems Architect
• **Reviewed by:** [Regulatory Affairs, Quality Assurance - TBD]
• **Approved by:** [Engineering Manager, Quality Manager - TBD]
• **Next Review Date:** [Upon completion of Phase 1 development, or within 90 days]

---

**Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original Date] | [Original Author] | Initial document for FDA Pre-Sub |
| 2.0 | 2025-10-15 | Will [Last Name] | Complete rewrite with detailed architecture: Added Camera & Image Processing section (1.3.3), comprehensive Safety Management expansion (1.3.9), actuator control detail (1.3.5), hardware interlock specifications (footpedal, smoothing device, photodiode), safety state machine, fault handling procedures, two-tier logging architecture, updated block diagram reflecting hardware safety interlocks and module relationships |

---

**End of Section 1: Software Development**
