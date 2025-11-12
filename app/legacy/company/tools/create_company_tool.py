"""
Tool wrapper for creating or updating company records with contact info lookup.

This is a thin wrapper around CompanyService.create_with_contact_enrichment()
"""

from typing import Optional, Dict, Any
from sqlmodel import Session
from app.db.engine import engine
from app.services.company_service import CompanyService
from app.finance_agent.utils.Google_CSE import search_company_contact


def create_company_tool(
    company_name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or update a company record with auto-enrichment.

    This tool wraps CompanyService.create_with_contact_enrichment()

    Args:
        company_name: Name of the company (required)
        address: Company address (optional, will auto-fetch if missing)
        phone: Company phone (optional, will auto-fetch if missing)

    Returns:
        dict with id, name, address, phone, status
    """
    with Session(engine) as session:
        company_service = CompanyService(session)
        result = company_service.create_with_contact_enrichment(
            name=company_name,
            address=address,
            phone=phone,
            google_search_fn=search_company_contact
        )
        session.commit()
        return result
