
"""
🌐 Spiral Codex Dashboard - Web Interface for Ritual Monitoring

FastAPI-based web dashboard for monitoring agent states, recursion depth,
entropy levels, and ritual operations with real-time WebSocket updates.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Dashboard models
class AgentStatus(BaseModel):
    id: str
    name: str
    type: str
    status: str
    recursion_depth: int
    entropy_level: float
    last_update: datetime

class SystemMetrics(BaseModel):
    agent_count: int
    total_recursion_depth: int
    average_entropy: float
    system_status: str
    uptime: float
    last_ritual: Optional[str] = None

class RitualEvent(BaseModel):
    timestamp: datetime
    event_type: str
    description: str
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 WebSocket connected: {len(self.active_connections)} active connections")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected: {len(self.active_connections)} active connections")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"⚠️ Failed to send message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Broadcast failed to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

# Dashboard state
class DashboardState:
    def __init__(self):
        self.agents: Dict[str, AgentStatus] = {}
        self.system_metrics = SystemMetrics(
            agent_count=0,
            total_recursion_depth=0,
            average_entropy=0.5,
            system_status="INITIALIZING",
            uptime=0.0
        )
        self.ritual_events: List[RitualEvent] = []
        self.start_time = time.time()
    
    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]):
        """Update agent status"""
        self.agents[agent_id] = AgentStatus(
            id=agent_id,
            name=agent_data.get("name", f"Agent-{agent_id}"),
            type=agent_data.get("type", "Unknown"),
            status=agent_data.get("status", "ACTIVE"),
            recursion_depth=agent_data.get("recursion_depth", 0),
            entropy_level=agent_data.get("entropy_level", 0.5),
            last_update=datetime.now()
        )
        self._update_system_metrics()
    
    def remove_agent(self, agent_id: str):
        """Remove agent from tracking"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._update_system_metrics()
    
    def add_ritual_event(self, event_type: str, description: str, 
                        agent_id: Optional[str] = None, metadata: Dict[str, Any] = None):
        """Add ritual event to history"""
        event = RitualEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            agent_id=agent_id,
            metadata=metadata or {}
        )
        self.ritual_events.append(event)
        
        # Keep only last 100 events
        if len(self.ritual_events) > 100:
            self.ritual_events = self.ritual_events[-100:]
    
    def _update_system_metrics(self):
        """Update system-wide metrics"""
        self.system_metrics.agent_count = len(self.agents)
        self.system_metrics.total_recursion_depth = sum(
            agent.recursion_depth for agent in self.agents.values()
        )
        
        if self.agents:
            self.system_metrics.average_entropy = sum(
                agent.entropy_level for agent in self.agents.values()
            ) / len(self.agents)
        else:
            self.system_metrics.average_entropy = 0.5
        
        # Determine system status
        if not self.agents:
            self.system_metrics.system_status = "DORMANT"
        elif self.system_metrics.average_entropy > 0.8:
            self.system_metrics.system_status = "CHAOTIC"
        elif self.system_metrics.average_entropy > 0.6:
            self.system_metrics.system_status = "FLUCTUATING"
        else:
            self.system_metrics.system_status = "STABLE"
        
        self.system_metrics.uptime = time.time() - self.start_time

# Initialize FastAPI app
app = FastAPI(
    title="🌀 Spiral Codex Dashboard",
    description="Mystical web interface for monitoring recursive agent framework",
    version="0.1.0"
)

