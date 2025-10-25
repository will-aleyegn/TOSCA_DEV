# Dependency Injection & Service Architecture

## Problem Statement

**MainWindow is tightly coupled to all core services**, directly instantiating:
- `DatabaseManager`
- `SessionManager`
- `EventLogger`
- `SafetyManager`
- `CameraController`
- `ProtocolEngine`

This violates the **Dependency Inversion Principle** and creates:
- ❌ Impossible to unit test MainWindow in isolation
- ❌ Cannot swap implementations for testing
- ❌ Difficult to manage service lifecycle
- ❌ Tight coupling between UI and business logic
- ❌ Cannot reuse services in other contexts

---

## Current Architecture (Tight Coupling)

```
┌──────────────────────────────────────────┐
│           MainWindow.__init__()           │
│                                          │
│  self.db_manager = DatabaseManager()     │ ❌ Creates dependency
│  self.session_manager = SessionManager() │ ❌ Creates dependency
│  self.event_logger = EventLogger()       │ ❌ Creates dependency
│  self.safety_manager = SafetyManager()   │ ❌ Creates dependency
│  self.camera_controller = CameraController() │ ❌ Creates dependency
│  self.protocol_engine = ProtocolEngine() │ ❌ Creates dependency
└──────────────────────────────────────────┘
```

**Problem:** MainWindow is responsible for creating AND using services.

---

## Proposed Architecture (Dependency Injection)

```
┌─────────────────┐
│    main.py      │
│                 │
│ ┌─────────────┐ │
│ │  Services   │ │ ← Creates all services
│ │  Container  │ │
│ └──────┬──────┘ │
│        │        │
│        ▼        │
│  ┌──────────┐  │
│  │MainWindow│  │ ← Receives services via constructor
│  └──────────┘  │
└─────────────────┘
```

**Solution:** Services created in `main.py` and injected into MainWindow.

---

## Detailed Design

### 1. Service Container

**File:** `src/core/services.py`

```python
"""
TOSCA Application Services Container.

Manages creation and lifecycle of all application services.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from ..config import settings
from ..database.db_manager import DatabaseManager
from ..core.event_logger import EventLogger
from ..core.safety import SafetyManager
from ..core.session_manager import SessionManager
from ..core.protocol_engine import ProtocolEngine
from ..hardware.laser_controller import LaserController
from ..hardware.actuator_controller import ActuatorController
from ..hardware.camera_controller import CameraController
from ..hardware.gpio_controller import GPIOController

logger = logging.getLogger(__name__)


@dataclass
class ApplicationServices:
    """
    Container for all application services.

    Provides centralized access to core services and hardware controllers.
    """

    # Core services
    db_manager: DatabaseManager
    session_manager: SessionManager
    event_logger: EventLogger
    safety_manager: SafetyManager
    protocol_engine: ProtocolEngine

    # Hardware controllers (optional - may not be available)
    laser_controller: Optional[LaserController] = None
    actuator_controller: Optional[ActuatorController] = None
    camera_controller: Optional[CameraController] = None
    gpio_controller: Optional[GPIOController] = None

    def cleanup(self) -> None:
        """Cleanup all services and controllers."""
        logger.info("Cleaning up application services...")

        # Cleanup hardware controllers
        if self.camera_controller:
            self.camera_controller.cleanup()
        if self.laser_controller:
            self.laser_controller.cleanup()
        if self.actuator_controller:
            self.actuator_controller.cleanup()
        if self.gpio_controller:
            self.gpio_controller.cleanup()

        # Cleanup core services
        if self.db_manager:
            self.db_manager.close()

        logger.info("Application services cleaned up")


class ServiceFactory:
    """
    Factory for creating application services.

    Handles service instantiation and dependency wiring.
    """

    @staticmethod
    def create_services() -> ApplicationServices:
        """
        Create all application services.

        Returns:
            ApplicationServices container with all services initialized
        """
        logger.info("Creating application services...")

        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize()
        logger.info("✓ Database initialized")

        # Initialize core services
        session_manager = SessionManager(db_manager)
        event_logger = EventLogger(db_manager)
        safety_manager = SafetyManager()
        logger.info("✓ Core services initialized")

        # Initialize hardware controllers (with error handling)
        laser_controller = ServiceFactory._create_laser_controller(event_logger)
        actuator_controller = ServiceFactory._create_actuator_controller(event_logger)
        camera_controller = ServiceFactory._create_camera_controller(event_logger)
        gpio_controller = ServiceFactory._create_gpio_controller(event_logger)

        # Initialize protocol engine
        protocol_engine = ProtocolEngine(
            safety_manager=safety_manager,
            laser_controller=laser_controller,
            actuator_controller=actuator_controller,
        )
        logger.info("✓ Protocol engine initialized")

        # Wire safety manager dependencies
        if laser_controller:
            safety_manager.set_laser_controller_reference(laser_controller)

        logger.info("✓ All services initialized successfully")

        return ApplicationServices(
            db_manager=db_manager,
            session_manager=session_manager,
            event_logger=event_logger,
            safety_manager=safety_manager,
            protocol_engine=protocol_engine,
            laser_controller=laser_controller,
            actuator_controller=actuator_controller,
            camera_controller=camera_controller,
            gpio_controller=gpio_controller,
        )

    @staticmethod
    def _create_laser_controller(event_logger: EventLogger) -> Optional[LaserController]:
        """Create laser controller with error handling."""
        try:
            controller = LaserController(event_logger=event_logger)
            logger.info("✓ Laser controller created")
            return controller
        except Exception as e:
            logger.warning(f"Laser controller not available: {e}")
            return None

    @staticmethod
    def _create_actuator_controller(event_logger: EventLogger) -> Optional[ActuatorController]:
        """Create actuator controller with error handling."""
        try:
            controller = ActuatorController(event_logger=event_logger)
            logger.info("✓ Actuator controller created")
            return controller
        except Exception as e:
            logger.warning(f"Actuator controller not available: {e}")
            return None

    @staticmethod
    def _create_camera_controller(event_logger: EventLogger) -> Optional[CameraController]:
        """Create camera controller with error handling."""
        try:
            controller = CameraController(event_logger=event_logger)
            logger.info("✓ Camera controller created")
            return controller
        except Exception as e:
            logger.warning(f"Camera controller not available: {e}")
            return None

    @staticmethod
    def _create_gpio_controller(event_logger: EventLogger) -> Optional[GPIOController]:
        """Create GPIO controller with error handling."""
        try:
            controller = GPIOController(event_logger=event_logger)
            logger.info("✓ GPIO controller created")
            return controller
        except Exception as e:
            logger.warning(f"GPIO controller not available: {e}")
            return None
```

