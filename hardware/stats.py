"""Hardware statistics collector for Raspberry Pi"""

import os
import platform
import socket
import psutil
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class HardwareStats:
    """Collects and provides hardware statistics for Raspberry Pi"""
    
    def __init__(self):
        """Initialize hardware stats collector"""
        logger.info("Initializing hardware stats collector")
        self._validate_system()
    
    def _validate_system(self):
        """Validate that we're running on a supported system"""
        try:
            # Check if we can access system info
            psutil.cpu_percent(interval=None)
            logger.info("Hardware stats collector initialized successfully")
        except Exception as e:
            logger.warning(f"Could not validate system: {e}")
    
    def _get_cpu_temperature(self) -> float:
        """
        Get CPU temperature in Celsius
        Reads from thermal zone on Raspberry Pi
        """
        try:
            # Try reading from Raspberry Pi thermal zone
            thermal_paths = [
                '/sys/class/thermal/thermal_zone0/temp',  # Raspberry Pi
                '/sys/devices/virtual/thermal/thermal_zone0/temp'  # Alternative
            ]
            
            for path in thermal_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        return round(temp, 1)
            
            # If no thermal zone found, return 0
            logger.warning("No thermal zone found for CPU temperature")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error reading CPU temperature: {e}")
            return 0.0
    
    def _get_os_info(self) -> Dict[str, str]:
        """Get OS information"""
        try:
            return {
                "hostname": os.getenv("PUBLIC_HOSTNAME", socket.gethostname()),
                "platform": platform.system(),
                "arch": platform.machine()
            }
        except Exception as e:
            logger.error(f"Error getting OS info: {e}")
            return {
                "hostname": "unknown",
                "platform": "unknown",
                "arch": "unknown"
            }
    
    def _get_cpu_usage(self) -> List[float]:
        """
        Get per-core CPU usage percentages as numbers
        Returns a list of float values (0-100)
        """
        try:
            # Get per-core CPU usage
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            return [round(usage, 1) for usage in per_cpu]
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return [0.0]
    
    def _get_memory_usage(self) -> Dict[str, int]:
        """
        Get memory usage in bytes
        Returns used and total memory
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "used": mem.used,
                "total": mem.total
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {
                "used": 0,
                "total": 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Collect and return all hardware statistics
        
        Returns:
            Dictionary containing:
            - os: {hostname, platform, arch}
            - cpuTemp: CPU temperature in Celsius
            - cpuUsage: List of per-core usage percentages (numbers)
            - memoryUsage: {used, total} in bytes
        """
        try:
            stats = {
                "success": True,
                "os": self._get_os_info(),
                "cpuTemp": self._get_cpu_temperature(),
                "cpuUsage": self._get_cpu_usage(),
                "memoryUsage": self._get_memory_usage()
            }
            return stats
        except Exception as e:
            logger.error(f"Error collecting hardware stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "os": {"hostname": "unknown", "platform": "unknown", "arch": "unknown"},
                "cpuTemp": 0.0,
                "cpuUsage": [0.0],
                "memoryUsage": {"used": 0, "total": 0}
            }
