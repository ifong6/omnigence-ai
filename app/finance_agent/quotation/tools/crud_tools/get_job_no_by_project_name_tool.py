"""
Tool for retrieving job numbers by project name.

This module provides a simple lookup function to get job number by project title.
"""

from typing import Optional
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    JobFields
)
from database.db_helper import find_one_by_field
from database.supabase.db_connection import execute_query

def get_job_no_by_project_name_tool(project_name: str) -> Optional[str]:
    """
    Fetch the job_no of a given project name from design_job or inspection_job tables.

    IMPORTANT: Jobs are now stored in separate tables:
    - Finance.design_job for DESIGN jobs
    - Finance.inspection_job for INSPECTION jobs

    This tool searches for jobs by their title (project name) and returns the
    most recent job number. Since a company only does one type of job, this
    function tries design_job first, then inspection_job.

    Args:
        project_name: The project title/name to search for (exact match)
            Examples: "ABC建築工程", "結構安全檢測"

    Returns:
        Optional[str]: The job number if found (e.g., "JCP-25-01-1"),
                       None if no matching project found

    Examples:
        >>> # Find job number for existing project
        >>> job_no = get_job_no_by_project_name_tool("結構安全檢測")
        >>> # Returns: "JCP-25-01-1" or "JICP-25-01-1"

        >>> # Project not found
        >>> job_no = get_job_no_by_project_name_tool("Non-existent Project")
        >>> # Returns: None

    Workflow:
        1. Try design_job table first
        2. If not found, try inspection_job table
        3. Return job_no if found, None otherwise

    Notes:
        - Uses exact match on project title (case-sensitive)
        - Returns the most recent job if multiple jobs have the same title
        - Returns None (not an error) if project doesn't exist
    """

    # Try design_job first
    rows = execute_query(
        f"""
        SELECT {JobFields.JOB_NO}
        FROM {DatabaseSchema.DESIGN_JOB_TABLE}
        WHERE {JobFields.TITLE} = %s
        ORDER BY {JobFields.ID} DESC
        LIMIT 1
        """,
        params=(project_name,),
        fetch_results=True
    )

    if rows:
        return rows[0][JobFields.JOB_NO]

    # If not found in design_job, try inspection_job
    rows = execute_query(
        f"""
        SELECT {JobFields.JOB_NO}
        FROM {DatabaseSchema.INSPECTION_JOB_TABLE}
        WHERE {JobFields.TITLE} = %s
        ORDER BY {JobFields.ID} DESC
        LIMIT 1
        """,
        params=(project_name,),
        fetch_results=True
    )

    return rows[0][JobFields.JOB_NO] if rows else None
