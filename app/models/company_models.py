# app/models/company_models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from app.models.enums import DBTable

# ============================================================
# Base: Shared fields (NOT a table)
# ============================================================

class CompanyBaseModel(SQLModel):
    """
    Shared fields, not a table.
    Used for Schema and Model to inherit common fields.
    """
    name: str = Field(index=True, max_length=200)
    alias: Optional[str] = Field(default=None, max_length=64)
    address: Optional[str] = Field(default=None, max_length=300)
    phone: Optional[str] = Field(default=None, max_length=32)


# ============================================================
# Schema: Table structure / ORM mapping
# ============================================================

class CompanySchema(CompanyBaseModel, table=True):
    """
    ORM mapping of the Finance.company table Schema.
    """
    __tablename__: str = DBTable.COMPANY_TABLE.table
    __table_args__ = (
        Index("idx_company_alias", "alias"),
        {"schema": DBTable.COMPANY_TABLE.schema},  # must be last and wrapped in a tuple
    )

    id: Optional[int] = Field(default=None, primary_key=True)


# ============================================================
# Model: Business data shape / DTO
# ============================================================

class CompanyCreateModel(SQLModel):
    """
    Used for creating Company records (business layer).
    Does not include id, id is handled by DB.
    """
    name: str
    alias: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class CompanyUpdateModel(SQLModel):
    """
    Used for updating Company records (business layer).
    All fields are optional (only update provided fields).
    """
    name: Optional[str] = None
    alias: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class CompanyReadModel(SQLModel):
    """
    Used for reading / returning Company records (business layer).
    """
    id: int
    name: str
    alias: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


# ============================================================
# Backward compatibility aliases
# ============================================================

Company = CompanySchema  # DEPRECATED: Please migrate to CompanySchema
CompanyCreate = CompanyCreateModel  # DEPRECATED: Please migrate to CompanyCreateModel
CompanyUpdate = CompanyUpdateModel  # DEPRECATED: Please migrate to CompanyUpdateModel
CompanyRow = CompanyReadModel  # DEPRECATED: Please migrate to CompanyReadModel
CompanyModel = CompanyBaseModel  # DEPRECATED: Please migrate to CompanyBaseModel
CompanyBase = CompanyBaseModel  # DEPRECATED: Please migrate to CompanyBaseModel
