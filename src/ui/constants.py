"""
UI constants for TOSCA application.

Provides standardized dimensions, colors, and other UI-related constants
to ensure consistency across all widgets and dialogs.
"""

# Widget Width Constants
# ======================
# Standard widths for common widget sizes to maintain UI consistency

# Main widget widths (for control panels)
WIDGET_WIDTH_EXTRA_WIDE = 900  # Extra wide widgets (protocol builder)
WIDGET_WIDTH_STANDARD = 800  # Standard widget width (laser, TEC, GPIO, safety, config)
WIDGET_WIDTH_MEDIUM = 700  # Medium widgets (actuator, GPIO alternative)
WIDGET_WIDTH_COMPACT = 600  # Compact widgets (treatment setup)
WIDGET_WIDTH_GRID = 450  # Grid layout widgets (4-column fit for Hardware Tab)
WIDGET_WIDTH_NARROW = 450  # Narrow widgets (active treatment scroll, camera controls)
WIDGET_WIDTH_MINIMAL = 400  # Minimal widgets (subject info)
WIDGET_WIDTH_PANEL = 350  # Side panels (camera group)

# Input field widths
INPUT_WIDTH_STANDARD = 100  # Standard input fields (exposure, gain)
INPUT_WIDTH_BUTTON = 120  # Standard button width (stop button)
INPUT_WIDTH_LABEL = 150  # Standard label minimum width
INPUT_WIDTH_LABEL_COMPACT = 110  # Compact label width (interlocks)

# Dialog/Window widths (if needed in future)
DIALOG_WIDTH_SMALL = 400
DIALOG_WIDTH_MEDIUM = 600
DIALOG_WIDTH_LARGE = 800

# Spacing Constants
# =================
SPACING_SMALL = 5
SPACING_MEDIUM = 10
SPACING_LARGE = 20

# Height Constants
# ================
BUTTON_HEIGHT_STANDARD = 30
BUTTON_HEIGHT_LARGE = 50  # For important actions (enable output, etc.)

# Common UI Colors
# ================
# Safety-critical color scheme
COLOR_SUCCESS = "#4CAF50"  # Green - safe/enabled
COLOR_WARNING = "#FFC107"  # Amber - warning
COLOR_ERROR = "#f44336"  # Red - error/disabled
COLOR_INFO = "#2196F3"  # Blue - info/aiming laser
COLOR_NEUTRAL = "#9E9E9E"  # Gray - neutral/off

# Color aliases for semantic meaning
COLOR_LASER_ENABLE = COLOR_SUCCESS  # Laser enable button
COLOR_LASER_DISABLE = COLOR_ERROR  # Laser disable button
COLOR_TEC_ENABLE = COLOR_INFO  # TEC enable button
COLOR_TEC_DISABLE = COLOR_NEUTRAL  # TEC disable button
COLOR_AIMING_LASER_ON = COLOR_INFO  # Aiming laser on
COLOR_AIMING_LASER_OFF = COLOR_NEUTRAL  # Aiming laser off

# Status colors
COLOR_STATUS_CONNECTED = COLOR_SUCCESS
COLOR_STATUS_DISCONNECTED = COLOR_ERROR
COLOR_STATUS_CONNECTING = COLOR_WARNING

# Font Sizes
# ==========
FONT_SIZE_SMALL = "10px"
FONT_SIZE_STANDARD = "12px"
FONT_SIZE_LARGE = "14px"
FONT_SIZE_XLARGE = "16px"
FONT_SIZE_BUTTON_LARGE = "16px"  # For large action buttons
