"""
Module: Line Protocol Engine
Project: TOSCA Laser Control System

Purpose: Execute line-based treatment protocols with concurrent actions (movement, laser, dwell).
         Provides real-time control, safety monitoring, and execution logging.
Safety Critical: Yes
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.protocol_line import (
    DwellParams,
    HomeParams,
    LaserRampParams,
    LaserSetParams,
    LineBasedProtocol,
    MoveParams,
    ProtocolLine,
)

logger = logging.getLogger(__name__)

# Configuration constants
MAX_RETRIES = 3  # Maximum number of retries for hardware operations
RETRY_DELAY = 1.0  # Delay between retries in seconds
LINE_TIMEOUT = 120.0  # Maximum time for any single line in seconds


class ExecutionState(Enum):
    """Protocol execution states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class LineBasedProtocolEngine:
    """
    Execute line-based protocols with concurrent action support.

    Manages protocol execution lifecycle, safety checks, and event logging.
    Each line can contain concurrent operations (movement + laser + dwell).
    """

    def __init__(
        self,
        laser_controller: Optional[Any] = None,
        actuator_controller: Optional[Any] = None,
        safety_manager: Optional[Any] = None,
    ) -> None:
        """
        Initialize line-based protocol engine.

        Args:
            laser_controller: Laser hardware controller (optional for testing)
            actuator_controller: Actuator hardware controller (optional for testing)
            safety_manager: Safety system manager (optional for testing)
        """
        self.laser = laser_controller
        self.actuator = actuator_controller
        self.safety_manager = safety_manager

        # SAFETY-CRITICAL: Connect to real-time safety monitoring
        # If laser enable permission is revoked during execution, stop immediately
        if self.safety_manager is not None:
            self.safety_manager.laser_enable_changed.connect(self._on_laser_enable_changed)
            logger.info("Line-based protocol engine connected to real-time safety monitoring")

        self.state = ExecutionState.IDLE
        self.current_protocol: Optional[LineBasedProtocol] = None
        self.current_line_number: Optional[int] = None
        self.current_loop_iteration: int = 0

        self.execution_log: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially
        self._stop_requested = False

        # Callbacks for UI updates
        self.on_line_start: Optional[Callable[[int, int], None]] = None  # (line_num, loop_iter)
        self.on_line_complete: Optional[Callable[[int, int], None]] = None
        self.on_progress_update: Optional[Callable[[float], None]] = None  # Overall progress 0-1
        self.on_state_change: Optional[Callable[[ExecutionState], None]] = None

        # Current actuator position tracking (for duration estimation)
        self.current_position_mm: float = 0.0

    async def execute_protocol(
        self, protocol: LineBasedProtocol, record: bool = False, stop_on_error: bool = True
    ) -> tuple[bool, str]:
        """
        Execute line-based protocol from start to finish.

        Args:
            protocol: LineBasedProtocol to execute
            record: Whether to record execution to database
            stop_on_error: If False, continue with next line on non-critical failures

        Returns:
            (success, message)
        """
        # Validate protocol
        valid, errors = protocol.validate()
        if not valid:
            error_msg = f"Protocol validation failed: {'; '.join(errors)}"
            logger.error(error_msg)
            return False, error_msg

        # Safety checks
        safety_ok, safety_msg = self._perform_safety_checks()
        if not safety_ok:
            logger.error(f"Safety check failed: {safety_msg}")
            return False, safety_msg

        # Initialize execution
        self.current_protocol = protocol
        self.execution_log = []
        self.start_time = datetime.now()
        self.end_time = None
        self._stop_requested = False
        self.stop_on_error = stop_on_error
        self._set_state(ExecutionState.RUNNING)

        logger.info(f"Starting line-based protocol execution: {protocol.protocol_name}")
        logger.info(f"  Lines: {len(protocol.lines)}")
        logger.info(f"  Loop count: {protocol.loop_count}")
        logger.info(f"  Total duration: {protocol.calculate_total_duration():.1f}s")

        failed_lines = []
        try:
            # Execute protocol with loop count
            for loop_iter in range(protocol.loop_count):
                self.current_loop_iteration = loop_iter + 1
                logger.info(f"Loop iteration {self.current_loop_iteration}/{protocol.loop_count}")

                # Execute all lines in sequence
                loop_failures = await self._execute_lines_with_recovery(
                    protocol.lines, loop_iter + 1
                )
                failed_lines.extend(loop_failures)

                # Check if we should stop on error
                if loop_failures and stop_on_error:
                    break

            # Execution completed
            self.end_time = datetime.now()

            # Determine final state based on failures
            if failed_lines and stop_on_error:
                self._set_state(ExecutionState.ERROR)
                error_msg = f"Protocol failed with {len(failed_lines)} errors"
                logger.error(error_msg)
                return False, error_msg
            elif failed_lines:
                self._set_state(ExecutionState.COMPLETED)
                duration = (self.end_time - self.start_time).total_seconds()
                warning_msg = (
                    f"Protocol completed with warnings in {duration:.1f} seconds. "
                    f"{len(failed_lines)} non-critical lines failed."
                )
                logger.warning(warning_msg)
                if record:
                    self._save_execution_record()
                return True, warning_msg
            else:
                self._set_state(ExecutionState.COMPLETED)
                duration = (self.end_time - self.start_time).total_seconds()
                logger.info(f"Protocol completed successfully in {duration:.1f} seconds")
                if record:
                    self._save_execution_record()
                return True, "Protocol completed successfully"

        except Exception as e:
            self.end_time = datetime.now()
            self._set_state(ExecutionState.ERROR)
            error_msg = f"Protocol execution error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def _execute_lines_with_recovery(
        self, lines: List[ProtocolLine], loop_iteration: int
    ) -> List[ProtocolLine]:
        """Execute protocol lines with optional error recovery."""
        failed_lines = []
        total_lines = len(lines)

        for idx, line in enumerate(lines):
            # Check for stop request
            if self._stop_requested:
                logger.info("Execution stopped by user")
                raise RuntimeError("Execution stopped by user")

            # Handle pause
            await self._pause_event.wait()

            try:
                # Update progress
                line_progress = idx / total_lines if total_lines > 0 else 0.0
                loop_progress = (loop_iteration - 1) / self.current_protocol.loop_count
                overall_progress = loop_progress + line_progress / self.current_protocol.loop_count

                if self.on_progress_update:
                    self.on_progress_update(overall_progress)

                # Execute line
                await self._execute_line(line, loop_iteration)

            except Exception as e:
                # All line operations are critical (movement + laser)
                logger.error(f"Line {line.line_number} failed: {e}")

                if self.stop_on_error:
                    raise  # Re-raise to stop protocol
                else:
                    logger.warning(f"Continuing despite line {line.line_number} failure...")
                    failed_lines.append(line)

        return failed_lines

    async def _execute_line(self, line: ProtocolLine, loop_iteration: int) -> None:
        """
        Execute single protocol line with concurrent operations.

        Each line may contain:
        - Movement (move to position or home)
        - Laser control (set power or ramp power)
        - Dwell (wait time)

        These operations execute concurrently where possible.
        """
        self.current_line_number = line.line_number
        logger.info(
            f"Executing Line {line.line_number} (Loop {loop_iteration}): "
            f"{line.get_summary(self.current_position_mm)}"
        )

        # Callback: line start
        if self.on_line_start:
            self.on_line_start(line.line_number, loop_iteration)

        # Log line start
        self.execution_log.append(
            {
                "line_number": line.line_number,
                "loop_iteration": loop_iteration,
                "timestamp": datetime.now().isoformat(),
                "event": "start",
            }
        )

        try:
            # Execute with timeout protection
            await asyncio.wait_for(self._execute_line_with_retry(line), timeout=LINE_TIMEOUT)

            # Log line complete
            self.execution_log.append(
                {
                    "line_number": line.line_number,
                    "loop_iteration": loop_iteration,
                    "timestamp": datetime.now().isoformat(),
                    "event": "complete",
                }
            )

            # Callback: line complete
            if self.on_line_complete:
                self.on_line_complete(line.line_number, loop_iteration)

        except asyncio.TimeoutError:
            error_msg = f"Line {line.line_number} timed out after {LINE_TIMEOUT}s"
            logger.error(error_msg)
            self.execution_log.append(
                {
                    "line_number": line.line_number,
                    "loop_iteration": loop_iteration,
                    "timestamp": datetime.now().isoformat(),
                    "event": "timeout",
                    "error": error_msg,
                }
            )
            raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(f"Line {line.line_number} failed: {str(e)}")
            self.execution_log.append(
                {
                    "line_number": line.line_number,
                    "loop_iteration": loop_iteration,
                    "timestamp": datetime.now().isoformat(),
                    "event": "error",
                    "error": str(e),
                }
            )
            raise

    async def _execute_line_with_retry(self, line: ProtocolLine) -> None:
        """Execute line with retry logic for hardware operations."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                await self._execute_line_internal(line)
                return  # Success, exit retry loop

            except RuntimeError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Line {line.line_number} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {RETRY_DELAY}s..."
                    )
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Line {line.line_number} failed after {MAX_RETRIES} attempts")

        # All retries failed
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"Line {line.line_number} failed without error details")

    async def _execute_line_internal(self, line: ProtocolLine) -> None:
        """
        Internal line execution with concurrent operations.

        Executes movement, laser, and dwell operations concurrently where possible.
        """
        # Create concurrent tasks for line operations
        tasks = []

        # Movement task (if specified)
        if line.movement is not None:
            tasks.append(self._execute_movement(line.movement))

        # Laser task (if specified)
        if line.laser is not None:
            tasks.append(self._execute_laser(line.laser))

        # Dwell task (if specified)
        if line.dwell is not None:
            tasks.append(self._execute_dwell(line.dwell))

        # Execute all tasks concurrently
        if tasks:
            # Use gather to run all tasks and propagate any exceptions
            await asyncio.gather(*tasks)

    async def _execute_movement(self, movement: MoveParams | HomeParams) -> None:
        """Execute movement operation (move or home)."""
        if isinstance(movement, MoveParams):
            await self._execute_move(movement)
        elif isinstance(movement, HomeParams):
            await self._execute_home(movement)

    async def _execute_move(self, params: MoveParams) -> None:
        """Execute move to position."""
        from core.protocol_line import MoveType

        target_mm = params.target_position_mm
        speed_mm_per_s = params.speed_mm_per_s

        # Calculate absolute target position
        if params.move_type == MoveType.RELATIVE:
            absolute_target_mm = self.current_position_mm + target_mm
        else:
            absolute_target_mm = target_mm

        logger.debug(
            f"Moving actuator to {absolute_target_mm:.2f}mm at {speed_mm_per_s:.2f}mm/s "
            f"(type: {params.move_type.value})"
        )

        if self.actuator:
            # Convert mm to µm for controller
            target_um = int(absolute_target_mm * 1000)
            speed_um_per_s = int(speed_mm_per_s * 1000)

            # Set speed
            success = self.actuator.set_speed(speed_um_per_s)
            if not success:
                raise RuntimeError(f"Failed to set actuator speed to {speed_um_per_s}µm/s")

            # Move to position
            success = self.actuator.set_position(target_um)
            if not success:
                raise RuntimeError(f"Failed to move actuator to {target_um}µm")

            # Calculate movement time for async sleep
            distance_mm = abs(absolute_target_mm - self.current_position_mm)
            move_time = distance_mm / speed_mm_per_s if speed_mm_per_s > 0 else 1.0

            # Update current position
            self.current_position_mm = absolute_target_mm

            # Wait for movement to complete
            await asyncio.sleep(move_time)
        else:
            # Simulate movement when no hardware
            distance_mm = abs(absolute_target_mm - self.current_position_mm)
            move_time = distance_mm / speed_mm_per_s if speed_mm_per_s > 0 else 1.0
            self.current_position_mm = absolute_target_mm
            await asyncio.sleep(move_time)

    async def _execute_home(self, params: HomeParams) -> None:
        """Execute homing operation."""
        speed_mm_per_s = params.speed_mm_per_s

        logger.debug(f"Homing actuator at {speed_mm_per_s:.2f}mm/s")

        if self.actuator:
            # Convert mm/s to µm/s for controller
            speed_um_per_s = int(speed_mm_per_s * 1000)

            # Set speed
            success = self.actuator.set_speed(speed_um_per_s)
            if not success:
                raise RuntimeError(f"Failed to set actuator speed to {speed_um_per_s}µm/s")

            # Home (move to position 0)
            success = self.actuator.set_position(0)
            if not success:
                raise RuntimeError("Failed to home actuator")

            # Estimate homing time
            distance_mm = abs(self.current_position_mm)
            home_time = distance_mm / speed_mm_per_s if speed_mm_per_s > 0 else 2.0

            # Update current position
            self.current_position_mm = 0.0

            # Wait for homing to complete
            await asyncio.sleep(home_time)
        else:
            # Simulate homing
            distance_mm = abs(self.current_position_mm)
            home_time = distance_mm / speed_mm_per_s if speed_mm_per_s > 0 else 2.0
            self.current_position_mm = 0.0
            await asyncio.sleep(home_time)

    async def _execute_laser(self, laser: LaserSetParams | LaserRampParams) -> None:
        """Execute laser operation (set or ramp)."""
        if isinstance(laser, LaserSetParams):
            await self._execute_laser_set(laser)
        elif isinstance(laser, LaserRampParams):
            await self._execute_laser_ramp(laser)

    async def _execute_laser_set(self, params: LaserSetParams) -> None:
        """Execute set laser power."""
        power_watts = params.power_watts

        logger.debug(f"Setting laser power to {power_watts:.2f}W")

        if self.laser:
            # Convert watts to milliamps (hardware uses mA)
            # Note: Actual conversion depends on laser specs
            # Using 1W = 1000mA as placeholder (needs calibration)
            current_ma = power_watts * 1000.0

            success = self.laser.set_current(current_ma)
            if not success:
                raise RuntimeError(f"Failed to set laser power to {power_watts}W")

        # Small delay for hardware response
        await asyncio.sleep(0.1)

    async def _execute_laser_ramp(self, params: LaserRampParams) -> None:
        """Execute laser power ramp."""
        start_watts = params.start_power_watts
        end_watts = params.end_power_watts
        duration_s = params.duration_s

        logger.debug(
            f"Ramping laser power from {start_watts:.2f}W to {end_watts:.2f}W "
            f"over {duration_s:.1f}s"
        )

        # Update interval (Hz)
        update_rate = 10
        update_interval = 1.0 / update_rate
        num_steps = int(duration_s * update_rate)

        for step in range(num_steps):
            # Check for stop/pause
            if self._stop_requested:
                raise RuntimeError("Execution stopped")
            await self._pause_event.wait()

            # Calculate current power (linear ramp)
            progress = step / num_steps if num_steps > 0 else 1.0
            current_power = start_watts + (end_watts - start_watts) * progress

            if self.laser:
                # Convert to milliamps
                current_ma = current_power * 1000.0

                success = self.laser.set_current(current_ma)
                if not success:
                    raise RuntimeError(
                        f"Failed to set laser power to {current_power:.2f}W during ramp"
                    )

            await asyncio.sleep(update_interval)

    async def _execute_dwell(self, params: DwellParams) -> None:
        """Execute dwell (wait) operation."""
        duration_s = params.duration_s

        logger.debug(f"Dwelling for {duration_s:.1f}s")

        # Break into smaller intervals to check for pause/stop
        remaining = duration_s
        interval = 0.1

        while remaining > 0:
            if self._stop_requested:
                raise RuntimeError("Execution stopped")
            await self._pause_event.wait()

            sleep_time = min(interval, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time

    def _perform_safety_checks(self) -> tuple[bool, str]:
        """
        Perform pre-execution safety checks.

        Verifies all safety conditions through SafetyManager before protocol execution.

        Returns:
            (safety_ok, message)
        """
        logger.debug("Performing safety checks...")

        # If no safety manager configured, allow execution (testing mode)
        if self.safety_manager is None:
            logger.warning("No safety manager configured - skipping safety checks (testing mode)")
            return True, "Safety checks skipped (testing mode)"

        # Check if laser enable is permitted
        if not self.safety_manager.is_laser_enable_permitted():
            status_text = self.safety_manager.get_safety_status_text()
            logger.error(f"Safety check failed: {status_text}")
            return False, f"Safety check failed: {status_text}"

        # All safety checks passed
        logger.info("Safety checks passed - all interlocks satisfied")
        return True, "Safety checks passed - all interlocks satisfied"

    def _save_execution_record(self) -> None:
        """Save execution record to database."""
        # TODO(#100): Implement database persistence for line-based protocol execution
        logger.debug("Database persistence not yet implemented for line-based protocols")

    def pause(self) -> None:
        """Pause protocol execution."""
        if self.state == ExecutionState.RUNNING:
            self._pause_event.clear()
            self._set_state(ExecutionState.PAUSED)
            logger.info("Protocol execution paused")

    def resume(self) -> None:
        """Resume paused execution."""
        if self.state == ExecutionState.PAUSED:
            self._pause_event.set()
            self._set_state(ExecutionState.RUNNING)
            logger.info("Protocol execution resumed")

    def stop(self) -> None:
        """Stop protocol execution with selective shutdown."""
        logger.info("Stopping protocol execution")
        self._stop_requested = True
        self._pause_event.set()  # Unpause if paused
        self._set_state(ExecutionState.STOPPED)

        # SELECTIVE SHUTDOWN: Only disable laser (not camera/actuator/monitoring)
        if self.laser:
            self.laser.set_output(False)  # Disable laser output
            self.laser.set_current(0.0)  # Set current to zero for safety
            logger.info("Laser disabled (selective shutdown policy)")

    def _on_laser_enable_changed(self, enabled: bool) -> None:
        """
        Real-time safety callback - called when laser enable permission changes.

        SAFETY-CRITICAL: Implements continuous safety monitoring during protocol
        execution. If safety interlocks fail mid-protocol, immediately stops with
        selective shutdown (laser only).

        Args:
            enabled: True if laser permitted, False if denied
        """
        # Only act if currently executing
        if self.state != ExecutionState.RUNNING:
            return

        # If laser permission revoked, STOP IMMEDIATELY
        if not enabled:
            logger.critical(
                "SAFETY INTERLOCK FAILURE during line-based protocol execution - "
                "stopping protocol and disabling laser (selective shutdown)"
            )

            # Stop protocol (calls self.stop() which disables laser)
            self.stop()

            # Log for audit trail
            logger.warning(
                "Protocol stopped mid-execution due to safety system. "
                "Laser disabled (selective shutdown). "
                "Other systems remain operational for assessment."
            )

    def _set_state(self, new_state: ExecutionState) -> None:
        """Update execution state and notify callback."""
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary for logging/display."""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            "protocol_name": (
                self.current_protocol.protocol_name if self.current_protocol else None
            ),
            "state": self.state.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "total_lines_executed": len(
                [log for log in self.execution_log if log["event"] == "complete"]
            ),
            "loop_iterations": self.current_loop_iteration,
            "execution_log": self.execution_log,
        }
