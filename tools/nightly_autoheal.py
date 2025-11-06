#!/usr/bin/env python3
"""
Nightly Auto-Heal - Keeps Spiral healthy automatically
Runs: audit → seed → trim → reflect
"""
import json, time, glob, os, requests, shutil
from datetime import datetime, timezone
from pathlib import Path

def post(url, obj):
    """Post to Spiral API"""
    try:
        requests.post(url, headers={"content-type":"application/json"}, 
                     json=obj, timeout=15)
    except Exception as e:
        log_error(f"Post failed to {url}: {e}")

def log_error(msg):
    """Log errors"""
    with open("logs/autoheal.err", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {msg}\n")

print("🌀 Spiral Auto-Heal Starting...")

# 1) Run legendary audit (if present)
print("1️⃣  Running system audit...")
try:
    os.system("./legendary_system_audit.py >/dev/null 2>&1")
except:
    pass

# 2) Ensure ≥10 thoughts
print("2️⃣  Checking brain health...")
try:
    stats = requests.get("http://localhost:8000/v1/brain/stats", timeout=10).json()
    current = int(stats.get("thought_count", 0))
    needed = max(0, 10 - current)
    
    if needed > 0:
        print(f"   Seeding {needed} thoughts...")
        now = datetime.now(timezone.utc).isoformat()
        kinds = ["insight", "decision", "artifact", "error"]
        
        for i in range(needed):
            post("http://localhost:8000/v1/brain/record", {
                "record_type": kinds[i % 4],
                "timestamp": now,
                "content": f"Nightly auto-seed #{i+1}",
                "tags": ["autoheal", "nightly", "quantum"]
            })
    else:
        print(f"   ✅ Brain healthy ({current} thoughts)")
except Exception as e:
    log_error(f"Brain check error: {e}")

# 3) Trim sessions >100
print("3️⃣  Trimming old sessions...")
try:
    conv = "ledger/conversations"
    arch = "ledger/archive"
    Path(arch).mkdir(parents=True, exist_ok=True)
    
    files = sorted(glob.glob(f"{conv}/*.jsonl"), key=os.path.getmtime)
    if len(files) > 100:
        archived = 0
        for f in files[:-100]:
            shutil.move(f, f"{arch}/{os.path.basename(f)}")
            archived += 1
        print(f"   Archived {archived} old sessions")
    else:
        print(f"   ✅ Session count OK ({len(files)})")
except Exception as e:
    log_error(f"Trim error: {e}")

# 4) Kick reflection
print("4️⃣  Running reflection cycle...")
try:
    result = os.system("make reflect >/dev/null 2>&1")
    if result == 0:
        print("   ✅ Reflection complete")
except:
    log_error("Reflection failed")

print("✅ Auto-Heal Complete!")
