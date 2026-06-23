import os
import sys

from AppKit import NSImage, NSSize

from .constants import LOGO_BLACK_PATH, LOGO_WHITE_PATH


def _module_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _resource_dir():
    if getattr(sys, "frozen", False):
        return os.environ.get("RESOURCEPATH", _module_dir())
    return _module_dir()


def resolve_asset_path(*relative_parts):
    """Find bundled assets in py2app and development layouts."""
    candidates = [
        os.path.join(_module_dir(), *relative_parts),
        os.path.join(_resource_dir(), *relative_parts),
    ]
    if len(relative_parts) == 2 and relative_parts[0] == "logo":
        filename = relative_parts[1]
        candidates.extend([
            os.path.join(_resource_dir(), filename),
            os.path.join(_module_dir(), filename),
        ])
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def load_image(relative_parts, size=18, template=False):
    path = resolve_asset_path(*relative_parts)
    image = NSImage.alloc().initWithContentsOfFile_(path)
    if image is not None:
        image.setSize_(NSSize(size, size))
        if template:
            image.setTemplate_(True)
        return image
    return None


def load_status_bar_fallback_image(size=16):
    image = NSImage.imageWithSystemSymbolName_accessibilityDescription_("sparkles", "Grok Overlay")
    if image is not None:
        image.setSize_(NSSize(size, size))
        image.setTemplate_(True)
    return image


def load_status_bar_images():
    # Colored PNG logos must not use template mode — template masks hide them in the menu bar.
    white = load_image(LOGO_WHITE_PATH.split("/"), size=18, template=False)
    black = load_image(LOGO_BLACK_PATH.split("/"), size=18, template=False)
    fallback = load_status_bar_fallback_image()
    return white, black, fallback