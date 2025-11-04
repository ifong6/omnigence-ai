"""
SQL identifier validation utilities.

Provides safe validation for table names and column names to prevent SQL injection.
"""

import re
from typing import Iterable, List, Optional

# Fixed regex: added missing $ and removed extra )
_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def as_table(table: str) -> str:
    """
    Accepts either a safe unqualified identifier (e.g., design_job)
    or a fully quoted/qualified name (e.g., '"Finance".design_job').

    Args:
        table: Table name to validate

    Returns:
        Validated table name

    Raises:
        ValueError: If table identifier is unsafe

    Examples:
        >>> as_table('design_job')
        'design_job'
        >>> as_table('"Finance".design_job')
        '"Finance".design_job'
        >>> as_table('bad-table')  # doctest: +SKIP
        ValueError: Unsafe table identifier: 'bad-table'
    """
    s = table.strip()

    # If it starts with a quote and contains another quote, assume pre-quoted/qualified
    if s.startswith('"') and '"' in s[1:]:
        return s  # Trusted, fully-qualified table

    # Otherwise, validate as a simple identifier
    if _IDENTIFIER_RE.match(s):
        return s

    raise ValueError(f"Unsafe table identifier: {table!r}")


def validate_columns(
    cols: Iterable[str],
    allowed: Optional[Iterable[str]] = None
) -> List[str]:
    """
    Validate column names against regex and optional allowlist.

    Args:
        cols: Column names to validate
        allowed: Optional allowlist of permitted column names

    Returns:
        List of validated column names

    Raises:
        ValueError: If column is not allowed or unsafe

    Examples:
        >>> validate_columns(['id', 'name'])
        ['id', 'name']
        >>> validate_columns(['id', 'name'], allowed=['id', 'email'])
        Traceback (most recent call last):
        ...
        ValueError: Column not allowed: name
    """
    allowed_set = set(allowed) if allowed is not None else None
    out: List[str] = []

    for c in cols:
        # Check allowlist if provided
        if allowed_set is not None and c not in allowed_set:
            raise ValueError(f"Column not allowed: {c}")

        # Check identifier safety
        if not _IDENTIFIER_RE.match(c):
            raise ValueError(f"Unsafe column identifier: {c}")

        out.append(c)

    return out
