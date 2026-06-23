# FORK of https://github.com/tchlux/macos-grok-overlay (Thomas C.H. Lux, MIT)
# Modified by reckless using Grok (xAI) — no manual coding by reckless. See ATTRIBUTION.md
#
# Python libraries
import os
import traceback

# Apple libraries
import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyRegular,
    NSAppearanceNameAqua,
    NSAppearanceNameDarkAqua,
    NSBackingStoreBuffered,
    NSButton,
    NSColor,
    NSFont,
    NSImage,
    NSImageLeft,
    NSKeyValueObservingOptionNew,
    NSMakeRect,
    NSMenu,
    NSMenuItem,
    NSNotificationCenter,
    NSSize,
    NSStatusBar,
    NSVariableStatusItemLength,
    NSView,
    NSViewHeightSizable,
    NSViewWidthSizable,
    NSWindow,
    NSNormalWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorFullScreenPrimary,
    NSWindowCollectionBehaviorManaged,
    NSWindowDidResizeNotification,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskFullSizeContentView,
    NSWindowStyleMaskMiniaturizable,
    NSWindowStyleMaskResizable,
    NSWindowStyleMaskTitled,
    NSWindowTitleHidden,
    NSEvent,
    NSEventMaskLeftMouseDown,
    NSEventMaskRightMouseDown,
    NSEventModifierFlagCommand,
    NSEventModifierFlagControl,
    NSEventModifierFlagOption,
    NSEventModifierFlagShift,
    NSEventTypeRightMouseDown,
    NSEventTypeRightMouseUp,
    NSObject,
    NSScreen,
    NSWorkspace,
)
from AVFoundation import AVCaptureDevice, AVMediaTypeAudio
from Foundation import NSDate, NSURL, NSURLRequest
from WebKit import (
    WKNavigationActionPolicyAllow,
    WKNavigationActionPolicyCancel,
    WKNavigationTypeLinkActivated,
    WKUserScript,
    WKUserScriptInjectionTimeAtDocumentEnd,
    WKWebView,
    WKWebViewConfiguration,
    WKWebsiteDataStore,
)

IN_APP_POPUP_HOST_SUFFIXES = (
    "grok.com",
    "x.ai",
    "x.com",
    "twitter.com",
)

# Local libraries
from .constants import (
    APP_TITLE,
    COMPACT_WINDOW_HEIGHT,
    COMPACT_WINDOW_WIDTH,
    CORNER_RADIUS,
    FRAME_SAVE_NAME,
    STATUS_ITEM_CONTEXT,
    WEBSITE,
    LAUNCHER_TRIGGER,
    QUICK_ASK_TRIGGER,
    get_safari_user_agent,
    parse_css_rgb_color,
)
from .assets import load_status_bar_images
from .grok_inject import build_submit_question_js
from .attribution import show_attribution_alert
from .grok_build import find_agent_executable, install_grok_cli, launch_grok_build, offer_grok_cli_install
from .hotkey import CarbonHotKeyManager
from .quick_ask import QuickAskController
from .launcher import (
    install_startup,
    is_startup_installed,
    uninstall_startup,
)
from .listener import (
    load_custom_launcher_trigger,
    set_custom_launcher_trigger,
    update_menu_trigger_label,
)
from .health_checks import LOG_PATH, reset_crash_counter, show_startup_alert


# Custom window (contains entire application).
class AppWindow(NSWindow):
    def canBecomeKeyWindow(self):
        return True

    def keyDown_(self, event):
        self.delegate().keyDown_(event)


# Custom view (contains click-and-drag area on top sliver of overlay).
class DragArea(NSView):
    def initWithFrame_(self, frame):
        objc.super(DragArea, self).initWithFrame_(frame)
        self.setWantsLayer_(True)
        return self

    def setBackgroundColor_(self, color):
        self.layer().setBackgroundColor_(color.CGColor())

    def mouseDown_(self, event):
        self.window().performWindowDragWithEvent_(event)


