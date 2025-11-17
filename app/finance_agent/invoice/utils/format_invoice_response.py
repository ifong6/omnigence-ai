"""
Utility functions for formatting invoice responses.

This module provides functions to format and log invoice responses.
"""

from typing import Any, Dict


def print_invoice_request(user_input: str):
    """
    Print invoice request for logging/debugging (server-side only).

    Args:
        user_input: User's invoice request input
    """
    print("\n" + "=" * 80)
    print("INVOICE REQUEST")
    print("=" * 80)
    print(f"User Input: {user_input}")
    print("=" * 80 + "\n")


def format_invoice_response(response: Any) -> Dict[str, Any]:
    """
    Format invoice response for frontend display.

    This function processes the ReAct agent response and formats it
    for clean JSON output to the frontend.

    Args:
        response: Raw response from invoke_react_agent

    Returns:
        dict: Formatted response with structure:
            {
                "status": "success" or "error",
                "message": str,
                "invoice": {...} (if successful),
                "raw_output": str (agent's final answer)
            }
    """
    print("\n" + "=" * 80)
    print("INVOICE RESPONSE")
    print("=" * 80)

    try:
        # Extract the response content
        if hasattr(response, 'get'):
            output = response.get('output', '')
            intermediate_steps = response.get('intermediate_steps', [])
        else:
            output = str(response)
            intermediate_steps = []

        print(f"Agent Output: {output}")

        # Log intermediate steps for debugging (server-side only)
        if intermediate_steps:
            print("\nIntermediate Steps:")
            for idx, (action, observation) in enumerate(intermediate_steps, 1):
                print(f"  Step {idx}:")
                print(f"    Tool: {action.tool if hasattr(action, 'tool') else 'N/A'}")
                print(f"    Input: {action.tool_input if hasattr(action, 'tool_input') else 'N/A'}")
                print(f"    Output: {observation[:200]}...")  # Truncate long outputs

        print("=" * 80 + "\n")

        # Try to extract invoice data from output
        # The output should contain invoice information if successful
        import json
        try:
            # Try to parse as JSON
            invoice_data = json.loads(output)
            return {
                "status": "success",
                "message": "Invoice processed successfully",
                "invoice": invoice_data.get("invoice", invoice_data),
                "raw_output": output
            }
        except json.JSONDecodeError:
            # Not JSON, return as text
            return {
                "status": "success",
                "message": output,
                "raw_output": output
            }

    except Exception as e:
        error_msg = f"Error formatting invoice response: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print("=" * 80 + "\n")
        return {
            "status": "error",
            "message": error_msg,
            "raw_output": str(response)
        }
