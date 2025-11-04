from langchain_core.tools import Tool
from app.finance_agent.quotation.tools.crud_tools.create_quotation_no_tool import create_quotation_no_tool
from app.finance_agent.quotation.tools.crud_tools.get_job_no_by_project_name_tool import get_job_no_by_project_name_tool
from app.finance_agent.quotation.tools.crud_tools.extract_quotation_info_tool import extract_quotation_info_tool
from app.finance_agent.quotation.tools.crud_tools.get_client_info_by_project_name_tool import get_client_info_by_project_name_tool
from app.finance_agent.quotation.tools.crud_tools.create_quotation_in_db import create_quotation_in_db
from app.finance_agent.quotation.tools.crud_tools.update_quotation_tool import update_quotation_tool
from app.finance_agent.quotation.tools.output_quotation_info_for_ui import output_quotation_info_for_ui

quotation_crud_tools = [
    Tool(
        name="get_job_no_by_project_name_tool",
        func=get_job_no_by_project_name_tool,
        description="""STEP 1: Fetch job number by project title/name (NOT job number).
        Input: Project title string (e.g., "校園實驗室消防安全檢測")
        Output: Job number string (e.g., "JCP-25-04-1") or None if not found.
        Example: get_job_no_by_project_name_tool("校園實驗室消防安全檢測") → "JCP-25-04-1"
        Note: If user provides job number like "JCP-25-04-1", you must extract the project title from context first."""
    ),
    Tool(
        name="create_quotation_no_tool",
        func=create_quotation_no_tool,
        description="""STEP 2: Generate quotation number from job number.
        Input: Job number from step 1 (e.g., "JCP-25-04-1")
        Output: {"quotation_no": "Q-JCP-25-04-q1", "revision_str": "00"}
        Example: create_quotation_no_tool("JCP-25-04-1") → {"quotation_no": "Q-JCP-25-04-q1", "revision_str": "00"}"""
    ),
    Tool(
        name="get_client_info_by_project_name_tool",
        func=get_client_info_by_project_name_tool,
        description="""STEP 3: Fetch client/company information by project title.
        Input: Project title string (same as step 1)
        Output: {"name": "澳門科技大學", "address": "...", "phone": "..."}
        Example: get_client_info_by_project_name_tool("校園實驗室消防安全檢測") → client info dict"""
    ),
    Tool(
        name="extract_quotation_info_tool",
        func=extract_quotation_info_tool,
        description="""STEP 4: Extract structured quotation info using LLM.
        Input: JSON dict with {"user_input": "...", "client_info": {from step 3}, "quotation_no": "from step 2"}
        Output: QuotationInfo object with project items, amounts, etc.
        Example: extract_quotation_info_tool({"user_input": "items: 區域A 12,500mop...", "client_info": {...}, "quotation_no": "Q-JCP-25-04-q1"})
        IMPORTANT: Pass as JSON dict, not plain string!"""
    ),
    Tool(
        name="create_quotation_in_db",
        func=create_quotation_in_db,
        description="""STEP 5: Save quotation to database.
        Input: Pass the output from extract_quotation_info_tool directly as extracted_info. JSON format:
        {"extracted_info": <output_from_step_4>, "quotation_no": "Q-JCP-25-04-q1", "revision_str": "00"}
        IMPORTANT: For extracted_info, use the EXACT output from extract_quotation_info_tool (the QuotationInfo with all fields).
        Just structure it as: {"extracted_info": {all the fields from step 4 output}, "quotation_no": "...", "revision_str": "00"}
        Output: {"success": True, "quotation_no": "...", "items_inserted": 2}"""
    ),
    Tool(
        name="update_quotation_tool",
        func=update_quotation_tool,
        description="""Update existing quotation items in database.
        Required: quo_no. Optional: item_id or item_description to target specific items.
        Can update: project_item_description, sub_amount, quantity, unit, total_amount, currency, revision, date_issued.
        Example: Update item price, quantity, or description."""
    ),
    Tool(
        name="output_quotation_info_for_ui",
        func=output_quotation_info_for_ui,
        description="""FINAL STEP: Format and output quotation data for UI rendering.
        Input: Quotation number
        Output: Complete quotation data formatted for frontend display.
        Call this LAST after quotation is created."""
    )
]