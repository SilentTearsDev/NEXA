import os, shutil, subprocess, webbrowser, sys
from pathlib import Path
from base.registry import load_all
from base.roots import NEXA_ROOT  # for resolving relative paths

def _ex(path: str):
    p = os.path.expandvars(os.path.expanduser(path))
    return p if os.path.exists(p) else None

def _which_any(cands):
    for c in cands:
        full = _ex(c)
        if full: return full
        w = shutil.which(os.path.expandvars(os.path.expanduser(c)))
        if w: return w
    return None

def _looks_url(s: str):
    s = (s or "").strip().lower()
    return s.startswith("http://") or s.startswith("https://") or s.startswith("www.")

def _normalize_url(s: str):
    s = s.strip()
    if s.lower().startswith("www."): return "https://" + s
    return s

def _open_url(url: str):
    try:
        url = _normalize_url(url)
        ok = webbrowser.open(url)
        if not ok and sys.platform.startswith("win"):
            try: os.startfile(url)
            except Exception: pass
        return True, f"✅ Opening in browser: {url}"
    except Exception as e:
        return False, f"⚠️ URL open error: {e}"

def _resolve_relative(p: str) -> str:
    """If not absolute, interpret relative to the Nexa root."""
    pp = Path(os.path.expandvars(os.path.expanduser(p)))
    if pp.is_absolute():
        return str(pp)
    return str((NEXA_ROOT / pp).resolve())

def _launch(exe: str, args: list[str]):
    try:
        subprocess.Popen([exe, *args], shell=False)
        return True, f"✅ Launching: {exe}{(' ' + ' '.join(args)) if args else ''}"
    except Exception as e:
        return False, f"⚠️ Launch error: {e}"

def _launch_builtin(entry: dict):
    # program (candidates | path) vagy url
    if entry.get("type") == "url":
        return _open_url(entry.get("url",""))

    if entry.get("type") == "program":
        cands = entry.get("candidates")
        if isinstance(cands, list) and cands:
            exe = _which_any(cands)
            if not exe: return False, "❌ Built-in executable not found."
            return _launch(exe, entry.get("args", []))
        p = entry.get("path","").strip()
        if not p:
            return False, "❌ Built-in path missing."
        abs_path = _resolve_relative(p)
        if not os.path.exists(abs_path):
            return False, f"❌ Built-in path not found: {abs_path}"
        return _launch(abs_path, entry.get("args", []))

    return False, "❌ Invalid built-in entry."

def launch_command(raw: str):
    state = load_all()
    funcs    = state["functions"]
    plugs    = state["plugins"]
    adds     = state["addons"]
    builtins = state["builtins"]

    if _looks_url(raw):
        return _open_url(raw)

    s = raw.strip()
    if s.lower().startswith("func "):
        name = s[5:].strip().lower()
        meta = plugs.get(name) or adds.get(name)
        if not meta: return False, f"❌ No such plugin/addon: {name}"
        if not meta.get("active"): return False, f"⛔ {name} is not active."
        path = meta.get("path","").strip()
        if not path: return False, "❌ Path missing."
        abs_path = _resolve_relative(path)
        if not os.path.exists(abs_path): return False, f"❌ Path not found: {abs_path}"
        return _launch(abs_path, [])

    key = s.lower()
    # user functions
    if key in funcs:
        f = funcs[key]
        if f.get("type") == "program":
            p = f.get("path","")
            abs_path = _resolve_relative(p)
            if not os.path.exists(abs_path): return False, f"❌ Not found: {abs_path}"
            return _launch(abs_path, f.get("args", []))
        if f.get("type") == "url":
            return _open_url(f.get("url",""))

    # built-ins (from editable registry)
    if key in builtins:
        return _launch_builtin(builtins[key])

    # direct exe/path
    p = _ex(key) or shutil.which(key)
    if p: return _launch(p, [])
    return False, f"❌ Unknown function or path: {raw}"

def process_image_for(name: str) -> str|None:
    """Process name suitable for taskkill"""
    from base.registry import load_all
    state = load_all()
    funcs = state["functions"]; plugs = state["plugins"]; adds = state["addons"]; builtins = state["builtins"]
    k = name.strip().lower()
    if k.startswith("func "): k = k[5:].strip().lower()
    if k in funcs and funcs[k].get("type") == "program":
        from os.path import basename
        return basename(_resolve_relative(funcs[k].get("path",""))).lower()
    if k in builtins:
        b = builtins[k]
        if b.get("process_name"): return b["process_name"].lower()
        # derive from candidates/path
        cand = None
        if b.get("candidates"): cand = b["candidates"][0]
        elif b.get("path"): cand = _resolve_relative(b["path"])
        if cand:
            from os.path import basename
            return basename(os.path.expandvars(cand)).lower()
    m = plugs.get(k) or adds.get(k)
    if m and m.get("path"):
        from os.path import basename
        return basename(_resolve_relative(m["path"])).lower()
    return None
