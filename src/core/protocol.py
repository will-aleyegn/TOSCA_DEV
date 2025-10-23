"""
Protocol data model classes for action-based treatment protocols.

Defines action types, protocol structure, and validation logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ActionType(Enum):
    """Available protocol action types."""

    SET_LASER_POWER = "SetLaserPower"
    RAMP_LASER_POWER = "RampLaserPower"
    MOVE_ACTUATOR = "MoveActuator"
    WAIT = "Wait"
    LOOP = "Loop"


class RampType(Enum):
    """Power ramp curve types."""

    CONSTANT = "constant"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"


@dataclass
class ActionParameters:
    """Base class for action parameters."""

    pass


@dataclass
class SetLaserPowerParams(ActionParameters):
    """Parameters for SetLaserPower action."""

    power_watts: float

    def validate(self, max_power: float) -> tuple[bool, str]:
        """Validate parameters against safety limits."""
        if self.power_watts < 0:
            return False, "Power cannot be negative"
        if self.power_watts > max_power:
            return False, f"Power {self.power_watts}W exceeds limit {max_power}W"
        return True, ""


@dataclass
class RampLaserPowerParams(ActionParameters):
    """Parameters for RampLaserPower action."""

    start_power_watts: float
    end_power_watts: float
    duration_seconds: float
    ramp_type: RampType = RampType.LINEAR

    def validate(self, max_power: float, max_duration: float) -> tuple[bool, str]:
        """Validate parameters against safety limits."""
        if self.start_power_watts < 0 or self.end_power_watts < 0:
            return False, "Power cannot be negative"
        if max(self.start_power_watts, self.end_power_watts) > max_power:
            return False, f"Power exceeds limit {max_power}W"
        if self.duration_seconds <= 0:
            return False, "Duration must be positive"
        if self.duration_seconds > max_duration:
            return False, f"Duration exceeds limit {max_duration}s"
        return True, ""


@dataclass
class MoveActuatorParams(ActionParameters):
    """Parameters for MoveActuator action."""

    target_position_um: float
    speed_um_per_sec: float

    def validate(
        self, min_position: float, max_position: float, max_speed: float
    ) -> tuple[bool, str]:
        """Validate parameters against safety limits."""
        if self.target_position_um < min_position:
            return False, f"Position {self.target_position_um} below minimum {min_position}"
        if self.target_position_um > max_position:
            return False, f"Position {self.target_position_um} above maximum {max_position}"
        if self.speed_um_per_sec <= 0:
            return False, "Speed must be positive"
        if self.speed_um_per_sec > max_speed:
            return False, f"Speed exceeds limit {max_speed} µm/s"
        return True, ""


@dataclass
class WaitParams(ActionParameters):
    """Parameters for Wait action."""

    duration_seconds: float

    def validate(self, max_duration: float) -> tuple[bool, str]:
        """Validate parameters against safety limits."""
        if self.duration_seconds <= 0:
            return False, "Duration must be positive"
        if self.duration_seconds > max_duration:
            return False, f"Duration exceeds limit {max_duration}s"
        return True, ""


@dataclass
class LoopParams(ActionParameters):
    """Parameters for Loop action."""

    repeat_count: int  # -1 for infinite
    actions: List["ProtocolAction"] = field(default_factory=list)

    def validate(self) -> tuple[bool, str]:
        """Validate loop parameters."""
        if self.repeat_count == 0:
            return False, "Repeat count cannot be zero"
        if self.repeat_count < -1:
            return False, "Repeat count must be -1 (infinite) or positive"
        if not self.actions:
            return False, "Loop must contain at least one action"
        return True, ""


@dataclass
class ProtocolAction:
    """Single action in a protocol sequence."""

    action_id: int
    action_type: ActionType
    parameters: ActionParameters
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary for JSON serialization."""
        params_dict: Dict[str, Any] = {}

        if isinstance(self.parameters, SetLaserPowerParams):
            params_dict = {"power_watts": self.parameters.power_watts}

        elif isinstance(self.parameters, RampLaserPowerParams):
            params_dict = {
                "start_power_watts": self.parameters.start_power_watts,
                "end_power_watts": self.parameters.end_power_watts,
                "duration_seconds": self.parameters.duration_seconds,
                "ramp_type": self.parameters.ramp_type.value,
            }

        elif isinstance(self.parameters, MoveActuatorParams):
            params_dict = {
                "target_position_um": self.parameters.target_position_um,
                "speed_um_per_sec": self.parameters.speed_um_per_sec,
            }

        elif isinstance(self.parameters, WaitParams):
            params_dict = {"duration_seconds": self.parameters.duration_seconds}

        elif isinstance(self.parameters, LoopParams):
            params_dict = {
                "repeat_count": self.parameters.repeat_count,
                "actions": [action.to_dict() for action in self.parameters.actions],
            }

        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "parameters": params_dict,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ProtocolAction":
        """Create action from dictionary (JSON deserialization)."""
        action_type = ActionType(data["action_type"])
        params_data = data["parameters"]

        params: Union[
            SetLaserPowerParams, RampLaserPowerParams, MoveActuatorParams, WaitParams, LoopParams
        ]
        if action_type == ActionType.SET_LASER_POWER:
            params = SetLaserPowerParams(power_watts=params_data["power_watts"])

        elif action_type == ActionType.RAMP_LASER_POWER:
            params = RampLaserPowerParams(
                start_power_watts=params_data["start_power_watts"],
                end_power_watts=params_data["end_power_watts"],
                duration_seconds=params_data["duration_seconds"],
                ramp_type=RampType(params_data.get("ramp_type", "linear")),
            )

        elif action_type == ActionType.MOVE_ACTUATOR:
            params = MoveActuatorParams(
                target_position_um=params_data["target_position_um"],
                speed_um_per_sec=params_data["speed_um_per_sec"],
            )

        elif action_type == ActionType.WAIT:
            params = WaitParams(duration_seconds=params_data["duration_seconds"])

        elif action_type == ActionType.LOOP:
            nested_actions = [
                ProtocolAction.from_dict(action_data) for action_data in params_data["actions"]
            ]
            params = LoopParams(repeat_count=params_data["repeat_count"], actions=nested_actions)

        else:
            raise ValueError(f"Unknown action type: {action_type}")

        return ProtocolAction(
            action_id=data["action_id"],
            action_type=action_type,
            parameters=params,
            notes=data.get("notes", ""),
        )


