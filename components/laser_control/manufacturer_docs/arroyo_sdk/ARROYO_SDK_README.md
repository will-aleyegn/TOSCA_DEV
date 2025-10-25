# Arroyo Instruments Laser Control Resources

Downloaded: 2025-10-24

## Contents

### 1. Documentation

#### ArroyoComputerInterfacingManual.pdf (1.3 MB)
- **Official serial communication API documentation**
- RS232 serial interface specification
- Command syntax and protocol
- Baud rates up to 115k baud
- Compatible with ILX and Newport laser diode drivers
- Case-insensitive command set
- Virtual serial port usage guide

#### Arroyo_4320_Manual.pdf (851 KB)
- User manual for Arroyo 4320 Laser Diode Driver
- Complete device specifications
- Operating procedures
- Safety information
- Hardware configuration

### 2. Python SDK

#### arroyo_tec/ (GitHub Repository)
- **Official Arroyo Instruments Python API**
- Source: https://github.com/ArroyoInst/arroyo_tec
- Files:
  - `serial_interface.py` - Main API class for TEC controller communication
  - `example_script.py` - Usage examples
  - `README.md` - Repository documentation

**Features:**
- Serial communication wrapper
- Read/write device settings
- Temperature control
- Status monitoring
- Python class-based interface

## Quick Start

### Using the Python API

```python
from arroyo_tec.serial_interface import ArroyoTEC

# Connect to TEC controller
tec = ArroyoTEC(port='COM3', baudrate=38400)

# Read temperature
temp = tec.read_temperature()

# Set target temperature
tec.set_temperature(25.0)
```

### Serial Communication Protocol

Based on `ArroyoComputerInterfacingManual.pdf`:

- **Baud Rate:** 38400, 57600, or 115200 (configurable)
- **Data Format:** 8-N-1 (8 data bits, no parity, 1 stop bit)
- **Command Format:** ASCII text commands
- **Command Terminator:** Carriage return (CR) or line feed (LF)
- **Case Insensitive:** Commands accept uppercase or lowercase

### Common Commands

```
LAS:LDI?        - Query laser diode current
LAS:LDI <value> - Set laser diode current (mA)
LAS:OUT <0|1>   - Enable/disable laser output
TEC:T?          - Query TEC temperature
TEC:T <value>   - Set TEC temperature (°C)
```

See `ArroyoComputerInterfacingManual.pdf` for complete command reference.

## TOSCA Integration Notes

### Hardware Configuration
- **Device:** Arroyo laser driver and TEC controller
- **Interface:** Serial (RS232/USB virtual COM port)
- **Default Baud:** 38400 (TOSCA standard)
- **Protocol:** ASCII text commands

### Integration Steps
1. Install pyserial: `pip install pyserial`
2. Reference `serial_interface.py` for API patterns
3. Implement laser controller HAL following camera controller pattern
4. Use command set from `ArroyoComputerInterfacingManual.pdf`

### Key API Features Needed
- Connect/disconnect
- Set laser current (mA)
- Set laser power (mW)
- Enable/disable output
- Read status
- Monitor temperature
- Safety interlocks

## Resources

- **Official Website:** https://www.arroyoinstruments.com/
- **Download Center:** https://www.arroyoinstruments.com/download-center/
- **GitHub API:** https://github.com/ArroyoInst/arroyo_tec
- **Support:** Arroyo Instruments technical support

## File Sizes
- ArroyoComputerInterfacingManual.pdf: 1.3 MB
- Arroyo_4320_Manual.pdf: 851 KB
- arroyo_tec repository: ~20 KB (Python source)

## Next Steps for TOSCA

1. Review `ArroyoComputerInterfacingManual.pdf` for command set
2. Study `serial_interface.py` for API patterns
3. Create `src/hardware/laser_controller.py` following actuator controller pattern
4. Implement PyQt6 signals for status updates
5. Add safety interlocks (temperature monitoring, current limits)
6. Test with actual hardware on COM port
