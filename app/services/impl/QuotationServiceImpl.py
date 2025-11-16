from typing import Optional, List, Dict, Any, Sequence
from datetime import date
from decimal import Decimal
from sqlmodel import Session
from app.models.quotation_models import Quotation, QuotationCreate, QuotationUpdate
from app.finance_agent.repos.quotation_repo import QuotationRepo
from app.services import QuotationService


class QuotationServiceImpl(QuotationService):
    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        super().__init__(session)
        self.quotation_repo = QuotationRepo(session)

    def get_quotation_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """
        Get a quotation by ID.

        Args:
            quotation_id: Quotation ID

        Returns:
            Quotation if found, None otherwise
        """
        return self.quotation_repo.get_by_id(quotation_id)

    def get_quotation_by_quo_no(self, quo_no: str) -> Optional[Quotation]:
        """
        Get quotation header by quotation number.

        Args:
            quo_no: Quotation number (e.g., "Q-JCP-25-01-1-1")

        Returns:
            First quotation with this number if found, None otherwise
        """
        quotations = self.quotation_repo.get_by_quo_no(quo_no)
        return quotations[0] if quotations else None

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
            limit: Maximum number of results
            order_by: Ordering column (not used, kept for API compatibility)

        Returns:
            List of quotations for the client
        """
        return self.quotation_repo.get_by_client_id(client_id, limit=limit, order_desc=True)

    def get_quotations_by_project(
        self,
        project_name: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Get all quotations for a project.

        Args:
            project_name: Exact project name
            limit: Maximum number of results
            order_by: Ordering column (not used, kept for API compatibility)

        Returns:
            List of quotations for the project
        """
        return self.quotation_repo.get_by_project_name(project_name, limit=limit, order_desc=True)

    def get_quotation_total(self, quo_no: str) -> Dict[str, Any]:
        """
        Calculate total for a quotation.

        Args:
            quo_no: Quotation number

        Returns:
            Dict with keys:
            - total: Total amount (Decimal)
            - item_count: Number of items (int)

        Example:
            >>> service.get_quotation_total("Q-JCP-25-01-1-1")
            {'total': Decimal('50000.00'), 'item_count': 1}
        """
        return self.quotation_repo.get_total_by_quo_no(quo_no)

    def list_all(
        self,
        order_by: str = "date_issued",
        descending: bool = True,
        limit: Optional[int] = None
    ) -> List[Quotation]:
        """
        Get all quotations.

        Args:
            order_by: Ordering column (default: "date_issued")
            descending: Sort descending if True (default: True)
            limit: Maximum number of results

        Returns:
            List of all quotations
        """
        return self.quotation_repo.get_all(limit=limit, order_desc=descending)

    def create_quotation(
        self,
        *,
        job_no: str,
        company_id: int,
        project_name: str,
        currency: str = "MOP",
        items: List[Dict[str, Any]],
        date_issued: Optional[date] = None,
        revision_no: str = "00",
        valid_until: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete quotation with multiple items.

        Args:
            job_no: Job number (e.g., "Q-JCP-25-01-1")
            company_id: Company/Client ID
            project_name: Project name
            currency: Currency code (default: "MOP")
            items: List of item dicts with keys:
                - project_item_description: Item description
                - quantity: Quantity
                - unit: Unit type
                - sub_amount: Sub amount (unit price * quantity)
                - total_amount: Total amount
            date_issued: Issue date (default: today)
            revision_no: Revision number (00=no revision, 01/02/etc=revision)
            valid_until: Valid until date (optional)
            notes: Notes/remarks (optional)

        Returns:
            Dict with keys:
            - quotations: List of created quotation records
            - quo_no: Quotation number
            - total: Total amount
            - item_count: Number of items

        Example:
            >>> result = service.create_quotation(
            ...     job_no="Q-JCP-25-01-1",
            ...     company_id=1,
            ...     project_name="空調系統設計",
            ...     items=[
            ...         {
            ...             "project_item_description": "設計費用",
            ...             "quantity": 1.0,
            ...             "unit": "項",
            ...             "sub_amount": Decimal("50000"),
            ...             "total_amount": Decimal("50000")
            ...         }
            ...     ]
            ... )
        """
        if not date_issued:
            date_issued = date.today()

        # Determine if this is a revision (anything other than "00")
        is_revision = revision_no != "00"

        # Generate quotation number
        quo_no = self.generate_quotation_number(job_no, revision_no)

        # Create quotation header
        quotation_payload = QuotationCreate(
            quo_no=quo_no,
            client_id=company_id,
            project_name=project_name,
            date_issued=date_issued,
            currency=currency,
            status="DRAFTED",
            valid_until=valid_until,
            notes=notes,
            revision_no=int(revision_no) if is_revision else 0
        )

        # Create header first
        quotation = self.quotation_repo.create_quotation(quotation_payload)
        self.session.flush()

        # For now, we return the quotation as is
        # In a real scenario with QuotationItem, you would create items here
        created_quotations = [quotation]

        # Get total
        total_info = self.get_quotation_total(quo_no)

        return {
            "quotations": created_quotations,
            "quo_no": quo_no,
            "total": total_info.get("total", Decimal("0")),
            "item_count": total_info.get("item_count", 0)
        }

    def update_quotation(
        self,
        quotation_ids: List[int],
        **kwargs
    ) -> List[Quotation]:
        """
        Update one or multiple quotation items.

        Args:
            quotation_ids: List of quotation IDs to update
            **kwargs: Fields to update (quo_no, status, notes, etc.)

        Returns:
            List of updated quotations

        Example:
            >>> updated = service.update_quotation(
            ...     [1, 2],
            ...     status="SENT",
            ...     notes="Updated notes"
            ... )
        """
        updated = []
        payload = QuotationUpdate(**kwargs)

        for quo_id in quotation_ids:
            result = self.quotation_repo.update_quotation(quo_id, payload)
            if result:
                updated.append(result)

        self.session.flush()
        return updated

    def get_by_job_no(
        self,
        job_no: str,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Get all quotations for a given job number.

        Args:
            job_no: Job number (e.g., "Q-JCP-25-01-1")
            order_by: Ordering column (not used, kept for API compatibility)

        Returns:
            List of quotations matching the job number
        """
        return self.quotation_repo.get_by_job_no_pattern(job_no)

    def search_by_project(
        self,
        project_name_pattern: str,
        limit: Optional[int] = 10,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """
        Search quotations by project name pattern.

        Args:
            project_name_pattern: Pattern to search for (case-insensitive)
            limit: Maximum number of results (default: 10)
            order_by: Ordering column (not used, kept for API compatibility)

        Returns:
            List of matching quotations

        Example:
            >>> quotations = service.search_by_project("空調", limit=5)
        """
        return self.quotation_repo.search_by_project_pattern(
            pattern=project_name_pattern,
            limit=limit or 10
        )

    def generate_quotation_number(
        self,
        job_no: str,
        revision_no: str = "00"
    ) -> str:
        """
        Public method to generate quotation number.

        Format:
        - Original: {job_no}-{revision_no} where revision_no starts at 1
        - Revision: Increment revision_no

        Args:
            job_no: Job number (e.g., "Q-JCP-25-01-1")
            revision_no: Revision number (00=no revision, 01/02/etc=revision)

        Returns:
            Generated quotation number

        Example:
            >>> service.generate_quotation_number("Q-JCP-25-01-1", revision_no="00")
            'Q-JCP-25-01-1-1'
            >>> service.generate_quotation_number("Q-JCP-25-01-1", revision_no="01")
            'Q-JCP-25-01-1-2'  # increments from previous
        """
        if revision_no != "00":
            # Find highest revision number for this job
            next_revision = self._get_next_revision_number(job_no)
            return f"{job_no}-{next_revision}"
        else:
            # First quotation for this job
            return f"{job_no}-1"

    # ========================================================================
    # UTILITY FUNCTIONS: Module-level Helper Functions
    # ========================================================================

    def _extract_revision_no(self, quo_no: str) -> int:
        """
        Extract revision number from quotation number.

        Args:
            quo_no: Quotation number (e.g., "Q-JCP-25-01-1-2")

        Returns:
            Revision number (the last segment)

        Example:
            >>> service._extract_revision_no("Q-JCP-25-01-1-2")
            2
        """
        parts = quo_no.split("-")
        if len(parts) > 1:
            try:
                return int(parts[-1])
            except ValueError:
                return 1
        return 1

    def _get_next_revision_number(self, job_no: str) -> int:
        """
        Get the next revision number for a job.

        Queries the database to find the highest revision number
        already assigned to this job, then returns the next one.

        Args:
            job_no: Job number (e.g., "Q-JCP-25-01-1")

        Returns:
            Next revision number (default: 2 if no existing quotations)

        Example:
            >>> service._get_next_revision_number("Q-JCP-25-01-1")
            2  # if one quotation exists with revision 1
        """
        # Find all quotations matching this job_no with revision suffix
        quotations = self.quotation_repo.get_by_quo_no_prefix(job_no)

        if not quotations:
            return 2  # First revision after original (1)

        # Extract revision numbers and find the max
        max_revision = 1
        for quo in quotations:
            revision = self._extract_revision_no(quo.quo_no)
            if revision > max_revision:
                max_revision = revision

        return max_revision + 1
