"""
Actuator sequence builder models.

Defines action types and sequence step structures for building
automated movement sequences.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ActionType(Enum):
    """Types of actions that can be performed in a sequence."""

    MOVE_ABSOLUTE = "Move Absolute"
    MOVE_RELATIVE = "Move Relative"
    HOME = "Home"
    PAUSE = "Pause"
    SET_SPEED = "Set Speed"
    SCAN = "Scan"


class SequenceAction:
    """Single action in a movement sequence."""

    def __init__(self, action_type: ActionType, params: Optional[dict[str, Any]] = None) -> None:
        self.action_type = action_type
        self.params = params or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"action_type": self.action_type.name, "params": self.params}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SequenceAction":
        """Create from dictionary (JSON deserialization)."""
        return cls(ActionType[data["action_type"]], data["params"])

    def __str__(self) -> str:
        """Human-readable string representation."""
        # Get laser power for display
        laser_power = self.params.get("laser_power", 0)
        power_str = f" @ {laser_power:.0f}mW" if laser_power > 0 else ""

        if self.action_type == ActionType.MOVE_ABSOLUTE:
            pos = self.params.get("position", 0)
            unit = self.params.get("unit", "um")
            return f"Move to {pos:.1f} {unit}{power_str}"

        elif self.action_type == ActionType.MOVE_RELATIVE:
            dist = self.params.get("distance", 0)
            unit = self.params.get("unit", "um")
            return f"Move {dist:+.1f} {unit}{power_str}"

        elif self.action_type == ActionType.HOME:
            return f"Home{power_str}"

        elif self.action_type == ActionType.PAUSE:
            dur = self.params.get("duration", 0)
            return f"Pause {dur:.1f}s{power_str}"

        elif self.action_type == ActionType.SET_SPEED:
            speed = self.params.get("speed", 0)
            unit = self.params.get("unit", "um")
            return f"Set speed {speed:.1f} {unit}/s{power_str}"

        elif self.action_type == ActionType.SCAN:
            direction = self.params.get("direction", "positive")
            dur = self.params.get("duration", 0)
            return f"Scan {direction} {dur:.1f}s{power_str}"

        return str(self.action_type.value)


class ActuatorSequence:
    """Complete movement sequence with loop configuration."""

    def __init__(self) -> None:
        self.actions: list[SequenceAction] = []
        self.loop_enabled = False
        self.loop_count = 1

    def add_action(self, action: SequenceAction) -> None:
        """Add action to sequence."""
        self.actions.append(action)

    def remove_action(self, index: int) -> None:
        """Remove action at index."""
        if 0 <= index < len(self.actions):
            del self.actions[index]

    def move_action_up(self, index: int) -> bool:
        """Move action up in sequence."""
        if index > 0 and index < len(self.actions):
            self.actions[index], self.actions[index - 1] = (
                self.actions[index - 1],
                self.actions[index],
            )
            return True
        return False

    def move_action_down(self, index: int) -> bool:
        """Move action down in sequence."""
        if index >= 0 and index < len(self.actions) - 1:
            self.actions[index], self.actions[index + 1] = (
                self.actions[index + 1],
                self.actions[index],
            )
            return True
        return False

    def clear(self) -> None:
        """Clear all actions."""
        self.actions = []

    def save(self, file_path: Path) -> None:
        """Save sequence to JSON file."""
        data = {
            "actions": [action.to_dict() for action in self.actions],
            "loop_enabled": self.loop_enabled,
            "loop_count": self.loop_count,
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, file_path: Path) -> None:
        """Load sequence from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        self.actions = [SequenceAction.from_dict(action_data) for action_data in data["actions"]]
        self.loop_enabled = data.get("loop_enabled", False)
        self.loop_count = data.get("loop_count", 1)

    def __len__(self) -> int:
        """Return number of actions in sequence."""
        return len(self.actions)
