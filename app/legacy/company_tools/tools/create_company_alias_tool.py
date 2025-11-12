"""
Tool wrapper for creating intelligent company aliases using LLM.

This is a thin wrapper around CompanyService.generate_alias_with_llm()
"""

from sqlmodel import Session
from app.db.engine import engine
from app.services.company_service import CompanyService
from app.llm.invoke_claude_llm import invoke_claude_llm


def create_company_alias_tool(tool_input) -> dict:
    """
    Generate and assign an intelligent alias to a company using LLM.

    This tool wraps CompanyService.generate_alias_with_llm()

    Args:
        tool_input: Either a company name (string) or company ID (int)

    Returns:
        dict: Updated company information with the new alias, or error dict

    Examples:
        >>> create_company_alias_tool("澳門科技大學")
        {"id": 1, "name": "澳門科技大學", "alias": "澳科大", "status": "alias_created"}

        >>> create_company_alias_tool({"company_id": 5})
        {"id": 5, "name": "金龍酒店", "alias": "金龍", "status": "alias_created"}
    """
    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Try to parse as int first (company_id)
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

            # If name provided, lookup company first
            if company_name and not company_id:
                company = company_service.get_by_name(company_name.strip())
                if not company:
                    return {
                        "error": "Company not found",
                        "status": "not_found"
                    }
                company_id = company.id

            # Generate alias
            result = company_service.generate_alias_with_llm(
                company_id=company_id,
                llm_fn=invoke_claude_llm
            )
            session.commit()
            return result

    except Exception as e:
        error_msg = f"Error generating company alias: {str(e)}"
        print(f"[ERROR][create_company_alias_tool] {error_msg}")
        return {
            "error": error_msg,
            "status": "error"
        }
