import AppKit

enum AppMenu {
    private static let copyAction = Selector("copy:")
    private static let pasteAction = Selector("paste:")
    private static let selectAllAction = Selector("selectAll:")
    private static let startDictationAction = Selector("startDictation:")

    static func install(on appDelegate: AppDelegate) {
        let mainMenu = NSMenu()

        let appMenuItem = NSMenuItem()
        mainMenu.addItem(appMenuItem)

        let appMenu = NSMenu()
        appMenuItem.submenu = appMenu

        let appName = Bundle.main.object(forInfoDictionaryKey: "CFBundleName") as? String ?? "Grok Build"
        appMenu.addItem(
            withTitle: "About \(appName)",
            action: #selector(AppDelegate.showAttribution(_:)),
            keyEquivalent: "",
            target: appDelegate
        )
        appMenu.addItem(.separator())
        appMenu.addItem(
            withTitle: "Quit \(appName)",
            action: #selector(AppDelegate.quitApplication(_:)),
            keyEquivalent: "q",
            target: appDelegate
        )

        let editMenuItem = NSMenuItem()
        mainMenu.addItem(editMenuItem)

        let editMenu = NSMenu(title: "Edit")
        editMenuItem.submenu = editMenu
        editMenu.addResponderItem(
            withTitle: "Copy",
            action: copyAction,
            keyEquivalent: "c"
        )
        editMenu.addResponderItem(
            withTitle: "Paste",
            action: pasteAction,
            keyEquivalent: "v"
        )
        editMenu.addResponderItem(
            withTitle: "Paste and Match Style",
            action: #selector(GrokTerminalView.pasteAsPlainText(_:)),
            keyEquivalent: "V"
        )
        editMenu.addResponderItem(
            withTitle: "Select All",
            action: selectAllAction,
            keyEquivalent: "a"
        )
        editMenu.addItem(.separator())
        editMenu.addResponderItem(
            withTitle: "Start Dictation",
            action: startDictationAction,
            keyEquivalent: ""
        )

        NSApp.mainMenu = mainMenu
    }
}

private extension NSMenu {
    @discardableResult
    func addItem(
        withTitle title: String,
        action: Selector,
        keyEquivalent: String,
        target: AnyObject? = nil
    ) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: action, keyEquivalent: keyEquivalent)
        item.target = target ?? NSApp
        addItem(item)
        return item
    }

    @discardableResult
    func addResponderItem(
        withTitle title: String,
        action: Selector,
        keyEquivalent: String
    ) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: action, keyEquivalent: keyEquivalent)
        item.target = nil
        addItem(item)
        return item
    }
}