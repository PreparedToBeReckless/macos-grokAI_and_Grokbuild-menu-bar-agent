// FORK of https://github.com/tchlux/macos-grok-overlay — see ATTRIBUTION.md
// Grok Build added by reckless using Grok (xAI); no manual coding by reckless.
import AppKit

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var windowController: TerminalWindowController?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        AppMenu.install(on: self)

        guard let agentPath = AgentLocator.findAgentExecutable() else {
            offerInstallOrQuit()
            return
        }

        let controller = TerminalWindowController(
            agentPath: agentPath,
            workDir: AgentLocator.workingDirectory()
        )
        windowController = controller
        controller.showAndLaunch()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    func applicationWillTerminate(_ notification: Notification) {
        windowController?.terminateAgent()
    }

    @objc func quitApplication(_ sender: Any?) {
        windowController?.terminateAgent()
        NSApp.terminate(sender)
    }

    @objc func showAttribution(_ sender: Any?) {
        Attribution.showAlert()
    }

    private func offerInstallOrQuit() {
        let alert = NSAlert()
        alert.messageText = "Install Grok Build?"
        alert.informativeText = """
        The Grok CLI (`agent`) is not installed yet.

        Grok Build can open Terminal and run the official installer:
          \(AgentLocator.installCommand)

        After installation finishes, open Grok Build again.
        """
        alert.addButton(withTitle: "Install")
        alert.addButton(withTitle: "Quit")

        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            launchInstaller()
        } else {
            NSApp.terminate(nil)
        }
    }

    private func launchInstaller() {
        let script = AgentLocator.installCommand
        let source = """
        tell application "Terminal"
            activate
            do script "\(script.replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\""))"
        end tell
        """
        var error: NSDictionary?
        if let appleScript = NSAppleScript(source: source) {
            appleScript.executeAndReturnError(&error)
        }
        NSApp.terminate(nil)
    }
}