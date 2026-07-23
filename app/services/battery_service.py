"""
SupportSight Battery Service

Collects and provides detailed battery diagnostics.
Gracefully handles systems without batteries (desktops).
"""

from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class BatteryService:
    """
    Service for battery diagnostics and monitoring.

    Provides information about battery status, health,
    and charging. Handles systems without batteries gracefully.
    """

    @classmethod
    def has_battery(cls) -> bool:
        """
        Check if the system has a battery.

        Returns:
            True if battery is present, False otherwise
        """
        if not PSUTIL_AVAILABLE:
            return False

        try:
            battery = psutil.sensors_battery()
            return battery is not None
        except Exception:
            return False

    @classmethod
    def get_battery_status(cls) -> Optional[Dict[str, Any]]:
        """
        Get battery status information.

        Returns:
            Dictionary with battery details or None if no battery
        """
        if not PSUTIL_AVAILABLE:
            return cls._no_battery_status()

        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return cls._no_battery_status()

            return {
                'has_battery': True,
                'percent': battery.percent,
                'is_charging': battery.power_plugged,
                'is_plugged_in': battery.power_plugged,
                'seconds_left': battery.secsleft,
                'status': cls._get_status_string(battery),
                'health': cls._estimate_battery_health(battery)
            }
        except Exception:
            return cls._no_battery_status()

    @classmethod
    def _no_battery_status(cls) -> Dict[str, Any]:
        """Return status for systems without battery."""
        return {
            'has_battery': False,
            'percent': 100,
            'is_charging': True,
            'is_plugged_in': True,
            'seconds_left': -1,
            'status': 'Desktop System - No Battery',
            'health': 'N/A',
            'is_desktop': True
        }

    @classmethod
    def _get_status_string(cls, battery) -> str:
        """
        Get human-readable battery status string.

        Args:
            battery: psutil battery sensor object

        Returns:
            Status string
        """
        if battery.power_plugged:
            if battery.percent == 100:
                return 'Fully Charged'
            elif battery.percent >= 90:
                return 'Charging Complete'
            return 'Charging'
        else:
            if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
                return 'On Battery'
            elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
                return 'On Battery'
            return 'Discharging'

    @classmethod
    def _estimate_battery_health(cls, battery) -> str:
        """
        Estimate battery health based on available information.

        Args:
            battery: psutil battery sensor object

        Returns:
            Health estimate string
        """
        # Note: psutil doesn't provide cycle count or design capacity
        # We can make rough estimates based on behavior
        percent = battery.percent

        if percent >= 80:
            return 'Good'
        elif percent >= 50:
            return 'Fair'
        return 'Poor'

    @classmethod
    def get_percent(cls) -> float:
        """
        Get battery percentage.

        Returns:
            Battery percentage (0-100)
        """
        if not PSUTIL_AVAILABLE:
            return 100

        try:
            battery = psutil.sensors_battery()
            return battery.percent if battery else 100
        except Exception:
            return 100

    @classmethod
    def is_charging(cls) -> bool:
        """
        Check if battery is charging.

        Returns:
            True if charging, False otherwise
        """
        if not PSUTIL_AVAILABLE:
            return True

        try:
            battery = psutil.sensors_battery()
            return battery.power_plugged if battery else True
        except Exception:
            return True

    @classmethod
    def is_plugged_in(cls) -> bool:
        """
        Check if power is plugged in.

        Returns:
            True if plugged in, False otherwise
        """
        return cls.is_charging()

    @classmethod
    def get_time_remaining(cls) -> Optional[int]:
        """
        Get remaining time in seconds.

        Returns:
            Seconds remaining or None
        """
        if not PSUTIL_AVAILABLE:
            return -1

        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.secsleft
            return -1
        except Exception:
            return -1

    @classmethod
    def get_formatted_time_remaining(cls) -> str:
        """
        Get formatted time remaining string.

        Returns:
            Formatted time string
        """
        seconds = cls.get_time_remaining()

        if seconds == -1:
            return 'Calculating...'

        if seconds == psutil.POWER_TIME_UNLIMITED:
            return 'Unlimited'

        if seconds == psutil.POWER_TIME_UNKNOWN:
            return 'Unknown'

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f'{hours}h {minutes}m'
        return f'{minutes}m'

    @classmethod
    def get_battery_info(cls) -> Dict[str, Any]:
        """
        Get comprehensive battery information.

        Returns:
            Dictionary with all battery details
        """
        status = cls.get_battery_status()

        return {
            'has_battery': status.get('has_battery', False),
            'is_desktop': status.get('is_desktop', False),
            'percent': status.get('percent', 100),
            'is_charging': status.get('is_charging', True),
            'is_plugged_in': status.get('is_plugged_in', True),
            'time_remaining': status.get('seconds_left', -1),
            'time_remaining_formatted': cls.get_formatted_time_remaining(),
            'status': status.get('status', 'Unknown'),
            'health': status.get('health', 'Unknown'),
            'full_status': status
        }

    @classmethod
    def get_battery_health_status(cls, threshold: float = 20.0) -> Dict[str, Any]:
        """
        Get battery health status based on charge level.

        Args:
            threshold: Low battery threshold percentage

        Returns:
            Dictionary with health status
        """
        status = cls.get_battery_status()

        if not status.get('has_battery', False):
            return {
                'status': 'no_battery',
                'severity': 'info',
                'message': 'Desktop system - no battery present',
                'has_battery': False
            }

        percent = status.get('percent', 100)
        is_charging = status.get('is_charging', True)

        if is_charging:
            return {
                'status': 'charging',
                'severity': 'info',
                'message': f'Battery charging at {percent}%',
                'has_battery': True,
                'percent': percent
            }

        if percent <= threshold:
            return {
                'status': 'critical',
                'severity': 'danger',
                'message': f'Battery critically low at {percent}%',
                'has_battery': True,
                'percent': percent
            }
        elif percent <= threshold * 1.5:
            return {
                'status': 'warning',
                'severity': 'warning',
                'message': f'Battery low at {percent}%',
                'has_battery': True,
                'percent': percent
            }

        return {
            'status': 'healthy',
            'severity': 'success',
            'message': f'Battery at {percent}%',
            'has_battery': True,
            'percent': percent
        }
