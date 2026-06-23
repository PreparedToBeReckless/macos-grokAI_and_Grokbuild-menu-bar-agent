# Python libraries.
import getpass
import os
import subprocess
import sys
import time
from pathlib import Path

# Apple libraries.
import plistlib
from Foundation import NSDictionary, NSBundle
from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt

# Local libraries
from .constants import APP_TITLE
from .health_checks import reset_crash_counter


def get_plist_path():
    username = getpass.getuser()
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    return launch_agents_dir / f"com.{username}.macos{APP_TITLE.lower()}overlay.plist"


def _bundle_executable(app_path):
    plist_path = os.path.join(app_path, "Contents", "Info.plist")
    with open(plist_path, "rb") as plist_file:
        plist_data = plistlib.load(plist_file)
    executable_name = plist_data.get("CFBundleExecutable")
    if not executable_name:
        raise RuntimeError(f"CFBundleExecutable missing from {plist_path}")
    return os.path.join(app_path, "Contents", "MacOS", executable_name)


def get_app_bundle_path():
    if getattr(sys, "frozen", False):
        bundle_path = NSBundle.mainBundle().bundlePath()
        if bundle_path:
            return bundle_path
        app_path = sys.argv[0]
        while app_path and not app_path.endswith(".app"):
            app_path = os.path.dirname(app_path)
        return app_path or None
    return None


# Get the command used to launch this app.
def get_executable():
    app_bundle = get_app_bundle_path()
    if app_bundle:
        # Launch the .app via `open` so login startup runs as a normal GUI process.
        return ["/usr/bin/open", "-a", app_bundle]
    return [sys.executable, "-m", f"macos_{APP_TITLE.lower()}_overlay"]


def is_startup_installed():
    return get_plist_path().exists()


def _install_startup_error(message):
    print(message, flush=True)
    return False, message


# Install the app as a startup application using a Launch Agent.
def install_startup():
    username = getpass.getuser()
    program_args = get_executable()
    plist = {
        "Label": f"com.{username}.macos{APP_TITLE.lower()}overlay",
        "ProgramArguments": program_args,
        "RunAtLoad": True,
        "KeepAlive": False,
    }
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = get_plist_path()
    try:
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        with open(plist_path, "wb") as handle:
            plistlib.dump(plist, handle)
    except PermissionError:
        return _install_startup_error(
            "Could not write to ~/Library/LaunchAgents.\n\n"
            "That folder must be owned by your user account. "
            "In Terminal, run:\n"
            "  sudo chown $(whoami):staff ~/Library/LaunchAgents"
        )
    except OSError as exc:
        return _install_startup_error(f"Could not create the login item file:\n{exc}")

    result = subprocess.run(
        ["launchctl", "load", "-w", str(plist_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        try:
            plist_path.unlink(missing_ok=True)
        except OSError:
            pass
        return _install_startup_error(
            "macOS could not enable the login item.\n\n"
            f"{detail or 'launchctl load failed.'}"
        )

    print(f"Installed as startup app. Launch Agent created at {plist_path}.", flush=True)
    print(f"To disable, run: macos-{APP_TITLE.lower()}-overlay --uninstall-startup", flush=True)
    return True, (
        "Grok Overlay will now start automatically when you log in.\n\n"
        "The menu item will change to \"Uninstall Autolauncher\" "
        "after the app restarts."
    )


# Uninstall the app from running at login.
def uninstall_startup():
    plist_path = get_plist_path()
    if plist_path.exists():
        unload = subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True,
            text=True,
        )
        if unload.returncode != 0:
            print(
                "Failed to unload launch agent. Encountered error when running "
                f"`launchctl unload {plist_path}`.\n{unload.stderr.strip()}\n"
            )
        else:
            print("Uninstalled Launch Agent.")
        print(f"Removed {plist_path}.")
        os.remove(plist_path)
        return True
    else:
        print("Launch Agent not found. Nothing to uninstall.")
        return False


# Check if the current process has Accessibility permissions.
def check_permissions(ask=True):
    print(
        "\nChecking permission to utilize macOS Accessibility features to listen for "
        "the Option+Space keyboard sequence. If permission is not currently granted, "
        "a request will be made through the dialogue for the current executor "
        "(e.g., Terminal, python3, ...).\n",
        flush=True,
    )
    options = NSDictionary.dictionaryWithObject_forKey_(
        True,
        kAXTrustedCheckOptionPrompt
    )
    is_trusted = AXIsProcessTrustedWithOptions(options if ask else None)
    return is_trusted


def open_accessibility_settings():
    subprocess.run(
        [
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ],
        check=False,
    )


# Spawn a child process to check the latest permission status.
def get_updated_permission_status():
    result = subprocess.run(
        get_executable() + ["--check-permissions"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


# Wait for permissions to be granted, checking periodically.
def wait_for_permissions(max_wait_sec=60, wait_interval_sec=5):
    elapsed = 0
    while elapsed < max_wait_sec:
        if get_updated_permission_status():
            return True
        time.sleep(wait_interval_sec)
        elapsed += wait_interval_sec
        reset_crash_counter()
    return False


# Ensure Accessibility permissions are granted, relaunching if necessary.
# Returns: True (ready), "restart" (exit for KeepAlive relaunch), False (failed).
def ensure_accessibility_permissions():
    if check_permissions():
        return True
    print(
        "Accessibility permission is required for the keyboard shortcut. "
        "Open System Settings → Privacy & Security → Accessibility and enable this app.",
        flush=True,
    )
    open_accessibility_settings()
    if wait_for_permissions():
        print(
            "Permissions granted. Exiting so the autolauncher can restart with access.",
            flush=True,
        )
        return "restart"
    print(
        "Permissions not granted within the time limit. "
        "Uninstalling autolauncher since startup cannot work without Accessibility access.",
        flush=True,
    )
    uninstall_startup()
    return False