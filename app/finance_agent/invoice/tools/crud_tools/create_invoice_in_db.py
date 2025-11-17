"""
Tool for creating invoice records in the Finance database.

This module provides functionality to:
- Create invoice records (one row per invoice item)
- Auto-create or lookup client companies
- Handle invoice items with proper field mapping
"""

from typing import Any, Dict, List
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    InvoiceFields,
    InvoiceDefaults,
    ErrorMessages
)
from app.finance_agent.utils.db_helper import DatabaseError
from app.postgres.db_connection import execute_query
from app.finance_agent.job_list.tools.create_company_tool import create_company_tool
from app.prompt.invoice_prompt_template import InvoiceInfo


# ============================================================================
# Business Logic Functions
# ============================================================================

def _extract_invoice_info(
    tool_input: Any
) -> InvoiceInfo:
    """
    Extract invoice information from various input formats.

    Args:
        tool_input: Can be dict with 'extracted_info', or InvoiceInfo object

    Returns:
        InvoiceInfo object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if isinstance(tool_input, InvoiceInfo):
        # Direct InvoiceInfo object
        return tool_input

    # Must be dict at this point (parse_tool_input handles str->dict conversion)
    if not isinstance(tool_input, dict):
        raise ValueError(f"Expected dict or InvoiceInfo, got {type(tool_input)}")

    # Extract from dict
    if 'extracted_info' not in tool_input:
        raise ValueError("'extracted_info' is required in input")

    invoice_info_data = tool_input['extracted_info']

    # Handle InvoiceInfo object
    if isinstance(invoice_info_data, InvoiceInfo):
        invoice_info = invoice_info_data
    # Handle dict (agent may serialize InvoiceInfo to dict)
    elif isinstance(invoice_info_data, dict):
        # Reconstruct InvoiceInfo from dict
        invoice_info = InvoiceInfo(**invoice_info_data)
    else:
        raise ValueError(
            f"'extracted_info' must be InvoiceInfo object or dict, got {type(invoice_info_data)}"
        )

    return invoice_info


def _ensure_client_exists(
    invoice_info: InvoiceInfo
) -> int:
    """
    Ensure client company exists in database, create if needed.

    Args:
        invoice_info: Invoice info containing client details

    Returns:
        int: Company ID

    Raises:
        ValueError: If client name is missing
        DatabaseError: If company creation fails
    """
    if not invoice_info.client_name:
        raise ValueError("client_name is required")

    company_result = create_company_tool(
        company_name=invoice_info.client_name,
        address=invoice_info.client_address or '',
        phone=invoice_info.client_phone or ''
    )

    if 'id' not in company_result:
        raise DatabaseError(f"Failed to get company ID: {company_result}")

    return company_result['id']


def _insert_invoice_items(
    invoice_info: InvoiceInfo,
    invoice_no: str,
    company_id: int
) -> List[Dict[str, Any]]:
    """
    Insert invoice items into database (one row per item).

    Args:
        invoice_info: Invoice information with invoice items
        invoice_no: Generated invoice number
        company_id: Client company ID

    Returns:
        List of inserted item records

    Raises:
        DatabaseError: If insertion fails
    """
    if not invoice_info.invoice_items:
        raise ValueError("No invoice items to insert")

    inserted_rows = []

    for item in invoice_info.invoice_items:
        rows = execute_query(
            f"""
            INSERT INTO {DatabaseSchema.INVOICE_TABLE} (
                {InvoiceFields.INV_NO},
                {InvoiceFields.DATE_ISSUED},
                {InvoiceFields.DUE_DATE},
                {InvoiceFields.CLIENT_ID},
                {InvoiceFields.PROJECT_NAME},
                {InvoiceFields.JOB_NO},
                {InvoiceFields.QUOTATION_NO},
                {InvoiceFields.INVOICE_ITEM_DESCRIPTION},
                {InvoiceFields.SUB_AMOUNT},
                {InvoiceFields.TOTAL_AMOUNT},
                {InvoiceFields.CURRENCY},
                {InvoiceFields.STATUS},
                {InvoiceFields.AMOUNT},
                {InvoiceFields.UNIT},
                {InvoiceFields.NOTES}
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {InvoiceFields.ID}, {InvoiceFields.INV_NO},
                      {InvoiceFields.DATE_ISSUED}, {InvoiceFields.DUE_DATE},
                      {InvoiceFields.CLIENT_ID}, {InvoiceFields.PROJECT_NAME},
                      {InvoiceFields.JOB_NO}, {InvoiceFields.QUOTATION_NO},
                      {InvoiceFields.INVOICE_ITEM_DESCRIPTION},
                      {InvoiceFields.SUB_AMOUNT}, {InvoiceFields.TOTAL_AMOUNT},
                      {InvoiceFields.CURRENCY}, {InvoiceFields.STATUS},
                      {InvoiceFields.AMOUNT}, {InvoiceFields.UNIT},
                      {InvoiceFields.NOTES}
            """,
            params=(
                invoice_no,
                invoice_info.date or None,
                invoice_info.due_date or None,
                company_id,
                invoice_info.project_name,
                invoice_info.job_no or None,
                invoice_info.quotation_no or None,
                item.content,  # invoice_item_description
                float(item.subtotal),  # sub_amount
                float(invoice_info.total_amount),  # total_amount (same for all items)
                invoice_info.currency,
                invoice_info.status or InvoiceDefaults.STATUS,
                float(item.quantity),  # amount field stores quantity
                item.unit,  # unit field stores unit type (e.g., "Lot")
                invoice_info.notes or ""
            ),
            fetch_results=True
        )

        if rows:
            inserted_rows.append(rows[0])

    if not inserted_rows:
        raise DatabaseError("Failed to insert invoice items: No data returned")

    return inserted_rows


def _format_creation_response(
    invoice_no: str,
    inserted_rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Format the response for successful invoice creation.

    Args:
        invoice_no: Created invoice number
        inserted_rows: List of inserted item records

    Returns:
        Dict with success status and item details
    """
    return {
        "success": True,
        "invoice_no": invoice_no,
        "items_inserted": len(inserted_rows),
        "items": [
            {
                "id": row[InvoiceFields.ID],
                "invoice_item_description": row[InvoiceFields.INVOICE_ITEM_DESCRIPTION],
                "sub_amount": row[InvoiceFields.SUB_AMOUNT],
                "amount": row[InvoiceFields.AMOUNT],
                "unit": row[InvoiceFields.UNIT]
            }
            for row in inserted_rows
        ]
    }


# ============================================================================
# Main Tool Function
# ============================================================================

def create_invoice_in_db(tool_input: Any) -> Dict[str, Any]:
    """
    Create a new invoice in the database based on the invoice information.

    This function handles the complete invoice creation workflow:
    1. Extracts and validates invoice information
    2. Ensures client company exists (creates if needed)
    3. Inserts invoice items (ONE ROW PER ITEM)

    Important: This tool creates one database row per invoice item, not one row
    for the entire invoice. Each item has its own sub_amount, while all items
    share the same total_amount.

    Args:
        tool_input: Can be either:
            - Dict with keys:
                - extracted_info: InvoiceInfo Pydantic object (required)
                - invoice_no: Invoice number (required)
            - InvoiceInfo Pydantic object directly (requires 'no' field)

    Returns:
        dict: Success response with structure:
            {
                "success": True,
                "invoice_no": "INV-JCP-25-01-1",
                "items_inserted": 2,
                "items": [
                    {
                        "id": 1,
                        "invoice_item_description": "樑模板計算",
                        "sub_amount": 5000.0,
                        "amount": 1.0,
                        "unit": "Lot"
                    },
                    ...
                ]
            }

        On error: {"error": "error message"}

    Examples:
        >>> # With dict input
        >>> result = create_invoice_in_db({
        ...     "extracted_info": invoice_info_obj,
        ...     "invoice_no": "INV-JCP-25-01-1"
        ... })

        >>> # With InvoiceInfo object (must have 'no' field)
        >>> result = create_invoice_in_db(invoice_info_obj)

    Workflow:
        1. Parse input and extract invoice info
        2. Validate client information exists
        3. Check if client company exists, create if needed
        4. Insert one row per invoice item with:
           - Individual sub_amount per item
           - Shared total_amount across all items
           - amount = item.quantity (e.g., 1)
           - unit = item.unit (e.g., "Lot")
           - status = invoice status (pending, paid, etc.)
        5. Return success response with created items

    Field Mapping:
        - amount ← item.quantity (numeric, e.g., 1)
        - unit ← item.unit (string, e.g., "Lot")
        - sub_amount ← item.subtotal (per item)
        - total_amount ← invoice_info.total_amount (same for all)
        - status ← invoice_info.status (pending/paid/overdue/cancelled)
    """
    try:
        # Parse tool input first (handles JSON string -> dict conversion)
        if isinstance(tool_input, str):
            tool_input = parse_tool_input(
                tool_input,
                required_keys=['extracted_info', 'invoice_no'],
                tool_name="create_invoice_in_db"
            )

        # Extract and validate invoice information
        invoice_info = _extract_invoice_info(tool_input)

        # Get invoice number from input or from invoice_info
        if isinstance(tool_input, dict):
            invoice_no = tool_input.get('invoice_no', invoice_info.no)
        else:
            invoice_no = invoice_info.no

        if not invoice_no:
            raise ValueError("invoice_no is required")

        # Ensure client company exists
        company_id = _ensure_client_exists(invoice_info)

        # Insert invoice items (one row per item)
        inserted_rows = _insert_invoice_items(
            invoice_info=invoice_info,
            invoice_no=invoice_no,
            company_id=company_id
        )

        # Format and return success response
        return _format_creation_response(invoice_no, inserted_rows)

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        error_msg = f"Unexpected error creating invoice: {str(e)}"
        print(f"[ERROR][create_invoice_in_db] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}
