
import time
import os
import hashlib
from subprocess import run

LEDGER_FILE = "codex_immutable_ledger.json"
RENDER_SCRIPT = "generate_symbolic_brain_map_v2.py"
CHECK_INTERVAL = 3  # seconds

def file_hash(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def watch_file(filepath, on_change):
    last_hash = file_hash(filepath)
    while True:
        time.sleep(CHECK_INTERVAL)
        new_hash = file_hash(filepath)
        if new_hash != last_hash:
            print("[Update Detected] Ledger changed, re-rendering brain map...")
            on_change()
            last_hash = new_hash

def regenerate():
    result = run(["python3", RENDER_SCRIPT])
    if result.returncode == 0:
        print("[✓] Brain map updated.")
    else:
        print("[✗] Error during brain map generation.")

if __name__ == "__main__":
    if not os.path.exists(LEDGER_FILE):
        print("Ledger file not found. Waiting for it to appear...")
    print("Watching ledger for changes...")
    watch_file(LEDGER_FILE, regenerate)
