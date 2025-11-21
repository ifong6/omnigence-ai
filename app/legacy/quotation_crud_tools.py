from langchain_core.tools import Tool
from app.legacy.quotation_tools.tools.crud_tools.create_quotation_no_tool import create_quotation_no_tool
from app.legacy.quotation_tools.tools.crud_tools.get_job_no_by_project_name_tool import get_job_no_by_project_name_tool
from app.legacy.quotation_tools.tools.crud_tools.extract_quotation_info_tool import extract_quotation_info_tool
from app.legacy.quotation_tools.tools.crud_tools.get_client_info_by_project_name_tool import get_client_info_by_project_name_tool
from app.legacy.quotation_tools.tools.crud_tools.create_quotation_in_db import create_quotation_in_db
from app.legacy.quotation_tools.tools.crud_tools.update_quotation_tool import update_quotation_tool
from app.legacy.quotation_tools.tools.output_quotation_info_for_ui import output_quotation_info_for_ui
"""
Quotation CRUD Tools

Typical Creation Flow:
  get_job_no_by_project_name → create_quotation_no → get_client_info →
  extract_quotation_info → create_quotation_in_db → output_quotation_info_for_ui

Priority: High (DB ops) > Medium (data gathering) > Supporting (ID gen) > Final (formatting)
Note: Workflows vary - updates skip most steps, queries may skip creation entirely.
"""

quotation_crud_tools = [
    # ID Resolution Tools (Priority: Supporting)
    Tool(
        name="get_job_no_by_project_name_tool",
        func=get_job_no_by_project_name_tool,
        description="""Fetch job_no by project title. Use when user provides title, not job number.
        Input: "校園實驗室消防安全檢測" → Output: "JCP-25-04-1" | None"""
    ),
    Tool(
        name="create_quotation_no_tool",
        func=create_quotation_no_tool,
        description="""Generate quotation_no from job_no. Call after getting job_no.
        Input: "JCP-25-04-1" → Output: {"quotation_no": "Q-JCP-25-04-q1", "revision_str": "00"}"""
    ),

    # Data Gathering Tools (Priority: Medium)
    Tool(
        name="get_client_info_by_project_name_tool",
        func=get_client_info_by_project_name_tool,
        description="""Fetch client details by project title. Can call in parallel with create_quotation_no_tool.
        Input: "校園實驗室消防安全檢測" → Output: {"name": "澳門科技大學", "address": "...", "phone": "..."}"""
    ),
    Tool(
        name="extract_quotation_info_tool",
        func=extract_quotation_info_tool,
        description="""Parse user input into structured QuotationInfo using LLM. Call before create_quotation_in_db.
        Input: JSON dict {"user_input": "...", "client_info": {...}, "quotation_no": "..."}
        Output: QuotationInfo with items, amounts, etc. IMPORTANT: Pass as JSON dict, not string!"""
    ),

    # Database Operations (Priority: High)
    Tool(
        name="create_quotation_in_db",
        func=create_quotation_in_db,
        description="""Save quotation to database. Call after extract_quotation_info_tool.
        Input: {"extracted_info": <QuotationInfo_from_extract_tool>, "quotation_no": "Q-...", "revision_str": "00"}
        Output: {"success": True, "quotation_no": "...", "items_inserted": 2}"""
    ),
    Tool(
        name="update_quotation_tool",
        func=update_quotation_tool,
        description="""Update existing quotation items. Use independently for modifications.
        Required: quo_no. Optional: item_id | item_description (filter specific items)
        Can update: project_item_description, sub_amount, quantity, unit, total_amount, currency, revision, date_issued
        Example: {"quo_no": "Q-JCP-25-04-q1", "item_id": 7, "sub_amount": 8000}"""
    ),

    # UI Formatting Tools (Priority: Final)
    Tool(
        name="output_quotation_info_for_ui",
        func=output_quotation_info_for_ui,
        description="""Format quotation for frontend display. Call as final step after create/update.
        Input: "Q-JCP-25-04-q1" → Output: Complete UI data with items, totals, client info"""
    )
]