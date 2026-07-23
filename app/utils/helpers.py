"""
SupportSight Helper Functions

Reusable utility functions for formatting and calculations.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict, Any


def format_bytes(bytes_value: Optional[Union[int, float]], precision: int = 2) -> str:
    """
    Convert bytes to human-readable format.

    Args:
        bytes_value: Number of bytes
        precision: Decimal precision

    Returns:
        Formatted string (e.g., "1.50 GB")

    Example:
        >>> format_bytes(1073741824)
        '1.00 GB'
    """
    if bytes_value is None or bytes_value < 0:
        return '0 B'

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    value = float(bytes_value)

    while value >= 1024.0 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    return f'{value:.{precision}f} {units[unit_index]}'


def format_percentage(value: Optional[Union[int, float]], precision: int = 1) -> str:
    """
    Format a value as a percentage.

    Args:
        value: Numeric value (0-100 or 0-1)
        precision: Decimal precision

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(85.5)
        '85.5%'
    """
    if value is None:
        return '0%'

    # If value > 1, assume it's already a percentage
    if value > 1:
        return f'{value:.{precision}f}%'

    # Otherwise, convert from decimal
    return f'{value * 100:.{precision}f}%'


def format_datetime(dt: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format a datetime object as a string.

    Args:
        dt: datetime object or ISO string
        format_str: strftime format string

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ''

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt

    return dt.strftime(format_str)


def format_duration(seconds: Optional[float]) -> str:
    """
    Format duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string

    Example:
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds is None:
        return '0s'

    seconds = int(seconds)
    if seconds < 60:
        return f'{seconds}s'

    minutes = seconds // 60
    seconds = seconds % 60

    if minutes < 60:
        return f'{minutes}m {seconds}s'

    hours = minutes // 60
    minutes = minutes % 60

    return f'{hours}h {minutes}m {seconds}s'


def calculate_percentage(part: Union[int, float], total: Union[int, float], 
                         precision: int = 1) -> float:
    """
    Calculate percentage with safe division.

    Args:
        part: Numerator value
        total: Denominator value
        precision: Decimal precision

    Returns:
        Percentage value
    """
    if total == 0 or total is None:
        return 0.0

    return round((part / total) * 100, precision)


def safe_divide(numerator: Union[int, float], denominator: Union[int, float],
                default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails

    Returns:
        Result of division or default
    """
    if denominator == 0 or denominator is None:
        return default

    return numerator / denominator


def truncate_string(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def get_severity_color(severity: str) -> str:
    """
    Get Bootstrap color class for severity level.

    Args:
        severity: Severity level (critical, warning, info, success)

    Returns:
        Bootstrap color class
    """
    colors = {
        'critical': 'danger',
        'danger': 'danger',
        'error': 'danger',
        'warning': 'warning',
        'warn': 'warning',
        'info': 'info',
        'information': 'info',
        'success': 'success',
        'ok': 'success'
    }
    return colors.get(severity.lower(), 'info')


def get_health_score_color(score: int) -> str:
    """
    Get color for health score.

    Args:
        score: Health score (0-100)

    Returns:
        CSS color or Bootstrap class
    """
    if score >= 80:
        return '#28a745'  # Green
    elif score >= 60:
        return '#ffc107'  # Yellow
    elif score >= 40:
        return '#fd7e14'  # Orange
    return '#dc3545'  # Red


def get_health_score_label(score: int) -> str:
    """
    Get health score category label.

    Args:
        score: Health score (0-100)

    Returns:
        Category label
    """
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    elif score >= 40:
        return 'Fair'
    return 'Poor'


class Timer:
    """Context manager for timing code execution."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()

    @property
    def elapsed_formatted(self) -> str:
        """Get formatted elapsed time."""
        if self.elapsed is None:
            return '0s'
        return format_duration(self.elapsed)
