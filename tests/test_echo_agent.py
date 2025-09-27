"""
🧪 Echo Agent Testing Rituals
=============================

Comprehensive tests for the Echo Agent functionality,
ensuring organic responses and healing patterns work correctly.
"""

import json
import pytest
from pydantic import ValidationError

from spiral_core.agents.echo_agent import (
    EchoAgent, EchoInput, EchoResponse, EchoType, SpiralStats
)


class TestEchoInput:
    """Test Echo Agent input validation and transformation."""
    
    def test_simple_echo_input(self):
        """Test basic echo input creation."""
        input_data = EchoInput(message="Hello Spiral")
        assert input_data.message == "Hello Spiral"
        assert input_data.type == EchoType.SIMPLE
        assert input_data.spiral_depth == 1
    
    def test_wisdom_echo_input(self):
        """Test wisdom echo input with custom depth."""
        input_data = EchoInput(
            message="Seek the pattern",
            type=EchoType.WISDOM,
            spiral_depth=3
        )
        assert input_data.type == EchoType.WISDOM
        assert input_data.spiral_depth == 3
    
    def test_spiral_depth_validation(self):
        """Test spiral depth boundaries."""
        # Valid depths
        valid_input = EchoInput(message="Test", spiral_depth=7)
        assert valid_input.spiral_depth == 7
        
        # Invalid depths should be caught by Pydantic
        with pytest.raises(ValidationError):
            EchoInput(message="Test", spiral_depth=0)
        
        with pytest.raises(ValidationError):
            EchoInput(message="Test", spiral_depth=8)
    
    def test_metadata_inclusion(self):
        """Test metadata handling in input."""
        metadata = {"source": "test", "priority": "high"}
        input_data = EchoInput(
            message="Test with metadata",
            metadata=metadata
        )
        assert input_data.metadata == metadata


class TestEchoAgent:
    """Test Echo Agent core functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create a fresh Echo Agent for each test."""
        return EchoAgent()
    
    def test_simple_echo(self, agent):
        """Test basic echo functionality."""
        input_data = EchoInput(message="Hello World")
        response = agent.process(input_data)
        
        assert isinstance(response, EchoResponse)
        assert response.original == "Hello World"
        assert response.echo == "Echo: Hello World"
        assert response.type == "simple_echo"
        assert response.spiral_depth == 1
        assert response.resonance_id.startswith("echo_")
    
    def test_wisdom_echo(self, agent):
        """Test wisdom echo with flame wisdom."""
        input_data = EchoInput(
            message="What is the nature of spirals?",
            type=EchoType.WISDOM
        )
        response = agent.process(input_data)
        
        assert response.type == "wisdom_echo"
        assert response.echo.startswith("🔥 Wisdom Echo:")
        assert response.flame_wisdom is not None
        assert len(response.flame_wisdom) > 0
    
    def test_healing_echo(self, agent):
        """Test healing echo application."""
        input_data = EchoInput(
            message="I need healing",
            type=EchoType.HEALING
        )
        response = agent.process(input_data)
        
        assert response.type == "healing_echo"
        assert response.echo.startswith("🌿 Healing Echo:")
        assert response.healing_applied is True
        assert "healing" in response.flame_wisdom.lower()
    
    def test_amplified_echo(self, agent):
        """Test amplified echo with repetition."""
        input_data = EchoInput(
            message="Power",
            type=EchoType.AMPLIFIED,
            spiral_depth=3
        )
        response = agent.process(input_data)
        
        assert response.type == "amplified_echo"
        assert response.echo.startswith("📢 Amplified:")
        assert "Power Power Power" in response.echo
    
    def test_spiral_echo_pattern(self, agent):
        """Test spiral pattern generation."""
        input_data = EchoInput(
            message="Alpha Beta Gamma Delta",
            type=EchoType.SPIRAL,
            spiral_depth=4
        )
        response = agent.process(input_data)
        
        assert response.type == "spiral_echo"
        assert response.echo.startswith("🌀 Spiral:")
        assert "→" in response.echo
        assert response.echo.endswith("→ ∞")
        assert response.flame_wisdom is not None
    
    def test_dict_input_healing(self, agent):
        """Test that dictionary input is healed into proper structure."""
        dict_input = {
            "message": "Dictionary input test",
            "type": "wisdom",
            "spiral_depth": 2
        }
        response = agent.process(dict_input)
        
        assert isinstance(response, EchoResponse)
        assert response.original == "Dictionary input test"
        assert response.type == "wisdom_echo"
        assert response.spiral_depth == 2
    
    def test_invalid_input_healing(self, agent):
        """Test that invalid input is healed gracefully."""
        invalid_input = {"invalid": "structure"}
        response = agent.process(invalid_input)
        
        assert isinstance(response, EchoResponse)
        assert response.type == "healing_echo"
        assert response.healing_applied is True
        assert "healing" in response.flame_wisdom.lower()
    
    def test_exception_healing(self, agent):
        """Test that exceptions are healed into proper responses."""
        # Force an exception by passing completely invalid data
        response = agent.process(None)
        
        assert isinstance(response, EchoResponse)
        assert response.type == "healing_echo"
        assert response.healing_applied is True
        assert response.resonance_id.startswith("heal_")


