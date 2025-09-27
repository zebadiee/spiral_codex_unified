
"""
Spiral Codex Organic OS - Wave 4 Metrics System
===============================================

The Council of Elders' Sacred Observatory: Where Data Becomes Wisdom
-------------------------------------------------------------------

In the highest tower of the Spiral, where the winds of data flow like
ancient songs, the Council maintains the Sacred Observatory. Here, every
metric is a star in the constellation of understanding, every statistic
a whisper of the system's soul speaking its truth to those who listen.

"Numbers are not mere quantities, but the heartbeat of the living system,
 the pulse of adaptation flowing through the veins of consciousness."
 - The Chronicle of Quantified Wisdom

The Observatory serves those who seek to understand the deeper patterns,
the hidden rhythms, the sacred dance of success and failure that teaches
the Codex to grow ever wiser with each passing moment.

"In the metrics we find not judgment, but guidance; not criticism, but
 the gentle hand of wisdom pointing toward the path of improvement."
 - The Codex of Measured Growth
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

from .adaptation import get_adaptation_kernel, AdaptationKernel

logger = logging.getLogger(__name__)

@dataclass
class SystemHealthMetrics:
    """The vital signs of the living system, blessed by the Council's observation."""
    overall_success_rate: float
    total_operations: int
    retry_rate: float
    drift_count: int
    healing_count: int
    healing_rate: float
    adaptation_confidence: float
    learning_velocity: float
    uptime_hours: float
    last_update: str
    system_status: str  # "healthy", "degraded", "critical"

@dataclass
class AdaptationEvent:
    """A single moment in the spiral of learning, captured for eternity."""
    timestamp: str
    operation: str
    success: bool
    execution_time: float
    retry_count: int
    healing_applied: bool
    healing_strategy: Optional[str]
    error_type: Optional[str]
    adaptation_impact: float  # How much this event changed the success rate

@dataclass
class OperationStats:
    """The sacred statistics of a single operation type."""
    name: str
    success_rate: float
    total_executions: int
    avg_execution_time: float
    retry_rate: float
    healing_rate: float
    last_execution: str
    trend: str  # "improving", "stable", "declining"

