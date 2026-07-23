"""
SupportSight Network Service

Collects and provides detailed network diagnostics and monitoring.
"""

import socket
import subprocess
import platform
from typing import Dict, List, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class NetworkService:
    """
    Service for network diagnostics and monitoring.

    Provides information about network interfaces,
    connections, DNS, and internet connectivity.
    """

    @classmethod
    def get_hostname(cls) -> str:
        """
        Get the system hostname.

        Returns:
            System hostname
        """
        return socket.gethostname()

    @classmethod
    def get_local_ip(cls) -> str:
        """
        Get local IP address.

        Returns:
            Local IP address or 'N/A'
        """
        try:
            # Create a socket and connect to an external server
            # This doesn't actually send data, just determines the routing
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            try:
                # Connect to a public DNS server (doesn't send data)
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
            finally:
                s.close()
            return local_ip
        except Exception:
            # Fallback: try to get from hostname
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip.startswith('127.'):
                    return 'N/A'
                return local_ip
            except Exception:
                return 'N/A'

    @classmethod
    def get_public_ip(cls, timeout: int = 5) -> Optional[str]:
        """
        Get public IP address.

        Args:
            timeout: Request timeout in seconds

        Returns:
            Public IP address or None
        """
        try:
            import requests
            response = requests.get('https://api.ipify.org', timeout=timeout)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass

        try:
            import requests
            response = requests.get('https://icanhazip.com', timeout=timeout)
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            pass

        return None

    @classmethod
    def get_interfaces(cls) -> Dict[str, List[str]]:
        """
        Get network interfaces and their addresses.

        Returns:
            Dictionary mapping interface names to addresses
        """
        if not PSUTIL_AVAILABLE:
            return {}

        interfaces = {}
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                addresses = []
                for addr in addrs:
                    addresses.append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                interfaces[interface] = addresses
        except Exception:
            pass

        return interfaces

    @classmethod
    def get_interface_stats(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get network interface statistics.

        Returns:
            Dictionary with interface statistics
        """
        if not PSUTIL_AVAILABLE:
            return {}

        stats = {}
        try:
            for interface, net_stats in psutil.net_io_counters(pernic=True).items():
                stats[interface] = {
                    'bytes_sent': net_stats.bytes_sent,
                    'bytes_recv': net_stats.bytes_recv,
                    'packets_sent': net_stats.packets_sent,
                    'packets_recv': net_stats.packets_recv,
                    'errin': net_stats.errin,
                    'errout': net_stats.errout,
                    'dropin': net_stats.dropin,
                    'dropout': net_stats.dropout
                }
        except Exception:
            pass

        return stats

    @classmethod
    def get_dns_servers(cls) -> List[str]:
        """
        Get DNS servers.

        Returns:
            List of DNS server addresses
        """
        if not PSUTIL_AVAILABLE:
            return []

        dns_servers = []
        try:
            for name, servers in psutil.net_if_stats().items():
                # psutil doesn't directly provide DNS, try other methods
                pass
        except Exception:
            pass

        # Try to read from system
        if cls.is_windows():
            try:
                import subprocess
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'DNS Servers' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            dns = parts[1].strip()
                            if dns and dns not in dns_servers:
                                dns_servers.append(dns)
            except Exception:
                pass

        return dns_servers

    @classmethod
    def get_default_gateway(cls) -> Optional[str]:
        """
        Get default gateway address.

        Returns:
            Gateway IP address or None
        """
        if not PSUTIL_AVAILABLE:
            return None

        try:
            # Get default gateway from routing table
            if cls.is_windows():
                result = subprocess.run(
                    ['route', 'print', '0.0.0.0'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
            else:
                # Linux
                result = subprocess.run(
                    ['ip', 'route', 'show', 'default'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                parts = result.stdout.split()
                if parts and parts[0] == 'default':
                    for i, part in enumerate(parts):
                        if part == 'via' and i + 1 < len(parts):
                            return parts[i + 1]
        except Exception:
            pass

        return None

    @classmethod
    def check_internet_connectivity(cls, host: str = '8.8.8.8', timeout: int = 3) -> Dict[str, Any]:
        """
        Check internet connectivity.

        Args:
            host: Host to ping for connectivity check
            timeout: Timeout in seconds

        Returns:
            Dictionary with connectivity status
        """
        result = {
            'connected': False,
            'latency': None,
            'host': host
        }

        try:
            if cls.is_windows():
                ping_result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), host],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1
                )
            else:
                ping_result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), host],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1
                )

            result['connected'] = ping_result.returncode == 0

            # Extract latency
            if result['connected'] and ping_result.stdout:
                output = ping_result.stdout
                if 'time=' in output:
                    try:
                        time_part = output.split('time=')[1].split()[0]
                        result['latency'] = float(time_part)
                    except (ValueError, IndexError):
                        pass

        except subprocess.TimeoutExpired:
            result['connected'] = False
        except Exception:
            result['connected'] = False

        return result

    @classmethod
    def ping_host(cls, host: str, count: int = 4, timeout: int = 5) -> Dict[str, Any]:
        """
        Ping a host.

        Args:
            host: Host to ping
            count: Number of pings
            timeout: Timeout in seconds

        Returns:
            Dictionary with ping results
        """
        result = {
            'host': host,
            'packets_sent': 0,
            'packets_received': 0,
            'packet_loss': 100.0,
            'min_latency': None,
            'max_latency': None,
            'avg_latency': None,
            'success': False
        }

        try:
            if cls.is_windows():
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]

            ping_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout * count + 5
            )

            output = ping_result.stdout

            # Parse results
            if 'Received' in output or 'received' in output:
                for line in output.split('\n'):
                    if 'Received' in line or 'received' in line:
                        parts = line.replace('Received', 'received').split(',')
                        for part in parts:
                            if 'sent' in part.lower():
                                try:
                                    result['packets_sent'] = int(part.split()[0])
                                except (ValueError, IndexError):
                                    pass
                            if 'received' in part.lower():
                                try:
                                    result['packets_received'] = int(part.split()[0])
                                except (ValueError, IndexError):
                                    pass

                    if 'Minimum' in line or 'minimum' in line:
                        try:
                            if cls.is_windows():
                                times = line.split('Minimum = ')[1].split('ms')[0]
                                result['min_latency'] = float(times)
                            else:
                                times = line.split('min/avg/max = ')[1].split('/')
                                result['min_latency'] = float(times[0])
                                result['avg_latency'] = float(times[1])
                                result['max_latency'] = float(times[2])
                        except (IndexError, ValueError):
                            pass

                    if not cls.is_windows() and 'min/avg/max' in line:
                        try:
                            times = line.split('=')[1].split('/')
                            result['min_latency'] = float(times[0])
                            result['avg_latency'] = float(times[1])
                            result['max_latency'] = float(times[2])
                        except (IndexError, ValueError):
                            pass

            if result['packets_sent'] > 0:
                result['packet_loss'] = (
                    (result['packets_sent'] - result['packets_received']) /
                    result['packets_sent'] * 100
                )
                result['success'] = result['packets_received'] > 0

        except Exception:
            pass

        return result

    @classmethod
    def get_connections(cls, kind: str = 'inet') -> List[Dict[str, Any]]:
        """
        Get network connections.

        Args:
            kind: Type of connections ('inet', 'inet4', 'inet6', 'tcp', 'udp')

        Returns:
            List of connection dictionaries
        """
        if not PSUTIL_AVAILABLE:
            return []

        connections = []
        try:
            for conn in psutil.net_connections(kind=kind):
                try:
                    connections.append({
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    })
                except Exception:
                    continue
        except Exception:
            pass

        return connections

    @classmethod
    def get_network_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive network information.

        Returns:
            Dictionary with all network details
        """
        return {
            'hostname': cls.get_hostname(),
            'local_ip': cls.get_local_ip(),
            'public_ip': cls.get_public_ip(),
            'interfaces': cls.get_interfaces(),
            'interface_stats': cls.get_interface_stats(),
            'dns_servers': cls.get_dns_servers(),
            'default_gateway': cls.get_default_gateway(),
            'internet_connectivity': cls.check_internet_connectivity()
        }

    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'

    @classmethod
    def get_connection_quality(cls) -> Dict[str, Any]:
        """
        Get connection quality metrics.

        Returns:
            Dictionary with quality metrics
        """
        connectivity = cls.check_internet_connectivity()

        quality = 'unknown'
        severity = 'info'

        if connectivity['connected']:
            if connectivity['latency'] is not None:
                if connectivity['latency'] < 50:
                    quality = 'excellent'
                    severity = 'success'
                elif connectivity['latency'] < 100:
                    quality = 'good'
                    severity = 'success'
                elif connectivity['latency'] < 200:
                    quality = 'fair'
                    severity = 'warning'
                else:
                    quality = 'poor'
                    severity = 'warning'
            else:
                quality = 'connected'
                severity = 'success'
        else:
            quality = 'disconnected'
            severity = 'danger'

        return {
            'quality': quality,
            'severity': severity,
            'latency': connectivity.get('latency'),
            'connected': connectivity['connected']
        }
