import AppKit

/// Terminal view that reliably accepts keyboard, paste, and dictation input.
final class GrokTerminalView: LocalProcessTerminalView {
    override func mouseDown(with event: NSEvent) {
        window?.makeFirstResponder(self)
        super.mouseDown(with: event)
    }

    override func insertText(_ string: Any, replacementRange: NSRange) {
        let text: String?
        switch string {
        case let value as String:
            text = value
        case let value as NSString:
            text = value as String
        case let value as NSAttributedString:
            text = value.string
        default:
            text = nil
        }
        guard let text else { return }
        send(txt: text)
    }

    @objc func pasteAsPlainText(_ sender: Any) {
        paste(sender)
    }
}