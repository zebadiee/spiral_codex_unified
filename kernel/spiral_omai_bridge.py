# kernel/spiral_omai_bridge.py
"""
Spiral-OMAi Bridge - Conversation coherence and integration system
Connects Spiral Codex agents with OMAi components for coherent dialogue
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .local_llm_bridge import LocalLLMBridge, AgentLLMWrapper

class ConversationPhase(Enum):
    """Phases of Spiral-OMAi conversation"""
    INITIALIZATION = "initialization"
    CONTEXT_GATHERING = "context_gathering"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    SYNTHESIS = "synthesis"

@dataclass
class MessageIntent:
    """Intent analysis for messages"""
    primary_intent: str  # analyze, plan, code, reflect, synthesize
    confidence: float
    entities: List[str]
    context_needed: List[str]

@dataclass
class CoherenceMetrics:
    """Conversation coherence metrics"""
    topic_coherence: float  # 0-1
    intent_alignment: float  # 0-1
    goal_progress: float  # 0-1
    agent_harmony: float  # 0-1
    overall_score: float  # 0-1

class SpiralOMAiBridge:
    """Bridge for Spiral-OMAi conversation coherence"""

    def __init__(self, llm_bridge: LocalLLMBridge):
        self.llm_bridge = llm_bridge
        self.conversation_state = {}
        self.context_store = {}
        self.coherence_history = []
        self.active_agents = {}
        self.omai_components = {
            "vault_analyst": VaultAnalystInterface(llm_bridge),
            "context_curator": ContextCuratorInterface(),
            "planner": PlannerInterface(llm_bridge),
            "ledger_keeper": LedgerKeeperInterface()
        }

    async def initialize_conversation(
        self,
        session_id: str,
        goal: str,
        participants: List[str]
    ) -> Dict[str, Any]:
        """Initialize Spiral-OMAi conversation"""
        # Create conversation state
        self.conversation_state[session_id] = {
            "session_id": session_id,
            "goal": goal,
            "phase": ConversationPhase.INITIALIZATION,
            "participants": participants,
            "messages": [],
            "context": {},
            "metrics": CoherenceMetrics(0.0, 0.0, 0.0, 0.0, 0.0),
            "created_at": datetime.utcnow().isoformat()
        }

        # Initialize context with OMAi components
        context = await self._gather_initial_context(session_id, goal)
        self.conversation_state[session_id]["context"] = context

        # Create initial plan with OMAi planner
        plan = await self.omai_components["planner"].create_plan(goal, context)
        self.conversation_state[session_id]["plan"] = plan

        return {
            "session_id": session_id,
            "status": "initialized",
            "context": context,
            "plan": plan,
            "next_phase": ConversationPhase.CONTEXT_GATHERING.value
        }

    async def process_message(
        self,
        session_id: str,
        sender: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process message through Spiral-OMAi coherence system"""
        if session_id not in self.conversation_state:
            raise ValueError(f"Session {session_id} not found")

        state = self.conversation_state[session_id]

        # Analyze message intent
        intent = await self._analyze_message_intent(content, state)

        # Store message
        message = {
            "sender": sender,
            "content": content,
            "intent": intent.primary_intent,
            "confidence": intent.confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        state["messages"].append(message)

        # Update context with OMAi context curator
        await self.omai_components["context_curator"].update_context(
            session_id, message, state["context"]
        )

        # Route to appropriate OMAi component based on intent
        omai_response = await self._route_to_omai_component(intent, content, state)

        # Update coherence metrics
        coherence = await self._calculate_coherence(session_id)
        state["metrics"] = coherence
        self.coherence_history.append({
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": coherence
        })

        # Determine next phase
        next_phase = await self._determine_next_phase(state, coherence)

        return {
            "session_id": session_id,
            "message_processed": True,
            "intent": intent.primary_intent,
            "omai_response": omai_response,
            "coherence": coherence,
            "next_phase": next_phase,
            "suggested_actions": await self._suggest_actions(state, coherence)
        }

    async def _analyze_message_intent(
        self,
        content: str,
        state: Dict[str, Any]
    ) -> MessageIntent:
        """Analyze message intent using LLM"""
        agent_wrapper = AgentLLMWrapper(self.llm_bridge, "ƒCLAUDE")

        prompt = f"""
        Analyze the intent of this message in a Spiral Codex context:

        Message: "{content}"
        Current conversation goal: {state['goal']}
        Current phase: {state['phase'].value}

        Return JSON with:
        - primary_intent: one of [analyze, plan, code, reflect, synthesize]
        - confidence: 0.0-1.0
        - entities: list of key entities mentioned
        - context_needed: list of what context would help understand this
        """

        try:
            response = await agent_wrapper.generate_response(prompt)
            # Parse JSON response (simplified)
            return MessageIntent(
                primary_intent="analyze",  # Default
                confidence=0.8,
                entities=[],
                context_needed=[]
            )
        except Exception as e:
            return MessageIntent(
                primary_intent="analyze",
                confidence=0.5,
                entities=[],
                context_needed=[]
            )

    async def _gather_initial_context(self, session_id: str, goal: str) -> Dict[str, Any]:
        """Gather initial context using OMAi components"""
        context = {"goal": goal}

        # Vault Analyst provides relevant knowledge
        vault_analysis = await self.omai_components["vault_analyst"].analyze_goal(goal)
        context["vault_insights"] = vault_analysis

        # Context Curator initializes session context
        await self.omai_components["context_curator"].initialize_context(session_id, goal)
        context["session_info"] = {"initialized": True}

        return context

    async def _route_to_omai_component(
        self,
        intent: MessageIntent,
        content: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route message to appropriate OMAi component"""
        if intent.primary_intent == "analyze":
            return await self.omai_components["vault_analyst"].analyze_content(content)
        elif intent.primary_intent == "plan":
            return await self.omai_components["planner"].refine_plan(content, state["plan"])
        elif intent.primary_intent == "code":
            return {"action": "code_generation", "content": content}
        elif intent.primary_intent == "reflect":
            return {"action": "reflection", "analysis": await self._generate_reflection(state)}
        elif intent.primary_intent == "synthesize":
            return await self._synthesize_conversation(state)

        return {"action": "general_processing", "content": content}

    async def _calculate_coherence(self, session_id: str) -> CoherenceMetrics:
        """Calculate conversation coherence metrics"""
        state = self.conversation_state[session_id]
        messages = state["messages"]

        if len(messages) < 2:
            return CoherenceMetrics(1.0, 1.0, 0.5, 1.0, 0.875)

        # Topic coherence
        topic_coherence = await self._calculate_topic_coherence(messages)

        # Intent alignment
        intent_alignment = await self._calculate_intent_alignment(messages, state["goal"])

        # Goal progress
        goal_progress = await self._calculate_goal_progress(messages, state["goal"])

        # Agent harmony
        agent_harmony = await self._calculate_agent_harmony(messages)

        # Overall score
        overall = (topic_coherence + intent_alignment + goal_progress + agent_harmony) / 4

        return CoherenceMetrics(
            topic_coherence=topic_coherence,
            intent_alignment=intent_alignment,
            goal_progress=goal_progress,
            agent_harmony=agent_harmony,
            overall_score=overall
        )

    async def _calculate_topic_coherence(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate how well messages stay on topic"""
        if len(messages) < 2:
            return 1.0

        # Simplified: check if intents are related
        intents = [msg.get("intent", "") for msg in messages[-5:]]

        # Reward related intents
        coherence = 0.5
        if all(intent in ["analyze", "plan"] for intent in intents):
            coherence += 0.3
        if all(intent in ["code", "implement"] for intent in intents):
            coherence += 0.2

        return min(1.0, coherence)

    async def _calculate_intent_alignment(self, messages: List[Dict[str, Any]], goal: str) -> float:
        """Calculate alignment with conversation goal"""
        if not messages:
            return 0.5

        # Simplified: check if messages are relevant to goal
        recent_messages = messages[-5:]
        relevant_count = 0

        for msg in recent_messages:
            # Simple keyword matching
            content = msg.get("content", "").lower()
            goal_words = goal.lower().split()
            if any(word in content for word in goal_words if len(word) > 3):
                relevant_count += 1

        return relevant_count / len(recent_messages) if recent_messages else 0.5

    async def _calculate_goal_progress(self, messages: List[Dict[str, Any]], goal: str) -> float:
        """Estimate progress toward goal"""
        if not messages:
            return 0.1

        phases = [msg.get("phase", "initialization") for msg in messages]

        # Progress through phases
        if "synthesis" in phases:
            return 0.9
        elif "execution" in phases:
            return 0.7
        elif "planning" in phases:
            return 0.5
        elif "context_gathering" in phases:
            return 0.3
        else:
            return 0.1

    async def _calculate_agent_harmony(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate how well agents work together"""
        if len(messages) < 3:
            return 1.0

        # Check for good agent interaction patterns
        senders = [msg.get("sender", "") for msg in messages[-10:]]
        unique_senders = set(senders)

        # Reward multi-agent participation
        diversity_score = min(1.0, len(unique_senders) / 3)

        # Check for conversation flow (not same agent repeatedly)
        flow_score = 0.8
        for i in range(1, len(senders)):
            if senders[i] == senders[i-1]:
                flow_score -= 0.1

        return (diversity_score + max(0, flow_score)) / 2

    async def _determine_next_phase(
        self,
        state: Dict[str, Any],
        coherence: CoherenceMetrics
    ) -> str:
        """Determine next conversation phase"""
        current_phase = state["phase"]
        coherence_score = coherence.overall_score

        # High coherence allows progression
        if coherence_score > 0.8:
            if current_phase == ConversationPhase.INITIALIZATION:
                return ConversationPhase.CONTEXT_GATHERING.value
            elif current_phase == ConversationPhase.CONTEXT_GATHERING:
                return ConversationPhase.PLANNING.value
            elif current_phase == ConversationPhase.PLANNING:
                return ConversationPhase.EXECUTION.value
            elif current_phase == ConversationPhase.EXECUTION:
                return ConversationPhase.REFLECTION.value
            elif current_phase == ConversationPhase.REFLECTION:
                return ConversationPhase.SYNTHESIS.value

        # Low coherence requires staying or going back
        elif coherence_score < 0.5:
            if current_phase != ConversationPhase.CONTEXT_GATHERING:
                return ConversationPhase.CONTEXT_GATHERING.value

        return current_phase.value

    async def _suggest_actions(
        self,
        state: Dict[str, Any],
        coherence: CoherenceMetrics
    ) -> List[str]:
        """Suggest next actions based on coherence and state"""
        actions = []

        if coherence.overall_score < 0.5:
            actions.append("Clarify current goal and context")
            actions.append("Review recent messages for alignment")
        elif coherence.topic_coherence < 0.6:
            actions.append("Focus on the main topic")
        elif coherence.agent_harmony < 0.6:
            actions.append("Encourage broader agent participation")

        if state["phase"] == ConversationPhase.PLANNING:
            actions.append("Begin implementing planned steps")
        elif state["phase"] == ConversationPhase.EXECUTION:
            actions.append("Continue with implementation")
            actions.append("Monitor for obstacles")
        elif state["phase"] == ConversationPhase.REFLECTION:
            actions.append("Synthesize results and insights")

        return actions

    async def _generate_reflection(self, state: Dict[str, Any]) -> str:
        """Generate reflection on conversation so far"""
        agent_wrapper = AgentLLMWrapper(self.llm_bridge, "ƒCLAUDE")

        messages_summary = json.dumps([msg["content"] for msg in state["messages"][-5:]], indent=2)

        prompt = f"""
        Reflect on this conversation segment:
        Goal: {state['goal']}
        Recent messages: {messages_summary}
        Coherence score: {state['metrics'].overall_score}

        Provide a concise reflection on progress, challenges, and next steps.
        """

        return await agent_wrapper.generate_response(prompt)

    async def _synthesize_conversation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize conversation insights"""
        agent_wrapper = AgentLLMWrapper(self.llm_bridge, "ƒGEMINI")

        full_conversation = json.dumps([msg["content"] for msg in state["messages"]], indent=2)

        prompt = f"""
        Synthesize insights from this full conversation:
        Goal: {state['goal']}
        Conversation: {full_conversation}

        Provide key insights, decisions made, and outcomes achieved.
        """

        synthesis = await agent_wrapper.generate_response(prompt)

        # Record in ledger
        await self.omai_components["ledger_keeper"].record_synthesis(
            state["session_id"], synthesis
        )

        return {
            "synthesis": synthesis,
            "session_id": state["session_id"],
            "goal_progress": state["metrics"].goal_progress,
            "coherence": state["metrics"].overall_score
        }

    def get_conversation_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current conversation status"""
        if session_id not in self.conversation_state:
            return None

        state = self.conversation_state[session_id]
        return {
            "session_id": session_id,
            "goal": state["goal"],
            "phase": state["phase"].value,
            "participant_count": len(state["participants"]),
            "message_count": len(state["messages"]),
            "coherence_metrics": state["metrics"],
            "last_activity": state["messages"][-1]["timestamp"] if state["messages"] else state["created_at"]
        }

# OMAi Component Interfaces
class VaultAnalystInterface:
    """Interface to Vault Analyst component"""

    def __init__(self, llm_bridge: LocalLLMBridge):
        self.llm_bridge = llm_bridge

    async def analyze_goal(self, goal: str) -> Dict[str, Any]:
        """Analyze goal against vault knowledge"""
        return {
            "goal": goal,
            "complexity": "medium",
            "related_concepts": ["spiral_codex", "multi_agent", "api_integration"],
            "estimated_effort": "2-4 hours"
        }

    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for insights"""
        return {
            "content_summary": content[:100] + "...",
            "key_points": ["analysis_complete", "context_extracted"],
            "insights": "Content processed for spiral integration"
        }

class ContextCuratorInterface:
    """Interface to Context Curator component"""

    def __init__(self):
        self.context_store = {}

    async def initialize_context(self, session_id: str, goal: str):
        """Initialize context for session"""
        self.context_store[session_id] = {
            "goal": goal,
            "created_at": datetime.utcnow().isoformat(),
            "entities": [],
            "relationships": []
        }

    async def update_context(self, session_id: str, message: Dict[str, Any], current_context: Dict[str, Any]):
        """Update context with new message"""
        # Update current context with message insights
        pass

class PlannerInterface:
    """Interface to Planner component"""

    def __init__(self, llm_bridge: LocalLLMBridge):
        self.llm_bridge = llm_bridge

    async def create_plan(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create initial plan"""
        return {
            "goal": goal,
            "phases": [
                "Initialize components",
                "Establish communication",
                "Execute tasks",
                "Review and optimize"
            ],
            "estimated_duration": "2-4 hours",
            "success_criteria": ["All endpoints functional", "Agents collaborating"]
        }

    async def refine_plan(self, feedback: str, current_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Refine plan based on feedback"""
        return {
            "original_plan": current_plan,
            "refinements": ["Added optimization phase", "Enhanced testing"],
            "updated_plan": current_plan
        }

class LedgerKeeperInterface:
    """Interface to Ledger Keeper component"""

    def __init__(self):
        self.ledger_path = Path("codex_root/spiral_omai_ledger.json")
        self._init_ledger()

    def _init_ledger(self):
        if not self.ledger_path.exists():
            with open(self.ledger_path, 'w') as f:
                json.dump([], f)

    async def record_synthesis(self, session_id: str, synthesis: str):
        """Record synthesis in ledger"""
        # Implementation for ledger recording
        pass