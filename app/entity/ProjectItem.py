from typing import Optional
from pydantic import BaseModel, Field

class ProjectItem(BaseModel):
    no: str = Field(pattern=r'^[1-9][0-9]?$')
    content: str
    quantity: str
    unit: str
    unit_price: str
    subtotal: Optional[str] = None

