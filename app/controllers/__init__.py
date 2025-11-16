"""
Controllers Package

This package contains all API controllers following the REST architecture.

Controllers provide:
- HTTP request/response handling
- Request validation (via Pydantic models)
- Response formatting (standardized JSON responses)
- Error handling and exception mapping
- API documentation (via FastAPI)
- Separation between HTTP layer and business logic (Service layer)

Architecture:
- Controller → Service → DAO → Database
- Controller handles: HTTP requests, validation, response formatting
- Service handles: Business logic, transaction management, orchestration
- DAO handles: Database operations, queries, ORM

Example usage:
    # Clean imports using __init__.py exports
    from app.controllers import (
        JobController,
        QuotationController,
        CompanyController,
        AgentController
    )
    from app.controllers.job_controller import router as job_router
    from fastapi import FastAPI

    # Create FastAPI app
    app = FastAPI()

    # Include routers
    app.include_router(job_router)
    app.include_router(quotation_router)
    app.include_router(company_router)
    app.include_router(agent_router)

Router Exports:
    All controller modules export FastAPI routers that can be included
    in the main application:

    - job_router: /api/jobs endpoints
    - quotation_router: /api/quotations endpoints
    - company_router: /api/companies endpoints
    - agent_router: /api/agents endpoints
"""

# Base controller
from app.controllers.base_controller import BaseController

# Specific controllers
from app.controllers.job_controller import JobController, router as job_router
from app.controllers.quotation_controller import QuotationController, router as quotation_router
from app.controllers.company_controller import CompanyController, router as company_router
from app.controllers.agent_controller import AgentController, router as agent_router


__all__ = [
    # Base controller
    "BaseController",
    # Controller classes
    "JobController",
    "QuotationController",
    "CompanyController",
    "AgentController",
    # Routers for FastAPI app
    "job_router",
    "quotation_router",
    "company_router",
    "agent_router",
]
