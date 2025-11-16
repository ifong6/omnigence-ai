"""
General utility/helper functions for the application.

This module contains reusable utility functions that don't fit into
specific layers (controller, service, dao, etc.).
"""

from typing import Optional, Any, Dict, List
from datetime import datetime, date
from decimal import Decimal
import re


# =============================================================================
# String Utilities
# =============================================================================

def normalize_string(s: Optional[str]) -> Optional[str]:
    """
    Normalize a string by collapsing whitespace and returning None if empty.

    This is useful for cleaning user input where multiple spaces, tabs, or
    newlines should be collapsed into single spaces.

    Args:
        s: Input string (can be None)

    Returns:
        Normalized string with collapsed whitespace, or None if empty

    Examples:
        >>> normalize_string("  hello   world  ")
        'hello world'
        >>> normalize_string("   ")
        None
        >>> normalize_string(None)
        None
        >>> normalize_string("hello\\n\\nworld")
        'hello world'
    """
    if not s:
        return None
    # Collapse all whitespace (spaces, tabs, newlines) into single spaces
    normalized = " ".join(str(s).split())
    return normalized or None


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding a suffix if truncated.

    Args:
        s: Input string
        max_length: Maximum length (including suffix)
        suffix: String to append when truncated (default: "...")

    Returns:
        Truncated string

    Examples:
        >>> truncate_string("Hello World", 5)
        'He...'
        >>> truncate_string("Hello", 10)
        'Hello'
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def to_snake_case(s: str) -> str:
    """
    Convert a string to snake_case.

    Args:
        s: Input string (camelCase, PascalCase, etc.)

    Returns:
        snake_case string

    Examples:
        >>> to_snake_case("HelloWorld")
        'hello_world'
        >>> to_snake_case("companyName")
        'company_name'
    """
    # Insert underscore before uppercase letters
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
    return s.lower()


def to_camel_case(s: str) -> str:
    """
    Convert a string to camelCase.

    Args:
        s: Input string (snake_case, etc.)

    Returns:
        camelCase string

    Examples:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("company_name")
        'companyName'
    """
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# =============================================================================
# Number Utilities
# =============================================================================

def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """
    Safely convert a value to Decimal, with fallback.

    Args:
        value: Value to convert (int, float, str, None)
        default: Default value if conversion fails

    Returns:
        Decimal value

    Examples:
        >>> safe_decimal("123.45")
        Decimal('123.45')
        >>> safe_decimal(None)
        Decimal('0')
        >>> safe_decimal("invalid", Decimal('10'))
        Decimal('10')
    """
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round a Decimal to a specific number of decimal places.

    Args:
        value: Decimal value to round
        places: Number of decimal places (default: 2)

    Returns:
        Rounded Decimal

    Examples:
        >>> round_decimal(Decimal('123.456'), 2)
        Decimal('123.46')
    """
    quantize_str = '0.' + '0' * places if places > 0 else '1'
    return value.quantize(Decimal(quantize_str))


# =============================================================================
# Date/Time Utilities
# =============================================================================

def format_date(d: Optional[date], fmt: str = "%Y-%m-%d") -> Optional[str]:
    """
    Format a date object as a string.

    Args:
        d: Date object (can be None)
        fmt: Format string (default: ISO 8601)

    Returns:
        Formatted date string, or None if input is None

    Examples:
        >>> from datetime import date
        >>> format_date(date(2025, 1, 15))
        '2025-01-15'
        >>> format_date(None)
        None
    """
    if d is None:
        return None
    return d.strftime(fmt)


def parse_date(s: Optional[str], fmt: str = "%Y-%m-%d") -> Optional[date]:
    """
    Parse a string into a date object.

    Args:
        s: Date string (can be None)
        fmt: Format string (default: ISO 8601)

    Returns:
        Parsed date object, or None if parsing fails

    Examples:
        >>> parse_date("2025-01-15")
        datetime.date(2025, 1, 15)
        >>> parse_date(None)
        None
    """
    if not s:
        return None
    try:
        return datetime.strptime(s, fmt).date()
    except ValueError:
        return None


# =============================================================================
# Collection Utilities
# =============================================================================

def remove_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with None values from a dictionary.

    Args:
        d: Input dictionary

    Returns:
        New dictionary without None values

    Examples:
        >>> remove_none_values({"a": 1, "b": None, "c": "hello"})
        {'a': 1, 'c': 'hello'}
    """
    return {k: v for k, v in d.items() if v is not None}


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.

    Args:
        lst: Input list
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten a nested list into a single list.

    Args:
        nested_list: Nested list

    Returns:
        Flattened list

    Examples:
        >>> flatten_list([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested_list for item in sublist]


# =============================================================================
# Validation Utilities
# =============================================================================

def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.

    Args:
        email: Email string to validate

    Returns:
        True if valid email format, False otherwise

    Examples:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Check if a string is a valid phone number (basic validation).

    Args:
        phone: Phone string to validate

    Returns:
        True if valid phone format, False otherwise

    Examples:
        >>> is_valid_phone("+853-1234-5678")
        True
        >>> is_valid_phone("123")
        False
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's 8-15 digits
    return cleaned.isdigit() and 8 <= len(cleaned) <= 15


# =============================================================================
# Business-Specific Utilities
# =============================================================================

def generate_job_number(prefix: str, year: int, month: int, sequence: int) -> str:
    """
    Generate a standardized job number.

    Args:
        prefix: Job prefix (e.g., "Q" for quotation, "I" for invoice)
        year: Year (last 2 digits)
        month: Month (1-12)
        sequence: Sequence number

    Returns:
        Formatted job number

    Examples:
        >>> generate_job_number("Q", 25, 1, 1)
        'Q-25-01-1'
        >>> generate_job_number("I", 25, 12, 42)
        'I-25-12-42'
    """
    return f"{prefix}-{year:02d}-{month:02d}-{sequence}"


def parse_job_number(job_no: str) -> Optional[Dict[str, Any]]:
    """
    Parse a job number into its components.

    Args:
        job_no: Job number string (e.g., "Q-25-01-1")

    Returns:
        Dictionary with prefix, year, month, sequence, or None if invalid

    Examples:
        >>> parse_job_number("Q-25-01-1")
        {'prefix': 'Q', 'year': 25, 'month': 1, 'sequence': 1}
        >>> parse_job_number("invalid")
        None
    """
    pattern = r'^([A-Z]+)-(\d{2})-(\d{2})-(\d+)$'
    match = re.match(pattern, job_no)
    if not match:
        return None

    prefix, year, month, sequence = match.groups()
    return {
        'prefix': prefix,
        'year': int(year),
        'month': int(month),
        'sequence': int(sequence)
    }


def calculate_percentage(part: Decimal, total: Decimal) -> Decimal:
    """
    Calculate percentage of part relative to total.

    Args:
        part: Part value
        total: Total value

    Returns:
        Percentage (0-100)

    Examples:
        >>> calculate_percentage(Decimal('25'), Decimal('100'))
        Decimal('25.00')
        >>> calculate_percentage(Decimal('0'), Decimal('100'))
        Decimal('0.00')
    """
    if total == 0:
        return Decimal('0')
    return round_decimal((part / total) * 100, 2)
