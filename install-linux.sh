#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != Linux ]]; then
    echo 'This installer is for Linux.' >&2
    exit 1
fi
if [[ "$EUID" -eq 0 ]]; then
    echo 'Run this installer as your desktop user, without sudo.' >&2
    echo 'It will ask for administrator access only if Python packages are missing.' >&2
    exit 1
fi
installer_source=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export LC_MESSAGES=C
echo 'Selector Moebius 1.0 - Linux installer'
if ! python3 -c 'import sys, tkinter, venv, ensurepip; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
    echo 'Installing Python 3, Tkinter and virtual environment support...'
    if ! command -v sudo >/dev/null; then
        echo 'sudo is required to install missing system packages. Ask your administrator to install Python 3.10+, Tkinter and venv.' >&2
        exit 1
    fi
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-tk python3-pip
    elif command -v dnf >/dev/null; then
        sudo dnf install -y python3 python3-tkinter python3-pip
    elif command -v zypper >/dev/null; then
        sudo zypper --non-interactive install python3 python3-tk python3-pip
    elif command -v pacman >/dev/null; then
        sudo pacman -S --needed --noconfirm python python-pip tk
    else
        echo 'Unsupported package manager. Install Python 3.10+, Tkinter, pip and venv with your system package manager, then run this installer again.' >&2
        exit 1
    fi
fi
if ! python3 -c 'import sys, tkinter, venv, ensurepip; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
    echo 'Python 3.10+, Tkinter and venv are required. Upgrade your distribution or install a compatible Python version.' >&2
    exit 1
fi
exec python3 "$installer_source/instaladores/install.py" "$@"
