from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SAEnum, Computed, Numeric, text
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.models.enums import UnitType, DBTable

# ============================================================================
# QUOTATION HEADER (Finance.quotation table)
# ============================================================================

class QuotationBase(SQLModel):
    """Base fields for quotation header."""
    quo_no: str = Field(index=True, max_length=50)
    client_id: int = Field(foreign_key="Finance.company.id")
    project_name: str
    date_issued: date
    status: str = Field(default="DRAFTED", max_length=20)  # DRAFTED, SENT, ACCEPTED, REJECTED, EXPIRED
    currency: str = Field(default="MOP", max_length=3)
    revision_no: int = Field(default=0)
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class Quotation(QuotationBase, table=True):
    """
    Quotation header model mapped to Finance.quotation table.

    Represents a quotation with metadata. Line items are in QuotationItem.
    """
    __tablename__: str = DBTable.QUOTATION_TABLE.table
    __table_args__ = {"schema": DBTable.QUOTATION_TABLE.schema}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"server_default": "now()"})
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"server_default": "now()"})

    # Relationship to items
    items: List["QuotationItem"] = Relationship(back_populates="quotation")


class QuotationCreate(QuotationBase):
    """Input model for creating quotation header."""
    pass


class QuotationUpdate(SQLModel):
    """Input model for updating quotation header."""
    quo_no: Optional[str] = None
    client_id: Optional[int] = None
    project_name: Optional[str] = None
    date_issued: Optional[date] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    revision_no: Optional[int] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class QuotationRow(QuotationBase):
    """Output model for quotation header with all fields."""
    id: int
    created_at: datetime
    updated_at: datetime


# ============================================================================
# QUOTATION ITEM (Finance.quotation_item table)
# ============================================================================

class QuotationItemBase(SQLModel):
    """Base fields for quotation line item."""
    quotation_id: int = Field(foreign_key="Finance.quotation.id")
    item_desc: str
    quantity: int
    unit_price: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)


class QuotationItem(QuotationItemBase, table=True):
    """
    Quotation item model mapped to Finance.quotation_item table.

    Represents a line item in a quotation. The amount is calculated automatically.
    """
    __tablename__: str = DBTable.QUOTATION_ITEM_TABLE.table
    __table_args__ = {"schema": DBTable.QUOTATION_ITEM_TABLE.schema}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Use SAEnum to properly map to PostgreSQL enum type
    unit: UnitType = Field(
        default=UnitType.Lot,
        sa_column=Column(
            SAEnum(UnitType, name="unit_type", schema="Finance", create_type=False),
            nullable=False,
            server_default="Lot"
        )
    )

    # Generated column - computed by database as GENERATED ALWAYS
    # SQLAlchemy will exclude this from INSERT/UPDATE statements
    amount: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(
            Numeric(12, 2),
            Computed("quantity * unit_price"),  # Mark as computed
            nullable=True
        )
    )

    # Relationship to quotation
    quotation: Optional[Quotation] = Relationship(back_populates="items")


class QuotationItemCreate(QuotationItemBase):
    """Input model for creating quotation item."""
    pass


class QuotationItemUpdate(SQLModel):
    """Input model for updating quotation item."""
    item_desc: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None


class QuotationItemRow(QuotationItemBase):
    """Output model for quotation item with all fields."""
    id: int
    amount: Decimal
