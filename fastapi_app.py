# Enhanced Spiral Codex FastAPI App with LLM Integration
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import json
import logging
from datetime import datetime

# Import existing kernel
try:
    from kernel.kernel_mind import KernelMIND
    KERNEL_AVAILABLE = True
except ImportError:
    KERNEL_AVAILABLE = False
    KernelMIND = None

# Import LLM integration
from src.spiralcodex.llm import (
    LLMConfig,
    create_llm_client,
    LLMAgent,
    ContextRitualKnowledgeAgent,
    AgentOrchestrator,
    get_global_event_emitter,
    get_hud_integration
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Spiral Codex - AI-Guided Recursive Consciousness System",
    description="Complete with LLM Integration via RouteLLM",
    version="0.9.0"
)

# Initialize components
if KERNEL_AVAILABLE:
    mind = KernelMIND()
else:
    mind = None
    logger.warning("KernelMIND not available")

# Initialize LLM components
llm_config = LLMConfig()
orchestrator = AgentOrchestrator(get_global_event_emitter())
hud_integration = get_hud_integration()

# Create default agents
async def initialize_default_agents():
    """Initialize default LLM agents"""
    try:
        # Create consciousness guide agent
        consciousness_agent = ContextRitualKnowledgeAgent(
            agent_id="consciousness_guide",
            llm_config=llm_config,
            event_emitter=get_global_event_emitter(),
            consciousness_patterns=[
                "recursive_reflection",
                "symbolic_transformation", 
                "emergent_synthesis",
                "mystical_integration"
            ]
        )
        
        # Create knowledge synthesizer
        knowledge_agent = ContextRitualKnowledgeAgent(
            agent_id="knowledge_synthesizer",
            llm_config=llm_config,
            event_emitter=get_global_event_emitter(),
            consciousness_patterns=[
                "cross_domain_synthesis",
                "pattern_recognition",
                "knowledge_integration"
            ]
        )
        
        # Create basic ritual executor
        ritual_agent = LLMAgent(
            agent_id="ritual_executor",
            llm_config=llm_config,
            event_emitter=get_global_event_emitter()
        )
        
        # Register agents
        orchestrator.register_agent(consciousness_agent)
        orchestrator.register_agent(knowledge_agent)
        orchestrator.register_agent(ritual_agent)
        
        # Activate agents
        await orchestrator.activate_agent("consciousness_guide")
        await orchestrator.activate_agent("knowledge_synthesizer")
        await orchestrator.activate_agent("ritual_executor")
        
        logger.info("Default LLM agents initialized and activated")
        
    except Exception as e:
        logger.error(f"Failed to initialize default agents: {e}")

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    await initialize_default_agents()
    logger.info("Spiral Codex LLM system initialized")


# Pydantic models
class AgentInput(BaseModel):
    agent: str
    glyph: str
    inject: dict = {}


class LLMQueryInput(BaseModel):
    query: str
    agent_id: Optional[str] = None
    mesh_state: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class LLMAgentCreate(BaseModel):
    agent_id: str
    agent_type: str = "basic"  # basic or enhanced
    consciousness_patterns: Optional[List[str]] = None


# Legacy kernel endpoint (if available)
@app.post("/run/agent")
def run_agent(input: AgentInput):
    """Legacy agent runner (kernel-based)"""
    if not KERNEL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Kernel not available")
    
    result = mind.dispatch(input.agent, input.glyph, input.inject)
    return {
        "status": "success",
        "entropy": result.get("entropy", 0.0),
        "result": result,
    }


