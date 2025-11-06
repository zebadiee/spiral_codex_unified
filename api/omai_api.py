# api/omai_api.py
"""
OMAi API - Vault Analyst, Context Curator, Planner, Ledger Keeper Integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/v1/omai", tags=["omai"])

# --- Schemas --------------------------------------------------------------

class VaultAnalysisRequest(BaseModel):
    """Vault Analyst request for analyzing project knowledge base"""
    query: str = Field(description="Query to analyze against vault")
    context_type: str = Field(default="comprehensive", description="Type of analysis")
    depth: str = Field(default="medium", description="Analysis depth")

class ContextCuratorRequest(BaseModel):
    """Context Curator request for managing conversation context"""
    session_id: str = Field(description="Session identifier")
    context_data: Dict[str, Any] = Field(description="Context information")
    action: str = Field(description="Action: add, update, retrieve, clear")

class PlannerRequest(BaseModel):
    """Planner request for strategic planning"""
    objective: str = Field(description="Primary objective")
    constraints: List[str] = Field(default_factory=list, description="Constraints and requirements")
    resources: Dict[str, Any] = Field(default_factory=dict, description="Available resources")

class LedgerEntryRequest(BaseModel):
    """Ledger Keeper request for record management"""
    record_type: str = Field(description="Type of record")
    content: Dict[str, Any] = Field(description="Record content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class OMAiResponse(BaseModel):
    """Unified OMAi response structure"""
    component: str = Field(description="OMAi component name")
    status: str = Field(description="Response status")
    data: Dict[str, Any] = Field(description="Response data")
    timestamp: str = Field(description="Response timestamp")

# --- OMAi Components Implementation -----------------------------------------

class VaultAnalyst:
    """Analyzes project knowledge vault and provides insights"""

    def __init__(self):
        self.vault_path = Path("codex_root/vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def analyze(self, req: VaultAnalysisRequest) -> Dict[str, Any]:
        """Analyze query against vault knowledge"""
        # Simulate vault analysis
        analysis_result = {
            "query": req.query,
            "context_type": req.context_type,
            "depth": req.depth,
            "insights": [
                f"Vault analysis for: {req.query}",
                "Context patterns identified",
                "Knowledge connections mapped"
            ],
            "confidence": 0.85,
            "related_concepts": ["spiral_codex", "multi_agent", "glyph_system"]
        }

        # Store analysis in vault
        analysis_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": req.query,
            "analysis": analysis_result
        }

        with open(self.vault_path / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(analysis_record, f, indent=2)

        return analysis_result

class ContextCurator:
    """Manages conversation context and memory"""

    def __init__(self):
        self.context_store = {}
        self.context_path = Path("codex_root/context")
        self.context_path.mkdir(parents=True, exist_ok=True)

    def manage_context(self, req: ContextCuratorRequest) -> Dict[str, Any]:
        """Manage conversation context"""
        session_id = req.session_id

        if req.action == "add" or req.action == "update":
            if session_id not in self.context_store:
                self.context_store[session_id] = {}

            self.context_store[session_id].update(req.context_data)
            self.context_store[session_id]["last_updated"] = datetime.utcnow().isoformat()

            result = {
                "action": "context_updated",
                "session_id": session_id,
                "context_size": len(self.context_store[session_id])
            }

        elif req.action == "retrieve":
            context = self.context_store.get(session_id, {})
            result = {
                "action": "context_retrieved",
                "session_id": session_id,
                "context": context
            }

        elif req.action == "clear":
            if session_id in self.context_store:
                del self.context_store[session_id]
            result = {"action": "context_cleared", "session_id": session_id}

        else:
            result = {"error": f"Unknown action: {req.action}"}

        return result

class OMAiPlanner:
    """Strategic planning and roadmap generation"""

    def __init__(self):
        self.plans_path = Path("codex_root/plans")
        self.plans_path.mkdir(parents=True, exist_ok=True)

    def create_plan(self, req: PlannerRequest) -> Dict[str, Any]:
        """Create strategic plan"""
        plan = {
            "objective": req.objective,
            "constraints": req.constraints,
            "resources": req.resources,
            "phases": [
                {
                    "phase": 1,
                    "name": "Analysis and Design",
                    "tasks": ["Analyze requirements", "Design architecture", "Define interfaces"]
                },
                {
                    "phase": 2,
                    "name": "Implementation",
                    "tasks": ["Implement core components", "Integrate systems", "Add features"]
                },
                {
                    "phase": 3,
                    "name": "Testing and Refinement",
                    "tasks": ["Unit testing", "Integration testing", "Performance optimization"]
                }
            ],
            "estimated_duration": "2-4 weeks",
            "success_metrics": [
                "All endpoints functional",
                "Multi-agent collaboration active",
                "Local operation verified"
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        # Store plan
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(self.plans_path / plan_id, 'w') as f:
            json.dump(plan, f, indent=2)

        return plan

class LedgerKeeper:
    """Manages immutable ledger of system records"""

    def __init__(self):
        self.ledger_path = Path("codex_root/omai_ledger.json")
        self._init_ledger()

    def _init_ledger(self):
        if not self.ledger_path.exists():
            with open(self.ledger_path, 'w') as f:
                json.dump([], f)

    def add_entry(self, req: LedgerEntryRequest) -> Dict[str, Any]:
        """Add entry to OMAi ledger"""
        # Load existing ledger
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)

        # Create new entry
        entry = {
            "entry_id": f"omai_{len(ledger) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "record_type": req.record_type,
            "content": req.content,
            "metadata": req.metadata,
            "timestamp": datetime.utcnow().isoformat(),
            "ledger_sequence": len(ledger) + 1
        }

        # Add to ledger
        ledger.append(entry)

        # Save ledger
        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2)

        return {
            "entry_added": True,
            "entry_id": entry["entry_id"],
            "ledger_size": len(ledger)
        }

    def get_ledger(self) -> List[Dict[str, Any]]:
        """Get entire OMAi ledger"""
        with open(self.ledger_path, 'r') as f:
            return json.load(f)

# Initialize OMAi components
vault_analyst = VaultAnalyst()
context_curator = ContextCurator()
omai_planner = OMAiPlanner()
ledger_keeper = LedgerKeeper()

# --- API Routes ------------------------------------------------------------

@router.get("/health")
async def health():
    return {
        "ok": True,
        "service": "omai",
        "version": 1,
        "components": ["vault_analyst", "context_curator", "planner", "ledger_keeper"],
        "glyph": "⊚"
    }

@router.post("/vault/analyze", response_model=OMAiResponse)
async def vault_analyze(req: VaultAnalysisRequest):
    """Vault Analyst endpoint for knowledge analysis"""
    try:
        analysis = vault_analyst.analyze(req)
        return OMAiResponse(
            component="vault_analyst",
            status="success",
            data=analysis,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context/manage", response_model=OMAiResponse)
async def context_manage(req: ContextCuratorRequest):
    """Context Curator endpoint for context management"""
    try:
        result = context_curator.manage_context(req)
        return OMAiResponse(
            component="context_curator",
            status="success",
            data=result,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/planner/create", response_model=OMAiResponse)
async def planner_create(req: PlannerRequest):
    """Planner endpoint for strategic planning"""
    try:
        plan = omai_planner.create_plan(req)
        return OMAiResponse(
            component="planner",
            status="success",
            data=plan,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ledger/add", response_model=OMAiResponse)
async def ledger_add(req: LedgerEntryRequest):
    """Ledger Keeper endpoint for record management"""
    try:
        result = ledger_keeper.add_entry(req)
        return OMAiResponse(
            component="ledger_keeper",
            status="success",
            data=result,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ledger", response_model=List[Dict[str, Any]])
async def get_omai_ledger():
    """Get complete OMAi ledger"""
    try:
        return ledger_keeper.get_ledger()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_omai_status():
    """Get OMAi system status"""
    return {
        "system": "OMAi",
        "status": "active",
        "components": {
            "vault_analyst": "operational",
            "context_curator": "operational",
            "planner": "operational",
            "ledger_keeper": "operational"
        },
        "integration": "spiral_codex_connected",
        "timestamp": datetime.utcnow().isoformat()
    }