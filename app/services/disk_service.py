"""
SupportSight Disk Service

Collects and provides detailed disk/storage diagnostics.
"""

import os
from typing import Dict, List, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class DiskService:
    """
    Service for disk diagnostics and monitoring.

    Provides information about disk partitions, usage,
    I/O statistics, and storage health.
    """

    @classmethod
    def get_partitions(cls, all: bool = False) -> List[Dict[str, Any]]:
        """
        Get all disk partitions.

        Args:
            all: Include fake partitions if True

        Returns:
            List of partition information dictionaries
        """
        if not PSUTIL_AVAILABLE:
            return []

        try:
            partitions = psutil.disk_partitions(all=all)
            result = []

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'options': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except (PermissionError, FileNotFoundError):
                    # Handle drives that aren't ready
                    result.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'options': partition.opts,
                        'total': 0,
                        'used': 0,
                        'free': 0,
                        'percent': 0,
                        'error': 'Unable to read disk usage'
                    })

            return result
        except Exception:
            return []

    @classmethod
    def get_disk_usage(cls, path: str = None) -> Dict[str, Any]:
        """
        Get disk usage for a specific path.

        Args:
            path: Path to check (defaults to current drive)

        Returns:
            Dictionary with disk usage information
        """
        if not PSUTIL_AVAILABLE:
            return cls._empty_usage()

        if path is None:
            path = os.getcwd()

        try:
            usage = psutil.disk_usage(path)
            return {
                'path': path,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except Exception:
            return cls._empty_usage()

    @classmethod
    def _empty_usage(cls) -> Dict[str, Any]:
        """Return empty usage structure."""
        return {
            'path': None,
            'total': 0,
            'used': 0,
            'free': 0,
            'percent': 0
        }

    @classmethod
    def get_disk_io(cls) -> Dict[str, Any]:
        """
        Get disk I/O statistics.

        Returns:
            Dictionary with I/O statistics
        """
        if not PSUTIL_AVAILABLE:
            return cls._empty_io_stats()

        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                return {
                    'read_count': io_counters.read_count,
                    'write_count': io_counters.write_count,
                    'read_bytes': io_counters.read_bytes,
                    'write_bytes': io_counters.write_bytes,
                    'read_time': io_counters.read_time,
                    'write_time': io_counters.write_time,
                    'read_speed': 0,  # Calculated field
                    'write_speed': 0  # Calculated field
                }
        except Exception:
            pass

        return cls._empty_io_stats()

    @classmethod
    def _empty_io_stats(cls) -> Dict[str, Any]:
        """Return empty I/O stats structure."""
        return {
            'read_count': 0,
            'write_count': 0,
            'read_bytes': 0,
            'write_bytes': 0,
            'read_time': 0,
            'write_time': 0
        }

    @classmethod
    def get_per_disk_io(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get per-disk I/O statistics.

        Returns:
            Dictionary mapping drive letters to I/O stats
        """
        if not PSUTIL_AVAILABLE:
            return {}

        try:
            io_counters = psutil.disk_io_counters(perdisk=True)
            result = {}

            for disk_name, counters in io_counters.items():
                result[disk_name] = {
                    'read_count': counters.read_count,
                    'write_count': counters.write_count,
                    'read_bytes': counters.read_bytes,
                    'write_bytes': counters.write_bytes,
                    'read_time': counters.read_time,
                    'write_time': counters.write_time
                }

            return result
        except Exception:
            return {}

    @classmethod
    def get_disk_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive disk information.

        Returns:
            Dictionary with all disk details
        """
        partitions = cls.get_partitions()
        io_stats = cls.get_disk_io()

        # Calculate totals across all partitions
        total_space = sum(p.get('total', 0) for p in partitions)
        used_space = sum(p.get('used', 0) for p in partitions)
        free_space = sum(p.get('free', 0) for p in partitions)
        overall_percent = (used_space / total_space * 100) if total_space > 0 else 0

        return {
            'partitions': partitions,
            'io_stats': io_stats,
            'per_disk_io': cls.get_per_disk_io(),
            'total_space': total_space,
            'used_space': used_space,
            'free_space': free_space,
            'overall_percent': overall_percent
        }

    @classmethod
    def detect_ssd_hdd(cls, path: str = None) -> Dict[str, Any]:
        """
        Attempt to detect if a disk is SSD or HDD.

        Args:
            path: Path to check

        Returns:
            Dictionary with disk type information
        """
        if not PSUTIL_AVAILABLE:
            return {'type': 'unknown', 'method': 'none'}

        result = {
            'type': 'unknown',
            'method': 'none',
            'confidence': 'low'
        }

        if cls.is_windows():
            try:
                import winreg
                key_path = r'HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0'

                registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(registry, key_path)

                try:
                    device_type = winreg.QueryValueEx(key, 'Device Type')
                    # ATA device types: 0 = disk, 5 = cdrom
                    if device_type and device_type[0] == 0:
                        # Further check via rotation rate if available
                        result['type'] = 'unknown_sata'
                        result['method'] = 'device_type'
                except FileNotFoundError:
                    pass

                winreg.CloseKey(key)
                winreg.CloseKey(registry)
            except Exception:
                pass

        # Fallback: Use seek ratio as a heuristic
        # SSDs typically have very low seek times
        io_stats = cls.get_disk_io()
        if io_stats.get('read_count', 0) > 0:
            read_time = io_stats.get('read_time', 0)
            read_count = io_stats.get('read_count', 1)
            avg_seek_time = read_time / read_count if read_count > 0 else 100

            if avg_seek_time < 1:  # Very low seek time suggests SSD
                result['type'] = 'ssd'
                result['method'] = 'seek_time_heuristic'
                result['confidence'] = 'medium'
            elif avg_seek_time > 5:  # Higher seek time suggests HDD
                result['type'] = 'hdd'
                result['method'] = 'seek_time_heuristic'
                result['confidence'] = 'medium'

        return result

    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        import platform
        return platform.system() == 'Windows'

    @classmethod
    def get_critical_partitions(cls, threshold: float = 90.0) -> List[Dict[str, Any]]:
        """
        Get partitions exceeding usage threshold.

        Args:
            threshold: Usage percentage threshold

        Returns:
            List of critical partitions
        """
        partitions = cls.get_partitions()
        critical = []

        for partition in partitions:
            if partition.get('percent', 0) >= threshold:
                critical.append(partition)

        return critical

    @classmethod
    def get_partition_health_status(cls, percent: float, threshold: float = 90.0) -> Dict[str, Any]:
        """
        Get health status for a partition based on usage.

        Args:
            percent: Usage percentage
            threshold: Warning threshold

        Returns:
            Dictionary with health status
        """
        status = 'healthy'
        severity = 'success'

        if percent >= threshold:
            status = 'critical'
            severity = 'danger'
        elif percent >= threshold * 0.8:
            status = 'warning'
            severity = 'warning'

        return {
            'status': status,
            'severity': severity,
            'percent': percent,
            'threshold': threshold,
            'is_critical': percent >= threshold,
            'is_warning': threshold * 0.8 <= percent < threshold
        }
