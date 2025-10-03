"""
Utility functions for NLP processing.
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def clean_query(query: str) -> str:
    """Clean and normalize user query."""
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove special characters that might interfere with parsing
    query = re.sub(r'[^\w\s\-.:@/]', ' ', query)
    
    # Normalize common abbreviations
    abbreviations = {
        'src': 'source',
        'dst': 'destination',
        'dest': 'destination',
        'ip': 'ip address',
        'usr': 'user',
        'pwd': 'password',
        'auth': 'authentication',
        'conn': 'connection',
        'req': 'request',
        'resp': 'response'
    }
    
    words = query.split()
    normalized_words = []
    
    for word in words:
        lower_word = word.lower()
        if lower_word in abbreviations:
            normalized_words.append(abbreviations[lower_word])
        else:
            normalized_words.append(word)
    
    return ' '.join(normalized_words)


def extract_keywords(query: str) -> List[str]:
    """Extract relevant keywords from query."""
    # Security-related keywords
    security_keywords = [
        'attack', 'malware', 'virus', 'threat', 'intrusion', 'breach',
        'unauthorized', 'suspicious', 'anomaly', 'alert', 'warning',
        'failed', 'denied', 'blocked', 'rejected', 'error',
        'login', 'logout', 'authentication', 'authorization',
        'firewall', 'antivirus', 'ids', 'ips', 'siem',
        'network', 'traffic', 'connection', 'session',
        'user', 'admin', 'administrator', 'root',
        'critical', 'high', 'medium', 'low', 'severity'
    ]
    
    words = query.lower().split()
    keywords = []
    
    for word in words:
        # Remove punctuation
        clean_word = re.sub(r'[^\w]', '', word)
        
        # Add if it's a security keyword or looks important
        if (clean_word in security_keywords or 
            len(clean_word) > 3 or
            re.match(r'\d+\.\d+\.\d+\.\d+', word) or  # IP address
            re.match(r'[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', word)):  # Email
            keywords.append(clean_word)
    
    return list(set(keywords))


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format."""
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def validate_domain(domain: str) -> bool:
    """Validate domain name format."""
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, domain))


def extract_iocs(text: str) -> Dict[str, List[str]]:
    """Extract Indicators of Compromise (IoCs) from text."""
    iocs = {
        'ip_addresses': [],
        'domains': [],
        'emails': [],
        'urls': [],
        'file_hashes': []
    }
    
    # IP addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = re.findall(ip_pattern, text)
    iocs['ip_addresses'] = [ip for ip in ips if validate_ip_address(ip)]
    
    # Domains
    domain_pattern = r'\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+\b'
    domains = re.findall(domain_pattern, text)
    iocs['domains'] = [domain for domain in domains if validate_domain(domain)]
    
    # Emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    iocs['emails'] = re.findall(email_pattern, text)
    
    # URLs
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+\.[a-zA-Z]{2,}'
    iocs['urls'] = re.findall(url_pattern, text)
    
    # File hashes (MD5, SHA1, SHA256)
    hash_patterns = [
        r'\b[a-fA-F0-9]{32}\b',  # MD5
        r'\b[a-fA-F0-9]{40}\b',  # SHA1
        r'\b[a-fA-F0-9]{64}\b'   # SHA256
    ]
    
    for pattern in hash_patterns:
        hashes = re.findall(pattern, text)
        iocs['file_hashes'].extend(hashes)
    
    # Remove duplicates
    for key in iocs:
        iocs[key] = list(set(iocs[key]))
    
    return iocs


def similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0