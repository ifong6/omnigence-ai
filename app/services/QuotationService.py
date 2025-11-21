from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Sequence
from datetime import date
from sqlmodel import Session
from app.models.quotation_models import QuotationSchema, QuotationCreate, QuotationUpdate, QuotationItemSchema


class QuotationService(ABC):
    """
    Abstract base class for managing quotation-related business logic.
    """

    def __init__(self, session: Session):
        self.session = session

    # -----------------------------------------------------------------------
    # Basic retrieval APIs
    # -----------------------------------------------------------------------

    @abstractmethod
    def get_quotation_by_id(self, quotation_id: int) -> Optional[QuotationSchema]:
        pass

    @abstractmethod
    def get_quotation_by_quo_no(self, quo_no: str) -> Optional[QuotationSchema]:
        pass

    @abstractmethod
    def get_quotations_by_client(
        self,
        client_id: int,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[QuotationSchema]:
        pass

    @abstractmethod
    def get_quotations_by_project(
        self,
        project_name: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[QuotationSchema]:
        pass

    @abstractmethod
    def get_quotation_total(self, quo_no: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_all(
        self,
        order_by: str = "date_issued",
        descending: bool = True,
        limit: Optional[int] = None
    ) -> List[QuotationSchema]:
        pass

    # -----------------------------------------------------------------------
    # CREATE quotation (new version: index grows, revision always R00)
    # -----------------------------------------------------------------------

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
        pass

    # -----------------------------------------------------------------------
    # NEW UPDATE LOGIC = create revision R01 / R02 / R03...
    # -----------------------------------------------------------------------

    @abstractmethod
    def update_quotation(
        self,
        base_quotation_id: int,
        update_payload: QuotationUpdate,
    ) -> Optional[QuotationSchema]:
        """
        Create a new revision based on an existing quotation (R00 → R01 → R02).
        """
        pass

    # -----------------------------------------------------------------------
    # Query helpers
    # -----------------------------------------------------------------------

    @abstractmethod
    def get_by_job_no(
        self,
        job_no: str,
        order_by: str | None = None
    ) -> Sequence[QuotationSchema]:
        pass

    @abstractmethod
    def search_by_project(
        self,
        project_name_pattern: str,
        limit: Optional[int] = 10,
        order_by: str | None = None
    ) -> Sequence[QuotationSchema]:
        pass

    @abstractmethod
    def generate_quotation_number(
        self,
        job_no: str,
        revision_no: str = "00"
    ) -> str:
        pass
