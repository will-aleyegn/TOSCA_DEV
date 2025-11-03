"""
Protocol execution engine for running action-based treatment protocols.

Executes protocols with real-time control, safety monitoring, and logging.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.protocol import (
    LoopParams,
    MoveActuatorParams,
    Protocol,
    ProtocolAction,
    RampLaserPowerParams,
    SetLaserPowerParams,
    WaitParams,
)

logger = logging.getLogger(__name__)

# Configuration constants
MAX_RETRIES = 3  # Maximum number of retries for hardware operations
RETRY_DELAY = 1.0  # Delay between retries in seconds
ACTION_TIMEOUT = 60.0  # Maximum time for any single action in seconds


class ExecutionState(Enum):
    """Protocol execution states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class ProtocolEngine:
    """
    Execute action-based protocols with real-time hardware control.

    Manages protocol execution lifecycle, safety checks, and event logging.
    """

    def __init__(
        self,
        laser_controller: Optional[Any] = None,
        actuator_controller: Optional[Any] = None,
        safety_manager: Optional[Any] = None,
    ) -> None:
        """
        Initialize protocol engine.

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
            logger.info("Protocol engine connected to real-time safety monitoring")

        self.state = ExecutionState.IDLE
        self.current_protocol: Optional[Protocol] = None
        self.current_action_id: Optional[int] = None

        self.execution_log: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially
        self._stop_requested = False

        # Callbacks for UI updates
        self.on_action_start: Optional[Callable[[ProtocolAction], None]] = None
        self.on_action_complete: Optional[Callable[[ProtocolAction], None]] = None
        self.on_progress_update: Optional[Callable[[float], None]] = None
        self.on_state_change: Optional[Callable[[ExecutionState], None]] = None

    async def execute_protocol(
        self, protocol: Protocol, record: bool = False, stop_on_error: bool = True
    ) -> tuple[bool, str]:
        """
        Execute protocol from start to finish.

        Args:
            protocol: Protocol to execute
            record: Whether to record execution to database
            stop_on_error: If False, continue with next action on non-critical failures

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
        self._set_state(ExecutionState.RUNNING)
        self.stop_on_error = stop_on_error

        logger.info(f"Starting protocol execution: {protocol.protocol_name}")

        failed_actions = []
        try:
            # Execute all actions
            failed_actions = await self._execute_actions_with_recovery(protocol.actions)

            # Execution completed
            self.end_time = datetime.now()

            # Determine final state based on failures
            if failed_actions and stop_on_error:
                self._set_state(ExecutionState.ERROR)
                error_msg = f"Protocol failed with {len(failed_actions)} errors"
                logger.error(error_msg)
                return False, error_msg
            elif failed_actions:
                self._set_state(ExecutionState.COMPLETED)
                duration = (self.end_time - self.start_time).total_seconds()
                warning_msg = (
                    f"Protocol completed with warnings in {duration:.1f} seconds. "
                    f"{len(failed_actions)} non-critical actions failed."
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

    async def _execute_actions_with_recovery(
        self, actions: List[ProtocolAction]
    ) -> List[ProtocolAction]:
        """Execute actions with optional error recovery."""
        failed_actions = []

        for action in actions:
            # Check for stop request
            if self._stop_requested:
                logger.info("Execution stopped by user")
                raise RuntimeError("Execution stopped by user")

            # Handle pause
            await self._pause_event.wait()

            try:
                # Execute action
                await self._execute_action(action)

            except Exception as e:
                # Check if this is a critical action (laser/actuator operations are critical)
                is_critical = isinstance(
                    action.parameters,
                    (SetLaserPowerParams, RampLaserPowerParams, MoveActuatorParams),
                )

                if self.stop_on_error or is_critical:
                    logger.error(f"Critical action {action.action_id} failed: {e}")
                    raise  # Re-raise to stop protocol
                else:
                    logger.warning(
                        f"Non-critical action {action.action_id} failed: {e}. Continuing..."
                    )
                    failed_actions.append(action)

        return failed_actions

    async def _execute_action(self, action: ProtocolAction) -> None:
        """Execute single protocol action with timeout and error handling."""
        self.current_action_id = action.action_id
        logger.info(f"Executing action {action.action_id}: {action.action_type.value}")

        # Callback: action start
        if self.on_action_start:
            self.on_action_start(action)

        # Log action start
        self.execution_log.append(
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "timestamp": datetime.now().isoformat(),
                "event": "start",
            }
        )

        try:
            # Execute with timeout protection
            await asyncio.wait_for(self._execute_action_with_retry(action), timeout=ACTION_TIMEOUT)

            # Log action complete
            self.execution_log.append(
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "timestamp": datetime.now().isoformat(),
                    "event": "complete",
                }
            )

            # Callback: action complete
            if self.on_action_complete:
                self.on_action_complete(action)

        except asyncio.TimeoutError:
            error_msg = f"Action {action.action_id} timed out after {ACTION_TIMEOUT}s"
            logger.error(error_msg)
            self.execution_log.append(
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "timestamp": datetime.now().isoformat(),
                    "event": "timeout",
                    "error": error_msg,
                }
            )
            raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(f"Action {action.action_id} failed: {str(e)}")
            self.execution_log.append(
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "timestamp": datetime.now().isoformat(),
                    "event": "error",
                    "error": str(e),
                }
            )
            raise

    async def _execute_action_with_retry(self, action: ProtocolAction) -> None:
        """Execute action with retry logic for hardware operations."""
        # Actions that don't need retry (wait, loop)
        if isinstance(action.parameters, (WaitParams, LoopParams)):
            await self._execute_action_internal(action)
            return

        # Hardware operations with retry logic
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                await self._execute_action_internal(action)
                return  # Success, exit retry loop

            except RuntimeError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Action {action.action_id} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {RETRY_DELAY}s..."
                    )
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Action {action.action_id} failed after {MAX_RETRIES} attempts")

        # All retries failed
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"Action {action.action_id} failed without error details")

    async def _execute_action_internal(self, action: ProtocolAction) -> None:
        """Internal action execution without retry logic."""
        # Execute based on action type
        if isinstance(action.parameters, SetLaserPowerParams):
            await self._execute_set_laser_power(action.parameters)

        elif isinstance(action.parameters, RampLaserPowerParams):
            await self._execute_ramp_laser_power(action.parameters)

        elif isinstance(action.parameters, MoveActuatorParams):
            await self._execute_move_actuator(action.parameters)

        elif isinstance(action.parameters, WaitParams):
            await self._execute_wait(action.parameters)

        elif isinstance(action.parameters, LoopParams):
            await self._execute_loop(action.parameters)

    async def _execute_set_laser_power(self, params: SetLaserPowerParams) -> None:
        """Execute SetLaserPower action."""
        logger.debug(f"Setting laser power to {params.power_watts}W")

        if self.laser:
            # Convert watts to milliamps (hardware controller uses mA)
            # Note: Actual W->mA conversion depends on laser diode specs
            # For now, using 1W = 1000mA as placeholder (needs calibration)
            current_ma = params.power_watts * 1000.0

            success = self.laser.set_current(current_ma)
            if not success:
                raise RuntimeError(
                    f"Failed to set laser power to {params.power_watts}W ({current_ma}mA)"
                )

        # Small delay for hardware response
        await asyncio.sleep(0.1)

    async def _execute_ramp_laser_power(self, params: RampLaserPowerParams) -> None:
        """Execute RampLaserPower action."""
        logger.debug(
            f"Ramping laser power from {params.start_power_watts}W "
            f"to {params.end_power_watts}W over {params.duration_seconds}s"
        )

        # Update interval (Hz)
        update_rate = 10
        update_interval = 1.0 / update_rate
        num_steps = int(params.duration_seconds * update_rate)

        for step in range(num_steps):
            # Check for stop/pause
            if self._stop_requested:
                raise RuntimeError("Execution stopped")
            await self._pause_event.wait()

            # Calculate current power based on ramp type
            progress = step / num_steps
            current_power = self._calculate_ramp_value(
                params.start_power_watts,
                params.end_power_watts,
                progress,
                params.ramp_type,
            )

            if self.laser:
                # Convert watts to milliamps for hardware controller
                current_ma = current_power * 1000.0

                success = self.laser.set_current(current_ma)
                if not success:
                    raise RuntimeError(f"Failed to set laser power to {current_power}W during ramp")

            # Progress callback
            if self.on_progress_update:
                self.on_progress_update(progress)

            await asyncio.sleep(update_interval)

    def _calculate_ramp_value(
        self, start: float, end: float, progress: float, ramp_type: Any
    ) -> float:
        """Calculate ramped value based on ramp type."""
        from core.protocol import RampType

        if ramp_type == RampType.LINEAR:
            return start + (end - start) * progress

        elif ramp_type == RampType.LOGARITHMIC:
            import math

            # Logarithmic curve (starts fast, slows down)
            return start + (end - start) * math.log10(1 + 9 * progress)

        elif ramp_type == RampType.EXPONENTIAL:
            # Exponential curve (starts slow, speeds up)
            return start + (end - start) * (progress**2)

        else:  # CONSTANT
            return end

    async def _execute_move_actuator(self, params: MoveActuatorParams) -> None:
        """Execute MoveActuator action."""
        # Set laser power if specified for this move action
        if params.laser_power_watts is not None:
            logger.debug(f"Setting laser power to {params.laser_power_watts}W for move action")
            power_params = SetLaserPowerParams(power_watts=params.laser_power_watts)
            await self._execute_set_laser_power(power_params)

        logger.debug(
            f"Moving actuator to {params.target_position_um}µm " f"at {params.speed_um_per_sec}µm/s"
        )

        if self.actuator:
            # Set movement speed (controller expects int)
            speed_int = int(params.speed_um_per_sec)
            success = self.actuator.set_speed(speed_int)
            if not success:
                raise RuntimeError(f"Failed to set actuator speed to {speed_int}µm/s")

            # Move to target position
            success = self.actuator.set_position(params.target_position_um)
            if not success:
                raise RuntimeError(f"Failed to move actuator to {params.target_position_um}µm")

            # Estimate movement time for async sleep
            # Note: In real hardware, actuator emits position_reached signal when done
            # For protocol execution, we estimate time based on assumed current position
            # This is a limitation of not having synchronous position queries
            assumed_current = 1500.0  # µm (midpoint of typical range)
            distance = abs(params.target_position_um - assumed_current)
            move_time = distance / params.speed_um_per_sec if params.speed_um_per_sec > 0 else 1.0

            await asyncio.sleep(move_time)
        else:
            # Simulate movement time when no hardware connected
            assumed_current = 1500.0  # µm
            distance = abs(params.target_position_um - assumed_current)
            move_time = distance / params.speed_um_per_sec if params.speed_um_per_sec > 0 else 1.0
            await asyncio.sleep(move_time)

    async def _execute_wait(self, params: WaitParams) -> None:
        """Execute Wait action."""
        logger.debug(f"Waiting for {params.duration_seconds}s")

        # Break into smaller intervals to check for pause/stop
        remaining = params.duration_seconds
        interval = 0.1

        while remaining > 0:
            if self._stop_requested:
                raise RuntimeError("Execution stopped")
            await self._pause_event.wait()

            sleep_time = min(interval, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time

    async def _execute_loop(self, params: LoopParams) -> None:
        """Execute Loop action (repeated action sequence)."""
        if params.repeat_count == -1:
            # Infinite loop
            logger.info("Starting infinite loop (Ctrl+C to stop)")
            iteration = 0
            while not self._stop_requested:
                iteration += 1
                logger.debug(f"Loop iteration {iteration}")
                await self._execute_actions_with_recovery(params.actions)
        else:
            # Finite loop
            logger.debug(f"Starting loop: {params.repeat_count} iterations")
            for i in range(params.repeat_count):
                if self._stop_requested:
                    raise RuntimeError("Execution stopped")

                logger.debug(f"Loop iteration {i+1}/{params.repeat_count}")
                await self._execute_actions_with_recovery(params.actions)

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
        # TODO(#127): Implement database persistence for protocol execution records
        logger.debug("Database persistence not yet implemented for protocol execution")
        # raise NotImplementedError("Database persistence not yet implemented")

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
        """Stop protocol execution."""
        logger.info("Stopping protocol execution")
        self._stop_requested = True
        self._pause_event.set()  # Unpause if paused
        self._set_state(ExecutionState.STOPPED)

        # Emergency: turn off laser immediately (selective shutdown)
        if self.laser:
            self.laser.set_output(False)  # Disable laser output
            self.laser.set_current(0.0)  # Set current to zero for safety

    def _on_laser_enable_changed(self, enabled: bool) -> None:
        """
        Real-time safety callback - called when laser enable permission changes.

        SAFETY-CRITICAL: This implements continuous safety monitoring during protocol
        execution. If safety interlocks fail mid-protocol, this callback is triggered
        and immediately stops execution with selective shutdown (laser only).

        Args:
            enabled: True if laser is permitted, False if denied

        Note: This callback is connected to SafetyManager.laser_enable_changed signal.
        """
        # Only act if we're currently executing a protocol
        if self.state != ExecutionState.RUNNING:
            return

        # If laser permission revoked during execution, STOP IMMEDIATELY
        if not enabled:
            logger.critical(
                "SAFETY INTERLOCK FAILURE during protocol execution - "
                "stopping protocol and disabling laser (selective shutdown)"
            )

            # Stop protocol execution (calls self.stop() which disables laser)
            self.stop()

            # Log detailed reason for audit trail
            logger.warning(
                "Protocol stopped mid-execution due to safety system. "
                "Laser disabled (selective shutdown). "
                "Other systems (camera, actuator) remain operational for assessment."
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
            "total_actions_executed": len(
                [log for log in self.execution_log if log["event"] == "complete"]
            ),
            "execution_log": self.execution_log,
        }
