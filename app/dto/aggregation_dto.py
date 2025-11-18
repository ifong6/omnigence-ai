from typing import Any, Dict, Literal, List
from pydantic import BaseModel, Field

class AggregationResponseDTO(BaseModel):
    message: str
    status: Literal["success", "partial", "error", "empty"]
    agent_responses: Dict[str, Any] = Field(default_factory=dict)
    session_id: str
    flow_uuid: str
    identified_agents: List[str] = Field(default_factory=list)
