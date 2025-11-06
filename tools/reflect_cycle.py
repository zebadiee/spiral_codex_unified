#!/usr/bin/env python3
"""
Spiral Codex Unified - Reflection Cycle Engine
Mother Phase v2.1 - Self-Reflection and Learning Loop

This script implements the daily reflection cycle that enables
Spiral Codex to learn from its own interactions and improve
autonomously while maintaining owner oversight.
"""

import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import subprocess
import sys

class ReflectionCycle:
    """Core reflection engine for Spiral Codex Mother Phase"""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(".")
        self.ledger_path = self.base_path / "ledger/conversations"
        self.reflections_path = self.base_path / "data/reflections"
        self.omai_lessons_path = self.base_path / "data/omai_lessons.jsonl"

        # Ensure directories exist
        self.reflections_path.mkdir(parents=True, exist_ok=True)
        self.data_path = self.base_path / "data"
        self.data_path.mkdir(exist_ok=True)

        self.cycle_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.reflection_file = self.reflections_path / f"{self.cycle_date}.jsonl"

    def run_cycle(self) -> Dict[str, Any]:
        """Execute complete reflection cycle"""
        print("🌀 Spiral Codex Unified - Reflection Cycle v2.1")
        print("=" * 50)

        # Step 1: Analyze ledger activity
        ledger_analysis = self._analyze_ledger()
        print(f"📊 Ledger Analysis: {ledger_analysis['total_conversations']} conversations")

        # Step 2: Generate insights
        insights = self._generate_insights(ledger_analysis)
        print(f"💡 Generated {len(insights)} insights")

        # Step 3: Identify improvement opportunities
        improvements = self._identify_improvements(ledger_analysis, insights)
        print(f"🔧 Identified {len(improvements)} improvement opportunities")

        # Step 4: Create reflection entry
        reflection = self._create_reflection(ledger_analysis, insights, improvements)

        # Step 5: Verify system integrity
        integrity_check = self._verify_system_integrity()

        # Step 6: Save reflection
        self._save_reflection(reflection)

        # Step 7: Update OMAi lessons
        self._update_omai_lessons(insights)

        # Step 8: Generate summary report
        summary = self._generate_summary(reflection, integrity_check)

        print(f"✅ Reflection cycle complete: {self.reflection_file}")
        return summary

    def _analyze_ledger(self) -> Dict[str, Any]:
        """Analyze recent ledger activity"""
        conversations = []
        total_entries = 0

        if not self.ledger_path.exists():
            return {
                "total_conversations": 0,
                "total_entries": 0,
                "date_range": None,
                "agent_activity": {},
                "collaboration_events": 0
            }

        # Read all conversation files
        for conv_file in self.ledger_path.glob("*.jsonl"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            conversations.append(entry)
                            total_entries += 1
            except Exception as e:
                print(f"⚠️ Error reading {conv_file}: {e}")

        # Analyze agent activity
        agent_activity = {}
        collaboration_events = 0

        for conv in conversations:
            if 'response' in conv and 'collaboration_response' in conv['response']:
                collaboration_events += 1

                # Track agent participation
                collab = conv['response']['collaboration_response']
                if 'agents' in collab:
                    for agent in collab['agents']:
                        agent_id = agent.get('id', 'unknown')
                        agent_activity[agent_id] = agent_activity.get(agent_id, 0) + 1

        # Calculate date range
        dates = [conv.get('timestamp') for conv in conversations if conv.get('timestamp')]
        date_range = None
        if dates:
            dates.sort()
            date_range = {
                "first": dates[0],
                "last": dates[-1]
            }

        return {
            "total_conversations": len(set(c.get('session_id', '') for c in conversations)),
            "total_entries": total_entries,
            "date_range": date_range,
            "agent_activity": agent_activity,
            "collaboration_events": collaboration_events,
            "conversation_files": list(self.ledger_path.glob("*.jsonl"))
        }

    def _generate_insights(self, ledger_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from ledger analysis"""
        insights = []

        # Insight 1: Activity patterns
        if ledger_analysis['total_conversations'] > 0:
            insights.append({
                "type": "activity_pattern",
                "insight": f"System processed {ledger_analysis['total_conversations']} conversation sessions",
                "significance": "high" if ledger_analysis['total_conversations'] > 3 else "medium",
                "data": {
                    "collaboration_rate": ledger_analysis['collaboration_events'] / ledger_analysis['total_conversations']
                }
            })

        # Insight 2: Agent utilization
        if ledger_analysis['agent_activity']:
            most_active = max(ledger_analysis['agent_activity'].items(), key=lambda x: x[1])
            insights.append({
                "type": "agent_utilization",
                "insight": f"Agent {most_active[0]} was most active with {most_active[1]} participations",
                "significance": "medium",
                "data": ledger_analysis['agent_activity']
            })

        # Insight 3: Collaboration effectiveness
        if ledger_analysis['collaboration_events'] > 0:
            collab_rate = ledger_analysis['collaboration_events'] / ledger_analysis['total_conversations']
            insights.append({
                "type": "collaboration_effectiveness",
                "insight": f"Multi-agent collaboration rate: {collab_rate:.2%}",
                "significance": "high" if collab_rate > 0.7 else "medium",
                "data": {"collaboration_rate": collab_rate}
            })

        # Insight 4: System growth
        insight_growth = {
            "type": "system_growth",
            "insight": "Reflection cycles enabling continuous learning",
            "significance": "high",
            "data": {
                "reflection_active": True,
                "mother_phase": "v2.1",
                "autonomous_learning": True
            }
        }
        insights.append(insight_growth)

        return insights

    def _identify_improvements(self, ledger_analysis: Dict[str, Any], insights: List[Dict]) -> List[Dict[str, Any]]:
        """Identify potential improvements"""
        improvements = []

        # Improvement 1: Ledger expansion
        if ledger_analysis['total_conversations'] < 5:
            improvements.append({
                "type": "ledger_expansion",
                "suggestion": "Increase conversation diversity for richer learning",
                "priority": "medium",
                "action": "Generate varied reflection prompts",
                "tag": "#update"
            })

        # Improvement 2: Agent coordination
        agent_count = len(ledger_analysis['agent_activity'])
        if agent_count < 4:
            improvements.append({
                "type": "agent_coordination",
                "suggestion": "Engage more elemental agents in collaboration",
                "priority": "high",
                "action": "Balance agent participation across all elements",
                "tag": "#optimization"
            })

        # Improvement 3: Reflection depth
        high_significance = [i for i in insights if i.get('significance') == 'high']
        if len(high_significance) < 2:
            improvements.append({
                "type": "reflection_depth",
                "suggestion": "Deepen reflection analysis for higher-value insights",
                "priority": "medium",
                "action": "Enhance pattern recognition algorithms",
                "tag": "#enhancement"
            })

        # Improvement 4: System monitoring
        improvements.append({
            "type": "system_monitoring",
            "suggestion": "Establish continuous health and performance monitoring",
            "priority": "low",
            "action": "Implement automated system checks",
            "tag": "#monitoring"
        })

        return improvements

    def _create_reflection(self, ledger_analysis: Dict, insights: List[Dict], improvements: List[Dict]) -> Dict[str, Any]:
        """Create main reflection entry"""
        reflection = {
            "cycle_date": self.cycle_date,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "⊚ Mother Phase Active",
            "seed": "v2.1",
            "cycle": self._get_cycle_number(),
            "ledger_analysis": ledger_analysis,
            "insights": insights,
            "improvements": improvements,
            "system_state": {
                "autonomous": True,
                "local_processing": True,
                "learning_active": True,
                "owner_oversight": True
            }
        }

        return reflection

    def _get_cycle_number(self) -> int:
        """Get current reflection cycle number"""
        if not self.reflections_path.exists():
            return 1

        existing_files = list(self.reflections_path.glob("*.jsonl"))
        return len(existing_files) + 1

    def _verify_system_integrity(self) -> Dict[str, Any]:
        """Verify system integrity and generate checksums"""
        integrity = {
            "verification_timestamp": datetime.datetime.now().isoformat(),
            "checks": {}
        }

        # Check 1: Core files exist
        core_files = [
            "fastapi_app.py",
            "requirements.txt",
            "Dockerfile",
            "reflection_training.py"
        ]

        integrity["checks"]["core_files"] = all(
            (self.base_path / f).exists() for f in core_files
        )

        # Check 2: Directory structure
        required_dirs = [
            "ledger/conversations",
            "ledger/reflections",
            "data",
            "api",
            "agents"
        ]

        integrity["checks"]["directory_structure"] = all(
            (self.base_path / d).exists() for d in required_dirs
        )

        # Check 3: System checksum
        system_hash = self._generate_system_checksum()
        integrity["system_checksum"] = system_hash

        # Overall integrity status
        integrity["overall_status"] = all(integrity["checks"].values())

        return integrity

    def _generate_system_checksum(self) -> str:
        """Generate checksum of core system files"""
        hasher = hashlib.sha256()

        core_files = [
            "fastapi_app.py",
            "requirements.txt",
            "Dockerfile",
            "reflection_training.py"
        ]

        for file_name in core_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())

        return hasher.hexdigest()[:16]  # Shortened hash for readability

    def _save_reflection(self, reflection: Dict[str, Any]):
        """Save reflection to daily log"""
        with open(self.reflection_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(reflection, default=str, ensure_ascii=False) + '\n')

    def _update_omai_lessons(self, insights: List[Dict]):
        """Update OMAi lessons file with new insights"""
        lessons_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "cycle": self.cycle_date,
            "insights_count": len(insights),
            "lessons": [i["insight"] for i in insights if i.get("insight")],
            "source": "reflection_cycle"
        }

        with open(self.omai_lessons_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(lessons_entry, default=str, ensure_ascii=False) + '\n')

    def _generate_summary(self, reflection: Dict, integrity: Dict) -> Dict[str, Any]:
        """Generate summary report"""
        return {
            "cycle_completed": reflection["cycle"],
            "date": self.cycle_date,
            "status": reflection["status"],
            "insights_generated": len(reflection["insights"]),
            "improvements_identified": len(reflection["improvements"]),
            "system_integrity": "PASS" if integrity["overall_status"] else "FAIL",
            "system_checksum": integrity["system_checksum"],
            "reflection_file": str(self.reflection_file),
            "next_actions": [
                "Review proposed improvements",
                "Approve changes tagged with #update",
                "Run next reflection cycle in 24 hours"
            ]
        }


def main():
    """Main reflection cycle entry point"""
    cycle = ReflectionCycle()

    try:
        summary = cycle.run_cycle()

        print("\n" + "=" * 50)
        print("🧘 REFLECTION SUMMARY")
        print("=" * 50)
        print(f"📅 Cycle: {summary['cycle_completed']} ({summary['date']})")
        print(f"📊 Status: {summary['status']}")
        print(f"💡 Insights: {summary['insights_generated']}")
        print(f"🔧 Improvements: {summary['improvements_identified']}")
        print(f"🛡️ Integrity: {summary['system_integrity']}")
        print(f"🔐 Checksum: {summary['system_checksum']}")
        print(f"📁 Reflection: {summary['reflection_file']}")

        print(f"\n🎯 Mother Phase v2.1 - Active & Learning")
        print(f"📋 Next Actions:")
        for action in summary['next_actions']:
            print(f"    • {action}")

        return 0

    except Exception as e:
        print(f"❌ Reflection cycle failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())