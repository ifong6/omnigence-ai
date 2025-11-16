"""
Models Package

Exports all SQLModel database models, DTOs, and enums for the application.
Following clean import pattern for easy usage.
"""

# Enums
from app.models.enums import UnitType, QuotationStatus, DBTable

# Company Models
from app.models.company_models import (
    Company,
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyRow,
)

# Job Models
from app.models.job_models import (
    DesignJob,
    InspectionJob,
    JobBase,
    JobCreate,
    JobUpdate,
    JobRow,
)

# Quotation Models
from app.models.quotation_models import (
    Quotation,
    QuotationItem,
    QuotationBase,
    QuotationItemBase,
    QuotationCreate,
    QuotationUpdate,
    QuotationRow,
    QuotationItemCreate,
    QuotationItemUpdate,
    QuotationItemRow,
)

# Invoice Models
from app.models.invoice_models import (
    Invoice,
    InvoiceItem,
    PaymentRecord,
    InvoiceBase,
    InvoiceItemBase,
    PaymentRecordBase,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceRow,
    InvoiceItemCreate,
    InvoiceItemUpdate,
    InvoiceItemRow,
    PaymentRecordCreate,
    PaymentRecordUpdate,
    PaymentRecordRow,
)

# Flow Models (DB table)
from app.models.flow_models import (
    Flow,
    FlowRow,
)

# Flow Schemas (LangGraph payloads - re-exported from schemas package)
from app.schemas.flow_schema import (
    FlowBase,
    FlowCreate,
)

__all__ = [
    # Enums
    "UnitType",
    "QuotationStatus",
    "DBTable",
    # Company
    "Company",
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyRow",
    # Jobs
    "DesignJob",
    "InspectionJob",
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobRow",
    # Quotations
    "Quotation",
    "QuotationItem",
    "QuotationBase",
    "QuotationItemBase",
    "QuotationCreate",
    "QuotationUpdate",
    "QuotationRow",
    "QuotationItemCreate",
    "QuotationItemUpdate",
    "QuotationItemRow",
    # Invoices
    "Invoice",
    "InvoiceItem",
    "PaymentRecord",
    "InvoiceBase",
    "InvoiceItemBase",
    "PaymentRecordBase",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceRow",
    "InvoiceItemCreate",
    "InvoiceItemUpdate",
    "InvoiceItemRow",
    "PaymentRecordCreate",
    "PaymentRecordUpdate",
    "PaymentRecordRow",
    # Flow (append-only audit log)
    "Flow",
    "FlowBase",
    "FlowCreate",
    "FlowRow",
]
