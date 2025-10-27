# Watchdog Timer Implementation Plan

## Problem Statement

**CRITICAL SAFETY ISSUE:** The TOSCA system has **NO watchdog timer** to detect system freezes. If the GUI or main thread freezes while the laser is active, the laser could remain ON indefinitely, creating a **severe safety hazard**.

### Current State
- `SafetyManager` has no heartbeat monitoring
- No application-level freeze detection
- No automatic emergency shutdown on freeze
- Protocol engine has no execution timeout watchdog

---

## Safety Requirements

### Regulatory & Safety Standards
For laser control systems, watchdog timers are typically required by:
- **IEC 60601-2-22** (Medical lasers)
- **ANSI Z136** (Laser safety standards)
- **ISO 13849** (Safety-related control systems)

### TOSCA Safety Requirement
**The system MUST automatically disable the laser within 3 seconds if the control software becomes unresponsive.**

---

## Proposed Multi-Level Watchdog Architecture

```
┌─────────────────────────────────────────────────────┐
│          Application Watchdog (Level 1)             │
│  QTimer-based heartbeat monitoring in SafetyManager │
│           Timeout: 3 seconds (3 missed beats)       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         Protocol Execution Watchdog (Level 2)        │
│       Monitors individual protocol action timeouts   │
│              Timeout: 60 seconds per action          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│        Hardware Watchdog (Level 3) [Optional]        │
│    External hardware timer (Arduino or dedicated)    │
│         Must receive periodic signal from app        │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Level 1: Application Watchdog (SafetyManager)

**File:** `src/core/safety.py`

```python
"""Enhanced SafetyManager with watchdog timer."""

import logging
from datetime import datetime
from enum import Enum

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)


class SafetyState(Enum):
    """Safety system states."""
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    WATCHDOG_TIMEOUT = "WATCHDOG_TIMEOUT"  # New state


