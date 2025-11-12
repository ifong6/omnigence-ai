"""
Tool for getting company ID by name.

Refactored to use centralized CompanyService with SQLModel ORM.
"""

from typing import Optional
from sqlmodel import Session

from app.db.engine import engine
from app.services.company_service import CompanyService


def get_company_id_tool(company_name: str) -> Optional[int]:
    """
    Get company ID by name using CompanyService. Returns None if not found.

    Args:
        company_name: Company name to search for

    Returns:
        Company ID (int) or None

    Example:
        >>> get_company_id_tool("澳門科技大學")
        15
        >>> get_company_id_tool("NonExistent Company")
        None
    """
    with Session(engine) as session:
        company_service = CompanyService(session)
        company = company_service.get_by_name(company_name)
        return company.id if company else None
