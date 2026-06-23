import AppKit

enum Attribution {
    static let text = """
    ORIGINAL PROJECT (please credit)
      macos-grok-overlay
      by Thomas C.H. Lux (@tchlux)
      https://github.com/tchlux/macos-grok-overlay
      MIT License — see LICENSE in the repository

    THIS FORK
      Maintained by: reckless
      Modifications: made using Grok (xAI assistant)
      reckless did not write application code manually.

      See ATTRIBUTION.md in the repository for full details.
    """

    static func showAlert() {
        let alert = NSAlert()
        alert.messageText = "Attribution"
        alert.informativeText = text
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
}