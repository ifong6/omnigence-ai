from pydantic import BaseModel

class UserRequest(BaseModel):
    message: str
    session_id: str