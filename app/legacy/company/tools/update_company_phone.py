"""
Tool for updating company phone.

Refactored to use centralized CompanyService with SQLModel ORM.
"""

from sqlmodel import Session
from app.db.engine import engine
from app.services.company_service import CompanyService
import json


def update_company_phone(tool_input) -> dict:
    """
    Update company phone. Identify company by company_id or company_name.

    Args:
        tool_input: {"company_id" or "company_name": ..., "new_phone": str}

    Returns:
        dict with id, name, address, phone, status ("updated", "error", or "not_found")
    """

    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Strip surrounding quotes if present
        stripped = tool_input.strip().strip("'").strip('"')
        try:
            params = json.loads(stripped)
        except json.JSONDecodeError:
            return {
                "error": f"Invalid input format. Expected JSON dict. Received: {tool_input}",
                "status": "error"
            }
    elif isinstance(tool_input, dict):
        params = tool_input
    else:
        return {
            "error": "Invalid input type. Expected dict or JSON string",
            "status": "error"
        }

    company_id = params.get("company_id")
    company_name = params.get("company_name")
    new_phone = params.get("new_phone")

    # Validate inputs
    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    if not new_phone:
        return {
            "error": "new_phone is required",
            "status": "error"
        }

    # Use CompanyService to find and update the company
    try:
        with Session(engine) as session:
            company_service = CompanyService(session)

            # Find the company
            if company_id:
                company = company_service.get_by_id(company_id)
            else:
                company = company_service.get_by_name(company_name.strip() if company_name else "")

            if not company:
                return {
                    "error": "Company not found",
                    "status": "not_found"
                }

            # Update the company phone
            updated_company = company_service.update(
                company_id=company.id,
                phone=new_phone.strip()
            )

            if not updated_company:
                return {
                    "error": "Failed to update company phone",
                    "status": "error"
                }

            session.commit()

            return {
                "id": updated_company.id,
                "name": updated_company.name,
                "address": updated_company.address,
                "phone": updated_company.phone,
                "status": "updated",
                "message": f"Company ID {updated_company.id} phone updated successfully"
            }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
