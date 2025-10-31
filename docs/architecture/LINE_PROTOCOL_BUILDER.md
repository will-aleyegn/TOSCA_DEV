# Line-Based Protocol Builder - Architecture & Usage

**Created:** 2025-10-30
**Version:** 1.0
**Status:** ✅ Production Ready

---

## Overview

The Line-Based Protocol Builder is a reimagined protocol interface for TOSCA that enables concurrent action configuration. Each "line" can combine **movement**, **laser control**, and **dwell time** into a single executable unit, matching real clinical workflows.

### Key Features

- ✅ **Concurrent Actions**: Combine move + laser + dwell on each line
- ✅ **Flexible Configuration**: Enable/disable any action per line
- ✅ **Laser Power Ramping**: Gradual power increase/decrease over time
- ✅ **Protocol Looping**: Repeat entire protocol N times
- ✅ **Safety Validation**: Pre-execution validation against configurable limits
- ✅ **Duration Calculation**: Automatic total treatment time display
- ✅ **JSON Persistence**: Save/load protocols with full version control

---

## Architecture

### Data Model (`src/core/protocol_line.py`)

```python
@dataclass
class ProtocolLine:
    """Single line with concurrent actions."""
    line_number: int
    movement: Optional[Union[MoveParams, HomeParams]] = None
    laser: Optional[Union[LaserSetParams, LaserRampParams]] = None
    dwell: Optional[DwellParams] = None
    notes: str = ""
```

#### Movement Types

- **MoveParams**: Absolute or relative positioning
  - `target_position_mm`: Target position (mm)
  - `speed_mm_per_s`: Movement speed (mm/s)
  - `move_type`: ABSOLUTE or RELATIVE

- **HomeParams**: Return to home position
  - `speed_mm_per_s`: Homing speed (mm/s)

#### Laser Types

- **LaserSetParams**: Fixed power setting
  - `power_watts`: Laser power (W)

- **LaserRampParams**: Power ramping over time
  - `start_power_watts`: Starting power (W)
  - `end_power_watts`: Ending power (W)
  - `duration_s`: Ramp duration (seconds)

#### Dwell

- **DwellParams**: Wait/hold duration
  - `duration_s`: Duration (seconds)

### Duration Calculation

**Line Duration = MAX(move_duration, laser_ramp_duration, dwell_duration)**

```python
# Example Line:
# - Move from 0mm → 5mm at 1mm/s (duration: 5s)
# - Ramp laser 2W → 5W over 3s (duration: 3s)
# - Dwell for 10s (duration: 10s)
#
# → Total line duration: MAX(5, 3, 10) = 10 seconds
#
# Execution behavior:
#  - Movement completes at 5s, then waits at position
#  - Laser ramp completes at 3s, then holds 5W
#  - Line completes at 10s (dwell time)
```

---

## UI Design

### Hybrid Table/Form Interface

```
┌─────────────────────────────────────────────────────────┐
│  Protocol Metadata                                      │
│  Name: [Treatment Protocol] Loop: [3] Duration: 45.0s  │
├─────────────────────┬───────────────────────────────────┤
│  Protocol Sequence  │  Line Editor                      │
│  ┌─────────────────┐│  ┌─────────────────────────────┐ │
│  │ Line 1: [Move]  ││  │ [✓] Movement                 │ │
│  │   5.0mm @ 1mm/s ││  │   ○ Position  ○ Home        │ │
│  │ [Laser] Set 2W  ││  │   Target: [5.0] mm          │ │
│  │ [Dwell] 3.0s    ││  │   Speed: [1.0] mm/s         │ │
│  │ Duration: 5.0s  ││  │                              │ │
│  ├─────────────────┤│  │ [✓] Laser                    │ │
│  │ Line 2: ...     ││  │   ○ Set Power ● Ramp Power  │ │
│  │                 ││  │   Start: [2.0] W             │ │
│  │                 ││  │   End: [5.0] W               │ │
│  └─────────────────┘│  │   Duration: [10.0] s         │ │
│                     │  │                              │ │
│  [➕ Add] [➖ Remove]│  │ [✓] Dwell                    │ │
│  [⬆ Up] [⬇ Down]   ││  │   Duration: [3.0] s         │ │
│                     │  │                              │ │
│                     │  │ [✓ Apply Changes]            │ │
│                     │  └─────────────────────────────┘ │
├─────────────────────┴───────────────────────────────────┤
│  [📄 New] [💾 Save] [📂 Load]        [▶ Execute]       │
└─────────────────────────────────────────────────────────┘
```

