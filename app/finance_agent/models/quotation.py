"""
Quotation model TypedDicts for type-safe database operations.

Provides lightweight type definitions for quotation records.
"""

from typing import Optional, TypedDict
from datetime import date
from decimal import Decimal


class QuotationRow(TypedDict, total=False):
    """
    Row shape returned from the database for quotation table.
    """
    id: int
    quo_no: str
    date_issued: Optional[date]
    client_id: Optional[int]
    project_name: Optional[str]
    project_item_description: Optional[str]
    sub_amount: Optional[Decimal]
    total_amount: Optional[Decimal]
    currency: Optional[str]
    revision: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]


class QuotationCreate(TypedDict, total=False):
    """
    Payload for creating a new quotation.

    Only quo_no is required per the database schema.
    """
    quo_no: str
    date_issued: Optional[date]
    client_id: Optional[int]
    project_name: Optional[str]
    project_item_description: Optional[str]
    sub_amount: Optional[Decimal]
    total_amount: Optional[Decimal]
    currency: Optional[str]
    revision: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]


class QuotationUpdate(TypedDict, total=False):
    """
    Payload for updating an existing quotation.

    All fields are optional - only provided fields will be updated.
    """
    quo_no: Optional[str]
    date_issued: Optional[date]
    client_id: Optional[int]
    project_name: Optional[str]
    project_item_description: Optional[str]
    sub_amount: Optional[Decimal]
    total_amount: Optional[Decimal]
    currency: Optional[str]
    revision: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]
