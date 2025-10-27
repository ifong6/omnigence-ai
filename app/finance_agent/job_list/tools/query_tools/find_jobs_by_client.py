from app.postgres.db_connection import execute_query

query = """
    WITH companies AS (
    SELECT c.id FROM "Finance".company c
    WHERE c.name ILIKE ('%' || $1 || '%')
        OR similarity(c.name, $1) >= COALESCE($2, show_limit())
    UNION
    SELECT ca.company_id
    FROM "Finance".company_alias ca
    WHERE ca.alias ILIKE ('%' || $1 || '%')
        OR similarity(ca.alias, $1) >= COALESCE($2, show_limit())
    )
    SELECT j.id, j.job_no, j.title, j.status, j.type, j.date_created, c.name AS company_name
    FROM "Finance".job j
    JOIN "Finance".company c ON c.id = j.company_id
    WHERE j.company_id IN (SELECT id FROM companies)
    ORDER BY j.date_created DESC, j.id DESC;
"""

def find_jobs_by_client_tool(client_name: str):
    """
    Find jobs by client name.
    
    args:
        client_name: str
        
    returns:
        list[dict]: The jobs
    """
    rows = execute_query(
        query = query, 
        params = (
            client_name, 
            0.25
        ),
        fetch_results=True, 
    )
    
    return rows