"""
Quotation DAO for CRUD operations on Finance.quotation table.

Provides type-safe database operations for quotation headers with specialized
query methods including filtering by client, project, and quotation number.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from sqlmodel import Session, select
from sqlalchemy import func
from app.dao.base_dao import BaseDAO
from app.models.quotation_models import Quotation, QuotationCreate, QuotationUpdate


def _payload_to_dict(payload: QuotationCreate | QuotationUpdate) -> Dict[str, Any]:
    """
    Convert SQLModel payload to dict, filtering out None values.

    Args:
        payload: QuotationCreate or QuotationUpdate instance

    Returns:
        Dictionary with non-None fields only
    """
    return payload.model_dump(exclude_none=True)


class QuotationDAO(BaseDAO[Quotation]):
    """
    DAO for managing quotations in Finance.quotation table.

    Handles all database operations for quotation headers including:
    - Quotation creation and updates
    - Querying by quo_no, client_id, project_name
    - Calculating totals and item counts
    - Listing quotations with pagination and sorting

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = QuotationDAO(session)
        ...     quotation = dao.create_quotation(QuotationCreate(
        ...         quo_no="Q-JCP-25-01-1",
        ...         client_id=123,
        ...         project_name="Office Renovation",
        ...         date_issued=date.today()
        ...     ))
    """

    def __init__(self, session: Session):
        """
        Initialize DAO with database session.

        Args:
            session: Active SQLModel database session
        """
        super().__init__(model=Quotation, session=session)

    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================

    def create_quotation(self, payload: QuotationCreate) -> Quotation:
        """
        Create a new quotation.

        Args:
            payload: Quotation creation data

        Returns:
            Created Quotation instance with auto-generated fields

        Example:
            >>> quotation = dao.create_quotation(QuotationCreate(
            ...     quo_no="Q-JCP-25-01-1",
            ...     client_id=123,
            ...     project_name="Office Design",
            ...     date_issued=date.today(),
            ...     currency="MOP"
            ... ))
        """
        data = _payload_to_dict(payload)
        return super().create(**data)

    def update_quotation(
        self, quotation_id: int, payload: QuotationUpdate
    ) -> Optional[Quotation]:
        """
        Update an existing quotation.

        Args:
            quotation_id: Quotation ID to update
            payload: Fields to update (only non-None values)

        Returns:
            Updated Quotation if found, None otherwise

        Example:
            >>> updated = dao.update_quotation(
            ...     quotation_id=123,
            ...     payload=QuotationUpdate(status="SENT")
            ... )
        """
        data = _payload_to_dict(payload)
        if not data:
            return None
        return super().update(quotation_id, **data)

    def get_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """
        Get quotation by ID.

        Args:
            quotation_id: Quotation ID

        Returns:
            Quotation if found, None otherwise
        """
        return super().get(quotation_id)

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    def get_by_quo_no(
        self, quo_no: str, *, limit: Optional[int] = None, offset: int = 0
    ) -> List[Quotation]:
        """
        Get quotations by quotation number.

        Note: Multiple quotations can share the same quo_no (revisions).

        Args:
            quo_no: Quotation number (e.g., "Q-JCP-25-01-1")
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Quotation instances

        Example:
            >>> quotations = dao.get_by_quo_no("Q-JCP-25-01-1")
        """
        stmt = (
            select(Quotation)
            .where(Quotation.quo_no == quo_no)
            .order_by(Quotation.id.asc())  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    def get_by_client_id(
        self,
        client_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Quotation]:
        """
        Get all quotations for a specific client/company.

        Args:
            client_id: Client/Company ID to filter by
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by date descending (default: True)

        Returns:
            List of Quotation instances

        Example:
            >>> # Get 10 most recent quotations for client
            >>> quotations = dao.get_by_client_id(
            ...     client_id=123,
            ...     limit=10,
            ...     order_desc=True
            ... )
        """
        stmt = select(Quotation).where(Quotation.client_id == client_id)

        # Sort by issue date
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore
        )

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_by_project_name(
        self,
        project_name: str,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Quotation]:
        """
        Get all quotations for a specific project.

        Args:
            project_name: Project name to filter by
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by date descending (default: True)

        Returns:
            List of Quotation instances

        Example:
            >>> quotations = dao.get_by_project_name(
            ...     project_name="Office Renovation",
            ...     limit=10
            ... )
        """
        stmt = select(Quotation).where(Quotation.project_name == project_name)

        # Sort by issue date
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore
        )

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_all(
        self, limit: Optional[int] = None, offset: int = 0, order_desc: bool = True
    ) -> List[Quotation]:
        """
        Get all quotations with pagination.

        Args:
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by date descending (default: True)

        Returns:
            List of all Quotation instances

        Example:
            >>> # Get first 20 quotations, newest first
            >>> quotations = dao.get_all(limit=20, order_desc=True)
        """
        stmt = select(Quotation)

        # Sort by issue date
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore
        )

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================

    def update_by_quo_no(
        self, quo_no: str, payload: QuotationUpdate
    ) -> List[Quotation]:
        """
        Update all quotations with the same quotation number.

        This is useful for updating all revisions of a quotation at once.

        Args:
            quo_no: Quotation number to filter by
            payload: Fields to update (only non-None values)

        Returns:
            List of updated Quotation instances

        Example:
            >>> # Mark all revisions as EXPIRED
            >>> updated = dao.update_by_quo_no(
            ...     quo_no="Q-JCP-25-01-1",
            ...     payload=QuotationUpdate(status="EXPIRED")
            ... )
        """
        data = _payload_to_dict(payload)
        if not data:
            return []

        quotations = self.get_by_quo_no(quo_no)

        for quotation in quotations:
            for key, value in data.items():
                setattr(quotation, key, value)

        self.session.flush()
        return quotations

    # ========================================================================
    # AGGREGATE OPERATIONS
    # ========================================================================

    def get_total_by_quo_no(self, quo_no: str) -> Dict[str, Any]:
        """
        Calculate total amount and item count for a quotation number.

        Note: This aggregates across all revisions with the same quo_no.

        Args:
            quo_no: Quotation number

        Returns:
            Dictionary with 'total' (Decimal) and 'item_count' (int)

        Example:
            >>> result = dao.get_total_by_quo_no("Q-JCP-25-01-1")
            >>> print(f"Total: {result['total']}, Items: {result['item_count']}")
        """
        # Note: This assumes there's a total_amount field or needs to be updated
        # based on your actual schema. If quotation items are separate, this
        # would need to join with quotation_item table.

        stmt = select(func.count(Quotation.id).label("item_count")).where(  # type: ignore
            Quotation.quo_no == quo_no
        )

        row = self.session.exec(stmt).first()

        if row:
            count = row or 0
            # For now, returning count only
            # Total calculation would need quotation items
            return {"total": Decimal("0"), "item_count": count}

        return {"total": Decimal("0"), "item_count": 0}


class QuotationItemDAO(BaseDAO):
    """
    DAO for managing quotation items in Finance.quotation_item table.

    This handles individual line items within quotations.

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = QuotationItemDAO(session)
        ...     item = dao.create(
        ...         quotation_id=123,
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
        from app.models.quotation_models import QuotationItem
        super().__init__(model=QuotationItem, session=session)

    def get_by_quotation_id(self, quotation_id: int) -> List:
        """
        Get all items for a specific quotation.

        Args:
            quotation_id: Quotation ID to filter by

        Returns:
            List of QuotationItem instances

        Example:
            >>> items = dao.get_by_quotation_id(123)
        """
        return self.find_many_by(quotation_id=quotation_id)

    def calculate_total(self, quotation_id: int) -> Decimal:
        """
        Calculate total amount for all items in a quotation.

        Args:
            quotation_id: Quotation ID

        Returns:
            Total amount as Decimal

        Example:
            >>> total = dao.calculate_total(123)
            >>> print(f"Total: MOP {total}")
        """
        items = self.get_by_quotation_id(quotation_id)
        return sum((item.amount or Decimal("0") for item in items), Decimal("0"))
