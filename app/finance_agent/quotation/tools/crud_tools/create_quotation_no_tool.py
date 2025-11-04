"""
Tool for generating quotation numbers with sequence and revision tracking.

This module provides functionality to generate unique quotation numbers
based on job numbers, with support for sequences and revisions.
"""

from typing import Any, Dict, List, Tuple
import re
from app.finance_agent.utils.tool_input_parser import parse_tool_input_as_string, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    QuotationFields,
    QuotationPrefixes,
    QuotationDefaults
)
from database.db_helper import DatabaseError
from database.supabase.db_connection import execute_query


# ============================================================================
# Business Logic Functions
# ============================================================================

def _parse_input(tool_input: Any) -> Tuple[str, bool]:
    """
    Parse and validate tool input.

    Args:
        tool_input: Can be JSON string, dict, or plain string

    Returns:
        Tuple of (job_no, is_revision)

    Raises:
        ValueError: If job_no is missing
    """
    # Handle dict input
    if isinstance(tool_input, dict):
        job_no = tool_input.get('job_no')
        is_revision = tool_input.get('is_revision', False)
    # Handle string input (try JSON first, then plain string)
    elif isinstance(tool_input, str):
        import json
        try:
            params = json.loads(tool_input)
            job_no = params.get('job_no')
            is_revision = params.get('is_revision', False)
        except json.JSONDecodeError:
            # Plain string - treat as job_no
            job_no = tool_input
            is_revision = False
    else:
        raise ValueError(f"Unexpected input type: {type(tool_input)}")

    if not job_no:
        raise ValueError("job_no is required")

    return job_no, is_revision


def _generate_quotation_prefix(job_no: str) -> str:
    """
    Generate quotation prefix from job number.

    Removes the last part after the final dash and adds "Q-" prefix.

    Args:
        job_no: Job number (e.g., "JCP-25-01-1")

    Returns:
        Quotation prefix (e.g., "Q-JCP-25-01")

    Examples:
        >>> _generate_quotation_prefix("JCP-25-01-1")
        "Q-JCP-25-01"
        >>> _generate_quotation_prefix("ABC-2024-05-2")
        "Q-ABC-2024-05"
    """
    parts = job_no.rsplit("-", 1)  # Split from right, only once
    job_no_base = parts[0]
    return f"{QuotationPrefixes.QUOTATION}{job_no_base}"


def _fetch_existing_quotations(quotation_prefix: str) -> List[Dict[str, Any]]:
    """
    Fetch existing quotations with the given prefix.

    Args:
        quotation_prefix: Quotation prefix to search for

    Returns:
        List of existing quotation records
    """
    quotations = execute_query(
        f"""
        SELECT {QuotationFields.QUO_NO}
        FROM {DatabaseSchema.QUOTATION_TABLE}
        WHERE {QuotationFields.QUO_NO} LIKE %s
        ORDER BY {QuotationFields.QUO_NO} DESC
        """,
        params=(f"{quotation_prefix}-%",),
        fetch_results=True
    )

    return quotations or []


def _parse_sequence_and_revision(
    existing_quotations: List[Dict[str, Any]]
) -> Tuple[int, Dict[int, int]]:
    """
    Parse existing quotation numbers to extract max sequence and revisions.

    Args:
        existing_quotations: List of quotation records

    Returns:
        Tuple of (max_sequence_number, sequence_revisions_dict)
        where sequence_revisions_dict is {seq_num: max_revision}

    Examples:
        Input: ["Q-JCP-25-01-q1-R00", "Q-JCP-25-01-q1-R01", "Q-JCP-25-01-q2-R00"]
        Output: (2, {1: 1, 2: 0})
    """
    max_seq = 0
    seq_revisions = {}  # {seq_num: max_revision}

    for row in existing_quotations:
        quo_no = row[QuotationFields.QUO_NO]

        # Extract sequence and revision from pattern like "Q-JCP-25-01-q2-R01"
        # Support both old format (r0) and new format (R00)
        match = re.search(r'-q(\d+)-[rR](\d+)$', quo_no)
        if match:
            seq_num = int(match.group(1))
            rev_num = int(match.group(2))
            max_seq = max(max_seq, seq_num)

            # Track max revision for each sequence
            if seq_num not in seq_revisions:
                seq_revisions[seq_num] = rev_num
            else:
                seq_revisions[seq_num] = max(seq_revisions[seq_num], rev_num)

    return max_seq, seq_revisions


