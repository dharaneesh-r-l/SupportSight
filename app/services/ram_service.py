"""
SupportSight RAM Service

Collects and provides detailed RAM/memory diagnostics and monitoring.
"""

import time
from typing import Dict, List, Any
from collections import deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class RAMService:
    """
    Service for RAM diagnostics and monitoring.

    Provides real-time memory usage, availability, and historical tracking.
    """

    # Class-level storage for historical data
    _usage_history: deque = deque(maxlen=60)

    @classmethod
    def get_memory(cls) -> Dict[str, Any]:
        """
        Get comprehensive memory information.

        Returns:
            Dictionary with memory details
        """
        if not PSUTIL_AVAILABLE:
            return cls._empty_memory_info()

        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'active': getattr(memory, 'active', 0),
                'inactive': getattr(memory, 'inactive', 0),
                'buffers': getattr(memory, 'buffers', 0),
                'cached': getattr(memory, 'cached', 0),
                'shared': getattr(memory, 'shared', 0)
            }
        except Exception:
            return cls._empty_memory_info()

    @classmethod
    def _empty_memory_info(cls) -> Dict[str, Any]:
        """Return empty memory info structure."""
        return {
            'total': 0,
            'available': 0,
            'used': 0,
            'free': 0,
            'percent': 0
        }

    @classmethod
    def get_total(cls) -> int:
        """
        Get total RAM in bytes.

        Returns:
            Total RAM in bytes
        """
        memory = cls.get_memory()
        return memory.get('total', 0)

    @classmethod
    def get_used(cls) -> int:
        """
        Get used RAM in bytes.

        Returns:
            Used RAM in bytes
        """
        memory = cls.get_memory()
        return memory.get('used', 0)

    @classmethod
    def get_available(cls) -> int:
        """
        Get available RAM in bytes.

        Returns:
            Available RAM in bytes
        """
        memory = cls.get_memory()
        return memory.get('available', 0)

    @classmethod
    def get_percent(cls) -> float:
        """
        Get RAM usage percentage.

        Returns:
            RAM usage percentage (0-100)
        """
        memory = cls.get_memory()
        return memory.get('percent', 0.0)

    @classmethod
    def get_swap(cls) -> Dict[str, Any]:
        """
        Get swap memory information.

        Returns:
            Dictionary with swap memory details
        """
        if not PSUTIL_AVAILABLE:
            return cls._empty_memory_info()

        try:
            swap = psutil.swap_memory()
            return {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent,
                'sin': swap.sin,  # Pages swapped in
                'sout': swap.sout  # Pages swapped out
            }
        except Exception:
            return cls._empty_memory_info()

    @classmethod
    def record_usage(cls) -> float:
        """
        Record current memory usage to history.

        Returns:
            Current memory usage percentage
        """
        percent = cls.get_percent()
        cls._usage_history.append({
            'timestamp': time.time(),
            'usage': percent,
            'used': cls.get_used(),
            'available': cls.get_available()
        })
        return percent

    @classmethod
    def get_usage_history(cls, points: int = 60) -> List[Dict[str, Any]]:
        """
        Get historical memory usage data.

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
        Calculate average memory usage over a period.

        Args:
            duration: Duration in seconds

        Returns:
            Average memory usage percentage
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
    def get_memory_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive memory information.

        Returns:
            Dictionary with all memory details
        """
        return {
            'memory': cls.get_memory(),
            'swap': cls.get_swap(),
            'usage_history': cls.get_usage_history(),
            'average_usage': cls.get_average_usage()
        }

    @classmethod
    def get_top_processes(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get processes with highest memory usage.

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of top memory-consuming processes
        """
        if not PSUTIL_AVAILABLE:
            return []

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
            try:
                info = proc.info
                memory_info = info.get('memory_info', None)
                memory_percent = info.get('memory_percent', 0)

                if memory_percent and memory_percent > 0:
                    processes.append({
                        'pid': info.get('pid'),
                        'name': info.get('name'),
                        'memory_mb': memory_info.rss / (1024 * 1024) if memory_info else 0,
                        'memory_percent': memory_percent
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage and return top processes
        processes.sort(key=lambda x: x.get('memory_percent') or 0, reverse=True)
        return processes[:limit]

    @classmethod
    def get_memory_health_status(cls, threshold: float = 90.0) -> Dict[str, Any]:
        """
        Get memory health status based on usage threshold.

        Args:
            threshold: Usage percentage to consider as warning

        Returns:
            Dictionary with health status information
        """
        memory = cls.get_memory()
        usage = memory.get('percent', 0)
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
            'total': memory.get('total', 0),
            'used': memory.get('used', 0),
            'available': memory.get('available', 0),
            'is_critical': usage > threshold,
            'is_warning': usage > threshold * 0.8 and usage <= threshold
        }

    @classmethod
    def get_detailed_breakdown(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed memory breakdown by type.

        Returns:
            Dictionary with memory breakdown
        """
        memory = cls.get_memory()

        return {
            'physical': {
                'total': memory.get('total', 0),
                'used': memory.get('used', 0),
                'available': memory.get('available', 0),
                'percent': memory.get('percent', 0),
                'active': memory.get('active', 0),
                'inactive': memory.get('inactive', 0),
                'cached': memory.get('cached', 0),
                'buffers': memory.get('buffers', 0),
                'shared': memory.get('shared', 0)
            },
            'virtual': cls.get_swap()
        }
