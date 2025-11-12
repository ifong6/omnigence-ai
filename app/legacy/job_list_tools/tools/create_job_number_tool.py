"""
Tool for generating job numbers for multiple jobs in batch.

Refactored to use centralized JobService with SQLModel ORM.
"""

from datetime import datetime
import json
from typing import List, Dict, Any
from sqlmodel import Session

from app.db.engine import engine
from app.services.job_service import JobService

# ---- helpers ---------------------------------------------------------------

def _current_year_2() -> str:
    """Get current year as 2-digit string (e.g., '25' for 2025)."""
    return datetime.now().strftime("%y")

def _normalize_job_type(job_type: str) -> str:
    """
    Normalize job type to DESIGN or INSPECTION.

    Args:
        job_type: Type of job (case-insensitive)

    Returns:
        "DESIGN" for design jobs, "INSPECTION" for inspection jobs
    """
    jt = (job_type or "").strip().upper()
    return "DESIGN" if jt == "DESIGN" else "INSPECTION"

def _ensure_list(input_val: Any) -> List[Dict[str, Any]]:
    """
    Convert input to list of dictionaries, handling JSON strings.

    Args:
        input_val: Either a JSON string or a list of dicts

    Returns:
        List of dictionaries

    Raises:
        ValueError: If input cannot be converted to expected format
    """
    # Accept JSON string or list[dict]
    if isinstance(input_val, str):
        s = input_val.strip().strip('"').strip("'")
        return json.loads(s)
    if isinstance(input_val, list):
        return input_val
    raise ValueError(f"Invalid input type: {type(input_val)}; expected list or JSON list")

# ---- main tool -------------------------------------------------------------

def create_job_number_tool(list_of_jobs) -> List[str]:
    """
    Generate job numbers for new projects using JobService with independent counters per job type.

    This tool generates job numbers WITHOUT creating actual job records in the database.
    It's useful when agents need to preview job numbers before full job creation.

    Input: [{'job_type': 'DESIGN'|'INSPECTION', 'job_title': '...'}, ...]
    Output: ['JCP-25-01-1', 'JICP-25-03-1', ...]

    Rules:
      - DESIGN uses Finance.design_job only; INSPECTION uses Finance.inspection_job only
      - Counter is per table and per year (YY)
      - The last '-X' is a per-call, per-type running index starting at 1

    Args:
        list_of_jobs: List of job dictionaries or JSON string representation
                     Each dict must have 'job_type' key

    Returns:
        List of generated job numbers (e.g., ["JCP-25-01-1", "JICP-25-03-1"])
        On error, returns list with error message

    Example:
        >>> create_job_number_tool([
        ...     {"job_type": "DESIGN", "job_title": "Building Design"},
        ...     {"job_type": "INSPECTION", "job_title": "Safety Check"}
        ... ])
        ['JCP-25-01-1', 'JICP-25-01-1']
    """
    print(f"[DEBUG][create_job_number_tool] Received input type: {type(list_of_jobs)}")
    print(f"[DEBUG][create_job_number_tool] Received input: {list_of_jobs}")

    try:
        jobs = _ensure_list(list_of_jobs)
        print(f"[DEBUG][create_job_number_tool] Parsed jobs: {jobs}")
    except Exception as e:
        error_msg = f"Error: {e}"
        print(f"[ERROR][create_job_number_tool] {error_msg}")
        return [error_msg]

    # Validate shape
    for i, j in enumerate(jobs):
        if not isinstance(j, dict) or "job_type" not in j:
            error_msg = f"Error: item {i} must be a dict with 'job_type'"
            print(f"[ERROR][create_job_number_tool] {error_msg}")
            return [error_msg]

    # Use JobService to get current sequences and generate job numbers
    with Session(engine) as session:
        job_service = JobService(session)

        # Pre-scan: find which types we have
        types_present = {"DESIGN": False, "INSPECTION": False}
        for j in jobs:
            jt = _normalize_job_type(j.get("job_type", ""))
            types_present[jt] = True

        # Load current counters per type using _parse_seq helper
        seq_by_type = {}
        if types_present["DESIGN"]:
            from sqlmodel import select, desc
            from app.models.job_models import DesignJob
            from app.services.job_service import _parse_seq
            stmt = select(DesignJob.job_no).order_by(desc(DesignJob.id)).limit(1)
            last_job_no = session.exec(stmt).first()
            seq_by_type["DESIGN"] = _parse_seq(last_job_no)
            print(f"[DEBUG][create_job_number_tool] Latest DESIGN seq: {seq_by_type['DESIGN']}")

        if types_present["INSPECTION"]:
            from sqlmodel import select, desc
            from app.models.job_models import InspectionJob
            from app.services.job_service import _parse_seq
            stmt = select(InspectionJob.job_no).order_by(desc(InspectionJob.id)).limit(1)
            last_job_no = session.exec(stmt).first()
            seq_by_type["INSPECTION"] = _parse_seq(last_job_no)
            print(f"[DEBUG][create_job_number_tool] Latest INSPECTION seq: {seq_by_type['INSPECTION']}")

        # Per-call, per-type suffix index: start at 1 and increment within this batch
        suffix_idx_by_type = {"DESIGN": 0, "INSPECTION": 0}

        yy = _current_year_2()
        out: List[str] = []

        for j in jobs:
            jt = _normalize_job_type(j.get("job_type", ""))
            prefix = "JCP" if jt == "DESIGN" else "JICP"

            # bump table/year sequence
            seq_by_type[jt] = seq_by_type.get(jt, 0) + 1
            no_str = f"{seq_by_type[jt]:02d}"

            # bump within-batch suffix per type
            suffix_idx_by_type[jt] = suffix_idx_by_type.get(jt, 0) + 1
            x = suffix_idx_by_type[jt]

            job_number = f"{prefix}-{yy}-{no_str}-{x}"
            print(f"[DEBUG][create_job_number_tool] Generated: {job_number} for {jt}")
            out.append(job_number)

        print(f"[DEBUG][create_job_number_tool] Final output: {out}")
        return out
