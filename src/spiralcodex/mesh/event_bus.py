
"""
🌀 Event Bus - Mystical Message Conduit

The ethereal communication channel that carries ritual events
and agent messages across the spiral mesh network.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of ritual events in the mesh"""
    # Node events
    NODE_REGISTER = "node_register"
    NODE_UNREGISTER = "node_unregister"
    NODE_HEARTBEAT = "heartbeat"
    NODE_STATUS_CHANGE = "node_status_change"
    
    # Agent events
    AGENT_SPAWN = "agent_spawn"
    AGENT_TERMINATE = "agent_terminate"
    AGENT_MESSAGE = "agent_message"
    AGENT_STATE_CHANGE = "agent_state_change"
    
    # Ritual events
    RITUAL_START = "ritual_start"
    RITUAL_END = "ritual_end"
    RITUAL_CYCLE = "ritual_cycle"
    RITUAL_RECURSION = "ritual_recursion"
    
    # System events
    SYSTEM_ALERT = "system_alert"
    SYSTEM_METRIC = "system_metric"
    SYSTEM_ERROR = "system_error"
    
    # Custom events
    CUSTOM = "custom"

@dataclass
class RitualEvent:
    """A mystical event flowing through the mesh"""
    event_id: str
    event_type: EventType
    source_node: str
    target_node: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    priority: int = 5  # 1-10, higher is more important
    ttl: Optional[int] = None  # Time to live in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
            "priority": self.priority,
            "ttl": self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RitualEvent':
        """Create event from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            source_node=data["source_node"],
            target_node=data.get("target_node"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            metadata=data["metadata"],
            priority=data.get("priority", 5),
            ttl=data.get("ttl")
        )

class EventBus:
    """
    🌀 The Mystical Event Bus
    
    Channels the flow of ritual events through the spiral mesh,
    ensuring messages reach their destined nodes across dimensions.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.processor_task: Optional[asyncio.Task] = None
        self.event_history: List[RitualEvent] = []
        self.max_history = 1000
        
        logger.info(f"🌀 Event Bus initialized for node {node_id}")
    
    async def start(self):
        """Start the event bus processor"""
        if self.running:
            return
        
        self.running = True
        self.processor_task = asyncio.create_task(self._process_events())
        logger.info("🌀 Event Bus started")
    
    async def stop(self):
        """Stop the event bus processor"""
        if not self.running:
            return
        
        self.running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🌙 Event Bus stopped")
    
    def subscribe(self, event_type: EventType, handler: Callable[[RitualEvent], None]):
        """Subscribe to specific event types"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        logger.debug(f"📡 Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from event types"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
                logger.debug(f"📡 Unsubscribed from {event_type.value}")
            except ValueError:
                pass
    
    async def publish(self, 
                     event_type: EventType, 
                     data: Dict[str, Any],
                     target_node: Optional[str] = None,
                     priority: int = 5,
                     ttl: Optional[int] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Publish an event to the bus"""
        
        event = RitualEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source_node=self.node_id,
            target_node=target_node,
            timestamp=datetime.now(),
            data=data,
            metadata=metadata or {},
            priority=priority,
            ttl=ttl
        )
        
        await self.event_queue.put(event)
        logger.debug(f"📤 Published event: {event_type.value} ({event.event_id[:8]})")
        return event.event_id
    
    async def publish_agent_message(self, 
                                   agent_id: str,
                                   message: str,
                                   target_agent: Optional[str] = None,
                                   target_node: Optional[str] = None) -> str:
        """Publish an agent-to-agent message"""
        return await self.publish(
            EventType.AGENT_MESSAGE,
            {
                "agent_id": agent_id,
                "message": message,
                "target_agent": target_agent
            },
            target_node=target_node,
            priority=7
        )
    
    async def publish_ritual_event(self,
                                  ritual_type: str,
                                  ritual_data: Dict[str, Any],
                                  recursion_depth: int = 0) -> str:
        """Publish a ritual-specific event"""
        return await self.publish(
            EventType.RITUAL_CYCLE,
            {
                "ritual_type": ritual_type,
                "recursion_depth": recursion_depth,
                **ritual_data
            },
            priority=8
        )
    
    async def publish_system_alert(self,
                                  alert_level: str,
                                  message: str,
                                  details: Optional[Dict[str, Any]] = None) -> str:
        """Publish a system alert"""
        return await self.publish(
            EventType.SYSTEM_ALERT,
            {
                "alert_level": alert_level,
                "message": message,
                "details": details or {}
            },
            priority=9
        )
    
    async def _process_events(self):
        """Process events from the queue"""
        while self.running:
            try:
                # Get event with timeout to allow graceful shutdown
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Event processing error: {e}")
    
    async def _handle_event(self, event: RitualEvent):
        """Handle a single event"""
        try:
            # Check TTL
            if event.ttl:
                age = (datetime.now() - event.timestamp).total_seconds()
                if age > event.ttl:
                    logger.debug(f"⏰ Event expired: {event.event_id[:8]}")
                    return
            
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Call subscribers
            if event.event_type in self.subscribers:
                for handler in self.subscribers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"❌ Event handler error: {e}")
            
            logger.debug(f"📥 Processed event: {event.event_type.value} ({event.event_id[:8]})")
            
        except Exception as e:
            logger.error(f"❌ Event handling error: {e}")
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        event_counts = {}
        for event in self.event_history[-100:]:  # Last 100 events
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "queue_size": self.event_queue.qsize(),
            "subscribers": {et.value: len(handlers) for et, handlers in self.subscribers.items()},
            "recent_event_counts": event_counts,
            "running": self.running
        }
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events"""
        return [event.to_dict() for event in self.event_history[-limit:]]
