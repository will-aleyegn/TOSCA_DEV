# -*- coding: utf-8 -*-
"""
Pydantic configuration models for TOSCA Laser Control System.

Provides type-safe configuration with validation.
"""

from pydantic import BaseModel, Field, ValidationInfo, field_validator


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
        default=500, ge=100, le=900, description="Heartbeat interval (must be < watchdog timeout)"
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

    @field_validator("watchdog_heartbeat_ms")
    @classmethod
    def validate_heartbeat(cls, v: int, info: ValidationInfo) -> int:
        """Ensure heartbeat is less than watchdog timeout."""
        gpio_timeout = 1000
        if v >= gpio_timeout:
            raise ValueError(f"Heartbeat {v}ms must be less than watchdog timeout {gpio_timeout}ms")
        return v


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
    research_mode: bool = Field(default=True, description="Mark system as research-only (not for clinical use)")
    show_warning_on_startup: bool = Field(default=True, description="Show research mode warning dialog on startup")


class TOSCAConfig(BaseModel):
    """Root configuration for TOSCA system."""

    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    gui: GUIConfig = Field(default_factory=GUIConfig)
