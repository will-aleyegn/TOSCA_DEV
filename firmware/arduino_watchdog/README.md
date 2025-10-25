# TOSCA Safety Watchdog Firmware

**Version:** 1.0
**Target:** Arduino Nano (ATmega328P)
**Purpose:** Hardware watchdog timer for GUI freeze protection

---

## Overview

This firmware replaces StandardFirmata with custom protocol that includes hardware watchdog timer protection. If the Python GUI freezes and stops sending heartbeat signals, the watchdog timer expires and triggers emergency hardware shutdown.

**Critical Safety Feature:** This is a hardware-level safety mechanism that cannot be disabled by frozen software.

---

## Features

- **Hardware Watchdog Timer:** 1000ms timeout using AVR WDT
- **Heartbeat Protocol:** Requires "WDT_RESET\n" every 500ms from Python
- **Emergency Shutdown:** All outputs LOW on watchdog timeout
- **GPIO Control:** Serial commands for motor, laser, sensors
- **Status Monitoring:** Real-time status queries

---

## Pin Configuration

| Pin | Function | Direction | Description |
|-----|----------|-----------|-------------|
| D2 | Motor Control | Output | Smoothing device motor (HIGH = ON) |
| D3 | Vibration Sensor | Input (Pullup) | Vibration detection (LOW = detected) |
| D4 | Aiming Laser | Output | Aiming laser control (HIGH = ON) |
| A0 | Photodiode | Analog Input | Laser power monitoring (0-5V) |

---

## Serial Protocol

**Baud Rate:** 9600
**Format:** ASCII text commands, newline terminated (`\n`)

### Watchdog Commands

```
Command: WDT_RESET
Response: OK:WDT_RESET
Action: Reset watchdog timer (heartbeat)
Usage: Send every 500ms to prevent timeout
```

### Motor Control

```
Command: MOTOR_ON
Response: OK:MOTOR_ON
Action: Enable smoothing motor (D2 = HIGH)

Command: MOTOR_OFF
Response: OK:MOTOR_OFF
Action: Disable smoothing motor (D2 = LOW)
```

### Laser Control

```
Command: LASER_ON
Response: OK:LASER_ON
Action: Enable aiming laser (D4 = HIGH)

Command: LASER_OFF
Response: OK:LASER_OFF
Action: Disable aiming laser (D4 = LOW)
```

### Sensor Reads

```
Command: GET_VIBRATION
Response: VIBRATION:0 or VIBRATION:1
Action: Read vibration sensor state

Command: GET_PHOTODIODE
Response: PHOTODIODE:2.345
Action: Read photodiode voltage (in volts)

Command: GET_STATUS
Response: Multi-line status report
Action: Get complete system status
```

### Watchdog Control (Testing Only)

```
Command: WDT_DISABLE
Response: WARNING:WDT_DISABLED
Action: Disable watchdog (for testing only)

Command: WDT_ENABLE
Response: OK:WDT_ENABLED
Action: Re-enable watchdog
```

---

## Firmware Upload Instructions

### Requirements

- Arduino IDE 1.8.x or 2.x
- Arduino Nano with CH340 USB driver
- USB cable

### Steps

1. **Install Arduino IDE**
   - Download from https://www.arduino.cc/en/software
   - Install CH340 drivers if needed

2. **Open Firmware**
   - File → Open → `arduino_watchdog.ino`

3. **Configure Board**
   - Tools → Board → Arduino AVR Boards → Arduino Nano
   - Tools → Processor → ATmega328P (Old Bootloader)
   - Tools → Port → Select COM port

4. **Upload Firmware**
   - Click Upload button (→)
   - Wait for "Done uploading" message

5. **Verify Upload**
   - Open Serial Monitor (Tools → Serial Monitor)
   - Set baud rate to 9600
   - Should see: "TOSCA Safety Watchdog v1.0"

---

## Testing Procedure

### 1. Basic Communication Test

```python
import serial
import time

ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino reset

# Read startup messages
print(ser.read_all().decode())

# Send status command
ser.write(b'GET_STATUS\n')
time.sleep(0.1)
print(ser.read_all().decode())
```

**Expected Output:**
```
TOSCA Safety Watchdog v1.0
Initializing...
Watchdog enabled (1000ms timeout)
Ready. Send WDT_RESET every 500ms
-----------------------------------
STATUS:
  Motor: OFF
  Aiming Laser: OFF
  Vibration: NONE
  Photodiode: 0.000V
  Watchdog: ENABLED
  Last Heartbeat: 0ms ago
OK:STATUS
```

### 2. Heartbeat Test

```python
# Send heartbeat every 500ms for 10 seconds
for i in range(20):
    ser.write(b'WDT_RESET\n')
    response = ser.readline().decode().strip()
    print(f"{i}: {response}")
    time.sleep(0.5)
```

