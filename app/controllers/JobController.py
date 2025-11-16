from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.controllers.BaseController import BaseController
from app.services.impl.JobServiceImpl import JobServiceImpl
from app.dto.job_dtos import (
    CreateJobDTO,
    UpdateJobDTO,
    JobDTO,
    JobSearchResponseDTO
)
from app.dto.base_response import SuccessResponse
from app.db.supabase.engine import get_session

# Create router
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


class JobController(BaseController):
    @staticmethod
    @router.post("/", response_model=SuccessResponse[JobDTO], status_code=201)
    @BaseController.handle_exceptions
    def create_job(
        request: CreateJobDTO,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request("/api/jobs", request.model_dump())

        service = JobServiceImpl(session)

        job = service.create_job(
            company_id=request.company_id,
            title=request.title,
            job_type=request.job_type,
            status=getattr(request, 'status', 'NEW')
        )

        # Convert Model to DTO
        job_dto = JobDTO.model_validate(job)

        response = BaseController.success_response(
            data=job_dto.model_dump(),
            message="Job created successfully"
        )

        BaseController.log_response("/api/jobs", response)
        return response

    @staticmethod
    @router.get("/{job_id}", response_model=SuccessResponse[JobDTO])
    @BaseController.handle_exceptions
    def get_job(
        job_id: int,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(f"/api/jobs/{job_id}", {"job_id": job_id})

        service = JobServiceImpl(session)
        job = service.get_job_by_id(job_id)

        if not job:
            raise BaseController.not_found_response(
                message=f"Job with ID {job_id} not found",
                resource_type="job",
                resource_id=str(job_id)
            )

        # Convert Model to DTO
        job_dto = JobDTO.model_validate(job)

        return BaseController.success_response(data=job_dto.model_dump())

    @staticmethod
    @router.get("/by-number/{job_no}", response_model=SuccessResponse[JobDTO])
    @BaseController.handle_exceptions
    def get_job_by_number(
        job_no: str,
        session: Session = Depends(get_session)
    ):
        """
        Get job by job number.

        Path Parameters:
            - job_no: str - Job number (e.g., "JCP-25-01-1")

        Returns:
            Job details if found

        Raises:
            404 if job not found

        Example:
            GET /api/jobs/by-number/JCP-25-01-1
        """
        BaseController.log_request(f"/api/jobs/by-number/{job_no}", {"job_no": job_no})

        service = JobServiceImpl(session)
        job = service.get_job_by_job_no(job_no)

        if not job:
            raise BaseController.not_found_response(
                message=f"Job {job_no} not found",
                resource_type="job",
                resource_id=job_no
            )

        # Convert Model to DTO
        job_dto = JobDTO.model_validate(job)

        return BaseController.success_response(data=job_dto.model_dump())

    @staticmethod
    @router.get("/company/{company_id}", response_model=SuccessResponse[JobSearchResponseDTO])
    @BaseController.handle_exceptions
    def get_jobs_by_company(
        company_id: int,
        limit: Optional[int] = Query(10, description="Maximum number of results"),
        offset: int = Query(0, description="Number of results to skip"),
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(
            f"/api/jobs/company/{company_id}",
            {"company_id": company_id, "limit": limit, "offset": offset}
        )

        service = JobServiceImpl(session)
        jobs = service.get_jobs_by_company_id(
            company_id=company_id,
            limit=limit,
            offset=offset
        )

        # Convert Models to DTOs
        jobs_dto = [JobDTO.model_validate(job) for job in jobs]

        return BaseController.success_response(
            data={
                "jobs": [dto.model_dump() for dto in jobs_dto],
                "count": len(jobs_dto),
                "limit": limit,
                "offset": offset
            },
            message=f"Found {len(jobs_dto)} jobs for company {company_id}"
        )

    @staticmethod
    @router.patch("/{job_id}", response_model=SuccessResponse[JobDTO])
    @BaseController.handle_exceptions
    def update_job(
        job_id: int,
        request: UpdateJobDTO,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(f"/api/jobs/{job_id}", request.model_dump())

        service = JobServiceImpl(session)

        # Check if job exists
        existing_job = service.get_job_by_id(job_id)
        if not existing_job:
            raise BaseController.not_found_response(
                message=f"Job with ID {job_id} not found",
                resource_type="job",
                resource_id=str(job_id)
            )

        # Update job
        updated_job = service.update_job(job_id=job_id, payload=request)

        if not updated_job:
            raise BaseController.error_response(
                message="Failed to update job",
                status_code=500
            )

        # Convert Model to DTO
        job_dto = JobDTO.model_validate(updated_job)

        return BaseController.success_response(
            data=job_dto.model_dump(),
            message="Job updated successfully"
        )

    @staticmethod
    @router.get("/", response_model=SuccessResponse[JobSearchResponseDTO])
    @BaseController.handle_exceptions
    def list_jobs(
        job_type: Optional[str] = Query(None, description="Filter by job type: DESIGN or INSPECTION"),
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: Optional[int] = Query(20, description="Maximum number of results"),
        offset: int = Query(0, description="Number of results to skip"),
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(
            "/api/jobs",
            {"job_type": job_type, "status": status, "limit": limit, "offset": offset}
        )

        service = JobServiceImpl(session)

        # Get all jobs (would need filtering logic in service)
        jobs = service.list_all_jobs(limit=limit, offset=offset)

        # Convert Models to DTOs
        jobs_dto = [JobDTO.model_validate(job) for job in jobs]

        return BaseController.success_response(
            data={
                "jobs": [dto.model_dump() for dto in jobs_dto],
                "count": len(jobs_dto),
                "limit": limit,
                "offset": offset
            }
        )
