"""
Tool for creating quotation records in the Finance database.

This module provides functionality to:
- Create quotation records (one row per project item)
- Auto-create or lookup client companies
- Handle quotation items with proper field mapping
"""

from typing import Any, Dict, List
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    QuotationFields,
    QuotationDefaults,
    ErrorMessages
)
from app.finance_agent.utils.db_helper import DatabaseError
from app.postgres.db_connection import execute_query
from app.finance_agent.job_list.tools.create_company_tool import create_company_tool
from app.prompt.quotation_prompt_template import QuotationInfo


# ============================================================================
# Business Logic Functions
# ============================================================================

def _extract_quotation_info(
    tool_input: Any
) -> tuple[QuotationInfo, str, str]:
    """
    Extract quotation information from various input formats.

    Args:
        tool_input: Can be dict with 'extracted_info', or QuotationInfo object

    Returns:
        Tuple of (quotation_info, quotation_no, revision_str)

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if isinstance(tool_input, QuotationInfo):
        # Direct QuotationInfo object
        return tool_input, tool_input.no or '', QuotationDefaults.REVISION

    # Must be dict at this point (parse_tool_input handles str->dict conversion)
    if not isinstance(tool_input, dict):
        raise ValueError(f"Expected dict or QuotationInfo, got {type(tool_input)}")

    # Extract from dict
    if 'extracted_info' not in tool_input:
        raise ValueError("'extracted_info' is required in input")

    quotation_info_data = tool_input['extracted_info']

    # Handle QuotationInfo object
    if isinstance(quotation_info_data, QuotationInfo):
        quotation_info = quotation_info_data
    # Handle dict (agent may serialize QuotationInfo to dict)
    elif isinstance(quotation_info_data, dict):
        # Reconstruct QuotationInfo from dict
        quotation_info = QuotationInfo(**quotation_info_data)
    else:
        raise ValueError(
            f"'extracted_info' must be QuotationInfo object or dict, got {type(quotation_info_data)}"
        )

    quotation_no = tool_input.get('quotation_no', quotation_info.no or '')
    revision_str = tool_input.get('revision_str', QuotationDefaults.REVISION)

    return quotation_info, quotation_no, revision_str


def _ensure_client_exists(
    quotation_info: QuotationInfo
) -> int:
    """
    Ensure client company exists in database, create if needed.

    Args:
        quotation_info: Quotation info containing client details

    Returns:
        int: Company ID

    Raises:
        ValueError: If client name is missing
        DatabaseError: If company creation fails
    """
    if not quotation_info.client_name:
        raise ValueError("client_name is required")

    company_result = create_company_tool(
        company_name=quotation_info.client_name,
        address=quotation_info.client_address or '',
        phone=quotation_info.client_phone or ''
    )

    if 'id' not in company_result:
        raise DatabaseError(f"Failed to get company ID: {company_result}")

    return company_result['id']


def _insert_quotation_items(
    quotation_info: QuotationInfo,
    quotation_no: str,
    company_id: int,
    revision: int
) -> List[Dict[str, Any]]:
    """
    Insert quotation items into database (one row per item).

    Args:
        quotation_info: Quotation information with project items
        quotation_no: Generated quotation number
        company_id: Client company ID
        revision: Revision number

    Returns:
        List of inserted item records

    Raises:
        DatabaseError: If insertion fails
    """
    if not quotation_info.project_items:
        raise ValueError("No project items to insert")

    inserted_rows = []

    for item in quotation_info.project_items:
        rows = execute_query(
            f"""
            INSERT INTO {DatabaseSchema.QUOTATION_TABLE} (
                {QuotationFields.QUO_NO},
                {QuotationFields.DATE_ISSUED},
                {QuotationFields.CLIENT_ID},
                {QuotationFields.PROJECT_NAME},
                {QuotationFields.PROJECT_ITEM_DESCRIPTION},
                {QuotationFields.SUB_AMOUNT},
                {QuotationFields.TOTAL_AMOUNT},
                {QuotationFields.CURRENCY},
                {QuotationFields.REVISION},
                {QuotationFields.AMOUNT},
                {QuotationFields.UNIT}
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {QuotationFields.ID}, {QuotationFields.QUO_NO},
                      {QuotationFields.DATE_ISSUED}, {QuotationFields.CLIENT_ID},
                      {QuotationFields.PROJECT_NAME}, {QuotationFields.PROJECT_ITEM_DESCRIPTION},
                      {QuotationFields.SUB_AMOUNT}, {QuotationFields.TOTAL_AMOUNT},
                      {QuotationFields.CURRENCY}, {QuotationFields.REVISION},
                      {QuotationFields.AMOUNT}, {QuotationFields.UNIT}
            """,
            params=(
                quotation_no,
                quotation_info.date or None,
                company_id,
                quotation_info.project_name,
                item.content,  # project_item_description
                float(item.subtotal),  # sub_amount
                float(quotation_info.total_amount),  # total_amount (same for all items)
                quotation_info.currency,
                str(revision),
                float(item.quantity),  # amount field stores quantity
                item.unit  # unit field stores unit type (e.g., "Lot")
            ),
            fetch_results=True
        )

        if rows:
            inserted_rows.append(rows[0])

    if not inserted_rows:
        raise DatabaseError("Failed to insert quotation items: No data returned")

    return inserted_rows


def _format_creation_response(
    quotation_no: str,
    inserted_rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Format the response for successful quotation creation.

    Args:
        quotation_no: Created quotation number
        inserted_rows: List of inserted item records

    Returns:
        Dict with success status and item details
    """
    return {
        "success": True,
        "quotation_no": quotation_no,
        "items_inserted": len(inserted_rows),
        "items": [
            {
                "id": row[QuotationFields.ID],
                "project_item_description": row[QuotationFields.PROJECT_ITEM_DESCRIPTION],
                "sub_amount": row[QuotationFields.SUB_AMOUNT],
                "amount": row[QuotationFields.AMOUNT],
                "unit": row[QuotationFields.UNIT]
            }
            for row in inserted_rows
        ]
    }


# ============================================================================
# Main Tool Function
# ============================================================================

def create_quotation_in_db(tool_input: Any) -> Dict[str, Any]:
    """
    Create a new quotation in the database based on the quotation information.

    This function handles the complete quotation creation workflow:
    1. Extracts and validates quotation information
    2. Ensures client company exists (creates if needed)
    3. Inserts quotation items (ONE ROW PER ITEM)

    Important: This tool creates one database row per project item, not one row
    for the entire quotation. Each item has its own sub_amount, while all items
    share the same total_amount.

    Args:
        tool_input: Can be either:
            - Dict with keys:
                - extracted_info: QuotationInfo Pydantic object (required)
                - quotation_no: Quotation number (optional, defaults to info.no)
                - revision_str: Revision string (optional, defaults to "00")
            - QuotationInfo Pydantic object directly

    Returns:
        dict: Success response with structure:
            {
                "success": True,
                "quotation_no": "Q-JCP-25-01-q1",
                "items_inserted": 2,
                "items": [
                    {
                        "id": 1,
                        "project_item_description": "支撐架計算",
                        "sub_amount": 7000.0,
                        "amount": 1.0,
                        "unit": "Lot"
                    },
                    ...
                ]
            }

        On error: {"error": "error message"}

    Examples:
        >>> # With dict input
        >>> result = create_quotation_in_db({
        ...     "extracted_info": quotation_info_obj,
        ...     "quotation_no": "Q-JCP-25-01-q1",
        ...     "revision_str": "00"
        ... })

        >>> # With QuotationInfo object
        >>> result = create_quotation_in_db(quotation_info_obj)

    Workflow:
        1. Parse input and extract quotation info
        2. Validate client information exists
        3. Check if client company exists, create if needed
        4. Insert one row per project item with:
           - Individual sub_amount per item
           - Shared total_amount across all items
           - amount = item.quantity (e.g., 1)
           - unit = item.unit (e.g., "Lot")
        5. Return success response with created items

    Field Mapping:
        - amount ← item.quantity (numeric, e.g., 1)
        - unit ← item.unit (string, e.g., "Lot")
        - sub_amount ← item.subtotal (per item)
        - total_amount ← quotation_info.total_amount (same for all)
    """
    try:
        # Parse tool input first (handles JSON string -> dict conversion)
        if isinstance(tool_input, str):
            tool_input = parse_tool_input(
                tool_input,
                required_keys=['extracted_info'],
                tool_name="create_quotation_in_db"
            )

        # Extract and validate quotation information
        quotation_info, quotation_no, revision_str = _extract_quotation_info(tool_input)

        # Parse revision
        revision = int(revision_str) if revision_str else 0

        # Ensure client company exists
        company_id = _ensure_client_exists(quotation_info)

        # Insert quotation items (one row per item)
        inserted_rows = _insert_quotation_items(
            quotation_info=quotation_info,
            quotation_no=quotation_no,
            company_id=company_id,
            revision=revision
        )

        # Format and return success response
        return _format_creation_response(quotation_no, inserted_rows)

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        error_msg = f"Unexpected error creating quotation: {str(e)}"
        print(f"[ERROR][create_quotation_in_db] {error_msg}")
        return {"error": error_msg}