def _calculate_next_sequence_and_revision(
    is_revision: bool,
    max_seq: int,
    seq_revisions: Dict[int, int]
) -> Tuple[str, str]:
    """
    Calculate the next sequence number and revision.

    Args:
        is_revision: True if creating revision, False if new sequence
        max_seq: Maximum sequence number found
        seq_revisions: Dict mapping sequence numbers to their max revisions

    Returns:
        Tuple of (sequence_string, revision_string)

    Examples:
        >>> # New sequence
        >>> _calculate_next_sequence_and_revision(False, 2, {1: 1, 2: 0})
        ("q3", "00")

        >>> # New revision of existing sequence
        >>> _calculate_next_sequence_and_revision(True, 2, {1: 1, 2: 0})
        ("q2", "01")
    """
    if is_revision:
        # Create a new revision of the latest sequence
        seq_no = f"{QuotationPrefixes.SEQUENCE}{max_seq}"
        latest_revision = seq_revisions.get(max_seq, 0)
        revision_str = f"{latest_revision + 1:02d}"
    else:
        # Create a new sequence with revision "00"
        seq_no = f"{QuotationPrefixes.SEQUENCE}{max_seq + 1}"
        revision_str = QuotationDefaults.REVISION

    return seq_no, revision_str


# ============================================================================
# Main Tool Function
# ============================================================================

def create_quotation_no_tool(tool_input: Any) -> Dict[str, Any]:
    """
    Generate a new quotation number based on the given job number with sequence
    and revision tracking.

    This tool creates unique quotation numbers following the pattern:
    Q-{job_no_base}-q{sequence}-R{revision}

    The tool maintains two counters:
    - Sequence number (q1, q2, q3, ...): Increments for new quotations
    - Revision number (R00, R01, R02, ...): Increments for revisions of same quotation

    Args:
        tool_input: Can be either:
            - JSON string: '{"job_no": "JCP-25-01-1", "is_revision": false}'
            - Dictionary: {"job_no": "JCP-25-01-1", "is_revision": true}
            - Plain string: "JCP-25-01-1" (is_revision defaults to False)

    Required Parameter:
        - job_no: Job number (e.g., "JCP-25-01-1")

    Optional Parameter:
        - is_revision: Boolean (default False)
            - False: Create new sequence (increment q), reset revision to R00
            - True: Keep same sequence (same q), increment revision (R01, R02, ...)

    Returns:
        dict: {
            "quotation_no": str (e.g., "Q-JCP-25-01-q1"),
            "revision_str": str (e.g., "00", "01", "02")
        }

        On error: {"error": "error message"}

    Examples:
        >>> # First quotation for a job
        >>> create_quotation_no_tool("JCP-25-01-1")
        {"quotation_no": "Q-JCP-25-01-q1", "revision_str": "00"}

        >>> # Second quotation (new sequence)
        >>> create_quotation_no_tool({"job_no": "JCP-25-01-1", "is_revision": False})
        {"quotation_no": "Q-JCP-25-01-q2", "revision_str": "00"}

        >>> # Revision of first quotation
        >>> create_quotation_no_tool({"job_no": "JCP-25-01-1", "is_revision": True})
        {"quotation_no": "Q-JCP-25-01-q1", "revision_str": "01"}

    Workflow:
        1. Parse input to get job_no and is_revision flag
        2. Generate quotation prefix: Q-{job_no_base}
           (e.g., "JCP-25-01-1" → "Q-JCP-25-01")
        3. Query database for existing quotations with this prefix
        4. Parse existing quotations to find:
           - Maximum sequence number
           - Maximum revision for each sequence
        5. Calculate next sequence and revision:
           - If is_revision=True: Same sequence, increment revision
           - If is_revision=False: New sequence, reset revision to "00"
        6. Return quotation number (without revision suffix) and revision string

    Full Quotation Number Format:
        The complete quotation number stored in the database combines:
        - quotation_no: "Q-JCP-25-01-q1"
        - revision: "R01"
        - Full: "Q-JCP-25-01-q1-R01"
    """
    try:
        # Parse and validate input
        job_no, is_revision = _parse_input(tool_input)

        # Generate quotation prefix from job number
        quotation_prefix = _generate_quotation_prefix(job_no)

        # Fetch existing quotations with this prefix
        existing_quotations = _fetch_existing_quotations(quotation_prefix)

        # Determine sequence and revision numbers
        if not existing_quotations:
            # First quotation for this project
            seq_no = f"{QuotationPrefixes.SEQUENCE}1"
            revision_str = QuotationDefaults.REVISION
        else:
            # Parse existing quotations
            max_seq, seq_revisions = _parse_sequence_and_revision(existing_quotations)

            # Calculate next sequence and revision
            seq_no, revision_str = _calculate_next_sequence_and_revision(
                is_revision, max_seq, seq_revisions
            )

        # Build final quotation number (without revision suffix)
        quotation_no = f"{quotation_prefix}-{seq_no}"

        return {
            "quotation_no": quotation_no,
            "revision_str": revision_str
        }

    except (ValueError, ToolInputError) as e:
        return {"error": str(e)}
    except DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        error_msg = f"Unexpected error creating quotation number: {str(e)}"
        print(f"[ERROR][create_quotation_no_tool] {error_msg}")
        return {"error": error_msg}
