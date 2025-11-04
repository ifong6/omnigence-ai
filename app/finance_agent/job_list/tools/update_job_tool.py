from typing import Any, Dict, Optional
from app.finance_agent.utils.constants import JobFields
from database.supabase.db_enum import DBTable_Enum
from database.supabase.db_connection import execute_query

# ============================================================================
# Main Tool Function
# ============================================================================

def update_job_tool(tool_input: Any) -> str:
    """
    Update job fields by title. Use 'current' or 'now' for quotation_issued_at to set current timestamp.

    IMPORTANT: Jobs are stored in separate tables:
    - DESIGN jobs -> Finance.design_job table
    - INSPECTION jobs -> Finance.inspection_job table

    This tool will automatically find the correct table based on the job title.

    Args:
        tool_input: {"title": str (required), "job_type": str, "new_title": str, "status": str, "quotation_status": str, ...}

    Returns:
        Success message with updated job details or error message
    """
    title = tool_input['title']
    job_type = tool_input['job_type']
    new_title = tool_input['new_title']
    status = tool_input['status']
    quotation_status = tool_input['quotation_status']
    quotation_issued_at = tool_input['quotation_issued_at']
    date_created = tool_input['date_created']
    job_no = tool_input['job_no']
    company_id = tool_input['company_id']
    id = tool_input['id']

    return _format_success_message(job_type, id, company_id, title, status, job_no, date_created, quotation_status, quotation_issued_at)

# ============================================================================
# Business Logic Functions
# ============================================================================

def _validate_and_normalize_updates(
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate and normalize update parameters.

    Args:
        params: Raw update parameters from tool input

    Returns:
        Dict of validated and normalized field updates

    Raises:
        ValueError: If validation fails
    """
    updates = {}

    # Normalize job type if provided
    if 'job_type' in params:
        try:
            updates["type"] = params['job_type']
        except ValueError as e:
            raise ValueError(str(e))

    # Handle new title (rename field for clarity)
    if 'new_title' in params:
        updates["title"] = params['new_title']

    # Direct field mappings
    field_mappings = {
        'company_id': JobFields.COMPANY_ID,
        'job_no': JobFields.JOB_NO,
        'status': JobFields.STATUS,
        'quotation_status': JobFields.QUOTATION_STATUS,
    }

    for param_name, field_name in field_mappings.items():
        if param_name in params:
            updates[field_name] = params[param_name]

    # Handle quotation_issued_at with special logic for 'current'/'now'
    if 'quotation_issued_at' in params:
        value = params['quotation_issued_at']
        if value in ['current', 'now']:
            # This will be handled specially in the SQL
            updates[JobFields.QUOTATION_ISSUED_AT] = 'CURRENT_TIMESTAMP'
        else:
            updates[JobFields.QUOTATION_ISSUED_AT] = value

    return updates


def _build_update_query(
    updates: Dict[str, Any],
    title: str,
    table: str
) -> tuple[str, tuple]:
    """
    Build SQL UPDATE query with proper handling of CURRENT_TIMESTAMP.

    Args:
        updates: Validated field updates
        title: Job title to identify record
        table: Table name (design_job or inspection_job)

    Returns:
        Tuple of (query_string, parameters_tuple)
    """
    set_clauses = []
    params = []

    for field, value in updates.items():
        if value == 'CURRENT_TIMESTAMP':
            # Special handling for CURRENT_TIMESTAMP - don't parameterize
            set_clauses.append(f"{field} = CURRENT_TIMESTAMP")
        else:
            set_clauses.append(f"{field} = %s")
            params.append(value)

    # Add title parameter for WHERE clause
    params.append(title)

    query = f"""
        UPDATE {table}
        SET {', '.join(set_clauses)}
        WHERE {JobFields.TITLE} = %s
        RETURNING {JobFields.ID}, {JobFields.COMPANY_ID},
                  {JobFields.TITLE}, {JobFields.STATUS}, {JobFields.JOB_NO},
                  {JobFields.DATE_CREATED}, {JobFields.QUOTATION_STATUS},
                  {JobFields.QUOTATION_ISSUED_AT}
    """

    return query, tuple(params)


def _find_job_table(title: str) -> Optional[tuple[str, str]]:
    """
    Find which table (design_job or inspection_job) contains the job with given title.

    Args:
        title: Job title to search for

    Returns:
        Tuple of (table_name, job_type) if found, None otherwise
    """


    # Try design_job first
    design_query = f"""
        SELECT 1 FROM {DBTable_Enum.DESIGN_JOB_TABLE}
        WHERE {JobFields.TITLE} = %s
        LIMIT 1
    """
    design_result = execute_query(design_query, params=(title,), fetch=True)
    if design_result:
        return (DBTable_Enum.DESIGN_JOB_TABLE, 'DESIGN')

    # Try inspection_job
    inspection_query = f"""
        SELECT 1 FROM {DBTable_Enum.INSPECTION_JOB_TABLE}
        WHERE {JobFields.TITLE} = %s
        LIMIT 1
    """
    inspection_result = execute_query(inspection_query, params=(title,), fetch=True)
    if inspection_result:
        return (DBTable_Enum.INSPECTION_JOB_TABLE, 'INSPECTION')

    return None


def _format_success_message(job_type: str, id: int, company_id: int, title: str, status: str, job_no: str, date_created: str, quotation_status: str, quotation_issued_at: str) -> str:
    return (
        f"Successfully updated {job_type} job: "
        f"ID={id}, "
        f"Company ID={company_id}, "
        f"Title={title}, "
        f"Status={status}, "
        f"Job No={job_no}, "
        f"Created={date_created}, "
        f"Quotation Status={quotation_status}, "
        f"Quotation Issued At={quotation_issued_at}"
    )

