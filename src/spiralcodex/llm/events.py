"""
LLM Event System for Spiral Codex
Integrates LLM results with mesh network and HUD overlays
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class LLMEvent:
    """LLM event data structure"""
    event_type: str
    agent_id: str
    data: Dict[str, Any]
    timestamp: str
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"llm_{self.agent_id}_{int(datetime.utcnow().timestamp() * 1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class LLMEventEmitter:
    """
    Event emitter for LLM-related events in Spiral Codex
    Integrates with existing mesh network and HUD systems
    """
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_history: List[LLMEvent] = []
        self.websocket_clients: List[Any] = []  # WebSocket connections for real-time updates
        self.max_history = 1000
    
    def add_handler(self, event_type: str, handler: Callable):
        """Add event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Added handler for event type: {event_type}")
    
    def remove_handler(self, event_type: str, handler: Callable):
        """Remove event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                logger.info(f"Removed handler for event type: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event type: {event_type}")
    
    async def emit_agent_event(self, agent_id: str, event_type: str, data: Dict[str, Any]):
        """Emit agent-specific LLM event"""
        event = LLMEvent(
            event_type=f"agent_{event_type}",
            agent_id=agent_id,
            data=data,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await self._process_event(event)
    
    async def emit_orchestration_event(self, event_type: str, data: Dict[str, Any]):
        """Emit orchestration-level event"""
        event = LLMEvent(
            event_type=f"orchestration_{event_type}",
            agent_id="orchestrator",
            data=data,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await self._process_event(event)
    
    async def emit_llm_workflow_event(self, agent_id: str, workflow_phase: str, data: Dict[str, Any]):
        """Emit LLM workflow-specific events"""
        event = LLMEvent(
            event_type=f"workflow_{workflow_phase}",
            agent_id=agent_id,
            data=data,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await self._process_event(event)
    
    async def _process_event(self, event: LLMEvent):
        """Process and distribute event"""
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Call registered handlers
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler failed for {event.event_type}: {e}")
        
        # Send to WebSocket clients (HUD integration)
        await self._broadcast_to_websockets(event)
        
        # Log event
        logger.info(f"LLM Event: {event.event_type} from {event.agent_id}")
    
    async def _broadcast_to_websockets(self, event: LLMEvent):
        """Broadcast event to WebSocket clients for HUD updates"""
        if not self.websocket_clients:
            return
        
        message = {
            "type": "llm_event",
            "event": event.to_dict()
        }
        
        # Remove disconnected clients
        active_clients = []
        for client in self.websocket_clients:
            try:
                await client.send_text(json.dumps(message))
                active_clients.append(client)
            except Exception as e:
                logger.warning(f"WebSocket client disconnected: {e}")
        
        self.websocket_clients = active_clients
    
    def add_websocket_client(self, websocket):
        """Add WebSocket client for real-time updates"""
        self.websocket_clients.append(websocket)
        logger.info("WebSocket client added for LLM events")
    
    def remove_websocket_client(self, websocket):
        """Remove WebSocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
            logger.info("WebSocket client removed from LLM events")
    
    def get_event_history(self, event_type: str = None, agent_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get filtered event history"""
        filtered_events = self.event_history
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if agent_id:
            filtered_events = [e for e in filtered_events if e.agent_id == agent_id]
        
        # Return most recent events
        recent_events = filtered_events[-limit:] if limit else filtered_events
        return [event.to_dict() for event in recent_events]
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics for monitoring"""
        if not self.event_history:
            return {"total_events": 0, "event_types": {}, "agents": {}}
        
        event_types = {}
        agents = {}
        
        for event in self.event_history:
            # Count by event type
            if event.event_type not in event_types:
                event_types[event.event_type] = 0
            event_types[event.event_type] += 1
            
            # Count by agent
            if event.agent_id not in agents:
                agents[event.agent_id] = 0
            agents[event.agent_id] += 1
        
        return {
            "total_events": len(self.event_history),
            "event_types": event_types,
            "agents": agents,
            "websocket_clients": len(self.websocket_clients),
            "last_event_time": self.event_history[-1].timestamp if self.event_history else None
        }


class HUDIntegration:
    """
    Integration layer for HUD overlays with LLM events
    """
    
    def __init__(self, event_emitter: LLMEventEmitter):
        self.event_emitter = event_emitter
        self.hud_overlays: Dict[str, Dict[str, Any]] = {}
        
        # Register HUD-specific event handlers
        self._setup_hud_handlers()
    
    def _setup_hud_handlers(self):
        """Setup event handlers for HUD integration"""
        
        async def handle_agent_activation(event: LLMEvent):
            """Handle agent activation for HUD display"""
            self.hud_overlays[f"agent_{event.agent_id}"] = {
                "type": "agent_status",
                "agent_id": event.agent_id,
                "status": "active",
                "timestamp": event.timestamp,
                "data": event.data
            }
        
        async def handle_query_processing(event: LLMEvent):
            """Handle query processing for HUD display"""
            overlay_key = f"query_{event.agent_id}"
            self.hud_overlays[overlay_key] = {
                "type": "query_processing",
                "agent_id": event.agent_id,
                "status": "processing",
                "query": event.data.get("query", "Unknown"),
                "timestamp": event.timestamp
            }
        
        async def handle_workflow_completion(event: LLMEvent):
            """Handle workflow completion for HUD display"""
            overlay_key = f"result_{event.agent_id}"
            workflow_result = event.data.get("workflow_result", {})
            knowledge = workflow_result.get("knowledge", {})
            
            self.hud_overlays[overlay_key] = {
                "type": "llm_result",
                "agent_id": event.agent_id,
                "status": "completed",
                "knowledge_response": knowledge.get("knowledge_response", "No response"),
                "model_used": knowledge.get("model_used", "unknown"),
                "tokens_used": knowledge.get("tokens_used", 0),
                "timestamp": event.timestamp
            }
        
        # Register handlers
        self.event_emitter.add_handler("agent_activated", handle_agent_activation)
        self.event_emitter.add_handler("agent_query_processing_started", handle_query_processing)
        self.event_emitter.add_handler("agent_query_processing_completed", handle_workflow_completion)
        self.event_emitter.add_handler("agent_enhanced_processing_completed", handle_workflow_completion)
    
    def get_hud_overlays(self) -> Dict[str, Any]:
        """Get current HUD overlays"""
        return {
            "llm_overlays": self.hud_overlays,
            "overlay_count": len(self.hud_overlays),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_overlay(self, overlay_key: str):
        """Clear specific HUD overlay"""
        if overlay_key in self.hud_overlays:
            del self.hud_overlays[overlay_key]
    
    def clear_all_overlays(self):
        """Clear all HUD overlays"""
        self.hud_overlays.clear()
    
    async def update_mesh_integration(self, mesh_data: Dict[str, Any]):
        """Update mesh network integration data"""
        mesh_overlay = {
            "type": "mesh_integration",
            "mesh_nodes": mesh_data.get("nodes", []),
            "active_connections": mesh_data.get("connections", 0),
            "llm_agents": len([k for k in self.hud_overlays.keys() if k.startswith("agent_")]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.hud_overlays["mesh_integration"] = mesh_overlay
        
        # Emit mesh integration event
        await self.event_emitter.emit_orchestration_event(
            "mesh_integration_updated",
            mesh_overlay
        )


# Global event emitter instance
_global_event_emitter = None

def get_global_event_emitter() -> LLMEventEmitter:
    """Get or create global event emitter instance"""
    global _global_event_emitter
    if _global_event_emitter is None:
        _global_event_emitter = LLMEventEmitter()
    return _global_event_emitter

def get_hud_integration() -> HUDIntegration:
    """Get HUD integration instance"""
    return HUDIntegration(get_global_event_emitter())
