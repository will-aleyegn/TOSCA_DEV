# Laser Control - Manufacturer Documentation

**Last Updated:** 2025-10-25
**Hardware:** Arroyo Instruments Laser Driver and TEC Controller
**Communication:** Serial (38400 baud, ASCII commands)
**Model:** 4320 Series

---

## Folder Structure

```
manufacturer_docs/
├── README.md                           (this file)
├── arroyo_manuals/                    Arroyo PDF manuals
│   ├── Arroyo_4320_Manual.pdf         (851 KB - device manual)
│   └── ArroyoComputerInterfacingManual.pdf (1.3 MB - programming guide)
│
└── arroyo_sdk/                        Official Python SDK
    ├── arroyo_tec/                    Python package
    └── ARROYO_SDK_README.md           SDK usage guide
```

---

## Quick Reference

**For hardware specifications:**
→ Read `arroyo_manuals/Arroyo_4320_Manual.pdf`

**For programming/serial commands:**
→ Read `arroyo_manuals/ArroyoComputerInterfacingManual.pdf`

**For Python API:**
→ Read `arroyo_sdk/ARROYO_SDK_README.md`

---

## Arroyo Manuals

### Arroyo_4320_Manual.pdf (851 KB)
**Purpose:** Complete device operation manual
**Contents:**
- Hardware specifications
- Front panel operation
- Laser driver specifications
  - Current range: 0-2000 mA
  - Current resolution: 0.1 mA
- TEC controller specifications
  - Temperature control
  - Temperature monitoring
- Safety features and interlocks
- Installation and setup
- Troubleshooting

**Use when:** Understanding hardware capabilities, front panel operation, specifications

---

### ArroyoComputerInterfacingManual.pdf (1.3 MB)
**Purpose:** Programming and computer interface guide
**Contents:**
- Serial communication protocol
- ASCII command set
- Command syntax and responses
- Current control commands
- TEC control commands
- Status query commands
- Error codes and handling
- Example programs

**Key Command Categories:**

#### Laser Current Control
- `LAS:SET:CURRent <value>` - Set laser current (mA)
- `LAS:CURRent?` - Query current setpoint
- `LAS:LDI?` - Query actual laser current
- `LAS:OUT <0|1>` - Enable/disable laser output

#### TEC Control
- `TEC:SET:TEMPerature <value>` - Set temperature (°C)
- `TEC:TEMPerature?` - Query temperature setpoint
- `TEC:T?` - Query actual temperature
- `TEC:OUT <0|1>` - Enable/disable TEC

#### Status Queries
- `*IDN?` - Identify device
- `LAS:LIM:CURRent?` - Query current limit
- `TEC:LIM:TEMPerature?` - Query temperature limits
- `SYSTem:ERRor?` - Query error status

**Use when:** Implementing serial control, writing custom software, debugging communication

---

## Python SDK

### arroyo_sdk/arroyo_tec/
**Purpose:** Official Arroyo Instruments Python SDK
**Source:** https://github.com/arroyo (SDK from manufacturer)

**Key Components:**

#### ArroyoController Class
Main class for laser/TEC control

**Initialization:**
```python
from arroyo_tec import ArroyoController

controller = ArroyoController(port='COM4', baudrate=38400)
controller.connect()
```

**Current Control:**
```python
# Set laser current
controller.set_laser_current(1500.0)  # 1500 mA

# Query current
current = controller.get_laser_current()

# Enable/disable output
controller.enable_laser_output(True)
controller.enable_laser_output(False)
```

**TEC Control:**
```python
# Set temperature
controller.set_tec_temperature(25.0)  # 25°C

# Query temperature
temp = controller.get_tec_temperature()

# Enable/disable TEC
controller.enable_tec(True)
```

**Status Queries:**
```python
# Get device info
info = controller.get_device_info()

# Query limits
current_limit = controller.get_current_limit()
temp_limits = controller.get_temperature_limits()

# Check errors
errors = controller.get_errors()
```

---

## Common Use Cases

### Use Case 1: Laser Current Control
**Documentation:** ArroyoComputerInterfacingManual.pdf (Current commands)
**SDK:** `ArroyoController.set_laser_current()`
**Example:** Basic current control with limits enforcement

### Use Case 2: TEC Temperature Control
**Documentation:** ArroyoComputerInterfacingManual.pdf (TEC commands)
**SDK:** `ArroyoController.set_tec_temperature()`
**Example:** Temperature setpoint with monitoring

