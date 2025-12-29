#!/usr/bin/env python3
# NexaLite — v1.6.0 (URL edition)
# Offline PC assistant — launches apps, manages shortcuts, small-talk, color-configurable UI,
# first-run data folder selection (DEFAULT = Documents\NexaLite), and Dev Tools.
# NOTE: HTML shortcut type removed; use URL type instead.

import os
import shlex
import json
import glob
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
from datetime import datetime
import random
import webbrowser
import sys

APP_TITLE   = "NexaLite — Local PC Assistant"
VERSION     = "1.6.0 Release"
CREATOR     = "Silent Dead Studio"
BUILD_NOTES = [
    "Default data dir: Documents\\NexaLite",
    "Blue/white theme, customizable via Nexa_tools (Reset available)",
    "Color safety: if bg == fg, theme resets to defaults automatically",
    "Configurable data directory — selectable at first launch, changeable later",
    "run/r command to open apps or .exe files; direct URLs also supported",
    "Developer Tools with add/del/list/b commands",
    "URL shortcut type (HTML type removed)",
    "Latest-Godot auto-detection",
    "Extended small-talk with exact replies for 'who are you?'/'how are you?'",
]

# ------------------------------------------------------------
# Bootstrap (data folder pointer only)
# ------------------------------------------------------------
HOME = Path(os.path.expandvars(r"%USERPROFILE%"))
DOCS_DIR = HOME / "Documents" / "NexaLite"  # <- DEFAULT
DOCS_DIR.mkdir(parents=True, exist_ok=True)
BOOTSTRAP_FILE = DOCS_DIR / "bootstrap.json"

DEFAULT_BG = "#103976"
DEFAULT_FG = "#ffffff"
DEFAULT_ENTRY_BG = "#081f44"

