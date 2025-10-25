from langchain_core.tools import Tool
from app.finance_agent.job_list.tools.query_tools.find_jobs_by_client import find_jobs_by_client_tool

job_query_tools = [
    Tool(
        name="find_jobs_by_client",
        func=find_jobs_by_client_tool,
        description="Find jobs by client name."
    )
]