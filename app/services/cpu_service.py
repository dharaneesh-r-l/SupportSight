"""
SupportSight CPU Service

Collects and provides detailed CPU diagnostics and monitoring.
"""

import time
from typing import Dict, List, Any, Optional
from collections import deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class CPUService:
    """
    Service for CPU diagnostics and monitoring.

    Provides real-time CPU usage, frequency, core information,
    and historical usage tracking.
    """

    # Class-level storage for historical data
    _usage_history: deque = deque(maxlen=60)

    @classmethod
    def get_usage(cls) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage as a percentage (0-100)
        """
        if not PSUTIL_AVAILABLE:
            return 0.0

        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    @classmethod
    def get_usage_per_cpu(cls) -> List[float]:
        """
        Get CPU usage percentage for each core.

        Returns:
            List of CPU usage percentages for each core
        """
        if not PSUTIL_AVAILABLE:
            return []

        try:
            return psutil.cpu_percent(interval=0.1, percpu=True)
        except Exception:
            return []

    @classmethod
    def get_frequency(cls) -> Dict[str, Any]:
        """
        Get CPU frequency information.

        Returns:
            Dictionary with current, min, and max frequency
        """
        if not PSUTIL_AVAILABLE:
            return {'current': 0, 'min': 0, 'max': 0, 'unit': 'MHz'}

        try:
            freq = psutil.cpu_freq()
            if freq:
                return {
                    'current': round(freq.current, 2),
                    'min': round(freq.min, 2) if freq.min else 0,
                    'max': round(freq.max, 2) if freq.max else 0,
                    'unit': 'MHz'
                }
        except Exception:
            pass

        return {'current': 0, 'min': 0, 'max': 0, 'unit': 'MHz'}

    @classmethod
    def get_core_count(cls) -> Dict[str, int]:
        """
        Get CPU core count information.

        Returns:
            Dictionary with physical and logical core counts
        """
        if not PSUTIL_AVAILABLE:
            return {'physical': 0, 'logical': 0}

        try:
            return {
                'physical': psutil.cpu_count(logical=False) or 0,
                'logical': psutil.cpu_count(logical=True) or 0
            }
        except Exception:
            return {'physical': 0, 'logical': 0}

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Get CPU statistics.

        Returns:
            Dictionary with CPU statistics
        """
        if not PSUTIL_AVAILABLE:
            return {}

        try:
            stats = psutil.cpu_stats()
            return {
                'ctx_switches': stats.ctx_switches,
                'interrupts': stats.interrupts,
                'soft_interrupts': stats.soft_interrupts,
                'syscalls': stats.syscalls
            }
        except Exception:
            return {}

    @classmethod
    def get_times(cls) -> Dict[str, float]:
        """
        Get CPU time statistics.

        Returns:
            Dictionary with user, system, idle times
        """
        if not PSUTIL_AVAILABLE:
            return {'user': 0, 'system': 0, 'idle': 0}

        try:
            times = psutil.cpu_times()
            return {
                'user': times.user,
                'system': times.system,
                'idle': times.idle,
                'interrupt': getattr(times, 'interrupt', 0),
                'dpc': getattr(times, 'dpc', 0)
            }
        except Exception:
            return {'user': 0, 'system': 0, 'idle': 0}

    @classmethod
    def record_usage(cls) -> float:
        """
        Record current CPU usage to history.

        Returns:
            Current CPU usage
        """
        usage = cls.get_usage()
        cls._usage_history.append({
            'timestamp': time.time(),
            'usage': usage
        })
        return usage

    @classmethod
    def get_usage_history(cls, points: int = 60) -> List[Dict[str, Any]]:
        """
        Get historical CPU usage data.

        Args:
            points: Number of data points to return

        Returns:
            List of historical usage data points
        """
        history = list(cls._usage_history)
        if len(history) > points:
            return history[-points:]
        return history

    @classmethod
    def get_average_usage(cls, duration: int = 60) -> float:
        """
        Calculate average CPU usage over a period.

        Args:
            duration: Duration in seconds (uses available history)

        Returns:
            Average CPU usage percentage
        """
        history = list(cls._usage_history)
        if not history:
            return 0.0

        current_time = time.time()
        cutoff_time = current_time - duration

        recent_usage = [
            point['usage'] for point in history
            if point['timestamp'] >= cutoff_time
        ]

        if not recent_usage:
            return 0.0

        return sum(recent_usage) / len(recent_usage)

    @classmethod
    def get_cpu_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive CPU information.

        Returns:
            Dictionary with all CPU details
        """
        return {
            'usage': cls.get_usage(),
            'usage_per_cpu': cls.get_usage_per_cpu(),
            'frequency': cls.get_frequency(),
            'core_count': cls.get_core_count(),
            'stats': cls.get_stats(),
            'times': cls.get_times(),
            'usage_history': cls.get_usage_history(),
            'average_usage': cls.get_average_usage()
        }

    @classmethod
    def get_top_processes(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get processes with highest CPU usage.

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of top CPU-consuming processes
        """
        if not PSUTIL_AVAILABLE:
            return []

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                cpu_percent = info.get('cpu_percent', 0)
                if cpu_percent and cpu_percent > 0:
                    processes.append({
                        'pid': info.get('pid'),
                        'name': info.get('name'),
                        'cpu_percent': cpu_percent,
                        'memory_percent': info.get('memory_percent', 0)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage and return top processes
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:limit]

    @classmethod
    def get_cpu_health_status(cls, threshold: float = 85.0) -> Dict[str, Any]:
        """
        Get CPU health status based on usage threshold.

        Args:
            threshold: Usage percentage to consider as warning

        Returns:
            Dictionary with health status information
        """
        usage = cls.get_usage()
        average_usage = cls.get_average_usage()

        status = 'healthy'
        severity = 'success'

        if usage > threshold:
            status = 'critical'
            severity = 'danger'
        elif usage > threshold * 0.8:
            status = 'warning'
            severity = 'warning'

        return {
            'status': status,
            'severity': severity,
            'current_usage': usage,
            'average_usage': average_usage,
            'threshold': threshold,
            'is_critical': usage > threshold,
            'is_warning': usage > threshold * 0.8 and usage <= threshold
        }
