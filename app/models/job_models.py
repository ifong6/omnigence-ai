from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.models.enums import DBTable

# Shared fields between job models
class JobBase(SQLModel):
    company_id: int = Field(foreign_key="Finance.company.id")
    title: str
    status: str  # DB enforces enum: 'NEW'|'IN_PROGRESS'|'COMPLETED'|'CANCELLED'
    job_no: Optional[str] = None
    quotation_status: Optional[str] = None  # DB enforces enum
    quotation_issued_at: Optional[datetime] = None


# Database table models
class DesignJob(JobBase, table=True):
    __tablename__: str = DBTable.DESIGN_JOB_TABLE.table
    __table_args__ = {"schema": DBTable.DESIGN_JOB_TABLE.schema}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Database-generated field (server_default=now())
    # Only defined in table model to prevent it from being sent in INSERT
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )


class InspectionJob(JobBase, table=True):
    __tablename__: str = DBTable.INSPECTION_JOB_TABLE.table
    __table_args__ = {"schema": DBTable.INSPECTION_JOB_TABLE.schema}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Database-generated field (server_default=now())
    # Only defined in table model to prevent it from being sent in INSERT
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )


# Create input models (optional id for auto-generation)
class JobCreate(JobBase):
    id: Optional[int] = None


# Update input models (all optional)
class JobUpdate(SQLModel):
    company_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    job_no: Optional[str] = None
    date_created: Optional[datetime] = None
    quotation_status: Optional[str] = None
    quotation_issued_at: Optional[datetime] = None


# Read output models (contains all fields including DB-generated)
class JobRow(JobBase):
    id: int
    date_created: datetime  # Database-generated field
