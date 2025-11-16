from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.controllers.BaseController import BaseController
from app.services.impl.CompanyServiceImpl import CompanyServiceImpl
from app.dto.company_dto import (
    CreateCompanyDTO,
    UpdateCompanyDTO,
    CompanyDTO,
    CompanyListResponseDTO,
    CompanySearchResponseDTO
)
from app.dto.base_response import SuccessResponse
from app.db.supabase.engine import get_session

# Create router
router = APIRouter(prefix="/api/companies", tags=["Companies"])

class CompanyController(BaseController):
    @staticmethod
    @router.post("/", response_model=SuccessResponse[CompanyDTO], status_code=201)
    @BaseController.handle_exceptions
    def create_company(
        request: CreateCompanyDTO,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request("/api/companies", request.model_dump())

        service = CompanyServiceImpl(session)

        # Create company - Service returns Model
        company = service.create(
            name=request.name,
            alias=request.alias,
            address=request.address,
            phone=request.phone
        )

        # Convert Model to DTO
        company_dto = CompanyDTO.model_validate(company)

        response = BaseController.success_response(
            data=company_dto.model_dump(),
            message="Company created successfully"
        )

        BaseController.log_response("/api/companies", response)
        return response

    @staticmethod
    @router.post("/get-or-create", response_model=SuccessResponse[CompanyDTO])
    @BaseController.handle_exceptions
    def get_or_create_company(
        request: CreateCompanyDTO,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request("/api/companies/get-or-create", request.model_dump())

        service = CompanyServiceImpl(session)

        # Get or create company - Service returns Model
        company = service.get_or_create(
            name=request.name,
            alias=request.alias,
            address=request.address,
            phone=request.phone
        )

        # Convert Model to DTO
        company_dto = CompanyDTO.model_validate(company)

        return BaseController.success_response(
            data=company_dto.model_dump(),
            message="Company retrieved or created successfully"
        )

    @staticmethod
    @router.get("/{company_id}", response_model=SuccessResponse[CompanyDTO])
    @BaseController.handle_exceptions
    def get_company(
        company_id: int,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(f"/api/companies/{company_id}", {"company_id": company_id})

        service = CompanyServiceImpl(session)
        company = service.get_by_id(company_id)

        if not company:
            raise BaseController.not_found_response(
                message=f"Company with ID {company_id} not found",
                resource_type="company",
                resource_id=str(company_id)
            )

        # Convert Model to DTO
        company_dto = CompanyDTO.model_validate(company)

        return BaseController.success_response(data=company_dto.model_dump())

    @staticmethod
    @router.get("/by-name/{name}", response_model=SuccessResponse[CompanyDTO])
    @BaseController.handle_exceptions
    def get_company_by_name(
        name: str,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(f"/api/companies/by-name/{name}", {"name": name})

        service = CompanyServiceImpl(session)
        company = service.get_by_name(name)

        if not company:
            raise BaseController.not_found_response(
                message=f"Company '{name}' not found",
                resource_type="company",
                resource_id=name
            )

        # Convert Model to DTO
        company_dto = CompanyDTO.model_validate(company)

        return BaseController.success_response(data=company_dto.model_dump())

    @staticmethod
    @router.get("/search/", response_model=SuccessResponse[CompanySearchResponseDTO])
    @BaseController.handle_exceptions
    def search_companies(
        q: str = Query(..., description="Search query (name or alias)"),
        limit: int = Query(10, description="Maximum number of results"),
        session: Session = Depends(get_session)
    ):
        BaseController.log_request("/api/companies/search", {"query": q, "limit": limit})

        service = CompanyServiceImpl(session)
        companies = service.search_by_name(search_term=q, limit=limit)

        # Convert Models to DTOs
        companies_dto = [CompanyDTO.model_validate(company) for company in companies]

        return BaseController.success_response(
            data={
                "companies": [dto.model_dump() for dto in companies_dto],
                "count": len(companies_dto)
            },
            message=f"Found {len(companies_dto)} companies matching '{q}'"
        )

    @staticmethod
    @router.patch("/{company_id}", response_model=SuccessResponse[CompanyDTO])
    @BaseController.handle_exceptions
    def update_company(
        company_id: int,
        request: UpdateCompanyDTO,
        session: Session = Depends(get_session)
    ):
        BaseController.log_request(f"/api/companies/{company_id}", request.model_dump())

        service = CompanyServiceImpl(session)

        # Check if company exists
        existing = service.get_by_id(company_id)
        if not existing:
            raise BaseController.not_found_response(
                message=f"Company with ID {company_id} not found",
                resource_type="company",
                resource_id=str(company_id)
            )

        # Update company - Service returns Model
        updated = service.update(
            company_id=company_id,
            name=request.name,
            alias=request.alias,
            address=request.address,
            phone=request.phone
        )

        if not updated:
            raise BaseController.error_response(
                message="Failed to update company",
                status_code=500
            )

        # Convert Model to DTO
        company_dto = CompanyDTO.model_validate(updated)

        return BaseController.success_response(
            data=company_dto.model_dump(),
            message="Company updated successfully"
        )

    @staticmethod
    @router.get("/", response_model=SuccessResponse[CompanyListResponseDTO])
    @BaseController.handle_exceptions
    def list_companies(
        limit: Optional[int] = Query(20, description="Maximum number of results"),
        offset: int = Query(0, description="Number of results to skip"),
        session: Session = Depends(get_session)
    ):
        BaseController.log_request("/api/companies", {"limit": limit, "offset": offset})

        service = CompanyServiceImpl(session)
        companies = service.list_all(limit=limit)

        # Convert Models to DTOs
        companies_dto = [CompanyDTO.model_validate(company) for company in companies]

        return BaseController.success_response(
            data={
                "companies": [dto.model_dump() for dto in companies_dto],
                "total_count": len(companies_dto),
                "limit": limit,
                "offset": offset
            }
        )
