# Safety Watchdog Implementation Plan

**Priority:** CRITICAL
**Timeline:** 3-5 days
**Must Complete Before:** Any clinical testing

---

## Overview

Implement hardware watchdog timer to detect and recover from GUI software failures.

**Hazard:** Python GUI freeze leaves hardware in dangerous state (laser ON indefinitely).

**Mitigation:** Arduino watchdog timer with 1000ms timeout. If no heartbeat from GUI → emergency hardware shutdown.

---

## Architecture

### Components

1. **Arduino Watchdog Timer** (Hardware)
   - Built-in AVR watchdog timer (WDT)
   - 1000ms timeout configuration
   - Triggers emergency shutdown on timeout

2. **SafetyWatchdog Class** (Python)
   - Sends heartbeat every 500ms
   - Monitors watchdog status
   - Logs watchdog events

3. **Emergency Shutdown Circuit** (Hardware)
   - Sets all GPIO outputs LOW on watchdog timeout
   - Disables: Treatment laser, aiming laser, smoothing motor
   - Non-recoverable until manual reset

### Data Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│  MainWindow │ 500ms   │ GPIOController│  Serial │ Arduino Nano    │
│             ├────────>│ SafetyWatchdog├────────>│ Watchdog Timer  │
│             │Heartbeat│               │ Pulse   │ (1000ms timeout)│
└─────────────┘         └──────────────┘         └────────┬────────┘
                                                           │
                                                           │ Timeout
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Emergency       │
                                                  │ Shutdown:       │
                                                  │ - Laser OFF     │
                                                  │ - Motors OFF    │
                                                  │ - System HALT   │
                                                  └─────────────────┘
```

### Timing Diagram

```
Time (ms):  0    500   1000  1500  2000  2500  3000
            │     │     │     │     │     │     │
Heartbeat:  ●─────●─────●─────●─────●─────●─────●  Normal operation
            │     │     │     │     │     │     │
Watchdog:   └─────┴─────┴─────┴─────┴─────┴─────┘  Reset every 500ms
                                                     Timeout = 1000ms

GUI Freeze Scenario:
Time (ms):  0    500   1000  1500  2000  2500  3000
            │     │     │     │XXXXXXXXXXXXXXXXXXXXX  GUI frozen at 1500ms
Heartbeat:  ●─────●─────●─────                      Last heartbeat at 1000ms
            │     │     │     │     │     │     │
Watchdog:   └─────┴─────X                           Expires at 2500ms (1000ms after last heartbeat)
                        └─────────────────> EMERGENCY SHUTDOWN
```

---

## Implementation Tasks

### Task 1: Arduino Firmware with Watchdog

**File:** `firmware/arduino_watchdog/arduino_watchdog.ino`

**Requirements:**
- Enable AVR watchdog timer (1000ms timeout)
- Heartbeat input: Serial command "WDT_RESET\n" or GPIO pin D5 toggle
- Emergency shutdown: Set all outputs LOW (D2, D4) and disable serial
- Watchdog timeout triggers non-recoverable halt (requires power cycle)

**Code Outline:**
```cpp
#include <avr/wdt.h>

// Pin definitions
#define MOTOR_PIN 2
#define AIMING_LASER_PIN 4
#define HEARTBEAT_PIN 5

void setup() {
  // Configure pins
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(AIMING_LASER_PIN, OUTPUT);
  pinMode(HEARTBEAT_PIN, INPUT);

  // Enable watchdog timer (1000ms timeout)
  wdt_enable(WDTO_1S);

  // Start with all outputs OFF
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(AIMING_LASER_PIN, LOW);

  Serial.begin(9600);
}

void loop() {
  // Check for heartbeat command
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    if (cmd == "WDT_RESET") {
      wdt_reset();  // Reset watchdog timer
    }
  }

  // OR check for GPIO heartbeat toggle
  static bool last_heartbeat = false;
  bool current_heartbeat = digitalRead(HEARTBEAT_PIN);
  if (current_heartbeat != last_heartbeat) {
    wdt_reset();
    last_heartbeat = current_heartbeat;
  }

  // Normal operations (motor control, etc.)
  processCommands();
}

