# Vulture Whitelist for TOSCA Medical Device Software
# This file contains patterns for code that should NOT be flagged as dead code

# ============================================================================
# Abstract Base Classes (ABCs) - Not directly instantiated
# ============================================================================
HardwareControllerBase  # ABC for all hardware controllers
MockHardwareBase  # ABC for test mocks

# ============================================================================
# Public API Methods - May be used by external code or plugins
# ============================================================================
# Protocol engine public APIs
ActionType  # Enum used by protocol definitions
ActionParameters  # Base class for protocol actions

# Hardware controller public interfaces
connect  # Common method across all hardware controllers
disconnect  # Common method across all hardware controllers
is_connected  # Common method across all hardware controllers

# ============================================================================
# Safety-Critical Modules - Manual review required, never auto-remove
# ============================================================================
# src/core/safety.py
SafetyManager  # Core safety controller
SafetyState  # Safety state machine
check_interlock  # Interlock validation method
emergency_stop  # E-Stop handler

# src/hardware/gpio_controller.py
GPIOController  # Arduino GPIO interface
read_footpedal  # Footpedal deadman switch
read_photodiode  # Photodiode power verification
read_smoothing_health  # Smoothing device health check
send_watchdog_heartbeat  # Hardware watchdog heartbeat

# src/core/safety_watchdog.py
SafetyWatchdog  # Hardware watchdog manager
heartbeat_thread  # Watchdog heartbeat thread

# ============================================================================
# Test Fixtures and Test-Only Code
# ============================================================================
create_mock_session  # Test fixture for session creation
create_mock_subject  # Test fixture for subject creation
mock_hardware_setup  # Test fixture for hardware mocking
pytest_configure  # Pytest configuration hook
pytest_collection_modifyitems  # Pytest collection hook

# ============================================================================
# Future-Use Placeholder Functions (Documented in roadmap)
# ============================================================================
export_to_csv  # Planned for future data export feature (Phase 7)
import_protocol_from_file  # Planned for protocol import (Phase 6)
calculate_treatment_metrics  # Planned for analytics dashboard (Phase 8)

# ============================================================================
# Signal/Slot Methods - May appear unused due to dynamic connections
# ============================================================================
# PyQt6 signals and slots are connected dynamically and may not show
# direct references in static analysis

_on_camera_frame_ready  # Signal handler naming pattern
_on_hardware_connected  # Signal handler naming pattern
_on_safety_fault  # Signal handler naming pattern
_on_interlock_changed  # Signal handler naming pattern

# Specific signal handlers that may be flagged
camera_frame_ready  # PyQt6 signal
hardware_connected  # PyQt6 signal
safety_fault_occurred  # PyQt6 signal
interlock_status_changed  # PyQt6 signal

# ============================================================================
# Configuration and Data Models (Pydantic)
# ============================================================================
# Pydantic models may have fields that appear unused but are validated
Config  # Base configuration class
HardwareConfig  # Hardware configuration model
SafetyConfig  # Safety configuration model
ProtocolConfig  # Protocol configuration model

# ============================================================================
# Database Models (SQLAlchemy)
# ============================================================================
# SQLAlchemy models may have columns that appear unused but are queried
Subject  # SQLAlchemy model
Session  # SQLAlchemy model
Event  # SQLAlchemy model
Protocol  # SQLAlchemy model

# ============================================================================
# Module-Level Variables and Constants
# ============================================================================
RESEARCH_MODE_WARNING  # Shown on startup
VERSION  # Application version string
BUILD_DATE  # Build timestamp
SAFETY_INTERLOCK_TIMEOUT_MS  # Safety timing constant

# ============================================================================
# Development and Debugging Code
# ============================================================================
# Code marked with DEVELOPMENT_MODE flag - kept for debugging
debug_mode  # Development flag
verbose_logging  # Verbose log flag
hardware_simulation_mode  # Simulation mode flag

# ============================================================================
# Legacy Code Pending Migration
# ============================================================================
# These are scheduled for removal but need coordination with hardware team
# TODO: Remove after Phase 6 completion
legacy_laser_calibration  # Old calibration method (replaced by auto-calibration)
manual_tec_control  # Manual TEC override (deprecated, use protocol-based)

# ============================================================================
# Notes for False Positives
# ============================================================================
# If vulture flags something from here, it means:
# 1. The whitelist pattern is too generic (make it more specific)
# 2. The code was removed but whitelist wasn't updated (remove from whitelist)
# 3. The code is genuinely unused and should be reviewed for removal
