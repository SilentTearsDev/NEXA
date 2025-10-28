# ============================================================
# NexaLite — Root path resolver
# Handles correct folder resolution for both source and PyInstaller EXE
# ============================================================

from pathlib import Path
import sys, os

def _get_app_dir() -> Path:
    """
    Returns the directory of the running NexaLite app.
    Works both in normal Python and PyInstaller-frozen mode.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as a frozen .exe (PyInstaller)
        # sys.executable -> C:\Users\<user>\Documents\ALL_PROJECTS\Nexa\NexaLite_v2.0.exe
        return Path(sys.executable).resolve().parent
    else:
        # Running from source (main.py inside NexaLite/)
        return Path(__file__).resolve().parent.parent


def _find_nexa_root(start_dir: Path) -> Path:
    """
    Ensures we get the Nexa root folder.
    It looks upward from the app directory until it finds a folder named 'Nexa'.
    """
    for parent in [start_dir] + list(start_dir.parents):
        if parent.name.lower() == "nexa":
            return parent
    # Fallback: assume Nexa root is one level above
    return start_dir.parent


# ----------------------------------------------------------------
# Resolve key folders
# ----------------------------------------------------------------
NEXALITE_DIR = _get_app_dir()         # NexaLite/ or the folder of the .exe
NEXA_ROOT    = _find_nexa_root(NEXALITE_DIR)  # parent Nexa folder
PLUGINS_DIR  = NEXA_ROOT / "plugins"
ADDONS_DIR   = NEXA_ROOT / "addons"
DATA_DIR     = NEXALITE_DIR / "data"

# ----------------------------------------------------------------
# Safety: auto-create plugin/addon folders if missing
# ----------------------------------------------------------------
for folder in (PLUGINS_DIR, ADDONS_DIR, DATA_DIR):
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[warn] Could not create {folder}: {e}")

# ----------------------------------------------------------------
# Simple debug function
# ----------------------------------------------------------------
if __name__ == "__main__":
    print("=== NexaLite Roots Debug ===")
    print(f"App dir   : {NEXALITE_DIR}")
    print(f"Nexa root : {NEXA_ROOT}")
    print(f"Plugins   : {PLUGINS_DIR}")
    print(f"Addons    : {ADDONS_DIR}")
    print(f"Data dir  : {DATA_DIR}")
    input("\nPress Enter to exit...")
