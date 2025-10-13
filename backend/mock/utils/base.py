"""
Base Classes and Utilities for Dynamic Mock Data Generation
"""

import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import hashlib
import socket
import threading
from dataclasses import dataclass
from enum import Enum


class MockDataType(Enum):
    """Types of mock data we can generate"""
    WINDOWS_EVENT = "windows_event"
    NETWORK_LOG = "network_log"
    SYSTEM_METRIC = "system_metric" 
    AUTHENTICATION = "authentication"
    SECURITY_ALERT = "security_alert"
    PROCESS_LOG = "process_log"
    FILE_ACCESS = "file_access"
    AUDITBEAT_EVENT = "auditbeat_event"
    PACKETBEAT_EVENT = "packetbeat_event"
    FILEBEAT_EVENT = "filebeat_event"


class SeverityLevel(Enum):
    """Security event severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MockEvent:
    """Base structure for a mock security event"""
    id: str
    timestamp: datetime
    event_type: MockDataType
    severity: SeverityLevel
    source: str
    data: Dict[str, Any]
    

class BaseMockGenerator(ABC):
    """
    Abstract base class for all mock data generators.
    Provides common functionality for realistic data generation.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or int(time.time())
        random.seed(self.seed)
        self._last_generated = datetime.now()
        self._generation_count = 0
        self._lock = threading.Lock()
        
    @abstractmethod
    def generate_event(self) -> MockEvent:
        """Generate a single mock event"""
        pass
    
    @abstractmethod
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of mock events"""
        pass
    
    def _get_realistic_timestamp(self, variance_seconds: int = 300) -> datetime:
        """Generate a realistic timestamp with some variance"""
        base_time = datetime.now()
        variance = random.randint(-variance_seconds, variance_seconds)
        return base_time + timedelta(seconds=variance)
    
    def _generate_id(self) -> str:
        """Generate a unique event ID"""
        with self._lock:
            self._generation_count += 1
            unique_string = f"{self.seed}-{self._generation_count}-{time.time()}"
            return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _generate_uuid(self) -> str:
        """Generate a standard UUID"""
        return str(uuid.uuid4())
    
    def _get_random_ip(self, private: bool = True) -> str:
        """Generate a random IP address"""
        if private:
            # Generate private IP ranges
            ranges = [
                "192.168.{}.{}",
                "10.{}.{}.{}",
                "172.{}.{}.{}"
            ]
            range_choice = random.choice(ranges)
            if "192.168" in range_choice:
                return range_choice.format(
                    random.randint(0, 255),
                    random.randint(1, 254)
                )
            elif "10." in range_choice:
                return range_choice.format(
                    random.randint(0, 255),
                    random.randint(0, 255), 
                    random.randint(1, 254)
                )
            else:  # 172.x range
                return range_choice.format(
                    random.randint(16, 31),
                    random.randint(0, 255),
                    random.randint(1, 254)
                )
        else:
            # Generate public IP
            return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def _get_random_hostname(self) -> str:
        """Generate a realistic hostname"""
        prefixes = ["WIN", "SRV", "WKS", "DC", "DB", "WEB", "APP"]
        departments = ["HR", "IT", "FIN", "MKT", "OPS", "DEV", "SEC"]
        
        prefix = random.choice(prefixes)
        dept = random.choice(departments)
        number = random.randint(1, 999)
        
        return f"{prefix}-{dept}-{number:03d}"
    
    def _get_random_username(self) -> str:
        """Generate a realistic username"""
        first_names = [
            "john", "jane", "mike", "sarah", "david", "lisa", "robert", "mary",
            "james", "jennifer", "michael", "patricia", "william", "linda", "richard", "elizabeth"
        ]
        last_names = [
            "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis",
            "rodriguez", "martinez", "hernandez", "lopez", "gonzalez", "wilson", "anderson", "thomas"
        ]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        formats = [
            f"{first}.{last}",
            f"{first}{last}",
            f"{first[0]}{last}",
            f"{first}.{last}{random.randint(1, 99)}"
        ]
        
        return random.choice(formats)
    
    def _get_random_process(self) -> Dict[str, Any]:
        """Generate realistic process information"""
        processes = [
            {"name": "svchost.exe", "path": "C:\\Windows\\System32\\svchost.exe", "pid": random.randint(1000, 9999)},
            {"name": "explorer.exe", "path": "C:\\Windows\\explorer.exe", "pid": random.randint(1000, 9999)},
            {"name": "chrome.exe", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "pid": random.randint(1000, 9999)},
            {"name": "powershell.exe", "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "pid": random.randint(1000, 9999)},
            {"name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe", "pid": random.randint(1000, 9999)},
            {"name": "notepad.exe", "path": "C:\\Windows\\System32\\notepad.exe", "pid": random.randint(1000, 9999)},
        ]
        
        process = random.choice(processes)
        process["pid"] = random.randint(1000, 9999)  # Always randomize PID
        return process
    
    def _get_random_file_path(self) -> str:
        """Generate realistic file paths"""
        paths = [
            "C:\\Windows\\System32\\{}",
            "C:\\Program Files\\{}\\{}",
            "C:\\Users\\{}\\Documents\\{}",
            "C:\\Users\\{}\\Desktop\\{}",
            "C:\\Temp\\{}",
            "D:\\Projects\\{}\\{}"
        ]
        
        files = [
            "document.docx", "report.pdf", "data.xlsx", "config.ini", "log.txt",
            "backup.zip", "image.jpg", "script.ps1", "database.db", "settings.json"
        ]
        
        path_template = random.choice(paths)
        filename = random.choice(files)
        
        if "{}" in path_template:
            if path_template.count("{}") == 1:
                return path_template.format(filename)
            elif path_template.count("{}") == 2:
                username = self._get_random_username()
                return path_template.format(username, filename)
            else:
                folder = random.choice(["Application", "Service", "Tool", "Utility"])
                return path_template.format(folder, filename)
        
        return path_template
    
    def _get_weighted_severity(self) -> SeverityLevel:
        """Get severity with realistic distribution (more low/medium, fewer critical)"""
        weights = {
            SeverityLevel.LOW: 0.5,
            SeverityLevel.MEDIUM: 0.3, 
            SeverityLevel.HIGH: 0.15,
            SeverityLevel.CRITICAL: 0.05
        }
        
        rand = random.random()
        cumulative = 0
        
        for severity, weight in weights.items():
            cumulative += weight
            if rand <= cumulative:
                return severity
        
        return SeverityLevel.LOW


class MockDataScheduler:
    """
    Background scheduler that continuously generates new mock data
    """
    
    def __init__(self, generators: List[BaseMockGenerator], interval_seconds: int = 5):
        self.generators = generators
        self.interval = interval_seconds
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()
        self.latest_data = {}
        
    def start(self):
        """Start the background data generation"""
        with self._lock:
            if not self.is_running:
                self.is_running = True
                self._thread = threading.Thread(target=self._generation_loop, daemon=True)
                self._thread.start()
    
    def stop(self):
        """Stop the background data generation"""
        with self._lock:
            self.is_running = False
            if self._thread:
                self._thread.join(timeout=self.interval + 1)
    
    def _generation_loop(self):
        """Main generation loop running in background thread"""
        while self.is_running:
            try:
                for generator in self.generators:
                    # Generate new batch of events
                    events = generator.generate_batch(count=random.randint(3, 8))
                    
                    # Store in latest_data by data type
                    data_type = events[0].event_type if events else None
                    if data_type:
                        with self._lock:
                            if data_type not in self.latest_data:
                                self.latest_data[data_type] = []
                            
                            # Add new events and keep only recent ones (last 1000)
                            self.latest_data[data_type].extend(events)
                            self.latest_data[data_type] = self.latest_data[data_type][-1000:]
                
                # Sleep until next generation cycle
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Mock data generation error: {e}")
                time.sleep(1)  # Brief pause on error
    
    def get_latest_data(self, data_type: Optional[MockDataType] = None, limit: int = 100) -> List[MockEvent]:
        """Get the latest generated data"""
        with self._lock:
            if data_type:
                return self.latest_data.get(data_type, [])[-limit:]
            else:
                # Return all data types combined
                all_events = []
                for events in self.latest_data.values():
                    all_events.extend(events)
                
                # Sort by timestamp and return latest
                all_events.sort(key=lambda x: x.timestamp, reverse=True)
                return all_events[:limit]
