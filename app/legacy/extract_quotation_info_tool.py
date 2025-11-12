"""
Tool for extracting quotation information using LLM.

This module provides functionality to parse user input and extract structured
quotation information using OpenAI's structured output.
"""

from typing import Any, Dict
import datetime
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.prompt.quotation_prompt_template import (
    EXTRACT_QUOTATION_PROMPT_TEMPLATE,
    QuotationInfoExtractOutput,
    QuotationInfo
)


# ============================================================================
# Business Logic Functions
# ============================================================================

def _validate_extraction_params(params: Dict[str, Any]) -> None:
    """
    Validate that all required parameters for extraction are present.

    Args:
        params: Parsed parameters

    Raises:
        ValueError: If any required parameter is missing
    """
    required = ['user_input', 'client_info', 'quotation_no']
    missing = [key for key in required if not params.get(key)]

    if missing:
        raise ValueError(
            f"Missing required parameters: {', '.join(missing)}. "
            "Make sure to fetch job_no, client_info, and create quotation_no first."
        )


def _build_extraction_prompt(
    user_input: str,
    client_info: Dict[str, Any],
    quotation_no: str
) -> str:
    """
    Build the prompt for LLM extraction.

    Args:
        user_input: User's quotation request
        client_info: Client company information
        quotation_no: Generated quotation number

    Returns:
        Formatted system prompt for extraction
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    return EXTRACT_QUOTATION_PROMPT_TEMPLATE.format(
        user_input=user_input,
        client_info=client_info,
        quotation_no=quotation_no,
        date=current_date
    )


def _invoke_llm_extraction(prompt: str) -> QuotationInfo:
    """
    Invoke LLM to extract structured quotation information.

    Args:
        prompt: Formatted extraction prompt

    Returns:
        QuotationInfo: Extracted quotation information

    Raises:
        Exception: If LLM invocation fails
    """
    parsed_response = invoke_claude_llm(prompt, QuotationInfoExtractOutput)

    # parsed_response is a Pydantic QuotationInfoExtractOutput object
    # Access quotation_info via attribute
    return parsed_response.quotation_info


# ============================================================================
# Main Tool Function
# ============================================================================

def extract_quotation_info_tool(tool_input: Any) -> QuotationInfo | Dict[str, str]:
    """
    Extract structured quotation data from user input using LLM.

    Args:
        tool_input: {"user_input": str, "client_info": dict, "quotation_no": str}

    Returns:
        QuotationInfo object with client, project items, totals, etc. or {"error": "..."}
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['user_input', 'client_info', 'quotation_no'],
            tool_name="extract_quotation_info_tool"
        )

        # Validate all required fields are non-empty
        _validate_extraction_params(params)

        # Build extraction prompt
        prompt = _build_extraction_prompt(
            user_input=params['user_input'],
            client_info=params['client_info'],
            quotation_no=params['quotation_no']
        )

        # Invoke LLM to extract quotation info
        quotation_info = _invoke_llm_extraction(prompt)

        return quotation_info

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except Exception as e:
        error_msg = f"Unexpected error extracting quotation info: {str(e)}"
        print(f"[ERROR][extract_quotation_info_tool] {error_msg}")
        return {"error": error_msg}
