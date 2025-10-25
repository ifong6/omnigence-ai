"""
Shared utility for parsing tool inputs consistently across all tools.

This module provides a standardized way to handle different input types
(string, dict, JSON) that tools receive from the LangChain agent.
"""

import json
from typing import Any, Dict, Optional, Union


class ToolInputError(Exception):
    """Custom exception for tool input parsing errors."""
    pass


def parse_tool_input(
    tool_input: Union[str, Dict[str, Any]],
    required_keys: Optional[list[str]] = None,
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
        tool_input = tool_input.strip()

        # Strip markdown code fences if present (```json ... ```)
        if tool_input.startswith("```json"):
            tool_input = tool_input[7:]  # Remove ```json
        elif tool_input.startswith("```"):
            tool_input = tool_input[3:]  # Remove ```
        if tool_input.endswith("```"):
            tool_input = tool_input[:-3]  # Remove trailing ```
        tool_input = tool_input.strip()

        if (tool_input.startswith("'") and tool_input.endswith("'")) or \
           (tool_input.startswith('"') and tool_input.endswith('"')):
            tool_input = tool_input[1:-1]

        # Replace Python None, True, False with JSON equivalents
        # Use word boundaries to avoid replacing these inside strings
        import re
        tool_input = re.sub(r'\bNone\b', 'null', tool_input)
        tool_input = re.sub(r'\bTrue\b', 'true', tool_input)
        tool_input = re.sub(r'\bFalse\b', 'false', tool_input)

        # Try to parse as JSON
        try:
            params = json.loads(tool_input)
            if not isinstance(params, dict):
                raise ToolInputError(
                    f"{tool_name}: Parsed JSON is not a dictionary. Got: {type(params)}"
                )
        except json.JSONDecodeError as e:
            raise ToolInputError(
                f"{tool_name}: Invalid JSON input. Error: {str(e)}"
            )

    else:
        raise ToolInputError(
            f"{tool_name}: Unexpected input type: {type(tool_input)}. "
            f"Expected dict or JSON string."
        )

    # Validate required keys
    if required_keys:
        missing_keys = [key for key in required_keys if key not in params]
        if missing_keys:
            raise ToolInputError(
                f"{tool_name}: Missing required parameters: {', '.join(missing_keys)}. "
                f"Provided: {list(params.keys())}"
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
            f"{tool_name}: Expected parameter '{param_name}' in dict. "
            f"Got keys: {list(tool_input.keys())}"
        )

    else:
        raise ToolInputError(
            f"{tool_name}: Cannot convert {type(tool_input)} to string"
        )
