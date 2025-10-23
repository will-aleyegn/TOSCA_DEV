# Xeryon Actuator - Lessons Learned

**Purpose:** Document API quirks, common mistakes, and solutions for the Xeryon actuator
**Hardware:** Xeryon XLS Linear Stage
**Library:** Xeryon.py (v1.88)

---

## Critical Requirement: Index Finding

### Issue #1: Absolute Positioning Requires Index

**Problem:**
Attempting to use `setDPOS()` before finding the index position results in unpredictable behavior or errors.

**Root Cause:**
The Xeryon controller needs a reference point (index) to calculate absolute positions. Without it, the encoder is not "valid" and position commands may fail or move to incorrect positions.

**Solution:**
```python
# ALWAYS find index before absolute positioning
axis.findIndex()

# Verify encoder is valid
if axis.isEncoderValid():
    # Now safe to use absolute positioning
    axis.setDPOS(1500)
```

**When to find index:**
- At startup
- After power cycle
- After any error that invalidates encoder
- If `isEncoderValid()` returns False

**Time required:** 10-30 seconds depending on stage position

---

## Settings File Requirement

### Issue #2: Missing settings_default.txt

**Problem:**
The Xeryon.py library expects a `settings_default.txt` file in the same directory as the script.

**Error if missing:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'settings_default.txt'
```

**Solution:**
Ensure `settings_default.txt` is present in:
- `actuator_module/` directory (copied from docs/actuator-control/)
- OR in the same directory as your script
- OR pass custom settings file: `controller.start(external_settings_default="path/to/settings.txt")`

**File content:**
Contains default parameters for stage control (SSPD, HLIM, LLIM, PTOL, etc.)

---

## Units and Conversion

### Issue #3: Encoder Units vs. Real Units

**Problem:**
The Xeryon controller works internally in "encoder units" which are hardware-specific. Converting to real-world units (mm, µm) requires knowing the stage's encoder resolution.

**Root Cause:**
Different Xeryon stages have different encoder resolutions. The `Axis` class handles conversion, but you must:
1. Specify the correct stage type (XLS_312 for TOSCA)
2. Set working units explicitly

**Solution:**
```python
# Specify stage type during initialization
axis = Axis(controller, "A", XLS_Stage.XLS_312)

# Set working units
axis.setUnit(Units.mu)  # Micrometers for TOSCA

# Now positions are in µm
axis.setDPOS(1500)  # Move to 1500 µm

# Or specify units explicitly
axis.setDPOS(1.5, Units.mm)  # Same as 1500 µm
```

**Available units:**
- `Units.mm` - Millimeters
- `Units.mu` - Micrometers (recommended for TOSCA)
- `Units.nm` - Nanometers
- `Units.enc` - Raw encoder units
- `Units.deg`, `Units.rad` - For rotary stages

---

## Thermal Protection

### Issue #4: Thermal Protection Triggered

**Problem:**
After continuous operation, status bits 2 or 3 activate and motor stops.

**Error message:**
```
Thermal protection activated (bit 2 or 3)
```

**Root Cause:**
Piezoelectric stages generate heat during operation. Continuous movement or high-speed operation triggers thermal protection.

**Solution:**
1. **Power cycle:** Unplug USB cable for 30+ seconds
2. **Wait for cooldown:** Let stage cool before resuming
3. **Re-enable:** Send `ENBL=1` command
4. **Avoid continuous operation:** Add rest periods during long sequences

**Prevention:**
- Lower speed (reduce SSPD)
- Add delays between movements
- Don't run at maximum amplitude continuously
- Monitor status bits 2-3

**AUTO_SEND_ENBL flag:**
In Xeryon.py, `AUTO_SEND_ENBL = False` by default. If set to True, it automatically sends ENBL=1 on thermal errors (bypasses safety - use cautiously).

---

## Position Limits and Error Recovery

### Issue #5: ELIM Error (Error Limit Exceeded)

**Problem:**
Attempting to move beyond HLIM/LLIM or moving too fast triggers ELIM error (status bit 16).

**Symptoms:**
- Motor signals switch off
- Stage enters safe mode
- Following error exceeds ELIM value

**Root Cause:**
- Moving beyond physical limits
- Speed too high for load
- Position limits (HLIM/LLIM) set incorrectly

**Solution:**
```python
# Set appropriate limits for TOSCA (0-3mm range)
axis.sendCommand("HLIM=3000")  # 3000 µm = 3 mm
axis.sendCommand("LLIM=0")

# If error occurs:
axis.reset()  # Reset controller
# OR
axis.sendCommand("ENBL=1")  # Re-enable amplifier

