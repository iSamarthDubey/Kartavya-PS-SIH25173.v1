#!/usr/bin/env python3
"""
🚢 Port Management Utility
Handles port availability checks and process management for Windows/Unix
"""

import socket
import subprocess
import platform
import time
import logging
from typing import List, Dict, Optional, Tuple
import psutil

logger = logging.getLogger(__name__)


class PortManager:
    """Manages port availability and process termination"""
    
    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
        self.is_unix = platform.system().lower() in ['linux', 'darwin']
        
    def is_port_in_use(self, port: int, host: str = 'localhost') -> bool:
        """
        Check if a port is currently in use
        
        Args:
            port: Port number to check
            host: Host to check (default: localhost)
            
        Returns:
            bool: True if port is in use, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)  # 1 second timeout
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.warning(f"Error checking port {port}: {e}")
            return False
    
    def find_available_port(self, start_port: int = 8000, end_port: int = 8100) -> Optional[int]:
        """
        Find an available port in the given range
        
        Args:
            start_port: Starting port number
            end_port: Ending port number
            
        Returns:
            int: Available port number or None if none found
        """
        for port in range(start_port, end_port + 1):
            if not self.is_port_in_use(port):
                return port
        return None
    
    def get_processes_using_port(self, port: int) -> List[Dict]:
        """
        Get list of processes using a specific port
        
        Args:
            port: Port number to check
            
        Returns:
            List[Dict]: List of process information dictionaries
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': ' '.join(proc.info['cmdline'] or []),
                                'status': proc.status()
                            })
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.warning(f"Error getting processes for port {port}: {e}")
            
        return processes
    
    def get_port_info(self, port: int) -> Dict:
        """
        Get comprehensive information about a port
        
        Args:
            port: Port number to check
            
        Returns:
            Dict: Port information including availability and processes
        """
        in_use = self.is_port_in_use(port)
        processes = self.get_processes_using_port(port) if in_use else []
        
        return {
            'port': port,
            'in_use': in_use,
            'available': not in_use,
            'processes': processes,
            'process_count': len(processes)
        }
    
    def terminate_processes_on_port(self, port: int, force: bool = False, timeout: int = 10) -> Dict:
        """
        Terminate processes using a specific port
        
        Args:
            port: Port number
            force: Whether to force kill processes (SIGKILL vs SIGTERM)
            timeout: Timeout in seconds for graceful termination
            
        Returns:
            Dict: Results of termination attempts
        """
        processes = self.get_processes_using_port(port)
        
        if not processes:
            return {
                'success': True,
                'message': f'No processes found using port {port}',
                'terminated': [],
                'failed': []
            }
        
        logger.info(f"Found {len(processes)} process(es) using port {port}")
        
        terminated = []
        failed = []
        
        for proc_info in processes:
            pid = proc_info['pid']
            name = proc_info['name']
            
            try:
                proc = psutil.Process(pid)
                
                if force:
                    # Force kill immediately
                    proc.kill()
                    logger.info(f"Force killed process {pid} ({name})")
                else:
                    # Graceful termination
                    proc.terminate()
                    logger.info(f"Terminated process {pid} ({name})")
                    
                    # Wait for process to terminate
                    try:
                        proc.wait(timeout=timeout)
                    except psutil.TimeoutExpired:
                        logger.warning(f"Process {pid} ({name}) didn't terminate gracefully, force killing...")
                        proc.kill()
                
                terminated.append({
                    'pid': pid,
                    'name': name,
                    'cmdline': proc_info['cmdline']
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                error_msg = f"Failed to terminate process {pid} ({name}): {e}"
                logger.warning(error_msg)
                failed.append({
                    'pid': pid,
                    'name': name,
                    'error': str(e)
                })
            except Exception as e:
                error_msg = f"Unexpected error terminating process {pid} ({name}): {e}"
                logger.error(error_msg)
                failed.append({
                    'pid': pid,
                    'name': name,
                    'error': str(e)
                })
        
        # Wait a moment and verify port is free
        time.sleep(1)
        still_in_use = self.is_port_in_use(port)
        
        return {
            'success': not still_in_use,
            'message': f'Port {port} is now {"available" if not still_in_use else "still in use"}',
            'terminated': terminated,
            'failed': failed,
            'port_available': not still_in_use
        }
    
    def ensure_port_available(self, port: int, auto_kill: bool = True, force: bool = False) -> Tuple[bool, str]:
        """
        Ensure a port is available for use
        
        Args:
            port: Port number to check/free
            auto_kill: Whether to automatically kill processes using the port
            force: Whether to force kill processes
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_port_in_use(port):
            return True, f"Port {port} is already available"
        
        logger.info(f"Port {port} is in use")
        
        if not auto_kill:
            processes = self.get_processes_using_port(port)
            proc_names = [p['name'] for p in processes]
            return False, f"Port {port} is in use by: {', '.join(proc_names)}"
        
        logger.info(f"Attempting to free port {port}...")
        result = self.terminate_processes_on_port(port, force=force)
        
        if result['success']:
            logger.info(f"✅ Successfully freed port {port}")
            return True, f"Port {port} freed successfully"
        else:
            failed_processes = [f"{p['name']} (PID: {p['pid']})" for p in result['failed']]
            return False, f"Failed to free port {port}. Processes still running: {', '.join(failed_processes)}"
    
    def get_recommended_port(self, preferred_port: int = 8000) -> Tuple[int, str]:
        """
        Get a recommended port, preferring the specified port but finding alternative if needed
        
        Args:
            preferred_port: The preferred port number
            
        Returns:
            Tuple[int, str]: (port_number, message)
        """
        if not self.is_port_in_use(preferred_port):
            return preferred_port, f"Using preferred port {preferred_port}"
        
        # Try to find alternative port
        alternative = self.find_available_port(preferred_port + 1, preferred_port + 100)
        
        if alternative:
            return alternative, f"Port {preferred_port} in use, using alternative port {alternative}"
        else:
            return preferred_port, f"No alternative ports found, will attempt to free {preferred_port}"
    
    def validate_port_range(self, port: int) -> Tuple[bool, str]:
        """
        Validate if a port number is in a valid range
        
        Args:
            port: Port number to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not isinstance(port, int):
            return False, "Port must be an integer"
        
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
        
        if port < 1024:
            return False, "Port numbers below 1024 require elevated privileges"
        
        # Common problematic ports
        reserved_ports = [
            3000,  # Common dev server
            5000,  # Flask default
            5432,  # PostgreSQL
            6379,  # Redis
            9200,  # Elasticsearch
            27017, # MongoDB
        ]
        
        if port in reserved_ports:
            return True, f"Warning: Port {port} is commonly used by other services"
        
        return True, f"Port {port} is valid"


def setup_port_for_service(port: int, service_name: str = "Backend Service", auto_kill: bool = True) -> Tuple[bool, int, str]:
    """
    Setup and ensure a port is available for a service
    
    Args:
        port: Desired port number
        service_name: Name of the service for logging
        auto_kill: Whether to automatically kill processes using the port
        
    Returns:
        Tuple[bool, int, str]: (success, final_port, message)
    """
    manager = PortManager()
    
    # Validate port
    valid, validation_msg = manager.validate_port_range(port)
    if not valid:
        return False, port, f"Invalid port: {validation_msg}"
    
    if validation_msg.startswith("Warning"):
        logger.warning(validation_msg)
    
    # Check if port is available
    port_info = manager.get_port_info(port)
    
    if port_info['available']:
        logger.info(f"✅ Port {port} is available for {service_name}")
        return True, port, f"Port {port} ready for {service_name}"
    
    logger.info(f"🚨 Port {port} is in use by {port_info['process_count']} process(es)")
    
    # Log processes using the port
    for proc in port_info['processes']:
        logger.info(f"   - PID {proc['pid']}: {proc['name']} ({proc['cmdline'][:100]}...)")
    
    if auto_kill:
        logger.info(f"🔄 Attempting to free port {port} for {service_name}...")
        success, message = manager.ensure_port_available(port, auto_kill=True, force=False)
        
        if success:
            logger.info(f"✅ {message}")
            return True, port, message
        else:
            logger.error(f"❌ {message}")
            
            # Try to find alternative port
            alternative, alt_message = manager.get_recommended_port(port)
            if alternative != port:
                logger.info(f"🔄 {alt_message}")
                return True, alternative, alt_message
            else:
                return False, port, message
    else:
        return False, port, f"Port {port} is in use and auto_kill is disabled"


if __name__ == "__main__":
    # Test the port manager
    manager = PortManager()
    
    # Test port checking
    test_port = 8000
    print(f"🧪 Testing Port Manager with port {test_port}")
    
    info = manager.get_port_info(test_port)
    print(f"Port info: {info}")
    
    if info['in_use']:
        print(f"Processes using port {test_port}:")
        for proc in info['processes']:
            print(f"  - {proc}")
    
    # Test port setup
    success, final_port, message = setup_port_for_service(test_port, "Test Service")
    print(f"Setup result: success={success}, port={final_port}, message='{message}'")