### 2. Updated main.py

**File:** `src/main.py`

```python
"""
TOSCA Laser Control System - Main Entry Point

This is the primary entry point for the TOSCA application.
Initializes services and launches the main window.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def setup_logging() -> logging.Logger:
    """Configure application-wide logging."""
    log_dir = Path(__file__).parent.parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "tosca.log"),
            logging.StreamHandler(sys.stdout)
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("TOSCA Laser Control System Starting")
    logger.info("=" * 60)
    return logger


def main() -> int:
    """
    Main application entry point.

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    logger = setup_logging()

    try:
        # Import PyQt6 after logging is set up
        from PyQt6.QtWidgets import QApplication

        logger.info("Initializing Qt Application")
        app = QApplication(sys.argv)
        app.setApplicationName("TOSCA Laser Control")
        app.setOrganizationName("Aleyegn")

        # ✅ Create all services using Service Factory
        from core.services import ServiceFactory

        logger.info("Initializing application services...")
        services = ServiceFactory.create_services()

        # ✅ Create main window with dependency injection
        from ui.main_window import MainWindow

        logger.info("Creating main window")
        window = MainWindow(services=services)
        window.show()

        logger.info("Application ready")
        return_code: int = app.exec()

        # Cleanup services
        logger.info("Application shutting down normally")
        services.cleanup()

        return return_code

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Fatal error during application startup: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### 3. Refactored MainWindow

**File:** `src/ui/main_window.py`

```python
"""
Main application window with tab-based navigation.
"""

