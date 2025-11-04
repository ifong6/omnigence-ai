"""
Tool for creating new jobs in the Finance database.

This module provides functionality to create job records with improved:
- Input validation and parsing
- Error handling
- Code organization
- Type safety
- Repository pattern for clean database access
"""

from typing import Any, Dict, Optional
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError
from app.finance_agent.utils.constants import (
    JobType,
    JobStatus,
    JobFields,
    ErrorMessages
)
from app.finance_agent.repository.design_job_repo import DesignJobRepo
from app.finance_agent.repository.inspection_job_repo import InspectionJobRepo
from app.finance_agent.models.job import JobCreate, JobRow


# ============================================================================
# Business Logic Functions
# ============================================================================

def _validate_and_normalize_job_data(
    params: Dict[str, Any]
) -> tuple[JobCreate, str]:
    """
    Validate and normalize job creation parameters.

    Args:
        params: Raw job parameters from tool input

    Returns:
        Tuple of (JobCreate TypedDict, job_type string)

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

    # Normalize job type to uppercase
    job_type_normalized = job_type.strip().upper()

    # Validate job type is either DESIGN or INSPECTION
    if job_type_normalized not in [JobType.DESIGN, JobType.INSPECTION]:
        raise ValueError(f"job_type must be 'DESIGN' or 'INSPECTION', got '{job_type}'")

    # Build JobCreate TypedDict
    # NOTE: status, quotation_status, quotation_issued_at have database defaults
    # NOTE: 'type' field not included - table name (design_job/inspection_job) indicates job type
    job_data: JobCreate = {
        'company_id': company_id,
        'title': job_title,
        'status': 'NEW'  # type: ignore - must match database enum exactly
    }

    # Add optional job_no if provided
    if params.get('job_no'):
        job_data['job_no'] = params.get('job_no')

    return job_data, job_type_normalized


def _format_job_success_message(job_row: JobRow, job_type: str):
    """
    Format success message with created job details.

    Args:
        job_row: Created job record from database
        job_type: Job type (DESIGN or INSPECTION)

    Returns:
        Formatted success message string
    """
    return (
        f"Successfully created {job_type} job: "
        f"ID={job_row['id']}, "
        f"Company ID={job_row['company_id']}, "
        f"Title={job_row['title']}, "
        f"Status={job_row['status']}, "
        f"Job No={job_row['job_no']}, "
        f"Created={job_row['date_created']}, "
        f"Quotation Status={job_row['quotation_status']}, "
        f"Quotation Issued At={job_row['quotation_issued_at']}"
)

# ============================================================================
# Main Tool Function
# ============================================================================

def create_job_tool(tool_input: Any) -> str:
    """
    Create a new job for a company. Get company_id first using get_company_id_tool.

    IMPORTANT: Jobs are stored in separate tables based on type:
    - DESIGN jobs -> Finance.design_job table (via DesignJobRepo)
    - INSPECTION jobs -> Finance.inspection_job table (via InspectionJobRepo)

    Args:
        tool_input: {"company_id": int, "job_type": str, "job_title": str, "job_no": str (optional)}
            - job_type: Must be "DESIGN" or "INSPECTION"
            - status: Set automatically by database to "New"

    Returns:
        Success message with job details or error message

    Examples:
        >>> create_job_tool({"company_id": 5, "job_type": "DESIGN", "job_title": "空調系統設計", "job_no": "JCP-25-01-1"})
        "Successfully created DESIGN job: ID=1, Company ID=5, Title=空調系統設計, Status=New, Job No=JCP-25-01-1, Created=2025-01-27"

        >>> create_job_tool({"company_id": 3, "job_type": "INSPECTION", "job_title": "消防安全檢查", "job_no": "JICP-25-01-1"})
        "Successfully created INSPECTION job: ID=2, Company ID=3, Title=消防安全檢查, Status=New, Job No=JICP-25-01-1, Created=2025-01-27"
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
            job_data, job_type = _validate_and_normalize_job_data(params)
        except ValueError as e:
            return f"Error: {str(e)}"

        # Use appropriate repository based on job type
        if job_type == JobType.DESIGN:
            repo = DesignJobRepo()
            design_job_row: JobRow = repo.create(job_data)
        elif job_type == JobType.INSPECTION:
            repo = InspectionJobRepo()
            inspection_job_row: JobRow = repo.create(job_data)
        else:
            return f"Error: Invalid job_type '{job_type}'. Must be 'DESIGN' or 'INSPECTION'"

        # Format and return success message
        return _format_job_success_message(design_job_row if job_type == JobType.DESIGN else inspection_job_row, job_type)

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error creating job: {str(e)}"
        print(f"[ERROR][create_job_tool] {error_msg}")
        return error_msg
