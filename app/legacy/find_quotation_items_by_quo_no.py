"""
Query tool for fetching quotation items by quotation number.

Refactored to use centralized QuotationService with SQLModel ORM.
"""

from typing import List, Dict, Any
from sqlmodel import Session

from app.db.engine import engine
from app.services.quotation_service import QuotationService


def find_quotation_items_by_quo_no(quotation_no: str) -> List[Dict[str, Any]]:
    """
    Find all quotation items by quotation number using QuotationService.

    Refactored to use centralized QuotationService with SQLModel ORM.

    Args:
        quotation_no: The quotation number (e.g., "Q-JCP-25-01-q1-R00")

    Returns:
        list[dict]: List of quotation items with the following structure:
            [
                {
                    "id": 1,
                    "quo_no": "Q-JCP-25-01-q1-R00",
                    "date_issued": "2025-01-15",
                    "client_id": 5,
                    "project_name": "校園實驗室消防安全檢測",
                    "project_item_description": "支撐架計算",
                    "sub_amount": 7000.0,
                    "total_amount": 13000.0,
                    "currency": "MOP",
                    "revision": "00",
                    "quantity": 1.0,
                    "unit": "Lot"
                },
                ...
            ]

    Example:
        >>> items = find_quotation_items_by_quo_no("Q-JCP-25-01-q1-R00")
        >>> print(f"Found {len(items)} items")
        >>> for item in items:
        ...     print(f"{item['project_item_description']}: {item['sub_amount']} {item['currency']}")
    """
    try:
        with Session(engine) as session:
            quotation_service = QuotationService(session)
            items = quotation_service.get_quotations_by_quo_no(quotation_no)

            # Convert Quotation ORM objects to dicts
            return [
                {
                    "id": item.id,
                    "quo_no": item.quo_no,
                    "date_issued": str(item.date_issued) if item.date_issued else None,
                    "client_id": item.client_id,
                    "project_name": item.project_name,
                    "project_item_description": item.project_item_description,
                    "sub_amount": float(item.sub_amount) if item.sub_amount else 0,
                    "total_amount": float(item.total_amount) if item.total_amount else 0,
                    "currency": item.currency,
                    "revision": item.revision,
                    "quantity": item.quantity,
                    "unit": item.unit
                }
                for item in items
            ]

    except Exception as e:
        print(f"[ERROR][find_quotation_items_by_quo_no] Failed to query quotation items: {e}")
        import traceback
        traceback.print_exc()
        return []
