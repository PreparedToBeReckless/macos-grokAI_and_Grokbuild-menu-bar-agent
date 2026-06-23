# Attribution (read this first)

## Original project — please credit them

This repository is a **fork** of **[macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay)** by **Thomas C.H. Lux** ([@tchlux](https://github.com/tchlux)).

- **This fork:** https://github.com/PreparedToBeReckless/macos-grokAI_and_Grokbuild-menuebar-agent  
- **Upstream:** https://github.com/tchlux/macos-grok-overlay
- **Original license:** MIT (see [LICENSE](LICENSE))  
- **Original author:** Thomas C.H. Lux — `thomas.ch.lux@gmail.com`

Most of the core overlay architecture, pyobjc/WebKit integration, and original design come from that project. **If you use or share this code, credit the upstream repository and its author.**

---

## This fork — how it was modified

| | |
|---|---|
| **Fork maintainer** | **reckless** |
| **How it was built** | **reckless used [Grok](https://grok.com) (xAI) to modify the project.** Prompts and review only — **reckless did not write application code manually.** |
| **Current version** | 0.0.51 (see `macos_grok_overlay/about/version.txt`) |

Major additions in this fork (via Grok-assisted sessions):

- **Grok Build** — native macOS app (Swift + [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm)) running the Grok CLI `agent` in its own embedded terminal
- Menu bar / status item fixes, autolauncher, Grok Build menu integration
- DMG packaging for **Grok Overlay** + **Grok Build**, build scripts (`build-dmg.sh`, `clean.sh`, etc.)

---

## Other dependencies to credit

- **[SwiftTerm](https://github.com/migueldeicaza/SwiftTerm)** — embedded terminal in Grok Build (MIT)
- **Grok CLI (`agent`)** — https://x.ai/cli — separate install, not bundled

---

## Not affiliated with xAI

This is an **unofficial** community fork. It is **not** a product of xAI or Thomas Lux's official releases unless upstream merges these changes.

---

## Quick copy-paste credit line

```
Based on macos-grok-overlay by Thomas C.H. Lux (https://github.com/tchlux/macos-grok-overlay).
Fork: https://github.com/PreparedToBeReckless/macos-grokAI_and_Grokbuild-menuebar-agent
Maintained by reckless; modifications made using Grok (xAI) — no manual coding by reckless.
```