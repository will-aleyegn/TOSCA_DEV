"""
Base mock implementation for hardware controllers.

Provides configurable mock base class for hardware controllers used in testing.
Supports simulation of connection failures, errors, delays, and state tracking.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from hardware.hardware_controller_base import HardwareControllerBase, QObjectABCMeta


class MockHardwareBase(HardwareControllerBase, metaclass=QObjectABCMeta):
    """
    Concrete mock implementation of HardwareControllerBase for testing.

    Provides configurable behaviors to simulate hardware scenarios:
    - Connection failures
    - Operation errors
    - Response delays (timeout simulation)
    - Call tracking for verification
    """

    def __init__(self, event_logger: Optional[Any] = None) -> None:
        """Initialize mock with default configurable states."""
        super().__init__(event_logger)

        # Configurable test behaviors
        self.simulate_connection_failure: bool = False
        self.simulate_status_error: bool = False
        self.response_delay_s: float = 0.0
        self.error_message: str = "Simulated hardware error"

        # State tracking for verification
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self.connect_kwargs: dict[str, Any] | None = None
        self.disconnect_call_count: int = 0

    def reset(self) -> None:
        """Reset all configuration and state-tracking to defaults."""
        self.simulate_connection_failure = False
        self.simulate_status_error = False
        self.response_delay_s = 0.0
        self.error_message = "Simulated hardware error"

        self.call_log.clear()
        self.connect_kwargs = None
        self.disconnect_call_count = 0
        self.is_connected = False

    def connect(self, **kwargs: Any) -> bool:
        """Simulate connecting to hardware."""
        self.call_log.append(("connect", kwargs))
        self.connect_kwargs = kwargs

        if self.response_delay_s > 0:
            time.sleep(self.response_delay_s)

        if self.simulate_connection_failure:
            self.is_connected = False
            self.error_occurred.emit("Simulated connection failure")
            self.connection_changed.emit(False)
            return False

        self.is_connected = True
        self.connection_changed.emit(True)
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from hardware."""
        self.call_log.append(("disconnect", {}))
        self.disconnect_call_count += 1

        if self.response_delay_s > 0:
            time.sleep(self.response_delay_s)

        if self.is_connected:
            self.is_connected = False
            self.connection_changed.emit(False)

    def get_status(self) -> dict[str, Any]:
        """Simulate getting hardware status."""
        self.call_log.append(("get_status", {}))

        if self.response_delay_s > 0:
            time.sleep(self.response_delay_s)

        if not self.is_connected:
            self.error_occurred.emit("Hardware not connected")
            return {"connected": False}

        if self.simulate_status_error:
            self.error_occurred.emit(self.error_message)
            return {"connected": True, "error": True}

        return self._get_mock_status()

    def _get_mock_status(self) -> dict[str, Any]:
        """
        Provide default status dictionary.

        Subclasses override this for device-specific status.
        """
        return {"connected": True, "is_mock": True}
