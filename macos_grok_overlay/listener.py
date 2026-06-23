# Python libraries
import json
from pathlib import Path

# Apple libraries
from AppKit import (
    NSColor,
    NSEvent,
    NSFont,
    NSMakeRect,
    NSTextAlignmentCenter,
    NSTextField,
    NSView,
    NSEventMaskKeyDown,
    NSEventModifierFlagCommand,
    NSEventModifierFlagControl,
    NSEventModifierFlagOption,
    NSEventModifierFlagShift,
)

# Local libraries
from .constants import LAUNCHER_TRIGGER
from .health_checks import LOG_DIR

TRIGGER_FILE = LOG_DIR / "custom_trigger.json"
SPECIAL_KEY_NAMES = {
    49: "Space", 36: "Return", 53: "Escape",
    122: "F1", 120: "F2", 99: "F3", 118: "F4",
    96: "F5", 97: "F6", 98: "F7", 100: "F8",
    101: "F9", 109: "F10", 103: "F11", 111: "F12",
    123: "Left Arrow", 124: "Right Arrow",
    125: "Down Arrow", 126: "Up Arrow",
}


def ns_event_flags_to_cg_flags(modifiers):
    flags = 0
    if modifiers & NSEventModifierFlagShift:
        flags |= 0x00020000
    if modifiers & NSEventModifierFlagControl:
        flags |= 0x00040000
    if modifiers & NSEventModifierFlagOption:
        flags |= 0x00080000
    if modifiers & NSEventModifierFlagCommand:
        flags |= 0x00100000
    return flags


def update_menu_trigger_label(app):
    flags = LAUNCHER_TRIGGER.get("flags", 0)
    key = LAUNCHER_TRIGGER.get("key", "")
    app.updateTriggerMenu(get_trigger_string(None, flags, key))


def load_custom_launcher_trigger(app):
    if TRIGGER_FILE.exists():
        try:
            with open(TRIGGER_FILE, "r") as trigger_file:
                data = json.load(trigger_file)
                launcher_trigger = {"flags": data["flags"], "key": data["key"]}
            print(
                f"Overwriting default with a custom launch trigger:\n  {launcher_trigger}",
                flush=True,
            )
            print(
                f"Disable custom override and return to default by deleting the file:\n  {TRIGGER_FILE}",
                flush=True,
            )
            LAUNCHER_TRIGGER.update(launcher_trigger)
            update_menu_trigger_label(app)
        except (json.JSONDecodeError, KeyError):
            pass
    app.refresh_hotkey()


def get_modifier_names(flags):
    modifier_names = []
    if flags & 0x00020000:
        modifier_names.append("Shift")
    if flags & 0x00040000:
        modifier_names.append("Control")
    if flags & 0x00080000:
        modifier_names.append("Option")
    if flags & 0x00100000:
        modifier_names.append("Command")
    return modifier_names


def get_trigger_string(event, flags, keycode):
    modifier_names = get_modifier_names(flags)
    key_name = SPECIAL_KEY_NAMES.get(keycode)
    if not key_name:
        if event is not None:
            key_name = event.charactersIgnoringModifiers() or str(keycode)
        else:
            key_name = {
                0: "A", 1: "S", 2: "D", 3: "F", 4: "H", 5: "G", 6: "Z", 7: "X", 8: "C", 9: "V",
                11: "B", 12: "Q", 13: "W", 14: "E", 15: "R", 16: "Y", 17: "T",
                31: "O", 35: "P", 32: "U", 34: "I", 46: "M", 45: "N", 47: "?", 44: ",",
                18: "1", 19: "2", 20: "3", 21: "4", 22: "6", 23: "5", 25: "9", 29: "0",
                27: "7", 24: "=", 26: "-", 28: "8", 43: ";", 41: "'", 42: "\\", 39: "L", 38: "J", 37: "K",
            }.get(keycode, str(keycode))
    return " + ".join(modifier_names + [key_name]) if modifier_names else key_name


