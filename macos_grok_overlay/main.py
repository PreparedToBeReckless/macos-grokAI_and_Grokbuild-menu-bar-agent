# Python libraries
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Local libraries.
from .constants import APP_TITLE
from .app import AppDelegate, NSApplication
from .launcher import install_startup, uninstall_startup
from .health_checks import health_check_decorator

APP_BUNDLE_NAME = "Grok Overlay.app"


def find_app_bundle():
    candidates = [
        Path("/Applications") / APP_BUNDLE_NAME,
        Path.home() / "Applications" / APP_BUNDLE_NAME,
        Path(__file__).resolve().parents[2] / "dmg-builder" / "dist" / APP_BUNDLE_NAME,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def launch_detached_app_bundle():
    app_bundle = find_app_bundle()
    if app_bundle is None:
        return False
    subprocess.Popen(
        ["open", "-n", str(app_bundle)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return True


def should_detach_from_terminal(args):
    if getattr(sys, "frozen", False):
        return False
    if os.environ.get("GROK_OVERLAY_DETACHED") == "1":
        return False
    if args.install_startup or args.uninstall_startup or args.check_permissions:
        return False
    return sys.stdout.isatty()


# Main executable for running the application from the command line.
@health_check_decorator
def main():
    parser = argparse.ArgumentParser(
        description=(
            f"macOS {APP_TITLE} Overlay App - Dedicated window that can be summoned "
            "and dismissed with the keyboard command Option+Space."
        )
    )
    parser.add_argument(
        "--install-startup",
        action="store_true",
        help="Install the app to run at login",
    )
    parser.add_argument(
        "--uninstall-startup",
        action="store_true",
        help="Uninstall the app from running at login",
    )
    parser.add_argument(
        "--check-permissions",
        action="store_true",
        help="Legacy flag kept for compatibility (no longer required)",
    )
    args = parser.parse_args()

    if args.install_startup:
        result = install_startup()
        if isinstance(result, tuple):
            ok, message = result
            if message:
                print(message, flush=True)
            if not ok:
                sys.exit(1)
        return

    if args.uninstall_startup:
        uninstall_startup()
        return

    if args.check_permissions:
        print("Accessibility permission is no longer required for the keyboard shortcut.")
        sys.exit(0)

    if should_detach_from_terminal(args):
        if launch_detached_app_bundle():
            print(f"Launched {APP_BUNDLE_NAME} as its own app process.")
            return
        print(
            "Tip: install Grok Overlay.app to /Applications and launch from Finder "
            "for a standalone app process.",
            flush=True,
        )

    print()
    print(f"Starting {APP_TITLE} Overlay.")
    print("Use Option+Space to show/hide the window.")
    print()
    print(f"To run at login, use:      macos-{APP_TITLE.lower()}-overlay --install-startup")
    print(f"To remove from login, use: macos-{APP_TITLE.lower()}-overlay --uninstall-startup")
    print()
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()