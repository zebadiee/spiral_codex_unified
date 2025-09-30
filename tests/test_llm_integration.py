"""
Tests for LLM Integration in Spiral Codex
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.spiralcodex.llm import (
    LLMConfig,
    RouteLLMClient,
    MockRouteLLMClient,
    create_llm_client,
    LLMAgent,
    ContextRitualKnowledgeAgent,
    AgentOrchestrator,
    LLMEventEmitter,
    HUDIntegration,
    get_global_event_emitter
)


class TestLLMConfig:
    """Test LLM configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LLMConfig()
        
        assert config.routers == ["mf"]
        assert config.strong_model == "gpt-4-1106-preview"
        assert config.weak_model == "gpt-3.5-turbo"
        assert config.threshold == 0.11593
        assert config.enable_ritual_context is True
        assert config.max_context_length == 4000
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
    
    def test_config_to_dict(self):
        """Test configuration serialization"""
        config = LLMConfig(
            routers=["bert"],
            strong_model="gpt-4",
            weak_model="gpt-3.5-turbo",
            threshold=0.5
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["routers"] == ["bert"]
        assert config_dict["strong_model"] == "gpt-4"
        assert config_dict["threshold"] == 0.5


class TestMockRouteLLMClient:
    """Test mock LLM client"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client for testing"""
        config = LLMConfig()
        return MockRouteLLMClient(config)
    
    def test_mock_client_initialization(self, mock_client):
        """Test mock client initialization"""
        assert mock_client.is_initialized is True
        assert isinstance(mock_client.config, LLMConfig)
    
    @pytest.mark.asyncio
    async def test_context_to_ritual(self, mock_client):
        """Test context to ritual transformation"""
        context = {
            "user_query": "What is consciousness?",
            "test_mode": True
        }
        
        result = await mock_client.context_to_ritual(context)
        
        assert "ritual_instructions" in result
        assert "context_hash" in result
        assert "timestamp" in result
        assert "model_used" in result
        assert "tokens_used" in result
        assert result["model_used"] == "mock-model"
        assert result["tokens_used"] == 42
    
    @pytest.mark.asyncio
    async def test_ritual_to_knowledge(self, mock_client):
        """Test ritual to knowledge transformation"""
        ritual = {
            "ritual_instructions": "Mock ritual instructions",
            "context_hash": 12345,
            "timestamp": datetime.utcnow().isoformat()
        }
        query = "What is the meaning of life?"
        
        result = await mock_client.ritual_to_knowledge(ritual, query)
        
        assert "knowledge_response" in result
        assert "ritual_hash" in result
        assert "query" in result
        assert "timestamp" in result
        assert result["query"] == query
        assert result["ritual_hash"] == 12345
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, mock_client):
        """Test complete workflow"""
        context = {"user_query": "Test query"}
        query = "Test query"
        
        result = await mock_client.full_workflow(context, query)
        
        assert "workflow_complete" in result
        assert "context" in result
        assert "ritual" in result
        assert "knowledge" in result
        assert "total_duration" in result
        assert result["workflow_complete"] is True


