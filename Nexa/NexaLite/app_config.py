#!/usr/bin/env python3
# NexaLite — Local PC Assistant (v2.0 Release Build)
# Created by Silent Dead Studio

import os
from pathlib import Path

# ------------------------------------------------------------
# App Information
# ------------------------------------------------------------
APP_TITLE   = "NexaLite — Local PC Assistant"
VERSION     = "2.0 Release"
CREATOR     = "Silent Dead Studio"

# ------------------------------------------------------------
# Visual Defaults
# ------------------------------------------------------------
DEFAULT_BG        = "#103976"
DEFAULT_FG        = "#ffffff"
DEFAULT_ENTRY_BG  = "#081f44"

# ------------------------------------------------------------
# Build Notes (for dev_info / release documentation)
# ------------------------------------------------------------
BUILD_NOTES = [
    "NexaLite v2.0 — Local PC Assistant (Release Build)",
    "Modular architecture: separated into base, commands, speech, and ui packages for easier maintenance.",
    "Single built-in shortcut: np (opens Windows Notepad).",
    "Core command set: r, add func, del func, c func, list, nexa_tools, time, help, clear, q.",
    "Supports automatic plugin and addon detection within the Nexa root directory.",
    "Theme customization via Nexa_tools (background, text color, and instant reset to defaults).",
    "User-defined shortcuts saved in JSON — supports both program (.exe) and URL entries.",
    "Plugins and addons can be run directly using 'r func <name>'.",
    "Close known apps safely with 'c func <name>' (graceful task termination).",
    "Integrated smalltalk system with greetings, questions, jokes, and fun facts.",
    "All data is stored locally — no internet, accounts, or external APIs required.",
    "Release-ready: lightweight, portable, and fully compatible with PyInstaller one-file builds."
]

# ------------------------------------------------------------
# Default Paths (resolved dynamically at runtime)
# ------------------------------------------------------------
HOME = Path(os.path.expandvars(r"%USERPROFILE%"))
DOCS_DIR = HOME / "Documents" / "NexaLite"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
BOOTSTRAP_FILE = DOCS_DIR / "bootstrap.json"
