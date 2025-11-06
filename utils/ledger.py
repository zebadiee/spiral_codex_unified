# utils/ledger.py
import os, json, hashlib
from datetime import datetime
from typing import Dict, Any

LEDGER_DIR = os.getenv("LEDGER_PATH", "ledger/conversations")

def _ensure_dir():
    os.makedirs(LEDGER_DIR, exist_ok=True)

def _hash(record: Dict[str, Any]) -> str:
    blob = json.dumps(record, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()

def append(event: Dict[str, Any], session_id: str = "default") -> str:
    _ensure_dir()
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    record = {"ts": ts, **event}
    record["hash"] = _hash(record)
    path = os.path.join(LEDGER_DIR, f"{session_id}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path
