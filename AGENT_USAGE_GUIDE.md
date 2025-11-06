# Using Codex and Claude Agents - Quick Guide

## 🤖 Agent Overview

The Spiral Codex system now includes two specialized AI agents:

### ƒCODEX (⊕ Fire/Breaker)
- **Specialty:** Code synthesis, debugging, refactoring
- **Use for:** Implementation, optimization, bug fixes
- **Glyph:** ⊕ (Creation/Initiation)

### ƒCLAUDE (⊨ Ice/Bastion)
- **Specialty:** Strategic analysis, planning, documentation
- **Use for:** Architecture design, reviews, comprehensive planning
- **Glyph:** ⊨ (Truth-Binding)

---

## 🚀 Quick Start

```python
from agent_orchestrator import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()
orchestrator.initialize_agents()

# Check status
status = orchestrator.get_agent_status()
print(status)
```

---

## 📋 Common Tasks

### 1. Generate New Code (Codex)

```python
result = orchestrator.route_task({
    "task_type": "code_generation",
    "language": "python",
    "context": {
        "feature": "Add glyph parser",
        "requirements": [
            "Parse ⊕⊡⊠⊨⊚ symbols",
            "Return element mapping"
        ]
    }
})
```

### 2. Refactor Code (Codex)

```python
result = orchestrator.route_task({
    "task_type": "refactor",
    "context": {
        "file": "kernel/glyph_engine.py",
        "focus": ["performance", "readability"]
    }
})
```

### 3. Debug Analysis (Codex)

```python
result = orchestrator.route_task({
    "task_type": "debug",
    "context": {
        "error": "ImportError in agent_registry",
        "traceback": "...",
        "files": ["agents/agent_registry.py"]
    }
})
```

### 4. Strategic Planning (Claude)

```python
result = orchestrator.route_task({
    "task_type": "planning",
    "depth": "comprehensive",
    "context": {
        "project": "Integrate brain ledger with API",
        "constraints": ["maintain CI/CD", "backwards compatibility"],
        "timeline": "2 days"
    }
})
```

### 5. Code Review (Claude)

```python
result = orchestrator.route_task({
    "task_type": "review",
    "context": {
        "files": ["agent_orchestrator.py", "agents/agent_codex.py"],
        "focus": ["security", "maintainability", "documentation"]
    }
})
```

### 6. Documentation (Claude)

```python
result = orchestrator.route_task({
    "task_type": "documentation",
    "context": {
        "module": "codex_root/brain/",
        "doc_types": ["api_documentation", "user_guide"]
    }
})
```

---

## 🔮 Multi-Agent Collaboration

For complex tasks requiring both planning and implementation:

```python
result = orchestrator.collaborate({
    "project": "Build symbolic brain API endpoint",
    "description": "Create FastAPI endpoint for brain ledger queries",
    "complexity": "high",
    "entropy": 0.5
})

# Result includes:
# 1. Claude's strategic plan
# 2. Codex's implementation
# 3. VibeKeeper's entropy monitoring
```

---

## 🎯 Task Type Reference

### Codex Tasks
- `code_generation` - Create new code
- `code_completion` - Complete partial code
- `refactor` - Optimize existing code
- `debug` - Analyze and fix bugs

### Claude Tasks
- `analysis` - Deep analytical reasoning
- `planning` - Strategic project planning
- `documentation` - Generate docs
- `reasoning` - Multi-step logic problems
- `review` - Code review and suggestions

### Other Agents
- `entropy` / `vibe` - VibeKeeper entropy monitoring
- `archive` / `store` - Archivist memory management

---

## 📊 Response Format

All agents return structured data:

```python
{
    "agent": "ƒCODEX",          # Agent identifier
    "glyph": "⊕",               # Associated glyph
    "element": "fire",          # Elemental type
    "action": "code_generation", # Task performed
    "status": "ready",          # Current status
    "context": {...},           # Task context
    "capabilities": [...]       # Agent abilities
}
```

---

## 🌀 Workflow Examples

### Example 1: New Feature Development

```python
# 1. Claude plans architecture
plan = orchestrator.route_task({
    "task_type": "planning",
    "context": {"feature": "Add glyph validation"}
})

# 2. Codex implements
code = orchestrator.route_task({
    "task_type": "code_generation",
    "context": {"plan": plan, "language": "python"}
})

# 3. Claude reviews
review = orchestrator.route_task({
    "task_type": "review",
    "context": {"implementation": code}
})
```

### Example 2: Debug Session

```python
# 1. Codex analyzes error
analysis = orchestrator.route_task({
    "task_type": "debug",
    "context": {"error": "...", "stack_trace": "..."}
})

# 2. Claude reasons about root cause
reasoning = orchestrator.route_task({
    "task_type": "reasoning",
    "context": {"analysis": analysis}
})

# 3. Codex implements fix
fix = orchestrator.route_task({
    "task_type": "code_generation",
    "context": {"fix_for": reasoning}
})
```

---

## 🔧 Configuration

Agent behavior is configured in:
- `config/epoch_config.yml` - Glyph and element mappings
- `config/entropy_bindings.yml` - Entropy thresholds
- `agents/agent_registry.py` - Agent registration

---

## 💡 Tips

1. **Use Claude for planning** - Let Claude design before Codex implements
2. **Combine agents** - Use `collaborate()` for complex tasks
3. **Monitor entropy** - Check VibeKeeper status during long operations
4. **Provide context** - More context = better results
5. **Iterate** - Refine with multiple agent calls

---

**Status:** ⊚ Agent System Active
**Agents:** ƒCODEX | ƒCLAUDE | ƒVIBE_KEEPER | ƒARCHIVIST
