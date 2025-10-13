"""
ULTIMATE CIRCUIT BREAKER SYSTEM FOR EXTERNAL SIEM APIs
Advanced circuit breaker with intelligent recovery, health monitoring, and performance optimization
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import random

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing recovery


class FailureType(Enum):
    """Types of failures to track"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    AUTHENTICATION_ERROR = "auth_error"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class FailureRecord:
    """Record of a failure"""
    timestamp: float
    failure_type: FailureType
    error_message: str
    response_time: Optional[float] = None
    http_status: Optional[int] = None
    
    @property
    def age_seconds(self) -> float:
        """Get age of this failure in seconds"""
        return time.time() - self.timestamp


@dataclass
class HealthMetrics:
    """Health metrics for a service"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    failure_history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        return 100.0 - self.success_rate
    
    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if len(self.response_times) < 5:
            return self.avg_response_time
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    @property
    def recent_failure_rate(self) -> float:
        """Calculate failure rate for recent requests (last 50)"""
        recent_failures = len([f for f in self.failure_history if f.age_seconds < 300])  # 5 minutes
        recent_total = min(50, self.total_requests)
        if recent_total == 0:
            return 0.0
        return (recent_failures / recent_total) * 100


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    name: str
    failure_threshold: int = 5           # Failures before opening
    success_threshold: int = 3           # Successes to close from half-open
    timeout_seconds: float = 60.0        # Time to stay open
    max_timeout_seconds: float = 300.0   # Maximum backoff time
    failure_rate_threshold: float = 50.0 # Failure rate % to trigger opening
    slow_call_threshold: float = 10.0    # Slow call threshold in seconds
    slow_call_rate_threshold: float = 50.0 # Slow call rate % to trigger
    minimum_throughput: int = 10         # Minimum requests before evaluation
    sliding_window_size: int = 100       # Size of sliding window for metrics
    
    # Advanced settings
    exponential_backoff: bool = True     # Use exponential backoff
    jitter: bool = True                  # Add jitter to backoff
    health_check_interval: float = 30.0  # Health check frequency
    recovery_factor: float = 0.1         # Gradual recovery factor


class AdvancedCircuitBreaker:
    """🛡️ ULTIMATE CIRCUIT BREAKER FOR EXTERNAL APIS"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = HealthMetrics()
        
        # State management
        self.state_changed_time = time.time()
        self.next_attempt_time = 0.0
        self.backoff_multiplier = 1.0
        
        # Advanced features
        self.recovery_mode = False
        self.gradual_recovery_rate = 1.0  # Start with normal rate
        self.health_check_task: Optional[asyncio.Task] = None
        self.state_history: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_failure: Optional[Callable] = None
        self.on_success: Optional[Callable] = None
        
        logger.info(f"🛡️ Advanced Circuit Breaker initialized: {self.config.name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker protection"""
        # Check if circuit is open
        if not await self._should_allow_request():
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN for {self.config.name}. "
                f"Next attempt in {self._time_until_next_attempt():.1f} seconds"
            )
        
        # Execute the protected function
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            
            # Record successful execution
            execution_time = time.time() - start_time
            await self._record_success(execution_time)
            
            return result
            
        except Exception as e:
            # Record failure
            execution_time = time.time() - start_time
            await self._record_failure(e, execution_time)
            raise
    
    async def _should_allow_request(self) -> bool:
        """Determine if request should be allowed"""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            if current_time >= self.next_attempt_time:
                await self._transition_to_half_open()
                return True
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            # In gradual recovery mode, allow only a percentage of requests
            if self.recovery_mode:
                return random.random() < self.gradual_recovery_rate
            return True
        
        return False
    
    async def _record_success(self, response_time: float):
        """Record successful request"""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.metrics.consecutive_successes += 1
        self.metrics.consecutive_failures = 0
        self.metrics.last_success_time = time.time()
        
        # Update response time metrics
        self.metrics.response_times.append(response_time)
        self._update_avg_response_time(response_time)
        
        # Check for slow calls
        is_slow_call = response_time > self.config.slow_call_threshold
        if is_slow_call:
            logger.warning(f"🐌 Slow call detected for {self.config.name}: {response_time:.2f}s")
        
        # Handle state transitions
        if self.state == CircuitState.HALF_OPEN:
            if self.metrics.consecutive_successes >= self.config.success_threshold:
                await self._transition_to_closed()
            elif self.recovery_mode:
                # Gradually increase recovery rate
                self.gradual_recovery_rate = min(1.0, self.gradual_recovery_rate * 1.1)
        
        # Callback
        if self.on_success:
            await self._safe_callback(self.on_success, response_time, is_slow_call)
        
        logger.debug(f"✅ Success recorded for {self.config.name} ({response_time:.3f}s)")
    
    async def _record_failure(self, exception: Exception, response_time: Optional[float] = None):
        """Record failed request"""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.consecutive_failures += 1
        self.metrics.consecutive_successes = 0
        self.metrics.last_failure_time = time.time()
        
        # Classify failure type
        failure_type = self._classify_failure(exception)
        
        # Record failure
        failure_record = FailureRecord(
            timestamp=time.time(),
            failure_type=failure_type,
            error_message=str(exception),
            response_time=response_time,
            http_status=getattr(exception, 'status_code', None)
        )
        self.metrics.failure_history.append(failure_record)
        
        # Check if circuit should open
        await self._evaluate_circuit_state()
        
        # Reset recovery rate on failure during recovery
        if self.state == CircuitState.HALF_OPEN and self.recovery_mode:
            self.gradual_recovery_rate *= 0.5  # Reduce recovery rate
        
        # Callback
        if self.on_failure:
            await self._safe_callback(self.on_failure, failure_record)
        
        logger.warning(f"❌ Failure recorded for {self.config.name}: {failure_type.value} - {exception}")
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """Classify the type of failure"""
        exception_str = str(exception).lower()
        exception_type = type(exception).__name__.lower()
        
        if 'timeout' in exception_str or 'timeout' in exception_type:
            return FailureType.TIMEOUT
        elif 'connection' in exception_str or 'connection' in exception_type:
            return FailureType.CONNECTION_ERROR
        elif 'auth' in exception_str or 'unauthorized' in exception_str:
            return FailureType.AUTHENTICATION_ERROR
        elif 'rate limit' in exception_str or 'too many requests' in exception_str:
            return FailureType.RATE_LIMIT
        elif 'service unavailable' in exception_str or '503' in exception_str:
            return FailureType.SERVICE_UNAVAILABLE
        elif hasattr(exception, 'status_code') and 400 <= getattr(exception, 'status_code') < 600:
            return FailureType.HTTP_ERROR
        else:
            return FailureType.UNKNOWN_ERROR
    
    async def _evaluate_circuit_state(self):
        """Evaluate if circuit should change state"""
        if self.state == CircuitState.OPEN:
            return  # Already open
        
        # Check if minimum throughput is met
        if self.metrics.total_requests < self.config.minimum_throughput:
            return
        
        should_open = False
        reason = ""
        
        # Check consecutive failures
        if self.metrics.consecutive_failures >= self.config.failure_threshold:
            should_open = True
            reason = f"consecutive failures ({self.metrics.consecutive_failures})"
        
        # Check failure rate
        elif self.metrics.failure_rate >= self.config.failure_rate_threshold:
            should_open = True
            reason = f"high failure rate ({self.metrics.failure_rate:.1f}%)"
        
        # Check slow call rate
        slow_calls = len([
            rt for rt in self.metrics.response_times 
            if rt > self.config.slow_call_threshold
        ])
        slow_call_rate = (slow_calls / len(self.metrics.response_times)) * 100 if self.metrics.response_times else 0
        
        if slow_call_rate >= self.config.slow_call_rate_threshold:
            should_open = True
            reason = f"high slow call rate ({slow_call_rate:.1f}%)"
        
        if should_open:
            await self._transition_to_open(reason)
    
    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        if self.state == CircuitState.CLOSED:
            return
        
        logger.info(f"✅ Circuit breaker CLOSED for {self.config.name}")
        
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_changed_time = time.time()
        self.backoff_multiplier = 1.0
        self.recovery_mode = False
        self.gradual_recovery_rate = 1.0
        
        await self._record_state_change(old_state, CircuitState.CLOSED, "Recovery completed")
    
    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        if self.state == CircuitState.HALF_OPEN:
            return
        
        logger.info(f"🔄 Circuit breaker HALF_OPEN for {self.config.name}")
        
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_changed_time = time.time()
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
        
        # Enable gradual recovery mode for high-traffic scenarios
        if self.metrics.total_requests > 1000:
            self.recovery_mode = True
            self.gradual_recovery_rate = self.config.recovery_factor
        
        await self._record_state_change(old_state, CircuitState.HALF_OPEN, "Testing recovery")
    
    async def _transition_to_open(self, reason: str):
        """Transition circuit to OPEN state"""
        if self.state == CircuitState.OPEN:
            return
        
        logger.warning(f"🚨 Circuit breaker OPEN for {self.config.name}: {reason}")
        
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_changed_time = time.time()
        
        # Calculate next attempt time with exponential backoff
        if self.config.exponential_backoff:
            backoff_time = min(
                self.config.timeout_seconds * self.backoff_multiplier,
                self.config.max_timeout_seconds
            )
            
            # Add jitter to prevent thundering herd
            if self.config.jitter:
                jitter_factor = random.uniform(0.8, 1.2)
                backoff_time *= jitter_factor
            
            self.backoff_multiplier *= 2.0  # Exponential backoff
        else:
            backoff_time = self.config.timeout_seconds
        
        self.next_attempt_time = time.time() + backoff_time
        
        # Start health check task
        if self.health_check_task:
            self.health_check_task.cancel()
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        await self._record_state_change(old_state, CircuitState.OPEN, reason)
    
    async def _record_state_change(self, from_state: CircuitState, to_state: CircuitState, reason: str):
        """Record state change for analytics"""
        state_record = {
            "timestamp": time.time(),
            "from_state": from_state.value,
            "to_state": to_state.value,
            "reason": reason,
            "metrics_snapshot": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.success_rate,
                "failure_rate": self.metrics.failure_rate,
                "avg_response_time": self.metrics.avg_response_time,
                "consecutive_failures": self.metrics.consecutive_failures
            }
        }
        
        self.state_history.append(state_record)
        
        # Limit history size
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
        
        # Callback
        if self.on_state_change:
            await self._safe_callback(self.on_state_change, from_state, to_state, reason)
    
    async def _health_check_loop(self):
        """Background health check during OPEN state"""
        try:
            while self.state == CircuitState.OPEN:
                await asyncio.sleep(self.config.health_check_interval)
                
                if self.state != CircuitState.OPEN:
                    break
                
                # Check if it's time to attempt recovery
                if time.time() >= self.next_attempt_time:
                    logger.debug(f"🔍 Health check ready for {self.config.name}")
                    break
                    
        except asyncio.CancelledError:
            logger.debug(f"🛑 Health check cancelled for {self.config.name}")
    
    def _time_until_next_attempt(self) -> float:
        """Calculate time until next attempt is allowed"""
        if self.state != CircuitState.OPEN:
            return 0.0
        return max(0.0, self.next_attempt_time - time.time())
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time with exponential moving average"""
        if self.metrics.avg_response_time == 0:
            self.metrics.avg_response_time = response_time
        else:
            # Exponential moving average (alpha = 0.1)
            self.metrics.avg_response_time = (
                0.9 * self.metrics.avg_response_time + 0.1 * response_time
            )
    
    async def _safe_callback(self, callback: Callable, *args, **kwargs):
        """Execute callback safely without affecting circuit breaker"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Callback error for {self.config.name}: {e}")
    
    # Public API Methods
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state and metrics"""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "state_duration": time.time() - self.state_changed_time,
            "next_attempt_in": self._time_until_next_attempt(),
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
                "failure_rate": self.metrics.failure_rate,
                "avg_response_time": self.metrics.avg_response_time,
                "p95_response_time": self.metrics.p95_response_time,
                "consecutive_failures": self.metrics.consecutive_failures,
                "consecutive_successes": self.metrics.consecutive_successes,
                "last_success_time": self.metrics.last_success_time,
                "last_failure_time": self.metrics.last_failure_time,
                "recent_failure_rate": self.metrics.recent_failure_rate
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
                "failure_rate_threshold": self.config.failure_rate_threshold
            },
            "recovery": {
                "recovery_mode": self.recovery_mode,
                "gradual_recovery_rate": self.gradual_recovery_rate,
                "backoff_multiplier": self.backoff_multiplier
            }
        }
    
    def get_failure_analysis(self) -> Dict[str, Any]:
        """Get detailed failure analysis"""
        failure_types = defaultdict(int)
        recent_failures = []
        
        for failure in self.metrics.failure_history:
            failure_types[failure.failure_type.value] += 1
            
            if failure.age_seconds < 600:  # Last 10 minutes
                recent_failures.append({
                    "timestamp": failure.timestamp,
                    "type": failure.failure_type.value,
                    "message": failure.error_message[:100],  # Truncate
                    "age_seconds": failure.age_seconds,
                    "response_time": failure.response_time,
                    "http_status": failure.http_status
                })
        
        return {
            "failure_types": dict(failure_types),
            "total_failures": len(self.metrics.failure_history),
            "recent_failures": recent_failures[-10:],  # Last 10 failures
            "most_common_failure": max(failure_types.items(), key=lambda x: x[1])[0] if failure_types else None
        }
    
    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get performance analysis"""
        if not self.metrics.response_times:
            return {"message": "No performance data available"}
        
        response_times = list(self.metrics.response_times)
        
        return {
            "response_time_stats": {
                "min": min(response_times),
                "max": max(response_times),
                "avg": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": self.metrics.p95_response_time,
                "p99": sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) > 10 else max(response_times)
            },
            "slow_calls": {
                "threshold": self.config.slow_call_threshold,
                "count": len([rt for rt in response_times if rt > self.config.slow_call_threshold]),
                "rate": (len([rt for rt in response_times if rt > self.config.slow_call_threshold]) / len(response_times)) * 100
            },
            "trend": self._calculate_performance_trend()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend"""
        if len(self.metrics.response_times) < 10:
            return "insufficient_data"
        
        recent_times = list(self.metrics.response_times)[-10:]
        older_times = list(self.metrics.response_times)[:-10][-10:] if len(self.metrics.response_times) > 10 else []
        
        if not older_times:
            return "insufficient_data"
        
        recent_avg = statistics.mean(recent_times)
        older_avg = statistics.mean(older_times)
        
        if recent_avg < older_avg * 0.9:
            return "improving"
        elif recent_avg > older_avg * 1.1:
            return "degrading"
        else:
            return "stable"
    
    async def reset(self):
        """Reset circuit breaker to initial state"""
        logger.info(f"🔄 Resetting circuit breaker: {self.config.name}")
        
        if self.health_check_task:
            self.health_check_task.cancel()
        
        self.state = CircuitState.CLOSED
        self.state_changed_time = time.time()
        self.next_attempt_time = 0.0
        self.backoff_multiplier = 1.0
        self.recovery_mode = False
        self.gradual_recovery_rate = 1.0
        
        # Don't reset metrics - keep for analysis
        # self.metrics = HealthMetrics()
        
        await self._record_state_change(CircuitState.OPEN, CircuitState.CLOSED, "Manual reset")
    
    async def force_open(self, reason: str = "Manual override"):
        """Force circuit breaker to OPEN state"""
        logger.warning(f"🚨 Force opening circuit breaker: {self.config.name} - {reason}")
        await self._transition_to_open(reason)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerManager:
    """🏭 CIRCUIT BREAKER FACTORY AND MANAGER"""
    
    def __init__(self):
        self.breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self.global_stats = {
            "total_breakers": 0,
            "open_breakers": 0,
            "half_open_breakers": 0,
            "closed_breakers": 0
        }
        
        logger.info("🏭 Circuit Breaker Manager initialized")
    
    def create_breaker(self, 
                      name: str, 
                      config: Optional[CircuitBreakerConfig] = None) -> AdvancedCircuitBreaker:
        """Create a new circuit breaker"""
        if name in self.breakers:
            logger.warning(f"⚠️ Circuit breaker already exists: {name}")
            return self.breakers[name]
        
        if config is None:
            config = CircuitBreakerConfig(name=name)
        
        breaker = AdvancedCircuitBreaker(config)
        
        # Set up callbacks for global tracking
        breaker.on_state_change = self._on_state_change
        
        self.breakers[name] = breaker
        self.global_stats["total_breakers"] += 1
        self.global_stats["closed_breakers"] += 1
        
        logger.info(f"✅ Circuit breaker created: {name}")
        return breaker
    
    def get_breaker(self, name: str) -> Optional[AdvancedCircuitBreaker]:
        """Get existing circuit breaker"""
        return self.breakers.get(name)
    
    async def _on_state_change(self, 
                              from_state: CircuitState, 
                              to_state: CircuitState, 
                              reason: str):
        """Handle state changes for global tracking"""
        # Update global stats
        if from_state != to_state:
            # Decrease old state count
            if from_state == CircuitState.OPEN:
                self.global_stats["open_breakers"] -= 1
            elif from_state == CircuitState.HALF_OPEN:
                self.global_stats["half_open_breakers"] -= 1
            elif from_state == CircuitState.CLOSED:
                self.global_stats["closed_breakers"] -= 1
            
            # Increase new state count
            if to_state == CircuitState.OPEN:
                self.global_stats["open_breakers"] += 1
            elif to_state == CircuitState.HALF_OPEN:
                self.global_stats["half_open_breakers"] += 1
            elif to_state == CircuitState.CLOSED:
                self.global_stats["closed_breakers"] += 1
    
    def get_global_status(self) -> Dict[str, Any]:
        """Get global circuit breaker status"""
        breaker_states = {}
        for name, breaker in self.breakers.items():
            breaker_states[name] = breaker.get_state()
        
        return {
            "global_stats": self.global_stats.copy(),
            "breakers": breaker_states,
            "health_summary": {
                "healthy_percentage": (self.global_stats["closed_breakers"] / 
                                     max(1, self.global_stats["total_breakers"])) * 100,
                "degraded_count": self.global_stats["half_open_breakers"],
                "failed_count": self.global_stats["open_breakers"]
            }
        }
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        logger.info("🔄 Resetting all circuit breakers")
        
        for breaker in self.breakers.values():
            await breaker.reset()
    
    async def cleanup_all(self):
        """Cleanup all circuit breakers"""
        logger.info("🧹 Cleaning up all circuit breakers")
        
        for breaker in self.breakers.values():
            await breaker.cleanup()
        
        self.breakers.clear()
        self.global_stats = {
            "total_breakers": 0,
            "open_breakers": 0,
            "half_open_breakers": 0,
            "closed_breakers": 0
        }


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get the global circuit breaker manager"""
    return circuit_breaker_manager


