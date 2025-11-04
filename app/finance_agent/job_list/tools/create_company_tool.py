from typing import Any, Dict, Optional
from database.db_helper import (
find_one_by_field,
    insert_record,
    update_record,
    DatabaseError
)

from database.supabase.db_enum import DBTable_Enum
from app.finance_agent.utils.Google_CSE import search_company_contact

# ============================================================================
# Main Tool Function
# ============================================================================

def create_company_tool(
    company_name: str,
    address: Optional[str] = "",
    phone: Optional[str] = ""
) -> dict:
    """
    Create or update a company record.

    - Find by name; if found, fill missing address/phone.
    - If address/phone not provided, attempt Google CSE lookup.
    - Normalize address and return {id, name, address, phone, status}.

    Args:
        company_name: Company name (required).
        address: Company address (optional; auto-fetched if missing).
        phone: Company phone number (optional; auto-fetched if missing).

    Returns:
        dict: {id, name, address, phone, status: "created" | "existing"}
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
    
    Return provided address and phone if both exist; 
    otherwise search Google CSE and return fetched values, 
    falling back to the originals on failure.
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
        table=DBTable_Enum.COMPANY_TABLE,
        field="name",
        value=company_name,
        operation_name="check existing company"
    )

    if not company:
        return None

    # Check if we need to update missing fields
    company_id = company["id"]
    current_addr = company.get("address")
    current_phone = company.get("phone")

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
            table=DBTable_Enum.COMPANY_TABLE,
            fields={
                "address": new_addr,
                "phone": new_phone
            },
            where_clause=f"id = %s",
            where_params=(company_id,),
            returning=f"id",
            operation_name="update company contact info"
        )

    return {
        "id": company_id,
        "name": company_name,
        "address": new_addr,
        "phone": new_phone,
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
        table=DBTable_Enum.COMPANY_TABLE,
        fields={
            "name": company_name,
            "address": address,
            "phone": phone
        },
        returning=f"id, name, address, phone",
        operation_name="create company"
    )

    if not company:
        raise DatabaseError("Failed to create company: No data returned")

    # Convert to dict if needed (execute_query may return tuple)
    if not isinstance(company, dict):
        company = dict(company)

    company["status"] = "created"
    return company

