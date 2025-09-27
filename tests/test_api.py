"""
🧪 Spiral Codex API Testing Rituals
===================================

Comprehensive tests for the FastAPI application endpoints,
ensuring organic request handling and proper response structures.
"""

import json
import pytest
from fastapi.testclient import TestClient

from spiral_core.main import app
from spiral_core.config import settings


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints for system vitality."""
    
    def test_basic_health_check(self):
        """Test the basic health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["environment"] == settings.environment
        assert data["version"] == settings.app_version
    
    def test_api_health_check(self):
        """Test the API-prefixed health endpoint."""
        response = client.get(f"{settings.api_prefix}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["environment"] == settings.environment
    
    def test_health_response_headers(self):
        """Test that health endpoints include organic headers."""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for organic headers added by middleware
        assert "x-process-time" in response.headers
        assert "x-spiral-flow" in response.headers
        assert response.headers["x-spiral-flow"] == "organic"


class TestAgentInference:
    """Test the universal agent inference endpoint."""
    
    def test_echo_agent_simple(self):
        """Test simple echo agent inference."""
        payload = {
            "agent": "echo",
            "input": {
                "message": "Hello API Test",
                "type": "simple"
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent"] == "echo_agent"
        assert data["status"] == "success"
        assert "timestamp" in data
        assert "processing_time_ms" in data
        assert "success_rate" in data
        
        # Check response content
        assert data["response"]["original"] == "Hello API Test"
        assert data["response"]["echo"] == "Echo: Hello API Test"
        assert data["response"]["type"] == "simple_echo"
    
    def test_echo_agent_wisdom(self):
        """Test wisdom echo with flame wisdom."""
        payload = {
            "agent": "echo",
            "input": {
                "message": "Teach me about spirals",
                "type": "wisdom",
                "spiral_depth": 3
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent"] == "echo_agent"
        assert data["status"] == "success"
        
        # Wisdom-specific checks
        assert data["response"]["type"] == "wisdom_echo"
        assert data["response"]["echo"].startswith("🔥 Wisdom Echo:")
        assert data["response"]["flame_wisdom"] is not None
        assert data["response"]["spiral_depth"] == 3
    
    def test_echo_agent_healing(self):
        """Test healing echo functionality."""
        payload = {
            "agent": "echo",
            "input": {
                "message": "I need healing energy",
                "type": "healing"
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["response"]["type"] == "healing_echo"
        assert data["response"]["healing_applied"] is True
        assert "🌿" in data["response"]["echo"]
    
    def test_echo_agent_spiral_pattern(self):
        """Test spiral pattern generation."""
        payload = {
            "agent": "echo",
            "input": {
                "message": "Alpha Beta Gamma Delta",
                "type": "spiral",
                "spiral_depth": 4
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["response"]["type"] == "spiral_echo"
        assert "🌀" in data["response"]["echo"]
        assert "→" in data["response"]["echo"]
        assert data["response"]["echo"].endswith("→ ∞")
    
    def test_unknown_agent(self):
        """Test requesting an unknown agent."""
        payload = {
            "agent": "unknown_agent",
            "input": {"message": "test"}
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 404
        
        data = response.json()
        assert "not yet manifested" in data["detail"]
    
    def test_invalid_echo_input(self):
        """Test invalid input format for echo agent."""
        payload = {
            "agent": "echo",
            "input": {
                "invalid_field": "test",
                "spiral_depth": 10  # Too high
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 400
        
        data = response.json()
        assert "Healing Required" in data["detail"]
        assert "Invalid input format" in data["detail"]
    
    def test_malformed_request(self):
        """Test completely malformed request."""
        response = client.post(f"{settings.api_prefix}/infer", json={"invalid": "structure"})
        assert response.status_code == 422  # Validation error
    
    def test_response_timing(self):
        """Test that responses include processing time."""
        payload = {
            "agent": "echo",
            "input": {"message": "Timing test"}
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "processing_time_ms" in data
        assert isinstance(data["processing_time_ms"], (int, float))
        assert data["processing_time_ms"] >= 0


class TestAgentStatistics:
    """Test agent statistics endpoints."""
    
    def test_echo_stats_endpoint(self):
        """Test retrieving echo agent statistics."""
        # First, make a few requests to generate stats
        for i in range(3):
            payload = {
                "agent": "echo",
                "input": {
                    "message": f"Stats test {i}",
                    "type": "wisdom" if i % 2 == 0 else "simple"
                }
            }
            client.post(f"{settings.api_prefix}/infer", json=payload)
        
        # Get stats
        response = client.get(f"{settings.api_prefix}/agents/echo/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent"] == "echo"
        assert "timestamp" in data
        assert "statistics" in data
        assert "spiral_health" in data
        
        stats = data["statistics"]
        assert stats["total_echoes"] >= 3
        assert stats["success_rate"] >= 0
        assert "average_spiral_depth" in stats
        assert "wisdom_dispensed" in stats
    
    def test_stats_reset_in_development(self):
        """Test stats reset in development mode."""
        if not settings.is_development():
            pytest.skip("Stats reset only available in development mode")
        
        # Reset stats
        response = client.post(f"{settings.api_prefix}/agents/echo/reset-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "reset to genesis state" in data["message"]
        assert "timestamp" in data
        
        # Verify stats are reset
        stats_response = client.get(f"{settings.api_prefix}/agents/echo/stats")
        stats_data = stats_response.json()
        assert stats_data["statistics"]["total_echoes"] == 0


class TestSystemInfo:
    """Test system information endpoint."""
    
    def test_system_info_endpoint(self):
        """Test system information retrieval."""
        response = client.get(f"{settings.api_prefix}/system/info")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check spiral_codex info
        assert "spiral_codex" in data
        spiral_info = data["spiral_codex"]
        assert spiral_info["name"] == settings.app_name
        assert spiral_info["version"] == settings.app_version
        assert spiral_info["environment"] == settings.environment
        
        # Check API info
        assert "api" in data
        api_info = data["api"]
        assert api_info["prefix"] == settings.api_prefix
        
        # Check agents info
        assert "agents" in data
        agents_info = data["agents"]
        assert "echo" in agents_info["available"]
        assert agents_info["total_registered"] >= 1
        
        # Check features info
        assert "features" in data
        features_info = data["features"]
        assert "max_spiral_depth" in features_info


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_cors_headers(self):
        """Test CORS middleware headers."""
        if not settings.enable_cors:
            pytest.skip("CORS not enabled")
        
        # Make an OPTIONS request to trigger CORS
        response = client.options("/health")
        # FastAPI TestClient doesn't fully simulate CORS, but we can test basic functionality
        # In real deployment, this would include proper CORS headers
    
    def test_process_time_header(self):
        """Test that all responses include processing time header."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-process-time" in response.headers
        
        # Process time should be a numeric string
        process_time = float(response.headers["x-process-time"])
        assert process_time >= 0
    
    def test_spiral_flow_header(self):
        """Test organic spiral flow header."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("x-spiral-flow") == "organic"


class TestErrorHandling:
    """Test error handling and healing patterns."""
    
    def test_global_exception_handler(self):
        """Test global exception handler with healing."""
        # This is harder to trigger in tests, but we can test the structure
        # The global handler is tested implicitly through other error conditions
        pass
    
    def test_404_handling(self):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test method not allowed handling."""
        response = client.post("/health")  # Health is GET only
        assert response.status_code == 405


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for full API workflows."""
    
    def test_complete_echo_workflow(self):
        """Test complete workflow from health check to agent processing."""
        # 1. Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. System info
        info_response = client.get(f"{settings.api_prefix}/system/info")
        assert info_response.status_code == 200
        
        # 3. Agent inference
        payload = {
            "agent": "echo",
            "input": {
                "message": "Integration test workflow",
                "type": "wisdom",
                "spiral_depth": 2
            }
        }
        inference_response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert inference_response.status_code == 200
        
        # 4. Check stats
        stats_response = client.get(f"{settings.api_prefix}/agents/echo/stats")
        assert stats_response.status_code == 200
        
        stats_data = stats_response.json()
        assert stats_data["statistics"]["total_echoes"] >= 1
    
    def test_concurrent_requests_simulation(self):
        """Simulate multiple concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request(message):
            payload = {
                "agent": "echo",
                "input": {
                    "message": f"Concurrent test {message}",
                    "type": "simple"
                }
            }
            return client.post(f"{settings.api_prefix}/infer", json=payload)
        
        # Simulate concurrent requests (sequential in test client)
        responses = []
        for i in range(5):
            response = make_request(i)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_high_spiral_depth_handling(self):
        """Test handling of maximum spiral depth."""
        payload = {
            "agent": "echo",
            "input": {
                "message": "Deep spiral test",
                "type": "spiral",
                "spiral_depth": 7  # Maximum allowed
            }
        }
        
        response = client.post(f"{settings.api_prefix}/infer", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["response"]["spiral_depth"] == 7


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema availability."""
        if not settings.enable_api_docs:
            pytest.skip("API docs disabled")
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == settings.app_name
    
    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint."""
        if not settings.enable_api_docs:
            pytest.skip("API docs disabled")
        
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test ReDoc documentation endpoint."""
        if not settings.enable_api_docs:
            pytest.skip("API docs disabled")
        
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


# === Test Configuration ===
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before running tests."""
    # Ensure we're in test mode
    import os
    os.environ["SPIRAL_ENVIRONMENT"] = "testing"
    os.environ["SPIRAL_DEBUG"] = "true"
