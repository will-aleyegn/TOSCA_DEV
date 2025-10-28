# TOSCA UI Redesign - Code Review Implementation Plan

**Date:** 2025-10-27
**Review Type:** Comprehensive Safety & Architecture Review
**Priority:** CRITICAL - Thread safety issue must be fixed immediately

---

## Executive Summary

Comprehensive code review identified **1 critical**, **3 high priority**, and **4 medium/low priority** issues. The most urgent finding is a thread safety violation that could cause crashes during treatment execution. This document provides detailed implementation plans with code examples for each fix.

**Overall Code Grade: B** - Good architecture, critical safety issues need immediate attention

---

## 🔴 CRITICAL: Fix Protocol Execution Thread Safety (Day 1)

### Issue
**Location:** `src/ui/widgets/active_treatment_widget.py:49-55`
**Problem:** Creating asyncio event loop inside QThread violates both Qt and asyncio threading models
**Risk:** Race conditions, deadlocks, crashes during treatment execution

### Implementation Plan

#### Step 1: Create Protocol Worker Class
Create new file: `src/ui/workers/protocol_worker.py`

```python
"""Thread-safe protocol execution worker using Qt's QRunnable pattern."""

from typing import Any, Optional
import logging
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

logger = logging.getLogger(__name__)


class ProtocolWorkerSignals(QObject):
    """Signals for protocol execution worker."""

    execution_started = pyqtSignal()
    execution_complete = pyqtSignal(bool, str)  # (success, message)
    execution_error = pyqtSignal(str)  # error_message
    progress_update = pyqtSignal(int, str)  # (percentage, status)
    action_executed = pyqtSignal(str, dict)  # (action_type, params)


class ProtocolWorker(QRunnable):
    """
    Thread-safe protocol execution worker.

    Executes treatment protocols in background thread using Qt's
    thread pool, avoiding dangerous asyncio-in-QThread pattern.
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
        self._is_cancelled = False

    def run(self) -> None:
        """Execute protocol in background thread."""
        try:
            logger.info(f"Starting protocol execution: {self.protocol.name}")
            self.signals.execution_started.emit()

            # Convert async to sync execution
            # If protocol_engine.execute_protocol is async, we need sync version
            if hasattr(self.protocol_engine, 'execute_protocol_sync'):
                success, message = self.protocol_engine.execute_protocol_sync(
                    self.protocol,
                    record=True,
                    progress_callback=self._on_progress
                )
            else:
                # Fallback: Create sync wrapper if needed
                success, message = self._execute_sync(self.protocol)

            self.signals.execution_complete.emit(success, message)
            logger.info(f"Protocol execution complete: {success}, {message}")

        except Exception as e:
            logger.error(f"Protocol execution error: {e}", exc_info=True)
            self.signals.execution_error.emit(str(e))

    def _execute_sync(self, protocol: Any) -> tuple[bool, str]:
        """
        Synchronous protocol execution wrapper.

        This should be implemented in protocol_engine.py as a native
        sync method, but provided here as fallback.
        """
        # Implementation depends on protocol engine structure
        # This is a placeholder showing the pattern
        try:
            for i, action in enumerate(protocol.actions):
                if self._is_cancelled:
                    return False, "Execution cancelled"

                # Execute action
                self.protocol_engine.execute_action(action)

                # Report progress
                progress = int((i + 1) / len(protocol.actions) * 100)
                self._on_progress(progress, f"Executing: {action.type}")

            return True, "Protocol completed successfully"

        except Exception as e:
            return False, f"Execution failed: {str(e)}"

    def _on_progress(self, percentage: int, status: str) -> None:
        """Progress callback for protocol execution."""
        self.signals.progress_update.emit(percentage, status)

    def cancel(self) -> None:
        """Request cancellation of protocol execution."""
        self._is_cancelled = True
        logger.info("Protocol execution cancellation requested")
```

#### Step 2: Update ActiveTreatmentWidget

Update `src/ui/widgets/active_treatment_widget.py`:

