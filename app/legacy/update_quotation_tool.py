from typing import Any, Dict, List
from sqlmodel import Session

from app.db.engine import engine
from app.services.quotation_service import QuotationService
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError


# ============================================================================
# Business Logic Functions
# ============================================================================

def _get_quotation_ids_to_update(
    session: Session,
    params: Dict[str, Any]
) -> List[int]:
    """
    Get list of quotation item IDs to update based on filters.

    Args:
        session: SQLModel session
        params: Parameters containing quo_no and optional filters

    Returns:
        List of quotation item IDs to update
    """
    quotation_service = QuotationService(session)
    quo_no = params['quo_no']

    # Case 1: Update specific item by ID
    if 'item_id' in params:
        return [params['item_id']]

    # Case 2: Get all items with quo_no
    items = quotation_service.get_quotations_by_quo_no(quo_no)

    # Case 3: Filter by description if provided
    if 'item_description' in params:
        items = [
            item for item in items
            if item.project_item_description == params['item_description']
        ]

    ids = [item.id for item in items if item.id is not None]
    return ids


def _build_update_fields(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build update fields dict for QuotationService.

    Args:
        params: Parameters containing fields to update

    Returns:
        Dict of fields to update
    """
    update_fields = {}

    # Field mappings
    field_mappings = {
        'project_item_description': 'project_item_description',
        'sub_amount': 'sub_amount',
        'quantity': 'quantity',
        'unit': 'unit',
        'total_amount': 'total_amount',
        'currency': 'currency',
        'revision': 'revision',
        'date_issued': 'date_issued',
    }

    for param_name, field_name in field_mappings.items():
        if param_name in params:
            value = params[param_name]

            # Handle special date values
            if param_name == 'date_issued' and value in ['current', 'now']:
                from datetime import date
                value = date.today()

            update_fields[field_name] = value

    return update_fields


def _format_update_response(updated_items: List) -> str:
    """
    Format success message with updated quotation item details.

    Args:
        updated_items: List of updated Quotation ORM objects

    Returns:
        Formatted success message string
    """
    if not updated_items:
        return "No items were updated."

    result_message = f"Successfully updated {len(updated_items)} quotation item(s):\n"

    for item in updated_items:
        result_message += (
            f"  - ID={item.id}, "
            f"Quo No={item.quo_no}, "
            f"Item={item.project_item_description}, "
            f"Sub Amount={item.sub_amount}, "
            f"Quantity={item.quantity}, "
            f"Unit={item.unit}, "
            f"Total={item.total_amount} {item.currency}, "
            f"Revision={item.revision}\n"
        )

    return result_message


# ============================================================================
# Main Tool Function
# ============================================================================

def update_quotation_tool(tool_input: Any) -> str:
    """
    Update existing quotation item(s) in the database using QuotationService.

    Refactored to use centralized QuotationService with SQLModel ORM.

    This tool provides flexible updates for quotation items, allowing you to:
    - Update specific items by ID
    - Update items matching a description
    - Update all items in a quotation
    - Update multiple fields at once

    Args:
        tool_input: Can be either:
            - JSON string: '{"quo_no": "Q-JCP-25-03-q1", "item_id": 7, ...}'
            - Dictionary: {"quo_no": "Q-JCP-25-03-q1", "sub_amount": 8000}

    Required Parameter:
        - quo_no: Quotation number to identify which quotation to update

    Optional Filters (choose one to target specific items):
        - item_id: Update only the item with this ID
        - item_description: Update only items matching this description
        - (no filter): Update all items in the quotation

    Optional Fields to Update:
        - project_item_description: New item description
        - sub_amount: New subtotal for the item
        - quantity: New quantity (e.g., 1, 2, 3)
        - unit: New unit type (e.g., "Lot", "Each")
        - total_amount: New total amount (same for all items)
        - currency: New currency code
        - revision: New revision string
        - date_issued: New date or 'current'/'now' for today

    Returns:
        Success message with updated item details, or error message

    Examples:
        >>> # Update a specific item by ID
        >>> update_quotation_tool({
        ...     "quo_no": "Q-JCP-25-03-q1",
        ...     "item_id": 7,
        ...     "sub_amount": 8000
        ... })

        >>> # Update all items with matching description
        >>> update_quotation_tool({
        ...     "quo_no": "Q-JCP-25-03-q1",
        ...     "item_description": "支撐架計算",
        ...     "sub_amount": 8000,
        ...     "unit": "Each"
        ... })

        >>> # Update total amount for all items in quotation
        >>> update_quotation_tool({
        ...     "quo_no": "Q-JCP-25-03-q1",
        ...     "total_amount": 15000
        ... })
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['quo_no'],
            tool_name="update_quotation_tool"
        )

        # Use QuotationService with session
        with Session(engine) as session:
            # Get IDs of items to update
            quotation_ids = _get_quotation_ids_to_update(session, params)

            if not quotation_ids:
                return f"Error: No quotation items found with quo_no={params['quo_no']}"

            # Build update fields
            update_fields = _build_update_fields(params)

            if not update_fields:
                return "Error: No fields to update provided"

            # Update quotations using QuotationService
            quotation_service = QuotationService(session)
            updated_items = quotation_service.update_quotation(
                quotation_ids,
                **update_fields
            )

            # Commit transaction
            session.commit()

            # Format and return success response
            return _format_update_response(updated_items)

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error updating quotation: {str(e)}"
        print(f"[ERROR][update_quotation_tool] {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg
