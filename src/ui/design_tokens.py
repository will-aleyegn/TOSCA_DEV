"""
Design tokens for TOSCA UI - central source of truth for colors, typography, spacing.

This module provides consistent design values across the entire TOSCA application.
All UI components should import these tokens instead of hard-coding values.

Medical Device Context:
    - Colors chosen for high contrast and medical device suitability
    - Touch-friendly sizing for clinical environments
    - Safety-critical elements (E-Stop, warnings) use prominent colors
    - Light theme support for bright clinical environments (500-1000 lux surgical lighting)

Usage:
    from src.ui.design_tokens import Colors, Typography, Spacing, ButtonSizes, ThemeMode, set_theme

    # Set theme (defaults to DARK)
    set_theme(ThemeMode.LIGHT)

    # Use colors
    button.setStyleSheet(f"background-color: {Colors.SAFE}; {Typography.BUTTON_PRIMARY}")
    layout.setSpacing(Spacing.NORMAL)
"""

from enum import Enum
from typing import Final


class ThemeMode(Enum):
    """Theme mode enumeration for TOSCA UI."""
    DARK = "dark"
    LIGHT = "light"


# Global theme state (defaults to dark)
_current_theme = ThemeMode.DARK


# Theme-specific color palettes

class _DarkTheme:
    """Dark theme palette for TOSCA medical device UI (reduced eye strain)."""

    # Safety states (primary semantic colors) - MUTED PALETTE
    SAFE: str = "#388E3C"  # Deeper green - system safe
    WARNING: str = "#F57C00"  # Muted orange - warning state
    DANGER: str = "#C62828"  # Darker red - unsafe/error
    EMERGENCY: str = "#C62828"  # Darker red - emergency stop

    # Connection states
    CONNECTED: str = "#388E3C"  # Deeper green - hardware connected
    DISCONNECTED: str = "#9E9E9E"  # Gray - hardware offline

    # UI structure
    PRIMARY: str = "#1976D2"  # Blue - primary actions
    TREATING: str = "#0277BD"  # Deeper blue - treating state
    SECONDARY: str = "#757575"  # Gray - secondary actions
    BACKGROUND: str = "#1E1E1E"  # Dark background - main
    PANEL: str = "#2B2B2B"  # Dark panel - background
    HEADER: str = "#37474F"  # Blue-gray - section headers

    # Hardware subsystems
    CAMERA: str = "#64B5F6"  # Light blue
    ACTUATOR: str = "#81C784"  # Light green
    LASER: str = "#FFD54F"  # Yellow
    TEC: str = "#FF8A65"  # Light orange

    # Text (for dark backgrounds)
    TEXT_PRIMARY: str = "#E0E0E0"  # Light gray - readable on dark
    TEXT_SECONDARY: str = "#9E9E9E"  # Medium gray
    TEXT_DISABLED: str = "#616161"  # Darker gray for disabled

    # Backgrounds (subtle overlays for dark theme)
    BG_SUCCESS: str = "#1B5E20"  # Dark green overlay
    BG_WARNING: str = "#E65100"  # Dark orange overlay
    BG_ERROR: str = "#B71C1C"  # Dark red overlay
    BG_INFO: str = "#01579B"  # Dark blue overlay

    # Borders
    BORDER_DEFAULT: str = "#BDBDBD"  # Gray
    BORDER_FOCUS: str = "#1976D2"  # Blue
    BORDER_ERROR: str = "#F44336"  # Red
    BORDER_SUCCESS: str = "#4CAF50"  # Green


