import objc
from AppKit import (
    NSApp,
    NSBackingStoreBuffered,
    NSBezelStyleRounded,
    NSColor,
    NSFont,
    NSMakeRect,
    NSNotificationCenter,
    NSObject,
    NSPanel,
    NSPopUpMenuWindowLevel,
    NSScreen,
    NSTextField,
    NSWindowStyleMaskFullSizeContentView,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskUtilityWindow,
)


class QuickAskController(NSObject):
    def initWithAppDelegate_(self, app_delegate):
        self = objc.super(QuickAskController, self).init()
        if self is None:
            return None
        self.app_delegate = app_delegate
        self.panel = None
        self.input_field = None
        return self

    def _ensure_panel(self):
        if self.panel is not None:
            return

        width = 560
        height = 64
        screen = NSScreen.mainScreen().frame()
        origin_x = screen.origin.x + (screen.size.width - width) / 2
        origin_y = screen.origin.y + screen.size.height - height - 96

        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(origin_x, origin_y, width, height),
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskUtilityWindow
            | NSWindowStyleMaskFullSizeContentView,
            NSBackingStoreBuffered,
            False,
        )
        self.panel.setTitle_("Ask Grok")
        self.panel.setFloatingPanel_(True)
        self.panel.setBecomesKeyOnlyIfNeeded_(False)
        self.panel.setHidesOnDeactivate_(False)
        self.panel.setLevel_(NSPopUpMenuWindowLevel)
        self.panel.setBackgroundColor_(NSColor.windowBackgroundColor())

        content = self.panel.contentView()
        bounds = content.bounds()
        self.input_field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(16, 14, bounds.size.width - 32, 28)
        )
        self.input_field.setPlaceholderString_("Ask Grok anything...")
        self.input_field.setFont_(NSFont.systemFontOfSize_(15))
        self.input_field.setBezelStyle_(NSBezelStyleRounded)
        self.input_field.setTarget_(self)
        self.input_field.setAction_("submitQuickAsk:")
        content.addSubview_(self.input_field)

        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            "panelDidResignKey:",
            "NSWindowDidResignKeyNotification",
            self.panel,
        )

    def show(self):
        self._ensure_panel()
        self.input_field.setStringValue_("")

        screen = NSScreen.mainScreen().frame()
        width = 560
        height = 64
        origin_x = screen.origin.x + (screen.size.width - width) / 2
        origin_y = screen.origin.y + screen.size.height - height - 96
        self.panel.setFrame_display_(NSMakeRect(origin_x, origin_y, width, height), True)

        NSApp.activateIgnoringOtherApps_(True)
        self.panel.makeKeyAndOrderFront_(None)
        self.input_field.becomeFirstResponder()

    def hide(self):
        if self.panel is not None:
            self.panel.orderOut_(None)

    def submitQuickAsk_(self, sender):
        question = self.input_field.stringValue().strip()
        if not question:
            return
        self.hide()
        self.app_delegate.submitQuestion_(question)

    def panelDidResignKey_(self, notification):
        if notification.object() == self.panel:
            self.hide()

    def cleanup(self):
        NSNotificationCenter.defaultCenter().removeObserver_(self)
        self.hide()
        self.panel = None
        self.input_field = None