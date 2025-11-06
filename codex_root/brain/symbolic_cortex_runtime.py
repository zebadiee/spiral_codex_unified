
import json
from hashlib import sha256
from datetime import datetime
from pathlib import Path

LEDGER_FILE = "codex_immutable_ledger.json"
PERCEPTION_FILE = "incoming_perception.json"

# Simulated routing rules for decision modeling
ROUTING_RULES = [
    {"if": ["ΨEmotion", "ƒMemory"], "then": "ƒAI_Reflect"},
    {"if": ["ΨEcho0"], "then": "ƒAI_Scan"},
    {"if": ["ΨEcho2"], "then": "ƒAI_Express"}
]

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

def append_thought(ledger, decision_trace):
    thought = {
        "id": f"ƒTHOUGHT_{len(ledger)}",
        "name": "ThoughtTrace",
        "structure_type": "CognitiveLink",
        "symbol_code": "*",
        "semantic_layer": "Decision",
        "function_binding": "ƒ(x) = routed()",
        "linked_glyphs": decision_trace,
        "archetypal_role": "Reflex",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    thought_hash = hash_entry(thought)
    previous_hash = ledger[-1]["hash"] if ledger else "0" * 64
    chain_input = (previous_hash + thought_hash).encode()
    chain_hash = sha256(chain_input).hexdigest()

    ledger.append({
        "record_type": "glyph",
        "record_id": thought["id"],
        "hash": thought_hash,
        "chain_hash": chain_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ledger_protocol": "SHA-256 integrity log (decision trace)"
    })

    print(f"[+] Thought appended: {thought['id']}")
    return ledger

def route_perception(perception, ledger):
    active_glyphs = [entry.get("record_id") for entry in ledger]
    matched = []

    for rule in ROUTING_RULES:
        if all(trigger in active_glyphs for trigger in rule["if"]):
            target = rule["then"]
            print(f"[✓] Rule triggered → {target}")
            matched.append(target)

    if matched:
        ledger = append_thought(ledger, matched)
        save_ledger(ledger)
    else:
        print("[…] No decision rule matched perception.")

if __name__ == "__main__":
    print("Symbolic Cortex Runtime Engaged.")
    ledger = load_ledger()

    if not Path(PERCEPTION_FILE).exists():
        print("Waiting for perception input...")
    else:
        with open(PERCEPTION_FILE, "r") as f:
            perception = json.load(f)
        route_perception(perception, ledger)