class _LightTheme:
    """Light theme palette for bright clinical environments (500-1000 lux surgical lighting)."""

    # Safety states (darker for light backgrounds, WCAG 2.1 AA compliant)
    SAFE: str = "#2E7D32"  # Darker green - system safe
    WARNING: str = "#EF6C00"  # Darker orange - warning state
    DANGER: str = "#C62828"  # Keep same - high contrast
    EMERGENCY: str = "#B71C1C"  # Even darker red - emergency stop

    # Connection states
    CONNECTED: str = "#2E7D32"  # Darker green - hardware connected
    DISCONNECTED: str = "#757575"  # Darker gray - hardware offline

    # UI structure
    PRIMARY: str = "#1565C0"  # Darker blue - primary actions
    TREATING: str = "#0277BD"  # Deeper blue - treating state
    SECONDARY: str = "#616161"  # Darker gray - secondary actions
    BACKGROUND: str = "#FAFAFA"  # Light gray background
    PANEL: str = "#FFFFFF"  # White panel - background
    HEADER: str = "#E0E0E0"  # Light gray - section headers

    # Hardware subsystems (darker for light backgrounds)
    CAMERA: str = "#1976D2"  # Darker blue
    ACTUATOR: str = "#388E3C"  # Darker green
    LASER: str = "#F57C00"  # Darker yellow
    TEC: str = "#E64A19"  # Darker orange

    # Text (for light backgrounds)
    TEXT_PRIMARY: str = "#212121"  # Dark gray - readable on light
    TEXT_SECONDARY: str = "#616161"  # Medium gray
    TEXT_DISABLED: str = "#9E9E9E"  # Light gray for disabled

    # Backgrounds (light overlays)
    BG_SUCCESS: str = "#E8F5E9"  # Light green overlay
    BG_WARNING: str = "#FFF3E0"  # Light orange overlay
    BG_ERROR: str = "#FFEBEE"  # Light red overlay
    BG_INFO: str = "#E3F2FD"  # Light blue overlay

    # Borders
    BORDER_DEFAULT: str = "#BDBDBD"  # Gray
    BORDER_FOCUS: str = "#1976D2"  # Blue
    BORDER_ERROR: str = "#D32F2F"  # Red
    BORDER_SUCCESS: str = "#388E3C"  # Green


class Colors:
    """
    Dynamic color palette for TOSCA medical device UI.

    Colors automatically adjust based on current theme (dark/light).
    Use set_theme() to switch between themes at runtime.

    UPDATED 2025-11-05: Added light theme support for bright clinical environments.
    Dark theme: Muted palette for reduced eye strain during long procedures.
    Light theme: High contrast for 500-1000 lux surgical lighting.
    """

    @property
    def SAFE(self) -> str:
        return _DarkTheme.SAFE if _current_theme == ThemeMode.DARK else _LightTheme.SAFE

    @property
    def WARNING(self) -> str:
        return _DarkTheme.WARNING if _current_theme == ThemeMode.DARK else _LightTheme.WARNING

    @property
    def DANGER(self) -> str:
        return _DarkTheme.DANGER if _current_theme == ThemeMode.DARK else _LightTheme.DANGER

    @property
    def EMERGENCY(self) -> str:
        return _DarkTheme.EMERGENCY if _current_theme == ThemeMode.DARK else _LightTheme.EMERGENCY

    @property
    def CONNECTED(self) -> str:
        return _DarkTheme.CONNECTED if _current_theme == ThemeMode.DARK else _LightTheme.CONNECTED

    @property
    def DISCONNECTED(self) -> str:
        return _DarkTheme.DISCONNECTED if _current_theme == ThemeMode.DARK else _LightTheme.DISCONNECTED

    @property
    def PRIMARY(self) -> str:
        return _DarkTheme.PRIMARY if _current_theme == ThemeMode.DARK else _LightTheme.PRIMARY

    @property
    def TREATING(self) -> str:
        return _DarkTheme.TREATING if _current_theme == ThemeMode.DARK else _LightTheme.TREATING

    @property
    def SECONDARY(self) -> str:
        return _DarkTheme.SECONDARY if _current_theme == ThemeMode.DARK else _LightTheme.SECONDARY

    @property
    def BACKGROUND(self) -> str:
        return _DarkTheme.BACKGROUND if _current_theme == ThemeMode.DARK else _LightTheme.BACKGROUND

    @property
    def PANEL(self) -> str:
        return _DarkTheme.PANEL if _current_theme == ThemeMode.DARK else _LightTheme.PANEL

    @property
    def HEADER(self) -> str:
        return _DarkTheme.HEADER if _current_theme == ThemeMode.DARK else _LightTheme.HEADER

    @property
    def CAMERA(self) -> str:
        return _DarkTheme.CAMERA if _current_theme == ThemeMode.DARK else _LightTheme.CAMERA

    @property
    def ACTUATOR(self) -> str:
        return _DarkTheme.ACTUATOR if _current_theme == ThemeMode.DARK else _LightTheme.ACTUATOR

    @property
    def LASER(self) -> str:
        return _DarkTheme.LASER if _current_theme == ThemeMode.DARK else _LightTheme.LASER

    @property
    def TEC(self) -> str:
        return _DarkTheme.TEC if _current_theme == ThemeMode.DARK else _LightTheme.TEC

    @property
    def TEXT_PRIMARY(self) -> str:
        return _DarkTheme.TEXT_PRIMARY if _current_theme == ThemeMode.DARK else _LightTheme.TEXT_PRIMARY

    @property
    def TEXT_SECONDARY(self) -> str:
        return _DarkTheme.TEXT_SECONDARY if _current_theme == ThemeMode.DARK else _LightTheme.TEXT_SECONDARY

    @property
    def TEXT_DISABLED(self) -> str:
        return _DarkTheme.TEXT_DISABLED if _current_theme == ThemeMode.DARK else _LightTheme.TEXT_DISABLED

    @property
    def BG_SUCCESS(self) -> str:
        return _DarkTheme.BG_SUCCESS if _current_theme == ThemeMode.DARK else _LightTheme.BG_SUCCESS

    @property
    def BG_WARNING(self) -> str:
        return _DarkTheme.BG_WARNING if _current_theme == ThemeMode.DARK else _LightTheme.BG_WARNING

    @property
    def BG_ERROR(self) -> str:
        return _DarkTheme.BG_ERROR if _current_theme == ThemeMode.DARK else _LightTheme.BG_ERROR

    @property
    def BG_INFO(self) -> str:
        return _DarkTheme.BG_INFO if _current_theme == ThemeMode.DARK else _LightTheme.BG_INFO

    @property
    def BORDER_DEFAULT(self) -> str:
        return _DarkTheme.BORDER_DEFAULT if _current_theme == ThemeMode.DARK else _LightTheme.BORDER_DEFAULT

    @property
    def BORDER_FOCUS(self) -> str:
        return _DarkTheme.BORDER_FOCUS if _current_theme == ThemeMode.DARK else _LightTheme.BORDER_FOCUS

    @property
    def BORDER_ERROR(self) -> str:
        return _DarkTheme.BORDER_ERROR if _current_theme == ThemeMode.DARK else _LightTheme.BORDER_ERROR

    @property
    def BORDER_SUCCESS(self) -> str:
        return _DarkTheme.BORDER_SUCCESS if _current_theme == ThemeMode.DARK else _LightTheme.BORDER_SUCCESS


