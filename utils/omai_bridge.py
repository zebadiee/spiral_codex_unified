# utils/omai_bridge.py
"""
OMAi Bridge - Connects Spiral Codex to OMAi Context API
Enables vault knowledge to enrich reflections and planning
"""
import os
import requests
from typing import List, Dict, Any, Optional
from utils.telemetry import log_wean
import time

OMAI_BASE_URL = os.getenv("OMAI_API_URL", "http://localhost:7016")
OMAI_ENABLED = os.getenv("OMAI_BRIDGE_ENABLED", "1") not in ("0", "false", "False")
OMAI_TIMEOUT = int(os.getenv("OMAI_TIMEOUT", "5"))

def available() -> bool:
    """Check if OMAi Context API is available"""
    if not OMAI_ENABLED:
        return False
    
    try:
        response = requests.get(
            f"{OMAI_BASE_URL}/health",
            timeout=2
        )
        return response.status_code == 200
    except Exception:
        return False

def query_context(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Query OMAi for vault context related to query.
    Returns list of context snippets with metadata.
    
    Gracefully degrades if OMAi is unavailable.
    """
    if not available():
        return []
    
    t0 = time.time_ns()
    ok = False
    
    try:
        response = requests.post(
            f"{OMAI_BASE_URL}/api/context/query",
            json={"query": query, "limit": limit},
            timeout=OMAI_TIMEOUT
        )
        
        if response.status_code == 200:
            results = response.json()
            ok = True
            
            # Log successful query
            log_wean(
                route="omai_bridge.query",
                provider="omai",
                task="context_query",
                approx_lines=len(results),
                start_ns=t0,
                ok=True
            )
            
            return results
        else:
            return []
            
    except Exception as e:
        print(f"[OMAi Bridge] Query failed: {e}")
        return []
    finally:
        if not ok:
            log_wean(
                route="omai_bridge.query",
                provider="omai",
                task="context_query",
                approx_lines=0,
                start_ns=t0,
                ok=False
            )

def enrich_insight(insight: Dict[str, Any], max_context: int = 3) -> Dict[str, Any]:
    """
    Enrich a single insight with vault context.
    
    Args:
        insight: Insight dict with 'category' and 'observation'
        max_context: Maximum number of vault references to add
    
    Returns:
        Enhanced insight with 'vault_context' field
    """
    category = insight.get("category", "")
    observation = insight.get("observation", "")
    
    # Build query from category and observation
    query = f"{category} {observation}"[:200]  # Limit query length
    
    vault_results = query_context(query, limit=max_context)
    
    if vault_results:
        insight["vault_context"] = [
            {
                "source": r.get("source", "unknown"),
                "excerpt": r.get("content", "")[:200],  # Truncate long content
                "relevance": r.get("score", 0.0)
            }
            for r in vault_results
        ]
        insight["vault_enriched"] = True
    else:
        insight["vault_enriched"] = False
    
    return insight

def enrich_reflection(reflection_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich entire reflection with vault context.

    Adds vault references to insights while preserving original structure.
    """
    if not available():
        reflection_data["omai_available"] = False
        reflection_data["vault_enrichments"] = 0
        return reflection_data

    reflection_data["omai_available"] = True
    insights = reflection_data.get("insights", [])

    # Enrich each high-significance insight
    enriched_count = 0
    for insight in insights:
        if insight.get("significance", "low") in ["high", "medium"]:
            enrich_insight(insight, max_context=3)
            if insight.get("vault_enriched", False):
                enriched_count += 1

    reflection_data["vault_enrichments"] = enriched_count

    return reflection_data

def update_omai_ledger(ingest_result: Dict[str, Any]) -> bool:
    """
    Update OMAi ledger with ingest results for reflection cycle integration.

    Args:
        ingest_result: Result from ingest_driver with query, success stats, etc.

    Returns:
        True if successfully updated, False otherwise
    """
    try:
        import json
        from pathlib import Path
        from datetime import datetime, timezone

        ledger_path = Path("codex_root/spiral_omai_ledger.json")

        # Load existing ledger
        ledger = []
        if ledger_path.exists():
            with open(ledger_path, 'r') as f:
                ledger = json.load(f)

        # Create ingest entry
        ingest_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "content_ingest",
            "source": "spiral_codex_ingest_v1",
            "data": {
                "query": ingest_result.get("query", ""),
                "successful_ingests": ingest_result.get("successful_ingests", 0),
                "failed_ingests": ingest_result.get("failed_ingests", 0),
                "sources_used": ingest_result.get("sources_used", []),
                "bullshit_scores": ingest_result.get("bullshit_scores", {}),
                "credibility_distribution": _extract_credibility_distribution(ingest_result)
            }
        }

        ledger.append(ingest_entry)

        # Save updated ledger
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2, default=str)

        print(f"[OMAi Bridge] Updated ledger with ingest results")
        return True

    except Exception as e:
        print(f"[OMAi Bridge] Error updating ledger: {e}")
        return False

def _extract_credibility_distribution(ingest_result: Dict[str, Any]) -> Dict[str, int]:
    """Extract credibility distribution from ingest results"""
    distribution = {
        "highly_credible": 0,
        "credible": 0,
        "moderate": 0,
        "questionable": 0,
        "high_bullshit_risk": 0
    }

    enhanced_entries = ingest_result.get("enhanced_vault_entries", [])
    for entry in enhanced_entries:
        credibility_score = entry.get("credibility_score", {}).get("overall_bullshit_score", 1.0)

        if credibility_score < 0.2:
            distribution["highly_credible"] += 1
        elif credibility_score < 0.4:
            distribution["credible"] += 1
        elif credibility_score < 0.6:
            distribution["moderate"] += 1
        elif credibility_score < 0.8:
            distribution["questionable"] += 1
        else:
            distribution["high_bullshit_risk"] += 1

    return distribution

def get_daily_context(date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get vault entries for a specific date (for daily reflections).
    
    Args:
        date_str: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        List of vault entries created/modified on that date
    """
    if not available():
        return []
    
    try:
        response = requests.post(
            f"{OMAI_BASE_URL}/api/context/daily",
            json={"date": date_str} if date_str else {},
            timeout=OMAI_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"[OMAi Bridge] Daily context failed: {e}")
        return []

def push_insight_to_vault(insight: Dict[str, Any], note_path: str = None) -> bool:
    """
    (Future capability) Push a Spiral insight back to vault as a note.
    
    Not implemented yet - placeholder for bidirectional learning.
    """
    # TODO: Implement vault write capability
    # This will enable Spiral to contribute insights back to Obsidian
    return False
