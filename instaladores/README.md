# Selector Moebius 1.0 installers

Download the ZIP for your operating system from the GitHub release and extract the **whole folder** before starting. The installer messages are in English. The application starts in Spanish; edit `app/configuracion.json` after installation to select `EN-uk`, `EN-us`, `PO`, `ES-la` or `ES`.

## Windows

Double-click **Install-Windows.cmd**. Windows PowerShell 5.1 or later is required. The installer reuses Python 3.10+ with Tkinter if available; otherwise it downloads the official Python 3.14.7 installer, verifies its SHA-256 checksum and Authenticode signature, and installs it for the current user with pip and Tkinter. The download supports x64, x86 and ARM64; ARM64 support in the Python installer is experimental.

Python is downloaded from [python.org](https://www.python.org/downloads/release/python-3147/) using the vendor's [unattended installer options](https://docs.python.org/3.14/using/windows.html). It does not modify the global PATH. Corporate execution policies may require administrator assistance; the launcher only requests a process-local execution policy and does not change the machine policy.

The application is installed in `%LOCALAPPDATA%\Programs\SelectorMoebius`. A shortcut is registered in the current user's **Start menu → Selector Moebius**. The installer asks **“Do you want to create a desktop shortcut?”**; enter `y` to create it. The desktop path uses Windows' known folder, including redirected/OneDrive desktops.

## Linux

From the extracted folder, run:

```bash
bash install-linux.sh
```

Run as your desktop user, **without sudo**. If Python packages are missing, the installer asks for administrator access through `sudo` and uses the available package manager:

| Distribution family | Packages |
| --- | --- |
| Debian / Ubuntu | `python3`, `python3-venv`, `python3-tk`, `python3-pip` |
| Fedora | `python3`, `python3-tkinter`, `python3-pip` |
| openSUSE | `python3`, `python3-tk`, `python3-pip` |
| Arch | `python`, `python-pip`, `tk` |

Use a distribution providing Python 3.10 or later. Other distributions can run the installer after their administrator installs Python, Tkinter, pip, venv and ensurepip. Package names/availability vary by distribution release; the installer reports failed package installation instead of proceeding with missing dependencies.

The application is installed in `$XDG_DATA_HOME/SelectorMoebius`, or `~/.local/share/SelectorMoebius` by default. It is registered with a `.desktop` entry in the user's applications directory and icons in the `hicolor` theme. Select **Selector Moebius** from the applications menu.

The installer asks **“Do you want to create a desktop shortcut?”**. It uses `xdg-user-dir DESKTOP` for localised desktop folders. Some desktops require right-clicking the new shortcut and selecting **Allow Launching**. Desktops that do not display desktop icons still provide the application menu entry.

For unattended installation, use `bash install-linux.sh --desktop yes` or `--desktop no`. A custom application directory is supported with `--base /path/to/SelectorMoebius`.

## Data, updates and removal

Both installers require Internet access when downloading Python or Python packages. Dependencies are installed in a private virtual environment; system Python packages are not replaced with pip. The application is registered for manual launch, not automatic startup at login.

The installation contains:

```text
SelectorMoebius/
  app/                  application, translations and icons
    configuracion.json  your settings
    listas/             your saved lists
  environment/          private Python environment
  installation.json     installation details
```

Close the application before reinstalling. Reinstallation preserves the installed settings and lists. It never imports private lists from the extracted source folder. If custom settings reference a separate workbook, keep that workbook available. Files created outside `listas/` are not treated as saved user data during upgrades.

To remove the application, first back up `app/listas/` and `app/configuracion.json`, then delete the installation folder and the Start menu/application menu and optional desktop shortcuts. On Linux, the menu entry is `$XDG_DATA_HOME/applications/SelectorMoebius.desktop` (default `~/.local/share/applications/SelectorMoebius.desktop`); its icons are named `SelectorMoebius.png` below `icons/hicolor/`. Python itself is retained because other applications may use it.

These are source-based installers, not standalone executables. On Windows the entry point is a CMD launcher plus PowerShell; on Linux it is a Bash script. The release ZIPs include all application resources and the license. Only Python and dependencies are downloaded during installation.
