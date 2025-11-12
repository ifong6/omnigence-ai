"""
Tool for retrieving all DESIGN jobs from the Finance database.
"""
from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum


def get_all_design_jobs_tool() -> str:
    """
    Get all DESIGN jobs from the database, ordered by creation date (newest first).

    Args:
        limit: Optional limit on number of jobs to return. If None, returns all jobs.

    Returns:
        Formatted string with all DESIGN job records or error message
    """
    try:
        query = f"""
            SELECT
                j.id,
                j.company_id,
                c.name as company_name,
                j.title,
                j.job_no,
                j.status,
                j.quotation_status,
                j.quotation_issued_at,
                j.date_created
            FROM {DBTable_Enum.DESIGN_JOB_TABLE} j
            LEFT JOIN {DBTable_Enum.COMPANY_TABLE} c ON j.company_id = c.id
            ORDER BY j.date_created DESC
        """

        rows = execute_query(query, fetch=True)

        if not rows:
            return "No DESIGN jobs found in the database."

        # Format results
        result = f"Total DESIGN jobs found: {len(rows)}\n\n"
        result += "=" * 100 + "\n"

        for idx, job in enumerate(rows, 1):
            result += f"\nDESIGN Job #{idx}:\n"
            result += f"  ID: {job['id']}\n"
            result += f"  Job No: {job['job_no']}\n"
            result += f"  Company: {job['company_name']} (ID: {job['company_id']})\n"
            result += f"  Title: {job['title']}\n"
            result += f"  Status: {job['status']}\n"
            result += f"  Quotation Status: {job['quotation_status']}\n"
            result += f"  Quotation Issued At: {job['quotation_issued_at'] or 'N/A'}\n"
            result += f"  Created: {job['date_created']}\n"
            result += "-" * 100 + "\n"

        return result

    except Exception as e:
        error_msg = f"Error retrieving DESIGN jobs: {str(e)}"
        print(f"[ERROR][get_all_design_jobs_tool] {error_msg}")
        return error_msg
