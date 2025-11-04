from typing import Literal, TypedDict, NotRequired
from datetime import datetime

# Type aliases
JobType = Literal["DESIGN", "INSPECTION"]
JobStatus = Literal["NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
QuotationStatus = Literal["NOT_CREATED", "CREATED", "ISSUED", "ACCEPTED", "REJECTED", "EXPIRED"]


class JobRow(TypedDict, total=True):
    """
    Row shape returned from the database for job tables.

    Used for both design_job and inspection_job tables.
    Note: 'type' field removed as it doesn't exist in DB tables (table name indicates job type)

    All fields are required when returned from database (total=True).
    Optional fields use NotRequired or have None as possible value.
    """
    id: int
    company_id: int
    title: str
    status: JobStatus
    job_no: str | None  # Can be None if not yet assigned
    date_created: datetime
    quotation_status: QuotationStatus | None  # Can be None
    quotation_issued_at: datetime | None  # Can be None


class JobCreate(TypedDict, total=False):
    """
    Payload for creating a new job.

    Only includes fields that can be set during creation.
    Note: 'type' field removed as it doesn't exist in DB tables (table name indicates job type)

    total=False means all fields are optional in the dict literal,
    but individually some are required for the business logic.
    """
    company_id: int  # Required
    title: str  # Required
    job_no: str | None  # Optional
    status: JobStatus  # Required
    quotation_status: QuotationStatus | None  # Optional


class JobUpdate(TypedDict, total=False):
    """
    Payload for updating an existing job.

    All fields are optional - only provided fields will be updated.
    total=False makes all keys optional in the TypedDict.
    """
    title: str | None
    status: JobStatus | None
    job_no: str | None
    quotation_status: QuotationStatus | None
    quotation_issued_at: datetime | None
