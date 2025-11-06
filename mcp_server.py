# mcp_server.py
"""
Spiral Codex Unified - MCP Server
Exports Spiral capabilities as standard MCP tools for agent federation
"""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List
import requests
import json
from datetime import datetime

app = FastAPI(title="Spiral MCP Server", version="0.1")

TOOLS: Dict[str, Dict[str, Any]] = {
    "claude.plan": {
        "description": "High-level plan for a goal",
        "schema": {"type":"object","properties":{"goal":{"type":"string"},"max_steps":{"type":"integer"}}}
    },
    "codex.generate": {
        "description": "Generate code for a spec",
        "schema": {"type":"object","properties":{"language":{"type":"string"},"spec":{"type":"string"}}}
    },
    "archivist.ledger.write": {
        "description":"Append record to ledger",
        "schema":{"type":"object","properties":{"session_id":{"type":"string"},"record":{"type":"object"}}}
    },
    "vault.query": {
        "description":"Query Obsidian vault via OMAi bridge",
        "schema":{"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer"}}}
    },
    "vibe.weanDecision": {
        "description":"Choose model provider per wean policy",
        "schema":{"type":"object","properties":{"route":{"type":"string"},"hint":{"type":"string"}}}
    },
    "llm.infer": {
        "description":"Run prompt on chosen provider",
        "schema":{"type":"object","properties":{"provider":{"type":"string"},"prompt":{"type":"string"}}}
    },
    "reflect.cycle": {
        "description": "Run reflection cycle with failure analysis",
        "schema": {"type":"object","properties":{"session_id":{"type":"string"},"focus_areas":{"type":"array"}}}
    },
    "rag.enhanced_query": {
        "description": "Enhanced RAG query with BM25 + vector scoring",
        "schema": {"type":"object","properties":{"query":{"type":"string"},"top_k":{"type":"integer"}}}
    },
    "chaos.test": {
        "description": "Run chaos test on system stability",
        "schema": {"type":"object","properties":{"target_url":{"type":"string"},"requests":{"type":"integer"}}}
    }
}

class ToolListResponse(BaseModel):
    tools: List[Dict[str, Any]]

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

@app.get("/")
async def root():
    return {"service": "Spiral MCP Server", "version": "0.1", "tools_count": len(TOOLS)}

@app.get("/tools/list", response_model=ToolListResponse)
def tools_list():
    return {"tools": [{"name": k, **v} for k,v in TOOLS.items()]}

@app.post("/tools/call")
def tools_call(call: ToolCall):
    n, a = call.name, call.arguments or {}

    try:
        if n == "claude.plan":
            # Placeholder for planning functionality
            return {
                "plan": f"High-level plan for: {a.get('goal', 'unknown goal')}",
                "steps": [f"Step {i+1}: Analyze {a.get('goal', 'task')}" for i in range(a.get('max_steps', 3))],
                "timestamp": datetime.utcnow().isoformat()
            }

        if n == "codex.generate":
            # Placeholder for code generation
            return {
                "code": f"# Generated {a.get('language', 'python')} code for: {a.get('spec', 'spec')}\n# Implementation would go here",
                "language": a.get('language', 'python'),
                "spec": a.get('spec', ''),
                "timestamp": datetime.utcnow().isoformat()
            }

        if n == "archivist.ledger.write":
            # Write to ledger
            import os
            os.makedirs("ledger/conversations", exist_ok=True)
            ledger_file = f"ledger/conversations/{a['session_id']}.jsonl"
            with open(ledger_file, "a") as f:
                f.write(json.dumps({**a["record"], "timestamp": datetime.utcnow().isoformat()}) + "\n")
            return {"ok": True, "ledger_file": ledger_file}

        if n == "vault.query":
            # Forward to OMAi MCP server
            try:
                r = requests.post("http://127.0.0.1:7018/tools/call",
                                  json={"name":"vault.query","arguments":a}, timeout=10)
                return r.json()
            except Exception as e:
                return {"error": f"OMAi bridge unavailable: {str(e)}"}

        if n == "vibe.weanDecision":
            # Placeholder for WEAN decision logic
            return {
                "provider": "local",  # Based on our analysis, local is preferred
                "reasoning": "Based on telemetry, local providers show 100% success vs 0% for external",
                "wean_local_pct": 85,
                "timestamp": datetime.utcnow().isoformat()
            }

        if n == "llm.infer":
            # Placeholder for LLM inference
            return {
                "provider": a.get('provider', 'codex'),
                "prompt": a.get('prompt', ''),
                "response": f"Response from {a.get('provider', 'codex')} for prompt: {a.get('prompt', '')[:100]}...",
                "timestamp": datetime.utcnow().isoformat()
            }

        if n == "reflect.cycle":
            # Trigger reflection cycle
            try:
                from tools.reflect_cycle import run_reflection_cycle
                result = run_reflection_cycle(
                    session_id=a.get('session_id', 'default'),
                    focus_areas=a.get('focus_areas', ['failures', 'performance', 'optimization'])
                )
                return {"reflection": result, "timestamp": datetime.utcnow().isoformat()}
            except Exception as e:
                return {"error": f"Reflection cycle failed: {str(e)}"}

        if n == "rag.enhanced_query":
            # Enhanced RAG query
            try:
                from utils.rag import enhanced_rag_query
                result = enhanced_rag_query(
                    query=a.get('query', ''),
                    top_k=a.get('top_k', 5)
                )
                return {"results": result, "timestamp": datetime.utcnow().isoformat()}
            except Exception as e:
                return {"error": f"Enhanced RAG failed: {str(e)}"}

        if n == "chaos.test":
            # Run chaos test
            try:
                from chaos_test_framework import run_chaos_test
                result = run_chaos_test(
                    target_url=a.get('target_url', 'http://127.0.0.1:7020/tools/list'),
                    num_requests=a.get('requests', 100)
                )
                return {"chaos_results": result, "timestamp": datetime.utcnow().isoformat()}
            except Exception as e:
                return {"error": f"Chaos test failed: {str(e)}"}

        raise HTTPException(status_code=404, detail=f"Unknown tool: {n}")

    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}", "tool": n, "arguments": a}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7020, reload=True)