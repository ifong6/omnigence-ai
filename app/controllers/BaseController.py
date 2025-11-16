from typing import Any, Dict, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status
from app.dto.base_response import (
    create_success_response,
    create_error_response,
    create_invalid_request_response,
    create_not_found_response,
    create_validation_error_response,
)

class BaseController:
    @staticmethod
    def success_response(data: Any, message: str = "Operation completed successfully") -> Dict[str, Any]:
        return create_success_response(data=data, message=message)

    @staticmethod
    def error_response(
        message: str,
        errors: Optional[list] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> HTTPException:
        response = create_error_response(message=message, errors=errors or [])
        raise HTTPException(status_code=status_code, detail=response)

    @staticmethod
    def invalid_request_response(
        message: str,
        reason: Optional[str] = None,
        suggestions: Optional[list] = None
    ) -> Dict[str, Any]:
        return create_invalid_request_response(
            message=message,
            reason=reason,
            suggestions=suggestions or []
        )

    @staticmethod
    def not_found_response(
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> HTTPException:
        response = create_not_found_response(
            message=message,
            resource_type=resource_type,
            resource_id=resource_id
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response)

    @staticmethod
    def validation_error_response(
        errors: list,
        message: str = "Validation failed"
    ) -> HTTPException:
        response = create_validation_error_response(errors=errors, message=message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response)

    @staticmethod
    def handle_exceptions(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions (already formatted)
                raise
            except ValueError as e:
                # Validation errors
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=create_error_response(
                        message="Invalid input",
                        errors=[{"code": "VALIDATION_ERROR", "message": str(e)}]
                    )
                )
            except PermissionError as e:
                # Permission errors
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=create_error_response(
                        message="Permission denied",
                        errors=[{"code": "PERMISSION_DENIED", "message": str(e)}]
                    )
                )
            except Exception as e:
                # Generic errors
                print(f"[ERROR][{func.__name__}]: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=create_error_response(
                        message="Internal server error",
                        errors=[{"code": "INTERNAL_ERROR", "message": str(e)}]
                    )
                )
        return wrapper

    @staticmethod
    def log_request(endpoint: str, data: Any) -> None:
        print(f"[REQUEST][{endpoint}] Received: {data}")

    @staticmethod
    def log_response(endpoint: str, response: Any) -> None:
        print(f"[RESPONSE][{endpoint}] Sent: {response}")
