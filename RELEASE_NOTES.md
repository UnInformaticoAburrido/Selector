# Selector Moebius 1.0

Organise classroom participation: create or import student lists and choose who takes part, by number or at random, without repeating a student during a round.

## Downloads

- **Windows:** download `Selector-Moebius-1.0-Windows.zip`, extract the entire folder and open `Install-Windows.cmd`.
- **Linux:** download `Selector-Moebius-1.0-Linux.zip`, extract the entire folder and run `bash install-linux.sh` as your desktop user.

The installers prepare Python 3 with Tkinter when needed, install the Python dependencies, register the application in the Start/application menu and offer an optional desktop shortcut. An Internet connection is required to download dependencies. Installer messages are in English. These packages contain the application source and setup scripts, not a standalone EXE or AppImage.

## Included

- Spanish (Spain), British English, American English, Portuguese (Portugal) and Latin American Spanish: 124 texts per language, editable in Excel.
- A configuration file for language, light/dark/system appearance, window size and window/fullscreen/borderless mode.
- Saved lists in a dedicated folder and quick switching by list name.
- List creation, first-column Excel/CSV import, participation tracking and confirmation before starting a new round.
- Icons at multiple resolutions and a button to open a GitHub bug report.

The default configuration is Spanish, light appearance and a 1280 × 720 window. Change `app/configuracion.json` after installation; for example, set `"languaje": "EN-uk"` for British English.

Close the application before reinstalling. Installed lists and settings are preserved. Native file-dialog controls follow the operating system language. See the included installer README for supported Linux package managers and desktop-specific behaviour.

License: PolyForm Noncommercial 1.0.0. Copyright © 2026 Dimitry (UnInformaticoAburrido). Preserve the license and required attribution notices.
