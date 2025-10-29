"""
Hardware abstraction layer for TOSCA components.

Provides unified interfaces for:
- Camera control (Allied Vision)
- Laser control (Arroyo Instruments)
- TEC control (Arroyo Instruments)
- Actuator control (Xeryon)
- GPIO/safety interlocks (Arduino Nano)
"""

from .hardware_controller_base import HardwareControllerBase
from .laser_controller import LaserController
from .tec_controller import TECController

__all__ = ["HardwareControllerBase", "LaserController", "TECController"]
