from datetime import datetime
from typing import ClassVar
from sqlmodel import SQLModel, Field, Session
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP

# ============================================================
#  SQLite-Compatible Schemas for Job Tests
# ============================================================

class DesignJobSchemaForTest(SQLModel, table=True):
    # SQLite-friendly version of DesignJobSchema (no schema / FK)
    __tablename__: ClassVar[str] = "design_job"
    __table_args__: ClassVar[dict] = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    company_id: int
    title: str

    status: str | None = None
    quotation_status: str | None = None
    job_no: str | None = None

    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


class InspectionJobSchemaForTest(SQLModel, table=True):
    # SQLite-friendly version of InspectionJobSchema (no schema / FK)
    __tablename__: ClassVar[str] = "inspection_job"
    __table_args__: ClassVar[dict] = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    company_id: int
    title: str

    status: str | None = None
    quotation_status: str | None = None
    job_no: str | None = None

    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

# ============================================================
#  SQLite-Compatible Quotation Schema for Testing
# ============================================================

class QuotationSchemaForTest(SQLModel, table=True):
    """
    SQLite-friendly 版本，aligned with production QuotationSchema fields
    """
    __tablename__: ClassVar[str] = "quotation"
    __table_args__: ClassVar[dict] = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)

    # Production schema fields (required)
    # Note: index=False to avoid "index already exists" error with extend_existing
    quo_no: str = Field(index=False, max_length=50)
    client_id: int
    project_name: str
    date_issued: datetime
    status: str = Field(default="DRAFTED", max_length=20)
    currency: str = Field(default="MOP", max_length=3)
    revision_no: int = Field(default=0)
    valid_until: datetime | None = None
    notes: str | None = None

    # Test-specific fields
    job_id: int | None = None
    company_id: int | None = None
    quotation_no: str | None = None
    total_amount: float | None = None

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

class QuotationItemSchemaForTest(SQLModel, table=True):
    # 👇 change name so it doesn’t clash with production QuotationItem
    __tablename__: ClassVar[str] = "quotation_item_test"

    id: int | None = Field(default=None, primary_key=True)
    quotation_id: int
    item_desc: str
    unit: str
    quantity: int
    unit_price: float
    amount: float

    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

# ============================================================
#  Generic SQLite Debug Helper
# ============================================================

def print_table_schema(session: Session, table_name: str):
    print("\n" + "=" * 60)
    print(f"TABLE STRUCTURE: {table_name}")
    print("=" * 60)

    # Table structure
    result = session.execute(text(f"PRAGMA table_info({table_name})"))
    for row in result:
        print(f"Column: {row[1]:<20} Type: {row[2]:<15} NotNull: {row[3]} PK: {row[5]}")

    print("\n" + "=" * 60)
    print(f"TABLE DATA: {table_name}")
    print("=" * 60)

    rows = session.execute(text(f"SELECT * FROM {table_name}")).all()
    if not rows:
        print("(No data)")
    else:
        for r in rows:
            print(r)

    print("=" * 60 + "\n")

