import ctypes
from ctypes import CFUNCTYPE, Structure, byref, c_int, c_uint32, c_void_p

# Carbon hotkeys work without Accessibility permission (unlike CGEventTap).
carbon = ctypes.CDLL("/System/Library/Frameworks/Carbon.framework/Carbon")

CARBON_CMD = 0x0100
CARBON_SHIFT = 0x0200
CARBON_OPTION = 0x0800
CARBON_CONTROL = 0x1000

K_EVENT_CLASS_KEYBOARD = 0x6B657962  # 'keyb'
K_EVENT_HOT_KEY_PRESSED = 6

HOTKEY_SIGNATURE = 0x47524F4B  # 'GROK'


class EventHotKeyID(Structure):
    _fields_ = [("signature", c_uint32), ("id", c_uint32)]


class EventTypeSpec(Structure):
    _fields_ = [("eventClass", c_uint32), ("eventKind", c_uint32)]


EVENT_HANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)

carbon.RegisterEventHotKey.argtypes = [
    c_uint32,
    c_uint32,
    EventHotKeyID,
    c_void_p,
    c_uint32,
    ctypes.POINTER(c_void_p),
]
carbon.RegisterEventHotKey.restype = c_int
carbon.UnregisterEventHotKey.argtypes = [c_void_p]
carbon.UnregisterEventHotKey.restype = c_int
carbon.GetApplicationEventTarget.restype = c_void_p
carbon.InstallEventHandler.argtypes = [
    c_void_p,
    EVENT_HANDLER,
    c_uint32,
    ctypes.POINTER(EventTypeSpec),
    c_void_p,
    ctypes.POINTER(c_void_p),
]
carbon.InstallEventHandler.restype = c_int
carbon.RemoveEventHandler.argtypes = [c_void_p]
carbon.RemoveEventHandler.restype = c_int


def cg_flags_to_carbon_modifiers(flags):
    modifiers = 0
    if flags & 0x00020000:
        modifiers |= CARBON_SHIFT
    if flags & 0x00040000:
        modifiers |= CARBON_CONTROL
    if flags & 0x00080000:
        modifiers |= CARBON_OPTION
    if flags & 0x00100000:
        modifiers |= CARBON_CMD
    return modifiers


class CarbonHotKeyManager:
    def __init__(self, callback, hotkey_id=1):
        self._callback = callback
        self._hotkey_id = hotkey_id
        self._hotkey_ref = c_void_p()
        self._handler_ref = c_void_p()
        self._handler_proc = EVENT_HANDLER(self._event_handler)
        self._handler_installed = False

    def _event_handler(self, _call_ref, _event, _user_data):
        try:
            self._callback()
        except Exception as exc:
            print(f"Hotkey callback failed: {exc}", flush=True)
        return 0

    def install_handler(self):
        if self._handler_installed:
            return
        event_spec = EventTypeSpec(K_EVENT_CLASS_KEYBOARD, K_EVENT_HOT_KEY_PRESSED)
        status = carbon.InstallEventHandler(
            carbon.GetApplicationEventTarget(),
            self._handler_proc,
            1,
            byref(event_spec),
            None,
            byref(self._handler_ref),
        )
        if status != 0:
            raise RuntimeError(f"InstallEventHandler failed with status {status}")
        self._handler_installed = True

    def register(self, keycode, cg_flags):
        self.unregister()
        carbon_modifiers = cg_flags_to_carbon_modifiers(cg_flags)
        hotkey_id = EventHotKeyID(HOTKEY_SIGNATURE, self._hotkey_id)
        status = carbon.RegisterEventHotKey(
            int(keycode),
            int(carbon_modifiers),
            hotkey_id,
            carbon.GetApplicationEventTarget(),
            0,
            byref(self._hotkey_ref),
        )
        if status != 0:
            raise RuntimeError(
                f"RegisterEventHotKey failed with status {status} "
                f"(key={keycode}, modifiers={carbon_modifiers})"
            )

    def unregister(self):
        if self._hotkey_ref.value:
            carbon.UnregisterEventHotKey(self._hotkey_ref)
            self._hotkey_ref = c_void_p()

    def cleanup(self):
        self.unregister()
        if self._handler_ref.value:
            carbon.RemoveEventHandler(self._handler_ref)
            self._handler_ref = c_void_p()
        self._handler_installed = False