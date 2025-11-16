"""
Custom validation functions for the application.

This module provides validation utilities for:
- Tool input parsing (LangChain/LangGraph)
- Business rule validation
- Data format validation
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from datetime import date

from app.utils.exceptions import ToolInputError, ValidationError


# =============================================================================
# Tool Input Parsing/Validation
# =============================================================================

def parse_tool_input(
    tool_input: Union[str, Dict[str, Any]],
    required_keys: Optional[List[str]] = None,
    tool_name: str = "tool"
) -> Dict[str, Any]:
    """
    Parse and validate tool input from various formats.

    This function handles the common pattern where LangChain agents can pass inputs as:
    - JSON string: '{"key": "value"}'
    - JSON string with quotes: '\'{"key": "value"}\''
    - Dictionary: {"key": "value"}

    Args:
        tool_input: Input from the LangChain agent
        required_keys: List of required parameter names. If provided, validates presence.
        tool_name: Name of the calling tool (for error messages)

    Returns:
        Dict[str, Any]: Parsed parameters dictionary

    Raises:
        ToolInputError: If input cannot be parsed or required keys are missing

    Examples:
        >>> params = parse_tool_input('{"name": "John"}', required_keys=["name"])
        >>> params = parse_tool_input({"name": "John"}, required_keys=["name"])
        >>> params = parse_tool_input('\'{"name": "John"}\'')
    """
    # Handle dict input
    if isinstance(tool_input, dict):
        params = tool_input

    # Handle string input
    elif isinstance(tool_input, str):
        # Strip outer quotes if present (LangChain sometimes wraps JSON in quotes)
        tool_input_str: str = tool_input.strip()

        # Strip markdown code fences if present (```json ... ```)
        if tool_input_str.startswith("```json"):
            tool_input_str = tool_input_str[7:]  # Remove ```json
        elif tool_input_str.startswith("```"):
            tool_input_str = tool_input_str[3:]  # Remove ```
        if tool_input_str.endswith("```"):
            tool_input_str = tool_input_str[:-3]  # Remove trailing ```
        tool_input_str = tool_input_str.strip()

        if (tool_input_str.startswith("'") and tool_input_str.endswith("'")) or \
           (tool_input_str.startswith('"') and tool_input_str.endswith('"')):
            tool_input_str = tool_input_str[1:-1]

        # Replace Python None, True, False with JSON equivalents
        # Use word boundaries to avoid replacing these inside strings
        tool_input_str = re.sub(r'\bNone\b', 'null', tool_input_str)
        tool_input_str = re.sub(r'\bTrue\b', 'true', tool_input_str)
        tool_input_str = re.sub(r'\bFalse\b', 'false', tool_input_str)

        # Try to parse as JSON
        try:
            params = json.loads(tool_input_str)
            if not isinstance(params, dict):
                raise ToolInputError(
                    f"Parsed JSON is not a dictionary. Got: {type(params)}",
                    tool_name=tool_name
                )
        except json.JSONDecodeError as e:
            raise ToolInputError(
                f"Invalid JSON input. Error: {str(e)}",
                tool_name=tool_name
            )

    else:
        raise ToolInputError(
            f"Unexpected input type: {type(tool_input)}. Expected dict or JSON string.",
            tool_name=tool_name
        )

    # Validate required keys
    if required_keys:
        missing_keys = [key for key in required_keys if key not in params]
        if missing_keys:
            raise ToolInputError(
                f"Missing required parameters: {', '.join(missing_keys)}. "
                f"Provided: {list(params.keys())}",
                tool_name=tool_name
            )

    return params


def parse_tool_input_as_string(
    tool_input: Union[str, Dict[str, Any]],
    param_name: str = "value",
    tool_name: str = "tool"
) -> str:
    """
    Parse tool input expecting a single string value.

    Useful for simple tools that just need one string parameter.

    Args:
        tool_input: Input from the LangChain agent
        param_name: The expected parameter name if dict is provided
        tool_name: Name of the calling tool (for error messages)

    Returns:
        str: The extracted string value

    Raises:
        ToolInputError: If input cannot be parsed as string

    Examples:
        >>> value = parse_tool_input_as_string("ABC Company")
        >>> value = parse_tool_input_as_string({"name": "ABC Company"}, param_name="name")
    """
    if isinstance(tool_input, str):
        # If it looks like JSON, try to parse it
        tool_input_stripped = tool_input.strip()
        if tool_input_stripped.startswith('{'):
            try:
                params = json.loads(tool_input_stripped)
                if isinstance(params, dict) and param_name in params:
                    return str(params[param_name])
            except json.JSONDecodeError:
                pass
        # Otherwise treat as plain string
        return tool_input

    elif isinstance(tool_input, dict):
        if param_name in tool_input:
            return str(tool_input[param_name])
        # If single key, use that
        if len(tool_input) == 1:
            return str(list(tool_input.values())[0])
        raise ToolInputError(
            f"Expected parameter '{param_name}' in dict. Got keys: {list(tool_input.keys())}",
            tool_name=tool_name
        )

    else:
        raise ToolInputError(
            f"Cannot convert {type(tool_input)} to string",
            tool_name=tool_name
        )


# =============================================================================
# Business Validation Functions
# =============================================================================

def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str],
    context: str = "data"
) -> None:
    """
    Validate that all required fields are present and not None.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context description for error messages

    Raises:
        ValidationError: If any required field is missing or None

    Examples:
        >>> validate_required_fields({"name": "ABC"}, ["name"])  # OK
        >>> validate_required_fields({}, ["name"])  # Raises ValidationError
    """
    missing = []
    none_values = []

    for field in required_fields:
        if field not in data:
            missing.append(field)
        elif data[field] is None:
            none_values.append(field)

    if missing or none_values:
        errors = []
        if missing:
            errors.append(f"Missing fields: {', '.join(missing)}")
        if none_values:
            errors.append(f"Fields with None value: {', '.join(none_values)}")

        raise ValidationError(
            f"{context} validation failed: {'; '.join(errors)}",
            details={"missing": missing, "none_values": none_values}
        )


def validate_positive_number(
    value: Union[int, float, Decimal],
    field_name: str,
    allow_zero: bool = False
) -> None:
    """
    Validate that a number is positive.

    Args:
        value: Number to validate
        field_name: Field name for error messages
        allow_zero: Whether to allow zero (default: False)

    Raises:
        ValidationError: If value is not positive

    Examples:
        >>> validate_positive_number(10, "quantity")  # OK
        >>> validate_positive_number(0, "quantity")  # Raises ValidationError
        >>> validate_positive_number(0, "quantity", allow_zero=True)  # OK
    """
    if allow_zero:
        if value < 0:
            raise ValidationError(
                f"{field_name} must be non-negative",
                field=field_name,
                value=value
            )
    else:
        if value <= 0:
            raise ValidationError(
                f"{field_name} must be positive",
                field=field_name,
                value=value
            )


def validate_date_range(
    start_date: date,
    end_date: date,
    start_field: str = "start_date",
    end_field: str = "end_date"
) -> None:
    """
    Validate that start_date is before or equal to end_date.

    Args:
        start_date: Start date
        end_date: End date
        start_field: Field name for start date (for error messages)
        end_field: Field name for end date (for error messages)

    Raises:
        ValidationError: If start_date is after end_date

    Examples:
        >>> from datetime import date
        >>> validate_date_range(date(2025, 1, 1), date(2025, 12, 31))  # OK
        >>> validate_date_range(date(2025, 12, 31), date(2025, 1, 1))  # Raises ValidationError
    """
    if start_date > end_date:
        raise ValidationError(
            f"{start_field} must be before or equal to {end_field}",
            details={
                start_field: str(start_date),
                end_field: str(end_date)
            }
        )


def validate_string_length(
    value: str,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> None:
    """
    Validate string length constraints.

    Args:
        value: String to validate
        field_name: Field name for error messages
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)

    Raises:
        ValidationError: If length constraints are violated

    Examples:
        >>> validate_string_length("hello", "name", min_length=3, max_length=10)  # OK
        >>> validate_string_length("hi", "name", min_length=3)  # Raises ValidationError
    """
    length = len(value)

    if min_length is not None and length < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters",
            field=field_name,
            value=value,
            details={"length": length, "min_length": min_length}
        )

    if max_length is not None and length > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters",
            field=field_name,
            value=value,
            details={"length": length, "max_length": max_length}
        )


def validate_enum_value(
    value: Any,
    allowed_values: List[Any],
    field_name: str
) -> None:
    """
    Validate that a value is in a list of allowed values.

    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Field name for error messages

    Raises:
        ValidationError: If value is not in allowed_values

    Examples:
        >>> validate_enum_value("active", ["active", "inactive"], "status")  # OK
        >>> validate_enum_value("pending", ["active", "inactive"], "status")  # Raises ValidationError
    """
    if value not in allowed_values:
        raise ValidationError(
            f"{field_name} must be one of: {', '.join(map(str, allowed_values))}",
            field=field_name,
            value=value,
            details={"allowed_values": allowed_values}
        )


def validate_non_empty_list(
    value: List[Any],
    field_name: str,
    min_items: int = 1
) -> None:
    """
    Validate that a list is not empty and has minimum items.

    Args:
        value: List to validate
        field_name: Field name for error messages
        min_items: Minimum number of items (default: 1)

    Raises:
        ValidationError: If list has fewer than min_items

    Examples:
        >>> validate_non_empty_list([1, 2, 3], "items")  # OK
        >>> validate_non_empty_list([], "items")  # Raises ValidationError
        >>> validate_non_empty_list([1], "items", min_items=2)  # Raises ValidationError
    """
    if len(value) < min_items:
        raise ValidationError(
            f"{field_name} must have at least {min_items} item(s)",
            field=field_name,
            value=value,
            details={"count": len(value), "min_items": min_items}
        )


# =============================================================================
# Format Validation Functions
# =============================================================================

def validate_job_number_format(job_no: str) -> None:
    """
    Validate job number format (e.g., "Q-25-01-1").

    Args:
        job_no: Job number to validate

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_job_number_format("Q-25-01-1")  # OK
        >>> validate_job_number_format("invalid")  # Raises ValidationError
    """
    pattern = r'^[A-Z]+-\d{2}-\d{2}-\d+$'
    if not re.match(pattern, job_no):
        raise ValidationError(
            "Invalid job number format. Expected format: PREFIX-YY-MM-SEQ (e.g., Q-25-01-1)",
            field="job_no",
            value=job_no
        )


def validate_email_format(email: str) -> None:
    """
    Validate email format.

    Args:
        email: Email to validate

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_email_format("user@example.com")  # OK
        >>> validate_email_format("invalid")  # Raises ValidationError
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(
            "Invalid email format",
            field="email",
            value=email
        )


def validate_phone_format(phone: str) -> None:
    """
    Validate phone number format (basic validation).

    Args:
        phone: Phone number to validate

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_phone_format("+853-1234-5678")  # OK
        >>> validate_phone_format("123")  # Raises ValidationError
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's 8-15 digits
    if not (cleaned.isdigit() and 8 <= len(cleaned) <= 15):
        raise ValidationError(
            "Invalid phone number format. Must be 8-15 digits.",
            field="phone",
            value=phone
        )
