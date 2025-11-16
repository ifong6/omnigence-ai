"""
DEPRECATED: This module is kept for backward compatibility.

Please use app.utils.validators instead:
    from app.utils import parse_tool_input, parse_tool_input_as_string, ToolInputError

This module re-exports from the centralized utils package.
"""

# Re-export from centralized utils
from app.utils.validators import parse_tool_input, parse_tool_input_as_string
from app.utils.exceptions import ToolInputError

__all__ = ["parse_tool_input", "parse_tool_input_as_string", "ToolInputError"]
