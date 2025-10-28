def summary():
    return (
        "Commands:\n"
        "  r <target>           — run function / path / URL (also: r func <name>)\n"
        "  add func <name>      — add a new function (program or URL)\n"
        "  del func <name>      — delete a function\n"
        "  c func <name>        — close a running program (known entries only)\n"
        "  list                 — list Functions + Plugins + Addons\n"
        "  dev_info             — show version, creator, paths\n"
        "  nexa_tools           — theme + manage Plugins/Addons (stub/UI)\n"
        "  time, help, clear, q\n"
    )

def topic(t: str):
    t = t.lower()
    if t in ("r","run"):
        return (
            "run / r — launch a function, direct .exe path, or a URL.\n"
            "  r <function>\n  r \"C:\\Path\\to\\app.exe\"\n  r https://example.com\n"
            "Special: r func <name> — runs an ACTIVE plugin/addon entry\n"
            "Built-in: np (Notepad).\n"
        )
    if t == "list": return "list — Functions and Plugins/Addons (Active & Path)."
    if t == "dev_info": return "dev_info — shows creator, version and important folders/files."
    if t == "nexa_tools": return "nexa_tools — theme + Plugins/Addons management."
    if t == "clear": return "clear — clears the screen (and reprints greeting)."
    if t in ("q","quit","exit"): return "q — quit NexaLite."
    if t in ("add","add func"): return "add func <name> — add a program or URL function by that name."
    if t in ("del","del func"): return "del func <name> — delete a function by that name."
    if t in ("c","close"): return "c func <name> — close a known program/plugin/addon by process image."
    return "No detailed help for this topic."

