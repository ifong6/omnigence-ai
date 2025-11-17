from typing import Optional
from pydantic import BaseModel, Field

class InvoiceItem(BaseModel):
    """
    InvoiceItem entity representing a line item in an invoice.

    Each invoice item represents a billable service or product with pricing details.
    """
    no: str = Field(pattern=r'^[1-9][0-9]?$')  # Item number (1-99)
    content: str  # Description of the service/product
    quantity: str  # Quantity (amount)
    unit: str  # Unit of measurement (e.g., "Lot", "件", "套", "m", "m²", "hr")
    unit_price: str  # Price per unit
    subtotal: Optional[str] = None  # Calculated: quantity * unit_price
