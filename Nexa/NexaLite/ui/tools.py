# ui/tools.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path

from app_config import DEFAULT_BG, DEFAULT_FG
from base.roots import NEXA_ROOT
from base.discover import sync_scan


def _rel_to_root(p: Path) -> str:
    """Try to store paths relative to Nexa root; fallback to absolute."""
    try:
        return str(p.resolve().relative_to(NEXA_ROOT.resolve()))
    except Exception:
        return str(p.resolve())


def _unique_name(base: str, existing: dict) -> str:
    """Make a unique key name (lowercase) inside a dict."""
    name = base.lower()
    if name not in existing:
        return name
    i = 2
    while f"{name}-{i}" in existing:
        i += 1
    return f"{name}-{i}"


class ToolsDialog(tk.Toplevel):
    """
    Nexa_tools — Theme + Plugins/Addons manager
    on_save: callback({"bg":hex, "fg":hex, "plugins":dict, "addons":dict})
    """
    def __init__(self, master, bg, fg, plugins: dict, addons: dict, on_save):
        super().__init__(master)
        self.title("Nexa_tools — appearance & storage")
        self.geometry("820x520")
        self.configure(bg=bg)

        self.on_save = on_save
        self.bg_var = tk.StringVar(value=bg or DEFAULT_BG)
        self.fg_var = tk.StringVar(value=fg or DEFAULT_FG)

        # work copies (do NOT mutate caller dicts until Save)
        self.plugins = {k: dict(v) for k, v in (plugins or {}).items()}
        self.addons  = {k: dict(v) for k, v in (addons  or {}).items()}

        # notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.plug_tab = tk.Frame(nb, bg=bg)
        self.add_tab  = tk.Frame(nb, bg=bg)
        self.theme_tab = tk.Frame(nb, bg=bg)

        nb.add(self.plug_tab, text="Plugins")
        nb.add(self.add_tab,  text="Addons")
        nb.add(self.theme_tab, text="Theme")

        # build tabs
        self._build_table_tab(self.plug_tab, is_plugins=True)
        self._build_table_tab(self.add_tab,  is_plugins=False)
        self._build_theme_tab(self.theme_tab)

        # bottom buttons
        btns = tk.Frame(self, bg=bg)
        btns.pack(fill="x", padx=10, pady=(0,10))
        tk.Button(btns, text="Cancel", command=self._cancel).pack(side="right", padx=(6,0))
        tk.Button(btns, text="Save",   command=self._save_all).pack(side="right", padx=(6,0))

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    # ---------- UI builders ----------
    def _build_table_tab(self, tab: tk.Frame, is_plugins: bool):
        bg = self.bg_var.get()
        fg = self.fg_var.get()

        header = tk.Frame(tab, bg=bg)
        header.pack(fill="x", padx=6, pady=(8,4))

        lbl = tk.Label(header, text="Double-click 'Active' to toggle. Use Add/Browse/Remove/Rescan below.",
                       bg=bg, fg=fg)
        lbl.pack(side="left")

        tree = ttk.Treeview(tab, columns=("active","path"), show="headings", height=15)
        tree.pack(fill="both", expand=True, padx=6, pady=6)
        tree.heading("active", text="Active")
        tree.heading("path", text="Path (relative to Nexa)")
        tree.column("active", width=80, anchor="center")
        tree.column("path", width=600, anchor="w")

        # fill with current
        data_ref = self.plugins if is_plugins else self.addons
        self._refresh_tree(tree, data_ref)

        # dblclick to toggle Active on that row
        def on_double(event):
            item = tree.identify_row(event.y)
            if not item:
                return
            name = tree.set(item, "path")  # we don't have name in columns; store name in iid instead
        tree.bind("<Double-1>", lambda e: self._toggle_active_on_click(e, tree, data_ref))

        # buttons
        controls = tk.Frame(tab, bg=bg)
        controls.pack(fill="x", padx=6, pady=(0,10))

        tk.Button(controls, text="Add…", command=lambda: self._add_entry(tree, data_ref)).pack(side="left", padx=(0,6))
        tk.Button(controls, text="Browse…", command=lambda: self._browse_set(tree, data_ref)).pack(side="left", padx=(0,6))
        tk.Button(controls, text="Remove", command=lambda: self._remove_selected(tree, data_ref)).pack(side="left", padx=(0,6))
        tk.Button(controls, text="Rescan", command=lambda: self._rescan_into(tree, data_ref, is_plugins)).pack(side="left", padx=(0,6))

        # store refs
        if is_plugins:
            self.plugins_tree = tree
            self.plugins_controls = controls
        else:
            self.addons_tree = tree
            self.addons_controls = controls

    def _build_theme_tab(self, tab: tk.Frame):
        bg = self.bg_var.get()
        fg = self.fg_var.get()

        pad = {"padx": 10, "pady": 6}
        tk.Label(tab, text="Window background:", bg=bg, fg=fg).grid(row=0, column=0, sticky="w", **pad)
        ent_bg = tk.Entry(tab, width=28, textvariable=self.bg_var)
        ent_bg.grid(row=0, column=1, sticky="w", **pad)
        tk.Button(tab, text="Pick…", command=self._pick_bg).grid(row=0, column=2, sticky="w", **pad)

        tk.Label(tab, text="Text color:", bg=bg, fg=fg).grid(row=1, column=0, sticky="w", **pad)
        ent_fg = tk.Entry(tab, width=28, textvariable=self.fg_var)
        ent_fg.grid(row=1, column=1, sticky="w", **pad)
        tk.Button(tab, text="Pick…", command=self._pick_fg).grid(row=1, column=2, sticky="w", **pad)

        tk.Button(tab, text="Reset to defaults", command=self._reset_theme).grid(row=2, column=1, sticky="w", **pad)

    # ---------- theme handlers ----------
    def _pick_bg(self):
        color = colorchooser.askcolor(title="Pick background", color=self.bg_var.get())[1]
        if color:
            self.bg_var.set(color)

    def _pick_fg(self):
        color = colorchooser.askcolor(title="Pick text color", color=self.fg_var.get())[1]
        if color:
            self.fg_var.set(color)

    def _reset_theme(self):
        self.bg_var.set(DEFAULT_BG)
        self.fg_var.set(DEFAULT_FG)

    # ---------- tree helpers ----------
    def _refresh_tree(self, tree: ttk.Treeview, data_ref: dict):
        tree.delete(*tree.get_children())
        for name in sorted(data_ref.keys()):
            info = data_ref[name]
            active = "yes" if info.get("active") else "no"
            path = info.get("path","")
            tree.insert("", "end", iid=name, values=(active, path))

    def _toggle_active_on_click(self, event, tree: ttk.Treeview, data_ref: dict):
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        info = data_ref.get(item_id)
        if not info:
            return
        info["active"] = not bool(info.get("active"))
        # reflect immediately
        tree.set(item_id, "active", "yes" if info["active"] else "no")

    # ---------- actions ----------
    def _add_entry(self, tree: ttk.Treeview, data_ref: dict):
        f = filedialog.askopenfilename(
            title="Select executable",
            filetypes=[("Executables", "*.exe;*.bat;*.cmd"), ("All files", "*.*")]
        )
        if not f:
            return
        p = Path(f)
        base = p.stem.lower()
        name = _unique_name(base, data_ref)
        data_ref[name] = {"active": True, "path": _rel_to_root(p)}
        # show instantly
        tree.insert("", "end", iid=name, values=("yes", data_ref[name]["path"]))

    def _browse_set(self, tree: ttk.Treeview, d: dict):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Browse", "Select a row first.")
            return
        item_id = sel[0]
        f = filedialog.askopenfilename(
            title="Select executable",
            filetypes=[("Executables", "*.exe;*.bat;*.cmd"), ("All files", "*.*")]
        )
        if not f:
            return
        p = Path(f)
        d[item_id]["path"] = _rel_to_root(p)
        tree.set(item_id, "path", d[item_id]["path"])

    def _remove_selected(self, tree: ttk.Treeview, d: dict):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Remove", "Select a row first.")
            return
        name = sel[0]
        if name in d:
            del d[name]
        tree.delete(name)

    def _rescan_into(self, tree: ttk.Treeview, d: dict, is_plugins: bool):
        # ask discover to scan the filesystem; get merged dicts back at app-level too
        plugins, addons = sync_scan()
        auto = plugins if is_plugins else addons
        # merge: keep existing, add only new keys
        added = 0
        for k, v in auto.items():
            if k not in d:
                d[k] = dict(v)
                added += 1
        # refresh UI
        self._refresh_tree(tree, d)
        messagebox.showinfo("Rescan", f"Scan complete.\nNew entries added: {added}")

    # ---------- save / cancel ----------
    def _save_all(self):
        # protect identical colors
        bg = self.bg_var.get() or DEFAULT_BG
        fg = self.fg_var.get() or DEFAULT_FG
        if bg == fg:
            bg, fg = DEFAULT_BG, DEFAULT_FG
            messagebox.showwarning("Theme", "Background and text colors were identical. Reset to defaults.")

        if callable(self.on_save):
            self.on_save({
                "bg": bg,
                "fg": fg,
                "plugins": self.plugins,
                "addons":  self.addons
            })
        self.destroy()

    def _cancel(self):
        self.destroy()
