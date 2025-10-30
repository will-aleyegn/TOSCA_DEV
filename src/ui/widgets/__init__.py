"""
UI widgets for TOSCA application.

Note: ActuatorWidget and TreatmentWidget removed in Phase 3 refactor (2025-10-30)
- ActuatorWidget: Replaced by ActuatorConnectionWidget with direct controller management
- TreatmentWidget: Replaced by ActiveTreatmentWidget
"""

from .camera_widget import CameraWidget
from .config_display_widget import ConfigDisplayWidget
from .laser_widget import LaserWidget
from .protocol_builder_widget import ProtocolBuilderWidget
from .safety_widget import SafetyWidget
from .subject_widget import SubjectWidget
from .tec_widget import TECWidget

__all__ = [
    "CameraWidget",
    "ConfigDisplayWidget",
    "LaserWidget",
    "ProtocolBuilderWidget",
    "SafetyWidget",
    "SubjectWidget",
    "TECWidget",
]
