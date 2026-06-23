import platform
import re

# Apple libraries
from Quartz import (
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)


def get_safari_user_agent():
    """Build a Safari user agent that tracks the host macOS major version."""
    mac_version = platform.mac_ver()[0] or "15.0"
    safari_major = mac_version.split(".")[0]
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        f"Version/{safari_major}.0 Safari/605.1.15"
    )


def parse_css_rgb_color(color_string):
    """Parse rgb()/rgba() CSS colors into normalized 0-1 floats."""
    if not color_string:
        return None
    match = re.search(r"rgba?\(([^)]+)\)", color_string.strip())
    if not match:
        return None
    parts = [part.strip() for part in match.group(1).split(",")]
    if len(parts) < 3:
        return None
    try:
        values = [float(parts[i]) for i in range(3)]
    except ValueError:
        return None
    if any(value > 1.0 for value in values):
        values = [value / 255.0 for value in values]
    return tuple(values)


WEBSITE = "https://grok.com?referrer=macos-grok-overlay"
LOGO_WHITE_PATH = "logo/logo_white.png"
LOGO_BLACK_PATH = "logo/logo_black.png"
FRAME_SAVE_NAME = "GrokWindowFrame"
COMPACT_WINDOW_WIDTH = 420
COMPACT_WINDOW_HEIGHT = 640
APP_TITLE = "Grok"
PERMISSION_CHECK_EXIT = 1
CORNER_RADIUS = 15.0
DRAG_AREA_HEIGHT = 30
STATUS_ITEM_CONTEXT = 1
LAUNCHER_TRIGGER_MASK = (
    kCGEventFlagMaskShift |
    kCGEventFlagMaskControl |
    kCGEventFlagMaskAlternate |
    kCGEventFlagMaskCommand
)
# Default trigger is "Option + Space".
LAUNCHER_TRIGGER = {
    "flags": kCGEventFlagMaskAlternate,
    "key": 49
}
# Global quick-ask palette: Option + Shift + G
QUICK_ASK_TRIGGER = {
    "flags": kCGEventFlagMaskAlternate | kCGEventFlagMaskShift,
    "key": 5,
}
