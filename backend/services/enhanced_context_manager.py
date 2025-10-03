"""
Enhanced Context Manager for SIEM NLP Assistant
Combines the new ContextManager with SIEM-specific features

Features:
- Persistent context storage with SQLite backend
- Thread-safe operations with TTL support
- SIEM-specific context types (investigations, alerts, queries)
- Elasticsearch query generation from context
- Session management for multi-user environment
"""

from __future__ import annotations
import sqlite3
import json
import time
import threading
import os
from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
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

class SIEMContextManager:
    """Enhanced context manager for SIEM operations with persistence and TTL."""

    def __init__(self, db_path: str = DEFAULT_DB):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._ensure_db()
        self._start_cleanup_thread()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.Connection(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_db(self):
        with self._conn() as conn:
            conn.executescript(CREATE_TABLE_SQL)
            conn.executescript(CREATE_INDEX_SQL)
            conn.commit()

    def _now(self) -> float:
        return time.time()

    def _start_cleanup_thread(self):
        """Start background thread for periodic cleanup of expired entries."""
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
        """Remove expired entries from database."""
        with self._lock:
            now = self._now()
            with self._conn() as conn:
                conn.execute("DELETE FROM contexts WHERE ttl IS NOT NULL AND ttl < ?", (now,))
                conn.commit()
                # Clear cache entries that might be expired
                expired_keys = []
                for cache_key, cached in self._cache.items():
                    if cached.get("ttl") and now > cached["ttl"]:
                        expired_keys.append(cache_key)
                for key in expired_keys:
                    self._cache.pop(key, None)

    def set_context(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Insert or update a context entry."""
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

    def get_context(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get a stored context value."""
        with self._lock:
            cache_key = (namespace, key)
            cached = self._cache.get(cache_key)
            if cached:
                ttl = cached.get("ttl")
                if ttl and self._now() > ttl:
                    self.delete_context(namespace, key)
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
                metadata = json.loads(row["metadata_json"] or "{}")
                
                self._cache[cache_key] = {
                    "value": value,
                    "metadata": metadata,
                    "version": row["version"],
                    "updated_at": row["updated_at"],
                    "ttl": row["ttl"],
                }
                return value

    def delete_context(self, namespace: str, key: str) -> bool:
        """Delete a context entry."""
        with self._lock:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM contexts WHERE namespace=? AND key=?", (namespace, key))
                conn.commit()
                deleted = cur.rowcount > 0
            self._cache.pop((namespace, key), None)
            return deleted

    def list_keys(self, namespace: str) -> List[str]:
        """List all non-expired keys in a namespace."""
        with self._lock:
            now = self._now()
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT key FROM contexts WHERE namespace=? AND (ttl IS NULL OR ttl > ?)",
                    (namespace, now)
                )
                return [row["key"] for row in cur.fetchall()]

    def search(self, namespace: str, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Search context entries by content."""
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

    # SIEM-Specific Methods

    def set_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 3600):
        """Store user session data with 1-hour default TTL."""
        self.set_context("user_sessions", user_id, session_data, ttl=ttl, 
                        metadata={"type": "session", "created": datetime.now().isoformat()})

    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session data."""
        return self.get_context("user_sessions", user_id)

    def set_investigation(self, investigation_id: str, investigation_data: Dict[str, Any], ttl: int = 86400):
        """Store investigation context with 24-hour default TTL."""
        self.set_context("investigations", investigation_id, investigation_data, ttl=ttl,
                        metadata={"type": "investigation", "created": datetime.now().isoformat()})

    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve investigation context."""
        return self.get_context("investigations", investigation_id)

    def set_query_cache(self, query_hash: str, results: Dict[str, Any], ttl: int = 1800):
        """Cache query results with 30-minute default TTL."""
        self.set_context("query_cache", query_hash, results, ttl=ttl,
                        metadata={"type": "query_cache", "cached_at": datetime.now().isoformat()})

    def get_query_cache(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached query results."""
        return self.get_context("query_cache", query_hash)

    def build_elasticsearch_context_query(self, namespace: str, keys: List[str]) -> Dict[str, Any]:
        """Build Elasticsearch query from stored context values."""
        must_clauses = []
        should_clauses = []
        
        for key in keys:
            value = self.get_context(namespace, key)
            if value is None:
                continue
                
            if isinstance(value, list):
                # Handle lists as terms queries
                if key in ['ip_addresses', 'source_ips', 'dest_ips']:
                    should_clauses.extend([
                        {"terms": {"source.ip": value}},
                        {"terms": {"destination.ip": value}},
                        {"terms": {"client.ip": value}}
                    ])
                elif key in ['usernames', 'users']:
                    should_clauses.extend([
                        {"terms": {"user.name": value}},
                        {"terms": {"user.id": value}}
                    ])
                elif key in ['processes', 'process_names']:
                    should_clauses.append({"terms": {"process.name": value}})
                else:
                    should_clauses.append({"terms": {key: value}})
                    
            elif isinstance(value, str):
                # Handle strings as match queries
                if key in ['event_type', 'action']:
                    must_clauses.append({"match": {"event.action": value}})
                elif key in ['host', 'hostname']:
                    must_clauses.append({"match": {"host.name": value}})
                else:
                    must_clauses.append({"match_phrase": {key: value}})
                    
            elif isinstance(value, (int, float)):
                # Handle numbers as exact matches
                must_clauses.append({"term": {key: value}})
                
            elif isinstance(value, dict):
                # Handle time ranges
                if key == 'time_range' and 'gte' in value:
                    must_clauses.append({"range": {"@timestamp": value}})

        query = {"bool": {}}
        if must_clauses:
            query["bool"]["must"] = must_clauses
        if should_clauses:
            query["bool"]["should"] = should_clauses
            query["bool"]["minimum_should_match"] = 1

        return query if query["bool"] else {"match_all": {}}

    def export_namespace(self, namespace: str, path: str) -> None:
        """Export namespace to JSON file."""
        with self._lock:
            now = self._now()
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM contexts WHERE namespace=? AND (ttl IS NULL OR ttl > ?)",
                    (namespace, now)
                )
                rows = cur.fetchall()
                
                export_data = {}
                for row in rows:
                    export_data[row["key"]] = {
                        "value": json.loads(row["value_json"]),
                        "metadata": json.loads(row["metadata_json"] or "{}"),
                        "version": row["version"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "ttl": row["ttl"],
                    }
                
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        with self._lock:
            now = self._now()
            with self._conn() as conn:
                cur = conn.cursor()
                
                # Total entries
                cur.execute("SELECT COUNT(*) as total FROM contexts")
                total = cur.fetchone()["total"]
                
                # Active (non-expired) entries
                cur.execute("SELECT COUNT(*) as active FROM contexts WHERE ttl IS NULL OR ttl > ?", (now,))
                active = cur.fetchone()["active"]
                
                # Entries by namespace
                cur.execute(
                    "SELECT namespace, COUNT(*) as count FROM contexts WHERE ttl IS NULL OR ttl > ? GROUP BY namespace",
                    (now,)
                )
                by_namespace = {row["namespace"]: row["count"] for row in cur.fetchall()}
                
                return {
                    "total_entries": total,
                    "active_entries": active,
                    "expired_entries": total - active,
                    "cache_size": len(self._cache),
                    "namespaces": by_namespace,
                    "database_path": self.db_path,
                }


# Demo and testing
if __name__ == "__main__":
    print("🛡️ SIEM Context Manager Demo")
    
    # Remove demo database
    demo_db = "demo_siem_contexts.db"
    try:
        os.remove(demo_db)
    except:
        pass
    
    cm = SIEMContextManager(demo_db)
    
    # Demo user session
    cm.set_user_session("analyst_1", {
        "name": "Security Analyst",
        "last_query": "show failed logins",
        "active_investigations": ["inv_001", "inv_002"]
    })
    
    # Demo investigation
    cm.set_investigation("inv_001", {
        "title": "Suspicious Login Activity",
        "indicators": {
            "ip_addresses": ["192.168.1.100", "10.0.0.50"],
            "usernames": ["admin_temp", "backup_user"],
            "time_range": {"gte": "2024-10-03T10:00:00Z", "lte": "2024-10-03T12:00:00Z"}
        },
        "status": "active"
    })
    
    # Generate Elasticsearch query
    es_query = cm.build_elasticsearch_context_query("investigations", ["inv_001"])
    print("Generated ES Query:", json.dumps(es_query, indent=2))
    
    # Show stats
    stats = cm.get_stats()
    print("Context Manager Stats:", json.dumps(stats, indent=2))
    
    print("Demo complete!")