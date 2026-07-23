"""
SupportSight Recommendation Service

Generates actionable recommendations based on system diagnostics.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.battery_service import BatteryService
from app.services.network_service import NetworkService


@dataclass
class Recommendation:
    """Represents a diagnostic recommendation."""
    component: str
    severity: str
    title: str
    description: str
    action_items: List[str]
    priority: int


class RecommendationService:
    """
    Service for generating system recommendations.

    Analyzes diagnostic data and provides actionable
    recommendations to improve system health.
    """

    # Component constants
    COMPONENT_CPU = 'cpu'
    COMPONENT_RAM = 'ram'
    COMPONENT_DISK = 'disk'
    COMPONENT_NETWORK = 'network'
    COMPONENT_BATTERY = 'battery'
    COMPONENT_GENERAL = 'general'

    # Severity constants
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_WARNING = 'warning'
    SEVERITY_INFO = 'info'

    @classmethod
    def generate_recommendations(cls, diagnostic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on diagnostic data.

        Args:
            diagnostic_data: Complete diagnostic data

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # CPU recommendations
        cpu_data = diagnostic_data.get('cpu', {})
        recommendations.extend(cls._analyze_cpu(cpu_data))

        # RAM recommendations
        ram_data = diagnostic_data.get('ram', {})
        recommendations.extend(cls._analyze_ram(ram_data))

        # Disk recommendations
        disk_data = diagnostic_data.get('disk', {})
        recommendations.extend(cls._analyze_disk(disk_data))

        # Battery recommendations
        battery_data = diagnostic_data.get('battery', {})
        recommendations.extend(cls._analyze_battery(battery_data))

        # Network recommendations
        network_data = diagnostic_data.get('network', {})
        recommendations.extend(cls._analyze_network(network_data))

        # Sort by priority (lower = higher priority)
        recommendations.sort(key=lambda x: x.get('priority', 999))

        return recommendations

    @classmethod
    def _analyze_cpu(cls, cpu_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze CPU data and generate recommendations."""
        recommendations = []

        usage = cpu_data.get('usage', 0)
        avg_usage = cpu_data.get('average_usage', usage)
        effective_usage = (usage + avg_usage) / 2

        if effective_usage >= 90:
            recommendations.append({
                'component': cls.COMPONENT_CPU,
                'severity': cls.SEVERITY_CRITICAL,
                'title': 'Critical CPU Usage',
                'description': f'Your CPU is under heavy load at {effective_usage:.1f}%. '
                               'This can cause system slowdown and responsiveness issues.',
                'action_items': [
                    'Close unnecessary applications and browser tabs',
                    'Check Task Manager for processes consuming high CPU',
                    'Consider ending resource-intensive background processes',
                    'Run a malware scan to check for malicious software',
                    'Consider upgrading your CPU if usage is consistently high'
                ],
                'priority': 1
            })
        elif effective_usage >= 80:
            recommendations.append({
                'component': cls.COMPONENT_CPU,
                'severity': cls.SEVERITY_WARNING,
                'title': 'High CPU Usage',
                'description': f'Your CPU usage is elevated at {effective_usage:.1f}%. '
                               'Consider reducing system load.',
                'action_items': [
                    'Review running processes in Task Manager',
                    'Close unused applications',
                    'Disable startup programs you don\'t need',
                    'Check for Windows updates'
                ],
                'priority': 3
            })
        elif effective_usage >= 70:
            recommendations.append({
                'component': cls.COMPONENT_CPU,
                'severity': cls.SEVERITY_INFO,
                'title': 'Moderate CPU Usage',
                'description': f'CPU usage is at {effective_usage:.1f}%. '
                               'This is normal during active use.',
                'action_items': [
                    'Monitor usage patterns',
                    'Keep applications updated'
                ],
                'priority': 5
            })

        return recommendations

    @classmethod
    def _analyze_ram(cls, ram_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze RAM data and generate recommendations."""
        recommendations = []

        memory = ram_data.get('memory', {})
        usage = memory.get('percent', 0)
        avg_usage = ram_data.get('average_usage', usage)
        effective_usage = (usage + avg_usage) / 2

        if effective_usage >= 95:
            recommendations.append({
                'component': cls.COMPONENT_RAM,
                'severity': cls.SEVERITY_CRITICAL,
                'title': 'Critical Memory Usage',
                'description': f'Your system is running critically low on memory at {effective_usage:.1f}%. '
                               'This can cause system instability and crashes.',
                'action_items': [
                    'Save all open work immediately',
                    'Restart your computer',
                    'Check for memory leaks in applications',
                    'Consider adding more RAM',
                    'Close all unnecessary applications'
                ],
                'priority': 1
            })
        elif effective_usage >= 85:
            recommendations.append({
                'component': cls.COMPONENT_RAM,
                'severity': cls.SEVERITY_WARNING,
                'title': 'High Memory Usage',
                'description': f'Memory usage is high at {effective_usage:.1f}%. '
                               'The system may be using virtual memory (disk).',
                'action_items': [
                    'Close unused applications',
                    'Check for memory-hungry browser extensions',
                    'Consider increasing virtual memory',
                    'Run Disk Cleanup to free up resources'
                ],
                'priority': 2
            })
        elif effective_usage >= 70:
            recommendations.append({
                'component': cls.COMPONENT_RAM,
                'severity': cls.SEVERITY_INFO,
                'title': 'Elevated Memory Usage',
                'description': f'Memory usage is at {effective_usage:.1f}%. '
                               'Consider closing unused applications.',
                'action_items': [
                    'Review open applications',
                    'Clear browser cache periodically'
                ],
                'priority': 4
            })

        return recommendations

    @classmethod
    def _analyze_disk(cls, disk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze disk data and generate recommendations."""
        recommendations = []

        partitions = disk_data.get('partitions', [])
        critical_partitions = []
        warning_partitions = []

        for partition in partitions:
            usage = partition.get('percent', 0)
            if usage >= 95:
                critical_partitions.append((partition.get('mountpoint', 'Unknown'), usage))
            elif usage >= 85:
                warning_partitions.append((partition.get('mountpoint', 'Unknown'), usage))

        for mountpoint, usage in critical_partitions:
            recommendations.append({
                'component': cls.COMPONENT_DISK,
                'severity': cls.SEVERITY_CRITICAL,
                'title': f'Disk Space Critical on {mountpoint}',
                'description': f'Drive {mountpoint} has only {100-usage:.1f}% free space remaining. '
                               'Low disk space can cause system crashes and prevent updates.',
                'action_items': [
                    'Run Disk Cleanup immediately',
                    'Delete temporary files (Ctrl+Shift+Delete)',
                    'Uninstall unused applications',
                    'Move large files to external storage',
                    'Consider upgrading to a larger drive'
                ],
                'priority': 1
            })

        for mountpoint, usage in warning_partitions:
            recommendations.append({
                'component': cls.COMPONENT_DISK,
                'severity': cls.SEVERITY_WARNING,
                'title': f'Low Disk Space on {mountpoint}',
                'description': f'Drive {mountpoint} has only {100-usage:.1f}% free space. '
                               'Consider freeing up some space.',
                'action_items': [
                    'Run Windows Disk Cleanup',
                    'Empty Recycle Bin',
                    'Delete temporary internet files',
                    'Remove unused programs',
                    'Move media files to another drive'
                ],
                'priority': 2
            })

        # Check for SSD vs HDD
        for partition in partitions:
            fs_type = partition.get('filesystem', '').lower()
            mountpoint = partition.get('mountpoint', '')
            if 'hdd' in str(disk_data) or 'ssd' in str(disk_data):
                disk_type = disk_data.get('disk_type', {})
                if disk_type.get('type') == 'hdd' and mountpoint in ['C:', '/']:
                    recommendations.append({
                        'component': cls.COMPONENT_DISK,
                        'severity': cls.SEVERITY_INFO,
                        'title': 'Traditional Hard Drive Detected',
                        'description': 'Your system is using a traditional hard drive. '
                                       'Consider upgrading to SSD for better performance.',
                        'action_items': [
                            'Consider migrating to an SSD',
                            'Defragment HDD if needed (not for SSD)',
                            'Enable write caching for better performance'
                        ],
                        'priority': 6
                    })
                break

        return recommendations

    @classmethod
    def _analyze_battery(cls, battery_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze battery data and generate recommendations."""
        recommendations = []

        if not battery_data.get('has_battery', False):
            return recommendations

        percent = battery_data.get('percent', 100)
        is_charging = battery_data.get('is_charging', False)

        if not is_charging and percent <= 10:
            recommendations.append({
                'component': cls.COMPONENT_BATTERY,
                'severity': cls.SEVERITY_CRITICAL,
                'title': 'Critical Battery Level',
                'description': f'Battery is at {percent}%. Connect to power immediately '
                               'to prevent data loss.',
                'action_items': [
                    'Connect to power outlet immediately',
                    'Save all open work',
                    'Consider shutting down if you cannot charge'
                ],
                'priority': 1
            })
        elif not is_charging and percent <= 20:
            recommendations.append({
                'component': cls.COMPONENT_BATTERY,
                'severity': cls.SEVERITY_WARNING,
                'title': 'Low Battery',
                'description': f'Battery is at {percent}%. Find a power source soon.',
                'action_items': [
                    'Connect to power outlet',
                    'Save your work',
                    'Consider reducing screen brightness'
                ],
                'priority': 2
            })
        elif is_charging and percent >= 95:
            recommendations.append({
                'component': cls.COMPONENT_BATTERY,
                'severity': cls.SEVERITY_INFO,
                'title': 'Battery Fully Charged',
                'description': f'Battery is at {percent}%. You may unplug for optimal battery health.',
                'action_items': [
                    'Unplug to avoid overcharging',
                    'Consider using the laptop on battery periodically'
                ],
                'priority': 5
            })

        # Battery health check
        health = battery_data.get('health', 'Good')
        if health == 'Poor':
            recommendations.append({
                'component': cls.COMPONENT_BATTERY,
                'severity': cls.SEVERITY_WARNING,
                'title': 'Battery Health Degraded',
                'description': 'Your battery health has degraded. Consider replacement.',
                'action_items': [
                    'Consider replacing the battery',
                    'Monitor battery capacity',
                    'Avoid keeping laptop plugged in constantly'
                ],
                'priority': 3
            })

        return recommendations

    @classmethod
    def _analyze_network(cls, network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze network data and generate recommendations."""
        recommendations = []

        connectivity = network_data.get('internet_connectivity', {})
        is_connected = connectivity.get('connected', False)

        if not is_connected:
            recommendations.append({
                'component': cls.COMPONENT_NETWORK,
                'severity': cls.SEVERITY_CRITICAL,
                'title': 'No Internet Connection',
                'description': 'Your system cannot connect to the internet. '
                               'Check your network adapter and connection.',
                'action_items': [
                    'Check if Wi-Fi/Ethernet is enabled',
                    'Restart your router/modem',
                    'Check network cable connection',
                    'Run Windows Network Troubleshooter',
                    'Check if the website is down'
                ],
                'priority': 1
            })
            return recommendations

        latency = connectivity.get('latency')
        if latency is not None:
            if latency >= 300:
                recommendations.append({
                    'component': cls.COMPONENT_NETWORK,
                    'severity': cls.SEVERITY_WARNING,
                    'title': 'High Network Latency',
                    'description': f'Network latency is {latency}ms. This may cause slow connections.',
                    'action_items': [
                        'Try restarting your router',
                        'Check for network congestion',
                        'Consider using a wired connection',
                        'Contact your ISP if issue persists'
                    ],
                    'priority': 3
                })
            elif latency >= 150:
                recommendations.append({
                    'component': cls.COMPONENT_NETWORK,
                    'severity': cls.SEVERITY_INFO,
                    'title': 'Moderate Network Latency',
                    'description': f'Network latency is {latency}ms. Connection is usable but could be better.',
                    'action_items': [
                        'Close bandwidth-intensive applications',
                        'Check for background downloads',
                        'Consider upgrading your internet plan'
                    ],
                    'priority': 4
                })

        return recommendations

    @classmethod
    def get_recommendations_for_scan(cls, scan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recommendations for a completed scan.

        Args:
            scan_data: Scan data dictionary

        Returns:
            List of recommendations
        """
        return cls.generate_recommendations(scan_data)

    @classmethod
    def get_summary(cls, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of recommendations.

        Args:
            recommendations: List of recommendations

        Returns:
            Summary dictionary
        """
        critical = [r for r in recommendations if r['severity'] == cls.SEVERITY_CRITICAL]
        warnings = [r for r in recommendations if r['severity'] == cls.SEVERITY_WARNING]
        info = [r for r in recommendations if r['severity'] == cls.SEVERITY_INFO]

        return {
            'total': len(recommendations),
            'critical': len(critical),
            'warnings': len(warnings),
            'info': len(info),
            'action_required': len(critical) > 0 or len(warnings) > 0
        }
