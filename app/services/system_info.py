"""
SupportSight System Information Service

Collects and provides general Windows system information.
"""

import platform
import socket
import os
from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemInfoService:
    """
    Service for collecting general system information.

    Provides detailed information about the operating system,
    computer hardware, and system configuration.
    """

    @classmethod
    def get_computer_name(cls) -> str:
        """Get the computer name."""
        return socket.gethostname()

    @classmethod
    def get_username(cls) -> str:
        """Get the current username."""
        return os.environ.get('USERNAME', os.environ.get('USER', 'Unknown'))

    @classmethod
    def get_processor_name(cls) -> str:
        """
        Get accurate human-readable processor model name.
        Works on Windows (Registry), Linux (/proc/cpuinfo), and macOS.

        Returns:
            Processor brand string (e.g., 'AMD Ryzen 5 5600H with Radeon Graphics')
        """
        system = platform.system()

        if system == 'Windows':
            try:
                import winreg
                reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')
                proc_name = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
                winreg.CloseKey(key)
                winreg.CloseKey(reg)
                if proc_name:
                    return proc_name
            except Exception:
                pass

        elif system == 'Linux':
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.strip().startswith('model name'):
                            return line.split(':', 1)[1].strip()
            except Exception:
                pass

        elif system == 'Darwin':
            try:
                import subprocess
                result = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass

        raw_proc = platform.processor()
        if raw_proc and not raw_proc.startswith('Intel64 Family') and not raw_proc.startswith('AMD64 Family'):
            return raw_proc
        return raw_proc or 'Generic x86_64 Processor'

    @classmethod
    def get_platform_info(cls) -> Dict[str, str]:
        """
        Get platform information with accurate OS and Processor names.
        Cross-platform: Windows, Linux (Render/cloud), macOS.

        Returns:
            Dictionary with platform details
        """
        system = platform.system()

        if system == 'Windows':
            win_ver = cls.get_windows_version()
            sys_name = win_ver.get('name', system)
            release = win_ver.get('display_version') or platform.release()
            version = win_ver.get('build') or platform.version()
        elif system == 'Linux':
            # Try to get a friendly Linux distro name
            try:
                import distro
                sys_name = f"{distro.name()} {distro.version()}".strip()
            except ImportError:
                try:
                    with open('/etc/os-release') as f:
                        lines = dict(l.strip().split('=', 1) for l in f if '=' in l)
                    sys_name = lines.get('PRETTY_NAME', 'Linux').strip('"')
                except Exception:
                    sys_name = 'Linux'
            release = platform.release()
            version = platform.version()
        else:
            sys_name = system
            release = platform.release()
            version = platform.version()

        return {
            'system': sys_name,
            'release': release,
            'version': version,
            'architecture': platform.machine(),
            'processor': cls.get_processor_name(),
            'node': platform.node()
        }

    @classmethod
    def get_windows_version(cls) -> Dict[str, str]:
        """
        Get accurate Windows version information including Windows 11 detection.

        Returns:
            Dictionary with Windows version details
        """
        if platform.system() != 'Windows':
            return {
                'name': platform.system(),
                'version': platform.version(),
                'build': '',
                'display_version': '',
                'edition': ''
            }

        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')

            try:
                product_name = winreg.QueryValueEx(key, 'ProductName')[0]
            except Exception:
                product_name = 'Windows'

            try:
                build_str = winreg.QueryValueEx(key, 'CurrentBuild')[0]
            except Exception:
                build_str = platform.version()

            display_version = ''
            try:
                display_version = winreg.QueryValueEx(key, 'DisplayVersion')[0]
            except Exception:
                pass

            ubr = ''
            try:
                ubr = winreg.QueryValueEx(key, 'UBR')[0]
            except Exception:
                pass

            edition = ''
            try:
                edition = winreg.QueryValueEx(key, 'EditionID')[0]
            except Exception:
                pass

            winreg.CloseKey(key)
            winreg.CloseKey(registry)

            # Windows 11 Check: Build >= 22000 is Windows 11
            build_num = int(build_str) if build_str.isdigit() else 0
            if build_num >= 22000:
                os_name = product_name.replace('Windows 10', 'Windows 11')
            else:
                os_name = product_name

            full_build = f"{build_str}.{ubr}" if ubr else build_str

            return {
                'name': os_name,
                'version': f"Build {full_build}",
                'build': full_build,
                'display_version': display_version,
                'edition': edition
            }
        except Exception:
            return {
                'name': 'Windows',
                'version': platform.release(),
                'build': platform.version(),
                'display_version': '',
                'edition': ''
            }

    @classmethod
    def get_boot_time(cls) -> Optional[str]:
        """
        Get system boot time.

        Returns:
            Boot time as ISO formatted string or None
        """
        if not PSUTIL_AVAILABLE:
            return None

        try:
            boot_time = psutil.boot_time()
            from datetime import datetime
            return datetime.fromtimestamp(boot_time).isoformat()
        except Exception:
            return None

    @classmethod
    def get_uptime(cls) -> Dict[str, Any]:
        """
        Get system uptime.

        Returns:
            Dictionary with uptime information
        """
        if not PSUTIL_AVAILABLE:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'total_seconds': 0}

        try:
            boot_time = psutil.boot_time()
            import time
            uptime_seconds = time.time() - boot_time

            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)

            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'total_seconds': uptime_seconds
            }
        except Exception:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'total_seconds': 0}

    @classmethod
    def get_platform_system(cls) -> str:
        """
        Get the platform system name.

        Returns:
            Platform system name
        """
        return platform.system()

    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'

    @classmethod
    def is_linux(cls) -> bool:
        """Check if running on Linux."""
        return platform.system() == 'Linux'

    @classmethod
    def is_mac(cls) -> bool:
        """Check if running on macOS."""
        return platform.system() == 'Darwin'

    @classmethod
    def get_system_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dictionary with all system information
        """
        info = {
            'computer_name': cls.get_computer_name(),
            'username': cls.get_username(),
            'platform': cls.get_platform_info(),
            'boot_time': cls.get_boot_time(),
            'uptime': cls.get_uptime()
        }

        # Add Windows-specific info if applicable
        if cls.is_windows():
            info['windows_version'] = cls.get_windows_version()

        # Add CPU info
        info['cpu'] = cls.get_cpu_info()

        # Add memory info
        info['memory'] = cls.get_memory_info()

        return info

    @classmethod
    def get_cpu_info(cls) -> Dict[str, Any]:
        """
        Get basic CPU information.

        Returns:
            Dictionary with CPU details
        """
        if not PSUTIL_AVAILABLE:
            return {
                'processor': platform.processor(),
                'architecture': platform.machine(),
                'physical_cores': 'N/A',
                'logical_cores': 'N/A'
            }

        try:
            return {
                'processor': platform.processor() or 'Unknown',
                'architecture': platform.machine(),
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None
            }
        except Exception:
            return {
                'processor': platform.processor(),
                'architecture': platform.machine()
            }

    @classmethod
    def get_memory_info(cls) -> Dict[str, Any]:
        """
        Get basic memory information.

        Returns:
            Dictionary with memory details
        """
        if not PSUTIL_AVAILABLE:
            return {
                'total': 0,
                'available': 0
            }

        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            }
        except Exception:
            return {'total': 0, 'available': 0}

    @classmethod
    def get_motherboard_info(cls) -> Dict[str, str]:
        """
        Get motherboard information (Windows only).

        Returns:
            Dictionary with motherboard details
        """
        if not cls.is_windows():
            return {'manufacturer': 'N/A', 'product': 'N/A'}

        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(registry, r'SYSTEM\CurrentControlSet\Control\SystemInformation')

            info = {}
            try:
                info['manufacturer'] = winreg.QueryValueEx(key, 'SystemManufacturer')[0]
            except FileNotFoundError:
                info['manufacturer'] = 'Unknown'

            try:
                info['product'] = winreg.QueryValueEx(key, 'SystemProductName')[0]
            except FileNotFoundError:
                info['product'] = 'Unknown'

            winreg.CloseKey(key)
            winreg.CloseKey(registry)

            return info
        except Exception:
            return {'manufacturer': 'Unknown', 'product': 'Unknown'}

    @classmethod
    def get_bios_info(cls) -> Dict[str, str]:
        """
        Get BIOS information (Windows only).

        Returns:
            Dictionary with BIOS details
        """
        if not cls.is_windows():
            return {'vendor': 'N/A', 'version': 'N/A', 'date': 'N/A'}

        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(registry, r'HARDWARE\DESCRIPTION\System\BIOS')

            info = {}
            try:
                info['vendor'] = winreg.QueryValueEx(key, 'BIOSVendor')[0]
            except FileNotFoundError:
                info['vendor'] = 'Unknown'

            try:
                info['version'] = winreg.QueryValueEx(key, 'BIOSVersion')[0]
            except FileNotFoundError:
                info['version'] = 'Unknown'

            try:
                info['date'] = winreg.QueryValueEx(key, 'BIOSReleaseDate')[0]
            except FileNotFoundError:
                info['date'] = 'Unknown'

            winreg.CloseKey(key)
            winreg.CloseKey(registry)

            return info
        except Exception:
            return {'vendor': 'Unknown', 'version': 'Unknown', 'date': 'Unknown'}