class SafetyManager(QObject):
    """
    Central safety manager with watchdog timer.

    Monitors system health and enforces laser safety interlocks.
    """

    # Signals
    safety_state_changed = pyqtSignal(SafetyState)
    laser_enable_changed = pyqtSignal(bool)
    safety_event = pyqtSignal(str, str)  # (event_type, message)
    watchdog_timeout = pyqtSignal()  # Emitted on watchdog timeout
    heartbeat_missed = pyqtSignal(int)  # Emitted when heartbeat missed

    def __init__(self, config=None) -> None:
        super().__init__()

        # Import configuration
        if config is None:
            from ..config import settings
            config = settings.safety

        # Safety state
        self.state = SafetyState.UNSAFE
        self.emergency_stop_active = False

        # Interlock status
        self.gpio_interlock_ok = False
        self.session_valid = False
        self.power_limit_ok = True

        # Laser enable permission
        self.laser_enable_permitted = False

        # Watchdog configuration
        self.watchdog_enabled = config.watchdog_enabled
        self.watchdog_interval_ms = config.watchdog_interval_ms
        self.max_missed_heartbeats = config.max_missed_heartbeats

        # Watchdog state
        self.last_heartbeat = datetime.now()
        self.missed_heartbeat_count = 0
        self.watchdog_active = False

        # Watchdog timer (monitors heartbeat)
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self._check_heartbeat)

        # Start watchdog if enabled
        if self.watchdog_enabled:
            self._start_watchdog()

        logger.info(f"Safety manager initialized (watchdog: {self.watchdog_enabled})")

    def _start_watchdog(self) -> None:
        """Start watchdog monitoring."""
        if not self.watchdog_active:
            self.last_heartbeat = datetime.now()
            self.missed_heartbeat_count = 0
            self.watchdog_timer.start(self.watchdog_interval_ms)
            self.watchdog_active = True
            logger.info(
                f"Watchdog started (interval: {self.watchdog_interval_ms}ms, "
                f"max missed: {self.max_missed_heartbeats})"
            )

    def _stop_watchdog(self) -> None:
        """Stop watchdog monitoring."""
        if self.watchdog_active:
            self.watchdog_timer.stop()
            self.watchdog_active = False
            logger.info("Watchdog stopped")

    def refresh_heartbeat(self) -> None:
        """
        Refresh heartbeat signal from application.

        This method MUST be called regularly by the main application
        loop (e.g., every 500ms) to indicate the application is responsive.
        """
        self.last_heartbeat = datetime.now()
        self.missed_heartbeat_count = 0

    def _check_heartbeat(self) -> None:
        """
        Check if heartbeat is current (called by watchdog timer).

        This method runs independently of the main application thread.
        If the application freezes, heartbeat will not be refreshed,
        and this method will detect the timeout.
        """
        if not self.watchdog_enabled:
            return

        # Calculate time since last heartbeat
        elapsed_ms = (datetime.now() - self.last_heartbeat).total_seconds() * 1000

        # Check if heartbeat is overdue
        if elapsed_ms > self.watchdog_interval_ms:
            self.missed_heartbeat_count += 1
            logger.warning(
                f"Heartbeat missed ({self.missed_heartbeat_count}/{self.max_missed_heartbeats}) "
                f"- elapsed: {elapsed_ms:.0f}ms"
            )
            self.heartbeat_missed.emit(self.missed_heartbeat_count)

            # Check if timeout threshold exceeded
            if self.missed_heartbeat_count >= self.max_missed_heartbeats:
                self._on_watchdog_timeout()

    def _on_watchdog_timeout(self) -> None:
        """
        Handle watchdog timeout (CRITICAL PATH).

        This method is called when the watchdog detects a system freeze.
        It must execute quickly and reliably to ensure safety.
        """
        logger.critical(
            f"⚠️  WATCHDOG TIMEOUT DETECTED ⚠️ "
            f"System unresponsive for {self.missed_heartbeat_count} heartbeat periods"
        )

        # Update state
        self.state = SafetyState.WATCHDOG_TIMEOUT
        self.laser_enable_permitted = False

        # Emit signals
        self.safety_state_changed.emit(self.state)
        self.laser_enable_changed.emit(False)
        self.watchdog_timeout.emit()
        self.safety_event.emit("watchdog_timeout", "SYSTEM FREEZE DETECTED")

        # Trigger emergency stop
        self.trigger_emergency_stop_from_watchdog()

    def trigger_emergency_stop_from_watchdog(self) -> None:
        """
        Trigger emergency stop from watchdog timeout.

        NOTE: This runs in the QTimer thread, which may still be
        active even if the main GUI thread is frozen.
        """
        logger.critical("EMERGENCY STOP TRIGGERED BY WATCHDOG")

        # Attempt to disable laser via hardware controller reference
        # (This requires SafetyManager to have a reference to hardware)
        if hasattr(self, 'laser_controller') and self.laser_controller:
            try:
                self.laser_controller.set_output(False)
                self.laser_controller.set_current(0.0)
                logger.critical("Laser disabled by watchdog")
            except Exception as e:
                logger.critical(f"Failed to disable laser in watchdog: {e}")

        # Set emergency stop flag
        self.emergency_stop_active = True

    def set_laser_controller_reference(self, laser_controller) -> None:
        """
        Set reference to laser controller for watchdog emergency shutoff.

        Args:
            laser_controller: LaserController instance
        """
        self.laser_controller = laser_controller
        logger.info("Laser controller reference set for watchdog emergency shutoff")

    def get_watchdog_status(self) -> dict:
        """
        Get watchdog status information.

        Returns:
            Dictionary with watchdog status
        """
        if not self.watchdog_enabled:
            return {
                "enabled": False,
                "active": False,
            }

        elapsed_ms = (datetime.now() - self.last_heartbeat).total_seconds() * 1000

        return {
            "enabled": True,
            "active": self.watchdog_active,
            "interval_ms": self.watchdog_interval_ms,
            "max_missed": self.max_missed_heartbeats,
            "missed_count": self.missed_heartbeat_count,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "time_since_heartbeat_ms": elapsed_ms,
            "status": "OK" if self.missed_heartbeat_count == 0 else "WARNING",
        }

    # ... (rest of SafetyManager methods)
```

### Level 2: Protocol Execution Watchdog

**Already implemented in `protocol_engine.py:218`:**
```python
# Action-level timeout protection
await asyncio.wait_for(
    self._execute_action_with_retry(action),
    timeout=ACTION_TIMEOUT
)
```

**Enhancement - Add protocol-level watchdog:**
```python
class ProtocolEngine:
    async def execute_protocol(self, protocol: Protocol, ...) -> tuple[bool, str]:
        # ... existing code

        # Add protocol-level timeout (e.g., max 30 minutes)
        from ..config import settings
        max_protocol_duration = settings.protocol.max_protocol_duration_s

        try:
            await asyncio.wait_for(
                self._execute_all_actions(protocol.actions),
                timeout=max_protocol_duration
            )
        except asyncio.TimeoutError:
            logger.critical(f"Protocol timeout after {max_protocol_duration}s")
            return False, "Protocol exceeded maximum duration"
```

### Level 3: Hardware Watchdog (Future Enhancement)

**External hardware watchdog using Arduino:**

```python
class HardwareWatchdog:
    """
    External hardware watchdog using Arduino.

    Arduino receives periodic ping from application.
    If ping stops, Arduino triggers relay to cut laser power.
    """

    def __init__(self, gpio_controller):
        self.gpio = gpio_controller
        self.ping_interval_ms = 500

        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self._send_ping)
        self.ping_timer.start(self.ping_interval_ms)

    def _send_ping(self):
        """Send heartbeat ping to hardware watchdog."""
        if self.gpio.is_connected:
            # Toggle watchdog pin
            self.gpio.board.digital[5].write(1)
            QTimer.singleShot(10, lambda: self.gpio.board.digital[5].write(0))
