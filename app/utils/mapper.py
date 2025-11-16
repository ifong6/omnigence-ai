"""
DTO ↔ ORM Mapping Utilities

This module provides utilities for converting between:
- DTOs (Pydantic models) - Used in API/Service layers
- ORM models (SQLModel) - Used in DAO/Database layers

Key Principles:
1. DTOs provide validation, type safety, and API contracts
2. ORMs represent database structure
3. Mappers decouple the two layers for flexibility
"""

from typing import TypeVar, Type, List, Optional, Dict, Any
from pydantic import BaseModel
from sqlmodel import SQLModel


# Type variables for generic mapping functions
DTO_T = TypeVar('DTO_T', bound=BaseModel)
ORM_T = TypeVar('ORM_T', bound=SQLModel)


# =============================================================================
# ORM → DTO Conversions
# =============================================================================

def orm_to_dto(
    orm_obj: ORM_T,
    dto_class: Type[DTO_T],
    exclude: Optional[set[str]] = None,
    **extra_fields: Any
) -> DTO_T:
    """
    Convert an ORM model instance to a DTO.

    This uses Pydantic's from_attributes feature (formerly from_orm).
    The DTO class must have `model_config = ConfigDict(from_attributes=True)`.

    Args:
        orm_obj: ORM model instance (e.g., Company, Job, Quotation)
        dto_class: DTO class to convert to (e.g., CompanyDTO)
        exclude: Optional set of field names to exclude
        **extra_fields: Additional fields to add to the DTO

    Returns:
        DTO instance populated from ORM object

    Examples:
        >>> from app.models import Company
        >>> from app.dto import CompanyDTO
        >>> company = Company(id=1, name="ABC Corp", address="123 St")
        >>> dto = orm_to_dto(company, CompanyDTO)
        >>> isinstance(dto, CompanyDTO)
        True

        >>> # With extra computed fields
        >>> dto = orm_to_dto(company, CompanyWithStatsDTO, job_count=5)
    """
    # Get all attributes from ORM object
    data = {}
    for field_name in dto_class.model_fields.keys():
        if exclude and field_name in exclude:
            continue
        if hasattr(orm_obj, field_name):
            data[field_name] = getattr(orm_obj, field_name)

    # Add extra fields
    data.update(extra_fields)

    # Create DTO using model_validate with from_attributes
    return dto_class.model_validate(orm_obj, **extra_fields)


def orm_list_to_dto_list(
    orm_list: List[ORM_T],
    dto_class: Type[DTO_T],
    exclude: Optional[set[str]] = None
) -> List[DTO_T]:
    """
    Convert a list of ORM instances to a list of DTOs.

    Args:
        orm_list: List of ORM model instances
        dto_class: DTO class to convert to
        exclude: Optional set of field names to exclude

    Returns:
        List of DTO instances

    Examples:
        >>> companies = [Company(id=1, name="A"), Company(id=2, name="B")]
        >>> dtos = orm_list_to_dto_list(companies, CompanyDTO)
        >>> len(dtos)
        2
    """
    return [orm_to_dto(orm_obj, dto_class, exclude) for orm_obj in orm_list]


# =============================================================================
# DTO → ORM Conversions
# =============================================================================

def dto_to_orm(
    dto_obj: DTO_T,
    orm_class: Type[ORM_T],
    exclude: Optional[set[str]] = None,
    **override_fields: Any
) -> ORM_T:
    """
    Convert a DTO to an ORM model instance.

    Note: This creates a NEW instance. It does NOT persist to database.
    Use with DAO/Repository create() or update() methods.

    Args:
        dto_obj: DTO instance (e.g., CreateCompanyDTO)
        orm_class: ORM class to create (e.g., Company)
        exclude: Optional set of field names to exclude
        **override_fields: Fields to override or add

    Returns:
        ORM instance (not yet persisted)

    Examples:
        >>> from app.dto import CreateCompanyDTO
        >>> from app.models import Company
        >>> dto = CreateCompanyDTO(name="ABC Corp", address="123 St")
        >>> company = dto_to_orm(dto, Company)
        >>> company.name
        'ABC Corp'

        >>> # With overrides
        >>> company = dto_to_orm(dto, Company, created_by_id=1)
    """
    # Convert DTO to dict
    data = dto_obj.model_dump(exclude_unset=True, exclude=exclude)

    # Apply overrides
    data.update(override_fields)

    # Create ORM instance
    return orm_class(**data)


def dto_to_dict(
    dto_obj: DTO_T,
    exclude_unset: bool = True,
    exclude_none: bool = False,
    exclude: Optional[set[str]] = None
) -> Dict[str, Any]:
    """
    Convert a DTO to a plain dictionary.

    Useful for partial updates where you only want to update provided fields.

    Args:
        dto_obj: DTO instance
        exclude_unset: Exclude fields that were not set (default: True)
        exclude_none: Exclude fields with None values (default: False)
        exclude: Optional set of field names to exclude

    Returns:
        Dictionary representation

    Examples:
        >>> from app.dto import UpdateCompanyDTO
        >>> dto = UpdateCompanyDTO(name="New Name")  # phone not set
        >>> dto_to_dict(dto, exclude_unset=True)
        {'name': 'New Name'}

        >>> dto_to_dict(dto, exclude_unset=False)
        {'name': 'New Name', 'phone': None, 'address': None, 'alias': None}
    """
    return dto_obj.model_dump(
        exclude_unset=exclude_unset,
        exclude_none=exclude_none,
        exclude=exclude
    )