class TestLLMAgent:
    """Test LLM agent functionality"""
    
    @pytest.fixture
    def mock_event_emitter(self):
        """Create mock event emitter"""
        emitter = Mock(spec=LLMEventEmitter)
        emitter.emit_agent_event = AsyncMock()
        return emitter
    
    @pytest.fixture
    def llm_agent(self, mock_event_emitter):
        """Create LLM agent for testing"""
        config = LLMConfig()
        return LLMAgent("test_agent", config, mock_event_emitter)
    
    def test_agent_initialization(self, llm_agent):
        """Test agent initialization"""
        assert llm_agent.agent_id == "test_agent"
        assert llm_agent.is_active is False
        assert len(llm_agent.context_history) == 0
    
    @pytest.mark.asyncio
    async def test_agent_activation(self, llm_agent, mock_event_emitter):
        """Test agent activation"""
        await llm_agent.activate()
        
        assert llm_agent.is_active is True
        mock_event_emitter.emit_agent_event.assert_called_once()
        
        # Check event call
        call_args = mock_event_emitter.emit_agent_event.call_args
        assert call_args[0][0] == "test_agent"  # agent_id
        assert call_args[0][1] == "agent_activated"  # event_type
    
    @pytest.mark.asyncio
    async def test_agent_deactivation(self, llm_agent, mock_event_emitter):
        """Test agent deactivation"""
        await llm_agent.activate()
        await llm_agent.deactivate()
        
        assert llm_agent.is_active is False
        assert mock_event_emitter.emit_agent_event.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_query_inactive_agent(self, llm_agent):
        """Test processing query with inactive agent"""
        result = await llm_agent.process_query("test query")
        
        assert "error" in result
        assert result["error"] == "Agent not active"
        assert result["agent_id"] == "test_agent"
    
    @pytest.mark.asyncio
    async def test_process_query_active_agent(self, llm_agent, mock_event_emitter):
        """Test processing query with active agent"""
        await llm_agent.activate()
        
        result = await llm_agent.process_query(
            "What is consciousness?",
            mesh_state={"nodes": 3},
            session_data={"session_id": "test"}
        )
        
        assert "agent_id" in result
        assert "query" in result
        assert "result" in result
        assert "context" in result
        assert result["agent_id"] == "test_agent"
        assert result["query"] == "What is consciousness?"
        
        # Check context history
        assert len(llm_agent.context_history) == 1
        context = llm_agent.context_history[0]
        assert context.agent_id == "test_agent"
        assert context.user_query == "What is consciousness?"
        assert context.mesh_state == {"nodes": 3}
    
    @pytest.mark.asyncio
    async def test_get_status(self, llm_agent):
        """Test getting agent status"""
        status = await llm_agent.get_status()
        
        assert "agent_id" in status
        assert "is_active" in status
        assert "llm_status" in status
        assert "context_history_length" in status
        assert status["agent_id"] == "test_agent"
        assert status["is_active"] is False
        assert status["context_history_length"] == 0