```python
# Remove the ProtocolExecutionThread class entirely (lines 33-61)
# Add new imports
from PyQt6.QtCore import QThreadPool
from ui.workers.protocol_worker import ProtocolWorker

class ActiveTreatmentWidget(QWidget):
    """Active treatment monitoring dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self.protocol_engine: Optional[Any] = None
        self.safety_manager: Optional[Any] = None
        self.camera_widget: Optional[Any] = None
        self.current_worker: Optional[ProtocolWorker] = None  # Track active worker

        # ... rest of initialization ...

    def start_protocol_execution(self, protocol: Any) -> None:
        """
        Start protocol execution in background thread.

        Args:
            protocol: Protocol to execute
        """
        if not self.protocol_engine:
            logger.error("Protocol engine not set")
            self._log_event("ERROR: Protocol engine not configured", urgent=True)
            return

        if self.current_worker:
            logger.warning("Protocol already executing")
            return

        # Create worker
        self.current_worker = ProtocolWorker(self.protocol_engine, protocol)

        # Connect signals
        self.current_worker.signals.execution_started.connect(self._on_execution_started)
        self.current_worker.signals.execution_complete.connect(self._on_execution_complete)
        self.current_worker.signals.execution_error.connect(self._on_execution_error)
        self.current_worker.signals.progress_update.connect(self._on_progress_update)

        # Start execution in thread pool
        QThreadPool.globalInstance().start(self.current_worker)
        logger.info("Protocol execution started in background thread")

    def _on_execution_started(self) -> None:
        """Handle protocol execution start."""
        self._log_event("Protocol execution started")
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Executing")

    def _on_execution_complete(self, success: bool, message: str) -> None:
        """
        Handle protocol execution completion.

        Args:
            success: Whether execution was successful
            message: Completion message
        """
        status = "COMPLETE" if success else "FAILED"
        self._log_event(f"Protocol {status}: {message}")
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else self.progress_bar.value())
        self.status_label.setText(f"Status: {status}")
        self.current_worker = None

    def _on_execution_error(self, error_message: str) -> None:
        """
        Handle protocol execution error.

        Args:
            error_message: Error description
        """
        self._log_event(f"ERROR: {error_message}", urgent=True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: ERROR")
        self.current_worker = None

        # Show error dialog
        QMessageBox.critical(self, "Execution Error",
                            f"Protocol execution failed:\n{error_message}")

    def _on_progress_update(self, percentage: int, status: str) -> None:
        """
        Handle progress updates.

        Args:
            percentage: Progress percentage (0-100)
            status: Current status message
        """
        self.progress_bar.setValue(percentage)
        self.action_label.setText(status)

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        if self.current_worker:
            self.current_worker.cancel()
            self._log_event("Stop requested - cancelling protocol")

        if self.protocol_engine:
            self.protocol_engine.stop()

        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Stopped")

    def cleanup(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Cleaning up ActiveTreatmentWidget...")

        # Cancel any running protocol
        if self.current_worker:
            self.current_worker.cancel()

        # Wait for thread pool to finish (with timeout)
        pool = QThreadPool.globalInstance()
        if not pool.waitForDone(2000):  # 2 second timeout
            logger.warning("Thread pool did not finish in time")

        # Stop protocol engine
        if self.protocol_engine and hasattr(self.protocol_engine, 'stop'):
            self.protocol_engine.stop()

        logger.info("ActiveTreatmentWidget cleanup complete")
```

#### Step 3: Testing Plan

1. **Unit Test:** Create `tests/test_protocol_worker.py`
2. **Integration Test:** Test with mock protocol engine
3. **Stress Test:** Run multiple protocols sequentially
4. **Failure Test:** Test cancellation and error handling

---

## 🟠 HIGH PRIORITY: Protocol Validation (Day 2-3)

### Issue
**Location:** `src/ui/widgets/treatment_setup_widget.py:180-199`
**Problem:** No validation of JSON protocol structure
**Risk:** Malformed protocols could crash system

### Implementation Plan

#### Step 1: Define Protocol Schema
Create new file: `src/core/protocol_schema.py`

