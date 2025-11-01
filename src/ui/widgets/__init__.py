"""
UI widgets for TOSCA application.

Note: Removed widgets (replaced by newer implementations):
- ActuatorWidget: Replaced by ActuatorConnectionWidget (Phase 3, 2025-10-30)
- TreatmentWidget: Replaced by ActiveTreatmentWidget (Phase 3, 2025-10-30)
- ProtocolBuilderWidget: Replaced by LineProtocolBuilderWidget (Task 8, 2025-11-01)
"""

from .camera_widget import CameraWidget
from .config_display_widget import ConfigDisplayWidget
from .laser_widget import LaserWidget
from .safety_widget import SafetyWidget
from .subject_widget import SubjectWidget
from .tec_widget import TECWidget

__all__ = [
    "CameraWidget",
    "ConfigDisplayWidget",
    "LaserWidget",
    "SafetyWidget",
    "SubjectWidget",
    "TECWidget",
]
