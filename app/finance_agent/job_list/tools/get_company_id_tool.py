"""
Tool for retrieving company ID from the Finance database.

This module provides a simple lookup function to get company ID by name.
"""

from typing import Optional
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    CompanyFields
)
from app.finance_agent.utils.db_helper import find_one_by_field


def get_company_id_tool(company_name: str) -> Optional[int]:
    """
    Get the company ID from the database by company name.

    This is a simple lookup tool that searches for a company by exact name match
    and returns its ID. This is commonly used before creating jobs, as jobs
    require a valid company_id foreign key.

    Args:
        company_name: Company name to search for (case-sensitive exact match)

    Returns:
        Optional[int]: The company ID if found, None if not found

    Examples:
        >>> # Find existing company
        >>> company_id = get_company_id_tool("ABC Engineering")
        >>> # Returns: 17

        >>> # Company not found
        >>> company_id = get_company_id_tool("Non-existent Company")
        >>> # Returns: None

    Workflow:
        1. Query company table by name
        2. Return ID if found, None otherwise

    Usage Pattern:
        This tool is typically used in a sequence:
        1. Try to get company ID
        2. If None, create company first using create_company_tool
        3. Use the company ID to create a job

        Example agent workflow:
        ```
        company_id = get_company_id_tool("ABC Corp")
        if company_id is None:
            result = create_company_tool("ABC Corp")
            company_id = result["id"]
        create_job_tool({
            "company_id": company_id,
            "job_type": "inspection",
            "job_title": "Safety Inspection"
        })
        ```
    """
    company = find_one_by_field(
        table=DatabaseSchema.COMPANY_TABLE,
        field=CompanyFields.NAME,
        value=company_name,
        operation_name="get company ID"
    )

    return company[CompanyFields.ID] if company else None
