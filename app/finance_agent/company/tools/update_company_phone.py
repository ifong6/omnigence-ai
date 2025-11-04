from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum
from typing import Optional
import json


def update_company_phone(tool_input) -> dict:
    """
    Update company phone. Identify company by company_id or company_name.

    Args:
        tool_input: {"company_id" or "company_name": ..., "new_phone": str}

    Returns:
        dict with id, name, address, phone, status ("updated", "error", or "not_found")
    """

    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Strip surrounding quotes if present
        stripped = tool_input.strip().strip("'").strip('"')
        try:
            params = json.loads(stripped)
        except json.JSONDecodeError:
            return {
                "error": f"Invalid input format. Expected JSON dict. Received: {tool_input}",
                "status": "error"
            }
    elif isinstance(tool_input, dict):
        params = tool_input
    else:
        return {
            "error": "Invalid input type. Expected dict or JSON string",
            "status": "error"
        }

    company_id = params.get("company_id")
    company_name = params.get("company_name")
    new_phone = params.get("new_phone")

    # Validate inputs
    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    if not new_phone:
        return {
            "error": "new_phone is required",
            "status": "error"
        }

    # Find the company
    if company_id:
        query = f"SELECT id, name, address, phone FROM {DBTable_Enum.COMPANY_TABLE} WHERE id = %s LIMIT 1"
        params = (company_id,)
    else:
        query = f"SELECT id, name, address, phone FROM {DBTable_Enum.COMPANY_TABLE} WHERE name = %s LIMIT 1"
        params = (company_name.strip() if company_name else None,)

    existing = execute_query(query, params=params, fetch=True)

    if not existing:
        return {
            "error": f"Company not found",
            "status": "not_found"
        }

    # Get current values
    current = existing[0]
    company_id = current["id"]

    # Update the company phone
    try:
        rows = execute_query(
            f"""
            UPDATE {DBTable_Enum.COMPANY_TABLE}
            SET phone = %s
            WHERE id = %s
            RETURNING id, name, address, phone
            """,
            params=(new_phone.strip(), company_id),
            fetch=True
        )

        result = rows[0] if rows else None
        if result:
            result["status"] = "updated"
            result["message"] = f"Company ID {company_id} phone updated successfully"
            return result
        else:
            return {
                "error": "Failed to update company phone",
                "status": "error"
            }
        result["status"] = "updated"
        result["message"] = f"Company ID {company_id} phone updated successfully"
        return result

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
