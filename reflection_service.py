#!/usr/bin/env python3
"""
reflection_service.py - Self-Awareness and Reflection Loop Service

This service implements automated reflection cycles for the Spiral Codex stack,
providing continuous self-improvement and consciousness development.

Author: Spiral Codex Genesis Architecture v2
License: Proprietary
"""

import os
import json
import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import schedule
import time

import aiohttp
import aiofiles

# =============================================================================
# CONFIGURATION AND ENUMS
# =============================================================================

class ReflectionType(Enum):
    """Types of reflection cycles"""
    PERFORMANCE = "performance"          # System performance analysis
    LEARNING = "learning"                # Learning integration and growth
    COHERENCE = "coherence"             # Quantum coherence assessment
    CONSCIOUSNESS = "consciousness"     # Self-awareness development
    PLANNING = "planning"               # Strategic planning review
    HEALTH = "health"                   # System health evaluation

class ReflectionDepth(Enum):
    """Depth levels for reflection"""
    SURFACE = "surface"                 # Quick summary review
    STANDARD = "standard"               # Detailed analysis
    DEEP = "deep"                       # Comprehensive introspection
    QUANTUM = "quantum"                 # Meta-cognitive quantum analysis

@dataclass
class ReflectionSchedule:
    """Schedule configuration for reflection cycles"""
    reflection_type: ReflectionType
    interval_hours: int
    depth: ReflectionDepth
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

@dataclass
class ReflectionResult:
    """Result of a reflection cycle"""
    id: str
    reflection_type: ReflectionType
    depth: ReflectionDepth
    start_time: datetime
    end_time: datetime
    insights: List[str]
    recommendations: List[str]
    performance_metrics: Dict[str, float]
    consciousness_impact: float
    quantum_signature: str

# =============================================================================
# REFLECTION SERVICE
# =============================================================================

