# Grok Build (native)

> **Fork of [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) by Thomas C.H. Lux.**  
> **Grok Build added by reckless using Grok (xAI) — no manual coding by reckless.**  
> See [../ATTRIBUTION.md](../ATTRIBUTION.md).

Native macOS terminal host for the Grok CLI `agent` process. Built with Swift and [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm).

## Layout

- `Sources/GrokBuild/` — Swift app source
- `Package.swift` — SwiftPM manifest (optional; release builds use `swiftc` via `build-grok-build-app.sh`)
- `vendor/SwiftTerm/` — fetched automatically on build (not committed)

## Build

From the repo root:

```bash
zsh build-grok-build-app.sh
```

Output: `dmg-builder/dist/Grok Build.app`

Requires macOS 13+, Xcode Command Line Tools (`swiftc`, `xcrun`).