def _read_bootstrap() -> dict:
    if BOOTSTRAP_FILE.exists():
        try:
            return json.loads(BOOTSTRAP_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _write_bootstrap(data: dict):
    BOOTSTRAP_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _default_data_dir_candidates() -> list[Path]:
    home = Path(os.path.expandvars(r"%USERPROFILE%"))
    # Order: Documents (default), Desktop, (fallback) %APPDATA%\NexaLite
    return [
        home / "Documents" / "NexaLite",
        home / "Desktop"   / "NexaLite",
        Path(os.path.expandvars(r"%APPDATA%")) / "NexaLite",
    ]

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Global dynamic paths (depend on DATA_DIR)
# ------------------------------------------------------------
DATA_DIR: Path | None = None
SHORTCUTS_FILE: Path | None = None
SETTINGS_FILE:  Path | None = None

def set_data_dir(new_dir: Path):
    global DATA_DIR, SHORTCUTS_FILE, SETTINGS_FILE, BOOTSTRAP_FILE
    DATA_DIR = new_dir
    _ensure_dir(DATA_DIR)
    SHORTCUTS_FILE = DATA_DIR / "shortcuts.json"
    SETTINGS_FILE  = DATA_DIR / "settings.json"
    # bootstrap marad a DATA_DIR-ben
    BOOTSTRAP_FILE = DATA_DIR / "bootstrap.json"
    if not BOOTSTRAP_FILE.exists():
        _write_bootstrap({"data_dir": str(DATA_DIR)})

# ------------------------------------------------------------
# Built-in shortcuts (GX removed)
# ------------------------------------------------------------
BUILTIN = {
    "dc": {  # Discord
        "type": "program",
        "dynamic": False,
        "candidates": [
            r"%LOCALAPPDATA%\Discord\Update.exe",
            r"%USERPROFILE%\AppData\Local\Discord\Update.exe",
        ],
        "args": ["--processStart", "Discord.exe"],
        "label": "Discord",
    },
    "spoti": {  # Spotify
        "type": "program",
        "dynamic": False,
        "candidates": [
            r"%APPDATA%\Spotify\Spotify.exe",
            r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe",
        ],
        "args": [],
        "label": "Spotify",
    },
    "gd": {  # Godot — always choose the latest EXE
        "type": "program",
        "dynamic": True,
        "candidates": [],
        "args": [],
        "label": "Godot (latest)",
    },
}

# ------------------------------------------------------------
# User shortcuts (in DATA_DIR)
# ------------------------------------------------------------
def load_user_shortcuts():
    if SHORTCUTS_FILE and SHORTCUTS_FILE.exists():
        try:
            return json.loads(SHORTCUTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_user_shortcuts(data: dict):
    if SHORTCUTS_FILE:
        SHORTCUTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

USER_SHORTCUTS = {}

# ------------------------------------------------------------
# Settings (theme)
# ------------------------------------------------------------
def load_settings():
    if SETTINGS_FILE and SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"bg": DEFAULT_BG, "fg": DEFAULT_FG}

def save_settings(s):
    if SETTINGS_FILE:
        SETTINGS_FILE.write_text(json.dumps(s, indent=2), encoding="utf-8")

SETTINGS = {"bg": DEFAULT_BG, "fg": DEFAULT_FG}

# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------
def ex(path: str) -> str | None:
    p = os.path.expandvars(os.path.expanduser(path))
    return p if os.path.exists(p) else None

def which_any(cands: list[str]) -> str | None:
    for cand in cands:
        full = ex(cand)
        if full:
            return full
        w = shutil.which(os.path.expandvars(os.path.expanduser(cand)))
        if w:
            return w
    return None

def find_latest_godot() -> str | None:
    search_roots = [
        r"%USERPROFILE%\Downloads",
        r"%USERPROFILE%\Desktop",
        r"%PROGRAMFILES%\Godot",
        r"%PROGRAMFILES(x86)%\Godot",
        r"%LOCALAPPDATA%\Programs",
        r"%USERPROFILE%\AppData\Local\Godot",
    ]
    patterns = ["Godot*.exe", "godot*.exe"]
    candidates = []
    for root in search_roots:
        root_exp = os.path.expandvars(root)
        if not os.path.isdir(root_exp):
            continue
        for pat in patterns:
            for f in glob.glob(str(Path(root_exp) / "**" / pat), recursive=True):
                try:
                    candidates.append((f, os.path.getmtime(f)))
                except Exception:
                    pass
    for d in [r"C:\Program Files\Godot\Godot.exe", r"C:\Godot\Godot.exe"]:
        p = ex(d)
        if p:
            try:
                candidates.append((p, os.path.getmtime(p)))
            except Exception:
                candidates.append((p, 0))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def launch_path(exe: str, args: list[str]):
    try:
        subprocess.Popen([exe, *args], shell=False)
        return True, f"✅ Launching: {exe}{(' ' + ' '.join(args)) if args else ''}"
    except Exception as e:
        return False, f"⚠️ Launch error: {e}"

# -------------- URL helpers --------------
def _looks_like_url(s: str) -> bool:
    if not s:
        return False
    s = s.strip().lower()
    return s.startswith("http://") or s.startswith("https://") or s.startswith("www.")

def _normalize_url(s: str) -> str:
    s = s.strip()
    if s.lower().startswith("www."):
        return "https://" + s
    return s

def open_url_in_browser(url: str) -> tuple[bool, str]:
    try:
        url = _normalize_url(url)
        ok = webbrowser.open(url)
        if not ok and sys.platform.startswith("win"):
            try:
                os.startfile(url)
            except Exception:
                pass
        return True, f"✅ Opening in browser: {url}"
    except Exception as e:
        return False, f"⚠️ URL open error: {e}"

# ------------------------------------------------------------
# Launch logic (programs + URL)
# ------------------------------------------------------------
def launch_shortcut(name: str) -> tuple[bool, str]:
    n_raw = name.strip()
    if _looks_like_url(n_raw):
        return open_url_in_browser(n_raw)

    n = n_raw.lower()

    # User-defined shortcuts
    if n in USER_SHORTCUTS:
        info = USER_SHORTCUTS[n]
        t = info.get("type")

        if t == "program":
            path = os.path.expandvars(os.path.expanduser(info.get("path", "")))
            if not os.path.exists(path):
                return False, f"❌ Not found: {path}"
            args = list(info.get("args", []))
            return launch_path(path, args)

        elif t == "url":
            url = info.get("url", "")
            if not url.strip():
                return False, "❌ URL shortcut is empty."
            return open_url_in_browser(url)

        # Backward-compat: if régi jsonban még 'html' van, próbáljuk URL-ként kezelni
        elif t == "html":
            html = info.get("html", "").strip()
            if _looks_like_url(html):
                return open_url_in_browser(html)
            return False, "❌ HTML type is no longer supported. Please recreate as URL."

    # Built-ins
    if n in BUILTIN:
        conf = BUILTIN[n]
        if conf["type"] == "program":
            if conf.get("dynamic") and n == "gd":
                exe = find_latest_godot()
                if not exe:
                    return False, "❌ Godot not found."
                return launch_path(exe, conf.get("args", []))
            else:
                exe = which_any(conf.get("candidates", []))
                if not exe:
                    return False, f"❌ Shortcut not found: {n}"
                return launch_path(exe, conf.get("args", []))

    # As direct exe/path
    p = ex(n) or shutil.which(n)
    if p:
        return launch_path(p, [])
    return False, f"❌ Unknown shortcut or path: {name}"

# ------------------------------------------------------------
# Small talk (includes exact answers you requested)
# ------------------------------------------------------------
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are 10 types of people: those who understand binary and those who don’t.",
    "I would tell you a UDP joke, but you might not get it.",
    "A SQL query walks into a bar, goes up to two tables and asks: ‘Can I join you?’",
]