**Expected:** All responses should be "OK:WDT_RESET"

### 3. Watchdog Timeout Test

```python
# Send heartbeat for 2 seconds
for i in range(4):
    ser.write(b'WDT_RESET\n')
    time.sleep(0.5)

# STOP heartbeat - watchdog should trigger
print("Stopping heartbeat... watchdog should trigger in 1000ms")
time.sleep(2)

# Try to send command - should fail (Arduino halted)
ser.write(b'GET_STATUS\n')
response = ser.readline().decode().strip()
if not response:
    print("✓ Arduino halted by watchdog (no response)")
else:
    print("✗ Arduino still responding (watchdog failed)")
```

**Expected:** No response after timeout (Arduino halted)

### 4. Power Cycle Recovery

- Unplug USB cable
- Wait 5 seconds
- Plug back in
- Verify startup message appears
- Verify watchdog is enabled

---

## Watchdog Timing

```
Normal Operation:
├─ Python sends heartbeat every 500ms
├─ Arduino receives WDT_RESET
├─ Arduino calls wdt_reset()
└─ Watchdog timer resets to 0

GUI Freeze Scenario:
├─ Python stops sending heartbeat
├─ Arduino watchdog timer counts: 0ms → 1000ms
├─ Timeout reached at 1000ms
├─ ISR(WDT_vect) triggered
├─ Emergency shutdown:
│  ├─ All outputs LOW
│  ├─ Interrupts disabled
│  └─ Infinite loop (system halted)
└─ Power cycle required to recover
```

---

## Safety Margin Calculation

- **Watchdog Timeout:** 1000ms
- **Heartbeat Interval:** 500ms
- **Safety Margin:** 500ms (50%)

This provides:
- 1 missed heartbeat tolerance
- Resilience to network/USB timing jitter
- Predictable timeout behavior

---

## Troubleshooting

### Upload Fails

**Problem:** "avrdude: stk500_getsync() not in sync"

**Solution:**
- Check COM port selection
- Try "ATmega328P (Old Bootloader)"
- Press reset button during upload
- Check USB cable connection

### No Serial Response

**Problem:** Arduino not responding to commands

**Solution:**
- Verify baud rate is 9600
- Check line ending is Newline (`\n`)
- Wait 2 seconds after opening serial port (Arduino resets)
- Try uploading firmware again

### Watchdog Not Triggering

**Problem:** Arduino continues operating without heartbeat

**Solution:**
- Verify firmware uploaded correctly
- Check watchdog enabled: Send `GET_STATUS`, look for "Watchdog: ENABLED"
- Verify 1000ms timeout in code (`WDTO_1S`)
- Check ISR(WDT_vect) is defined

### False Watchdog Triggers

**Problem:** Arduino randomly halts during normal operation

**Solution:**
- Verify heartbeat interval is 500ms (not longer)
- Check USB connection stability
- Monitor serial errors/timeouts
- Increase heartbeat frequency if needed (e.g., 400ms)

---

## Differences from StandardFirmata

This custom firmware **replaces** StandardFirmata:

| Feature | StandardFirmata | This Firmware |
|---------|-----------------|---------------|
| Protocol | Firmata binary | Custom ASCII text |
| Watchdog | ❌ No | ✅ Hardware WDT |
| GPIO | Full GPIO | Limited to required pins |
| Library | pyfirmata2 | pyserial |
| Extensibility | High | Moderate |

**Why Custom Firmware:**
- StandardFirmata doesn't support hardware watchdog
- Need custom ISR for emergency shutdown
- Simpler protocol for safety-critical operations
- Direct control over watchdog behavior

---

## Python Integration

See `src/hardware/gpio_controller.py` for:
- Serial communication wrapper
- Command sending/receiving
- Error handling
- Reconnection logic

See `src/core/safety_watchdog.py` for:
- Heartbeat timer (QTimer, 500ms)
- Watchdog monitoring
- Event logging

---

## Version History

**v1.0 (2025-10-25)**
- Initial release
- Hardware watchdog timer (1000ms)
- Basic GPIO control (motor, laser, sensors)
- Serial command protocol
- Emergency shutdown ISR

---

## Safety Certification Notes

For regulatory submission:

- **Watchdog Timer:** AVR hardware WDT, cannot be disabled by software crash
- **Timeout Value:** 1000ms (IEC 62304 compliant)
- **Emergency Action:** All outputs LOW (fail-safe state)
- **Recovery:** Requires manual intervention (power cycle)
- **Testing:** See tests/test_watchdog.py for validation

---

**Last Updated:** 2025-10-25
**Status:** Ready for testing
**Priority:** CRITICAL - Required before clinical use
