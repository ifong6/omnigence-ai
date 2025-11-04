from langchain_core.tools import Tool
from app.finance_agent.job_list.tools.query_tools.find_design_jobs_by_client_tool import find_design_jobs_by_client_tool
from app.finance_agent.job_list.tools.query_tools.find_inspection_jobs_by_client_tool import find_inspection_jobs_by_client_tool

job_query_tools = [
    Tool(
        name="find_design_jobs_by_client",
        func=find_design_jobs_by_client_tool,
        description="Find DESIGN jobs by client name. Use this for companies that do design work."
    ),
    Tool(
        name="find_inspection_jobs_by_client",
        func=find_inspection_jobs_by_client_tool,
        description="Find INSPECTION jobs by client name. Use this for companies that do inspection work."
    )
]