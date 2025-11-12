from typing import Any, Dict, Literal, Union
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from app.finance_agent.tools.company_service_tool import company_service_tool
from app.finance_agent.tools.job_service_tool import job_service_tool
from app.finance_agent.tools.quotation_service_tool import quotation_service_tool
import json

# --------- Company ---------
class CompanyCall(BaseModel):
    operation: Literal["get_or_create", "search", "get_by_id", "update", "list_all"]
    params: Dict[str, Any] = Field(default_factory=dict)

def _company_dispatch(call: str) -> Any:
    """
    Dispatch company service operations.
    Input should be JSON string: {"operation": "...", "params": {...}}
    """
    try:
        data = json.loads(call)
        validated = CompanyCall(**data)
        return company_service_tool(operation=validated.operation, params=validated.params)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format. {e}"
    except Exception as e:
        return f"Error: {e}. Expected format: {{'operation': '...', 'params': {{}}}}"

COMPANY_SERVICE = StructuredTool.from_function(
    name="CompanyService",
    description=(
        "Company CRUD/search. Operations: get_or_create, search, get_by_id, update, list_all. "
        "Input must be valid JSON: {\"operation\": \"...\", \"params\": {...}}"
    ),
    func=_company_dispatch,
)

# --------- Job ---------
class JobCall(BaseModel):
    operation: Literal["create", "get_by_job_no", "get_by_company", "update", "list_all"]
    params: Dict[str, Any] = Field(default_factory=dict)

def _job_dispatch(call: str) -> Any:
    """
    Dispatch job service operations.
    Input should be JSON string: {"operation": "...", "params": {...}}
    """
    try:
        data = json.loads(call)
        validated = JobCall(**data)
        return job_service_tool(operation=validated.operation, params=validated.params)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format. {e}"
    except Exception as e:
        return f"Error: {e}. Expected format: {{'operation': '...', 'params': {{}}}}"

JOB_SERVICE = StructuredTool.from_function(
    name="JobService",
    description=(
        "Job CRUD/list for DESIGN (JCP) and INSPECTION (JICP). "
        "Operations: create, get_by_job_no, get_by_company, update, list_all. "
        "IMPORTANT: Use 'title' parameter for job name (NOT 'name' or 'project'). "
        "CREATE example: {\"operation\": \"create\", \"params\": {\"company_id\": 1, \"title\": \"消防系統設計\", \"job_type\": \"DESIGN\"}}. "
        "LIST example: {\"operation\": \"list_all\", \"params\": {\"job_type\": \"INSPECTION\"}}."
    ),
    func=_job_dispatch,
)

# --------- Quotation ---------
class QuotationCall(BaseModel):
    operation: Literal[
        "generate_number", "create", "get_by_quo_no", "get_by_job_no",
        "search", "update", "get_total", "list_all"
    ]
    params: Dict[str, Any] = Field(default_factory=dict)

def _quotation_dispatch(call: str) -> Any:
    """
    Dispatch quotation service operations.
    Input should be JSON string: {"operation": "...", "params": {...}}
    """
    try:
        data = json.loads(call)
        validated = QuotationCall(**data)
        return quotation_service_tool(operation=validated.operation, params=validated.params)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format. {e}"
    except Exception as e:
        return f"Error: {e}. Expected format: {{'operation': '...', 'params': {{}}}}"

QUOTATION_SERVICE = StructuredTool.from_function(
    name="QuotationService",
    description=(
        "Quotation operations with auto numbering. "
        "Operations: generate_number, create, get_by_quo_no, get_by_job_no, search, update, get_total, list_all. "
        "IMPORTANT: When creating quotations, items must have: item_desc (description), quantity (integer), unit_price (Decimal), unit (optional, default 'Lot'). "
        "CREATE example: {\"operation\": \"create\", \"params\": {\"job_no\": \"JICP-25-02-1\", \"company_id\": 27, \"project_name\": \"結構安全檢測\", "
        "\"items\": [{\"item_desc\": \"Foundation inspection\", \"quantity\": 1, \"unit_price\": 20000}]}}. "
        "GENERATE_NUMBER example: {\"operation\": \"generate_number\", \"params\": {\"job_no\": \"JICP-25-02-1\"}}."
    ),
    func=_quotation_dispatch,
)

# Unified export of all service tools for the CRUD React Agent to use
SERVICE_TOOLS = [COMPANY_SERVICE, JOB_SERVICE, QUOTATION_SERVICE]
