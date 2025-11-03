"""
Common base class for QObject-based hardware mocks.

Provides shared functionality for mocking QObject controllers without
requiring HardwareControllerBase inheritance.

Advanced failure simulation capabilities:
- Intermittent failures (random failure injection)
- Timeout simulation (configurable operation timeouts)
- Device busy states (temporary unavailability)
- Hardware limit violations
- Serial communication errors
- Power supply failures
- Calibration failures
- Error state persistence
- Realistic error message generation
"""

from __future__ import annotations

import random
import time
from enum import Enum
from typing import Any, Optional

from PyQt6.QtCore import QObject


class FailureMode(Enum):
    """Enumeration of available failure modes."""

    NONE = "none"
    CONNECTION_FAILURE = "connection_failure"
    OPERATION_ERROR = "operation_error"
    TIMEOUT = "timeout"
    DEVICE_BUSY = "device_busy"
    COMMUNICATION_ERROR = "communication_error"
    POWER_FAILURE = "power_failure"
    CALIBRATION_ERROR = "calibration_error"
    HARDWARE_LIMIT_VIOLATION = "hardware_limit_violation"
    INTERMITTENT_FAILURE = "intermittent_failure"


class MockQObjectBase(QObject):
    """
    Base class for QObject-based hardware mocks.

    Provides common functionality:
    - Call logging for verification
    - Configurable response delays
    - Simulation of connection and operation errors
    - Reset mechanism for test isolation

    Advanced failure simulation:
    - Intermittent failures with configurable probability
    - Timeout simulation for slow/stuck operations
    - Device busy states
    - Communication errors
    - Power supply failures
    - Calibration failures
    - Hardware limit violations
    - Error state persistence
    - Realistic error message generation
    """

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock state and configuration."""
        super().__init__(parent)
        self.reset()

    def reset(self) -> None:
        """Reset mock to initial state for test isolation."""
        # Basic failure simulation (backward compatible)
        self.simulate_connection_failure: bool = False
        self.simulate_operation_error: bool = False
        self.error_message: str = "Simulated hardware error"
        self.response_delay_s: float = 0.0

        # Advanced failure simulation
        self.failure_mode: FailureMode = FailureMode.NONE
        self.intermittent_failure_probability: float = 0.0  # 0.0-1.0
        self.timeout_threshold_s: float = 5.0  # Operations timeout after this
        self.device_busy_duration_s: float = 1.0  # How long device stays busy
        self.calibration_required: bool = False
        self.power_supply_voltage_v: float = 12.0  # Nominal voltage
        self.min_power_voltage_v: float = 10.0  # Minimum required voltage
        self.hardware_limits: dict[str, tuple[float, float]] = {}  # {param: (min, max)}
        self.persist_error_state: bool = False  # Keep error state across calls
        self.current_error_state: Optional[str] = None  # Active error message

        # State tracking
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._busy_until: float = 0.0  # Timestamp when device becomes available
        self._operation_start_time: float = 0.0  # Track operation duration
        self._last_calibration_time: float = time.time()
        self._failure_count: int = 0  # Track number of failures

        # Signal emission tracking
        self.signal_log: list[tuple[str, tuple[Any, ...], float]] = (
            []
        )  # (signal_name, args, timestamp)
        self.enable_signal_logging: bool = True  # Enable/disable signal logging
        self._last_signal_time: dict[str, float] = {}  # Track last emission time per signal

    def _log_call(self, func_name: str, **kwargs: Any) -> None:
        """Log method call for test verification."""
        self.call_log.append((func_name, kwargs))

    def _apply_delay(self) -> None:
        """Apply configured delay to simulate slow hardware."""
        if self.response_delay_s > 0:
            time.sleep(self.response_delay_s)

    # Advanced failure simulation methods

    def _should_fail(self) -> tuple[bool, Optional[str]]:
        """
        Check if operation should fail based on current failure modes.

        Returns:
            Tuple of (should_fail, error_message)
        """
        # Check for persistent error state
        if self.persist_error_state and self.current_error_state:
            return (True, self.current_error_state)

        # Check basic failure modes (backward compatible)
        if self.simulate_connection_failure:
            return (True, "Connection failed (simulated)")
        if self.simulate_operation_error:
            return (True, self.error_message)

        # Check advanced failure modes
        if self.failure_mode == FailureMode.DEVICE_BUSY:
            is_busy, msg = self._check_device_busy()
            if is_busy:
                return (True, msg)

        if self.failure_mode == FailureMode.TIMEOUT:
            is_timeout, msg = self._check_timeout()
            if is_timeout:
                return (True, msg)

        if self.failure_mode == FailureMode.POWER_FAILURE:
            power_ok, msg = self._check_power_supply()
            if not power_ok:
                return (True, msg)

        if self.failure_mode == FailureMode.CALIBRATION_ERROR:
            calibrated, msg = self._check_calibration()
            if not calibrated:
                return (True, msg)

        if self.failure_mode == FailureMode.COMMUNICATION_ERROR:
            return (True, "Serial communication error (simulated)")

        if self.failure_mode == FailureMode.INTERMITTENT_FAILURE:
            fails, msg = self._check_intermittent_failure()
            if fails:
                return (True, msg)

        return (False, None)

    def _check_intermittent_failure(self) -> tuple[bool, Optional[str]]:
        """
        Check if intermittent failure should occur.

        Returns:
            Tuple of (should_fail, error_message)
        """
        if random.random() < self.intermittent_failure_probability:
            self._failure_count += 1
            return (
                True,
                f"Intermittent failure #{self._failure_count} (simulated)",
            )
        return (False, None)

    def _check_device_busy(self) -> tuple[bool, Optional[str]]:
        """
        Check if device is currently busy.

        Returns:
            Tuple of (is_busy, error_message)
        """
        current_time = time.time()
        if current_time < self._busy_until:
            remaining_s = self._busy_until - current_time
            return (True, f"Device busy (available in {remaining_s:.1f}s)")
        return (False, None)

    def _check_timeout(self) -> tuple[bool, Optional[str]]:
        """
        Check if operation has timed out.

        Returns:
            Tuple of (timed_out, error_message)
        """
        if self._operation_start_time > 0:
            elapsed = time.time() - self._operation_start_time
            if elapsed > self.timeout_threshold_s:
                return (
                    True,
                    f"Operation timeout after {elapsed:.1f}s (threshold: {self.timeout_threshold_s}s)",
                )
        return (False, None)

    def _check_power_supply(self) -> tuple[bool, Optional[str]]:
        """
        Check if power supply voltage is sufficient.

        Returns:
            Tuple of (power_ok, error_message)
        """
        if self.power_supply_voltage_v < self.min_power_voltage_v:
            return (
                False,
                f"Insufficient power: {self.power_supply_voltage_v}V "
                f"(minimum: {self.min_power_voltage_v}V)",
            )
        return (True, None)

    def _check_calibration(self) -> tuple[bool, Optional[str]]:
        """
        Check if device calibration is valid.

        Returns:
            Tuple of (calibrated, error_message)
        """
        if self.calibration_required:
            time_since_cal = time.time() - self._last_calibration_time
            return (
                False,
                f"Calibration required (last calibrated {time_since_cal:.0f}s ago)",
            )
        return (True, None)

    def _check_hardware_limits(self, parameter: str, value: float) -> tuple[bool, Optional[str]]:
        """
        Check if parameter value is within hardware limits.

        Args:
            parameter: Parameter name
            value: Value to check

        Returns:
            Tuple of (within_limits, error_message)
        """
        if parameter in self.hardware_limits:
            min_val, max_val = self.hardware_limits[parameter]
            if value < min_val:
                return (
                    False,
                    f"{parameter} {value} below minimum {min_val}",
                )
            if value > max_val:
                return (
                    False,
                    f"{parameter} {value} above maximum {max_val}",
                )
        return (True, None)

    def _set_busy_state(self) -> None:
        """Set device to busy state for configured duration."""
        self._busy_until = time.time() + self.device_busy_duration_s

    def _start_operation(self) -> None:
        """Mark start of operation for timeout tracking."""
        self._operation_start_time = time.time()

    def _end_operation(self) -> None:
        """Mark end of operation."""
        self._operation_start_time = 0.0

    def _set_error_state(self, error_message: str) -> None:
        """
        Set persistent error state.

        Args:
            error_message: Error message to persist
        """
        if self.persist_error_state:
            self.current_error_state = error_message
            self._failure_count += 1

    def _clear_error_state(self) -> None:
        """Clear persistent error state."""
        self.current_error_state = None

    def perform_calibration(self) -> bool:
        """
        Perform device calibration (for testing calibration failures).

        Returns:
            True if successful
        """
        if self.failure_mode == FailureMode.CALIBRATION_ERROR:
            return False

        self._last_calibration_time = time.time()
        self.calibration_required = False
        return True

    def get_failure_statistics(self) -> dict[str, Any]:
        """
        Get failure simulation statistics.

        Returns:
            Dictionary with failure statistics
        """
        return {
            "failure_count": self._failure_count,
            "failure_mode": self.failure_mode.value,
            "current_error_state": self.current_error_state,
            "device_busy": time.time() < self._busy_until,
            "operation_in_progress": self._operation_start_time > 0,
            "calibration_required": self.calibration_required,
            "power_voltage_v": self.power_supply_voltage_v,
            "call_count": len(self.call_log),
        }

    # Signal emission tracking and validation methods

    def _log_signal_emission(self, signal_name: str, *args: Any) -> None:
        """
        Log signal emission for verification and debugging.

        Args:
            signal_name: Name of the emitted signal
            *args: Signal parameters
        """
        if self.enable_signal_logging:
            timestamp = time.time()
            self.signal_log.append((signal_name, args, timestamp))
            self._last_signal_time[signal_name] = timestamp

    def get_signal_emissions(
        self, signal_name: Optional[str] = None
    ) -> list[tuple[str, tuple[Any, ...], float]]:
        """
        Get logged signal emissions.

        Args:
            signal_name: Optional filter for specific signal name

        Returns:
            List of (signal_name, args, timestamp) tuples
        """
        if signal_name is None:
            return self.signal_log.copy()
        return [entry for entry in self.signal_log if entry[0] == signal_name]

    def get_signal_emission_count(self, signal_name: str) -> int:
        """
        Get number of times a signal was emitted.

        Args:
            signal_name: Name of the signal

        Returns:
            Number of emissions
        """
        return len(self.get_signal_emissions(signal_name))

    def was_signal_emitted(self, signal_name: str) -> bool:
        """
        Check if a signal was emitted at least once.

        Args:
            signal_name: Name of the signal

        Returns:
            True if signal was emitted
        """
        return self.get_signal_emission_count(signal_name) > 0

    def get_last_signal_args(self, signal_name: str) -> Optional[tuple[Any, ...]]:
        """
        Get arguments from the last emission of a signal.

        Args:
            signal_name: Name of the signal

        Returns:
            Tuple of signal arguments, or None if never emitted
        """
        emissions = self.get_signal_emissions(signal_name)
        if not emissions:
            return None
        return emissions[-1][1]

    def get_signal_timing(self, signal_name: str) -> Optional[float]:
        """
        Get timestamp of last emission for a signal.

        Args:
            signal_name: Name of the signal

        Returns:
            Timestamp of last emission, or None if never emitted
        """
        return self._last_signal_time.get(signal_name)

    def get_signal_interval(self, signal_name: str) -> Optional[float]:
        """
        Get time interval between last two emissions of a signal.

        Args:
            signal_name: Name of the signal

        Returns:
            Time interval in seconds, or None if less than 2 emissions
        """
        emissions = self.get_signal_emissions(signal_name)
        if len(emissions) < 2:
            return None
        return emissions[-1][2] - emissions[-2][2]

    def verify_signal_sequence(self, *signal_names: str) -> bool:
        """
        Verify that signals were emitted in the expected sequence.

        Args:
            *signal_names: Expected signal names in order

        Returns:
            True if signals were emitted in the specified order
        """
        if not signal_names:
            return True

        # Extract signal names from log in order
        emitted_sequence = [entry[0] for entry in self.signal_log]

        # Find the subsequence
        seq_idx = 0
        for signal_name in emitted_sequence:
            if seq_idx < len(signal_names) and signal_name == signal_names[seq_idx]:
                seq_idx += 1

        return seq_idx == len(signal_names)

    def verify_signal_parameters(self, signal_name: str, expected_args: tuple[Any, ...]) -> bool:
        """
        Verify that a signal was emitted with expected parameters.

        Args:
            signal_name: Name of the signal
            expected_args: Expected signal arguments

        Returns:
            True if signal was emitted with matching parameters
        """
        emissions = self.get_signal_emissions(signal_name)
        return any(args == expected_args for _, args, _ in emissions)

    def clear_signal_log(self) -> None:
        """Clear signal emission log."""
        self.signal_log.clear()
        self._last_signal_time.clear()

    def get_signal_statistics(self) -> dict[str, Any]:
        """
        Get signal emission statistics.

        Returns:
            Dictionary with signal statistics
        """
        # Count emissions per signal
        signal_counts: dict[str, int] = {}
        for signal_name, _, _ in self.signal_log:
            signal_counts[signal_name] = signal_counts.get(signal_name, 0) + 1

        return {
            "total_emissions": len(self.signal_log),
            "unique_signals": len(signal_counts),
            "signal_counts": signal_counts,
            "logging_enabled": self.enable_signal_logging,
        }
