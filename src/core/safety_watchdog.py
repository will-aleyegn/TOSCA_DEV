# -*- coding: utf-8 -*-
"""
Safety watchdog for TOSCA laser control system.

Sends periodic heartbeat to hardware watchdog timer. If GUI freezes,
heartbeat stops, watchdog expires, hardware performs emergency shutdown.
"""

import logging
from typing import Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)


class SafetyWatchdog(QObject):
    """
    Software watchdog that sends heartbeat to hardware watchdog timer.

    Architecture:
    - Python sends heartbeat every 500ms (QTimer)
    - Arduino has 1000ms timeout (AVR hardware watchdog)
    - If GUI freezes → heartbeat stops → watchdog expires → emergency shutdown

    Safety Margin:
    - Heartbeat interval: 500ms
    - Watchdog timeout: 1000ms
    - Safety margin: 500ms (50%)
    - Tolerance: 1 missed heartbeat before timeout

    Emergency Shutdown (on watchdog timeout):
    - All GPIO outputs LOW (motor OFF, lasers OFF)
    - Arduino system halted (requires power cycle)
    - Non-recoverable without manual intervention

    Usage:
        watchdog = SafetyWatchdog(gpio_controller, event_logger)
        watchdog.start()  # Begin heartbeat
        # ... normal operation ...
        watchdog.stop()  # Stop heartbeat before shutdown
    """

    # Signals
    watchdog_timeout_detected = pyqtSignal()  # Watchdog expired (external detection)
    heartbeat_sent = pyqtSignal()  # Heartbeat successfully sent
    heartbeat_failed = pyqtSignal(str)  # Heartbeat failed (error message)

    def __init__(
        self, gpio_controller: Optional[Any] = None, event_logger: Optional[Any] = None
    ) -> None:
        """
        Initialize safety watchdog.

        Args:
            gpio_controller: GPIO controller with send_watchdog_heartbeat() method
            event_logger: Event logger for watchdog events (optional)
        """
        super().__init__()

        self.gpio_controller = gpio_controller
        self.event_logger = event_logger

        # Heartbeat timer (500ms interval)
        # 50% safety margin before 1000ms hardware timeout
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.setInterval(500)  # ms
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)

        # Tracking
        self.heartbeat_count = 0
        self.failed_heartbeats = 0
        self.consecutive_failures = 0
        self.is_running = False

        logger.info(
            "Safety watchdog initialized (heartbeat: 500ms, "
            "hardware timeout: 1000ms, margin: 500ms)"
        )

    def start(self) -> bool:
        """
        Start watchdog heartbeat.

        Begins sending heartbeat every 500ms to hardware watchdog.
        Requires GPIO controller to be connected.

        Returns:
            True if started successfully, False if cannot start
        """
        # Verify GPIO controller available and connected
        if not self.gpio_controller:
            logger.error("Cannot start watchdog - no GPIO controller configured")
            return False

        if (
            not hasattr(self.gpio_controller, "is_connected")
            or not self.gpio_controller.is_connected
        ):
            logger.error("Cannot start watchdog - GPIO controller not connected")
            return False

        if not hasattr(self.gpio_controller, "send_watchdog_heartbeat"):
            logger.error(
                "Cannot start watchdog - GPIO controller missing send_watchdog_heartbeat() method"
            )
            return False

        # Start heartbeat timer
        self.heartbeat_timer.start()
        self.is_running = True
        self.heartbeat_count = 0
        self.failed_heartbeats = 0
        self.consecutive_failures = 0

        logger.info("Safety watchdog started - heartbeat active")

        # Log event
        if self.event_logger:
            try:
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.SYSTEM_STARTUP,
                    description="Safety watchdog heartbeat started (500ms interval)",
                    severity=EventSeverity.INFO,
                )
            except Exception as e:
                logger.warning(f"Failed to log watchdog start event: {e}")

        return True

    def stop(self) -> None:
        """
        Stop watchdog heartbeat.

        IMPORTANT: Must be called before disconnecting GPIO controller
        or closing application. Hardware watchdog will timeout if
        heartbeat stops unexpectedly.
        """
        if not self.is_running:
            logger.debug("Watchdog already stopped")
            return

        self.heartbeat_timer.stop()
        self.is_running = False

        logger.info(
            f"Safety watchdog stopped (total: {self.heartbeat_count} heartbeats, "
            f"failures: {self.failed_heartbeats})"
        )

        # Log event
        if self.event_logger:
            try:
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.SYSTEM_SHUTDOWN,
                    description=(
                        f"Safety watchdog stopped ({self.heartbeat_count} heartbeats sent, "
                        f"{self.failed_heartbeats} failures)"
                    ),
                    severity=EventSeverity.WARNING,
                )
            except Exception as e:
                logger.warning(f"Failed to log watchdog stop event: {e}")

    def _send_heartbeat(self) -> None:
        """
        Send heartbeat to hardware watchdog (internal, called by timer).

        Calls GPIO controller's send_watchdog_heartbeat() method.
        Tracks success/failure statistics.
        """
        try:
            # Send heartbeat to hardware
            success = self.gpio_controller.send_watchdog_heartbeat()

            if success:
                # Heartbeat sent successfully
                self.heartbeat_count += 1
                self.consecutive_failures = 0
                self.heartbeat_sent.emit()

                # Log every 100 heartbeats (every 50 seconds)
                if self.heartbeat_count % 100 == 0:
                    logger.debug(
                        f"Watchdog heartbeat #{self.heartbeat_count} "
                        f"(failures: {self.failed_heartbeats})"
                    )

            else:
                # Heartbeat failed
                self.failed_heartbeats += 1
                self.consecutive_failures += 1

                error_msg = (
                    f"Heartbeat send failed (consecutive: {self.consecutive_failures}, "
                    f"total: {self.failed_heartbeats})"
                )
                logger.error(error_msg)
                self.heartbeat_failed.emit(error_msg)

                # CRITICAL: If 3 consecutive failures, assume connection lost
                if self.consecutive_failures >= 3:
                    logger.critical(
                        "Watchdog heartbeat failed 3 consecutive times - "
                        "GPIO connection may be lost!"
                    )
                    self._handle_critical_failure()

        except Exception as e:
            self.failed_heartbeats += 1
            self.consecutive_failures += 1

            error_msg = f"Watchdog heartbeat exception: {e}"
            logger.error(error_msg)
            self.heartbeat_failed.emit(error_msg)

            if self.consecutive_failures >= 3:
                self._handle_critical_failure()

    def _handle_critical_failure(self) -> None:
        """
        Handle critical heartbeat failure (3 consecutive failures).

        Stops watchdog to prevent false timeout triggers.
        Emits signal for UI notification.
        """
        logger.critical("CRITICAL: Stopping watchdog due to repeated heartbeat failures")

        self.stop()
        self.watchdog_timeout_detected.emit()

        # Log critical event
        if self.event_logger:
            try:
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.SYSTEM_ERROR,
                    description=(
                        f"Safety watchdog stopped due to {self.consecutive_failures} "
                        "consecutive heartbeat failures - GPIO connection lost"
                    ),
                    severity=EventSeverity.EMERGENCY,
                )
            except Exception as e:
                logger.error(f"Failed to log critical watchdog failure: {e}")

    def simulate_freeze(self) -> None:
        """
        Simulate GUI freeze for testing.

        Stops heartbeat timer to trigger hardware watchdog timeout.
        Hardware should perform emergency shutdown after 1000ms.

        ⚠️  WARNING: TESTING ONLY - DO NOT USE IN PRODUCTION
        ⚠️  This will cause hardware watchdog to expire and halt Arduino
        ⚠️  Power cycle required to recover

        Usage:
            watchdog.simulate_freeze()
            # Wait 1000ms → hardware watchdog triggers
            # → Emergency shutdown (all outputs LOW)
            # → Arduino halts (requires power cycle)
        """
        logger.warning("⚠️  SIMULATING GUI FREEZE - WATCHDOG SHOULD TRIGGER IN 1000ms")
        logger.warning("⚠️  Hardware will halt - power cycle required to recover")

        # Stop heartbeat timer (simulates frozen GUI)
        self.heartbeat_timer.stop()
        self.is_running = False

        # Log test event
        if self.event_logger:
            try:
                from core.event_logger import EventSeverity, EventType

                self.event_logger.log_event(
                    event_type=EventType.SYSTEM_ERROR,
                    description="GUI freeze simulation - watchdog test (hardware will timeout)",
                    severity=EventSeverity.CRITICAL,
                )
            except Exception as e:
                logger.error(f"Failed to log freeze simulation: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get watchdog statistics.

        Returns:
            Dictionary with heartbeat statistics
        """
        success_rate = 0.0
        if self.heartbeat_count + self.failed_heartbeats > 0:
            success_rate = (
                self.heartbeat_count / (self.heartbeat_count + self.failed_heartbeats) * 100
            )

        return {
            "is_running": self.is_running,
            "heartbeat_count": self.heartbeat_count,
            "failed_heartbeats": self.failed_heartbeats,
            "consecutive_failures": self.consecutive_failures,
            "success_rate": success_rate,
            "heartbeat_interval_ms": 500,
            "hardware_timeout_ms": 1000,
            "safety_margin_ms": 500,
        }
