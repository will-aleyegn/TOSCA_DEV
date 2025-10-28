"""
Thread-safe protocol execution worker using Qt's QRunnable pattern.

This module provides a safe alternative to the dangerous asyncio-in-QThread
pattern, using QRunnable with QThreadPool for background protocol execution.
"""

import asyncio
import logging
import threading
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

logger = logging.getLogger(__name__)


class ProtocolWorkerSignals(QObject):
    """
    Signals for protocol execution worker.

    These signals are emitted from the worker thread but connected to slots
    in the main GUI thread via Qt's queued connection mechanism.
    """

    execution_started = pyqtSignal()
    execution_complete = pyqtSignal(bool, str)  # (success, message)
    execution_error = pyqtSignal(str)  # error_message
    progress_update = pyqtSignal(int, str)  # (percentage, status)
    action_executed = pyqtSignal(str, dict)  # (action_type, params)


class ProtocolWorker(QRunnable):
    """
    Thread-safe protocol execution worker.

    Executes treatment protocols in background thread using Qt's
    thread pool, avoiding the dangerous asyncio-in-QThread pattern.

    This implementation uses asyncio.run() to safely execute async
    protocol code within a self-contained event loop that exists
    only for the duration of this worker's execution.

    Safety Features:
    - Thread-safe cancellation via threading.Event
    - Proper error handling and logging
    - Progress reporting via Qt signals
    - Clean event loop lifecycle management
    """

    def __init__(self, protocol_engine: Any, protocol: Any) -> None:
        """
        Initialize protocol worker.

        Args:
            protocol_engine: Engine to execute protocol
            protocol: Protocol to execute
        """
        super().__init__()
        self.protocol_engine = protocol_engine
        self.protocol = protocol
        self.signals = ProtocolWorkerSignals()

        # Thread-safe cancellation event
        self._cancel_event = threading.Event()

        logger.debug(f"ProtocolWorker created for protocol: {protocol.name}")

    def run(self) -> None:
        """
        Execute protocol in background thread.

        This method runs in a worker thread from QThreadPool. It creates
        a self-contained asyncio event loop using asyncio.run(), which is
        safe because the loop exists entirely within this thread and does
        not conflict with Qt's main event loop.
        """
        try:
            # Check for early cancellation
            if self._cancel_event.is_set():
                logger.info("Protocol cancelled before execution started")
                self.signals.execution_complete.emit(False, "Cancelled before start")
                return

            logger.info(f"Starting protocol execution: {self.protocol.name}")
            self.signals.execution_started.emit()

            # SAFE PATTERN: Use asyncio.run() to execute async protocol code.
            # The event loop is created, used, and destroyed entirely within
            # this worker thread. No interaction with Qt's event loop.
            #
            # Note: This assumes protocol_engine.execute_protocol accepts
            # a cancel_event parameter for graceful cancellation.
            success, message = asyncio.run(
                self.protocol_engine.execute_protocol(
                    self.protocol,
                    record=True,
                    cancel_event=self._cancel_event,
                    progress_callback=self._on_progress,
                )
            )

            # Check if cancellation occurred during execution
            if self._cancel_event.is_set():
                logger.info("Protocol execution was cancelled")
                self.signals.execution_complete.emit(False, "Execution cancelled")
            else:
                self.signals.execution_complete.emit(success, message)
                logger.info(f"Protocol execution complete: {success}, {message}")

        except asyncio.CancelledError:
            # Handle async cancellation
            logger.info("Protocol execution cancelled (CancelledError)")
            self.signals.execution_complete.emit(False, "Execution cancelled")

        except Exception as e:
            # Catch all other exceptions
            logger.error(f"Protocol execution error: {e}", exc_info=True)
            self.signals.execution_error.emit(str(e))

    def _on_progress(
        self, percentage: int, status: str, action_type: str = None, params: dict = None
    ) -> None:
        """
        Progress callback for protocol execution.

        This method is called by the protocol engine to report progress.
        It emits Qt signals that are safely delivered to the GUI thread.

        Args:
            percentage: Progress percentage (0-100)
            status: Current status message
            action_type: Optional action type being executed
            params: Optional action parameters
        """
        self.signals.progress_update.emit(percentage, status)

        if action_type and params:
            self.signals.action_executed.emit(action_type, params)

    def cancel(self) -> None:
        """
        Request cancellation of protocol execution.

        This is thread-safe and can be called from the GUI thread.
        The worker checks the cancel event periodically during execution.

        Note: Cancellation is cooperative - the protocol engine must
        check the cancel_event and respond appropriately.
        """
        logger.info("Protocol execution cancellation requested")
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        """
        Check if cancellation has been requested.

        Returns:
            True if cancellation requested, False otherwise
        """
        return self._cancel_event.is_set()
