"""
Script to ingest security logs into Elasticsearch or vector database.
"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_to_elasticsearch(logs: List[Dict[str, Any]], index_name: str):
    """Ingest logs to Elasticsearch."""
    try:
        from elasticsearch import Elasticsearch
        from elasticsearch.helpers import bulk
        
        # Initialize Elasticsearch client
        es = Elasticsearch([{
            'host': os.getenv('ELASTICSEARCH_HOST', 'localhost'),
            'port': int(os.getenv('ELASTICSEARCH_PORT', 9200))
        }])
        
        # Prepare documents for bulk indexing
        docs = []
        for log in logs:
            doc = {
                '_index': index_name,
                '_source': log
            }
            docs.append(doc)
        
        # Bulk index documents
        success, failed = bulk(es, docs)
        logger.info(f"Successfully indexed {success} documents")
        
        if failed:
            logger.warning(f"Failed to index {len(failed)} documents")
        
    except Exception as e:
        logger.error(f"Failed to ingest to Elasticsearch: {e}")


def process_log_file(file_path: str) -> List[Dict[str, Any]]:
    """Process a log file and extract structured data."""
    logs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Try to parse as JSON first
                    log_entry = json.loads(line)
                except json.JSONDecodeError:
                    # If not JSON, create a simple log entry
                    log_entry = {
                        '@timestamp': datetime.now().isoformat(),
                        'message': line,
                        'source_file': os.path.basename(file_path),
                        'line_number': line_num
                    }
                
                # Ensure timestamp exists
                if '@timestamp' not in log_entry:
                    log_entry['@timestamp'] = datetime.now().isoformat()
                
                logs.append(log_entry)
                
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
    
    return logs


def ingest_directory(directory_path: str, pattern: str = "*.log"):
    """Ingest all log files from a directory."""
    import glob
    
    log_files = glob.glob(os.path.join(directory_path, pattern))
    total_logs = 0
    
    for file_path in log_files:
        logger.info(f"Processing file: {file_path}")
        logs = process_log_file(file_path)
        
        if logs:
            index_name = f"security-logs-{datetime.now().strftime('%Y-%m')}"
            ingest_to_elasticsearch(logs, index_name)
            total_logs += len(logs)
    
    logger.info(f"Total logs ingested: {total_logs}")


def create_sample_logs(output_file: str, count: int = 100):
    """Create sample security logs for testing."""
    import random
    
    sample_events = [
        "Failed login attempt",
        "Successful authentication",
        "Suspicious network activity",
        "Malware detected",
        "Firewall rule triggered",
        "User privilege escalation",
        "Unusual file access",
        "Port scan detected"
    ]
    
    severity_levels = ["low", "medium", "high", "critical"]
    source_ips = ["192.168.1.100", "10.0.0.50", "172.16.1.200", "203.0.113.10"]
    users = ["admin", "user1", "service_account", "guest"]
    
    logs = []
    
    for i in range(count):
        log_entry = {
            '@timestamp': (datetime.now() - 
                          timedelta(minutes=random.randint(0, 1440))).isoformat(),
            'message': random.choice(sample_events),
            'severity': random.choice(severity_levels),
            'source_ip': random.choice(source_ips),
            'user': random.choice(users),
            'event_id': f"EVT-{i+1:04d}",
            'source': 'sample_generator'
        }
        logs.append(log_entry)
    
    with open(output_file, 'w') as f:
        for log in logs:
            f.write(json.dumps(log) + '\n')
    
    logger.info(f"Created {count} sample logs in {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Ingest security logs')
    parser.add_argument('--action', choices=['ingest', 'generate'], required=True,
                       help='Action to perform')
    parser.add_argument('--source', help='Source file or directory')
    parser.add_argument('--output', help='Output file for generated logs')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of sample logs to generate')
    parser.add_argument('--index', default='security-logs',
                       help='Elasticsearch index name')
    
    args = parser.parse_args()
    
    if args.action == 'generate':
        if not args.output:
            args.output = 'sample_logs.jsonl'
        create_sample_logs(args.output, args.count)
    
    elif args.action == 'ingest':
        if not args.source:
            logger.error("Source file or directory required for ingestion")
            return
        
        if os.path.isfile(args.source):
            logs = process_log_file(args.source)
            ingest_to_elasticsearch(logs, args.index)
        elif os.path.isdir(args.source):
            ingest_directory(args.source)
        else:
            logger.error(f"Source path does not exist: {args.source}")


if __name__ == "__main__":
    from datetime import timedelta
    main()