def chat_reply(text: str) -> str | None:
    t = text.strip().lower()

    # exact phrases first
    if "who are you" in t:
        return "Im Nexa your local pc assisstant."
    if "how are you" in t:
        return "im good thanks :)"

    # name mention
    if "nexa" in t:
        return "I'm here. What should I run?"

    # greetings
    if any(g in t for g in {"hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"}):
        return "Hey! Need something launched? Try `r gd` or type `help`."

    # capabilities / creator / version
    if "what can you do" in t or "help me" in t:
        return "I launch programs/URLs via shortcuts, list/manage them in Dev Tools, and you can theme me in Nexa_tools."
    if "who made you" in t or "creator" in t:
        return f"I was created by {CREATOR}."
    if "version" in t:
        return f"My current version is {VERSION}."

    # time/date
    if "time is it" in t or t == "time?" or t == "time":
        now = datetime.now()
        return f"It’s {now.strftime('%H:%M:%S')} on {now.strftime('%Y-%m-%d')}."
    if "date" in t:
        now = datetime.now()
        return f"Today is {now.strftime('%Y-%m-%d')}."

    # jokes / thanks / bye
    if "joke" in t or "vicc" in t:
        return random.choice(JOKES)
    if "thanks" in t or "thank you" in t or "köszi" in t or "köszönöm" in t:
        return "You're welcome 🙂"
    if any(b in t for b in ["bye", "goodbye", "see ya", "viszlát", "szia"]):
        return "Bye! If you need me, just type `help`."

    return None

# ------------------------------------------------------------
# Help
# ------------------------------------------------------------
def print_dev_help(printer):
    rows = [
        ("add",            "to make custom shortcuts (opens GUI)"),
        ("del <name>",     "delete shortcut by name"),
        ("list",           "lists all your custom shortcuts"),
        ("b",              "back to normal mode"),
    ]
    title = "Developer Tools — commands"
    printer(title); printer("-" * len(title))
    left_w = max(len(r[0]) for r in rows) + 2
    printer("Command".ljust(left_w) + "Description")
    printer("-" * (left_w + 12))
    for cmd, desc in rows:
        printer(cmd.ljust(left_w) + desc)

def help_summary() -> str:
    return (
        "Commands: run/r, list, help, dev, time, nexa_tools, dev_info, clear, q\n"
        "More help: help <topic>\n"
        "Topics: r, list, dev, time, nexa_tools, dev_info, clear, q\n"
    )

def help_topic(topic: str) -> str:
    t = topic.lower()
    if t in ("r", "run"):
        return (
            "run / r — launch a shortcut, direct .exe path, or a URL.\n"
            "Usage:\n"
            "  r <shortcut>\n"
            "  r \"C:\\Path\\to\\app.exe\"\n"
            "  r https://example.com\n"
            "Built-ins: gd, dc, spoti. Add more in Dev Tools.\n"
        )
    if t == "list":
        return "list — show shortcuts grouped by type and source."
    if t == "dev":
        return (
            "dev — open Developer Tools (manage custom shortcuts).\n"
            "Commands:\n"
            "  add              — to make custom shortcuts (opens GUI)\n"
            "  del <name>       — delete shortcut by name\n"
            "  list             — lists all your custom shortcuts\n"
            "  b                — back to normal mode\n"
        )
    if t == "time":
        return "time — shows current local date & time."
    if t == "nexa_tools":
        return (
            "nexa_tools — customize Nexa and choose the local save folder.\n"
            "Appearance:\n"
            "  • Window Background / Text Color — click Pick… to choose colors\n"
            "  • Reset — restores the default blue/white theme instantly\n"
            "Storage:\n"
            "  • Data folder — select from dropdown (Documents/Desktop/AppData) or choose Custom… to browse\n"
            "  • On save, Nexa stores settings/shortcuts in the selected folder\n"
        )
    if t == "dev_info":
        return "dev_info — shows creator, version and build notes."
    if t == "clear":
        return "clear — clears the screen."
    if t in ("q", "quit", "exit"):
        return "q — quit NexaLite. (Aliases: exit, quit)"
    return "No detailed help for this topic."

# ------------------------------------------------------------
# Color helpers
# ------------------------------------------------------------
def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def _darken(hex_color, factor=0.25):
    r, g, b = _hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return _rgb_to_hex((r, g, b))

