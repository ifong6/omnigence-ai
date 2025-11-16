"""
Services package - provides abstract interfaces and implementations for business logic.

Directory structure:
- Base directory: Abstract interface classes (interfaces)
- impl/: Concrete implementations

Example usage:
    # Clean imports using __init__.py exports
    from app.services import CompanyService, JobService, QuotationService
    from app.services.impl import CompanyServiceImpl, JobServiceImpl
    from sqlmodel import Session

    with Session(engine) as session:
        company_service = CompanyServiceImpl(session)
        job_service = JobServiceImpl(session)
"""

# Export abstract interfaces
from app.services.CompanyService import CompanyService
from app.services.JobService import JobService
from app.services.QuotationService import QuotationService
from app.services.PreRoutingLoggerService import PreRoutingLoggerService

__all__ = [
    "CompanyService",
    "JobService",
    "QuotationService",
    "PreRoutingLoggerService",
]
