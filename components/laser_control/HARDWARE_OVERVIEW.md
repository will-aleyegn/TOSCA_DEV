# TOSCA Laser Control System - Hardware Overview

**Document Version:** 1.0
**Date:** 2025-11-04
**Status:** Production Hardware Configuration
**Last Updated:** Hardware upgrade to SEMINEX dual-wavelength laser system

---

## System Architecture

TOSCA uses a dual-laser system integrated into a single SEMINEX laser unit:

1. **Treatment Laser (1550nm)** - High-power diode laser for therapeutic applications
2. **Aiming Beam** - Integrated low-power laser for alignment and targeting

---

## Component Overview

### 1. SEMINEX Laser Unit (Dual-Wavelength)

**Part Number:** SEMINEX-2CM-004-189

**Description:** Integrated dual-wavelength laser system combining treatment and aiming beams in a single fiber-coupled package.

**Specifications:**
- **Treatment Wavelength:** 1550nm (primary therapeutic beam)
- **Aiming Beam:** Integrated alignment laser
- **Output:** Fiber-coupled
- **Power:** Controlled independently (treatment via Arroyo, aiming via LDD200)

**Documentation:**
- `components/laser_control/seminex_laser_unit/docs/SEMINEX-2CM-004-189-laser-TOSCA.pdf`

---

### 2. Treatment Laser Control System

#### 2.1 Arroyo 6300 Laser Driver

**Function:** Precision current source for 1550nm treatment laser

**Specifications:**
- **Current Range:** 0-5000 mA (configurable max: 2000 mA for safety)
- **Power Control:** Constant current mode
- **Interface:** RS-232 serial @ 38400 baud
- **COM Port:** COM4 (configurable in `config.yaml`)

**Key Features:**
- Programmable current limit
- Built-in laser safety interlocks
- Real-time current/voltage monitoring
- Temperature-dependent power compensation

**Documentation:**
- `components/laser_control/arroyo_drivers/docs/Arroyo4300LaserSourceUsersManual.pdf`
- `components/laser_control/arroyo_drivers/docs/4300-Series-LaserSource-Datasheet.pdf`
- `components/laser_control/arroyo_drivers/docs/ArroyoComputerInterfacingManual.pdf`

**Python Integration:**
- Controller: `src/hardware/laser_controller.py`
- Protocol: Custom serial command set (see Arroyo Computer Interfacing Manual)

---

#### 2.2 Arroyo 5305 TEC Controller

**Function:** Thermoelectric cooler (TEC) temperature stabilization for treatment laser diode

**Specifications:**
- **Temperature Range:** 15-35°C
- **Temperature Stability:** ±0.01°C
- **TEC Current:** Up to 5A
- **Interface:** RS-232 serial @ 38400 baud
- **COM Port:** COM9 (configurable in `config.yaml`)

**Key Features:**
- PID temperature control
- Overheat protection
- Thermistor-based feedback
- Automatic safety shutdown

**Documentation:**
- `components/laser_control/arroyo_drivers/docs/Arroyo5300TECSourceUsersManual.pdf`
- `components/laser_control/arroyo_drivers/docs/5300-Series-TECSource-Datasheet.pdf`
- `components/laser_control/arroyo_drivers/docs/ArroyoComputerInterfacingManual.pdf`

**Python Integration:**
- Controller: `src/hardware/tec_controller.py`
- Protocol: Custom serial command set (see Arroyo Computer Interfacing Manual)

**Safety Critical:**
- Treatment laser CANNOT operate without stable TEC temperature
- TEC failure triggers automatic laser shutdown
- Temperature monitoring logged to database every 500ms

---

### 3. Aiming Beam Control System

#### 3.1 LDD200 Laser Diode Driver

**Part Number:** LDD200

**Function:** 200mA constant current driver for SEMINEX integrated aiming beam

