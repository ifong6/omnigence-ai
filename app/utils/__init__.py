"""
Utils Package

This package contains utility modules for the application.
"""

# Exceptions
from app.utils.exceptions import (
    ApplicationError,
    BusinessError,
    ValidationError,
    StateConflictError,
    NotFoundError,
    PersistenceError,
    DatabaseConnectionError,
    UniqueConstraintError,
    ToolInputError,
    AgentExecutionError,
    ExternalServiceError,
)

# Validators
from app.utils.validators import (
    parse_tool_input,
    parse_tool_input_as_string,
    validate_required_fields,
    validate_positive_number,
    validate_date_range,
    validate_string_length,
    validate_enum_value,
    validate_non_empty_list,
    validate_job_number_format,
    validate_email_format,
    validate_phone_format,
)

# Helpers
from app.utils.helpers import (
    normalize_string,
    truncate_string,
    to_snake_case,
    to_camel_case,
    safe_decimal,
    round_decimal,
    format_date,
    parse_date,
    remove_none_values,
    chunk_list,
    flatten_list,
    is_valid_email,
    is_valid_phone,
    generate_job_number,
    parse_job_number,
    calculate_percentage,
)

# Mapper
from app.utils.mapper import (
    orm_to_dto,
    orm_list_to_dto_list,
    orm_to_dto_with_relations,
    dto_to_orm,
    dto_to_dict,
    create_dto_to_orm,
    update_orm_from_dto,
    create_paginated_response,
    bulk_create_dtos_to_orms,
)


__all__ = [
    # Exceptions
    "ApplicationError",
    "BusinessError",
    "ValidationError",
    "StateConflictError",
    "NotFoundError",
    "PersistenceError",
    "DatabaseConnectionError",
    "UniqueConstraintError",
    "ToolInputError",
    "AgentExecutionError",
    "ExternalServiceError",
    # Validators
    "parse_tool_input",
    "parse_tool_input_as_string",
    "validate_required_fields",
    "validate_positive_number",
    "validate_date_range",
    "validate_string_length",
    "validate_enum_value",
    "validate_non_empty_list",
    "validate_job_number_format",
    "validate_email_format",
    "validate_phone_format",
    # Helpers
    "normalize_string",
    "truncate_string",
    "to_snake_case",
    "to_camel_case",
    "safe_decimal",
    "round_decimal",
    "format_date",
    "parse_date",
    "remove_none_values",
    "chunk_list",
    "flatten_list",
    "is_valid_email",
    "is_valid_phone",
    "generate_job_number",
    "parse_job_number",
    "calculate_percentage",
    # Mapper
    "orm_to_dto",
    "orm_list_to_dto_list",
    "orm_to_dto_with_relations",
    "dto_to_orm",
    "dto_to_dict",
    "create_dto_to_orm",
    "update_orm_from_dto",
    "create_paginated_response",
    "bulk_create_dtos_to_orms",
]
