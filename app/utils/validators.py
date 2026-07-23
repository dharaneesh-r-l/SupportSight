"""
SupportSight Input Validators

Form and input validation utilities.
"""

import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, 'Email is required'

    if len(email) > 120:
        return False, 'Email must be less than 120 characters'

    # RFC 5322 compliant email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Invalid email format'

    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a username.

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, 'Username is required'

    if len(username) < 3:
        return False, 'Username must be at least 3 characters'

    if len(username) > 80:
        return False, 'Username must be less than 80 characters'

    # Only allow alphanumeric characters and underscores
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, username):
        return False, 'Username can only contain letters, numbers, and underscores'

    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a password meets security requirements.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, 'Password is required'

    if len(password) < 8:
        return False, 'Password must be at least 8 characters'

    if len(password) > 128:
        return False, 'Password must be less than 128 characters'

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password must contain at least one special character'

    return True, None


def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)

    if missing_fields:
        field_str = ', '.join(missing_fields)
        return False, f'Missing required fields: {field_str}'

    return True, None


def validate_integer(value: any, min_value: int = None, max_value: int = None,
                     field_name: str = 'Value') -> Tuple[bool, Optional[str]]:
    """
    Validate an integer value.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of field for error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return False, f'{field_name} must be a number'

    if min_value is not None and int_value < min_value:
        return False, f'{field_name} must be at least {min_value}'

    if max_value is not None and int_value > max_value:
        return False, f'{field_name} must be at most {max_value}'

    return True, None


def validate_percentage(value: any, field_name: str = 'Value') -> Tuple[bool, Optional[str]]:
    """
    Validate a percentage value (0-100).

    Args:
        value: Value to validate
        field_name: Name of field for error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, error = validate_integer(value, min_value=0, max_value=100, field_name=field_name)
    return is_valid, error


def sanitize_string(text: str, max_length: int = None) -> str:
    """
    Sanitize a string by removing potentially harmful characters.

    Args:
        text: String to sanitize
        max_length: Maximum length

    Returns:
        Sanitized string
    """
    if not text:
        return ''

    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)

    # Strip whitespace
    text = text.strip()

    if max_length:
        text = text[:max_length]

    return text


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, 'URL is required'

    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(pattern, url):
        return False, 'Invalid URL format'

    return True, None
