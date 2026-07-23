"""
SupportSight Health Score Service

Calculates and provides system health scores based on
CPU, RAM, disk, battery, and network diagnostics.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.battery_service import BatteryService
from app.services.network_service import NetworkService


@dataclass
class HealthComponent:
    """Represents a health score component."""
    name: str
    score: float
    weight: float
    status: str
    details: Dict[str, Any]


class HealthScoreService:
    """
    Service for calculating system health scores.

    Provides comprehensive health scoring based on multiple
    system components with configurable weights.
    """

    # Default component weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'cpu': 0.25,
        'ram': 0.25,
        'disk': 0.20,
        'battery': 0.15,
        'network': 0.15
    }

    # Health thresholds
    THRESHOLDS = {
        'cpu': {'warning': 70, 'critical': 85},
        'ram': {'warning': 75, 'critical': 90},
        'disk': {'warning': 80, 'critical': 90},
        'battery': {'warning': 30, 'critical': 15},
        'network': {'warning': 200, 'critical': 500}  # latency in ms
    }

    @classmethod
    def calculate_component_score(cls, component: str, data: Dict[str, Any]) -> HealthComponent:
        """
        Calculate health score for a single component.

        Args:
            component: Component name
            data: Component data

        Returns:
            HealthComponent with score and details
        """
        weights = cls.DEFAULT_WEIGHTS
        thresholds = cls.THRESHOLDS

        if component == 'cpu':
            return cls._calculate_cpu_score(data, weights['cpu'], thresholds['cpu'])
        elif component == 'ram':
            return cls._calculate_ram_score(data, weights['ram'], thresholds['ram'])
        elif component == 'disk':
            return cls._calculate_disk_score(data, weights['disk'], thresholds['disk'])
        elif component == 'battery':
            return cls._calculate_battery_score(data, weights['battery'], thresholds['battery'])
        elif component == 'network':
            return cls._calculate_network_score(data, weights['network'], thresholds['network'])

        return HealthComponent(
            name=component,
            score=50,
            weight=0,
            status='unknown',
            details={}
        )

    @classmethod
    def _calculate_cpu_score(cls, data: Dict[str, Any], weight: float,
                              thresholds: Dict[str, float]) -> HealthComponent:
        """Calculate CPU health score."""
        usage = data.get('usage', 0)
        avg_usage = data.get('average_usage', usage)

        # Use average usage for more stable scoring
        effective_usage = (usage + avg_usage) / 2

        # Calculate score (100 = excellent, 0 = critical)
        score = cls._usage_to_score(effective_usage, thresholds['critical'], thresholds['warning'])

        return HealthComponent(
            name='cpu',
            score=score,
            weight=weight,
            status=cls._get_status(score),
            details={
                'current_usage': usage,
                'average_usage': avg_usage,
                'usage': effective_usage,
                'threshold_warning': thresholds['warning'],
                'threshold_critical': thresholds['critical']
            }
        )

    @classmethod
    def _calculate_ram_score(cls, data: Dict[str, Any], weight: float,
                              thresholds: Dict[str, float]) -> HealthComponent:
        """Calculate RAM health score."""
        memory = data.get('memory', {})
        usage = memory.get('percent', 0)
        avg_usage = data.get('average_usage', usage)

        effective_usage = (usage + avg_usage) / 2
        score = cls._usage_to_score(effective_usage, thresholds['critical'], thresholds['warning'])

        return HealthComponent(
            name='ram',
            score=score,
            weight=weight,
            status=cls._get_status(score),
            details={
                'current_usage': usage,
                'average_usage': avg_usage,
                'usage': effective_usage,
                'total': memory.get('total', 0),
                'used': memory.get('used', 0),
                'available': memory.get('available', 0),
                'threshold_warning': thresholds['warning'],
                'threshold_critical': thresholds['critical']
            }
        )

    @classmethod
    def _calculate_disk_score(cls, data: Dict[str, Any], weight: float,
                               thresholds: Dict[str, float]) -> HealthComponent:
        """Calculate disk health score."""
        partitions = data.get('partitions', [])

        if not partitions:
            return HealthComponent(
                name='disk',
                score=100,
                weight=weight,
                status='healthy',
                details={'message': 'No partitions found'}
            )

        # Calculate worst-case score across all partitions
        worst_score = 100
        worst_partition = None
        partition_scores = []

        for partition in partitions:
            usage = partition.get('percent', 0)
            score = cls._usage_to_score(usage, thresholds['critical'], thresholds['warning'])
            partition_scores.append({
                'mountpoint': partition.get('mountpoint', 'Unknown'),
                'usage': usage,
                'score': score
            })

            if score < worst_score:
                worst_score = score
                worst_partition = partition.get('mountpoint', 'Unknown')

        return HealthComponent(
            name='disk',
            score=worst_score,
            weight=weight,
            status=cls._get_status(worst_score),
            details={
                'partition_scores': partition_scores,
                'worst_partition': worst_partition,
                'threshold_warning': thresholds['warning'],
                'threshold_critical': thresholds['critical']
            }
        )

    @classmethod
    def _calculate_battery_score(cls, data: Dict[str, Any], weight: float,
                                  thresholds: Dict[str, float]) -> HealthComponent:
        """Calculate battery health score."""
        if not data.get('has_battery', False):
            return HealthComponent(
                name='battery',
                score=100,
                weight=weight,
                status='healthy',
                details={'message': 'No battery (desktop system)'}
            )

        percent = data.get('percent', 100)
        is_charging = data.get('is_charging', False)

        # If charging, battery is fine
        if is_charging:
            score = 100
            status = 'healthy'
        else:
            # Calculate based on remaining charge
            score = (percent / 100) * 100
            if percent <= thresholds['critical']:
                status = 'critical'
            elif percent <= thresholds['warning']:
                status = 'warning'
            else:
                status = 'healthy'

        return HealthComponent(
            name='battery',
            score=score,
            weight=weight,
            status=status,
            details={
                'percent': percent,
                'is_charging': is_charging,
                'time_remaining': data.get('time_remaining_formatted', 'N/A'),
                'health': data.get('health', 'Unknown'),
                'threshold_warning': thresholds['warning'],
                'threshold_critical': thresholds['critical']
            }
        )

    @classmethod
    def _calculate_network_score(cls, data: Dict[str, Any], weight: float,
                                  thresholds: Dict[str, float]) -> HealthComponent:
        """Calculate network health score."""
        connectivity = data.get('internet_connectivity', {})
        is_connected = connectivity.get('connected', False)

        if not is_connected:
            return HealthComponent(
                name='network',
                score=0,
                weight=weight,
                status='critical',
                details={
                    'connected': False,
                    'message': 'No internet connection'
                }
            )

        latency = connectivity.get('latency')
        if latency is None:
            # Connected but couldn't measure latency
            score = 75
            status = 'fair'
        else:
            score = cls._latency_to_score(latency, thresholds['critical'], thresholds['warning'])
            status = cls._get_status(score)

        return HealthComponent(
            name='network',
            score=score,
            weight=weight,
            status=status,
            details={
                'connected': True,
                'latency': latency,
                'local_ip': data.get('local_ip', 'N/A'),
                'public_ip': data.get('public_ip', 'N/A'),
                'threshold_warning': thresholds['warning'],
                'threshold_critical': thresholds['critical']
            }
        )

    @classmethod
    def _usage_to_score(cls, usage: float, critical_threshold: float,
                        warning_threshold: float) -> float:
        """
        Convert usage percentage to health score.

        Args:
            usage: Usage percentage (0-100)
            critical_threshold: Threshold for critical status
            warning_threshold: Threshold for warning status

        Returns:
            Health score (0-100)
        """
        if usage >= critical_threshold:
            # Linear scale from critical_threshold to 100
            # At critical_threshold, score = 20
            # At 100, score = 0
            scale = 20 / (100 - critical_threshold)
            score = 20 - (usage - critical_threshold) * scale
            return max(0, min(20, score))
        elif usage >= warning_threshold:
            # Linear scale from warning_threshold to critical_threshold
            # At warning_threshold, score = 60
            # At critical_threshold, score = 20
            scale = 40 / (critical_threshold - warning_threshold)
            score = 60 - (usage - warning_threshold) * scale
            return max(20, min(60, score))
        else:
            # Linear scale from 0 to warning_threshold
            # At 0, score = 100
            # At warning_threshold, score = 60
            scale = 40 / warning_threshold
            score = 100 - usage * scale
            return max(60, min(100, score))

    @classmethod
    def _latency_to_score(cls, latency: float, critical_threshold: float,
                           warning_threshold: float) -> float:
        """
        Convert latency to health score.

        Args:
            latency: Latency in milliseconds
            critical_threshold: Threshold for critical status
            warning_threshold: Threshold for warning status

        Returns:
            Health score (0-100)
        """
        if latency >= critical_threshold:
            scale = 20 / (critical_threshold - warning_threshold)
            score = 20 - (latency - critical_threshold) * scale
            return max(0, min(20, score))
        elif latency >= warning_threshold:
            scale = 40 / (critical_threshold - warning_threshold)
            score = 60 - (latency - warning_threshold) * scale
            return max(20, min(60, score))
        else:
            scale = 40 / warning_threshold
            score = 100 - latency * scale
            return max(60, min(100, score))

    @classmethod
    def _get_status(cls, score: float) -> str:
        """Get status string from score."""
        if score >= 80:
            return 'healthy'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'warning'
        return 'critical'

    @classmethod
    def calculate_overall_score(cls, components: List[HealthComponent]) -> float:
        """
        Calculate overall health score from components.

        Args:
            components: List of HealthComponent objects

        Returns:
            Overall health score (0-100)
        """
        if not components:
            return 0

        total_weight = sum(c.weight for c in components)
        if total_weight == 0:
            return 0

        weighted_sum = sum(c.score * c.weight for c in components)
        return round(weighted_sum / total_weight, 1)

    @classmethod
    def get_overall_health(cls) -> Dict[str, Any]:
        """
        Get overall system health score.

        Returns:
            Dictionary with health score and component details
        """
        # Collect all diagnostic data
        cpu_data = CPUService.get_cpu_info()
        ram_data = RAMService.get_memory_info()
        disk_data = DiskService.get_disk_info()
        battery_data = BatteryService.get_battery_info()
        network_data = NetworkService.get_network_info()

        # Calculate component scores
        cpu_component = cls._calculate_cpu_score(cpu_data, cls.DEFAULT_WEIGHTS['cpu'],
                                                   cls.THRESHOLDS['cpu'])
        ram_component = cls._calculate_ram_score(ram_data, cls.DEFAULT_WEIGHTS['ram'],
                                                   cls.THRESHOLDS['ram'])
        disk_component = cls._calculate_disk_score(disk_data, cls.DEFAULT_WEIGHTS['disk'],
                                                     cls.THRESHOLDS['disk'])
        battery_component = cls._calculate_battery_score(battery_data, cls.DEFAULT_WEIGHTS['battery'],
                                                           cls.THRESHOLDS['battery'])
        network_component = cls._calculate_network_score(network_data, cls.DEFAULT_WEIGHTS['network'],
                                                           cls.THRESHOLDS['network'])

        components = [cpu_component, ram_component, disk_component, battery_component, network_component]
        overall_score = cls.calculate_overall_score(components)

        return {
            'overall_score': overall_score,
            'category': cls.get_health_category(overall_score),
            'components': [c.__dict__ for c in components],
            'cpu': cpu_data,
            'ram': ram_data,
            'disk': disk_data,
            'battery': battery_data,
            'network': network_data
        }

    @classmethod
    def get_health_category(cls, score: float) -> str:
        """
        Get health category from score.

        Args:
            score: Health score (0-100)

        Returns:
            Category string
        """
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        return 'Poor'

    @classmethod
    def get_health_color(cls, score: float) -> str:
        """
        Get color code for health score.

        Args:
            score: Health score (0-100)

        Returns:
            Hex color code
        """
        if score >= 80:
            return '#28a745'  # Green
        elif score >= 60:
            return '#ffc107'  # Yellow
        elif score >= 40:
            return '#fd7e14'  # Orange
        return '#dc3545'  # Red

    @classmethod
    def get_quick_health_check(cls) -> Dict[str, Any]:
        """
        Get a quick health check summary.

        Returns:
            Dictionary with quick health status
        """
        cpu_status = CPUService.get_cpu_health_status()
        ram_status = RAMService.get_memory_health_status()
        connectivity = NetworkService.check_internet_connectivity()

        issues = []
        if cpu_status['is_critical']:
            issues.append('High CPU usage')
        elif cpu_status['is_warning']:
            issues.append('Elevated CPU usage')

        if ram_status['is_critical']:
            issues.append('High memory usage')
        elif ram_status['is_warning']:
            issues.append('Elevated memory usage')

        if not connectivity['connected']:
            issues.append('No internet connection')

        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'cpu_status': cpu_status,
            'ram_status': ram_status,
            'network_status': connectivity
        }
