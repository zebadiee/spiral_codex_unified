# Spiral Codex - Agent Coordination System
# Orchestrates Codex and Claude agents for project tasks

from agents.agent_registry import AgentRegistry
from typing import Dict, Any


class AgentOrchestrator:
    """
    Coordinates multiple AI agents for complex project tasks
    Uses glyph-based routing and elemental specialization
    """

    def __init__(self):
        self.memory = {}  # Shared memory across agents
        self.registry = AgentRegistry(self.memory)
        self.active_agents = {}

    def initialize_agents(self):
        """Initialize all registered agents"""
        self.registry.register_all()
        self.active_agents = self.registry.all()
        return {
            "status": "initialized",
            "agent_count": len(self.active_agents),
            "agents": list(self.active_agents.keys()),
        }

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route task to appropriate agent based on type
        
        Task routing logic:
        - code_* tasks -> Codex (⊕ Fire/Breaker)
        - analysis/planning/docs -> Claude (⊨ Ice/Bastion)
        - entropy/vibe -> VibeKeeper
        - archival -> Archivist
        """
        task_type = task.get("task_type", "")
        
        # Code-related tasks to Codex
        if any(x in task_type for x in ["code", "debug", "refactor", "implement"]):
            agent = self.active_agents.get("ƒCODEX")
            return agent.handle(task) if agent else {"error": "Codex not available"}
        
        # Strategic/analytical tasks to Claude
        elif any(x in task_type for x in ["analysis", "planning", "documentation", "review", "reasoning"]):
            agent = self.active_agents.get("ƒCLAUDE")
            return agent.handle(task) if agent else {"error": "Claude not available"}
        
        # Entropy monitoring to VibeKeeper
        elif "entropy" in task_type or "vibe" in task_type:
            agent = self.active_agents.get("ƒVIBE_KEEPER")
            return agent.handle(task) if agent else {"error": "VibeKeeper not available"}
        
        # Archival tasks to Archivist
        elif "archive" in task_type or "store" in task_type:
            agent = self.active_agents.get("ƒARCHIVIST")
            return agent.handle(task) if agent else {"error": "Archivist not available"}
        
        else:
            return {"error": "Unknown task type", "task": task}

    def collaborate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-agent collaboration for complex tasks
        Claude plans, Codex implements, VibeKeeper monitors
        """
        results = {"collaboration": True, "steps": []}
        
        # Step 1: Claude analyzes and plans
        claude_task = {
            "task_type": "planning",
            "context": task,
            "depth": "comprehensive"
        }
        plan = self.route_task(claude_task)
        results["steps"].append({"agent": "ƒCLAUDE", "phase": "planning", "result": plan})
        
        # Step 2: Codex implements
        codex_task = {
            "task_type": "code_generation",
            "context": task,
            "plan": plan
        }
        implementation = self.route_task(codex_task)
        results["steps"].append({"agent": "ƒCODEX", "phase": "implementation", "result": implementation})
        
        # Step 3: VibeKeeper monitors
        vibe_task = {
            "entropy": task.get("entropy", 0.4),
            "context": "multi_agent_collaboration"
        }
        vibe_check = self.route_task({"task_type": "entropy", **vibe_task})
        results["steps"].append({"agent": "ƒVIBE_KEEPER", "phase": "monitoring", "result": vibe_check})
        
        results["status"] = "collaboration_complete"
        return results

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all active agents"""
        return {
            "orchestrator": "active",
            "agents": {
                name: {
                    "glyph": getattr(agent, "glyph", "N/A"),
                    "element": getattr(agent, "element", "N/A"),
                    "specialty": getattr(agent, "specialty", "N/A")
                }
                for name, agent in self.active_agents.items()
            }
        }


# Example usage
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    init_status = orchestrator.initialize_agents()
    print("🌌 Spiral Codex Agent System")
    print(f"Initialized: {init_status}")
    
    # Test Codex
    codex_result = orchestrator.route_task({
        "task_type": "code_generation",
        "language": "python",
        "context": {"feature": "glyph parser"}
    })
    print(f"\n⊕ Codex Response: {codex_result}")
    
    # Test Claude
    claude_result = orchestrator.route_task({
        "task_type": "analysis",
        "depth": "deep",
        "context": {"subject": "spiral codex architecture"}
    })
    print(f"\n⊨ Claude Response: {claude_result}")
    
    # Test collaboration
    collab_result = orchestrator.collaborate({
        "project": "integrate epoch os",
        "complexity": "high",
        "entropy": 0.5
    })
    print(f"\n🔮 Collaboration Result: {collab_result}")
