from typing import Optional, Sequence, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select
from app.models.job_models import DesignJob, InspectionJob, JobCreate, JobUpdate
from app.services import JobService


def _payload_to_dict(payload: JobCreate | JobUpdate) -> Dict[str, Any]:
    """Convert Pydantic/SQLModel payload to dictionary, excluding None values."""
    return payload.model_dump(exclude_none=True)


class JobServiceImpl(JobService):
    """
    Job service implementation using SQLModel models directly.

    No DAO layer - direct Session operations for CRUD.
    """

    def __init__(self, session: Session):
        super().__init__(session)
        self.session = session
        # Model references for clarity and consistency
        self.design_model = DesignJob
        self.inspection_model = InspectionJob

    # ========================================================================
    # CORE CRUD OPERATIONS (with job_type)
    # ========================================================================

    def create_job(
        self,
        *,
        company_id: int,
        title: str,
        job_type: str,
        index: int = 1,
        status: str = "NEW",
        quotation_status: str = "NOT_CREATED",
    ) -> DesignJob | InspectionJob:
        """Create a new job (DESIGN or INSPECTION)."""
        if job_type not in ("DESIGN", "INSPECTION"):
            raise ValueError(f"Invalid job_type: {job_type}. Must be 'DESIGN' or 'INSPECTION'")

        # Generate job number
        job_no = self._generate_job_number(job_type, company_id, index)

        # Create job payload
        payload = JobCreate(
            company_id=company_id,
            title=title,
            job_no=job_no,
            status=status,
            quotation_status=quotation_status,
        )

        data = _payload_to_dict(payload)

        if job_type == "DESIGN":
            job = self.design_model(**data)
        else:  # INSPECTION
            job = self.inspection_model(**data)

        self.session.add(job)
        self.session.flush()
        self.session.refresh(job)
        return job

    def update(
        self,
        job_id: int,
        job_type: str,
        *,
        title: Optional[str] = None,
        status: Optional[str] = None,
        quotation_status: Optional[str] = None,
        quotation_issued_at: Optional[datetime] = None,
    ) -> Optional[DesignJob | InspectionJob]:
        """Update job by ID and type."""
        if job_type not in ("DESIGN", "INSPECTION"):
            raise ValueError(f"Invalid job_type: {job_type}")

        payload = JobUpdate(
            title=title,
            status=status,
            quotation_status=quotation_status,
            quotation_issued_at=quotation_issued_at,
        )

        if job_type == "DESIGN":
            return self._update_design_job(job_id, payload)
        else:  # INSPECTION
            return self._update_inspection_job(job_id, payload)

    # ========================================================================
    # INTERFACE METHODS (matching JobService)
    # ========================================================================

    def list_all_with_company(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> list[dict]:
        """
        Get all jobs of a specific type with basic job+company info dict.

        order_by:
          - None or "date_created_desc" (default): newest first
          - "date_created_asc": oldest first
        """
        jobs = self.list_all(job_type, limit=limit, order_by=order_by)
        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "company_id": job.company_id,
            }
            for job in jobs
        ]

    def get_by_id(
        self,
        job_id: int,
        job_type: str,
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by ID and type."""
        if job_type == "DESIGN":
            return self.session.get(self.design_model, job_id)
        elif job_type == "INSPECTION":
            return self.session.get(self.inspection_model, job_id)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def get_by_job_no(
        self,
        job_no: str,
        job_type: str,
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by job number and type."""
        if job_type == "DESIGN":
            stmt = select(self.design_model).where(self.design_model.job_no == job_no)
            return self.session.exec(stmt).first()
        elif job_type == "INSPECTION":
            stmt = select(self.inspection_model).where(self.inspection_model.job_no == job_no)
            return self.session.exec(stmt).first()
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def get_by_company(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> Sequence[DesignJob | InspectionJob]:
        """
        Get all jobs for a company (by type).

        order_by:
          - None or "date_created_desc" (default): newest first
          - "date_created_asc": oldest first
        """
        order_desc = self._resolve_order_desc(order_by)

        if job_type == "DESIGN":
            return self._get_design_jobs_by_company(company_id, limit=limit, offset=0, order_desc=order_desc)
        elif job_type == "INSPECTION":
            return self._get_inspection_jobs_by_company(company_id, limit=limit, offset=0, order_desc=order_desc)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def get_by_company_with_info(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> list[dict]:
        """
        Get all jobs for a company with basic job+company info dict.

        order_by:
          - None or "date_created_desc" (default): newest first
          - "date_created_asc": oldest first
        """
        jobs = self.get_by_company(company_id, job_type, limit=limit, order_by=order_by)

        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "company_id": job.company_id,
            }
            for job in jobs
        ]

    def list_all(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> Sequence[DesignJob | InspectionJob]:
        """
        Get all jobs of a specific type.

        order_by:
          - None or "date_created_desc" (default): newest first
          - "date_created_asc": oldest first
        """
        order_desc = self._resolve_order_desc(order_by)

        if job_type == "DESIGN":
            return self._list_all_design_jobs(limit=limit, offset=0, order_desc=order_desc)
        elif job_type == "INSPECTION":
            return self._list_all_inspection_jobs(limit=limit, offset=0, order_desc=order_desc)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    # ========================================================================
    # PRIVATE HELPERS: Direct SQLModel Operations
    # ========================================================================

    def _update_design_job(self, job_id: int, payload: JobUpdate) -> Optional[DesignJob]:
        """Update a design job directly."""
        job = self.session.get(self.design_model, job_id)
        if not job:
            return None

        data = _payload_to_dict(payload)
        if not data:
            return job  # No changes

        for key, value in data.items():
            setattr(job, key, value)

        self.session.add(job)
        self.session.flush()
        self.session.refresh(job)
        return job

    def _update_inspection_job(self, job_id: int, payload: JobUpdate) -> Optional[InspectionJob]:
        """Update an inspection job directly."""
        job = self.session.get(self.inspection_model, job_id)
        if not job:
            return None

        data = _payload_to_dict(payload)
        if not data:
            return job  # No changes

        for key, value in data.items():
            setattr(job, key, value)

        self.session.add(job)
        self.session.flush()
        self.session.refresh(job)
        return job

    def _get_design_jobs_by_company(
        self,
        company_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> list[DesignJob]:
        """Get design jobs by company ID."""
        stmt = select(self.design_model).where(self.design_model.company_id == company_id)
        stmt = stmt.order_by(
            self.design_model.date_created.desc()  # type: ignore
            if order_desc
            else self.design_model.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    def _get_inspection_jobs_by_company(
        self,
        company_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> list[InspectionJob]:
        """Get inspection jobs by company ID."""
        stmt = select(self.inspection_model).where(self.inspection_model.company_id == company_id)
        stmt = stmt.order_by(
            self.inspection_model.date_created.desc()  # type: ignore
            if order_desc
            else self.inspection_model.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    def _list_all_design_jobs(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> list[DesignJob]:
        """List all design jobs."""
        stmt = select(self.design_model)
        stmt = stmt.order_by(
            self.design_model.date_created.desc()  # type: ignore
            if order_desc
            else self.design_model.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    def _list_all_inspection_jobs(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> list[InspectionJob]:
        """List all inspection jobs."""
        stmt = select(self.inspection_model)
        stmt = stmt.order_by(
            self.inspection_model.date_created.desc()  # type: ignore   
            if order_desc
            else self.inspection_model.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def _generate_job_number(
        self,
        job_type: str,
        company_id: int,
        index: int = 1,
    ) -> str:
        """Generate job number based on type and date."""
        today = date.today()
        year = today.strftime("%y")  # YY format
        month = today.strftime("%m")  # MM format

        if job_type == "DESIGN":
            return f"Q-JCP-{year}-{month}-{index}"
        elif job_type == "INSPECTION":
            return f"Q-JICP-{year}-{month}-{index}"
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    @staticmethod
    def _resolve_order_desc(order_by: str | None) -> bool:
        """
        Turn order_by string into a boolean flag for descending order.

        Returns True for desc, False for asc.
        """
        if order_by == "date_created_asc":
            return False
        # Default and "date_created_desc"
        return True