# The main delegate for running the overlay app.
class AppDelegate(NSObject):
    def init(self):
        self = objc.super(AppDelegate, self).init()
        if self is None:
            return None
        self.hotkey_manager = None
        self.quick_ask_hotkey_manager = None
        self.quick_ask_controller = None
        self.pending_question = None
        self.trigger_capture_monitor = None
        self.popup_windows = []
        self._web_content_loaded = False
        return self

    def applicationDidFinishLaunching_(self, notification):
        try:
            self._finish_launching()
            reset_crash_counter()
        except Exception:
            error_trace = traceback.format_exc()
            with open(LOG_PATH, "w") as log_file:
                log_file.write("Startup failed in applicationDidFinishLaunching_:\n")
                log_file.write(error_trace)
            print("ERROR: Grok Overlay failed during startup.", flush=True)
            print(error_trace, flush=True)
            show_startup_alert(
                "Grok Overlay could not finish starting.\n\n"
                f"Details were saved to:\n{LOG_PATH}"
            )
            NSApp.terminate_(None)

    def _register_hotkey(self, manager, trigger_name, key, flags):
        try:
            manager.register(key, flags)
        except Exception as exc:
            print(f"Failed to register {trigger_name} hotkey: {exc}", flush=True)

    def _ensure_web_content_loaded(self):
        if self._web_content_loaded:
            return
        self._web_content_loaded = True
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)

    def _finish_launching(self):
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        initial_frame = self._compact_window_frame()
        self.window = AppWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            initial_frame,
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskClosable
            | NSWindowStyleMaskMiniaturizable
            | NSWindowStyleMaskResizable
            | NSWindowStyleMaskFullSizeContentView,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setTitle_("Grok")
        self.window.setLevel_(NSNormalWindowLevel)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorFullScreenPrimary
            | NSWindowCollectionBehaviorManaged
        )
        self.window.setTitlebarAppearsTransparent_(True)
        self.window.setTitleVisibility_(NSWindowTitleHidden)
        self.window.setFrameAutosaveName_(FRAME_SAVE_NAME)

        config = WKWebViewConfiguration.alloc().init()
        config.preferences().setJavaScriptCanOpenWindowsAutomatically_(True)
        config.setMediaTypesRequiringUserActionForPlayback_(0)
        try:
            config.preferences().setValue_forKey_(True, "mediaDevicesEnabled")
        except Exception:
            pass

        self.webview = WKWebView.alloc().initWithFrame_configuration_(
            ((0, 0), (800, 600)),
            config,
        )
        self.webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        self.webview.setCustomUserAgent_(get_safari_user_agent())
        self.webview.setUIDelegate_(self)
        self.webview.setNavigationDelegate_(self)

        self.content_view = NSView.alloc().initWithFrame_(self.window.contentView().bounds())
        self.content_view.setWantsLayer_(True)
        self.content_view.layer().setCornerRadius_(CORNER_RADIUS)
        self.content_view.layer().setBackgroundColor_(NSColor.windowBackgroundColor().CGColor())
        self.window.setContentView_(self.content_view)

        content_bounds = self.content_view.bounds()
        self.content_view.addSubview_(self.webview)
        self.webview.setFrame_(content_bounds)
        self.drag_area = None

        configuration = self.webview.configuration()
        user_content_controller = configuration.userContentController()
        user_content_controller.addScriptMessageHandler_name_(self, "backgroundColorHandler")

        script = """
            function _post(bg){try{const h=window.webkit?.messageHandlers?.backgroundColorHandler;h&&h.postMessage(bg);}catch(e){}}
            function _getColor(el){if(!el) return null; const c=getComputedStyle(el).backgroundColor; return (!c||c==='rgba(0, 0, 0, 0)'||c==='transparent')?null:c;}
            function sendBackgroundColor(){
                const bg=_getColor(document.body)||_getColor(document.documentElement)||'rgb(255,255,255)';
                _post(bg);
            }
            document.addEventListener('DOMContentLoaded', sendBackgroundColor);
            window.addEventListener('load', sendBackgroundColor);
            new MutationObserver(sendBackgroundColor).observe(document.documentElement,{attributes:true,attributeFilter:['style'],subtree:true,childList:true});
        """
        user_script = WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(
            script,
            WKUserScriptInjectionTimeAtDocumentEnd,
            True,
        )
        user_content_controller.addUserScript_(user_script)

        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        if hasattr(self.status_item, "setBehavior_"):
            # Keep the icon in the menu bar (not relegated to the overflow tray).
            self.status_item.setBehavior_(1)
        if hasattr(self.status_item, "setVisible_"):
            self.status_item.setVisible_(True)

        self.logo_white, self.logo_black, self.logo_fallback = load_status_bar_images()
        button = self.status_item.button()
        button.setHidden_(False)
        button.setToolTip_("Grok Overlay — click to show/hide, right-click for menu")
        button.setFont_(NSFont.boldSystemFontOfSize_(11))
        self.updateStatusItemImage()

        button.addObserver_forKeyPath_options_context_(
            self,
            "effectiveAppearance",
            NSKeyValueObservingOptionNew,
            STATUS_ITEM_CONTEXT,
        )

        menu = NSMenu.alloc().init()

        ask_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Ask Grok...", "showQuickAsk:", "")
        ask_item.setTarget_(self)
        menu.addItem_(ask_item)

        ask_shortcut_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("    Option + Shift + G", "", "")
        ask_shortcut_item.setEnabled_(False)
        menu.addItem_(ask_shortcut_item)

        menu.addItem_(NSMenuItem.separatorItem())

        grok_build_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Grok Build", "launchGrokBuild:", "")
        grok_build_item.setTarget_(self)
        menu.addItem_(grok_build_item)

        menu.addItem_(NSMenuItem.separatorItem())

        show_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Open Chat Window", "showCompactGrokWindow:", "")
        show_item.setTarget_(self)
        menu.addItem_(show_item)

        fullscreen_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Enter Full Screen", "toggleFullScreen:", "f")
        fullscreen_item.setTarget_(self)
        menu.addItem_(fullscreen_item)

        hide_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide " + APP_TITLE, "hideWindow:", "h")
        hide_item.setTarget_(self)
        menu.addItem_(hide_item)

        home_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Home", "goToWebsite:", "g")
        home_item.setTarget_(self)
        menu.addItem_(home_item)

        clear_data_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Clear Web Cache", "clearWebViewData:", "")
        clear_data_item.setTarget_(self)
        menu.addItem_(clear_data_item)

        mic_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Request Microphone Access", "requestMicrophoneAccess:", "")
        mic_item.setTarget_(self)
        menu.addItem_(mic_item)

        if is_startup_installed():
            uninstall_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Uninstall Autolauncher", "uninstall:", "")
            uninstall_item.setTarget_(self)
            menu.addItem_(uninstall_item)
        else:
            install_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Install Autolauncher", "install:", "")
            install_item.setTarget_(self)
            menu.addItem_(install_item)

        menu.addItem_(NSMenuItem.separatorItem())

        set_trigger_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Set New Trigger", "setTrigger:", "")
        set_trigger_item.setTarget_(self)
        menu.addItem_(set_trigger_item)

        trigger_label = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Current Trigger", "", "")
        trigger_label.setEnabled_(False)
        menu.addItem_(trigger_label)

        self.trigger_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("", "", "")
        self.trigger_item.setEnabled_(False)
        menu.addItem_(self.trigger_item)

        menu.addItem_(NSMenuItem.separatorItem())

        attribution_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Attribution", "showAttribution:", "")
        attribution_item.setTarget_(self)
        menu.addItem_(attribution_item)

        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "terminate:", "q")
        quit_item.setTarget_(NSApp)
        menu.addItem_(quit_item)

        self.status_menu = menu
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("statusItemClicked:")
        self.status_item.button().sendActionOn_(NSEventMaskLeftMouseDown | NSEventMaskRightMouseDown)

        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            "windowDidResize:",
            NSWindowDidResizeNotification,
            self.window,
        )

        self.local_mouse_monitor = None

        self.quick_ask_controller = QuickAskController.alloc().initWithAppDelegate_(self)

        self.hotkey_manager = CarbonHotKeyManager(self.toggleWindow_, hotkey_id=1)
        self.hotkey_manager.install_handler()
        self._register_hotkey(
            self.hotkey_manager,
            "launcher",
            LAUNCHER_TRIGGER["key"],
            LAUNCHER_TRIGGER["flags"],
        )

        self.quick_ask_hotkey_manager = CarbonHotKeyManager(self.showQuickAsk_, hotkey_id=2)
        self.quick_ask_hotkey_manager.install_handler()
        self._register_hotkey(
            self.quick_ask_hotkey_manager,
            "quick ask",
            QUICK_ASK_TRIGGER["key"],
            QUICK_ASK_TRIGGER["flags"],
        )

        update_menu_trigger_label(self)
        load_custom_launcher_trigger(self)
        self.window.setDelegate_(self)
        self.hideWindow_(None)

    def _compact_window_frame(self):
        screen = NSScreen.mainScreen().visibleFrame()
        width = COMPACT_WINDOW_WIDTH
        height = COMPACT_WINDOW_HEIGHT
        origin_x = screen.origin.x + screen.size.width - width - 16
        origin_y = screen.origin.y + screen.size.height - height - 8
        return NSMakeRect(origin_x, origin_y, width, height)

    def _position_window_near_clock(self):
        self.window.setFrame_display_(self._compact_window_frame(), True)

    def statusItemClicked_(self, sender):
        event = NSApp.currentEvent()
        if event is not None and (
            event.type() == NSEventTypeRightMouseDown
            or event.type() == NSEventTypeRightMouseUp
            or (event.modifierFlags() & NSEventModifierFlagControl)
        ):
            self.status_item.popUpStatusItemMenu_(self.status_menu)
            return
        self.toggleCompactGrokWindow_(sender)

    def showCompactGrokWindow_(self, sender=None):
        if not self.window.isVisible():
            self._position_window_near_clock()
        self.showWindow_(None)

    def toggleCompactGrokWindow_(self, sender=None):
        if self.window.isVisible():
            self.hideWindow_(None)
        else:
            self.showCompactGrokWindow_(sender)

    def toggleFullScreen_(self, sender=None):
        self.showWindow_(None)
        self.window.toggleFullScreen_(None)

    def toggleWindow_(self, sender=None):
        self.toggleCompactGrokWindow_(sender)

    def applicationShouldHandleReopen_hasVisibleWindows_(self, _app, has_visible_windows):
        if not has_visible_windows:
            self.showCompactGrokWindow_(None)
        return True

    def refresh_hotkey(self):
        if self.hotkey_manager is None:
            return
        if None in LAUNCHER_TRIGGER.values():
            return
        try:
            self.hotkey_manager.register(
                LAUNCHER_TRIGGER["key"],
                LAUNCHER_TRIGGER["flags"],
            )
        except Exception as exc:
            print(f"Failed to register hotkey: {exc}", flush=True)

    def showQuickAsk_(self, sender=None):
        if self.quick_ask_controller is not None:
            self.quick_ask_controller.show()

    def showAttribution_(self, sender=None):
        show_attribution_alert()

    def launchGrokBuild_(self, sender=None):
        if find_agent_executable() is None:
            if offer_grok_cli_install():
                ok, message = install_grok_cli()
                if not ok and message:
                    show_startup_alert(message)
            return
        ok, message = launch_grok_build()
        if not ok and message:
            show_startup_alert(message)

    def submitQuestion_(self, question):
        self.pending_question = question
        self.showCompactGrokWindow_(None)
        self.performSelector_withObject_afterDelay_("_injectPendingQuestion:", None, 0.2)

    def _injectPendingQuestion_(self, _sender):
        if not self.pending_question:
            return
        question = self.pending_question
        javascript = build_submit_question_js(question)
        self.webview.evaluateJavaScript_completionHandler_(
            javascript,
            lambda _result, _error: setattr(self, "pending_question", None),
        )

    def showWindow_(self, sender):
        self._ensure_web_content_loaded()
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        if not self.pending_question:
            self.webview.evaluateJavaScript_completionHandler_(
                "[...document.querySelectorAll('textarea')].sort((a,b)=>a.contains(b)?-1:b.contains(a)?1:0).pop()?.focus();",
                None,
            )

    def hideWindow_(self, sender):
        self.window.orderOut_(None)

    def goToWebsite_(self, sender):
        self._web_content_loaded = True
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)

    def clearWebViewData_(self, sender):
        data_store = self.webview.configuration().websiteDataStore()
        data_types = WKWebsiteDataStore.allWebsiteDataTypes()
        data_store.removeDataOfTypes_modifiedSince_completionHandler_(
            data_types,
            NSDate.distantPast(),
            lambda: print("Data cleared", flush=True),
        )

    def requestMicrophoneAccess_(self, sender):
        try:
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                AVMediaTypeAudio,
                lambda granted: print(
                    f"Microphone access {'granted' if granted else 'denied'}.",
                    flush=True,
                ),
            )
        except Exception as exc:
            print(f"Failed to request microphone access: {exc}", flush=True)

    def install_(self, sender):
        result = install_startup()
        if isinstance(result, tuple):
            ok, message = result
        else:
            ok, message = bool(result), ""
        if ok:
            show_startup_alert(message)
            NSApp.terminate_(None)
        elif message:
            show_startup_alert(message)

    def uninstall_(self, sender):
        if uninstall_startup():
            show_startup_alert(
                "Grok Overlay will no longer start automatically at login."
            )
            NSApp.hide_(None)

    def setTrigger_(self, sender):
        set_custom_launcher_trigger(self)

    def updateTriggerMenu(self, key_string=""):
        self.trigger_item.setTitle_("    " + key_string)

    def keyDown_(self, event):
        modifiers = event.modifierFlags()
        key_command = modifiers & NSEventModifierFlagCommand
        key_alt = modifiers & NSEventModifierFlagOption
        key_control = modifiers & NSEventModifierFlagControl
        key = event.charactersIgnoringModifiers()
        responder = self.window.firstResponder()

        if responder is None:
            return

        if (key_command or key_control) and (not key_alt):
            if key == "a":
                responder.selectAll_(None)
            elif key == "c":
                responder.copy_(None)
            elif key == "x":
                responder.cut_(None)
            elif key == "v":
                responder.paste_(None)
            elif key == "h":
                self.hideWindow_(None)
            elif key == "q":
                NSApp.terminate_(None)

    def windowShouldClose_(self, sender):
        self.hideWindow_(None)
        return False

    def windowDidResize_(self, notification):
        bounds = self.window.contentView().bounds()
        if hasattr(self, "content_view") and self.content_view is not None:
            self.content_view.setFrame_(bounds)
        self.webview.setFrame_(bounds)

    def userContentController_didReceiveScriptMessage_(self, user_content_controller, message):
        if message.name() == "backgroundColorHandler":
            rgb_values = parse_css_rgb_color(message.body())
            if rgb_values is not None:
                r, g, b = rgb_values
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)
                if hasattr(self, "content_view") and self.content_view is not None:
                    self.content_view.layer().setBackgroundColor_(color.CGColor())

    def _normalized_url_host(self, url):
        if url is None:
            return ""
        host = (url.host() or "").lower()
        if host.startswith("www."):
            return host[4:]
        return host

    def _host_matches_suffixes(self, host, suffixes):
        for suffix in suffixes:
            if host == suffix or host.endswith("." + suffix):
                return True
        return False

    def _should_keep_navigation_in_app(self, url):
        host = self._normalized_url_host(url)
        return self._host_matches_suffixes(host, IN_APP_POPUP_HOST_SUFFIXES)

    def _open_in_default_browser(self, url):
        if url is None:
            return False
        return NSWorkspace.sharedWorkspace().openURL_(url)

    def webView_decidePolicyForNavigationAction_decisionHandler_(
        self,
        web_view,
        navigation_action,
        decision_handler,
    ):
        request_url = navigation_action.request().URL()

        if navigation_action.targetFrame() is None:
            decision_handler(WKNavigationActionPolicyAllow)
            return

        if navigation_action.navigationType() != WKNavigationTypeLinkActivated:
            decision_handler(WKNavigationActionPolicyAllow)
            return

        if self._should_keep_navigation_in_app(request_url):
            decision_handler(WKNavigationActionPolicyAllow)
            return

        self._open_in_default_browser(request_url)
        decision_handler(WKNavigationActionPolicyCancel)

    def webView_createWebViewWithConfiguration_forNavigationAction_windowFeatures_(
        self,
        web_view,
        configuration,
        navigation_action,
        window_features,
    ):
        if navigation_action.targetFrame() is not None:
            return None

        request_url = navigation_action.request().URL()
        if not self._should_keep_navigation_in_app(request_url):
            self._open_in_default_browser(request_url)
            return None

        popup_webview = WKWebView.alloc().initWithFrame_configuration_(
            web_view.frame(),
            configuration,
        )
        popup_webview.setUIDelegate_(self)
        popup_webview.setNavigationDelegate_(self)

        popup_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            web_view.window().frame(),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False,
        )
        popup_window.setTitle_("Sign In")
        popup_window.setContentView_(popup_webview)
        popup_webview.loadRequest_(navigation_action.request())
        popup_window.makeKeyAndOrderFront_(None)
        self.popup_windows.append((popup_window, popup_webview))
        return popup_webview

    def webViewDidClose_(self, web_view):
        self.popup_windows = [
            (window, view)
            for window, view in self.popup_windows
            if view != web_view
        ]

    def webView_didFinishNavigation_(self, web_view, navigation):
        if self.pending_question:
            self.performSelector_withObject_afterDelay_("_injectPendingQuestion:", None, 0.3)

    def updateStatusItemImage(self):
        button = self.status_item.button()
        appearance = button.effectiveAppearance()
        is_dark = (
            appearance.bestMatchFromAppearancesWithNames_(
                [NSAppearanceNameAqua, NSAppearanceNameDarkAqua]
            )
            == NSAppearanceNameDarkAqua
        )
        image = self.logo_white if is_dark else self.logo_black
        if image is None:
            image = self.logo_fallback
        button.setTitle_("Grok")
        if image is None:
            button.setImage_(None)
            button.setImagePosition_(NSImageLeft)
            return
        button.setImage_(image)
        button.setImagePosition_(NSImageLeft)

    def observeValueForKeyPath_ofObject_change_context_(self, key_path, obj, change, context):
        if context == STATUS_ITEM_CONTEXT and key_path == "effectiveAppearance":
            self.updateStatusItemImage()

    def applicationWillTerminate_(self, notification):
        if hasattr(self, "status_item") and self.status_item is not None:
            try:
                self.status_item.button().removeObserver_forKeyPath_context_(
                    self,
                    "effectiveAppearance",
                    STATUS_ITEM_CONTEXT,
                )
            except Exception:
                pass

        if hasattr(self, "local_mouse_monitor") and self.local_mouse_monitor is not None:
            NSEvent.removeMonitor_(self.local_mouse_monitor)
            self.local_mouse_monitor = None

        if self.trigger_capture_monitor is not None:
            NSEvent.removeMonitor_(self.trigger_capture_monitor)
            self.trigger_capture_monitor = None

        if self.hotkey_manager is not None:
            self.hotkey_manager.cleanup()
            self.hotkey_manager = None

        if self.quick_ask_hotkey_manager is not None:
            self.quick_ask_hotkey_manager.cleanup()
            self.quick_ask_hotkey_manager = None

        if self.quick_ask_controller is not None:
            self.quick_ask_controller.cleanup()
            self.quick_ask_controller = None

        if hasattr(self, "webview") and self.webview is not None:
            controller = self.webview.configuration().userContentController()
            controller.removeScriptMessageHandlerForName_("backgroundColorHandler")

        NSNotificationCenter.defaultCenter().removeObserver_(self)