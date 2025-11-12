"""
Tool wrapper for getting company information by ID or name.

This is a thin wrapper around CompanyService get methods.
"""

from sqlmodel import Session
from app.db.engine import engine
from app.services.company_service import CompanyService


def get_company_tool(tool_input) -> dict:
    """
    Get company information by ID or name.

    This tool wraps CompanyService.get_by_id() and get_by_name()

    Args:
        tool_input: Either a company name (string) or company ID (int)

    Returns:
        dict: Company information with id, name, address, phone
              or error dict if not found
    """
    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Try to parse as int first
        try:
            company_id = int(tool_input)
            company_name = None
        except ValueError:
            # It's a company name
            company_id = None
            company_name = tool_input
    elif isinstance(tool_input, int):
        company_id = tool_input
        company_name = None
    elif isinstance(tool_input, dict):
        company_id = tool_input.get("company_id")
        company_name = tool_input.get("company_name")
    else:
        return {
            "error": "Invalid input type. Expected string, int, or dict",
            "status": "error"
        }

    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    try:
        with Session(engine) as session:
            company_service = CompanyService(session)

            # Get company by ID or name
            if company_id:
                company = company_service.get_by_id(company_id)
            else:
                company = company_service.get_by_name(company_name.strip() if company_name else "")

            if not company:
                return {
                    "error": "Company not found",
                    "status": "not_found"
                }

            return {
                "id": company.id,
                "name": company.name,
                "address": company.address,
                "phone": company.phone,
                "status": "found"
            }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
