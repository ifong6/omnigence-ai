"""
Helper utilities for formatting and logging quotation responses.

This module provides functions to:
- Print incoming quotation requests for debugging
- Format agent responses for frontend consumption
- Extract quotation data from intermediate tool results
"""

import json
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# Constants
# ============================================================================

_DIVIDER = "=" * 80
_STATUS_SUCCESS = "success"
_STATUS_PARTIAL = "partial"


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_quotation_number(intermediate_steps: List[Tuple]) -> Optional[str]:
    """
    Extract quotation number from create_quotation_no_tool result.

    Args:
        intermediate_steps: List of (action, result) tuples

    Returns:
        Quotation number if found, None otherwise
    """
    for step in intermediate_steps:
        if isinstance(step, tuple) and len(step) == 2:
            action, result = step
            tool_name = action.tool if hasattr(action, 'tool') else str(action)

            if 'create_quotation_no_tool' in str(tool_name) and isinstance(result, dict):
                return result.get('quotation_no')

    return None


def _extract_created_items(intermediate_steps: List[Tuple]) -> List[Dict[str, Any]]:
    """
    Extract created items from create_quotation_in_db result.

    Args:
        intermediate_steps: List of (action, result) tuples

    Returns:
        List of created item dicts
    """
    for step in intermediate_steps:
        if isinstance(step, tuple) and len(step) == 2:
            action, result = step
            tool_name = action.tool if hasattr(action, 'tool') else str(action)

            if 'create_quotation_in_db' in str(tool_name) and isinstance(result, dict):
                if result.get('success'):
                    return result.get('items', [])

    return []


def _extract_quotation_data(intermediate_steps: List[Tuple]) -> Optional[Dict[str, Any]]:
    """
    Extract UI-formatted quotation data from output_quotation_info_for_ui result.

    Args:
        intermediate_steps: List of (action, result) tuples

    Returns:
        Quotation data dict if found, None otherwise
    """
    for step in intermediate_steps:
        if isinstance(step, tuple) and len(step) == 2:
            action, result = step
            tool_name = action.tool if hasattr(action, 'tool') else str(action)

            if 'output_quotation_info_for_ui' in str(tool_name) and isinstance(result, dict):
                return result

    return None


def _print_tool_steps(
    intermediate_steps: List[Tuple],
    quotation_no: Optional[str],
    created_items: List[Dict[str, Any]]
) -> None:
    """
    Print detailed information about tool execution steps.

    Args:
        intermediate_steps: List of (action, result) tuples
        quotation_no: Extracted quotation number
        created_items: List of created items
    """
    print(f"\n🔧 Tool Calls: {len(intermediate_steps)} steps executed")

    for step in intermediate_steps:
        if isinstance(step, tuple) and len(step) == 2:
            action, result = step
            tool_name = action.tool if hasattr(action, 'tool') else str(action)
            print(f"\n   Step: {tool_name}")

            # Print quotation number generation
            if 'create_quotation_no_tool' in str(tool_name) and quotation_no:
                print(f"      → Generated: {quotation_no}")

            # Print created items
            if 'create_quotation_in_db' in str(tool_name) and created_items:
                print(f"      → Created {len(created_items)} items")
                for item in created_items:
                    print(
                        f"         • {item.get('project_item_description')}: "
                        f"{item.get('sub_amount')} "
                        f"(qty: {item.get('quantity')}, unit: {item.get('unit')})"
                    )

            # Print UI formatting confirmation
            if 'output_quotation_info_for_ui' in str(tool_name):
                print(f"      → Formatted for UI")


def _print_frontend_response(
    frontend_response: Dict[str, Any],
    created_items: List[Dict[str, Any]]
) -> None:
    """
    Print summary of frontend response.

    Args:
        frontend_response: Formatted response dict
        created_items: List of created items
    """
    print(f"\n📤 Frontend Response:")
    print(f"   Status: {frontend_response['status']}")
    print(f"   Quotation No: {frontend_response['quotation_no']}")
    print(f"   Items Created: {len(created_items)}")

    if frontend_response['quotation_data']:
        print(f"   UI Data: Available ✅")
    else:
        print(f"   UI Data: Not available (agent may have stopped early)")