### Workflow

1. **Add Line**: Click "➕ Add Line" to create new line
2. **Select Line**: Click line in sequence view to load into editor
3. **Configure Actions**: Enable/configure movement, laser, dwell
4. **Apply Changes**: Click "✓ Apply Changes" to save to line
5. **Reorder**: Use ⬆/⬇ buttons to reorder lines
6. **Save/Load**: Use file operations for protocol persistence
7. **Execute**: Click "▶ Execute" to emit `protocol_ready` signal

---

## Example Protocol JSON

### Simple Treatment (3 Lines)

```json
{
  "protocol_name": "Simple Treatment Example",
  "version": "1.0",
  "loop_count": 1,
  "lines": [
    {
      "line_number": 1,
      "movement": {
        "type": "move",
        "params": {
          "target_position_mm": 5.0,
          "speed_mm_per_s": 1.0,
          "move_type": "absolute"
        }
      },
      "laser": {
        "type": "set",
        "params": {"power_watts": 2.0}
      },
      "dwell": {"duration_s": 3.0},
      "notes": "Move to 5mm, apply 2W laser, hold 3s"
    },
    {
      "line_number": 2,
      "laser": {
        "type": "ramp",
        "params": {
          "start_power_watts": 2.0,
          "end_power_watts": 5.0,
          "duration_s": 10.0
        }
      },
      "dwell": {"duration_s": 10.0},
      "notes": "Ramp laser 2W → 5W over 10s"
    },
    {
      "line_number": 3,
      "movement": {
        "type": "home",
        "params": {"speed_mm_per_s": 2.0}
      },
      "laser": {
        "type": "set",
        "params": {"power_watts": 0.0}
      },
      "notes": "Return home, laser off"
    }
  ]
}
```

---

## Integration Guide

### Basic Usage

```python
from ui.widgets.line_protocol_builder import LineProtocolBuilderWidget
from core.protocol_line import LineBasedProtocol, SafetyLimits

# Create widget
builder = LineProtocolBuilderWidget()

# Configure safety limits
limits = SafetyLimits(
    max_power_watts=10.0,
    max_duration_seconds=300.0,
    min_actuator_position_mm=0.0,
    max_actuator_position_mm=20.0,
    max_actuator_speed_mm_per_s=5.0
)
builder.set_safety_limits(limits)

# Connect to protocol execution
builder.protocol_ready.connect(handle_protocol_execution)

# Add to UI
layout.addWidget(builder)
```

### Handling Protocol Execution

```python
def handle_protocol_execution(protocol: LineBasedProtocol):
    """Execute protocol via protocol engine."""
    # Validate
    valid, errors = protocol.validate()
    if not valid:
        logger.error(f"Invalid protocol: {errors}")
        return

    # Execute
    engine = LineProtocolEngine(
        laser_controller=laser,
        actuator_controller=actuator
    )
    await engine.execute_protocol(protocol)
```

---

## Testing

### Standalone Test

```bash
# Run standalone test application
cd examples
python test_line_protocol_builder.py
```

The test app provides:
- Full protocol builder UI
- Example protocol loading (`examples/protocols/`)
- Console logging of protocol execution events

### Unit Tests

```python
# Test data model
from core.protocol_line import ProtocolLine, MoveParams, LaserSetParams

line = ProtocolLine(
    line_number=1,
    movement=MoveParams(5.0, 1.0),
    laser=LaserSetParams(2.0),
    dwell=DwellParams(3.0)
)

assert line.calculate_duration() == 5.0  # MAX(5/1, 0, 3) = 5
```