**Specifications:**
- **Output Current:** 0-200 mA
- **Control:** Analog voltage input (0-5V)
- **Power Supply:** +5V
- **Response Time:** <10 µs

**Key Features:**
- Analog voltage control (0-5V → 0-200mA linear)
- Built-in current limiting
- Low noise operation
- Compact footprint

**Documentation:**
- `components/laser_control/ldd200_aiming_driver/docs/AIMING-BEAM-driver.pdf`

**Control Integration:**
- Controlled via MCP4725 DAC (see below)
- DAC output (0-5V) → LDD200 analog input → Aiming beam current (0-200mA)

---

#### 3.2 MCP4725 12-bit DAC

**Part Number:** MCP4725

**Function:** I2C-controlled digital-to-analog converter for precise aiming beam power control

**Specifications:**
- **Resolution:** 12-bit (4096 discrete levels)
- **Output Range:** 0-5V (rail-to-rail)
- **Interface:** I2C (address 0x62)
- **Settling Time:** 6 µs typical
- **Power Supply:** +5V

**Key Features:**
- Non-volatile memory (EEPROM)
- Programmable power-on default
- Single-byte fast mode for real-time control
- Multi-byte normal mode for EEPROM programming

**Documentation:**
- `components/laser_control/mcp4725_dac/docs/mcp4725-DAC-chip.pdf`

**I2C Configuration:**
- **Address:** 0x62 (7-bit address, configurable via solder jumpers)
- **Bus:** Shared with MPU6050 accelerometer
- **Pins:** Arduino A4 (SDA), A5 (SCL)
- **Pull-ups:** 4.7kΩ to +5V (required for I2C)

**Control Range:**
- **DAC Value:** 0-4095 (12-bit)
- **Output Voltage:** 0-5V
- **Aiming Beam Current:** 0-200mA (via LDD200)
- **Default Power:** 2048 (50%, ~100mA, ~2.5V)

**Python Integration:**
- Library: `Adafruit_MCP4725` (recommended)
- Controller: `src/hardware/gpio_controller.py` (to be updated)
- Methods:
  - `start_aiming_beam()` → Set DAC to default power (2048)
  - `stop_aiming_beam()` → Set DAC to 0
  - `set_aiming_beam_power(value)` → Set DAC to specific value (0-4095)

---

### 4. Arduino Uno GPIO Controller

**Part Number:** Arduino Uno (ATmega328P)

**Function:** Dedicated safety controller for hardware interlocks and aiming beam control

**Firmware:**
- Location: `firmware/arduino_watchdog/arduino_watchdog_v2/arduino_watchdog_v2.ino`
- Version: v2.0 (requires MCP4725 I2C support - **to be implemented**)

**I2C Bus Configuration:**

The Arduino I2C bus (A4/A5) is shared between two devices:

| Device | I2C Address | Function |
|--------|-------------|----------|
| MPU6050 Accelerometer | 0x68 | Vibration detection for smoothing motor |
| MCP4725 DAC | 0x62 | Aiming beam power control |

**Pin Assignments:**

| Pin | Function | Direction | Device/Purpose |
|-----|----------|-----------|----------------|
| **A0** | Photodiode | Analog Input | Treatment laser power monitoring (0-5V) |
| **A4** | SDA (I2C Data) | I2C Bus | MPU6050 + MCP4725 |
| **A5** | SCL (I2C Clock) | I2C Bus | MPU6050 + MCP4725 |
| **D2** | Motor Control | PWM Output | Smoothing motor (1.5-3.0V) |
| **D3** | Vibration Sensor | Digital Input | MPU6050 interrupt pin |
| **D5** | Footpedal | Digital Input | Deadman switch (future) |
| **D9** | Motor PWM | PWM Output | Smoothing motor speed control |

**Serial Protocol (115200 baud):**