# ============================================================================
# Public Functions
# ============================================================================

def print_quotation_request(user_input: str) -> None:
    """
    Print the incoming quotation request for debugging/logging.

    This function logs the user's quotation request to the console for
    debugging and monitoring purposes. The output is server-side only
    and not sent to the frontend.

    Args:
        user_input: The user's quotation request

    Example:
        >>> print_quotation_request("支撐架計算 7000MOP, 吊燈計算 6000MOP")
        # Prints:
        # ================================================================================
        # QUOTATION CRUD HANDLER - REQUEST
        # ================================================================================
        #
        # 📥 Received Request:
        #    支撐架計算 7000MOP, 吊燈計算 6000MOP
        # ================================================================================
    """
    print(f"\n{_DIVIDER}")
    print("QUOTATION CRUD HANDLER - REQUEST")
    print(_DIVIDER)
    print(f"\n📥 Received Request:")
    print(f"   {user_input}")
    print(f"{_DIVIDER}\n")


def format_quotation_response(agent_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the agent response into a clean structure for frontend.
    Also prints detailed response information for debugging/logging.

    This function processes the raw agent response, extracts relevant quotation
    data from intermediate tool results, and formats it for frontend consumption.
    All print statements are server-side only for logging/debugging.

    Args:
        agent_response: The raw response from invoke_react_agent containing:
            - input: User's original input
            - output: Agent's final response text
            - intermediate_steps: List of (action, result) tuples from tool calls

    Returns:
        dict: Formatted response for frontend with structure:
            {
                "status": "success" | "partial",
                "user_input": str,              # Original user request
                "agent_output": str,            # Agent's final response text
                "quotation_no": str | None,     # Generated quotation number
                "quotation_data": dict | None,  # Full UI-ready quotation data
                "created_items": list,          # Items created in database
                "steps_executed": int           # Number of tool calls executed
            }

    Example:
        >>> response = format_quotation_response(agent_result)
        >>> # Prints detailed logs to console (server-side only)
        >>> # Returns clean dict for frontend:
        >>> {
        ...     "status": "success",
        ...     "quotation_no": "Q-JCP-25-01-q1",
        ...     "created_items": [...],
        ...     ...
        ... }

    Workflow:
        1. Print response header with user input and agent output
        2. Extract data from intermediate tool results:
           - Quotation number from create_quotation_no_tool
           - Created items from create_quotation_in_db
           - UI data from output_quotation_info_for_ui
        3. Print tool execution details
        4. Build and return frontend response
        5. Print frontend response summary

    Status Values:
        - "success": Quotation created successfully with all data
        - "partial": Some data available but workflow may be incomplete
    """
    # Print header
    print(f"\n{_DIVIDER}")
    print("QUOTATION CRUD HANDLER - RESPONSE")
    print(_DIVIDER)

    # Extract and print user input
    user_input = agent_response.get('input', '')
    print(f"\n📝 User Input:")
    print(f"   {user_input}")

    # Extract and print final output
    final_output = agent_response.get('output', '')
    print(f"\n✅ Agent Output:")
    print(f"   {final_output}")

    # Extract data from intermediate steps
    intermediate_steps = agent_response.get('intermediate_steps', [])
    quotation_no = _extract_quotation_number(intermediate_steps)
    created_items = _extract_created_items(intermediate_steps)
    quotation_data = _extract_quotation_data(intermediate_steps)

    # Print tool execution details
    _print_tool_steps(intermediate_steps, quotation_no, created_items)

    # Build frontend response
    frontend_response = {
        "status": _STATUS_SUCCESS if (quotation_data or created_items) else _STATUS_PARTIAL,
        "user_input": user_input,
        "agent_output": final_output,
        "quotation_no": quotation_no,
        "quotation_data": quotation_data,
        "created_items": created_items,
        "steps_executed": len(intermediate_steps)
    }

    # Print frontend response summary
    _print_frontend_response(frontend_response, created_items)
    print(f"{_DIVIDER}\n")

    return frontend_response