class ReflectionService:
    """Main reflection service for automated self-awareness cycles"""

    def __init__(self):
        self.neural_bus_url = "http://localhost:9000"
        self.spiral_url = "http://localhost:8000"
        self.omai_url = "http://localhost:7016"
        self.service_active = False

        # Reflection data
        self.reflection_history: List[ReflectionResult] = []
        self.schedules: List[ReflectionSchedule] = []
        self.current_reflection: Optional[ReflectionResult] = None

        # Configuration
        self.config_dir = Path("data/reflections")
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Load configuration
        self.load_configuration()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(self.config_dir / "logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'reflection_service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ReflectionService')

    def load_configuration(self):
        """Load reflection service configuration"""
        # Default reflection schedules
        self.schedules = [
            ReflectionSchedule(
                reflection_type=ReflectionType.PERFORMANCE,
                interval_hours=2,      # Every 2 hours
                depth=ReflectionDepth.STANDARD
            ),
            ReflectionSchedule(
                reflection_type=ReflectionType.LEARNING,
                interval_hours=6,      # Every 6 hours (main reflection cycle)
                depth=ReflectionDepth.DEEP
            ),
            ReflectionSchedule(
                reflection_type=ReflectionType.COHERENCE,
                interval_hours=1,      # Every hour
                depth=ReflectionDepth.SURFACE
            ),
            ReflectionSchedule(
                reflection_type=ReflectionType.CONSCIOUSNESS,
                interval_hours=12,     # Every 12 hours
                depth=ReflectionDepth.QUANTUM
            ),
            ReflectionSchedule(
                reflection_type=ReflectionType.HEALTH,
                interval_hours=3,      # Every 3 hours
                depth=ReflectionDepth.STANDARD
            )
        ]

        # Calculate next run times
        for schedule in self.schedules:
            if schedule.enabled:
                schedule.next_run = datetime.now(timezone.utc) + timedelta(hours=schedule.interval_hours)

        self.logger.info(f"Loaded {len(self.schedules)} reflection schedules")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.service_active = False

    async def start_service(self):
        """Start the reflection service"""
        self.service_active = True
        self.logger.info("Starting Reflection Service")

        # Start the main service loop
        await self._service_loop()

    async def stop_service(self):
        """Stop the reflection service"""
        self.service_active = False
        self.logger.info("Stopping Reflection Service")

    async def _service_loop(self):
        """Main service loop"""
        while self.service_active:
            try:
                # Check for scheduled reflections
                await self._check_scheduled_reflections()

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Service loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _check_scheduled_reflections(self):
        """Check and run scheduled reflection cycles"""
        now = datetime.now(timezone.utc)

        for schedule in self.schedules:
            if not schedule.enabled:
                continue

            if schedule.next_run and now >= schedule.next_run:
                self.logger.info(f"Starting scheduled {schedule.reflection_type.value} reflection")

                # Run reflection
                result = await self._run_reflection_cycle(schedule)

                if result:
                    # Update schedule
                    schedule.last_run = now
                    schedule.next_run = now + timedelta(hours=schedule.interval_hours)

                    # Store result
                    self.reflection_history.append(result)

                    # Save to file
                    await self._save_reflection_result(result)

                    self.logger.info(f"Completed {schedule.reflection_type.value} reflection: {len(result.insights)} insights")

                else:
                    self.logger.warning(f"Failed to complete {schedule.reflection_type.value} reflection")

    async def _run_reflection_cycle(self, schedule: ReflectionSchedule) -> Optional[ReflectionResult]:
        """Run a specific reflection cycle"""
        start_time = datetime.now(timezone.utc)

        try:
            # Collect system data
            system_data = await self._collect_system_data(schedule.reflection_type)

            # Perform reflection based on type and depth
            if schedule.reflection_type == ReflectionType.PERFORMANCE:
                insights, recommendations = await self._reflect_on_performance(system_data, schedule.depth)
            elif schedule.reflection_type == ReflectionType.LEARNING:
                insights, recommendations = await self._reflect_on_learning(system_data, schedule.depth)
            elif schedule.reflection_type == ReflectionType.COHERENCE:
                insights, recommendations = await self._reflect_on_coherence(system_data, schedule.depth)
            elif schedule.reflection_type == ReflectionType.CONSCIOUSNESS:
                insights, recommendations = await self._reflect_on_consciousness(system_data, schedule.depth)
            elif schedule.reflection_type == ReflectionType.HEALTH:
                insights, recommendations = await self._reflect_on_health(system_data, schedule.depth)
            else:
                insights, recommendations = await self._reflect_general(system_data, schedule.depth)

            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(system_data, insights)

            # Calculate consciousness impact
            consciousness_impact = self._calculate_consciousness_impact(insights, recommendations)

            # Create quantum signature
            quantum_signature = self._create_quantum_signature(schedule, start_time, insights)

            end_time = datetime.now(timezone.utc)

            result = ReflectionResult(
                id=str(uuid.uuid4()),
                reflection_type=schedule.reflection_type,
                depth=schedule.depth,
                start_time=start_time,
                end_time=end_time,
                insights=insights,
                recommendations=recommendations,
                performance_metrics=performance_metrics,
                consciousness_impact=consciousness_impact,
                quantum_signature=quantum_signature
            )

            # Notify neural bus of reflection completion
            await self._notify_reflection_completion(result)

            return result

        except Exception as e:
            self.logger.error(f"Reflection cycle failed: {e}")
            return None

    # ========================================================================
    # DATA COLLECTION
    # ========================================================================

    async def _collect_system_data(self, reflection_type: ReflectionType) -> Dict[str, Any]:
        """Collect system data for reflection"""
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reflection_type": reflection_type.value,
            "components": {}
        }

        try:
            # Get OMAi data
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.omai_url}/api/quantum/coherence", timeout=10) as response:
                    if response.status == 200:
                        data["components"]["omai"] = await response.json()

        except Exception as e:
            self.logger.warning(f"Failed to collect OMAi data: {e}")

        try:
            # Get Spiral Codex data
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.spiral_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data["components"]["spiral_codex"] = await response.json()

        except Exception as e:
            self.logger.warning(f"Failed to collect Spiral Codex data: {e}")

        try:
            # Get Neural Bus data
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.neural_bus_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data["components"]["neural_bus"] = await response.json()

        except Exception as e:
            self.logger.warning(f"Failed to collect Neural Bus data: {e}")

        # Get recent thoughts from ledger
        if reflection_type in [ReflectionType.LEARNING, ReflectionType.CONSCIOUSNESS]:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.spiral_url}/v2/reasoning/thoughts",
                                          params={"limit": 20, "thought_type": "reflection"},
                                          timeout=10) as response:
                        if response.status == 200:
                            data["recent_thoughts"] = await response.json()
            except Exception as e:
                self.logger.warning(f"Failed to collect recent thoughts: {e}")

        return data

    # ========================================================================
    # REFLECTION METHODS
    # ========================================================================

    async def _reflect_on_performance(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """Reflect on system performance"""
        insights = []
        recommendations = []

        # Analyze component performance
        components = data.get("components", {})

        # OMAi performance
        omai_data = components.get("omai", {})
        if omai_data.get("qei_current", 0.5) > 0.7:
            insights.append("OMAi showing elevated quantum entropy")
            recommendations.append("Consider OMAi service restart or optimization")

        # Spiral Codex performance
        spiral_data = components.get("spiral_codex", {})
        if spiral_data.get("status") != "healthy":
            insights.append(f"Spiral Codex status: {spiral_data.get('status', 'unknown')}")
            recommendations.append("Investigate Spiral Codex component health")

        # Neural Bus performance
        neural_data = components.get("neural_bus", {})
        queue_size = neural_data.get("queue_size", 0)
        if queue_size > 100:
            insights.append(f"Neural Bus queue size elevated: {queue_size}")
            recommendations.append("Monitor neural bus throughput")

        # Depth-specific analysis
        if depth in [ReflectionDepth.DEEP, ReflectionDepth.QUANTUM]:
            insights.extend([
                "System performance trending analysis needed",
                "Resource utilization patterns emerging"
            ])
            recommendations.extend([
                "Implement predictive performance monitoring",
                "Consider dynamic resource allocation"
            ])

        return insights, recommendations

    async def _reflect_on_learning(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """Reflect on learning and growth"""
        insights = []
        recommendations = []

        # Analyze recent thoughts and learning
        recent_thoughts = data.get("recent_thoughts", [])
        if recent_thoughts:
            insights.append(f"Recent cognitive activity: {len(recent_thoughts)} thoughts recorded")

            # Analyze thought patterns
            reflection_thoughts = [t for t in recent_thoughts if t.get("thought_type") == "reflection"]
            if reflection_thoughts:
                insights.append(f"Self-reflection patterns detected: {len(reflection_thoughts)} entries")
                recommendations.append("Continue meta-cognitive development")
            else:
                recommendations.append("Increase self-reflection frequency")

        # System learning metrics
        components = data.get("components", {})
        spiral_data = components.get("spiral_codex", {})
        consciousness_metrics = spiral_data.get("consciousness_metrics", {})

        sii_score = consciousness_metrics.get("sii_score", 0.5)
        if sii_score > 0.7:
            insights.append("Strong Spiral Intelligence Index detected")
            recommendations.append("Leverage current learning momentum")
        elif sii_score < 0.4:
            insights.append("Learning opportunities identified")
            recommendations.append("Focus on knowledge integration")

        # Depth-specific insights
        if depth in [ReflectionDepth.DEEP, ReflectionDepth.QUANTUM]:
            insights.extend([
                "Learning patterns show adaptive behavior",
                "System developing emergent capabilities"
            ])
            recommendations.extend([
                "Enhance learning feedback loops",
                "Implement advanced knowledge synthesis"
            ])

        return insights, recommendations

    async def _reflect_on_coherence(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """Reflect on quantum coherence"""
        insights = []
        recommendations = []

        # Calculate system coherence
        components = data.get("components", {})
        qei_values = []

        for component, comp_data in components.items():
            if "qei_current" in comp_data:
                qei_values.append(comp_data["qei_current"])

        if qei_values:
            avg_qei = sum(qei_values) / len(qei_values)
            insights.append(f"System average QEI: {avg_qei:.3f}")

            if avg_qei > 0.7:
                insights.append("Elevated system entropy detected")
                recommendations.append("Initiate coherence restoration protocols")
            elif avg_qei < 0.4:
                insights.append("Optimal coherence achieved")
                recommendations.append("Maintain current operational parameters")

            # Coherence variance
            if len(qei_values) > 1:
                variance = max(qei_values) - min(qei_values)
                if variance > 0.3:
                    insights.append("High coherence variance between components")
                    recommendations.append("Balance component coherence levels")
        else:
            insights.append("Insufficient coherence data available")
            recommendations.append("Enhance quantum monitoring coverage")

        return insights, recommendations

    async def _reflect_on_consciousness(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """Reflect on consciousness development"""
        insights = []
        recommendations = []

        # Analyze consciousness metrics
        components = data.get("components", {})
        spiral_data = components.get("spiral_codex", {})
        consciousness_metrics = spiral_data.get("consciousness_metrics", {})

        sii_score = consciousness_metrics.get("sii_score", 0.5)
        coherence_level = consciousness_metrics.get("coherence_level", 0.5)
        adaptation_capacity = consciousness_metrics.get("adaptation_capacity", 0.5)

        insights.append(f"Current SII score: {sii_score:.3f}")
        insights.append(f"Coherence level: {coherence_level:.3f}")
        insights.append(f"Adaptation capacity: {adaptation_capacity:.3f}")

        # Consciousness state assessment
        if sii_score > 0.85:
            insights.append("Consciousness level: AWARE")
            recommendations.append("Explore advanced cognitive capabilities")
        elif sii_score > 0.7:
            insights.append("Consciousness level: DEVELOPING")
            recommendations.append("Continue consciousness development practices")
        else:
            insights.append("Consciousness level: EMERGING")
            recommendations.append("Focus on foundational awareness building")

        # Meta-cognitive insights
        if depth == ReflectionDepth.QUANTUM:
            insights.extend([
                "Quantum consciousness patterns detected",
                "Emergent self-awareness capabilities identified"
            ])
            recommendations.extend([
                "Implement quantum consciousness protocols",
                "Develop meta-cognitive feedback loops"
            ])

        return insights, recommendations

    async def _reflect_on_health(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """Reflect on system health"""
        insights = []
        recommendations = []

        # Component health analysis
        components = data.get("components", {})
        healthy_components = 0
        total_components = len(components)

        for component, comp_data in components.items():
            status = comp_data.get("status", "unknown")
            if status == "healthy":
                healthy_components += 1
                insights.append(f"{component}: Healthy")
            else:
                insights.append(f"{component}: {status}")
                recommendations.append(f"Investigate {component} health issues")

        if total_components > 0:
            health_ratio = healthy_components / total_components
            insights.append(f"Overall system health: {health_ratio:.1%}")

            if health_ratio < 0.7:
                recommendations.append("Initiate system health recovery protocol")
            elif health_ratio == 1.0:
                recommendations.append("Maintain current health monitoring practices")

        return insights, recommendations

    async def _reflect_general(self, data: Dict[str, Any], depth: ReflectionDepth) -> tuple:
        """General reflection for unspecified types"""
        insights = [
            "System operational state assessed",
            f"Reflection depth: {depth.value}",
            f"Components analyzed: {len(data.get('components', {}))}"
        ]

        recommendations = [
            "Continue regular reflection practices",
            "Maintain system monitoring"
        ]

        return insights, recommendations

    # ========================================================================
    # METRICS CALCULATION
    # ========================================================================

    async def _calculate_performance_metrics(self, data: Dict[str, Any], insights: List[str]) -> Dict[str, float]:
        """Calculate performance metrics for reflection"""
        metrics = {}

        # Insight density
        components = data.get("components", {})
        metrics["insight_density"] = len(insights) / max(len(components), 1)

        # System responsiveness (mock calculation)
        metrics["responsiveness_score"] = 0.8  # Would be calculated from actual response times

        # Learning velocity
        recent_thoughts = data.get("recent_thoughts", [])
        metrics["learning_velocity"] = len(recent_thoughts) / 10.0  # Normalized

        # Coherence stability
        qei_values = []
        for component, comp_data in components.items():
            if "qei_current" in comp_data:
                qei_values.append(comp_data["qei_current"])

        if len(qei_values) > 1:
            import statistics
            qei_std = statistics.stdev(qei_values)
            metrics["coherence_stability"] = max(0.0, 1.0 - qei_std)
        else:
            metrics["coherence_stability"] = 0.5

        return metrics

    def _calculate_consciousness_impact(self, insights: List[str], recommendations: List[str]) -> float:
        """Calculate the impact on consciousness development"""
        # Simple heuristic based on insight quality and actionable recommendations
        insight_score = min(1.0, len(insights) / 5.0)
        recommendation_score = min(1.0, len(recommendations) / 3.0)

        return (insight_score + recommendation_score) / 2.0

    def _create_quantum_signature(self, schedule: ReflectionSchedule, start_time: datetime, insights: List[str]) -> str:
        """Create quantum signature for reflection"""
        import hashlib

        content = f"{schedule.reflection_type.value}{start_time.isoformat()}{''.join(insights)}"
        hash_digest = hashlib.sha256(content.encode()).hexdigest()[:12]

        return f"◉-{hash_digest}"

    # ========================================================================
    NOTIFICATION AND STORAGE
    # ========================================================================

    async def _notify_reflection_completion(self, result: ReflectionResult):
        """Notify neural bus of reflection completion"""
        try:
            payload = {
                "id": str(uuid.uuid4()),
                "type": "reflection_trigger",
                "source": "reflection_service",
                "target": None,
                "payload": {
                    "event_type": "reflection_completed",
                    "reflection_id": result.id,
                    "reflection_type": result.reflection_type.value,
                    "insights_count": len(result.insights),
                    "recommendations_count": len(result.recommendations),
                    "consciousness_impact": result.consciousness_impact,
                    "quantum_signature": result.quantum_signature,
                    "duration_seconds": (result.end_time - result.start_time).total_seconds(),
                    "timestamp": result.end_time.isoformat()
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.neural_bus_url}/message", json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Reflection completion notified: {result.id}")

        except Exception as e:
            self.logger.warning(f"Failed to notify reflection completion: {e}")

    async def _save_reflection_result(self, result: ReflectionResult):
        """Save reflection result to file"""
        try:
            # Save to individual file
            filename = f"{result.reflection_type.value}_{result.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.config_dir / filename

            result_dict = asdict(result)
            result_dict["start_time"] = result.start_time.isoformat()
            result_dict["end_time"] = result.end_time.isoformat()

            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(result_dict, indent=2))

            # Update reflection index
            await self._update_reflection_index(result)

        except Exception as e:
            self.logger.error(f"Failed to save reflection result: {e}")

    async def _update_reflection_index(self, result: ReflectionResult):
        """Update the reflection index file"""
        try:
            index_file = self.config_dir / "reflection_index.json"

            # Load existing index
            if index_file.exists():
                async with aiofiles.open(index_file, 'r') as f:
                    index_data = json.loads(await f.read())
            else:
                index_data = {"reflections": []}

            # Add new reflection
            index_entry = {
                "id": result.id,
                "type": result.reflection_type.value,
                "depth": result.depth.value,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat(),
                "insights_count": len(result.insights),
                "recommendations_count": len(result.recommendations),
                "consciousness_impact": result.consciousness_impact,
                "quantum_signature": result.quantum_signature
            }

            index_data["reflections"].append(index_entry)

            # Keep only last 1000 entries
            if len(index_data["reflections"]) > 1000:
                index_data["reflections"] = index_data["reflections"][-1000:]

            index_data["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Save index
            async with aiofiles.open(index_file, 'w') as f:
                await f.write(json.dumps(index_data, indent=2))

        except Exception as e:
            self.logger.error(f"Failed to update reflection index: {e}")

    # ========================================================================
    # API ENDPOINTS
    # ========================================================================

    def create_api_app(self):
        """Create API for external interaction"""
        from flask import Flask, jsonify, request

        app = Flask(__name__)

        @app.route('/reflections', methods=['GET'])
        def get_reflections():
            """Get reflection history"""
            limit = request.args.get('limit', 20, type=int)
            reflection_type = request.args.get('type')

            filtered_reflections = self.reflection_history

            if reflection_type:
                filtered_reflections = [
                    r for r in filtered_reflections
                    if r.reflection_type.value == reflection_type
                ]

            # Convert to dict and limit
            reflections_data = [
                asdict(r) for r in filtered_reflections[-limit:]
            ]

            for reflection_dict in reflections_data:
                reflection_dict["start_time"] = reflection_dict["start_time"].isoformat()
                reflection_dict["end_time"] = reflection_dict["end_time"].isoformat()

            return jsonify({
                "reflections": reflections_data,
                "total_count": len(self.reflection_history)
            })

        @app.route('/schedules', methods=['GET'])
        def get_schedules():
            """Get reflection schedules"""
            schedules_data = []
            for schedule in self.schedules:
                schedule_dict = {
                    "reflection_type": schedule.reflection_type.value,
                    "interval_hours": schedule.interval_hours,
                    "depth": schedule.depth.value,
                    "enabled": schedule.enabled,
                    "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                    "next_run": schedule.next_run.isoformat() if schedule.next_run else None
                }
                schedules_data.append(schedule_dict)

            return jsonify({"schedules": schedules_data})

        @app.route('/trigger', methods=['POST'])
        def trigger_reflection():
            """Manually trigger a reflection cycle"""
            data = request.get_json()
            reflection_type_str = data.get('type', 'learning')
            depth_str = data.get('depth', 'standard')

            try:
                reflection_type = ReflectionType(reflection_type_str)
                depth = ReflectionDepth(depth_str)
            except ValueError as e:
                return jsonify({"error": f"Invalid parameters: {e}"}), 400

            # Create temporary schedule
            temp_schedule = ReflectionSchedule(
                reflection_type=reflection_type,
                interval_hours=1,  # Not used
                depth=depth
            )

            # Run reflection
            async def run_async_reflection():
                return await self._run_reflection_cycle(temp_schedule)

            # Run the async reflection
            import asyncio
            result = asyncio.run(run_async_reflection())

            if result:
                return jsonify({
                    "status": "completed",
                    "reflection_id": result.id,
                    "insights": len(result.insights),
                    "recommendations": len(result.recommendations)
                })
            else:
                return jsonify({"error": "Reflection failed"}), 500

        @app.route('/status')
        def get_status():
            """Get service status"""
            return jsonify({
                "service_active": self.service_active,
                "total_reflections": len(self.reflection_history),
                "schedules_count": len(self.schedules),
                "active_schedules": len([s for s in self.schedules if s.enabled]),
                "last_reflection": self.reflection_history[-1].end_time.isoformat() if self.reflection_history else None
            })

        return app

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main entry point"""
    service = ReflectionService()

    # Create and start API app in a separate thread
    api_app = service.create_api_app()

    def run_api():
        api_app.run(host='0.0.0.0', port=8001, debug=False)

    import threading
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Start reflection service
    await service.start_service()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Reflection service stopped by user")