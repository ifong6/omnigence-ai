# app/models/flow_models.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.models.enums import DBTable

class FlowBaseModel(SQLModel):
    """
    Shared fields, not a table.
    Used for Schema and Model to inherit common fields.
    """
    session_id: UUID
    user_request_summary: Optional[str] = None
    identified_agents: Optional[str] = Field(default=None, max_length=255)


# ============================================================
# Schema: Table structure / ORM mapping
# ============================================================

class FlowSchema(FlowBaseModel, table=True):
    """
    ORM mapping of the Finance.flow table Schema.
    """
    __tablename__: str = DBTable.FLOW_TABLE.table
    __table_args__ = {"schema": DBTable.FLOW_TABLE.schema}

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # DB generated timestamp, application does not pass, filled by server_default(now())
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=True,
        ),
    )


# ============================================================
# Model: Business data shape / DTO
# ============================================================

class FlowCreateModel(SQLModel):
    """
    Used for Flow creation.
    Does not include id / created_at, id & created_at are handled by DB.
    """
    session_id: UUID
    user_request_summary: Optional[str] = None
    identified_agents: Optional[list[str]] = None


class FlowReadModel(SQLModel):
    """
    Used for Flow read operations.
    """
    id: UUID
    session_id: UUID
    user_request_summary: Optional[str] = None
    identified_agents: Optional[list[str]] = None
    created_at: datetime


# ============================================================
# Backward compatibility aliases
# ============================================================

Flow = FlowSchema  # DEPRECATED: Please migrate to FlowSchema
FlowRow = FlowReadModel  # DEPRECATED: Please migrate to FlowReadModel
FlowBase = FlowBaseModel  # DEPRECATED: Please migrate to FlowBaseModel
