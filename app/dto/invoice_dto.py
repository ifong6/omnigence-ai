from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class UnitType(str, Enum):
    """Unit types for invoice items - matches Finance.unit_type enum"""
    Lot = "Lot"
    m2 = "m²"
    m3 = "m³"
    piece = "piece"
    set = "set"
    hour = "hour"
    day = "day"


class InvoiceStatus(str, Enum):
    """Invoice status values"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    VOID = "VOID"


class PaymentStatus(str, Enum):
    """Payment status for invoice"""
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    FULLY_PAID = "FULLY_PAID"


class PaymentMethod(str, Enum):
    """Payment methods"""
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"
    CHECK = "CHECK"
    CREDIT_CARD = "CREDIT_CARD"
    OTHER = "OTHER"


# ============================================================================
# OUTPUT DTOs (Response Models)
# ============================================================================

class InvoiceItemDTO(BaseModel):
    """
    DTO for invoice line item.

    Represents a single line item in an invoice.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="Item ID")
    invoice_id: Optional[int] = Field(None, description="Parent invoice ID")
    item_desc: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity", gt=0)
    unit: UnitType = Field(default=UnitType.Lot, description="Unit of measurement")
    unit_price: Decimal = Field(..., description="Unit price", ge=0)
    amount: Optional[Decimal] = Field(None, description="Total amount (quantity × unit_price)")
    tax_rate: Optional[Decimal] = Field(None, description="Tax rate (e.g., 0.05 for 5%)", ge=0, le=1)
    tax_amount: Optional[Decimal] = Field(None, description="Tax amount")


class PaymentRecordDTO(BaseModel):
    """
    DTO for payment record.

    Tracks individual payments made against an invoice.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="Payment record ID")
    invoice_id: int = Field(..., description="Associated invoice ID")
    payment_date: date = Field(..., description="Payment date")
    amount: Decimal = Field(..., description="Payment amount", gt=0)
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference_no: Optional[str] = Field(None, description="Payment reference number")
    notes: Optional[str] = Field(None, description="Payment notes")
    created_at: Optional[datetime] = Field(None, description="Record creation timestamp")


class InvoiceDTO(BaseModel):
    """
    DTO for invoice header.

    This represents the invoice metadata without line items.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="Invoice ID")
    invoice_no: str = Field(..., description="Invoice number (e.g., INV-JCP-25-01-001)")
    quotation_id: Optional[int] = Field(None, description="Related quotation ID")
    client_id: int = Field(..., description="Client/Company ID")
    project_name: str = Field(..., description="Project name")
    date_issued: date = Field(..., description="Invoice issue date")
    due_date: date = Field(..., description="Payment due date")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Invoice status")
    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID, description="Payment status")
    currency: str = Field(default="MOP", description="Currency code (e.g., MOP, HKD, USD)")
    subtotal: Decimal = Field(..., description="Subtotal before tax", ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), description="Total tax amount", ge=0)
    total_amount: Decimal = Field(..., description="Total amount including tax", ge=0)
    amount_paid: Decimal = Field(default=Decimal("0.00"), description="Amount paid so far", ge=0)
    amount_due: Decimal = Field(..., description="Amount still due", ge=0)
    notes: Optional[str] = Field(None, description="Invoice notes")
    payment_terms: Optional[str] = Field(None, description="Payment terms (e.g., 'Net 30')")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class InvoiceWithItemsDTO(InvoiceDTO):
    """
    DTO for invoice with all line items.

    Extends InvoiceDTO with the full list of items.
    """
    items: list[InvoiceItemDTO] = Field(default_factory=list, description="List of invoice items")

    @property
    def item_count(self) -> int:
        """Get number of items."""
        return len(self.items)

    @property
    def is_fully_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.amount_paid >= self.total_amount

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        from datetime import date as date_module
        return self.due_date < date_module.today() and not self.is_fully_paid


class InvoiceWithClientDTO(InvoiceDTO):
    """
    DTO for invoice with client information.

    Extends InvoiceDTO with client/company details from JOIN queries.
    """
    client_name: str = Field(..., description="Client/Company name")
    client_address: Optional[str] = Field(None, description="Client address")
    client_phone: Optional[str] = Field(None, description="Client phone")


