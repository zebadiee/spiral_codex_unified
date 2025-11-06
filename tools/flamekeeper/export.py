import json
from datetime import datetime
from .ledger import load_ledger
from .thought import create_thought

EXPORT_FILE = "codex_export.json"

def replay_and_export(loops=2):
    ledger = load_ledger()
    thought_ids = [entry["record_id"] for entry in ledger if entry["record_id"].startswith("ƒTHOUGHT")]
    replayed = []

    for _ in range(loops):
        for tid in thought_ids:
            ledger = create_thought(ledger, [tid], replay=True)
            replayed.append(ledger[-1]["record_id"])

    with open("codex_immutable_ledger.json", "w") as f:
        json.dump(ledger, f, indent=2)

    export = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "thought_chain": thought_ids,
        "replayed": replayed,
        "last_hash": ledger[-1]["hash"] if ledger else None
    }

    with open(EXPORT_FILE, "w") as f:
        json.dump(export, f, indent=2)

    print(f"[✓] Exported replay to {EXPORT_FILE}")