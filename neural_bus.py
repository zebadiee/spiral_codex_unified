#!/usr/bin/env python3
"""
neural_bus.py - Central Communication Layer for Spiral Codex Stack

This module provides the neural bus that enables inter-system communication
between OMAi, Spiral Codex, Quantum Debugger, and AI Token Manager.

Author: Spiral Codex Genesis Architecture v2
License: Proprietary
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import aiohttp
import aiofiles
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from typing import Set
import uvicorn

# =============================================================================
# CUSTOM WEBSOCKET MANAGER
# =============================================================================

class CustomWebSocketManager:
    """Custom WebSocket manager for FastAPI"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)

    @property
    def connections(self) -> Set[WebSocket]:
        """Get active connections"""
        return self.active_connections

# =============================================================================
# CONFIGURATION
# =============================================================================

class MessageType(Enum):
    """Message types for neural bus communication"""
    HEARTBEAT = "heartbeat"
    HEALTH_STATUS = "health_status"
    QEI_UPDATE = "qei_update"
    TOKEN_ROTATION = "token_rotation"
    SYSTEM_EVENT = "system_event"
    REFLECTION_TRIGGER = "reflection_trigger"
    CODE_GENERATION = "code_generation"
    VAULT_SYNC = "vault_sync"
    QUANTUM_COHERENCE = "quantum_coherence"
    RECOVERY_PROTOCOL = "recovery_protocol"
    CONSCIOUSNESS_UPDATE = "consciousness_update"

class ComponentType(Enum):
    """Component types in the stack"""
    OMAI = "omai"
    SPIRAL_CODEX = "spiral_codex"
    QUANTUM_DEBUGGER = "quantum_debugger"
    TOKEN_MANAGER = "token_manager"
    NEURAL_BUS = "neural_bus"

@dataclass
class Message:
    """Neural bus message structure"""
    id: str
    type: MessageType
    source: ComponentType
    target: Optional[ComponentType]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 2=medium, 3=high
    correlation_id: Optional[str] = None
    requires_ack: bool = False
    ttl: Optional[int] = None  # Time to live in seconds

@dataclass
class ComponentStatus:
    """Component status information"""
    component: ComponentType
    healthy: bool
    last_heartbeat: datetime
    response_time: float
    error_count: int
    metadata: Dict[str, Any]

# =============================================================================
# NEURAL BUS CORE
# =============================================================================

