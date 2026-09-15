@echo off
setlocal
echo Selector Moebius 1.0 - Windows installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instaladores\install-windows.ps1"
if errorlevel 1 (
    echo Installation did not complete. Please review the message above.
    pause
    exit /b 1
)
pause
