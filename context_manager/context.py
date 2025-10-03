"""
Enhanced Context Manager for maintaining conversation state with persistence.
Features: SQLite persistence, TTL support, thread safety, caching, search capabilities.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
import sqlite3
import threading
import time
import os
import hashlib

logger = logging.getLogger(__name__)


DEFAULT_DB = "siem_contexts.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contexts (
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    metadata_json TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    ttl REAL,
    PRIMARY KEY (namespace, key)
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_contexts_namespace ON contexts(namespace);
CREATE INDEX IF NOT EXISTS idx_contexts_ttl ON contexts(ttl);
CREATE INDEX IF NOT EXISTS idx_contexts_updated ON contexts(updated_at);
"""


class ContextManager:
    """Enhanced context manager with persistence, TTL, and thread safety."""
    
    def __init__(self, max_history: int = 50, db_path: str = DEFAULT_DB):
        """Initialize enhanced context manager."""
        self.max_history = max_history
        self.db_path = db_path
        self._lock = threading.RLock()
        self._cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        
        # Legacy in-memory storage for backward compatibility
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_data: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {
            'default_time_range': 'last_hour',
            'max_results': 100,
            'preferred_format': 'table'
        }
        
        # Initialize database
        self._ensure_db()
        self._load_session_from_db()
        self._start_cleanup_thread()

    def _conn(self) -> sqlite3.Connection:
        """Create database connection."""
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_db(self):
        """Initialize database schema."""
        with self._conn() as conn:
            conn.executescript(CREATE_TABLE_SQL)
            conn.executescript(CREATE_INDEX_SQL)
            conn.commit()

    def _now(self) -> float:
        return time.time()

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_expired():
            while True:
                try:
                    time.sleep(300)  # Clean every 5 minutes
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            now = self._now()
            with self._conn() as conn:
                conn.execute("DELETE FROM contexts WHERE ttl IS NOT NULL AND ttl < ?", (now,))
                conn.commit()

    def _load_session_from_db(self):
        """Load session data from database."""
        # Load conversation history
        history = self.get_persistent_context("session", "conversation_history", default=[])
        if history:
            self.conversation_history = history[-self.max_history:]
        
        # Load session data
        session = self.get_persistent_context("session", "session_data", default={})
        if session:
            self.session_data = session
        
        # Load user preferences
        prefs = self.get_persistent_context("session", "user_preferences", default={})
        if prefs:
            self.user_preferences.update(prefs)

    def _save_session_to_db(self):
        """Save session data to database."""
        self.set_persistent_context("session", "conversation_history", self.conversation_history, ttl=86400)
        self.set_persistent_context("session", "session_data", self.session_data, ttl=86400)
        self.set_persistent_context("session", "user_preferences", self.user_preferences)

    # New persistent context methods (YOUR shared code integrated)
    def set_context(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Insert or update a context entry.

        ttl: seconds from now. If None => non-expiring.
        metadata: arbitrary dict stored alongside the value.
        """
        with self._lock:
            now = self._now()
            meta_json = json.dumps(metadata or {})
            val_json = json.dumps(value)

            with self._conn() as conn:
                cur = conn.cursor()
                # try update first
                cur.execute(
                    "SELECT version FROM contexts WHERE namespace=? AND key=?",
                    (namespace, key),
                )
                row = cur.fetchone()
                if row:
                    version = row["version"] + 1
                    cur.execute(
                        "UPDATE contexts SET value_json=?, metadata_json=?, version=?, updated_at=?, ttl=? WHERE namespace=? AND key=?",
                        (val_json, meta_json, version, now, (now + ttl) if ttl else None, namespace, key),
                    )
                else:
                    version = 1
                    cur.execute(
                        "INSERT INTO contexts(namespace, key, value_json, metadata_json, version, created_at, updated_at, ttl) VALUES (?,?,?,?,?,?,?,?)",
                        (namespace, key, val_json, meta_json, version, now, now, (now + ttl) if ttl else None),
                    )
                conn.commit()

            # update local cache
            self._cache[(namespace, key)] = {
                "value": value,
                "metadata": metadata or {},
                "version": version,
                "updated_at": now,
                "ttl": (now + ttl) if ttl else None,
            }

    def _is_expired_row(self, row: sqlite3.Row) -> bool:
        ttl = row["ttl"]
        if ttl is None:
            return False
        return self._now() > float(ttl)

    def get_context(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get a stored context value. Returns default if not present or expired."""
        with self._lock:
            cache_key = (namespace, key)
            # check cache first
            cached = self._cache.get(cache_key)
            if cached:
                ttl = cached.get("ttl")
                if ttl and self._now() > ttl:
                    # expired -> delete and fall through
                    try:
                        self.delete_context(namespace, key)
                    except Exception:
                        pass
                else:
                    return cached["value"]

            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                row = cur.fetchone()
                if not row:
                    return default
                if self._is_expired_row(row):
                    # remove expired
                    cur.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                    conn.commit()
                    self._cache.pop(cache_key, None)
                    return default

                value = json.loads(row["value_json"])
                metadata = json.loads(row["metadata_json"] or "{}")
                version = int(row["version"])
                updated_at = float(row["updated_at"]) if row["updated_at"] else None
                ttl = float(row["ttl"]) if row["ttl"] else None

                # warm cache
                self._cache[cache_key] = {
                    "value": value,
                    "metadata": metadata,
                    "version": version,
                    "updated_at": updated_at,
                    "ttl": ttl,
                }
                return value

    def delete_context(self, namespace: str, key: str) -> bool:
        """Delete a context entry."""
        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                conn.commit()
            existed = self._cache.pop((namespace, key), None) is not None
            return cur.rowcount > 0 or existed

    def list_keys(self, namespace: str) -> List[str]:
        """List all non-expired keys in a namespace."""
        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT key, ttl FROM contexts WHERE namespace=?", (namespace,))
                rows = cur.fetchall()
                res = []
                for r in rows:
                    if r["ttl"] and self._now() > float(r["ttl"]):
                        # lazy cleanup
                        conn.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, r["key"]))
                    else:
                        res.append(r["key"])
                conn.commit()
                return res

    def search(self, namespace: str, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """A simple substring search across value_json and metadata_json.
        Not a replacement for a true full-text search, but useful for quick lookups.
        """
        with self._lock:
            q = f"%{query}%"
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT key, value_json, metadata_json, version, ttl FROM contexts WHERE namespace=? AND (value_json LIKE ? OR metadata_json LIKE ?) LIMIT ?",
                    (namespace, q, q, limit),
                )
                rows = cur.fetchall()
                results = []
                for r in rows:
                    if r["ttl"] and self._now() > float(r["ttl"]):
                        # skip expired
                        continue
                    results.append({
                        "key": r["key"],
                        "value": json.loads(r["value_json"]),
                        "metadata": json.loads(r["metadata_json"] or "{}"),
                        "version": r["version"],
                    })
                return results

    def export_namespace(self, namespace: str, path: str) -> None:
        """Export a namespace to a JSON file."""
        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM contexts WHERE namespace=?", (namespace,))
                rows = cur.fetchall()
                out = {}
                for r in rows:
                    if r["ttl"] and self._now() > float(r["ttl"]):
                        continue
                    out[r["key"]] = {
                        "value": json.loads(r["value_json"]),
                        "metadata": json.loads(r["metadata_json"] or "{}"),
                        "version": r["version"],
                        "updated_at": r["updated_at"],
                        "ttl": r["ttl"],
                    }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(out, f, indent=2, ensure_ascii=False)

    def import_namespace(self, namespace: str, path: str, overwrite: bool = False) -> None:
        """Import a JSON exported by export_namespace into the given namespace.
        If overwrite is False, existing keys will be skipped.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                for key, entry in data.items():
                    cur.execute("SELECT 1 FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                    if cur.fetchone() and not overwrite:
                        continue
                    # compute ttl remaining if present
                    ttl = None
                    if entry.get("ttl"):
                        ttl = float(entry["ttl"]) - self._now()
                        if ttl <= 0:
                            continue
                    self.set_context(namespace, key, entry["value"], ttl=int(ttl) if ttl else None, metadata=entry.get("metadata"))

    def build_elasticsearch_context_query(self, namespace: str, keys: List[str]) -> Dict[str, Any]:
        """Create a simple Elasticsearch bool must query using stored context values.

        Example: if key 'usernames' stores ['alice','bob'] and 'ips' stores ['1.2.3.4'],
        create a bool -> should -> terms for common fields. This is opinionated and
        intended to be adapted to your project's mapping.
        """
        parts = []
        for key in keys:
            val = self.get_context(namespace, key)
            if val is None:
                continue
            # heuristics: lists -> terms, strings -> match, numbers -> term
            if isinstance(val, list):
                # try map key to typical fields
                probable_fields = [key, f"{key}.keyword", f"{key}.raw"]
                parts.append({
                    "bool": {"should": [{"terms": {f: val}} for f in probable_fields], "minimum_should_match": 1}
                })
            elif isinstance(val, (int, float)):
                parts.append({"term": {key: val}})
            elif isinstance(val, str):
                parts.append({"match_phrase": {key: val}})
            else:
                # fallback to match on stringified JSON
                parts.append({"match": {key: json.dumps(val)}})

        if not parts:
            return {"match_none": {}}

        return {"bool": {"must": parts}}

    # Original set_persistent_context method (for backward compatibility)
    def set_persistent_context(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store persistent context with optional TTL."""
        with self._lock:
            now = self._now()
            meta_json = json.dumps(metadata or {})
            val_json = json.dumps(value)

            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT version FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                row = cur.fetchone()
                
                if row:
                    version = row["version"] + 1
                    cur.execute(
                        "UPDATE contexts SET value_json=?, metadata_json=?, version=?, updated_at=?, ttl=? WHERE namespace=? AND key=?",
                        (val_json, meta_json, version, now, (now + ttl) if ttl else None, namespace, key),
                    )
                else:
                    version = 1
                    cur.execute(
                        "INSERT INTO contexts(namespace, key, value_json, metadata_json, version, created_at, updated_at, ttl) VALUES (?,?,?,?,?,?,?,?)",
                        (namespace, key, val_json, meta_json, version, now, now, (now + ttl) if ttl else None),
                    )
                conn.commit()

            # Update cache
            self._cache[(namespace, key)] = {
                "value": value,
                "metadata": metadata or {},
                "version": version,
                "updated_at": now,
                "ttl": (now + ttl) if ttl else None,
            }

    def get_persistent_context(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get persistent context value."""
        with self._lock:
            cache_key = (namespace, key)
            cached = self._cache.get(cache_key)
            if cached:
                ttl = cached.get("ttl")
                if ttl and self._now() > ttl:
                    self.delete_persistent_context(namespace, key)
                    return default
                return cached["value"]

            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                row = cur.fetchone()
                if not row:
                    return default
                    
                if row["ttl"] and self._now() > float(row["ttl"]):
                    cur.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                    conn.commit()
                    return default

                value = json.loads(row["value_json"])
                self._cache[cache_key] = {
                    "value": value,
                    "metadata": json.loads(row["metadata_json"] or "{}"),
                    "version": row["version"],
                    "updated_at": row["updated_at"],
                    "ttl": row["ttl"],
                }
                return value

    def delete_persistent_context(self, namespace: str, key: str) -> bool:
        """Delete persistent context."""
        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                conn.commit()
                deleted = cur.rowcount > 0
            self._cache.pop((namespace, key), None)
            return deleted

    def search_context(self, namespace: str, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Search context entries."""
        with self._lock:
            q = f"%{query}%"
            now = self._now()
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    """SELECT key, value_json, metadata_json, version 
                       FROM contexts 
                       WHERE namespace=? AND (ttl IS NULL OR ttl > ?) 
                       AND (value_json LIKE ? OR metadata_json LIKE ?) 
                       ORDER BY updated_at DESC LIMIT ?""",
                    (namespace, now, q, q, limit),
                )
                results = []
                for row in cur.fetchall():
                    results.append({
                        "key": row["key"],
                        "value": json.loads(row["value_json"]),
                        "metadata": json.loads(row["metadata_json"] or "{}"),
                        "version": row["version"],
                    })
                return results

    # Enhanced investigation methods
    def start_investigation(self, investigation_name: str, initial_indicators: Dict[str, Any], user_id: str = "default") -> str:
        """Start a new security investigation."""
        investigation_id = f"inv_{int(self._now())}"
        
        investigation_data = {
            "name": investigation_name,
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "indicators": initial_indicators,
            "timeline": [],
            "related_queries": []
        }
        
        self.set_persistent_context("investigations", investigation_id, investigation_data, ttl=7*24*3600)
        logger.info(f"Started investigation: {investigation_id}")
        return investigation_id

    def add_to_investigation(self, investigation_id: str, findings: Dict[str, Any]):
        """Add findings to investigation."""
        investigation = self.get_persistent_context("investigations", investigation_id)
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
        
        investigation["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "findings": findings
        })
        
        if "indicators" in findings:
            for key, value in findings["indicators"].items():
                if key in investigation["indicators"]:
                    if isinstance(investigation["indicators"][key], list):
                        investigation["indicators"][key].extend(value if isinstance(value, list) else [value])
                    else:
                        investigation["indicators"][key] = [investigation["indicators"][key]]
                        investigation["indicators"][key].extend(value if isinstance(value, list) else [value])
                else:
                    investigation["indicators"][key] = value
        
        self.set_persistent_context("investigations", investigation_id, investigation, ttl=7*24*3600)

    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Get investigation data."""
        return self.get_persistent_context("investigations", investigation_id)

    def list_investigations(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all investigations."""
        results = self.search_context("investigations", "", limit=100)
        if user_id:
            results = [r for r in results if r["value"].get("created_by") == user_id]
        return results

    # Query caching methods
    def cache_query_result(self, query: str, results: Dict[str, Any], user_id: str = "default", ttl: int = 1800):
        """Cache query results."""
        query_hash = hashlib.md5(f"{query}_{user_id}".encode()).hexdigest()
        self.set_persistent_context("query_cache", query_hash, {
            "query": query,
            "results": results,
            "user_id": user_id,
            "cached_at": datetime.now().isoformat()
        }, ttl=ttl)

    def get_cached_query_result(self, query: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        query_hash = hashlib.md5(f"{query}_{user_id}".encode()).hexdigest()
        return self.get_persistent_context("query_cache", query_hash)

    # Enhanced Elasticsearch query generation
    def build_elasticsearch_investigation_query(self, investigation_id: str) -> Dict[str, Any]:
        """Build Elasticsearch query from investigation context."""
        investigation = self.get_investigation(investigation_id)
        if not investigation:
            return {"match_all": {}}
        
        must_clauses = []
        should_clauses = []
        
        indicators = investigation.get("indicators", {})
        for key, values in indicators.items():
            if not values:
                continue
                
            if isinstance(values, list):
                if key in ['ip_addresses', 'source_ips', 'dest_ips']:
                    should_clauses.extend([
                        {"terms": {"source.ip": values}},
                        {"terms": {"destination.ip": values}},
                        {"terms": {"client.ip": values}}
                    ])
                elif key in ['usernames', 'users']:
                    should_clauses.extend([
                        {"terms": {"user.name": values}},
                        {"terms": {"user.id": values}}
                    ])
                elif key in ['processes', 'process_names']:
                    should_clauses.append({"terms": {"process.name": values}})
                else:
                    should_clauses.append({"terms": {key: values}})
            elif isinstance(values, str):
                if key in ['event_type', 'action']:
                    must_clauses.append({"match": {"event.action": values}})
                elif key in ['host', 'hostname']:
                    must_clauses.append({"match": {"host.name": values}})
                else:
                    must_clauses.append({"match_phrase": {key: values}})
            elif isinstance(values, dict) and key == 'time_range':
                must_clauses.append({"range": {"@timestamp": values}})

        query = {"bool": {}}
        if must_clauses:
            query["bool"]["must"] = must_clauses
        if should_clauses:
            query["bool"]["should"] = should_clauses
            query["bool"]["minimum_should_match"] = 1

        return query if query["bool"] else {"match_all": {}}

    # Legacy methods (enhanced with persistence)
    
    def add_interaction(self, user_query: str, parsed_query: Dict[str, Any], 
                       siem_query: Dict[str, Any], results: List[Dict[str, Any]]):
        """Add an interaction to the conversation history (now persistent)."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_query': user_query,
            'parsed_query': parsed_query,
            'siem_query': siem_query,
            'results_count': len(results),
            'results_summary': self._summarize_results(results)
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only recent interactions
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Save to database
        self._save_session_to_db()
    
    def get_conversation_context(self, num_interactions: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self.conversation_history[-num_interactions:]
    
    def get_related_queries(self, current_query: str) -> List[Dict[str, Any]]:
        """Find related queries from conversation history and database."""
        related = []
        current_words = set(current_query.lower().split())
        
        # Search in-memory history
        for interaction in self.conversation_history:
            query_words = set(interaction['user_query'].lower().split())
            overlap = len(current_words.intersection(query_words))
            
            if overlap > 1:  # At least 2 words in common
                related.append({
                    'query': interaction['user_query'],
                    'timestamp': interaction['timestamp'],
                    'similarity_score': overlap / len(current_words.union(query_words)),
                    'source': 'current_session'
                })
        
        # Search in persistent storage
        search_results = self.search_context("conversations", current_query, limit=10)
        for result in search_results:
            interaction = result["value"]
            if interaction.get('user_query'):
                query_words = set(interaction['user_query'].lower().split())
                overlap = len(current_words.intersection(query_words))
                if overlap > 1:
                    related.append({
                        'query': interaction['user_query'],
                        'timestamp': interaction.get('timestamp', ''),
                        'similarity_score': overlap / len(current_words.union(query_words)),
                        'source': 'history'
                    })
        
        # Sort by similarity score and remove duplicates
        seen_queries = set()
        unique_related = []
        for item in sorted(related, key=lambda x: x['similarity_score'], reverse=True):
            if item['query'] not in seen_queries:
                seen_queries.add(item['query'])
                unique_related.append(item)
        
        return unique_related[:5]  # Return top 5 related queries
    
    def update_session_data(self, key: str, value: Any):
        """Update session data (now persistent)."""
        self.session_data[key] = value
        self._save_session_to_db()
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.session_data.get(key, default)
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference (now persistent)."""
        self.user_preferences[key] = value
        self._save_session_to_db()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        return self.user_preferences.get(key, default)
    
    def get_query_suggestions(self, partial_query: str = "") -> List[str]:
        """Get query suggestions based on history and partial input (enhanced with search)."""
        suggestions = []
        
        # Add suggestions from recent queries
        for interaction in self.conversation_history[-10:]:
            query = interaction['user_query']
            if partial_query.lower() in query.lower():
                suggestions.append(query)
        
        # Search persistent storage for suggestions
        if partial_query:
            search_results = self.search_context("conversations", partial_query, limit=5)
            for result in search_results:
                interaction = result["value"]
                if interaction.get('user_query') and interaction['user_query'] not in suggestions:
                    suggestions.append(interaction['user_query'])
        
        # Add common query patterns
        common_patterns = [
            "Show me failed login attempts from the last hour",
            "Find all high severity alerts today",
            "Count security events from IP 192.168.1.100",
            "Search for malware detection in the last 24 hours",
            "Display network anomalies this week",
            "Show user authentication failures",
            "Find DNS queries to suspicious domains",
            "Analyze traffic patterns for unusual activity"
        ]
        
        for pattern in common_patterns:
            if not partial_query or partial_query.lower() in pattern.lower():
                if pattern not in suggestions:
                    suggestions.append(pattern)
        
        return suggestions[:8]  # Increased limit
    
    def _summarize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of query results."""
        if not results:
            return {'count': 0}
        
        summary = {
            'count': len(results),
            'sample_fields': list(results[0].keys()) if results else [],
            'has_timestamps': any('@timestamp' in str(result) for result in results),
            'has_ip_addresses': any('ip' in str(result).lower() for result in results)
        }
        
        return summary
    
    def clear_session(self):
        """Clear current session data (enhanced with persistent cleanup)."""
        self.conversation_history = []
        self.session_data = {}
        
        # Clear from database
        self.delete_persistent_context("session", "conversation_history")
        self.delete_persistent_context("session", "session_data")
    
    def export_session(self) -> str:
        """Export session data as JSON (enhanced with persistent data)."""
        # Include both in-memory and persistent data
        persistent_investigations = self.search_context("investigations", "", limit=100)
        persistent_cache = self.search_context("query_cache", "", limit=50)
        
        export_data = {
            'conversation_history': self.conversation_history,
            'session_data': self.session_data,
            'user_preferences': self.user_preferences,
            'investigations': persistent_investigations,
            'cached_queries': persistent_cache,
            'export_timestamp': datetime.now().isoformat()
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_session(self, session_json: str):
        """Import session data from JSON (enhanced with persistent storage)."""
        try:
            data = json.loads(session_json)
            self.conversation_history = data.get('conversation_history', [])
            self.session_data = data.get('session_data', {})
            self.user_preferences.update(data.get('user_preferences', {}))
            
            # Import investigations
            investigations = data.get('investigations', [])
            for inv in investigations:
                self.set_persistent_context("investigations", inv["key"], inv["value"], 
                                          metadata=inv.get("metadata"))
            
            # Save to database
            self._save_session_to_db()
            logger.info("Enhanced session data imported successfully")
        except Exception as e:
            logger.error(f"Failed to import session data: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics."""
        total_queries = len(self.conversation_history)
        
        # Get database stats
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT namespace, COUNT(*) as count FROM contexts GROUP BY namespace")
            db_stats = {row["namespace"]: row["count"] for row in cur.fetchall()}
            
            cur.execute("SELECT COUNT(*) as total FROM contexts")
            total_contexts = cur.fetchone()["total"]
        
        if total_queries == 0:
            base_stats = {'total_queries': 0}
        else:
            # Calculate average results per query
            total_results = sum(interaction['results_count'] for interaction in self.conversation_history)
            avg_results = total_results / total_queries if total_queries > 0 else 0
            
            # Find most common query types
            query_types = [interaction['parsed_query'].get('intent', 'unknown') 
                          for interaction in self.conversation_history]
            
            base_stats = {
                'total_queries': total_queries,
                'average_results_per_query': round(avg_results, 2),
                'session_duration': self._calculate_session_duration(),
                'most_common_intents': self._get_most_common(query_types)
            }
        
        base_stats.update({
            'persistent_contexts': total_contexts,
            'contexts_by_namespace': db_stats,
            'cache_size': len(self._cache),
            'database_path': self.db_path
        })
        
        return base_stats

    # Utility methods for dashboard and monitoring
    def get_dashboard_data(self, user_id: str = "default") -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            "user_session": {
                "conversation_history": self.conversation_history[-10:],
                "session_data": self.session_data,
                "user_preferences": self.user_preferences
            },
            "active_investigations": self.list_investigations(user_id),
            "recent_queries": [h['user_query'] for h in self.conversation_history[-5:]],
            "system_stats": self.get_session_stats()
        }

    def cleanup_old_data(self, days_old: int = 30):
        """Cleanup data older than specified days."""
        cutoff_time = self._now() - (days_old * 24 * 3600)
        with self._conn() as conn:
            conn.execute("DELETE FROM contexts WHERE created_at < ?", (cutoff_time,))
            conn.commit()
            logger.info(f"Cleaned up contexts older than {days_old} days")
    
    def _calculate_session_duration(self) -> str:
        """Calculate session duration."""
        if len(self.conversation_history) < 2:
            return "0 minutes"
        
        start_time = datetime.fromisoformat(self.conversation_history[0]['timestamp'])
        end_time = datetime.fromisoformat(self.conversation_history[-1]['timestamp'])
        duration = end_time - start_time
        
        return f"{duration.total_seconds() / 60:.1f} minutes"
    
    def _get_most_common(self, items: List[str], top_n: int = 3) -> List[Dict[str, Any]]:
        """Get most common items in a list."""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{'item': item, 'count': count} for item, count in sorted_items[:top_n]]