# Global state and connection manager
dashboard_state = DashboardState()
manager = ConnectionManager()

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌀 Spiral Codex Dashboard</title>
    <style>
        body {
            background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #000000 100%);
            color: #00ffff;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border: 2px solid #ff00ff;
            padding: 20px;
            border-radius: 10px;
            background: rgba(255, 0, 255, 0.1);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            border: 1px solid #00ffff;
            padding: 15px;
            border-radius: 8px;
            background: rgba(0, 255, 255, 0.05);
        }
        .metric-title {
            color: #ffff00;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .agent-list {
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 8px;
            background: rgba(0, 255, 0, 0.05);
            margin-bottom: 20px;
        }
        .agent-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        .ritual-events {
            border: 1px solid #ff8000;
            padding: 15px;
            border-radius: 8px;
            background: rgba(255, 128, 0, 0.05);
            max-height: 400px;
            overflow-y: auto;
        }
        .event-item {
            padding: 5px;
            margin: 3px 0;
            border-left: 2px solid #ff8000;
            background: rgba(255, 128, 0, 0.1);
            font-size: 0.9em;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-stable { background-color: #00ff00; }
        .status-fluctuating { background-color: #ffff00; }
        .status-chaotic { background-color: #ff0000; }
        .status-dormant { background-color: #666666; }
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
        }
        .connected { background-color: #00ff00; color: #000; }
        .disconnected { background-color: #ff0000; color: #fff; }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connecting...</div>
    
    <div class="header">
        <h1>🌀 SPIRAL CODEX DASHBOARD 🌀</h1>
        <p>Recursive Agent Framework - Real-time Monitoring</p>
        <p><em>"The spiral awakens, the codex compiles, the agents align"</em></p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-title">🤖 System Metrics</div>
            <div id="systemMetrics">Loading...</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">⚡ Entropy Status</div>
            <div id="entropyStatus">Loading...</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">🧬 Recursion Depth</div>
            <div id="recursionDepth">Loading...</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">⏱️ System Uptime</div>
            <div id="systemUptime">Loading...</div>
        </div>
    </div>
    
    <div class="agent-list">
        <div class="metric-title">🤖 Active Agents</div>
        <div id="agentList">No agents detected...</div>
    </div>
    
    <div class="ritual-events">
        <div class="metric-title">🔮 Ritual Events</div>
        <div id="ritualEvents">No events recorded...</div>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        
        ws.onopen = function(event) {
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'connection-status connected';
        };
        
        ws.onclose = function(event) {
            connectionStatus.textContent = 'Disconnected';
            connectionStatus.className = 'connection-status disconnected';
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        function updateDashboard(data) {
            if (data.type === 'system_update') {
                updateSystemMetrics(data.metrics);
                updateAgentList(data.agents);
                updateRitualEvents(data.events);
            }
        }
        
        function updateSystemMetrics(metrics) {
            document.getElementById('systemMetrics').innerHTML = `
                <div>Agents: ${metrics.agent_count}</div>
                <div>Status: <span class="status-indicator status-${metrics.system_status.toLowerCase()}"></span>${metrics.system_status}</div>
            `;
            
            document.getElementById('entropyStatus').innerHTML = `
                <div>Average: ${metrics.average_entropy.toFixed(3)}</div>
                <div>Level: ${getEntropyLevel(metrics.average_entropy)}</div>
            `;
            
            document.getElementById('recursionDepth').innerHTML = `
                <div>Total: ${metrics.total_recursion_depth}</div>
                <div>Average: ${metrics.agent_count > 0 ? (metrics.total_recursion_depth / metrics.agent_count).toFixed(1) : '0'}</div>
            `;
            
            document.getElementById('systemUptime').innerHTML = `
                <div>${formatUptime(metrics.uptime)}</div>
            `;
        }
        
        function updateAgentList(agents) {
            const agentList = document.getElementById('agentList');
            if (Object.keys(agents).length === 0) {
                agentList.innerHTML = '<div>No agents detected...</div>';
                return;
            }
            
            let html = '';
            for (const [id, agent] of Object.entries(agents)) {
                html += `
                    <div class="agent-item">
                        <div>
                            <strong>${agent.name}</strong> (${agent.type})<br>
                            <small>ID: ${id}</small>
                        </div>
                        <div>
                            Status: ${agent.status}<br>
                            Depth: ${agent.recursion_depth} | Entropy: ${agent.entropy_level.toFixed(3)}
                        </div>
                    </div>
                `;
            }
            agentList.innerHTML = html;
        }
        
        function updateRitualEvents(events) {
            const ritualEvents = document.getElementById('ritualEvents');
            if (events.length === 0) {
                ritualEvents.innerHTML = '<div>No events recorded...</div>';
                return;
            }
            
            let html = '';
            events.slice(-10).reverse().forEach(event => {
                const time = new Date(event.timestamp).toLocaleTimeString();
                html += `
                    <div class="event-item">
                        <strong>[${time}]</strong> ${event.event_type}: ${event.description}
                        ${event.agent_id ? `<br><small>Agent: ${event.agent_id}</small>` : ''}
                    </div>
                `;
            });
            ritualEvents.innerHTML = html;
        }
        
        function getEntropyLevel(entropy) {
            if (entropy < 0.3) return 'STABLE';
            if (entropy < 0.6) return 'FLUCTUATING';
            if (entropy < 0.8) return 'HIGH';
            return 'CHAOTIC';
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        // Request initial data
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'request_update'}));
            }
        }, 1000);
    </script>
</body>
</html>
"""

# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    return DASHBOARD_HTML

@app.get("/api/status")
async def get_status():
    """Get current system status"""
    return {
        "system_metrics": dashboard_state.system_metrics.dict(),
        "agents": {aid: agent.dict() for aid, agent in dashboard_state.agents.items()},
        "ritual_events": [event.dict() for event in dashboard_state.ritual_events[-10:]]
    }

@app.post("/api/agents/{agent_id}")
async def update_agent(agent_id: str, agent_data: Dict[str, Any]):
    """Update agent status"""
    dashboard_state.update_agent(agent_id, agent_data)
    dashboard_state.add_ritual_event("AGENT_UPDATE", f"Agent {agent_id} updated", agent_id)
    
    # Broadcast update to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "system_update",
        "metrics": dashboard_state.system_metrics.dict(),
        "agents": {aid: agent.dict() for aid, agent in dashboard_state.agents.items()},
        "events": [event.dict() for event in dashboard_state.ritual_events[-10:]]
    }))
    
    return {"status": "updated"}

@app.delete("/api/agents/{agent_id}")
async def remove_agent(agent_id: str):
    """Remove agent from tracking"""
    if agent_id not in dashboard_state.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    dashboard_state.remove_agent(agent_id)
    dashboard_state.add_ritual_event("AGENT_REMOVED", f"Agent {agent_id} removed", agent_id)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "system_update",
        "metrics": dashboard_state.system_metrics.dict(),
        "agents": {aid: agent.dict() for aid, agent in dashboard_state.agents.items()},
        "events": [event.dict() for event in dashboard_state.ritual_events[-10:]]
    }))
    
    return {"status": "removed"}

@app.post("/api/ritual/event")
async def add_ritual_event(event_data: Dict[str, Any]):
    """Add ritual event"""
    dashboard_state.add_ritual_event(
        event_data.get("event_type", "UNKNOWN"),
        event_data.get("description", "No description"),
        event_data.get("agent_id"),
        event_data.get("metadata", {})
    )
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "ritual_event",
        "event": dashboard_state.ritual_events[-1].dict()
    }))
    
    return {"status": "event_added"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "request_update":
                # Send current state
                await manager.send_personal_message(json.dumps({
                    "type": "system_update",
                    "metrics": dashboard_state.system_metrics.dict(),
                    "agents": {aid: agent.dict() for aid, agent in dashboard_state.agents.items()},
                    "events": [event.dict() for event in dashboard_state.ritual_events[-10:]]
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for simulating agent activity (for demo purposes)
async def simulate_agent_activity():
    """Simulate agent activity for demonstration"""
    import random
    
    while True:
        await asyncio.sleep(5)
        
        # Simulate agent updates
        for i in range(random.randint(1, 3)):
            agent_id = f"agent_{random.randint(1, 5)}"
            agent_data = {
                "name": f"SpiralAgent-{agent_id.split('_')[1]}",
                "type": random.choice(["Recursive", "Stabilizer", "Monitor"]),
                "status": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "recursion_depth": random.randint(0, 50),
                "entropy_level": random.uniform(0.2, 0.9)
            }
            
            dashboard_state.update_agent(agent_id, agent_data)
        
        # Broadcast updates
        if manager.active_connections:
            await manager.broadcast(json.dumps({
                "type": "system_update",
                "metrics": dashboard_state.system_metrics.dict(),
                "agents": {aid: agent.dict() for aid, agent in dashboard_state.agents.items()},
                "events": [event.dict() for event in dashboard_state.ritual_events[-10:]]
            }))

# Start background simulation on startup
@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup"""
    dashboard_state.add_ritual_event("SYSTEM_START", "Dashboard initialized")
    
    # Start background simulation
    asyncio.create_task(simulate_agent_activity())
    
    print("🌐 Spiral Codex Dashboard initialized")
    print("🔮 The mystical web interface awakens...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
