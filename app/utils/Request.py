from pydantic import BaseModel

class RequestBody(BaseModel):
    user_input: str
    agent_type: str
    session_id: str  # Required for checkpointing/resumption