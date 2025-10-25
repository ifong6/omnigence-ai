"""
Tool for extracting quotation information using LLM.

This module provides functionality to parse user input and extract structured
quotation information using OpenAI's structured output.
"""

from typing import Any, Dict
import datetime
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.llm.invoke_openai_llm import invoke_openai_llm
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
    parsed_response = invoke_openai_llm(prompt, QuotationInfoExtractOutput)

    # parsed_response is a Pydantic QuotationInfoExtractOutput object
    # Access quotation_info via attribute (not .get())
    return parsed_response.quotation_info


# ============================================================================
# Main Tool Function
# ============================================================================

def extract_quotation_info_tool(tool_input: Any) -> QuotationInfo | Dict[str, str]:
    """
    Extract structured quotation information from user input using LLM.

    This tool uses OpenAI's structured output to parse natural language quotation
    requests into structured QuotationInfo objects containing:
    - Client information (name, address, phone)
    - Project details (name, items with descriptions and amounts)
    - Quotation metadata (number, date, currency, totals)

    Args:
        tool_input: Can be either:
            - JSON string: '{"user_input": "...", "client_info": {...}, "quotation_no": "..."}'
            - Dictionary with keys:
                - user_input: User's quotation request (e.g., "支撐架計算 7000MOP")
                - client_info: Dict with client details from get_client_info_by_project_name_tool
                - quotation_no: Generated quotation number from create_quotation_no_tool

    Returns:
        QuotationInfo: Pydantic object with structured quotation data including:
            - client_name, client_address, client_phone
            - project_name
            - project_items: List of items with content, quantity, unit, subtotal
            - total_amount, currency
            - date, no (quotation number)

        On error: {"error": "error message"}

    Examples:
        >>> # Typical usage in agent workflow
        >>> result = extract_quotation_info_tool({
        ...     "user_input": "支撐架計算 7000MOP, 吊燈計算 6000MOP",
        ...     "client_info": {
        ...         "name": "ABC Engineering",
        ...         "address": "123 Main St",
        ...         "phone": "1234567"
        ...     },
        ...     "quotation_no": "Q-JCP-25-01-q1"
        ... })
        >>> # Returns: QuotationInfo(
        >>> #     client_name="ABC Engineering",
        >>> #     project_items=[
        >>> #         ProjectItem(content="支撐架計算", quantity=1, unit="Lot", subtotal=7000),
        >>> #         ProjectItem(content="吊燈計算", quantity=1, unit="Lot", subtotal=6000)
        >>> #     ],
        >>> #     total_amount=13000,
        >>> #     ...
        >>> # )

    Workflow:
        1. Parse and validate input parameters
        2. Build extraction prompt with user input, client info, and quotation number
        3. Invoke OpenAI LLM with structured output schema
        4. Return extracted QuotationInfo object

    LLM Prompt Details:
        The LLM is prompted to:
        - Parse item descriptions and amounts from natural language
        - Default unit to "Lot" if not specified
        - Default quantity to 1 if not specified
        - Calculate total_amount as sum of all item subtotals
        - Use provided client info and quotation number
        - Use current date if not specified

    Error Handling:
        - Returns {"error": "..."} for:
          - Missing required parameters
          - Invalid JSON input
          - LLM invocation failures
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