import logging
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ..core.services import ApplicationServices

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window.

    Receives all services via dependency injection.
    """

    def __init__(self, services: ApplicationServices) -> None:
        """
        Initialize main window.

        Args:
            services: Application services container (injected dependency)
        """
        super().__init__()

        # ✅ Receive services instead of creating them
        self.services = services
        self.db_manager = services.db_manager
        self.session_manager = services.session_manager
        self.event_logger = services.event_logger
        self.safety_manager = services.safety_manager
        self.protocol_engine = services.protocol_engine

        # Hardware controllers (may be None)
        self.camera_controller = services.camera_controller
        self.laser_controller = services.laser_controller
        self.actuator_controller = services.actuator_controller
        self.gpio_controller = services.gpio_controller

        logger.info("Initializing main window")

        self.setWindowTitle("TOSCA Laser Control System")
        self.setGeometry(100, 100, 1400, 900)

        # Log system startup
        self.event_logger.log_system_event(
            EventType.SYSTEM_STARTUP,
            "TOSCA system started",
            EventSeverity.INFO
        )

        self._init_ui()
        self._init_status_bar()
        self._setup_watchdog()

        logger.info("Main window initialized")

    def _setup_watchdog(self) -> None:
        """Setup watchdog heartbeat."""
        from PyQt6.QtCore import QTimer

        # Send heartbeat to safety manager every 500ms
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(500)

        # Connect watchdog signals
        self.safety_manager.watchdog_timeout.connect(self._on_watchdog_timeout)

    def _send_heartbeat(self) -> None:
        """Send heartbeat to watchdog."""
        self.safety_manager.refresh_heartbeat()

    def _on_watchdog_timeout(self) -> None:
        """Handle watchdog timeout."""
        logger.critical("Watchdog timeout detected in MainWindow")
        # Handle timeout...

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Application closing, cleaning up resources...")

        # Log system shutdown
        self.event_logger.log_system_event(
            EventType.SYSTEM_SHUTDOWN,
            "TOSCA system shutting down",
            EventSeverity.INFO
        )

        # ✅ Services cleanup handled by main.py
        # No need to cleanup individual services here

        logger.info("Cleanup complete")
        event.accept()
```

---

## Benefits

### Testability
```python
# tests/test_main_window.py
def test_main_window_initialization():
    """Test MainWindow with mock services."""

    # Create mock services
    mock_services = create_mock_services()

    # Inject mock services into MainWindow
    window = MainWindow(services=mock_services)

    # Test window behavior with mocks
    assert window.db_manager == mock_services.db_manager
    assert window.safety_manager == mock_services.safety_manager
```

### Flexibility
```python
# Can create different service configurations
dev_services = ServiceFactory.create_services()  # Development
test_services = create_test_services()  # Testing
prod_services = create_production_services()  # Production
```

### Reusability
```python
# Services can be used outside of MainWindow
services = ServiceFactory.create_services()

# Use protocol engine in CLI tool
result = await services.protocol_engine.execute_protocol(protocol)

# Use event logger in background service
services.event_logger.log_system_event(...)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_services.py
def test_service_factory_creates_all_services():
    """Test that ServiceFactory creates all required services."""

    services = ServiceFactory.create_services()

    assert services.db_manager is not None
    assert services.session_manager is not None
    assert services.event_logger is not None
    assert services.safety_manager is not None
    assert services.protocol_engine is not None

def test_services_cleanup():
    """Test that services cleanup properly."""

    services = ServiceFactory.create_services()
    services.cleanup()

    # Verify cleanup occurred
    assert not services.db_manager.engine.pool.checkedout()
```

### Integration Tests

```python
# tests/integration/test_main_window_integration.py
def test_main_window_with_real_services():
    """Test MainWindow with real services."""

    services = ServiceFactory.create_services()
    window = MainWindow(services=services)

    # Test full integration
    window.show()
    # ... test UI interactions

    window.close()
    services.cleanup()
```

---

## Migration Strategy

### Phase 1: Create Service Infrastructure (1 day)
1. Create `src/core/services.py`
2. Implement `ApplicationServices` and `ServiceFactory`
3. Write unit tests for service factory

### Phase 2: Update main.py (0.5 days)
1. Refactor `main()` to use `ServiceFactory`
2. Pass services to `MainWindow`
3. Test application startup

### Phase 3: Refactor MainWindow (1 day)
1. Update `MainWindow.__init__()` to accept services
2. Remove service instantiation code
3. Update all widget initialization to use injected services
4. Test all UI functionality

### Phase 4: Update Tests (0.5 days)
1. Create mock services for testing
2. Update existing tests to use dependency injection
3. Add new tests for service factory

### Phase 5: Documentation (0.5 days)
1. Update architecture documentation
2. Update developer guidelines
3. Create service usage examples

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Service infrastructure | 1 day | Create services module |
| Update main.py | 0.5 days | Implement DI in main |
| Refactor MainWindow | 1 day | Remove tight coupling |
| Update tests | 0.5 days | Mock services, new tests |
| Documentation | 0.5 days | Docs and examples |
| **Total** | **3.5 days** | |

---

## Success Criteria

1. ✅ All services created in `main.py`
2. ✅ MainWindow receives services via constructor
3. ✅ No service instantiation in MainWindow
4. ✅ Unit tests use mock services
5. ✅ Integration tests use real services
6. ✅ Application runs without errors
7. ✅ All tests pass

---

**Status:** 📋 Ready for Implementation
**Priority:** 🔴 CRITICAL
**Effort:** 3.5 days
**Risk:** Medium (requires careful refactoring)
**Dependencies:** None
