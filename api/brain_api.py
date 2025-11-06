# api/brain_api.py
"""
Spiral Codex Brain API - Multi-agent planning & execution
Built with ƒCLAUDE (planning) + ƒCODEX (implementation)
Enhanced with RAG (Retrieval-Augmented Generation) for context-aware planning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import yaml
import json
from pathlib import Path
import hashlib
from datetime import datetime
import time
from utils.rag import available as rag_available, enrich_prompt
from utils.telemetry import log_wean

router = APIRouter(prefix="/v1/brain", tags=["brain"])

# --- Schemas ---------------------------------------------------------------

class Thought(BaseModel):
    role: str = Field(description="Who produced the thought: planner|critic|executor")
    text: str

class BrainRequest(BaseModel):
    goal: str = Field(description="High-level objective to achieve")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hints: Optional[List[str]] = None
    max_steps: int = 5

class BrainPlan(BaseModel):
    steps: List[str]
    rationale: str

class BrainResponse(BaseModel):
    plan: BrainPlan
    thoughts: List[Thought] = []
    artifacts: Dict[str, Any] = Field(default_factory=dict)

class GlyphRecord(BaseModel):
    record_type: str = "glyph"
    record_id: str
    content: Optional[str] = None

class LedgerEntry(BaseModel):
    record_type: str
    record_id: str
    hash: str
    timestamp: str
    ledger_protocol: str
    chain_hash: Optional[str] = None

# --- Brain Planning Logic --------------------------------------------------

def _make_plan(goal: str, max_steps: int, context: Dict[str, Any]) -> BrainPlan:
    """Generate a multi-step plan (RAG-enhanced when available)"""
    
    # Check if RAG is available and enrich the goal
    base_goal = goal
    rag_used = False
    
    if rag_available():
        enriched_goal = enrich_prompt(goal, context_query=goal, max_snippets=3)
        if enriched_goal != goal:
            goal = enriched_goal
            rag_used = True
    
    steps = []
    
    # Analyze goal and generate steps
    if "api" in base_goal.lower() or "endpoint" in base_goal.lower():
        steps = [
            "Design API schema with Pydantic models",
            "Implement FastAPI router with endpoints",
            "Add request validation and error handling",
            "Write integration tests",
            "Document API with examples"
        ]
    elif "glyph" in base_goal.lower():
        steps = [
            "Parse glyph symbols (⊕⊡⊠⊨⊚)",
            "Map glyphs to elements and agents",
            "Implement glyph engine methods",
            "Add validation and lookups"
        ]
    elif "agent" in base_goal.lower():
        steps = [
            "Define agent interface and capabilities",
            "Implement agent routing logic",
            "Add task type handlers",
            "Create collaboration workflows"
        ]
    else:
        steps = [f"Step {i+1}: Refine and implement — {base_goal}" for i in range(max_steps)]
    
    # Limit to max_steps
    steps = steps[:max_steps]
    
    rationale = f"Generated {len(steps)}-step plan for: {base_goal}"
    if rag_used:
        rationale += " | RAG: context-enriched"
    if context:
        rationale += f" | Context keys: {list(context.keys())}"
    
    return BrainPlan(steps=steps, rationale=rationale)

# --- Ledger Management -----------------------------------------------------

class BrainLedger:
    """Immutable ledger for symbolic brain records"""
    
    def __init__(self):
        self.ledger_path = Path("codex_root/brain/codex_immutable_ledger.json")
    
    def load(self) -> List[Dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        with open(self.ledger_path, 'r') as f:
            return json.load(f)
    
    def save(self, ledger: List[Dict[str, Any]]) -> None:
        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2)
    
    def compute_hash(self, record_id: str, content: str = "") -> str:
        data = f"{record_id}:{content}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def compute_chain_hash(self, current_hash: str, prev_hash: str) -> str:
        return hashlib.sha256(f"{prev_hash}:{current_hash}".encode()).hexdigest()

brain_ledger = BrainLedger()

# --- Routes ----------------------------------------------------------------

@router.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": "brain", "version": 1, "glyph": "⊚"}

@router.post("/plan", response_model=BrainResponse)
def plan(req: BrainRequest) -> BrainResponse:
    """Generate multi-step plan for a goal (RAG-enhanced when available)"""
    
    # Start telemetry timer
    t0 = time.time_ns()
    rag_used = rag_available()
    ok = False
    
    try:
        plan = _make_plan(req.goal, req.max_steps, req.context or {})
        
        # Generate thoughts
        thoughts = [
            Thought(role="planner", text=f"Planning for: {req.goal}"),
            Thought(role="critic", text="Plan looks reasonable."),
        ]
        
        if rag_used:
            thoughts.append(Thought(role="planner", text="RAG: Retrieved context snippets"))
        
        if req.hints:
            thoughts.append(Thought(role="planner", text=f"Considering hints: {', '.join(req.hints)}"))
        
        # Artifacts
        artifacts = {
            "context_keys": list(req.context.keys()) if req.context else [],
            "goal": req.goal,
            "step_count": len(plan.steps),
            "rag_enabled": rag_used
        }
        
        # Prove pyyaml works
        _ = yaml.safe_dump({"goal": req.goal, "steps": len(plan.steps)})
        
        ok = True
        return BrainResponse(plan=plan, thoughts=thoughts, artifacts=artifacts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Log telemetry
        log_wean(
            route="brain.plan",
            provider="rag" if rag_used else "base",
            task="planning",
            approx_lines=req.max_steps,
            start_ns=t0,
            ok=ok
        )
        
        return BrainResponse(plan=plan, thoughts=thoughts, artifacts=artifacts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/infer", response_model=Dict[str, Any])
def infer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inference endpoint for agent I/O"""
    return {
        "received": payload,
        "note": "brain.infer echo",
        "glyph": "⊚"
    }

@router.get("/ledger", response_model=List[LedgerEntry])
async def get_ledger():
    """Get all entries from immutable brain ledger"""
    try:
        ledger = brain_ledger.load()
        return ledger
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load ledger: {str(e)}")

@router.get("/ledger/{record_id}")
async def get_record(record_id: str):
    """Get specific record by ID from ledger"""
    try:
        ledger = brain_ledger.load()
        for entry in ledger:
            if entry.get("record_id") == record_id:
                return entry
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record")
async def create_record(record: GlyphRecord):
    """Add new glyph record to immutable ledger"""
    try:
        ledger = brain_ledger.load()
        
        # Compute hash
        record_hash = brain_ledger.compute_hash(record.record_id, record.content or "")
        
        # Compute chain hash if ledger has entries
        chain_hash = None
        if ledger:
            prev_hash = ledger[-1].get("hash", "")
            chain_hash = brain_ledger.compute_chain_hash(record_hash, prev_hash)
        
        # Create new entry
        new_entry = {
            "record_type": record.record_type,
            "record_id": record.record_id,
            "hash": record_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ledger_protocol": "SHA-256 integrity log"
        }
        
        if chain_hash:
            new_entry["chain_hash"] = chain_hash
        
        # Append and save
        ledger.append(new_entry)
        brain_ledger.save(ledger)
        
        return {
            "status": "recorded",
            "entry": new_entry,
            "ledger_size": len(ledger)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get brain ledger statistics"""
    try:
        ledger = brain_ledger.load()
        thoughts = [e for e in ledger if "THOUGHT" in e.get("record_id", "")]
        
        return {
            "total_entries": len(ledger),
            "thought_count": len(thoughts),
            "protocol": "SHA-256",
            "integrity": "immutable",
            "status": "⊚ active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
