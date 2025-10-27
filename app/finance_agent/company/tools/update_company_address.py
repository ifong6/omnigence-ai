from app.postgres.db_connection import execute_query
from typing import Optional
import json


def _normalize_address(addr: Optional[str]) -> Optional[str]:
    """Normalize address by collapsing whitespace."""
    if not addr:
        return None
    return " ".join(addr.split())


def update_company_address(tool_input) -> dict:
    """
    Update a company's address.

    You can identify the company either by company_id OR company_name.

    Args:
        tool_input: Dict with keys {company_id OR company_name, new_address}

    Returns:
        dict: {
            "id": int,
            "name": str,
            "address": str or None,
            "phone": str or None,
            "status": "updated" or "error" or "not_found"
        }
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
    new_address = params.get("new_address")

    # Validate inputs
    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    if not new_address:
        return {
            "error": "new_address is required",
            "status": "error"
        }

    # Find the company
    if company_id:
        query = "SELECT id, name, address, phone FROM \"Finance\".company WHERE id = %s LIMIT 1"
        params = (company_id,)
    else:
        query = "SELECT id, name, address, phone FROM \"Finance\".company WHERE name = %s LIMIT 1"
        params = (company_name.strip(),)

    existing = execute_query(query, params=params, fetch_results=True)

    if not existing:
        return {
            "error": f"Company not found",
            "status": "not_found"
        }

    # Get current values
    current = existing[0]
    company_id = current["id"]

    # Normalize the new address
    normalized_address = _normalize_address(new_address)

    # Update the company address
    try:
        rows = execute_query(
            """
            UPDATE "Finance".company
            SET address = %s
            WHERE id = %s
            RETURNING id, name, address, phone
            """,
            params=(normalized_address, company_id),
            fetch_results=True
        )

        result = rows[0]
        result["status"] = "updated"
        result["message"] = f"Company ID {company_id} address updated successfully"
        return result

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
