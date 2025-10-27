"""
Tool for updating existing jobs in the Finance database.

This module provides functionality to update job records with improved:
- Input validation
- Error handling
- Code organization
- Type safety
"""

from typing import Any, Dict, Optional
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    JobType,
    JobStatus,
    QuotationStatus,
    DatabaseSchema,
    JobFields,
    ErrorMessages,
    SuccessMessages
)
from app.finance_agent.utils.db_helper import update_record, DatabaseError


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
            updates[JobFields.TYPE] = JobType.normalize(params['job_type'])
        except ValueError as e:
            raise ValueError(str(e))

    # Handle new title (rename field for clarity)
    if 'new_title' in params:
        updates[JobFields.TITLE] = params['new_title']

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
    title: str
) -> tuple[str, tuple]:
    """
    Build SQL UPDATE query with proper handling of CURRENT_TIMESTAMP.

    Args:
        updates: Validated field updates
        title: Job title to identify record

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
        UPDATE {DatabaseSchema.JOB_TABLE}
        SET {', '.join(set_clauses)}
        WHERE {JobFields.TITLE} = %s
        RETURNING {JobFields.ID}, {JobFields.COMPANY_ID}, {JobFields.TYPE},
                  {JobFields.TITLE}, {JobFields.STATUS}, {JobFields.JOB_NO},
                  {JobFields.DATE_CREATED}, {JobFields.QUOTATION_STATUS},
                  {JobFields.QUOTATION_ISSUED_AT}
    """

    return query, tuple(params)


def _format_success_message(job: Dict[str, Any]) -> str:
    """
    Format success message with updated job details.

    Args:
        job: Updated job record from database

    Returns:
        Formatted success message string
    """
    return (
        f"Successfully updated job: "
        f"ID={job[JobFields.ID]}, "
        f"Company ID={job[JobFields.COMPANY_ID]}, "
        f"Type={job[JobFields.TYPE]}, "
        f"Title={job[JobFields.TITLE]}, "
        f"Status={job[JobFields.STATUS]}, "
        f"Job No={job[JobFields.JOB_NO]}, "
        f"Created={job[JobFields.DATE_CREATED]}, "
        f"Quotation Status={job.get(JobFields.QUOTATION_STATUS)}, "
        f"Quotation Issued At={job.get(JobFields.QUOTATION_ISSUED_AT)}"
    )


# ============================================================================
# Main Tool Function
# ============================================================================

def update_job_tool(tool_input: Any) -> str:
    """
    Update an existing job's fields by job title.

    This tool provides flexible updates for job records, allowing updates to:
    - Company assignment
    - Job type (normalized to "Inspection" or "Design")
    - Job title
    - Job number
    - Status
    - Quotation status
    - Quotation issued timestamp (supports 'current'/'now' for CURRENT_TIMESTAMP)

    Args:
        tool_input: Can be either:
            - JSON string: '{"title": "Project Name", "status": "Completed"}'
            - Dictionary: {"title": "Project Name", "quotation_status": "ISSUED"}

    Required Parameter:
        - title: Job title to identify which job to update

    Optional Parameters:
        - company_id: New company ID
        - job_type: New job type ('inspection' or 'design')
        - new_title: New title for the job
        - job_no: New job number
        - status: New status
        - quotation_status: New quotation status (e.g., 'ISSUED', 'CREATED')
        - quotation_issued_at: New timestamp or 'current'/'now' for current time

    Returns:
        Success message with updated job details, or error message

    Examples:
        >>> # Update quotation status
        >>> update_job_tool({"title": "ABC Project", "quotation_status": "ISSUED"})

        >>> # Update multiple fields
        >>> update_job_tool({
        ...     "title": "ABC Project",
        ...     "status": "Completed",
        ...     "quotation_issued_at": "current"
        ... })

    Error Handling:
        - Returns descriptive error messages for:
          - Missing title parameter
          - Invalid JSON input
          - No fields to update
          - Job not found
          - Database errors
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['title'],
            tool_name="update_job_tool"
        )

        title = params['title']

        # Validate and normalize update fields
        try:
            updates = _validate_and_normalize_updates(params)
        except ValueError as e:
            return f"Error: {str(e)}"

        # Check if there are any fields to update
        if not updates:
            return ErrorMessages.NO_ITEMS_TO_UPDATE

        # Build and execute update query
        query, query_params = _build_update_query(updates, title)

        from app.postgres.db_connection import execute_query
        rows = execute_query(
            query=query,
            params=query_params,
            fetch_results=True
        )

        # Handle results
        if rows:
            return _format_success_message(rows[0])
        else:
            return ErrorMessages.RECORD_NOT_FOUND.format(
                tool="update_job_tool",
                entity="job",
                field="title",
                value=title
            )

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error updating job: {str(e)}"
        print(f"[ERROR][update_job_tool] {error_msg}")
        return error_msg
