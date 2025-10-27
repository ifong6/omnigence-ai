"""
Tool for updating quotation items in the Finance database.

This module provides functionality to update existing quotation items with
flexible filtering and field updates.
"""

from typing import Any, Dict, List, Optional, Tuple
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    QuotationFields,
    ErrorMessages
)
from app.finance_agent.utils.db_helper import DatabaseError
from app.postgres.db_connection import execute_query


# ============================================================================
# Business Logic Functions
# ============================================================================

def _build_where_clause(
    params: Dict[str, Any]
) -> Tuple[List[str], List[Any]]:
    """
    Build WHERE clause for identifying quotation items to update.

    Args:
        params: Parameters containing quo_no and optional filters

    Returns:
        Tuple of (where_conditions, where_values)
    """
    where_conditions = [f"{QuotationFields.QUO_NO} = %s"]
    where_values = [params['quo_no']]

    # Add optional item-specific filters
    if 'item_id' in params:
        where_conditions.append(f"{QuotationFields.ID} = %s")
        where_values.append(params['item_id'])
    elif 'item_description' in params:
        where_conditions.append(f"{QuotationFields.PROJECT_ITEM_DESCRIPTION} = %s")
        where_values.append(params['item_description'])

    return where_conditions, where_values


def _build_update_fields(
    params: Dict[str, Any]
) -> Tuple[List[str], List[Any]]:
    """
    Build SET clause for updating quotation fields.

    Args:
        params: Parameters containing fields to update

    Returns:
        Tuple of (update_fields, update_values)
    """
    update_fields = []
    update_values = []

    # Field mappings with type conversions
    field_mappings = {
        'project_item_description': (QuotationFields.PROJECT_ITEM_DESCRIPTION, str),
        'sub_amount': (QuotationFields.SUB_AMOUNT, float),
        'amount': (QuotationFields.AMOUNT, float),
        'unit': (QuotationFields.UNIT, str),
        'total_amount': (QuotationFields.TOTAL_AMOUNT, float),
        'currency': (QuotationFields.CURRENCY, str),
        'revision': (QuotationFields.REVISION, str),
    }

    for param_name, (field_name, converter) in field_mappings.items():
        if param_name in params:
            update_fields.append(f"{field_name} = %s")
            update_values.append(converter(params[param_name]))

    # Special handling for date_issued (supports 'current'/'now')
    if 'date_issued' in params:
        value = params['date_issued']
        if value in ['current', 'now']:
            update_fields.append(f"{QuotationFields.DATE_ISSUED} = CURRENT_DATE")
        else:
            update_fields.append(f"{QuotationFields.DATE_ISSUED} = %s")
            update_values.append(value)

    return update_fields, update_values


def _format_update_response(rows: List[Dict[str, Any]]) -> str:
    """
    Format success message with updated quotation item details.

    Args:
        rows: Updated quotation item records

    Returns:
        Formatted success message string
    """
    result_message = f"Successfully updated {len(rows)} quotation item(s):\n"

    for row in rows:
        result_message += (
            f"  - ID={row[QuotationFields.ID]}, "
            f"Quo No={row[QuotationFields.QUO_NO]}, "
            f"Item={row.get(QuotationFields.PROJECT_ITEM_DESCRIPTION)}, "
            f"Sub Amount={row.get(QuotationFields.SUB_AMOUNT)}, "
            f"Amount={row.get(QuotationFields.AMOUNT)}, "
            f"Unit={row.get(QuotationFields.UNIT)}, "
            f"Total={row.get(QuotationFields.TOTAL_AMOUNT)} {row.get(QuotationFields.CURRENCY)}, "
            f"Revision={row.get(QuotationFields.REVISION)}\n"
        )

    return result_message


# ============================================================================
# Main Tool Function
# ============================================================================

def update_quotation_tool(tool_input: Any) -> str:
    """
    Update existing quotation item(s) in the database.

    This tool provides flexible updates for quotation items, allowing you to:
    - Update specific items by ID or description
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
        - amount: New quantity (e.g., 1, 2, 3)
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

        >>> # Update date to current date
        >>> update_quotation_tool({
        ...     "quo_no": "Q-JCP-25-03-q1",
        ...     "date_issued": "current"
        ... })

    Error Handling:
        - Returns descriptive error messages for:
          - Missing quo_no parameter
          - Invalid JSON input
          - No fields to update
          - No matching items found
          - Database errors
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['quo_no'],
            tool_name="update_quotation_tool"
        )

        # Build WHERE clause for filtering
        where_conditions, where_values = _build_where_clause(params)

        # Build SET clause for updates
        update_fields, update_values = _build_update_fields(params)

        # Validate we have fields to update
        if not update_fields:
            return ErrorMessages.NO_ITEMS_TO_UPDATE

        # Combine values: update values first, then where values
        all_values = update_values + where_values

        # Build and execute query
        query = f"""
            UPDATE {DatabaseSchema.QUOTATION_TABLE}
            SET {', '.join(update_fields)}
            WHERE {' AND '.join(where_conditions)}
            RETURNING {QuotationFields.ID}, {QuotationFields.QUO_NO},
                      {QuotationFields.PROJECT_ITEM_DESCRIPTION},
                      {QuotationFields.SUB_AMOUNT}, {QuotationFields.AMOUNT},
                      {QuotationFields.UNIT}, {QuotationFields.TOTAL_AMOUNT},
                      {QuotationFields.CURRENCY}, {QuotationFields.REVISION},
                      {QuotationFields.DATE_ISSUED}
        """

        rows = execute_query(
            query=query,
            params=tuple(all_values),
            fetch_results=True
        )

        # Handle results
        if rows:
            return _format_update_response(rows)
        else:
            return ErrorMessages.RECORD_NOT_FOUND.format(
                tool="update_quotation_tool",
                entity="quotation item",
                field="quo_no",
                value=params['quo_no']
            )

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error updating quotation: {str(e)}"
        print(f"[ERROR][update_quotation_tool] {error_msg}")
        return error_msg
