# TOSCA Future Work Items

**Purpose:** Track deferred implementation tasks extracted from code TODOs

**Last Updated:** 2025-10-23

---

## Database Integration

### Event Logging Database Storage
**Status:** Deferred
**Priority:** Medium
**Description:** Implement database storage for event logs
**Current State:** Event logger currently uses file-based logging only
**Related Files:** src/core/event_logger.py:130

### Session Database Persistence
**Status:** Deferred
**Priority:** Medium
**Description:** Save session records to database
**Current State:** Sessions tracked in memory only
**Related Files:** src/core/session.py:209

### Protocol Execution Recording
**Status:** Deferred
**Priority:** Medium
**Description:** Record protocol execution events to database
**Current State:** In-memory tracking only
**Related Files:** src/core/protocol_engine.py:348

---

## Camera Features

### Auto-Record When Laser On
**Status:** Deferred
**Priority:** Low
**Description:** Automatically start video recording when laser is activated
**Current State:** Manual recording only
**Related Files:** src/ui/widgets/camera_widget.py:43

---

## Protocol Builder Features

### Unsaved Changes Prompt
**Status:** Deferred
**Priority:** Low
**Description:** Prompt user to save when loading protocol with unsaved changes
**Current State:** No unsaved changes detection
**Related Files:** src/ui/widgets/protocol_builder_widget.py:378

### Action Type Selection Menu
**Status:** Deferred
**Priority:** Medium
**Description:** Show action type selection menu in protocol builder
**Current State:** Placeholder implementation
**Related Files:** src/ui/widgets/protocol_builder_widget.py:454

### Action Editor Dialog
**Status:** Deferred
**Priority:** Medium
**Description:** Implement action editor dialog for protocol actions
**Current State:** Placeholder implementation
**Related Files:** src/ui/widgets/protocol_builder_widget.py:462

### Protocol Execution Engine
**Status:** Deferred
**Priority:** High
**Description:** Implement protocol execution (Run and Run & Record buttons)
**Current State:** Placeholder implementation
**Related Files:**
- src/ui/widgets/protocol_builder_widget.py:548
- src/ui/widgets/protocol_builder_widget.py:554

---

## Hardware Integration

### Laser Controller Integration
**Status:** Deferred
**Priority:** High
**Description:** Integrate actual laser controller hardware API calls
**Current State:** Placeholder logging only
**Related Files:**
- src/core/protocol_engine.py:207 (set_power)
- src/core/protocol_engine.py:242 (dwell action)
- src/core/protocol_engine.py:375 (emergency stop)

### Actuator Controller Integration
**Status:** Deferred
**Priority:** High
**Description:** Integrate actual actuator controller hardware API calls
**Current State:** Placeholder logging only
**Related Files:** src/core/protocol_engine.py:281

---

## Safety System

### Safety Checks Implementation
**Status:** Deferred
**Priority:** Critical
**Description:** Implement actual hardware safety checks
**Current State:** Placeholder returns True
**Related Files:** src/core/protocol_engine.py:336

---

## Treatment Widget

### Session-Based Treatment Control
**Status:** Deferred
**Priority:** Medium
**Description:** Enable treatment controls based on active session state
**Current State:** Only enabled in dev mode
**Related Files:** src/ui/widgets/treatment_widget.py:136

---

## Notes

- All items were extracted from code TODO comments during code review (2025-10-23)
- Items marked as "Deferred" should be planned in future development cycles
- Critical/High priority items should be scheduled first
- Review this document quarterly to update priorities and status
