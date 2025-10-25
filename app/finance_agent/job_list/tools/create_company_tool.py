"""
Tool for creating or updating company records in the Finance database.

This module provides functionality to:
- Create new company records
- Update existing company records if contact info is missing
- Auto-fetch contact info via Google CSE if not provided
"""

from typing import Any, Dict, Optional
from app.finance_agent.utils.tool_input_parser import parse_tool_input_as_string, ToolInputError
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    CompanyFields,
    ErrorMessages
)
from app.finance_agent.utils.db_helper import (
    find_one_by_field,
    insert_record,
    update_record,
    DatabaseError
)
from app.finance_agent.utils.Google_CSE import search_company_contact


# ============================================================================
# Business Logic Functions
# ============================================================================

def _normalize_address(addr: Optional[str]) -> Optional[str]:
    """
    Normalize address by collapsing whitespace.

    Args:
        addr: Raw address string

    Returns:
        Normalized address or None
    """
    if not addr:
        return None
    return " ".join(addr.split())


def _fetch_missing_contact_info(
    company_name: str,
    address: Optional[str],
    phone: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Fetch missing contact information via Google CSE.

    Args:
        company_name: Company name for search
        address: Current address (if any)
        phone: Current phone (if any)

    Returns:
        Tuple of (address, phone) with fetched values filled in
    """
    # Only search if either field is missing
    if address and phone:
        return address, phone

    try:
        found = search_company_contact(company_name)

        if not address and found.get("address"):
            address = _normalize_address(found["address"])

        if not phone and found.get("phone"):
            phone = found["phone"].strip() if found["phone"] else None

    except Exception as e:
        # Search failure should not block database operations
        print(f"[WARN][create_company_tool] Google CSE search failed: {str(e)}")

    return address, phone


def _check_and_update_existing_company(
    company_name: str,
    address: Optional[str],
    phone: Optional[str]
) -> Optional[Dict[str, Any]]:
    """
    Check if company exists and update if contact info is missing.

    Args:
        company_name: Company name to search for
        address: New address (if available)
        phone: New phone (if available)

    Returns:
        Company dict with status="existing" if found, None otherwise
    """
    company = find_one_by_field(
        table=DatabaseSchema.COMPANY_TABLE,
        field=CompanyFields.NAME,
        value=company_name,
        operation_name="check existing company"
    )

    if not company:
        return None

    # Check if we need to update missing fields
    company_id = company[CompanyFields.ID]
    current_addr = company.get(CompanyFields.ADDRESS)
    current_phone = company.get(CompanyFields.PHONE)

    need_update = False
    new_addr = current_addr
    new_phone = current_phone

    # Update address if current is empty and we have a new one
    if (not current_addr or not current_addr.strip()) and address:
        new_addr = address
        need_update = True

    # Update phone if current is empty and we have a new one
    if (not current_phone or not str(current_phone).strip()) and phone:
        new_phone = phone
        need_update = True

    if need_update:
        update_record(
            table=DatabaseSchema.COMPANY_TABLE,
            fields={
                CompanyFields.ADDRESS: new_addr,
                CompanyFields.PHONE: new_phone
            },
            where_clause=f"{CompanyFields.ID} = %s",
            where_params=(company_id,),
            returning=f"{CompanyFields.ID}",
            operation_name="update company contact info"
        )

    return {
        CompanyFields.ID: company_id,
        CompanyFields.NAME: company_name,
        CompanyFields.ADDRESS: new_addr,
        CompanyFields.PHONE: new_phone,
        "status": "existing"
    }


def _create_new_company(
    company_name: str,
    address: Optional[str],
    phone: Optional[str]
) -> Dict[str, Any]:
    """
    Create a new company record.

    Args:
        company_name: Company name
        address: Company address
        phone: Company phone

    Returns:
        Created company dict with status="created"
    """
    company = insert_record(
        table=DatabaseSchema.COMPANY_TABLE,
        fields={
            CompanyFields.NAME: company_name,
            CompanyFields.ADDRESS: address,
            CompanyFields.PHONE: phone
        },
        returning=f"{CompanyFields.ID}, {CompanyFields.NAME}, "
                 f"{CompanyFields.ADDRESS}, {CompanyFields.PHONE}",
        operation_name="create company"
    )

    if not company:
        raise DatabaseError("Failed to create company: No data returned")

    company["status"] = "created"
    return company


# ============================================================================
# Main Tool Function
# ============================================================================

def create_company_tool(
    company_name: str,
    address: Optional[str] = "",
    phone: Optional[str] = ""
) -> dict:
    """
    Create a new company if it doesn't exist. If it exists and DB has missing
    contact fields, update them. If address/phone not provided, auto-fetch using Google CSE.

    This tool intelligently handles company creation with the following features:
    - Checks if company already exists before creating
    - Updates missing contact info for existing companies
    - Auto-fetches contact info via Google CSE if not provided
    - Normalizes addresses (collapses whitespace)

    Args:
        company_name: Company name (required)
        address: Company address (optional, will auto-fetch if missing)
        phone: Company phone number (optional, will auto-fetch if missing)

    Returns:
        dict: Company record with the following fields:
            - id: Company ID
            - name: Company name
            - address: Company address
            - phone: Company phone
            - status: "created" (new company) or "existing" (found in DB)

    Raises:
        ValueError: If company_name is empty or missing
        DatabaseError: If database operations fail

    Examples:
        >>> # Create with full info
        >>> result = create_company_tool(
        ...     company_name="ABC Engineering",
        ...     address="123 Main St, Macau",
        ...     phone="+853 1234 5678"
        ... )
        >>> # Returns: {"id": 1, "name": "ABC Engineering", ..., "status": "created"}

        >>> # Create with auto-fetch (will search via Google CSE)
        >>> result = create_company_tool(company_name="ABC Engineering")
        >>> # Returns: {"id": 1, "name": "ABC Engineering", ..., "status": "created"}

        >>> # Update existing company's missing contact info
        >>> result = create_company_tool(
        ...     company_name="Existing Company",
        ...     phone="+853 8888 8888"
        ... )
        >>> # Returns: {"id": 5, "name": "Existing Company", ..., "status": "existing"}

    Workflow:
        1. Validate company name
        2. Normalize address and phone
        3. If contact info missing, try to fetch via Google CSE
        4. Check if company exists in database
        5a. If exists: Update missing fields (if any) and return
        5b. If not exists: Create new company record and return
    """
    # Validate input
    if not company_name or not company_name.strip():
        raise ValueError("company_name is required and cannot be empty")

    # Normalize inputs
    company_name = company_name.strip()
    address = _normalize_address(address) if address else None
    phone = phone.strip() if phone else None

    # Fetch missing contact info via Google CSE
    address, phone = _fetch_missing_contact_info(company_name, address, phone)

    # Check if company exists and update if needed
    existing_company = _check_and_update_existing_company(
        company_name, address, phone
    )

    if existing_company:
        return existing_company

    # Create new company
    return _create_new_company(company_name, address, phone)
