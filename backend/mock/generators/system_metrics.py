"""
Dynamic System Metrics Generator
Generates realistic system performance metrics matching Metricbeat structure
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class SystemMetricsGenerator(BaseMockGenerator):
    """
    Generates realistic system metrics that match actual Metricbeat output
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Base system state (persists across generations for realism)
        self.base_cpu_percent = random.uniform(15.0, 45.0)
        self.base_memory_percent = random.uniform(25.0, 65.0)
        self.base_disk_percent = random.uniform(20.0, 80.0)
        
        # Network interface names
        self.network_interfaces = [
            "Ethernet0", "Wi-Fi", "Local Area Connection", 
            "VMware Network Adapter", "VirtualBox Host-Only"
        ]
        
        # Disk names
        self.disks = ["C:", "D:", "System Reserved"]
        
        # Process names for top processes
        self.common_processes = [
            "System", "dwm.exe", "explorer.exe", "svchost.exe", "chrome.exe",
            "firefox.exe", "code.exe", "teams.exe", "outlook.exe", "notepad.exe"
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single system metrics event"""
        
        # Choose metric type
        metric_types = ["system", "cpu", "memory", "disk", "network", "process"]
        metric_type = random.choice(metric_types)
        
        # Generate base event structure
        timestamp = self._get_realistic_timestamp()
        event_data = {
            "@timestamp": timestamp.isoformat(),
            "agent": {
                "type": "metricbeat",
                "version": "9.1.4",
                "hostname": self._get_random_hostname(),
                "ephemeral_id": self._generate_id()[:8]
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "name": self._get_random_hostname(),
                "os": {
                    "name": "Windows",
                    "family": "windows",
                    "version": random.choice(["10.0.19045", "11.0.22631", "2019", "2022"]),
                    "platform": "windows",
                    "kernel": random.choice(["10.0.19041", "10.0.22000"])
                },
                "architecture": "x86_64"
            },
            "event": {
                "dataset": f"system.{metric_type}",
                "module": "system",
                "action": f"system-{metric_type}-collection",
                "category": ["host"],
                "duration": random.randint(1000000, 5000000),  # nanoseconds
                "type": ["info"]
            },
            "metricset": {
                "name": metric_type,
                "period": 10000  # 10 seconds
            }
        }
        
        # Add metric-specific data
        if metric_type == "system":
            self._add_system_metrics(event_data)
        elif metric_type == "cpu":
            self._add_cpu_metrics(event_data)
        elif metric_type == "memory":
            self._add_memory_metrics(event_data)
        elif metric_type == "disk":
            self._add_disk_metrics(event_data)
        elif metric_type == "network":
            self._add_network_metrics(event_data)
        elif metric_type == "process":
            self._add_process_metrics(event_data)
        
        # Determine severity based on metrics
        severity = self._calculate_severity(event_data, metric_type)
        
        # Add severity and status fields to event data for dashboard metrics
        event_data["severity"] = severity.value  # Convert enum to integer
        event_data["status"] = random.choice(["active", "resolved", "investigating"])
        
        # Add additional classification fields for system metrics
        if severity.value >= 3:  # HIGH or CRITICAL
            event_data["alert_type"] = "performance_alert"
            event_data["threat_level"] = "system_performance"
        elif severity.value >= 2:  # MEDIUM
            event_data["alert_type"] = "performance_warning"
            event_data["threat_level"] = "system_performance"
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=timestamp,
            event_type=MockDataType.SYSTEM_METRIC,
            severity=severity,
            source="metricbeat",
            data=event_data
        )
    
    def _add_system_metrics(self, event_data: Dict[str, Any]):
        """Add system-wide metrics"""
        # Add realistic CPU usage with some variance
        cpu_variance = random.uniform(-10.0, 10.0)
        current_cpu = max(0.0, min(100.0, self.base_cpu_percent + cpu_variance))
        
        # Add realistic memory usage
        memory_variance = random.uniform(-5.0, 5.0)
        current_memory = max(0.0, min(100.0, self.base_memory_percent + memory_variance))
        
        event_data["system"] = {
            "cpu": {
                "cores": random.choice([4, 6, 8, 12, 16]),
                "idle": {
                    "pct": round(1.0 - (current_cpu / 100.0), 4),
                    "norm": {
                        "pct": round((1.0 - (current_cpu / 100.0)) / random.choice([4, 6, 8]), 4)
                    }
                },
                "iowait": {
                    "pct": round(random.uniform(0.0001, 0.01), 4)
                },
                "system": {
                    "pct": round(random.uniform(0.01, 0.05), 4)
                },
                "user": {
                    "pct": round(current_cpu / 100.0 * random.uniform(0.6, 0.8), 4)
                },
                "total": {
                    "pct": round(current_cpu / 100.0, 4)
                }
            },
            "memory": {
                "total": random.randint(8000000000, 32000000000),  # 8-32 GB
                "used": {
                    "bytes": 0,  # Will be calculated
                    "pct": round(current_memory / 100.0, 4)
                },
                "free": {
                    "bytes": 0   # Will be calculated
                },
                "available": {
                    "bytes": 0   # Will be calculated
                },
                "cached": {
                    "bytes": random.randint(1000000000, 4000000000)
                }
            },
            "load": {
                "1": round(random.uniform(0.1, 4.0), 2),
                "5": round(random.uniform(0.1, 3.5), 2),
                "15": round(random.uniform(0.1, 3.0), 2),
                "norm": {
                    "1": round(random.uniform(0.01, 0.5), 2),
                    "5": round(random.uniform(0.01, 0.4), 2),
                    "15": round(random.uniform(0.01, 0.3), 2)
                }
            },
            "uptime": {
                "duration": {
                    "ms": random.randint(3600000, 2592000000)  # 1 hour to 30 days
                }
            }
        }
        
        # Calculate memory values
        total_memory = event_data["system"]["memory"]["total"]
        used_memory = int(total_memory * (current_memory / 100.0))
        free_memory = total_memory - used_memory
        
        event_data["system"]["memory"]["used"]["bytes"] = used_memory
        event_data["system"]["memory"]["free"]["bytes"] = free_memory
        event_data["system"]["memory"]["available"]["bytes"] = free_memory + event_data["system"]["memory"]["cached"]["bytes"]
    
    def _add_cpu_metrics(self, event_data: Dict[str, Any]):
        """Add detailed CPU metrics"""
        cores = random.choice([4, 6, 8, 12, 16])
        
        event_data["system"] = {
            "cpu": {
                "cores": cores,
                "user": {
                    "pct": round(random.uniform(0.1, 0.6), 4),
                    "ticks": random.randint(1000000, 10000000)
                },
                "system": {
                    "pct": round(random.uniform(0.01, 0.1), 4),
                    "ticks": random.randint(100000, 1000000)
                },
                "idle": {
                    "pct": round(random.uniform(0.3, 0.85), 4),
                    "ticks": random.randint(10000000, 100000000)
                },
                "iowait": {
                    "pct": round(random.uniform(0.001, 0.02), 4),
                    "ticks": random.randint(10000, 100000)
                },
                "irq": {
                    "pct": round(random.uniform(0.0001, 0.001), 4),
                    "ticks": random.randint(1000, 10000)
                },
                "nice": {
                    "pct": 0.0,
                    "ticks": 0
                },
                "softirq": {
                    "pct": round(random.uniform(0.001, 0.005), 4),
                    "ticks": random.randint(5000, 50000)
                },
                "steal": {
                    "pct": 0.0,
                    "ticks": 0
                },
                "total": {
                    "pct": round(random.uniform(0.15, 0.7), 4)
                }
            }
        }
    
    def _add_memory_metrics(self, event_data: Dict[str, Any]):
        """Add detailed memory metrics"""
        total_memory = random.randint(8000000000, 32000000000)  # 8-32 GB
        used_pct = random.uniform(0.25, 0.75)
        used_memory = int(total_memory * used_pct)
        
        event_data["system"] = {
            "memory": {
                "total": total_memory,
                "used": {
                    "bytes": used_memory,
                    "pct": round(used_pct, 4)
                },
                "free": {
                    "bytes": total_memory - used_memory
                },
                "actual": {
                    "used": {
                        "bytes": used_memory - random.randint(1000000000, 2000000000),
                        "pct": round(used_pct * 0.8, 4)
                    },
                    "free": {
                        "bytes": total_memory - (used_memory - random.randint(1000000000, 2000000000))
                    }
                },
                "swap": {
                    "total": {
                        "bytes": random.randint(2000000000, 8000000000)
                    },
                    "used": {
                        "bytes": random.randint(0, 1000000000),
                        "pct": round(random.uniform(0.0, 0.1), 4)
                    },
                    "free": {
                        "bytes": random.randint(2000000000, 8000000000)
                    }
                }
            }
        }
    
    def _add_disk_metrics(self, event_data: Dict[str, Any]):
        """Add disk I/O and usage metrics"""
        disk_name = random.choice(self.disks)
        
        total_space = random.randint(100000000000, 2000000000000)  # 100GB - 2TB
        used_pct = random.uniform(0.2, 0.85)
        used_space = int(total_space * used_pct)
        
        event_data["system"] = {
            "diskio": {
                "name": disk_name,
                "read": {
                    "count": random.randint(100000, 1000000),
                    "time": random.randint(10000, 100000),
                    "bytes": random.randint(10000000000, 100000000000)
                },
                "write": {
                    "count": random.randint(50000, 500000),
                    "time": random.randint(5000, 50000),
                    "bytes": random.randint(5000000000, 50000000000)
                },
                "io": {
                    "time": random.randint(15000, 150000)
                },
                "iostat": {
                    "read": {
                        "request": {
                            "time": random.randint(1, 10),
                            "merges_per_sec": round(random.uniform(0.1, 5.0), 2)
                        },
                        "per_sec": {
                            "bytes": random.randint(1000000, 10000000)
                        }
                    },
                    "write": {
                        "request": {
                            "time": random.randint(1, 15),
                            "merges_per_sec": round(random.uniform(0.1, 3.0), 2)
                        },
                        "per_sec": {
                            "bytes": random.randint(500000, 5000000)
                        }
                    },
                    "busy": round(random.uniform(0.01, 0.3), 4),
                    "service_time": round(random.uniform(1.0, 10.0), 2)
                }
            },
            "filesystem": {
                "device_name": disk_name,
                "mount_point": disk_name + "\\" if disk_name != "System Reserved" else "System Reserved",
                "type": "NTFS",
                "total": total_space,
                "used": {
                    "bytes": used_space,
                    "pct": round(used_pct, 4)
                },
                "free": total_space - used_space,
                "available": total_space - used_space,
                "files": random.randint(100000, 1000000),
                "free_files": random.randint(1000000, 10000000)
            }
        }
    
    def _add_network_metrics(self, event_data: Dict[str, Any]):
        """Add network interface metrics"""
        interface = random.choice(self.network_interfaces)
        
        event_data["system"] = {
            "network": {
                "name": interface,
                "out": {
                    "bytes": random.randint(1000000000, 10000000000),
                    "packets": random.randint(1000000, 10000000),
                    "errors": random.randint(0, 100),
                    "dropped": random.randint(0, 50)
                },
                "in": {
                    "bytes": random.randint(5000000000, 50000000000),
                    "packets": random.randint(5000000, 50000000),
                    "errors": random.randint(0, 100),
                    "dropped": random.randint(0, 50)
                }
            }
        }
    
    def _add_process_metrics(self, event_data: Dict[str, Any]):
        """Add process metrics"""
        process_name = random.choice(self.common_processes)
        
        event_data["system"] = {
            "process": {
                "name": process_name,
                "pid": random.randint(1000, 9999),
                "ppid": random.randint(100, 1000),
                "pgid": random.randint(1000, 9999),
                "state": random.choice(["running", "sleeping", "stopped"]),
                "cpu": {
                    "user": {
                        "ticks": random.randint(100000, 1000000)
                    },
                    "system": {
                        "ticks": random.randint(10000, 100000)
                    },
                    "total": {
                        "pct": round(random.uniform(0.001, 0.1), 4)
                    },
                    "start_time": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat()
                },
                "memory": {
                    "size": random.randint(10000000, 500000000),  # 10MB - 500MB
                    "rss": {
                        "bytes": random.randint(5000000, 250000000),
                        "pct": round(random.uniform(0.001, 0.05), 4)
                    },
                    "share": random.randint(1000000, 50000000)
                },
                "fd": {
                    "open": random.randint(10, 200),
                    "limit": {
                        "soft": 1024,
                        "hard": 4096
                    }
                }
            }
        }
    
    def _calculate_severity(self, event_data: Dict[str, Any], metric_type: str) -> SeverityLevel:
        """Calculate severity based on metric values"""
        
        if "system" not in event_data:
            return SeverityLevel.LOW
            
        system_data = event_data["system"]
        
        # CPU-based severity
        if "cpu" in system_data and "total" in system_data["cpu"]:
            cpu_pct = system_data["cpu"]["total"].get("pct", 0)
            if cpu_pct > 0.9:  # > 90%
                return SeverityLevel.CRITICAL
            elif cpu_pct > 0.75:  # > 75%
                return SeverityLevel.HIGH
            elif cpu_pct > 0.5:  # > 50%
                return SeverityLevel.MEDIUM
        
        # Memory-based severity
        if "memory" in system_data and "used" in system_data["memory"]:
            memory_pct = system_data["memory"]["used"].get("pct", 0)
            if memory_pct > 0.95:  # > 95%
                return SeverityLevel.CRITICAL
            elif memory_pct > 0.85:  # > 85%
                return SeverityLevel.HIGH
            elif memory_pct > 0.7:  # > 70%
                return SeverityLevel.MEDIUM
        
        # Disk-based severity
        if "filesystem" in system_data and "used" in system_data["filesystem"]:
            disk_pct = system_data["filesystem"]["used"].get("pct", 0)
            if disk_pct > 0.95:  # > 95%
                return SeverityLevel.CRITICAL
            elif disk_pct > 0.9:  # > 90%
                return SeverityLevel.HIGH
            elif disk_pct > 0.8:  # > 80%
                return SeverityLevel.MEDIUM
        
        return SeverityLevel.LOW
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of system metrics"""
        return [self.generate_event() for _ in range(count)]
