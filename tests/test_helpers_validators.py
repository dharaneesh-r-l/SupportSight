import pytest
from app.utils.helpers import (
    format_bytes, format_percentage, format_datetime, format_duration,
    calculate_percentage, safe_divide, truncate_string, chunk_list,
    deep_merge, sanitize_filename, get_severity_color, get_health_score_color,
    get_health_score_label, Timer
)
from app.utils.validators import (
    validate_email, validate_username, validate_password,
    validate_required_fields, validate_integer, validate_percentage,
    sanitize_string, validate_url
)
from datetime import datetime


def test_format_bytes():
    assert format_bytes(0) == '0.00 B'
    assert format_bytes(None) == '0 B'
    assert format_bytes(-10) == '0 B'
    assert format_bytes(1024) == '1.00 KB'
    assert format_bytes(1048576) == '1.00 MB'
    assert format_bytes(1073741824) == '1.00 GB'


def test_format_percentage():
    assert format_percentage(None) == '0%'
    assert format_percentage(85.5) == '85.5%'
    assert format_percentage(0.855) == '85.5%'


def test_format_datetime():
    dt = datetime(2026, 7, 22, 12, 34, 56)
    assert format_datetime(dt) == '2026-07-22 12:34:56'
    assert format_datetime(None) == ''
    assert format_datetime('2026-07-22T12:34:56Z') == '2026-07-22 12:34:56'
    assert format_datetime('invalid-date') == 'invalid-date'


def test_format_duration():
    assert format_duration(None) == '0s'
    assert format_duration(45) == '45s'
    assert format_duration(125) == '2m 5s'
    assert format_duration(3665) == '1h 1m 5s'


def test_calculate_percentage():
    assert calculate_percentage(50, 100) == 50.0
    assert calculate_percentage(0, 100) == 0.0
    assert calculate_percentage(50, 0) == 0.0


def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=99.0) == 99.0


def test_truncate_string():
    assert truncate_string("hello world", 20) == "hello world"
    assert truncate_string("hello world long string", 10) == "hello w..."


def test_chunk_list():
    lst = [1, 2, 3, 4, 5]
    assert chunk_list(lst, 2) == [[1, 2], [3, 4], [5]]


def test_deep_merge():
    d1 = {'a': 1, 'b': {'x': 10}}
    d2 = {'c': 2, 'b': {'y': 20}}
    res = deep_merge(d1, d2)
    assert res == {'a': 1, 'b': {'x': 10, 'y': 20}, 'c': 2}


def test_sanitize_filename():
    assert sanitize_filename("file/name:test?.txt") == "filenametest.txt"


def test_get_severity_color():
    assert get_severity_color('critical') == 'danger'
    assert get_severity_color('warning') == 'warning'
    assert get_severity_color('ok') == 'success'
    assert get_severity_color('unknown') == 'info'


def test_get_health_score():
    assert get_health_score_color(90) == '#28a745'
    assert get_health_score_label(90) == 'Excellent'
    assert get_health_score_label(70) == 'Good'
    assert get_health_score_label(50) == 'Fair'
    assert get_health_score_label(30) == 'Poor'


def test_timer():
    with Timer() as t:
        _ = 1 + 1
    assert t.elapsed >= 0
    assert 's' in t.elapsed_formatted


def test_validate_email():
    assert validate_email('user@example.com')[0] is True
    assert validate_email('')[0] is False
    assert validate_email('invalid-email')[0] is False


def test_validate_username():
    assert validate_username('valid_user123')[0] is True
    assert validate_username('a')[0] is False
    assert validate_username('user@invalid')[0] is False


def test_validate_password():
    assert validate_password('ValidPass123!')[0] is True
    assert validate_password('short')[0] is False
    assert validate_password('nouppercase1!')[0] is False
    assert validate_password('NOLOWERCASE1!')[0] is False
    assert validate_password('NoDigits!')[0] is False
    assert validate_password('NoSpecialChar1')[0] is False


def test_validate_required_fields():
    data = {'a': 1, 'b': 'hello'}
    assert validate_required_fields(data, ['a', 'b'])[0] is True
    assert validate_required_fields(data, ['a', 'c'])[0] is False


def test_validate_integer():
    assert validate_integer('10', 0, 100)[0] is True
    assert validate_integer('abc')[0] is False
    assert validate_integer(150, 0, 100)[0] is False


def test_validate_percentage():
    assert validate_percentage(50)[0] is True
    assert validate_percentage(150)[0] is False


def test_sanitize_string():
    assert sanitize_string("<b>Hello</b>") == "Hello"


def test_validate_url():
    assert validate_url("https://example.com")[0] is True
    assert validate_url("invalid-url")[0] is False
