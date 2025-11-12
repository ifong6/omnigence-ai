from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Index, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.constants import DBTable


class CompanyBase(SQLModel):
    """Shared attributes for create/update/read operations."""
    name: str = Field(index=True, max_length=200)
    alias: Optional[str] = Field(default=None, max_length=64)
    address: Optional[str] = Field(default=None, max_length=300)
    phone: Optional[str] = Field(default=None, max_length=32)


class Company(CompanyBase, table=True):
    """
    Company model mapped to Finance.company table.

    Provides ORM capabilities for company records.
    """
    __tablename__ = DBTable.COMPANY_TABLE.split(".")[1]
    __table_args__ = (
        Index("idx_company_alias", "alias"),
        {"schema": "Finance"},  # ✅ must be last and wrapped in a tuple
    )

    id: Optional[int] = Field(default=None, primary_key=True)


# ======================================================================
# Input/Output Models (aligned with job_models.py)
# ======================================================================

class CompanyCreate(CompanyBase):
    """Used for company creation."""
    pass


class CompanyUpdate(SQLModel):
    """Used for partial company updates."""
    name: Optional[str] = None
    alias: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class CompanyRow(Company):
    """Used for read operations."""
    pass