```python
"""JSON schema definitions for treatment protocols."""

PROTOCOL_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "version", "actions"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "description": "Protocol name"
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Semantic version (e.g., 1.0.0)"
        },
        "description": {
            "type": "string",
            "maxLength": 500,
            "description": "Optional protocol description"
        },
        "created_by": {
            "type": "string",
            "description": "Protocol author"
        },
        "created_date": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 creation date"
        },
        "safety_checks": {
            "type": "object",
            "properties": {
                "max_laser_power": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 5.0,
                    "description": "Maximum laser power in watts"
                },
                "max_duration": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3600,
                    "description": "Maximum duration in seconds"
                }
            }
        },
        "actions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "items": {
                "type": "object",
                "required": ["action_type", "parameters"],
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": [
                            "move_absolute",
                            "move_relative",
                            "set_laser_power",
                            "laser_on",
                            "laser_off",
                            "delay",
                            "capture_image",
                            "wait_for_temp",
                            "set_motor_speed"
                        ]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Action-specific parameters"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional action comment"
                    }
                }
            }
        }
    }
}

# Parameter schemas for each action type
ACTION_PARAMETER_SCHEMAS = {
    "move_absolute": {
        "required": ["position"],
        "properties": {
            "position": {
                "type": "number",
                "minimum": 0,
                "maximum": 50000,
                "description": "Absolute position in micrometers"
            },
            "velocity": {
                "type": "number",
                "minimum": 0.5,
                "maximum": 400,
                "description": "Movement velocity in mm/s"
            }
        }
    },
    "set_laser_power": {
        "required": ["power"],
        "properties": {
            "power": {
                "type": "number",
                "minimum": 0,
                "maximum": 5.0,
                "description": "Laser power in watts"
            }
        }
    },
    "delay": {
        "required": ["duration"],
        "properties": {
            "duration": {
                "type": "number",
                "minimum": 0.001,
                "maximum": 60,
                "description": "Delay duration in seconds"
            }
        }
    }
    # ... more action parameter schemas ...
}
```

#### Step 2: Add Validation to TreatmentSetupWidget

Update `src/ui/widgets/treatment_setup_widget.py`:

```python
import json
import jsonschema
from pathlib import Path
from core.protocol_schema import PROTOCOL_SCHEMA_V1
from core.protocol import Protocol

class TreatmentSetupWidget(QWidget):

    def _on_load_protocol_clicked(self) -> None:
        """Handle protocol load button click with validation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Protocol File",
            str(Path.home() / "Documents" / "TOSCA" / "protocols"),
            "Protocol Files (*.json);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            # Read file
            with open(file_path, 'r') as f:
                protocol_data = json.load(f)

            # Validate against schema
            self._validate_protocol(protocol_data)

            # Additional safety validations
            self._validate_safety_limits(protocol_data)

            # Create protocol object
            self.loaded_protocol = Protocol.from_dict(protocol_data)

            # Update UI
            self.protocol_name_label.setText(f"Loaded: {self.loaded_protocol.name}")
            self.protocol_info_label.setText(
                f"Actions: {len(self.loaded_protocol.actions)}, "
                f"Version: {protocol_data.get('version', 'unknown')}"
            )

            # Update validation checklist
            self._update_validation_display()

            logger.info(f"Protocol loaded and validated: {self.loaded_protocol.name}")

        except FileNotFoundError:
            QMessageBox.critical(self, "File Not Found",
                               f"Protocol file not found:\n{file_path}")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON",
                               f"Failed to parse protocol file:\n{e}")
        except jsonschema.ValidationError as e:
            QMessageBox.critical(self, "Invalid Protocol",
                               f"Protocol validation failed:\n{e.message}\n\n"
                               f"Path: {'/'.join(str(x) for x in e.path)}")
        except ValueError as e:
            QMessageBox.critical(self, "Safety Violation",
                               f"Protocol failed safety checks:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Load Failed",
                               f"Failed to load protocol:\n{e}")
            logger.error(f"Protocol load error: {e}", exc_info=True)

    def _validate_protocol(self, protocol_data: dict) -> None:
        """
        Validate protocol against JSON schema.

        Args:
            protocol_data: Protocol dictionary to validate

        Raises:
            jsonschema.ValidationError: If validation fails
        """
        jsonschema.validate(instance=protocol_data, schema=PROTOCOL_SCHEMA_V1)
        logger.debug("Protocol passed schema validation")

    def _validate_safety_limits(self, protocol_data: dict) -> None:
        """
        Validate protocol against safety limits.

        Args:
            protocol_data: Protocol dictionary to validate

        Raises:
            ValueError: If safety limits are violated
        """
        # Check total duration
        total_duration = 0
        max_power = 0

        for action in protocol_data.get('actions', []):
            if action['action_type'] == 'delay':
                total_duration += action['parameters'].get('duration', 0)
            elif action['action_type'] == 'set_laser_power':
                power = action['parameters'].get('power', 0)
                max_power = max(max_power, power)

        # Enforce limits
        if total_duration > 3600:  # 1 hour max
            raise ValueError(f"Total duration ({total_duration}s) exceeds 1 hour limit")

        if max_power > 5.0:  # 5W max
            raise ValueError(f"Maximum power ({max_power}W) exceeds 5W limit")

        logger.debug(f"Protocol safety validation passed: "
                    f"duration={total_duration}s, max_power={max_power}W")
```