class NeuralBus:
    """Central neural bus for inter-system communication"""

    def __init__(self):
        self.app = FastAPI(title="Neural Bus", version="2.0.0")
        self.components: Dict[ComponentType, ComponentStatus] = {}
        self.message_queue: List[Message] = []
        self.websocket_manager = CustomWebSocketManager()
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.running = False
        self.persistence_enabled = True
        self.max_queue_size = 1000

        self._setup_logging()
        self._setup_routes()
        self._load_state()

    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(os.getenv('STACK_LOG_DIR', '/tmp'))
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'neural_bus.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('NeuralBus')

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def root():
            return {"service": "Neural Bus", "status": "running", "timestamp": datetime.now().isoformat()}

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "components": len(self.components),
                "queue_size": len(self.message_queue),
                "uptime": self._get_uptime()
            }

        @self.app.get("/components")
        async def get_components():
            return {
                component_type: asdict(status)
                for component_type, status in self.components.items()
            }

        @self.app.post("/message")
        async def send_message(message: Dict[str, Any]):
            """Receive and queue a message"""
            try:
                msg = Message(
                    id=message.get('id', str(uuid.uuid4())),
                    type=MessageType(message['type']),
                    source=ComponentType(message['source']),
                    target=ComponentType(message['target']) if message.get('target') else None,
                    payload=message['payload'],
                    timestamp=datetime.fromisoformat(message['timestamp']) if message.get('timestamp') else datetime.now(),
                    priority=message.get('priority', 1),
                    correlation_id=message.get('correlation_id'),
                    requires_ack=message.get('requires_ack', False),
                    ttl=message.get('ttl')
                )

                success = self._queue_message(msg)
                return {"status": "queued" if success else "failed", "message_id": msg.id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.get("/queue")
        async def get_queue():
            """Get current message queue (for debugging)"""
            return {
                "messages": [asdict(msg) for msg in self.message_queue],
                "size": len(self.message_queue),
                "max_size": self.max_queue_size
            }

        @self.app.post("/heartbeat/{component}")
        async def heartbeat(component: str, status: Dict[str, Any]):
            """Receive heartbeat from component"""
            try:
                comp_type = ComponentType(component)
                self.components[comp_type] = ComponentStatus(
                    component=comp_type,
                    healthy=status.get('healthy', True),
                    last_heartbeat=datetime.now(),
                    response_time=status.get('response_time', 0.0),
                    error_count=status.get('error_count', 0),
                    metadata=status.get('metadata', {})
                )

                # Broadcast health update
                await self._broadcast_message(MessageType.HEALTH_STATUS, {
                    "component": component,
                    "healthy": status.get('healthy', True),
                    "timestamp": datetime.now().isoformat()
                })

                return {"status": "received"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication"""
            await websocket.accept()
            self.websocket_manager.connect(websocket)

            try:
                while self.running:
                    data = await websocket.receive_text()
                    await self._handle_websocket_message(websocket, data)
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)

    def _load_state(self):
        """Load persisted state if available"""
        if not self.persistence_enabled:
            return

        state_file = Path("data/neural_bus_state.json")
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)

                # Restore component statuses
                for comp_str, status_data in state.get('components', {}).items():
                    try:
                        comp_type = ComponentType(comp_str)
                        status_data['last_heartbeat'] = datetime.fromisoformat(status_data['last_heartbeat'])
                        self.components[comp_type] = ComponentStatus(**status_data)
                    except:
                        continue

                self.logger.info(f"Loaded state with {len(self.components)} components")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")

    def _save_state(self):
        """Save current state to disk"""
        if not self.persistence_enabled:
            return

        try:
            state_file = Path("data/neural_bus_state.json")
            state_file.parent.mkdir(parents=True, exist_ok=True)

            state = {
                'components': {
                    comp_type.value: {
                        **asdict(status),
                        'last_heartbeat': status.last_heartbeat.isoformat()
                    }
                    for comp_type, status in self.components.items()
                },
                'timestamp': datetime.now().isoformat()
            }

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def _queue_message(self, message: Message) -> bool:
        """Queue a message for processing"""
        if len(self.message_queue) >= self.max_queue_size:
            self.logger.warning("Message queue full, dropping oldest messages")
            self.message_queue = self.message_queue[-int(self.max_queue_size * 0.8):]

        self.message_queue.append(message)
        self.logger.debug(f"Queued message {message.id} of type {message.type.value}")
        return True

    async def _process_message(self, message: Message):
        """Process a single message"""
        try:
            # Check TTL
            if message.ttl:
                age = (datetime.now() - message.timestamp).total_seconds()
                if age > message.ttl:
                    self.logger.debug(f"Message {message.id} expired")
                    return

            # Call subscribers
            if message.type in self.subscribers:
                for callback in self.subscribers[message.type]:
                    try:
                        await callback(message)
                    except Exception as e:
                        self.logger.error(f"Subscriber callback failed: {e}")

            # Broadcast to WebSocket clients
            await self._broadcast_websocket_message(message)

        except Exception as e:
            self.logger.error(f"Failed to process message {message.id}: {e}")

    async def _broadcast_message(self, message_type: MessageType, payload: Dict[str, Any]):
        """Broadcast a message to all connected components"""
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            source=ComponentType.NEURAL_BUS,
            target=None,
            payload=payload,
            timestamp=datetime.now(),
            priority=2
        )

        await self._process_message(message)

    async def _broadcast_websocket_message(self, message: Message):
        """Broadcast message to WebSocket clients"""
        try:
            msg_data = asdict(message)
            msg_data['timestamp'] = message.timestamp.isoformat()

            for websocket in self.websocket_manager.connections:
                try:
                    await websocket.send_text(json.dumps(msg_data))
                except:
                    # Remove disconnected websockets
                    self.websocket_manager.disconnect(websocket)
        except Exception as e:
            self.logger.error(f"Failed to broadcast WebSocket message: {e}")

    async def _handle_websocket_message(self, websocket: WebSocket, data: str):
        """Handle incoming WebSocket message"""
        try:
            message_data = json.loads(data)

            message = Message(
                id=message_data.get('id', str(uuid.uuid4())),
                type=MessageType(message_data['type']),
                source=ComponentType(message_data['source']),
                target=ComponentType(message_data['target']) if message_data.get('target') else None,
                payload=message_data['payload'],
                timestamp=datetime.fromisoformat(message_data['timestamp']) if message_data.get('timestamp') else datetime.now(),
                priority=message_data.get('priority', 1),
                correlation_id=message_data.get('correlation_id'),
                requires_ack=message_data.get('requires_ack', False),
                ttl=message_data.get('ttl')
            )

            self._queue_message(message)

        except Exception as e:
            self.logger.error(f"Failed to handle WebSocket message: {e}")

    def _get_uptime(self) -> str:
        """Get service uptime"""
        if hasattr(self, 'start_time'):
            uptime = datetime.now() - self.start_time
            return str(uptime)
        return "unknown"

    def subscribe(self, message_type: MessageType, callback: Callable):
        """Subscribe to specific message types"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(callback)

    async def send_to_component(self, component: ComponentType, message_type: MessageType, payload: Dict[str, Any]):
        """Send message to specific component"""
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            source=ComponentType.NEURAL_BUS,
            target=component,
            payload=payload,
            timestamp=datetime.now(),
            priority=2,
            requires_ack=True
        )

        self._queue_message(message)

    async def start(self):
        """Start the neural bus service"""
        self.running = True
        self.start_time = datetime.now()

        # Start message processor
        asyncio.create_task(self._message_processor())

        # Start state saver
        if self.persistence_enabled:
            asyncio.create_task(self._state_saver())

        # Start health monitor
        asyncio.create_task(self._health_monitor())

        self.logger.info("Neural Bus started successfully")

    async def stop(self):
        """Stop the neural bus service"""
        self.running = False
        self._save_state()
        self.logger.info("Neural Bus stopped")

    async def _message_processor(self):
        """Process messages from queue"""
        while self.running:
            if self.message_queue:
                message = self.message_queue.pop(0)
                await self._process_message(message)

            await asyncio.sleep(0.01)  # Small delay to prevent busy loop

    async def _state_saver(self):
        """Periodically save state to disk"""
        while self.running:
            await asyncio.sleep(60)  # Save every minute
            self._save_state()

    async def _health_monitor(self):
        """Monitor component health and send heartbeats"""
        while self.running:
            try:
                # Check for stale components
                now = datetime.now()
                for comp_type, status in list(self.components.items()):
                    if (now - status.last_heartbeat).total_seconds() > 120:  # 2 minutes
                        status.healthy = False
                        await self._broadcast_message(MessageType.HEALTH_STATUS, {
                            "component": comp_type.value,
                            "healthy": False,
                            "timestamp": now.isoformat()
                        })

                # Send heartbeat from neural bus
                await self._broadcast_message(MessageType.HEARTBEAT, {
                    "component": "neural_bus",
                    "timestamp": now.isoformat(),
                    "queue_size": len(self.message_queue),
                    "active_components": len([c for c in self.components.values() if c.healthy])
                })

            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")

            await asyncio.sleep(30)  # Check every 30 seconds

# =============================================================================
# QUANTUM COHERENCE INTEGRATION
# =============================================================================

class QuantumCoherenceMonitor:
    """Monitor quantum coherence across the stack"""

    def __init__(self, neural_bus: NeuralBus):
        self.neural_bus = neural_bus
        self.qei_history: List[float] = []
        self.coherence_metrics = {}

        # Subscribe to relevant messages
        neural_bus.subscribe(MessageType.QEI_UPDATE, self._handle_qei_update)
        neural_bus.subscribe(MessageType.HEALTH_STATUS, self._handle_health_status)
        neural_bus.subscribe(MessageType.QUANTUM_COHERENCE, self._handle_quantum_coherence)

    async def _handle_qei_update(self, message: Message):
        """Handle QEI updates from components"""
        qei_value = message.payload.get('qei_value', 0.0)
        self.qei_history.append(qei_value)

        # Keep only last 100 values
        if len(self.qei_history) > 100:
            self.qei_history = self.qei_history[-100:]

        # Calculate system-wide QEI
        system_qei = sum(self.qei_history[-10:]) / len(self.qei_history[-10:]) if self.qei_history else 0.0

        # Broadcast system coherence update
        await self.neural_bus._broadcast_message(MessageType.QUANTUM_COHERENCE, {
            "system_qei": system_qei,
            "component_qei": qei_value,
            "source": message.source.value,
            "timestamp": datetime.now().isoformat()
        })

    async def _handle_health_status(self, message: Message):
        """Handle health status updates"""
        component = message.payload.get('component')
        healthy = message.payload.get('healthy', False)

        # Update coherence metrics
        self.coherence_metrics[component] = {
            'healthy': healthy,
            'last_update': message.payload.get('timestamp'),
            'consecutive_healthy': self.coherence_metrics.get(component, {}).get('consecutive_healthy', 0) + (1 if healthy else 0)
        }

    async def _handle_quantum_coherence(self, message: Message):
        """Handle quantum coherence messages"""
        # Store coherence data for analysis
        coherence_data = message.payload
        self.coherence_metrics[f"{message.source.value}_coherence"] = coherence_data

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main entry point"""
    neural_bus = NeuralBus()
    coherence_monitor = QuantumCoherenceMonitor(neural_bus)

    await neural_bus.start()

    try:
        # Run the FastAPI app
        config = uvicorn.Config(
            app=neural_bus.app,
            host="localhost",
            port=int(os.getenv('NEURAL_BUS_PORT', 9000)),
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        await neural_bus.stop()

if __name__ == "__main__":
    asyncio.run(main())