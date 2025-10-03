from typing import Annotated, Optional, Any
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel

class MainFlowState(BaseModel):
    user_input: str
    agents: list[str] = None
    
    # Flow control
    messages: Annotated[list[AnyMessage], add_messages] = None  # Main conversation flow
    agent_responses_summary: Optional[str] = None
    
    # Human interaction
    human_clarification_flag: bool = False
    human_feedback: Optional[list[str]] = None
    interrupt_flag: bool = False
    feedback_outcome: Optional[str] = None
    
    # Operations
  
    
