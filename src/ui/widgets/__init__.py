"""
UI widgets for TOSCA application.
"""

from .actuator_widget import ActuatorWidget
from .camera_widget import CameraWidget
from .protocol_builder_widget import ProtocolBuilderWidget
from .safety_widget import SafetyWidget
from .subject_widget import SubjectWidget
from .treatment_widget import TreatmentWidget

__all__ = [
    "ActuatorWidget",
    "CameraWidget",
    "ProtocolBuilderWidget",
    "SafetyWidget",
    "SubjectWidget",
    "TreatmentWidget",
]
