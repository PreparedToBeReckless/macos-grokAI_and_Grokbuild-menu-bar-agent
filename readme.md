> ## ⚠️ ATTRIBUTION — READ FIRST
>
> **This is a fork of [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) by [Thomas C.H. Lux](https://github.com/tchlux) (MIT).**  
> Please credit the **original upstream project and author** if you use or share this code.
>
> **Fork maintainer:** **reckless**  
> **How this fork was made:** **reckless used [Grok](https://grok.com) (xAI) to modify the project — no manual coding by reckless.**
>
> I WANT EVERYONE TO BE AWARE THIS WAS FULLY MODDED BY GROK BUILD
> 
> I TAKE NO CREDIT IN ITS CODING ALL CREDIT SHOULD GO TO THOMAS AND ME USING AI LOL  
>
> **Full details:** [ATTRIBUTION.md](ATTRIBUTION.md)

<p align="center">
  <h1 align="center"><code>macos-grok-overlay</code> (reckless fork)</h1>
</p>

<p align="center">
A simple macOS overlay application for pinning <code>grok.com</code> to a dedicated window and key command <code>option+space</code>.
<br><br>
<em>Fork of <a href="https://github.com/tchlux/macos-grok-overlay">tchlux/macos-grok-overlay</a> — modified by reckless via Grok (xAI).</em>
</p>

![Launcher Sample](images/macos-grok-overlay.jpeg)


## Installation (this fork)

  **Use the release DMG for this fork** — it includes **Grok Overlay** and **Grok Build**.

**Download:** [Grok-Overlay-0.0.43.dmg](https://github.com/PreparedToBeReckless/macos-grok-overlay-reckless-fork/releases/latest)  
Open the DMG and drag both apps to Applications.

[![DMG Installer](images/dmg-installer-preview.png)](https://github.com/PreparedToBeReckless/macos-grok-overlay-reckless-fork/releases/latest)

**Compatibility:** Release builds target `arm64` (Apple Silicon). Intel Macs can try building from source with `PY2APP_ARCH=x86_64 zsh build-dmg.sh`.

> **Do not use** `pip install macos-grok-overlay` **for this fork.**  
> That installs the **original** [upstream package on PyPI](https://pypi.org/project/macos-grok-overlay/) by Thomas Lux — not Grok Build or any changes here.

  To install **this fork** from source via pip (Python/CLI only — no `.app` bundles):

```bash
python3 -m pip install "git+https://github.com/PreparedToBeReckless/macos-grok-overlay-reckless-fork.git"
```

  After a DMG or pip install, you can enable autolaunch from Terminal with:

```bash
macos-grok-overlay --install-startup
```

  You will get a request like this to enable Accessibility the first time this launches.

![Accessibility Request](images/macos-grok-overlay-accessibility.png)

  The Accessibility access is required for the background task to listen for the `Option+Space` keyboard command. But please don't just take my word for it, look at the [listener code yourself](macos_grok_overlay/listener.py) and see. ;)

  Within a few seconds of approving Accessibility access, you should see a little icon like this appear along the top of your screen.

![Menu Sample](images/macos-grok-overlay-menu.png)

  And you're done! Now this should launch automatically and constantly run in the background. If you ever decide you do not want it, see the uninstall instructions below.


## Usage

  Once the application is launched, it should immediately open a window dedicated to `grok.com`. You'll need to log in there, but you should only need to do that once. After installing, pressing `Option + Space` while the window is open will hide it, and pressing it again at any point will reveal it and pin it as the top-most window overlay on top of other applications. This enables quick and easy access to Grok on macOS.

<video controls loop autoplay>
  <source src="https://github.com/tchlux/macos-grok-overlay/raw/main/images/macos-grok-overlay.mp4" type="video/mp4">
</video>

  There is a dropdown menu with basic options that shows when you click the menubar icon. Personally I find that using `Option + Space` to summon and dismiss the dialogue as needed is the most convenient.

<video controls loop autoplay>
  <source src="https://github.com/tchlux/macos-grok-overlay/raw/main/images/macos-grok-overlay-menu.mp4" type="video/mp4">
</video>

  If you decide you want to uninstall the application, you can do that by clicking the option in the menubar dropdown, or from the command line with:

```bash
macos-grok-overlay --uninstall-startup
```


## How it works

  This is a very thin `pyobjc` application written to contain a web view of the current production Grok website. Most of the logic contained in this small application is for stylistic purposes, making the overlay shaped correctly, resizeable, draggable, and able to be summoned anywhere easily with a single (modifiable) keyboard command. There's also a few steps needed to listen specifically for the `Option + Space` keyboard command, which requires Accessibility access to macOS.

  **Grok Build** is a companion native app (Swift + SwiftTerm) that runs the Grok CLI `agent` in its own embedded terminal window — separate from Terminal.app. Install both apps from the DMG.


## Building from source

  Requires **Python 3.12** (Homebrew) and **Xcode Command Line Tools** (`swiftc`).

```bash
# Full DMG (Grok Overlay + Grok Build)
zsh build-dmg.sh

# Local test copy
open test-install/Grok\ Overlay.app

# Clean artifacts and old installers
zsh clean.sh
```

  Output: `Grok-Overlay-<version>.dmg` and `Grok-Overlay-latest.dmg`.


## Final thoughts

  The **original** [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) was a small fun weekend project by Thomas Lux, and is not a product of the xAI team nor formally affiliated with them.

  **This fork** is maintained by **reckless** and was modified entirely through **Grok (xAI)** — reckless did not write code manually. It is also unofficial and not affiliated with xAI or the upstream author unless merged upstream.

  See **[ATTRIBUTION.md](ATTRIBUTION.md)** before redistributing or building on this work.
