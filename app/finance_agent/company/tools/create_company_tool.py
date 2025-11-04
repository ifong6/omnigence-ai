from typing import Optional, Dict, Any, Tuple

from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum
from app.finance_agent.utils.Google_CSE import search_company_contact

TABLE = DBTable_Enum.COMPANY_TABLE

# -------------------------- Main Tool Function --------------------------

def create_company_tool(
    company_name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or update a company record intelligently:
    - Validates and normalizes inputs.
    - Auto-fills missing address/phone via Google CSE.
    - Updates existing company if any field is missing.
    - Creates new record if not found.

    Args:
        company_name: Name of the company (required).
        address: Company address (optional, will auto-fetch if missing).
        phone: Company phone (optional, will auto-fetch if missing).

    Returns:
        A dictionary containing:
            - id: Company ID
            - name: Company name
            - address: Company address
            - phone: Company phone
            - status: "created" or "existing"
    """
    if not company_name or not company_name.strip():
        raise ValueError("company_name is required and cannot be empty")

    # Step 1. Normalize user input
    name = company_name.strip()
    address = normalize_str(address)
    phone = normalize_str(phone)

    # Step 2. Try to fill missing fields using Google CSE
    address, phone = _fetch_missing_contact_info(name, address, phone)

    # Step 3. Check if company already exists
    existing_rows = _select_company_by_name(name)
    if existing_rows:
        company_id, _, current_addr, current_phone = existing_rows[0]
        result = _update_contact_if_missing(company_id, current_addr, current_phone, address, phone)
        if result["name"] is None:
            result["name"] = name
        return result

    # Step 4. Create a new record if not found
    inserted = execute_query(
        f'INSERT INTO {TABLE} (name, address, phone) VALUES (%s, %s, %s) '
        f'RETURNING id, name, address, phone',
        (name, address, phone),
        fetch=True
    )
    if not inserted:
        raise RuntimeError("Failed to create company: no data returned")

    company_id, company_name, company_address, company_phone = inserted[0]
    return {
        "id": company_id,
        "name": company_name,
        "address": company_address,
        "phone": company_phone,
        "status": "created"
    }


# -------------------------- Helper Functions --------------------------

def normalize_str(s: Optional[str]) -> Optional[str]:
    """Collapse whitespace and return None if empty."""
    if not s:
        return None
    s = " ".join(str(s).split())
    return s or None


def _fetch_missing_contact_info(
    company_name: str,
    address: Optional[str],
    phone: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """Best-effort enrichment via Google CSE; never blocks DB ops."""
    if address and phone:
        return address, phone
    try:
        found = search_company_contact(company_name) or {}
        address = address or normalize_str(found.get("address"))
        phone   = phone   or normalize_str(found.get("phone"))
    except Exception as e:
        print(f"[WARN][create_company_tool] CSE lookup failed: {e}")
    return address, phone


def _select_company_by_name(name: str):
    """Query the company by name."""
    return execute_query(
        f'SELECT id, name, address, phone FROM {TABLE} WHERE name = %s',
        (name,), fetch=True
    ) or []


def _update_contact_if_missing(
    company_id: int,
    current_addr: Optional[str],
    current_phone: Optional[str],
    new_addr: Optional[str],
    new_phone: Optional[str]
) -> Dict[str, Any]:
    """Update missing contact info only if fields are empty."""
    final_addr = normalize_str(current_addr) or new_addr
    final_phone = normalize_str(current_phone) or new_phone

    if final_addr != normalize_str(current_addr) or final_phone != normalize_str(current_phone):
        updated = execute_query(
            f'UPDATE {TABLE} SET address = %s, phone = %s WHERE id = %s '
            f'RETURNING id, name, address, phone',
            (final_addr, final_phone, company_id),
            fetch=True
        )
        if updated:
            company_id, company_name, company_address, company_phone = updated[0]
            return {
                "id": company_id,
                "name": company_name,
                "address": company_address,
                "phone": company_phone,
                "status": "existing"
            }

    # Nothing to update; return current values
    return {
        "id": company_id,
        "name": None,  # will be filled at call site
        "address": normalize_str(current_addr),
        "phone": normalize_str(current_phone),
        "status": "existing"
    }
