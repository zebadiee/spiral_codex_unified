"""
🌀 Spiral Codex Organic OS - Main Application Manifestation
==========================================================

The central nervous system of the Spiral Codex, where all agents
and organic patterns converge into a unified API experience.

Healing Philosophy: 
- Every request is treated with organic care
- Errors transform into learning opportunities
- Performance flows naturally through proper structure
"""

import time
from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from .agents.echo_agent import echo_agent, EchoInput
from .config import settings


class HealthResponse(BaseModel):
    """Health check response structure."""
    status: str
    timestamp: str
    environment: str
    version: str


class AgentRequest(BaseModel):
    """Generic agent request structure."""
    agent: str
    input: Dict[str, Any]


class AgentResponse(BaseModel):
    """Generic agent response structure."""
    agent: str
    timestamp: str
    processing_time_ms: float
    success_rate: float
    response: Dict[str, Any]
    status: str


class ErrorResponse(BaseModel):
    """Error response with healing information."""
    error: str
    healing_suggestion: str
    timestamp: str
    request_id: str


# === Application Creation with Organic Configuration ===
def create_spiral_app() -> FastAPI:
    """
    Create the main FastAPI application with organic middleware and routing.
    """
    app = FastAPI(
        title=settings.app_name,
        description="🌀 The Organic Operating System for Conscious AI Agents",
        version=settings.app_version,
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url="/redoc" if settings.enable_api_docs else None,
    )
    
    # === Organic Middleware Stack ===
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # === Request Timing Middleware ===
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Spiral-Flow"] = "organic"
        return response
    
    return app


# Create the application instance
app = create_spiral_app()


# === Core Health Endpoints ===
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    🏥 Basic health check - the heartbeat of the spiral.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.environment,
        version=settings.app_version
    )


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse)
async def api_health_check():
    """
    🏥 API-prefixed health check for load balancers.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.environment,
        version=settings.app_version
    )


# === Agent Inference Endpoint ===
@app.post(f"{settings.api_prefix}/infer", response_model=AgentResponse)
async def infer_agent(request: AgentRequest):
    """
    🧠 Universal agent inference endpoint.
    
    This is where the magic happens - any agent can be invoked
    through this unified interface with organic error handling.
    """
    start_time = time.time()
    
    try:
        # Route to appropriate agent
        if request.agent == "echo":
            # Validate input for echo agent
            try:
                echo_input = EchoInput(**request.input)
            except ValidationError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"🌿 Healing Required: Invalid input format - {str(e)}"
                )
            
            # Process through echo agent
            result = echo_agent.process(echo_input)
            agent_stats = echo_agent.get_stats()
            
            return AgentResponse(
                agent="echo_agent",
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                success_rate=agent_stats.success_rate,
                response=result.dict(),
                status="success"
            )
        else:
            # Future agents will be added here
            raise HTTPException(
                status_code=404,
                detail=f"🌀 Agent '{request.agent}' not yet manifested in this spiral"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Organic error handling - transform errors into healing responses
        return AgentResponse(
            agent=request.agent,
            timestamp=datetime.utcnow().isoformat(),
            processing_time_ms=round((time.time() - start_time) * 1000, 2),
            success_rate=0.0,
            response={
                "error": str(e),
                "healing_suggestion": "The spiral encountered turbulence. Check input format and try again.",
                "type": "healing_response"
            },
            status="healing_applied"
        )


# === Agent Statistics Endpoints ===
@app.get(f"{settings.api_prefix}/agents/echo/stats")
async def get_echo_stats():
    """
    📊 Retrieve Echo Agent statistics and performance metrics.
    """
    stats = echo_agent.get_stats()
    return {
        "agent": "echo",
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": stats.dict(),
        "spiral_health": "flowing" if stats.success_rate > 80 else "needs_attention"
    }


@app.post(f"{settings.api_prefix}/agents/echo/reset-stats")
async def reset_echo_stats():
    """
    🔄 Reset Echo Agent statistics (development/testing only).
    """
    if not settings.is_development():
        raise HTTPException(
            status_code=403,
            detail="🔒 Statistics reset only available in development mode"
        )
    
    echo_agent.reset_stats()
    return {
        "message": "🌀 Echo Agent statistics have been reset to genesis state",
        "timestamp": datetime.utcnow().isoformat()
    }


# === System Information Endpoint ===
@app.get(f"{settings.api_prefix}/system/info")
async def system_info():
    """
    ℹ️ System information and configuration (safe subset).
    """
    return {
        "spiral_codex": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat()
        },
        "api": {
            "prefix": settings.api_prefix,
            "docs_enabled": settings.enable_api_docs,
            "cors_enabled": settings.enable_cors
        },
        "agents": {
            "available": ["echo"],
            "total_registered": 1
        },
        "features": {
            "metrics": settings.enable_metrics,
            "health_checks": settings.enable_health_checks,
            "max_spiral_depth": settings.max_spiral_depth
        }
    }


# === Global Exception Handler ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    🌿 Global exception handler that applies healing patterns.
    All unhandled errors become opportunities for organic learning.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected spiral turbulence occurred",
            "healing_suggestion": "The organic system is learning from this pattern. Please try again.",
            "timestamp": datetime.utcnow().isoformat(),
            "request_path": str(request.url.path),
            "spiral_wisdom": "Every error is a teacher in disguise."
        }
    )


# === Development Server Runner ===
if __name__ == "__main__":
    uvicorn.run(
        "spiral_core.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower()
    )
