from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status codes."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"


class ErrorDetail(BaseModel):
    """Detailed error information."""
    model_config = ConfigDict(from_attributes=True)

    field: Optional[str] = Field(None, description="Field that caused the error")
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")


# Generic type for data payload
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """
    Base response model for all API responses.

    This provides a consistent structure for success and error responses.

    Example:
        Success:
        {
            "status": "success",
            "message": "Operation completed successfully",
            "data": {...},
            "timestamp": "2025-01-15T10:30:00Z"
        }

        Error:
        {
            "status": "error",
            "message": "Validation failed",
            "errors": [
                {
                    "field": "email",
                    "code": "INVALID_FORMAT",
                    "message": "Email format is invalid"
                }
            ],
            "timestamp": "2025-01-15T10:30:00Z"
        }
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(..., description="Response status indicator")
    message: str = Field(..., description="Human-readable message")
    data: Optional[T] = Field(None, description="Response payload (optional)")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Error details (if any)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID (optional)")


class SuccessResponse(BaseModel, Generic[T]):
    """
    Success response with data payload.

    Use this when an operation completes successfully and returns data.
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Always 'success'")
    message: str = Field(default="Operation completed successfully", description="Success message")
    data: T = Field(..., description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class ErrorResponse(BaseModel):
    """
    Error response for failed operations.

    Use this when an operation fails or validation errors occur.
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Error status")
    message: str = Field(..., description="Error summary message")
    errors: List[ErrorDetail] = Field(default_factory=list, description="Detailed error list")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class InvalidRequestResponse(BaseModel):
    """
    Response for invalid requests that don't match the workflow.

    Use this when a user's request cannot be processed by the current workflow.

    Example:
        {
            "status": "invalid",
            "message": "This request cannot be processed by the quotation workflow",
            "reason": "The request appears to be related to HR operations, not finance",
            "suggestions": [
                "Please use the HR workflow for employee-related requests",
                "Contact support if you need help routing your request"
            ],
            "timestamp": "2025-01-15T10:30:00Z"
        }
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.INVALID, description="Always 'invalid'")
    message: str = Field(..., description="Why the request is invalid")
    reason: Optional[str] = Field(None, description="Detailed explanation")
    suggestions: List[str] = Field(default_factory=list, description="Helpful suggestions for the user")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class ValidationErrorResponse(BaseModel):
    """
    Response for validation errors.

    Use this when input data fails validation.
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Always 'error'")
    message: str = Field(default="Validation failed", description="Error message")
    errors: List[ErrorDetail] = Field(..., description="List of validation errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class NotFoundResponse(BaseModel):
    """
    Response for resource not found errors.

    Use this when a requested resource doesn't exist.
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.NOT_FOUND, description="Always 'not_found'")
    message: str = Field(..., description="What was not found")
    resource_type: Optional[str] = Field(None, description="Type of resource (e.g., 'quotation', 'job')")
    resource_id: Optional[str] = Field(None, description="ID of the missing resource")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Response for paginated data.

    Use this when returning lists with pagination.

    Example:
        {
            "status": "success",
            "message": "Retrieved quotations successfully",
            "data": [...],
            "pagination": {
                "page": 1,
                "page_size": 20,
                "total_items": 150,
                "total_pages": 8
            },
            "timestamp": "2025-01-15T10:30:00Z"
        }
    """
    model_config = ConfigDict(from_attributes=True)

    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    message: str = Field(..., description="Response message")
    data: List[T] = Field(..., description="List of items")
    pagination: Dict[str, int] = Field(
        ...,
        description="Pagination info: page, page_size, total_items, total_pages"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


# ============================================================================
# Helper Functions
# ============================================================================

def create_success_response(
    data: Any,
    message: str = "Operation completed successfully",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper function to create a success response.

    Args:
        data: The response data payload
        message: Success message (optional)
        request_id: Request tracking ID (optional)

    Returns:
        Dictionary representing the success response

    Example:
        >>> response = create_success_response(
        ...     data={"quotation_id": 123},
        ...     message="Quotation created successfully"
        ... )
    """
    return SuccessResponse(
        message=message,
        data=data,
        request_id=request_id
    ).model_dump()


def create_error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper function to create an error response.

    Args:
        message: Error summary message
        errors: List of detailed errors (optional)
        request_id: Request tracking ID (optional)

    Returns:
        Dictionary representing the error response

    Example:
        >>> response = create_error_response(
        ...     message="Failed to create quotation",
        ...     errors=[{"code": "INVALID_COMPANY", "message": "Company not found"}]
        ... )
    """
    error_details = []
    if errors:
        error_details = [ErrorDetail(**err) for err in errors]

    return ErrorResponse(
        message=message,
        errors=error_details,
        request_id=request_id
    ).model_dump()


def create_invalid_request_response(
    message: str,
    reason: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper function to create an invalid request response.

    Args:
        message: Why the request is invalid
        reason: Detailed explanation (optional)
        suggestions: List of helpful suggestions (optional)
        request_id: Request tracking ID (optional)

    Returns:
        Dictionary representing the invalid request response

    Example:
        >>> response = create_invalid_request_response(
        ...     message="Request not valid for quotation workflow",
        ...     reason="This appears to be an HR-related request",
        ...     suggestions=["Use the HR workflow", "Contact support for help"]
        ... )
    """
    return InvalidRequestResponse(
        message=message,
        reason=reason,
        suggestions=suggestions or [],
        request_id=request_id
    ).model_dump()


def create_not_found_response(
    message: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper function to create a not found response.

    Args:
        message: What was not found
        resource_type: Type of resource (e.g., 'quotation')
        resource_id: ID of the missing resource
        request_id: Request tracking ID (optional)

    Returns:
        Dictionary representing the not found response

    Example:
        >>> response = create_not_found_response(
        ...     message="Quotation not found",
        ...     resource_type="quotation",
        ...     resource_id="Q-JCP-25-01-1"
        ... )
    """
    return NotFoundResponse(
        message=message,
        resource_type=resource_type,
        resource_id=resource_id,
        request_id=request_id
    ).model_dump()


def create_validation_error_response(
    errors: List[Dict[str, Any]],
    message: str = "Validation failed",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper function to create a validation error response.

    Args:
        errors: List of validation errors
        message: Error message (optional)
        request_id: Request tracking ID (optional)

    Returns:
        Dictionary representing the validation error response

    Example:
        >>> response = create_validation_error_response(
        ...     errors=[
        ...         {"field": "email", "code": "INVALID_FORMAT", "message": "Invalid email"},
        ...         {"field": "age", "code": "OUT_OF_RANGE", "message": "Age must be positive"}
        ...     ]
        ... )
    """
    error_details = [ErrorDetail(**err) for err in errors]

    return ValidationErrorResponse(
        message=message,
        errors=error_details,
        request_id=request_id
    ).model_dump()
