import os, json
from pathlib import Path

HOME = Path(os.path.expandvars(r"%USERPROFILE%"))
DEFAULT_DATA_DIR = HOME / "Documents" / "NexaLite"

class Paths:
    def __init__(self):
        self.data_dir      = DEFAULT_DATA_DIR
        self.bootstrap     = self.data_dir / "bootstrap.json"
        self.functions     = self.data_dir / "functions.json"
        self.settings      = self.data_dir / "settings.json"
        self.plugins       = self.data_dir / "plugins.json"
        self.addons        = self.data_dir / "addons.json"
    self.builtins      = self.data_dir / "builtins.json"   # <-- NEW
    self.devstate      = self.data_dir / "dev_state.json"  # (optional, for dev saves)

    def ensure(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.bootstrap.exists():
            self.bootstrap.write_text(json.dumps({"data_dir": str(self.data_dir)}, indent=2), encoding="utf-8")

    def load_bootstrap(self):
        if self.bootstrap.exists():
            try:
                obj = json.loads(self.bootstrap.read_text(encoding="utf-8"))
                dd = obj.get("data_dir")
                if dd:
                    self.set_data_dir(Path(dd))
            except Exception:
                pass

    def set_data_dir(self, p: Path):
        self.data_dir = p
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bootstrap = self.data_dir / "bootstrap.json"
        self.functions = self.data_dir / "functions.json"
        self.settings  = self.data_dir / "settings.json"
        self.plugins   = self.data_dir / "plugins.json"
        self.addons    = self.data_dir / "addons.json"
        self.builtins  = self.data_dir / "builtins.json"
        self.devstate  = self.data_dir / "dev_state.json"
        self.bootstrap.write_text(json.dumps({"data_dir": str(self.data_dir)}, indent=2), encoding="utf-8")

PATHS = Paths()
