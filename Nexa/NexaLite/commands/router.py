import shlex
from datetime import datetime

from commands.helptext import summary, topic
from base.registry import load_all, save_functions, save_builtins
from base.run import launch_command
from base.close import close_command
from base.storage import PATHS
from base.discover import sync_scan_report

# Developer tool state (runtime only; not persisted)
DEV_MODE = False


def _print_dev_menu(print_fn):
    """List hidden developer options and usage."""
    print_fn("")
    print_fn("🔧 Developer Tool — Hidden features")
    print_fn("-----------------------------------")
    print_fn("• Factory reset:")
    print_fn("    nexa_reset")
    print_fn("    → Deletes ALL NexaLite data (functions/settings/plugins/addons/builtins) and restores defaults.")
    print_fn("")
    print_fn("• Edit built-ins (add/remove built-in shortcuts):")
    print_fn("    add builtin <name>")
    print_fn("    del builtin <name>")
    print_fn("    → Create URL/program built-ins or remove existing ones (even 'np' if you want).")
    print_fn("")
    print_fn("• Extra tools:")
    print_fn("    scan")
    print_fn("    → Force-rescan plugins/addons in the Nexa root and print a short report.")
    print_fn("")
    print_fn("Tip: disable dev mode any time with:  dev_tool disable")
    print_fn("")


