from typing import Annotated, Optional, Any
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class MainFlowState(BaseModel):
    """
    MainFlowState: Root graph state for the main orchestration flow.

    This state manages the overall conversation flow, agent routing,
    and coordination between different specialized agents.
    """
    user_input: str
    identified_agents: list[str] = []

    # Session tracking
    session_id: str  # User session identifier
    flow_uuid: str   # Unique ID for this flow execution (for DB logging)

    # Flow control
    intents: list[str] = []
    messages: Annotated[list[AnyMessage], add_messages] = []  # Main conversation flow
    classifier_msg: str = ""  # Classifier analysis message for logging
    agent_responses_summary: Any = None  # Agent responses (can be dict, str, etc.)

    # Human interaction
    human_clarification_flag: bool = False
    human_feedback: Optional[list[str]] = None
    interrupt_flag: bool = False
    feedback_outcome: Optional[str] = None

    # Final response
    final_response: Optional[Any] = None  # Final response to return to client
