# -*- coding: utf-8 -*-
"""
Pydantic configuration models for TOSCA Laser Control System.

Provides type-safe configuration with validation.
"""

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class CameraConfig(BaseModel):
    """Camera hardware configuration."""

    gui_fps_target: float = Field(
        default=30.0, ge=1.0, le=60.0, description="GUI update rate limit (FPS)"
    )
    hardware_fps: float = Field(
        default=30.0, ge=1.0, le=120.0, description="Camera acquisition frame rate"
    )
    fps_update_interval: int = Field(
        default=30, ge=1, description="Frames between FPS calculations"
    )

    # Video Recording Settings
    video_codec: str = Field(default="H264", description="Video codec (H264, MJPEG, mp4v)")
    video_quality_crf: int = Field(
        default=28,
        ge=0,
        le=51,
        description="H.264 Constant Rate Factor (0=lossless, 51=worst, 23=default, 28=good)",
    )
    video_preset: str = Field(
        default="medium",
        description=(
            "H.264 encoding preset "
            "(ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)"
        ),
    )
    video_fallback_codec: str = Field(
        default="MJPG", description="Fallback codec if primary codec unavailable"
    )


class ActuatorConfig(BaseModel):
    """Actuator hardware configuration."""

    com_port: str = Field(default="COM3", description="Serial port for actuator")
    baudrate: int = Field(default=9600, description="Serial baudrate (TOSCA uses 9600, NOT 115200)")
    position_timer_ms: int = Field(
        default=100, ge=10, le=1000, description="Position update interval (ms)"
    )
    homing_check_initial_ms: int = Field(
        default=100, ge=10, le=500, description="Initial homing check delay (ms)"
    )
    homing_check_loop_ms: int = Field(
        default=200, ge=50, le=1000, description="Homing loop check delay (ms)"
    )
    position_check_initial_ms: int = Field(
        default=100, ge=10, le=500, description="Initial position check delay (ms)"
    )
    position_check_loop_ms: int = Field(
        default=50, ge=10, le=500, description="Position loop check delay (ms)"
    )


class LaserConfig(BaseModel):
    """Laser hardware configuration."""

    com_port: str = Field(default="COM4", description="Serial port for laser controller")
    baudrate: int = Field(default=38400, description="Serial baudrate")
    timeout_s: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Serial read timeout (seconds)"
    )
    write_timeout_s: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Serial write timeout (seconds)"
    )
    monitor_timer_ms: int = Field(
        default=500, ge=100, le=5000, description="Status update interval (ms)"
    )
    max_current_ma: float = Field(
        default=2000.0, ge=0.0, le=3000.0, description="Maximum laser current (mA)"
    )
    min_current_ma: float = Field(default=0.0, ge=0.0, description="Minimum laser current (mA)")


class GPIOConfig(BaseModel):
    """GPIO hardware configuration."""

    com_port: str = Field(default="COM4", description="Serial port for Arduino Nano")
    baudrate: int = Field(default=9600, description="Serial baudrate")
    timeout_s: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Serial read timeout (seconds)"
    )
    write_timeout_s: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Serial write timeout (seconds)"
    )
    monitor_timer_ms: int = Field(
        default=100, ge=50, le=1000, description="Status update interval (ms)"
    )
    watchdog_timeout_ms: int = Field(
        default=1000, ge=100, le=5000, description="Hardware watchdog timeout (ms)"
    )
    motor_control_pin: int = Field(
        default=2, ge=0, le=13, description="Arduino digital pin for motor control"
    )
    vibration_sensor_pin: int = Field(
        default=3, ge=0, le=13, description="Arduino digital pin for vibration sensor"
    )
    photodiode_pin: int = Field(
        default=0, ge=0, le=7, description="Arduino analog pin for photodiode (A0-A7)"
    )


class HardwareConfig(BaseModel):
    """Combined hardware configuration."""

    camera: CameraConfig = Field(default_factory=CameraConfig)
    actuator: ActuatorConfig = Field(default_factory=ActuatorConfig)
    laser: LaserConfig = Field(default_factory=LaserConfig)
    gpio: GPIOConfig = Field(default_factory=GPIOConfig)


class SafetyConfig(BaseModel):
    """Safety system configuration."""

    watchdog_enabled: bool = Field(default=True, description="Enable hardware watchdog timer")
    watchdog_heartbeat_ms: int = Field(
        default=500,
        ge=100,
        le=4000,
        description="Heartbeat interval (must be < watchdog timeout)",
    )
    emergency_stop_enabled: bool = Field(
        default=True, description="Enable emergency stop functionality"
    )
    interlock_check_enabled: bool = Field(
        default=True, description="Enable safety interlock checking"
    )
    laser_enable_requires_interlocks: bool = Field(
        default=True, description="Laser cannot enable without valid interlocks"
    )


class GUIConfig(BaseModel):
    """GUI configuration."""

    window_title: str = Field(default="TOSCA Laser Control System", description="Main window title")
    default_tab_index: int = Field(
        default=0, ge=0, le=4, description="Default selected tab on startup"
    )
    auto_connect_hardware: bool = Field(
        default=False, description="Auto-connect to hardware on startup"
    )
    enable_developer_mode: bool = Field(default=False, description="Enable developer mode features")
    research_mode: bool = Field(
        default=True, description="Mark system as research-only (not for clinical use)"
    )
    show_warning_on_startup: bool = Field(
        default=True, description="Show research mode warning dialog on startup"
    )


class LoggingConfig(BaseModel):
    """Logging and audit trail configuration."""

    retention_days: int = Field(
        default=2555,
        ge=1,
        description="Log file retention period (days). Default 2555 = 7 years for FDA compliance.",
    )
    rotation_size_mb: int = Field(
        default=100, ge=1, le=1000, description="Maximum log file size before rotation (MB)"
    )
    enable_rotation: bool = Field(default=True, description="Enable automatic log rotation")
    enable_cleanup: bool = Field(
        default=True, description="Enable automatic cleanup of old log files"
    )


class TOSCAConfig(BaseModel):
    """Root configuration for TOSCA system."""

    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    gui: GUIConfig = Field(default_factory=GUIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @model_validator(mode="after")
    def validate_heartbeat_against_timeout(self) -> "TOSCAConfig":
        """
        Ensure heartbeat is less than watchdog timeout.

        Validates that safety heartbeat interval is shorter than
        the GPIO watchdog timeout to prevent false timeout triggers.

        Returns:
            Validated config instance

        Raises:
            ValueError: If heartbeat >= timeout
        """
        heartbeat = self.safety.watchdog_heartbeat_ms
        timeout = self.hardware.gpio.watchdog_timeout_ms

        if heartbeat >= timeout:
            raise ValueError(
                f"Safety heartbeat interval ({heartbeat}ms) must be less than "
                f"GPIO watchdog timeout ({timeout}ms). "
                f"Recommended: heartbeat = timeout / 2 = {timeout // 2}ms"
            )

        # Additional safety margin check (heartbeat should be < 90% of timeout)
        safety_margin = 0.9
        if heartbeat >= timeout * safety_margin:
            logger.warning(
                f"Safety heartbeat ({heartbeat}ms) is close to timeout ({timeout}ms). "
                f"Recommended margin: heartbeat < {timeout * safety_margin:.0f}ms"
            )

        return self