def _normalize_hex(h: str) -> str:
    if not h:
        return ""
    h = h.strip().lower()
    if h.startswith("#"):
        h = h[1:]
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return f"#{h}"

# ------------------------------------------------------------
# First-run DataDir dialog
# ------------------------------------------------------------
class DataDirDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Choose data folder for Nexa")
        self.resizable(False, False)
        self.configure(bg="#0b2a5a")
        self.result = None  # Path

        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text="Where should Nexa store its data?", bg="#0b2a5a", fg="white").grid(row=0, column=0, columnspan=4, sticky="w", **pad)

        options = _default_data_dir_candidates()
        self.opt_labels = [
            f"Documents\\NexaLite ({str(options[0])})",
            f"Desktop\\NexaLite ({str(options[1])})",
            f"%APPDATA%\\NexaLite ({str(options[2])})",
            "Custom…",
        ]
        self.opt_values = [str(options[0]), str(options[1]), str(options[2]), "CUSTOM"]

        tk.Label(self, text="Location:", bg="#0b2a5a", fg="white").grid(row=1, column=0, sticky="w", **pad)

        self.choice_var = tk.StringVar(value=self.opt_labels[0])  # default: Documents
        self.choice = ttk.Combobox(self, textvariable=self.choice_var, values=self.opt_labels, state="readonly", width=70)
        self.choice.grid(row=1, column=1, columnspan=3, sticky="we", **pad)
        self.choice.bind("<<ComboboxSelected>>", self._on_choice)

        self.path_entry = tk.Entry(self, width=68, bg="#081f44", fg="white", insertbackground="white")
        self.path_entry.grid(row=2, column=0, columnspan=3, sticky="we", **pad)
        self.path_entry.insert(0, self.opt_values[0])

        tk.Button(self, text="Browse…", command=self._browse).grid(row=2, column=3, sticky="e", **pad)

        btn = tk.Frame(self, bg="#0b2a5a")
        btn.grid(row=99, column=0, columnspan=4, sticky="e", padx=10, pady=(0,10))
        tk.Button(btn, text="Cancel", command=self._cancel).pack(side="right", padx=(6,0))
        tk.Button(btn, text="Use this folder", command=self._save).pack(side="right")

        self.grid_columnconfigure(1, weight=1)

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _on_choice(self, *_):
        sel = self.choice_var.get()
        idx = self.opt_labels.index(sel)
        val = self.opt_values[idx]
        if val == "CUSTOM":
            self._browse()
        else:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, val)

    def _browse(self):
        d = filedialog.askdirectory(title="Select data folder")
        if d:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)
            self.choice_var.set("Custom…")

    def _cancel(self):
        self.result = None
        self.destroy()

    def _save(self):
        p = self.path_entry.get().strip()
        if not p:
            messagebox.showerror("Error", "Please choose a data folder.")
            return
        self.result = Path(p)
        self.destroy()

