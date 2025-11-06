import json
from hashlib import sha256
from datetime import datetime

LEDGER_FILE = "codex_immutable_ledger.json"

def load_ledger():
    try:
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_ledger(ledger):
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def hash_entry(entry):
    serialized = json.dumps(entry, sort_keys=True).encode()
    return sha256(serialized).hexdigest()

def append_entry(ledger, entry, protocol):
    h = hash_entry(entry)
    prev = ledger[-1]["hash"] if ledger else "0" * 64
    ch = sha256((prev + h).encode()).hexdigest()
    record = {
        "record_type": "glyph",
        "record_id": entry["id"],
        "hash": h,
        "chain_hash": ch,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ledger_protocol": protocol
    }
    ledger.append(record)
    return ledger