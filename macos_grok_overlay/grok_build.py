# FORK of https://github.com/tchlux/macos-grok-overlay — see ATTRIBUTION.md
# Modified by reckless using Grok (xAI); no manual coding by reckless.
import os
import shutil
import subprocess
from pathlib import Path


GROK_CLI_INSTALL_URL = "https://x.ai/cli/install.sh"
GROK_CLI_INSTALL_COMMAND = f"curl -fsSL {GROK_CLI_INSTALL_URL} | bash"
SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "Grok Overlay"
AGENT_COMMAND_PATH = SUPPORT_DIR / "launch-grok-build.command"
INSTALL_COMMAND_PATH = SUPPORT_DIR / "install-grok-cli.command"


def find_agent_executable():
    candidates = [
        Path.home() / ".grok" / "bin" / "agent",
        Path.home() / ".local" / "bin" / "agent",
    ]
    which_path = shutil.which("agent")
    if which_path:
        candidates.append(Path(which_path))

    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file() and os.access(resolved, os.X_OK):
            return resolved
    return None


def default_working_directory():
    desktop_grok = Path.home() / "Desktop" / "grok"
    if desktop_grok.is_dir():
        return desktop_grok
    return Path.home()


def _write_executable_command(path, body):
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)


def ensure_agent_command():
    work_dir = default_working_directory()
    _write_executable_command(
        AGENT_COMMAND_PATH,
        f"""#!/bin/zsh
export PATH="$HOME/.grok/bin:$HOME/.local/bin:$PATH"
cd {shlex_quote(str(work_dir))}
exec agent
""",
    )
    return AGENT_COMMAND_PATH


def ensure_install_command():
    _write_executable_command(
        INSTALL_COMMAND_PATH,
        f"""#!/bin/zsh
{GROK_CLI_INSTALL_COMMAND}
""",
    )
    return INSTALL_COMMAND_PATH


def shlex_quote(value):
    if not value:
        return "''"
    if all(ch not in " \t\n\"'$\\`" for ch in value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _open_command_file(command_path):
    return subprocess.run(
        ["/usr/bin/open", str(command_path)],
        capture_output=True,
        text=True,
    )


def _overlay_app_bundle():
    import sys

    if not getattr(sys, "frozen", False):
        return None
    try:
        executable = Path(sys.executable).resolve()
        bundle = executable.parent.parent.parent
        if bundle.suffix == ".app" and bundle.is_dir():
            return bundle
    except OSError:
        return None
    return None


def find_grok_build_app():
    candidates = []
    overlay_bundle = _overlay_app_bundle()
    if overlay_bundle is not None:
        candidates.append(overlay_bundle.parent / "Grok Build.app")

    candidates.extend(
        [
            Path("/Applications") / "Grok Build.app",
            Path.home() / "Applications" / "Grok Build.app",
        ]
    )

    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        executable = resolved / "Contents" / "MacOS" / "GrokBuild"
        if resolved.is_dir() and executable.is_file():
            return resolved
    return None


def _open_grok_build_app(app_path):
    return subprocess.run(
        ["/usr/bin/open", "-n", str(app_path)],
        capture_output=True,
        text=True,
    )


def _run_agent_in_terminal(work_dir):
    applescript = """on run argv
    set workDir to item 1 of argv
    tell application "Terminal"
        activate
        do script "export PATH=\\"$HOME/.grok/bin:$HOME/.local/bin:$PATH\\"; cd " & quoted form of workDir & "; agent"
    end tell
end run
"""
    return subprocess.run(
        ["/usr/bin/osascript", "-", str(work_dir)],
        input=applescript,
        capture_output=True,
        text=True,
    )


def offer_grok_cli_install():
    try:
        from AppKit import (
            NSAlert,
            NSAlertFirstButtonReturn,
            NSApplication,
            NSApplicationActivationPolicyRegular,
        )

        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        app.activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Install Grok Build?")
        alert.setInformativeText_(
            "The Grok CLI (`agent`) is not installed yet.\n\n"
            "Grok Overlay will open Terminal and run the official installer:\n"
            f"  {GROK_CLI_INSTALL_COMMAND}\n\n"
            "After installation finishes, use Grok Build again from this menu."
        )
        alert.addButtonWithTitle_("Install")
        alert.addButtonWithTitle_("Cancel")
        return alert.runModal() == NSAlertFirstButtonReturn
    except Exception:
        return False


def install_grok_cli():
    result = _open_command_file(ensure_install_command())
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        return False, f"Could not open Terminal to install Grok Build.\n\n{detail or 'open failed.'}"
    return True, ""


def launch_grok_build():
    if find_agent_executable() is None:
        return False, (
            "Could not find the Grok Build agent.\n\n"
            "Install the Grok CLI so `agent` is available, usually at:\n"
            "  ~/.grok/bin/agent"
        )

    grok_build_app = find_grok_build_app()
    if grok_build_app is not None:
        result = _open_grok_build_app(grok_build_app)
        if result.returncode == 0:
            return True, ""
        detail = (result.stderr or result.stdout or "").strip()
        return False, f"Could not open Grok Build.\n\n{detail or 'open failed.'}"

    result = _run_agent_in_terminal(default_working_directory())
    if result.returncode == 0:
        return True, ""
    detail = (result.stderr or result.stdout or "").strip()
    return False, f"Could not open Terminal for Grok Build.\n\n{detail or 'Terminal launch failed.'}"