Current commands (v2.0):
```
WDT_RESET           → Reset watchdog timer (500ms heartbeat)
MOTOR_SPEED:xxx     → Set motor PWM (0-153 max)
MOTOR_ON            → Enable motor at default speed
MOTOR_OFF           → Disable motor
LASER_ON            → Enable aiming beam (MCP4725 DAC to default)
LASER_OFF           → Disable aiming beam (MCP4725 DAC to 0)
GET_PHOTODIODE      → Read photodiode voltage (A0)
GET_STATUS          → Full system status report
ACCEL_CALIBRATE     → Zero accelerometer baseline
ACCEL_SET_THRESHOLD:x.xx → Set vibration threshold (g's)
```

**Required Firmware Updates (v3.0):**
- [ ] Add Adafruit_MCP4725 library support
- [ ] Implement I2C multi-device initialization
- [ ] Add `SET_AIMING_POWER:xxxx` command (0-4095 DAC value)
- [ ] Update `LASER_ON` to use MCP4725 DAC (default: 2048)
- [ ] Update `LASER_OFF` to use MCP4725 DAC (value: 0)
- [ ] Add I2C bus error detection and recovery
- [ ] Test I2C bus sharing between MPU6050 + MCP4725

---

## Control Flow Diagrams

### Treatment Laser Control Flow

```
Python (laser_controller.py)
    ↓ Serial @ 38400 baud
Arroyo 6300 Laser Driver
    ↓ Current output (0-2000mA)
SEMINEX 1550nm Treatment Beam
    ↓ Optical output
Photodiode (feedback)
    ↓ Voltage (0-5V)
Arduino A0 (monitoring)
    ↓ Serial @ 115200 baud
Python (gpio_controller.py)
```

### Aiming Beam Control Flow

```
Python (gpio_controller.py)
    ↓ I2C commands
Arduino Uno (I2C master)
    ↓ I2C @ 0x62
MCP4725 DAC
    ↓ Analog voltage (0-5V)
LDD200 Driver
    ↓ Current output (0-200mA)
SEMINEX Aiming Beam
```

### Temperature Control Flow

```
Python (tec_controller.py)
    ↓ Serial @ 38400 baud
Arroyo 5305 TEC Controller
    ↓ TEC current (±5A)
Peltier Module
    ↓ Heat transfer
SEMINEX Laser Diode
    ↓ Thermistor feedback
Arroyo 5305 TEC Controller
    ↓ PID control loop
```

---

## Safety Interlocks

### Hardware Interlocks (Primary - Arduino-enforced)

1. **Watchdog Timer**
   - Timeout: 1000ms
   - Required heartbeat: Every 500ms via `WDT_RESET` command
   - Failure action: Halt system, disable all outputs

2. **Photodiode Power Verification**
   - Monitor: Continuous analog read on A0
   - Expected: Proportional to laser current
   - Failure action: Safety manager triggers laser shutdown

3. **Smoothing Motor + Vibration Detection**
   - Motor: PWM control on D9 (1.5-3.0V, DO NOT EXCEED 153!)
   - Vibration: MPU6050 accelerometer via I2C
   - Validation: Motor ON + Vibration detected = healthy
   - Failure action: Safety manager disables treatment laser

4. **Footpedal Deadman Switch** (future - D5)
   - Type: Normally-open momentary switch
   - Requirement: Active-high for laser operation
   - Failure action: Immediate laser shutdown

### Software Interlocks (Secondary - Python safety.py)

1. **Emergency Stop (E-Stop)**
   - Global button in main window toolbar
   - Highest priority interrupt
   - Action: Locks system in EMERGENCY_STOP state

2. **Power Limit Enforcement**
   - Maximum: 2000mA (configured in `config.yaml`)
   - Enforcement: Pre-treatment validation + runtime monitoring
   - Action: Reject commands exceeding limit

3. **Session Validation**
   - Requirement: Active subject + session required for laser operation
   - Enforcement: Safety manager state machine
   - Action: Prevent laser enable without valid session