---

## 🟠 HIGH PRIORITY: Non-Blocking Hardware Connections (Day 3-4)

### Issue
**Locations:** `gpio_widget.py:295`, `laser_widget.py:274`, `actuator_widget.py:170`
**Problem:** Hardware connections block UI thread for 2+ seconds
**Risk:** UI freezes, poor user experience, missed safety events

### Implementation Plan

#### Step 1: Create Connection Worker
Create new file: `src/ui/workers/connection_worker.py`

```python
"""Thread-safe hardware connection worker."""

import logging
from typing import Any, Callable, Optional
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

logger = logging.getLogger(__name__)


class ConnectionWorkerSignals(QObject):
    """Signals for connection worker."""

    connection_started = pyqtSignal(str)  # device_name
    connection_complete = pyqtSignal(str, bool, str)  # (device, success, message)
    connection_error = pyqtSignal(str, str)  # (device, error)
    connection_progress = pyqtSignal(str, int, str)  # (device, percentage, status)


class ConnectionWorker(QRunnable):
    """
    Worker for hardware connections in background thread.

    Prevents UI blocking during long connection operations.
    """

    def __init__(self,
                 device_name: str,
                 controller: Any,
                 connect_fn: Callable,
                 connect_args: dict) -> None:
        """
        Initialize connection worker.

        Args:
            device_name: Name of device (for logging)
            controller: Hardware controller instance
            connect_fn: Connection function to call
            connect_args: Arguments for connection function
        """
        super().__init__()
        self.device_name = device_name
        self.controller = controller
        self.connect_fn = connect_fn
        self.connect_args = connect_args
        self.signals = ConnectionWorkerSignals()

    def run(self) -> None:
        """Execute connection in background thread."""
        try:
            logger.info(f"Starting connection to {self.device_name}")
            self.signals.connection_started.emit(self.device_name)

            # Report initial progress
            self.signals.connection_progress.emit(
                self.device_name, 10, "Opening port..."
            )

            # Perform connection
            success = self.connect_fn(**self.connect_args)

            # Report completion
            if success:
                message = f"{self.device_name} connected successfully"
                self.signals.connection_complete.emit(
                    self.device_name, True, message
                )
            else:
                message = f"{self.device_name} connection failed"
                self.signals.connection_complete.emit(
                    self.device_name, False, message
                )

            logger.info(f"Connection result: {message}")

        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"{self.device_name} {error_msg}", exc_info=True)
            self.signals.connection_error.emit(self.device_name, str(e))
```

#### Step 2: Update Hardware Widgets

Update each hardware widget to use connection worker. Example for `src/ui/widgets/gpio_widget.py`:

```python
from PyQt6.QtCore import QThreadPool, pyqtSlot
from ui.workers.connection_worker import ConnectionWorker

class GPIOWidget(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.controller = None
        self.is_connecting = False
        self.connection_worker = None
        # ... rest of init ...

    def _on_connect_clicked(self) -> None:
        """Handle connect button click - non-blocking."""
        if self.is_connecting:
            logger.warning("Connection already in progress")
            return

        logger.info("Initiating GPIO connection...")

        # Update UI immediately
        self.is_connecting = True
        self.connect_button.setEnabled(False)
        self.connection_status_label.setText("Connecting...")
        self.connection_status_label.setStyleSheet("color: #FFC107;")  # Yellow

        # Create controller if needed
        if not self.controller:
            try:
                from hardware.gpio_controller import GPIOController
                self.controller = GPIOController()
                # Connect signals
                self.controller.connection_changed.connect(self._on_connection_changed)
                self.controller.vibration_update.connect(self._on_vibration_update)
                self.controller.photodiode_update.connect(self._on_photodiode_update)
                self.controller.watchdog_heartbeat.connect(self._on_watchdog_heartbeat)
                self.controller.error_occurred.connect(self._on_error_occurred)
            except ImportError as e:
                logger.error(f"Failed to create GPIO controller: {e}")
                self.connection_status_label.setText("Import Error")
                self.connection_status_label.setStyleSheet("color: #F44336;")  # Red
                self.connect_button.setEnabled(True)
                self.is_connecting = False
                return

        # Get port from config or combo box
        config = get_config()
        port = config.hardware.gpio.com_port

        # Create worker
        self.connection_worker = ConnectionWorker(
            device_name="GPIO",
            controller=self.controller,
            connect_fn=self.controller.connect,
            connect_args={"port": port}
        )

        # Connect signals
        self.connection_worker.signals.connection_complete.connect(
            self._on_connection_complete
        )
        self.connection_worker.signals.connection_error.connect(
            self._on_connection_error
        )
        self.connection_worker.signals.connection_progress.connect(
            self._on_connection_progress
        )

        # Start in thread pool
        QThreadPool.globalInstance().start(self.connection_worker)

    @pyqtSlot(str, bool, str)
    def _on_connection_complete(self, device: str, success: bool, message: str) -> None:
        """
        Handle connection completion.

        Args:
            device: Device name
            success: Whether connection succeeded
            message: Status message
        """
        self.is_connecting = False
        self.connection_worker = None

        if success:
            self.connection_status_label.setText("Connected")
            self.connection_status_label.setStyleSheet("color: #4CAF50;")  # Green
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            logger.info(f"GPIO connected: {message}")
        else:
            self.connection_status_label.setText("Failed")
            self.connection_status_label.setStyleSheet("color: #F44336;")  # Red
            self.connect_button.setEnabled(True)
            logger.error(f"GPIO connection failed: {message}")

    @pyqtSlot(str, str)
    def _on_connection_error(self, device: str, error: str) -> None:
        """
        Handle connection error.

        Args:
            device: Device name
            error: Error message
        """
        self.is_connecting = False
        self.connection_worker = None
        self.connection_status_label.setText(f"Error: {error[:20]}")
        self.connection_status_label.setStyleSheet("color: #F44336;")  # Red
        self.connect_button.setEnabled(True)
        logger.error(f"GPIO connection error: {error}")

        # Show error dialog
        QMessageBox.critical(self, "Connection Error",
                           f"Failed to connect to GPIO:\n{error}")

    @pyqtSlot(str, int, str)
    def _on_connection_progress(self, device: str, percentage: int, status: str) -> None:
        """
        Handle connection progress update.

        Args:
            device: Device name
            percentage: Progress percentage
            status: Status message
        """
        self.connection_status_label.setText(f"{status} ({percentage}%)")

    # Public interface for MainWindow
    def connect_hardware(self) -> None:
        """Public method to initiate connection."""
        self._on_connect_clicked()

    def disconnect_hardware(self) -> None:
        """Public method to disconnect."""
        self._on_disconnect_clicked()

    def is_connected(self) -> bool:
        """Check if hardware is connected."""
        return self.controller and self.controller.is_connected
```

---

## 🟠 HIGH PRIORITY: Resource Cleanup (Day 4-5)

### Issue
**Locations:** Multiple widgets lack cleanup methods
**Problem:** Resources not released on shutdown
**Risk:** Memory leaks, hanging threads, corrupted state

### Implementation Plan

#### Step 1: Update All Widgets with Cleanup

Template for proper cleanup implementation:

