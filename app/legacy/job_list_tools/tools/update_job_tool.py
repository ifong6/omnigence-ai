"""
Tool for updating job records.

Refactored to use centralized JobService with SQLModel ORM.
"""

from typing import Any, Dict, Optional
from datetime import datetime
from sqlmodel import Session

from app.db.engine import engine
from app.services.job_service import JobService
from app.finance_agent.utils.tool_input_parser import parse_tool_input, ToolInputError

# ============================================================================
# Main Tool Function
# ============================================================================

def update_job_tool(tool_input: Any) -> str:
    """
    Update job fields using JobService. Use 'current' or 'now' for quotation_issued_at to set current timestamp.

    IMPORTANT: Jobs are stored in separate tables:
    - DESIGN jobs -> Finance.design_job table
    - INSPECTION jobs -> Finance.inspection_job table

    Args:
        tool_input: {
            "job_id": int (required),
            "job_type": str (required, "DESIGN" or "INSPECTION"),
            "title": str (optional, new title),
            "status": str (optional),
            "quotation_status": str (optional),
            "quotation_issued_at": str (optional, use "current" or "now" for current timestamp)
        }

    Returns:
        Success message with updated job details or error message

    Example:
        >>> update_job_tool({
        ...     "job_id": 15,
        ...     "job_type": "DESIGN",
        ...     "status": "IN_PROGRESS",
        ...     "quotation_status": "ISSUED",
        ...     "quotation_issued_at": "current"
        ... })
        "Successfully updated DESIGN job: ID=15, Title=..., Status=IN_PROGRESS, ..."
    """
    try:
        # Parse and validate input
        params = parse_tool_input(
            tool_input,
            required_keys=['job_id', 'job_type'],
            tool_name="update_job_tool"
        )

        job_id = params.get('job_id')
        job_type = params.get('job_type', '').strip().upper()

        # Validate job_type
        if job_type not in ['DESIGN', 'INSPECTION']:
            return f"Error: job_type must be 'DESIGN' or 'INSPECTION', got '{job_type}'"

        # Prepare update kwargs
        update_kwargs = {}

        if 'title' in params:
            update_kwargs['title'] = params['title']

        if 'status' in params:
            update_kwargs['status'] = params['status']

        if 'quotation_status' in params:
            update_kwargs['quotation_status'] = params['quotation_status']

        # Handle quotation_issued_at with special 'current'/'now' logic
        if 'quotation_issued_at' in params:
            value = params['quotation_issued_at']
            if value in ['current', 'now']:
                update_kwargs['quotation_issued_at'] = datetime.now()
            else:
                update_kwargs['quotation_issued_at'] = value

        # Use JobService to update
        with Session(engine) as session:
            job_service = JobService(session)

            job = job_service.update(
                job_id=job_id,
                job_type=job_type,
                **update_kwargs
            )

            if not job:
                return f"Error: {job_type} job with ID {job_id} not found"

            session.commit()

            return _format_success_message(job_type, job)

    except ToolInputError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error updating job: {str(e)}"
        print(f"[ERROR][update_job_tool] {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg

# ============================================================================
# Formatting Functions
# ============================================================================

def _format_success_message(job_type: str, job) -> str:
    """
    Format success message with updated job details.

    Args:
        job_type: Job type (DESIGN or INSPECTION)
        job: Updated job (DesignJob or InspectionJob ORM model)

    Returns:
        Formatted success message string
    """
    return (
        f"Successfully updated {job_type} job: "
        f"ID={job.id}, "
        f"Company ID={job.company_id}, "
        f"Title={job.title}, "
        f"Status={job.status}, "
        f"Job No={job.job_no}, "
        f"Created={job.date_created}, "
        f"Quotation Status={job.quotation_status}, "
        f"Quotation Issued At={job.quotation_issued_at}"
    )

