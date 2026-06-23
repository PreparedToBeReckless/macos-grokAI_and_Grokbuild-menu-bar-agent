"""
macOS Grok Overlay - A macOS overlay app for Grok.

FORK: https://github.com/tchlux/macos-grok-overlay (Thomas C.H. Lux, MIT)
Maintained by reckless; modifications via Grok (xAI) — see ATTRIBUTION.md
"""

import os

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ABOUT_DIR = os.path.join(DIRECTORY, "about")
with open(os.path.join(ABOUT_DIR, "version.txt")) as f:
    __version__ = f.read().strip()
with open(os.path.join(ABOUT_DIR, "author.txt")) as f:
    __author__ = f.read().strip()

__upstream__ = "https://github.com/tchlux/macos-grok-overlay"
__upstream_author__ = "Thomas C.H. Lux (tchlux)"
__fork_maintainer__ = "reckless"
__fork_method__ = "Modified using Grok (xAI); no manual coding by reckless."

__all__ = ["main"]

from .main import main
