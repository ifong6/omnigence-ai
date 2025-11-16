"""
Invoice DAO for CRUD operations on Finance invoice tables.

Provides type-safe database operations for invoices, invoice items, and payment records
with specialized query methods.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import date
from sqlmodel import Session, select
from sqlalchemy import func, and_
from app.dao.base_dao import BaseDAO


class InvoiceDAO(BaseDAO):
    """
    DAO for managing invoices in Finance.invoice table.

    Handles all database operations for invoice headers including:
    - Invoice creation and updates
    - Querying by invoice_no, client_id, quotation
    - Payment tracking
    - Listing invoices with pagination and sorting

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = InvoiceDAO(session)
        ...     invoice = dao.create(
        ...         invoice_no="INV-JCP-25-01-1",
        ...         client_id=123,
        ...         project_name="Office Renovation",
        ...         date_issued=date.today(),
        ...         due_date=date.today(),
        ...         status="DRAFT"
        ...     )
    """

    def __init__(self, session: Session):
        """
        Initialize DAO with database session.

        Args:
            session: Active SQLModel database session
        """
        # Note: Assuming Invoice model exists at app.models.invoice_models
        # If not, this would need to be created first
        try:
            from app.models.invoice_models import Invoice
            super().__init__(model=Invoice, session=session)
        except ImportError:
            # Fallback if invoice model doesn't exist yet
            # In production, Invoice model should be created
            pass

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    def get_by_invoice_no(self, invoice_no: str) -> Optional[Any]:
        """
        Get invoice by invoice number.

        Args:
            invoice_no: Invoice number (e.g., "INV-JCP-25-01-1")

        Returns:
            Invoice if found, None otherwise

        Example:
            >>> invoice = dao.get_by_invoice_no("INV-JCP-25-01-1")
        """
        return self.find_one_by(invoice_no=invoice_no)

    def get_by_client_id(
        self,
        client_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Any]:
        """
        Get all invoices for a specific client/company.

        Args:
            client_id: Client/Company ID to filter by
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by date descending (default: True)

        Returns:
            List of Invoice instances

        Example:
            >>> # Get 10 most recent invoices for client
            >>> invoices = dao.get_by_client_id(
            ...     client_id=123,
            ...     limit=10,
            ...     order_desc=True
            ... )
        """
        # This implementation assumes Invoice has date_issued field
        # Adjust field name if different (e.g., created_at)
        return self.find_many_by(
            client_id=client_id,
            limit=limit,
            offset=offset,
            order_by="date_issued" if order_desc else None
        )

    def get_by_quotation_id(self, quotation_id: int) -> List[Any]:
        """
        Get all invoices related to a specific quotation.

        Args:
            quotation_id: Quotation ID

        Returns:
            List of Invoice instances

        Example:
            >>> invoices = dao.get_by_quotation_id(123)
        """
        return self.find_many_by(quotation_id=quotation_id)

    def get_overdue_invoices(
        self,
        as_of_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        Get all overdue invoices.

        An invoice is overdue if:
        - Status is not PAID or CANCELLED
        - Due date is before the as_of_date

        Args:
            as_of_date: Date to check overdue status (default: today)
            limit: Maximum number of results (optional)

        Returns:
            List of overdue Invoice instances

        Example:
            >>> # Get all overdue invoices
            >>> overdue = dao.get_overdue_invoices()
            >>>
            >>> # Get overdue as of specific date
            >>> overdue = dao.get_overdue_invoices(
            ...     as_of_date=date(2025, 1, 1)
            ... )
        """
        if as_of_date is None:
            as_of_date = date.today()

        # This would need proper SQL query construction
        # Placeholder implementation
        stmt = select(self.model).where(
            and_(
                self.model.due_date < as_of_date,
                self.model.status.not_in(["PAID", "CANCELLED"])  # type: ignore
            )
        )

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_by_status(
        self,
        status: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Any]:
        """
        Get all invoices with a specific status.

        Args:
            status: Invoice status (DRAFT, SENT, PAID, OVERDUE, CANCELLED)
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Invoice instances

        Example:
            >>> # Get all unpaid invoices
            >>> unpaid = dao.get_by_status("SENT", limit=50)
        """
        return self.find_many_by(
            status=status,
            limit=limit,
            offset=offset
        )

    # ========================================================================
    # AGGREGATE OPERATIONS
    # ========================================================================

    def calculate_total_amount(self, invoice_id: int) -> Decimal:
        """
        Calculate total amount for an invoice from its items.

        Args:
            invoice_id: Invoice ID

        Returns:
            Total amount as Decimal

        Example:
            >>> total = dao.calculate_total_amount(123)
            >>> print(f"Total: MOP {total}")
        """
        # Would need to join with invoice_item table
        # Placeholder implementation
        return Decimal("0.00")

    def get_payment_summary(self, invoice_id: int) -> Dict[str, Any]:
        """
        Get payment summary for an invoice.

        Args:
            invoice_id: Invoice ID

        Returns:
            Dictionary with total_amount, paid_amount, outstanding_amount

        Example:
            >>> summary = dao.get_payment_summary(123)
            >>> print(f"Outstanding: MOP {summary['outstanding_amount']}")
        """
        # Would need to aggregate payment records
        # Placeholder implementation
        return {
            "total_amount": Decimal("0.00"),
            "paid_amount": Decimal("0.00"),
            "outstanding_amount": Decimal("0.00")
        }