```python
class WidgetWithResources(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.controller = None
        self.timer = None
        self.worker = None
        self._connections = []  # Track signal connections

    def cleanup(self) -> None:
        """
        Clean up all resources before shutdown.

        This method should:
        1. Stop any running operations
        2. Disconnect signals
        3. Release hardware resources
        4. Clean up timers
        5. Wait for threads to finish
        """
        logger.info(f"Cleaning up {self.__class__.__name__}...")

        # Stop operations
        if self.worker:
            self.worker.cancel()
            self.worker = None

        # Stop timers
        if self.timer and self.timer.isActive():
            self.timer.stop()
            self.timer = None

        # Disconnect signals (prevent late emissions)
        for connection in self._connections:
            try:
                connection.disconnect()
            except TypeError:
                pass  # Already disconnected
        self._connections.clear()

        # Release hardware
        if self.controller:
            try:
                if hasattr(self.controller, 'is_connected') and self.controller.is_connected:
                    self.controller.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting controller: {e}")
            finally:
                self.controller = None

        # Wait for thread pool (with timeout)
        pool = QThreadPool.globalInstance()
        if not pool.waitForDone(1000):  # 1 second timeout
            logger.warning("Thread pool did not finish in time")

        logger.info(f"{self.__class__.__name__} cleanup complete")
```

#### Step 2: Update MainWindow Cleanup

Update `src/ui/main_window.py`:

```python
def closeEvent(self, event: QCloseEvent) -> None:
    """Handle application close event."""
    logger.info("Application closing...")

    # Check for active treatment
    if self.protocol_engine and self.protocol_engine.is_running():
        reply = QMessageBox.warning(
            self,
            "Active Treatment",
            "A treatment is currently active. Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            event.ignore()
            return

    # Stop safety systems first
    if self.safety_manager:
        logger.info("Stopping safety manager...")
        self.safety_manager.shutdown()

    if self.safety_watchdog:
        logger.info("Stopping safety watchdog...")
        self.safety_watchdog.stop()

    # Clean up widgets in reverse order of dependency
    cleanup_order = [
        self.active_treatment_widget,
        self.treatment_setup_widget,
        self.camera_widget,
        self.actuator_widget,
        self.laser_widget,
        self.safety_widget,
        self.subject_widget
    ]

    for widget in cleanup_order:
        if widget and hasattr(widget, 'cleanup'):
            try:
                widget.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up {widget.__class__.__name__}: {e}")

    # Close database
    if self.db_manager:
        self.db_manager.close()

    # Log shutdown
    if self.event_logger:
        self.event_logger.log_system_event(
            EventType.SYSTEM_SHUTDOWN,
            "TOSCA system shutdown",
            EventSeverity.INFO
        )

    logger.info("Application closed")
    event.accept()
```

---

## 🟡 MEDIUM PRIORITY: Exception Handling (Week 2)

### Implementation Checklist

1. **Replace broad except blocks** with specific exception types
2. **Add proper logging** to all exception handlers
3. **Create custom exceptions** for domain-specific errors
4. **Implement exception hierarchy**

Example implementation:

```python
# src/core/exceptions.py
class TOSCAException(Exception):
    """Base exception for TOSCA system."""
    pass

class HardwareException(TOSCAException):
    """Hardware-related exceptions."""
    pass

class ProtocolException(TOSCAException):
    """Protocol-related exceptions."""
    pass

class SafetyException(TOSCAException):
    """Safety-critical exceptions."""
    pass

# Usage in widgets
try:
    result = hardware_operation()
except SerialException as e:
    logger.error(f"Serial communication error: {e}")
    raise HardwareException(f"Failed to communicate with device: {e}") from e
except TimeoutError as e:
    logger.error(f"Hardware timeout: {e}")
    raise HardwareException(f"Device not responding: {e}") from e
```

---

## 🟡 MEDIUM PRIORITY: Widget Decoupling (Week 2)

### Implementation Checklist

1. **Add public interfaces** to all hardware widgets
2. **Remove direct private method calls** from MainWindow
3. **Consider event bus** for widget communication
4. **Document public APIs**

---

## 🟢 LOW PRIORITY: Constants Module (Week 3)

### Implementation Plan

Create `src/ui/constants.py`:

