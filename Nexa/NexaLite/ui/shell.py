import tkinter as tk
from tkinter import messagebox, filedialog
from app_config import APP_TITLE, DEFAULT_BG, DEFAULT_FG, DEFAULT_ENTRY_BG
from base.storage import PATHS
from base.registry import (
    load_all, save_functions, save_settings, save_plugins, save_addons, save_builtins
)
from base.discover import sync_scan
from commands.router import handle_command
from ui.tools import ToolsDialog


class NexaShell(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)

    # prepare data file paths
        PATHS.ensure()
        PATHS.load_bootstrap()

    # load state
        self.state = load_all()
        self.functions = self.state["functions"]
        self.settings  = self.state["settings"]
        self.plugins   = self.state["plugins"]
        self.addons    = self.state["addons"]
        self.builtins  = self.state["builtins"]

    # --- automatic plugin/addon scan (in Nexa root) ---
        self.plugins, self.addons = sync_scan()

        # UI
        self.geometry("900x560")
        self.output = tk.Text(self, wrap="word", state="disabled", font=("Consolas", 12))
        self.output.pack(fill="both", expand=True, padx=10, pady=(10, 8))

        bottom = tk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.prompt = tk.Label(bottom, text="›", width=2)
        self.prompt.pack(side="left")

        self.entry = tk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)

        self.apply_theme(self.settings.get("bg", DEFAULT_BG), self.settings.get("fg", DEFAULT_FG))
        self._greet()
        self.entry.focus_set()

    # ---------- theming ----------
    def apply_theme(self, bg, fg):
        if not bg: bg = DEFAULT_BG
        if not fg: fg = DEFAULT_FG
        if bg == fg:
            bg, fg = DEFAULT_BG, DEFAULT_FG

        def darker(hx, f=0.25):
            h = hx.lstrip('#')
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
            r = max(0, int(r * (1 - f)))
            g = max(0, int(g * (1 - f)))
            b = max(0, int(b * (1 - f)))
            return f"#{r:02x}{g:02x}{b:02x}"

        entry_bg = darker(bg, 0.25) if bg else DEFAULT_ENTRY_BG
        self.configure(bg=bg)
        self.output.configure(bg=bg, fg=fg, insertbackground=fg)
        self.prompt.configure(bg=bg, fg=fg)
        self.entry.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        self.settings["bg"] = bg
        self.settings["fg"] = fg

    # ---------- greet / print ----------
    def _greet(self):
        self._print("Hello! 👋 I'm Nexa — your local PC assistant.")
        self._print("Type 'help' anytime for a quick list of commands.")

    def _print(self, text=""):
        self.output.configure(state="normal")
        self.output.insert("end", text + ("\n" if not text.endswith("\n") else ""))
        self.output.see("end")
        self.output.configure(state="disabled")

    # ---------- input handling ----------
    def on_enter(self, _=None):
        cmdline = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not cmdline:
            return
        self._print(f"» {cmdline}")
        handle_command(
            raw=cmdline,
            print_fn=self._ui_print_hook,
            open_tools_fn=self._open_tools_dialog,   # real Tools dialog
            add_func_dialog_fn=self._add_func_dialog, # with Browse button
            add_builtin_dialog_fn=self._add_builtin_dialog,  # DEV TOOL ONLY
        )

    def _ui_print_hook(self, msg: str):
        if msg == "__CLEAR__":
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.configure(state="disabled")
            self._greet()
            return
        if msg == "__QUIT__":
            self._print("Bye.")
            self.after(150, self.destroy)
            return
        self._print(msg)

    # ---------- Tools (plugins/addons + theme) ----------
    def _open_tools_dialog(self):
        dlg = ToolsDialog(
            master=self,
            bg=self.settings.get("bg", DEFAULT_BG),
            fg=self.settings.get("fg", DEFAULT_FG),
            plugins=self.plugins,
            addons=self.addons,
            on_save=self._on_tools_save
        )
        self.wait_window(dlg)

    def _on_tools_save(self, data):
        # theme
        bg, fg = data["bg"], data["fg"]
        if bg == fg:
            bg, fg = DEFAULT_BG, DEFAULT_FG
        self.apply_theme(bg, fg)
        save_settings({"bg": bg, "fg": fg})

        # registries
        self.plugins = dict(data["plugins"])
        self.addons  = dict(data["addons"])
        save_plugins(self.plugins)
        save_addons(self.addons)

        self._print("✅ Settings saved. Plugins/Addons updated.")

    # ---------- Add function dialog (with Browse support) ----------
    def _add_func_dialog(self, fname: str):
        win = tk.Toplevel(self)
        win.title(f"Add function — {fname}")
        win.resizable(False, False)

        tk.Label(win, text="Type:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        vtype = tk.StringVar(value="program")
        tk.OptionMenu(win, vtype, "program", "url").grid(row=0, column=1, padx=6, pady=6, sticky="we")

        tk.Label(win, text="Path or URL:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        val = tk.Entry(win, width=44)
        val.grid(row=1, column=1, padx=6, pady=6, sticky="we")

        def browse():
            if vtype.get() == "program":
                f = filedialog.askopenfilename(
                    title="Select executable",
                    filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
                )
                if f:
                    val.delete(0, "end")
                    val.insert(0, f)
            else:
                messagebox.showinfo("Info", "Browse is available only for 'program' type.")

        tk.Button(win, text="Browse…", command=browse).grid(row=1, column=2, padx=6, pady=6)

        def save():
            t = vtype.get()
            s = val.get().strip()
            if not s:
                messagebox.showerror("Error", "Value required.")
                return
            if t == "program":
                self.functions[fname] = {"type": "program", "path": s, "args": []}
            else:
                self.functions[fname] = {"type": "url", "url": s}
            save_functions(self.functions)
            self._print(f"✅ Saved function: {fname}")
            win.destroy()

        tk.Button(win, text="Cancel", command=win.destroy).grid(row=2, column=0, padx=6, pady=8)
        tk.Button(win, text="Save", command=save).grid(row=2, column=2, padx=6, pady=8, sticky="e")
        win.grab_set()

    # ---------- Add built-in dialog (DEV TOOL ONLY) ----------
    def _add_builtin_dialog(self, name: str):
        win = tk.Toplevel(self)
        win.title(f"Add built-in — {name}")
        win.resizable(False, False)

        tk.Label(win, text="Type:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        vtype = tk.StringVar(value="program")
        tk.OptionMenu(win, vtype, "program", "url").grid(row=0, column=1, padx=6, pady=6, sticky="we")

    # PROGRAM fields
        tk.Label(win, text="Program path:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        ent_path = tk.Entry(win, width=44)
        ent_path.grid(row=1, column=1, padx=6, pady=6, sticky="we")
        tk.Button(win, text="Browse…", command=lambda: self._browse_into(ent_path)).grid(row=1, column=2, padx=6, pady=6)

    # new name + tip (instead of process image)
        tk.Label(win, text="Function name (optional):").grid(row=2, column=0, padx=6, pady=6, sticky="e")
        ent_proc = tk.Entry(win, width=44)
        ent_proc.grid(row=2, column=1, padx=6, pady=(6, 2), sticky="we")

        tip = tk.Label(
            win,
            text="Used by 'c func <name>' to close the program (e.g. notepad.exe). Leave blank to auto-detect.",
            fg="#7f8fa6", font=("Segoe UI", 8), justify="left", wraplength=340
        )
        tip.grid(row=3, column=1, columnspan=2, sticky="w", padx=6, pady=(0, 8))

    # URL field
        tk.Label(win, text="URL:").grid(row=4, column=0, padx=6, pady=6, sticky="e")
        ent_url = tk.Entry(win, width=44)
        ent_url.grid(row=4, column=1, padx=6, pady=6, sticky="we")

        def save():
            t = vtype.get()
            built = dict(self.builtins)
            if t == "program":
                p = ent_path.get().strip()
                if not p:
                    messagebox.showerror("Error", "Program path required.")
                    return
                proc = ent_proc.get().strip() or None
                if not proc:
                    import os
                    proc = os.path.basename(p)
                built[name] = {"type": "program", "path": p, "args": [], "process_name": proc}
            else:
                u = ent_url.get().strip()
                if not u:
                    messagebox.showerror("Error", "URL required.")
                    return
                built[name] = {"type": "url", "url": u}
            save_builtins(built)
            self.builtins = built
            self._print(f"✅ Saved built-in: {name}")
            win.destroy()

        tk.Button(win, text="Cancel", command=win.destroy).grid(row=99, column=0, padx=6, pady=8)
        tk.Button(win, text="Save", command=save).grid(row=99, column=2, padx=6, pady=8, sticky="e")
        win.grab_set()

    def _browse_into(self, entry: tk.Entry):
        f = filedialog.askopenfilename(
            title="Select executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if f:
            entry.delete(0, "end")
            entry.insert(0, f)

