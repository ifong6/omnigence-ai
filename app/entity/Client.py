from pydantic import BaseModel
from typing import Optional

class Client(BaseModel):
    name: Optional[str] = ""
    address: Optional[str] = ""