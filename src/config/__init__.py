# -*- coding: utf-8 -*-
"""
Configuration module for TOSCA Laser Control System.

Provides centralized configuration management with:
- Pydantic models for type safety
- YAML file loading
- Validation
- Singleton pattern for global access
"""

from .config_loader import get_config
from .models import (
    ActuatorConfig,
    CameraConfig,
    GPIOConfig,
    GUIConfig,
    HardwareConfig,
    LaserConfig,
    SafetyConfig,
    TOSCAConfig,
)

__all__ = [
    "get_config",
    "TOSCAConfig",
    "HardwareConfig",
    "CameraConfig",
    "ActuatorConfig",
    "LaserConfig",
    "GPIOConfig",
    "SafetyConfig",
    "GUIConfig",
]
