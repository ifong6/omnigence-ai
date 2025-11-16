from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Sequence
from datetime import date
from sqlmodel import Session
from app.models.quotation_models import Quotation


class QuotationService(ABC):
    """
    Abstract base class for managing quotation-related business logic.

    Uses SQLModel sessions for transactional operations.
    """

    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        self.session = session

    @abstractmethod
    def get_quotation_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """Get a quotation by ID."""
        pass

    @abstractmethod
    def get_quotation_by_quo_no(self, quo_no: str) -> Optional[Quotation]:
        """Get quotation header by quotation number."""
        pass

    @abstractmethod
    def get_quotations_by_client(
        self,
        client_id: int,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """Get all quotations for a client."""
        pass

    @abstractmethod
    def get_quotations_by_project(
        self,
        project_name: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """Get all quotations for a project."""
        pass

    @abstractmethod
    def get_quotation_total(self, quo_no: str) -> Dict[str, Any]:
        """Calculate total for a quotation."""
        pass

    @abstractmethod
    def list_all(
        self,
        order_by: str = "date_issued",
        descending: bool = True,
        limit: Optional[int] = None
    ) -> List[Quotation]:
        """Get all quotations."""
        pass

    @abstractmethod
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
        """Create a complete quotation with multiple items."""
        pass

    @abstractmethod
    def update_quotation(
        self,
        quotation_ids: List[int],
        **kwargs
    ) -> List[Quotation]:
        """Update one or multiple quotation items."""
        pass

    @abstractmethod
    def get_by_job_no(
        self, job_no: str, order_by: str | None = None
    ) -> Sequence[Quotation]:
        """Get all quotations for a given job number."""
        pass

    @abstractmethod
    def search_by_project(
        self,
        project_name_pattern: str,
        limit: Optional[int] = 10,
        order_by: str | None = None
    ) -> Sequence[Quotation]:
        """Search quotations by project name pattern."""
        pass

    @abstractmethod
    def generate_quotation_number(
        self,
        job_no: str,
        revision_no: str = "00"
    ) -> str:
        """Public method to generate quotation number."""
        pass
