"""
Tool for retrieving client information by project name.

This module provides functionality to lookup client (company) details
by joining job and company tables.
"""

from typing import Optional, Dict, Any
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    JobFields,
    CompanyFields
)
from database.supabase.db_connection import execute_query


def get_client_info_by_project_name_tool(
    project_name: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch the client information for a given project name by joining
    the design_job/inspection_job and company tables.

    IMPORTANT: Jobs are now stored in separate tables:
    - Finance.design_job for DESIGN jobs
    - Finance.inspection_job for INSPECTION jobs

    This tool is commonly used when creating quotations to retrieve the
    client's contact information (name, address, phone) for a specific project.

    Args:
        project_name: The project title/name to search for (exact match)
            Examples: "CCC大樓-公共部份樓宇檢測", "結構安全檢測"

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing client info if found:
            {
                "id": int,           # Company ID
                "name": str,         # Company name
                "address": str,      # Company address
                "phone": str         # Company phone
            }
            None if no matching project found

    Examples:
        >>> # Find client info for existing project
        >>> client = get_client_info_by_project_name_tool("結構安全檢測")
        >>> # Returns:
        >>> # {
        >>> #     "id": 1,
        >>> #     "name": "長聯建築工程有限公司",
        >>> #     "address": "庇山耶街56號地下",
        >>> #     "phone": "28352513"
        >>> # }

        >>> # Project not found
        >>> client = get_client_info_by_project_name_tool("Non-existent")
        >>> # Returns: None

    Workflow:
        1. Try design_job table first (JOIN with company)
        2. If not found, try inspection_job table (JOIN with company)
        3. Return company details if found, None otherwise

    Usage Pattern:
        This tool is typically used during quotation creation:
        1. Get job number by project name
        2. Get client info by project name (this tool)
        3. Create quotation number
        4. Extract quotation items
        5. Create quotation with client info

        Example agent workflow:
        ```
        job_no = get_job_no_by_project_name_tool("My Project")
        client_info = get_client_info_by_project_name_tool("My Project")

        if not client_info:
            return "Error: Client not found for project"

        # Use client_info in quotation creation
        create_quotation_in_db({
            "extracted_info": quotation_info,
            "quotation_no": quo_no,
            # client_info will be looked up again inside, but this
            # validation ensures the project exists first
        })
        ```

    Notes:
        - Uses exact match on project title (case-sensitive)
        - Returns the most recent job if multiple jobs have the same title
        - Returns None (not an error) if project doesn't exist
        - Company information comes from the job's associated company_id
        - Since a company only does one type of job, searches design first then inspection
    """
    # Try design_job first
    rows = execute_query(
        f"""
        SELECT
            c.{CompanyFields.ID},
            c.{CompanyFields.NAME},
            c.{CompanyFields.ADDRESS},
            c.{CompanyFields.PHONE}
        FROM {DatabaseSchema.DESIGN_JOB_TABLE} j
        INNER JOIN {DatabaseSchema.COMPANY_TABLE} c
            ON j.{JobFields.COMPANY_ID} = c.{CompanyFields.ID}
        WHERE j.{JobFields.TITLE} = %s
        ORDER BY j.{JobFields.ID} DESC
        LIMIT 1
        """,
        params=(project_name,),
        fetch_results=True
    )

    if rows:
        return {
            CompanyFields.ID: rows[0][CompanyFields.ID],
            CompanyFields.NAME: rows[0][CompanyFields.NAME],
            CompanyFields.ADDRESS: rows[0][CompanyFields.ADDRESS],
            CompanyFields.PHONE: rows[0][CompanyFields.PHONE]
        }

    # If not found in design_job, try inspection_job
    rows = execute_query(
        f"""
        SELECT
            c.{CompanyFields.ID},
            c.{CompanyFields.NAME},
            c.{CompanyFields.ADDRESS},
            c.{CompanyFields.PHONE}
        FROM {DatabaseSchema.INSPECTION_JOB_TABLE} j
        INNER JOIN {DatabaseSchema.COMPANY_TABLE} c
            ON j.{JobFields.COMPANY_ID} = c.{CompanyFields.ID}
        WHERE j.{JobFields.TITLE} = %s
        ORDER BY j.{JobFields.ID} DESC
        LIMIT 1
        """,
        params=(project_name,),
        fetch_results=True
    )

    if rows:
        return {
            CompanyFields.ID: rows[0][CompanyFields.ID],
            CompanyFields.NAME: rows[0][CompanyFields.NAME],
            CompanyFields.ADDRESS: rows[0][CompanyFields.ADDRESS],
            CompanyFields.PHONE: rows[0][CompanyFields.PHONE]
        }

    return None
