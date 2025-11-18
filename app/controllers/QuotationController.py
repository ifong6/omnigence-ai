from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.controllers.BaseController import BaseController
from app.services.impl import QuotationServiceImpl
from app.dto.quotation_dto import (
    CreateQuotationDTO,
    UpdateQuotationDTO,
    QuotationDTO,
    QuotationSearchResponseDTO,
    QuotationCreateResponseDTO
)
from app.dto.base_response import SuccessResponse
from app.db.supabase.engine import get_session


# Create router
router = APIRouter(prefix="/api/quotations", tags=["Quotations"])


class QuotationController(BaseController):
    """
    Controller for quotation management endpoints.

    Provides REST API endpoints for:
    - Creating quotations with line items
    - Retrieving quotations by ID, number, job, or client
    - Updating quotation status and details
    - Generating quotation numbers
    - Calculating totals
    """

    @staticmethod
    @router.post("/", response_model=SuccessResponse[QuotationCreateResponseDTO], status_code=201)
    @BaseController.handle_exceptions
    def create_quotation(
        request: CreateQuotationDTO,
        session: Session = Depends(get_session)
    ):
        """
        Create a new quotation with line items.

        Request Body:
            - job_no: str - Associated job number
            - company_id: int - Client company ID
            - project_name: str - Project name
            - items: List[CreateQuotationItemDTO] - Line items
            - currency: str (optional) - Currency code (default: "MOP")
            - date_issued: date (optional) - Issue date (default: today)
            - revision_no: str (optional) - Revision number (00=no revision, 01/02/etc=revision)
            - valid_until: date (optional) - Validity end date
            - notes: str (optional) - Additional notes

        Returns:
            Created quotation with items and generated quotation number

        Example:
            POST /api/quotations
            {
                "job_no": "JCP-25-01-1",
                "company_id": 123,
                "project_name": "Office Renovation",
                "currency": "MOP",
                "items": [
                    {
                        "item_desc": "Design Services",
                        "quantity": 1,
                        "unit": "Lot",
                        "unit_price": 50000.00
                    }
                ]
            }
        """
        BaseController.log_request("/api/quotations", request.model_dump())

        # Initialize service
        service = QuotationServiceImpl(session)

        # Create quotation
        result = service.create_quotation(
            job_no=request.job_no,
            company_id=request.company_id,
            project_name=request.project_name,
            items=[item.model_dump() for item in request.items],
            currency=request.currency,
            date_issued=request.date_issued,
            revision_no=request.revision_no,
            valid_until=request.valid_until,
            notes=request.notes
        )

        # Convert Models to DTOs in the result
        quotations_dto = [
            QuotationDTO.model_validate(q) for q in result.get("quotations", [])
        ]

        response_data = {
            "quotations": [dto.model_dump() for dto in quotations_dto],
            "quo_no": result.get("quo_no"),
            "total": float(result.get("total", 0)),
            "item_count": result.get("item_count", 0)
        }

        response = BaseController.success_response(
            data=response_data,
            message="Quotation created successfully"
        )

        BaseController.log_response("/api/quotations", response)
        return response

    @staticmethod
    @router.get("/{quotation_id}", response_model=SuccessResponse[QuotationDTO])
    @BaseController.handle_exceptions
    def get_quotation(
        quotation_id: int,
        session: Session = Depends(get_session)
    ):
        """
        Get quotation by ID.

        Path Parameters:
            - quotation_id: int - Quotation ID

        Returns:
            Quotation details with line items

        Raises:
            404 if quotation not found

        Example:
            GET /api/quotations/123
        """
        BaseController.log_request(f"/api/quotations/{quotation_id}", {"quotation_id": quotation_id})

        service = QuotationServiceImpl(session)
        quotation = service.get_quotation_by_id(quotation_id)

        if not quotation:
            raise BaseController.not_found_response(
                message=f"Quotation with ID {quotation_id} not found",
                resource_type="quotation",
                resource_id=str(quotation_id)
            )

        # Convert Model to DTO
        quotation_dto = QuotationDTO.model_validate(quotation)

        return BaseController.success_response(data=quotation_dto.model_dump())

    @staticmethod
    @router.get("/by-number/{quo_no}", response_model=SuccessResponse[QuotationDTO])
    @BaseController.handle_exceptions
    def get_quotation_by_number(
        quo_no: str,
        session: Session = Depends(get_session)
    ):
        """
        Get quotation by quotation number.

        Path Parameters:
            - quo_no: str - Quotation number (e.g., "Q-JCP-25-01-1")

        Returns:
            Quotation details if found

        Raises:
            404 if quotation not found

        Example:
            GET /api/quotations/by-number/Q-JCP-25-01-1
        """
        BaseController.log_request(f"/api/quotations/by-number/{quo_no}", {"quo_no": quo_no})

        service = QuotationServiceImpl(session)
        quotation = service.get_quotation_by_quo_no(quo_no)

        if not quotation:
            raise BaseController.not_found_response(
                message=f"Quotation {quo_no} not found",
                resource_type="quotation",
                resource_id=quo_no
            )

        # Convert Model to DTO
        quotation_dto = QuotationDTO.model_validate(quotation)

        return BaseController.success_response(data=quotation_dto.model_dump())

    @staticmethod
    @router.get("/by-job/{job_no}", response_model=SuccessResponse[QuotationSearchResponseDTO])
    @BaseController.handle_exceptions
    def get_quotations_by_job(
        job_no: str,
        session: Session = Depends(get_session)
    ):
        """
        Get all quotations for a specific job.

        Path Parameters:
            - job_no: str - Job number (e.g., "JCP-25-01-1")

        Returns:
            List of quotations for the job

        Example:
            GET /api/quotations/by-job/JCP-25-01-1
        """
        BaseController.log_request(f"/api/quotations/by-job/{job_no}", {"job_no": job_no})

        service = QuotationServiceImpl(session)
        quotations = service.get_by_job_no(job_no)

        # Convert Models to DTOs
        quotations_dto = [QuotationDTO.model_validate(q) for q in quotations]

        return BaseController.success_response(
            data={
                "quotations": [dto.model_dump() for dto in quotations_dto],
                "count": len(quotations_dto)
            },
            message=f"Found {len(quotations_dto)} quotations for job {job_no}"
        )

    @staticmethod
    @router.get("/by-client/{client_id}", response_model=SuccessResponse[QuotationSearchResponseDTO])
    @BaseController.handle_exceptions
    def get_quotations_by_client(
        client_id: int,
        limit: Optional[int] = Query(10, description="Maximum number of results"),
        session: Session = Depends(get_session)
    ): 
        BaseController.log_request(
            f"/api/quotations/by-client/{client_id}",
            {"client_id": client_id, "limit": limit}
        )

        service = QuotationServiceImpl(session)
        quotations = service.get_quotations_by_client(
            client_id=client_id,
            limit=limit,
        )

        # Convert Models to DTOs
        quotations_dto = [QuotationDTO.model_validate(q) for q in quotations]

        return BaseController.success_response(
            data={
                "quotations": [dto.model_dump() for dto in quotations_dto],
                "count": len(quotations_dto)
            }
        )

    @staticmethod
    @router.patch("/{quotation_id}", response_model=SuccessResponse[QuotationDTO])
    @BaseController.handle_exceptions
    def update_quotation(
        quotation_id: int,
        request: UpdateQuotationDTO,
        session: Session = Depends(get_session)
    ): 
        BaseController.log_request(f"/api/quotations/{quotation_id}", request.model_dump())

        service = QuotationServiceImpl(session)

        # Check if quotation exists
        existing = service.get_quotation_by_id(quotation_id)
        if not existing:
            raise BaseController.not_found_response(
                message=f"Quotation with ID {quotation_id} not found",
                resource_type="quotation",
                resource_id=str(quotation_id)
            )

        # Update quotation
        updated = service.update_quotation(quotation_ids=[quotation_id], **request.model_dump())

        if not updated:
            raise BaseController.error_response(
                message="Failed to update quotation",
                status_code=500
            )

        # Convert Model to DTO
        quotation_dto = QuotationDTO.model_validate(updated)

        return BaseController.success_response(
            data=quotation_dto.model_dump(),
            message="Quotation updated successfully"
        )

    @staticmethod
    @router.post("/generate-number", response_model=dict)
    @BaseController.handle_exceptions
    def generate_quotation_number(
        job_no: str = Query(..., description="Job number"),
        revision_no: str = Query("00", description="Revision number (00=no revision, 01/02/etc=revision)"),
        session: Session = Depends(get_session)
    ):
        """
        Generate a quotation number for a job.

        Query Parameters:
            - job_no: str - Job number (e.g., "JCP-25-01-1")
            - revision_no: str (optional) - Revision number (default: "00")

        Returns:
            Generated quotation number

        Example:
            POST /api/quotations/generate-number?job_no=JCP-25-01-1&revision_no=00
        """
        BaseController.log_request(
            "/api/quotations/generate-number",
            {"job_no": job_no, "revision_no": revision_no}
        )

        service = QuotationServiceImpl(session)
        quo_no = service.generate_quotation_number(job_no=job_no, revision_no=revision_no)

        return BaseController.success_response(
            data={"quotation_number": quo_no},
            message="Quotation number generated successfully"
        )

    @staticmethod
    @router.get("/{quo_no}/total", response_model=dict)
    @BaseController.handle_exceptions
    def get_quotation_total(
        quo_no: str,
        session: Session = Depends(get_session)
    ):
        """
        Calculate total amount for a quotation.

        Path Parameters:
            - quo_no: str - Quotation number

        Returns:
            Total amount and item count

        Example:
            GET /api/quotations/Q-JCP-25-01-1/total
        """
        BaseController.log_request(f"/api/quotations/{quo_no}/total", {"quo_no": quo_no})

        service = QuotationServiceImpl(session)
        total_info = service.get_quotation_total(quo_no)

        return BaseController.success_response(
            data=total_info,
            message="Total calculated successfully"
        )
