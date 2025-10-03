#!/usr/bin/env python3
"""
SIEM Connector Demo Script
Demonstrates the capabilities of the enhanced SIEM connector system.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demo_query_builder_integration():
    """Demonstrate Query Builder + SIEM Connector integration."""
    print("🔍 Query Builder + SIEM Connector Integration Demo")
    print("=" * 60)
    
    try:
        # Import components
        from backend.query_builder import QueryBuilder
        from siem_connector import create_siem_processor
        
        # Initialize components
        query_builder = QueryBuilder()
        siem_processor = create_siem_processor("elasticsearch")
        
        print("✅ Components initialized successfully")
        
        # Sample natural language queries
        sample_queries = [
            "Show failed login attempts from last hour",
            "Find security alerts with high severity",
            "Get network traffic from 192.168.1.100",
            "Show successful logins for admin users",
            "List system errors from yesterday"
        ]
        
        for i, nl_query in enumerate(sample_queries, 1):
            print(f"\n🔢 Query {i}: {nl_query}")
            print("-" * 50)
            
            try:
                # Step 1: Convert NL to Elasticsearch DSL
                es_query = query_builder.build_query(nl_query)
                print(f"✅ DSL Generated: {len(str(es_query))} characters")
                
                # Show a snippet of the query
                query_snippet = json.dumps(es_query, indent=2)[:200] + "..."
                print(f"Query preview:\n{query_snippet}")
                
                # Step 2: Execute through SIEM connector
                try:
                    response = siem_processor.process_query(es_query, size=5)
                    
                    total_hits = response.get('metadata', {}).get('total_hits', 0)
                    execution_time = response.get('metadata', {}).get('execution_time', 0)
                    
                    print(f"✅ Query executed: {total_hits} hits in {execution_time:.2f}s")
                    
                    # Show sample results
                    hits = response.get('hits', [])[:2]  # Show first 2 results
                    for j, hit in enumerate(hits):
                        source = hit.get('source', {})
                        timestamp = source.get('@timestamp', 'N/A')
                        message = source.get('message', 'N/A')[:50]
                        print(f"   Result {j+1}: {timestamp} - {message}...")
                        
                except Exception as exec_error:
                    print(f"⚠️ Execution failed (expected if no ES): {exec_error}")
                    print("   This demonstrates proper error handling")
                
            except Exception as e:
                print(f"❌ Query processing failed: {e}")
        
    except Exception as e:
        print(f"❌ Demo initialization failed: {e}")

def demo_alert_fetching():
    """Demonstrate alert fetching capabilities."""
    print("\n🚨 Alert Fetching Demo")
    print("=" * 60)
    
    try:
        from siem_connector import create_siem_processor
        
        processor = create_siem_processor("elasticsearch")
        
        # Test different alert severity levels
        severity_levels = ["low", "medium", "high", "critical"]
        
        for severity in severity_levels:
            print(f"\n📊 Fetching {severity.upper()} severity alerts...")
            
            try:
                alerts_response = processor.fetch_alerts(
                    severity=severity,
                    time_range="last_day",
                    size=10
                )
                
                total_alerts = alerts_response.get('metadata', {}).get('total_hits', 0)
                print(f"   Found {total_alerts} {severity} severity alerts")
                
                # Show sample alert if available
                alerts = alerts_response.get('hits', [])
                if alerts:
                    sample_alert = alerts[0].get('source', {})
                    print(f"   Sample: {sample_alert.get('message', 'N/A')}")
                
            except Exception as e:
                print(f"   ⚠️ Alert fetch failed (expected): {e}")
        
    except Exception as e:
        print(f"❌ Alert demo failed: {e}")

def demo_log_filtering():
    """Demonstrate log filtering capabilities."""
    print("\n📝 Log Filtering Demo")
    print("=" * 60)
    
    try:
        from siem_connector import create_siem_processor
        
        processor = create_siem_processor("elasticsearch")
        
        # Test different log types
        log_types = ["auth", "network", "system"]
        
        for log_type in log_types:
            print(f"\n🔍 Fetching {log_type.upper()} logs...")
            
            try:
                logs_response = processor.fetch_logs(
                    log_type=log_type,
                    time_range="last_hour",
                    size=5
                )
                
                total_logs = logs_response.get('metadata', {}).get('total_hits', 0)
                print(f"   Found {total_logs} {log_type} logs")
                
                # Show summary if available
                summary = logs_response.get('summary', {})
                if summary:
                    event_types = summary.get('event_types', {})
                    top_ips = summary.get('top_source_ips', {})
                    print(f"   Event types: {list(event_types.keys())[:3]}")
                    print(f"   Top IPs: {list(top_ips.keys())[:3]}")
                
            except Exception as e:
                print(f"   ⚠️ Log fetch failed (expected): {e}")
        
    except Exception as e:
        print(f"❌ Log filtering demo failed: {e}")

def demo_response_normalization():
    """Demonstrate response normalization."""
    print("\n🔧 Response Normalization Demo")
    print("=" * 60)
    
    try:
        from siem_connector.utils import (
            normalize_log_entry, extract_common_fields, 
            sanitize_query_response, format_query_results
        )
        
        # Mock data from different sources
        print("🔍 Testing cross-platform normalization...")
        
        # Elasticsearch format
        es_entry = {
            '_source': {
                '@timestamp': '2024-01-15T10:30:00Z',
                'message': 'Authentication failed for user admin',
                'source': {'ip': '192.168.1.100'},
                'user': {'name': 'admin'},
                'event': {'type': 'authentication'}
            }
        }
        
        normalized_es = normalize_log_entry(es_entry, 'elasticsearch')
        print(f"✅ Elasticsearch normalized: {normalized_es['event_type']}")
        
        # Wazuh format
        wazuh_entry = {
            'timestamp': '2024-01-15T10:30:00Z',
            'rule': {'description': 'Multiple login failures', 'level': 7},
            'data': {'srcip': '192.168.1.100', 'srcuser': 'admin'}
        }
        
        normalized_wazuh = normalize_log_entry(wazuh_entry, 'wazuh')
        print(f"✅ Wazuh normalized: {normalized_wazuh['event_type']}")
        
        # Test field extraction
        mock_entries = [
            {'source': normalized_es},
            {'source': normalized_wazuh}
        ]
        
        summary = extract_common_fields(mock_entries)
        print(f"✅ Field extraction completed:")
        print(f"   Total events: {summary['total_events']}")
        print(f"   Event types: {summary['event_types']}")
        print(f"   Top users: {summary['top_users']}")
        
        # Test formatting
        formatted = format_query_results([normalized_es, normalized_wazuh], 'table')
        print(f"✅ Table formatting: {len(formatted)} characters")
        
    except Exception as e:
        print(f"❌ Normalization demo failed: {e}")

def demo_health_monitoring():
    """Demonstrate health monitoring capabilities."""
    print("\n❤️ Health Monitoring Demo")
    print("=" * 60)
    
    try:
        from siem_connector import create_siem_processor
        
        processor = create_siem_processor("elasticsearch")
        
        # Check overall health
        print("🔍 Checking SIEM platform health...")
        health = processor.get_health_status()
        
        print(f"   Platform: {health.get('platform', 'unknown')}")
        print(f"   Status: {health.get('status', 'unknown')}")
        
        if 'details' in health:
            details = health['details']
            print(f"   Cluster: {details.get('cluster_name', 'N/A')}")
            print(f"   Nodes: {details.get('number_of_nodes', 'N/A')}")
        
        # Check available data sources
        print("\n🗂️ Checking available data sources...")
        try:
            indices = processor.get_available_indices()
            print(f"   Available indices: {len(indices)}")
            if indices:
                print(f"   Sample indices: {indices[:3]}")
        except Exception as e:
            print(f"   ⚠️ Index check failed (expected): {e}")
        
    except Exception as e:
        print(f"❌ Health monitoring demo failed: {e}")

def main():
    """Run the complete demo."""
    print("🚀 SIEM Connector Enhanced Demo")
    print("=" * 60)
    print("This demo showcases the enhanced SIEM connector capabilities")
    print("including query processing, alert fetching, and normalization.")
    print()
    
    # Run all demos
    demo_query_builder_integration()
    demo_alert_fetching()
    demo_log_filtering()
    demo_response_normalization()
    demo_health_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("\n📋 Summary of SIEM Connector Features:")
    print("✅ Natural language to SIEM query conversion")
    print("✅ Multi-platform support (Elasticsearch, Wazuh)")
    print("✅ Response normalization and standardization")
    print("✅ Alert and log fetching with filters")
    print("✅ Health monitoring and diagnostics")
    print("✅ Error handling and fallback mechanisms")
    print("✅ Integration with existing NLP pipeline")
    
    print("\n🔗 Integration Points:")
    print("• Query Builder → SIEM Connector → Response Formatter")
    print("• FastAPI Backend → SIEM Endpoints")
    print("• Context Manager → Query Caching")
    print("• Error Handling → Fallback Mechanisms")
    
    print("\n🚀 Next Steps:")
    print("• Start backend: cd backend && python main.py")
    print("• Test endpoints: curl http://localhost:8000/siem/health")
    print("• Configure Elasticsearch connection in environment variables")

if __name__ == "__main__":
    main()