# Create singleton instance
Colors = Colors()


class Typography:
    """Typography scale for consistent text sizing."""

    # Headers
    H1: Final[str] = "font-size: 18pt; font-weight: bold; line-height: 1.2;"
    H2: Final[str] = "font-size: 14pt; font-weight: bold; line-height: 1.3;"
    H3: Final[str] = "font-size: 12pt; font-weight: bold; line-height: 1.4;"

    # Body text
    BODY: Final[str] = "font-size: 11pt; line-height: 1.5;"
    SMALL: Final[str] = "font-size: 10pt; line-height: 1.5;"
    TINY: Final[str] = "font-size: 9pt; line-height: 1.5;"

    # Monospace (for logs, codes)
    MONO: Final[str] = (
        "font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 10pt;"
    )

    # Button text
    BUTTON_PRIMARY: Final[str] = "font-size: 14pt; font-weight: bold;"
    BUTTON_SECONDARY: Final[str] = "font-size: 12pt; font-weight: normal;"
    BUTTON_TERTIARY: Final[str] = "font-size: 11pt; font-weight: normal;"


class Spacing:
    """Spacing scale for consistent layouts (in pixels)."""

    TIGHT: Final[int] = 4  # Minimal spacing
    NORMAL: Final[int] = 8  # Default spacing
    RELAXED: Final[int] = 12  # Comfortable spacing
    LOOSE: Final[int] = 16  # Generous spacing
    SECTION: Final[int] = 24  # Between major sections


class ButtonSizes:
    """Standardized button dimensions (height in pixels)."""

    EMERGENCY: Final[int] = 60  # E-Stop height
    PRIMARY: Final[int] = 50  # Important actions
    SECONDARY: Final[int] = 40  # Regular actions
    TERTIARY: Final[int] = 30  # Minor actions


