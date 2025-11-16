from typing import Optional, Any, Dict


# =============================================================================
# Base Application Exceptions
# =============================================================================

class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception

    def __str__(self) -> str:
        """String representation of the error."""
        base = f"{self.__class__.__name__}: {self.message}"
        if self.details:
            base += f" | Details: {self.details}"
        if self.original_exception:
            base += f" | Caused by: {type(self.original_exception).__name__}: {self.original_exception}"
        return base


# =============================================================================
# Business Logic Exceptions
# =============================================================================

class BusinessError(ApplicationError):
    pass


class ValidationError(BusinessError):
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)
        self.field = field
        self.value = value


class StateConflictError(BusinessError):
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        attempted_action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if current_state:
            details["current_state"] = current_state
        if attempted_action:
            details["attempted_action"] = attempted_action
        super().__init__(message, details)


class NotFoundError(BusinessError):
    def __init__(
        self,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if entity_type:
            details["entity_type"] = entity_type
        if entity_id is not None:
            details["entity_id"] = entity_id
        super().__init__(message, details)


# =============================================================================
# Data Persistence Exceptions
# =============================================================================

class PersistenceError(ApplicationError):
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        details = details or {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        super().__init__(message, details, original_exception)


class DatabaseConnectionError(PersistenceError):
    pass


class UniqueConstraintError(PersistenceError):
    def __init__(
        self,
        message: str,
        constraint: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if constraint:
            details["constraint"] = constraint
        if value is not None:
            details["duplicate_value"] = value
        super().__init__(message, details=details)


# =============================================================================
# Tool/Agent Exceptions
# =============================================================================

class ToolInputError(ValidationError):
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if tool_name:
            details["tool_name"] = tool_name
        super().__init__(message, details=details)


class AgentExecutionError(ApplicationError):
    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        node_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        details = details or {}
        if agent_name:
            details["agent_name"] = agent_name
        if node_name:
            details["node_name"] = node_name
        super().__init__(message, details, original_exception)

#--------------------------------------------------------
# HUMAN IN THE LOOP INTERRUPTION EXCEPTION
#--------------------------------------------------------

class InterruptException(Exception):
    """
    Exception for human-in-the-loop interruptions in LangGraph flows.

    This follows the LangGraph interrupt pattern for pausing graph execution
    and requesting user input.
    """
    def __init__(
        self,
        state: Any,
        value: Any,
        resumable: bool = True,
        ns: Optional[str] = None
    ):
        super().__init__(str(value))
        self.state = state
        self.value = value
        self.resumable = resumable
        self.ns = ns


# =============================================================================
# LLM/External Service Exceptions
# =============================================================================

class ExternalServiceError(ApplicationError):
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):  
        details = details or {}
        if service_name:
            details["service_name"] = service_name
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, details, original_exception)