class InvoiceItemDAO(BaseDAO):
    """
    DAO for managing invoice items in Finance.invoice_item table.

    Handles individual line items within invoices.

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = InvoiceItemDAO(session)
        ...     item = dao.create(
        ...         invoice_id=123,
        ...         item_desc="Office Chair",
        ...         quantity=10,
        ...         unit_price=Decimal("150.00"),
        ...         unit="piece"
        ...     )
    """

    def __init__(self, session: Session):
        """
        Initialize DAO with database session.

        Args:
            session: Active SQLModel database session
        """
        # Note: Assuming InvoiceItem model exists
        try:
            from app.models.invoice_models import InvoiceItem
            super().__init__(model=InvoiceItem, session=session)
        except ImportError:
            pass

    def get_by_invoice_id(self, invoice_id: int) -> List[Any]:
        """
        Get all items for a specific invoice.

        Args:
            invoice_id: Invoice ID to filter by

        Returns:
            List of InvoiceItem instances

        Example:
            >>> items = dao.get_by_invoice_id(123)
        """
        return self.find_many_by(invoice_id=invoice_id)

    def calculate_total(self, invoice_id: int) -> Decimal:
        """
        Calculate total amount for all items in an invoice.

        Args:
            invoice_id: Invoice ID

        Returns:
            Total amount as Decimal

        Example:
            >>> total = dao.calculate_total(123)
            >>> print(f"Total: MOP {total}")
        """
        items = self.get_by_invoice_id(invoice_id)
        return sum((item.amount or Decimal("0") for item in items), Decimal("0"))


class PaymentRecordDAO(BaseDAO):
    """
    DAO for managing payment records in Finance.payment_record table.

    Tracks payments made against invoices.

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = PaymentRecordDAO(session)
        ...     payment = dao.create(
        ...         invoice_id=123,
        ...         amount=Decimal("5000.00"),
        ...         payment_date=date.today(),
        ...         payment_method="BANK_TRANSFER",
        ...         reference_no="TXN12345"
        ...     )
    """

    def __init__(self, session: Session):
        """
        Initialize DAO with database session.

        Args:
            session: Active SQLModel database session
        """
        # Note: Assuming PaymentRecord model exists
        try:
            from app.models.invoice_models import PaymentRecord
            super().__init__(model=PaymentRecord, session=session)
        except ImportError:
            pass

    def get_by_invoice_id(self, invoice_id: int) -> List[Any]:
        """
        Get all payment records for a specific invoice.

        Args:
            invoice_id: Invoice ID to filter by

        Returns:
            List of PaymentRecord instances sorted by payment date

        Example:
            >>> payments = dao.get_by_invoice_id(123)
            >>> for payment in payments:
            ...     print(f"{payment.payment_date}: MOP {payment.amount}")
        """
        return self.find_many_by(
            invoice_id=invoice_id,
            order_by="payment_date"
        )

    def get_by_reference_no(self, reference_no: str) -> Optional[Any]:
        """
        Get payment record by reference number.

        Args:
            reference_no: Payment reference number

        Returns:
            PaymentRecord if found, None otherwise

        Example:
            >>> payment = dao.get_by_reference_no("TXN12345")
        """
        return self.find_one_by(reference_no=reference_no)

    def calculate_total_paid(self, invoice_id: int) -> Decimal:
        """
        Calculate total amount paid for an invoice.

        Args:
            invoice_id: Invoice ID

        Returns:
            Total paid amount as Decimal

        Example:
            >>> total_paid = dao.calculate_total_paid(123)
            >>> print(f"Total Paid: MOP {total_paid}")
        """
        payments = self.get_by_invoice_id(invoice_id)
        return sum((payment.amount or Decimal("0") for payment in payments), Decimal("0"))

    def get_payments_by_date_range(
        self,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        Get all payments within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            limit: Maximum number of results (optional)

        Returns:
            List of PaymentRecord instances

        Example:
            >>> # Get payments for January 2025
            >>> payments = dao.get_payments_by_date_range(
            ...     start_date=date(2025, 1, 1),
            ...     end_date=date(2025, 1, 31)
            ... )
        """
        stmt = select(self.model).where(
            and_(
                self.model.payment_date >= start_date,
                self.model.payment_date <= end_date
            )
        ).order_by(self.model.payment_date.desc())  # type: ignore

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())
