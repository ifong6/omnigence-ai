from datetime import datetime
import json
from typing import List, Dict, Any
from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum

# ---- helpers ---------------------------------------------------------------

def _current_year_2() -> str:
    """Get current year as 2-digit string (e.g., '25' for 2025)."""
    return datetime.now().strftime("%y")

def _prefix_for(job_type: str) -> str:
    """
    Determine the job number prefix based on job type.

    Args:
        job_type: Type of job (case-insensitive)

    Returns:
        "JCP" for design jobs, "JICP" for inspection jobs
    """
    # job_type can be any case; only two values are used to choose the table/prefix
    jt = (job_type or "").strip().upper()
    return "JCP" if jt == "DESIGN" else "JICP"   # default to JICP only if explicitly not DESIGN

def _table_for_prefix(prefix: str) -> str:
    """
    Get the database table name for a given prefix.

    Args:
        prefix: Job number prefix ("JCP" or "JICP")

    Returns:
        Table name string
    """
    return DBTable_Enum.DESIGN_JOB_TABLE if prefix == "JCP" \
           else DBTable_Enum.INSPECTION_JOB_TABLE

def _latest_seq_for_year(prefix: str, yy: str) -> int:
    """
    Read the latest job_no for this prefix and year, from its OWN table.
    If none found for this year, return 0 (so next becomes 01).

    Args:
        prefix: Job number prefix ("JCP" or "JICP")
        yy: Two-digit year string (e.g., "25")

    Returns:
        Latest sequential number for this prefix/year, or 0 if none found
    """
    table = _table_for_prefix(prefix)
    # Fast filter by prefix and year, and order by the numeric middle part (NO) desc
    rows = execute_query(
        query=f"""
            SELECT job_no
            FROM {table}
            WHERE job_no LIKE %s
            ORDER BY date_created DESC, id DESC
            LIMIT 1;
        """,
        params=(f"{prefix}-{yy}-%",),
        fetch=True,
    )
    if not rows:
        return 0

    job_no = rows[0]["job_no"] or ""
    # Expected: PREFIX-YY-NO-X
    parts = job_no.split("-")
    if len(parts) >= 4 and parts[1] == yy:
        try:
            return int(parts[2])
        except ValueError:
            return 0
    return 0

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
    Generate job numbers for new projects with independent counters per job type.

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

    yy = _current_year_2()

    # Pre-scan: find which types we have and fetch their latest seq once
    types_present = {"DESIGN": False, "INSPECTION": False}
    for j in jobs:
        jt = (j.get("job_type") or "").strip().upper()
        if jt == "DESIGN":
            types_present["DESIGN"] = True
        else:
            types_present["INSPECTION"] = True  # treat everything else as INSPECTION for prefix/table

    # Load current counters per type (based on their own table)
    seq_by_type = {}
    if types_present["DESIGN"]:
        seq_by_type["DESIGN"] = _latest_seq_for_year("JCP", yy)
        print(f"[DEBUG][create_job_number_tool] Latest DESIGN seq for {yy}: {seq_by_type['DESIGN']}")
    if types_present["INSPECTION"]:
        seq_by_type["INSPECTION"] = _latest_seq_for_year("JICP", yy)
        print(f"[DEBUG][create_job_number_tool] Latest INSPECTION seq for {yy}: {seq_by_type['INSPECTION']}")

    # Per-call, per-type suffix index: start at 1 and increment within this batch
    suffix_idx_by_type = {"DESIGN": 0, "INSPECTION": 0}

    out: List[str] = []
    for j in jobs:
        jt = (j.get("job_type") or "").strip().upper()
        jt = "DESIGN" if jt == "DESIGN" else "INSPECTION"

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
