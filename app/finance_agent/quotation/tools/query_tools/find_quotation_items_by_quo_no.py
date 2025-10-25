"""
Query tool for fetching quotation items by quotation number.

This module provides functionality to retrieve all project items
associated with a specific quotation number from the database.
"""

from app.postgres.db_connection import execute_query
from typing import List, Dict, Any


def find_quotation_items_by_quo_no(quotation_no: str) -> List[Dict[str, Any]]:
    """
    Find all quotation items by quotation number.

    This function queries the Finance.quotation table to retrieve all items
    associated with a specific quotation number.

    Args:
        quotation_no: The quotation number (e.g., "Q-JCP-25-01-q1")

    Returns:
        list[dict]: List of quotation items with the following structure:
            [
                {
                    "id": 1,
                    "quo_no": "Q-JCP-25-01-q1",
                    "date_issued": "2025-01-15",
                    "client_id": 5,
                    "project_name": "校園實驗室消防安全檢測",
                    "project_item_description": "支撐架計算",
                    "sub_amount": 7000.0,
                    "total_amount": 13000.0,
                    "currency": "MOP",
                    "revision": "00",
                    "amount": 1.0,
                    "unit": "Lot"
                },
                ...
            ]

    Example:
        >>> items = find_quotation_items_by_quo_no("Q-JCP-25-01-q1")
        >>> print(f"Found {len(items)} items")
        >>> for item in items:
        ...     print(f"{item['project_item_description']}: {item['sub_amount']} {item['currency']}")
    """
    query = """
        SELECT
            q.id,
            q.quo_no,
            q.date_issued,
            q.client_id,
            q.project_name,
            q.project_item_description,
            q.sub_amount,
            q.total_amount,
            q.currency,
            q.revision,
            q.amount,
            q.unit
        FROM "Finance".quotation q
        WHERE q.quo_no = %s
        ORDER BY q.id ASC;
    """

    try:
        rows = execute_query(
            query=query,
            params=(quotation_no,),
            fetch_results=True
        )

        # Convert RealDictRow to regular dict for JSON serialization
        return [dict(row) for row in rows] if rows else []

    except Exception as e:
        print(f"[ERROR][find_quotation_items_by_quo_no] Failed to query quotation items: {e}")
        return []
