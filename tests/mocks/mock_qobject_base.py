"""
Common base class for QObject-based hardware mocks.

Provides shared functionality for mocking QObject controllers without
requiring HardwareControllerBase inheritance.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from PyQt6.QtCore import QObject


class MockQObjectBase(QObject):
    """
    Base class for QObject-based hardware mocks.

    Provides common functionality:
    - Call logging for verification
    - Configurable response delays
    - Simulation of connection and operation errors
    - Reset mechanism for test isolation
    """

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize mock state and configuration."""
        super().__init__(parent)
        self.reset()

    def reset(self) -> None:
        """Reset mock to initial state for test isolation."""
        # Configurable behaviors
        self.simulate_connection_failure: bool = False
        self.simulate_operation_error: bool = False
        self.error_message: str = "Simulated hardware error"
        self.response_delay_s: float = 0.0

        # State tracking
        self.call_log: list[tuple[str, dict[str, Any]]] = []

    def _log_call(self, func_name: str, **kwargs: Any) -> None:
        """Log method call for test verification."""
        self.call_log.append((func_name, kwargs))

    def _apply_delay(self) -> None:
        """Apply configured delay to simulate slow hardware."""
        if self.response_delay_s > 0:
            time.sleep(self.response_delay_s)
