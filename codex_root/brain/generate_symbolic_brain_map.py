
import json
from hashlib import sha256
from graphviz import Digraph
from pathlib import Path

LEDGER_FILE = "codex_immutable_ledger.json"
OUTPUT_FILE = "symbolic_brain_map"

def load_ledger():
    try:
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def hash_label(hash_val):
    return hash_val[:8] + "..."

def build_brain_map(ledger):
    dot = Digraph(comment="Symbolic Brain Map")
    dot.attr(rankdir='LR', fontname="Courier", fontsize="10")

    # Left Brain - Logical Glyphs
    for i, entry in enumerate(ledger):
        lid = f"L{i}"
        label = entry.get("record_id", f"ƒ{i}")
        h = entry.get("hash", "")[:8] + "..."
        dot.node(lid, f"{label}\n{h}", shape="box", style="filled", fillcolor="lightblue")

    # Right Brain - Abstract Patterns
    for i, entry in enumerate(ledger):
        rid = f"R{i}"
        label = f"ΨEcho{i}"
        role = entry.get("archetypal_role", "Abstract")
        dot.node(rid, f"{label}\n{role}", shape="ellipse", style="filled", fillcolor="plum")

    # Corpus Callosum - Interlinks
    for i in range(len(ledger)):
        dot.edge(f"L{i}", f"R{i}", label="ƒ↔Ψ", fontsize="8", fontcolor="gray")

    # Central Root - Merkle Hash
    hashes = [entry["hash"] for entry in ledger if "hash" in entry]
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        hashes = [sha256((hashes[i] + hashes[i + 1]).encode()).hexdigest()
                  for i in range(0, len(hashes), 2)]

    if hashes:
        root_hash = hashes[0]
        dot.node("ROOT", f"MerkleRoot\n{hash_label(root_hash)}", shape="diamond", style="filled", fillcolor="gold")
        for i in range(len(ledger)):
            dot.edge(f"L{i}", "ROOT", style="dotted", color="black", arrowhead="none")

    return dot

if __name__ == "__main__":
    ledger = load_ledger()
    if not ledger:
        print("Ledger is empty or missing.")
    else:
        brain = build_brain_map(ledger)
        brain.render(OUTPUT_FILE, format="png", cleanup=True)
        print(f"Symbolic brain map rendered as {OUTPUT_FILE}.png")
