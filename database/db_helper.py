"""
Database helper functions with improved error handling and logging.

This module provides wrapper functions around database operations to:
- Centralize error handling
- Add logging
- Provide consistent return formats
- Handle common database patterns
"""

from typing import Any, Dict, List, Optional, Tuple
from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum
import logging

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


def safe_execute_query(
    query: str,
    params: Optional[Tuple] = None,
    fetch_results: bool = True,
    operation_name: str = "database operation"
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a database query with error handling and logging.

    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_results: Whether to fetch and return results
        operation_name: Description of operation for logging/errors

    Returns:
        List of result rows as dicts if fetch_results=True, None otherwise

    Raises:
        DatabaseError: If query execution fails
    """
    return execute_query(query=query, params=params, fetch=True)   


def find_one_by_field(
    table: str,
    field: str,
    value: Any,
    operation_name: str = "find record"
) -> Optional[Dict[str, Any]]:
    """
    Find a single record by a field value.

    Args:
        table: Table name (including schema if needed)
        field: Field name to search by
        value: Value to search for
        operation_name: Description for logging

    Returns:
        Record dict if found, None otherwise

    Example:
        >>> company = find_one_by_field(
        ...     table='"Finance".company',
        ...     field="name",
        ...     value="ABC Company"
        ... )
    """
    query = f"""
        SELECT *
        FROM {table}
        WHERE {field} = %s
        LIMIT 1
    """

    results = safe_execute_query(
        query=query,
        params=(value,),
        fetch_results=True,
        operation_name=f"{operation_name} by {field}"
    )

    return results[0] if results else None


def find_many_by_field(
    table: str,
    field: str,
    value: Any,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    operation_name: str = "find records"
) -> List[Dict[str, Any]]:
    """
    Find multiple records by a field value.

    Args:
        table: Table name (including schema if needed)
        field: Field name to search by
        value: Value to search for
        order_by: Optional ORDER BY clause (e.g., "id DESC")
        limit: Optional LIMIT value
        operation_name: Description for logging

    Returns:
        List of matching records

    Example:
        >>> quotations = find_many_by_field(
        ...     table='"Finance".quotation',
        ...     field="quo_no",
        ...     value="Q-JCP-25-01-q1",
        ...     order_by="id ASC"
        ... )
    """
    query = f"""
        SELECT *
        FROM {table}
        WHERE {field} = %s
    """

    if order_by:
        query += f" ORDER BY {order_by}"

    if limit:
        query += f" LIMIT {limit}"

    return safe_execute_query(
        query=query,
        params=(value,),
        fetch_results=True,
        operation_name=f"{operation_name} by {field}"
    ) or []


def insert_record(
    table: str,
    fields: Dict[str, Any],
    returning: str = "*",
    operation_name: str = "insert record"
) -> Optional[Dict[str, Any]]:
    """
    Insert a record and return the inserted row.

    Args:
        table: Table name (including schema if needed)
        fields: Dictionary of field names to values
        returning: RETURNING clause (default: all fields)
        operation_name: Description for logging

    Returns:
        Inserted record dict

    Example:
        >>> # For DESIGN type jobs, use "Finance".design_job table
        >>> job = insert_record(
        ...     table='"Finance".design_job',
        ...     fields={
        ...         "company_id": 1,
        ...         "type": "DESIGN",
        ...         "title": "Test Project"
        ...     }
        ... )
        >>>
        >>> # For INSPECTION type jobs, use "Finance".inspection_job table
        >>> job = insert_record(
        ...     table='"Finance".inspection_job',
        ...     fields={
        ...         "company_id": 1,
        ...         "type": "INSPECTION",
        ...         "title": "Test Project"
        ...     }
        ... )
    """
    field_names = list(fields.keys())
    field_values = list(fields.values())
    placeholders = ", ".join(["%s"] * len(field_values))

    query = f"""
        INSERT INTO {table} ({", ".join(field_names)})
        VALUES ({placeholders})
        RETURNING {returning}
    """

    results = safe_execute_query(
        query=query,
        params=tuple(field_values),
        fetch_results=True,
        operation_name=operation_name
    )

    return results[0] if results else None


def update_record(
    table: str,
    fields: Dict[str, Any],
    where_clause: str,
    where_params: Tuple,
    returning: str = "*",
    operation_name: str = "update record"
) -> List[Dict[str, Any]]:
    """
    Update record(s) and return the updated row(s).

    Args:
        table: Table name (including schema if needed)
        fields: Dictionary of field names to values to update
        where_clause: WHERE clause (e.g., "id = %s")
        where_params: Parameters for WHERE clause
        returning: RETURNING clause (default: all fields)
        operation_name: Description for logging

    Returns:
        List of updated record dicts

    Example:
        >>> updated_jobs = update_record(
        ...     table='"Finance".design_job',
        ...     fields={"status": "Completed"},
        ...     where_clause="id = %s",
        ...     where_params=(123,)
        ... )
    """
    if not fields:
        raise ValueError("No fields provided to update")

    set_clauses = [f"{field} = %s" for field in fields.keys()]
    set_values = list(fields.values())

    query = f"""
        UPDATE {table}
        SET {", ".join(set_clauses)}
        WHERE {where_clause}
        RETURNING {returning}
    """

    all_params = tuple(set_values) + where_params

    return safe_execute_query(
        query=query,
        params=all_params,
        fetch_results=True,
        operation_name=operation_name
    ) or []
