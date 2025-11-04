from typing import Optional
from database.supabase.db_enum import DBTable_Enum
from database.db_helper import find_one_by_field


def get_company_id_tool(company_name: str) -> Optional[int]:
    """
    Get company ID by name. Returns None if not found.

    Args:
        company_name: Company name to search for

    Returns:
        Company ID (int) or None
    """
    company = find_one_by_field(
        table=DBTable_Enum.COMPANY_TABLE,
        field="name",
        value=company_name,
        operation_name="get company ID"
    )

    # RealDictRow objects can be accessed with string keys like dicts
    return company["id"] if company else None