class TestContextRitualKnowledgeAgent:
    """Test enhanced agent with consciousness patterns"""
    
    @pytest.fixture
    def enhanced_agent(self):
        """Create enhanced agent for testing"""
        config = LLMConfig()
        consciousness_patterns = ["test_pattern_1", "test_pattern_2"]
        return ContextRitualKnowledgeAgent(
            "enhanced_agent",
            config,
            consciousness_patterns=consciousness_patterns
        )
    
    def test_enhanced_agent_initialization(self, enhanced_agent):
        """Test enhanced agent initialization"""
        assert enhanced_agent.agent_id == "enhanced_agent"
        assert enhanced_agent.consciousness_patterns == ["test_pattern_1", "test_pattern_2"]
        assert len(enhanced_agent.ritual_cache) == 0
    
    @pytest.mark.asyncio
    async def test_enhanced_context_analysis(self, enhanced_agent):
        """Test enhanced context analysis"""
        from src.spiralcodex.llm.agents import AgentContext
        
        context = AgentContext(
            agent_id="enhanced_agent",
            mesh_state={"test": "data"},
            user_query="Test query",
            session_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        
        result = await enhanced_agent.enhanced_context_analysis(context)
        
        assert "enhanced_analysis" in result
        assert "consciousness_patterns" in result
        assert "timestamp" in result
        assert result["consciousness_patterns"] == ["test_pattern_1", "test_pattern_2"]
    
    @pytest.mark.asyncio
    async def test_get_ritual_cache_status(self, enhanced_agent):
        """Test ritual cache status"""
        status = await enhanced_agent.get_ritual_cache_status()
        
        assert "cache_size" in status
        assert "cached_rituals" in status
        assert "consciousness_patterns" in status
        assert status["cache_size"] == 0
        assert status["consciousness_patterns"] == ["test_pattern_1", "test_pattern_2"]


class TestAgentOrchestrator:
    """Test agent orchestrator"""
    
    @pytest.fixture
    def mock_event_emitter(self):
        """Create mock event emitter"""
        emitter = Mock(spec=LLMEventEmitter)
        emitter.emit_orchestration_event = AsyncMock()
        return emitter
    
    @pytest.fixture
    def orchestrator(self, mock_event_emitter):
        """Create orchestrator for testing"""
        return AgentOrchestrator(mock_event_emitter)
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent"""
        agent = Mock(spec=LLMAgent)
        agent.agent_id = "mock_agent"
        agent.is_active = False
        agent.activate = AsyncMock()
        agent.deactivate = AsyncMock()
        agent.process_query = AsyncMock(return_value={"result": "mock_result"})
        agent.get_status = AsyncMock(return_value={"status": "mock_status"})
        return agent
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert len(orchestrator.agents) == 0
        assert len(orchestrator.active_sessions) == 0
    
    def test_register_agent(self, orchestrator, mock_agent):
        """Test agent registration"""
        orchestrator.register_agent(mock_agent)
        
        assert "mock_agent" in orchestrator.agents
        assert orchestrator.agents["mock_agent"] == mock_agent
    
    def test_unregister_agent(self, orchestrator, mock_agent):
        """Test agent unregistration"""
        orchestrator.register_agent(mock_agent)
        orchestrator.unregister_agent("mock_agent")
        
        assert "mock_agent" not in orchestrator.agents
    
    @pytest.mark.asyncio
    async def test_activate_agent(self, orchestrator, mock_agent):
        """Test agent activation through orchestrator"""
        orchestrator.register_agent(mock_agent)
        
        result = await orchestrator.activate_agent("mock_agent")
        
        assert result is True
        mock_agent.activate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_activate_nonexistent_agent(self, orchestrator):
        """Test activating non-existent agent"""
        result = await orchestrator.activate_agent("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_route_query_no_agents(self, orchestrator, mock_event_emitter):
        """Test routing query with no active agents"""
        result = await orchestrator.route_query("test query")
        
        assert "error" in result
        assert result["error"] == "No active agents available"
    
    @pytest.mark.asyncio
    async def test_route_query_with_active_agent(self, orchestrator, mock_agent, mock_event_emitter):
        """Test routing query to active agent"""
        mock_agent.is_active = True
        orchestrator.register_agent(mock_agent)
        
        result = await orchestrator.route_query(
            "test query",
            session_id="test_session"
        )
        
        assert result == {"result": "mock_result"}
        mock_agent.process_query.assert_called_once()
        mock_event_emitter.emit_orchestration_event.assert_called_once()
        
        # Check session tracking
        assert "test_session" in orchestrator.active_sessions
        session_data = orchestrator.active_sessions["test_session"]
        assert len(session_data["queries"]) == 1
        assert session_data["queries"][0]["query"] == "test query"
    
    @pytest.mark.asyncio
    async def test_get_orchestrator_status(self, orchestrator, mock_agent):
        """Test getting orchestrator status"""
        mock_agent.is_active = True
        orchestrator.register_agent(mock_agent)
        orchestrator.active_sessions["session1"] = {}
        
        status = await orchestrator.get_orchestrator_status()
        
        assert "total_agents" in status
        assert "active_agents" in status
        assert "active_sessions" in status
        assert "agent_statuses" in status
        assert status["total_agents"] == 1
        assert status["active_agents"] == 1
        assert status["active_sessions"] == 1


class TestLLMEventEmitter:
    """Test LLM event system"""
    
    @pytest.fixture
    def event_emitter(self):
        """Create event emitter for testing"""
        return LLMEventEmitter()
    
    def test_event_emitter_initialization(self, event_emitter):
        """Test event emitter initialization"""
        assert len(event_emitter.event_handlers) == 0
        assert len(event_emitter.event_history) == 0
        assert len(event_emitter.websocket_clients) == 0
        assert event_emitter.max_history == 1000
    
    def test_add_handler(self, event_emitter):
        """Test adding event handler"""
        def test_handler(event):
            pass
        
        event_emitter.add_handler("test_event", test_handler)
        
        assert "test_event" in event_emitter.event_handlers
        assert test_handler in event_emitter.event_handlers["test_event"]
    
    def test_remove_handler(self, event_emitter):
        """Test removing event handler"""
        def test_handler(event):
            pass
        
        event_emitter.add_handler("test_event", test_handler)
        event_emitter.remove_handler("test_event", test_handler)
        
        assert test_handler not in event_emitter.event_handlers.get("test_event", [])
    
    @pytest.mark.asyncio
    async def test_emit_agent_event(self, event_emitter):
        """Test emitting agent event"""
        handler_called = False
        
        def test_handler(event):
            nonlocal handler_called
            handler_called = True
            assert event.agent_id == "test_agent"
            assert event.event_type == "agent_test_event"
        
        event_emitter.add_handler("agent_test_event", test_handler)
        
        await event_emitter.emit_agent_event(
            "test_agent",
            "test_event",
            {"test": "data"}
        )
        
        assert handler_called
        assert len(event_emitter.event_history) == 1
        
        event = event_emitter.event_history[0]
        assert event.agent_id == "test_agent"
        assert event.event_type == "agent_test_event"
        assert event.data == {"test": "data"}
    
    def test_get_event_history(self, event_emitter):
        """Test getting event history"""
        # Add some test events manually
        from src.spiralcodex.llm.events import LLMEvent
        
        event1 = LLMEvent("test_event", "agent1", {"data": 1}, datetime.utcnow().isoformat())
        event2 = LLMEvent("test_event", "agent2", {"data": 2}, datetime.utcnow().isoformat())
        event3 = LLMEvent("other_event", "agent1", {"data": 3}, datetime.utcnow().isoformat())
        
        event_emitter.event_history = [event1, event2, event3]
        
        # Test filtering by event type
        filtered = event_emitter.get_event_history(event_type="test_event")
        assert len(filtered) == 2
        
        # Test filtering by agent
        filtered = event_emitter.get_event_history(agent_id="agent1")
        assert len(filtered) == 2
        
        # Test limit
        filtered = event_emitter.get_event_history(limit=1)
        assert len(filtered) == 1
    
    def test_get_event_statistics(self, event_emitter):
        """Test getting event statistics"""
        from src.spiralcodex.llm.events import LLMEvent
        
        event1 = LLMEvent("test_event", "agent1", {}, datetime.utcnow().isoformat())
        event2 = LLMEvent("test_event", "agent2", {}, datetime.utcnow().isoformat())
        event3 = LLMEvent("other_event", "agent1", {}, datetime.utcnow().isoformat())
        
        event_emitter.event_history = [event1, event2, event3]
        
        stats = event_emitter.get_event_statistics()
        
        assert stats["total_events"] == 3
        assert stats["event_types"]["test_event"] == 2
        assert stats["event_types"]["other_event"] == 1
        assert stats["agents"]["agent1"] == 2
        assert stats["agents"]["agent2"] == 1


class TestHUDIntegration:
    """Test HUD integration"""
    
    @pytest.fixture
    def hud_integration(self):
        """Create HUD integration for testing"""
        event_emitter = LLMEventEmitter()
        return HUDIntegration(event_emitter)
    
    def test_hud_integration_initialization(self, hud_integration):
        """Test HUD integration initialization"""
        assert len(hud_integration.hud_overlays) == 0
        assert isinstance(hud_integration.event_emitter, LLMEventEmitter)
    
    def test_get_hud_overlays(self, hud_integration):
        """Test getting HUD overlays"""
        # Add test overlay
        hud_integration.hud_overlays["test_overlay"] = {"type": "test", "data": "test"}
        
        overlays = hud_integration.get_hud_overlays()
        
        assert "llm_overlays" in overlays
        assert "overlay_count" in overlays
        assert "timestamp" in overlays
        assert overlays["overlay_count"] == 1
        assert "test_overlay" in overlays["llm_overlays"]
    
    def test_clear_overlay(self, hud_integration):
        """Test clearing specific overlay"""
        hud_integration.hud_overlays["test_overlay"] = {"type": "test"}
        hud_integration.clear_overlay("test_overlay")
        
        assert "test_overlay" not in hud_integration.hud_overlays
    
    def test_clear_all_overlays(self, hud_integration):
        """Test clearing all overlays"""
        hud_integration.hud_overlays["overlay1"] = {"type": "test1"}
        hud_integration.hud_overlays["overlay2"] = {"type": "test2"}
        
        hud_integration.clear_all_overlays()
        
        assert len(hud_integration.hud_overlays) == 0


class TestClientFactory:
    """Test LLM client factory function"""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    def test_create_llm_client_with_routellm(self):
        """Test creating client when RouteLLM is available"""
        config = LLMConfig()
        
        # Mock RouteLLM availability
        with patch('src.spiralcodex.llm.router.ROUTELLM_AVAILABLE', True):
            client = create_llm_client(config)
            assert isinstance(client, RouteLLMClient)
    
    def test_create_llm_client_without_routellm(self):
        """Test creating client when RouteLLM is not available"""
        config = LLMConfig()
        
        # Mock RouteLLM unavailability
        with patch('src.spiralcodex.llm.router.ROUTELLM_AVAILABLE', False):
            client = create_llm_client(config)
            assert isinstance(client, MockRouteLLMClient)
    
    def test_create_llm_client_default_config(self):
        """Test creating client with default config"""
        client = create_llm_client()
        assert client is not None
        assert isinstance(client.config, LLMConfig)


if __name__ == "__main__":
    pytest.main([__file__])
