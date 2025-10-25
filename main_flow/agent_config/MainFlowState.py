from typing import Annotated, Optional, Any
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class MainFlowState(BaseModel):
    user_input: str
    identified_agents: list[str] = None

    # Session tracking
    session_id: Optional[str] = None  # User session identifier
    flow_uuid: Optional[str] = None  # Unique ID for this flow execution (for DB logging)

    # Flow control
    intents: list[str] = None
    messages: Annotated[list[AnyMessage], add_messages] = None  # Main conversation flow
    classifier_msg: Optional[str] = None  # Classifier analysis message for logging
    agent_responses_summary: Optional[Any] = None  # Agent responses (can be dict, str, etc.)

    # Human interaction
    human_clarification_flag: bool = False
    human_feedback: Optional[list[str]] = None
    interrupt_flag: bool = False
    feedback_outcome: Optional[str] = None

    # Final response
    final_response: Optional[Any] = None  # Final response to return to client

    # Operations
  
    