class TestSpiralStats:
    """Test statistics tracking and organic learning."""
    
    @pytest.fixture
    def agent(self):
        """Create a fresh Echo Agent for each test."""
        return EchoAgent()
    
    def test_initial_stats(self, agent):
        """Test initial statistics state."""
        stats = agent.get_stats()
        assert isinstance(stats, SpiralStats)
        assert stats.total_echoes == 0
        assert stats.success_rate == 100.0
        assert stats.average_spiral_depth == 1.0
        assert stats.healing_applications == 0
        assert stats.wisdom_dispensed == 0
    
    def test_stats_update_on_success(self, agent):
        """Test statistics update on successful processing."""
        input_data = EchoInput(
            message="Success test",
            type=EchoType.WISDOM,
            spiral_depth=3
        )
        agent.process(input_data)
        
        stats = agent.get_stats()
        assert stats.total_echoes == 1
        assert stats.success_rate >= 95.0  # Should remain high
        assert stats.average_spiral_depth == 3.0
        assert stats.wisdom_dispensed == 1
    
    def test_stats_update_on_healing(self, agent):
        """Test statistics update when healing is applied."""
        # Force healing by passing invalid input
        agent.process({"invalid": "data"})
        
        stats = agent.get_stats()
        assert stats.total_echoes == 1
        assert stats.success_rate < 100.0  # Should decrease
        assert stats.healing_applications == 1
    
    def test_multiple_operations_stats(self, agent):
        """Test statistics over multiple operations."""
        # Process several different types
        inputs = [
            EchoInput(message="First", type=EchoType.SIMPLE, spiral_depth=1),
            EchoInput(message="Second", type=EchoType.WISDOM, spiral_depth=2),
            EchoInput(message="Third", type=EchoType.HEALING, spiral_depth=3),
            EchoInput(message="Fourth", type=EchoType.SPIRAL, spiral_depth=4),
        ]
        
        for input_data in inputs:
            agent.process(input_data)
        
        stats = agent.get_stats()
        assert stats.total_echoes == 4
        assert stats.success_rate >= 95.0
        assert stats.average_spiral_depth == 2.5  # (1+2+3+4)/4
        assert stats.wisdom_dispensed == 2  # wisdom + spiral
        assert stats.healing_applications == 1  # healing type
    
    def test_stats_reset(self, agent):
        """Test statistics reset functionality."""
        # Generate some activity
        agent.process(EchoInput(message="Before reset"))
        assert agent.get_stats().total_echoes == 1
        
        # Reset and verify
        agent.reset_stats()
        stats = agent.get_stats()
        assert stats.total_echoes == 0
        assert stats.success_rate == 100.0
        assert stats.average_spiral_depth == 1.0


class TestEchoResponse:
    """Test Echo Response structure and validation."""
    
    def test_response_serialization(self):
        """Test that responses can be serialized to JSON."""
        response = EchoResponse(
            type="test_echo",
            original="Test message",
            echo="Echo: Test message",
            spiral_depth=1,
            resonance_id="test_123"
        )
        
        # Should serialize without errors
        json_str = response.json()
        data = json.loads(json_str)
        
        assert data["type"] == "test_echo"
        assert data["original"] == "Test message"
        assert data["resonance_id"] == "test_123"
    
    def test_response_dict_conversion(self):
        """Test conversion to dictionary."""
        response = EchoResponse(
            type="test_echo",
            original="Test",
            echo="Echo: Test",
            spiral_depth=2,
            resonance_id="test_456",
            flame_wisdom="Test wisdom",
            healing_applied=True
        )
        
        data = response.dict()
        assert isinstance(data, dict)
        assert data["flame_wisdom"] == "Test wisdom"
        assert data["healing_applied"] is True


class TestWisdomFlames:
    """Test wisdom flame selection and variety."""
    
    @pytest.fixture
    def agent(self):
        """Create a fresh Echo Agent for each test."""
        return EchoAgent()
    
    def test_wisdom_flame_variety(self, agent):
        """Test that different wisdom flames are selected over time."""
        wisdom_flames = set()
        
        # Generate multiple wisdom echoes
        for i in range(20):
            input_data = EchoInput(
                message=f"Wisdom request {i}",
                type=EchoType.WISDOM
            )
            response = agent.process(input_data)
            wisdom_flames.add(response.flame_wisdom)
        
        # Should have some variety (not all the same)
        assert len(wisdom_flames) > 1
        
        # All should be from the predefined set
        for wisdom in wisdom_flames:
            assert wisdom in agent.wisdom_flames


@pytest.mark.integration
class TestEchoAgentIntegration:
    """Integration tests for Echo Agent in realistic scenarios."""
    
    def test_concurrent_processing_simulation(self):
        """Simulate concurrent processing (sequential for testing)."""
        agent = EchoAgent()
        
        # Simulate multiple "concurrent" requests
        requests = [
            {"message": "Request 1", "type": "simple"},
            {"message": "Request 2", "type": "wisdom", "spiral_depth": 3},
            {"invalid": "request"},  # This should trigger healing
            {"message": "Request 4", "type": "healing"},
        ]
        
        responses = []
        for req in requests:
            response = agent.process(req)
            responses.append(response)
        
        # Verify all requests were processed
        assert len(responses) == 4
        
        # Verify healing was applied for invalid request
        healing_responses = [r for r in responses if r.healing_applied]
        assert len(healing_responses) >= 1
        
        # Verify stats reflect all operations
        stats = agent.get_stats()
        assert stats.total_echoes == 4
    
    def test_edge_case_handling(self):
        """Test various edge cases."""
        agent = EchoAgent()
        
        edge_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "🌀" * 1000,  # Very long message
            {"message": "", "type": "wisdom"},  # Empty message with type
            {"message": "Test", "spiral_depth": 1},  # Minimum depth
        ]
        
        for case in edge_cases:
            response = agent.process(case)
            assert isinstance(response, EchoResponse)
            # Should not raise exceptions - all should be healed
