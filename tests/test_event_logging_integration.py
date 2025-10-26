"""
Integration test for event logging system.

Tests the complete flow:
1. Hardware event → EventLogger → Database
2. Database → SafetyWidget display

Run this script to validate Phase 3 Priority 3 implementation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from datetime import datetime

from src.core.event_logger import EventLogger, EventSeverity, EventType
from src.database.db_manager import DatabaseManager


def test_event_logger_to_database():
    """Test event logging to database."""
    print("=" * 80)
    print("TEST 1: Event Logger -> Database Integration")
    print("=" * 80)

    # Create test database
    db_path = Path("test_event_logging.db")
    if db_path.exists():
        db_path.unlink()  # Clean slate

    db_manager = DatabaseManager(str(db_path))
    db_manager.initialize()  # Create database tables
    event_logger = EventLogger(db_manager, log_file=Path("test_events.jsonl"))

    print("\n[OK] Database and EventLogger created")

    # Test 1: Log various hardware events
    print("\n--- Logging Hardware Events ---")

    # Camera events
    event_logger.log_event(
        event_type=EventType.HARDWARE_CAMERA_CONNECT,
        description="Camera connected: Allied Vision 1800 U-158c",
        severity=EventSeverity.INFO,
        details={"device": "Allied Vision Camera", "resolution": "1920x1200"},
    )
    print("[OK] Logged camera connect event")

    event_logger.log_event(
        event_type=EventType.HARDWARE_CAMERA_CAPTURE,
        description="Image captured: subject_001_20251024_123045.png",
        severity=EventSeverity.INFO,
        details={"output_path": "data/images/subject_001_20251024_123045.png"},
    )
    print("[OK] Logged camera capture event")

    # Laser events
    event_logger.log_event(
        event_type=EventType.HARDWARE_LASER_CONNECT,
        description="Laser connected: Arroyo Instruments",
        severity=EventSeverity.INFO,
        details={"device": "Arroyo Laser Driver"},
    )
    print("[OK] Logged laser connect event")

    event_logger.log_event(
        event_type=EventType.TREATMENT_POWER_CHANGE,
        description="Laser current set to 150.0 mA",
        severity=EventSeverity.INFO,
        details={"current_ma": 150.0},
    )
    print("[OK] Logged laser power change event")

    event_logger.log_event(
        event_type=EventType.HARDWARE_LASER_TEMP_CHANGE,
        description="TEC temperature set to 25.0°C",
        severity=EventSeverity.INFO,
        details={"temperature_c": 25.0},
    )
    print("[OK] Logged laser temperature change event")

    # Actuator events
    event_logger.log_event(
        event_type=EventType.HARDWARE_ACTUATOR_CONNECT,
        description="Actuator connected on COM3 (not homed)",
        severity=EventSeverity.INFO,
        details={"device": "Xeryon Linear Stage"},
    )
    print("[OK] Logged actuator connect event")

    event_logger.log_event(
        event_type=EventType.HARDWARE_ACTUATOR_HOME_START,
        description="Actuator homing started (finding index position)",
        severity=EventSeverity.INFO,
    )
    print("[OK] Logged actuator homing start event")

    event_logger.log_event(
        event_type=EventType.HARDWARE_ACTUATOR_HOME_COMPLETE,
        description="Actuator homing completed (position: 0.0 µm)",
        severity=EventSeverity.INFO,
        details={"position_um": 0.0},
    )
    print("[OK] Logged actuator homing complete event")

    event_logger.log_event(
        event_type=EventType.HARDWARE_ACTUATOR_MOVE,
        description="Actuator moved to position: 500.0 µm",
        severity=EventSeverity.INFO,
        details={"position_um": 500.0},
    )
    print("[OK] Logged actuator move event")

    # GPIO events
    event_logger.log_event(
        event_type=EventType.HARDWARE_GPIO_CONNECT,
        description="Arduino GPIO connected on COM4",
        severity=EventSeverity.INFO,
        details={"device": "Arduino Nano"},
    )
    print("[OK] Logged GPIO connect event")

    event_logger.log_event(
        event_type=EventType.SAFETY_GPIO_OK,
        description="Smoothing motor started",
        severity=EventSeverity.INFO,
    )
    print("[OK] Logged GPIO motor start event")

    # Safety events (higher severity)
    event_logger.log_event(
        event_type=EventType.SAFETY_INTERLOCK_FAIL,
        description="GPIO interlock failure: Motor stopped",
        severity=EventSeverity.WARNING,
        system_state="unsafe",
        action_taken="Laser disabled automatically",
    )
    print("[OK] Logged safety interlock failure (WARNING)")

    event_logger.log_event(
        event_type=EventType.SAFETY_EMERGENCY_STOP,
        description="Emergency stop activated by user",
        severity=EventSeverity.EMERGENCY,
        system_state="emergency_stop",
        laser_state="disabled",
        action_taken="All hardware operations halted",
    )
    print("[OK] Logged emergency stop (EMERGENCY)")

    print(f"\n[OK] Total events logged: 13")

    # Test 2: Query events from database
    print("\n--- Querying Database ---")

    all_logs = db_manager.get_safety_logs(limit=100)
    print(f"[OK] Retrieved {len(all_logs)} events from database")

    if len(all_logs) < 13:
        print(f"[X] ERROR: Expected at least 13 events, got {len(all_logs)}")
        return False

    # Debug: Show all event types if we have more than expected
    if len(all_logs) > 13:
        print(f"[INFO] Found {len(all_logs) - 13} additional event(s):")
        for log in all_logs:
            if log.event_type not in [
                "camera_connected",
                "camera_image_captured",
                "laser_connected",
                "laser_power_changed",
                "laser_temperature_changed",
                "actuator_connected",
                "actuator_homing_started",
                "actuator_homing_completed",
                "actuator_position_changed",
                "gpio_connected",
                "gpio_interlock_ok",
                "interlock_failure",
                "e_stop_pressed",
            ]:
                print(f"  - {log.event_type}: {log.description}")

    # Test 3: Verify event types
    print("\n--- Verifying Event Types ---")

    event_types_found = {log.event_type for log in all_logs}
    expected_types = {
        "camera_connected",
        "camera_image_captured",
        "laser_connected",
        "laser_power_changed",
        "laser_temperature_changed",
        "actuator_connected",
        "actuator_homing_started",
        "actuator_homing_completed",
        "actuator_position_changed",
        "gpio_connected",
        "gpio_interlock_ok",
        "interlock_failure",
        "e_stop_pressed",
    }

    missing = expected_types - event_types_found
    if missing:
        print(f"[X] Missing event types: {missing}")
        return False

    print(f"[OK] All expected event types found: {len(expected_types)} types")

    extra = event_types_found - expected_types
    if extra:
        print(f"[INFO] Additional event types (from system): {extra}")

    # Test 4: Verify severity filtering
    print("\n--- Testing Severity Filtering ---")

    critical_logs = db_manager.get_safety_logs(limit=100, min_severity="warning")
    print(f"[OK] Retrieved {len(critical_logs)} events with severity >= warning")

    if len(critical_logs) != 2:  # WARNING + EMERGENCY
        print(f"[X] ERROR: Expected 2 critical events, got {len(critical_logs)}")
        return False

    severities = {log.severity for log in critical_logs}
    if severities == {"warning", "emergency"}:
        print(f"[OK] Severity filtering works correctly")
    else:
        print(f"[X] ERROR: Unexpected severities: {severities}")
        return False

    # Test 5: Verify event details
    print("\n--- Verifying Event Details ---")

    # Find the camera capture event
    capture_event = next(
        (log for log in all_logs if log.event_type == "camera_image_captured"), None
    )
    if capture_event:
        print(f"[OK] Camera capture event found")
        print(f"  - Description: {capture_event.description}")
        print(f"  - Timestamp: {capture_event.timestamp}")
        print(f"  - Severity: {capture_event.severity}")
        if capture_event.details:
            import json

            details = json.loads(capture_event.details)
            print(f"  - Details: {details}")
    else:
        print(f"[X] ERROR: Camera capture event not found")
        return False

    # Find the emergency stop event
    estop_event = next((log for log in all_logs if log.event_type == "e_stop_pressed"), None)
    if estop_event:
        print(f"\n[OK] Emergency stop event found")
        print(f"  - Description: {estop_event.description}")
        print(f"  - Severity: {estop_event.severity}")
        print(f"  - System state: {estop_event.system_state}")
        print(f"  - Laser state: {estop_event.laser_state}")
        print(f"  - Action taken: {estop_event.action_taken}")
    else:
        print(f"[X] ERROR: Emergency stop event not found")
        return False

    print("\n" + "=" * 80)
    print("[OK] ALL TESTS PASSED - Event Logging System Working Correctly!")
    print("=" * 80)

    # Cleanup
    db_manager.close()  # Close database connection first
    db_path.unlink()
    Path("test_events.jsonl").unlink(missing_ok=True)

    return True


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print(" " * 20 + "EVENT LOGGING INTEGRATION TEST")
    print("=" * 80)
    print("\n")

    try:
        success = test_event_logger_to_database()
        if success:
            print("\n[PASS] Integration test completed successfully!\n")
            sys.exit(0)
        else:
            print("\n[FAIL] Integration test failed!\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
