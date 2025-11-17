"""
Tool for generating invoice numbers based on job numbers.

This module provides functionality to generate unique invoice numbers
linked to specific jobs.
"""

from typing import Any, Dict
from app.finance_agent.utils.tool_input_parser import parse_tool_input_as_string, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    InvoiceFields,
    InvoicePrefixes
)
from app.finance_agent.utils.db_helper import DatabaseError
from app.postgres.db_connection import execute_query


# ============================================================================
# Business Logic Functions
# ============================================================================

def _parse_input(tool_input: Any) -> str:
    """
    Parse and validate tool input.

    Args:
        tool_input: Can be JSON string, dict, or plain string

    Returns:
        job_no string

    Raises:
        ValueError: If job_no is missing
    """
    # Handle dict input
    if isinstance(tool_input, dict):
        job_no = tool_input.get('job_no')
    # Handle string input (try JSON first, then plain string)
    elif isinstance(tool_input, str):
        import json
        try:
            params = json.loads(tool_input)
            job_no = params.get('job_no')
        except json.JSONDecodeError:
            # Plain string - treat as job_no
            job_no = tool_input
    else:
        raise ValueError(f"Unexpected input type: {type(tool_input)}")

    if not job_no:
        raise ValueError("job_no is required")

    return job_no


def _generate_invoice_no(job_no: str) -> str:
    """
    Generate invoice number from job number.

    Simply replaces the job number prefix with INV- prefix.

    Args:
        job_no: Job number (e.g., "JCP-25-01-1" or "JICP-25-01-1")

    Returns:
        Invoice number (e.g., "INV-JCP-25-01-1" or "INV-JICP-25-01-1")

    Examples:
        >>> _generate_invoice_no("JCP-25-01-1")
        "INV-JCP-25-01-1"
        >>> _generate_invoice_no("JICP-25-01-2")
        "INV-JICP-25-01-2"
    """
    return f"{InvoicePrefixes.INVOICE}{job_no}"


def _check_invoice_exists(invoice_no: str) -> bool:
    """
    Check if invoice with given number already exists in database.

    Args:
        invoice_no: Invoice number to check

    Returns:
        True if invoice exists, False otherwise
    """
    result = execute_query(
        f"""
        SELECT COUNT(*) as count
        FROM {DatabaseSchema.INVOICE_TABLE}
        WHERE {InvoiceFields.INV_NO} = %s
        """,
        params=(invoice_no,),
        fetch_results=True
    )

    if result and len(result) > 0:
        return result[0].get('count', 0) > 0

    return False


# ============================================================================
# Main Tool Function
# ============================================================================

def create_invoice_no_tool(tool_input: Any) -> Dict[str, Any]:
    """
    Generate a new invoice number based on the given job number.

    This tool creates invoice numbers following the pattern:
    INV-{job_no}

    Args:
        tool_input: Can be either:
            - JSON string: '{"job_no": "JCP-25-01-1"}'
            - Dictionary: {"job_no": "JCP-25-01-1"}
            - Plain string: "JCP-25-01-1"

    Required Parameter:
        - job_no: Job number (e.g., "JCP-25-01-1" or "JICP-25-01-1")

    Returns:
        dict: {
            "invoice_no": str (e.g., "INV-JCP-25-01-1"),
            "exists": bool (True if invoice already exists for this job)
        }

        On error: {"error": "error message"}

    Examples:
        >>> # First invoice for a job
        >>> create_invoice_no_tool("JCP-25-01-1")
        {"invoice_no": "INV-JCP-25-01-1", "exists": False}

        >>> # Invoice already exists
        >>> create_invoice_no_tool({"job_no": "JCP-25-01-1"})
        {"invoice_no": "INV-JCP-25-01-1", "exists": True}

    Workflow:
        1. Parse input to get job_no
        2. Generate invoice number: INV-{job_no}
        3. Check if invoice already exists in database
        4. Return invoice number and existence status

    Note:
        Unlike quotations which can have multiple versions (q1, q2, etc.),
        each job typically has only ONE invoice. If an invoice already exists,
        the system should update it rather than create a new one.
    """
    try:
        # Parse and validate input
        job_no = _parse_input(tool_input)

        # Generate invoice number
        invoice_no = _generate_invoice_no(job_no)

        # Check if invoice already exists
        exists = _check_invoice_exists(invoice_no)

        return {
            "invoice_no": invoice_no,
            "exists": exists
        }

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        error_msg = f"Unexpected error creating invoice number: {str(e)}"
        print(f"[ERROR][create_invoice_no_tool] {error_msg}")
        return {"error": error_msg}
