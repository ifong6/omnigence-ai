from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import UnitType, QuotationStatus

# ============================================================================
# OUTPUT DTOs (Response Models)
# ============================================================================

class QuotationItemDTO(BaseModel):
    """
    DTO for quotation line item.

    Represents a single line item in a quotation.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="Item ID")
    quotation_id: Optional[int] = Field(None, description="Parent quotation ID")
    item_desc: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity", gt=0)
    unit: UnitType = Field(default=UnitType.Lot, description="Unit of measurement")
    unit_price: Decimal = Field(..., description="Unit price", ge=0)
    amount: Decimal = Field(..., description="Total amount (quantity × unit_price)")


class QuotationDTO(BaseModel):
    """
    DTO for quotation header.

    This represents the quotation metadata without line items.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="Quotation ID")
    quo_no: str = Field(..., description="Quotation number (e.g., Q-JCP-25-01-q1-R00)")
    client_id: int = Field(..., description="Client/Company ID")
    project_name: str = Field(..., description="Project name")
    date_issued: date = Field(..., description="Quotation issue date")
    status: QuotationStatus = Field(default=QuotationStatus.DRAFTED, description="Quotation status")
    currency: str = Field(default="MOP", description="Currency code (e.g., MOP, HKD, USD)")
    revision_no: int = Field(default=0, description="Revision number", ge=0)
    valid_until: Optional[date] = Field(None, description="Quotation validity end date")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class QuotationWithItemsDTO(QuotationDTO):
    """
    DTO for quotation with all line items.

    Extends QuotationDTO with the full list of items.
    """
    items: List[QuotationItemDTO] = Field(default_factory=list, description="List of quotation items")

    @property
    def total_amount(self) -> Decimal:
        return sum(
            ( (item.amount or Decimal("0")) for item in self.items ),
            Decimal("0")
        )

class QuotationWithClientDTO(QuotationDTO):
    """
    DTO for quotation with client information.

    Extends QuotationDTO with client/company details from JOIN queries.
    """
    client_name: str = Field(..., description="Client/Company name")
    client_address: Optional[str] = Field(None, description="Client address")
    client_phone: Optional[str] = Field(None, description="Client phone")


class QuotationListResponseDTO(BaseModel):
    """
    DTO for paginated quotation list responses.

    This wraps a list of quotations with metadata.
    """
    quotations: List[QuotationWithClientDTO] = Field(..., description="List of quotations")
    total_count: int = Field(..., description="Total number of quotations")
    limit: Optional[int] = Field(None, description="Applied limit")


class QuotationSearchResponseDTO(BaseModel):
    """
    DTO for quotation search/list results.

    Simple wrapper for quotation results with count.
    """
    quotations: List[QuotationDTO] = Field(..., description="List of quotations")
    count: int = Field(..., description="Number of results returned")


class QuotationCreateResponseDTO(BaseModel):
    """
    DTO for quotation creation response.

    Contains the created quotations with summary info.
    """
    quotations: List[QuotationDTO] = Field(..., description="Created quotation records")
    quo_no: str = Field(..., description="Generated quotation number")
    total: float = Field(..., description="Total amount")
    item_count: int = Field(..., description="Number of items created")


# ============================================================================
# INPUT DTOs (Request Models)
# ============================================================================

class CreateQuotationItemDTO(BaseModel):
    """
    DTO for creating a quotation item.

    Used when creating a quotation with items.
    """
    item_desc: str = Field(..., description="Item description", min_length=1, max_length=500)
    quantity: int = Field(..., description="Quantity", gt=0)
    unit: UnitType = Field(default=UnitType.Lot, description="Unit of measurement")
    unit_price: Decimal = Field(..., description="Unit price", ge=0)


class CreateQuotationDTO(BaseModel):
    """
    DTO for quotation creation requests.

    This validates input data before it reaches the service layer.
    """
    job_no: str = Field(..., description="Associated job number", min_length=1)
    company_id: int = Field(..., description="Client/Company ID", gt=0)
    project_name: str = Field(..., description="Project name", min_length=1, max_length=500)
    currency: str = Field(default="MOP", description="Currency code", min_length=3, max_length=3)
    items: List[CreateQuotationItemDTO] = Field(..., description="List of quotation items", min_length=1)
    date_issued: Optional[date] = Field(None, description="Issue date (defaults to today)")
    revision_no: str = Field(default="00", description="Revision number (00=no revision, 01/02/etc=revision)")
    valid_until: Optional[date] = Field(None, description="Validity end date")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)


