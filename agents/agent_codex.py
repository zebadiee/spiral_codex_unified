# Q: How does Codex agent assist with code generation and completion?
# R: Codex specializes in code synthesis, pattern recognition, and technical implementation.

import importlib
import os
import sys
from typing import Any, Dict


class CodexAgent:
    """
    Codex Agent - Code synthesis and technical implementation specialist
    Glyph: ⊕ (Creation/Initiation)
    Element: Fire (Breaker) - Penetration through complexity
    """

    def __init__(self, memory):
        self.mem = memory
        self.glyph = "⊕"
        self.element = "fire"
        self.specialty = "code_synthesis"

    def handle(self, payload: dict):
        task_type = payload.get("task_type", "code_generation")
        context = payload.get("context", {})
        language = payload.get("language", "python")

        if task_type == "code_generation":
            return self._generate_code(context, language)
        elif task_type == "code_completion":
            return self._complete_code(context, language)
        elif task_type == "refactor":
            return self._refactor_code(context)
        elif task_type == "debug":
            return self._debug_analysis(context)
        else:
            return self._general_assist(context)

    def _generate_code(self, context: dict, language: str):
        """Generate new code based on specifications"""
        return {
            "agent": "ƒCODEX",
            "glyph": self.glyph,
            "element": self.element,
            "action": "code_generation",
            "language": language,
            "status": "ready",
            "capabilities": [
                "function_creation",
                "class_design",
                "algorithm_implementation",
                "api_integration",
            ],
            "context": context,
        }

    def _complete_code(self, context: dict, language: str):
        """Complete partial code snippets"""
        return {
            "agent": "ƒCODEX",
            "glyph": self.glyph,
            "action": "code_completion",
            "language": language,
            "status": "completing",
            "context": context,
        }

    def _refactor_code(self, context: dict):
        """Refactor and optimize existing code"""
        return {
            "agent": "ƒCODEX",
            "glyph": self.glyph,
            "action": "refactoring",
            "status": "analyzing",
            "focus": ["optimization", "readability", "maintainability"],
            "context": context,
        }

    def _debug_analysis(self, context: dict):
        """Analyze and suggest fixes for bugs"""
        return {
            "agent": "ƒCODEX",
            "glyph": self.glyph,
            "action": "debugging",
            "status": "investigating",
            "analysis_depth": "deep",
            "context": context,
        }

    def _general_assist(self, context: dict):
        """General technical assistance"""
        return {
            "agent": "ƒCODEX",
            "glyph": self.glyph,
            "action": "technical_assist",
            "status": "ready",
            "specialties": [
                "code_patterns",
                "best_practices",
                "architecture_design",
                "performance_optimization",
            ],
            "context": context,
        }


class AgentOrchestrator:
    """
    Coordinates Spiral Codex agents for one-shot routing scenarios.
    Embedded here so Codex can act as the core coordinator when invoked directly.
    """

    def __init__(self):
        root = os.path.dirname(os.path.dirname(__file__))
        if root not in sys.path:
            sys.path.insert(0, root)

        AgentRegistry = importlib.import_module("agents.agent_registry").AgentRegistry
        self.memory: Dict[str, Any] = {}
        self.registry = AgentRegistry(self.memory)
        self.active_agents: Dict[str, Any] = {}
        self._initialized = False

    def initialize_agents(self) -> Dict[str, Any]:
        if not self._initialized:
            self.registry.register_all()
            self.active_agents = self.registry.all()
            self._initialized = True
        return {
            "status": "initialized",
            "agent_count": len(self.active_agents),
            "agents": list(self.active_agents.keys()),
        }

    def _ensure_agents(self):
        if not self._initialized:
            init_status = self.initialize_agents()
            agents = init_status.get("agents", [])
            for agent_name in agents:
                print(f"[+] Loaded {agent_name}")

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route task to appropriate agent based on type.
        """
        self._ensure_agents()
        task_type = task.get("task_type", "")

        if any(x in task_type for x in ["code", "debug", "refactor", "implement"]):
            agent = self.active_agents.get("ƒCODEX")
            return agent.handle(task) if agent else {"error": "Codex not available"}
        elif any(
            x in task_type
            for x in ["analysis", "planning", "documentation", "review", "reasoning"]
        ):
            agent = self.active_agents.get("ƒCLAUDE")
            return agent.handle(task) if agent else {"error": "Claude not available"}
        elif "entropy" in task_type or "vibe" in task_type:
            agent = self.active_agents.get("ƒVIBE_KEEPER")
            return agent.handle(task) if agent else {"error": "VibeKeeper not available"}
        elif "archive" in task_type or "store" in task_type:
            agent = self.active_agents.get("ƒARCHIVIST")
            return agent.handle(task) if agent else {"error": "Archivist not available"}
        else:
            return {"error": "Unknown task type", "task": task}

    def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lightweight wrapper to support one-shot bootstrapping payloads that
        don't specify task_type explicitly.
        """
        self._ensure_agents()
        task_type = payload.get("task_type")
        if not task_type:
            task_type = "code_generation"
            payload = {
                "task_type": task_type,
                "context": {
                    "prompt": payload.get("prompt"),
                    "task": payload.get("task"),
                    "approx_lines": payload.get("approx_lines", 0),
                },
                "language": payload.get("language", "python"),
            }

        result = self.route_task(payload)
        handled_by = result.get("agent", "unknown")
        context = payload.get("context") or {}
        prompt = context.get("prompt") or payload.get("prompt") or payload.get("task_type", "task")
        agent_label = handled_by.split("ƒ")[-1] if isinstance(handled_by, str) else handled_by
        print(f"[→] {agent_label} handling: {prompt}")
        return result


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    orchestrator.route(
        {
            "prompt": "Initial handshake",
            "task": "boot",
            "approx_lines": 0,
        }
    )
