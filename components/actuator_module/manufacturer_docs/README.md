# Actuator Module - Manufacturer Documentation

**Last Updated:** 2025-10-25
**Hardware:** Xeryon XLA-5-125-10MU Linear Stage
**Communication:** Serial (9600 baud)
**Library:** Xeryon Python Library

---

## Folder Structure

```
manufacturer_docs/
├── README.md                    (this file)
├── xeryon_manuals/             Xeryon PDF manuals
│   ├── Controller Manual.pdf   (1.8 MB - controller documentation)
│   └── XLA5.pdf                (283 KB - XLA5 stage specifications)
│
└── xeryon_library/             Official Python library
    ├── Xeryon.py               (60 KB - v1.88 official library)
    ├── XeryonDemo.py           Demo script
    └── README.md               Library usage guide
```

---

## Quick Reference

**For hardware specifications:**
→ Read `xeryon_manuals/XLA5.pdf`

**For controller commands:**
→ Read `xeryon_manuals/Controller Manual.pdf`

**For Python API:**
→ Read `xeryon_library/README.md` and `Xeryon.py` source code

---

## Xeryon Manuals

### Controller Manual.pdf (1.8 MB)
**Purpose:** Complete controller command reference
**Contents:**
- Serial communication protocol
- ASCII command set
- Motion control commands
- Position, velocity, acceleration control
- Homing and calibration
- Status and error codes
- Configuration parameters

**Key commands:**
- `P<pos>` - Move to absolute position
- `R<pos>` - Move relative position
- `V<vel>` - Set velocity
- `A<accel>` - Set acceleration
- `D<decel>` - Set deceleration
- `H` - Home the stage
- `S` - Stop motion
- `?` - Query status

**Use when:** Implementing low-level serial control, understanding command protocol

---

### XLA5.pdf (283 KB)
**Purpose:** XLA-5 stage specifications and datasheet
**Contents:**
- Mechanical specifications
- Travel range: 125mm
- Resolution: 10µm
- Speed range: 0.5 to 400 mm/s
- Electrical specifications
- Mounting information
- Dimensions and weight

**Use when:** Understanding hardware capabilities, planning mechanical integration

---

## Xeryon Python Library

### Xeryon.py (60 KB - Version 1.88)
**Purpose:** Official Xeryon Python library for serial communication
**Language:** Python 3.x
**Dependencies:** pyserial

**Key Classes:**

#### XeryonController
Main controller class for communication

**Methods:**
- `__init__(port, baudrate=9600)` - Initialize connection
- `connect()` / `disconnect()` - Connection management
- `move_absolute(position_mm)` - Move to absolute position
- `move_relative(distance_mm)` - Move relative distance
- `set_velocity(velocity_mm_s)` - Set motion velocity
- `set_acceleration(accel)` - Set acceleration
- `set_deceleration(decel)` - Set deceleration
- `home()` - Home the stage
- `stop()` - Emergency stop
- `get_position()` - Query current position
- `is_moving()` - Check if stage is moving

**Example Usage:**
```python
from Xeryon import XeryonController

# Connect
controller = XeryonController(port='COM3', baudrate=9600)
controller.connect()

# Configure motion
controller.set_velocity(100)  # 100 mm/s
controller.set_acceleration(50000)

# Move
controller.move_absolute(50.0)  # Move to 50mm
while controller.is_moving():
    time.sleep(0.1)

# Disconnect
controller.disconnect()
```

---

## Common Use Cases

### Use Case 1: Stage Homing
**Documentation:** Controller Manual.pdf (Homing section)
**Library:** `Xeryon.py` - `home()` method
**Example:** `../examples/01_test_connection.py`

### Use Case 2: Position Control
**Documentation:** Controller Manual.pdf (Position commands)
**Library:** `Xeryon.py` - `move_absolute()`, `move_relative()`
**Example:** `../examples/02_basic_movement.py`

### Use Case 3: Velocity Control
**Documentation:** Controller Manual.pdf (Velocity commands)
**Library:** `Xeryon.py` - `set_velocity()`, `set_acceleration()`
**Example:** `../examples/03_velocity_control.py`

### Use Case 4: Sequence Builder
**Documentation:** Controller Manual.pdf (Sequential commands)
**Library:** Custom implementation
**Example:** `../examples/06_sequence_builder.py`

---

## Integration with TOSCA

### Where This is Used

**Production code:**
- `src/hardware/actuator_controller.py` - Main actuator HAL implementation
- Uses serial communication based on Xeryon.py patterns

**Testing code:**
- `components/actuator_module/examples/` - 6 example scripts
- `components/actuator_module/tests/` - Hardware tests

**Documentation:**
- `components/actuator_module/README.md` - Module overview
- `components/actuator_module/LESSONS_LEARNED.md` - API quirks

---

## Hardware API Features (Use Native, Not Software)

Per TOSCA Hardware API Usage Rule, ALWAYS use these native features:

**✅ Native Features to Use:**
1. **Position Control** - Hardware absolute/relative positioning
2. **Velocity Control** - Hardware velocity profiles (0.5-400 mm/s)
3. **Acceleration/Deceleration** - Hardware profiles (1000-65500)
4. **Homing** - Hardware homing with limit switches
5. **Status Feedback** - Hardware position reporting
6. **Emergency Stop** - Hardware stop command

**❌ Don't Implement in Software:**
- Position control loops (use `P` command)
- Velocity ramping (use `V`, `A`, `D` commands)
- Motion profiling (hardware handles this)

---

## Important Notes

### Communication Settings
- **Port:** COM3 (typical), configurable
- **Baud Rate:** 9600 (standard)
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None

### Motion Limits
- **Travel Range:** 0 to 125 mm
- **Min Velocity:** 0.5 mm/s
- **Max Velocity:** 400 mm/s
- **Acceleration Range:** 1000 to 65500
- **Deceleration Range:** 1000 to 65500

### Safety Considerations
- Always home before precision positioning
- Check position limits before moving
- Implement emergency stop functionality
- Monitor for error codes

---

## External Resources

**Xeryon Website:**
- https://www.xeryon.com/

**Product Page:**
- https://www.xeryon.com/product/xla-linear-actuator/

**Support:**
- Contact Xeryon technical support for questions

---

## Version Information

- **Xeryon Library:** v1.88
- **Controller Firmware:** Check with hardware
- **Stage Model:** XLA-5-125-10MU
- **Travel Range:** 125mm
- **Resolution:** 10µm

---

**Last Updated:** 2025-10-25
**Location:** components/actuator_module/manufacturer_docs/README.md