```python
"""UI constants and configuration values."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UIConstants:
    """UI dimension and styling constants."""

    # Window dimensions
    MAIN_WINDOW_WIDTH = 1200
    MAIN_WINDOW_HEIGHT = 900

    # Widget dimensions
    MIN_BUTTON_HEIGHT = 35
    ESTOP_BUTTON_HEIGHT = 40
    CRITICAL_BUTTON_HEIGHT = 50

    # Font sizes (minimum 11px for safety)
    FONT_SIZE_MINIMUM = 11
    FONT_SIZE_BODY = 12
    FONT_SIZE_HEADER = 14
    FONT_SIZE_CRITICAL = 16

    # Colors (medical device appropriate)
    COLOR_SAFETY_GREEN = "#4CAF50"
    COLOR_ALERT_YELLOW = "#FFC107"
    COLOR_DANGER_RED = "#F44336"
    COLOR_INFO_BLUE = "#2196F3"
    COLOR_DISABLED_GRAY = "#9E9E9E"

    # Timeouts (milliseconds)
    GPIO_CONNECTION_TIMEOUT = 2000
    LASER_CONNECTION_TIMEOUT = 3000
    ACTUATOR_CONNECTION_TIMEOUT = 5000
    WATCHDOG_HEARTBEAT_INTERVAL = 400
    SAFETY_POLLING_INTERVAL = 500

    # Safety thresholds
    VIBRATION_THRESHOLD_G = 0.8
    VIBRATION_BASELINE_G = 0.14
    MAX_LASER_POWER_W = 5.0
    MIN_LASER_POWER_W = 0.0
    MAX_ACTUATOR_POSITION_UM = 50000
    MIN_ACTUATOR_VELOCITY_MM_S = 0.5
    MAX_ACTUATOR_VELOCITY_MM_S = 400.0

    # Protocol limits
    MAX_PROTOCOL_ACTIONS = 1000
    MAX_PROTOCOL_DURATION_S = 3600
    MAX_PROTOCOL_NAME_LENGTH = 100


# Usage
from ui.constants import UIConstants

button.setMinimumHeight(UIConstants.MIN_BUTTON_HEIGHT)
label.setStyleSheet(f"font-size: {UIConstants.FONT_SIZE_BODY}px;")
```

---

## Testing Strategy

### Unit Tests Required
1. **ProtocolWorker** - Test execution, cancellation, progress
2. **ConnectionWorker** - Test success, failure, timeout
3. **Protocol validation** - Test valid/invalid schemas
4. **Resource cleanup** - Test proper deallocation

### Integration Tests Required
1. **End-to-end protocol execution** with real hardware
2. **Multi-device connection** sequence
3. **Emergency stop** during protocol
4. **Application shutdown** during active treatment

### Performance Tests Required
1. **UI responsiveness** during connections
2. **Memory leak detection** over extended runs
3. **Thread pool efficiency**
4. **Protocol execution timing**

---

## Implementation Schedule

### Week 1 (Immediate)
- **Day 1:** Fix thread safety (CRITICAL)
- **Day 2-3:** Implement protocol validation
- **Day 3-4:** Non-blocking connections
- **Day 4-5:** Resource cleanup
- **Day 5:** Testing and validation

### Week 2 (Next Sprint)
- Exception handling improvements
- Widget decoupling
- Additional testing
- Documentation updates

### Week 3 (Following Sprint)
- Constants module
- Architecture improvements
- Performance optimization
- Final testing

---

## Success Metrics

1. **Zero crashes** during 100 protocol executions
2. **UI response time** < 100ms during connections
3. **Clean shutdown** in < 2 seconds
4. **Zero memory leaks** over 24-hour run
5. **100% protocol validation** coverage
6. **Zero thread deadlocks** in stress testing

---

## Risk Mitigation

1. **Backup current working code** before changes
2. **Test each fix in isolation** before integration
3. **Maintain fallback options** for critical operations
4. **Document all changes** in git commits
5. **Peer review** critical changes
6. **Gradual rollout** with monitoring

---

**Implementation Owner:** Development Team
**Review Required By:** Safety Engineer
**Approval Required For:** Thread safety fix (CRITICAL)

**Document Status:** Ready for implementation
**Last Updated:** 2025-10-27
