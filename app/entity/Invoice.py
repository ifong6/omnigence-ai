from typing import List, Optional
from pydantic import BaseModel
from app.entity.Client import Client
from app.entity.InvoiceItem import InvoiceItem

class Invoice(BaseModel):
    """
    Invoice entity representing an invoice document.

    Invoices are typically generated after work is completed based on quotations and jobs.
    They contain billing information sent to clients for payment.
    """
    invoice_id: Optional[str] = ""
    client: Client
    project_name: Optional[str] = ""
    job_no: Optional[str] = ""  # Link to the original job
    quotation_no: Optional[str] = ""  # Link to the original quotation (if applicable)
    no: Optional[str] = ""  # Invoice number (e.g., INV-JCP-25-01-1)
    date: Optional[str] = ""  # Invoice issue date
    invoiceItems: List[InvoiceItem] = None
    total_amount: Optional[str] = ""
    currency: Optional[str] = "MOP"
    status: Optional[str] = "pending"  # pending, paid, overdue, cancelled
    due_date: Optional[str] = ""  # Payment due date
    notes: Optional[str] = ""  # Additional notes or remarks
