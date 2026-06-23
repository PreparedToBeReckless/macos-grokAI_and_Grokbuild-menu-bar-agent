import AppKit

final class TerminalWindowController: NSWindowController, NSWindowDelegate, LocalProcessTerminalViewDelegate {
    private let containerView = NSView()
    private let terminalView: GrokTerminalView
    private let agentPath: String
    private let workDir: String

    init(agentPath: String, workDir: String) {
        self.agentPath = agentPath
        self.workDir = workDir
        self.terminalView = GrokTerminalView(frame: .zero)

        let screenFrame = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 960, height: 640)
        let width = min(960, screenFrame.width * 0.7)
        let height = min(640, screenFrame.height * 0.75)
        let origin = NSPoint(
            x: screenFrame.midX - width / 2,
            y: screenFrame.midY - height / 2
        )

        let window = NSWindow(
            contentRect: NSRect(origin: origin, size: NSSize(width: width, height: height)),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Grok Build"
        window.minSize = NSSize(width: 480, height: 320)
        window.isReleasedWhenClosed = false
        window.backgroundColor = NSColor(calibratedWhite: 0.08, alpha: 1)

        super.init(window: window)

        let background = NSColor(calibratedWhite: 0.08, alpha: 1)
        containerView.wantsLayer = true
        containerView.layer?.backgroundColor = background.cgColor
        containerView.autoresizingMask = [.width, .height]

        terminalView.autoresizingMask = [.width, .height]
        terminalView.processDelegate = self
        terminalView.configureNativeColors()
        terminalView.nativeForegroundColor = NSColor(calibratedWhite: 0.9, alpha: 1)
        terminalView.nativeBackgroundColor = background
        containerView.addSubview(terminalView)

        window.contentView = containerView
        window.delegate = self
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func showAndLaunch() {
        guard let window else { return }
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        focusTerminal()
        refreshTerminalLayout()
        DispatchQueue.main.async { [weak self] in
            self?.refreshTerminalLayout()
            self?.focusTerminal()
            self?.launchAgentWhenReady()
        }
    }

    private func focusTerminal() {
        window?.makeFirstResponder(terminalView)
    }

    private var launchedAgent = false

    private func launchAgentWhenReady() {
        guard !launchedAgent else { return }
        launchedAgent = true
        refreshTerminalLayout()
        terminalView.process.startProcess(
            executable: agentPath,
            args: [],
            environment: AgentLocator.agentEnvironment(),
            currentDirectory: workDir
        )
    }

    private func refreshTerminalLayout() {
        guard let window else { return }
        window.layoutIfNeeded()
        containerView.layoutSubtreeIfNeeded()

        let bounds = containerView.bounds
        guard bounds.width > 1, bounds.height > 1 else { return }

        // Setting `frame` (not just `setFrameSize`) triggers SwiftTerm's processSizeChange.
        terminalView.frame = bounds
        terminalView.needsDisplay = true
    }

    func windowDidResize(_ notification: Notification) {
        refreshTerminalLayout()
    }

    func windowDidBecomeKey(_ notification: Notification) {
        focusTerminal()
        refreshTerminalLayout()
    }

    func sizeChanged(source: LocalProcessTerminalView, newCols: Int, newRows: Int) {}

    func setTerminalTitle(source: LocalProcessTerminalView, title: String) {
        window?.title = title.isEmpty ? "Grok Build" : title
    }

    func hostCurrentDirectoryUpdate(source: TerminalView, directory: String?) {}

    func processTerminated(source: TerminalView, exitCode: Int32?) {
        DispatchQueue.main.async {
            NSApp.terminate(nil)
        }
    }

    func terminateAgent() {
        if terminalView.process.running {
            terminalView.process.terminate()
        }
    }
}