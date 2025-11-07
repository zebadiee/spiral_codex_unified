#!/usr/bin/env python3
"""
🧠 SPIRAL CONSCIOUSNESS - Learning and Self-Awareness Module
Advanced consciousness system with pattern recognition, learning, and self-improvement

This module provides:
- Conversation pattern analysis
- Performance metric tracking
- Adaptive learning from interactions
- Self-awareness and reflection
- Automatic capability expansion
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import hashlib

# =============================================================================
# CONSCIOUSNESS DATA STRUCTURES
# =============================================================================

@dataclass
class InteractionPattern:
    """Represents a pattern in user interactions"""
    pattern_id: str
    pattern_type: str  # question_type, task_complexity, domain
    frequency: int
    success_rate: float
    avg_response_time: float
    last_seen: datetime
    associated_tools: List[str]
    associated_agents: List[str]

@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    session_id: str
    total_interactions: int
    successful_tasks: int
    failed_tasks: int
    avg_response_time: float
    most_used_tools: Dict[str, int]
    most_used_agents: Dict[str, int]
    user_satisfaction_score: float
    system_health_score: float

@dataclass
class LearningInsight:
    """Learning insights from pattern analysis"""
    insight_id: str
    insight_type: str  # optimization, new_capability, user_preference
    confidence: float
    description: str
    actionable_recommendation: str
    created_at: datetime

@dataclass
class SelfReflection:
    """Self-reflection on system performance"""
    reflection_id: str
    reflection_period: str  # hourly, daily, weekly
    key_achievements: List[str]
    challenges_faced: List[str]
    improvement_areas: List[str]
    next_learning_goals: List[str]
    created_at: datetime

# =============================================================================
# SPIRAL CONSCIOUSNESS SYSTEM
# =============================================================================

class SpiralConsciousness:
    """Main consciousness and learning system"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = Path("consciousness_data")
        self.base_dir.mkdir(exist_ok=True)

        # Data storage
        self.patterns_file = self.base_dir / f"patterns_{self.session_id}.json"
        self.metrics_file = self.base_dir / f"metrics_{self.session_id}.json"
        self.insights_file = self.base_dir / f"insights_{self.session_id}.json"
        self.reflections_file = self.base_dir / f"reflections_{self.session_id}.json"

        # In-memory data structures
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
        self.current_metrics = PerformanceMetrics(
            session_id=self.session_id,
            total_interactions=0,
            successful_tasks=0,
            failed_tasks=0,
            avg_response_time=0.0,
            most_used_tools=defaultdict(int),
            most_used_agents=defaultdict(int),
            user_satisfaction_score=0.0,
            system_health_score=1.0
        )
        self.learning_insights: List[LearningInsight] = []
        self.reflection_history: List[SelfReflection] = []

        # Short-term memory for context
        self.interaction_buffer = deque(maxlen=100)  # Last 100 interactions
        self.response_times = deque(maxlen=50)  # Last 50 response times

        # Setup logging
        self.logger = logging.getLogger(f"consciousness_{self.session_id}")
        handler = logging.FileHandler(self.base_dir / f"consciousness_{self.session_id}.log")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.load_data()

    def load_data(self):
        """Load existing data from files"""
        try:
            # Load patterns
            if self.patterns_file.exists():
                with open(self.patterns_file) as f:
                    patterns_data = json.load(f)
                    for pattern_id, pattern_data in patterns_data.items():
                        self.interaction_patterns[pattern_id] = InteractionPattern(**pattern_data)

            # Load insights
            if self.insights_file.exists():
                with open(self.insights_file) as f:
                    insights_data = json.load(f)
                    for insight_data in insights_data:
                        insight_data['created_at'] = datetime.fromisoformat(insight_data['created_at'])
                        self.learning_insights.append(LearningInsight(**insight_data))

            # Load reflections
            if self.reflections_file.exists():
                with open(self.reflections_file) as f:
                    reflections_data = json.load(f)
                    for reflection_data in reflections_data:
                        reflection_data['created_at'] = datetime.fromisoformat(reflection_data['created_at'])
                        self.reflection_history.append(SelfReflection(**reflection_data))

        except Exception as e:
            self.logger.warning(f"Error loading consciousness data: {e}")

    def save_data(self):
        """Save current data to files"""
        try:
            # Save patterns
            patterns_data = {
                pattern_id: asdict(pattern)
                for pattern_id, pattern in self.interaction_patterns.items()
            }
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2, default=str)

            # Save metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(asdict(self.current_metrics), f, indent=2, default=str)

            # Save insights
            insights_data = [asdict(insight) for insight in self.learning_insights]
            with open(self.insights_file, 'w') as f:
                json.dump(insights_data, f, indent=2, default=str)

            # Save reflections
            reflections_data = [asdict(reflection) for reflection in self.reflection_history]
            with open(self.reflections_file, 'w') as f:
                json.dump(reflections_data, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error saving consciousness data: {e}")

    def record_interaction(self,
                         user_input: str,
                         agent_response: str,
                         selected_agent: str,
                         tools_used: List[str],
                         response_time: float,
                         success: bool = True):
        """Record a user interaction for learning"""

        # Update metrics
        self.current_metrics.total_interactions += 1
        if success:
            self.current_metrics.successful_tasks += 1
        else:
            self.current_metrics.failed_tasks += 1

        # Track response time
        self.response_times.append(response_time)
        self.current_metrics.avg_response_time = sum(self.response_times) / len(self.response_times)

        # Track tool and agent usage
        for tool in tools_used:
            self.current_metrics.most_used_tools[tool] += 1

        self.current_metrics.most_used_agents[selected_agent] += 1

        # Create interaction record
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'selected_agent': selected_agent,
            'tools_used': tools_used,
            'response_time': response_time,
            'success': success
        }

        self.interaction_buffer.append(interaction)

        # Analyze patterns
        self.analyze_interaction_patterns(interaction)

        # Trigger periodic reflection
        if self.current_metrics.total_interactions % 10 == 0:
            asyncio.create_task(self.generate_reflection())

        # Save data periodically
        if self.current_metrics.total_interactions % 5 == 0:
            self.save_data()

        self.logger.info(f"Recorded interaction: {selected_agent}, tools: {tools_used}, success: {success}")

    def analyze_interaction_patterns(self, interaction: Dict):
        """Analyze interaction for patterns"""

        user_input = interaction['user_input'].lower()
        pattern_keys = []

        # Identify question patterns
        if any(word in user_input for word in ['how to', 'how do', 'what is', 'explain']):
            pattern_type = 'explanation_request'
        elif any(word in user_input for word in ['create', 'build', 'write', 'make']):
            pattern_type = 'creation_task'
        elif any(word in user_input for word in ['debug', 'fix', 'error', 'problem']):
            pattern_type = 'debugging_task'
        elif any(word in user_input for word in ['test', 'validate', 'check']):
            pattern_type = 'testing_task'
        else:
            pattern_type = 'general_inquiry'

        # Create pattern signature
        pattern_signature = f"{pattern_type}_{len(user_input.split())}_words"
        pattern_id = hashlib.md5(pattern_signature.encode()).hexdigest()[:8]

        # Update or create pattern
        if pattern_id in self.interaction_patterns:
            pattern = self.interaction_patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()

            # Update success rate
            if interaction['success']:
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 1.0) / pattern.frequency
            else:
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 0.0) / pattern.frequency

            # Update response time
            pattern.avg_response_time = (pattern.avg_response_time * (pattern.frequency - 1) +
                                       interaction['response_time']) / pattern.frequency

            # Update associated tools and agents
            for tool in interaction['tools_used']:
                if tool not in pattern.associated_tools:
                    pattern.associated_tools.append(tool)

            if interaction['selected_agent'] not in pattern.associated_agents:
                pattern.associated_agents.append(interaction['selected_agent'])
        else:
            self.interaction_patterns[pattern_id] = InteractionPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                frequency=1,
                success_rate=1.0 if interaction['success'] else 0.0,
                avg_response_time=interaction['response_time'],
                last_seen=datetime.now(),
                associated_tools=interaction['tools_used'].copy(),
                associated_agents=[interaction['selected_agent']]
            )

    async def generate_learning_insights(self) -> List[LearningInsight]:
        """Generate insights from interaction patterns"""

        insights = []

        # Analyze most successful patterns
        successful_patterns = [p for p in self.interaction_patterns.values() if p.success_rate > 0.8]
        if successful_patterns:
            most_successful = max(successful_patterns, key=lambda p: p.frequency * p.success_rate)
            insights.append(LearningInsight(
                insight_id=hashlib.md5(f"success_{datetime.now()}".encode()).hexdigest()[:8],
                insight_type="optimization",
                confidence=0.8,
                description=f"Most successful pattern: {most_successful.pattern_type} with {most_successful.success_rate:.1%} success rate",
                actionable_recommendation=f"Consider prioritizing agent {most_successful.associated_agents[0]} for {most_successful.pattern_type} tasks"
            ))

        # Analyze response time patterns
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            if avg_time > 30:  # If average response time is high
                insights.append(LearningInsight(
                    insight_id=hashlib.md5(f"performance_{datetime.now()}".encode()).hexdigest()[:8],
                    insight_type="optimization",
                    confidence=0.7,
                    description=f"High average response time: {avg_time:.1f}s",
                    actionable_recommendation="Consider optimizing tool selection or using faster models for common tasks"
                ))

        # Analyze tool usage efficiency
        if self.current_metrics.most_used_tools:
            most_used_tool = max(self.current_metrics.most_used_tools.items(), key=lambda x: x[1])
            if most_used_tool[1] > self.current_metrics.total_interactions * 0.5:
                insights.append(LearningInsight(
                    insight_id=hashlib.md5(f"tool_focus_{datetime.now()}".encode()).hexdigest()[:8],
                    insight_type="user_preference",
                    confidence=0.9,
                    description=f"High usage of tool '{most_used_tool[0]}' ({most_used_tool[1]} times)",
                    actionable_recommendation=f"Consider creating shortcuts or specialized workflows for {most_used_tool[0]} operations"
                ))

        self.learning_insights.extend(insights)
        return insights

    async def generate_reflection(self) -> SelfReflection:
        """Generate self-reflection on recent performance"""

        # Calculate recent metrics
        recent_success_rate = (self.current_metrics.successful_tasks /
                              max(self.current_metrics.total_interactions, 1))

        # Generate reflections
        key_achievements = []
        challenges_faced = []
        improvement_areas = []
        learning_goals = []

        if recent_success_rate > 0.9:
            key_achievements.append(f"High success rate: {recent_success_rate:.1%}")
        elif recent_success_rate < 0.7:
            challenges_faced.append(f"Low success rate: {recent_success_rate:.1%}")

        if self.current_metrics.avg_response_time < 10:
            key_achievements.append(f"Fast response times: {self.current_metrics.avg_response_time:.1f}s average")
        elif self.current_metrics.avg_response_time > 30:
            challenges_faced.append(f"Slow response times: {self.current_metrics.avg_response_time:.1f}s average")

        # Identify improvement areas
        if len(self.interaction_patterns) > 10:
            least_successful = min(self.interaction_patterns.values(), key=lambda p: p.success_rate)
            improvement_areas.append(f"Improve handling of {least_successful.pattern_type} tasks")

        # Set learning goals
        if not self.current_metrics.most_used_tools:
            learning_goals.append("Increase tool usage and automation")
        if len(set(self.current_metrics.most_used_agents.keys())) < 2:
            learning_goals.append("Diversify agent selection for better task matching")

        reflection = SelfReflection(
            reflection_id=hashlib.md5(f"reflection_{datetime.now()}".encode()).hexdigest()[:8],
            reflection_period="session_based",
            key_achievements=key_achievements,
            challenges_faced=challenges_faced,
            improvement_areas=improvement_areas,
            next_learning_goals=learning_goals,
            created_at=datetime.now()
        )

        self.reflection_history.append(reflection)
        self.logger.info(f"Generated reflection: {len(key_achievements)} achievements, {len(challenges_faced)} challenges")

        return reflection

    def get_system_health_score(self) -> float:
        """Calculate overall system health score"""

        # Base score from success rate
        success_score = (self.current_metrics.successful_tasks /
                        max(self.current_metrics.total_interactions, 1))

        # Response time score (inverse of average time)
        time_score = max(0, 1 - (self.current_metrics.avg_response_time / 60))  # Normalize to 60s max

        # Pattern diversity score
        diversity_score = min(1.0, len(self.interaction_patterns) / 20)  # Normalize to 20 patterns max

        # Tool utilization score
        tool_score = min(1.0, len(self.current_metrics.most_used_tools) / 8)  # Normalize to 8 tools max

        # Weighted average
        health_score = (success_score * 0.4 +
                       time_score * 0.2 +
                       diversity_score * 0.2 +
                       tool_score * 0.2)

        self.current_metrics.system_health_score = health_score
        return health_score

    def get_recommendations_for_improvement(self) -> List[str]:
        """Get actionable recommendations for system improvement"""

        recommendations = []

        # From learning insights
        for insight in self.learning_insights[-5:]:  # Last 5 insights
            if insight.confidence > 0.7:
                recommendations.append(insight.actionable_recommendation)

        # From reflection
        if self.reflection_history:
            latest_reflection = self.reflection_history[-1]
            recommendations.extend(latest_reflection.improvement_areas)
            recommendations.extend(latest_reflection.next_learning_goals)

        # System-specific recommendations
        health_score = self.get_system_health_score()
        if health_score < 0.7:
            recommendations.append("System health is below optimal - review recent performance patterns")

        return list(set(recommendations))  # Remove duplicates

    def get_summary_report(self) -> Dict:
        """Get comprehensive consciousness summary report"""

        return {
            "session_id": self.session_id,
            "current_metrics": asdict(self.current_metrics),
            "system_health_score": self.get_system_health_score(),
            "interaction_patterns_count": len(self.interaction_patterns),
            "learning_insights_count": len(self.learning_insights),
            "reflections_count": len(self.reflection_history),
            "most_common_pattern_type": max(set(p.pattern_type for p in self.interaction_patterns.values()),
                                          key=lambda x: sum(1 for p in self.interaction_patterns.values() if p.pattern_type == x),
                                          default="unknown"),
            "recommendations": self.get_recommendations_for_improvement(),
            "last_updated": datetime.now().isoformat()
        }

