"""
UI widgets for TOSCA application.
"""

from .actuator_widget import ActuatorWidget
from .camera_widget import CameraWidget
from .config_display_widget import ConfigDisplayWidget
from .laser_widget import LaserWidget
from .protocol_builder_widget import ProtocolBuilderWidget
from .safety_widget import SafetyWidget
from .subject_widget import SubjectWidget
from .tec_widget import TECWidget
from .treatment_widget import TreatmentWidget

__all__ = [
    "ActuatorWidget",
    "CameraWidget",
    "ConfigDisplayWidget",
    "LaserWidget",
    "ProtocolBuilderWidget",
    "SafetyWidget",
    "SubjectWidget",
    "TECWidget",
    "TreatmentWidget",
]
