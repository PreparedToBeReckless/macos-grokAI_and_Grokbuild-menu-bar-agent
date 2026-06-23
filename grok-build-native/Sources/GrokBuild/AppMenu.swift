import AppKit

enum AppMenu {
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
}