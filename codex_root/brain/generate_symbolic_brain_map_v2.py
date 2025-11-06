
import json
from hashlib import sha256
from graphviz import Digraph
from pathlib import Path

LEDGER_FILE = "codex_immutable_ledger.json"
OUTPUT_FILE = "symbolic_brain_map_v2"

SEMANTIC_COLOR_MAP = {
    "Test / Debug": "lightblue",
    "Vision": "lightyellow",
    "Memory": "lightgreen",
    "Emotive": "pink",
    "System": "lightgray"
}

AI_FUNCTIONS = {
    "ƒAI_Scan": ["ƒTEST0"],
    "ƒAI_Learn": ["ƒTEST1"],
    "ƒAI_Reflect": ["ƒTEST2"],
    "ƒAI_Express": ["ƒTEST3"]
}

def load_ledger():
    try:
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def get_color(semantic_layer):
    return SEMANTIC_COLOR_MAP.get(semantic_layer, "white")

def build_brain_map(ledger):
    dot = Digraph(comment="Symbolic Brain Map v2")
    dot.attr(rankdir='LR', fontname="Courier", fontsize="10")

    # Left Brain Nodes
    for i, entry in enumerate(ledger):
        lid = f"L{i}"
        label = entry.get("record_id", f"ƒ{i}")
        h = entry.get("hash", "")[:8] + "..."
        semantic = entry.get("semantic_layer", "System")
        color = get_color(semantic)
        dot.node(lid, f"{label}\n{h}", shape="box", style="filled", fillcolor=color)

    # Right Brain Nodes
    for i, entry in enumerate(ledger):
        rid = f"R{i}"
        label = f"ΨEcho{i}"
        role = entry.get("archetypal_role", "Abstract")
        dot.node(rid, f"{label}\n{role}", shape="ellipse", style="filled", fillcolor="plum")

    # Interlinks
    for i in range(len(ledger)):
        dot.edge(f"L{i}", f"R{i}", label="ƒ↔Ψ", fontsize="8", fontcolor="gray")

    # AI Function Nodes
    for func, targets in AI_FUNCTIONS.items():
        fid = f"{func}"
        dot.node(fid, func, shape="component", style="filled", fillcolor="lightgoldenrod")
        for target in targets:
            for i, entry in enumerate(ledger):
                if entry.get("record_id") == target:
                    dot.edge(fid, f"L{i}", label="exec", style="dashed", color="orange")

    # Behavioral Loops (Perceive → Learn → Reflect → Express)
    loop_funcs = ["ƒAI_Scan", "ƒAI_Learn", "ƒAI_Reflect", "ƒAI_Express"]
    for i in range(len(loop_funcs)):
        src = loop_funcs[i]
        dst = loop_funcs[(i + 1) % len(loop_funcs)]
        dot.edge(src, dst, style="bold", color="blue", label="loop", fontsize="8")

    # Merkle Root Summary
    hashes = [entry["hash"] for entry in ledger if "hash" in entry]
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        hashes = [sha256((hashes[i] + hashes[i + 1]).encode()).hexdigest()
                  for i in range(0, len(hashes), 2)]

    if hashes:
        root_hash = hashes[0]
        dot.node("ROOT", f"MerkleRoot\n{root_hash[:8]}...", shape="diamond", style="filled", fillcolor="gold")
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
        print(f"Symbolic brain map v2 rendered as {OUTPUT_FILE}.png")
