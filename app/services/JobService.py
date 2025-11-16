from abc import ABC, abstractmethod
from typing import Optional, Sequence
from datetime import datetime
from sqlmodel import Session
from app.models.job_models import DesignJob, InspectionJob

class JobService(ABC):
    """
    Abstract base class for managing job-related business logic.

    Handles separate job number sequences for DESIGN (JCP) and INSPECTION (JICP) jobs.
    """

    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        self.session = session

    @abstractmethod
    def create_job(
        self,
        *,
        company_id: int,
        title: str,
        job_type: str,
        index: int = 1,
        status: str = "NEW",
        quotation_status: str = "NOT_CREATED"
    ) -> DesignJob | InspectionJob:
        """Create a new job with auto-generated job_no."""
        pass

    @abstractmethod
    def update(
        self,
        job_id: int,
        job_type: str,
        *,
        title: Optional[str] = None,
        status: Optional[str] = None,
        quotation_status: Optional[str] = None,
        quotation_issued_at: Optional[datetime] = None
    ) -> Optional[DesignJob | InspectionJob]:
        """Update an existing job."""
        pass

    @abstractmethod
    def list_all_with_company(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """Get all jobs of a specific type with company information."""
        pass

    @abstractmethod
    def get_by_id(
        self,
        job_id: int,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by ID and type."""
        pass

    @abstractmethod
    def get_by_job_no(
        self,
        job_no: str,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by job number."""
        pass

    @abstractmethod
    def get_by_company(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[DesignJob | InspectionJob]:
        """Get all jobs for a company."""
        pass

    @abstractmethod
    def get_by_company_with_info(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """Get all jobs for a company with company information."""
        pass

    @abstractmethod
    def list_all(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[DesignJob | InspectionJob]:
        """Get all jobs of a specific type."""
        pass
