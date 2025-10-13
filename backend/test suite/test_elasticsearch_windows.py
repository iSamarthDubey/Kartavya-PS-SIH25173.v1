#!/usr/bin/env python3
"""
Test script to verify Elasticsearch connection and Windows Beats data
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from src.connectors.elastic import ElasticConnector
from src.core.nlp.intent_classifier import IntentClassifier, QueryIntent
from src.core.nlp.windows_query_builder import WindowsQueryBuilder
from src.core.nlp.entity_extractor import EntityExtractor

async def test_elasticsearch_connection():
    """Test basic Elasticsearch connection and check for Windows data."""
    print("🔍 Testing Elasticsearch Connection...")
    
    # Initialize connector
    connector = ElasticConnector()
    
    # Test connection
    if not connector.is_available():
        print("❌ Elasticsearch connection failed!")
        print("   Make sure Elasticsearch is running on localhost:9200")
        return False
    
    print("✅ Elasticsearch connection successful!")
    
    # Get cluster health
    health = connector.get_cluster_health()
    print(f"   Cluster Status: {health.get('status', 'unknown')}")
    print(f"   Nodes: {health.get('number_of_nodes', 0)}")
    
    # Check for indices
    indices = connector.get_indices()
    print(f"   Available indices: {len(indices)}")
    
    winlogbeat_indices = [idx for idx in indices if 'winlogbeat' in idx]
    metricbeat_indices = [idx for idx in indices if 'metricbeat' in idx]
    
    print(f"   Winlogbeat indices: {len(winlogbeat_indices)}")
    print(f"   Metricbeat indices: {len(metricbeat_indices)}")
    
    if winlogbeat_indices:
        print(f"   Latest winlogbeat: {sorted(winlogbeat_indices)[-1]}")
    if metricbeat_indices:
        print(f"   Latest metricbeat: {sorted(metricbeat_indices)[-1]}")
    
    return True

async def test_windows_security_queries():
    """Test Windows security event queries."""
    print("\n🔍 Testing Windows Security Queries...")
    
    connector = ElasticConnector()
    if not connector.is_available():
        print("❌ Elasticsearch not available for queries!")
        return
    
    # Test 1: Query failed logins
    print("\n1. Testing failed login query...")
    try:
        failed_logins = await connector.query_failed_logins("24h", 10)
        total_hits = failed_logins.get('metadata', {}).get('total_hits', 0)
        print(f"   Found {total_hits} failed login events in last 24h")
        
        if failed_logins.get('hits'):
            sample = failed_logins['hits'][0]
            print(f"   Sample event: {sample.get('message', 'No message')}")
            print(f"   User: {sample.get('user', {}).get('name', 'Unknown')}")
            print(f"   Time: {sample.get('@timestamp', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Failed login query failed: {e}")
    
    # Test 2: Query successful logins
    print("\n2. Testing successful login query...")
    try:
        successful_logins = await connector.query_successful_logins("24h", 10)
        total_hits = successful_logins.get('metadata', {}).get('total_hits', 0)
        print(f"   Found {total_hits} successful login events in last 24h")
        
        if successful_logins.get('hits'):
            sample = successful_logins['hits'][0]
            print(f"   Sample event: {sample.get('message', 'No message')}")
            print(f"   User: {sample.get('user', {}).get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"   ❌ Successful login query failed: {e}")
    
    # Test 3: Query system metrics
    print("\n3. Testing system metrics query...")
    try:
        metrics = await connector.query_system_metrics("1h", 5)
        total_hits = metrics.get('metadata', {}).get('total_hits', 0)
        print(f"   Found {total_hits} system metric events in last hour")
        
        if metrics.get('hits'):
            sample = metrics['hits'][0]
            raw_data = sample.get('raw', {})
            cpu_pct = raw_data.get('system', {}).get('cpu', {}).get('total', {}).get('pct')
            memory_pct = raw_data.get('system', {}).get('memory', {}).get('used', {}).get('pct')
            
            if cpu_pct is not None:
                print(f"   Sample CPU usage: {cpu_pct * 100:.1f}%")
            if memory_pct is not None:
                print(f"   Sample Memory usage: {memory_pct * 100:.1f}%")
            
    except Exception as e:
        print(f"   ❌ System metrics query failed: {e}")

async def test_natural_language_queries():
    """Test full natural language query pipeline."""
    print("\n🧠 Testing Natural Language Query Pipeline...")
    
    # Initialize components
    classifier = IntentClassifier()
    extractor = EntityExtractor()
    query_builder = WindowsQueryBuilder()
    connector = ElasticConnector()
    
    test_queries = [
        "Show me failed login attempts from the last hour",
        "Find successful logins for user Administrator",
        "What are the system CPU metrics today?",
        "Show me process creation events",
        "Find any suspicious user activity"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        try:
            # Classify intent
            intent, confidence = classifier.classify_intent(query)
            print(f"   Intent: {intent.value} (confidence: {confidence:.2f})")
            
            # Extract entities
            entities = await extractor.extract_entities(query)
            print(f"   Entities: {[e['value'] for e in entities]}")
            
            # Build query
            es_query = query_builder.build_query(intent, entities, query)
            print(f"   Generated Elasticsearch DSL query (size: {len(str(es_query))} chars)")
            
            # Execute query (if we have connection)
            if connector.is_available():
                # Use the appropriate connector method based on intent
                if intent == QueryIntent.SHOW_FAILED_LOGINS:
                    result = await connector.query_failed_logins("1h", 5)
                elif intent == QueryIntent.SHOW_SUCCESSFUL_LOGINS:
                    result = await connector.query_successful_logins("1h", 5)
                elif intent == QueryIntent.GET_SYSTEM_METRICS:
                    result = await connector.query_system_metrics("1h", 5)
                else:
                    # Use general Windows query
                    result = await connector.query_windows_security_events(
                        {"time_range": {"gte": "now-1h", "lte": "now"}}, 5
                    )
                
                total_hits = result.get('metadata', {}).get('total_hits', 0)
                print(f"   Results: {total_hits} events found")
                
                if result.get('hits'):
                    sample = result['hits'][0]
                    print(f"   Sample: {sample.get('message', 'No message')[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")

async def test_dashboard_aggregations():
    """Test dashboard aggregation queries."""
    print("\n📊 Testing Dashboard Aggregations...")
    
    connector = ElasticConnector()
    query_builder = WindowsQueryBuilder()
    
    if not connector.is_available():
        print("❌ Elasticsearch not available for aggregations!")
        return
    
    # Test failed logins aggregation
    print("\n1. Testing failed logins aggregation...")
    try:
        agg_query = query_builder.build_aggregation_query(
            QueryIntent.SHOW_FAILED_LOGINS, [], "24h"
        )
        
        # Execute aggregation query directly
        result = connector.send_query_to_elastic(agg_query, size=0)
        
        aggregations = result.get('aggregations', {})
        if aggregations:
            print("   ✅ Aggregation query successful!")
            
            # Check time series data
            time_series = aggregations.get('failed_logins_over_time', {}).get('buckets', [])
            print(f"   Time series buckets: {len(time_series)}")
            
            # Check top IPs
            top_ips = aggregations.get('top_source_ips', {}).get('buckets', [])
            print(f"   Top source IPs: {len(top_ips)}")
            if top_ips:
                print(f"   Most common IP: {top_ips[0].get('key', 'Unknown')} ({top_ips[0].get('doc_count', 0)} events)")
        else:
            print("   No aggregation data returned")
            
    except Exception as e:
        print(f"   ❌ Aggregation query failed: {e}")

def print_elasticsearch_sample_query():
    """Print sample Elasticsearch query to show what we're generating."""
    print("\n📝 Sample Generated Elasticsearch Query:")
    print("   Query: 'Show me failed login attempts from the last hour'")
    
    query_builder = WindowsQueryBuilder()
    classifier = IntentClassifier()
    
    intent, _ = classifier.classify_intent("Show me failed login attempts from the last hour")
    sample_query = query_builder.build_query(intent, [], "Show me failed login attempts from the last hour")
    
    print(json.dumps(sample_query, indent=2))

async def main():
    """Main test function."""
    print("SYNRGY - Windows Elasticsearch Integration Test")
    print("=" * 55)
    
    # Test 1: Basic connection
    if not await test_elasticsearch_connection():
        return
    
    # Test 2: Windows security queries
    await test_windows_security_queries()
    
    # Test 3: Natural language processing
    await test_natural_language_queries()
    
    # Test 4: Dashboard aggregations
    await test_dashboard_aggregations()
    
    # Show sample query
    print_elasticsearch_sample_query()
    
    print("\n✅ All tests completed!")
    print("\n🎯 Ready to test SYNRGY with your Windows logs!")
    print("   Start the backend with: python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8001 --reload")

if __name__ == "__main__":
    asyncio.run(main())