# ------------------------------------------------------------
# Nexa_tools (theme + data dir change) with Reset button
# ------------------------------------------------------------
class ToolsDialog(tk.Toplevel):
    def __init__(self, master, current_bg, current_fg, current_data_dir: Path):
        super().__init__(master)
        self.master = master
        self.title("Nexa_tools — appearance & storage")
        self.configure(bg=current_bg)
        self.resizable(False, False)
        self.result = None  # {"bg":"#rrggbb","fg":"#rrggbb","data_dir": Path or None}

        pad = {"padx": 10, "pady": 6}

        for col in (0,1,2,3,4):
            self.grid_columnconfigure(col, weight=0)
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text="Window background:", bg=current_bg, fg=current_fg).grid(row=0, column=0, sticky="w", **pad)
        self.bg_entry = tk.Entry(self, width=26)
        self.bg_entry.insert(0, current_bg)
        self.bg_entry.grid(row=0, column=1, sticky="we", **pad)
        tk.Button(self, text="Pick…", command=self.pick_bg).grid(row=0, column=2, sticky="e", padx=(0,14), pady=6)

        tk.Label(self, text="Text color:", bg=current_bg, fg=current_fg).grid(row=1, column=0, sticky="w", **pad)
        self.fg_entry = tk.Entry(self, width=26)
        self.fg_entry.insert(0, current_fg)
        self.fg_entry.grid(row=1, column=1, sticky="we", **pad)
        tk.Button(self, text="Pick…", command=self.pick_fg).grid(row=1, column=2, sticky="e", padx=(0,14), pady=6)

        self.reset_btn = tk.Button(self, text="Reset", command=self._reset)
        self.reset_btn.grid(row=0, column=4, rowspan=2, sticky="ns", padx=(6,10), pady=6)

        tk.Label(self, text="Data folder:", bg=current_bg, fg=current_fg).grid(row=2, column=0, sticky="w", **pad)
        base_opts = _default_data_dir_candidates()
        self.dd_labels = [
            f"Documents\\NexaLite ({str(base_opts[0])})",
            f"Desktop\\NexaLite ({str(base_opts[1])})",
            f"%APPDATA%\\NexaLite ({str(base_opts[2])})",
            "Custom…",
        ]
        self.dd_values = [str(base_opts[0]), str(base_opts[1]), str(base_opts[2]), "CUSTOM"]

        self.dd_choice_var = tk.StringVar(value="Custom…")
        self.dd_choice = ttk.Combobox(self, textvariable=self.dd_choice_var, values=self.dd_labels, state="readonly", width=70)
        self.dd_choice.grid(row=2, column=1, columnspan=3, sticky="we", **pad)
        self.dd_choice.bind("<<ComboboxSelected>>", self._on_dd_choice)

        tk.Label(self, text="Selected path:", bg=current_bg, fg=current_fg).grid(row=3, column=0, sticky="w", **pad)
        self.dd_entry = tk.Entry(self, width=68)
        self.dd_entry.grid(row=3, column=1, columnspan=2, sticky="we", **pad)
        self.dd_entry.insert(0, str(current_data_dir))
        tk.Button(self, text="Browse…", command=self._browse_dir).grid(row=3, column=3, sticky="e", padx=(0,14), pady=6)

        btn = tk.Frame(self, bg=current_bg)
        btn.grid(row=99, column=0, columnspan=5, sticky="e", padx=10, pady=(8,10))
        tk.Button(btn, text="Cancel", command=self._cancel).pack(side="right", padx=(6,0))
        tk.Button(btn, text="Save", command=self._save).pack(side="right", padx=(6,0))

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def pick_bg(self):
        color = colorchooser.askcolor(title="Pick background", color=self.bg_entry.get())[1]
        if color:
            self.bg_entry.delete(0, "end"); self.bg_entry.insert(0, color)

    def pick_fg(self):
        color = colorchooser.askcolor(title="Pick text color", color=self.fg_entry.get())[1]
        if color:
            self.fg_entry.delete(0, "end"); self.fg_entry.insert(0, color)

    def _on_dd_choice(self, *_):
        sel = self.dd_choice_var.get()
        idx = self.dd_labels.index(sel)
        val = self.dd_values[idx]
        if val == "CUSTOM":
            self._browse_dir()
        else:
            self.dd_entry.delete(0, "end")
            self.dd_entry.insert(0, val)

    def _browse_dir(self):
        d = filedialog.askdirectory(title="Select data folder")
        if d:
            self.dd_entry.delete(0, "end")
            self.dd_entry.insert(0, d)
            self.dd_choice_var.set("Custom…")

    def _cancel(self):
        self.result = None; self.destroy()

    def _save(self):
        bg = _normalize_hex(self.bg_entry.get().strip() or DEFAULT_BG)
        fg = _normalize_hex(self.fg_entry.get().strip() or DEFAULT_FG)

        # if colors identical → reset to defaults (safety)
        if bg == fg:
            bg, fg = DEFAULT_BG, DEFAULT_FG
            try:
                self.master.print("⚠️ Background and text colors were identical. Theme reset to default.")
            except Exception:
                pass

        new_dir = Path(self.dd_entry.get().strip()) if self.dd_entry.get().strip() else None
        self.result = {"bg": bg, "fg": fg, "data_dir": new_dir}
        self.destroy()

    def _reset(self):
        self.bg_entry.delete(0, "end"); self.bg_entry.insert(0, DEFAULT_BG)
        self.fg_entry.delete(0, "end"); self.fg_entry.insert(0, DEFAULT_FG)
        self.master.apply_theme(DEFAULT_BG, DEFAULT_FG)
        self.master.print("🔄 Theme reset to default (blue background, white text).")
        save_settings({"bg": DEFAULT_BG, "fg": DEFAULT_FG})

