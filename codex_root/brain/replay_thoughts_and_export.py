
import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path

LEDGER_FILE = "codex_immutable_ledger.json"
EXPORT_FILE = "codex_export.json"

def load_ledger():
    with open(LEDGER_FILE, "r") as f:
        return json.load(f)

def save_ledger(ledger):
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def hash_entry(entry):
    serialized = json.dumps(entry, sort_keys=True).encode()
    return sha256(serialized).hexdigest()

def replay_thoughts(ledger, loops=2):
    thought_ids = [entry["record_id"] for entry in ledger if entry["record_id"].startswith("ƒTHOUGHT")]
    replayed = []
    for loop in range(loops):
        for tid in thought_ids:
            replay = {
                "id": f"ƒTHOUGHT_{len(ledger)}",
                "name": "ReplayedThought",
                "structure_type": "Reverberation",
                "symbol_code": "~",
                "semantic_layer": "Memory",
                "function_binding": f"ƒ(x) = replay({tid})",
                "linked_glyphs": [tid],
                "archetypal_role": "Replay",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            h = hash_entry(replay)
            prev = ledger[-1]["hash"] if ledger else "0" * 64
            ch = sha256((prev + h).encode()).hexdigest()
            ledger.append({
                "record_type": "glyph",
                "record_id": replay["id"],
                "hash": h,
                "chain_hash": ch,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "ledger_protocol": "SHA-256 integrity log (thought replay)"
            })
            replayed.append(replay)
    return ledger, replayed

def export_codex(ledger, replays):
    thoughts = [entry for entry in ledger if entry["record_id"].startswith("ƒTHOUGHT")]
    export = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "thought_chain": [t["record_id"] for t in thoughts],
        "replayed": [r["id"] for r in replays],
        "last_hash": ledger[-1]["hash"] if ledger else None
    }
    with open(EXPORT_FILE, "w") as f:
        json.dump(export, f, indent=2)
    print(f"[✓] Codex exported: {EXPORT_FILE}")

if __name__ == "__main__":
    ledger = load_ledger()
    ledger, replays = replay_thoughts(ledger, loops=2)
    save_ledger(ledger)
    export_codex(ledger, replays)
