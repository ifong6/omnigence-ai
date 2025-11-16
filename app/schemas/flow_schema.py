from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel

class FlowBase(SQLModel):
    """
    Base schema for Flow (DB logging) operations.
    Contains common fields for flow execution tracking.
    """
    session_id: UUID
    identified_agents: Optional[str] = None
    user_request_summary: Optional[str] = None


class FlowCreate(FlowBase):
    """
    Schema for creating a new Flow record in the database.

    Used by PreRoutingLoggerService to log flow execution details.
    The 'id' field is optional and will be auto-generated if not provided.

    Note: Flow is an append-only audit log table. Records are created but never updated.
    """
    id: Optional[UUID] = None
