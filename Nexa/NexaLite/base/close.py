import subprocess
from base.run import process_image_for

def close_command(name: str):
    proc = process_image_for(name)
    if not proc:
        return False, "❌ I only close known program-type entries (np, your program funcs, active plugins/addons)."
    try:
        res = subprocess.run(["taskkill", "/IM", proc, "/T", "/F"], capture_output=True, text=True, shell=False)
        if res.returncode == 0:
            return True, f"🛑 Closed: {proc}"
        return False, f"⚠️ Could not close {proc}. {res.stderr.strip() or res.stdout.strip()}"
    except Exception as e:
        return False, f"⚠️ Close error: {e}"
