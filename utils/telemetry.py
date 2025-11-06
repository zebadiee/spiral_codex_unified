# utils/telemetry.py
import os, csv, time
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
WEAN_CSV = LOG_DIR / os.getenv("WEAN_LOG", "wean.csv")
ENABLED = os.getenv("TELEMETRY_ON", "1") not in ("0", "false", "False")

def _ensure():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not WEAN_CSV.exists():
        with WEAN_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["ts","route","provider","task","approx_lines","latency_ms","ok"])

def log_wean(route: str, provider: str, task: str, approx_lines: int, start_ns: int, ok: bool):
    if not ENABLED:
        return
    _ensure()
    ms = max(0, (time.time_ns() - start_ns) // 1_000_000)
    with WEAN_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.utcnow().isoformat(timespec="seconds")+"Z",
            route, provider, task, approx_lines, ms, int(bool(ok)),
        ])
