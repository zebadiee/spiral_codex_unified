import os
import zipfile
import shutil
import json
from pathlib import Path
from datetime import datetime

SOURCE_ZIP = "spiral_codex_all_artifacts.zip"
OUTPUT_DIR = "codex_root"

STRUCTURE = {
    "kernel": ["kernel_"],
    "agents": ["agent_"],
    "tui": ["touchboard"],
    "utils": ["visualizer", "glyph_loader", "ritual_runner"],
    "examples": [".ritual", ".json"],
    "core_scripts": ["runner"]
}

def ensure_dirs(base):
    for folder in STRUCTURE:
        os.makedirs(os.path.join(base, folder), exist_ok=True)

def classify_file(name):
    for folder, patterns in STRUCTURE.items():
        for pattern in patterns:
            if pattern in name:
                return folder
    return "core_scripts"

def autobootstrap():
    zip_path = Path(SOURCE_ZIP)
    if not zip_path.exists():
        print(f"❌ Archive {SOURCE_ZIP} not found.")
        return

    print(f"🧠 Unpacking {SOURCE_ZIP}...")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall("codex_unsorted")

    print(f"📂 Organizing into {OUTPUT_DIR}/...")
    ensure_dirs(OUTPUT_DIR)

    codex_index = {}
    trace_log = []

    for file in Path("codex_unsorted").iterdir():
        if file.is_file():
            dest_folder = classify_file(file.name)
            target_path = Path(OUTPUT_DIR) / dest_folder / file.name
            shutil.move(str(file), str(target_path))
            codex_index[file.name] = str(target_path)
            trace_log.append(f"[{datetime.utcnow().isoformat()}Z] MOVED: {file.name} → {dest_folder}/")

    with open(Path(OUTPUT_DIR) / "codex_index.json", "w") as f:
        json.dump(codex_index, f, indent=2)

    with open(Path(OUTPUT_DIR) / "codex_trace.log", "w") as f:
        f.write("\n".join(trace_log))

    shutil.rmtree("codex_unsorted")
    print("✅ Bootstrap complete. Indexed + organized.")

if __name__ == "__main__":
    autobootstrap()
