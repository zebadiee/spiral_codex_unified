#!/usr/bin/env python3
"""
Omarchy Web CLI - Browser-based terminal dashboard
Real-time status, Web3 proofs, signed ledger entries
Port: 8010
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from pathlib import Path
from datetime import datetime
import httpx

app = FastAPI(title="Omarchy Web CLI", version="1.0.0")

# Configuration
SPIRAL_URL = "http://localhost:8000"
OMAI_URL = "http://localhost:7016"
LEDGER_DIR = Path(__file__).parent.parent / "ledger" / "conversations"
WEAN_CSV = Path(__file__).parent.parent / "logs" / "wean.csv"

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve Omarchy Web CLI dashboard"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🌀 Spiral Codex - Omarchy Web CLI</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0e27;
            color: #00ffcc;
            font-family: 'Monaco', 'Courier New', monospace;
            padding: 20px;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            border: 2px solid #00ffcc;
            padding: 20px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1e47 100%);
        }
        .header h1 {
            font-size: 2em;
            text-shadow: 0 0 10px #00ffcc;
            margin-bottom: 10px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .panel {
            border: 1px solid #00ffcc;
            padding: 15px;
            background: rgba(0, 255, 204, 0.05);
            border-radius: 5px;
        }
        .panel h2 {
            color: #ff00ff;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-ok { background: #00ff00; box-shadow: 0 0 10px #00ff00; }
        .status-warn { background: #ffff00; box-shadow: 0 0 10px #ffff00; }
        .status-error { background: #ff0000; box-shadow: 0 0 10px #ff0000; }
        .metric { margin: 8px 0; }
        .metric-label { color: #888; }
        .metric-value { color: #00ffcc; font-weight: bold; }
        .log-entry {
            background: rgba(0, 255, 204, 0.1);
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #00ffcc;
            font-size: 0.9em;
        }
        .timestamp { color: #888; font-size: 0.8em; }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #1a1e47;
            border: 1px solid #00ffcc;
            position: relative;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ffcc, #ff00ff);
            transition: width 0.3s;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 0.9em;
        }
        .blink { animation: blink 2s infinite; }
        @keyframes blink {
            0%, 49% { opacity: 1; }
            50%, 100% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌀 SPIRAL CODEX 2025 - OMARCHY WEB CLI</h1>
        <p>Research-Grade Autonomous Intelligence | MIT-Compliant | Web3-Ready</p>
    </div>

    <div class="grid">
        <div class="panel">
            <h2>📊 System Health</h2>
            <div class="metric">
                <span class="status-indicator" id="spiral-status"></span>
                <span class="metric-label">Spiral API:</span>
                <span class="metric-value" id="spiral-version">—</span>
            </div>
            <div class="metric">
                <span class="status-indicator" id="omai-status"></span>
                <span class="metric-label">OMAi Context:</span>
                <span class="metric-value" id="omai-service">—</span>
            </div>
            <div class="metric">
                <span class="metric-label">Uptime:</span>
                <span class="metric-value" id="uptime">—</span>
            </div>
        </div>

        <div class="panel">
            <h2>⚡ Local Usage</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="local-bar" style="width: 0%"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Last Provider:</span>
                <span class="metric-value" id="last-provider">—</span>
            </div>
            <div class="metric">
                <span class="metric-label">Latency:</span>
                <span class="metric-value" id="last-latency">—</span>
            </div>
        </div>

        <div class="panel">
            <h2>⏰ Nightly Automation</h2>
            <div class="metric">
                <span class="metric-label">OMAi Reindex:</span>
                <span class="metric-value" id="omai-timer">—</span>
            </div>
            <div class="metric">
                <span class="metric-label">Spiral Reflect:</span>
                <span class="metric-value" id="spiral-timer">—</span>
            </div>
            <div class="metric">
                <span class="metric-label blink">Status:</span>
                <span class="metric-value">ARMED ✅</span>
            </div>
        </div>

        <div class="panel">
            <h2>🎓 MIT Priority System</h2>
            <div class="metric">
                <span class="metric-label">ManuAGI Score:</span>
                <span class="metric-value" style="color: #ff00ff;">3.0 (CRITICAL)</span>
            </div>
            <div class="metric">
                <span class="metric-label">MIT OCW:</span>
                <span class="metric-value">1.4 (MEDIUM)</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Sources:</span>
                <span class="metric-value" id="priority-count">—</span>
            </div>
        </div>
    </div>

    <div class="panel">
        <h2>💬 Latest Ledger Entries</h2>
        <div id="ledger-log"></div>
    </div>

    <div class="footer">
        <p>Spiral Codex 2025 | Autonomous • Verifiable • MIT-Compliant • Web3-Ready</p>
        <p><em>"What is remembered becomes ritual. What is ritual becomes recursion. What is recursion becomes alive."</em></p>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Update health status
            if (data.spiral) {
                document.getElementById('spiral-status').className = 
                    'status-indicator ' + (data.spiral.ok ? 'status-ok' : 'status-error');
                document.getElementById('spiral-version').textContent = 
                    data.spiral.version || 'n/a';
            }
            
            if (data.omai) {
                document.getElementById('omai-status').className = 
                    'status-indicator ' + (data.omai.ok ? 'status-ok' : 'status-error');
                document.getElementById('omai-service').textContent = 
                    data.omai.service || 'n/a';
            }
            
            // Update usage
            if (data.wean) {
                const pct = data.wean.local_pct || 0;
                document.getElementById('local-bar').style.width = pct + '%';
                document.getElementById('last-provider').textContent = 
                    data.wean.last_provider || '—';
                document.getElementById('last-latency').textContent = 
                    (data.wean.last_latency || '—') + 'ms';
            }
            
            // Update ledger
            if (data.ledger && data.ledger.length > 0) {
                const logDiv = document.getElementById('ledger-log');
                logDiv.innerHTML = '';
                data.ledger.slice(-5).forEach(entry => {
                    const div = document.createElement('div');
                    div.className = 'log-entry';
                    div.innerHTML = `
                        <span class="timestamp">${entry.ts}</span><br>
                        <strong>${entry.role}:</strong> ${entry.content.substring(0, 100)}...
                    `;
                    logDiv.appendChild(div);
                });
            }
            
            // Update timers
            if (data.timers) {
                document.getElementById('omai-timer').textContent = data.timers.omai || '—';
                document.getElementById('spiral-timer').textContent = data.timers.spiral || '—';
            }
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected, attempting reconnect...');
            setTimeout(() => window.location.reload(), 5000);
        };
    </script>
</body>
</html>
"""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time status updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Fetch current status
            status = await get_system_status()
            await manager.broadcast(status)
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def get_system_status() -> dict:
    """Gather system status from all services"""
    status = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "spiral": {},
        "omai": {},
        "wean": {},
        "ledger": [],
        "timers": {}
    }
    
    # Check Spiral health
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{SPIRAL_URL}/health")
            status["spiral"] = resp.json()
    except:
        status["spiral"] = {"ok": False}
    
    # Check OMAi health
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{OMAI_URL}/health")
            status["omai"] = resp.json()
    except:
        status["omai"] = {"ok": False}
    
    # Read wean telemetry
    if WEAN_CSV.exists():
        try:
            lines = WEAN_CSV.read_text().strip().split('\n')
            if len(lines) > 1:
                last = lines[-1].split(',')
                status["wean"] = {
                    "last_provider": last[2] if len(last) > 2 else "—",
                    "last_latency": last[5] if len(last) > 5 else "—",
                    "local_pct": calculate_local_pct(lines[-50:])
                }
        except:
            pass
    
    # Read latest ledger entries
    if LEDGER_DIR.exists():
        try:
            latest = sorted(LEDGER_DIR.glob("*.jsonl"))[-1]
            with latest.open() as f:
                entries = [json.loads(line) for line in f.readlines()[-5:]]
                status["ledger"] = entries
        except:
            pass
    
    # Timer info (static for now)
    status["timers"] = {
        "omai": "23:45 GMT daily",
        "spiral": "00:00 GMT daily"
    }
    
    return status

def calculate_local_pct(lines: list) -> int:
    """Calculate local usage percentage from wean lines"""
    local = sum(1 for line in lines if 'local' in line.lower())
    total = len(lines)
    return int((local / total * 100)) if total > 0 else 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