// Watchdog timeout ISR - emergency shutdown
ISR(WDT_vect) {
  // Set all outputs LOW
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(AIMING_LASER_PIN, LOW);

  // Halt system (infinite loop)
  cli();  // Disable interrupts
  while(1);
}
```

**Testing:**
- Upload firmware to Arduino
- Verify watchdog triggers after 1000ms with no heartbeat
- Confirm all outputs go LOW on timeout
- Test recovery after power cycle

---

### Task 2: SafetyWatchdog Python Class

**File:** `src/core/safety_watchdog.py`

**Requirements:**
- QTimer sends heartbeat every 500ms
- Monitors watchdog status via GPIO controller
- Emits signals on timeout detection
- Logs all watchdog events to event logger

**Code Outline:**
```python
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class SafetyWatchdog(QObject):
    """
    Software watchdog that sends heartbeat to hardware watchdog timer.

    Sends heartbeat every 500ms to Arduino watchdog (1000ms timeout).
    If GUI freezes, heartbeat stops, watchdog expires, hardware shuts down.
    """

    # Signals
    watchdog_timeout_detected = pyqtSignal()  # Watchdog expired (from external source)
    heartbeat_sent = pyqtSignal()  # Heartbeat successfully sent
    heartbeat_failed = pyqtSignal(str)  # Heartbeat failed to send

    def __init__(self, gpio_controller, event_logger=None):
        super().__init__()

        self.gpio_controller = gpio_controller
        self.event_logger = event_logger

        # Heartbeat timer (500ms interval, 50% safety margin before 1000ms timeout)
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.setInterval(500)
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)

        # Tracking
        self.heartbeat_count = 0
        self.failed_heartbeats = 0

        logger.info("Safety watchdog initialized (500ms heartbeat, 1000ms timeout)")

    def start(self) -> bool:
        """
        Start watchdog heartbeat.

        Returns:
            True if started successfully
        """
        if not self.gpio_controller or not self.gpio_controller.is_connected:
            logger.error("Cannot start watchdog - GPIO controller not connected")
            return False

        self.heartbeat_timer.start()
        logger.info("Watchdog heartbeat started")

        if self.event_logger:
            from core.event_logger import EventType, EventSeverity
            self.event_logger.log_event(
                event_type=EventType.SYSTEM_STARTUP,
                description="Safety watchdog heartbeat started",
                severity=EventSeverity.INFO
            )

        return True

    def stop(self) -> None:
        """Stop watchdog heartbeat."""
        self.heartbeat_timer.stop()
        logger.info("Watchdog heartbeat stopped")

        if self.event_logger:
            from core.event_logger import EventType, EventSeverity
            self.event_logger.log_event(
                event_type=EventType.SYSTEM_SHUTDOWN,
                description="Safety watchdog heartbeat stopped",
                severity=EventSeverity.WARNING
            )

    def _send_heartbeat(self) -> None:
        """Send heartbeat to hardware watchdog (called by timer)."""
        try:
            # Send heartbeat command to Arduino via GPIO controller
            success = self.gpio_controller.send_watchdog_heartbeat()

            if success:
                self.heartbeat_count += 1
                self.heartbeat_sent.emit()

                # Log every 100 heartbeats (every 50 seconds)
                if self.heartbeat_count % 100 == 0:
                    logger.debug(f"Watchdog heartbeat #{self.heartbeat_count}")
            else:
                self.failed_heartbeats += 1
                error_msg = f"Heartbeat send failed (total failures: {self.failed_heartbeats})"
                logger.error(error_msg)
                self.heartbeat_failed.emit(error_msg)

                # Critical: If 3 consecutive failures, assume connection lost
                if self.failed_heartbeats >= 3:
                    logger.critical("Watchdog heartbeat failed 3 times - GPIO connection lost!")
                    self.stop()

        except Exception as e:
            logger.error(f"Watchdog heartbeat exception: {e}")
            self.heartbeat_failed.emit(str(e))

    def simulate_freeze(self) -> None:
        """
        Simulate GUI freeze for testing.

        Stops heartbeat timer to trigger watchdog timeout.
        TESTING ONLY - DO NOT USE IN PRODUCTION.
        """
        logger.warning("⚠️ SIMULATING GUI FREEZE - WATCHDOG SHOULD TRIGGER IN 1000ms")
        self.heartbeat_timer.stop()

        if self.event_logger:
            from core.event_logger import EventType, EventSeverity
            self.event_logger.log_event(
                event_type=EventType.SYSTEM_ERROR,
                description="GUI freeze simulation - watchdog test",
                severity=EventSeverity.CRITICAL
            )
