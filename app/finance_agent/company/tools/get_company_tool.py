from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum


def get_company_tool(tool_input) -> dict:
    """
    Get company information by ID or name.

    Args:
        tool_input: Either a company name (string) or company ID (int)

    Returns:
        dict: Company information with id, name, address, phone
              or error dict if not found
    """

    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Try to parse as int first
        try:
            company_id = int(tool_input)
            company_name = None
        except ValueError:
            # It's a company name
            company_id = None
            company_name = tool_input
    elif isinstance(tool_input, int):
        company_id = tool_input
        company_name = None
    elif isinstance(tool_input, dict):
        company_id = tool_input.get("company_id")
        company_name = tool_input.get("company_name")
    else:
        return {
            "error": "Invalid input type. Expected string, int, or dict",
            "status": "error"
        }

    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    if company_id:
        query = f"""
            SELECT id, name, address, phone
            FROM {DBTable_Enum.COMPANY_TABLE}
            WHERE id = %s
            LIMIT 1
        """
        params = (company_id,)
    else:
        query = f"""
            SELECT id, name, address, phone
            FROM {DBTable_Enum.COMPANY_TABLE}
            WHERE name = %s
            LIMIT 1
        """
        params = (company_name.strip() if company_name else None,)

    try:
        rows = execute_query(query, params=params, fetch=True)

        if not rows:
            return {
                "error": f"Company not found",
                "status": "not_found"
            }

        result = dict(rows[0])
        result["status"] = "found"
        return result

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
