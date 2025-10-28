import json
from pathlib import Path
from base.storage import PATHS

def _read(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _write(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

_DEFAULT_SETTINGS = {"bg":"#103976","fg":"#ffffff"}
_DEFAULT_BUILTINS = {
    # keep 'np' as a default built-in
    "np": {
        "type": "program",
        "candidates": ["notepad.exe", r"%SystemRoot%\system32\notepad.exe"],
        "args": [],
        "process_name": "notepad.exe"
    }
}

def load_all():
    # ha nincs builtins.json, az alapértelmezettet adjuk vissza (és NEM írjuk ki rögtön)
    return {
        "functions": _read(PATHS.functions, {}),
        "settings":  _read(PATHS.settings,  _DEFAULT_SETTINGS),
        "plugins":   _read(PATHS.plugins,   {}),
        "addons":    _read(PATHS.addons,    {}),
        "builtins":  _read(PATHS.builtins,  _DEFAULT_BUILTINS),
    }

def save_functions(d: dict): _write(PATHS.functions, d)
def save_settings(d: dict):  _write(PATHS.settings,  d)
def save_plugins(d: dict):   _write(PATHS.plugins,   d)
def save_addons(d: dict):    _write(PATHS.addons,    d)
def save_builtins(d: dict):  _write(PATHS.builtins,  d)
