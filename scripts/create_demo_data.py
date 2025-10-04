"""
🚀 Quick Setup Script for SIEM NLP Assistant MVP
Creates synthetic demo data for immediate testing.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_timestamp(hours_ago=0, minutes_ago=0):
    """Generate timestamp in ISO format."""
    dt = datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)
    return dt.isoformat()


def generate_failed_login_logs(count=200):
    """Generate failed login attempt logs."""
    logs = []
    users = ['admin', 'root', 'user1', 'testuser', 'service_account', 'backup_admin']
    source_ips = ['192.168.1.100', '10.0.0.50', '172.16.0.25', '203.0.113.45', '198.51.100.78']
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 72), minutes_ago=random.randint(0, 59)),
            'event_type': 'authentication',
            'event_action': 'logon',
            'event_outcome': 'failure',
            'user_name': random.choice(users),
            'source_ip': random.choice(source_ips),
            'event_code': random.choice(['4625', '529', '530']),  # Windows failed login codes
            'logon_type': random.choice(['2', '3', '10']),  # Interactive, Network, RemoteInteractive
            'failure_reason': random.choice([
                'Unknown user name or bad password',
                'Account locked out',
                'Account disabled',
                'Password expired'
            ]),
            'host_name': f'workstation-{random.randint(1, 20)}',
            'severity': random.choice(['medium', 'high']),
            'dataset': 'windows_security',
            'message': 'Failed login attempt detected'
        }
        logs.append(log)
    
    return logs


def generate_successful_login_logs(count=150):
    """Generate successful login logs."""
    logs = []
    users = ['john.doe', 'jane.smith', 'admin', 'it_support', 'manager1']
    source_ips = ['192.168.1.50', '10.0.0.100', '172.16.0.10']
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 48), minutes_ago=random.randint(0, 59)),
            'event_type': 'authentication',
            'event_action': 'logon',
            'event_outcome': 'success',
            'user_name': random.choice(users),
            'source_ip': random.choice(source_ips),
            'event_code': '4624',  # Windows successful login
            'logon_type': random.choice(['2', '3', '10']),
            'host_name': f'workstation-{random.randint(1, 20)}',
            'severity': 'low',
            'dataset': 'windows_security',
            'message': 'Successful login'
        }
        logs.append(log)
    
    return logs


def generate_malware_alerts(count=50):
    """Generate malware detection alerts."""
    logs = []
    malware_types = ['trojan', 'ransomware', 'spyware', 'adware', 'rootkit']
    malware_names = ['TrojanDownloader.Win32', 'Ransom.Cryptolocker', 'Spyware.Agent', 'Adware.Generic']
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 24), minutes_ago=random.randint(0, 59)),
            'event_type': 'malware',
            'event_action': 'detection',
            'event_outcome': 'blocked',
            'malware_type': random.choice(malware_types),
            'malware_name': random.choice(malware_names),
            'file_path': f'C:\\Users\\user{random.randint(1, 10)}\\Downloads\\suspicious_file_{i}.exe',
            'process_name': random.choice(['chrome.exe', 'explorer.exe', 'svchost.exe']),
            'host_name': f'workstation-{random.randint(1, 20)}',
            'severity': random.choice(['high', 'critical']),
            'dataset': 'wazuh_alerts',
            'message': 'Malware detected and quarantined'
        }
        logs.append(log)
    
    return logs


def generate_network_activity(count=300):
    """Generate network activity logs."""
    logs = []
    protocols = ['tcp', 'udp', 'icmp']
    dest_ports = [80, 443, 22, 3389, 445, 3306, 5432, 8080]
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 12), minutes_ago=random.randint(0, 59)),
            'event_type': 'network',
            'event_action': 'connection',
            'event_outcome': random.choice(['allowed', 'blocked']),
            'source_ip': f'192.168.{random.randint(1, 10)}.{random.randint(1, 254)}',
            'dest_ip': f'10.0.{random.randint(1, 10)}.{random.randint(1, 254)}',
            'source_port': random.randint(1024, 65535),
            'dest_port': random.choice(dest_ports),
            'protocol': random.choice(protocols),
            'bytes_sent': random.randint(100, 10000),
            'bytes_received': random.randint(100, 10000),
            'host_name': f'firewall-{random.randint(1, 3)}',
            'severity': random.choice(['low', 'medium']),
            'dataset': 'network_logs',
            'message': 'Network connection logged'
        }
        logs.append(log)
    
    return logs


def generate_security_alerts(count=75):
    """Generate generic security alerts."""
    logs = []
    alert_types = ['intrusion_attempt', 'privilege_escalation', 'suspicious_process', 'data_exfiltration']
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 24), minutes_ago=random.randint(0, 59)),
            'event_type': 'security_alert',
            'event_action': random.choice(alert_types),
            'event_outcome': 'detected',
            'alert_severity': random.choice(['low', 'medium', 'high', 'critical']),
            'rule_name': f'Security Rule {random.randint(1000, 9999)}',
            'source_ip': f'192.168.{random.randint(1, 10)}.{random.randint(1, 254)}',
            'user_name': random.choice(['admin', 'user1', 'service_account', 'unknown']),
            'host_name': f'server-{random.randint(1, 10)}',
            'severity': random.choice(['medium', 'high', 'critical']),
            'dataset': 'security_alerts',
            'message': 'Security alert triggered'
        }
        logs.append(log)
    
    return logs


def generate_system_errors(count=100):
    """Generate system error logs."""
    logs = []
    error_types = ['application_crash', 'service_failure', 'disk_error', 'memory_error']
    services = ['SQL Server', 'IIS', 'Apache', 'nginx', 'Docker', 'Windows Update']
    
    for i in range(count):
        log = {
            '@timestamp': generate_timestamp(hours_ago=random.randint(0, 48), minutes_ago=random.randint(0, 59)),
            'event_type': 'system_error',
            'event_action': random.choice(error_types),
            'event_outcome': 'failure',
            'error_code': f'0x{random.randint(1000, 9999):04X}',
            'service_name': random.choice(services),
            'host_name': f'server-{random.randint(1, 10)}',
            'severity': random.choice(['medium', 'high']),
            'dataset': 'system_logs',
            'message': f'System error occurred: {random.choice(error_types)}'
        }
        logs.append(log)
    
    return logs


def create_demo_dataset(output_dir='datasets/synthetic'):
    """Create complete demo dataset."""
    logger.info("🎨 Generating synthetic demo data...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate all log types
    all_logs = []
    
    logger.info("  📝 Generating failed login logs...")
    all_logs.extend(generate_failed_login_logs(200))
    
    logger.info("  ✅ Generating successful login logs...")
    all_logs.extend(generate_successful_login_logs(150))
    
    logger.info("  🦠 Generating malware alerts...")
    all_logs.extend(generate_malware_alerts(50))
    
    logger.info("  🌐 Generating network activity...")
    all_logs.extend(generate_network_activity(300))
    
    logger.info("  🚨 Generating security alerts...")
    all_logs.extend(generate_security_alerts(75))
    
    logger.info("  ⚠️ Generating system errors...")
    all_logs.extend(generate_system_errors(100))
    
    # Sort by timestamp
    all_logs.sort(key=lambda x: x['@timestamp'])
    
    # Save to file
    output_file = output_path / 'demo_security_logs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        for log in all_logs:
            f.write(json.dumps(log) + '\n')
    
    logger.info(f"✅ Generated {len(all_logs)} demo logs")
    logger.info(f"📁 Saved to: {output_file}")
    
    # Save summary
    summary = {
        'total_logs': len(all_logs),
        'failed_logins': 200,
        'successful_logins': 150,
        'malware_alerts': 50,
        'network_logs': 300,
        'security_alerts': 75,
        'system_errors': 100,
        'time_range': {
            'start': all_logs[0]['@timestamp'],
            'end': all_logs[-1]['@timestamp']
        }
    }
    
    summary_file = output_path / 'summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"📊 Summary saved to: {summary_file}")
    
    return output_file, len(all_logs)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 SIEM NLP Assistant - Demo Data Generator")
    logger.info("=" * 60)
    
    output_file, count = create_demo_dataset()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Demo data generation complete!")
    logger.info(f"📁 File: {output_file}")
    logger.info(f"📊 Total logs: {count}")
    logger.info("\n📌 Next steps:")
    logger.info("  1. Start Elasticsearch: docker-compose -f docker/docker-compose.yml up -d elasticsearch")
    logger.info("  2. Ingest data: python scripts/quick_ingest.py")
    logger.info("  3. Start app: python app.py")
    logger.info("=" * 60)
