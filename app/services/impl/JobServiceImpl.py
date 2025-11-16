from typing import Optional, Sequence, List, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select
from app.models.job_models import DesignJob, InspectionJob, JobCreate, JobUpdate
from app.services import JobService


def _payload_to_dict(payload: JobCreate | JobUpdate) -> Dict[str, Any]:
    """Convert Pydantic payload to dictionary, excluding None values."""
    return payload.model_dump(exclude_none=True)


class JobServiceImpl(JobService):
    """
    Job service implementation using SQLModel directly.

    No DAO layer - direct Session operations for CRUD.
    """

    def __init__(self, session: Session):
        super().__init__(session)

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
        quotation_status: str = "NOT_CREATED"
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
            quotation_status=quotation_status
        )

        # Create job directly using SQLModel
        data = _payload_to_dict(payload)

        if job_type == "DESIGN":
            job = DesignJob(**data)
        else:  # INSPECTION
            job = InspectionJob(**data)

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
        quotation_issued_at: Optional[datetime] = None
    ) -> Optional[DesignJob | InspectionJob]:
        """Update job by ID and type."""
        if job_type not in ("DESIGN", "INSPECTION"):
            raise ValueError(f"Invalid job_type: {job_type}")

        # Build update payload
        payload = JobUpdate(
            title=title,
            status=status,
            quotation_status=quotation_status,
            quotation_issued_at=quotation_issued_at
        )

        # Get and update the job
        if job_type == "DESIGN":
            return self._update_design_job(job_id, payload)
        else:  # INSPECTION
            return self._update_inspection_job(job_id, payload)

    def get_by_id(
        self,
        job_id: int,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by ID and type."""
        if job_type == "DESIGN":
            return self.session.get(DesignJob, job_id)
        elif job_type == "INSPECTION":
            return self.session.get(InspectionJob, job_id)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def get_by_job_no(
        self,
        job_no: str,
        job_type: str
    ) -> Optional[DesignJob | InspectionJob]:
        """Get job by job number and type."""
        if job_type == "DESIGN":
            stmt = select(DesignJob).where(DesignJob.job_no == job_no)
            return self.session.exec(stmt).first()
        elif job_type == "INSPECTION":
            stmt = select(InspectionJob).where(InspectionJob.job_no == job_no)
            return self.session.exec(stmt).first()
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def get_by_company(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True
    ) -> List[DesignJob | InspectionJob]:
        """Get jobs by company ID and type."""
        if job_type == "DESIGN":
            return self._get_design_jobs_by_company(company_id, limit, offset, order_desc)
        elif job_type == "INSPECTION":
            return self._get_inspection_jobs_by_company(company_id, limit, offset, order_desc)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    def list_all(
        self,
        job_type: str,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True
    ) -> List[DesignJob | InspectionJob]:
        """List all jobs by type."""
        if job_type == "DESIGN":
            return self._list_all_design_jobs(limit, offset, order_desc)
        elif job_type == "INSPECTION":
            return self._list_all_inspection_jobs(limit, offset, order_desc)
        else:
            raise ValueError(f"Invalid job_type: {job_type}")

    # ========================================================================
    # CONVENIENCE METHODS: Auto-detect job type
    # ========================================================================

    def get_job_by_id(self, job_id: int) -> Optional[DesignJob | InspectionJob]:
        """Get job by ID, checking both DESIGN and INSPECTION tables."""
        # Try DESIGN first
        job = self.session.get(DesignJob, job_id)
        if job:
            return job
        # Then try INSPECTION
        return self.session.get(InspectionJob, job_id)

    def get_job_by_job_no(self, job_no: str) -> Optional[DesignJob | InspectionJob]:
        """Get job by job number, checking both DESIGN and INSPECTION tables."""
        # Try DESIGN first
        stmt = select(DesignJob).where(DesignJob.job_no == job_no)
        job = self.session.exec(stmt).first()
        if job:
            return job
        # Then try INSPECTION
        stmt = select(InspectionJob).where(InspectionJob.job_no == job_no)
        return self.session.exec(stmt).first()

    def get_jobs_by_company_id(
        self,
        company_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Sequence[DesignJob | InspectionJob]:
        """Get all jobs for a company (both DESIGN and INSPECTION)."""
        design_jobs = self._get_design_jobs_by_company(company_id)
        inspection_jobs = self._get_inspection_jobs_by_company(company_id)

        # Combine and sort by date_created descending
        all_jobs = list(design_jobs) + list(inspection_jobs)
        all_jobs.sort(key=lambda j: j.date_created, reverse=True)

        # Apply offset and limit
        if offset:
            all_jobs = all_jobs[offset:]
        if limit:
            all_jobs = all_jobs[:limit]

        return all_jobs

    def update_job(
        self,
        job_id: int,
        payload
    ) -> Optional[DesignJob | InspectionJob]:
        """Update job by ID, auto-detecting job type."""
        # Build update payload from DTO
        update_payload = JobUpdate(
            title=getattr(payload, 'title', None),
            status=getattr(payload, 'status', None),
            quotation_status=getattr(payload, 'quotation_status', None),
            quotation_issued_at=getattr(payload, 'quotation_issued_at', None)
        )

        # Try DESIGN first
        design_job = self.session.get(DesignJob, job_id)
        if design_job:
            return self._update_design_job(job_id, update_payload)

        # Then try INSPECTION
        inspection_job = self.session.get(InspectionJob, job_id)
        if inspection_job:
            return self._update_inspection_job(job_id, update_payload)

        return None

    def list_all_jobs(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Sequence[DesignJob | InspectionJob]:
        """List all jobs (both DESIGN and INSPECTION)."""
        design_jobs = self._list_all_design_jobs()
        inspection_jobs = self._list_all_inspection_jobs()

        # Combine and sort by date_created descending
        all_jobs = list(design_jobs) + list(inspection_jobs)
        all_jobs.sort(key=lambda j: j.date_created, reverse=True)

        # Apply offset and limit
        if offset:
            all_jobs = all_jobs[offset:]
        if limit:
            all_jobs = all_jobs[:limit]

        return all_jobs

    # ========================================================================
    # QUERY HELPERS WITH COMPANY INFO
    # ========================================================================

    def get_by_company_with_info(
        self,
        company_id: int,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """Get jobs by company with basic info dict."""
        jobs = self.get_by_company(company_id, job_type, limit=limit)

        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "company_id": job.company_id
            }
            for job in jobs
        ]

    def list_all_with_company(
        self,
        job_type: str,
        limit: Optional[int] = None,
        order_by: str | None = None
    ) -> list[dict]:
        """List all jobs with basic info dict."""
        jobs = self.list_all(job_type, limit=limit)

        return [
            {
                "id": job.id,
                "job_no": job.job_no,
                "title": job.title,
                "status": job.status,
                "quotation_status": job.quotation_status,
                "company_id": job.company_id
            }
            for job in jobs
        ]

    # ========================================================================
    # PRIVATE HELPERS: Direct SQLModel Operations
    # ========================================================================

    def _update_design_job(self, job_id: int, payload: JobUpdate) -> Optional[DesignJob]:
        """Update a design job directly."""
        job = self.session.get(DesignJob, job_id)
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
        job = self.session.get(InspectionJob, job_id)
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
        order_desc: bool = True
    ) -> List[DesignJob]:
        """Get design jobs by company ID."""
        stmt = select(DesignJob).where(DesignJob.company_id == company_id)
        stmt = stmt.order_by(
            DesignJob.date_created.desc() if order_desc else DesignJob.date_created.asc()  # type: ignore
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
        order_desc: bool = True
    ) -> List[InspectionJob]:
        """Get inspection jobs by company ID."""
        stmt = select(InspectionJob).where(InspectionJob.company_id == company_id)
        stmt = stmt.order_by(
            InspectionJob.date_created.desc() if order_desc else InspectionJob.date_created.asc()  # type: ignore
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
        order_desc: bool = True
    ) -> List[DesignJob]:
        """List all design jobs."""
        stmt = select(DesignJob)
        stmt = stmt.order_by(
            DesignJob.date_created.desc() if order_desc else DesignJob.date_created.asc()  # type: ignore
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
        order_desc: bool = True
    ) -> List[InspectionJob]:
        """List all inspection jobs."""
        stmt = select(InspectionJob)
        stmt = stmt.order_by(
            InspectionJob.date_created.desc() if order_desc else InspectionJob.date_created.asc()  # type: ignore
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
        index: int = 1
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
