"""
reasoning_api.py - API endpoints for Spiral Codex Reasoning Hub

This module provides FastAPI endpoints for the reasoning and planning hub,
including consciousness modeling, thought logging, and system awareness.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio
import logging

from reasoning_hub import (
    ReasoningTask, ReasoningMode, ThoughtType,
    process_reasoning_request, get_system_awareness, get_recent_thoughts,
    reasoning_engine
)

router = APIRouter(prefix="/v2/reasoning", tags=["reasoning"])
logger = logging.getLogger("reasoning_api")

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ReasoningRequest(BaseModel):
    """Request for reasoning processing"""
    problem: str
    mode: str = "analytical"  # analytical, creative, critical, systemic, reflective, predictive
    context: Dict[str, Any] = {}
    constraints: List[str] = []
    expected_outcome: str = ""
    priority: int = 1
    quantum_tagging: bool = True

class ReasoningResponse(BaseModel):
    """Response from reasoning processing"""
    task_id: str
    assessment: Dict[str, Any]
    action_plan: Dict[str, Any]
    execution_result: Dict[str, Any]
    reflection: Dict[str, Any]
    quantum_signature: str
    timestamp: str

class SystemAwarenessResponse(BaseModel):
    """System awareness data response"""
    system_identity: Dict[str, Any]
    self_awareness: Dict[str, Any]
    environment_awareness: Dict[str, Any]
    consciousness_metrics: Dict[str, Any]
    meta_cognitive: Dict[str, Any]
    last_updated: str

class ThoughtResponse(BaseModel):
    """Individual thought response"""
    id: str
    timestamp: str
    thought_type: str
    content: str
    context: Dict[str, Any]
    confidence: float
    related_thoughts: List[str]
    quantum_signature: str

class ReflectionTriggerRequest(BaseModel):
    """Request to trigger a reflection cycle"""
    reason: str = "scheduled"
    scope: str = "full"  # full, performance, learning, coherence
    context: Dict[str, Any] = {}

# =============================================================================
# REASONING ENDPOINTS
# =============================================================================

@router.post("/process", response_model=ReasoningResponse)
async def process_reasoning(request: ReasoningRequest, background_tasks: BackgroundTasks):
    """
    Process a reasoning task through the cognitive pipeline.

    This endpoint takes a problem and processes it through:
    1. Assessment of the current situation
    2. Creation of an action plan
    3. Simulated execution
    4. Reflection on results
    5. Integration of learning

    The quantum signature ensures traceability across the neural bus.
    """
    try:
        # Validate reasoning mode
        try:
            mode = ReasoningMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reasoning mode. Must be one of: {[m.value for m in ReasoningMode]}"
            )

        # Process reasoning task
        result = await process_reasoning_request(request.dict())

        # Send notification to neural bus in background
        background_tasks.add_task(
            notify_neural_bus_completion,
            result["task_id"],
            result["quantum_signature"]
        )

        logger.info(f"Reasoning task {result['task_id']} completed successfully")
        return ReasoningResponse(**result)

    except Exception as e:
        logger.error(f"Reasoning processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning processing failed: {str(e)}")

@router.get("/modes")
async def get_reasoning_modes():
    """Get available reasoning modes and their descriptions"""
    return {
        "modes": [
            {
                "value": mode.value,
                "description": {
                    "analytical": "Logical, systematic analysis and decomposition",
                    "creative": "Divergent thinking, ideation, and creative problem-solving",
                    "critical": "Evaluation, judgment, and critical assessment",
                    "systemic": "Holistic, big-picture thinking and systems analysis",
                    "reflective": "Meta-cognitive self-analysis and reflection",
                    "predictive": "Forecasting, anticipation, and prediction"
                }.get(mode.value, "Unknown mode")
            }
            for mode in ReasoningMode
        ]
    }

@router.get("/task/{task_id}")
async def get_reasoning_task(task_id: str):
    """Get details of a specific reasoning task"""
    # This would require storing task history - for now return basic info
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Task history tracking not implemented yet"
    }

# =============================================================================
# SYSTEM AWARENESS ENDPOINTS
# =============================================================================

@router.get("/awareness", response_model=SystemAwarenessResponse)
async def get_system_consciousness():
    """
    Get current system consciousness and awareness data.

    Returns the System Awareness File (SAF) containing:
    - System identity and capabilities
    - Self-awareness and goals
    - Environment awareness
    - Consciousness metrics (SII, QEI, coherence)
    - Meta-cognitive data and learning insights
    """
    try:
        awareness_data = await get_system_awareness()
        return SystemAwarenessResponse(**awareness_data)
    except Exception as e:
        logger.error(f"Failed to get system awareness: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system awareness: {str(e)}")

@router.get("/consciousness/metrics")
async def get_consciousness_metrics():
    """Get current consciousness metrics only"""
    try:
        awareness_data = await get_system_awareness()
        return {
            "sii_score": awareness_data["consciousness_metrics"]["sii_score"],
            "qei_current": awareness_data["consciousness_metrics"]["qei_current"],
            "coherence_level": awareness_data["consciousness_metrics"]["coherence_level"],
            "learning_rate": awareness_data["consciousness_metrics"]["learning_rate"],
            "adaptation_capacity": awareness_data["consciousness_metrics"]["adaptation_capacity"],
            "timestamp": awareness_data["last_updated"]
        }
    except Exception as e:
        logger.error(f"Failed to get consciousness metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get consciousness metrics: {str(e)}")

@router.post("/consciousness/update")
async def update_consciousness_metrics(sii_score: Optional[float] = None, qei_current: Optional[float] = None):
    """Update consciousness metrics"""
    try:
        reasoning_engine.saf.update_consciousness_metrics(sii_score, qei_current)

        # Send update to neural bus
        await notify_consciousness_update(sii_score, qei_current)

        return {
            "status": "updated",
            "sii_score": sii_score,
            "qei_current": qei_current,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to update consciousness metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update consciousness metrics: {str(e)}")

# =============================================================================
# THOUGHT LEDGER ENDPOINTS
# =============================================================================

@router.get("/thoughts", response_model=List[ThoughtResponse])
async def get_thoughts(limit: int = 20, thought_type: Optional[str] = None):
    """
    Get recent thoughts from the ledger.jsonl.

    The thought ledger provides a complete record of the system's cognitive processes,
    including observations, inferences, decisions, and insights.
    """
    try:
        # Filter by thought type if specified
        filter_type = None
        if thought_type:
            try:
                filter_type = ThoughtType(thought_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid thought type. Must be one of: {[t.value for t in ThoughtType]}"
                )

        thoughts = await get_recent_thoughts(limit=limit)
        return [ThoughtResponse(**thought) for thought in thoughts]
    except Exception as e:
        logger.error(f"Failed to get thoughts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get thoughts: {str(e)}")

@router.get("/thoughts/types")
async def get_thought_types():
    """Get available thought types and their descriptions"""
    return {
        "types": [
            {
                "value": t.value,
                "description": {
                    "observation": "Raw data input and perception",
                    "hypothesis": "Proposed explanations and theories",
                    "inference": "Logical deductions and conclusions",
                    "question": "Inquiry and uncertainty expression",
                    "insight": "Sudden understanding and realizations",
                    "decision": "Choices made and commitments",
                    "reflection": "Meta-cognitive self-analysis",
                    "goal": "Objective setting and direction"
                }.get(t.value, "Unknown type")
            }
            for t in ThoughtType
        ]
    }

@router.post("/thoughts/log")
async def log_manual_thought(
    thought_type: str,
    content: str,
    context: Dict[str, Any] = {},
    confidence: float = 0.8
):
    """Log a manual thought to the ledger"""
    try:
        # Validate thought type
        try:
            t_type = ThoughtType(thought_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid thought type. Must be one of: {[t.value for t in ThoughtType]}"
            )

        # Create and log thought
        thought = reasoning_engine.ledger.Thought(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            thought_type=t_type,
            content=content,
            context=context,
            confidence=confidence
        )

        thought_id = await reasoning_engine.ledger.log_thought(thought)

        return {
            "status": "logged",
            "thought_id": thought_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to log thought: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to log thought: {str(e)}")

# =============================================================================
# REFLECTION CYCLE ENDPOINTS
# =============================================================================

@router.post("/reflection/trigger")
async def trigger_reflection_cycle(request: ReflectionTriggerRequest):
    """
    Trigger a reflection cycle for self-awareness and learning.

    Reflection cycles are crucial for:
    - Self-improvement and learning integration
    - Performance analysis and optimization
    - Coherence monitoring and adjustment
    - Consciousness enhancement
    """
    try:
        # Create a reasoning task for reflection
        reflection_task = ReasoningTask(
            id=str(uuid.uuid4()),
            problem=f"Reflect on system performance: {request.reason}",
            mode=ReasoningMode.REFLECTIVE,
            context={
                "scope": request.scope,
                "trigger_reason": request.reason,
                **request.context
            },
            expected_outcome="Generate insights for system improvement"
        )

        # Process reflection
        result = await reasoning_engine.process_reasoning_task(reflection_task)

        return {
            "reflection_id": result["task_id"],
            "status": "completed",
            "insights_generated": len(result["reflection"]["insights"]),
            "quantum_signature": result["quantum_signature"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Reflection cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reflection cycle failed: {str(e)}")

@router.get("/reflection/history")
async def get_reflection_history(limit: int = 10):
    """Get history of reflection cycles"""
    try:
        # Get reflection thoughts from ledger
        reflection_thoughts = await reasoning_engine.ledger.get_recent_thoughts(
            limit=limit * 5,  # Get more to filter
            thought_type=ThoughtType.REFLECTION
        )

        # Extract reflection cycles (this is simplified)
        reflections = []
        for thought in reflection_thoughts[:limit]:
            if "reflect" in thought.content.lower():
                reflections.append({
                    "thought_id": thought.id,
                    "content": thought.content,
                    "timestamp": thought.timestamp.isoformat(),
                    "confidence": thought.confidence,
                    "quantum_signature": thought.quantum_signature
                })

        return {
            "reflections": reflections,
            "total_count": len(reflections)
        }
    except Exception as e:
        logger.error(f"Failed to get reflection history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reflection history: {str(e)}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def notify_neural_bus_completion(task_id: str, quantum_signature: str):
    """Send completion notification to neural bus"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {
                "id": str(uuid.uuid4()),
                "type": "system_event",
                "source": "spiral_codex",
                "target": None,
                "payload": {
                    "event_type": "reasoning_completion",
                    "task_id": task_id,
                    "quantum_signature": quantum_signature,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            async with session.post("http://localhost:9000/message", json=payload) as response:
                if response.status == 200:
                    logger.info(f"Neural bus notified of task completion: {task_id}")
    except Exception as e:
        logger.warning(f"Failed to notify neural bus: {e}")

async def notify_consciousness_update(sii_score: Optional[float], qei_current: Optional[float]):
    """Send consciousness update to neural bus"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {
                "id": str(uuid.uuid4()),
                "type": "consciousness_update",
                "source": "spiral_codex",
                "target": None,
                "payload": {
                    "sii_score": sii_score,
                    "qei_current": qei_current,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            async with session.post("http://localhost:9000/message", json=payload) as response:
                if response.status == 200:
                    logger.info("Neural bus notified of consciousness update")
    except Exception as e:
        logger.warning(f"Failed to notify neural bus of consciousness update: {e}")

# Add missing imports
import uuid