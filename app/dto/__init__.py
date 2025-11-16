"""
DTO (Data Transfer Objects) Package

This package contains all DTOs used for service layer communication.

DTOs provide:
- Type safety and validation (via Pydantic)
- Clear API contracts
- Separation between database models and API responses
- Consistent serialization format
- Documentation via field descriptions

Usage:
    from app.dto.quotation_dto import CreateQuotationDTO, QuotationWithItemsDTO
    from app.dto.invoice_dto import CreateInvoiceDTO, InvoiceDTO
    from app.dto.job_dtos import CreateJobDTO, JobDTO
"""

# Quotation DTOs
from app.dto.quotation_dto import (
    QuotationDTO,
    QuotationItemDTO,
    QuotationWithItemsDTO,
    QuotationWithClientDTO,
    CreateQuotationDTO,
    CreateQuotationItemDTO,
    UpdateQuotationDTO,
    QuotationCreatedResponseDTO,
    QuotationUpdatedResponseDTO,
    QuotationNotFoundDTO,
    QuotationSummaryDTO,
    QuotationSearchDTO,
    QuotationStatus,
)

# Invoice DTOs
from app.dto.invoice_dto import (
    InvoiceDTO,
    InvoiceItemDTO,
    InvoiceWithItemsDTO,
    InvoiceWithClientDTO,
    InvoiceWithPaymentsDTO,
    CreateInvoiceDTO,
    CreateInvoiceItemDTO,
    CreateInvoiceFromQuotationDTO,
    UpdateInvoiceDTO,
    RecordPaymentDTO,
    PaymentRecordDTO,
    InvoiceCreatedResponseDTO,
    InvoiceUpdatedResponseDTO,
    PaymentRecordedResponseDTO,
    InvoiceNotFoundDTO,
    InvoiceSummaryDTO,
    InvoiceSearchDTO,
    InvoiceStatus,
    PaymentStatus,
    PaymentMethod,
)

# Job DTOs
from app.dto.job_dtos import (
    JobDTO,
    JobWithCompanyDTO,
    JobListResponseDTO,
    CreateJobDTO,
    UpdateJobDTO,
    JobCreatedResponseDTO,
    JobUpdatedResponseDTO,
    JobNotFoundDTO,
)

# Company DTOs
from app.dto.company_dto import (
    CompanyDTO,
    CompanyWithStatsDTO,
    CompanyListResponseDTO,
    CreateCompanyDTO,
    UpdateCompanyDTO,
    GetOrCreateCompanyDTO,
    SearchCompanyDTO,
    CompanyCreatedResponseDTO,
    CompanyUpdatedResponseDTO,
    CompanyNotFoundDTO,
    CompanyGetOrCreateResponseDTO,
    CompanyEnrichedResponseDTO,
    CompanyAliasGeneratedResponseDTO,
)

# Pre-routing DTOs
from app.dto.pre_routing_dto import (
    PreRoutingLoggerRequestDTO,
    PreRoutingLoggerResponseDTO,
    PreRoutingLoggerResultDTO,
)

# Agent Flow DTOs
from app.dto.agent_dto import (
    AgentFlowRequestDTO,
    FinanceAgentFlowRequestDTO,
    RequestBody,  # Backward compatibility alias
)

# Base Response DTOs
from app.dto.base_response import (
    # Response Models
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    InvalidRequestResponse,
    ValidationErrorResponse,
    NotFoundResponse,
    PaginatedResponse,
    # Supporting Models
    ResponseStatus,
    ErrorDetail,
    # Helper Functions
    create_success_response,
    create_error_response,
    create_invalid_request_response,
    create_not_found_response,
    create_validation_error_response,
)

__all__ = [
    # Quotation DTOs
    "QuotationDTO",
    "QuotationItemDTO",
    "QuotationWithItemsDTO",
    "QuotationWithClientDTO",
    "CreateQuotationDTO",
    "CreateQuotationItemDTO",
    "UpdateQuotationDTO",
    "QuotationCreatedResponseDTO",
    "QuotationUpdatedResponseDTO",
    "QuotationNotFoundDTO",
    "QuotationSummaryDTO",
    "QuotationSearchDTO",
    "QuotationStatus",
    # Invoice DTOs
    "InvoiceDTO",
    "InvoiceItemDTO",
    "InvoiceWithItemsDTO",
    "InvoiceWithClientDTO",
    "InvoiceWithPaymentsDTO",
    "CreateInvoiceDTO",
    "CreateInvoiceItemDTO",
    "CreateInvoiceFromQuotationDTO",
    "UpdateInvoiceDTO",
    "RecordPaymentDTO",
    "PaymentRecordDTO",
    "InvoiceCreatedResponseDTO",
    "InvoiceUpdatedResponseDTO",
    "PaymentRecordedResponseDTO",
    "InvoiceNotFoundDTO",
    "InvoiceSummaryDTO",
    "InvoiceSearchDTO",
    "InvoiceStatus",
    "PaymentStatus",
    "PaymentMethod",
    # Job DTOs
    "JobDTO",
    "JobWithCompanyDTO",
    "JobListResponseDTO",
    "CreateJobDTO",
    "UpdateJobDTO",
    "JobCreatedResponseDTO",
    "JobUpdatedResponseDTO",
    "JobNotFoundDTO",
    # Company DTOs
    "CompanyDTO",
    "CompanyWithStatsDTO",
    "CompanyListResponseDTO",
    "CreateCompanyDTO",
    "UpdateCompanyDTO",
    "GetOrCreateCompanyDTO",
    "SearchCompanyDTO",
    "CompanyCreatedResponseDTO",
    "CompanyUpdatedResponseDTO",
    "CompanyNotFoundDTO",
    "CompanyGetOrCreateResponseDTO",
    "CompanyEnrichedResponseDTO",
    "CompanyAliasGeneratedResponseDTO",
    # Pre-routing DTOs
    "PreRoutingLoggerRequestDTO",
    "PreRoutingLoggerResponseDTO",
    "PreRoutingLoggerResultDTO",
    # Agent Flow DTOs
    "AgentFlowRequestDTO",
    "FinanceAgentFlowRequestDTO",
    "RequestBody",
    # Base Response DTOs
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "InvalidRequestResponse",
    "ValidationErrorResponse",
    "NotFoundResponse",
    "PaginatedResponse",
    "ResponseStatus",
    "ErrorDetail",
    "create_success_response",
    "create_error_response",
    "create_invalid_request_response",
    "create_not_found_response",
    "create_validation_error_response",
]