### Use Case 3: Safe Laser Enable/Disable
**Documentation:** Arroyo_4320_Manual.pdf (Safety section)
**SDK:** `ArroyoController.enable_laser_output()`
**Example:** Enable with interlocks verification

### Use Case 4: Status Monitoring
**Documentation:** ArroyoComputerInterfacingManual.pdf (Status queries)
**SDK:** Status query methods
**Example:** Real-time monitoring loop

---

## Integration with TOSCA

### Where This is Used

**Production code:**
- `src/hardware/laser_controller.py` - Main laser HAL implementation
- Uses serial communication with Arroyo protocol
- PyQt6 signals for real-time status updates

**GUI code:**
- `src/ui/widgets/laser_widget.py` - Laser control GUI
- Current control, TEC control, output enable
- Status displays

**Documentation:**
- `components/laser_control/README.md` - Module overview
- `components/laser_control/ARROYO_API_REFERENCE.md` - API details

---

## Hardware API Features (Use Native, Not Software)

Per TOSCA Hardware API Usage Rule, ALWAYS use these native features:

**[DONE] Native Features to Use:**
1. **Current Control** - Hardware current regulation (0-2000 mA)
2. **TEC Control** - Hardware temperature control
3. **Safety Interlocks** - Hardware safety features
4. **Current Limiting** - Hardware current limits
5. **Temperature Monitoring** - Hardware temperature sensors
6. **Output Enable/Disable** - Hardware output control

**[FAILED] Don't Implement in Software:**
- Current regulation loops (use `LAS:SET:CURRent`)
- Temperature control loops (use `TEC:SET:TEMPerature`)
- Safety interlocks (use hardware features)
- Current ramping (implement safely if needed, or use hardware)

---

## Important Notes

### Communication Settings
- **Port:** COM4 (typical), configurable
- **Baud Rate:** 38400 (standard)
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None
- **Command Terminator:** `\r\n` (CR+LF)
- **Response Terminator:** `\n` (LF)

### Current Limits
- **Range:** 0 to 2000 mA
- **Resolution:** 0.1 mA
- **Safety:** Never exceed device limits
- **Compliance:** Check laser diode specifications

### Temperature Limits
- **Range:** Device-dependent (query with `TEC:LIM:TEMPerature?`)
- **Resolution:** 0.01°C
- **Safety:** Stay within specified range

### Safety Considerations
- **CRITICAL:** Always verify interlocks before enabling laser
- Check current limits before setting current
- Monitor TEC temperature during operation
- Implement emergency shutdown capability
- Follow laser safety regulations (ANSI Z136, IEC 60825)

---

## Communication Protocol

### Command Format
```
COMMAND<space>VALUE<CR><LF>
```

### Example Commands
```
LAS:SET:CURRent 1500.0<CR><LF>   # Set 1500 mA
LAS:CURRent?<CR><LF>              # Query setpoint
LAS:OUT 1<CR><LF>                 # Enable output
```

### Response Format
```
VALUE<LF>
```

### Error Handling
- Query errors with `SYSTem:ERRor?`
- Parse error codes per manual
- Implement timeout handling (typical: 500ms)

---

## External Resources

**Arroyo Instruments Website:**
- https://www.arroyoinstruments.com/

**Product Support:**
- https://www.arroyoinstruments.com/support/

**Python SDK GitHub:**
- Check manufacturer website for official repository

**Manuals and Downloads:**
- https://www.arroyoinstruments.com/downloads/

---

## Version Information

- **Device Model:** 4320 Series
- **Current Range:** 0-2000 mA
- **Communication Protocol:** ASCII over serial
- **Baud Rate:** 38400
- **SDK:** Official Arroyo Python package

---

## Safety Warnings

WARNING: **LASER SAFETY:**
- This device controls CLASS 3B or CLASS 4 lasers
- Requires proper laser safety training
- Use appropriate safety interlocks
- Follow institutional laser safety protocols
- Wear appropriate laser safety eyewear
- Post appropriate laser warning signs

WARNING: **ELECTRICAL SAFETY:**
- High current device (up to 2A)
- Ensure proper grounding
- Do not exceed current limits
- Monitor for thermal issues

---

**Last Updated:** 2025-10-25
**Location:** components/laser_control/manufacturer_docs/README.md
