from app.postgres.db_connection import execute_query
from typing import Optional
from app.finance_agent.utils.Google_CSE import search_company_contact


def _normalize_address(addr: Optional[str]) -> Optional[str]:
    """Normalize address by collapsing whitespace."""
    if not addr:
        return None
    return " ".join(addr.split())

def create_company_tool(
    company_name: str,
    address: Optional[str] = "",
    phone: Optional[str] = ""
    
) -> dict:
    """
    Create a new company in the database.

    If address or phone not provided, attempts to auto-fetch using Google Custom Search.

    Args:
        company_name: Company name (required)
        address: Company address (optional)
        phone: Company phone number (optional)

    Returns:
        dict: {
            "id": int,
            "name": str,
            "address": str or None,
            "phone": str or None,
            "status": "created" or "error"
        }
    """

    if not company_name or not company_name.strip():
        return {
            "error": "company_name is required",
            "status": "error"
        }

    company_name = company_name.strip()
    address = _normalize_address(address) if address else None
    phone = phone.strip() if phone else None

    # Check if company already exists
    existing = execute_query(
        """
        SELECT id, name, address, phone
        FROM "Finance".company
        WHERE name = %s
        LIMIT 1
        """,
        params=(company_name,),
        fetch_results=True
    )

    if existing:
        return {
            "id": existing[0]["id"],
            "name": existing[0]["name"],
            "address": existing[0]["address"],
            "phone": existing[0]["phone"],
            "status": "already_exists",
            "message": f"Company '{company_name}' already exists with ID {existing[0]['id']}"
        }

    # If address or phone missing, try Google CSE lookup
    if not address or not phone:
        try:
            found = search_company_contact(company_name)
            if not address and found.get("address"):
                address = _normalize_address(found["address"])
            if not phone and found.get("phone"):
                phone = found["phone"].strip() if found["phone"] else None
        except Exception as e:
            # Search failure should not block DB operations
            print(f"Warning: Google CSE lookup failed: {e}")

    # Insert new company
    try:
        rows = execute_query(
            """
            INSERT INTO "Finance".company (name, address, phone)
            VALUES (%s, %s, %s)
            RETURNING id, name, address, phone
            """,
            params=(company_name, address, phone),
            fetch_results=True
        )

        result = rows[0]
        result["status"] = "created"
        return result

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