# =============================================================================
# Specialized Mapping Functions
# =============================================================================

def create_dto_to_orm(
    create_dto: DTO_T,
    orm_class: Type[ORM_T],
    **defaults: Any
) -> ORM_T:
    """
    Convert a Create DTO to ORM instance with sensible defaults.

    This is a convenience wrapper for dto_to_orm() specifically for
    create operations, which often need default values.

    Args:
        create_dto: Create DTO (e.g., CreateCompanyDTO)
        orm_class: ORM class
        **defaults: Default values to set

    Returns:
        ORM instance ready for insertion

    Examples:
        >>> dto = CreateCompanyDTO(name="ABC")
        >>> company = create_dto_to_orm(dto, Company, created_by_id=1)
    """
    return dto_to_orm(create_dto, orm_class, **defaults)


def update_orm_from_dto(
    orm_obj: ORM_T,
    update_dto: DTO_T,
    exclude_unset: bool = True
) -> ORM_T:
    """
    Update an ORM instance with values from an Update DTO.

    Only updates fields that were provided in the DTO (exclude_unset=True).
    This is useful for partial updates.

    Args:
        orm_obj: Existing ORM instance to update
        update_dto: Update DTO with new values
        exclude_unset: Only update fields that were explicitly set (default: True)

    Returns:
        Updated ORM instance (same object, modified in-place)

    Examples:
        >>> company = Company(id=1, name="Old Name", address="Old Address")
        >>> update_dto = UpdateCompanyDTO(name="New Name")  # address not set
        >>> updated = update_orm_from_dto(company, update_dto)
        >>> company.name
        'New Name'
        >>> company.address  # Unchanged
        'Old Address'
    """
    update_data = dto_to_dict(update_dto, exclude_unset=exclude_unset)

    for field, value in update_data.items():
        if hasattr(orm_obj, field):
            setattr(orm_obj, field, value)

    return orm_obj


# =============================================================================
# Pagination Mapping Utilities
# =============================================================================

def create_paginated_response(
    orm_list: List[ORM_T],
    dto_class: Type[DTO_T],
    total_count: int,
    limit: Optional[int] = None,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Create a paginated response with DTOs.

    Args:
        orm_list: List of ORM instances (current page)
        dto_class: DTO class to convert to
        total_count: Total number of records
        limit: Applied limit
        offset: Applied offset

    Returns:
        Dictionary with items, total_count, limit, offset

    Examples:
        >>> companies = [Company(id=1), Company(id=2)]
        >>> response = create_paginated_response(
        ...     companies, CompanyDTO, total_count=10, limit=2, offset=0
        ... )
        >>> response['total_count']
        10
        >>> len(response['items'])
        2
    """
    return {
        'items': orm_list_to_dto_list(orm_list, dto_class),
        'total_count': total_count,
        'limit': limit,
        'offset': offset
    }


# =============================================================================
# Nested/Relationship Mapping
# =============================================================================

def orm_to_dto_with_relations(
    orm_obj: ORM_T,
    dto_class: Type[DTO_T],
    relations: Optional[Dict[str, tuple[str, Type[BaseModel]]]] = None
) -> DTO_T:
    """
    Convert ORM to DTO including nested relationships.

    Args:
        orm_obj: ORM instance
        dto_class: DTO class
        relations: Dict mapping ORM relation name to (DTO field name, DTO class)
                  e.g., {'items': ('items', QuotationItemDTO)}

    Returns:
        DTO with nested DTOs for relationships

    Examples:
        >>> quotation = Quotation(id=1, quo_no="Q-001", items=[...])
        >>> dto = orm_to_dto_with_relations(
        ...     quotation,
        ...     QuotationDTO,
        ...     relations={'items': ('items', QuotationItemDTO)}
        ... )
    """
    # Start with base conversion
    dto = orm_to_dto(orm_obj, dto_class)

    # Map relations if specified
    if relations:
        for orm_rel_name, (dto_field_name, nested_dto_class) in relations.items():
            if hasattr(orm_obj, orm_rel_name):
                orm_rel_value = getattr(orm_obj, orm_rel_name)

                # Handle list of relations
                if isinstance(orm_rel_value, list):
                    nested_dtos = orm_list_to_dto_list(orm_rel_value, nested_dto_class)
                    setattr(dto, dto_field_name, nested_dtos)
                # Handle single relation
                elif orm_rel_value is not None:
                    nested_dto = orm_to_dto(orm_rel_value, nested_dto_class)
                    setattr(dto, dto_field_name, nested_dto)

    return dto


# =============================================================================
# Bulk Operations
# =============================================================================

def bulk_create_dtos_to_orms(
    dto_list: List[DTO_T],
    orm_class: Type[ORM_T],
    **defaults: Any
) -> List[ORM_T]:
    """
    Convert a list of Create DTOs to ORM instances.

    Useful for bulk insert operations.

    Args:
        dto_list: List of Create DTOs
        orm_class: ORM class
        **defaults: Default values for all instances

    Returns:
        List of ORM instances

    Examples:
        >>> dtos = [
        ...     CreateCompanyDTO(name="A"),
        ...     CreateCompanyDTO(name="B")
        ... ]
        >>> companies = bulk_create_dtos_to_orms(dtos, Company)
        >>> len(companies)
        2
    """
    return [dto_to_orm(dto, orm_class, **defaults) for dto in dto_list]
