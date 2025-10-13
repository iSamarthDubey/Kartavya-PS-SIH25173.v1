"""
🔥 ADVANCED INTELLIGENT CACHE WARMING SYSTEM
Smart cache preloading based on query patterns, user behavior, and predictive analytics
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import hashlib
import random

from .redis_manager import RedisManager, redis_manager
from ..monitoring.performance_profiler import performance_profiler, QueryType

logger = logging.getLogger(__name__)


class WarmingPriority(Enum):
    """Cache warming priority levels"""
    CRITICAL = 1    # Most frequently accessed queries
    HIGH = 2        # Recent popular queries
    MEDIUM = 3      # Scheduled/time-based patterns
    LOW = 4         # Predictive/exploratory queries


class QueryPattern(Enum):
    """Types of query patterns detected"""
    FREQUENT = "frequent"           # High frequency queries
    TRENDING = "trending"           # Recently popular queries  
    SCHEDULED = "scheduled"         # Time-based regular queries
    SEASONAL = "seasonal"           # Date/time pattern queries
    USER_SPECIFIC = "user_specific" # User behavior patterns
    DASHBOARD = "dashboard"         # Dashboard/widget queries
    SEARCH_SEQUENCE = "search_sequence"  # Query sequences/drill-downs


@dataclass
class QueryAnalytics:
    """Analytics for a specific query"""
    query_hash: str
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: float = 0
    first_accessed: float = 0
    avg_response_time: float = 0.0
    users: Set[str] = field(default_factory=set)
    time_patterns: List[int] = field(default_factory=list)  # Hours of access
    success_rate: float = 100.0
    data_size_bytes: int = 0
    cache_value_score: float = 0.0
    
    @property
    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per day)"""
        if self.access_count == 0:
            return 0.0
        age_days = max(1, (time.time() - self.first_accessed) / 86400)
        return self.access_count / age_days
    
    @property
    def popularity_score(self) -> float:
        """Calculate popularity score (0-100)"""
        base_score = min(100, self.access_frequency * 10)
        user_diversity = len(self.users) * 5  # Bonus for multiple users
        recency = max(0, 50 - (time.time() - self.last_accessed) / 3600)  # Decay over hours
        return min(100, base_score + user_diversity + recency)


@dataclass
class WarmingTask:
    """Cache warming task"""
    query_hash: str
    query: str
    filters: Dict[str, Any]
    priority: WarmingPriority
    scheduled_time: float
    attempts: int = 0
    max_attempts: int = 3
    estimated_duration: float = 0.0
    
    @property
    def should_execute(self) -> bool:
        """Check if task should be executed now"""
        return (time.time() >= self.scheduled_time and 
                self.attempts < self.max_attempts)


