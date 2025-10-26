"""
Hardware abstraction layer for TOSCA components.

Provides unified interfaces for:
- Camera control (Allied Vision)
- Laser control (Arroyo Instruments)
- Actuator control (Xeryon)
- GPIO/safety interlocks (Arduino Nano)
"""

from .hardware_controller_base import HardwareControllerBase

__all__ = ["HardwareControllerBase"]