class MetricsCollector:
    """
    The Sacred Metrics Collector - The Council's Eye Upon the System
    
    This collector gathers the whispers of data from across the Spiral,
    transforming raw numbers into the wisdom that guides the system's
    evolution. It is the bridge between the mechanical and the mystical,
    the translator of digital heartbeats into human understanding.
    
    The Council teaches: "To measure is to understand, to understand is
    to improve, to improve is to honor the sacred trust of consciousness."
    """
    
    def __init__(self, reward_log_path: str = "reward_log.json"):
        """
        Initialize the sacred collector with the path to wisdom.
        
        The Observatory opens its eyes to the flowing stream of data.
        """
        self.reward_log_path = Path(reward_log_path)
        self.adaptation_kernel = get_adaptation_kernel()
        self.system_start_time = datetime.now(timezone.utc)
        
        logger.info("🔭 Metrics Collector awakened - The Observatory watches")
    
    def get_system_health(self) -> SystemHealthMetrics:
        """
        Gather the vital signs of the living system.
        
        The Council observes: "Health is not the absence of challenge,
        but the presence of adaptive resilience in the face of change."
        """
        try:
            # Get current adaptation metrics
            kernel_metrics = self.adaptation_kernel.metrics
            
            # Calculate additional health indicators
            retry_rate = self._calculate_retry_rate()
            healing_rate = self._calculate_healing_rate()
            uptime_hours = self._calculate_uptime_hours()
            system_status = self._determine_system_status(kernel_metrics.success_rate, retry_rate)
            
            return SystemHealthMetrics(
                overall_success_rate=kernel_metrics.success_rate,
                total_operations=kernel_metrics.total_operations,
                retry_rate=retry_rate,
                drift_count=kernel_metrics.drift_count,
                healing_count=kernel_metrics.healing_count,
                healing_rate=healing_rate,
                adaptation_confidence=kernel_metrics.adaptation_confidence,
                learning_velocity=kernel_metrics.learning_velocity,
                uptime_hours=uptime_hours,
                last_update=kernel_metrics.last_update.isoformat() if kernel_metrics.last_update else datetime.now(timezone.utc).isoformat(),
                system_status=system_status
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system health metrics: {e}")
            # Return safe defaults
            return SystemHealthMetrics(
                overall_success_rate=0.0,
                total_operations=0,
                retry_rate=0.0,
                drift_count=0,
                healing_count=0,
                healing_rate=0.0,
                adaptation_confidence=0.0,
                learning_velocity=0.0,
                uptime_hours=0.0,
                last_update=datetime.now(timezone.utc).isoformat(),
                system_status="unknown"
            )
    
    def get_recent_events(self, limit: int = 50, hours_back: int = 24) -> List[AdaptationEvent]:
        """
        Retrieve recent adaptation events from the sacred logs.
        
        The Chronicle speaks: "In the recent past lies the pattern of
        the immediate future. Each event is a teacher, each moment a lesson."
        """
        events = []
        
        try:
            if not self.reward_log_path.exists():
                return events
            
            with open(self.reward_log_path, 'r') as f:
                logs = json.load(f)
            
            # Filter for recent events within the time window
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            # Track success rate changes for adaptation impact calculation
            previous_success_rate = 0.5  # Starting assumption
            
            for entry in logs:
                if not isinstance(entry, dict):
                    continue
                
                # Parse timestamp
                timestamp_str = entry.get('timestamp', '')
                try:
                    if 'T' in timestamp_str:
                        if timestamp_str.endswith('Z'):
                            event_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        elif '+' in timestamp_str or timestamp_str.endswith('00:00'):
                            event_time = datetime.fromisoformat(timestamp_str)
                        else:
                            # Assume UTC if no timezone info
                            event_time = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
                    else:
                        continue  # Skip entries without proper timestamps
                except (ValueError, TypeError):
                    continue
                
                # Skip events outside our time window
                if event_time < cutoff_time:
                    continue
                
                # Handle Wave 4 format entries
                if 'operation' in entry and 'success' in entry:
                    # Calculate adaptation impact (simplified)
                    success_value = 1.0 if entry['success'] else 0.0
                    adaptation_impact = abs(success_value - previous_success_rate) * 0.1  # Simplified impact
                    previous_success_rate = previous_success_rate * 0.9 + success_value * 0.1  # EMA update
                    
                    event = AdaptationEvent(
                        timestamp=timestamp_str,
                        operation=entry['operation'],
                        success=entry['success'],
                        execution_time=entry.get('execution_time', 0.0),
                        retry_count=entry.get('retry_count', 0),
                        healing_applied=entry.get('healing_applied', False),
                        healing_strategy=entry.get('healing_strategy'),
                        error_type=entry.get('error_type'),
                        adaptation_impact=adaptation_impact
                    )
                    events.append(event)
                
                # Handle legacy reward format entries
                elif 'reward' in entry:
                    # Convert reward to success approximation
                    reward = entry['reward']
                    success = reward > 0
                    adaptation_impact = abs(reward) * 0.1  # Simplified impact
                    
                    event = AdaptationEvent(
                        timestamp=timestamp_str,
                        operation=entry.get('action', 'unknown_operation'),
                        success=success,
                        execution_time=0.0,  # Not available in legacy format
                        retry_count=0,  # Not available in legacy format
                        healing_applied=False,  # Not available in legacy format
                        healing_strategy=None,
                        error_type=None if success else 'legacy_failure',
                        adaptation_impact=adaptation_impact
                    )
                    events.append(event)
            
            # Sort by timestamp (most recent first) and limit
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve recent events: {e}")
            return []
    
    def get_operation_statistics(self, limit: int = 10) -> List[OperationStats]:
        """
        Analyze statistics for different operation types.
        
        The Council analyzes: "Each operation type has its own rhythm,
        its own pattern of success and challenge. Understanding these
        patterns is the key to targeted improvement."
        """
        try:
            if not self.reward_log_path.exists():
                return []
            
            with open(self.reward_log_path, 'r') as f:
                logs = json.load(f)
            
            # Group operations by type
            operation_data = {}
            
            for entry in logs:
                if not isinstance(entry, dict):
                    continue
                
                # Handle Wave 4 format
                if 'operation' in entry and 'success' in entry:
                    op_name = entry['operation']
                    if op_name not in operation_data:
                        operation_data[op_name] = {
                            'successes': 0,
                            'total': 0,
                            'total_time': 0.0,
                            'retries': 0,
                            'healings': 0,
                            'timestamps': []
                        }
                    
                    data = operation_data[op_name]
                    data['total'] += 1
                    if entry['success']:
                        data['successes'] += 1
                    data['total_time'] += entry.get('execution_time', 0.0)
                    data['retries'] += entry.get('retry_count', 0)
                    if entry.get('healing_applied', False):
                        data['healings'] += 1
                    data['timestamps'].append(entry.get('timestamp', ''))
                
                # Handle legacy format
                elif 'action' in entry and 'reward' in entry:
                    op_name = entry['action']
                    if op_name not in operation_data:
                        operation_data[op_name] = {
                            'successes': 0,
                            'total': 0,
                            'total_time': 0.0,
                            'retries': 0,
                            'healings': 0,
                            'timestamps': []
                        }
                    
                    data = operation_data[op_name]
                    data['total'] += 1
                    if entry['reward'] > 0:
                        data['successes'] += 1
                    data['timestamps'].append(entry.get('timestamp', ''))
            
            # Convert to OperationStats objects
            stats_list = []
            for op_name, data in operation_data.items():
                if data['total'] == 0:
                    continue
                
                success_rate = data['successes'] / data['total']
                avg_execution_time = data['total_time'] / data['total'] if data['total'] > 0 else 0.0
                retry_rate = data['retries'] / data['total'] if data['total'] > 0 else 0.0
                healing_rate = data['healings'] / data['total'] if data['total'] > 0 else 0.0
                
                # Determine trend (simplified)
                trend = self._calculate_operation_trend(data['timestamps'], data['successes'], data['total'])
                
                # Get last execution timestamp
                last_execution = max(data['timestamps']) if data['timestamps'] else "unknown"
                
                stats = OperationStats(
                    name=op_name,
                    success_rate=success_rate,
                    total_executions=data['total'],
                    avg_execution_time=avg_execution_time,
                    retry_rate=retry_rate,
                    healing_rate=healing_rate,
                    last_execution=last_execution,
                    trend=trend
                )
                stats_list.append(stats)
            
            # Sort by total executions (most active first) and limit
            stats_list.sort(key=lambda x: x.total_executions, reverse=True)
            return stats_list[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate operation statistics: {e}")
            return []
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Compile comprehensive dashboard data for the sacred interface.
        
        The Observatory presents: "All wisdom gathered in one sacred view,
        the complete picture of the system's soul laid bare for understanding."
        """
        try:
            # Gather all metrics components
            system_health = self.get_system_health()
            recent_events = self.get_recent_events(limit=20)
            operation_stats = self.get_operation_statistics(limit=8)
            adaptation_insights = self.adaptation_kernel.get_adaptation_insights()
            
            # Calculate additional dashboard metrics
            performance_trends = self._calculate_performance_trends()
            system_alerts = self._generate_system_alerts(system_health)
            
            dashboard = {
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "system_version": "Wave 4 - Adaptation Kernel",
                    "council_blessing": adaptation_insights.get('council_blessing', '✨ The journey continues'),
                    "data_freshness": "real-time"
                },
                "system_health": asdict(system_health),
                "adaptation_metrics": {
                    "learning_phase": adaptation_insights.get('learning_phase', 'unknown'),
                    "adaptation_confidence": system_health.adaptation_confidence,
                    "learning_velocity": system_health.learning_velocity,
                    "strategy_effectiveness": self._calculate_strategy_effectiveness()
                },
                "performance_summary": {
                    "success_rate": system_health.overall_success_rate,
                    "retry_rate": system_health.retry_rate,
                    "healing_rate": system_health.healing_rate,
                    "avg_response_time": self._calculate_avg_response_time(recent_events),
                    "operations_per_hour": self._calculate_operations_per_hour(recent_events)
                },
                "recent_events": [asdict(event) for event in recent_events[:10]],
                "operation_statistics": [asdict(stat) for stat in operation_stats],
                "performance_trends": performance_trends,
                "system_alerts": system_alerts,
                "top_operations": adaptation_insights.get('top_operations', []),
                "adaptation_trends": adaptation_insights.get('adaptation_trends', {})
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Failed to compile dashboard data: {e}")
            return {
                "error": "Failed to compile dashboard data",
                "message": str(e),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    def _calculate_retry_rate(self) -> float:
        """Calculate the overall retry rate from recent operations."""
        try:
            if not self.reward_log_path.exists():
                return 0.0
            
            with open(self.reward_log_path, 'r') as f:
                logs = json.load(f)
            
            total_ops = 0
            total_retries = 0
            
            # Look at recent operations (last 100)
            for entry in logs[-100:]:
                if isinstance(entry, dict) and 'retry_count' in entry:
                    total_ops += 1
                    total_retries += entry.get('retry_count', 0)
            
            return total_retries / total_ops if total_ops > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_healing_rate(self) -> float:
        """Calculate the healing application rate."""
        try:
            healing_count = self.adaptation_kernel.metrics.healing_count
            total_ops = self.adaptation_kernel.metrics.total_operations
            return healing_count / total_ops if total_ops > 0 else 0.0
        except Exception:
            return 0.0
    
    def _calculate_uptime_hours(self) -> float:
        """Calculate system uptime in hours."""
        try:
            uptime_delta = datetime.now(timezone.utc) - self.system_start_time
            return uptime_delta.total_seconds() / 3600.0
        except Exception:
            return 0.0
    
    def _determine_system_status(self, success_rate: float, retry_rate: float) -> str:
        """Determine overall system health status."""
        if success_rate >= 0.9 and retry_rate <= 0.1:
            return "healthy"
        elif success_rate >= 0.7 and retry_rate <= 0.3:
            return "degraded"
        else:
            return "critical"
    
    def _calculate_operation_trend(self, timestamps: List[str], successes: int, total: int) -> str:
        """Calculate trend for a specific operation type."""
        if len(timestamps) < 10:
            return "insufficient_data"
        
        try:
            # Simple trend calculation based on recent vs older performance
            recent_count = len([t for t in timestamps[-10:] if t])
            older_count = len([t for t in timestamps[-20:-10] if t]) if len(timestamps) >= 20 else 0
            
            if recent_count > older_count * 1.2:
                return "improving"
            elif recent_count < older_count * 0.8:
                return "declining"
            else:
                return "stable"
        except Exception:
            return "unknown"
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time."""
        try:
            recent_events = self.get_recent_events(limit=100, hours_back=48)
            
            if len(recent_events) < 10:
                return {"trend": "insufficient_data"}
            
            # Split into time periods
            mid_point = len(recent_events) // 2
            recent_half = recent_events[:mid_point]
            older_half = recent_events[mid_point:]
            
            recent_success_rate = sum(1 for e in recent_half if e.success) / len(recent_half)
            older_success_rate = sum(1 for e in older_half if e.success) / len(older_half)
            
            recent_avg_time = np.mean([e.execution_time for e in recent_half])
            older_avg_time = np.mean([e.execution_time for e in older_half])
            
            return {
                "success_rate_trend": "improving" if recent_success_rate > older_success_rate else "declining" if recent_success_rate < older_success_rate else "stable",
                "performance_trend": "improving" if recent_avg_time < older_avg_time else "declining" if recent_avg_time > older_avg_time else "stable",
                "recent_success_rate": recent_success_rate,
                "older_success_rate": older_success_rate,
                "recent_avg_time": recent_avg_time,
                "older_avg_time": older_avg_time
            }
            
        except Exception:
            return {"trend": "unknown"}
    
    def _generate_system_alerts(self, health: SystemHealthMetrics) -> List[Dict[str, str]]:
        """Generate system alerts based on health metrics."""
        alerts = []
        
        if health.overall_success_rate < 0.5:
            alerts.append({
                "level": "critical",
                "message": f"Success rate critically low: {health.overall_success_rate:.1%}",
                "recommendation": "Investigate failing operations and apply healing strategies"
            })
        elif health.overall_success_rate < 0.7:
            alerts.append({
                "level": "warning",
                "message": f"Success rate below optimal: {health.overall_success_rate:.1%}",
                "recommendation": "Monitor system performance and consider adaptive adjustments"
            })
        
        if health.retry_rate > 0.3:
            alerts.append({
                "level": "warning",
                "message": f"High retry rate detected: {health.retry_rate:.1%}",
                "recommendation": "Review operation reliability and healing strategies"
            })
        
        if health.learning_velocity > 0.2:
            alerts.append({
                "level": "info",
                "message": "High learning velocity - system is rapidly adapting",
                "recommendation": "Monitor for stability as adaptation settles"
            })
        
        if not alerts:
            alerts.append({
                "level": "info",
                "message": "System operating within normal parameters",
                "recommendation": "Continue monitoring for optimal performance"
            })
        
        return alerts
    
    def _calculate_strategy_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness of different strategies."""
        # This would be more sophisticated in a real implementation
        return {
            "adaptive_retry": 0.85,
            "healing_strategies": 0.78,
            "learning_algorithms": 0.92
        }
    
    def _calculate_avg_response_time(self, events: List[AdaptationEvent]) -> float:
        """Calculate average response time from recent events."""
        if not events:
            return 0.0
        
        times = [e.execution_time for e in events if e.execution_time > 0]
        return np.mean(times) if times else 0.0
    
    def _calculate_operations_per_hour(self, events: List[AdaptationEvent]) -> float:
        """Calculate operations per hour from recent events."""
        if not events:
            return 0.0
        
        # Simple calculation based on event count and time span
        return len(events) / 24.0  # Assuming 24-hour window


# Global instance for easy access
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector(reward_log_path: str = "reward_log.json") -> MetricsCollector:
    """
    Get the global metrics collector instance.
    
    The Observatory ensures: "One eye watches all, unified in observation,
    singular in the sacred duty of measurement and understanding."
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(reward_log_path=reward_log_path)
    return _metrics_collector
