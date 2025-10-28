# base/discover.py
from pathlib import Path
from base.roots import NEXA_ROOT, PLUGINS_DIR, ADDONS_DIR
from base.registry import load_all, save_plugins, save_addons

SCAN_EXTS = {".exe", ".bat", ".cmd"}  # executable on Windows

def _rel_to_root(p: Path) -> str:
    """Return a safe relative path to the Nexa root (fallback to absolute if not possible)."""
    try:
        return str(p.resolve().relative_to(NEXA_ROOT.resolve()))
    except Exception:
        return str(p.resolve())

def _scan_dir(root: Path) -> dict:
    """
    Returns: {name: {active: bool, path: 'rel/path'}}
    - Walks the directory tree (rglob)
    - Accepted extensions: SCAN_EXTS
    - On name collision, appends a number (name-2, name-3, ...)
    """
    found = {}
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return found

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() not in SCAN_EXTS:
            continue
        base = file.stem.lower()
        name = base
        i = 2
        while name in found:
            name = f"{base}-{i}"
            i += 1
        found[name] = {"active": True, "path": _rel_to_root(file)}
    return found

def sync_scan():
    """
    Merge automatically discovered plugins/addons with existing registries.
    Existing keys are NOT overwritten.
    Returns: (plugins_dict, addons_dict)
    """
    state = load_all()
    plugins = dict(state["plugins"])
    addons  = dict(state["addons"])

    auto_plugins = _scan_dir(PLUGINS_DIR)
    auto_addons  = _scan_dir(ADDONS_DIR)

    for k, v in auto_plugins.items():
        plugins.setdefault(k, v)
    for k, v in auto_addons.items():
        addons.setdefault(k, v)

    save_plugins(plugins)
    save_addons(addons)
    return plugins, addons

def sync_scan_report():
    """Diagnostic report text (scan results, counts, samples)."""
    plugins, addons = sync_scan()
    def _sample(d: dict, n=5):
        keys = list(sorted(d.keys()))[:n]
        return ", ".join(keys) if keys else "—"
    lines = []
    lines.append(f"Nexa root      : {NEXA_ROOT}")
    lines.append(f"Plugins folder : {PLUGINS_DIR}")
    lines.append(f"Addons folder  : {ADDONS_DIR}")
    lines.append(f"Plugins found  : {len(plugins)}  (sample: {_sample(plugins)})")
    lines.append(f"Addons found   : {len(addons)}   (sample: {_sample(addons)})")
    return "\n".join(lines)
