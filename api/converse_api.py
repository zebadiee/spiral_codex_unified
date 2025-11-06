# api/converse_api.py
"""
Converse API - Multi-agent conversation and collaboration system
Supports Codex, Claude, Copilot, Gemma, DeepSeek, Gemini agents
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import asyncio
from pathlib import Path

router = APIRouter(prefix="/v1/converse", tags=["converse"])

# --- Schemas --------------------------------------------------------------

class AgentMessage(BaseModel):
    """Message between agents"""
    agent_id: str = Field(description="Sending agent identifier")
    content: str = Field(description="Message content")
    message_type: str = Field(default="text", description="Type: text, code, plan, analysis")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationRequest(BaseModel):
    """Request to start or continue a conversation"""
    session_id: str = Field(description="Conversation session identifier")
    message: str = Field(description="User or agent message")
    participants: List[str] = Field(description="List of participating agents")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CollaborationRequest(BaseModel):
    """Request for multi-agent collaboration on a task"""
    task: str = Field(description="Task description")
    agents: List[str] = Field(description="Agents to collaborate")
    workflow: str = Field(default="sequential", description="sequential, parallel, or consensus")
    constraints: Optional[List[str]] = Field(default_factory=list)

class AgentCapability(BaseModel):
    """Agent capability definition"""
    agent_id: str
    capabilities: List[str]
    specialties: List[str]
    glyph: str
    element: str

class ConversationResponse(BaseModel):
    """Response from conversation system"""
    session_id: str
    messages: List[AgentMessage]
    participants: List[str]
    coherence_score: float = Field(description="Conversation coherence score")
    next_action: Optional[str] = None

# --- Agent Registry --------------------------------------------------------

class MultiAgentRegistry:
    """Registry for multiple AI agents"""

    def __init__(self):
        self.agents = {
            "ƒCODEX": {
                "id": "ƒCODEX",
                "name": "Codex",
                "capabilities": ["code_generation", "debugging", "refactoring", "implementation"],
                "specialties": ["Python", "FastAPI", "System Architecture"],
                "glyph": "⊕",
                "element": "fire",
                "status": "active"
            },
            "ƒCLAUDE": {
                "id": "ƒCLAUDE",
                "name": "Claude",
                "capabilities": ["analysis", "planning", "documentation", "reasoning"],
                "specialties": ["System Design", "Architecture", "Code Review"],
                "glyph": "⊨",
                "element": "ice",
                "status": "active"
            },
            "ƒCOPILOT": {
                "id": "ƒCOPILOT",
                "name": "Copilot",
                "capabilities": ["code_completion", "pattern_matching", "optimization"],
                "specialties": ["Code Patterns", "Best Practices", "IDE Integration"],
                "glyph": "⊗",
                "element": "earth",
                "status": "active"
            },
            "ƒGEMMA": {
                "id": "ƒGEMMA",
                "name": "Gemma",
                "capabilities": ["research", "data_analysis", "knowledge_synthesis"],
                "specialties": ["Information Retrieval", "Data Processing", "Documentation"],
                "glyph": "⊜",
                "element": "water",
                "status": "active"
            },
            "ƒDEEPSEEK": {
                "id": "ƒDEEPSEEK",
                "name": "DeepSeek",
                "capabilities": ["deep_reasoning", "problem_solving", "optimization"],
                "specialties": ["Complex Algorithms", "Performance Tuning", "Logic"],
                "glyph": "⊞",
                "element": "air",
                "status": "active"
            },
            "ƒGEMINI": {
                "id": "ƒGEMINI",
                "name": "Gemini",
                "capabilities": ["multimodal_analysis", "synthesis", "creative_problem_solving"],
                "specialties": ["Pattern Recognition", "Cross-domain Integration", "Innovation"],
                "glyph": "⊟",
                "element": "void",
                "status": "active"
            }
        }

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[Dict[str, Any]]:
        return list(self.agents.values())

    def get_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        return [agent for agent in self.agents.values()
                if capability in agent["capabilities"]]

# --- Conversation Manager --------------------------------------------------

class ConversationManager:
    """Manages multi-agent conversations"""

    def __init__(self):
        self.conversations = {}
        self.conversation_path = Path("codex_root/conversations")
        self.conversation_path.mkdir(parents=True, exist_ok=True)
        self.registry = MultiAgentRegistry()

    def create_session(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Create new conversation session"""
        if session_id in self.conversations:
            return {"error": "Session already exists"}

        # Validate participants
        valid_participants = []
        for participant in participants:
            agent = self.registry.get_agent(participant)
            if agent:
                valid_participants.append(agent)
            else:
                return {"error": f"Unknown agent: {participant}"}

        self.conversations[session_id] = {
            "session_id": session_id,
            "participants": valid_participants,
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "coherence_score": 1.0
        }

        return {
            "session_id": session_id,
            "participants": [p["id"] for p in valid_participants],
            "status": "created"
        }

    def add_message(self, session_id: str, message: AgentMessage) -> Dict[str, Any]:
        """Add message to conversation"""
        if session_id not in self.conversations:
            return {"error": "Session not found"}

        session = self.conversations[session_id]

        # Validate sender
        if message.agent_id not in [p["id"] for p in session["participants"]]:
            return {"error": "Sender not in participants"}

        session["messages"].append({
            "agent_id": message.agent_id,
            "content": message.content,
            "message_type": message.message_type,
            "metadata": message.metadata,
            "timestamp": datetime.utcnow().isoformat()
        })
        session["last_activity"] = datetime.utcnow().isoformat()

        # Calculate coherence score
        session["coherence_score"] = self._calculate_coherence(session["messages"])

        return {
            "session_id": session_id,
            "message_added": True,
            "coherence_score": session["coherence_score"]
        }

    def _calculate_coherence(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate conversation coherence score"""
        if len(messages) <= 1:
            return 1.0

        # Simple coherence calculation based on message patterns
        coherence = 0.8  # Base coherence

        # Check for conversation patterns
        if len(messages) >= 2:
            last_two = messages[-2:]
            # Reward agent interaction
            if last_two[0]["agent_id"] != last_two[1]["agent_id"]:
                coherence += 0.1

            # Reward task progression
            content_types = [msg.get("message_type", "text") for msg in last_two]
            if "plan" in content_types and "code" in content_types:
                coherence += 0.1

        return min(1.0, coherence)

    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details"""
        return self.conversations.get(session_id)

# --- Collaboration Engine --------------------------------------------------

class CollaborationEngine:
    """Handles multi-agent collaboration workflows"""

    def __init__(self):
        self.registry = MultiAgentRegistry()
        self.collaborations = {}

    def start_collaboration(self, req: CollaborationRequest) -> Dict[str, Any]:
        """Start multi-agent collaboration"""
        collaboration_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Validate agents
        valid_agents = []
        for agent_id in req.agents:
            agent = self.registry.get_agent(agent_id)
            if agent:
                valid_agents.append(agent)
            else:
                return {"error": f"Unknown agent: {agent_id}"}

        collaboration = {
            "collaboration_id": collaboration_id,
            "task": req.task,
            "agents": valid_agents,
            "workflow": req.workflow,
            "constraints": req.constraints,
            "status": "started",
            "results": [],
            "created_at": datetime.utcnow().isoformat()
        }

        self.collaborations[collaboration_id] = collaboration

        # Execute collaboration workflow
        if req.workflow == "sequential":
            results = self._execute_sequential(collaboration)
        elif req.workflow == "parallel":
            results = self._execute_parallel(collaboration)
        elif req.workflow == "consensus":
            results = self._execute_consensus(collaboration)
        else:
            results = [{"error": f"Unknown workflow: {req.workflow}"}]

        collaboration["results"] = results
        collaboration["completed_at"] = datetime.utcnow().isoformat()
        collaboration["status"] = "completed"

        return collaboration

    def _execute_sequential(self, collaboration: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute sequential collaboration"""
        results = []
        task = collaboration["task"]

        for agent in collaboration["agents"]:
            # Simulate agent processing
            result = {
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "task": task,
                "contribution": f"{agent['name']} contribution to: {task}",
                "capabilities_used": agent["capabilities"][:2],
                "glyph": agent["glyph"],
                "timestamp": datetime.utcnow().isoformat()
            }
            results.append(result)

        return results

    def _execute_parallel(self, collaboration: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute parallel collaboration"""
        results = []
        task = collaboration["task"]

        # All agents work simultaneously
        for agent in collaboration["agents"]:
            result = {
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "task": task,
                "contribution": f"{agent['name']} parallel contribution to: {task}",
                "capabilities_used": agent["capabilities"][:2],
                "glyph": agent["glyph"],
                "timestamp": datetime.utcnow().isoformat()
            }
            results.append(result)

        return results

    def _execute_consensus(self, collaboration: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute consensus collaboration"""
        results = []
        task = collaboration["task"]

        # First round: individual analysis
        individual_results = []
        for agent in collaboration["agents"]:
            result = {
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "analysis": f"{agent['name']} analysis of: {task}",
                "recommendation": f"{agent['name']} recommendation",
                "confidence": 0.8,
                "glyph": agent["glyph"]
            }
            individual_results.append(result)

        results.extend(individual_results)

        # Consensus result
        consensus = {
            "agent_id": "CONSENSUS",
            "task": task,
            "consensus": f"Consensus reached based on {len(individual_results)} agent analyses",
            "agreement_level": 0.85,
            "final_recommendation": f"Collaborative solution for: {task}",
            "glyph": "⊚"
        }
        results.append(consensus)

        return results

# Initialize components
conversation_manager = ConversationManager()
collaboration_engine = CollaborationEngine()

# --- API Routes ------------------------------------------------------------

@router.get("/health")
async def health():
    return {
        "ok": True,
        "service": "converse",
        "version": 1,
        "active_agents": len(MultiAgentRegistry().agents),
        "glyph": "⊚"
    }

@router.post("/session/create")
async def create_session(req: ConversationRequest):
    """Create new conversation session"""
    result = conversation_manager.create_session(req.session_id, req.participants)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/session/message")
async def add_message(req: ConversationRequest):
    """Add message to conversation session"""
    message = AgentMessage(
        agent_id=req.participants[0] if req.participants else "user",
        content=req.message,
        message_type="text"
    )
    result = conversation_manager.add_message(req.session_id, message)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get conversation session details"""
    session = conversation_manager.get_conversation(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/collaborate", response_model=Dict[str, Any])
async def collaborate(req: CollaborationRequest):
    """Start multi-agent collaboration"""
    result = collaboration_engine.start_collaboration(req)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/agents", response_model=List[AgentCapability])
async def get_agents():
    """Get all available agents and their capabilities"""
    registry = MultiAgentRegistry()
    return [
        AgentCapability(
            agent_id=agent["id"],
            capabilities=agent["capabilities"],
            specialties=agent["specialties"],
            glyph=agent["glyph"],
            element=agent["element"]
        )
        for agent in registry.get_all_agents()
    ]

@router.get("/agents/{capability}", response_model=List[AgentCapability])
async def get_agents_by_capability(capability: str):
    """Get agents with specific capability"""
    registry = MultiAgentRegistry()
    agents = registry.get_agents_by_capability(capability)
    return [
        AgentCapability(
            agent_id=agent["id"],
            capabilities=agent["capabilities"],
            specialties=agent["specialties"],
            glyph=agent["glyph"],
            element=agent["element"]
        )
        for agent in agents
    ]

@router.get("/status")
async def get_converse_status():
    """Get converse system status"""
    return {
        "system": "converse",
        "status": "active",
        "active_sessions": len(conversation_manager.conversations),
        "active_collaborations": len(collaboration_engine.collaborations),
        "available_agents": len(MultiAgentRegistry().agents),
        "timestamp": datetime.utcnow().isoformat()
    }