from langchain_core.tools import Tool
from app.finance_agent.company.tools.create_company_tool import create_company_tool
from app.finance_agent.company.tools.update_company_name import update_company_name
from app.finance_agent.company.tools.update_company_address import update_company_address
from app.finance_agent.company.tools.update_company_phone import update_company_phone
from app.finance_agent.company.tools.get_company_tool import get_company_tool


company_crud_tools = [
    Tool(
        name="create_company_tool",
        func=create_company_tool,
        description=(
            "Create a new company in the database. "
            "Input should be just the company name as a plain string, NOT a JSON object. "
            "Example: '金龍酒店'. "
            "Optionally, user can provide address and phone as additional parameters. "
            "If address or phone are not provided, the tool will attempt to auto-fetch them using Google Custom Search. "
            "Returns company details with status 'created', 'already_exists', or 'error'."
        )
    ),
    Tool(
        name="update_company_name",
        func=update_company_name,
        description=(
            "Update a company's name. "
            "You can identify the company by company_name (current name as string) or company_id (int). "
            "Provide the new_name parameter with the updated company name. "
            "Returns updated company details with status 'updated', 'not_found', or 'error'."
        )
    ),
    Tool(
        name="update_company_address",
        func=update_company_address,
        description=(
            "Update a company's address. "
            "You can identify the company by company_name (string) or company_id (int). "
            "Provide the new_address parameter with the updated address. "
            "Returns updated company details with status 'updated', 'not_found', or 'error'."
        )
    ),
    Tool(
        name="update_company_phone",
        func=update_company_phone,
        description=(
            "Update a company's phone number. "
            "You can identify the company by company_name (string) or company_id (int). "
            "Provide the new_phone parameter with the updated phone number. "
            "Returns updated company details with status 'updated', 'not_found', or 'error'."
        )
    ),
    Tool(
        name="get_company_tool",
        func=get_company_tool,
        description=(
            "Get company information by company_name (string) or company_id (int). "
            "Returns company details including id, name, address, phone, or error if not found."
        )
    )
]
