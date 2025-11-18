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
    # next_handlers: Optional[list[str]] = None  # DISABLED: Only using single crud_react_agent now
    # index: int = 0  # DISABLED: No longer needed for handler routing
    job_type: Optional[str] = None  # Job type: "inspection" or "design"

    # Control flags (workflow coordination)
    human_clarification_flag: bool = False  # Flag to indicate if human clarification is needed

    # Response fields (final output only)
    quotation_response: Optional[dict] = None  # Formatted response for frontend
    handler_result: Optional[dict] = None  # Result from handler execution (e.g., job creation)

    # Messages (LangGraph communication)
    messages: Optional[Annotated[list[AnyMessage], add_messages]] = []