class UpdateQuotationDTO(BaseModel):
    """
    DTO for quotation update requests.

    All fields are optional (only provided fields will be updated).
    """
    status: Optional[QuotationStatus] = Field(None, description="New status")
    date_issued: Optional[date] = Field(None, description="New issue date")
    valid_until: Optional[date] = Field(None, description="New validity date")
    notes: Optional[str] = Field(None, description="Updated notes", max_length=1000)
    currency: Optional[str] = Field(None, description="Currency code", min_length=3, max_length=3)


class UpdateQuotationItemDTO(BaseModel):
    """
    DTO for quotation item update requests.

    All fields are optional.
    """
    item_desc: Optional[str] = Field(None, description="Item description", min_length=1, max_length=500)
    quantity: Optional[int] = Field(None, description="Quantity", gt=0)
    unit: Optional[UnitType] = Field(None, description="Unit of measurement")
    unit_price: Optional[Decimal] = Field(None, description="Unit price", ge=0)


# ============================================================================
# OPERATION RESULT DTOs
# ============================================================================

class QuotationCreatedResponseDTO(BaseModel):
    """
    DTO for quotation creation response.

    Returns the created quotation with items and additional metadata.
    """
    quotation: QuotationWithItemsDTO = Field(..., description="Created quotation with items")
    message: str = Field(default="Quotation created successfully", description="Success message")


class QuotationUpdatedResponseDTO(BaseModel):
    """
    DTO for quotation update response.
    """
    quotation: QuotationDTO = Field(..., description="Updated quotation details")
    message: str = Field(default="Quotation updated successfully", description="Success message")
    fields_updated: List[str] = Field(default_factory=list, description="List of updated fields")


class QuotationNotFoundDTO(BaseModel):
    """
    DTO for quotation not found error.
    """
    error: str = Field(default="Quotation not found", description="Error message")
    quo_no: Optional[str] = Field(None, description="Quotation number that was not found")
    quotation_id: Optional[int] = Field(None, description="Quotation ID that was not found")


class QuotationSummaryDTO(BaseModel):
    """
    DTO for quotation summary (without full details).

    Useful for list views and dashboards.
    """
    id: int = Field(..., description="Quotation ID")
    quo_no: str = Field(..., description="Quotation number")
    client_name: str = Field(..., description="Client name")
    project_name: str = Field(..., description="Project name")
    date_issued: date = Field(..., description="Issue date")
    status: QuotationStatus = Field(..., description="Status")
    total_amount: Decimal = Field(..., description="Total amount")
    currency: str = Field(..., description="Currency")
    revision_no: int = Field(..., description="Revision number")


# ============================================================================
# SEARCH/FILTER DTOs
# ============================================================================

class QuotationSearchDTO(BaseModel):
    """
    DTO for quotation search/filter criteria.
    """
    client_id: Optional[int] = Field(None, description="Filter by client ID")
    project_name: Optional[str] = Field(None, description="Filter by project name (partial match)")
    job_no: Optional[str] = Field(None, description="Filter by job number")
    status: Optional[QuotationStatus] = Field(None, description="Filter by status")
    date_from: Optional[date] = Field(None, description="Filter by issue date (from)")
    date_to: Optional[date] = Field(None, description="Filter by issue date (to)")
    limit: Optional[int] = Field(default=10, description="Max results to return", gt=0, le=100)
    offset: Optional[int] = Field(default=0, description="Offset for pagination", ge=0)


# ============================================================================
# EXAMPLE USAGE IN DOCSTRINGS
# ============================================================================

"""
EXAMPLE USAGE:
--------------

# Create a quotation with items
create_dto = CreateQuotationDTO(
    job_no="JCP-25-01-1",
    company_id=15,
    project_name="空調系統設計",
    currency="MOP",
    items=[
        CreateQuotationItemDTO(
            item_desc="空調系統設計費用",
            quantity=1,
            unit=UnitType.Lot,
            unit_price=Decimal("50000.00")
        ),
        CreateQuotationItemDTO(
            item_desc="現場勘察費用",
            quantity=2,
            unit=UnitType.day,
            unit_price=Decimal("5000.00")
        )
    ]
)

# Service processes and returns typed response
response: QuotationCreatedResponseDTO = service.create_quotation(create_dto)
quotation: QuotationWithItemsDTO = response.quotation

# Access quotation details with full type safety
print(f"Quotation: {quotation.quo_no}")
print(f"Total: {quotation.total_amount} {quotation.currency}")
print(f"Items: {quotation.item_count}")

# Update quotation status
update_dto = UpdateQuotationDTO(status=QuotationStatus.SENT)
response = service.update_quotation(quotation.id, update_dto)

# Search quotations
search_dto = QuotationSearchDTO(
    status=QuotationStatus.DRAFTED,
    date_from=date(2025, 1, 1),
    limit=20
)
results = service.search_quotations(search_dto)
"""
