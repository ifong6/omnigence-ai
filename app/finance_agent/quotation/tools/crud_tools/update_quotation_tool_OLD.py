import json
from app.postgres.db_connection import execute_query

def update_quotation_tool(tool_input) -> str:
    """
    Update existing quotation item(s) in the database.

    Args:
        tool_input: Can be either:
            - A JSON string like '{"quo_no": "Q-JCP-25-03-q1", "item_description": "支撐架計算", ...}'
            - A dict with keys:
                - quo_no (required): Quotation number to identify which quotation to update
                - item_id (optional): Specific item ID to update
                - item_description (optional): Item description to match for update
                - Optional fields to update: project_item_description, sub_amount, amount, unit,
                  total_amount, currency, revision, date_issued

    Returns:
        A message indicating success or failure with the updated quotation details

    Examples:
        # Update a specific item by ID
        {"quo_no": "Q-JCP-25-03-q1", "item_id": 7, "sub_amount": 8000}

        # Update all items with matching description
        {"quo_no": "Q-JCP-25-03-q1", "item_description": "支撐架計算", "sub_amount": 8000}

        # Update all items in a quotation
        {"quo_no": "Q-JCP-25-03-q1", "total_amount": 15000}
    """
    try:
        # Parse input
        if isinstance(tool_input, str):
            try:
                params = json.loads(tool_input)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON input - {tool_input}"
        elif isinstance(tool_input, dict):
            params = tool_input
        else:
            return f"Error: Unexpected input type {type(tool_input)}"

        # quo_no is required to identify which quotation to update
        quo_no = params.get('quo_no')
        if not quo_no:
            return "Error: quo_no is required to identify the quotation to update"

        # Build WHERE clause
        where_conditions = ["quo_no = %s"]
        where_values = [quo_no]

        # Add optional filters
        if 'item_id' in params:
            where_conditions.append("id = %s")
            where_values.append(params['item_id'])
        elif 'item_description' in params:
            where_conditions.append("project_item_description = %s")
            where_values.append(params['item_description'])

        # Build dynamic update query based on provided parameters
        update_fields = []
        update_values = []

        if 'project_item_description' in params:
            update_fields.append("project_item_description = %s")
            update_values.append(params['project_item_description'])

        if 'sub_amount' in params:
            update_fields.append("sub_amount = %s")
            update_values.append(float(params['sub_amount']))

        if 'amount' in params:
            update_fields.append("amount = %s")
            update_values.append(float(params['amount']))

        if 'unit' in params:
            update_fields.append("unit = %s")
            update_values.append(params['unit'])

        if 'total_amount' in params:
            update_fields.append("total_amount = %s")
            update_values.append(float(params['total_amount']))

        if 'currency' in params:
            update_fields.append("currency = %s")
            update_values.append(params['currency'])

        if 'revision' in params:
            update_fields.append("revision = %s")
            update_values.append(str(params['revision']))

        if 'date_issued' in params:
            if params['date_issued'] in ['current', 'now']:
                update_fields.append("date_issued = CURRENT_DATE")
            else:
                update_fields.append("date_issued = %s")
                update_values.append(params['date_issued'])

        if not update_fields:
            return "Error: No fields to update. Please provide at least one field to update."

        # Combine update values and where values
        all_values = update_values + where_values

        query = f"""
            UPDATE "Finance".quotation
            SET {', '.join(update_fields)}
            WHERE {' AND '.join(where_conditions)}
            RETURNING id, quo_no, project_item_description, sub_amount, amount, unit, total_amount, currency, revision, date_issued
        """

        rows = execute_query(
            query=query,
            params=tuple(all_values),
            fetch_results=True
        )

        if rows:
            result_message = f"Successfully updated {len(rows)} quotation item(s):\n"
            for row in rows:
                result_message += f"  - ID={row['id']}, Quo No={row['quo_no']}, Item={row.get('project_item_description')}, "
                result_message += f"Sub Amount={row.get('sub_amount')}, Amount={row.get('amount')}, Unit={row.get('unit')}, "
                result_message += f"Total={row.get('total_amount')} {row.get('currency')}, Revision={row.get('revision')}\n"
            return result_message
        else:
            return f"Failed to update quotation: No items found matching quo_no='{quo_no}'"

    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON input - {str(e)}"
    except Exception as e:
        error_msg = f"Error updating quotation: {str(e)}"
        print(error_msg)
        return error_msg
