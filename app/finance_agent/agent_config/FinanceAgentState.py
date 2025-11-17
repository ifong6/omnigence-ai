from pydantic import BaseModel
from typing import Annotated, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class FinanceAgentState(BaseModel):
    # User context (input only)
    user_input: Optional[str] = None
    agent_type: Optional[str] = None  # Agent type from routing

    # Planning/routing fields (ephemeral workflow state)
    intents: Optional[list[str]] = None
    next_handlers: Optional[list[str]] = None
    index: int = 0  # Current index for processing next_handlers
    job_type: Optional[str] = None  # Job type: "inspection" or "design"

    # Control flags (workflow coordination)
    human_clarification_flag: bool = False  # Flag to indicate if human clarification is needed

    # Response fields (final output only)
    quotation_response: Optional[dict] = None  # Formatted response for frontend
    invoice_response: Optional[dict] = None  # Formatted invoice response for frontend

    # Messages (LangGraph communication)
    messages: Optional[Annotated[list[AnyMessage], add_messages]] = []

f"""
uuid -> db sql table: flow_table -> logs: summary provided by PreOrchestractorLogger

framework comes with state management? 
"""

# http long polling -> pull per minute 

# to do list

# ui - main_agent  - sub_agent1 (task1: %50)
#              \ - sub_agent2 (task2: %50)