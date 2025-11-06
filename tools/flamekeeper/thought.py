from datetime import datetime
from .ledger import hash_entry, append_entry

def create_thought(ledger, trace_ids, replay=False):
    replay_mode = "Replay" if replay else "Reflex"
    structure = "Reverberation" if replay else "CognitiveLink"
    thought = {
        "id": f"ƒTHOUGHT_{len(ledger)}",
        "name": "ReplayedThought" if replay else "ThoughtTrace",
        "structure_type": structure,
        "symbol_code": "*" if not replay else "~",
        "semantic_layer": "Memory" if replay else "Decision",
        "function_binding": f"ƒ(x) = {'replay' if replay else 'routed'}({','.join(trace_ids)})",
        "linked_glyphs": trace_ids,
        "archetypal_role": replay_mode,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    return append_entry(ledger, thought, f"SHA-256 integrity log ({replay_mode.lower()})")