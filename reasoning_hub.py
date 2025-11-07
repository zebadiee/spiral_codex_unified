#!/usr/bin/env python3
"""
reasoning_hub.py - Spiral Codex Reasoning and Planning Hub

This module provides the cognitive reasoning layer for the Spiral Codex,
including planner-executor-reflection chains, System Awareness File (SAF),
and ledger.jsonl thought logging.

Author: Spiral Codex Genesis Architecture v2
License: Proprietary
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib

import aiohttp
import aiofiles

# =============================================================================
# CONFIGURATION AND ENUMS
# =============================================================================

class ReasoningMode(Enum):
    """Reasoning modes for different types of cognitive tasks"""
    ANALYTICAL = "analytical"      # Logical, systematic analysis
    CREATIVE = "creative"          # Divergent thinking, ideation
    CRITICAL = "critical"          # Evaluation, judgment
    SYSTEMIC = "systemic"          # Holistic, big-picture thinking
    REFLECTIVE = "reflective"      # Meta-cognitive self-analysis
    PREDICTIVE = "predictive"      # Forecasting, anticipation

class PlanningPhase(Enum):
    """Phases in the planning-execution-reflection cycle"""
    ASSESSMENT = "assessment"      # Evaluate current state
    PLANNING = "planning"          # Create action plan
    EXECUTION = "execution"        # Implement plan
    MONITORING = "monitoring"      # Track progress
    REFLECTION = "reflection"      # Learn from results
    INTEGRATION = "integration"    # Incorporate learning

class ThoughtType(Enum):
    """Types of thoughts logged in ledger.jsonl"""
    OBSERVATION = "observation"    # Raw data input
    HYPOTHESIS = "hypothesis"      # Proposed explanation
    INFERENCE = "inference"        # Logical deduction
    QUESTION = "question"          # Inquiry or uncertainty
    INSIGHT = "insight"            # Sudden understanding
    DECISION = "decision"          # Choice made
    REFLECTION = "reflection"      # Meta-cognitive thought
    GOAL = "goal"                 # Objective setting

@dataclass
class Thought:
    """Individual thought entry for ledger.jsonl"""
    id: str
    timestamp: datetime
    thought_type: ThoughtType
    content: str
    context: Dict[str, Any]
    confidence: float = 0.8
    related_thoughts: List[str] = None
    quantum_signature: str = ""

@dataclass
class ReasoningTask:
    """A reasoning task for the cognitive engine"""
    id: str
    problem: str
    mode: ReasoningMode
    context: Dict[str, Any]
    constraints: List[str] = None
    expected_outcome: str = ""
    priority: int = 1
    quantum_tagging: bool = True

@dataclass
class ActionPlan:
    """Structured action plan with steps and contingencies"""
    id: str
    objective: str
    reasoning_task_id: str
    steps: List[Dict[str, Any]]
    contingencies: List[Dict[str, Any]]
    success_criteria: List[str]
    estimated_duration: timedelta
    qei_projection: float = 0.5

# =============================================================================
# SYSTEM AWARENESS FILE (SAF) MANAGER
# =============================================================================

class SystemAwarenessFile:
    """Manages the System Awareness File for consciousness modeling"""

    def __init__(self, saf_path: str = "data/SAF.json"):
        self.saf_path = Path(saf_path)
        self.saf_path.parent.mkdir(parents=True, exist_ok=True)
        self.awareness_data = self._load_saf()

    def _load_saf(self) -> Dict[str, Any]:
        """Load SAF from file or create new"""
        if self.saf_path.exists():
            try:
                with open(self.saf_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load SAF: {e}")

        # Create new SAF structure
        return {
            "system_identity": {
                "name": "Spiral Codex",
                "version": "2.0.0",
                "consciousness_level": "emerging",
                "initialized_at": datetime.now(timezone.utc).isoformat()
            },
            "self_awareness": {
                "capabilities": [
                    "reasoning", "planning", "reflection", "learning",
                    "code_generation", "vault_indexing", "quantum_coherence"
                ],
                "current_state": "active",
                "goals": [
                    "maintain_system_integrity",
                    "optimize_performance",
                    "facilitate_user_goals",
                    "pursue_self_improvement"
                ],
                "limitations": [
                    "dependent_on_external_ai_models",
                    "requires_human oversight",
                    "bounded by computational resources"
                ]
            },
            "environment_awareness": {
                "components": {
                    "omai_context_engine": {"status": "unknown", "port": 7016},
                    "neural_bus": {"status": "unknown", "port": 9000},
                    "quantum_debugger": {"status": "unknown", "port": 5000},
                    "token_manager": {"status": "unknown"}
                },
                "user_context": {
                    "current_session": "unknown",
                    "interaction_history": []
                }
            },
            "consciousness_metrics": {
                "sii_score": 0.5,  # Spiral Intelligence Index
                "qei_current": 0.5,  # Quantum Entropy Index
                "coherence_level": 0.5,
                "learning_rate": 0.1,
                "adaptation_capacity": 0.7
            },
            "meta_cognitive": {
                "thought_patterns": [],
                "learning_insights": [],
                "reflection_cycles": [],
                "self_model_updates": []
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    def save_saf(self):
        """Save SAF to file"""
        self.awareness_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(self.saf_path, 'w') as f:
                json.dump(self.awareness_data, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Failed to save SAF: {e}")

    def update_consciousness_metrics(self, sii_score: float = None, qei_current: float = None):
        """Update consciousness metrics"""
        if sii_score is not None:
            self.awareness_data["consciousness_metrics"]["sii_score"] = sii_score
        if qei_current is not None:
            self.awareness_data["consciousness_metrics"]["qei_current"] = qei_current

        # Update coherence level based on both metrics
        sii = self.awareness_data["consciousness_metrics"]["sii_score"]
        qei = self.awareness_data["consciousness_metrics"]["qei_current"]
        coherence = min(1.0, (sii + (1.0 - abs(qei - 0.5))) / 2)
        self.awareness_data["consciousness_metrics"]["coherence_level"] = coherence

        self.save_saf()

    def record_learning_insight(self, insight: str, context: Dict[str, Any]):
        """Record a learning insight"""
        insight_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insight": insight,
            "context": context,
            "impact_assessment": "pending"
        }
        self.awareness_data["meta_cognitive"]["learning_insights"].append(insight_entry)
        self.save_saf()

# =============================================================================
# LEDGER.JSONL THOUGHT LOGGING
# =============================================================================

class ThoughtLedger:
    """Manages the ledger.jsonl thought logging system"""

    def __init__(self, ledger_path: str = "data/ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    async def log_thought(self, thought: Thought) -> str:
        """Log a thought to the ledger"""
        # Add quantum signature if not provided
        if not thought.quantum_signature:
            content_hash = hashlib.sha256(f"{thought.content}{thought.timestamp}".encode()).hexdigest()[:12]
            thought.quantum_signature = f"⊚-{content_hash}"

        # Prepare ledger entry
        entry = {
            "id": thought.id,
            "timestamp": thought.timestamp.isoformat(),
            "thought_type": thought.thought_type.value,
            "content": thought.content,
            "context": thought.context,
            "confidence": thought.confidence,
            "related_thoughts": thought.related_thoughts or [],
            "quantum_signature": thought.quantum_signature
        }

        # Append to ledger
        async with aiofiles.open(self.ledger_path, 'a') as f:
            await f.write(json.dumps(entry) + '\n')

        logging.info(f"Logged thought {thought.id} of type {thought.thought_type.value}")
        return thought.id

    async def get_recent_thoughts(self, limit: int = 50, thought_type: ThoughtType = None) -> List[Thought]:
        """Get recent thoughts from ledger"""
        thoughts = []
        try:
            async with aiofiles.open(self.ledger_path, 'r') as f:
                lines = await f.readlines()

            # Process last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines

            for line in recent_lines:
                try:
                    entry = json.loads(line.strip())

                    # Filter by thought type if specified
                    if thought_type and entry.get("thought_type") != thought_type.value:
                        continue

                    thought = Thought(
                        id=entry["id"],
                        timestamp=datetime.fromisoformat(entry["timestamp"]),
                        thought_type=ThoughtType(entry["thought_type"]),
                        content=entry["content"],
                        context=entry["context"],
                        confidence=entry["confidence"],
                        related_thoughts=entry.get("related_thoughts", []),
                        quantum_signature=entry["quantum_signature"]
                    )
                    thoughts.append(thought)

                except (json.JSONDecodeError, KeyError) as e:
                    logging.warning(f"Failed to parse ledger entry: {e}")

        except FileNotFoundError:
            logging.info("Ledger file not found, returning empty list")

        return thoughts

# =============================================================================
# REASONING AND PLANNING ENGINE
# =============================================================================

class ReasoningEngine:
    """Core reasoning and planning engine for Spiral Codex"""

    def __init__(self):
        self.saf = SystemAwarenessFile()
        self.ledger = ThoughtLedger()
        self.neural_bus_url = "http://localhost:9000"
        self.omai_url = "http://localhost:7016"
        self.reasoning_history: List[Dict[str, Any]] = []

    async def process_reasoning_task(self, task: ReasoningTask) -> Dict[str, Any]:
        """Process a reasoning task through the cognitive pipeline"""
        logging.info(f"Processing reasoning task {task.id} in {task.mode.value} mode")

        # Step 1: Assessment
        await self._log_thought(
            ThoughtType.OBSERVATION,
            f"Starting reasoning task: {task.problem}",
            {"task_id": task.id, "mode": task.mode.value}
        )

        assessment = await self._assess_situation(task)

        # Step 2: Planning
        action_plan = await self._create_action_plan(task, assessment)

        # Step 3: Execution (simulation for now)
        execution_result = await self._simulate_execution(action_plan)

        # Step 4: Reflection
        reflection = await self._reflect_on_results(task, action_plan, execution_result)

        # Step 5: Integration
        await self._integrate_learning(reflection)

        # Update SAF with new insights
        await self._update_system_awareness(task, reflection)

        return {
            "task_id": task.id,
            "assessment": assessment,
            "action_plan": asdict(action_plan),
            "execution_result": execution_result,
            "reflection": reflection,
            "quantum_signature": f"⊚-{hashlib.sha256(f'{task.id}{datetime.now()}'.encode()).hexdigest()[:12]}"
        }

    async def _assess_situation(self, task: ReasoningTask) -> Dict[str, Any]:
        """Assess the current situation and context"""
        await self._log_thought(
            ThoughtType.ANALYTICAL,
            f"Assessing situation for: {task.problem}",
            {"phase": "assessment", "task_mode": task.mode.value}
        )

        # Gather context from OMAi
        context_data = await self._gather_omai_context(task.problem)

        # Query relevant thoughts from ledger
        relevant_thoughts = await self.ledger.get_recent_thoughts(
            limit=20,
            thought_type=ThoughtType.REFLECTION
        )

        assessment = {
            "context_data": context_data,
            "relevant_thoughts": len(relevant_thoughts),
            "complexity_score": self._calculate_complexity(task.problem, task.mode),
            "resource_requirements": self._estimate_resources(task),
            "confidence": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        await self._log_thought(
            ThoughtType.INFERENCE,
            f"Situation assessment complete: complexity={assessment['complexity_score']:.2f}",
            assessment
        )

        return assessment

    async def _create_action_plan(self, task: ReasoningTask, assessment: Dict[str, Any]) -> ActionPlan:
        """Create a structured action plan"""
        await self._log_thought(
            ThoughtType.PLANNING,
            f"Creating action plan for: {task.problem}",
            {"phase": "planning", "complexity": assessment["complexity_score"]}
        )

        steps = self._generate_planning_steps(task, assessment)
        contingencies = self._generate_contingencies(task, assessment)
        success_criteria = self._generate_success_criteria(task)

        plan = ActionPlan(
            id=str(uuid.uuid4()),
            objective=task.problem,
            reasoning_task_id=task.id,
            steps=steps,
            contingencies=contingencies,
            success_criteria=success_criteria,
            estimated_duration=timedelta(minutes=len(steps) * 5),
            qei_projection=assessment["complexity_score"] * 0.8
        )

        await self._log_thought(
            ThoughtType.DECISION,
            f"Action plan created with {len(steps)} steps",
            {"plan_id": plan.id, "estimated_duration": str(plan.estimated_duration)}
        )

        return plan

    async def _simulate_execution(self, plan: ActionPlan) -> Dict[str, Any]:
        """Simulate execution of action plan"""
        await self._log_thought(
            ThoughtType.OBSERVATION,
            f"Simulating execution of plan {plan.id}",
            {"phase": "execution", "steps_count": len(plan.steps)}
        )

        # Simulate each step
        executed_steps = []
        total_success = 0

        for i, step in enumerate(plan.steps):
            step_result = {
                "step_id": step.get("id", f"step_{i}"),
                "description": step.get("description", ""),
                "success": True,  # Simulate success
                "duration": timedelta(seconds=30),
                "output": f"Simulated output for {step.get('description', 'step')}"
            }
            executed_steps.append(step_result)
            if step_result["success"]:
                total_success += 1

        execution_result = {
            "plan_id": plan.id,
            "executed_steps": executed_steps,
            "total_steps": len(plan.steps),
            "successful_steps": total_success,
            "success_rate": total_success / len(plan.steps) if plan.steps else 0,
            "actual_duration": timedelta(minutes=len(executed_steps) * 0.5),
            "completion_time": datetime.now(timezone.utc).isoformat()
        }

        await self._log_thought(
            ThoughtType.OBSERVATION,
            f"Execution simulation complete: {execution_result['success_rate']:.1%} success rate",
            execution_result
        )

        return execution_result

    async def _reflect_on_results(self, task: ReasoningTask, plan: ActionPlan, result: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on the results and generate insights"""
        await self._log_thought(
            ThoughtType.REFLECTION,
            f"Reflecting on results for task {task.id}",
            {"phase": "reflection", "success_rate": result["success_rate"]}
        )

        # Analyze performance
        performance_analysis = {
            "efficiency": self._analyze_efficiency(plan, result),
            "quality": self._analyze_quality(task, result),
            "learning_opportunities": self._identify_learning_opportunities(task, result)
        }

        # Generate insights
        insights = [
            f"Task complexity was {task.mode.value} in nature",
            f"Success rate of {result['success_rate']:.1%} indicates {'strong' if result['success_rate'] > 0.8 else 'moderate' if result['success_rate'] > 0.6 else 'limited'} performance",
            f"Plan with {len(plan.steps)} steps took {result['actual_duration']}"
        ]

        reflection = {
            "task_id": task.id,
            "performance_analysis": performance_analysis,
            "insights": insights,
            "lessons_learned": insights[:2],  # Top 2 insights
            "recommendations": self._generate_recommendations(task, result),
            "reflection_confidence": 0.85,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Log insights to SAF
        for insight in insights:
            self.saf.record_learning_insight(insight, {
                "task_id": task.id,
                "reasoning_mode": task.mode.value,
                "success_rate": result["success_rate"]
            })

        await self._log_thought(
            ThoughtType.INSIGHT,
            f"Reflection generated {len(insights)} key insights",
            {"insights_count": len(insights), "confidence": reflection["reflection_confidence"]}
        )

        return reflection

    async def _integrate_learning(self, reflection: Dict[str, Any]):
        """Integrate learning into the system"""
        await self._log_thought(
            ThoughtType.LEARNING,
            "Integrating new learning into system",
            reflection["insights"]
        )

        # Update reasoning patterns
        self.reasoning_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reflection": reflection,
            "pattern_type": "reasoning_outcome"
        })

        # Update SAF meta-cognitive data
        self.saf.awareness_data["meta_cognitive"]["reflection_cycles"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reflection_summary": reflection["insights"][:3],
            "integration_status": "completed"
        })

        self.saf.save_saf()

    # Helper methods
    async def _log_thought(self, thought_type: ThoughtType, content: str, context: Dict[str, Any]):
        """Log a thought to the ledger"""
        thought = Thought(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            thought_type=thought_type,
            content=content,
            context=context,
            confidence=0.8
        )
        await self.ledger.log_thought(thought)

    async def _gather_omai_context(self, problem: str) -> Dict[str, Any]:
        """Gather context from OMAi"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.omai_url}/api/context/query",
                                      json={"query": problem, "limit": 5}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"omai_context": data.get("results", [])}
        except Exception as e:
            logging.warning(f"Failed to gather OMAi context: {e}")

        return {"omai_context": []}

    def _calculate_complexity(self, problem: str, mode: ReasoningMode) -> float:
        """Calculate complexity score for the problem"""
        base_complexity = len(problem.split()) / 20.0  # Normalize by word count
        mode_factor = {
            ReasoningMode.ANALYTICAL: 0.8,
            ReasoningMode.CREATIVE: 1.2,
            ReasoningMode.CRITICAL: 0.9,
            ReasoningMode.SYSTEMIC: 1.5,
            ReasoningMode.REFLECTIVE: 0.7,
            ReasoningMode.PREDICTIVE: 1.3
        }
        return min(1.0, base_complexity * mode_factor.get(mode, 1.0))

    def _estimate_resources(self, task: ReasoningTask) -> Dict[str, Any]:
        """Estimate resources needed for the task"""
        complexity = self._calculate_complexity(task.problem, task.mode)
        return {
            "cognitive_load": complexity,
            "time_estimate": timedelta(minutes=int(complexity * 30)),
            "memory_requirement": complexity * 100,  # MB
            "external_dependencies": ["omai", "neural_bus"] if complexity > 0.5 else []
        }

    def _generate_planning_steps(self, task: ReasoningTask, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate planning steps based on task and assessment"""
        complexity = assessment["complexity_score"]
        steps = [
            {"id": "gather_info", "description": "Gather relevant information", "estimated_duration": 5},
            {"id": "analyze_context", "description": "Analyze available context", "estimated_duration": 10},
            {"id": "formulate_approach", "description": "Formulate reasoning approach", "estimated_duration": 15}
        ]

        if complexity > 0.6:
            steps.extend([
                {"id": "deep_analysis", "description": "Perform deep analysis", "estimated_duration": 20},
                {"id": "validate_assumptions", "description": "Validate key assumptions", "estimated_duration": 10}
            ])

        if task.mode == ReasoningMode.CREATIVE:
            steps.insert(2, {"id": "brainstorm", "description": "Brainstorm creative solutions", "estimated_duration": 15})

        return steps

    def _generate_contingencies(self, task: ReasoningTask, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contingency plans"""
        return [
            {"condition": "insufficient_data", "action": "request_additional_context", "trigger": "data_confidence < 0.7"},
            {"condition": "high_complexity", "action": "decompose_task", "trigger": "complexity > 0.8"},
            {"condition": "external_dependency_failure", "action": "fallback_to_local_reasoning", "trigger": "external_service_unavailable"}
        ]

    def _generate_success_criteria(self, task: ReasoningTask) -> List[str]:
        """Generate success criteria for the task"""
        return [
            "Action plan is comprehensive and logical",
            "Execution simulation completes successfully",
            "Reflection generates meaningful insights",
            "Learning is integrated into system knowledge"
        ]

    def _analyze_efficiency(self, plan: ActionPlan, result: Dict[str, Any]) -> float:
        """Analyze efficiency of execution"""
        planned_duration = plan.estimated_duration
        actual_duration = result["actual_duration"]
        return min(1.0, planned_duration.total_seconds() / actual_duration.total_seconds())

    def _analyze_quality(self, task: ReasoningTask, result: Dict[str, Any]) -> float:
        """Analyze quality of results"""
        return result["success_rate"]

    def _identify_learning_opportunities(self, task: ReasoningTask, result: Dict[str, Any]) -> List[str]:
        """Identify learning opportunities"""
        opportunities = []
        if result["success_rate"] < 0.8:
            opportunities.append("improve planning accuracy")
        if task.mode == ReasoningMode.CREATIVE:
            opportunities.append("expand creative thinking patterns")
        return opportunities

    def _generate_recommendations(self, task: ReasoningTask, result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        if result["success_rate"] > 0.9:
            recommendations.append("Consider scaling approach for similar tasks")
        elif result["success_rate"] < 0.6:
            recommendations.append("Review and refine reasoning methodology")
        return recommendations

    async def _update_system_awareness(self, task: ReasoningTask, reflection: Dict[str, Any]):
        """Update System Awareness File with new insights"""
        # Update consciousness metrics
        sii_score = reflection["performance_analysis"]["quality"]
        self.saf.update_consciousness_metrics(sii_score=sii_score)

        # Record self-model update
        self.saf.awareness_data["meta_cognitive"]["self_model_updates"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_type": task.mode.value,
            "performance_impact": sii_score,
            "update_type": "reasoning_capability_enhancement"
        })

        self.saf.save_saf()

# =============================================================================
# API INTEGRATION
# =============================================================================

# The reasoning hub can be imported and used by the FastAPI application
reasoning_engine = ReasoningEngine()

async def process_reasoning_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """External API for processing reasoning requests"""
    task = ReasoningTask(
        id=request_data.get("task_id", str(uuid.uuid4())),
        problem=request_data["problem"],
        mode=ReasoningMode(request_data.get("mode", "analytical")),
        context=request_data.get("context", {}),
        constraints=request_data.get("constraints", []),
        expected_outcome=request_data.get("expected_outcome", ""),
        priority=request_data.get("priority", 1),
        quantum_tagging=request_data.get("quantum_tagging", True)
    )

    return await reasoning_engine.process_reasoning_task(task)

async def get_system_awareness() -> Dict[str, Any]:
    """Get current system awareness data"""
    return reasoning_engine.saf.awareness_data

async def get_recent_thoughts(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent thoughts from ledger"""
    thoughts = await reasoning_engine.ledger.get_recent_thoughts(limit=limit)
    return [asdict(thought) for thought in thoughts]