# app/models/quotation_models.py
import os
from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SAEnum, Computed, Numeric
from pydantic import BaseModel, Field as PydanticField
from app.models.enums import UnitType, DBTable

# Check if we should use schema prefix (default: True for production, False for testing)
USE_DB_SCHEMA = os.getenv("USE_DB_SCHEMA", "1") == "1"


# ============================================================
# Base: Shared fields (NOT a table)
# ============================================================

class QuotationBaseModel(SQLModel):
    """
    共享字段，不是表。
    用于 Schema 和 Model 继承公共字段。
    """
    quo_no: str = Field(index=True, max_length=50)
    client_id: int = Field(foreign_key="Finance.company.id" if USE_DB_SCHEMA else "company.id")
    project_name: str
    date_issued: date
    status: str = Field(default="DRAFTED", max_length=20)
    currency: str = Field(default="MOP", max_length=3)
    revision_no: int = Field(default=0)
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class QuotationItemBaseModel(SQLModel):
    """
    共享字段，不是表。
    用于 Schema 和 Model 继承公共字段。
    """
    quotation_id: int = Field(foreign_key="Finance.quotation.id" if USE_DB_SCHEMA else "quotation.id")
    item_desc: str
    quantity: int
    unit_price: Decimal = Field(default=Decimal("0.00"))


# ============================================================
# Schema: Table structure / ORM mapping
# ============================================================

class QuotationSchema(QuotationBaseModel, table=True):
    """
    ORM 映射 Finance.quotation 表的 Schema。

    注意：
    - created_at / updated_at 由 DB 生成，应用不传，由 server_default(now()) 填充。
    """
    __tablename__: str = DBTable.QUOTATION_TABLE.table
    __table_args__ = {"schema": DBTable.QUOTATION_TABLE.schema} if USE_DB_SCHEMA else {}

    id: Optional[int] = Field(default=None, primary_key=True)

    # DB 生成时间戳，插入时不需要传
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": "now()"},
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": "now()"},
    )

    # Relationship to items
    items: List["QuotationItemSchema"] = Relationship(back_populates="quotation")


class QuotationItemSchema(QuotationItemBaseModel, table=True):
    """
    ORM 映射 Finance.quotation_item 表的 Schema。

    注意：
    - amount 由 DB 生成 (GENERATED ALWAYS AS quantity * unit_price)。
    """
    __tablename__: str = DBTable.QUOTATION_ITEM_TABLE.table
    __table_args__ = {"schema": DBTable.QUOTATION_ITEM_TABLE.schema} if USE_DB_SCHEMA else {}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Use SAEnum to properly map to PostgreSQL enum type
    unit: UnitType = Field(
        default=UnitType.Lot,
        sa_column=Column(
            SAEnum(UnitType, name="unit_type", schema="Finance" if USE_DB_SCHEMA else None, create_type=False),
            nullable=False,
            server_default="Lot",
        ),
    )

    # Generated column - computed by database as GENERATED ALWAYS
    amount: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(
            Numeric(12, 2),
            Computed("quantity * unit_price"),
            nullable=True,
        ),
    )

    # Relationship to quotation
    quotation: Optional[QuotationSchema] = Relationship(back_populates="items")


# ============================================================
# Model: Business data shape / DTO
# ============================================================

class QuotationCreateModel(QuotationBaseModel):
    """
    创建 Quotation 记录时用的 DTO (业务层)。
    不包含 id / created_at / updated_at,这些都由 DB 负责。
    """
    pass


class QuotationUpdateModel(SQLModel):
    """
    更新 Quotation 记录时用的 DTO（业务层）。
    所有字段都是可选的（只更新提供的字段）。
    """
    quo_no: Optional[str] = None
    client_id: Optional[int] = None
    project_name: Optional[str] = None
    date_issued: Optional[date] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    revision_no: Optional[int] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class QuotationReadModel(QuotationBaseModel):
    """
    Used for reading / returning Quotation records (business layer).
    """
    id: int
    created_at: datetime
    updated_at: datetime


class QuotationItemCreateModel(QuotationItemBaseModel):
    """
    DTO for creating QuotationItem records (business layer).
    不包含 id / amount,这些都由 DB 负责。
    """
    pass


class QuotationItemUpdateModel(SQLModel):
    """
    DTO for updating QuotationItem records (business layer).
    所有字段都是可选的（只更新提供的字段）。
    """
    item_desc: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None


class QuotationItemReadModel(QuotationItemBaseModel):
    """
    读取 / 返回 QuotationItem 记录时用的 DTO（业务层）。
    """
    id: int
    amount: Decimal


# ============================================================
# 向后兼容别名（保持老代码暂时不崩）
# ============================================================

