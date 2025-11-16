"""
Agent Flow DTOs

DTOs for agent workflow/flow requests and responses.
These are used for invoking LangGraph workflows.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AgentFlowRequestDTO(BaseModel):
    """
    DTO for invoking agent flows (LangGraph workflows).

    This is used to pass user input and session context to agent workflows
    with checkpointing/resumption support.
    """
    user_input: str = Field(
        ...,
        description="User's natural language input/request"
    )
    agent_type: str = Field(
        ...,
        description="Type of agent to invoke (e.g., 'finance', 'quotation')"
    )
    session_id: str = Field(
        ...,
        description="Session ID for checkpointing and conversation resumption"
    )


class FinanceAgentFlowRequestDTO(AgentFlowRequestDTO):
    """
    Specialized DTO for finance agent flow requests.

    Inherits from AgentFlowRequestDTO with agent_type pre-set to 'finance'.
    """
    agent_type: str = Field(
        default="finance",
        description="Agent type (fixed to 'finance')"
    )


# Backward compatibility alias
# TODO: Deprecate this in favor of AgentFlowRequestDTO
RequestBody = AgentFlowRequestDTO
