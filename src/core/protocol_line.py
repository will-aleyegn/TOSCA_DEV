"""
Line-based protocol data model for concurrent action execution.

This module defines a new protocol structure where each "line" can contain
multiple concurrent actions (movement, laser control, dwell time).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class MoveType(Enum):
    """Actuator movement types."""

    ABSOLUTE = "absolute"
    RELATIVE = "relative"


@dataclass
class MoveParams:
    """Parameters for actuator movement."""

    target_position_mm: float
    speed_mm_per_s: float
    move_type: MoveType = MoveType.ABSOLUTE

    def validate(
        self, min_position: float, max_position: float, max_speed: float
    ) -> tuple[bool, str]:
        """Validate movement parameters against safety limits."""
        if self.move_type == MoveType.ABSOLUTE:
            if self.target_position_mm < min_position:
                return False, f"Position {self.target_position_mm}mm below minimum {min_position}mm"
            if self.target_position_mm > max_position:
                return False, f"Position {self.target_position_mm}mm above maximum {max_position}mm"

        if self.speed_mm_per_s <= 0:
            return False, "Speed must be positive"
        if self.speed_mm_per_s > max_speed:
            return False, f"Speed {self.speed_mm_per_s}mm/s exceeds limit {max_speed}mm/s"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "target_position_mm": self.target_position_mm,
            "speed_mm_per_s": self.speed_mm_per_s,
            "move_type": self.move_type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MoveParams":
        """Create from dictionary (JSON deserialization)."""
        return MoveParams(
            target_position_mm=data["target_position_mm"],
            speed_mm_per_s=data["speed_mm_per_s"],
            move_type=MoveType(data.get("move_type", "absolute")),
        )


@dataclass
class HomeParams:
    """Parameters for homing operation."""

    speed_mm_per_s: float = 2.0  # Default homing speed

    def validate(self, max_speed: float) -> tuple[bool, str]:
        """Validate homing parameters."""
        if self.speed_mm_per_s <= 0:
            return False, "Homing speed must be positive"
        if self.speed_mm_per_s > max_speed:
            return False, f"Homing speed {self.speed_mm_per_s}mm/s exceeds limit {max_speed}mm/s"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"speed_mm_per_s": self.speed_mm_per_s}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "HomeParams":
        """Create from dictionary (JSON deserialization)."""
        return HomeParams(speed_mm_per_s=data.get("speed_mm_per_s", 2.0))


@dataclass
class LaserSetParams:
    """Parameters for setting fixed laser power."""

    power_watts: float

    def validate(self, max_power: float) -> tuple[bool, str]:
        """Validate laser power parameters."""
        if self.power_watts < 0:
            return False, "Laser power cannot be negative"
        if self.power_watts > max_power:
            return False, f"Laser power {self.power_watts}W exceeds limit {max_power}W"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"power_watts": self.power_watts}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LaserSetParams":
        """Create from dictionary (JSON deserialization)."""
        return LaserSetParams(power_watts=data["power_watts"])


@dataclass
class LaserRampParams:
    """Parameters for ramping laser power over time."""

    start_power_watts: float
    end_power_watts: float
    duration_s: float  # Explicit ramp duration

    def validate(self, max_power: float, max_duration: float) -> tuple[bool, str]:
        """Validate laser ramp parameters."""
        if self.start_power_watts < 0 or self.end_power_watts < 0:
            return False, "Laser power cannot be negative"
        if max(self.start_power_watts, self.end_power_watts) > max_power:
            return False, f"Laser power exceeds limit {max_power}W"
        if self.duration_s <= 0:
            return False, "Ramp duration must be positive"
        if self.duration_s > max_duration:
            return False, f"Ramp duration {self.duration_s}s exceeds limit {max_duration}s"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "start_power_watts": self.start_power_watts,
            "end_power_watts": self.end_power_watts,
            "duration_s": self.duration_s,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LaserRampParams":
        """Create from dictionary (JSON deserialization)."""
        return LaserRampParams(
            start_power_watts=data["start_power_watts"],
            end_power_watts=data["end_power_watts"],
            duration_s=data["duration_s"],
        )


@dataclass
class DwellParams:
    """Parameters for dwelling (waiting) at current state."""

    duration_s: float

    def validate(self, max_duration: float) -> tuple[bool, str]:
        """Validate dwell parameters."""
        if self.duration_s <= 0:
            return False, "Dwell duration must be positive"
        if self.duration_s > max_duration:
            return False, f"Dwell duration {self.duration_s}s exceeds limit {max_duration}s"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"duration_s": self.duration_s}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DwellParams":
        """Create from dictionary (JSON deserialization)."""
        return DwellParams(duration_s=data["duration_s"])


@dataclass
class ProtocolLine:
    """
    Single line in a protocol with concurrent actions.

    Each line can optionally contain:
    - Movement (either standard move OR home, not both)
    - Laser control (either set power OR ramp power, not both)
    - Dwell time (explicit wait duration)

    The total duration of the line is the maximum of all enabled actions' durations.
    """

    line_number: int
    movement: Optional[Union[MoveParams, HomeParams]] = None
    laser: Optional[Union[LaserSetParams, LaserRampParams]] = None
    dwell: Optional[DwellParams] = None
    notes: str = ""

    def calculate_duration(self, current_position_mm: float = 0.0) -> float:
        """
        Calculate total line duration in seconds.

        Line duration is the MAXIMUM of:
        - Move duration (distance / speed)
        - Laser ramp duration (explicit)
        - Dwell duration (explicit)

        Args:
            current_position_mm: Current actuator position for move duration calculation

        Returns:
            Total line duration in seconds
        """
        durations = []

        # Movement duration
        if isinstance(self.movement, MoveParams):
            if self.movement.move_type == MoveType.ABSOLUTE:
                distance = abs(self.movement.target_position_mm - current_position_mm)
            else:  # RELATIVE
                distance = abs(self.movement.target_position_mm)

            move_duration = distance / self.movement.speed_mm_per_s
            durations.append(move_duration)

        elif isinstance(self.movement, HomeParams):
            # Homing duration depends on current position
            # Assume worst-case: full travel distance
            # This should be refined based on actual hardware limits
            home_duration = abs(current_position_mm) / self.movement.speed_mm_per_s
            durations.append(home_duration)

        # Laser ramp duration
        if isinstance(self.laser, LaserRampParams):
            durations.append(self.laser.duration_s)

        # Dwell duration
        if self.dwell is not None:
            durations.append(self.dwell.duration_s)

        # Return maximum duration, or 0 if no actions
        return max(durations) if durations else 0.0

    def get_summary(self, current_position_mm: float = 0.0) -> str:
        """
        Generate concise summary string for UI display.

        Example: "Line 1: [Move] 5.0mm @ 2.0mm/s | [Laser] Set 2.0W | [Dwell] 3.0s | Duration: 3.0s"
        """
        parts = [f"Line {self.line_number}:"]

        # Movement summary
        if isinstance(self.movement, MoveParams):
            move_type = "Abs" if self.movement.move_type == MoveType.ABSOLUTE else "Rel"
            parts.append(
                f"[Move {move_type}] {self.movement.target_position_mm:.1f}mm"
                f" @ {self.movement.speed_mm_per_s:.1f}mm/s"
            )
        elif isinstance(self.movement, HomeParams):
            parts.append(f"[Home] @ {self.movement.speed_mm_per_s:.1f}mm/s")

        # Laser summary
        if isinstance(self.laser, LaserSetParams):
            parts.append(f"[Laser] Set {self.laser.power_watts:.1f}W")
        elif isinstance(self.laser, LaserRampParams):
            parts.append(
                f"[Laser] Ramp {self.laser.start_power_watts:.1f}W"
                f" → {self.laser.end_power_watts:.1f}W"
            )

        # Dwell summary
        if self.dwell is not None:
            parts.append(f"[Dwell] {self.dwell.duration_s:.1f}s")

        # Total duration
        duration = self.calculate_duration(current_position_mm)
        parts.append(f"Duration: {duration:.1f}s")

        return " | ".join(parts)

    def validate(self, safety_limits: "SafetyLimits") -> tuple[bool, str]:
        """
        Validate line against safety limits.

        Returns:
            (is_valid, error_message)
        """
        # Validate movement
        if isinstance(self.movement, MoveParams):
            valid, error = self.movement.validate(
                safety_limits.min_actuator_position_mm,
                safety_limits.max_actuator_position_mm,
                safety_limits.max_actuator_speed_mm_per_s,
            )
            if not valid:
                return False, f"Movement: {error}"

        elif isinstance(self.movement, HomeParams):
            valid, error = self.movement.validate(safety_limits.max_actuator_speed_mm_per_s)
            if not valid:
                return False, f"Homing: {error}"

        # Validate laser
        if isinstance(self.laser, LaserSetParams):
            valid, error = self.laser.validate(safety_limits.max_power_watts)
            if not valid:
                return False, f"Laser: {error}"

        elif isinstance(self.laser, LaserRampParams):
            valid, error = self.laser.validate(
                safety_limits.max_power_watts,
                safety_limits.max_duration_seconds,
            )
            if not valid:
                return False, f"Laser ramp: {error}"

        # Validate dwell
        if self.dwell is not None:
            valid, error = self.dwell.validate(safety_limits.max_duration_seconds)
            if not valid:
                return False, f"Dwell: {error}"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "line_number": self.line_number,
            "notes": self.notes,
        }

        # Movement
        if isinstance(self.movement, MoveParams):
            result["movement"] = {"type": "move", "params": self.movement.to_dict()}
        elif isinstance(self.movement, HomeParams):
            result["movement"] = {"type": "home", "params": self.movement.to_dict()}

        # Laser
        if isinstance(self.laser, LaserSetParams):
            result["laser"] = {"type": "set", "params": self.laser.to_dict()}
        elif isinstance(self.laser, LaserRampParams):
            result["laser"] = {"type": "ramp", "params": self.laser.to_dict()}

        # Dwell
        if self.dwell is not None:
            result["dwell"] = self.dwell.to_dict()

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ProtocolLine":
        """Create from dictionary (JSON deserialization)."""
        # Parse movement
        movement: Optional[Union[MoveParams, HomeParams]] = None
        if "movement" in data and data["movement"] is not None:
            move_data = data["movement"]
            if move_data["type"] == "move":
                movement = MoveParams.from_dict(move_data["params"])
            elif move_data["type"] == "home":
                movement = HomeParams.from_dict(move_data["params"])

        # Parse laser
        laser: Optional[Union[LaserSetParams, LaserRampParams]] = None
        if "laser" in data and data["laser"] is not None:
            laser_data = data["laser"]
            if laser_data["type"] == "set":
                laser = LaserSetParams.from_dict(laser_data["params"])
            elif laser_data["type"] == "ramp":
                laser = LaserRampParams.from_dict(laser_data["params"])

        # Parse dwell
        dwell: Optional[DwellParams] = None
        if "dwell" in data and data["dwell"] is not None:
            dwell = DwellParams.from_dict(data["dwell"])

        return ProtocolLine(
            line_number=data["line_number"],
            movement=movement,
            laser=laser,
            dwell=dwell,
            notes=data.get("notes", ""),
        )


@dataclass
class SafetyLimits:
    """Safety limits for protocol validation."""

    max_power_watts: float = 10.0
    max_duration_seconds: float = 300.0
    min_actuator_position_mm: float = -20.0  # Support negative positions (bidirectional)
    max_actuator_position_mm: float = 20.0
    max_actuator_speed_mm_per_s: float = 5.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "max_power_watts": self.max_power_watts,
            "max_duration_seconds": self.max_duration_seconds,
            "min_actuator_position_mm": self.min_actuator_position_mm,
            "max_actuator_position_mm": self.max_actuator_position_mm,
            "max_actuator_speed_mm_per_s": self.max_actuator_speed_mm_per_s,
        }

    @staticmethod
    def from_dict(data: Dict[str, float]) -> "SafetyLimits":
        """Create from dictionary."""
        return SafetyLimits(
            max_power_watts=data.get("max_power_watts", 10.0),
            max_duration_seconds=data.get("max_duration_seconds", 300.0),
            min_actuator_position_mm=data.get("min_actuator_position_mm", 0.0),
            max_actuator_position_mm=data.get("max_actuator_position_mm", 20.0),
            max_actuator_speed_mm_per_s=data.get("max_actuator_speed_mm_per_s", 5.0),
        )


@dataclass
class LineBasedProtocol:
    """Complete treatment protocol with line-based concurrent actions."""

    protocol_name: str
    version: str
    lines: List[ProtocolLine]
    loop_count: int = 1  # Number of times to repeat the protocol
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

        if not self.lines:
            errors.append("Protocol must contain at least one line")

        if self.loop_count < 1:
            errors.append("Loop count must be at least 1")

        # Validate each line
        for line in self.lines:
            valid, error = line.validate(self.safety_limits)
            if not valid:
                errors.append(f"Line {line.line_number}: {error}")

        return len(errors) == 0, errors

    def calculate_total_duration(self) -> float:
        """
        Calculate total protocol duration in seconds.

        Accounts for loop count and simulates position changes.
        """
        total_duration = 0.0
        current_position_mm = 0.0  # Assume starting at home

        for _ in range(self.loop_count):
            for line in self.lines:
                line_duration = line.calculate_duration(current_position_mm)
                total_duration += line_duration

                # Update current position for next line
                if isinstance(line.movement, MoveParams):
                    if line.movement.move_type == MoveType.ABSOLUTE:
                        current_position_mm = line.movement.target_position_mm
                    else:  # RELATIVE
                        current_position_mm += line.movement.target_position_mm
                elif isinstance(line.movement, HomeParams):
                    current_position_mm = 0.0

        return total_duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol to dictionary for JSON serialization."""
        return {
            "protocol_name": self.protocol_name,
            "version": self.version,
            "description": self.description,
            "loop_count": self.loop_count,
            "created_date": (self.created_date.isoformat() if self.created_date else None),
            "author": self.author,
            "safety_limits": self.safety_limits.to_dict(),
            "lines": [line.to_dict() for line in self.lines],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LineBasedProtocol":
        """Create protocol from dictionary (JSON deserialization)."""
        created_date = None
        if data.get("created_date"):
            created_date = datetime.fromisoformat(data["created_date"])

        lines = [ProtocolLine.from_dict(line_data) for line_data in data["lines"]]
        safety_limits = SafetyLimits.from_dict(data.get("safety_limits", {}))

        return LineBasedProtocol(
            protocol_name=data["protocol_name"],
            version=data["version"],
            description=data.get("description", ""),
            loop_count=data.get("loop_count", 1),
            created_date=created_date,
            author=data.get("author", ""),
            safety_limits=safety_limits,
            lines=lines,
        )