# Then find index again
axis.findIndex()
```

**Prevention:**
- Always set HLIM/LLIM before operation
- Find index first to establish reference
- Don't exceed stage's physical travel range
- Use conservative speed settings initially

---

## Serial Communication

### Issue #6: COM Port Already in Use

**Problem:**
```
SerialException: could not open port 'COM3': PermissionError
```

**Root Cause:**
Another application (previous Python script, sequence builder, terminal emulator) has the port open.

**Solution:**
1. Close all applications using the port
2. In Python, ensure `controller.stop()` is called
3. Check Windows Device Manager for port conflicts
4. Try different COM port

**Prevention:**
Always use try/finally or context managers:
```python
controller = Xeryon(COM_port="COM3")
axis = Axis(controller, "A", XLS_Stage.XLS_312)

try:
    controller.start()
    # ... operations ...
finally:
    controller.stop()  # Ensures port is released
```

---

## Blocking Behavior

### Issue #7: Commands Block Until Complete

**Problem:**
Calling `setDPOS()` or `findIndex()` blocks the program until the operation completes.

**Root Cause:**
By design, Xeryon.py waits for position to be reached before returning (unless `DISABLE_WAITING = True`).

**Solution:**
This is actually desired behavior for most applications - it simplifies programming.

**If you need non-blocking:**
```python
# In Xeryon.py header, set:
DISABLE_WAITING = True

# Then manually check completion:
axis.setDPOS(1500)
while not axis.isPositionReached():
    time.sleep(0.01)
    # Do other work here
```

**For TOSCA:** Keep default blocking behavior - simpler and safer.

---

## Position Tolerance

### Issue #8: "Position Reached" Never Triggers

**Problem:**
`isPositionReached()` returns False even though stage appears to be at target.

**Root Cause:**
Position tolerance (PTOL) is too tight, or timeout (TOUT) is too short.

**Solution:**
```python
# Adjust position tolerance (default is 2 encoder units)
axis.sendCommand("PTOL=5")  # Allow ±5 encoder unit error

# Adjust timeout (default is 50ms)
axis.sendCommand("TOUT=100")  # Wait 100ms before using PTO2

# Secondary tolerance (fallback)
axis.sendCommand("PTO2=10")  # Wider tolerance after timeout
```

**For TOSCA:** Default values (PTOL=2, PTO2=10, TOUT=50) should work fine. Only adjust if needed.

---

## Threading Considerations

### Issue #9: Xeryon.py Uses Internal Threading

**Problem:**
Conflicts occur when creating external threads that communicate with the stage.

**Root Cause:**
Xeryon.py's `Communication` class uses threading internally for serial I/O.

**Solution:**
- Don't create external threads for Xeryon communication
- All Xeryon calls should be from main thread
- If you need background operation, use `external_communication_thread=True`:

```python
comm_thread = controller.start(external_communication_thread=True)
# ... your code ...
comm_thread.join()  # Wait for thread to finish
```

**For TOSCA:** Use Xeryon from main GUI thread or a dedicated worker thread, not from Qt event handlers.

---

## Debug Mode

### Issue #10: Testing Without Hardware

**Problem:**
Want to test code without connecting actual hardware.

**Solution:**
In Xeryon.py header:
```python
DEBUG_MODE = True  # Ignores some hardware checks
OUTPUT_TO_CONSOLE = True  # Verbose output for debugging
```

**Warning:** DEBUG_MODE bypasses safety checks. Only use for development, not production!

---

## Summary of Best Practices

1. **Always find index at startup:** `axis.findIndex()`
2. **Set position limits early:** HLIM=3000, LLIM=0 for TOSCA
3. **Use micrometers as working unit:** `axis.setUnit(Units.mu)`
4. **Check encoder validity before positioning:** `axis.isEncoderValid()`
5. **Use try/finally for cleanup:** Ensure `controller.stop()` is called
6. **Keep settings_default.txt accessible:** In script directory
7. **Monitor thermal protection:** Add rest periods for continuous operation
8. **Start with conservative speeds:** Increase SSPD gradually
9. **Verify position reached:** Check `axis.isPositionReached()`
10. **Handle errors gracefully:** Reset and re-home on ELIM errors

---

## Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Encoder not valid" | Index not found | Run `axis.findIndex()` |
| "Thermal protection" (bit 2/3) | Overheating | Power cycle, wait, send ENBL=1 |
| "Error limit exceeded" (bit 16) | Position limit or speed | Reset, find index, check HLIM/LLIM |
| "Safety timeout" (bit 18) | Motor on too long | Reset, check TOU2 setting |
| "Port in use" | COM port locked | Close other apps, call controller.stop() |
| "settings_default.txt not found" | Missing file | Copy from docs/actuator-control/ |

---

## When to Consult Xeryon Support

- Persistent thermal protection errors despite cooldown
- Mechanical issues (grinding, sticking, unusual noise)
- Encoder errors after successful index finding
- Hardware damage or physical obstructions
- Firmware updates needed

**Xeryon Support:** support@xeryon.com

---

**Remember:** The Xeryon stage is a precision piezoelectric device. Treat it carefully, follow index-finding protocol, and monitor thermal protection to ensure long-term reliability.