4. **TEC Temperature Validation**
   - Requirement: TEC within 15-35°C range and stable (±0.1°C)
   - Enforcement: Continuous monitoring via TEC controller
   - Action: Disable laser if temperature out of range

---

## Selective Shutdown Policy

When a safety fault occurs, TOSCA implements selective shutdown:

**DISABLE:**
- Treatment laser (immediate power-off via Arroyo 6300)

**MAINTAIN:**
- Camera (visual feedback for diagnosis)
- Linear actuator (controlled retraction)
- Aiming beam (low power, useful for alignment checking)
- GPIO monitoring (diagnostic data collection)
- Event logging (audit trail)

**Rationale:**
- Allows operator to diagnose the fault while maintaining safety
- Preserves visual feedback (camera + aiming beam)
- Maintains audit trail (logging continues)
- Only disables the high-power treatment laser (primary hazard)

---

## Configuration Files

### Primary Configuration (`config.yaml`)

```yaml
hardware:
  laser:
    com_port: "COM4"
    baudrate: 38400
    timeout_s: 1.0
    write_timeout_s: 1.0
    monitor_timer_ms: 500
    max_current_ma: 2000.0
    min_current_ma: 0.0

  tec:
    com_port: "COM9"
    baudrate: 38400
    timeout_s: 1.0
    write_timeout_s: 1.0
    monitor_timer_ms: 500
    min_temp_c: 15.0
    max_temp_c: 35.0
    stability_threshold_c: 0.1

  gpio:
    com_port: "COM6"
    baudrate: 115200
    timeout_s: 1.0
    write_timeout_s: 1.0
    monitor_timer_ms: 100
    watchdog_timeout_ms: 1000

    motor_pwm_pin: 9
    motor_pwm_min: 0
    motor_pwm_max: 153
    motor_default_speed: 100

    accelerometer_i2c: true
    accelerometer_address: 0x68
    vibration_threshold: 0.1

    photodiode_pin: 0

    # MCP4725 DAC for Aiming Beam Control
    mcp4725_i2c: true
    mcp4725_address: 0x62
    aiming_beam_dac_max: 4095
    aiming_beam_dac_default: 2048

    footpedal_pin: 5

safety:
  watchdog_enabled: true
  watchdog_heartbeat_ms: 500
  emergency_stop_enabled: true
  interlock_check_enabled: true
  laser_enable_requires_interlocks: true
```

---

## Communication Specifications

### Serial Communication Summary

| Device | COM Port | Baud Rate | Protocol | Python Controller |
|--------|----------|-----------|----------|-------------------|
| Arroyo 6300 (Laser) | COM4 | 38400 | Custom Arroyo | `src/hardware/laser_controller.py` |
| Arroyo 5305 (TEC) | COM9 | 38400 | Custom Arroyo | `src/hardware/tec_controller.py` |
| Arduino Uno (GPIO) | COM6 | 115200 | Custom ASCII | `src/hardware/gpio_controller.py` |
| Xeryon Actuator | COM3 | 9600 | Xeryon API | `src/hardware/actuator_controller.py` |

### I2C Communication (Arduino-managed)

| Device | I2C Address | Function | Library |
|--------|-------------|----------|---------|
| MPU6050 Accelerometer | 0x68 | Vibration detection | Adafruit_MPU6050 |
| MCP4725 DAC | 0x62 | Aiming beam control | Adafruit_MCP4725 |

---

## Power Requirements

### Treatment Laser System
- **Arroyo 6300:** 115VAC, 60Hz, 300W max
- **Arroyo 5305:** 115VAC, 60Hz, 150W max
- **SEMINEX Laser:** Powered via Arroyo controllers

### Aiming Beam System
- **LDD200 Driver:** +5V DC, <100mA
- **MCP4725 DAC:** +5V DC, <1mA
- **Arduino Uno:** USB-powered (5V, 500mA)

