from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum

def find_inspection_jobs_by_client_tool(client_name: str):
    """
    Find INSPECTION jobs by client name.

    Jobs are searched from Finance.inspection_job table only.

    args:
        client_name: str - The client/company name to search for

    returns:
        list[dict]: The INSPECTION jobs found for this client
    """
    query = f"""
        WITH companies AS (
            SELECT c.id FROM {DBTable_Enum.COMPANY_TABLE} c
            WHERE c.name ILIKE ('%' || $1 || '%')
                OR c.alias ILIKE ('%' || $1 || '%')
                OR similarity(c.name, $1) >= COALESCE($2, show_limit())
                OR similarity(c.alias, $1) >= COALESCE($2, show_limit())
        )
        SELECT j.id, j.job_no, j.title, j.status, 'INSPECTION' AS type, j.date_created, c.name AS company_name
        FROM {DBTable_Enum.INSPECTION_JOB_TABLE} j
        JOIN {DBTable_Enum.COMPANY_TABLE} c ON c.id = j.company_id
        WHERE j.company_id IN (SELECT id FROM companies)
        ORDER BY j.date_created DESC, j.id DESC;
    """

    rows = execute_query(
        query=query,
        params=(client_name, 0.25),
        fetch=True,
    )

    return rows