class BorderRadius:
    """Border radius for rounded corners (in pixels)."""

    SMALL: Final[int] = 2  # Subtle rounding
    NORMAL: Final[int] = 4  # Standard rounding
    LARGE: Final[int] = 8  # Prominent rounding


# Helper functions for creating consistent styles


def create_button_style(
    bg_color: str,
    text_color: str = "#FFFFFF",
    border_color: str = None,
    hover_color: str = None,
    disabled_bg: str = "#BDBDBD",
    disabled_text: str = "#757575",
    font_size: str = "12pt",
    padding: str = "10px 20px",
    border_radius: int = BorderRadius.NORMAL,
    min_height: int = ButtonSizes.SECONDARY,
) -> str:
    """
    Create consistent button stylesheet.

    Args:
        bg_color: Background color (hex)
        text_color: Text color (hex), default white
        border_color: Border color (hex), default slightly darker than bg
        hover_color: Hover background color (hex), default darker than bg
        disabled_bg: Disabled background color (hex)
        disabled_text: Disabled text color (hex)
        font_size: Font size (pt)
        padding: CSS padding value
        border_radius: Corner rounding (px)
        min_height: Minimum button height (px)

    Returns:
        Complete CSS stylesheet string for QPushButton
    """
    if border_color is None:
        border_color = _darken_color(bg_color, 0.2)
    if hover_color is None:
        hover_color = _darken_color(bg_color, 0.1)

    return (
        f"QPushButton {{ "
        f"  background-color: {bg_color}; "
        f"  color: {text_color}; "
        f"  border: 2px solid {border_color}; "
        f"  border-radius: {border_radius}px; "
        f"  padding: {padding}; "
        f"  font-size: {font_size}; "
        f"  font-weight: bold; "
        f"  min-height: {min_height}px; "
        f"}} "
        f"QPushButton:hover {{ "
        f"  background-color: {hover_color}; "
        f"}} "
        f"QPushButton:pressed {{ "
        f"  background-color: {_darken_color(bg_color, 0.15)}; "
        f"}} "
        f"QPushButton:disabled {{ "
        f"  background-color: {disabled_bg}; "
        f"  color: {disabled_text}; "
        f"  border-color: #9E9E9E; "
        f"}}"
    )


def create_input_style(
    border_color: str = Colors.BORDER_DEFAULT,
    focus_color: str = Colors.BORDER_FOCUS,
    bg_color: str = "#FFFFFF",
    padding: str = "8px",
    border_radius: int = BorderRadius.NORMAL,
) -> str:
    """
    Create consistent input field stylesheet.

    Args:
        border_color: Default border color
        focus_color: Border color when focused
        bg_color: Background color
        padding: CSS padding value
        border_radius: Corner rounding (px)

    Returns:
        Complete CSS stylesheet string for QLineEdit
    """
    return (
        f"QLineEdit {{ "
        f"  border: 1px solid {border_color}; "
        f"  border-radius: {border_radius}px; "
        f"  padding: {padding}; "
        f"  background-color: {bg_color}; "
        f"  font-size: 11pt; "
        f"}} "
        f"QLineEdit:focus {{ "
        f"  border: 2px solid {focus_color}; "
        f"}}"
    )


def create_label_style(
    font_size: str = "11pt",
    color: str = Colors.TEXT_PRIMARY,
    bold: bool = False,
) -> str:
    """
    Create consistent label stylesheet.

    Args:
        font_size: Font size (pt)
        color: Text color (hex)
        bold: Whether text should be bold

    Returns:
        Complete CSS stylesheet string for QLabel
    """
    weight = "bold" if bold else "normal"
    return f"font-size: {font_size}; color: {color}; font-weight: {weight};"