@dataclass
class SafetyLimits:
    """Safety limits for protocol validation."""

    max_power_watts: float = 10.0
    max_duration_seconds: float = 300.0
    min_actuator_position_um: float = 0.0
    max_actuator_position_um: float = 3000.0
    max_actuator_speed_um_per_sec: float = 200.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "max_power_watts": self.max_power_watts,
            "max_duration_seconds": self.max_duration_seconds,
            "min_actuator_position_um": self.min_actuator_position_um,
            "max_actuator_position_um": self.max_actuator_position_um,
        }

    @staticmethod
    def from_dict(data: Dict[str, float]) -> "SafetyLimits":
        """Create from dictionary."""
        return SafetyLimits(
            max_power_watts=data.get("max_power_watts", 10.0),
            max_duration_seconds=data.get("max_duration_seconds", 300.0),
            min_actuator_position_um=data.get("min_actuator_position_um", 0.0),
            max_actuator_position_um=data.get("max_actuator_position_um", 3000.0),
        )


@dataclass
class Protocol:
    """Complete treatment protocol with actions and metadata."""

    protocol_name: str
    version: str
    actions: List[ProtocolAction]
    description: str = ""
    created_date: Optional[datetime] = None
    author: str = ""
    safety_limits: SafetyLimits = field(default_factory=SafetyLimits)

    def __post_init__(self) -> None:
        """Set created_date if not provided."""
        if self.created_date is None:
            self.created_date = datetime.now()

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate entire protocol against safety limits.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        if not self.protocol_name:
            errors.append("Protocol name is required")

        if not self.actions:
            errors.append("Protocol must contain at least one action")

        # Validate each action
        for action in self.actions:
            valid, error = self._validate_action(action)
            if not valid:
                errors.append(f"Action {action.action_id}: {error}")

        return len(errors) == 0, errors

    def _validate_action(self, action: ProtocolAction) -> tuple[bool, str]:
        """Validate single action against safety limits."""
        if isinstance(action.parameters, SetLaserPowerParams):
            return action.parameters.validate(self.safety_limits.max_power_watts)

        elif isinstance(action.parameters, RampLaserPowerParams):
            return action.parameters.validate(
                self.safety_limits.max_power_watts,
                self.safety_limits.max_duration_seconds,
            )

        elif isinstance(action.parameters, MoveActuatorParams):
            return action.parameters.validate(
                self.safety_limits.min_actuator_position_um,
                self.safety_limits.max_actuator_position_um,
                self.safety_limits.max_actuator_speed_um_per_sec,
            )

        elif isinstance(action.parameters, WaitParams):
            return action.parameters.validate(self.safety_limits.max_duration_seconds)

        elif isinstance(action.parameters, LoopParams):
            valid, error = action.parameters.validate()
            if not valid:
                return False, error

            # Validate nested actions
            for nested_action in action.parameters.actions:
                valid, error = self._validate_action(nested_action)
                if not valid:
                    return False, f"Nested action: {error}"

            return True, ""

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol to dictionary for JSON serialization."""
        return {
            "protocol_name": self.protocol_name,
            "version": self.version,
            "description": self.description,
            "created_date": (self.created_date.isoformat() if self.created_date else None),
            "author": self.author,
            "safety_limits": self.safety_limits.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Protocol":
        """Create protocol from dictionary (JSON deserialization)."""
        created_date = None
        if data.get("created_date"):
            created_date = datetime.fromisoformat(data["created_date"])

        actions = [ProtocolAction.from_dict(a) for a in data["actions"]]

        safety_limits = SafetyLimits.from_dict(data.get("safety_limits", {}))

        return Protocol(
            protocol_name=data["protocol_name"],
            version=data["version"],
            description=data.get("description", ""),
            created_date=created_date,
            author=data.get("author", ""),
            safety_limits=safety_limits,
            actions=actions,
        )

    def calculate_total_duration(self) -> float:
        """
        Calculate estimated total duration in seconds.

        Note: Does not account for infinite loops.
        Returns -1 if protocol contains infinite loop.
        """
        return self._calculate_actions_duration(self.actions)

    def _calculate_actions_duration(self, actions: List[ProtocolAction]) -> float:
        """Recursively calculate duration for list of actions."""
        total = 0.0

        for action in actions:
            if isinstance(action.parameters, WaitParams):
                total += action.parameters.duration_seconds

            elif isinstance(action.parameters, RampLaserPowerParams):
                total += action.parameters.duration_seconds

            elif isinstance(action.parameters, LoopParams):
                if action.parameters.repeat_count == -1:
                    return -1.0  # Infinite loop

                nested_duration = self._calculate_actions_duration(action.parameters.actions)
                if nested_duration == -1.0:
                    return -1.0

                total += nested_duration * action.parameters.repeat_count

        return total
