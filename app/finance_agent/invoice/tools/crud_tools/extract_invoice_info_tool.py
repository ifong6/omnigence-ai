"""
Tool for extracting invoice information from user input using LLM.

This module uses an LLM to parse natural language input and extract
structured invoice information including items, pricing, and client details.
"""

from typing import Any, Dict
from app.llm.invoke_openai_llm import invoke_openai_llm
from app.prompt.invoice_prompt_template import (
    InvoiceInfoExtractOutput,
    EXTRACT_INVOICE_PROMPT_TEMPLATE
)


# ============================================================================
# Main Tool Function
# ============================================================================

def extract_invoice_info_tool(tool_input: Any) -> Dict[str, Any]:
    """
    Extract structured invoice information from natural language input using LLM.

    This tool uses an LLM to parse user input and extract:
    - Client information (name, address, phone)
    - Project details
    - Job and quotation references
    - Invoice items with pricing
    - Payment terms and due dates
    - Additional notes

    Args:
        tool_input: Can be either:
            - String: Direct user input to extract from
            - Dictionary with keys:
                - user_input: User's invoice request (required)
                - client_info: Pre-filled client info (optional)
                - job_no: Pre-filled job number (optional)
                - quotation_no: Pre-filled quotation number (optional)
                - date: Pre-filled invoice date (optional)

    Returns:
        dict: Extracted invoice information with structure:
            {
                "invoice_info": {
                    "client_name": str,
                    "client_address": str,
                    "client_phone": str,
                    "project_name": str,
                    "job_no": str or None,
                    "quotation_no": str or None,
                    "no": str or None,
                    "date": str or None,
                    "due_date": str or None,
                    "invoice_items": [
                        {
                            "no": int,
                            "content": str,
                            "quantity": str,
                            "unit": str,
                            "unit_price": str,
                            "subtotal": str
                        },
                        ...
                    ],
                    "total_amount": str,
                    "currency": str,
                    "status": str,
                    "notes": str
                },
                "messages": [str, ...]
            }

        On error: {"error": "error message"}

    Examples:
        >>> # Simple string input
        >>> extract_invoice_info_tool("長聯建築 A3連接橋計算 7000MOP")
        {
            "invoice_info": {
                "client_name": "長聯建築",
                "project_name": "A3連接橋計算",
                "invoice_items": [{"no": 1, "content": "...", ...}],
                "total_amount": "7000",
                ...
            },
            "messages": [...]
        }

        >>> # Dict input with pre-filled info
        >>> extract_invoice_info_tool({
        ...     "user_input": "樑模板計算 5000 MOP, 牆體模板計算 5000 MOP",
        ...     "client_info": "金輝工程有限公司",
        ...     "job_no": "JCP-25-01-1",
        ...     "date": "2025-01-20"
        ... })

    Workflow:
        1. Parse input to extract user_input and optional pre-filled fields
        2. Build prompt with user input and pre-filled information
        3. Invoke LLM to extract structured invoice information
        4. Return extracted invoice info with messages

    Note:
        The LLM will auto-generate item numbers sequentially (1, 2, 3, ...)
        and calculate subtotals. It will also validate that total_amount
        matches the sum of all subtotals.
    """
    try:
        # Parse input
        if isinstance(tool_input, str):
            user_input = tool_input
            client_info = ""
            job_no = ""
            quotation_no = ""
            date = ""
        elif isinstance(tool_input, dict):
            user_input = tool_input.get('user_input', '')
            client_info = tool_input.get('client_info', '')
            job_no = tool_input.get('job_no', '')
            quotation_no = tool_input.get('quotation_no', '')
            date = tool_input.get('date', '')
        else:
            raise ValueError(f"Unexpected input type: {type(tool_input)}")

        if not user_input:
            raise ValueError("user_input is required")

        # Build prompt
        system_prompt = EXTRACT_INVOICE_PROMPT_TEMPLATE.format(
            user_input=user_input,
            client_info=client_info,
            job_no=job_no,
            quotation_no=quotation_no,
            date=date
        )

        # Invoke LLM to extract invoice info
        parsed_response = invoke_openai_llm(system_prompt, InvoiceInfoExtractOutput)

        # Convert Pydantic model to dict for JSON serialization
        return {
            "invoice_info": parsed_response.invoice_info.model_dump(),
            "messages": parsed_response.messages
        }

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        error_msg = f"Unexpected error extracting invoice info: {str(e)}"
        print(f"[ERROR][extract_invoice_info_tool] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}