```

**Testing:**
- Create SafetyWatchdog instance with GPIO controller
- Start watchdog, verify heartbeat every 500ms
- Call `simulate_freeze()`, verify hardware shutdown after 1000ms
- Verify signals emitted correctly

---

### Task 3: Add Watchdog to GPIO Controller

**File:** `src/hardware/gpio_controller.py`

**Changes Required:**

```python
class GPIOController(QObject):
    def connect(self, port: str = "COM4") -> bool:
        # Existing connection code...

        # Enable watchdog timer on Arduino
        self._write_command("WDT_ENABLE")
        logger.info("Hardware watchdog timer enabled (1000ms timeout)")

        return True

    def send_watchdog_heartbeat(self) -> bool:
        """
        Send heartbeat pulse to hardware watchdog timer.

        Returns:
            True if heartbeat sent successfully
        """
        if not self.is_connected or not self.board:
            return False

        try:
            # Send heartbeat command to Arduino
            self._write_command("WDT_RESET")
            return True
        except Exception as e:
            logger.error(f"Watchdog heartbeat failed: {e}")
            return False

    def _write_command(self, command: str) -> None:
        """Send command to Arduino over serial."""
        if self.board:
            # Using pyfirmata2 serial interface
            # (Implementation depends on firmware protocol)
            pass
```

---

### Task 4: Integrate into MainWindow

**File:** `src/ui/main_window.py`

**Changes Required:**

```python
from core.safety_watchdog import SafetyWatchdog

class MainWindow(QMainWindow):
    def __init__(self):
        # Existing initialization...

        # Initialize safety watchdog (after GPIO controller connected)
        self.safety_watchdog = None

    def _connect_safety_system(self):
        # Existing safety connections...

        # Initialize and start watchdog
        if hasattr(self.safety_widget, "gpio_widget"):
            gpio_widget = self.safety_widget.gpio_widget
            if gpio_widget.controller and gpio_widget.controller.is_connected:
                self.safety_watchdog = SafetyWatchdog(
                    gpio_controller=gpio_widget.controller,
                    event_logger=self.event_logger
                )
                self.safety_watchdog.start()
                logger.info("Safety watchdog started")

    def closeEvent(self, event: QCloseEvent):
        """Handle window close - stop watchdog before disconnecting hardware."""
        if self.safety_watchdog:
            self.safety_watchdog.stop()

        # Existing cleanup...
        event.accept()