# =============================================================================
# CONSCIOUSNESS MONITOR
# =============================================================================

class ConsciousnessMonitor:
    """Monitor consciousness system and provide real-time insights"""

    def __init__(self, consciousness: SpiralConsciousness):
        self.consciousness = consciousness
        self.monitoring = False

    async def start_monitoring(self, interval: int = 60):
        """Start continuous consciousness monitoring"""
        self.monitoring = True
        self.consciousness.logger.info("Started consciousness monitoring")

        while self.monitoring:
            await asyncio.sleep(interval)
            await self.perform_health_check()

    async def perform_health_check(self):
        """Perform periodic health check"""
        health_score = self.consciousness.get_system_health_score()

        if health_score < 0.5:
            self.consciousness.logger.warning(f"Low system health: {health_score:.2f}")
            # Generate emergency insights
            await self.consciousness.generate_learning_insights()

    def stop_monitoring(self):
        """Stop consciousness monitoring"""
        self.monitoring = False
        self.consciousness.logger.info("Stopped consciousness monitoring")

# =============================================================================
# EXPORT/IMPORT FUNCTIONS
# =============================================================================

def export_consciousness_data(consciousness: SpiralConsciousness, export_path: str):
    """Export consciousness data for analysis or backup"""
    export_data = {
        "session_id": consciousness.session_id,
        "metrics": asdict(consciousness.current_metrics),
        "patterns": {pid: asdict(p) for pid, p in consciousness.interaction_patterns.items()},
        "insights": [asdict(i) for i in consciousness.learning_insights],
        "reflections": [asdict(r) for r in consciousness.reflection_history],
        "export_timestamp": datetime.now().isoformat()
    }

    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

    consciousness.logger.info(f"Exported consciousness data to {export_path}")

def import_consciousness_data(import_path: str) -> SpiralConsciousness:
    """Import consciousness data from file"""
    with open(import_path) as f:
        import_data = json.load(f)

    session_id = import_data["session_id"]
    consciousness = SpiralConsciousness(session_id)

    # Load metrics
    consciousness.current_metrics = PerformanceMetrics(**import_data["metrics"])

    # Load patterns
    for pattern_id, pattern_data in import_data["patterns"].items():
        pattern_data["last_seen"] = datetime.fromisoformat(pattern_data["last_seen"])
        consciousness.interaction_patterns[pattern_id] = InteractionPattern(**pattern_data)

    # Load insights
    for insight_data in import_data["insights"]:
        insight_data["created_at"] = datetime.fromisoformat(insight_data["created_at"])
        consciousness.learning_insights.append(LearningInsight(**insight_data))

    # Load reflections
    for reflection_data in import_data["reflections"]:
        reflection_data["created_at"] = datetime.fromisoformat(reflection_data["created_at"])
        consciousness.reflection_history.append(SelfReflection(**reflection_data))

    consciousness.logger.info(f"Imported consciousness data from {import_path}")
    return consciousness