# Convenience functions for common SIEM service configurations
def create_elasticsearch_breaker() -> AdvancedCircuitBreaker:
    """Create circuit breaker optimized for Elasticsearch"""
    config = CircuitBreakerConfig(
        name="elasticsearch",
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=30.0,
        failure_rate_threshold=30.0,
        slow_call_threshold=5.0,
        minimum_throughput=5
    )
    return circuit_breaker_manager.create_breaker("elasticsearch", config)


def create_wazuh_breaker() -> AdvancedCircuitBreaker:
    """Create circuit breaker optimized for Wazuh"""
    config = CircuitBreakerConfig(
        name="wazuh",
        failure_threshold=5,
        success_threshold=3,
        timeout_seconds=60.0,
        failure_rate_threshold=40.0,
        slow_call_threshold=10.0,
        minimum_throughput=5
    )
    return circuit_breaker_manager.create_breaker("wazuh", config)


def create_splunk_breaker() -> AdvancedCircuitBreaker:
    """Create circuit breaker optimized for Splunk"""
    config = CircuitBreakerConfig(
        name="splunk",
        failure_threshold=4,
        success_threshold=3,
        timeout_seconds=45.0,
        failure_rate_threshold=35.0,
        slow_call_threshold=8.0,
        minimum_throughput=5
    )
    return circuit_breaker_manager.create_breaker("splunk", config)
