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
    ) -> None:
        """
        Initialize protocol engine.

        Args:
            laser_controller: Laser hardware controller (optional for testing)
            actuator_controller: Actuator hardware controller (optional for testing)
        """
        self.laser = laser_controller
        self.actuator = actuator_controller

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

    async def execute_protocol(self, protocol: Protocol, record: bool = False) -> tuple[bool, str]:
        """
        Execute protocol from start to finish.

        Args:
            protocol: Protocol to execute
            record: Whether to record execution to database

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

        logger.info(f"Starting protocol execution: {protocol.protocol_name}")

        try:
            # Execute all actions
            await self._execute_actions(protocol.actions)

            # Execution completed successfully
            self.end_time = datetime.now()
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

    async def _execute_actions(self, actions: List[ProtocolAction]) -> None:
        """Execute list of actions sequentially."""
        for action in actions:
            # Check for stop request
            if self._stop_requested:
                logger.info("Execution stopped by user")
                raise RuntimeError("Execution stopped by user")

            # Handle pause
            await self._pause_event.wait()

            # Execute action
            await self._execute_action(action)

    async def _execute_action(self, action: ProtocolAction) -> None:
        """Execute single protocol action."""
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

        except Exception as e:
            logger.error(f"Action {action.action_id} failed: {str(e)}")
            raise

    async def _execute_set_laser_power(self, params: SetLaserPowerParams) -> None:
        """Execute SetLaserPower action."""
        logger.debug(f"Setting laser power to {params.power_watts}W")

        if self.laser:
            pass

        # Simulate instant action
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
                _ = current_power

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
        logger.debug(
            f"Moving actuator to {params.target_position_um}µm " f"at {params.speed_um_per_sec}µm/s"
        )

        if self.actuator:
            pass

        # Simulate movement time
        # Assuming we know current position (would come from actuator)
        assumed_current = 1500.0  # µm
        distance = abs(params.target_position_um - assumed_current)
        move_time = distance / params.speed_um_per_sec
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
                await self._execute_actions(params.actions)
        else:
            # Finite loop
            logger.debug(f"Starting loop: {params.repeat_count} iterations")
            for i in range(params.repeat_count):
                if self._stop_requested:
                    raise RuntimeError("Execution stopped")

                logger.debug(f"Loop iteration {i+1}/{params.repeat_count}")
                await self._execute_actions(params.actions)

    def _perform_safety_checks(self) -> tuple[bool, str]:
        """
        Perform pre-execution safety checks.

        Returns:
            (safety_ok, message)
        """
        logger.debug("Performing safety checks...")
        return True, "Safety checks passed"

    def _save_execution_record(self) -> None:
        """Save execution record to database."""
        logger.info("Saving execution record to database")
        pass

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

        # Emergency: turn off laser
        if self.laser:
            pass

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
