import Foundation

enum AgentLocator {
    static let installCommand = "curl -fsSL https://x.ai/cli/install.sh | bash"

    static func workingDirectory() -> String {
        let desktopGrok = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Desktop/grok", isDirectory: true)
        if FileManager.default.fileExists(atPath: desktopGrok.path) {
            return desktopGrok.path
        }
        return FileManager.default.homeDirectoryForCurrentUser.path
    }

    static func findAgentExecutable() -> String? {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let candidates = [
            home.appendingPathComponent(".grok/bin/agent"),
            home.appendingPathComponent(".local/bin/agent"),
        ]

        for candidate in candidates {
            var isDirectory: ObjCBool = false
            if FileManager.default.fileExists(atPath: candidate.path, isDirectory: &isDirectory),
               !isDirectory.boolValue,
               FileManager.default.isExecutableFile(atPath: candidate.path) {
                return candidate.path
            }
        }

        if let path = ProcessInfo.processInfo.environment["PATH"] {
            for entry in path.split(separator: ":") {
                let candidate = URL(fileURLWithPath: String(entry)).appendingPathComponent("agent")
                var isDirectory: ObjCBool = false
                if FileManager.default.fileExists(atPath: candidate.path, isDirectory: &isDirectory),
                   !isDirectory.boolValue,
                   FileManager.default.isExecutableFile(atPath: candidate.path) {
                    return candidate.path
                }
            }
        }

        return nil
    }

    static func agentEnvironment() -> [String] {
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        var env = Terminal.getEnvironmentVariables(termName: "xterm-256color")
        env.append("PATH=\(home)/.grok/bin:\(home)/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin")
        return env
    }
}