def set_custom_launcher_trigger(app):
    app.showWindow_(None)
    print("Setting new launcher trigger.", flush=True)

    content_view = app.window.contentView()
    content_bounds = content_view.bounds()

    overlay_view = NSView.alloc().initWithFrame_(content_bounds)
    overlay_view.setWantsLayer_(True)
    overlay_view.layer().setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.0, 0.5).CGColor())

    container_width = 400
    container_height = 180
    container_x = (content_bounds.size.width - container_width) / 2
    container_y = (content_bounds.size.height - container_height) / 2
    container_frame = NSMakeRect(container_x, container_y, container_width, container_height)
    container_view = NSView.alloc().initWithFrame_(container_frame)
    container_view.setWantsLayer_(True)
    container_view.layer().setBackgroundColor_(NSColor.windowBackgroundColor().CGColor())
    container_view.layer().setCornerRadius_(10)

    message_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 110, container_width, 40))
    message_label.setStringValue_("Press the new trigger key combination now.")
    message_label.setBezeled_(False)
    message_label.setDrawsBackground_(False)
    message_label.setEditable_(False)
    message_label.setSelectable_(False)
    message_label.setAlignment_(NSTextAlignmentCenter)
    message_label.setFont_(NSFont.boldSystemFontOfSize_(17))

    trigger_display_container = NSView.alloc().initWithFrame_(NSMakeRect(60, 50, 280, 38))
    trigger_display_container.setWantsLayer_(True)
    trigger_display_container.layer().setBackgroundColor_(NSColor.lightGrayColor().CGColor())
    trigger_display_container.layer().setCornerRadius_(5)

    trigger_display = NSTextField.alloc().initWithFrame_(NSMakeRect(0, -10, 280, 38))
    trigger_display.setStringValue_("Waiting for key press...")
    trigger_display.setBezeled_(False)
    trigger_display.setDrawsBackground_(False)
    trigger_display.setEditable_(False)
    trigger_display.setSelectable_(False)
    trigger_display.setAlignment_(NSTextAlignmentCenter)
    trigger_display.setFont_(NSFont.systemFontOfSize_(16))

    trigger_display_container.addSubview_(trigger_display)
    container_view.addSubview_(message_label)
    container_view.addSubview_(trigger_display_container)
    overlay_view.addSubview_(container_view)
    content_view.addSubview_(overlay_view)

    def finish_trigger_setup(event):
        flags = ns_event_flags_to_cg_flags(event.modifierFlags())
        keycode = event.keyCode()
        launcher_trigger = {"flags": flags, "key": keycode}
        with open(TRIGGER_FILE, "w") as trigger_file:
            json.dump(launcher_trigger, trigger_file)
        LAUNCHER_TRIGGER.update(launcher_trigger)
        update_menu_trigger_label(app)
        trigger_str = get_trigger_string(event, flags, keycode)
        print("New launcher trigger set:", flush=True)
        print(f"  {launcher_trigger}", flush=True)
        print(f"  {trigger_str}", flush=True)
        trigger_display.setStringValue_(trigger_str)
        overlay_view.performSelector_withObject_afterDelay_("removeFromSuperview", None, 1.5)
        if app.trigger_capture_monitor is not None:
            NSEvent.removeMonitor_(app.trigger_capture_monitor)
            app.trigger_capture_monitor = None
        app.refresh_hotkey()
        app.showWindow_(None)
        return None

    def capture_trigger_key(event):
        if event.keyCode() == 53:  # Escape cancels
            overlay_view.removeFromSuperview()
            if app.trigger_capture_monitor is not None:
                NSEvent.removeMonitor_(app.trigger_capture_monitor)
                app.trigger_capture_monitor = None
            return None
        return finish_trigger_setup(event)

    if app.trigger_capture_monitor is not None:
        NSEvent.removeMonitor_(app.trigger_capture_monitor)
    app.trigger_capture_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
        NSEventMaskKeyDown,
        capture_trigger_key,
    )