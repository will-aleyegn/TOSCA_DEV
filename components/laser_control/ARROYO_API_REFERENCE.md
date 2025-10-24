# Arroyo Instruments Laser Driver API Reference

**Last Updated:** 2025-10-24
**Purpose:** API reference for Arroyo laser driver serial communication

---

## Overview

Arroyo Instruments laser drivers use ASCII text-based serial communication protocol.

**Communication Settings:**
- **Baud Rate:** 38400 (TOSCA standard), 57600, or 115200
- **Data Format:** 8-N-1 (8 data bits, no parity, 1 stop bit)
- **Command Terminator:** CR (`\r`) or LF (`\n`)
- **Case Sensitivity:** Commands are case-insensitive

---

## Device Identification

### Query Device Information

```
*IDN?
```

**Response:** Model number and firmware version
**Example:** `Arroyo Instruments,4320 Laser Diode Driver,12345,v2.0`

---

## Laser Diode Current Control

### Set Laser Current

```
LAS:LDI <value>
```

**Parameters:**
- `value`: Current in Amperes (A)

**Example:**
```
LAS:LDI 0.500    # Set to 500 mA
```

### Query Actual Laser Current

```
LAS:LDI?
```

**Response:** Current in Amperes
**Example:** `0.500` (500 mA)

### Query Laser Current Setpoint

```
LAS:SET:LDI?
```

**Response:** Current setpoint in Amperes
**Example:** `0.500`

### Set Current Limit

```
LAS:LIM:LDI <value>
```

**Parameters:**
- `value`: Maximum current limit in Amperes

**Example:**
```
LAS:LIM:LDI 2.0    # Limit to 2000 mA
```

### Query Current Limit

```
LAS:LIM:LDI?
```

**Response:** Current limit in Amperes
**Example:** `2.0`

---

## Laser Output Control

### Enable/Disable Laser Output

```
LAS:OUT <value>
```

**Parameters:**
- `value`: `1` to enable, `0` to disable

**Example:**
```
LAS:OUT 1    # Enable laser output
LAS:OUT 0    # Disable laser output
```

### Query Output State

```
LAS:OUT?
```

**Response:** `1` (enabled) or `0` (disabled)

---

## TEC Temperature Control

### Set TEC Temperature Setpoint

```
TEC:T <value>
```

**Parameters:**
- `value`: Temperature in Celsius

**Example:**
```
TEC:T 25.0    # Set to 25°C
```

### Query Actual Temperature

```
TEC:T?
```

**Response:** Temperature in Celsius
**Example:** `25.1`

### Query Temperature Setpoint

```
TEC:SET:T?
```

**Response:** Temperature setpoint in Celsius
**Example:** `25.0`

### Set High Temperature Limit

```
TEC:LIM:THI <value>
```

**Parameters:**
- `value`: Maximum temperature in Celsius

**Example:**
```
TEC:LIM:THI 35.0    # Limit to 35°C
```

### Query High Temperature Limit

```
TEC:LIM:THI?
```

**Response:** High temperature limit in Celsius
**Example:** `35.0`

### Set Low Temperature Limit

```
TEC:LIM:TLO <value>
```

**Parameters:**
- `value`: Minimum temperature in Celsius

**Example:**
```
TEC:LIM:TLO 15.0    # Limit to 15°C
```

### Query Low Temperature Limit

```
TEC:LIM:TLO?
```

**Response:** Low temperature limit in Celsius
**Example:** `15.0`

---

## TEC Current and Voltage

### Query TEC Current

```
TEC:ITE?
```

**Response:** Current in Amperes
**Example:** `0.500`

### Query TEC Voltage

```
TEC:V?
```

**Response:** Voltage in Volts
**Example:** `12.5`

---

## Control Mode

### Set Operation Mode

```
TEC:MODE:<mode>
```

**Modes:**
- `T` - Temperature mode
- `R` - Resistance mode
- `ITE` - Current mode

**Example:**
```
TEC:MODE:T    # Set to temperature control mode
```

### Query Operation Mode

```
TEC:MODE?
```

**Response:** `T`, `R`, or `ITE`

---

## PID Control

### Set PID Parameters

```
TEC:PID <P>,<I>,<D>
```

**Parameters:**
- `P`: Proportional gain
- `I`: Integral gain
- `D`: Derivative gain

