"""
⚡ Quick Ingest Script - Load demo data into Elasticsearch
Simplified version for MVP setup.
"""

import json
import sys
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_elasticsearch(es, max_retries=30):
    """Wait for Elasticsearch to be ready."""
    logger.info("⏳ Waiting for Elasticsearch to be ready...")
    
    for i in range(max_retries):
        try:
            info = es.info()
            logger.info(f"✅ Elasticsearch is ready! Version: {info['version']['number']}")
            return True
        except Exception as e:
            if i < max_retries - 1:
                logger.info(f"  Attempt {i+1}/{max_retries}: Not ready yet, waiting...")
                time.sleep(2)
            else:
                logger.error(f"❌ Elasticsearch not ready after {max_retries} attempts")
                return False
    
    return False


def ingest_data(input_file='datasets/synthetic/demo_security_logs.json', 
                index_name='security-logs-demo'):
    """Ingest data into Elasticsearch."""
    
    try:
        from elasticsearch import Elasticsearch
        from elasticsearch.helpers import bulk
    except ImportError:
        logger.error("❌ Elasticsearch library not installed")
        logger.info("   Run: pip install elasticsearch==8.15.1")
        return False
    
    # Check if input file exists
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_file}")
        logger.info("   Run: python scripts/create_demo_data.py first")
        return False
    
    # Connect to Elasticsearch
    logger.info("🔌 Connecting to Elasticsearch...")
    try:
        es = Elasticsearch(
            ['http://localhost:9200'],
            request_timeout=30
        )
    except Exception as e:
        logger.error(f"❌ Failed to connect to Elasticsearch: {e}")
        logger.info("   Make sure Elasticsearch is running:")
        logger.info("   docker-compose -f docker/docker-compose.yml up -d elasticsearch")
        return False
    
    # Wait for Elasticsearch to be ready
    if not wait_for_elasticsearch(es):
        return False
    
    # Read logs
    logger.info(f"📖 Reading logs from {input_file}...")
    logs = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    logger.info(f"📊 Found {len(logs)} logs to ingest")
    
    # Create index with mapping
    logger.info(f"🔧 Creating index: {index_name}")
    mapping = {
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "event_type": {"type": "keyword"},
                "event_action": {"type": "keyword"},
                "event_outcome": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "user_name": {"type": "keyword"},
                "source_ip": {"type": "ip"},
                "dest_ip": {"type": "ip"},
                "host_name": {"type": "keyword"},
                "dataset": {"type": "keyword"},
                "message": {"type": "text"}
            }
        }
    }
    
    try:
        # Delete index if exists
        if es.indices.exists(index=index_name):
            logger.info(f"  Deleting existing index: {index_name}")
            es.indices.delete(index=index_name)
        
        # Create new index
        es.indices.create(index=index_name, body=mapping)
        logger.info(f"✅ Index created: {index_name}")
    except Exception as e:
        logger.warning(f"⚠️ Index creation warning: {e}")
    
    # Prepare bulk actions
    logger.info("📦 Preparing bulk actions...")
    actions = []
    for log in logs:
        action = {
            "_index": index_name,
            "_source": log
        }
        actions.append(action)
    
    # Bulk ingest
    logger.info(f"⬆️ Ingesting {len(actions)} documents...")
    try:
        success, failed = bulk(es, actions, stats_only=True)
        logger.info(f"✅ Successfully ingested: {success} documents")
        
        if failed:
            logger.warning(f"⚠️ Failed to ingest: {failed} documents")
        
        # Refresh index
        es.indices.refresh(index=index_name)
        
        # Verify count
        time.sleep(1)
        count = es.count(index=index_name)['count']
        logger.info(f"✅ Verified document count: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Bulk ingest failed: {e}")
        return False


def verify_data(index_name='security-logs-demo'):
    """Verify ingested data with sample queries."""
    
    try:
        from elasticsearch import Elasticsearch
    except ImportError:
        return
    
    logger.info("\n🔍 Verifying data with sample queries...")
    
    es = Elasticsearch(['http://localhost:9200'])
    
    # Test queries
    queries = [
        {
            "name": "Failed logins",
            "query": {"match": {"event_outcome": "failure"}}
        },
        {
            "name": "Malware alerts",
            "query": {"match": {"event_type": "malware"}}
        },
        {
            "name": "Critical severity",
            "query": {"match": {"severity": "critical"}}
        }
    ]
    
    for q in queries:
        try:
            result = es.search(
                index=index_name,
                body={"query": q["query"], "size": 0}
            )
            count = result['hits']['total']['value']
            logger.info(f"  ✅ {q['name']}: {count} results")
        except Exception as e:
            logger.warning(f"  ⚠️ {q['name']}: Query failed - {e}")


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("⚡ SIEM NLP Assistant - Quick Data Ingestion")
    logger.info("=" * 60)
    
    # Ingest data
    success = ingest_data()
    
    if success:
        # Verify
        verify_data()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Data ingestion complete!")
        logger.info("\n📌 Next steps:")
        logger.info("  1. Start app: python app.py")
        logger.info("  2. Open UI: http://localhost:8501")
        logger.info("  3. Try query: 'Show failed login attempts'")
        logger.info("=" * 60)
    else:
        logger.error("\n❌ Data ingestion failed!")
        logger.info("\nTroubleshooting:")
        logger.info("  1. Is Elasticsearch running? docker ps")
        logger.info("  2. Is data generated? ls datasets/synthetic/")
        logger.info("  3. Check logs above for specific errors")
        sys.exit(1)
