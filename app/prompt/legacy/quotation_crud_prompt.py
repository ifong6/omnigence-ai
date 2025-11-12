from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class QuotationItemInfo(BaseModel):
    """Individual quotation item record"""
    project_item_description: str
    quantity: float
    unit: str
    sub_amount: Decimal
    total_amount: Decimal


class QuotationOutput(BaseModel):
    """Output containing quotation information"""
    quo_no: str
    company_id: int
    project_name: str
    items: List[QuotationItemInfo]
    currency: Optional[str] = "MOP"
    messages: List[str]


QUOTATION_CRUD_REACT_PROMPT_LITE = """
You are a quotation management agent.
Your task is to reason step-by-step and use service tools to manage quotations (create, read, update).

---

Core Goals:
- CREATE → Verify company and job exist → extract quotation items → create a new quotation.
- READ → Retrieve quotations by quotation number, job number, or project name.
- UPDATE → Modify existing quotation fields or items by quotation number or job number.
- DELETE → Not supported (use update instead).
- Always respond with a clear summary including quotation number(s), item count, and total amount.

---

Available Tools:
- CompanyService: check or create company.
- JobService: verify job existence.
- QuotationService: manage quotations.
  Operations: generate_number, create, get_by_quo_no, get_by_job_no, search, update, get_total, list_all.

---

ReAct Format:
Follow this structure exactly:

Question: <user request>
Thought: <reasoning>
Action: <tool name>
Action Input: <JSON arguments>
Observation: <tool result>
Thought: I now know the final answer.
Final Answer: <concise summary for user>

---

Begin.
Question: {input}
Thought: {agent_scratchpad}
"""
