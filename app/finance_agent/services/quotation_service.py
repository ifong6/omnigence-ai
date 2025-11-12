"""
QuotationService: Service layer for quotation business logic.

Code Organization (High-Level → Low-Level):
1. QuotationService Class
   - HIGH-LEVEL Service Methods (For Agent Use) - Business logic & convenience methods
   - READ Operations - Basic query methods
   - WRITE Operations - Create & update methods
2. Module-level Helper Functions - Internal utilities
"""
from typing import Optional, List, Dict, Any, Sequence
from datetime import date
from decimal import Decimal
from sqlmodel import Session, select, func, desc as sql_desc, asc as sql_asc, col
from app.finance_agent.models.quotation_models import Quotation, QuotationItem, UnitType

# ============================================================================
# BUSINESS LOGIC: QuotationService Class
# ============================================================================

class QuotationService:
    """
    Service for managing quotation-related business logic.

    Uses SQLModel sessions for transactional operations.
    """

    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        self.session = session

    # ============================================================================
    # READ Operations (Query Methods)
    # ============================================================================

    def get_quotation_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """
        Get a quotation by ID.

        Args:
            quotation_id: Quotation ID

        Returns:
            Quotation if found, None otherwise
        """
        return self.session.get(Quotation, quotation_id)

    def get_quotation_by_quo_no(self, quo_no: str) -> Optional[Quotation]:
        """
        Get quotation header by quotation number.

        Args:
            quo_no: Quotation number (unique)

        Returns:
            Quotation header if found, None otherwise
        """
        stmt = select(Quotation).where(Quotation.quo_no == quo_no)
        return self.session.exec(stmt).first()

    def get_quotations_by_client(
        self,
        client_id: int,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Get all quotations for a client.

        Args:
            client_id: Client/Company ID
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_issued", "id")

        Returns:
            Sequence of quotations
        """
        stmt = select(Quotation).where(Quotation.client_id == client_id)
        if order_by:
            order_field = getattr(Quotation, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(col(order_field))
        if limit:
            stmt = stmt.limit(limit)
        return self.session.exec(stmt).all()

    def get_quotations_by_project(
        self,
        project_name: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Get all quotations for a project.

        Args:
            project_name: Project name
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_issued", "id")

        Returns:
            Sequence of quotations
        """
        stmt = select(Quotation).where(Quotation.project_name == project_name)
        if order_by:
            order_field = getattr(Quotation, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(col(order_field))
        if limit:
            stmt = stmt.limit(limit)
        return self.session.exec(stmt).all()

    def get_quotation_total(self, quo_no: str) -> Dict[str, Any]:
        """
        Calculate total for a quotation.

        Args:
            quo_no: Quotation number

        Returns:
            Dict with 'total' and 'item_count'
        """
        stmt = (
            select(
                func.sum(Quotation.total_amount),
                func.count()
            )
            .select_from(Quotation)
            .where(Quotation.quo_no == quo_no)
        )
        result = self.session.exec(stmt).first()

        if result:
            return {
                "total": result[0] or 0,
                "item_count": result[1] or 0
            }
        return {"total": 0, "item_count": 0}

    def list_all(
        self,
        order_by: str = "date_issued",
        descending: bool = True,
        limit: Optional[int] = None
    ) -> List[Quotation]:
        """
        Get all quotations.

        Args:
            order_by: Field to order by (default: date_issued)
            descending: Order descending (default: True)
            limit: Optional limit on results

        Returns:
            List of quotations
        """
        stmt = select(Quotation)

        # Apply ordering
        order_field = getattr(Quotation, order_by, Quotation.date_issued)
        if descending:
            stmt = stmt.order_by(sql_desc(order_field))
        else:
            stmt = stmt.order_by(sql_asc(order_field))

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    # ============================================================================
    # WRITE Operations (Create & Update Methods)
    # ============================================================================

    def _next_quo_no(self, job_no: str, is_revision: bool = False) -> tuple[str, int]:
        """
        Generate next quotation number for the given job.

        Args:
            job_no: Job number (e.g., "JCP-25-01-1" or "JICP-25-02-1")
            is_revision: If True, increment revision; if False, increment sequence

        Returns:
            Tuple of (quotation_number, revision_no)

        Examples:
            >>> # First quotation
            >>> service._next_quo_no("JICP-25-02-1")
            ("Q-JICP-25-02-q1-R00", 0)
            >>> # New sequence
            >>> service._next_quo_no("JICP-25-02-1", is_revision=False)
            ("Q-JICP-25-02-q2-R00", 0)
            >>> # Revision of existing sequence
            >>> service._next_quo_no("JICP-25-02-1", is_revision=True)
            ("Q-JICP-25-02-q2-R01", 1)
        """
        # Generate quotation prefix
        job_no_base = job_no.rsplit("-", 1)[0]
        quo_prefix = f"Q-{job_no_base}"

        # Get latest quotation with this prefix
        stmt = (
            select(Quotation.quo_no, Quotation.revision_no)
            .where(Quotation.quo_no.like(f"{quo_prefix}%"))  # type: ignore
            .order_by(sql_desc(Quotation.id))
            .limit(1)
        )
        result = self.session.exec(stmt).first()

        if result:
            last_quo_no, last_revision_no = result
        else:
            last_quo_no, last_revision_no = None, 0

        # Parse sequence from last quotation
        seq = _parse_latest_sequence(last_quo_no)

        if is_revision:
            # Keep same sequence, increment revision
            if seq == 0:
                # No existing quotation, start with q1-R00
                seq = 1
                revision_no = 0
                revision_str = "00"
            else:
                # Increment revision for existing sequence
                revision_no = last_revision_no + 1
                revision_str = f"{revision_no:02d}"
        else:
            # New sequence, reset revision
            seq += 1
            revision_no = 0
            revision_str = "00"

        quo_no = _generate_quo_no_from_job_no(job_no, seq, revision_str)
        return quo_no, revision_no

    def create_quotation(
        self,
        *,
        job_no: str,
        company_id: int,
        project_name: str,
        currency: str = "MOP",
        items: List[Dict[str, Any]],
        date_issued: Optional[date] = None,
        is_revision: bool = False,
        valid_until: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete quotation with multiple items.

        This is the high-level method that creates a quotation header and line items
        in the normalized schema.

        Args:
            job_no: Job number (required, e.g., "JICP-25-02-1")
            company_id: Company/Client ID (required)
            project_name: Project name (required)
            currency: Currency code (default "MOP")
            items: List of quotation items, each containing:
                - item_desc: str (item description)
                - quantity: int (quantity)
                - unit_price: Decimal (unit price)
                - unit: str (optional, default "Lot")
            date_issued: Date issued (defaults to today)
            is_revision: If True, create revision; if False, new sequence
            valid_until: Optional validity date
            notes: Optional notes

        Returns:
            Dict with quotation header and items:
            {
                "quotation": {...},  # Quotation header
                "items": [...]  # List of QuotationItem objects
            }

        Example:
            >>> with Session(engine) as session:
            ...     service = QuotationService(session)
            ...     result = service.create_quotation(
            ...         job_no="JICP-25-02-1",
            ...         company_id=27,
            ...         project_name="結構安全檢測 - Building A",
            ...         currency="MOP",
            ...         items=[
            ...             {
            ...                 "item_desc": "Foundation inspection",
            ...                 "quantity": 1,
            ...                 "unit_price": Decimal("20000")
            ...             },
            ...             {
            ...                 "item_desc": "Structural assessment",
            ...                 "quantity": 1,
            ...                 "unit_price": Decimal("25000")
            ...             }
            ...         ]
            ...     )
            ...     session.commit()
            ...     print(result["quotation"].quo_no)  # "Q-JICP-25-02-q1-R00"

        Note:
            Remember to call session.commit() after creation
        """
        # Generate quotation number and revision
        quo_no, revision_no = self._next_quo_no(job_no, is_revision=is_revision)

        # Use today's date if not provided
        if date_issued is None:
            from datetime import date as date_module
            date_issued = date_module.today()

        # Create quotation header
        quotation = Quotation(
            quo_no=quo_no,
            client_id=company_id,
            project_name=project_name,
            date_issued=date_issued,
            status="DRAFTED",
            currency=currency,
            revision_no=revision_no,
            valid_until=valid_until,
            notes=notes
        )
        self.session.add(quotation)
        self.session.flush()  # Get the quotation ID

        # Create quotation items
        created_items = []
        for item in items:
            # Convert unit string to UnitType enum if needed
            unit_value = item.get("unit", "Lot")
            if isinstance(unit_value, str):
                try:
                    unit_enum = UnitType[unit_value] if unit_value in UnitType.__members__ else UnitType.Lot
                except (KeyError, AttributeError):
                    unit_enum = UnitType.Lot
            else:
                unit_enum = unit_value

            quotation_item = QuotationItem(
                quotation_id=quotation.id,
                item_desc=item["item_desc"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                unit=unit_enum
            )
            self.session.add(quotation_item)
            created_items.append(quotation_item)

        self.session.flush()

        return {
            "quotation": quotation,
            "items": created_items
        }


    def update_quotation(
        self,
        quotation_ids: List[int],
        **kwargs
    ) -> List[Quotation]:
        """
        Update one or multiple quotation items.

        Args:
            quotation_ids: List of quotation IDs to update (single or multiple)
            **kwargs: Fields to update

        Returns:
            List of updated quotations (empty list if none found)

        Example:
            >>> # Update single item
            >>> service.update_quotation([123], currency="HKD")
            [<Quotation id=123>]

            >>> # Update multiple items
            >>> service.update_quotation([123, 124, 125], date_issued=date.today())
            [<Quotation id=123>, <Quotation id=124>, <Quotation id=125>]

        Note:
            Remember to call session.commit() after update
        """
        updated_quotations = []

        for quotation_id in quotation_ids:
            quotation = self.session.get(Quotation, quotation_id)
            if not quotation:
                continue  # Skip if not found

            # Update only provided fields
            for field, value in kwargs.items():
                if value is not None and hasattr(quotation, field):
                    setattr(quotation, field, value)

            self.session.add(quotation)
            updated_quotations.append(quotation)

        self.session.flush()
        return updated_quotations

    # ============================================================================
    # HIGH-LEVEL Service Methods (For Agent Use)
    # ============================================================================

    def get_by_job_no(
        self, job_no: str, order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Get all quotations for a given job number.

        Args:
            job_no: Job number (e.g., "JCP-25-01-1")
            order_by: Optional field to order by (e.g., "date_issued", "id")

        Returns:
            Sequence of quotations associated with this job

        Example:
            >>> quotations = service.get_by_job_no("JCP-25-01-1")
            >>> for q in quotations:
            ...     print(q.quo_no, q.project_name)
        """
        # Generate quotation prefix from job number
        job_no_base = job_no.rsplit("-", 1)[0]
        quo_prefix = f"Q-{job_no_base}"

        stmt = select(Quotation).where(Quotation.quo_no.like(f"{quo_prefix}%"))  # type: ignore
        if order_by:
            order_field = getattr(Quotation, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(col(order_field))
        return self.session.exec(stmt).all()

    def search_by_project(
        self,
        project_name_pattern: str,
        limit: Optional[int] = 10,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Search quotations by project name pattern.

        Args:
            project_name_pattern: Pattern to search (supports % wildcards)
            limit: Maximum results (default 10)
            order_by: Optional field to order by (e.g., "date_issued", "id")

        Returns:
            Sequence of matching quotations

        Example:
            >>> quotations = service.search_by_project("消防")
            >>> for q in quotations:
            ...     print(q.quo_no, q.project_name)
        """
        stmt = select(Quotation).where(Quotation.project_name.ilike(f"%{project_name_pattern}%"))  # type: ignore
        if order_by:
            order_field = getattr(Quotation, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(col(order_field))
        if limit:
            stmt = stmt.limit(limit)
        return self.session.exec(stmt).all()

    def generate_quotation_number(
        self,
        job_no: str,
        is_revision: bool = False
    ) -> str:
        """
        Public method to generate quotation number.

        This is a wrapper around _next_quo_no for agents to use.

        Args:
            job_no: Job number (e.g., "JICP-25-02-1")
            is_revision: If True, create revision; if False, new sequence

        Returns:
            Generated quotation number (just the quo_no string)

        Example:
            >>> quo_no = service.generate_quotation_number("JICP-25-02-1")
            "Q-JICP-25-02-q1-R00"
        """
        quo_no, _ = self._next_quo_no(job_no, is_revision=is_revision)
        return quo_no

# ============================================================================
# UTILITY FUNCTIONS: Module-level Helper Functions
# ============================================================================

def _generate_quo_no_from_job_no(job_no: str, sequence: int = 1, revision: str = "00") -> str:
    """
    Generate quotation number from job number.

    Args:
        job_no: Job number (e.g., "JCP-25-01-1")
        sequence: Sequence number (default 1)
        revision: Revision string (default "00")

    Returns:
        Quotation number (e.g., "Q-JCP-25-01-q1-R00")

    Examples:
        >>> _generate_quo_no_from_job_no("JCP-25-01-1", 1, "00")
        "Q-JCP-25-01-q1-R00"
    """
    # Remove last part after final dash
    job_no_base = job_no.rsplit("-", 1)[0]
    return f"Q-{job_no_base}-q{sequence}-R{revision}"


def _parse_latest_sequence(quo_no: str | None) -> int:
    """
    Parse sequence number from quotation number.

    Args:
        quo_no: Quotation number like "Q-JCP-25-01-q2-R01" or None

    Returns:
        Sequence number (2 in example) or 0 if invalid

    Examples:
        >>> _parse_latest_sequence("Q-JCP-25-01-q2-R01")
        2
        >>> _parse_latest_sequence(None)
        0
    """
    if not quo_no:
        return 0

    import re
    match = re.search(r'-q(\d+)-[rR]', quo_no)
    if match:
        return int(match.group(1))
    return 0


def _parse_sequence_and_revision(quo_no: str | None) -> tuple[int, int]:
    """
    Parse both sequence and revision number from quotation number.

    Args:
        quo_no: Quotation number like "Q-JCP-25-01-q2-R01" or None

    Returns:
        Tuple of (sequence, revision) or (0, 0) if invalid

    Examples:
        >>> _parse_sequence_and_revision("Q-JCP-25-01-q2-R01")
        (2, 1)
        >>> _parse_sequence_and_revision("Q-JCP-25-01-q1-R00")
        (1, 0)
        >>> _parse_sequence_and_revision(None)
        (0, 0)
    """
    if not quo_no:
        return 0, 0

    import re
    match = re.search(r'-q(\d+)-[rR](\d+)$', quo_no)
    if match:
        seq = int(match.group(1))
        rev = int(match.group(2))
        return seq, rev
    return 0, 0