class InvoiceWithPaymentsDTO(InvoiceWithItemsDTO):
    """
    DTO for invoice with items and payment history.

    Complete invoice view including all line items and payment records.
    """
    payments: list[PaymentRecordDTO] = Field(default_factory=list, description="Payment history")

    @property
    def payment_count(self) -> int:
        """Get number of payment records."""
        return len(self.payments)


class InvoiceListResponseDTO(BaseModel):
    """
    DTO for paginated invoice list responses.

    This wraps a list of invoices with metadata.
    """
    invoices: list[InvoiceWithClientDTO] = Field(..., description="List of invoices")
    total_count: int = Field(..., description="Total number of invoices")
    limit: Optional[int] = Field(None, description="Applied limit")


# ============================================================================
# INPUT DTOs (Request Models)
# ============================================================================

class CreateInvoiceItemDTO(BaseModel):
    """
    DTO for creating an invoice item.

    Used when creating an invoice with items.
    """
    item_desc: str = Field(..., description="Item description", min_length=1, max_length=500)
    quantity: int = Field(..., description="Quantity", gt=0)
    unit: UnitType = Field(default=UnitType.Lot, description="Unit of measurement")
    unit_price: Decimal = Field(..., description="Unit price", ge=0)
    tax_rate: Optional[Decimal] = Field(None, description="Tax rate (e.g., 0.05 for 5%)", ge=0, le=1)


class CreateInvoiceDTO(BaseModel):
    """
    DTO for invoice creation requests.

    This validates input data before it reaches the service layer.
    """
    quotation_id: Optional[int] = Field(None, description="Related quotation ID")
    company_id: int = Field(..., description="Client/Company ID", gt=0)
    project_name: str = Field(..., description="Project name", min_length=1, max_length=500)
    currency: str = Field(default="MOP", description="Currency code", min_length=3, max_length=3)
    items: list[CreateInvoiceItemDTO] = Field(..., description="List of invoice items", min_length=1)
    date_issued: Optional[date] = Field(None, description="Issue date (defaults to today)")
    due_date: date = Field(..., description="Payment due date")
    notes: Optional[str] = Field(None, description="Invoice notes", max_length=1000)
    payment_terms: Optional[str] = Field(None, description="Payment terms", max_length=200)


class CreateInvoiceFromQuotationDTO(BaseModel):
    """
    DTO for creating an invoice from an existing quotation.

    Simpler creation flow when converting a quotation to invoice.
    """
    quotation_id: int = Field(..., description="Quotation ID to convert", gt=0)
    due_date: date = Field(..., description="Payment due date")
    date_issued: Optional[date] = Field(None, description="Issue date (defaults to today)")
    notes: Optional[str] = Field(None, description="Invoice notes", max_length=1000)
    payment_terms: Optional[str] = Field(None, description="Payment terms", max_length=200)


class UpdateInvoiceDTO(BaseModel):
    """
    DTO for invoice update requests.

    All fields are optional (only provided fields will be updated).
    """
    status: Optional[InvoiceStatus] = Field(None, description="New status")
    payment_status: Optional[PaymentStatus] = Field(None, description="New payment status")
    date_issued: Optional[date] = Field(None, description="New issue date")
    due_date: Optional[date] = Field(None, description="New due date")
    notes: Optional[str] = Field(None, description="Updated notes", max_length=1000)
    payment_terms: Optional[str] = Field(None, description="Updated payment terms", max_length=200)


class RecordPaymentDTO(BaseModel):
    """
    DTO for recording a payment against an invoice.
    """
    invoice_id: int = Field(..., description="Invoice ID", gt=0)
    payment_date: date = Field(..., description="Payment date")
    amount: Decimal = Field(..., description="Payment amount", gt=0)
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference_no: Optional[str] = Field(None, description="Payment reference number", max_length=100)
    notes: Optional[str] = Field(None, description="Payment notes", max_length=500)


# ============================================================================
# OPERATION RESULT DTOs
# ============================================================================

class InvoiceCreatedResponseDTO(BaseModel):
    """
    DTO for invoice creation response.

    Returns the created invoice with items and additional metadata.
    """
    invoice: InvoiceWithItemsDTO = Field(..., description="Created invoice with items")
    message: str = Field(default="Invoice created successfully", description="Success message")