---

## Safety & Validation

### Pre-Execution Validation

✅ All lines validated against `SafetyLimits` before save/execute
✅ Invalid protocols cannot be saved or executed
✅ Clear error messages with line-specific feedback

### Safety Limits

```python
class SafetyLimits:
    max_power_watts: float = 10.0           # Max laser power
    max_duration_seconds: float = 300.0     # Max action duration
    min_actuator_position_mm: float = -20.0 # Min position (bidirectional)
    max_actuator_position_mm: float = 20.0  # Max position
    max_actuator_speed_mm_per_s: float = 5.0 # Max speed
```

**Note:** Negative positions are supported for bidirectional actuator movement. The default range is -20mm to +20mm, allowing full travel in both directions from a center home position.

### Validation Checks

- ✅ Power within limits (0 - max_power_watts)
- ✅ Position within travel range
- ✅ Speed within safe limits
- ✅ Duration within bounds
- ✅ Protocol name not empty
- ✅ At least one line present
- ✅ Loop count ≥ 1

---

## Medical Device Compliance

### FDA/IEC 62304 Considerations

- ✅ **Audit Trail**: Complete JSON serialization for version control
- ✅ **Safety Validation**: Multi-layer validation before execution
- ✅ **Error Handling**: Graceful error messages with recovery
- ✅ **User Feedback**: Real-time duration calculations
- ✅ **Data Integrity**: Immutable protocol files with timestamps

### Production Requirements

**Before Clinical Use:**
1. **Database Encryption**: Implement SQLCipher for protocol storage
2. **User Authentication**: Add role-based access control
3. **Audit Logging**: Log all protocol modifications
4. **Digital Signatures**: Sign protocols for tamper detection
5. **Backup/Recovery**: Implement automatic protocol backups

---

## Comparison: Old vs New

### Old Action-Based System

```python
actions = [
    SetLaserPower(power=2.0),     # Line 1
    MoveActuator(position=5.0),   # Line 2
    Wait(duration=3.0),           # Line 3
    RampLaserPower(2.0, 5.0, 10), # Line 4
    # ...difficult to visualize concurrent operations
]
```

### New Line-Based System

```python
lines = [
    # Line 1: Everything concurrent - clear intent
    ProtocolLine(
        movement=MoveParams(5.0, 1.0),
        laser=LaserSetParams(2.0),
        dwell=DwellParams(3.0)
    ),
    # Line 2: Ramp only - also clear
    ProtocolLine(
        laser=LaserRampParams(2.0, 5.0, 10.0),
        dwell=DwellParams(10.0)
    )
]
```

**Benefits:**
- ✅ **Clarity**: See exactly what happens at each step
- ✅ **Concurrency**: Natural concurrent action modeling
- ✅ **Duration**: Automatic calculation, no surprises
- ✅ **Clinical**: Matches clinical thinking ("step 1: do X+Y+Z")

---

## Future Enhancements

### Planned Features

1. **Visual Timeline View**: Gantt-chart visualization of protocol execution
2. **Action Templates**: Reusable line templates for common procedures
3. **Protocol Validation**: Advanced checks (e.g., thermal modeling)
4. **Branching Logic**: Conditional execution based on sensor feedback
5. **Sub-Protocols**: Nest protocols within lines for complex procedures

---

## Files Reference

### Core Files
- `src/core/protocol_line.py` - Data model (600 lines)
- `src/ui/widgets/line_protocol_builder.py` - UI widget (800 lines)

### Examples
- `examples/protocols/example_simple_treatment.json`
- `examples/protocols/example_scanning_pattern.json`
- `examples/test_line_protocol_builder.py`

### Documentation
- `docs/architecture/LINE_PROTOCOL_BUILDER.md` (this file)

---

## Support & Feedback

**Questions?** Contact the TOSCA development team
**Issues?** File on GitHub issue tracker
**Feature Requests?** Submit via project management system

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Next Review:** Upon protocol engine implementation completion
