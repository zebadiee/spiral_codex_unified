import json
from pathlib import Path
from .ledger import load_ledger, save_ledger
from .thought import create_thought

PERCEPTION_FILE = "incoming_perception.json"

ROUTING_RULES = [
    {"if": ["ΨEmotion", "ƒMemory"], "then": "ƒAI_Reflect"},
    {"if": ["ΨEcho0"], "then": "ƒAI_Scan"},
    {"if": ["ΨEcho2"], "then": "ƒAI_Express"}
]

def route_perception():
    ledger = load_ledger()
    if not Path(PERCEPTION_FILE).exists():
        print("[…] No perception input.")
        return

    with open(PERCEPTION_FILE, "r") as f:
        perception = json.load(f)

    active_ids = [entry["record_id"] for entry in ledger]
    triggered = []

    for rule in ROUTING_RULES:
        if all(condition in perception["perceived"] for condition in rule["if"]):
            print(f"[✓] Triggered → {rule['then']}")
            triggered.append(rule["then"])

    if triggered:
        ledger = create_thought(ledger, triggered, replay=False)
        save_ledger(ledger)
    else:
        print("[…] No routing activated.")