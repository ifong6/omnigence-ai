from typing import TypedDict, NotRequired
from typing_extensions import Required
from datetime import datetime
from uuid import UUID


class FlowRow(TypedDict, total=False):
    """
    Row shape returned from the database for flow table.

    Uses Required/NotRequired to specify which fields are guaranteed.
    """
    id: Required[UUID]
    session_id: Required[UUID]
    user_request_summary: NotRequired[str | None]
    created_at: Required[datetime]  # Automatically set by database
    identified_agents: NotRequired[str | None]


class FlowCreate(TypedDict, total=False):
    """
    Payload for creating a new flow log entry.

    id and session_id are required for creation.
    """
    id: Required[UUID]
    session_id: Required[UUID]
    user_request_summary: NotRequired[str | None]
    identified_agents: NotRequired[str | None]


class FlowUpdate(TypedDict, total=False):
    """
    Payload for updating an existing flow log.

    All fields are optional - only provided fields will be updated.
    """
    user_request_summary: str | None
    identified_agents: str | None
