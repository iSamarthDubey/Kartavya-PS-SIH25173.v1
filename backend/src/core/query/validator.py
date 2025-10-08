"""
Query Validator
Validates and sanitizes SIEM queries for safety and performance
"""

from typing import Dict, Tuple, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)

class QueryValidator:
    """
    Validates queries for safety, performance, and correctness
    """
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r'DELETE\s+FROM',
        r'DROP\s+TABLE',
        r'TRUNCATE',
        r'UPDATE\s+SET',
        r'INSERT\s+INTO',
        r'\*\s*:\s*\*',  # Wildcard everything
        r'\.\./',  # Directory traversal
        r'<script',  # XSS attempt
        r'javascript:',  # JavaScript injection
        r'cmd\.exe',  # Command execution
        r'/bin/sh',  # Shell execution
    ]
    
    # Performance thresholds
    MAX_SIZE = 10000
    DEFAULT_SIZE = 100
    MAX_AGGREGATION_BUCKETS = 1000
    MAX_TIME_RANGE_DAYS = 365
    MAX_QUERY_DEPTH = 5
    TIMEOUT_SECONDS = 30
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator
        
        Args:
            strict_mode: If True, apply stricter validation rules
        """
        self.strict_mode = strict_mode
        self.validation_stats = {
            "total_validated": 0,
            "passed": 0,
            "failed": 0,
            "modified": 0
        }
    
    async def validate(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a query for safety and performance
        
        Args:
            query: Query dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        self.validation_stats["total_validated"] += 1
        
        # Check for dangerous patterns
        danger_check = self._check_dangerous_patterns(query)
        if not danger_check[0]:
            self.validation_stats["failed"] += 1
            return danger_check
        
        # Check size limits
        size_check = self._check_size_limits(query)
        if not size_check[0]:
            self.validation_stats["failed"] += 1
            return size_check
        
        # Check aggregation complexity
        if "aggs" in query or "aggregations" in query:
            agg_check = self._check_aggregations(query)
            if not agg_check[0]:
                self.validation_stats["failed"] += 1
                return agg_check
        
        # Check query depth
        depth_check = self._check_query_depth(query)
        if not depth_check[0]:
            self.validation_stats["failed"] += 1
            return depth_check
        
        # Check time range
        time_check = self._check_time_range(query)
        if not time_check[0]:
            self.validation_stats["failed"] += 1
            return time_check
        
        self.validation_stats["passed"] += 1
        return True, None
    
    def _check_dangerous_patterns(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for dangerous patterns in query"""
        query_str = str(query)
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query_str, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False, f"Query contains dangerous pattern: {pattern}"
        
        return True, None
    
    def _check_size_limits(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check query size limits"""
        size = query.get("size", 0)
        
        if size > self.MAX_SIZE:
            return False, f"Query size {size} exceeds maximum {self.MAX_SIZE}"
        
        # Check from/size for pagination
        from_param = query.get("from", 0)
        if from_param + size > self.MAX_SIZE:
            return False, f"Pagination exceeds maximum: from({from_param}) + size({size}) > {self.MAX_SIZE}"
        
        return True, None
    
    def _check_aggregations(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check aggregation complexity"""
        aggs = query.get("aggs") or query.get("aggregations", {})
        
        # Check total bucket count
        bucket_count = self._count_aggregation_buckets(aggs)
        if bucket_count > self.MAX_AGGREGATION_BUCKETS:
            return False, f"Aggregation buckets ({bucket_count}) exceed maximum {self.MAX_AGGREGATION_BUCKETS}"
        
        # Check nesting depth
        depth = self._get_aggregation_depth(aggs)
        if depth > 3:
            return False, f"Aggregation nesting too deep: {depth} levels"
        
        return True, None
    
    def _count_aggregation_buckets(self, aggs: Dict, current_count: int = 0) -> int:
        """Count total aggregation buckets"""
        for key, value in aggs.items():
            if isinstance(value, dict):
                size = value.get("size", 10)
                current_count += size
                
                # Check nested aggregations
                if "aggs" in value or "aggregations" in value:
                    nested = value.get("aggs") or value.get("aggregations", {})
                    current_count = self._count_aggregation_buckets(nested, current_count)
        
        return current_count
    
    def _get_aggregation_depth(self, aggs: Dict, depth: int = 0) -> int:
        """Get aggregation nesting depth"""
        if not aggs:
            return depth
        
        max_depth = depth
        for key, value in aggs.items():
            if isinstance(value, dict):
                if "aggs" in value or "aggregations" in value:
                    nested = value.get("aggs") or value.get("aggregations", {})
                    nested_depth = self._get_aggregation_depth(nested, depth + 1)
                    max_depth = max(max_depth, nested_depth)
        
        return max_depth
    
    def _check_query_depth(self, query: Dict[str, Any], depth: int = 0) -> Tuple[bool, Optional[str]]:
        """Check query nesting depth"""
        if depth > self.MAX_QUERY_DEPTH:
            return False, f"Query nesting too deep: {depth} levels"
        
        if "query" in query:
            return self._check_query_depth(query["query"], depth + 1)
        
        if "bool" in query:
            bool_query = query["bool"]
            for clause in ["must", "should", "must_not", "filter"]:
                if clause in bool_query:
                    for sub_query in bool_query[clause]:
                        valid, error = self._check_query_depth(sub_query, depth + 1)
                        if not valid:
                            return False, error
        
        return True, None
    
    def _check_time_range(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check time range is reasonable"""
        # Look for range queries on timestamp fields
        if "query" in query:
            return self._check_time_range_in_query(query["query"])
        
        return True, None
    
    def _check_time_range_in_query(self, query_part: Dict) -> Tuple[bool, Optional[str]]:
        """Recursively check time ranges in query"""
        if "range" in query_part:
            for field, range_def in query_part["range"].items():
                if "@timestamp" in field or "timestamp" in field.lower():
                    # Check if range is too broad
                    if "gte" in range_def and "lte" in range_def:
                        # Simple check - could be enhanced
                        pass
        
        if "bool" in query_part:
            bool_query = query_part["bool"]
            for clause in ["must", "should", "must_not", "filter"]:
                if clause in bool_query:
                    for sub_query in bool_query[clause]:
                        valid, error = self._check_time_range_in_query(sub_query)
                        if not valid:
                            return False, error
        
        return True, None
    
    def add_safety_limits(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add safety limits to a query
        
        Args:
            query: Original query
            
        Returns:
            Query with safety limits added
        """
        self.validation_stats["modified"] += 1
        
        # Add size limit if not specified
        if "size" not in query:
            query["size"] = self.DEFAULT_SIZE
        elif query["size"] > self.MAX_SIZE:
            query["size"] = self.MAX_SIZE
            logger.info(f"Reduced query size to {self.MAX_SIZE}")
        
        # Add timeout
        if "timeout" not in query:
            query["timeout"] = f"{self.TIMEOUT_SECONDS}s"
        
        # Add terminate_after for safety
        if "terminate_after" not in query:
            query["terminate_after"] = self.MAX_SIZE * 10
        
        # Add track_total_hits limitation
        if "track_total_hits" not in query:
            query["track_total_hits"] = False
        
        return query
    
    def sanitize_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a query by removing dangerous elements
        
        Args:
            query: Original query
            
        Returns:
            Sanitized query
        """
        # Deep copy to avoid modifying original
        import copy
        sanitized = copy.deepcopy(query)
        
        # Remove script fields
        if "script_fields" in sanitized:
            del sanitized["script_fields"]
            logger.warning("Removed script_fields from query")
        
        # Remove scripts from aggregations
        if "aggs" in sanitized or "aggregations" in sanitized:
            self._remove_scripts_from_aggs(sanitized.get("aggs") or sanitized.get("aggregations", {}))
        
        return sanitized
    
    def _remove_scripts_from_aggs(self, aggs: Dict) -> None:
        """Remove script elements from aggregations"""
        for key, value in list(aggs.items()):
            if isinstance(value, dict):
                if "script" in value:
                    del value["script"]
                    logger.warning(f"Removed script from aggregation {key}")
                
                # Recurse into nested aggregations
                if "aggs" in value or "aggregations" in value:
                    nested = value.get("aggs") or value.get("aggregations", {})
                    self._remove_scripts_from_aggs(nested)
    
    def estimate_cost(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the cost/resources required for a query
        
        Args:
            query: Query to estimate
            
        Returns:
            Cost estimation dictionary
        """
        cost = {
            "estimated_docs_scanned": 0,
            "estimated_time_ms": 0,
            "complexity": "low",
            "warnings": []
        }
        
        # Estimate based on size
        size = query.get("size", self.DEFAULT_SIZE)
        cost["estimated_docs_scanned"] = size * 10  # Rough estimate
        
        # Check for expensive operations
        if "aggs" in query or "aggregations" in query:
            cost["complexity"] = "medium"
            cost["estimated_time_ms"] += 100
            
            aggs = query.get("aggs") or query.get("aggregations", {})
            bucket_count = self._count_aggregation_buckets(aggs)
            if bucket_count > 100:
                cost["complexity"] = "high"
                cost["warnings"].append(f"High aggregation bucket count: {bucket_count}")
        
        # Check for wildcards
        query_str = str(query)
        if "*" in query_str:
            cost["complexity"] = "medium" if cost["complexity"] == "low" else cost["complexity"]
            cost["warnings"].append("Query contains wildcards")
        
        # Check for regex
        if "regexp" in query_str:
            cost["complexity"] = "high"
            cost["warnings"].append("Query contains regex")
        
        return cost
    
    def get_validation_stats(self) -> Dict[str, int]:
        """Get validation statistics"""
        return self.validation_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset validation statistics"""
        self.validation_stats = {
            "total_validated": 0,
            "passed": 0,
            "failed": 0,
            "modified": 0
        }
