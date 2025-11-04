"""
Company model TypedDicts for type-safe database operations.

Provides lightweight type definitions for company records.
"""

from typing import Optional, TypedDict


class CompanyRow(TypedDict, total=False):
    """
    Row shape returned from the database for company table.
    """
    id: int
    name: str
    alias: Optional[str]
    address: Optional[str]
    phone: Optional[str]


class CompanyCreate(TypedDict, total=False):
    """
    Payload for creating a new company.

    Only name is required, other fields are optional.
    """
    name: str
    alias: Optional[str]
    address: Optional[str]
    phone: Optional[str]


class CompanyUpdate(TypedDict, total=False):
    """
    Payload for updating an existing company.

    All fields are optional - only provided fields will be updated.
    """
    name: Optional[str]
    alias: Optional[str]
    address: Optional[str]
    phone: Optional[str]