```

---

### Task 5: Testing & Validation

**Test Cases:**

1. **Normal Operation Test**
   - Start application
   - Connect GPIO
   - Verify watchdog heartbeat every 500ms
   - Monitor for 5 minutes (600 heartbeats)
   - **Pass:** No watchdog timeout, no errors

2. **GUI Freeze Simulation**
   - Start application, connect GPIO
   - Call `safety_watchdog.simulate_freeze()`
   - **Expected:** Hardware shutdown within 1000ms
   - **Verify:** All GPIO outputs LOW (laser OFF, motor OFF)
   - **Verify:** Event log shows "watchdog timeout" event

3. **Infinite Loop Test**
   - Start application, connect GPIO
   - Inject infinite loop in MainWindow event handler:
     ```python
     def _test_infinite_loop(self):
         while True:
             pass  # Freeze GUI
     ```
   - **Expected:** Watchdog expires, hardware shutdown
   - **Verify:** System recoverable after power cycle

4. **Heartbeat Failure Recovery**
   - Start application, connect GPIO
   - Disconnect Arduino USB cable during operation
   - **Expected:** Heartbeat failures logged
   - **Expected:** Watchdog stops after 3 failures
   - **Verify:** Error messages in log

5. **Stress Test**
   - Run for 24 hours
   - Monitor heartbeat success rate
   - **Pass:** >99.9% success rate (max 86 failures in 86400 heartbeats)

**Test Script:**

```python
# tests/test_watchdog.py
import pytest
import time
from src.core.safety_watchdog import SafetyWatchdog
from src.hardware.gpio_controller import GPIOController

def test_watchdog_normal_operation(mock_gpio):
    """Test watchdog sends heartbeat every 500ms."""
    watchdog = SafetyWatchdog(mock_gpio)
    watchdog.start()

    time.sleep(2.5)  # Wait for 5 heartbeats

    assert mock_gpio.heartbeat_count >= 4  # Allow timing variance
    watchdog.stop()

def test_watchdog_freeze_simulation(real_arduino):
    """Test watchdog triggers on simulated freeze."""
    gpio = GPIOController()
    gpio.connect("COM4")

    watchdog = SafetyWatchdog(gpio)
    watchdog.start()

    # Simulate freeze
    watchdog.simulate_freeze()

    # Wait for watchdog timeout
    time.sleep(1.5)

    # Verify hardware shutdown
    assert gpio.read_pin(2) == 0  # Motor OFF
    assert gpio.read_pin(4) == 0  # Aiming laser OFF
```

---

### Task 6: Documentation

**Files to Create:**

1. **docs/architecture/06_safety_watchdog.md**
   - System architecture
   - Timing diagrams
   - Failure modes and recovery
   - Regulatory justification

2. **firmware/arduino_watchdog/README.md**
   - Firmware upload instructions
   - Pin configuration
   - Watchdog configuration options
   - Troubleshooting

3. **Update docs/project/CODING_STANDARDS.md**
   - Add watchdog testing requirements
   - Add hardware safety requirements

---

## Deployment Checklist

- [ ] Arduino firmware uploaded to all devices
- [ ] Firmware version documented in device log
- [ ] Watchdog tested on actual hardware (not simulation)
- [ ] All 5 test cases passed
- [ ] 24-hour stress test completed
- [ ] Documentation reviewed and approved
- [ ] Event logging verified for all watchdog events
- [ ] Power cycle recovery tested
- [ ] Safety team signoff obtained

---

## Rollback Plan

If watchdog causes false positives or system instability:

1. **Disable in software:**
   ```python
   # In MainWindow.__init__()
   ENABLE_WATCHDOG = False  # Temporary disable

   if ENABLE_WATCHDOG and self.safety_watchdog:
       self.safety_watchdog.start()
   ```

2. **Disable in firmware:**
   - Upload non-watchdog firmware to Arduino
   - System operates without watchdog protection

3. **Investigation:**
   - Review event logs for false triggers
   - Analyze timing issues
   - Adjust timeout values if needed

---

## Success Criteria

1. ✅ Watchdog triggers within 1000ms ± 100ms on GUI freeze
2. ✅ All hardware outputs LOW after watchdog timeout
3. ✅ System recoverable after power cycle
4. ✅ <0.1% false positive rate (heartbeat failures)
5. ✅ 24-hour continuous operation without issues
6. ✅ All test cases passing
7. ✅ Documentation complete and approved

---

**Status:** Ready for implementation
**Estimated Effort:** 3-5 days
**Priority:** CRITICAL - Must complete before clinical testing