# ------------------------------------------------------------
# Dev: Add Shortcut dialog (URL + Program)
# ------------------------------------------------------------
class AddShortcutDialog(tk.Toplevel):
    def __init__(self, master, colors):
        super().__init__(master)
        bg = colors["bg"]; fg = colors["fg"]
        self.title("Add shortcut")
        self.configure(bg=bg)
        self.resizable(False, False)
        self.result = None

        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text="Shortcut name:", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", **pad)
        self.name_entry = tk.Entry(self, width=34)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="we", **pad)

        tk.Label(self, text="Type:", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", **pad)
        self.type_var = tk.StringVar(value="program")
        type_menu = ttk.Combobox(self, textvariable=self.type_var, values=["program", "url"], state="readonly", width=31)
        type_menu.grid(row=1, column=1, columnspan=2, sticky="we", **pad)
        type_menu.bind("<<ComboboxSelected>>", self._on_type_change)

        # program fields
        self.path_label = tk.Label(self, text="Program .exe path:", bg=bg, fg=fg)
        self.path_entry = tk.Entry(self, width=34)
        self.browse_btn = tk.Button(self, text="Browse…", command=self._browse)

        # url fields
        self.url_label = tk.Label(self, text="URL:", bg=bg, fg=fg)
        self.url_entry = tk.Entry(self, width=34)

        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.grid(row=99, column=0, columnspan=3, sticky="e", padx=10, pady=(0,10))
        tk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side="right", padx=(6,0))
        tk.Button(btn_frame, text="Save", command=self._save).pack(side="right")

        self._on_type_change()
        self.name_entry.focus_set()
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _on_type_change(self, *_):
        t = self.type_var.get()
        # hide all
        self.path_label.grid_remove(); self.path_entry.grid_remove(); self.browse_btn.grid_remove()
        self.url_label.grid_remove(); self.url_entry.grid_remove()

        if t == "program":
            self.path_label.grid(row=2, column=0, sticky="w", padx=10, pady=6)
            self.path_entry.grid(row=2, column=1, sticky="we", padx=10, pady=6)
            self.browse_btn.grid(row=2, column=2, sticky="we", padx=10, pady=6)
        elif t == "url":
            self.url_label.grid(row=2, column=0, sticky="w", padx=10, pady=6)
            self.url_entry.grid(row=2, column=1, columnspan=2, sticky="we", padx=10, pady=6)

    def _browse(self):
        file = filedialog.askopenfilename(title="Select .exe", filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if file:
            self.path_entry.delete(0, "end"); self.path_entry.insert(0, file)

    def _cancel(self):
        self.result = None; self.destroy()

    def _save(self):
        name = (self.name_entry.get() or "").strip().lower()
        if not name:
            messagebox.showerror("Error", "Please enter a shortcut name."); return
        t = self.type_var.get()
        if t == "program":
            path = (self.path_entry.get() or "").strip()
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Valid .exe path required."); return
            self.result = {"name": name, "type": "program", "path": path, "args": []}
        elif t == "url":
            url = (self.url_entry.get() or "").strip()
            if not url:
                messagebox.showerror("Error", "URL cannot be empty."); return
            self.result = {"name": name, "type": "url", "url": url}
        self.destroy()

# ------------------------------------------------------------
# App
# ------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x580")

        self.mode_dev = False
        self.pending_run = False

        # 1) Ensure DATA_DIR (first run prompt if needed) — DEFAULT = Documents\NexaLite
        self._ensure_data_dir()

        # 2) Load settings + UI
        global SETTINGS, USER_SHORTCUTS
        SETTINGS = load_settings()

        self.output = tk.Text(self, wrap="word", state="disabled", font=("Consolas", 12))
        self.output.pack(fill="both", expand=True, padx=10, pady=(10, 8))

        self.bottom = tk.Frame(self)
        self.bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.prompt = tk.Label(self.bottom, text="›", width=2)
        self.prompt.pack(side="left")

        self.entry = tk.Entry(self)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)

        self.apply_theme(SETTINGS["bg"], SETTINGS["fg"])

        # 3) Load shortcuts
        USER_SHORTCUTS = load_user_shortcuts()

        # greet
        self._greet()
        self.entry.focus_set()

    # ---------- data dir ----------
    def _ensure_data_dir(self):
        bs = _read_bootstrap()
        data_dir_str = bs.get("data_dir")
        if data_dir_str and data_dir_str.strip():
            set_data_dir(Path(data_dir_str))
            return
        # Ask user — preselect Documents\NexaLite (default)
        dlg = DataDirDialog(self)
        self.wait_window(dlg)
        if not dlg.result:
            fallback = DOCS_DIR
            set_data_dir(fallback)
            _write_bootstrap({"data_dir": str(fallback)})
        else:
            set_data_dir(dlg.result)
            _write_bootstrap({"data_dir": str(dlg.result)})

    def _change_data_dir(self, new_dir: Path):
        """Move existing data to new_dir, update bootstrap, update globals."""
        old_dir = DATA_DIR
        if not old_dir or old_dir == new_dir:
            return

        _ensure_dir(new_dir)

        try:
            if SHORTCUTS_FILE and SHORTCUTS_FILE.exists():
                shutil.move(str(SHORTCUTS_FILE), str(new_dir / "shortcuts.json"))
            if SETTINGS_FILE and SETTINGS_FILE.exists():
                shutil.move(str(SETTINGS_FILE), str(new_dir / "settings.json"))
            set_data_dir(new_dir)
            _write_bootstrap({"data_dir": str(new_dir)})
            self.print(f"📁 Data folder changed to: {new_dir}")
        except Exception as e:
            messagebox.showerror("Move error", f"Could not move data: {e}")

    # ---------- theming ----------
    def apply_theme(self, bg, fg):
        bg = _normalize_hex(bg) if bg else DEFAULT_BG
        fg = _normalize_hex(fg) if fg else DEFAULT_FG

        # Guard: identical colors → reset to defaults
        if bg == fg:
            bg, fg = DEFAULT_BG, DEFAULT_FG
            try:
                self.print("⚠️ Background and text colors were identical. Theme reset to default.")
            except Exception:
                pass

        def _dark_local(hex_color, factor=0.25):
            h = hex_color.lstrip('#')
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            return f"#{r:02x}{g:02x}{b:02x}"

        entry_bg = _dark_local(bg, 0.25) if bg else DEFAULT_ENTRY_BG
        self.configure(bg=bg)
        self.bottom.configure(bg=bg)
        self.output.configure(bg=bg, fg=fg, insertbackground=fg)
        self.prompt.configure(bg=bg, fg=fg)
        self.entry.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        SETTINGS["bg"] = bg; SETTINGS["fg"] = fg
        save_settings(SETTINGS)

    # ---------- greetings ----------
    def _greet(self):
        self.print("Hello! 👋 I'm Nexa — your local PC assistant.")
        self.print("Type 'help' anytime for a quick list of commands.")

    # ---------- print helper ----------
    def print(self, text=""):
        self.output.configure(state="normal")
        self.output.insert("end", text + ("\n" if not text.endswith("\n") else ""))
        self.output.see("end")
        self.output.configure(state="disabled")

    # ---------- event loop ----------
    def on_enter(self, _=None):
        cmdline = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not cmdline:
            return
        self.print(f"» {cmdline}")
        self.handle(cmdline)

    def handle(self, cmdline: str):
        if self.pending_run:
            name = cmdline.strip()
            _, msg = launch_shortcut(name)
            self.print(msg)
            self.pending_run = False
            return

        parts = shlex.split(cmdline)
        if not parts:
            return
        cmd, *args = parts
        cmd = cmd.lower()

        if self.mode_dev:
            self.handle_dev(cmd, args)
            return

        if cmd in ("run", "r"):
            if not args:
                self.print("What should I run? (shortcut, .exe path, or URL)")
                self.pending_run = True
            else:
                _, msg = launch_shortcut(" ".join(args))
                self.print(msg)
            return

        if cmd == "list":
            self.show_lists()
            return

        if cmd == "help":
            self.print(help_topic(args[0]) if args else help_summary())
            return

        if cmd == "time":
            now = datetime.now()
            self.print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}")
            return

        if cmd == "dev_info":
            self.show_dev_info()
            return

        if cmd in ("nexa_tools", "tools"):
            self.open_tools()
            return

        if cmd == "clear":
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.configure(state="disabled")
            self._greet()
            return

        if cmd in ("q", "exit", "quit"):
            self.print("Bye.")
            self.after(150, self.destroy)
            return

        if cmd == "dev":
            self.mode_dev = True
            print_dev_help(self.print)
            return

        # small talk fallback
        reply = chat_reply(cmdline)
        if reply:
            self.print(reply)
        else:
            self.print("I didn't get that. Type `help` or `help r` / `help dev` / `help nexa_tools`.")

    # ---------- Nexa_tools ----------
    def open_tools(self):
        dlg = ToolsDialog(self, SETTINGS["bg"], SETTINGS["fg"], DATA_DIR)
        self.wait_window(dlg)
        if dlg.result:
            # theme
            self.apply_theme(dlg.result["bg"], dlg.result["fg"])
            # data dir (if changed)
            new_dir = dlg.result.get("data_dir")
            if new_dir and Path(new_dir) != DATA_DIR:
                self._change_data_dir(Path(new_dir))
            self.print(f"✅ Theme updated. BG: {dlg.result['bg']}  FG: {dlg.result['fg']}")
        else:
            self.print("Canceled.")

    # ---------- lists ----------
    def show_lists(self):
        # Built-in Programs
        self.print("Built-in Program shortcuts:")
        any_prog = False
        for k in sorted(BUILTIN.keys()):
            if BUILTIN[k]["type"] != "program":
                continue
            any_prog = True
            path = find_latest_godot() if (BUILTIN[k].get("dynamic") and k == "gd") \
                   else which_any(BUILTIN[k].get("candidates", []))
            path = path or "(not found)"
            label = BUILTIN[k].get("label", k)
            self.print(f"  - {k}  [{label}]  ->  {path}")
        if not any_prog:
            self.print("  —")

        # Your Programs
        self.print("Your Program shortcuts:")
        shown_prog = False
        shown_url  = False
        for k in sorted(USER_SHORTCUTS.keys()):
            v = USER_SHORTCUTS[k]
            if v.get("type") == "program":
                shown_prog = True
                self.print(f"  - {k} (program) -> {v.get('path')} {' '.join(v.get('args', []))}")
        if not shown_prog:
            self.print("  —")

        # Your URLs
        self.print("Your URL shortcuts:")
        for k in sorted(USER_SHORTCUTS.keys()):
            v = USER_SHORTCUTS[k]
            if v.get("type") == "url":
                shown_url = True
                self.print(f"  - {k} -> {v.get('url')}")
        if not shown_url:
            self.print("  —")

    # ---------- Dev info ----------
    def show_dev_info(self):
        self.print("NexaLite — development info")
        self.print("---------------------------")
        self.print(f"Version : {VERSION}")
        self.print(f"Creator : {CREATOR}")
        self.print(f"Data dir: {DATA_DIR}")
        self.print(f"Shortcuts file: {SHORTCUTS_FILE}")
        self.print(f"Settings file : {SETTINGS_FILE}")
        self.print(f"Bootstrap   : {BOOTSTRAP_FILE}")
        self.print("Build notes:")
        for note in BUILD_NOTES:
            self.print(f"  • {note}")

    # ---------- Dev mode ----------
    def handle_dev(self, cmd: str, args: list[str]):
        if cmd in ("help", "?"):
            print_dev_help(self.print)
            return

        if cmd == "add":
            dlg = AddShortcutDialog(self, {"bg": SETTINGS["bg"], "fg": SETTINGS["fg"]})
            self.wait_window(dlg)
            if dlg.result:
                name = dlg.result["name"]
                if name in BUILTIN:
                    self.print("❌ You cannot overwrite a built-in name.")
                    return
                if name in USER_SHORTCUTS:
                    if not messagebox.askyesno("Overwrite?", f"'{name}' already exists. Overwrite it?"):
                        self.print("Canceled (not overwritten).")
                        return
                USER_SHORTCUTS[name] = {k: v for k, v in dlg.result.items() if k != "name"}
                save_user_shortcuts(USER_SHORTCUTS)
                self.print(f"✅ Saved: {name}  →  {SHORTCUTS_FILE}")
            else:
                self.print("Canceled.")
            return

        if cmd == "del":
            if not args:
                self.print("Usage: del <name>")
                return
            name = args[0].lower()
            if name in USER_SHORTCUTS:
                USER_SHORTCUTS.pop(name)
                save_user_shortcuts(USER_SHORTCUTS)
                self.print(f"🗑️ Deleted: {name}")
            else:
                self.print("No such shortcut.")
            return

        if cmd == "list":
            self.print("[Developer Tools] Your shortcuts:")
            if not USER_SHORTCUTS:
                self.print("  —")
            else:
                for k in sorted(USER_SHORTCUTS.keys()):
                    v = USER_SHORTCUTS[k]
                    if v.get("type") == "program":
                        self.print(f"  - {k} (program) -> {v.get('path')} {' '.join(v.get('args', []))}")
                    elif v.get("type") == "url":
                        self.print(f"  - {k} (url) -> {v.get('url')}")
                    elif v.get("type") == "html":  # legacy rows
                        self.print(f"  - {k} (legacy html) -> please recreate as URL")
            return

        if cmd == "b":
            self.mode_dev = False
            self.print("Developer Tools closed.")
            return

        if cmd in ("run", "r"):
            if not args:
                self.print("What should I run? (shortcut, .exe path, or URL)")
                self.pending_run = True
            else:
                _, msg = launch_shortcut(" ".join(args))
                self.print(msg)
            return

        reply = chat_reply(" ".join([cmd] + args))
        if reply:
            self.print(reply)
        else:
            self.print("Unknown Dev command. Type `help` (inside Dev) for a command table.")

# ------------------------------------------------------------
# main
# ------------------------------------------------------------
if __name__ == "__main__":
    if os.name != "nt":
        print("Note: optimized for Windows.")
    app = App()
    app.mainloop()
