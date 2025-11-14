
"""
System Monitor - Real-time system metrics and performance monitoring
"""

import asyncio
import json
import psutil
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class MetricType(Enum):
    """Types of system metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    QUEUE_LENGTH = "queue_length"


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    queue_length: int
    response_time_avg: float
    throughput: float
    error_rate: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    metric_type: MetricType
    threshold_value: float
    actual_value: float
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    resolved: bool = False


class SystemMonitor:
    """
    Real-time system performance monitor
    Tracks system metrics, detects anomalies, and provides performance insights
    """
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Metrics storage
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        
        # Performance thresholds
        self.thresholds = {
            MetricType.CPU_USAGE: {'warning': 70.0, 'critical': 90.0},
            MetricType.MEMORY_USAGE: {'warning': 80.0, 'critical': 95.0},
            MetricType.DISK_USAGE: {'warning': 85.0, 'critical': 95.0},
            MetricType.RESPONSE_TIME: {'warning': 5.0, 'critical': 10.0},
            MetricType.ERROR_RATE: {'warning': 0.05, 'critical': 0.1},
            MetricType.QUEUE_LENGTH: {'warning': 100, 'critical': 500}
        }
        
        # Alerts
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_history: List[PerformanceAlert] = []
        
        # Execution monitoring
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_metrics: List[Dict[str, Any]] = []
        
        # Baseline performance
        self.baseline_metrics = None
        self.performance_trends = {}
        
        # Start monitoring
        asyncio.create_task(self._start_monitoring())
    
    async def _start_monitoring(self):
        """Start the monitoring loop"""
        try:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
        except Exception as e:
            print(f"Error starting monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.is_monitoring:
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Update performance trends
                await self._update_performance_trends()
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
        except asyncio.CancelledError:
            print("Monitoring loop cancelled")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Active connections (approximate)
            connections = len(psutil.net_connections())
            
            # Calculate derived metrics
            queue_length = len(self.active_executions)
            
            # Response time average (from recent executions)
            recent_executions = self.execution_metrics[-10:] if self.execution_metrics else []
            response_time_avg = np.mean([
                e.get('execution_time', 1.0) for e in recent_executions
            ]) if recent_executions else 1.0
            
            # Throughput (executions per minute)
            now = datetime.now(timezone.utc)
            recent_window = now - timedelta(minutes=1)
            recent_count = sum(1 for e in self.execution_metrics 
                             if datetime.fromisoformat(e.get('timestamp', now.isoformat())) > recent_window)
            throughput = recent_count
            
            # Error rate
            recent_errors = sum(1 for e in recent_executions if not e.get('success', True))
            error_rate = recent_errors / len(recent_executions) if recent_executions else 0.0
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=connections,
                queue_length=queue_length,
                response_time_avg=response_time_avg,
                throughput=throughput,
                error_rate=error_rate,
                timestamp=now
            )
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            # Return default metrics
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_connections=0,
                queue_length=0,
                response_time_avg=1.0,
                throughput=0.0,
                error_rate=0.0,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _check_alerts(self, metrics: SystemMetrics):
        """Check for performance alerts"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Check CPU usage
            if metrics.cpu_usage > self.thresholds[MetricType.CPU_USAGE]['critical']:
                await self._create_alert(
                    MetricType.CPU_USAGE, metrics.cpu_usage,
                    self.thresholds[MetricType.CPU_USAGE]['critical'],
                    'critical', f"CPU usage critically high: {metrics.cpu_usage:.1f}%"
                )
            elif metrics.cpu_usage > self.thresholds[MetricType.CPU_USAGE]['warning']:
                await self._create_alert(
                    MetricType.CPU_USAGE, metrics.cpu_usage,
                    self.thresholds[MetricType.CPU_USAGE]['warning'],
                    'warning', f"CPU usage high: {metrics.cpu_usage:.1f}%"
                )
            
            # Check memory usage
            if metrics.memory_usage > self.thresholds[MetricType.MEMORY_USAGE]['critical']:
                await self._create_alert(
                    MetricType.MEMORY_USAGE, metrics.memory_usage,
                    self.thresholds[MetricType.MEMORY_USAGE]['critical'],
                    'critical', f"Memory usage critically high: {metrics.memory_usage:.1f}%"
                )
            elif metrics.memory_usage > self.thresholds[MetricType.MEMORY_USAGE]['warning']:
                await self._create_alert(
                    MetricType.MEMORY_USAGE, metrics.memory_usage,
                    self.thresholds[MetricType.MEMORY_USAGE]['warning'],
                    'warning', f"Memory usage high: {metrics.memory_usage:.1f}%"
                )
            
            # Check disk usage
            if metrics.disk_usage > self.thresholds[MetricType.DISK_USAGE]['critical']:
                await self._create_alert(
                    MetricType.DISK_USAGE, metrics.disk_usage,
                    self.thresholds[MetricType.DISK_USAGE]['critical'],
                    'critical', f"Disk usage critically high: {metrics.disk_usage:.1f}%"
                )
            elif metrics.disk_usage > self.thresholds[MetricType.DISK_USAGE]['warning']:
                await self._create_alert(
                    MetricType.DISK_USAGE, metrics.disk_usage,
                    self.thresholds[MetricType.DISK_USAGE]['warning'],
                    'warning', f"Disk usage high: {metrics.disk_usage:.1f}%"
                )
            
            # Check response time
            if metrics.response_time_avg > self.thresholds[MetricType.RESPONSE_TIME]['critical']:
                await self._create_alert(
                    MetricType.RESPONSE_TIME, metrics.response_time_avg,
                    self.thresholds[MetricType.RESPONSE_TIME]['critical'],
                    'critical', f"Response time critically high: {metrics.response_time_avg:.2f}s"
                )
            elif metrics.response_time_avg > self.thresholds[MetricType.RESPONSE_TIME]['warning']:
                await self._create_alert(
                    MetricType.RESPONSE_TIME, metrics.response_time_avg,
                    self.thresholds[MetricType.RESPONSE_TIME]['warning'],
                    'warning', f"Response time high: {metrics.response_time_avg:.2f}s"
                )
            
            # Check error rate
            if metrics.error_rate > self.thresholds[MetricType.ERROR_RATE]['critical']:
                await self._create_alert(
                    MetricType.ERROR_RATE, metrics.error_rate,
                    self.thresholds[MetricType.ERROR_RATE]['critical'],
                    'critical', f"Error rate critically high: {metrics.error_rate:.1%}"
                )
            elif metrics.error_rate > self.thresholds[MetricType.ERROR_RATE]['warning']:
                await self._create_alert(
                    MetricType.ERROR_RATE, metrics.error_rate,
                    self.thresholds[MetricType.ERROR_RATE]['warning'],
                    'warning', f"Error rate high: {metrics.error_rate:.1%}"
                )
            
            # Check queue length
            if metrics.queue_length > self.thresholds[MetricType.QUEUE_LENGTH]['critical']:
                await self._create_alert(
                    MetricType.QUEUE_LENGTH, metrics.queue_length,
                    self.thresholds[MetricType.QUEUE_LENGTH]['critical'],
                    'critical', f"Queue length critically high: {metrics.queue_length}"
                )
            elif metrics.queue_length > self.thresholds[MetricType.QUEUE_LENGTH]['warning']:
                await self._create_alert(
                    MetricType.QUEUE_LENGTH, metrics.queue_length,
                    self.thresholds[MetricType.QUEUE_LENGTH]['warning'],
                    'warning', f"Queue length high: {metrics.queue_length}"
                )
            
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    async def _create_alert(
        self,
        metric_type: MetricType,
        actual_value: float,
        threshold_value: float,
        severity: str,
        message: str
    ):
        """Create a performance alert"""
        try:
            # Check if similar alert already exists
            existing_alert = None
            for alert in self.active_alerts:
                if (alert.metric_type == metric_type and 
                    alert.severity == severity and 
                    not alert.resolved):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.actual_value = actual_value
                existing_alert.timestamp = datetime.now(timezone.utc)
            else:
                # Create new alert
                alert = PerformanceAlert(
                    alert_id=f"{metric_type.value}_{severity}_{int(datetime.now().timestamp())}",
                    metric_type=metric_type,
                    threshold_value=threshold_value,
                    actual_value=actual_value,
                    severity=severity,
                    message=message,
                    timestamp=datetime.now(timezone.utc)
                )
                
                self.active_alerts.append(alert)
                self.alert_history.append(alert)
                
                print(f"ALERT [{severity.upper()}]: {message}")
            
        except Exception as e:
            print(f"Error creating alert: {e}")
    
    async def _update_performance_trends(self):
        """Update performance trends analysis"""
        try:
            if len(self.metrics_history) < 10:
                return
            
            recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
            
            # Calculate trends for key metrics
            timestamps = [m.timestamp.timestamp() for m in recent_metrics]
            
            for metric_name in ['cpu_usage', 'memory_usage', 'response_time_avg', 'error_rate']:
                values = [getattr(m, metric_name) for m in recent_metrics]
                
                # Calculate trend (simple linear regression slope)
                if len(values) > 1:
                    trend = np.polyfit(timestamps, values, 1)[0]  # Slope
                    self.performance_trends[metric_name] = {
                        'trend': trend,
                        'current_value': values[-1],
                        'avg_value': np.mean(values),
                        'updated_at': datetime.now(timezone.utc)
                    }
            
        except Exception as e:
            print(f"Error updating performance trends: {e}")
    
    async def monitor_execution(self, ritual_id: str) -> Dict[str, Any]:
        """Monitor a specific ritual execution"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Add to active executions
            self.active_executions[ritual_id] = {
                'start_time': start_time,
                'status': 'running'
            }
            
            return {'status': 'monitoring_started', 'ritual_id': ritual_id}
            
        except Exception as e:
            print(f"Error starting execution monitoring: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def record_execution(self, orchestration_result) -> bool:
        """Record execution results for monitoring"""
        try:
            ritual_id = orchestration_result.ritual_id
            
            # Remove from active executions
            if ritual_id in self.active_executions:
                del self.active_executions[ritual_id]
            
            # Record execution metrics
            execution_record = {
                'ritual_id': ritual_id,
                'success': orchestration_result.success,
                'execution_time': orchestration_result.execution_time,
                'performance_metrics': orchestration_result.performance_metrics,
                'timestamp': orchestration_result.timestamp.isoformat()
            }
            
            self.execution_metrics.append(execution_record)
            
            # Keep only recent execution metrics
            if len(self.execution_metrics) > 1000:
                self.execution_metrics = self.execution_metrics[-1000:]
            
            return True
            
        except Exception as e:
            print(f"Error recording execution: {e}")
            return False
    
    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            if self.metrics_history:
                return self.metrics_history[-1]
            else:
                return await self._collect_system_metrics()
                
        except Exception as e:
            print(f"Error getting current metrics: {e}")
            return SystemMetrics(
                cpu_usage=0.0, memory_usage=0.0, disk_usage=0.0,
                network_io={}, active_connections=0, queue_length=0,
                response_time_avg=1.0, throughput=0.0, error_rate=0.0,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SystemMetrics]:
        """Get historical metrics"""
        try:
            metrics = self.metrics_history
            
            # Filter by time range
            if start_time:
                metrics = [m for m in metrics if m.timestamp >= start_time]
            if end_time:
                metrics = [m for m in metrics if m.timestamp <= end_time]
            
            # Apply limit
            if len(metrics) > limit:
                metrics = metrics[-limit:]
            
            return metrics
            
        except Exception as e:
            print(f"Error getting metrics history: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and statistics"""
        try:
            current_metrics = await self.get_current_metrics()
            
            # Calculate averages from recent history
            recent_metrics = self.metrics_history[-60:] if len(self.metrics_history) >= 60 else self.metrics_history
            
            if recent_metrics:
                avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
                avg_memory = np.mean([m.memory_usage for m in recent_metrics])
                avg_response_time = np.mean([m.response_time_avg for m in recent_metrics])
                avg_throughput = np.mean([m.throughput for m in recent_metrics])
                avg_error_rate = np.mean([m.error_rate for m in recent_metrics])
            else:
                avg_cpu = avg_memory = avg_response_time = avg_throughput = avg_error_rate = 0.0
            
            # Active alerts summary
            alert_summary = {
                'total_active': len(self.active_alerts),
                'by_severity': {}
            }
            
            for alert in self.active_alerts:
                severity = alert.severity
                alert_summary['by_severity'][severity] = alert_summary['by_severity'].get(severity, 0) + 1
            
            return {
                'current_metrics': asdict(current_metrics),
                'averages': {
                    'cpu_usage': avg_cpu,
                    'memory_usage': avg_memory,
                    'response_time': avg_response_time,
                    'throughput': avg_throughput,
                    'error_rate': avg_error_rate
                },
                'trends': self.performance_trends,
                'alerts': alert_summary,
                'active_executions': len(self.active_executions),
                'total_executions_recorded': len(self.execution_metrics),
                'monitoring_status': 'active' if self.is_monitoring else 'inactive'
            }
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    async def set_thresholds(self, new_thresholds: Dict[str, Dict[str, float]]):
        """Update performance thresholds"""
        try:
            for metric_type_str, thresholds in new_thresholds.items():
                try:
                    metric_type = MetricType(metric_type_str)
                    if metric_type in self.thresholds:
                        self.thresholds[metric_type].update(thresholds)
                except ValueError:
                    print(f"Unknown metric type: {metric_type_str}")
            
            print("Updated performance thresholds")
            
        except Exception as e:
            print(f"Error setting thresholds: {e}")
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        try:
            for alert in self.active_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    self.active_alerts.remove(alert)
                    print(f"Resolved alert: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error resolving alert: {e}")
            return False
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        try:
            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            print("Monitoring stopped")
            
        except Exception as e:
            print(f"Error stopping monitoring: {e}")
    
    def __del__(self):
        """Cleanup when monitor is destroyed"""
        if self.is_monitoring and self.monitoring_task:
            self.monitoring_task.cancel()
