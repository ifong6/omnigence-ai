# =============================================================
# MODULE PURPOSE:
#   ✅ Define the universal AgentResponse contract for ALL agents.
#   🧑‍💻 Developer use: Enforces consistent type-safety.
#   👩‍🦰 Human user: Not directly seen — only the "message" field surfaces.
#   🧩 Data handling: Base model for logging and aggregation.
# =============================================================

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Status of agent response"""
    SUCCESS = "success"  # ✅ Agent completed task successfully
    ERROR = "error"      # ❌ Agent failed with error
    PARTIAL = "partial"  # ⚠️ Agent returned something, but uncertain/incomplete
    EMPTY = "empty"      # ⭕ No response at all


class AgentResponse(BaseModel):
    """Universal contract for agent responses (v1.0)

    All agents should eventually return this standardized format.
    For now, legacy_adapter.py converts old formats to this contract.
    """

    # Identity
    agent_name: str = Field(description="Name of the agent that generated this response")

    # Core fields
    status: ResponseStatus = Field(description="Status of the agent operation")
    message: str = Field(description="Human-facing message for display")

    # Optional structured data
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Original/structured data from the agent"
    )

    # Diagnostics
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal warnings from agent execution"
    )
    error_details: Optional[str] = Field(
        default=None,
        description="Detailed error information if status is ERROR"
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