def handle_command(raw: str, print_fn, open_tools_fn=None, add_func_dialog_fn=None, add_builtin_dialog_fn=None):
    """
    Route a single command line and print responses through print_fn().
    UI-specific callbacks:
      - open_tools_fn(): opens Nexa Tools dialog
      - add_func_dialog_fn(name): opens Add Function dialog
      - add_builtin_dialog_fn(name): opens Add Built-in dialog (dev only)
    """
    global DEV_MODE

    parts = shlex.split(raw)
    if not parts:
        return
    cmd, *args = parts
    low = cmd.lower()

    # ---------- Developer Tool toggle / status ----------
    if low in ("dev_t", "dev_tool"):
        if not args:
            print_fn(f"Developer Tool is currently: {'ENABLED' if DEV_MODE else 'disabled'}")
            if DEV_MODE:
                _print_dev_menu(print_fn)
            else:
                print_fn("Enable it with:  dev_tool enable")
            return

        sub = args[0].lower()
        if sub == "enable":
            DEV_MODE = True
            print_fn("🔧 Developer Tool enabled. Hidden functions are now accessible.")
            _print_dev_menu(print_fn)
        elif sub == "disable":
            DEV_MODE = False
            print_fn("Developer Tool disabled.")
        else:
            print_fn("Usage: dev_tool enable | disable")
        return

    # ---------- Hidden developer-only: nexa_reset ----------
    if low == "nexa_reset":
        if not DEV_MODE:
            print_fn("⚠️ Access denied. Enable Developer Tool first: `dev_tool enable`.")
            return
        # delete all saved JSONs (factory reset)
        for p in [PATHS.functions, PATHS.settings, PATHS.plugins, PATHS.addons, PATHS.builtins, PATHS.bootstrap]:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass
        print_fn("🧨 All Nexa data deleted. NexaLite will recreate defaults on next launch.")
        return

    # ---------- Built-ins edit (dev only) ----------
    if low == "add" and len(args) >= 2 and args[0].lower() == "builtin":
        if not DEV_MODE:
            print_fn("⚠️ Developer Tool required. Use `dev_tool enable` first.")
            return
        name = args[1].lower()
        if not add_builtin_dialog_fn:
            print_fn("Add builtin dialog not available in this UI.")
            return
        add_builtin_dialog_fn(name)
        return

    if low == "del" and len(args) >= 2 and args[0].lower() == "builtin":
        if not DEV_MODE:
            print_fn("⚠️ Developer Tool required. Use `dev_tool enable` first.")
            return
        state = load_all()
        builtins = dict(state["builtins"])
        name = args[1].lower()
        if name in builtins:
            builtins.pop(name)
            save_builtins(builtins)
            print_fn(f"🗑️ Deleted built-in: {name}")
        else:
            print_fn("No such built-in.")
        return

    # ---------- Force rescan (plugins/addons) ----------
    if low == "scan":
        report = sync_scan_report()  # prints paths + counts
        print_fn("🔎 Rescan complete:\n" + report)
        return

    # ---------- Standard commands ----------
    if low in ("r", "run"):
        if not args:
            print_fn("What should I run? (function, func <name>, .exe path, or URL)")
        else:
            ok, msg = launch_command(" ".join(args))
            print_fn(msg)
        return

    if low == "add" and len(args) >= 2 and args[0].lower() == "func":
        fname = args[1].lower()
        if not add_func_dialog_fn:
            print_fn("Add func dialog not available in this UI.")
            return
        add_func_dialog_fn(fname)
        return

    if low == "del" and len(args) >= 2 and args[0].lower() == "func":
        state = load_all()
        funcs = dict(state["functions"])
        fname = args[1].lower()
        if fname in funcs:
            funcs.pop(fname)
            save_functions(funcs)
            print_fn(f"🗑️ Deleted function: {fname}")
        else:
            print_fn("No such function.")
        return

    if (low in ("c", "close")) and len(args) >= 2 and args[0].lower() == "func":
        ok, msg = close_command(" ".join(args))
        print_fn(msg)
        return

    if low == "list":
        state = load_all()
        # Built-ins
        print_fn("Built-in shortcuts:")
        if not state["builtins"]:
            print_fn("  —")
        else:
            for k, v in sorted(state["builtins"].items()):
                if v.get("type") == "program":
                    src = v.get("path") or "candidates"
                    print_fn(f"  - {k} (program) -> {src}")
                elif v.get("type") == "url":
                    print_fn(f"  - {k} (url) -> {v.get('url')}")
        # User functions
        print_fn("Your Functions:")
        if not state["functions"]:
            print_fn("  —")
        else:
            for k in sorted(state["functions"].keys()):
                v = state["functions"][k]
                if v.get("type") == "program":
                    print_fn(f"  - {k} (program) -> {v.get('path')} {' '.join(v.get('args', []))}")
                elif v.get("type") == "url":
                    print_fn(f"  - {k} (url) -> {v.get('url')}")
        # Plugins / Addons
        print_fn("Plugins (r func <name>):")
        if not state["plugins"]:
            print_fn("  —")
        else:
            for name, info in sorted(state["plugins"].items()):
                print_fn(f"  - {name}  [active: {'yes' if info.get('active') else 'no'}] -> {info.get('path','')}")
        print_fn("Addons (r func <name>):")
        if not state["addons"]:
            print_fn("  —")
        else:
            for name, info in sorted(state["addons"].items()):
                print_fn(f"  - {name}  [active: {'yes' if info.get('active') else 'no'}] -> {info.get('path','')}")
        if DEV_MODE:
            print_fn("")
            print_fn("Developer-only commands available:")
            print_fn("  - nexa_reset")
            print_fn("  - add builtin <name>")
            print_fn("  - del builtin <name>")
            print_fn("  - scan")
        return

    if low == "dev_info":
        from app_config import VERSION, CREATOR
        from base.roots import NEXALITE_DIR, NEXA_ROOT, PLUGINS_DIR, ADDONS_DIR
        print_fn("NexaLite — development info")
        print_fn("---------------------------")
        print_fn(f"Version : {VERSION}")
        print_fn(f"Creator : {CREATOR}")
        print_fn(f"Nexa root     : {NEXA_ROOT}")
        print_fn(f"NexaLite dir  : {NEXALITE_DIR}")
        print_fn(f"Plugins dir   : {PLUGINS_DIR}")
        print_fn(f"Addons dir    : {ADDONS_DIR}")
        print_fn(f"Data dir      : {PATHS.data_dir}")
        print_fn(f"Bootstrap file: {PATHS.bootstrap}")
        print_fn(f"Functions file: {PATHS.functions}")
        print_fn(f"Settings file : {PATHS.settings}")
        print_fn(f"Plugins file  : {PATHS.plugins}")
        print_fn(f"Addons file   : {PATHS.addons}")
        try:
            print_fn(f"Builtins file : {PATHS.builtins}")
        except Exception:
            pass
        print_fn(f"Developer Tool: {'ENABLED' if DEV_MODE else 'disabled'}")
        if DEV_MODE:
            _print_dev_menu(print_fn)
        return

    if low in ("nexa_tools", "tools"):
        if open_tools_fn:
            open_tools_fn()
        else:
            print_fn("nexa_tools UI not wired yet (stub).")
        return

    if low == "time":
        now = datetime.now()
        print_fn(now.strftime("%Y-%m-%d %H:%M:%S"))
        return

    if low == "help":
        print_fn(topic(args[0]) if args else summary())
        return

    if low == "clear":
        print_fn("__CLEAR__")
        return

    if low in ("q", "quit", "exit"):
        print_fn("__QUIT__")
        return

    # ---------- speech layer fallback ----------
    from speech.intents import respond
    ans = respond(raw)
    if ans:
        print_fn(ans)
    else:
        print_fn("I didn't get that. Try `help`, `help r`, or `dev_tool enable` for hidden options.")
