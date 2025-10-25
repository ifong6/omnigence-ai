"""
Tool for creating new jobs in the Finance database.

This module provides functionality to create job records with improved:
- Input validation and parsing
- Error handling
- Code organization
- Type safety
"""

from typing import Any, Dict, Optional
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    JobType,
    JobStatus,
    DatabaseSchema,
    JobFields,
    ErrorMessages,
    SuccessMessages
)
from app.finance_agent.utils.db_helper import insert_record, DatabaseError


# ============================================================================
# Business Logic Functions
# ============================================================================

def _validate_and_normalize_job_data(
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate and normalize job creation parameters.

    Args:
        params: Raw job parameters from tool input

    Returns:
        Dict of validated and normalized job fields

    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    company_id = params.get('company_id')
    if not company_id:
        raise ValueError("company_id is required")

    job_type = params.get('job_type')
    if not job_type:
        raise ValueError("job_type is required")

    job_title = params.get('job_title')
    if not job_title:
        raise ValueError("job_title is required")

    # Normalize job type
    try:
        normalized_job_type = JobType.normalize(job_type)
    except ValueError as e:
        raise ValueError(str(e))

    # Build validated fields dict
    job_data = {
        JobFields.COMPANY_ID: company_id,
        JobFields.TYPE: normalized_job_type,
        JobFields.TITLE: job_title,
        JobFields.STATUS: params.get('status', JobStatus.NEW.value),
        JobFields.JOB_NO: params.get('job_no')
    }

    return job_data


def _format_job_success_message(job: Dict[str, Any]) -> str:
    """
    Format success message with created job details.

    Args:
        job: Created job record from database

    Returns:
        Formatted success message string
    """
    return (
        f"Successfully created job: "
        f"ID={job[JobFields.ID]}, "
        f"Company ID={job[JobFields.COMPANY_ID]}, "
        f"Type={job[JobFields.TYPE]}, "
        f"Title={job[JobFields.TITLE]}, "
        f"Status={job[JobFields.STATUS]}, "
        f"Job No={job[JobFields.JOB_NO]}, "
        f"Created={job[JobFields.DATE_CREATED]}"
    )


# ============================================================================
# Main Tool Function
# ============================================================================

def create_job_tool(tool_input: Any) -> str:
    """
    Create a new job in the database for a specific company.

    Important: You MUST first get the company_id using get_company_id_tool.
    If company doesn't exist, create it first using create_company_tool.

    This tool creates a new job record with the following fields:
    - Company assignment (via company_id)
    - Job type (normalized to "Inspection" or "Design")
    - Job title
    - Job number (optional)
    - Status (defaults to "New")

    Args:
        tool_input: Can be either:
            - JSON string: '{"company_id": 17, "job_type": "inspection", ...}'
            - Dictionary: {"company_id": 17, "job_type": "design", ...}

    Required Parameters:
        - company_id: ID of the company (must exist in company table)
        - job_type: Type of job ('inspection' or 'design')
        - job_title: Title/name of the job

    Optional Parameters:
        - job_no: Job number (can be assigned later)
        - status: Job status (defaults to "New")

    Returns:
        Success message with created job details, or error message

    Examples:
        >>> # Create inspection job
        >>> create_job_tool({
        ...     "company_id": 17,
        ...     "job_type": "inspection",
        ...     "job_title": "Building Safety Inspection"
        ... })

        >>> # Create design job with job number
        >>> create_job_tool({
        ...     "company_id": 17,
        ...     "job_type": "design",
        ...     "job_title": "Structural Design Project",
        ...     "job_no": "JCP-2025-001",
        ...     "status": "In Progress"
        ... })

    Error Handling:
        - Returns descriptive error messages for:
          - Missing required parameters
          - Invalid JSON input
          - Invalid job type
          - Database errors (e.g., foreign key constraint if company_id doesn't exist)
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['company_id', 'job_type', 'job_title'],
            tool_name="create_job_tool"
        )

        # Validate and normalize job data
        try:
            job_data = _validate_and_normalize_job_data(params)
        except ValueError as e:
            return f"Error: {str(e)}"

        # Insert job record
        job = insert_record(
            table=DatabaseSchema.JOB_TABLE,
            fields=job_data,
            returning=f"{JobFields.ID}, {JobFields.COMPANY_ID}, {JobFields.TYPE}, "
                     f"{JobFields.TITLE}, {JobFields.STATUS}, {JobFields.JOB_NO}, "
                     f"{JobFields.DATE_CREATED}",
            operation_name="create job"
        )

        if job:
            return _format_job_success_message(job)
        else:
            return ErrorMessages.DB_QUERY_FAILED.format(
                tool="create_job_tool",
                error="No data returned from insert"
            )

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error creating job: {str(e)}"
        print(f"[ERROR][create_job_tool] {error_msg}")
        return error_msg
