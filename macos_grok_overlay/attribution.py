# Fork of https://github.com/tchlux/macos-grok-overlay — see ATTRIBUTION.md
from pathlib import Path


def attribution_text():
    path = Path(__file__).resolve().parent / "about" / "attribution.txt"
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return (
            "Fork of macos-grok-overlay by Thomas C.H. Lux (tchlux).\n"
            "https://github.com/tchlux/macos-grok-overlay\n\n"
            "This fork:\n"
            "https://github.com/PreparedToBeReckless/macos-grokAI_and_Grokbuild-menuebar-agent\n\n"
            "Modified by reckless using Grok (xAI). No manual coding by reckless.\n"
            "See ATTRIBUTION.md"
        )


def show_attribution_alert():
    try:
        from AppKit import NSAlert, NSApplication, NSApplicationActivationPolicyRegular

        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        app.activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Attribution")
        alert.setInformativeText_(attribution_text())
        alert.addButtonWithTitle_("OK")
        alert.runModal()
    except Exception:
        print(attribution_text(), flush=True)