#!/usr/bin/env python3
import requests, json, time
from pathlib import Path

KEY = "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"
MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "qwen/qwen3-coder:free",
    "z-ai/glm-4.5-air:free",
    "minimax/minimax-m2:free",
    "nvidia/nemotron-nano-9b-v2:free"
]

perf_file = Path("logs/model_perf.json")
perf_file.parent.mkdir(exist_ok=True)
perf = json.load(open(perf_file)) if perf_file.exists() else {m: {"ok": 0, "fail": 0, "ms": 0} for m in MODELS}

print("🌀 SPIRAL - Smart Model Rotation (5 Free Models)\n")
for m in MODELS:
    p = perf[m]
    total = p["ok"] + p["fail"]
    if total > 0:
        rate = (p["ok"] / total) * 100
        print(f"  {m.split('/')[1][:20]:20s} | {rate:5.1f}% | {p['ms']:5.0f}ms | {total} tries")

conversation = []

def chat(msg):
    for model in MODELS:
        t0 = time.time()
        try:
            conversation.append({"role": "user", "content": msg})
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": conversation},
                timeout=30
            )
            ms = (time.time() - t0) * 1000
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                conversation.append({"role": "assistant", "content": reply})
                perf[model]["ok"] += 1
                perf[model]["ms"] = perf[model]["ms"] * 0.8 + ms * 0.2
                json.dump(perf, open(perf_file, "w"))
                print(f"[{model.split('/')[1][:12]}] {ms:.0f}ms")
                return reply
            perf[model]["fail"] += 1
        except:
            perf[model]["fail"] += 1
    conversation.pop()
    return "All models failed"

print("\nReady Declan! (type 'stats' to see performance)\n")
while True:
    msg = input("🌀 You: ").strip()
    if not msg: continue
    if msg == "quit": break
    if msg == "stats":
        for m in MODELS:
            p = perf[m]
            total = p["ok"] + p["fail"]
            rate = (p["ok"] / total * 100) if total > 0 else 0
            print(f"  {m.split('/')[1][:20]:20s} | {rate:5.1f}% | {p['ms']:5.0f}ms")
        continue
    print(f"\n�� Spiral: ", end="", flush=True)
    print(chat(msg) + "\n")
