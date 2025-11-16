from pydantic import BaseModel, Field
from typing import Optional, List, Any
from decimal import Decimal
from datetime import date

class QuotationItemInput(BaseModel):
    """
    Schema for a single quotation item in the generation flow.
    """
    project_item_description: str = Field(..., description="Item description")
    quantity: float = Field(..., gt=0, description="Quantity")
    unit: str = Field(..., description="Unit type (e.g., '項', 'pcs', 'set')")
    sub_amount: Decimal = Field(..., description="Sub amount (unit price * quantity)")
    total_amount: Decimal = Field(..., description="Total amount")


class QuotationGenerationInput(BaseModel):
    """
    Input schema for quotation generation flow.

    This schema defines the required data to generate a quotation,
    including job details, client information, and line items.
    """
    job_no: str = Field(..., description="Job number (e.g., 'Q-JCP-25-01-1')")
    company_id: int = Field(..., description="Company/Client ID")
    project_name: str = Field(..., description="Project name")
    currency: str = Field(default="MOP", description="Currency code")
    items: List[QuotationItemInput] = Field(..., min_length=1, description="List of quotation items")
    date_issued: Optional[date] = Field(None, description="Issue date (defaults to today)")
    revision_no: str = Field(default="00", description="Revision number (00=no revision, 01/02/etc=revision)")
    valid_until: Optional[date] = Field(None, description="Valid until date")
    notes: Optional[str] = Field(None, description="Notes/remarks")


class QuotationGenerationOutput(BaseModel):
    """
    Output schema for quotation generation flow.

    This schema represents the result of a successful quotation generation,
    including the generated quotation number, total amount, and metadata.
    """
    quo_no: str = Field(..., description="Generated quotation number")
    total: Decimal = Field(..., description="Total quotation amount")
    item_count: int = Field(..., description="Number of line items")
    status: str = Field(default="DRAFTED", description="Quotation status")
    message: Optional[str] = Field(None, description="Success or info message")
    quotation_ids: Optional[List[int]] = Field(None, description="List of created quotation record IDs")


class QuotationUpdateInput(BaseModel):
    """
    Input schema for quotation update operations in the flow.
    """
    quotation_ids: List[int] = Field(..., min_length=1, description="List of quotation IDs to update")
    status: Optional[str] = Field(None, description="New status")
    notes: Optional[str] = Field(None, description="New notes")
    valid_until: Optional[date] = Field(None, description="New valid until date")


class QuotationQueryInput(BaseModel):
    """
    Input schema for querying quotations in the flow.
    """
    quo_no: Optional[str] = Field(None, description="Quotation number")
    job_no: Optional[str] = Field(None, description="Job number pattern")
    company_id: Optional[int] = Field(None, description="Company ID")
    project_name: Optional[str] = Field(None, description="Project name pattern")
    limit: Optional[int] = Field(10, gt=0, le=100, description="Maximum results")


class QuotationFlowResponse(BaseModel):
    """
    Generic response schema for quotation flow operations.

    Used to wrap responses from various quotation-related nodes
    with consistent structure including success status and errors.
    """
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Any] = Field(None, description="Response data (varies by operation)")
    error: Optional[str] = Field(None, description="Error message if failed")
    operation: str = Field(..., description="Operation type (e.g., 'create', 'update', 'query')")
