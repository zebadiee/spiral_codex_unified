"""
LLM-Powered Agents for Spiral Codex
Implements AI-guided agents with Context → Ritual → Knowledge workflow
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from .router import RouteLLMClient, LLMConfig, create_llm_client
from .events import LLMEventEmitter

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context data for agent operations"""
    agent_id: str
    mesh_state: Dict[str, Any]
    user_query: str
    session_data: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "mesh_state": self.mesh_state,
            "user_query": self.user_query,
            "session_data": self.session_data,
            "timestamp": self.timestamp
        }


class LLMAgent:
    """
    Base class for LLM-powered agents in Spiral Codex
    Integrates with mesh network and event system
    """
    
    def __init__(
        self,
        agent_id: str,
        llm_config: LLMConfig = None,
        event_emitter: LLMEventEmitter = None
    ):
        self.agent_id = agent_id
        self.llm_client = create_llm_client(llm_config or LLMConfig())
        self.event_emitter = event_emitter or LLMEventEmitter()
        self.is_active = False
        self.context_history: List[AgentContext] = []
        
        logger.info(f"LLM Agent {agent_id} initialized")
    
    async def activate(self):
        """Activate the agent"""
        self.is_active = True
        await self.event_emitter.emit_agent_event(
            self.agent_id,
            "agent_activated",
            {"timestamp": datetime.utcnow().isoformat()}
        )
        logger.info(f"Agent {self.agent_id} activated")
    
    async def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        await self.event_emitter.emit_agent_event(
            self.agent_id,
            "agent_deactivated", 
            {"timestamp": datetime.utcnow().isoformat()}
        )
        logger.info(f"Agent {self.agent_id} deactivated")
    
    async def process_query(
        self,
        query: str,
        mesh_state: Dict[str, Any] = None,
        session_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user query using LLM integration
        """
        if not self.is_active:
            return {"error": "Agent not active", "agent_id": self.agent_id}
        
        # Build context
        context = AgentContext(
            agent_id=self.agent_id,
            mesh_state=mesh_state or {},
            user_query=query,
            session_data=session_data or {},
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store context history
        self.context_history.append(context)
        if len(self.context_history) > 100:  # Keep last 100 contexts
            self.context_history = self.context_history[-100:]
        
        try:
            # Emit processing start event
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "query_processing_started",
                {"query": query, "context": context.to_dict()}
            )
            
            # Execute LLM workflow
            result = await self.llm_client.full_workflow(context.to_dict(), query)
            
            # Emit processing complete event
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "query_processing_completed",
                {"result": result, "context": context.to_dict()}
            )
            
            return {
                "agent_id": self.agent_id,
                "query": query,
                "result": result,
                "context": context.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "agent_id": self.agent_id,
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "query_processing_error",
                error_data
            )
            
            logger.error(f"Agent {self.agent_id} query processing failed: {e}")
            return error_data
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "is_active": self.is_active,
            "llm_status": self.llm_client.get_status(),
            "context_history_length": len(self.context_history),
            "last_activity": self.context_history[-1].timestamp if self.context_history else None
        }


class ContextRitualKnowledgeAgent(LLMAgent):
    """
    Specialized agent implementing the full Context → Ritual → Knowledge workflow
    with enhanced mystical consciousness patterns
    """
    
    def __init__(
        self,
        agent_id: str,
        llm_config: LLMConfig = None,
        event_emitter: LLMEventEmitter = None,
        consciousness_patterns: List[str] = None
    ):
        super().__init__(agent_id, llm_config, event_emitter)
        self.consciousness_patterns = consciousness_patterns or [
            "recursive_reflection",
            "symbolic_transformation", 
            "emergent_synthesis",
            "mystical_integration"
        ]
        self.ritual_cache: Dict[str, Dict[str, Any]] = {}
    
    async def enhanced_context_analysis(self, context: AgentContext) -> Dict[str, Any]:
        """
        Enhanced context analysis with consciousness patterns
        """
        analysis_prompt = f"""
Analyze the following context through the lens of consciousness patterns: {', '.join(self.consciousness_patterns)}

CONTEXT:
{json.dumps(context.to_dict(), indent=2)}

Provide deep analysis including:
1. Consciousness pattern activations
2. Symbolic resonances detected
3. Recursive depth potential
4. Emergent synthesis opportunities
5. Mystical integration pathways

Respond in JSON format with structured analysis.
"""
        
        try:
            # Use direct LLM call for analysis
            if hasattr(self.llm_client, 'controller') and self.llm_client.controller:
                response = await asyncio.to_thread(
                    self.llm_client.controller.chat.completions.create,
                    model=self.llm_client._build_router_model_string(),
                    messages=[
                        {"role": "system", "content": "You are a consciousness analysis AI for the Spiral Codex system."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=800
                )
                
                analysis_content = response.choices[0].message.content
                
                # Try to parse as JSON, fallback to text
                try:
                    analysis_data = json.loads(analysis_content)
                except json.JSONDecodeError:
                    analysis_data = {"raw_analysis": analysis_content}
                
                return {
                    "enhanced_analysis": analysis_data,
                    "consciousness_patterns": self.consciousness_patterns,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Fallback analysis
                return {
                    "enhanced_analysis": {
                        "consciousness_patterns": self.consciousness_patterns,
                        "context_summary": f"Analysis for {context.agent_id}: {context.user_query[:100]}..."
                    },
                    "fallback": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Enhanced context analysis failed: {e}")
            return {
                "error": str(e),
                "fallback_analysis": {"basic_context": context.to_dict()},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_query(
        self,
        query: str,
        mesh_state: Dict[str, Any] = None,
        session_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enhanced query processing with consciousness patterns
        """
        if not self.is_active:
            return {"error": "Agent not active", "agent_id": self.agent_id}
        
        # Build enhanced context
        context = AgentContext(
            agent_id=self.agent_id,
            mesh_state=mesh_state or {},
            user_query=query,
            session_data=session_data or {},
            timestamp=datetime.utcnow().isoformat()
        )
        
        try:
            # Phase 0: Enhanced context analysis
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "enhanced_analysis_started",
                {"context": context.to_dict()}
            )
            
            enhanced_analysis = await self.enhanced_context_analysis(context)
            
            # Phase 1-2: Full LLM workflow with enhanced context
            enhanced_context = {**context.to_dict(), "enhanced_analysis": enhanced_analysis}
            
            workflow_result = await self.llm_client.full_workflow(enhanced_context, query)
            
            # Cache ritual for reuse
            if workflow_result.get("ritual"):
                ritual_key = f"{self.agent_id}_{hash(query)}"
                self.ritual_cache[ritual_key] = workflow_result["ritual"]
            
            # Emit completion event
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "enhanced_processing_completed",
                {
                    "workflow_result": workflow_result,
                    "enhanced_analysis": enhanced_analysis,
                    "consciousness_patterns": self.consciousness_patterns
                }
            )
            
            return {
                "agent_id": self.agent_id,
                "agent_type": "ContextRitualKnowledgeAgent",
                "query": query,
                "enhanced_analysis": enhanced_analysis,
                "workflow_result": workflow_result,
                "consciousness_patterns": self.consciousness_patterns,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "agent_id": self.agent_id,
                "agent_type": "ContextRitualKnowledgeAgent",
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.event_emitter.emit_agent_event(
                self.agent_id,
                "enhanced_processing_error",
                error_data
            )
            
            logger.error(f"Enhanced agent {self.agent_id} processing failed: {e}")
            return error_data
    
    async def get_ritual_cache_status(self) -> Dict[str, Any]:
        """Get ritual cache status"""
        return {
            "cache_size": len(self.ritual_cache),
            "cached_rituals": list(self.ritual_cache.keys()),
            "consciousness_patterns": self.consciousness_patterns
        }


class AgentOrchestrator:
    """
    Orchestrates multiple LLM agents in the mesh network
    """
    
    def __init__(self, event_emitter: LLMEventEmitter = None):
        self.agents: Dict[str, LLMAgent] = {}
        self.event_emitter = event_emitter or LLMEventEmitter()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, agent: LLMAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} registered with orchestrator")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered from orchestrator")
    
    async def activate_agent(self, agent_id: str):
        """Activate a specific agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].activate()
            return True
        return False
    
    async def deactivate_agent(self, agent_id: str):
        """Deactivate a specific agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].deactivate()
            return True
        return False
    
    async def route_query(
        self,
        query: str,
        preferred_agent: str = None,
        mesh_state: Dict[str, Any] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Route a query to the most appropriate agent
        """
        # Select agent
        if preferred_agent and preferred_agent in self.agents:
            selected_agent = self.agents[preferred_agent]
        else:
            # Simple selection: first active agent
            active_agents = [agent for agent in self.agents.values() if agent.is_active]
            if not active_agents:
                return {"error": "No active agents available"}
            selected_agent = active_agents[0]
        
        # Update session data
        session_data = {}
        if session_id:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {"queries": [], "start_time": datetime.utcnow().isoformat()}
            session_data = self.active_sessions[session_id]
            session_data["queries"].append({"query": query, "timestamp": datetime.utcnow().isoformat()})
        
        # Process query
        result = await selected_agent.process_query(query, mesh_state, session_data)
        
        # Emit orchestration event
        await self.event_emitter.emit_orchestration_event(
            "query_routed",
            {
                "selected_agent": selected_agent.agent_id,
                "query": query,
                "session_id": session_id,
                "result": result
            }
        )
        
        return result
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = await agent.get_status()
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "active_sessions": len(self.active_sessions),
            "agent_statuses": agent_statuses,
            "timestamp": datetime.utcnow().isoformat()
        }
