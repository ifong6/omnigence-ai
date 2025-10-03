from pydantic import BaseModel
from typing import Optional

class QuoteIdResponse(BaseModel):
    success: bool
    latest_quote_id: Optional[str] = None
    error: Optional[str] = None        