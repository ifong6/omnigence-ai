"""
Job DTOs (Data Transfer Objects): Pydantic models for job service responses.

DTOs provide:
1. Type safety and validation
2. Clear API contracts
3. Separation between database models and API responses
4. Consistent serialization format
5. Documentation via field descriptions
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# OUTPUT DTOs (Response Models)
# ============================================================================

class JobDTO(BaseModel):
    """
    Base DTO for job responses.

    This represents the data structure returned by service methods.
    It's decoupled from the database model (DesignJob/InspectionJob).
    """
    model_config = ConfigDict(from_attributes=True)  # Allows creation from ORM objects

    id: int = Field(..., description="Job ID")
    job_no: str = Field(..., description="Job number (e.g., JCP-25-01-1)")
    company_id: int = Field(..., description="Associated company ID")
    title: str = Field(..., description="Job title")
    status: str = Field(..., description="Job status (NEW, IN_PROGRESS, etc.)")
    quotation_status: str = Field(..., description="Quotation status (NOT_CREATED, DRAFTED, etc.)")
    quotation_issued_at: Optional[datetime] = Field(None, description="Quotation issue timestamp")
    date_created: datetime = Field(..., description="Job creation timestamp")

    # Note: We can add computed fields, format transformations, etc. here
    # without affecting the database model


class JobWithCompanyDTO(JobDTO):
    """
    DTO for job with company information.

    Extends JobDTO with additional company details from JOIN queries.
    """
    company_name: str = Field(..., description="Company name")

    # Optional: Add more company fields if needed
    company_address: Optional[str] = Field(None, description="Company address")
    company_phone: Optional[str] = Field(None, description="Company phone")


class JobListResponseDTO(BaseModel):
    """
    DTO for paginated job list responses.

    This wraps a list of jobs with metadata (useful for pagination).
    """
    jobs: list[JobWithCompanyDTO] = Field(..., description="List of jobs")
    total_count: int = Field(..., description="Total number of jobs")
    limit: Optional[int] = Field(None, description="Applied limit")


# ============================================================================
# INPUT DTOs (Request Models)
# ============================================================================

class CreateJobDTO(BaseModel):
    """
    DTO for job creation requests.

    This validates input data before it reaches the service layer.
    """
    company_id: int = Field(..., description="Company ID (foreign key)", gt=0)
    title: str = Field(..., description="Job title", min_length=1, max_length=255)
    job_type: str = Field(..., description="Job type (DESIGN or INSPECTION)")
    index: int = Field(default=1, description="Item index", ge=1)
    status: str = Field(default="NEW", description="Initial job status")
    quotation_status: str = Field(default="NOT_CREATED", description="Initial quotation status")

    # Pydantic validators can be added here
    @property
    def is_valid_job_type(self) -> bool:
        return self.job_type in ["DESIGN", "INSPECTION"]


class UpdateJobDTO(BaseModel):
    """
    DTO for job update requests.

    All fields are optional (only provided fields will be updated).
    """
    title: Optional[str] = Field(None, description="New job title", min_length=1, max_length=255)
    status: Optional[str] = Field(None, description="New status")
    quotation_status: Optional[str] = Field(None, description="New quotation status")
    quotation_issued_at: Optional[datetime] = Field(None, description="Quotation issue date")


# ============================================================================
# OPERATION RESULT DTOs
# ============================================================================

class JobCreatedResponseDTO(BaseModel):
    """
    DTO for job creation response.

    Returns the created job with additional metadata.
    """
    job: JobDTO = Field(..., description="Created job details")
    message: str = Field(default="Job created successfully", description="Success message")


class JobUpdatedResponseDTO(BaseModel):
    """
    DTO for job update response.
    """
    job: JobDTO = Field(..., description="Updated job details")
    message: str = Field(default="Job updated successfully", description="Success message")
    fields_updated: list[str] = Field(default_factory=list, description="List of updated fields")


class JobNotFoundDTO(BaseModel):
    """
    DTO for job not found error.
    """
    error: str = Field(default="Job not found", description="Error message")
    job_id: Optional[int] = Field(None, description="Job ID that was not found")
    job_type: Optional[str] = Field(None, description="Job type that was queried")


# ============================================================================
# EXAMPLE USAGE IN DOCSTRINGS
# ============================================================================

"""
BEFORE (Without DTOs):
---------------------
# Service returns raw ORM object
job = service.create_job(company_id=15, title="空調系統設計", job_type="DESIGN")
# Problem: Exposes database model directly, no validation, unclear what fields are available

# Service returns plain dict
jobs = service.list_all_with_company("DESIGN", limit=10)
# Problem: No type safety, shape of dict is unclear, easy to make typos


AFTER (With DTOs):
------------------
# Input is validated
create_dto = CreateJobDTO(
    company_id=15,
    title="空調系統設計",
    job_type="DESIGN"
)
# If company_id is negative or title is empty, Pydantic raises ValidationError

# Service returns typed DTO
response: JobCreatedResponseDTO = service.create_job(create_dto)
job_dto: JobDTO = response.job
# IDE knows all fields: job_dto.id, job_dto.job_no, etc.
# Type checking catches errors at development time

# List returns typed DTO
response: JobListResponseDTO = service.list_all_with_company("DESIGN", limit=10)
for job in response.jobs:
    print(f"{job.job_no}: {job.title} ({job.company_name})")
# Clear structure, autocomplete works, type-safe
"""