**Example:**
```
TEC:PID 32.0,0.031,0.0
```

### Query PID Parameters

```
TEC:PID?
```

**Response:** `P,I,D`
**Example:** `32.0,0.031,0.0`

### Set Control Gain

```
TEC:GAIN <value>
```

**Parameters:**
- `value`: `1`, `3`, `5`, `10`, `30`, `50`, `100`, `300`, or `PID`

**Example:**
```
TEC:GAIN PID    # Use PID control
```

### Query Control Gain

```
TEC:GAIN?
```

**Response:** Gain value or `PID`

---

## Safety and Monitoring

### Beep Command

```
BEEP <count>
```

**Parameters:**
- `count`: Number of beeps (1-10)

**Example:**
```
BEEP 1    # Single beep
```

### Query Run Time

```
TIME?
```

**Response:** Time since power-on
**Example:** `01:23:45` (1 hour, 23 minutes, 45 seconds)

---

## TOSCA Integration Commands

### Essential Commands for TOSCA

#### Startup Sequence
```
*IDN?                    # Verify connection
LAS:LIM:LDI 2.0          # Set current limit to 2A
TEC:LIM:THI 35.0         # Set high temp limit
TEC:LIM:TLO 15.0         # Set low temp limit
TEC:MODE:T               # Set to temperature mode
TEC:T 25.0               # Set temperature to 25°C
TEC:GAIN PID             # Use PID control
```

#### Power Control
```
LAS:LDI 0.500            # Set laser to 500 mA
LAS:OUT 1                # Enable laser output
```

#### Monitoring (Poll every 500ms)
```
LAS:LDI?                 # Read actual current
TEC:T?                   # Read actual temperature
LAS:OUT?                 # Read output state
```

#### Shutdown Sequence
```
LAS:OUT 0                # Disable laser output
LAS:LDI 0.0              # Set current to zero
```

---

## Error Handling

### Command Response
- **Success:** Command accepted, query returns value
- **Error:** No response or timeout (1 second)
- **Invalid:** May return error code or ignore

### Best Practices
1. **Always verify:** After setting, query to confirm
2. **Check limits:** Verify setpoint is within device limits
3. **Timeout handling:** Wait 1 second for response
4. **Graceful shutdown:** Always disable output before disconnect

---

## Python Implementation Example

```python
import serial

# Connect
ser = serial.Serial(
    port='COM4',
    baudrate=38400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1.0
)

# Send command
def write_command(command: str) -> str:
    ser.write(str.encode(command) + b'\r\n')
    if '?' in command:
        return ser.readline().decode('utf-8').strip()
    return ''

# Example usage
device_id = write_command('*IDN?')
print(f"Connected to: {device_id}")

# Set current
write_command('LAS:LDI 0.500')

# Verify
actual_current = write_command('LAS:SET:LDI?')
print(f"Current set to: {actual_current} A")

# Enable output
write_command('LAS:OUT 1')

# Read current
current = write_command('LAS:LDI?')
print(f"Actual current: {current} A")

# Disable and close
write_command('LAS:OUT 0')
ser.close()
```

---

## Common Units

| Parameter | Unit | Example |
|-----------|------|---------|
| Current | Amperes (A) | `0.500` = 500 mA |
| Temperature | Celsius (°C) | `25.0` = 25°C |
| Voltage | Volts (V) | `12.5` = 12.5V |
| Time | Seconds (s) | `1.5` = 1.5 seconds |

---

## Device Limits (Model Dependent)

Check your specific device manual for actual limits:

- **Laser Current:** 0 - 2000 mA (typical)
- **TEC Temperature:** 0 - 50°C (typical)
- **TEC Current:** 0 - 10 A (typical)

---

## References

- **Computer Interfacing Manual:** `arroyo_laser_control/ArroyoComputerInterfacingManual.pdf`
- **Device Manual:** `arroyo_laser_control/Arroyo_4320_Manual.pdf`
- **GitHub API:** https://github.com/ArroyoInst/arroyo_tec
- **TOSCA Implementation:** `src/hardware/laser_controller.py`

---

**Note:** This reference covers the most common commands. See the full Computer Interfacing Manual for complete command set including advanced features like auto-tune, sensor constants, and modulation.
