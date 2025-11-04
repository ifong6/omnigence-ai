"""
Shared constants for the finance agent.

This module centralizes all magic strings, numbers, and configuration values
to improve maintainability and reduce duplication.
"""

from enum import Enum


# ============================================================================
# Database Constants
# ============================================================================

class DatabaseSchema:
    """Database table names with schema qualification."""
    DESIGN_JOB_TABLE = '"Finance".design_job'
    INSPECTION_JOB_TABLE = '"Finance".inspection_job'
    QUOTATION_TABLE = '"Finance".quotation'
    COMPANY_TABLE = '"Finance".company'


# ============================================================================
# Job Constants
# ============================================================================

class JobType(str, Enum):
    """Valid job types in the system."""
    INSPECTION = "INSPECTION"
    DESIGN = "DESIGN"

class JobStatus(str, Enum):
    """Valid job statuses - must match database enum values exactly."""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class QuotationStatus(str, Enum):
    """Valid quotation statuses."""
    NOT_CREATED = "NOT_CREATED"
    CREATED = "CREATED"
    ISSUED = "ISSUED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# ============================================================================
# Quotation Constants
# ============================================================================

class QuotationDefaults:
    """Default values for quotations."""
    UNIT = "Lot"
    QUANTITY = 1
    REVISION = "00"
    CURRENCY = "MOP"


class QuotationPrefixes:
    """Prefixes for quotation numbers."""
    QUOTATION = "Q-"
    SEQUENCE = "q"
    REVISION = "R"


# ============================================================================
# Error Messages
# ============================================================================

class ErrorMessages:
    """Standardized error messages."""

    # Input validation errors
    MISSING_REQUIRED_PARAM = "{tool}: Missing required parameter: {param}"
    INVALID_INPUT_TYPE = "{tool}: Invalid input type: {type}. Expected {expected}"
    INVALID_JSON = "{tool}: Invalid JSON input: {error}"

    # Database errors
    DB_QUERY_FAILED = "{tool}: Database query failed: {error}"
    RECORD_NOT_FOUND = "{tool}: No {entity} found with {field}='{value}'"
    DUPLICATE_RECORD = "{tool}: {entity} already exists with {field}='{value}'"

    # Business logic errors
    INVALID_JOB_TYPE = "Invalid job type: '{value}'. Must be 'Inspection' or 'Design'"
    INVALID_QUOTATION_STATUS = "Invalid quotation status: '{value}'"
    NO_ITEMS_TO_UPDATE = "No fields provided to update. Please specify at least one field."


# ============================================================================
# Success Messages
# ============================================================================

class SuccessMessages:
    """Standardized success messages."""
    CREATED = "Successfully created {entity}: {details}"
    UPDATED = "Successfully updated {entity}: {details}"
    DELETED = "Successfully deleted {entity}: {details}"
    FOUND = "Found {count} {entity}(s)"


# ============================================================================
# Database Field Names
# ============================================================================

class JobFields:
    """Field names for job table."""
    ID = "id"
    COMPANY_ID = "company_id"
    TYPE = "type"
    TITLE = "title"
    STATUS = "status"
    JOB_NO = "job_no"
    DATE_CREATED = "date_created"
    QUOTATION_STATUS = "quotation_status"
    QUOTATION_ISSUED_AT = "quotation_issued_at"


class QuotationFields:
    """Field names for quotation table."""
    ID = "id"
    QUO_NO = "quo_no"
    DATE_ISSUED = "date_issued"
    CLIENT_ID = "client_id"
    PROJECT_NAME = "project_name"
    PROJECT_ITEM_DESCRIPTION = "project_item_description"
    SUB_AMOUNT = "sub_amount"
    TOTAL_AMOUNT = "total_amount"
    CURRENCY = "currency"
    REVISION = "revision"
    QUANTITY = "quantity"  # Renamed from AMOUNT for clarity (stores item quantity, not price)
    UNIT = "unit"


class CompanyFields:
    """Field names for company table."""
    ID = "id"
    NAME = "name"
    ALIAS = "alias"
    ADDRESS = "address"
    PHONE = "phone"


# ============================================================================
# Validation Rules
# ============================================================================

class ValidationRules:
    """Validation rules and constraints."""
    MAX_COMPANY_NAME_LENGTH = 255
    MAX_PROJECT_NAME_LENGTH = 500
    MAX_PHONE_LENGTH = 20
    MIN_AMOUNT = 0
    MAX_AMOUNT = 999999999.99
