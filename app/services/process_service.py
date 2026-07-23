"""
SupportSight Process Service

Collects and provides detailed information about running processes.
"""

from typing import Dict, List, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ProcessService:
    """
    Service for process monitoring and management.

    Provides information about running processes,
    resource usage, and process details.
    """

    @classmethod
    def get_all_processes(cls, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all running processes.

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of process information dictionaries
        """
        if not PSUTIL_AVAILABLE:
            return []

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 
                                          'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                # Get additional memory info
                try:
                    mem_info = proc.memory_info()
                    info['memory_rss'] = mem_info.rss
                    info['memory_vms'] = mem_info.vms
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    info['memory_rss'] = 0
                    info['memory_vms'] = 0

                # Get create time
                try:
                    info['create_time'] = proc.create_time()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    info['create_time'] = 0

                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage by default
        processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)

        if limit:
            processes = processes[:limit]

        return processes

    @classmethod
    def get_process_by_pid(cls, pid: int) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific process.

        Args:
            pid: Process ID

        Returns:
            Process information dictionary or None
        """
        if not PSUTIL_AVAILABLE:
            return None

        try:
            proc = psutil.Process(pid)
            info = proc.info.copy()

            # Get detailed memory info
            try:
                mem_info = proc.memory_info()
                info['memory_rss'] = mem_info.rss
                info['memory_vms'] = mem_info.vms
                info['memory_percent'] = proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Get CPU usage
            try:
                info['cpu_percent'] = proc.cpu_percent(interval=0.1)
                info['cpu_times'] = proc.cpu_times()._asdict()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Get thread count
            try:
                info['num_threads'] = proc.num_threads()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Get open files
            try:
                info['open_files'] = len(proc.open_files())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                info['open_files'] = 0

            # Get connections
            try:
                info['connections'] = len(proc.connections())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                info['connections'] = 0

            return info
        except psutil.NoSuchProcess:
            return None
        except Exception:
            return None

    @classmethod
    def get_top_cpu_processes(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get processes with highest CPU usage.

        Args:
            limit: Maximum number of processes

        Returns:
            List of top CPU-consuming processes
        """
        return cls.get_all_processes(limit=limit)

    @classmethod
    def get_top_memory_processes(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get processes with highest memory usage.

        Args:
            limit: Maximum number of processes

        Returns:
            List of top memory-consuming processes
        """
        if not PSUTIL_AVAILABLE:
            return []

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
            try:
                info = proc.info
                try:
                    mem_info = proc.memory_info()
                    info['memory_rss'] = mem_info.rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    info['memory_rss'] = 0
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage
        processes.sort(key=lambda x: x.get('memory_percent') or 0, reverse=True)
        return processes[:limit]

    @classmethod
    def search_processes(cls, query: str) -> List[Dict[str, Any]]:
        """
        Search for processes by name.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching processes
        """
        if not PSUTIL_AVAILABLE:
            return []

        query_lower = query.lower()
        results = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                name = info.get('name', '').lower()
                if query_lower in name:
                    results.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return results

    @classmethod
    def get_process_count(cls) -> Dict[str, int]:
        """
        Get process count statistics.

        Returns:
            Dictionary with process counts
        """
        if not PSUTIL_AVAILABLE:
            return {'total': 0, 'running': 0, 'sleeping': 0}

        total = 0
        running = 0
        sleeping = 0

        for proc in psutil.process_iter(['status']):
            try:
                total += 1
                status = proc.info.get('status', '').lower()
                if status == psutil.STATUS_RUNNING:
                    running += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            'total': total,
            'running': running,
            'sleeping': sleeping
        }

    @classmethod
    def get_process_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive process information.

        Returns:
            Dictionary with all process details
        """
        return {
            'top_cpu': cls.get_top_cpu_processes(10),
            'top_memory': cls.get_top_memory_processes(10),
            'counts': cls.get_process_count(),
            'all_processes': cls.get_all_processes(50)
        }

    @classmethod
    def kill_process(cls, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        Terminate a process.

        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM

        Returns:
            Result dictionary
        """
        if not PSUTIL_AVAILABLE:
            return {'success': False, 'message': 'psutil not available'}

        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except psutil.NoSuchProcess:
            return {'success': False, 'message': f'Process {pid} not found'}
        except psutil.AccessDenied:
            return {'success': False, 'message': f'Access denied for process {pid}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @classmethod
    def get_user_processes(cls, username: str) -> List[Dict[str, Any]]:
        """
        Get processes running under a specific user.

        Args:
            username: Username to filter by

        Returns:
            List of processes owned by the user
        """
        if not PSUTIL_AVAILABLE:
            return []

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info.get('username') == username:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    @classmethod
    def get_zombie_processes(cls) -> List[Dict[str, Any]]:
        """
        Get zombie processes.

        Returns:
            List of zombie processes
        """
        if not PSUTIL_AVAILABLE:
            return []

        zombies = []
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'status']):
            try:
                info = proc.info
                status = info.get('status', '').lower()
                if status == psutil.STATUS_ZOMBIE:
                    zombies.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return zombies