```

---

## Integration with MainWindow

**File:** `src/ui/main_window.py`

```python
class MainWindow(QMainWindow):
    def __init__(self, ..., safety_manager: SafetyManager) -> None:
        super().__init__()

        self.safety_manager = safety_manager

        # Connect watchdog signals
        self.safety_manager.watchdog_timeout.connect(self._on_watchdog_timeout)
        self.safety_manager.heartbeat_missed.connect(self._on_heartbeat_missed)

        # Set laser controller reference for watchdog emergency shutoff
        if hasattr(self, 'laser_controller') and self.laser_controller:
            self.safety_manager.set_laser_controller_reference(self.laser_controller)

        # Start heartbeat timer
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(500)  # Send heartbeat every 500ms

    def _send_heartbeat(self) -> None:
        """Send heartbeat to watchdog (called every 500ms)."""
        self.safety_manager.refresh_heartbeat()

    def _on_heartbeat_missed(self, missed_count: int) -> None:
        """Handle missed heartbeat warning."""
        logger.warning(f"Heartbeat missed: {missed_count}")
        # Could show warning in UI

    def _on_watchdog_timeout(self) -> None:
        """Handle watchdog timeout (CRITICAL)."""
        logger.critical("WATCHDOG TIMEOUT - System freeze detected!")

        # Show critical error dialog
        QMessageBox.critical(
            self,
            "SYSTEM FREEZE DETECTED",
            "The watchdog timer detected a system freeze.\n\n"
            "The laser has been automatically disabled for safety.\n\n"
            "Please restart the application.",
        )

        # Force application exit
        QApplication.instance().quit()
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_safety_watchdog.py
import pytest
import time
from src.core.safety import SafetyManager

def test_watchdog_timeout():
    """Test watchdog triggers timeout when heartbeat stops."""

    safety = SafetyManager()

    # Send initial heartbeat
    safety.refresh_heartbeat()

    # Wait for timeout (3 seconds with 1s intervals)
    time.sleep(3.5)

    # Check that watchdog detected timeout
    assert safety.missed_heartbeat_count >= 3
    assert safety.state == SafetyState.WATCHDOG_TIMEOUT

def test_watchdog_refresh():
    """Test watchdog resets when heartbeat refreshed."""

    safety = SafetyManager()

    # Continuously refresh heartbeat
    for _ in range(5):
        time.sleep(0.5)
        safety.refresh_heartbeat()

    # Should have no missed heartbeats
    assert safety.missed_heartbeat_count == 0
```

### Integration Tests

```python
# tests/integration/test_watchdog_integration.py
def test_watchdog_disables_laser_on_timeout():
    """Test that watchdog disables laser on timeout."""

    # Setup
    laser = LaserController()
    safety = SafetyManager()
    safety.set_laser_controller_reference(laser)

    laser.connect()
    laser.set_output(True)

    # Stop sending heartbeats to trigger timeout
    time.sleep(3.5)

    # Verify laser was disabled
    assert not laser.is_output_enabled
```

### Manual Testing Procedure

1. **Normal Operation Test**
   - Start application
   - Verify watchdog status shows "OK"
   - Verify heartbeat counter increments

2. **Freeze Simulation Test**
   - Add `time.sleep(5)` in main event loop
   - Verify watchdog triggers timeout
   - Verify laser disables
   - Verify emergency stop activates

3. **Recovery Test**
   - Trigger watchdog timeout
   - Clear emergency stop
   - Resume operations
   - Verify watchdog resets

---

## Safety Validation Checklist

- [ ] Watchdog triggers within 3 seconds of freeze
- [ ] Laser automatically disables on timeout
- [ ] Emergency stop activates on timeout
- [ ] Watchdog resets after heartbeat resumes
- [ ] Watchdog status visible in UI
- [ ] Watchdog events logged
- [ ] Hardware watchdog integration tested (if implemented)

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Design & Review | 0.5 days | Architecture review, safety analysis |
| Implementation | 2 days | Code watchdog system |
| Testing | 1.5 days | Unit, integration, manual tests |
| Documentation | 0.5 days | User docs, operator training |
| **Total** | **4.5 days** | |

---

## Success Criteria

1. ✅ Watchdog detects freeze within 3 seconds
2. ✅ Laser automatically disabled on timeout
3. ✅ Emergency stop triggered on timeout
4. ✅ Watchdog status visible in UI
5. ✅ All tests pass
6. ✅ Safety documentation complete
7. ✅ Operators trained on watchdog behavior

---

**Status:** 📋 Ready for Implementation
**Priority:** 🔴 CRITICAL (Safety Issue)
**Effort:** 4.5 days
**Risk:** Medium (requires thorough testing)
**Dependencies:** Safety configuration module