class IntelligentCacheWarmer:
    """🧠 INTELLIGENT CACHE WARMING ENGINE"""
    
    def __init__(self, redis_manager: RedisManager = None):
        self.redis_manager = redis_manager or redis_manager
        self.query_analytics: Dict[str, QueryAnalytics] = {}
        self.warming_tasks: List[WarmingTask] = []
        self.warming_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.enabled = True
        self.max_concurrent_warming = 5
        self.warming_interval = 300  # 5 minutes
        self.max_warming_tasks = 100
        self.learning_window_days = 7
        self.min_access_count = 3  # Minimum accesses to consider for warming
        
        # Pattern detection
        self.query_sequences: Dict[str, List[str]] = defaultdict(list)
        self.user_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.time_patterns: Dict[int, Counter] = defaultdict(Counter)  # hour -> query_hash counter
        
        # Performance tracking
        self.warming_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "bytes_warmed": 0,
            "time_saved": 0.0,
            "cache_hits_generated": 0
        }
        
        # Active warming
        self.active_warming_tasks: Set[str] = set()
        self.warming_semaphore = asyncio.Semaphore(self.max_concurrent_warming)
        
        logger.info("🧠 Intelligent Cache Warmer initialized")
    
    async def start(self):
        """Start the cache warming engine"""
        if not self.enabled:
            logger.info("📊 Cache warming disabled")
            return
        
        logger.info("🔥 Starting intelligent cache warming engine...")
        
        # Start background tasks
        asyncio.create_task(self._learning_loop())
        asyncio.create_task(self._warming_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Cache warming engine started")
    
    async def record_query_access(self, 
                                 query: str, 
                                 filters: Dict[str, Any] = None,
                                 user_id: str = None,
                                 response_time: float = 0.0,
                                 success: bool = True,
                                 data_size: int = 0):
        """Record query access for learning patterns"""
        query_hash = self._generate_query_hash(query, filters)
        current_time = time.time()
        current_hour = datetime.now().hour
        
        # Update or create analytics
        if query_hash not in self.query_analytics:
            self.query_analytics[query_hash] = QueryAnalytics(
                query_hash=query_hash,
                query=query,
                filters=filters or {},
                first_accessed=current_time
            )
        
        analytics = self.query_analytics[query_hash]
        analytics.access_count += 1
        analytics.last_accessed = current_time
        analytics.data_size_bytes = max(analytics.data_size_bytes, data_size)
        
        # Update response time (moving average)
        if response_time > 0:
            if analytics.avg_response_time == 0:
                analytics.avg_response_time = response_time
            else:
                # Exponential moving average
                analytics.avg_response_time = 0.8 * analytics.avg_response_time + 0.2 * response_time
        
        # Track user access
        if user_id:
            analytics.users.add(user_id)
            self._update_user_patterns(user_id, query_hash, current_time)
        
        # Track time patterns
        analytics.time_patterns.append(current_hour)
        if len(analytics.time_patterns) > 50:  # Keep last 50 accesses
            analytics.time_patterns = analytics.time_patterns[-50:]
        
        self.time_patterns[current_hour][query_hash] += 1
        
        # Update success rate
        total_attempts = analytics.access_count
        if success:
            analytics.success_rate = ((analytics.success_rate * (total_attempts - 1)) + 100) / total_attempts
        else:
            analytics.success_rate = (analytics.success_rate * (total_attempts - 1)) / total_attempts
        
        # Calculate cache value score
        analytics.cache_value_score = self._calculate_cache_value(analytics)
        
        logger.debug(f"📊 Query analytics updated: {query_hash[:8]} (score: {analytics.cache_value_score:.2f})")
    
    def _generate_query_hash(self, query: str, filters: Dict[str, Any] = None) -> str:
        """Generate consistent hash for query + filters"""
        query_data = {
            "query": query.lower().strip(),
            "filters": filters or {}
        }
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.sha256(query_str.encode()).hexdigest()[:16]
    
    def _calculate_cache_value(self, analytics: QueryAnalytics) -> float:
        """Calculate cache value score for prioritization"""
        # Base score from popularity
        base_score = analytics.popularity_score
        
        # Response time factor (slower queries benefit more from caching)
        time_factor = min(50, analytics.avg_response_time * 10)
        
        # Data size factor (larger responses benefit more)
        size_factor = min(30, analytics.data_size_bytes / 1000)  # Per KB
        
        # User diversity bonus
        user_bonus = min(20, len(analytics.users) * 2)
        
        # Success rate penalty for unreliable queries
        success_penalty = (100 - analytics.success_rate) * 0.5
        
        total_score = base_score + time_factor + size_factor + user_bonus - success_penalty
        return max(0, min(100, total_score))
    
    def _update_user_patterns(self, user_id: str, query_hash: str, timestamp: float):
        """Update user behavior patterns"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                "queries": [],
                "sessions": [],
                "preferences": Counter()
            }
        
        user_data = self.user_patterns[user_id]
        
        # Track query sequence
        user_data["queries"].append((query_hash, timestamp))
        if len(user_data["queries"]) > 20:  # Keep last 20 queries
            user_data["queries"] = user_data["queries"][-20:]
        
        # Update preferences
        user_data["preferences"][query_hash] += 1
        
        # Detect query sequences
        if len(user_data["queries"]) >= 2:
            recent_queries = [q[0] for q in user_data["queries"][-5:]]  # Last 5 queries
            sequence_key = " -> ".join(recent_queries)
            self.query_sequences[user_id].append(sequence_key)
    
    async def _learning_loop(self):
        """Background learning and pattern detection"""
        while True:
            try:
                await asyncio.sleep(self.warming_interval)
                await self._analyze_patterns()
                await self._generate_warming_tasks()
            except Exception as e:
                logger.error(f"❌ Learning loop error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_patterns(self):
        """Analyze access patterns and detect trends"""
        current_time = time.time()
        cutoff_time = current_time - (self.learning_window_days * 86400)
        
        # Clean old analytics
        expired_hashes = [
            h for h, a in self.query_analytics.items()
            if a.last_accessed < cutoff_time
        ]
        for h in expired_hashes:
            del self.query_analytics[h]
        
        logger.debug(f"🔍 Analyzed {len(self.query_analytics)} active query patterns")
        
        # Detect trending queries (recently popular)
        recent_analytics = [
            a for a in self.query_analytics.values()
            if a.last_accessed > current_time - 3600  # Last hour
        ]
        trending = sorted(recent_analytics, key=lambda a: a.popularity_score, reverse=True)[:10]
        
        logger.debug(f"📈 Detected {len(trending)} trending queries")
        
        # Detect time-based patterns
        current_hour = datetime.now().hour
        popular_now = self.time_patterns.get(current_hour, Counter()).most_common(5)
        
        logger.debug(f"⏰ Popular queries for hour {current_hour}: {len(popular_now)}")
    
    async def _generate_warming_tasks(self):
        """Generate intelligent warming tasks based on patterns"""
        current_time = time.time()
        
        # Clear old tasks
        self.warming_tasks = [
            task for task in self.warming_tasks
            if task.scheduled_time > current_time - 3600  # Keep tasks from last hour
        ]
        
        # Generate new tasks based on different strategies
        await self._generate_frequency_based_tasks()
        await self._generate_time_based_tasks()
        await self._generate_predictive_tasks()
        
        # Limit total tasks
        if len(self.warming_tasks) > self.max_warming_tasks:
            # Keep highest priority tasks
            self.warming_tasks.sort(key=lambda t: t.priority.value)
            self.warming_tasks = self.warming_tasks[:self.max_warming_tasks]
        
        logger.debug(f"🎯 Generated {len(self.warming_tasks)} warming tasks")
    
    async def _generate_frequency_based_tasks(self):
        """Generate tasks for frequently accessed queries"""
        # High-value queries that aren't currently cached
        high_value_queries = [
            analytics for analytics in self.query_analytics.values()
            if (analytics.cache_value_score > 60 and
                analytics.access_count >= self.min_access_count)
        ]
        
        for analytics in sorted(high_value_queries, key=lambda a: a.cache_value_score, reverse=True)[:10]:
            # Check if already cached
            cache_key = f"kartavya:query:{analytics.query_hash}"
            if not await self.redis_manager.get(cache_key):
                task = WarmingTask(
                    query_hash=analytics.query_hash,
                    query=analytics.query,
                    filters=analytics.filters,
                    priority=WarmingPriority.CRITICAL,
                    scheduled_time=time.time() + random.randint(10, 120),  # Random delay
                    estimated_duration=analytics.avg_response_time
                )
                self.warming_tasks.append(task)
    
    async def _generate_time_based_tasks(self):
        """Generate tasks based on time patterns"""
        current_hour = datetime.now().hour
        next_hour = (current_hour + 1) % 24
        
        # Warm queries popular in the next hour
        popular_next_hour = self.time_patterns.get(next_hour, Counter()).most_common(5)
        
        for query_hash, count in popular_next_hour:
            if query_hash in self.query_analytics and count >= 2:  # At least 2 accesses
                analytics = self.query_analytics[query_hash]
                
                # Schedule for 10-15 minutes before the hour
                minutes_until_next_hour = (60 - datetime.now().minute) % 60
                schedule_time = time.time() + max(600, (minutes_until_next_hour - 15) * 60)
                
                task = WarmingTask(
                    query_hash=analytics.query_hash,
                    query=analytics.query,
                    filters=analytics.filters,
                    priority=WarmingPriority.HIGH,
                    scheduled_time=schedule_time,
                    estimated_duration=analytics.avg_response_time
                )
                self.warming_tasks.append(task)
    
    async def _generate_predictive_tasks(self):
        """Generate predictive warming tasks"""
        # User sequence predictions
        for user_id, user_data in self.user_patterns.items():
            if len(user_data["queries"]) >= 3:
                # Predict next query in sequence
                recent_sequence = [q[0] for q in user_data["queries"][-3:]]
                
                # Find common follow-up queries
                for other_user, other_data in self.user_patterns.items():
                    if other_user != user_id:
                        other_sequences = [q[0] for q in other_data["queries"]]
                        
                        # Look for pattern matches
                        for i in range(len(other_sequences) - 3):
                            if other_sequences[i:i+3] == recent_sequence:
                                if i + 3 < len(other_sequences):
                                    predicted_query_hash = other_sequences[i + 3]
                                    
                                    if predicted_query_hash in self.query_analytics:
                                        analytics = self.query_analytics[predicted_query_hash]
                                        
                                        task = WarmingTask(
                                            query_hash=analytics.query_hash,
                                            query=analytics.query,
                                            filters=analytics.filters,
                                            priority=WarmingPriority.MEDIUM,
                                            scheduled_time=time.time() + random.randint(30, 300),
                                            estimated_duration=analytics.avg_response_time
                                        )
                                        self.warming_tasks.append(task)
                                        break
    
    async def _warming_loop(self):
        """Background warming task execution"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._execute_warming_tasks()
            except Exception as e:
                logger.error(f"❌ Warming loop error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_warming_tasks(self):
        """Execute ready warming tasks"""
        ready_tasks = [
            task for task in self.warming_tasks
            if (task.should_execute and 
                task.query_hash not in self.active_warming_tasks)
        ]
        
        if not ready_tasks:
            return
        
        # Sort by priority and execute
        ready_tasks.sort(key=lambda t: t.priority.value)
        
        for task in ready_tasks[:self.max_concurrent_warming]:
            asyncio.create_task(self._execute_warming_task(task))
    
    async def _execute_warming_task(self, task: WarmingTask):
        """Execute a single warming task"""
        async with self.warming_semaphore:
            task.attempts += 1
            self.active_warming_tasks.add(task.query_hash)
            
            try:
                start_time = time.time()
                logger.info(f"🔥 Warming cache: {task.query_hash[:8]} (priority: {task.priority.name})")
                
                # Import here to avoid circular imports
                from ..connectors.multi_source_manager import MultiSourceManager
                
                # Create a multi-source manager instance for warming
                # In practice, you'd use the existing instance
                manager = MultiSourceManager()
                await manager.initialize()
                
                # Execute the query to warm the cache
                result = await manager.query_all_sources(
                    query=task.query,
                    filters=task.filters,
                    limit=100,  # Reasonable limit for warming
                    timeout=30.0
                )
                
                execution_time = time.time() - start_time
                
                if result and result.total_records > 0:
                    # Success
                    self.warming_stats["successful_tasks"] += 1
                    self.warming_stats["bytes_warmed"] += len(str(result.data))
                    self.warming_stats["time_saved"] += task.estimated_duration - execution_time
                    
                    # Record the warming
                    self.warming_history.append({
                        "query_hash": task.query_hash,
                        "priority": task.priority.name,
                        "execution_time": execution_time,
                        "records_count": result.total_records,
                        "timestamp": time.time(),
                        "success": True
                    })
                    
                    logger.info(f"✅ Cache warmed: {task.query_hash[:8]} ({result.total_records} records, {execution_time:.2f}s)")
                
                else:
                    # Failed or no results
                    self.warming_stats["failed_tasks"] += 1
                    logger.warning(f"⚠️ Cache warming failed: {task.query_hash[:8]}")
                
            except Exception as e:
                self.warming_stats["failed_tasks"] += 1
                logger.error(f"❌ Cache warming error for {task.query_hash[:8]}: {e}")
                
                self.warming_history.append({
                    "query_hash": task.query_hash,
                    "priority": task.priority.name,
                    "error": str(e),
                    "timestamp": time.time(),
                    "success": False
                })
            
            finally:
                self.active_warming_tasks.discard(task.query_hash)
                self.warming_tasks = [t for t in self.warming_tasks if t != task]
                self.warming_stats["total_tasks"] += 1
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                await self._cleanup_old_data()
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old analytics and history data"""
        current_time = time.time()
        
        # Clean warming history (keep last 1000 entries)
        if len(self.warming_history) > 1000:
            self.warming_history = self.warming_history[-1000:]
        
        # Clean time patterns older than learning window
        cutoff_time = current_time - (self.learning_window_days * 86400)
        
        # This is a simplified cleanup - in practice you'd want more sophisticated logic
        logger.debug("🧹 Performed cache warming data cleanup")
    
    async def get_warming_stats(self) -> Dict[str, Any]:
        """Get comprehensive warming statistics"""
        active_tasks_by_priority = Counter()
        for task in self.warming_tasks:
            active_tasks_by_priority[task.priority.name] += 1
        
        top_queries = sorted(
            self.query_analytics.values(),
            key=lambda a: a.cache_value_score,
            reverse=True
        )[:10]
        
        return {
            "enabled": self.enabled,
            "stats": self.warming_stats.copy(),
            "active_warming_tasks": len(self.active_warming_tasks),
            "pending_tasks": len(self.warming_tasks),
            "tasks_by_priority": dict(active_tasks_by_priority),
            "total_queries_tracked": len(self.query_analytics),
            "learning_window_days": self.learning_window_days,
            "top_queries": [
                {
                    "query_hash": q.query_hash[:8],
                    "cache_value_score": q.cache_value_score,
                    "access_count": q.access_count,
                    "users": len(q.users),
                    "avg_response_time": q.avg_response_time
                }
                for q in top_queries
            ],
            "recent_warming_history": self.warming_history[-20:],
            "cache_hit_improvement": self._calculate_cache_improvement()
        }
    
    def _calculate_cache_improvement(self) -> Dict[str, Any]:
        """Calculate cache hit rate improvement from warming"""
        recent_successful = len([
            h for h in self.warming_history[-100:]
            if h.get("success", False)
        ])
        
        estimated_hits = recent_successful * 0.3  # Estimate 30% hit rate from warming
        
        return {
            "estimated_additional_hits": estimated_hits,
            "time_saved_seconds": self.warming_stats["time_saved"],
            "bytes_warmed": self.warming_stats["bytes_warmed"],
            "warming_efficiency": (self.warming_stats["successful_tasks"] / 
                                 max(1, self.warming_stats["total_tasks"])) * 100
        }
    
    async def force_warm_query(self, query: str, filters: Dict[str, Any] = None, priority: WarmingPriority = WarmingPriority.HIGH):
        """Force immediate warming of a specific query"""
        query_hash = self._generate_query_hash(query, filters)
        
        task = WarmingTask(
            query_hash=query_hash,
            query=query,
            filters=filters or {},
            priority=priority,
            scheduled_time=time.time(),  # Immediate
            estimated_duration=5.0
        )
        
        logger.info(f"🔥 Force warming query: {query_hash[:8]}")
        await self._execute_warming_task(task)
    
    def get_query_recommendations(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get cache warming recommendations"""
        recommendations = []
        
        # Top value queries not currently warmed
        high_value = sorted(
            [a for a in self.query_analytics.values() if a.cache_value_score > 50],
            key=lambda a: a.cache_value_score,
            reverse=True
        )[:5]
        
        for analytics in high_value:
            recommendations.append({
                "type": "high_value",
                "query_hash": analytics.query_hash[:8],
                "score": analytics.cache_value_score,
                "reason": f"High cache value score ({analytics.cache_value_score:.1f})",
                "estimated_benefit": f"{analytics.avg_response_time:.2f}s saved per hit"
            })
        
        return recommendations


# Global cache warmer instance
cache_warmer = IntelligentCacheWarmer()


async def get_cache_warmer() -> IntelligentCacheWarmer:
    """Get the global cache warmer instance"""
    return cache_warmer