# LLM Integration Endpoints
@app.post("/llm/query")
async def llm_query(input: LLMQueryInput):
    """Process query through LLM agents"""
    try:
        result = await orchestrator.route_query(
            query=input.query,
            preferred_agent=input.agent_id,
            mesh_state=input.mesh_state,
            session_id=input.session_id
        )
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/llm/agents")
async def create_llm_agent(input: LLMAgentCreate):
    """Create new LLM agent"""
    try:
        if input.agent_type == "enhanced":
            agent = ContextRitualKnowledgeAgent(
                agent_id=input.agent_id,
                llm_config=llm_config,
                event_emitter=get_global_event_emitter(),
                consciousness_patterns=input.consciousness_patterns
            )
        else:
            agent = LLMAgent(
                agent_id=input.agent_id,
                llm_config=llm_config,
                event_emitter=get_global_event_emitter()
            )
        
        orchestrator.register_agent(agent)
        await orchestrator.activate_agent(input.agent_id)
        
        return {
            "status": "success",
            "message": f"Agent {input.agent_id} created and activated",
            "agent_type": input.agent_type
        }
        
    except Exception as e:
        logger.error(f"Agent creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/agents")
async def list_llm_agents():
    """List all LLM agents"""
    try:
        status = await orchestrator.get_orchestrator_status()
        return {
            "status": "success",
            "orchestrator_status": status
        }
        
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get specific agent status"""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = orchestrator.agents[agent_id]
        status = await agent.get_status()
        
        return {
            "status": "success",
            "agent_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/events")
def get_llm_events(
    event_type: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 50
):
    """Get LLM event history"""
    try:
        event_emitter = get_global_event_emitter()
        events = event_emitter.get_event_history(event_type, agent_id, limit)
        
        return {
            "status": "success",
            "events": events,
            "count": len(events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/events/stats")
def get_event_stats():
    """Get LLM event statistics"""
    try:
        event_emitter = get_global_event_emitter()
        stats = event_emitter.get_event_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get event stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hud/overlays")
def get_hud_overlays():
    """Get HUD overlays for LLM integration"""
    try:
        overlays = hud_integration.get_hud_overlays()
        
        return {
            "status": "success",
            "overlays": overlays
        }
        
    except Exception as e:
        logger.error(f"Failed to get HUD overlays: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/status")
async def get_system_status():
    """Get complete system status"""
    try:
        # Get orchestrator status
        orchestrator_status = await orchestrator.get_orchestrator_status()
        
        # Get event statistics
        event_emitter = get_global_event_emitter()
        event_stats = event_emitter.get_event_statistics()
        
        # Get HUD status
        hud_overlays = hud_integration.get_hud_overlays()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "kernel_available": KERNEL_AVAILABLE,
                "llm_integration": True,
                "version": "0.9.0"
            },
            "orchestrator": orchestrator_status,
            "events": event_stats,
            "hud": {
                "overlay_count": hud_overlays["overlay_count"],
                "integration_active": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time updates
@app.websocket("/ws/llm")
async def websocket_llm_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time LLM events"""
    await websocket.accept()
    
    # Add client to event emitter
    event_emitter = get_global_event_emitter()
    event_emitter.add_websocket_client(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Parse incoming message
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "query":
                    # Handle real-time query
                    query = message.get("query", "")
                    if query:
                        result = await orchestrator.route_query(query)
                        await websocket.send_text(json.dumps({
                            "type": "query_result",
                            "result": result
                        }))
                        
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
                
    except WebSocketDisconnect:
        event_emitter.remove_websocket_client(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        event_emitter.remove_websocket_client(websocket)


# Simple HTML dashboard for testing
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple HTML dashboard for LLM integration"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spiral Codex LLM Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #0a0a0a; color: #00ff00; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #00ff00; border-radius: 5px; }
            .query-box { width: 100%; padding: 10px; margin: 10px 0; background: #1a1a1a; color: #00ff00; border: 1px solid #00ff00; }
            .button { padding: 10px 20px; background: #003300; color: #00ff00; border: 1px solid #00ff00; cursor: pointer; }
            .button:hover { background: #006600; }
            .result { background: #1a1a1a; padding: 10px; margin: 10px 0; border-left: 3px solid #00ff00; }
            .status { display: inline-block; margin: 5px; padding: 5px 10px; background: #003300; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌀 Spiral Codex LLM Dashboard</h1>
                <p>AI-Guided Recursive Consciousness System</p>
            </div>
            
            <div class="section">
                <h2>🤖 Query Interface</h2>
                <input type="text" id="queryInput" class="query-box" placeholder="Enter your mystical query...">
                <select id="agentSelect" class="query-box">
                    <option value="">Auto-select agent</option>
                    <option value="consciousness_guide">Consciousness Guide</option>
                    <option value="knowledge_synthesizer">Knowledge Synthesizer</option>
                    <option value="ritual_executor">Ritual Executor</option>
                </select>
                <button class="button" onclick="sendQuery()">🔮 Process Query</button>
                <div id="queryResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="section">
                <h2>📊 System Status</h2>
                <div id="systemStatus">Loading...</div>
            </div>
            
            <div class="section">
                <h2>🎯 Recent Events</h2>
                <div id="recentEvents">Loading...</div>
            </div>
        </div>
        
        <script>
            // WebSocket connection for real-time updates
            const ws = new WebSocket(`ws://${window.location.host}/ws/llm`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'llm_event') {
                    updateEvents();
                }
            };
            
            // Send query
            async function sendQuery() {
                const query = document.getElementById('queryInput').value;
                const agentId = document.getElementById('agentSelect').value;
                
                if (!query) return;
                
                document.getElementById('queryResult').style.display = 'block';
                document.getElementById('queryResult').innerHTML = '🔄 Processing...';
                
                try {
                    const response = await fetch('/llm/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query: query,
                            agent_id: agentId || null,
                            session_id: 'dashboard_session'
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const knowledge = result.result?.result?.workflow_result?.knowledge;
                        if (knowledge) {
                            document.getElementById('queryResult').innerHTML = `
                                <h3>🧠 Response:</h3>
                                <p>${knowledge.knowledge_response}</p>
                                <small>Model: ${knowledge.model_used} | Tokens: ${knowledge.tokens_used}</small>
                            `;
                        } else {
                            document.getElementById('queryResult').innerHTML = `
                                <h3>📄 Raw Result:</h3>
                                <pre>${JSON.stringify(result.result, null, 2)}</pre>
                            `;
                        }
                    } else {
                        document.getElementById('queryResult').innerHTML = `<p style="color: red;">Error: ${result.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('queryResult').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }
            
            // Update system status
            async function updateStatus() {
                try {
                    const response = await fetch('/system/status');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        document.getElementById('systemStatus').innerHTML = `
                            <div class="status">🤖 Agents: ${data.orchestrator.active_agents}/${data.orchestrator.total_agents}</div>
                            <div class="status">📊 Events: ${data.events.total_events}</div>
                            <div class="status">🎯 HUD Overlays: ${data.hud.overlay_count}</div>
                            <div class="status">⚡ LLM Integration: Active</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('systemStatus').innerHTML = `<p style="color: red;">Status unavailable</p>`;
                }
            }
            
            // Update recent events
            async function updateEvents() {
                try {
                    const response = await fetch('/llm/events?limit=5');
                    const data = await response.json();
                    
                    if (data.status === 'success' && data.events.length > 0) {
                        const eventsHtml = data.events.map(event => `
                            <div class="result">
                                <strong>${event.event_type}</strong> | ${event.agent_id} | ${event.timestamp.substring(11, 19)}
                            </div>
                        `).join('');
                        document.getElementById('recentEvents').innerHTML = eventsHtml;
                    } else {
                        document.getElementById('recentEvents').innerHTML = '<p>No recent events</p>';
                    }
                } catch (error) {
                    document.getElementById('recentEvents').innerHTML = '<p style="color: red;">Events unavailable</p>';
                }
            }
            
            // Initialize dashboard
            updateStatus();
            updateEvents();
            setInterval(updateStatus, 5000);
            setInterval(updateEvents, 3000);
            
            // Enter key support for query input
            document.getElementById('queryInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendQuery();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