### Safety Recommendation
- Use separate power supplies for Arroyo controllers
- Use UPS backup for all laser control electronics
- Implement power-fail detection for graceful shutdown

---

## Maintenance and Calibration

### Regular Maintenance (Monthly)

1. **Photodiode Calibration**
   - Verify voltage readings match laser power meter
   - Document calibration curve in `calibration_data/`
   - Update photodiode conversion factor if needed

2. **TEC Performance Check**
   - Verify temperature stability (±0.01°C target)
   - Check TEC current vs. ambient temperature
   - Clean laser unit heat sink

3. **Aiming Beam Alignment**
   - Verify aiming beam co-alignment with treatment beam
   - Adjust if needed (mechanical adjustment on SEMINEX unit)
   - Document alignment procedure

### Annual Calibration (FDA Compliance)

1. **Power Output Verification**
   - Calibrated laser power meter measurement
   - Full power range sweep (0-2000mA)
   - Document in `calibration_data/laser_power_YYYYMMDD.csv`

2. **Safety Interlock Testing**
   - Watchdog timer timeout verification (must halt at 1000ms ±5%)
   - Photodiode detection threshold testing
   - Emergency stop response time (<100ms)

3. **Temperature Control Validation**
   - TEC stability testing over 8-hour period
   - Thermal cycling test (15-35°C range)
   - Document in `calibration_data/tec_stability_YYYYMMDD.csv`

---

## Troubleshooting

### Common Issues

#### Treatment Laser Won't Enable
1. Check TEC temperature (must be 15-35°C and stable)
2. Verify photodiode reading (should be >0.1V with aiming beam on)
3. Check safety interlocks (footpedal, smoothing motor, watchdog heartbeat)
4. Verify Arroyo 6300 serial communication (COM4 @ 38400)
5. Review safety log: `data/logs/safety_YYYYMMDD.jsonl`

#### Aiming Beam Not Responding
1. Check Arduino serial connection (COM6 @ 115200)
2. Test MCP4725 DAC via Arduino Serial Monitor:
   ```
   > LASER_ON
   < OK:LASER_ON
   ```
3. Verify I2C bus with `i2cdetect` command (should see 0x62 and 0x68)
4. Check LDD200 power supply (+5V)
5. Measure MCP4725 output voltage (multimeter on DAC output pin)

#### I2C Bus Conflicts (MPU6050 + MCP4725)
1. Verify unique addresses (0x68 vs 0x62)
2. Check pull-up resistors (4.7kΩ to +5V on both SDA and SCL)
3. Reduce I2C bus speed if communication errors
4. Monitor I2C traffic with logic analyzer if available

#### Watchdog Timeout Errors
1. Verify heartbeat interval (must be <500ms, recommend 250-400ms)
2. Check for Python thread blocking (async operations)
3. Monitor system CPU usage (high load can delay heartbeats)
4. Review Arduino serial buffer (may overflow if too many commands)

---

## References

### Manufacturer Documentation
- Arroyo Instruments: https://www.arroyoinstruments.com/
- SEMINEX: (Contact vendor for datasheet updates)
- Microchip (MCP4725): https://www.microchip.com/en-us/product/MCP4725

### Internal Documentation
- Architecture Overview: `docs/architecture/01_system_overview.md`
- Safety System Details: `docs/architecture/03_safety_system.md`
- Watchdog Implementation: `docs/architecture/07_safety_watchdog.md`
- Calibration Procedures: `docs/architecture/13_calibration_procedures.md`

### Firmware and Software
- Arduino Firmware: `firmware/arduino_watchdog/arduino_watchdog_v2/`
- Python Controllers: `src/hardware/`
- Configuration: `config.yaml`

---

**Document Maintained By:** TOSCA Development Team
**Next Review Date:** Upon firmware v3.0 release (MCP4725 implementation)
**Approval Required For Changes:** Yes (medical device hardware configuration)