# Model 别名
QuotationCreate = QuotationCreateModel  # DEPRECATED: 请迁移到 QuotationCreateModel
QuotationUpdate = QuotationUpdateModel  # DEPRECATED: 请迁移到 QuotationUpdateModel
QuotationRow = QuotationReadModel  # DEPRECATED: 请迁移到 QuotationReadModel

QuotationItemCreate = QuotationItemCreateModel  # DEPRECATED: 请迁移到 QuotationItemCreateModel
QuotationItemUpdate = QuotationItemUpdateModel  # DEPRECATED: 请迁移到 QuotationItemUpdateModel
QuotationItemRow = QuotationItemReadModel  # DEPRECATED: 请迁移到 QuotationItemReadModel

# Base 别名
QuotationBase = QuotationBaseModel  # DEPRECATED: 请迁移到 QuotationBaseModel
QuotationItemBase = QuotationItemBaseModel  # DEPRECATED: 请迁移到 QuotationItemBaseModel


# ============================================================
# Flow DTOs (Agent / LangGraph 用的流程级 DTO)
# ============================================================

class QuotationItemInput(BaseModel):
    """
    Schema for a single quotation item in the generation flow.
    (Flow / Agent layer, not directly corresponding to DB rows)
    """
    project_item_description: str = PydanticField(
        ..., description="Item description"
    )
    quantity: float = PydanticField(
        ..., gt=0, description="Quantity"
    )
    unit: str = PydanticField(
        ..., description="Unit type (e.g., '項', 'pcs', 'set')"
    )
    sub_amount: Decimal = PydanticField(
        ..., description="Sub amount (unit price * quantity)"
    )
    total_amount: Decimal = PydanticField(
        ..., description="Total amount"
    )


class QuotationGenerationInput(BaseModel):
    """
    Input schema for quotation generation flow.

    一条「生成报价」流程所需的完整输入。
    """
    job_no: str = PydanticField(
        ..., description="Job number (e.g., 'Q-JCP-25-01-1')"
    )
    company_id: int = PydanticField(
        ..., description="Company/Client ID"
    )
    project_name: str = PydanticField(
        ..., description="Project name"
    )
    currency: str = PydanticField(
        default="MOP", description="Currency code"
    )
    items: List[QuotationItemInput] = PydanticField(
        ..., min_length=1, description="List of quotation items"
    )
    date_issued: Optional[date] = PydanticField(
        None, description="Issue date (defaults to today)"
    )
    revision_no: str = PydanticField(
        default="00",
        description="Revision number (00=no revision, 01/02/etc=revision)",
    )
    valid_until: Optional[date] = PydanticField(
        None, description="Valid until date"
    )
    notes: Optional[str] = PydanticField(
        None, description="Notes/remarks"
    )


class QuotationGenerationOutput(BaseModel):
    """
    Output schema for quotation generation flow.
    """
    quo_no: str = PydanticField(
        ..., description="Generated quotation number"
    )
    total: Decimal = PydanticField(
        ..., description="Total quotation amount"
    )
    item_count: int = PydanticField(
        ..., description="Number of line items"
    )
    status: str = PydanticField(
        default="DRAFTED", description="Quotation status"
    )
    message: Optional[str] = PydanticField(
        None, description="Success or info message"
    )
    quotation_ids: Optional[List[int]] = PydanticField(
        None, description="List of created quotation record IDs"
    )


class QuotationUpdateInput(BaseModel):
    """
    Input schema for quotation update operations in the flow.
    """
    quotation_ids: List[int] = PydanticField(
        ..., min_length=1, description="List of quotation IDs to update"
    )
    status: Optional[str] = PydanticField(
        None, description="New status"
    )
    notes: Optional[str] = PydanticField(
        None, description="New notes"
    )
    valid_until: Optional[date] = PydanticField(
        None, description="New valid until date"
    )


class QuotationQueryInput(BaseModel):
    """
    Input schema for querying quotations in the flow.
    """
    quo_no: Optional[str] = PydanticField(
        None, description="Quotation number"
    )
    job_no: Optional[str] = PydanticField(
        None, description="Job number pattern"
    )
    company_id: Optional[int] = PydanticField(
        None, description="Company ID"
    )
    project_name: Optional[str] = PydanticField(
        None, description="Project name pattern"
    )
    limit: Optional[int] = PydanticField(
        10, gt=0, le=100, description="Maximum results"
    )


class QuotationFlowResponse(BaseModel):
    """
    Generic response schema for quotation flow operations.

    用来包住各种 quotation flow node 嘅返回值。
    """
    success: bool = PydanticField(
        ..., description="Whether operation succeeded"
    )
    data: Optional[Any] = PydanticField(
        None, description="Response data (varies by operation)"
    )
    error: Optional[str] = PydanticField(
        None, description="Error message if failed"
    )
    operation: str = PydanticField(
        ..., description="Operation type (e.g., 'create', 'update', 'query')"
    )
