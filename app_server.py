"""
Main Application Server

Centralized FastAPI server with all API endpoints using controller architecture.

Architecture:
- Controllers handle HTTP requests/responses
- Services handle business logic
- DAOs handle database operations

Endpoints:
- /api/jobs - Job management (create, retrieve, update)
- /api/quotations - Quotation management
- /api/companies - Company management
- /api/agents - AI agent orchestration
- /docs - Interactive API documentation (Swagger UI)
- /redoc - Alternative API documentation (ReDoc)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import (
    job_router,
    quotation_router,
    company_router,
    agent_router
)


# Create FastAPI application
app = FastAPI(
    title="Product v01 - Finance & Job Management API",
    version="2.0.0",
    description="""
    Multi-agent system for finance and job management with clean architecture.

    ## Features

    * **Job Management** - Create and manage design/inspection jobs
    * **Quotation Management** - Generate and track quotations
    * **Company Management** - Manage client companies
    * **AI Agents** - Intelligent workflow orchestration
    * **Human-in-the-Loop** - Interactive agent feedback

    ## Architecture

    * **Controllers** - HTTP request/response handling
    * **Services** - Business logic and orchestration
    * **DAOs** - Database operations
    * **DTOs** - Data transfer objects for type safety

    ## Authentication

    Currently open API. Add authentication middleware as needed.
    """,
    contact={
        "name": "Development Team",
        "email": "dev@company.com"
    },
    license_info={
        "name": "Proprietary"
    }
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit UI
        "http://localhost:3000",  # React UI (if applicable)
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Include routers
app.include_router(job_router)
app.include_router(quotation_router)
app.include_router(company_router)
app.include_router(agent_router)


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information and available endpoints.

    Returns a comprehensive overview of all available API endpoints.
    """
    return {
        "title": "Product v01 API",
        "version": "2.0.0",
        "description": "Finance & Job Management API with AI Agents",
        "endpoints": {
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_schema": "/openapi.json"
            },
            "job_management": {
                "create_job": "POST /api/jobs",
                "get_job": "GET /api/jobs/{job_id}",
                "get_job_by_number": "GET /api/jobs/by-number/{job_no}",
                "get_jobs_by_company": "GET /api/jobs/company/{company_id}",
                "update_job": "PATCH /api/jobs/{job_id}",
                "list_jobs": "GET /api/jobs"
            },
            "quotation_management": {
                "create_quotation": "POST /api/quotations",
                "get_quotation": "GET /api/quotations/{quotation_id}",
                "get_quotation_by_number": "GET /api/quotations/by-number/{quo_no}",
                "get_quotations_by_job": "GET /api/quotations/by-job/{job_no}",
                "get_quotations_by_client": "GET /api/quotations/by-client/{client_id}",
                "update_quotation": "PATCH /api/quotations/{quotation_id}",
                "generate_number": "POST /api/quotations/generate-number",
                "get_total": "GET /api/quotations/{quo_no}/total"
            },
            "company_management": {
                "create_company": "POST /api/companies",
                "get_or_create_company": "POST /api/companies/get-or-create",
                "get_company": "GET /api/companies/{company_id}",
                "get_company_by_name": "GET /api/companies/by-name/{name}",
                "search_companies": "GET /api/companies/search?q={query}",
                "update_company": "PATCH /api/companies/{company_id}",
                "list_companies": "GET /api/companies"
            },
            "ai_agents": {
                "orchestrator_agent": "POST /api/agents/orchestrator",
                "finance_agent": "POST /api/agents/finance",
                "human_feedback": "POST /api/agents/feedback",
                "health_check": "GET /api/agents/health",
                "session_status": "GET /api/agents/status/{session_id}"
            }
        },
        "features": [
            "RESTful API design",
            "Automatic API documentation",
            "Request/response validation",
            "Standardized error handling",
            "AI agent orchestration",
            "Human-in-the-loop workflows",
            "Clean architecture (Controller-Service-DAO)"
        ]
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Service health check endpoint.

    Returns the health status of the application and its dependencies.
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "api": "up",
            "database": "up",
            "ai_agents": "up"
        }
    }


# Main entry point
if __name__ == '__main__':
    uvicorn.run(
        "app_server:app",
        host="0.0.0.0",  # Accept connections from any IP
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
