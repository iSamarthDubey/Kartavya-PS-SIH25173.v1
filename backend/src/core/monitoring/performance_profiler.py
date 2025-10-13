"""
Performance Profiler for SIEM Backend
Comprehensive monitoring of API endpoints, database queries, and system performance
"""

import asyncio
import logging
import time
import json
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
from contextlib import asynccontextmanager
import traceback
import psutil
import os

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of queries to monitor"""
    API_ENDPOINT = "api_endpoint"
    DATABASE_QUERY = "database_query"
    CACHE_OPERATION = "cache_operation"
    EXTERNAL_API = "external_api"
    MULTI_SOURCE = "multi_source"


class PerformanceLevel(str, Enum):
    """Performance level thresholds"""
    EXCELLENT = "excellent"    # < 100ms
    GOOD = "good"             # 100ms - 500ms  
    ACCEPTABLE = "acceptable"  # 500ms - 2s
    SLOW = "slow"             # 2s - 5s
    CRITICAL = "critical"     # > 5s


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    query_id: str
    query_type: QueryType
    endpoint: str
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    @property
    def performance_level(self) -> PerformanceLevel:
        """Determine performance level based on execution time"""
        if self.execution_time < 0.1:
            return PerformanceLevel.EXCELLENT
        elif self.execution_time < 0.5:
            return PerformanceLevel.GOOD
        elif self.execution_time < 2.0:
            return PerformanceLevel.ACCEPTABLE
        elif self.execution_time < 5.0:
            return PerformanceLevel.SLOW
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class EndpointStats:
    """Statistics for a specific endpoint"""
    endpoint: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    recent_times: List[float] = field(default_factory=list)
    error_rates: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.total_requests == 0:
            return 0.0
        return self.total_time / self.total_requests
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.recent_times:
            return 0.0
        return statistics.quantiles(sorted(self.recent_times), n=20)[18]  # 95th percentile
    
    @property
    def current_performance_level(self) -> PerformanceLevel:
        """Get current performance level"""
        avg_time = self.avg_response_time
        if avg_time < 0.1:
            return PerformanceLevel.EXCELLENT
        elif avg_time < 0.5:
            return PerformanceLevel.GOOD
        elif avg_time < 2.0:
            return PerformanceLevel.ACCEPTABLE
        elif avg_time < 5.0:
            return PerformanceLevel.SLOW
        else:
            return PerformanceLevel.CRITICAL


class PerformanceProfiler:
    """Comprehensive performance profiler for backend operations"""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: List[PerformanceMetric] = []
        self.endpoint_stats: Dict[str, EndpointStats] = {}
        self.slow_query_threshold = 2.0  # seconds
        self.critical_query_threshold = 5.0  # seconds
        
        # Performance tracking
        self.active_requests: Dict[str, float] = {}  # request_id -> start_time
        self.alert_thresholds = {
            "avg_response_time": 1.0,    # 1 second
            "error_rate": 5.0,           # 5%
            "p95_response_time": 3.0,    # 3 seconds
        }
        
        # System monitoring
        self.system_stats_history: List[Dict[str, Any]] = []
        self.enable_system_monitoring = True
        
        logger.info("Performance profiler initialized")
    
    @asynccontextmanager
    async def profile_request(
        self, 
        query_type: QueryType, 
        endpoint: str, 
        query_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for profiling requests"""
        query_id = query_id or f"{endpoint}_{int(time.time() * 1000)}"
        metadata = metadata or {}
        
        start_time = time.time()
        start_memory = None
        start_cpu = None
        
        if self.enable_system_monitoring:
            try:
                process = psutil.Process()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
                start_cpu = process.cpu_percent()
            except Exception as e:
                logger.debug(f"Could not get system stats: {e}")
        
        self.active_requests[query_id] = start_time
        success = True
        error_message = None
        
        try:
            yield query_id
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Calculate memory/CPU delta
            memory_delta = None
            cpu_usage = None
            
            if self.enable_system_monitoring and start_memory is not None:
                try:
                    process = psutil.Process()
                    end_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_delta = end_memory - start_memory
                    cpu_usage = process.cpu_percent()
                except Exception:
                    pass
            
            # Create performance metric
            metric = PerformanceMetric(
                query_id=query_id,
                query_type=query_type,
                endpoint=endpoint,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=success,
                error_message=error_message,
                metadata=metadata,
                memory_usage=memory_delta,
                cpu_usage=cpu_usage
            )
            
            # Record the metric
            self._record_metric(metric)
            
            # Remove from active requests
            self.active_requests.pop(query_id, None)
            
            # Log slow queries
            if execution_time > self.slow_query_threshold:
                level = "WARNING" if execution_time < self.critical_query_threshold else "ERROR"
                logger.log(
                    getattr(logging, level),
                    f"🐌 Slow query detected [{query_id}]: {endpoint} took {execution_time:.3f}s"
                )
    
    def _record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        # Add to history
        self.metrics_history.append(metric)
        
        # Limit history size
        if len(self.metrics_history) > self.max_metrics_history:
            self.metrics_history = self.metrics_history[-self.max_metrics_history:]
        
        # Update endpoint stats
        endpoint = metric.endpoint
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = EndpointStats(endpoint=endpoint)
        
        stats = self.endpoint_stats[endpoint]
        stats.total_requests += 1
        stats.total_time += metric.execution_time
        stats.last_updated = metric.timestamp
        
        if metric.success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
            if metric.error_message:
                error_key = metric.error_message[:50]  # Truncate error message
                stats.error_rates[error_key] = stats.error_rates.get(error_key, 0) + 1
        
        # Update min/max times
        stats.min_time = min(stats.min_time, metric.execution_time)
        stats.max_time = max(stats.max_time, metric.execution_time)
        
        # Update recent times (keep last 100 for percentile calculations)
        stats.recent_times.append(metric.execution_time)
        if len(stats.recent_times) > 100:
            stats.recent_times = stats.recent_times[-100:]
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"error": "No metrics available in the specified time window"}
        
        # Overall stats
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.success)
        failed_requests = total_requests - successful_requests
        
        execution_times = [m.execution_time for m in recent_metrics]
        avg_response_time = statistics.mean(execution_times)
        median_response_time = statistics.median(execution_times)
        p95_response_time = statistics.quantiles(sorted(execution_times), n=20)[18] if len(execution_times) > 5 else max(execution_times)
        
        # Performance level distribution
        performance_levels = {}
        for level in PerformanceLevel:
            performance_levels[level.value] = sum(1 for m in recent_metrics if m.performance_level == level)
        
        # Slow queries
        slow_queries = [m for m in recent_metrics if m.execution_time > self.slow_query_threshold]
        critical_queries = [m for m in recent_metrics if m.execution_time > self.critical_query_threshold]
        
        # Top slow endpoints
        endpoint_response_times = {}
        for metric in recent_metrics:
            if metric.endpoint not in endpoint_response_times:
                endpoint_response_times[metric.endpoint] = []
            endpoint_response_times[metric.endpoint].append(metric.execution_time)
        
        slow_endpoints = []
        for endpoint, times in endpoint_response_times.items():
            avg_time = statistics.mean(times)
            if avg_time > self.slow_query_threshold:
                slow_endpoints.append({
                    "endpoint": endpoint,
                    "avg_response_time": avg_time,
                    "request_count": len(times),
                    "max_response_time": max(times)
                })
        
        slow_endpoints.sort(key=lambda x: x["avg_response_time"], reverse=True)
        
        # Error analysis
        error_analysis = {}
        for metric in recent_metrics:
            if not metric.success and metric.error_message:
                error_key = metric.error_message[:50]
                if error_key not in error_analysis:
                    error_analysis[error_key] = {
                        "count": 0,
                        "endpoints": set(),
                        "first_occurrence": metric.timestamp,
                        "last_occurrence": metric.timestamp
                    }
                error_analysis[error_key]["count"] += 1
                error_analysis[error_key]["endpoints"].add(metric.endpoint)
                error_analysis[error_key]["last_occurrence"] = max(
                    error_analysis[error_key]["last_occurrence"], 
                    metric.timestamp
                )
        
        # Convert sets to lists for JSON serialization
        for error_info in error_analysis.values():
            error_info["endpoints"] = list(error_info["endpoints"])
            error_info["first_occurrence"] = error_info["first_occurrence"].isoformat()
            error_info["last_occurrence"] = error_info["last_occurrence"].isoformat()
        
        return {
            "time_window_minutes": time_window_minutes,
            "overview": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (successful_requests / total_requests) * 100,
                "avg_response_time": avg_response_time,
                "median_response_time": median_response_time,
                "p95_response_time": p95_response_time,
            },
            "performance_distribution": performance_levels,
            "slow_queries": {
                "count": len(slow_queries),
                "critical_count": len(critical_queries),
                "threshold": self.slow_query_threshold,
                "examples": [
                    {
                        "endpoint": q.endpoint,
                        "execution_time": q.execution_time,
                        "timestamp": q.timestamp.isoformat(),
                        "query_id": q.query_id,
                        "error": q.error_message
                    }
                    for q in sorted(slow_queries, key=lambda x: x.execution_time, reverse=True)[:10]
                ]
            },
            "slow_endpoints": slow_endpoints[:10],
            "error_analysis": error_analysis,
            "active_requests": len(self.active_requests),
            "system_resources": self._get_system_stats() if self.enable_system_monitoring else None
        }
    
    def get_endpoint_details(self, endpoint: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific endpoint"""
        if endpoint not in self.endpoint_stats:
            return {"error": f"No statistics available for endpoint: {endpoint}"}
        
        stats = self.endpoint_stats[endpoint]
        
        # Get recent metrics for this endpoint
        recent_metrics = [
            m for m in self.metrics_history[-1000:] 
            if m.endpoint == endpoint
        ]
        
        # Response time distribution
        response_times = [m.execution_time for m in recent_metrics]
        
        distribution = {}
        for level in PerformanceLevel:
            distribution[level.value] = sum(
                1 for m in recent_metrics if m.performance_level == level
            )
        
        return {
            "endpoint": endpoint,
            "statistics": {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": stats.success_rate,
                "avg_response_time": stats.avg_response_time,
                "min_response_time": stats.min_time,
                "max_response_time": stats.max_time,
                "p95_response_time": stats.p95_response_time,
                "current_performance_level": stats.current_performance_level.value,
                "last_updated": stats.last_updated.isoformat()
            },
            "performance_distribution": distribution,
            "recent_errors": dict(list(stats.error_rates.items())[:10]),
            "recent_metrics": [
                {
                    "query_id": m.query_id,
                    "execution_time": m.execution_time,
                    "timestamp": m.timestamp.isoformat(),
                    "success": m.success,
                    "performance_level": m.performance_level.value,
                    "error": m.error_message
                }
                for m in recent_metrics[-20:]
            ]
        }
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                "memory": {
                    "total": memory.total / 1024 / 1024 / 1024,  # GB
                    "available": memory.available / 1024 / 1024 / 1024,  # GB
                    "percent": memory.percent,
                    "used": memory.used / 1024 / 1024 / 1024  # GB
                },
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "physical_count": psutil.cpu_count(logical=False)
                },
                "disk": {
                    "total": disk.total / 1024 / 1024 / 1024,  # GB
                    "used": disk.used / 1024 / 1024 / 1024,  # GB
                    "free": disk.free / 1024 / 1024 / 1024,  # GB
                    "percent": (disk.used / disk.total) * 100
                },
                "process": {
                    "pid": os.getpid(),
                    "memory_rss": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                    "memory_percent": psutil.Process().memory_percent(),
                    "cpu_percent": psutil.Process().cpu_percent()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        alerts = []
        
        for endpoint, stats in self.endpoint_stats.items():
            # Check average response time
            if stats.avg_response_time > self.alert_thresholds["avg_response_time"]:
                alerts.append({
                    "type": "high_response_time",
                    "severity": "warning" if stats.avg_response_time < 2.0 else "error",
                    "endpoint": endpoint,
                    "message": f"High average response time: {stats.avg_response_time:.3f}s",
                    "current_value": stats.avg_response_time,
                    "threshold": self.alert_thresholds["avg_response_time"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check error rate
            error_rate = 100 - stats.success_rate
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "error",
                    "endpoint": endpoint,
                    "message": f"High error rate: {error_rate:.1f}%",
                    "current_value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check P95 response time
            if stats.p95_response_time > self.alert_thresholds["p95_response_time"]:
                alerts.append({
                    "type": "high_p95_response_time",
                    "severity": "warning",
                    "endpoint": endpoint,
                    "message": f"High P95 response time: {stats.p95_response_time:.3f}s",
                    "current_value": stats.p95_response_time,
                    "threshold": self.alert_thresholds["p95_response_time"],
                    "timestamp": datetime.now().isoformat()
                })
        
        return sorted(alerts, key=lambda x: x["current_value"], reverse=True)
    
    def reset_stats(self):
        """Reset all performance statistics"""
        self.metrics_history.clear()
        self.endpoint_stats.clear()
        self.active_requests.clear()
        logger.info("🔄 Performance statistics reset")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        recent_metrics = self.metrics_history[-100:] if self.metrics_history else []
        
        if not recent_metrics:
            return {
                "status": "unknown",
                "message": "No recent metrics available"
            }
        
        # Calculate health scores
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        avg_response_time = statistics.mean([m.execution_time for m in recent_metrics])
        
        # Determine overall health
        if success_rate > 95 and avg_response_time < 1.0:
            status = "excellent"
            color = "green"
        elif success_rate > 90 and avg_response_time < 2.0:
            status = "good"
            color = "green"
        elif success_rate > 80 and avg_response_time < 5.0:
            status = "acceptable"
            color = "yellow"
        else:
            status = "critical"
            color = "red"
        
        return {
            "status": status,
            "color": color,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "active_requests": len(self.active_requests),
            "total_endpoints": len(self.endpoint_stats),
            "alerts_count": len(self.get_performance_alerts()),
            "system_resources": self._get_system_stats() if self.enable_system_monitoring else None,
            "timestamp": datetime.now().isoformat()
        }


# Global profiler instance
performance_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance"""
    return performance_profiler
