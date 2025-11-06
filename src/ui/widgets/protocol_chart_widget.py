"""
Module: Protocol Chart Widget
Project: TOSCA Laser Control System

Purpose: Reusable protocol visualization chart showing actuator position and laser power
         trajectories over time. Used in Protocol Builder and Treatment Workflow tabs.
Safety Critical: No
"""

import logging
from typing import Optional

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from core.protocol_line import (
    HomeParams,
    LaserRampParams,
    LaserSetCurrentParams,
    LaserSetParams,
    MoveParams,
    MoveType,
    ProtocolLine,
)
from ui.design_tokens import Colors

logger = logging.getLogger(__name__)


class ProtocolChartWidget(QWidget):
    """
    Reusable protocol visualization chart.

    Displays:
    - Actuator position trajectory (left Y-axis, blue)
    - Laser power/current trajectory (right Y-axis, orange)
    - Safety limit lines (if configured)
    - Time progression on X-axis
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.protocol_lines: list[ProtocolLine] = []
        self.safety_limits = None  # Optional safety limits

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the chart UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create pyqtgraph plot widget with dual Y-axes
        self.position_plot = pg.PlotWidget()
        self.position_plot.setBackground("w")
        self.position_plot.setLabel("left", "Position", units="mm", color="blue")
        self.position_plot.setLabel("bottom", "Time", units="s")
        self.position_plot.setTitle("Actuator Position & Laser Power Over Time")
        self.position_plot.showGrid(x=True, y=True, alpha=0.3)
        self.position_plot.setMinimumHeight(300)

        # Create second Y-axis for laser power/current (right side)
        self.laser_axis = pg.ViewBox()
        self.position_plot.scene().addItem(self.laser_axis)
        self.position_plot.getAxis("right").linkToView(self.laser_axis)
        self.laser_axis.setXLink(self.position_plot)
        self.position_plot.getAxis("right").setLabel("Power/Current", units="mW/mA", color="orange")
        self.position_plot.showAxis("right")
        self.position_plot.getAxis("right").setStyle(showValues=True)

        # Update views when plot is resized
        def update_views():
            self.laser_axis.setGeometry(self.position_plot.getViewBox().sceneBoundingRect())
            self.laser_axis.linkedViewChanged(
                self.position_plot.getViewBox(), self.laser_axis.XAxis
            )

        self.position_plot.getViewBox().sigResized.connect(update_views)

        # Add reference line at zero
        self.position_plot.addLine(
            y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
        )

        layout.addWidget(self.position_plot)

    def set_protocol_lines(self, lines: list[ProtocolLine]) -> None:
        """Set protocol lines and update the chart."""
        self.protocol_lines = lines
        self._update_chart()

    def set_safety_limits(self, safety_limits) -> None:
        """Set safety limits for position markers."""
        self.safety_limits = safety_limits
        self._update_chart()

    def clear_chart(self) -> None:
        """Clear all protocol data from chart."""
        self.protocol_lines = []
        self._update_chart()

    def _update_chart(self) -> None:
        """Update the position and laser power chart based on current protocol."""
        self.position_plot.clear()
        self.laser_axis.clear()

        if len(self.protocol_lines) == 0:
            # Add reference line and empty state
            self.position_plot.addLine(
                y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
            )
            return

        # Calculate position and laser power trajectories
        time_points = [0.0]
        position_points = [0.0]  # Start at home position
        laser_time_points = [0.0]
        laser_power_points = [0.0]  # Start with laser off
        current_position = 0.0
        current_time = 0.0

        for line in self.protocol_lines:
            line_loops = line.loop_count if hasattr(line, "loop_count") else 1

            for _ in range(line_loops):
                # Calculate duration for this line
                line_duration = line.calculate_duration(current_position)

                # Track start time for this line
                line_start_time = current_time

                # Update position based on movement
                if isinstance(line.movement, MoveParams):
                    target_pos = line.movement.target_position_mm
                    if line.movement.move_type == MoveType.RELATIVE:
                        target_pos = current_position + target_pos

                    # Add intermediate point for movement
                    time_points.append(current_time + line_duration)
                    position_points.append(target_pos)
                    current_position = target_pos

                elif isinstance(line.movement, HomeParams):
                    # Move to home (0)
                    time_points.append(current_time + line_duration)
                    position_points.append(0.0)
                    current_position = 0.0

                else:
                    # No movement, dwell at current position
                    if line.dwell is not None:
                        time_points.append(current_time + line.dwell.duration_s)
                        position_points.append(current_position)

                # Update laser power (convert W to mW or display mA for graph)
                if line.laser is not None:
                    if isinstance(line.laser, LaserSetParams):
                        # Power mode: Convert W to mW
                        power_mw = line.laser.power_watts * 1000.0
                        laser_time_points.append(line_start_time)
                        laser_power_points.append(power_mw)
                        laser_time_points.append(current_time + line_duration)
                        laser_power_points.append(power_mw)
                    elif isinstance(line.laser, LaserSetCurrentParams):
                        # Current mode: Display mA value directly
                        current_ma = line.laser.current_milliamps
                        laser_time_points.append(line_start_time)
                        laser_power_points.append(current_ma)
                        laser_time_points.append(current_time + line_duration)
                        laser_power_points.append(current_ma)
                    elif isinstance(line.laser, LaserRampParams):
                        # Ramping power - add intermediate points for smooth ramp (convert to mW)
                        num_points = 10
                        for i in range(num_points + 1):
                            fraction = i / num_points
                            ramp_time = line_start_time + (line.laser.duration_s * fraction)
                            ramp_power_w = line.laser.start_power_watts + (
                                (line.laser.end_power_watts - line.laser.start_power_watts)
                                * fraction
                            )
                            ramp_power_mw = ramp_power_w * 1000.0
                            laser_time_points.append(ramp_time)
                            laser_power_points.append(ramp_power_mw)
                else:
                    # Laser off during this line
                    laser_time_points.append(line_start_time)
                    laser_power_points.append(0.0)
                    laser_time_points.append(current_time + line_duration)
                    laser_power_points.append(0.0)

                current_time += line_duration

        # Plot position trajectory (left Y-axis, blue)
        self.position_plot.plot(
            time_points,
            position_points,
            pen=pg.mkPen("b", width=2),
            symbol="o",
            symbolSize=6,
            symbolBrush="b",
            name="Position",
        )

        # Plot laser power trajectory (right Y-axis, orange/red)
        laser_curve = pg.PlotCurveItem(
            laser_time_points,
            laser_power_points,
            pen=pg.mkPen(Colors.WARNING, width=2),
            name="Laser Power",
        )
        self.laser_axis.addItem(laser_curve)

        # Add reference lines
        self.position_plot.addLine(
            y=0, pen=pg.mkPen("r", width=1, style=pg.QtCore.Qt.PenStyle.DashLine)
        )

        # Add safety limit lines if available
        if self.safety_limits:
            self.position_plot.addLine(
                y=self.safety_limits.max_actuator_position_mm,
                pen=pg.mkPen("orange", width=1, style=pg.QtCore.Qt.PenStyle.DashLine),
            )
            self.position_plot.addLine(
                y=self.safety_limits.min_actuator_position_mm,
                pen=pg.mkPen("orange", width=1, style=pg.QtCore.Qt.PenStyle.DashLine),
            )
