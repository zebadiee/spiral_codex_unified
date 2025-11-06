#!/usr/bin/env python3
"""
Base Fetcher with Trial Logging
Wraps any HTTP fetch to automatically log attempts to ingest_trials.jsonl
"""
import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ingest_trial_logger import log_trial

class LoggingFetcher:
    """Auto-logs every fetch for training data"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Spiral-Codex/1.0 (Learning Agent; +ethical-ai)"
        })
    
    def fetch(self, url: str, provenance: str = "unknown") -> dict:
        """Fetch URL and log trial"""
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            if resp.status_code == 200:
                log_trial(
                    url=url,
                    status="success",
                    headers=dict(resp.headers),
                    content_preview=resp.text[:500],
                    provenance=provenance,
                )
                return {"ok": True, "content": resp.text, "headers": dict(resp.headers)}
            else:
                log_trial(
                    url=url,
                    status="failed",
                    error=f"HTTP {resp.status_code}",
                    provenance=provenance,
                )
                return {"ok": False, "error": f"HTTP {resp.status_code}"}
        
        except requests.Timeout:
            log_trial(url=url, status="timeout", error="Request timeout", provenance=provenance)
            return {"ok": False, "error": "timeout"}
        
        except Exception as e:
            log_trial(url=url, status="blocked", error=str(e), provenance=provenance)
            return {"ok": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    fetcher = LoggingFetcher()
    result = fetcher.fetch("https://httpbin.org/html", provenance="test_run")
    print(f"Result: {result['ok']}, logged to ingest_trials.jsonl")