class InvoiceUpdatedResponseDTO(BaseModel):
    """
    DTO for invoice update response.
    """
    invoice: InvoiceDTO = Field(..., description="Updated invoice details")
    message: str = Field(default="Invoice updated successfully", description="Success message")
    fields_updated: list[str] = Field(default_factory=list, description="List of updated fields")


class PaymentRecordedResponseDTO(BaseModel):
    """
    DTO for payment recording response.
    """
    payment: PaymentRecordDTO = Field(..., description="Recorded payment")
    invoice: InvoiceDTO = Field(..., description="Updated invoice details")
    message: str = Field(default="Payment recorded successfully", description="Success message")


class InvoiceNotFoundDTO(BaseModel):
    """
    DTO for invoice not found error.
    """
    error: str = Field(default="Invoice not found", description="Error message")
    invoice_no: Optional[str] = Field(None, description="Invoice number that was not found")
    invoice_id: Optional[int] = Field(None, description="Invoice ID that was not found")


class InvoiceSummaryDTO(BaseModel):
    """
    DTO for invoice summary (without full details).

    Useful for list views and dashboards.
    """
    id: int = Field(..., description="Invoice ID")
    invoice_no: str = Field(..., description="Invoice number")
    client_name: str = Field(..., description="Client name")
    project_name: str = Field(..., description="Project name")
    date_issued: date = Field(..., description="Issue date")
    due_date: date = Field(..., description="Due date")
    status: InvoiceStatus = Field(..., description="Invoice status")
    payment_status: PaymentStatus = Field(..., description="Payment status")
    total_amount: Decimal = Field(..., description="Total amount")
    amount_paid: Decimal = Field(..., description="Amount paid")
    amount_due: Decimal = Field(..., description="Amount due")
    currency: str = Field(..., description="Currency")
    is_overdue: bool = Field(..., description="Whether invoice is overdue")


# ============================================================================
# SEARCH/FILTER DTOs
# ============================================================================

class InvoiceSearchDTO(BaseModel):
    """
    DTO for invoice search/filter criteria.
    """
    client_id: Optional[int] = Field(None, description="Filter by client ID")
    project_name: Optional[str] = Field(None, description="Filter by project name (partial match)")
    quotation_id: Optional[int] = Field(None, description="Filter by quotation ID")
    status: Optional[InvoiceStatus] = Field(None, description="Filter by status")
    payment_status: Optional[PaymentStatus] = Field(None, description="Filter by payment status")
    date_from: Optional[date] = Field(None, description="Filter by issue date (from)")
    date_to: Optional[date] = Field(None, description="Filter by issue date (to)")
    overdue_only: bool = Field(default=False, description="Show only overdue invoices")
    limit: Optional[int] = Field(default=10, description="Max results to return", gt=0, le=100)
    offset: Optional[int] = Field(default=0, description="Offset for pagination", ge=0)


# ============================================================================
# EXAMPLE USAGE IN DOCSTRINGS
# ============================================================================

"""
EXAMPLE USAGE:
--------------

# Create an invoice from scratch
create_dto = CreateInvoiceDTO(
    company_id=15,
    project_name="空調系統設計",
    currency="MOP",
    items=[
        CreateInvoiceItemDTO(
            item_desc="空調系統設計費用",
            quantity=1,
            unit=UnitType.Lot,
            unit_price=Decimal("50000.00"),
            tax_rate=Decimal("0.05")
        )
    ],
    due_date=date(2025, 12, 31),
    payment_terms="Net 30"
)

# Or create from an existing quotation
create_from_quo_dto = CreateInvoiceFromQuotationDTO(
    quotation_id=123,
    due_date=date(2025, 12, 31),
    payment_terms="Net 30"
)

# Service processes and returns typed response
response: InvoiceCreatedResponseDTO = service.create_invoice(create_dto)
invoice: InvoiceWithItemsDTO = response.invoice

# Record a payment
payment_dto = RecordPaymentDTO(
    invoice_id=invoice.id,
    payment_date=date.today(),
    amount=Decimal("25000.00"),
    payment_method=PaymentMethod.BANK_TRANSFER,
    reference_no="TXN-12345"
)
payment_response = service.record_payment(payment_dto)

# Search overdue invoices
search_dto = InvoiceSearchDTO(
    payment_status=PaymentStatus.UNPAID,
    overdue_only=True,
    limit=20
)
results = service.search_invoices(search_dto)
"""
