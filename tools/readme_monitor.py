#!/usr/bin/env python3
"""
README Monitor - Broadcasts README changes to agent trinity
Triggers Codex (syntax), Claude (semantics), Gemini (governance)
"""
import os
import json
import requests
import datetime
import hashlib
from pathlib import Path

SPIRAL_DIR = Path.home() / "Documents" / "spiral_codex_unified"
README = SPIRAL_DIR / "README.md"
STATE_FILE = SPIRAL_DIR / "data" / "readme_state.json"
API = "http://localhost:8000/v1/agents/notify"

def get_file_hash(filepath):
    """Calculate SHA-256 hash of file"""
    if not filepath.exists():
        return None
    return hashlib.sha256(filepath.read_bytes()).hexdigest()

def load_state():
    """Load last known README state"""
    if not STATE_FILE.exists():
        return {"last_hash": None, "last_check": None}
    return json.loads(STATE_FILE.read_text())

def save_state(state):
    """Save current README state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def broadcast_audit(content):
    """Send README to agents for collaborative review"""
    payload = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event": "readme_audit",
        "agents": ["codex", "claude", "gemini"],
        "content": content,
        "metadata": {
            "file": str(README),
            "hash": get_file_hash(README)
        }
    }
    
    try:
        response = requests.post(API, json=payload, timeout=10)
        if response.ok:
            print(f"📡 README audit broadcasted to trinity")
            return True
        else:
            print(f"⚠️ Broadcast returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Spiral API not reachable at", API)
        return False
    except Exception as e:
        print(f"❌ Broadcast failed: {e}")
        return False

def main():
    """Check README for changes and trigger audit if needed"""
    if not README.exists():
        print(f"❌ README not found: {README}")
        return 1
    
    # Load previous state
    state = load_state()
    current_hash = get_file_hash(README)
    
    # Check if changed
    if current_hash == state.get("last_hash"):
        print("✓ README unchanged since last check")
        return 0
    
    print(f"📝 README changed (hash: {current_hash[:8]}...)")
    
    # Read content and broadcast
    content = README.read_text()
    success = broadcast_audit(content)
    
    if success:
        # Update state
        state["last_hash"] = current_hash
        state["last_check"] = datetime.datetime.utcnow().isoformat()
        save_state(state)
        print("✓ State updated")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
