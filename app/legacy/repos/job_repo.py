"""
Job Repository for CRUD operations on Finance job tables (design_job, inspection_job).

Provides type-safe database operations with validation and business logic.
"""

from typing import Dict, Any, Optional, List
from sqlmodel import Session, select

from app.finance_agent.repos.base_repo import OrmBaseRepository
from app.models.job_models import DesignJob, InspectionJob, JobCreate, JobUpdate, JobRow


def _payload_to_dict(payload: JobCreate | JobUpdate) -> Dict[str, Any]:
    """Convert SQLModel payload to dict; None 已在 model_dump 過濾。"""
    return payload.model_dump(exclude_none=True)


class DesignJobRepo(OrmBaseRepository[DesignJob]):
    """Repository for managing DESIGN jobs in Finance.design_job table."""

    def __init__(self, session: Session):
        super().__init__(model=DesignJob, session=session)

    # --- CRUD ---------------------------------------------------------------

    def create_job(self, payload: JobCreate) -> DesignJob:
        data = _payload_to_dict(payload)
        return super().create(**data)

    def update_job(self, job_id: int, payload: JobUpdate) -> Optional[DesignJob]:
        data = _payload_to_dict(payload)
        if not data:
            return None
        return super().update(job_id, **data)

    def get_by_id(self, job_id: int) -> Optional[DesignJob]:
        return super().get(job_id)

    def get_by_job_no(self, job_no: str) -> Optional[DesignJob]:
        return super().find_one_by(job_no=job_no)

    def get_by_company_id(
        self,
        company_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[DesignJob]:
        stmt = select(DesignJob).where(DesignJob.company_id == company_id)
        stmt = stmt.order_by(
            DesignJob.date_created.desc() if order_desc else DesignJob.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[DesignJob]:
        stmt = select(DesignJob)
        stmt = stmt.order_by(
            DesignJob.date_created.desc() if order_desc else DesignJob.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))


class InspectionJobRepo(OrmBaseRepository[InspectionJob]):
    """Repository for managing INSPECTION jobs in Finance.inspection_job table."""

    def __init__(self, session: Session):
        super().__init__(model=InspectionJob, session=session)

    # --- CRUD ---------------------------------------------------------------

    def create_job(self, payload: JobCreate) -> InspectionJob:
        data = _payload_to_dict(payload)
        return super().create(**data)

    def update_job(self, job_id: int, payload: JobUpdate) -> Optional[InspectionJob]:
        data = _payload_to_dict(payload)
        if not data:
            return None
        return super().update(job_id, **data)

    def get_by_id(self, job_id: int) -> Optional[InspectionJob]:
        return super().get(job_id)

    def get_by_job_no(self, job_no: str) -> Optional[InspectionJob]:
        return super().find_one_by(job_no=job_no)

    def get_by_company_id(
        self,
        company_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[InspectionJob]:
        stmt = select(InspectionJob).where(InspectionJob.company_id == company_id)
        stmt = stmt.order_by(
            InspectionJob.date_created.desc()  # type: ignore
            if order_desc
            else InspectionJob.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[InspectionJob]:
        stmt = select(InspectionJob)
        stmt = stmt.order_by(
            InspectionJob.date_created.desc()  # type: ignore
            if order_desc
            else InspectionJob.date_created.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))
