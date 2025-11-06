#!/usr/bin/env python3
"""
Ingest Trial Logger - Capture every fetch attempt for training
Appends {url, status, error, timestamp, headers, content_preview} to logs/ingest_trials.jsonl
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

TRIAL_LOG = Path(__file__).parent.parent / "logs" / "ingest_trials.jsonl"

def log_trial(
    url: str,
    status: str,
    error: Optional[str] = None,
    headers: Optional[dict] = None,
    content_preview: Optional[str] = None,
    provenance: Optional[str] = None,
):
    """Log a single fetch trial for future training"""
    TRIAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "url": url,
        "status": status,  # success | failed | timeout | blocked
        "error": error,
        "headers": headers or {},
        "content_preview": content_preview[:500] if content_preview else None,
        "provenance": provenance,
    }
    
    with TRIAL_LOG.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    """CLI: python ingest_trial_logger.py <url> <status> [error]"""
    if len(sys.argv) < 3:
        print("Usage: ingest_trial_logger.py <url> <status> [error]", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    status = sys.argv[2]
    error = sys.argv[3] if len(sys.argv) > 3 else None
    
    log_trial(url, status, error)
    print(f"✅ Logged {status} trial for {url}")

if __name__ == "__main__":
    main()
