"""
JobService: Service layer for job-related business logic.

Code Organization (High-Level → Low-Level):
1. JobService Class
   - HIGH-LEVEL Service Methods (For Agent Use) - Business logic & convenience methods
   - READ Operations - Basic query methods
   - WRITE Operations - Create & update methods
2. Module-level Helper Functions - Internal utilities

Handles separate job number sequences for DESIGN (JCP) and INSPECTION (JICP) jobs.
"""
from typing import Optional, Sequence
from datetime import datetime
from sqlmodel import Session, select, desc, col
from app.finance_agent.models.job_models import DesignJob, InspectionJob
from app.finance_agent.models.company_models import Company

# ============================================================================
# BUSINESS LOGIC: JobService Class
# ============================================================================

class JobService:
    """
    Service for managing job-related business logic.

    Handles separate job number sequences for DESIGN (JCP) and INSPECTION (JICP) jobs.

    Method Organization (High-Level → Low-Level):
    1. HIGH-LEVEL Service Methods - For Agent/Application Use
    2. READ Operations - Basic query methods
    3. WRITE Operations - Create & update methods
    """

    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        self.session = session

    # ========================================================================
    # HIGH-LEVEL Service Methods (For Agent Use)
    # ========================================================================

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
        """
        Create a new job with auto-generated job_no.

        Args:
            company_id: Company ID (foreign key)
            title: Job title
            job_type: "DESIGN" or "INSPECTION"
            index: Item index (default 1)
            status: Job status (default "NEW")
            quotation_status: Quotation status (default "NOT_CREATED")

        Returns:
            Created job (DesignJob or InspectionJob)

        Example:
            >>> with Session(engine) as session:
            ...     service = JobService(session)
            ...     job = service.create_job(
            ...         company_id=15,
            ...         title="空調系統設計",
            ...         job_type="DESIGN"
            ...     )
            ...     print(job.job_no)  # "JCP-25-01-1"
            ...     session.commit()

        Note:
            Remember to call session.commit() after creation
        """
        # Generate job number
        job_no = self._next_job_no(job_type, idx=index)

        # Create job based on type
        # Note: date_created is auto-set by database (server_default=now())
        if job_type == "DESIGN":
            job = DesignJob(
                company_id=company_id,
                title=title,
                status=status,
                job_no=job_no,
                quotation_status=quotation_status,
            )
        else:
            job = InspectionJob(
                company_id=company_id,
                title=title,
                status=status,
                job_no=job_no,
                quotation_status=quotation_status,
            )

        self.session.add(job)
        self.session.flush()  # Flush to get ID without committing
        return job

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
        """
        Update an existing job.

        Args:
            job_id: Job ID to update
            job_type: "DESIGN" or "INSPECTION"
            title: New title (optional)
            status: New status (optional)
            quotation_status: New quotation status (optional)
            quotation_issued_at: Quotation issued date (optional)

        Returns:
            Updated job if found, None otherwise

        Note:
            Remember to call session.commit() after update
        """
        job = self.get_by_id(job_id, job_type)
        if not job:
            return None

        # Update only provided fields
        if title is not None:
            job.title = title
        if status is not None:
            job.status = status
        if quotation_status is not None:
            job.quotation_status = quotation_status
        if quotation_issued_at is not None:
            job.quotation_issued_at = quotation_issued_at

        self.session.add(job)
        self.session.flush()
        return job

    def list_all_with_company(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """
        Get all jobs of a specific type with company information.

        Args:
            job_type: "DESIGN" or "INSPECTION"
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_created", "id")

        Returns:
            List of dicts with job and company info

        Example:
            >>> jobs = service.list_all_with_company("DESIGN", limit=10)
            >>> for job in jobs:
            ...     print(f"{job['job_no']}: {job['title']} ({job['company_name']})")
        """
        if job_type == "DESIGN":
            stmt = (
                select(DesignJob, Company.name.label("company_name"))  # type: ignore
                .join(Company, DesignJob.company_id == Company.id)  # type: ignore
            )
            if order_by:
                order_field = getattr(DesignJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))
                else:
                    stmt = stmt.order_by(desc(DesignJob.date_created))
            else:
                stmt = stmt.order_by(desc(DesignJob.date_created))
        else:
            stmt = (
                select(InspectionJob, Company.name.label("company_name"))  # type: ignore
                .join(Company, InspectionJob.company_id == Company.id)  # type: ignore
            )
            if order_by:
                order_field = getattr(InspectionJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))
                else:
                    stmt = stmt.order_by(desc(InspectionJob.date_created))
            else:
                stmt = stmt.order_by(desc(InspectionJob.date_created))

        if limit:
            stmt = stmt.limit(limit)

        results = self.session.exec(stmt).all()

        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "company_id": job.company_id,
                "company_name": company_name,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "quotation_issued_at": job.quotation_issued_at,
                "date_created": job.date_created
            }
            for job, company_name in results
        ]

    # ========================================================================
    # READ Operations (Basic Query Methods)
    # ========================================================================

    def get_by_id(
        self,
        job_id: int,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """
        Get job by ID and type.

        Args:
            job_id: Job ID
            job_type: "DESIGN" or "INSPECTION"

        Returns:
            Job if found, None otherwise
        """
        if job_type == "DESIGN":
            return self.session.get(DesignJob, job_id)
        else:
            return self.session.get(InspectionJob, job_id)

    def get_by_job_no(
        self,
        job_no: str,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """
        Get job by job number.

        Args:
            job_no: Job number (e.g., "JCP-25-01-1")
            job_type: "DESIGN" or "INSPECTION"

        Returns:
            Job if found, None otherwise
        """
        if job_type == "DESIGN":
            stmt = select(DesignJob).where(DesignJob.job_no == job_no)
        else:
            stmt = select(InspectionJob).where(InspectionJob.job_no == job_no)

        return self.session.exec(stmt).first()

    def get_by_company(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[DesignJob | InspectionJob]:
        """
        Get all jobs for a company.

        Args:
            company_id: Company ID
            job_type: "DESIGN" or "INSPECTION"
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_created", "id")

        Returns:
            Sequence of jobs
        """
        if job_type == "DESIGN":
            stmt = select(DesignJob).where(DesignJob.company_id == company_id)
            if order_by:
                order_field = getattr(DesignJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))
        else:
            stmt = select(InspectionJob).where(InspectionJob.company_id == company_id)
            if order_by:
                order_field = getattr(InspectionJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))

        if limit:
            stmt = stmt.limit(limit)

        return self.session.exec(stmt).all()

    def get_by_company_with_info(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """
        Get all jobs for a company with company information.

        Args:
            company_id: Company ID
            job_type: "DESIGN" or "INSPECTION"
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_created", "id")

        Returns:
            List of dicts with job and company info

        Example:
            >>> jobs = service.get_by_company_with_info(15, "DESIGN")
            >>> for job in jobs:
            ...     print(f"{job['job_no']}: {job['title']}")
        """
        if job_type == "DESIGN":
            stmt = (
                select(DesignJob, Company.name.label("company_name"))  # type: ignore
                .join(Company, DesignJob.company_id == Company.id)  # type: ignore
                .where(DesignJob.company_id == company_id)
            )
            if order_by:
                order_field = getattr(DesignJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))
        else:
            stmt = (
                select(InspectionJob, Company.name.label("company_name"))  # type: ignore
                .join(Company, InspectionJob.company_id == Company.id)  # type: ignore
                .where(InspectionJob.company_id == company_id)
            )
            if order_by:
                order_field = getattr(InspectionJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))

        if limit:
            stmt = stmt.limit(limit)

        results = self.session.exec(stmt).all()

        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "company_id": job.company_id,
                "company_name": company_name,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "quotation_issued_at": job.quotation_issued_at,
                "date_created": job.date_created
            }
            for job, company_name in results
        ]

    def list_all(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> Sequence[DesignJob | InspectionJob]:
        """
        Get all jobs of a specific type.

        Args:
            job_type: "DESIGN" or "INSPECTION"
            limit: Optional limit on results
            order_by: Optional field to order by (e.g., "date_created", "id")

        Returns:
            Sequence of jobs
        """
        if job_type == "DESIGN":
            stmt = select(DesignJob)
            if order_by:
                order_field = getattr(DesignJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))
        else:
            stmt = select(InspectionJob)
            if order_by:
                order_field = getattr(InspectionJob, order_by, None)
                if order_field is not None:
                    stmt = stmt.order_by(desc(col(order_field)))

        if limit:
            stmt = stmt.limit(limit)

        return self.session.exec(stmt).all()

    # ========================================================================
    # WRITE Operations (Create & Update Methods - Internal)
    # ========================================================================

    def _next_job_no(self, job_type: str, idx: int = 1) -> str:
        """
        Generate next job number for the given job type.

        Uses separate counters for DESIGN and INSPECTION jobs.
        Format: {PREFIX}-{YY}-{SEQ:02d}-{IDX}

        Args:
            job_type: "DESIGN" or "INSPECTION"
            idx: Item index within the job (default 1)

        Returns:
            Next job number string

        Examples:
            >>> # If last DESIGN job was "JCP-25-03-1"
            >>> service._next_job_no("DESIGN")
            "JCP-25-04-1"
            >>> # If last INSPECTION job was "JICP-25-10-2"
            >>> service._next_job_no("INSPECTION", idx=3)
            "JICP-25-11-3"
        """
        # Get the last job_no from the appropriate table
        if job_type == "DESIGN":
            stmt = select(DesignJob.job_no).order_by(desc(DesignJob.id)).limit(1)
        else:
            stmt = select(InspectionJob.job_no).order_by(desc(InspectionJob.id)).limit(1)

        last_job_no = self.session.exec(stmt).first()

        # Parse sequence from last job number
        seq = _parse_seq(last_job_no) + 1

        # Generate new job number
        yy = datetime.now().strftime("%y")
        prefix = "JCP" if job_type == "DESIGN" else "JICP"

        return f"{prefix}-{yy}-{seq:02d}-{idx}"

# ============================================================================
# UTILITY FUNCTIONS: Module-level Helper Functions
# ============================================================================

def _parse_seq(job_no: str | None) -> int:
    """
    Parse sequence number from job_no string.

    Args:
        job_no: Job number like "JCP-25-01-1" or None

    Returns:
        Sequence number (01 in example) or 0 if invalid

    Examples:
        >>> _parse_seq("JCP-25-01-1")
        1
        >>> _parse_seq("JICP-25-05-2")
        5
        >>> _parse_seq("NONE")
        0
        >>> _parse_seq(None)
        0
    """
    if not job_no or job_no == "NONE":
        return 0

    parts = job_no.split("-")
    if len(parts) >= 3:
        try:
            return int(parts[2])
        except ValueError:
            return 0
    return 0