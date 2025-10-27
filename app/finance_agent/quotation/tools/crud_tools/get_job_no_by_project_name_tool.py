"""
Tool for retrieving job numbers by project name.

This module provides a simple lookup function to get job number by project title.
"""

from typing import Optional
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    JobFields
)
from app.finance_agent.utils.db_helper import find_one_by_field


def get_job_no_by_project_name_tool(project_name: str) -> Optional[str]:
    """
    Fetch the job_no of a given project name from the Finance.job table.

    This tool searches for jobs by their title (project name) and returns the
    most recent job number. This is commonly used when creating quotations, as
    quotation numbers are derived from job numbers.

    Args:
        project_name: The project title/name to search for (exact match)
            Examples: "ABC建築工程", "結構安全檢測"

    Returns:
        Optional[str]: The job number if found (e.g., "JCP-25-01-1"),
                       None if no matching project found

    Examples:
        >>> # Find job number for existing project
        >>> job_no = get_job_no_by_project_name_tool("結構安全檢測")
        >>> # Returns: "JCP-25-01-1"

        >>> # Project not found
        >>> job_no = get_job_no_by_project_name_tool("Non-existent Project")
        >>> # Returns: None

    Workflow:
        1. Query job table by title (exact match)
        2. Order by ID descending to get most recent
        3. Return job_no if found, None otherwise

    Usage Pattern:
        This tool is typically used as the first step in quotation creation:
        1. Get job number by project name
        2. Use job number to generate quotation number
        3. Get client info by project name
        4. Create quotation

        Example agent workflow:
        ```
        job_no = get_job_no_by_project_name_tool("My Project")
        if not job_no:
            return "Error: Project not found"

        quo_result = create_quotation_no_tool(job_no)
        quotation_no = quo_result["quotation_no"]
        ```

    Notes:
        - Uses exact match on project title (case-sensitive)
        - Returns the most recent job if multiple jobs have the same title
        - Returns None (not an error) if project doesn't exist
    """
    from app.postgres.db_connection import execute_query

    # Note: Using execute_query directly here instead of find_one_by_field
    # because we need ORDER BY id DESC to get the most recent job
    rows = execute_query(
        f"""
        SELECT {JobFields.JOB_NO}
        FROM {DatabaseSchema.JOB_TABLE}
        WHERE {JobFields.TITLE} = %s
        ORDER BY {JobFields.ID} DESC
        LIMIT 1
        """,
        params=(project_name,),
        fetch_results=True
    )

    return rows[0][JobFields.JOB_NO] if rows else None
