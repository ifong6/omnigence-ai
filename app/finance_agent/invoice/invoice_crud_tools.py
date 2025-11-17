from langchain_core.tools import Tool
from app.finance_agent.invoice.tools.crud_tools.create_invoice_no_tool import create_invoice_no_tool
from app.finance_agent.invoice.tools.crud_tools.extract_invoice_info_tool import extract_invoice_info_tool
from app.finance_agent.invoice.tools.crud_tools.create_invoice_in_db import create_invoice_in_db
from app.finance_agent.invoice.tools.query_tools.find_invoice_by_no import find_invoice_by_no
from app.finance_agent.invoice.tools.query_tools.find_invoice_by_job_no import find_invoice_by_job_no
from app.finance_agent.quotation.tools.crud_tools.get_job_no_by_project_name_tool import get_job_no_by_project_name_tool
from app.finance_agent.quotation.tools.crud_tools.get_client_info_by_project_name_tool import get_client_info_by_project_name_tool
from app.finance_agent.invoice.tools.output_invoice_info_for_ui import output_invoice_info_for_ui

invoice_crud_tools = [
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
        name="find_invoice_by_job_no",
        func=find_invoice_by_job_no,
        description="""Check if invoice already exists for a job.
        Input: Job number (e.g., "JCP-25-04-1")
        Output: Invoice data if exists, or error if not found.
        Use this BEFORE creating a new invoice to avoid duplicates.
        Example: find_invoice_by_job_no("JCP-25-04-1") → invoice data or {"error": "..."}"""
    ),
    Tool(
        name="create_invoice_no_tool",
        func=create_invoice_no_tool,
        description="""STEP 2: Generate invoice number from job number.
        Input: Job number from step 1 (e.g., "JCP-25-04-1")
        Output: {"invoice_no": "INV-JCP-25-04-1", "exists": false}
        Example: create_invoice_no_tool("JCP-25-04-1") → {"invoice_no": "INV-JCP-25-04-1", "exists": false}
        Note: If exists=true, invoice already created for this job."""
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
        name="extract_invoice_info_tool",
        func=extract_invoice_info_tool,
        description="""STEP 4: Extract structured invoice info using LLM.
        Input: JSON dict with {"user_input": "...", "client_info": {from step 3}, "job_no": "from step 1", "date": "YYYY-MM-DD"}
        Output: InvoiceInfo object with invoice items, amounts, due dates, etc.
        Example: extract_invoice_info_tool({"user_input": "items: 樑模板計算 5000mop...", "client_info": {...}, "job_no": "JCP-25-04-1", "date": "2025-01-20"})
        IMPORTANT: Pass as JSON dict, not plain string!"""
    ),
    Tool(
        name="create_invoice_in_db",
        func=create_invoice_in_db,
        description="""STEP 5: Save invoice to database.
        Input: Pass the output from extract_invoice_info_tool directly as extracted_info. JSON format:
        {"extracted_info": <output_from_step_4>, "invoice_no": "INV-JCP-25-04-1"}
        IMPORTANT: For extracted_info, use the EXACT output from extract_invoice_info_tool (the InvoiceInfo with all fields).
        Just structure it as: {"extracted_info": {all the fields from step 4 output}, "invoice_no": "INV-JCP-25-04-1"}
        Output: {"success": True, "invoice_no": "...", "items_inserted": 2}"""
    ),
    Tool(
        name="find_invoice_by_no",
        func=find_invoice_by_no,
        description="""Query invoice by invoice number.
        Input: Invoice number (e.g., "INV-JCP-25-04-1")
        Output: Complete invoice data with items and client info.
        Use this to retrieve existing invoices."""
    ),
    Tool(
        name="output_invoice_info_for_ui",
        func=output_invoice_info_for_ui,
        description="""FINAL STEP: Format and output invoice data for UI rendering.
        Input: Invoice number
        Output: Complete invoice data formatted for frontend display.
        Call this LAST after invoice is created."""
    )
]
