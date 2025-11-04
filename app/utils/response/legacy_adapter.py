# =============================================================
# PURPOSE:
#   Bridge older agent outputs (dict/str/None) to new AgentResponse.
#   🧑‍💻 Developer: ensures backward compatibility.
#   👩‍🦰 Human user: Sees clean message instead of raw JSON.
#   🧩 Data handling: Guarantees uniform structure for aggregation.
# =============================================================

from typing import Any
from app.utils.response.agent_response import AgentResponse, ResponseStatus


def adapt_legacy(agent_name: str, legacy: Any) -> AgentResponse:
    """Convert any legacy agent output to standardized AgentResponse.

    This adapter allows old agent code to work without changes while
    providing a clean, typed interface for aggregation.

    Args:
        agent_name: Name of the agent that produced the response
        legacy: The raw response from the agent (can be dict, str, None, etc.)

    Returns:
        AgentResponse: Standardized response object

    Examples:
        >>> adapt_legacy("finance_agent", None)
        AgentResponse(agent_name="finance_agent", status="empty", message="No response.")

        >>> adapt_legacy("hr_agent", "Task completed")
        AgentResponse(agent_name="hr_agent", status="partial", message="Task completed")

        >>> adapt_legacy("finance_agent", {"status": "success", "agent_output": "Done"})
        AgentResponse(agent_name="finance_agent", status="success", message="Done")
    """

    # Handle None → EMPTY
    if legacy is None:
        return AgentResponse(
            agent_name=agent_name,
            status=ResponseStatus.EMPTY,
            message="No response."
        )

    # Handle string → PARTIAL (got text but not structured data)
    if isinstance(legacy, str):
        return AgentResponse(
            agent_name=agent_name,
            status=ResponseStatus.PARTIAL,
            message=legacy
        )

    # Handle dict (most common case)
    if isinstance(legacy, dict):
        # Extract message from various possible fields
        message = _extract_message(legacy)

        # Extract status
        status = _extract_status(legacy)

        # Extract warnings if present
        warnings = legacy.get("warnings", [])
        if isinstance(warnings, str):
            warnings = [warnings]
        elif not isinstance(warnings, list):
            warnings = []

        # Extract error details
        error_details = None
        if status == ResponseStatus.ERROR:
            error_details = legacy.get("error") or legacy.get("error_message")
            if error_details and not isinstance(error_details, str):
                error_details = str(error_details)

        return AgentResponse(
            agent_name=agent_name,
            status=status,
            message=message,
            data=legacy,  # Preserve original data for debugging
            warnings=warnings,
            error_details=error_details
        )

    # Fallback for unknown types
    return AgentResponse(
        agent_name=agent_name,
        status=ResponseStatus.PARTIAL,
        message=str(legacy)
    )


def _extract_message(data: dict) -> str:
    """Extract human-readable message from legacy dict response."""
    # Try common message fields in order of preference
    message = (
        data.get("agent_output") or
        data.get("message") or
        data.get("synthesized_message")
    )

    # Check nested result field
    if not message and "result" in data:
        result = data["result"]
        if isinstance(result, dict):
            message = result.get("agent_output") or result.get("message")

    # Check quotation_response for finance agent
    if not message and "quotation_response" in data:
        quotation = data["quotation_response"]
        if isinstance(quotation, dict):
            message = quotation.get("agent_output")

    # Fallback
    if not message:
        message = "Operation completed"

    return message


def _extract_status(data: dict) -> ResponseStatus:
    """Extract status from legacy dict response."""
    status_str = data.get("status", "success")

    # Handle nested status
    if "quotation_response" in data and isinstance(data["quotation_response"], dict):
        status_str = data["quotation_response"].get("status", status_str)

    # Convert to enum
    try:
        return ResponseStatus(status_str)
    except ValueError:
        # If status string is unrecognized, default to PARTIAL
        return ResponseStatus.PARTIAL
