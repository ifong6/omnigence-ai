from langchain_core.tools import Tool
from app.finance_agent.job_list.tools.create_job_tool import create_job_tool
from app.finance_agent.job_list.tools.finance_db_health_check_tool import finance_db_health_check_tool
from app.finance_agent.job_list.tools.create_company_tool import create_company_tool
from app.finance_agent.job_list.tools.get_company_id_tool import get_company_id_tool
from app.finance_agent.job_list.tools.extract_job_info_list_tool import extract_job_info_list_tool
from app.finance_agent.job_list.tools.create_job_number_tool import create_job_number_tool
from app.finance_agent.job_list.tools.update_job_tool import update_job_tool

job_crud_tools = [
    Tool(
        name="create_job_tool",
        func=create_job_tool,
        description="Create a new job in the database. IMPORTANT: First get company_id using get_company_id_tool. If company doesn't exist, create it first using create_company_tool. Required parameters: company_id (integer), job_type ('inspection' or 'design'), job_title (string), job_no (job number string like 'JCP-25-01-1'), status (optional, defaults to 'New')."
    ),
    Tool(
        name="finance_db_health_check_tool",
        func=finance_db_health_check_tool,
        description="Check the health of the finance database."
    ),
    Tool(
        name="create_company_tool",
        func=create_company_tool,
        description="Create a company in the database if not existed. Input should be just the company name as a plain string, NOT a JSON object. Example: '聯建築工程有限公司'"
    ),
    Tool(
        name="get_company_id_tool",
        func=get_company_id_tool,
        description="Get the company id from the company name. Input should be just the company name as a plain string, NOT a JSON object. Example: '聯建築工程有限公司'. Returns the company ID as an integer or None if not found."
    ),
    Tool(
        name="extract_job_info_list_tool",
        func=extract_job_info_list_tool,
        description="Extract the job info from the user input and return a list of job info."
    ),
    Tool(
        name="create_job_number_tool",
        func=create_job_number_tool,
        description="Create new job number(s) for a specific new project(s)."
    ),
    Tool(
        name="update_job_tool",
        func=update_job_tool,
        description="Update a job's fields by job title. Required: title (to identify the job). Optional fields to update: company_id, job_type, new_title, job_no, status, quotation_status, quotation_issued_at (use 'current' or 'now' for CURRENT_TIMESTAMP). Can pass just title as a plain string to set quotation_status='Issued' and quotation_issued_at=CURRENT_TIMESTAMP, or pass JSON for more control."
    )
]