def _darken_color(hex_color: str, factor: float = 0.2) -> str:
    """
    Darken a hex color by a factor (0.0 = no change, 1.0 = black).

    Args:
        hex_color: Hex color string (e.g., "#1976D2")
        factor: Darkening factor (0.0 to 1.0)

    Returns:
        Darkened hex color string
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip("#")

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Darken
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))

    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


# Pre-defined button styles for common use cases

BUTTON_PRIMARY = create_button_style(
    bg_color=Colors.PRIMARY,
    text_color="#FFFFFF",
    font_size="12pt",
    min_height=ButtonSizes.SECONDARY,
)

BUTTON_SECONDARY = create_button_style(
    bg_color="#F5F5F5",
    text_color="#424242",
    border_color=Colors.BORDER_DEFAULT,
    hover_color="#EEEEEE",
    font_size="12pt",
    min_height=ButtonSizes.SECONDARY,
)

BUTTON_SUCCESS = create_button_style(
    bg_color=Colors.SAFE,
    text_color="#FFFFFF",
    font_size="12pt",
    min_height=ButtonSizes.SECONDARY,
)

BUTTON_DANGER = create_button_style(
    bg_color=Colors.DANGER,
    text_color="#FFFFFF",
    font_size="12pt",
    min_height=ButtonSizes.SECONDARY,
)

BUTTON_EMERGENCY = create_button_style(
    bg_color=Colors.EMERGENCY,
    text_color="#FFFFFF",
    border_color="#B71C1C",
    font_size="18px",
    padding="12px 20px",
    min_height=ButtonSizes.EMERGENCY,
)

INPUT_DEFAULT = create_input_style()


# Status label helper functions


def create_status_label_style(
    status_type: str,
    font_size: str = "10pt",
    bold: bool = True,
    padding: str = "4px",
) -> str:
    """
    Create consistent status label stylesheet.

    Args:
        status_type: Status type - 'connected', 'disconnected', 'safe', 'unsafe', 'on', 'off'
        font_size: Font size (pt)
        bold: Whether text should be bold
        padding: CSS padding value

    Returns:
        Complete CSS stylesheet string for status QLabel
    """
    # Map status types to colors
    status_colors = {
        "connected": Colors.CONNECTED,
        "disconnected": Colors.DANGER,
        "safe": Colors.SAFE,
        "unsafe": Colors.DANGER,
        "warning": Colors.WARNING,
        "on": Colors.SAFE,
        "off": Colors.TEXT_SECONDARY,
        "enabled": Colors.SAFE,
        "disabled": Colors.TEXT_SECONDARY,
    }

    color = status_colors.get(status_type.lower(), Colors.TEXT_PRIMARY)
    weight = "bold" if bold else "normal"

    return f"font-size: {font_size}; color: {color}; font-weight: {weight}; padding: {padding};"


def create_connection_status_style(connected: bool) -> str:
    """
    Create connection status label stylesheet.

    Args:
        connected: True if connected, False if disconnected

    Returns:
        Complete CSS stylesheet for connection status label
    """
    return create_status_label_style("connected" if connected else "disconnected")


def create_output_status_style(enabled: bool) -> str:
    """
    Create output status label stylesheet (ON/OFF).

    Args:
        enabled: True if output enabled, False if disabled

    Returns:
        Complete CSS stylesheet for output status label
    """
    return create_status_label_style("on" if enabled else "off")


def create_safety_status_style(safe: bool) -> str:
    """
    Create safety status label stylesheet (SAFE/UNSAFE).

    Args:
        safe: True if safe, False if unsafe

    Returns:
        Complete CSS stylesheet for safety status label
    """
    return create_status_label_style("safe" if safe else "unsafe")


# Theme management functions


def set_theme(theme: ThemeMode) -> None:
    """
    Set the current UI theme.

    Args:
        theme: ThemeMode.DARK or ThemeMode.LIGHT

    Note:
        This sets the global theme state. All widgets using Colors will
        automatically reflect the new theme on next stylesheet update.
        Call refresh_all_stylesheets() to force immediate update.
    """
    global _current_theme
    _current_theme = theme


def get_current_theme() -> ThemeMode:
    """
    Get the current UI theme.

    Returns:
        Current ThemeMode (DARK or LIGHT)
    """
    return _current_theme


def toggle_theme() -> ThemeMode:
    """
    Toggle between dark and light themes.

    Returns:
        New theme mode after toggle
    """
    global _current_theme
    _current_theme = ThemeMode.LIGHT if _current_theme == ThemeMode.DARK else ThemeMode.DARK
    return _current_theme
