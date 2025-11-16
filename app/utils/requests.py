from abc import ABC
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

class Request(BaseModel, ABC):
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Request timestamp"
    )

class UserRequest(Request):
    message: str = Field(..., description="User's input message")

class HumanInTheLoopRequest(Request):
    message: str = Field(..., description="User's feedback message")
    session_id: str = Field(..., description="Session identifier")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Request timestamp"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="provided metadata for the request as correction, clarification or feedback"
    )
