"""
Tool for creating quotation records in the Finance database.

Refactored to use centralized QuotationService with SQLModel ORM.
"""

from typing import Any, Dict, List
from decimal import Decimal
from sqlmodel import Session

from app.db.engine import engine
from app.services.quotation_service import QuotationService
from app.services.company_service import CompanyService
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import QuotationDefaults
from app.prompt.quotation_prompt_template import QuotationInfo


# ============================================================================
# Business Logic Functions
# ============================================================================

def _extract_quotation_info(tool_input: Any) -> tuple[QuotationInfo, str]:
    """
    Extract quotation information from various input formats.

    Args:
        tool_input: Can be dict with 'extracted_info', or QuotationInfo object

    Returns:
        Tuple of (quotation_info, job_no)

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if isinstance(tool_input, QuotationInfo):
        # Direct QuotationInfo object
        # Extract job_no from quotation.no (e.g., "Q-JCP-25-01-q1" -> "JCP-25-01-1")
        job_no = _extract_job_no_from_quo_no(tool_input.no or '')
        return tool_input, job_no

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

    # Get job_no from input or extract from quotation_no
    job_no = tool_input.get('job_no', '')
    if not job_no and quotation_info.no:
        job_no = _extract_job_no_from_quo_no(quotation_info.no)

    return quotation_info, job_no


def _extract_job_no_from_quo_no(quo_no: str) -> str:
    """
    Extract job number from quotation number.

    Args:
        quo_no: Quotation number like "Q-JCP-25-01-q1-R00"

    Returns:
        Job number like "JCP-25-01-1"
    """
    if not quo_no:
        return ''

    # Remove "Q-" prefix and "-qX-RXX" suffix
    # "Q-JCP-25-01-q1-R00" -> "JCP-25-01"
    import re
    match = re.match(r'Q-(.+?)-q\d+', quo_no)
    if match:
        base = match.group(1)  # "JCP-25-01"
        return f"{base}-1"  # Add default index
    return ''


def _ensure_client_exists(session: Session, quotation_info: QuotationInfo) -> int:
    """
    Ensure client company exists in database, create if needed using CompanyService.

    Args:
        session: SQLModel session
        quotation_info: Quotation info containing client details

    Returns:
        int: Company ID

    Raises:
        ValueError: If client name is missing
    """
    if not quotation_info.client_name:
        raise ValueError("client_name is required")

    company_service = CompanyService(session)

    # Use get_or_create to ensure company exists
    company = company_service.get_or_create(
        name=quotation_info.client_name,
        address=quotation_info.client_address or None,
        phone=quotation_info.client_phone or None
    )

    return company.id


def _convert_items_to_dict(quotation_info: QuotationInfo) -> List[Dict[str, Any]]:
    """
    Convert QuotationInfo project items to format expected by QuotationService.

    Args:
        quotation_info: Quotation information with project items

    Returns:
        List of item dicts for QuotationService

    Raises:
        ValueError: If no project items
    """
    if not quotation_info.project_items:
        raise ValueError("No project items to insert")

    items = []
    for item in quotation_info.project_items:
        items.append({
            "project_item_description": item.content,
            "quantity": float(item.quantity),
            "unit": item.unit,
            "sub_amount": Decimal(str(item.subtotal)),
            "total_amount": Decimal(str(quotation_info.total_amount))
        })

    return items


def _format_creation_response(quotation_no: str, created_items: List) -> Dict[str, Any]:
    """
    Format the response for successful quotation creation.

    Args:
        quotation_no: Created quotation number
        created_items: List of created Quotation ORM objects

    Returns:
        Dict with success status and item details
    """
    return {
        "success": True,
        "quotation_no": quotation_no,
        "items_inserted": len(created_items),
        "items": [
            {
                "id": item.id,
                "project_item_description": item.project_item_description,
                "sub_amount": float(item.sub_amount) if item.sub_amount else 0,
                "quantity": item.quantity,
                "unit": item.unit
            }
            for item in created_items
        ]
    }


# ============================================================================
# Main Tool Function
# ============================================================================

def create_quotation_in_db(tool_input: Any) -> Dict[str, Any]:
    """
    Create a new quotation in the database using QuotationService.

    Refactored to use centralized QuotationService with SQLModel ORM.
    This function handles the complete quotation creation workflow:
    1. Extracts and validates quotation information
    2. Ensures client company exists (creates if needed using CompanyService)
    3. Creates quotation with multiple items using QuotationService

    Args:
        tool_input: Can be either:
            - Dict with keys:
                - extracted_info: QuotationInfo Pydantic object (required)
                - job_no: Job number (optional, can be extracted from quotation_no)
            - QuotationInfo Pydantic object directly

    Returns:
        dict: Success response with structure:
            {
                "success": True,
                "quotation_no": "Q-JCP-25-01-q1-R00",
                "items_inserted": 2,
                "items": [
                    {
                        "id": 1,
                        "project_item_description": "支撐架計算",
                        "sub_amount": 7000.0,
                        "quantity": 1.0,
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
        ...     "job_no": "JCP-25-01-1"
        ... })

        >>> # With QuotationInfo object
        >>> result = create_quotation_in_db(quotation_info_obj)

    Workflow:
        1. Parse input and extract quotation info and job_no
        2. Create session and initialize services
        3. Ensure client company exists (get_or_create)
        4. Convert items to service format
        5. Call QuotationService.create_quotation() to create all items
        6. Commit transaction
        7. Return success response with created items
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
        quotation_info, job_no = _extract_quotation_info(tool_input)

        if not job_no:
            raise ValueError("job_no is required (either in input or extractable from quotation_no)")

        # Use QuotationService with session
        with Session(engine) as session:
            # Ensure client company exists
            company_id = _ensure_client_exists(session, quotation_info)

            # Convert items to format expected by QuotationService
            items = _convert_items_to_dict(quotation_info)

            # Create quotation using QuotationService
            quotation_service = QuotationService(session)
            created_items = quotation_service.create_quotation(
                job_no=job_no,
                company_id=company_id,
                project_name=quotation_info.project_name or '',
                currency=quotation_info.currency or 'MOP',
                items=items,
                date_issued=quotation_info.date,
                revision_no="00"  # Default to no revision
            )

            # Commit transaction
            session.commit()

            # Format and return success response
            quotation_no = created_items[0].quo_no if created_items else ''
            return _format_creation_response(quotation_no, created_items)

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except Exception as e:
        error_msg = f"Unexpected error creating quotation: {str(e)}"
        print(f"[ERROR][create_quotation_in_db] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}
