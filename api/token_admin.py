"""
Token Admin API - Dynamic model management endpoints
Provides self-updating model discovery and performance-based rotation
"""
from fastapi import APIRouter, HTTPException
import json, pathlib, subprocess, tomllib, logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin = APIRouter(prefix="/v1/admin/tokens", tags=["admin-tokens"])
ROOT = pathlib.Path.home()/ "Documents"
CFG  = ROOT/"ai-token-manager"/"configs"/"infra"/"providers.toml"
CAT  = ROOT/"spiral_codex_unified"/"logs"/"model_catalog.json"

@admin.get("/models")
def list_models():
    """List current model weights and catalog information"""
    try:
        if CFG.exists():
            with open(CFG, "rb") as f:
                data = tomllib.load(f)
            weights = data.get("weights", {})
        else:
            weights = {}

        if CAT.exists():
            with open(CAT, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        else:
            catalog = {}

        return {
            "weights": weights,
            "catalog": catalog,
            "config_file": str(CFG),
            "catalog_file": str(CAT),
            "catalog_exists": CAT.exists()
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.post("/refresh")
def refresh_models():
    """Trigger manual refresh of OpenRouter models"""
    try:
        script_path = ROOT/"ai-token-manager/scripts/refresh_openrouter_models.py"
        if not script_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Refresher script not found: {script_path}"
            )

        p = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        ok = p.returncode == 0

        result = {
            "ok": ok,
            "returncode": p.returncode,
            "stdout": p.stdout[-1000:] if p.stdout else "",
            "stderr": p.stderr[-1000:] if p.stderr else ""
        }

        if not ok:
            logger.error(f"Model refresh failed: {p.stderr}")
            raise HTTPException(
                status_code=500,
                detail=result
            )

        logger.info("Model refresh completed successfully")
        return result

    except subprocess.TimeoutExpired:
        logger.error("Model refresh timed out")
        raise HTTPException(status_code=408, detail="Model refresh timed out after 2 minutes")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.post("/ban")
def ban_model(model_id: str):
    """Add a model to the denylist"""
    try:
        if not CFG.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")

        with open(CFG, "rb") as f:
            data = tomllib.load(f)

        ov = data.setdefault("overrides", {})
        deny = set(ov.get("denylist", []))
        deny.add(model_id)
        ov["denylist"] = sorted(deny)

        # Write back using tomli_w
        try:
            import tomli_w
        except ImportError:
            # Fallback if tomli_w not available
            raise HTTPException(
                status_code=500,
                detail="tomli_w library not available for writing TOML"
            )

        with open(CFG, "wb") as f:
            tomli_w.dump(data, f)

        logger.info(f"Model banned: {model_id}")
        return {"banned": model_id, "denylist_size": len(deny)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error banning model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.post("/unban")
def unban_model(model_id: str):
    """Remove a model from the denylist"""
    try:
        if not CFG.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")

        with open(CFG, "rb") as f:
            data = tomllib.load(f)

        ov = data.setdefault("overrides", {})
        deny = [m for m in ov.get("denylist", []) if m != model_id]
        ov["denylist"] = deny

        # Write back using tomli_w
        try:
            import tomli_w
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="tomli_w library not available for writing TOML"
            )

        with open(CFG, "wb") as f:
            tomli_w.dump(data, f)

        logger.info(f"Model unbanned: {model_id}")
        return {"unbanned": model_id, "denylist_size": len(deny)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unbanning model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.post("/weight")
def set_weight(model_id: str, weight: float):
    """Manually set a model weight"""
    try:
        if not CFG.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")

        # Validate weight
        if not 0.1 <= weight <= 10.0:
            raise HTTPException(
                status_code=400,
                detail="Weight must be between 0.1 and 10.0"
            )

        with open(CFG, "rb") as f:
            data = tomllib.load(f)

        w = data.setdefault("weights", {})
        w[model_id] = float(weight)

        # Write back using tomli_w
        try:
            import tomli_w
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="tomli_w library not available for writing TOML"
            )

        with open(CFG, "wb") as f:
            tomli_w.dump(data, f)

        logger.info(f"Model weight set: {model_id} = {weight}")
        return {"model": model_id, "weight": weight}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting weight for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.get("/policy")
def get_policy():
    """Get current token policy settings"""
    try:
        if not CFG.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")

        with open(CFG, "rb") as f:
            data = tomllib.load(f)

        return {
            "policy": data.get("policy", {}),
            "overrides": data.get("overrides", {}),
            "config_file": str(CFG)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin.get("/health")
def token_health():
    """Health check for token management system"""
    try:
        health = {
            "config_exists": CFG.exists(),
            "catalog_exists": CAT.exists(),
            "refresher_script_exists": (ROOT/"ai-token-manager/scripts/refresh_openrouter_models.py").exists(),
            "config_path": str(CFG),
            "catalog_path": str(CAT)
        }

        if CFG.exists():
            with open(CFG, "rb") as f:
                data = tomllib.load(f)
            health["weights_count"] = len(data.get("weights", {}))
            health["denylist_count"] = len(data.get("overrides", {}).get("denylist", []))

        if CAT.exists():
            with open(CAT, "r", encoding="utf-8") as f:
                catalog = json.load(f)
            health["catalog_updated"] = catalog.get("updated_at_iso")
            health["active_models"] = len(catalog.get("active", []))
            health["total_considered"] = len(catalog.get("considered", []))

        return health

    except Exception as e:
        logger.error(f"Error checking token health: {e}")
        raise HTTPException(status_code=500, detail=str(e))